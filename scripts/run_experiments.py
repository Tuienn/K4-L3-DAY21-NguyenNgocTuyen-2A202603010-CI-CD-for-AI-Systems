"""Run the three lab configurations and restore the best model and params."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from src.train import F1_THRESHOLD, train


def main():
    candidates = [
        {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
        {"n_estimators": 50, "learning_rate": 0.05, "max_depth": 2},
        {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 5},
    ]
    results = []
    best = None
    for params in candidates:
        f1 = train(params)
        report = json.loads(Path("outputs/report.json").read_text())
        results.append(report)
        if best is None or f1 > best["f1_score"]:
            best = report
            shutil.copy2("models/model.joblib", "models/best.joblib")
    Path("outputs/experiments.json").write_text(json.dumps(results, indent=2) + "\n")
    shutil.copy2("models/best.joblib", "models/model.joblib")
    Path("outputs/report.json").write_text(json.dumps(best, indent=2) + "\n")
    Path("params.yaml").write_text(yaml.safe_dump(best["params"], sort_keys=False))
    print(f"Selected {best['params']}: F1={best['f1_score']:.4f}")
    if best["f1_score"] < F1_THRESHOLD:
        raise SystemExit("No experiment passes F1 >= 0.65; try more configurations")


if __name__ == "__main__":
    main()
