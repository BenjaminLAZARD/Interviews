import contextlib

import langdetect
import numpy as np
import pandas as pd
import spacy
from deep_translator import GoogleTranslator
from langdetect import LangDetectException
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")


def remove_words_from_col(df_col: pd.Series, words: list[str]) -> pd.Series:
    """Remove words from column containing sentences.

    Parameters
    ----------
    - `df_col` (pd.Series) : _description_
    - `words` (list[str]) : _description_

    Returns
    -------
    - (_type_): _description_

    """
    col = df_col
    for word in words:
        col = col.str.replace(word, "")
    return col


# Function to process rows in batches
def extract_nouns_batch(texts: list[str]) -> list[str]:
    """Keep only POS nouns.

    Parameters
    ----------
    - `texts` (list[str]) : list of sentences

    Returns
    -------
    - (list[str]): list of nouns in texts

    """
    docs = nlp.pipe(texts)  # Use spaCy's pipe for batch processing
    results = []
    for doc in docs:
        nouns = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
        results.append(" ".join(nouns))
    return results


def detect_language(x: str) -> str:
    """Language of sentence x.

    Parameters
    ----------
    - `x` (str) : _description_

    Returns
    -------
    - (str): _description_

    """
    out = np.nan
    with contextlib.suppress(LangDetectException):
        out = langdetect.detect(x)
    return out


def translate_col(df_col:pd.Series, dest_language: str = "en")->list[str]:
    """Translate column for source language to target language.

    Parameters
    ----------
    - `df_col` (_type_) : _description_
    dest_language : str, optional
        _description_, by default "en"

    Returns
    -------
    - (_type_): _description_

    """
    translator = GoogleTranslator(source="auto", target="en")

    out = []
    for sentence in tqdm(df_col.values):
        out.append(translator.translate_batch([sentence], dest=dest_language))
    return out
