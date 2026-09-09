"""S0-05: transport turns signals into unit directions; zero -> no_direction; projection first."""

from pathlib import Path

import numpy as np
import pytest

from pccap.contracts import SiteId
from pccap.transport.transport import Transport, sign_convention_control

ROOT = Path(__file__).resolve().parents[2]
SITE = SiteId(1, 3, 4)


def test_unit_direction_and_sign():
    g = np.array([3.0, 4.0], dtype=np.float32)
    r = Transport().direction(g, SITE)
    assert r.status == "ok" and abs(np.linalg.norm(np.asarray(r.direction)) - 1) < 1e-6
    np.testing.assert_allclose(np.asarray(r.direction), [-0.6, -0.8], atol=1e-6)
    assert r.signal_norm == pytest.approx(5.0)


def test_zero_vector_is_no_direction():
    r = Transport().direction(np.zeros(5, np.float32), SITE)
    assert r.status == "no_direction" and r.direction is None


def test_projection_before_normalization():
    Q = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]], dtype=np.float32)  # allow first two coords
    r = Transport().direction(np.array([0.0, 0.0, 5.0], np.float32), SITE, allowed_subspace=Q)
    assert r.status == "no_direction" and r.projected  # projected signal vanishes -> no direction
    r2 = Transport().direction(np.array([1.0, 0.0, 100.0], np.float32), SITE, allowed_subspace=Q)
    np.testing.assert_allclose(np.asarray(r2.direction), [-1.0, 0.0, 0.0], atol=1e-6)


def test_nonfinite_raises():
    with pytest.raises(FloatingPointError):
        Transport().direction(np.array([np.nan, 1.0], np.float32), SITE)


def test_sign_is_fixed():
    with pytest.raises(ValueError):
        Transport(sign=0.5)


def test_sign_convention_control_recorded():
    out = ROOT / "results" / "S0" / "controls" / "sign_convention.json"
    rec = sign_convention_control(out)
    assert rec["descent_reduces_loss"] and rec["flipped_increases_loss"]
    assert out.exists()
