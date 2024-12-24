import pickle
from pathlib import Path

import pandas as pd

from src.model.preprocessing import (
    detect_language,
    extract_nouns_batch,
    remove_words_from_col,
    translate_col,
)


def predict(df: pd.DataFrame) -> pd.DataFrame:
    """Predicts clusters.

    Parameters
    ----------
    - `df` (pd.DataFrame) : dataframe similar to the train function input

    Returns
    -------
    - (pd.DataFrame): _description_

    """
    df.loc[:, "language"] = df.long_description.apply(detect_language)
    df = df[df.language.isin(["en", "fr", "de", "es", "pt"])]
    df.loc[df.language == "en", "translated_desc"] = df.loc[
        df.language == "en", "long_description",
    ]

    df.loc[df.language != "en", "translated_desc"] = translate_col(
        df.loc[df.language != "en", "long_description"], dest_language="en",
    )

    preprocessed_col = pd.Series(extract_nouns_batch(df.translated_desc), dtype="str")
    preprocessed_col = remove_words_from_col(
        preprocessed_col,
        [
            "campaign",
            "users",
            "video",
            "app",
            "wi",
            "ll",
            "th",
            "new",
            "eir",
            "brief",
            "foow",
        ],
    )

    # load the vectorizer and dbscan from pickle
    with Path("vectorizer.pkl").open("rb") as file:
        vectorizer = pickle.load(file)
    with Path("clusterizer.pkl").open("rb") as file:
        dbscan = pickle.load(file)
    X = vectorizer.transform(preprocessed_col)
    df.loc[:, "cluster"] = dbscan.predict(X)
    return df


if __name__ == "main":
    # Read dataset
    campaigns_df = pd.read_csv(
        "data/_SELECT_c_id_as_campaign_id_c_product_name_as_product_name_c_sho_202411281333.csv",
    )
    # Use only test set
    with Path("campaign_df_test.pkl").open("rb") as file:
        campaign_df_test = pickle.load(file)
    # Train model and save params
    df = predict(campaign_df_test)
    with Path("campaign_df_test_predicted.pkl").open("wb") as file:
        pickle.dump(df, file)
