from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd


class BaselineEstimator(BaseEstimator):
    def __init__(
        self, learning_rate: float = 0.1, n_estimators: int = 100, max_depth: int = 3
    ) -> None:
        self.estimator = GradientBoostingClassifier(
            learning_rate=learning_rate, n_estimators=n_estimators, max_depth=max_depth
        )
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> BaseEstimator:
        self.is_fitted = True
        return self.estimator.fit(X, y)

    def predict(self, X: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:
        return self.estimator.predict(X, y)

    @property
    def feature_importances(self):
        return self.estimator.feature_importances_
