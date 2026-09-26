"""ES99 is the mean of the worst 1 % of positions (fractional boundary, zero mass retained), not a percentile."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from aw import scoring as S  # noqa: E402
from aw import tail_figures as T  # noqa: E402


def test_single_severe_loss_among_zeros():
    x = np.zeros(1000)
    x[17] = 10.0
    assert abs(S.expected_shortfall(x, 0.99) - 1.0) < 1e-12
    assert abs(T.expected_shortfall(x, 0.99) - 1.0) < 1e-12
    assert np.quantile(np.maximum(x, 0), 0.99) == 0.0  # the defect Capex reported


def test_fractional_boundary_and_limits():
    x = np.array([5.0, 4.0, 3.0, 2.0, 1.0] + [0.0] * 5)  # n = 10, ES90 -> worst 1 position
    assert abs(S.expected_shortfall(x, 0.90) - 5.0) < 1e-12
    # ES85 -> worst 1.5 positions: (5 + 0.5 * 4) / 1.5 = 4.6667
    assert abs(S.expected_shortfall(x, 0.85) - (5.0 + 2.0) / 1.5) < 1e-12
    assert S.expected_shortfall(x, 0.0) == x.mean()  # whole distribution
    assert S.expected_shortfall(x, 1.0) == 5.0  # degenerate: the maximum
    assert np.isnan(S.expected_shortfall(np.array([]), 0.99))


def test_summary_and_statistics_use_expected_shortfall():
    rng = np.random.default_rng(3)
    d = rng.normal(0, 0.001, size=100_000)
    d[:10] = 8.0  # ten severe positions in 100,000 → ES99 = (10 × 8 + the 990 next-largest small positives) / 1000 ≈ 0.083
    stats = T.statistics(d)
    assert 0.080 < stats["es99_positive"] < 0.090
    assert np.quantile(np.maximum(d, 0), 0.99) < 0.01  # the percentile would hide the severe positions
