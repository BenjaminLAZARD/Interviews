from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_val_score
import pandas as pd
import pickle


def train(
    model: BaseEstimator,
    X: pd.DataFrame,
    y: pd.DataFrame,
    save_path: str,
) -> float:
    """trains the model on X and y and measures training performance over a 5 fold cross-validation"""
    mean_auc = cross_val_score(model, X, y, scoring="roc_auc", cv=5, n_jobs=6).mean()
    model.fit(X, y)

    with open(save_path, "wb") as f:
        pickle.dump(model, f)

    return mean_auc
