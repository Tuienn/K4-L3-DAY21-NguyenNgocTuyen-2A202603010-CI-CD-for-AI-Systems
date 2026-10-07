import pytest
from scripts.quality_gate import check_quality


@pytest.mark.parametrize('f1', [0.65, 0.8, 1.0])
def test_accepts_f1_at_or_above_threshold(f1):
    check_quality(f1)


@pytest.mark.parametrize('f1', [0.6499, 0.0, float('nan'), float('inf'), 1.01])
def test_blocks_low_or_invalid_f1(f1):
    with pytest.raises(SystemExit):
        check_quality(f1)
