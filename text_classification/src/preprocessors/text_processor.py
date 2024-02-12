import gc
import logging

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from torch.nn.functional import cosine_similarity
from tqdm import tqdm


class CustomTextTransformer(BaseEstimator, TransformerMixin):
    """
    A custom transformer to apply text transformations * and compute features in
    the specific case of this exercise (not generalizable). This assumes english
    language and must be tweaked further to accept another or several languages
    """

    removable_url_parts = "https:// http:// www com org"
    url_splitting = r"""{}""".format(
        "|".join((removable_url_parts + " " + "/ - \. \? \+ : , ; & _").split())
    )
    text_columns = ["query", "url_page", "alt", "title", "text"]
    to_be_embedded_text_columns = ["title", "text"]

    def __init__(self, gpu_available: bool = True) -> None:
        super().__init__()
        self.logger = logging.getLogger("customTextTransformer")
        self.logger.setLevel(logging.DEBUG)
        self.embedder_model = SentenceTransformer(
            "paraphrase-MiniLM-L6-v2", device="cuda" if gpu_available else None
        )

    def fit(self, X, y=None):
        # check that text features do exist in the dataframe
        assert set(self.text_columns).issubset(set(X.columns))
        return self

    def transform(
        self, X: pd.DataFrame, y: pd.DataFrame | np.ndarray = None
    ) -> pd.DataFrame:
        self.tqdm_total = X.shape[0]
        out = X.drop(columns=self.text_columns)

        # lemmatize url, query, alt
        self.processed_columns_content = {}
        for col in self.text_columns:
            self.logger.info(f"lemmatizing {col}")
            self.processed_columns_content[col] = self._split_and_preprocess(X, col)

        # check if lemmatized query word is in lemmatized previous texts
        for col in self.text_columns[1:]:  # not taking the query
            self.logger.info(f"checking if query in {col}")
            out.loc[:, f"query_in_{col}"] = self._query_in_other_string(
                self.processed_columns_content["query"],
                self.processed_columns_content[col],
                self.tqdm_total,
            )

        # undoing the lemma stage for selected columns
        for col in self.to_be_embedded_text_columns:
            self.logger.info(f"undoing lemma stage for {col}")
            del self.processed_columns_content[col]
            self.processed_columns_content[col] = (
                self._remove_accents_and_special_characters(X, col)
            )

        # embedding everything
        for col in self.text_columns:
            self.logger.info(f"embedding {col}")
            self.processed_columns_content[col] = self._get_text_series_embedding(
                self.processed_columns_content[col]
            )

        # adding cosimilarity features
        for col in self.text_columns[1:]:  # not taking the query
            self.logger.info(f"computing similarity query-{col}")
            out.loc[:, f"similarity query-{col}"] = self._compute_similarity(
                self.processed_columns_content["query"],
                self.processed_columns_content[col],
            )
            self._clean_gpu_processed_column(col)

        self._features_names = out.columns

        return out

    def get_features_names_out_(self) -> list[str]:
        return self._features_names

    def _clean_gpu_processed_column(self, col: str) -> None:
        del self.processed_columns_content[col]
        gc.collect()
        torch.cuda.empty_cache()

    def _get_text_series_embedding(
        self, s: pd.Series, show_progress: bool = True
    ) -> torch.Tensor:
        """
        Converts a pandas series containing text to tensors. Null values are
        not handled natively hence they are replaced before and after
        """
        # replacing null values with a dummy string
        mask = s.isna()
        s[mask] = ""
        with torch.no_grad():  # saving memory space in the GPU
            out = self.embedder_model.encode(
                s,
                show_progress_bar=show_progress,
                convert_to_tensor=True,
            )
        # restoring null values in appropriate indices
        out[mask] = np.nan
        # store outside GPU to avoid OOM (I only have 4Go VRAM)
        out = out.detach().to(device="cpu")
        gc.collect()
        torch.cuda.empty_cache()
        return out

    def _compute_similarity(
        self, t1: torch.Tensor, t2: torch.Tensor, use_gpu: bool = False
    ) -> np.ndarray:
        """
        Computes cosine similarity between 2 sensors of the same size.
        Perform this operation in a GPU efficient fashion (or outside)
        """
        if use_gpu:
            t1 = t1.cuda()
            t2 = t2.cuda()
        out = cosine_similarity(
            t1,
            t2,
        ).numpy()
        return out

    def _query_in_other_string(
        self, q: pd.Series | np.ndarray, o: pd.Series | np.ndarray, length: int = None
    ) -> list[int]:
        """check how many words of q appear in o."""
        if length is None:
            length = q.shape[0]

        return [
            (
                len([item for item in query if item in processed_url])
                if query is not None and processed_url is not None
                else 0
            )
            for query, processed_url in tqdm(zip(q.str.split(" "), o), total=length)
        ]

    def _remove_accents_and_special_characters(self, X: pd.DataFrame, column: str):
        """
        - normalize NFKD -> remove accents but keep letters
        - encode ascii/decode utf8 -> remove non english characters
        """
        return (
            X[column]
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )

    def _split_and_preprocess(self, X: pd.DataFrame, column: str):
        """
        - apply accent and special chars removal
        - split the text given several possible characters
        - apply in parallel a preprocessing function
        """
        return (
            self._remove_accents_and_special_characters(X, column)
            .str.split(self.url_splitting, regex=True)
            .parallel_apply(self._url_preprocessing)
        )

    def _url_preprocessing(self, x: list[str]) -> np.array:
        """
        Create a feature by applying the following changes
        (imports are included in the function to make it portable for parallel processing)
        - converts the words to lemmas using nltk package
        - converts to lowercase
        - eliminate words that have an origina length < 3
        - eliminate duplicates (and therefore plural forms because of the lemmatizer)
        - create a string with the lemmas (separator is " ")
        """
        import numpy as np
        from nltk.stem import WordNetLemmatizer

        if x is None:
            return None

        lemmatizer = WordNetLemmatizer()
        return " ".join(
            np.unique([lemmatizer.lemmatize(e).lower() for e in x if len(e) > 2])
        )
