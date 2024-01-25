from sklearn.datasets import fetch_openml
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from code.preprocessors.baseline import AgeTransformer, CustomPreprocessor
from code.estimators.baseline import BaselineEstimator
from code.training.base_trainer import train
from code.prediction.base_predictor import load_model_from_path
from code.evaluation.base_evaluator import evaluate

MODEL_PATH = "saved_models/baselinemodel.pkl"

X, y = fetch_openml(name="titanic", version=1, as_frame=True, return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = Pipeline(
    [
        ("ageTransformmer", AgeTransformer),
        ("preprocessor", CustomPreprocessor),
        ("estimator", BaselineEstimator),
    ]
)

cross_validated_training_score = train(
    model=model, X=X_train, y=y_train, save_path=MODEL_PATH
)

print(f"cross-validated auc score at training time: {cross_validated_training_score}")

fitted_model = load_model_from_path(MODEL_PATH)

evaluation_score = evaluate(fitted_model, X_test, y_test)


print(f"auc score at testing time: {evaluation_score}")
