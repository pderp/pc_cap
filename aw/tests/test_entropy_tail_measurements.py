import math

import numpy as np
import pytest

from aw.entropy_tail_measurements import (
    concentration,
    describe,
    entropy,
    histogram_comparison,
    kl,
    predictive_entropy,
)


def test_entropy_and_kl_known_distributions():
    assert entropy([.5, .5, 0]) == pytest.approx(math.log(2))
    assert kl([1, 0], [.5, .5])["value"] == pytest.approx(math.log(2))
    assert kl([.5, .5], [1, 0])["status"] == "infinite_support_mismatch"
    with pytest.raises(ValueError):
        entropy([1, 1])


def test_zero_uniform_and_concentrated_loss_mass():
    assert concentration(np.zeros(10))["entropy_nats"] is None
    assert concentration(np.ones(10))["effective_positions"] == pytest.approx(10)
    one = concentration([0, 0, 5, 0])
    assert one["effective_positions"] == pytest.approx(1)
    assert one["kl_to_uniform_nats"] == pytest.approx(math.log(4))
    assert one["half_mass_positions"] == 1
    assert concentration([0, 0, 50, 0]) == one


def test_fractional_tail_mass_preserves_zero_denominator():
    x = np.zeros(2500)
    x[:3] = [10, 8, 6]
    d = describe(x)
    assert d["es99_9_positive"] == pytest.approx((10 + 8 + .5 * 6) / 2.5)
    assert d["positive_mass"]["top_0_1_percent_mass_share"] == pytest.approx(21 / 24)
    assert d["exceedances"]["5.0"]["fraction"] == pytest.approx(3 / 2500)


def test_histogram_zeros_not_silently_discarded():
    result = histogram_comparison([10, 10], [0, 0])
    assert result["raw_a_to_b"]["value"] is None
    assert result["js_nats"] == pytest.approx(math.log(2))
    assert all(np.isfinite(r["a_to_b"]) for r in result["smoothed"].values())
    equal = histogram_comparison([0, 1, 20], [0, 1, 20])
    assert equal["raw_a_to_b"]["value"] == pytest.approx(0)


def test_logits_entropy_stable_and_shift_invariant():
    uniform = np.full(50257, 10000.)
    h, k = predictive_entropy(uniform)
    assert h == pytest.approx(math.log(50257))
    assert k == pytest.approx(0, abs=1e-12)
    peaked = np.full(50257, -10000.)
    peaked[0] = 10000.
    assert predictive_entropy(peaked)[0] == pytest.approx(0)
    assert np.all(uniform == 10000.)  # analysis must not modify cached data
