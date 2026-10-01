"""HT-17 statistical estimands, dependence, numerical models, and admission."""

import json

import numpy as np
import pytest
from scipy import integrate, stats

from aw import tail_class as t
from aw.tail_class_report import group_summary, matched_contrasts
from aw.tail_class_sources import load_delta, sha


@pytest.mark.parametrize("shape", [0.0, 0.6, -0.25])
def test_known_quantile_sample_recovers_shape_scale_and_exponential(shape):
    y = stats.genpareto.ppf((np.arange(6000) + 0.5) / 6000, shape, scale=2.3)
    fitted = t.fit_gpd(y)
    assert fitted["status"] == "eligible"
    assert fitted["optimizer"]["success"]
    assert fitted["shape"] == pytest.approx(shape, abs=0.012)
    assert fitted["scale"] == pytest.approx(2.3, abs=0.025)


@pytest.mark.parametrize("shape", [-0.2, -1e-8, 0, 1e-8, 0.7])
def test_likelihood_matches_scipy_with_window_multiplicities(shape):
    y = np.array([0.01, 0.4, 1, 3.0])
    w = np.array([3, 1, 2, 0])
    actual = t.gpd_nll([shape, np.log(2)], y, w)
    expected = -np.dot(w, stats.genpareto.logpdf(y, shape, loc=0, scale=2))
    assert actual == pytest.approx(expected, abs=1e-8)


@pytest.mark.parametrize("shape,reason", [(-0.7, "outside_manuscript_entropy_domain"),
                                         (-1.3, "endpoint_likelihood_boundary")])
def test_invalid_negative_shapes_are_not_published_estimates(shape, reason):
    y = stats.genpareto.ppf((np.arange(2000) + 0.5) / 2000, shape)
    fitted = t.fit_gpd(y)
    assert fitted["status"] == "invalid" and fitted["reason"] == reason
    assert fitted["shape"] is None and fitted["scale"] is None
    assert fitted["optimizer"]["shape"] < -0.5


def test_signed_population_strict_excess_and_sparse_screen():
    d = np.zeros((32, 127))
    d[0, :6] = [-4, -1e-12, 1e-12, 0.01, 0.02, 2]
    w, f = t.window_plan(32, 20)
    r, _ = t.analyze(d, weights=w, folds=f)
    assert r["negative_raw"] == 2 and r["benefit_beyond_noise_band"] == 1
    assert r["nonzero_in_noise_band"] == 2 and r["positive_raw"] == 4
    assert r["exact_zero"] == d.size - 6
    u = r["thresholds"]["0.01"]
    assert u["count"] == 2 and u["contributing_windows"] == 1
    assert u["conditional_mean_loss"] == pytest.approx(1.01)
    assert u["empty_bootstrap_draws"] > 0 and u["conditional_mean_interval"] is None
    assert u["fit"]["status"] == "not_identified"
    assert "exponential" not in u
    z, _ = t.analyze(np.zeros_like(d), weights=w, folds=f)
    assert z["thresholds"]["0.01"]["conditional_mean_loss"] is None
    assert z["thresholds"]["0.01"]["fraction"] == 0


def test_joint_bootstrap_copies_do_not_shrink_uncertainty_and_pair_to_zero():
    w, f = t.window_plan(80, 50)
    d = np.zeros((80, 127))
    d[:30, :4] = np.arange(1, 5)
    r, ws = t.analyze(d, weights=w, folds=f, bootstrap_fits=False)
    c = dict(id="a", windows=80, statistics=r, efficacy={"RET-GS": 0.8}, gate=None,
             realization=0, order=100, seed=None, population="same")
    one = group_summary([(c, ws)], w)
    duplicates = group_summary([(c, ws)] * 15, w)
    for u in map(str, t.THRESHOLDS):
        for key in ("frequency_interval", "conditional_mean_interval"):
            assert one["thresholds"][u][key] == pytest.approx(duplicates["thresholds"][u][key])
    groups = {("stage4", "zsre", "R1_learned_ff"): [(c, ws)],
              ("stage4", "zsre", "R1_nonlearned"): [(c, ws)]}
    contrast = matched_contrasts(groups, {"same": (w, f)})[0]
    assert contrast["thresholds"]["0.01"]["frequency"]["paired_window_interval"] == [0, 0]


def test_conditional_lognormal_density_integrates_to_one():
    model = dict(mu=0.8, sigma=0.7)
    u = 1.4
    value, _ = integrate.quad(lambda x: float(np.exp(t.lognormal_logpdf(x, u, model))),
                              u, np.inf)
    assert value == pytest.approx(1, abs=1e-8)


def test_cv_whole_window_holdout_and_zero_density_is_not_discarded(monkeypatch):
    ids = np.repeat(np.arange(100), 2)
    y = np.linspace(0.2, 1.0, len(ids))
    y[0] = 10.0
    _, folds = t.window_plan(100, 20)
    monkeypatch.setattr(t, "fit_gpd", lambda *a, **k: dict(status="eligible", shape=-0.25,
                                                         scale=0.3))
    result = t.cross_validate(y, ids, folds, 0.01)
    for row in result["folds"]:
        assert row["test"] == (folds[ids] == row["fold"]).sum()
        assert row["train"] + row["test"] == len(y)
    assert result["models"]["gpd"]["unsupported"] == 1
    assert result["models"]["gpd"]["log_likelihood"] is None
    assert result["gpd_minus_exponential_per_excess"] is None
    assert result["models"]["exponential"]["scored"] == len(y)


def test_bootstrap_invalid_draws_do_not_yield_success_conditioned_interval(monkeypatch):
    monkeypatch.setattr(t, "fit_gpd", lambda *a, **k: dict(status="invalid"))
    result = t.bootstrap_shape(np.array([1., 2., 3.]), np.array([0, 1, 2]),
                               np.ones((20, 3), int), dict(shape=0.2, scale=1.))
    assert result["invalid_draws"] == 20 and result["shape_interval"] is None


def test_vector_identity_finite_values_and_signed_difference(tmp_path):
    path = tmp_path / "vectors.npz"
    v = np.ones((2, 127, 5))
    v[0, 0, 0] = 0
    np.savez(path, values=v)
    c = dict(windows=2, vector=dict(path=str(path), sha256=sha(path)))
    d = load_delta(c, {})
    assert d[0, 0] == -1 and d[1, 0] == 0
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="hash changed"):
        load_delta(c, {})


def test_small_result_json_has_no_nan_or_infinity():
    w, f = t.window_plan(32, 20)
    result, _ = t.analyze(np.zeros((32, 127)), weights=w, folds=f)
    assert json.loads(json.dumps(result, allow_nan=False))["maximum"] == 0
