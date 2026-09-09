"""Independent numerical and protocol controls from PDF S0, D.2–D.9, E.2."""

import json

import numpy as np
import pytest

from pccap.metrics import (
    acc,
    active_fraction,
    bwt,
    damage,
    effective_rank,
    exact_match_aliases,
    forgetting,
    fwt,
    js,
    kl,
    late_acquisition_gain,
    normalize_answer,
    order_divergence,
    pr,
    scalar_quadratic_reversal,
    subspace_overlap,
    summarize,
)


def test_rank_uniform_unequal_zero_and_centering():
    uniform = np.vstack([np.eye(3), -np.eye(3)])
    assert effective_rank(uniform)["value"] == pytest.approx(3)
    unequal = uniform @ np.diag([4, 2, 1])
    assert 1 < effective_rank(unequal)["value"] < np.linalg.matrix_rank(unequal)
    assert effective_rank(uniform + 9)["value"] == pytest.approx(3)
    zero = effective_rank(np.ones((8, 3)))
    assert zero["value"] is None and zero["status"] == "undefined"
    assert zero["strata"]["effective_rank"] == 0
    assert zero["numerator"] == zero["denominator"] == 0


def test_participation_known_mass_and_extreme_scale():
    assert pr(np.ones((3, 4)))["value"] == 12
    assert pr([1, 0, 0])["value"] == 1
    assert pr([1, 1, 0], normalized=True)["value"] == pytest.approx(2 / 3)
    assert pr([1e300, 1e300])["value"] == 2
    assert pr([1e-300, 1e-300])["value"] == 2
    assert pr(np.zeros(8))["status"] == "undefined"
    assert active_fraction([1, 0.01, 0.011, 0])["value"] == 0.5
    assert active_fraction([0, 0])["status"] == "undefined"


def test_overlap_geometry_and_invalid_basis():
    a = np.eye(4)[:, :2]
    b = np.eye(4)[:, 2:]
    assert subspace_overlap(a, a)["value"] == 1
    assert subspace_overlap(a, b)["value"] == 0
    assert subspace_overlap(a, np.column_stack([a[:, 0], b[:, 0]]))["value"] == 0.5
    assert subspace_overlap(np.empty((4, 0)), np.empty((4, 0)))["status"] == "unsupported"
    with pytest.raises(ValueError, match="orthonormal"):
        subspace_overlap(2 * a, a)


def test_kl_direction_zeros_and_js_bounds():
    assert kl([0.5, 0.5], [0.25, 0.75])["value"] == pytest.approx(0.5 * np.log(4 / 3))
    assert kl([0, 1], [0, 1])["value"] == 0
    missing = kl([1, 0], [0, 1])
    assert missing["status"] == "unreachable" and missing["value"] is None
    assert missing["strata"]["right_unbounded"]
    assert js([1, 0], [0, 1])["value"] == pytest.approx(np.log(2))
    assert js([0.3, 0.7], [0.3, 0.7])["value"] == 0
    p = np.array([[0.5, 0.5], [1, 0]])
    q = np.array([[0.5, 0.5], [0.5, 0.5]])
    assert kl(p, q)["value"] == pytest.approx(np.log(2) / 2)
    assert js(p, q)["value"] == js(q, p)["value"]
    assert 0 <= js(p, q)["value"] <= np.log(2)


@pytest.fixture
def table():
    # Rows: base, post-task 1, post-task 2, post-task 3.
    return np.array([[0.1, 0.2, 0.3], [0.8, 0.3, 0.4], [0.9, 0.7, 0.5], [0.6, 0.8, 0.9]])


def test_accuracy_matrix_hand_computed(table):
    assert acc(table)["value"] == pytest.approx(2.3 / 3)
    assert bwt(table)["value"] == pytest.approx(-0.05)
    assert fwt(table)["value"] == pytest.approx(0.15)
    # First task peaks after task 2; last task is excluded from forgetting.
    assert forgetting(table)["value"] == pytest.approx(0.15)
    assert late_acquisition_gain(table, task_indices=[2])["value"] == pytest.approx(0.4)
    assert late_acquisition_gain(table)["value"] == pytest.approx(0.5)
    assert summarize(table)["BWT"] == bwt(table)
    assert bwt([[0.1], [0.7]])["status"] == "undefined"
    assert fwt([[0.1], [0.7]])["status"] == "undefined"
    assert forgetting([[0.1], [0.7]])["status"] == "undefined"


@pytest.mark.parametrize("theta", [-2.0, 0.0, 0.7, 3.0])
@pytest.mark.parametrize("eta", [0.0, 0.01, 0.1, 0.5])
def test_scalar_gradient_bracket_not_hessian_commutator(theta, eta):
    result = scalar_quadratic_reversal(theta, eta)
    assert result["value"] == pytest.approx(eta**2, abs=1e-12)
    assert result["strata"]["hessian_commutator"] == 0


def test_fixed_prefix_order_js_and_signed_damage():
    p = np.array([[[1.0, 0.0]], [[0.0, 1.0]], [[1.0, 0.0]]])
    assert order_divergence(p)["value"] == pytest.approx(2 * np.log(2) / 3)
    assert order_divergence(p[:1])["status"] == "undefined"
    assert damage([1.0, 2.0], [2.0, 4.0])["value"] == 1.5
    assert damage([1.0, 2.0], [0.5, 1.0])["value"] == -0.75


def test_complete_answer_unicode_delimiter_and_truncation():
    assert normalize_answer("  Ｎｅｗ\tStraße  ") == "new strasse"
    assert exact_match_aliases("New York\nignored", ["new york"])["value"] == 1
    assert exact_match_aliases("New Jersey", ["New York"])["value"] == 0
    assert exact_match_aliases("New", ["New York"], truncated=True)["value"] == 0
    assert exact_match_aliases("New York", ["New York"], truncated=True)["value"] == 1
    assert exact_match_aliases("The answer is New York", ["New York"])["value"] == 0
    assert exact_match_aliases("Paris!", ["Paris"])["value"] == 0
    with pytest.raises(ValueError):
        exact_match_aliases("", [])
    with pytest.raises(TypeError):
        exact_match_aliases("Paris", "Paris")


@pytest.mark.parametrize(
    "fn,args",
    [
        (effective_rank, ([[np.nan]],)),
        (pr, ([-1, 2],)),
        (pr, ([],)),
        (active_fraction, ([np.inf],)),
        (kl, ([0.2, 0.2], [0.5, 0.5])),
        (js, ([np.nan, 1], [0.5, 0.5])),
        (acc, ([[0.1, 0.2]],)),
        (bwt, ([[0.1], [np.nan]],)),
        (damage, ([1], [2, 3])),
    ],
)
def test_invalid_inputs_are_errors_not_silent_fallbacks(fn, args):
    with pytest.raises(ValueError):
        fn(*args)


def test_all_metrics_have_operands_and_are_strict_json(table):
    results = [
        effective_rank(np.eye(3)),
        effective_rank(np.zeros((2, 2))),
        pr([0]),
        pr([1, 2]),
        active_fraction([1, 0]),
        subspace_overlap(np.eye(2), np.eye(2)),
        kl([1, 0], [0, 1]),
        js([1, 0], [0, 1]),
        scalar_quadratic_reversal(),
        exact_match_aliases("New York", ["New Jersey"]),
        *summarize(table).values(),
    ]
    fields = {"value", "status", "units", "numerator", "denominator", "n", "strata", "exclusions"}
    for result in results:
        assert set(result) == fields
        assert result["status"] == "ok" or result["value"] is None
    json.dumps(results, allow_nan=False)
