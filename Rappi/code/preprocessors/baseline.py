from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder
import pandas as pd


class CustomPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        percentage_null_accepted: float = 0.5,
        categorical_columns: list[str] | None = None,
        ignored_columns: list[str] | None = ["name", "ticket", "body", "cabin"],
    ) -> None:
        self.percentage_null_accepted = percentage_null_accepted
        self.columns = []
        self.categorical_columns = categorical_columns
        self.ignored_columns = ignored_columns

    def fit(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> TransformerMixin:
        # ignore selected columns
        X = X[[col for col in X.columns if col not in self.ignored_columns]]

        # Pick columns with more than 50% null values and remove them, store chosen columns
        for column in X.columns:
            if X[column].isna().sum() / X.shape[0] <= self.percentage_null_accepted:
                self.columns.append(column)

        # TODO: fillna?

        # Select columns that are categories and OH-encode them
        categorical_columns = (
            self.categorical_columns
            if self.categorical_columns is not None
            else X.select_dtypes(include="category").columns
        )
        self.numerical_columns = [
            col for col in X.columns if col not in categorical_columns
        ]
        self.oh_encoder = OneHotEncoder(
            categories="auto", handle_unknown="infrequent_if_exist"
        )
        self.oh_encoder.fit(X[categorical_columns])

        return self

    def transform(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> pd.DataFrame:
        Xout = X.copy()

        # Use columns selected at fit time (takes into account ignored columns)
        Xout = Xout[self.columns]

        # Perform the same OH-encoding than what was done at training time
        Xoutn = Xout[self.numerical_columns]
        Xoutc = self.oh_encoder.transform(Xout[self.categorical_columns])

        return pd.concat([Xoutn, Xoutc])


class AgeTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> TransformerMixin:
        return X

    def transform(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> pd.DataFrame:
        X = X.copy()
        X.loc[:, "age"] = X.age.round()
        return X
