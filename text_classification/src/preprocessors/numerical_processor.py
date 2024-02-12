import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CustomNumericalPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        super().__init__()

    def fit(self, X: pd.DataFrame, y=None):
        assert {"height", "width"}.issubset(X.columns)

        out = X.copy()
        out.loc[:, "height"] = X.height.str.extract("(\d+)", expand=False).astype(
            "Int64"
        )
        out.loc[:, "width"] = X.width.str.extract("(\d+)", expand=False).astype("Int64")
        height_rescaled = out["height"][(out["height"] > -100) & (out["height"] < 1000)]
        self.height_mean = height_rescaled.mean()
        self.height_std = height_rescaled.std()
        assert abs(self.height_std) > 1e-8

        width_rescaled = out["width"][(out["width"] > -100) & (out["width"] < 1300)]
        self.width_mean = height_rescaled.mean()
        self.width_std = width_rescaled.std()
        assert abs(self.width_std) > 1e-8

        self._features_names = X.drop(columns=["height", "width"]).columns

        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        out = X.copy()
        out.loc[:, "height"] = X.height.str.extract("(\d+)", expand=False).astype(
            "Int64"
        )
        out.loc[:, "width"] = X.width.str.extract("(\d+)", expand=False).astype("Int64")
        out.loc[:, "height"] = (out["height"] - self.height_mean) / self.height_std
        out.loc[:, "width"] = (out["width"] - self.width_mean) / self.width_std
        return out.replace(pd.NaT, np.nan)

    def get_features_names_out(self) -> list[str]:
        return self._features_names
