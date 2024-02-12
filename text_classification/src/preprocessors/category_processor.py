import logging

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm


class CustomCategoricalTransformer(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        super().__init__()
        self.selected_items = {}
        self.logger = logging.getLogger("customTextTransformer")
        self.logger.setLevel(logging.DEBUG)

    def fit(self, X: pd.DataFrame, y: pd.DataFrame | np.ndarray = None):
        assert {
            "crossorigin",
            "longdesc",
            "sizes",
            "class",
            "style",
            "tree_path",
            "loading",
        }.issubset(set(X.columns))
        out = X.copy()

        if y is None:
            assert "is_relevant" in X.columns
        else:
            assert "is_relevant" not in X.columns
            out.loc[:, "is_relevant"] = y

        self.selected_items["class"] = self._get_selected_column_items(
            out, "class", "class_item"
        )
        self.selected_items["style"] = self._get_selected_style_items(out, "style")
        self.selected_items["tree_path"] = self._get_selected_tree_path_items(
            file_path="pickled.pickle"
        )  # preloaded for speed
        self.logger.info(f"fitting for variable loading")
        self.selected_items["loading"] = [
            "lazy",
            "eager",
            "auto",
        ]  # assumed pre-computed because of the super simple analysis

        return self

    def transform(self, X, y=None):
        out = X.copy()
        # simple on-the-fly categorical conversions
        self.logger.info(
            "transforming variables crossorigin, longdesc, referrerpolicy and sizes"
        )
        out.loc[:, "crossorigin"] = out["crossorigin"].isna().astype(bool)
        out.loc[:, "longdesc"] = (
            out["longdesc"]
            .apply(lambda x: True if x is not None and len(x) > 4 else False)
            .astype(bool)
        )
        out.loc[:, "sizes"] = out["sizes"].isna().astype(bool)
        out.loc[:, "referrerpolicy"] = out["referrerpolicy"].str.contains("no-referrer")

        # customized conversion for some columns
        for column in ["class", "style", "tree_path", "loading"]:
            self.logger.info(f"transforming variable {column}")
            self._create_feature_columns_from_selected_elements_recognition(
                out, self.selected_items[column], column
            )

        out = out.drop(columns=["class", "style", "tree_path", "loading"])

        self._features_names = out.columns

        # use labelencoder that handles nan values?
        return out.copy()  # copy in order to avoid the "fragmented df warning"

    def get_features_names_out_(self) -> list[str]:
        return self._features_names

    def _create_feature_columns_from_selected_elements_recognition(
        self,
        out: pd.DataFrame,
        selected_elements: np.ndarray | pd.Series,
        source_column: str,
    ) -> pd.Series:
        out.loc[:, f"no_{source_column}"] = out[source_column].isna()
        for item in selected_elements:
            out.loc[:, f"{source_column}_item_{item}"] = (
                out[source_column].str.contains(item, regex=False).astype(bool)
            )
        # useless as all other variable being 0 imply the following case anyway
        # out.loc[:, f"{source_column}_item_others"] = (out[source_column].notna() & (~out[source_column].str.contains("|".join(selected_elements))))

    def _get_selected_tree_path_items(self, file_path: str) -> np.ndarray | pd.Series:
        """
        For performance purposes we performed the analysis outside this class.
        This class requires the pickled output of _compute_terms_interdomain_statistics_df
        """
        self.logger.info(f"fitting for variable tree_path")
        d = pd.read_pickle(file_path)
        return (
            d[(d.interdomain_occurence < 10000) & (d.interdomain_relevance > 10)]
            .reset_index(drop=True)
            .css_item
        )

    def _get_selected_style_items(
        self, df: pd.DataFrame, extracted_css_classes_column="css_class"
    ) -> np.ndarray | pd.Series:
        self.logger.info(f"fitting for variable style")
        tmp = (
            df[["source", "is_relevant"]]
            .reset_index()
            .merge(
                self._extract_style_classes(df["style"], extracted_css_classes_column),
                how="left",
                left_on="index",
                right_on="original_index",
            )
            .drop(columns=["original_index"])
        )
        tmp = pd.DataFrame(
            tmp.groupby("index")[extracted_css_classes_column].apply(list)
        ).assign(
            source=df.source,
            is_relevant=df.is_relevant,
            style_processed=lambda d: d[extracted_css_classes_column].apply(
                lambda s: s if s[0] is not np.nan else np.nan
            ),
        )
        terms, terms_interdomain_relevance = self._count_terms(
            tmp, extracted_css_classes_column
        )
        d = self._compute_terms_interdomain_statistics_df(
            terms, terms_interdomain_relevance, "css_item"
        )
        return self._compute_selected_css_items_from_statistics_df(d, "css_item")

    def _compute_selected_css_items_from_statistics_df(
        self, d: pd.DataFrame, css_column: str
    ) -> np.ndarray | pd.Series:
        """
        This function return a list of items in the column "class" to be
        considered as individual labels. d is the output of
        _compute_terms_interdomain_statistics_df
        """
        return (
            d[d.interdomain_relevance >= 10].reset_index(drop=True)[css_column].values
        )

    def _extract_style_classes(
        self, s: pd.Series, css_items_column_name: str
    ) -> pd.Series:
        return (
            s.str.lower()
            .str.extractall(rf"(?P<{css_items_column_name}>[^;,:\"\n\s]+)[ ]*:")
            .droplevel(1)
            .reset_index()
            .rename(columns={"index": "original_index"})
        )

    def _get_selected_column_items(
        self, df: pd.DataFrame, column: str, variable_name: str
    ) -> np.ndarray | pd.Series:
        """
        Return a list of items in the column "column" to be
        considered as individual labels. df is the input dataframe of .transform
        """
        self.logger.info(f"fitting for variable {column}")
        tmp = df[["source", "is_relevant", column]].assign(
            class_processed=df[column].str.split(" ")
        )
        terms, terms_interdomain_relevance = self._count_terms(
            tmp,
            f"{column}_processed",
        )
        return self._compute_selected_class_items_from_statistics_df(
            self._compute_terms_interdomain_statistics_df(
                terms, terms_interdomain_relevance, variable_name
            )
        )

    def _compute_selected_class_items_from_statistics_df(
        self, d: pd.DataFrame
    ) -> np.ndarray | pd.Series:
        """
        Return a list of items in the column "class" to be
        considered as individual labels. d is the output of
        _compute_terms_interdomain_statistics_df
        """
        return (
            d[
                ((d["interdomain_occurence"] >= 100) & (d["relevance_rate"] >= 0.15))
                | ((d["interdomain_occurence"] < 100) & (d["relevance_rate"] >= 0.3))
            ][d["interdomain_occurence"] > 20]
            .reset_index(drop=True)
            .class_item.values
        )

    def _count_terms(
        self, tmp: pd.DataFrame, column_name: str
    ) -> (dict[str], dict[int]):
        """
        - Compute the number of domains where a specific class_item in column_name
        is mentioned (terms)
        - Compute the number of domains where a specific
        class_item in column_name is mentioned and is relevant
        (terms_interdomain_relevance)
        """
        terms = {}
        terms_interdomain_relevance = {}
        for row in tqdm(tmp.itertuples(), total=tmp.shape[0]):
            classes = getattr(row, column_name)
            if classes not in [None, np.nan, pd.NaT]:
                classes = [
                    cl.strip()
                    for cl in classes
                    if (cl not in [None, np.nan, pd.NaT]) and len(cl) > 2
                ]
                for cl in classes:
                    if cl in terms:
                        if row.source not in terms[cl] and row.is_relevant == 1:
                            if cl in terms_interdomain_relevance:
                                terms_interdomain_relevance[cl] += 1
                            else:
                                terms_interdomain_relevance[cl] = 1
                        terms[cl] += [row.source]
                    else:
                        terms[cl] = [row.source]
                        if row.is_relevant == 1:
                            terms_interdomain_relevance[cl] = 1
        return terms, terms_interdomain_relevance

    def _compute_terms_interdomain_statistics_df(
        self,
        terms: dict[str],
        terms_interdomain_relevance: dict[int],
        variable_name: str,
    ) -> pd.DataFrame:
        """
        Compute statistics from terms and terms_interdomain_relevance to be presented in a neat df
        """
        terms_interdomain_relevance = dict(
            sorted(
                terms_interdomain_relevance.items(), key=lambda x: x[1], reverse=True
            )
        )
        terms_interdomain_occurences = sorted(
            {k: len(np.unique(v)) for k, v in terms.items()}.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        terms_interdomain_occurences = {
            k: v for k, v in terms_interdomain_occurences if v > 9
        }
        d = {
            variable_name: [],
            "interdomain_occurence": [],
            "interdomain_relevance": [],
        }
        for key in terms_interdomain_occurences:
            d[variable_name].append(key)
            d["interdomain_occurence"].append(terms_interdomain_occurences[key])
            if key not in terms_interdomain_relevance:
                d["interdomain_relevance"].append(0)
            else:
                d["interdomain_relevance"].append(terms_interdomain_relevance[key])
        d = (
            pd.DataFrame(d)
            .assign(
                relevance_rate=lambda d: d.interdomain_relevance
                / d.interdomain_occurence
            )
            .sort_values(
                by=["interdomain_occurence", "relevance_rate"], ascending=[False, False]
            )
        )
        return d
