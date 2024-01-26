import pandas as pd
from numpy import ndarray
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder


class CustomPreprocessor(BaseEstimator, TransformerMixin):
    """A custom estimator that does the following in one piece
    - filter NaN columns and drop features or replace missing values
    - ignore selected columns
    - OH encode categorical features
    """

    def __init__(
        self,
        percentage_null_accepted: float = 0.5,
        categorical_columns: list[str] | None = None,
        ignored_columns: list[str] | None = ["name", "ticket", "body", "cabin"],
        fillNaN_value=-1,
    ) -> None:
        self.percentage_null_accepted = percentage_null_accepted
        self.columns = []
        self.categorical_columns = categorical_columns
        self.ignored_columns = ignored_columns
        self.fillNaN_value = fillNaN_value

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
        self.categorical_columns = [
            col for col in categorical_columns if col in self.columns
        ]
        self.numerical_columns = [
            col for col in self.columns if col not in self.categorical_columns
        ]

        # print(self.columns, self.numerical_columns, self.categorical_columns)

        self.oh_encoder = OneHotEncoder(
            categories="auto",
            handle_unknown="infrequent_if_exist",
            sparse_output=False,
            drop="if_binary",
        )
        self.oh_encoder.fit(X[self.categorical_columns])

        return self

    def transform(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> pd.DataFrame:
        Xout = X.reset_index(drop=True)

        # Perform the same OH-encoding than what was done at training time
        Xoutn = Xout[self.numerical_columns]
        Xoutc = pd.DataFrame(
            self.oh_encoder.transform(Xout[self.categorical_columns]),
            columns=self.oh_encoder.get_feature_names_out(),
        )

        # fillna of missing columns with a dummy value
        Xout = pd.concat([Xoutn, Xoutc], axis=1)
        self._features_names = (
            self.numerical_columns + list(self.oh_encoder.get_feature_names_out())
        )

        return Xout.fillna(self.fillNaN_value)

    def get_feature_names_out(self) -> list[str]:
        return self._features_names


class AgeTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> TransformerMixin:
        return self

    def transform(self, X: pd.DataFrame, y: pd.DataFrame | None = None) -> pd.DataFrame:
        Xout = X.reset_index(drop=True)
        Xout.loc[:, "age"] = Xout.age.round()
        return Xout
