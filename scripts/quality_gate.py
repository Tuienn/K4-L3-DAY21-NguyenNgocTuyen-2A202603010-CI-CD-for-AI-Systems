"""Fail closed unless the positive-class F1 meets the lab threshold."""
import math
import sys


def check_quality(f1: float) -> None:
    if not math.isfinite(f1) or not 0.65 <= f1 <= 1:
        raise SystemExit(f"FAILED: f1_score {f1} must be within [0.65, 1]. Release blocked.")
    print(f"PASSED: f1_score {f1:.4f} >= 0.65")


if __name__ == "__main__":
    check_quality(float(sys.argv[1]))
