import pandas as pd

from src.preprocessors.category_processor import CustomCategoricalTransformer


class Test_CustomCategoricalTransformer:

    def test_extract_style_classes(self):
        df = pd.DataFrame(
            {"class": ["class1:hey; class2:no", "class2:whatever; class3:something"]}
        )
        transformer = CustomCategoricalTransformer()
        classes = transformer._extract_style_classes(df["class"], "cssItem")
        assert set(classes.columns) == {"original_index", "cssItem"}
        assert classes.shape[0] == 4
        assert (
            classes.loc[classes["original_index"] == 1, ["cssItem"]]["cssItem"].values
            == ["class2", "class3"]
        ).all()

    def test_get_features_names_out(self):
        transformer = CustomCategoricalTransformer()
        transformer._features_names = ["bachibouzouk"]
        assert transformer.get_features_names_out_()[0] == "bachibouzouk"

    # etc.
