import pandas as pd
from sklearn.base import BaseEstimator
import pickle


def load_model_from_path(model_path: str) -> BaseEstimator:
    with open("data.pickle", "rb") as f:
        model = pickle.load(f)
    return model


def predict_from_path(model_path: str, X: pd.DataFrame) -> pd.DataFrame:
    """Loads model from saved_path, performs prediction, and output score"""
    model = load_model_from_path(model_path)

    return model.predict(X)
