from code.estimators.baseline import BaselineEstimator

import pandas as pd


def test_estimator():
    x = pd.DataFrame({"cat": [0, 1, 1, 1], "a": [0] * 4, "d": [0, 1, 0, 1]})
    y = [0, 1, 1, 0]
    model = BaselineEstimator()
    model.fit(x, y)
    y_hat = model.predict(x)

    assert y_hat.shape[0] == 4
    for x in y_hat:
        assert 0 <= x and x <= 1
