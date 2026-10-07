"""Train the selected model, or a weak candidate for the quality-gate demo."""
import os
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.train import train


if __name__ == '__main__':
    params = yaml.safe_load(Path('params.yaml').read_text())
    if os.getenv('QUALITY_GATE_DEMO', 'false').lower() == 'true':
        params = {'n_estimators': 50, 'learning_rate': 0.05, 'max_depth': 2}
        print('Quality-gate demo: training a weak candidate; selected params.yaml stays unchanged.')
    train(params)
