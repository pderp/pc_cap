"""Exact Gram/block identities and limiting loop sign (PDF D.9)."""

import json

import numpy as np
import pytest

from pccap.metrics.hvp import (
    block_accounting,
    commutator,
    commutator_gram,
    control_fixture,
    linearized_loop,
    run_controls,
)


def test_gram_sign_is_psd_not_negative_semidefinite():
    hi, hj, hk, _ = control_fixture()
    cs = [commutator(hi, hj), commutator(hi, hk), commutator(hj, hk)]
    for c in cs:
        np.testing.assert_array_equal(c.T, -c)
    gram = commutator_gram(cs)
    for i, a in enumerate(cs):
        for j, b in enumerate(cs):
            assert gram[i, j] == np.trace(a.T @ b) == -np.trace(a @ b)
    assert np.linalg.eigvalsh(gram).min() >= 0
    assert np.trace(gram) > 0
    assert np.linalg.eigvalsh(-gram).min() < 0


def test_full_block_accounting_requires_cross_terms():
    hi, hj, _, projectors = control_fixture()
    c = commutator(hi, hj)
    result = block_accounting(c, projectors)
    assert result["full_squared_frobenius"]["value"] == 20  # hand-calculated C entries
    assert result["sum_block_squared_frobenius"]["value"] == 20
    assert result["block_squared_frobenius"] == [[2, 8], [8, 2]]
    assert result["cross_block_squared_frobenius"] == 16
    # Restricted per-bank Hessian commutators alone lose 16/20 of the mass here.
    local = [commutator(p @ hi @ p, p @ hj @ p) for p in projectors]
    assert sum(float(np.sum(c**2)) for c in local) == 4


def test_loop_has_negative_sign_and_cubic_remainder():
    hi, hj, _, _ = control_fixture()
    c = commutator(hi, hj)
    errors = []
    for eta in (0.001, 0.0005):
        loop = linearized_loop(hi, hj, eta)
        right = np.eye(4) - eta**2 * c
        wrong = np.eye(4) + eta**2 * c
        errors.append(np.linalg.norm(loop - right))
        assert errors[-1] < np.linalg.norm(loop - wrong) / 100
    assert 7.5 < errors[0] / errors[1] < 8.5
    np.testing.assert_array_equal(linearized_loop(hi, hj, 0), np.eye(4))


def test_commuting_quadratics_do_not_fake_nonzero_commutator():
    a = np.diag([1.0, 2.0, 3.0, 4.0])
    b = np.diag([4.0, 3.0, 2.0, 1.0])
    np.testing.assert_array_equal(commutator(a, b), np.zeros((4, 4)))
    np.testing.assert_allclose(linearized_loop(a, b, 0.01), np.eye(4), atol=1e-15)
    # Scalar shifted minima need the separate actual-update control S0-07.
    from pccap.metrics.order import scalar_quadratic_reversal

    assert scalar_quadratic_reversal(0, 0.1)["value"] == pytest.approx(0.01)


def test_controls_fail_explicitly_for_invalid_topology_or_singular_map():
    hi, hj, _, p = control_fixture()
    with pytest.raises(ValueError, match="entire parameter"):
        block_accounting(commutator(hi, hj), p[:1])
    with pytest.raises(ValueError, match="mutually orthogonal"):
        block_accounting(commutator(hi, hj), [p[0], p[0]])
    with pytest.raises(ValueError, match="idempotent"):
        block_accounting(hi, [0.5 * np.eye(4)])
    with pytest.raises(ValueError, match="invertible"):
        linearized_loop(np.eye(4), hj, 1)
    with pytest.raises(ValueError, match="symmetric"):
        commutator(np.triu(hj), hi)
    with pytest.raises(ValueError, match="square"):
        commutator([[np.nan]], [[1]])


def test_saved_control_report_is_strict_json_and_all_controls_pass():
    report = run_controls()
    assert report["passed"] and all(report["checks"].values())
    json.dumps(report, allow_nan=False)
