import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier


class BaselineEstimator(GradientBoostingClassifier):
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

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.estimator.predict(X)

    # Property below are bogus: they should be inherited from GradientBoostingClassifier
    # But this is just an example
    @property
    def feature_importances(self):
        return self.estimator.feature_importances_

    @property
    def learning_rate(self):
        return self.estimator.learning_rate

    @property
    def n_estimators(self):
        return self.estimator.n_estimators

    @property
    def max_depth(self):
        return self.estimator.max_depth

    def decision_function(self, X):
        return self.estimator.decision_function(X)

    def predict_proba(self, X):
        return self.estimator.predict_proba(X)

    @property
    def classes_(self):
        return self.estimator.classes_
