"""Training contracts on synthetic data; no Azure credentials required."""
import json

import joblib
import mlflow
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score

from src.train import train

FEATURE_NAMES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]


def _make_temp_data(tmp_path):
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.random((200, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
    df["target"] = rng.integers(0, 2, size=200)
    train_path = tmp_path / "train.csv"
    eval_path = tmp_path / "holdout.csv"
    df.iloc[:160].to_csv(train_path, index=False)
    df.iloc[160:].to_csv(eval_path, index=False)
    return str(train_path), str(eval_path)


@pytest.fixture
def trained(tmp_path, monkeypatch):
    # Isolate test artifacts so tests never overwrite the selected lab model.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{tmp_path / 'mlflow.db'}")
    monkeypatch.setenv("MLFLOW_EXPERIMENT_NAME", "unit-tests")
    monkeypatch.setenv("MLFLOW_ARTIFACT_ROOT", str(tmp_path / "mlartifacts"))
    train_path, eval_path = _make_temp_data(tmp_path)
    result = train(
        {"n_estimators": 10, "learning_rate": 0.1, "max_depth": 2},
        data_path=train_path, eval_path=eval_path,
    )
    yield result, tmp_path, eval_path
    mlflow.set_tracking_uri("sqlite:///mlflow.db")


def test_train_returns_float(trained):
    result, _, _ = trained
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_report_file_created(trained):
    result, tmp_path, eval_path = trained
    report = json.loads((tmp_path / "outputs/report.json").read_text())
    holdout = pd.read_csv(eval_path)
    model = joblib.load(tmp_path / "models/model.joblib")
    preds = model.predict(holdout.drop(columns=["target"]))
    # Verify the report uses positive-class F1, not weighted F1 or accuracy.
    assert report["f1_score"] == pytest.approx(f1_score(holdout["target"], preds))
    assert report["accuracy"] == pytest.approx(accuracy_score(holdout["target"], preds))
    assert report["f1_score"] == result
    run = mlflow.get_run(report["run_id"])
    assert run.data.metrics["f1_score"] == result
    assert run.data.metrics["accuracy"] == report["accuracy"]
    assert report["train_rows"] == 160 and report["eval_rows"] == 40


def test_model_file_created(trained):
    _, tmp_path, _ = trained
    model = joblib.load(tmp_path / "models/model.joblib")
    assert list(model.feature_names_in_) == FEATURE_NAMES
    assert set(model.classes_) == {0, 1}
