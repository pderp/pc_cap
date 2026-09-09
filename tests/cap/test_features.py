"""CAP-01: key features have unit scale at every width; zero vector handled; single implementation."""

import numpy as np
import pytest

from pccap.cap.features import concat_keys, ln0, z


@pytest.mark.parametrize("d", [32, 768, 1024])
def test_unit_scale_keys(d):
    rng = np.random.default_rng(d)
    h = rng.standard_normal((50, d)).astype(np.float32) * rng.uniform(0.1, 100.0, size=(50, 1)).astype(np.float32)
    k = z(h)
    norms = np.linalg.norm(k, axis=-1)
    assert np.all(np.abs(norms - 1.0) < 2e-3), norms.min()
    assert k.dtype == np.float32


def test_ln0_centred_unit_variance():
    h = np.random.default_rng(0).standard_normal((4, 768)).astype(np.float32) * 7 + 3
    y = ln0(h)
    assert np.allclose(y.mean(-1), 0, atol=1e-5)
    assert np.allclose(y.var(-1), 1, atol=2e-3)


def test_zero_vector_is_zero_key_no_nan():
    k = z(np.zeros(768, np.float32))
    assert np.all(k == 0) and not np.isnan(k).any()


def test_scale_invariance():
    h = np.random.default_rng(1).standard_normal(768).astype(np.float32)
    assert np.allclose(z(h), z(3.5 * h), atol=1e-6)


def test_concat_keys_unit_scale():
    rng = np.random.default_rng(2)
    a, b = rng.standard_normal(768).astype(np.float32), rng.standard_normal(768).astype(np.float32)
    k = concat_keys(a, b)
    assert k.shape == (1536,) and abs(np.linalg.norm(k) - 1) < 2e-3
