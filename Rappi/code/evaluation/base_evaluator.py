from sklearn.metrics import roc_auc_score
from ..estimators.baseline import BaselineEstimator
import pandas as pd


def evaluate(
    model: BaselineEstimator, Xtest: pd.DataFrame, ytest: pd.DataFrame
) -> float:
    """Evaluate the performance of a trained model on the testing set using AUC score"""
    assert model.is_fitted

    ytest_hat = model.predict(Xtest)
    return roc_auc_score(ytest, ytest_hat, average="weighted")
