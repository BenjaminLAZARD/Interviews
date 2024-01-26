from code.estimators.baseline import BaselineEstimator
from code.training.base_trainer import train

import pandas as pd


def test_train(tmpdir):
    x = pd.DataFrame(
        {"cat": [0, 1, 1, 1] * 100, "a": [0] * 400, "d": [0, 1, 0, 1] * 100}
    )
    y = [0, 1, 1, 0] * 100
    model = BaselineEstimator()
    file_path = tmpdir.join("output.pkl")
    result = train(model=model, X=x, y=y, save_path=file_path.strpath)
    assert len(tmpdir.listdir()) == 1
    assert 0 <= result and result <= 1
