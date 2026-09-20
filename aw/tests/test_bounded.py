"""CPU float64 checks for the AW-B oracle: normalisation, identity limits, extreme logits, and the per-token bounds."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from aw import bounded as B  # noqa: E402

RNG = np.random.default_rng(20260920)


def random_pair(n=50257, batch=4, scale=8.0):
    lp0 = B.log_normalise(RNG.normal(0, scale, size=(batch, n)))
    lp1 = B.log_normalise(RNG.normal(0, scale, size=(batch, n)) + lp0)
    return lp0, lp1


def test_normalisation_and_limits():
    lp0, lp1 = random_pair(n=1000)
    for b in (0.0, 0.5, 1.0, 2.0, 4.0, np.inf):
        q = B.clip_tilt(lp0, lp1, b)
        assert np.allclose(np.exp(q).sum(-1), 1.0, atol=1e-12)
    assert np.allclose(B.clip_tilt(lp0, lp1, 0.0), lp0, atol=1e-12)
    assert np.allclose(B.clip_tilt(lp0, lp1, np.inf), lp1, atol=1e-12)
    assert np.allclose(B.mixture(lp0, lp1, 1.0), lp0, atol=1e-12)
    assert np.allclose(B.mixture(lp0, lp1, 0.0), lp1, atol=1e-12)
    assert np.allclose(B.shrink(lp0, lp1, 0.0), lp0, atol=1e-12)
    assert np.allclose(B.shrink(lp0, lp1, 1.0), lp1, atol=1e-12)
    for rho in (0.25, 0.5):
        assert np.allclose(np.exp(B.mixture(lp0, lp1, rho)).sum(-1), 1.0, atol=1e-12)
        assert np.allclose(np.exp(B.mixture(lp0, lp1, rho)), rho * np.exp(lp0) + (1 - rho) * np.exp(lp1), atol=1e-12)


def test_clip_bounds_every_token():
    lp0, lp1 = random_pair(n=20000, scale=12.0)
    targets = RNG.integers(0, lp0.shape[1], size=(lp0.shape[0], 64))  # 64 targets per row
    single = RNG.integers(0, lp0.shape[1], size=lp0.shape[0])  # one target per row
    assert B.loss_increase(lp0, lp0, single).shape == (lp0.shape[0],)
    for b in (0.25, 0.5, 1.0, 2.0, 4.0):
        q = B.clip_tilt(lp0, lp1, b)
        # per-token loss increase ≤ 2b and benefit ≤ 2b, for every token, not just sampled targets
        d = lp0 - q
        assert d.max() <= 2 * b + 1e-9
        assert d.min() >= -2 * b - 1e-9
        assert np.all(B.kl(lp0, q) <= 2 * b + 1e-9)
        assert np.all(np.abs(B.loss_increase(lp0, q, targets)) <= 2 * b + 1e-9)


def test_mixture_bound_matches_clip_bound():
    lp0, lp1 = random_pair(n=5000, scale=12.0)
    for b in (0.5, 1.0, 2.0):
        rho = B.matched_rho(b)
        q = B.mixture(lp0, lp1, rho)
        assert (lp0 - q).max() <= -np.log(rho) + 1e-9
        assert abs(-np.log(rho) - 2 * b) < 1e-12


def test_extreme_finite_logits():
    n = 300
    lp0 = B.log_normalise(np.concatenate([[700.0], np.full(n - 1, -700.0)])[None])
    lp1 = B.log_normalise(np.concatenate([[-700.0], np.full(n - 1, 700.0)])[None])
    for b in (0.5, 4.0, 40.0):
        q = B.clip_tilt(lp0, lp1, b)
        assert np.all(np.isfinite(q)) and np.allclose(np.exp(q).sum(), 1.0)
        assert (lp0 - q).max() <= 2 * b + 1e-9


def test_codex_illustration():
    # Codex, additional_work_plan3.md §3: clipping is not scalar KL truncation.
    lp0 = np.log(np.array([[0.99, 0.005, 0.005]]))
    lp1 = np.log(np.array([[0.01, 0.495, 0.495]]))
    assert abs(B.kl(lp0, lp1)[0] - 4.5032) < 1e-3
    q = B.clip_tilt(lp0, lp1, 0.5)
    assert abs(B.kl(lp0, q)[0] - 0.00704) < 1e-4


def test_no_top_k_shortcut_changes_result():
    # renormalisation must be over the whole vocabulary: dropping tail tokens changes Z
    lp0, lp1 = random_pair(n=4000)
    q_full = B.clip_tilt(lp0, lp1, 1.0)
    k = 100
    top = np.argsort(-lp0, axis=-1)[:, :k]
    lp0_k = B.log_normalise(np.take_along_axis(lp0, top, -1))
    lp1_k = B.log_normalise(np.take_along_axis(lp1, top, -1))
    q_k = B.clip_tilt(lp0_k, lp1_k, 1.0)
    assert not np.allclose(np.take_along_axis(q_full, top, -1), q_k, atol=1e-6)


def test_rejects_bad_inputs():
    lp0, lp1 = random_pair(n=10)
    with pytest.raises(ValueError):
        B.clip_tilt(lp0, lp1, -1.0)
    with pytest.raises(ValueError):
        B.mixture(lp0, lp1, 1.5)
    with pytest.raises(FloatingPointError):
        B.clip_tilt(np.array([[np.nan, 0.0]]), np.array([[0.0, 0.0]]), 1.0)
