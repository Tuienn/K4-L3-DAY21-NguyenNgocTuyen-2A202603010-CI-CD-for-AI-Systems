"""Train Adult income classification and record positive-class F1 in MLflow."""
import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from mlflow.models import infer_signature
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score

F1_THRESHOLD = 0.65


def train(
    params: dict,
    data_path: str = "data/train_batch1.csv",
    eval_path: str = "data/holdout.csv",
) -> float:
    df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)
    X_train, y_train = df_train.drop(columns=["target"]), df_train["target"]
    X_eval, y_eval = df_eval.drop(columns=["target"]), df_eval["target"]
    if list(X_train.columns) != list(X_eval.columns):
        raise ValueError("Training and holdout feature columns must match in order")

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "adult-income")
    if mlflow.get_experiment_by_name(experiment_name) is None:
        mlflow.create_experiment(
            experiment_name,
            artifact_location=Path(os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlartifacts")).resolve().as_uri(),
        )
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("random_state", 42)
        model = GradientBoostingClassifier(**params, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_eval)
        f1 = float(f1_score(y_eval, preds, zero_division=0))
        acc = float(accuracy_score(y_eval, preds))
        mlflow.log_metrics({"f1_score": f1, "accuracy": acc})
        mlflow.sklearn.log_model(
            model, "model", signature=infer_signature(X_eval, preds),
        )
        report = {
            "f1_score": f1,
            "accuracy": acc,
            "params": params,
            "train_rows": len(df_train),
            "eval_rows": len(df_eval),
            "run_id": run.info.run_id,
        }
        Path("outputs").mkdir(exist_ok=True)
        Path("outputs/report.json").write_text(json.dumps(report, indent=2) + "\n")
        Path("models").mkdir(exist_ok=True)
        joblib.dump(model, "models/model.joblib")
        mlflow.log_artifact("outputs/report.json")
        print(f"F1: {f1:.4f} | Accuracy: {acc:.4f} | MLflow run: {run.info.run_id}")
    return f1


if __name__ == "__main__":
    with open("params.yaml") as f:
        train(yaml.safe_load(f))
