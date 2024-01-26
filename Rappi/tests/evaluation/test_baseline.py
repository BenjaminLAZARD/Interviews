from code.estimators.baseline import BaselineEstimator
from code.evaluation.base_evaluator import evaluate

import pandas as pd
import pytest


def test_evaluate():
    x = pd.DataFrame({"cat": [0, 1, 1, 1] * 50, "a": [0] * 200, "d": [0, 1, 0, 1] * 50})
    y = [0, 1, 1, 0] * 50
    model = BaselineEstimator()
    with pytest.raises(AssertionError) as e:
        evaluate(model, x, y)
    model.fit(x, y)
    score = evaluate(model, x, y)
    assert 0 <= score and score <= 1
