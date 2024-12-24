import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from src.model.preprocessing import (
    detect_language,
    extract_nouns_batch,
    remove_words_from_col,
    translate_col,
)


def train(campaigns_df:pd.DataFrame)->None:
    """Trains a clustering model.

    Parameters :
    ----------
    - `campaigns_df` (_type_) : CSV with input data
    """
    # apply language detection and translation
    campaigns_df.loc[:, "language"] = campaigns_df.long_description.apply(
        detect_language,
    )
    campaigns_df = campaigns_df[
        campaigns_df.language.isin(["en", "fr", "de", "es", "pt"])
    ]
    campaigns_df.loc[campaigns_df.language == "en", "translated_desc"] = (
        campaigns_df.loc[campaigns_df.language == "en", "long_description"]
    )

    campaigns_df.loc[campaigns_df.language != "en", "translated_desc"] = translate_col(
        campaigns_df.loc[campaigns_df.language != "en", "long_description"],
        dest_language="en",
    )

    # apply TFIDF along with filters
    vectorizer = TfidfVectorizer(
        stop_words="english", max_df=0.7, min_df=0.05, ngram_range=(1, 1),
    )
    preprocessed_col = pd.Series(
        extract_nouns_batch(campaign_df_train.translated_desc), dtype="str",
    )
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
    X = vectorizer.fit_transform(preprocessed_col)

    # Apply clustering algorithm
    dbscan = HDBSCAN(
        metric="cosine", min_cluster_size=10, cluster_selection_epsilon=0.0, alpha=1.0,
    )
    campaign_df_train.loc[:, "cluster"] = dbscan.fit_predict(X)

    # save to pickle the vectorizer and dbscan
    with Path("vectorizer.pkl").open("wb") as file:
        pickle.dump(vectorizer, file)
    with Path("clusterizer.pkl").open("wb") as file:
        pickle.dump(dbscan, file)

# Define a function to name clusters
def generate_cluster_names(
    sentences: np.ndarray,
    embeddings: np.ndarray,
    clusters: list[int],
    top_n_terms: int = 5,
    ignored_terms: list[str] | None = None,
)->list[str]:
    """Find cluster names for text embeddings.

    Parameters
    ----------
    - `sentences` (np.ndarray) : setences (text)
    - `embeddings` (np.ndarray)
    - `clusters` (list[int]) : cluster labels
    top_n_terms : int, optional
        how many terms to use for cluster name, by default 5
    ignored_terms : list[str], optional
        terms to be ignored for cluster naming ocnvention
        , by default ["app", "campaign", "campaigns"]

    Returns
    -------
    - (_type_): list of cluster labels and key terms

    """
    if ignored_terms is None:
        ignored_terms = ["app", "campaign", "campaigns", "ll"]
    cluster_names = {}
    vectorizer = TfidfVectorizer(stop_words="english", max_features=10)

    for cluster_id in np.unique(clusters):

        # Get sentences and embeddings for this cluster
        cluster_indices = np.where(clusters == cluster_id)[0]
        cluster_sentences = sentences[cluster_indices]
        cluster_embeddings = embeddings[cluster_indices]

        # 1. Find the centroid sentence
        # centroid = cluster_embeddings.mean(axis=0)
        # distances = cosine_distances([centroid], cluster_embeddings).flatten()
        # closest_idx = cluster_indices[np.argmin(distances)]
        # representative_sentence = sentences[closest_idx]

        # 2. Extract top terms with TF-IDF
        tfidf_matrix = vectorizer.fit_transform(cluster_sentences)
        terms = vectorizer.get_feature_names_out()
        top_terms = terms[:top_n_terms]  # Select top N terms

        # 3. Combine to create a cluster name
        # cluster_name = f"{representative_sentence} ({', '.join(top_terms)})"
        cluster_name = [term for term in top_terms if term not in ignored_terms]
        cluster_names[cluster_id] = cluster_name

    return cluster_names


if __name__ == "main":
    # Read dataset
    campaigns_df = pd.read_csv(
        "data/_SELECT_c_id_as_campaign_id_c_product_name_as_product_name_c_sho_202411281333.csv",
    )
    # Use only training set
    campaign_df_train, campaign_df_test = train_test_split(
        campaigns_df, train_size=0.75, test_size=0.15, random_state=42,
    )
    # save test set to pickle
    with Path("campaign_df_test.pkl").open("wb") as file:
        pickle.dump(campaign_df_test, file)
    # Train model and save params
    train(campaign_df_train)
