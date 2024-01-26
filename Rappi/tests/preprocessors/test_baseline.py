from code.preprocessors.baseline import AgeTransformer, CustomPreprocessor

import numpy as np
import pandas as pd


def test_AgeTransformer():
    at = AgeTransformer()
    df = pd.DataFrame({"age": [2.3, 4, 3.7]})
    at.fit(df)
    out = at.transform(df)
    assert (out.age == np.array([2, 4, 4])).all()


def test_CustomPreprocessor():
    cp = CustomPreprocessor(
        percentage_null_accepted=0.5,
        ignored_columns=["a"],
        categorical_columns=["d", "a"],
    )
    df = pd.DataFrame(
        {"cat": [0, 1, 1], "a": [0] * 3, "b": [pd.NaT] * 3, "d": ["x", "p", "x"]}
    )
    cp.fit(df)
    assert cp.numerical_columns == ["cat"]
    assert cp.categorical_columns == ["d"]

    dft = cp.transform(df)
    assert set(dft.columns) == {"cat", "d_p", "d_x"}
    assert (dft["cat"] == np.array([0, 1, 1])).all()
    assert dft["d_p"][0] == dft["d_p"][2]
    assert dft["d_p"][0] in (0, 1)
