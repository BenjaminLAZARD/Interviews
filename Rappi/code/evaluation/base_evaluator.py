import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline

from ..estimators.baseline import BaselineEstimator


def evaluate(
    model: BaselineEstimator | Pipeline, Xtest: pd.DataFrame, ytest: pd.DataFrame
) -> float:
    """Evaluate the performance of a trained model on the testing set using AUC score"""
    if isinstance(model, BaselineEstimator):
        assert model.is_fitted
    if isinstance(model, Pipeline):
        assert model.named_steps["estimator"].is_fitted

    ytest_hat = model.predict(Xtest)
    return roc_auc_score(ytest, ytest_hat, average="weighted")
