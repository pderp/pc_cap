"""S1-04 (P4 on the grammar): basis/overlap arithmetic and the settled-error sampler's contract."""

import numpy as np
import pytest

from pccap.analysis import s1_p4


def test_basis_rank_and_overlap():
    rng = np.random.default_rng(0)
    U = np.linalg.qr(rng.standard_normal((32, 4)))[0]
    X = rng.standard_normal((500, 4)) @ U.T  # exact rank 4
    b = s1_p4.basis(X, r=16)
    assert b["insufficient_rank"] and b["r"] == 4 and b["captured_variance"] == pytest.approx(1.0)
    assert s1_p4.overlap(b["basis"], U) == pytest.approx(1.0, abs=1e-6)
    V = np.linalg.qr(rng.standard_normal((32, 8)))[0]
    V = V - U @ (U.T @ V)  # orthogonal complement directions
    V = np.linalg.qr(V)[0]
    assert s1_p4.overlap(b["basis"], V) == pytest.approx(0.0, abs=1e-6)
    full = s1_p4.basis(rng.standard_normal((300, 32)), r=16)
    assert full["r"] == 16 and not full["insufficient_rank"] and 0 < full["captured_variance"] < 1
    assert len(full["eigen_gaps"]) == 16 and all(g >= -1e-12 for g in full["eigen_gaps"])


@pytest.mark.slow
def test_error_sampler_shapes_and_determinism():
    from pccap.fixtures.grammar_generator import Grammar, Switches
    from pccap.fixtures.grammar_model import CFG, WEIGHTS, GrammarBase

    base = GrammarBase(weights=WEIGHTS)
    sampler = s1_p4.ErrorSampler(base, batch=4)
    ids, pos, tgt = s1_p4._batch(Grammar(), "private", [0, 1], np.arange(4), Switches.task)
    E, R = sampler.sample(ids, pos, tgt)
    assert E.shape == (4, CFG.n_layer, CFG.d) and R.shape == E.shape
    assert np.isfinite(E).all() and np.abs(E).sum() > 0
    E2, _ = sampler.sample(ids, pos, tgt)
    assert np.array_equal(E, E2)
