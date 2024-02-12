import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CustomColumnRemoverPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        super().__init__()
        self.columns_to_remove = ["source", "src", "ismap", "srcset", "id"]

    def fit(self, X: pd.DataFrame, y=None):
        assert set(self.columns_to_remove).issubset(set(X.columns))
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        out = X.drop(
            columns=(
                self.columns_to_remove + ["is_relevant"]
                if "is_relevant" in X.columns
                else self.columns_to_remove
            )
        )
        self._features_names = out.columns
        return out

    def get_features_names_out(self) -> list[str]:
        return self._features_names
