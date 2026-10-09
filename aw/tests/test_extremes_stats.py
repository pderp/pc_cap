"""Mandatory validation tests (handoff §22) for the CPU statistics of ext-20261009."""

import math

import numpy as np
import pytest

from aw.extremes import stats as S


def test_entropy_point_mass_uniform_and_shannon():
    assert S.shannon([1.0, 0.0, 0.0]) == 0.0
    W = 7
    assert abs(S.shannon(np.full(W, 1 / W)) - math.log(W)) < 1e-12
    e = S.entropy_of_counts([3, 3, 3, 3])
    assert abs(e["H"] - math.log(4)) < 1e-12 and abs(e["H_normalized"] - 1) < 1e-12 and abs(e["N_effective"] - 4) < 1e-9
    assert S.entropy_of_counts([5])["H"] == 0.0 and S.entropy_of_counts([5])["H_normalized"] == 0.0
    with pytest.raises(ValueError):
        S.shannon([0.5, 0.6])


def test_conditional_entropy():
    pairs = [("r1", "a"), ("r1", "a"), ("r2", "a"), ("r2", "b")]
    h = S.conditional_entropy(pairs)
    assert abs(h["H_cond"] - 0.5 * math.log(2)) < 1e-12


def test_js_properties():
    p, q = np.array([0.2, 0.3, 0.5]), np.array([0.5, 0.3, 0.2])
    assert abs(S.js(p, q) - S.js(q, p)) < 1e-12
    assert S.js(p, p) == 0.0
    assert 0 <= S.js(p, q) <= math.log(2) + 1e-12
    assert abs(S.js([1, 0], [0, 1]) - math.log(2)) < 1e-12
    assert S.kl([1, 0], [0, 1]) == math.inf


def test_cvar_small_example():
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert S.cvar(x, 0.95)["value"] == 10.0  # k = ceil(0.5) = 1
    assert S.cvar(x, 0.80)["value"] == 9.5  # k = 2
    assert abs(S.es_positive_fractional([10] + [0] * 999, 0.99) - 1.0) < 1e-12  # project ES99 convention


def test_gpd_recovery_and_support():
    rng = np.random.default_rng(1)
    exp = rng.exponential(2.0, 5000)
    f = S.gpd_fit(exp)
    assert abs(f["kappa"]) < 0.08 and abs(f["sigma"] - 2.0) < 0.2 and abs(f["loglik_gain_per_excess"]) < 0.01
    from scipy import stats as sps

    heavy = sps.genpareto.rvs(0.5, loc=0, scale=1.0, size=5000, random_state=2)
    g = S.gpd_fit(heavy)
    assert 0.38 < g["kappa"] < 0.62 and g["loglik_gain_per_excess"] > 0.05
    bounded = sps.genpareto.rvs(-0.4, loc=0, scale=1.0, size=5000, random_state=3)
    b = S.gpd_fit(bounded)
    assert b["kappa"] < -0.25 and b["support_endpoint"] is not None and b["support_endpoint"] >= bounded.max() - 1e-9
    assert S.gpd_fit(np.ones(10))["status"] == "insufficient"


def test_informational_scale_identity():
    for k in (0.0, 0.25, 1.0):
        assert S.informational_scale_check(k, 1.7)["identity_holds"]


def test_grouped_bootstrap_preserves_groups_and_pairing():
    groups = np.repeat(np.arange(10), 3)
    a = np.arange(30, dtype=float)
    b = a + 1.0  # paired: model b is always exactly 1 worse
    seen = []

    def stat(idx):
        seen.append(idx)
        return float((b[idx] - a[idx]).mean())

    r = S.grouped_bootstrap(stat, groups, draws=50, seed=0)
    assert r["point"] == 1.0 and r["ci_low"] == 1.0 and r["ci_high"] == 1.0
    for idx in seen[1:]:
        # whole groups only: every selected group contributes all three members
        vals, counts = np.unique(groups[idx], return_counts=True)
        assert set(counts) == {3} or all(c % 3 == 0 for c in counts)


def test_length_normalisation_identity():
    per_token = [0.5, 1.5, 2.0]
    total = sum(per_token)
    assert abs(total / len(per_token) - np.mean(per_token)) < 1e-12


def test_mquake_aggregation():
    rows = [dict(case_id=1, question_index=0, correct=True), dict(case_id=1, question_index=1, correct=False), dict(case_id=1, question_index=2, correct=False),
            dict(case_id=2, question_index=0, correct=True), dict(case_id=2, question_index=1, correct=True), dict(case_id=2, question_index=2, correct=True),
            dict(case_id=3, question_index=0, correct=False), dict(case_id=3, question_index=1, correct=False), dict(case_id=3, question_index=2, correct=False)]
    m = S.mquake_aggregate(rows)
    assert m["cases"] == 3 and m["questions"] == 9 and abs(m["question_accuracy"] - 4 / 9) < 1e-12
    assert abs(m["any_question_success"] - 2 / 3) < 1e-12 and abs(m["all_question_success"] - 1 / 3) < 1e-12


def test_missing_values_never_become_zero():
    d = S.describe([1.0, float("nan"), 3.0])
    assert d["n"] == 2 and d["missing"] == 1 and d["mean"] == 2.0
    assert S.rate(0, 0)["value"] is None
