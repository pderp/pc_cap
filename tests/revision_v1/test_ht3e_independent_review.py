import numpy as np
import pytest
from scripts.ht3e_independent_review import recovery_from_bands, tail


def test_fractional_tail_keeps_zero_positions_and_boundary_mass():
    x = [10, 9, *([-2] * 19)]
    es95, maximum = tail(x)
    assert maximum == 10
    assert es95 == pytest.approx((10 + 0.05 * 9) / 1.05)
    assert tail([-1, 0, -2]) == (0, 0)
    with pytest.raises(ValueError):
        tail([np.nan])


def test_late_harm_censor_uses_treatment_end_not_first_harm():
    r = recovery_from_bands({20: True, 60: True, 70: True, 80: False, 100: False})
    assert r["right_censored"] and r["censor_after_updates"] == 40
    assert "not time of first detected harm" in r["origin"]


def test_recovery_must_be_sustained_at_every_later_measured_point():
    r = recovery_from_bands({20: True, 60: False, 70: True, 80: False, 100: True})
    assert r["lag_interval_updates"] == [20, 40]
    assert not r["right_censored"]
    with pytest.raises(ValueError):
        recovery_from_bands({20: True, 60: True})
