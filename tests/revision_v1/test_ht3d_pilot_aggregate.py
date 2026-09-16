"""CPU-only checks for registered aggregation, missingness and direction."""

import copy
import math

import pytest
from scripts import ht3d_pilot_aggregate as a


def rows():
    return [
        dict(
            arm=arm,
            seed=seed,
            dataset=ds,
            run=f"{arm}-{seed}",
            status="complete",
            issues=[],
            ret_gs=0.8,
            ls_complete_answer=1.0,
            unseen_rate=0.1,
            es95=1.0,
            maximum=2.0,
            tail_population="tail",
            unseen_population="outside",
            retention_population="retention",
        )
        for arm in a.ARMS
        for seed in a.SEEDS
        for ds in a.DATASETS
    ]


def check(data, failures=(), source_errors=()):
    return a.comparisons(a.summarize(data), data, failures, source_errors)


def test_fractional_boundary_zeros_and_negative_harm():
    assert a.positive_tail([10, 6] + [0] * 23, [0] * 25) == {"es95": 9.2, "maximum": 10}
    assert a.positive_tail([1, 2], [2, 3]) == {"es95": 0.0, "maximum": 0.0}
    assert a.positive_tail([3], [0]) == pytest.approx({"es95": 3.0, "maximum": 3.0})


@pytest.mark.parametrize("on,off", [([], []), ([1], [1, 2]), ([math.nan], [0]), ([0], [math.inf])])
def test_invalid_tail_cannot_enter_averages(on, off):
    with pytest.raises(ValueError):
        a.positive_tail(on, off)


def test_strict_spread_boundary_and_signed_direction():
    t = a.separation([1, 2, 3], [0, 1, 2])
    assert t["signed_difference"] == 1 and t["seed_spread_threshold"] == 2
    assert not t["separated"]
    assert not a.separation([2, 3, 4], [0, 1, 2])["separated"]
    t = a.separation([3, 4, 5], [0, 1, 2])
    assert t["separated"] and not t["separated_decrease"]


def test_macro_weighting_and_no_seed_or_dataset_drop():
    data = rows()
    data[0]["ret_gs"] = 0.5
    assert a.summarize(data)["ordinary"]["ret_gs"]["mean"] == pytest.approx((8 * 0.8 + 0.5) / 9)
    data[0]["ret_gs"] = None
    s = a.summarize(data)["ordinary"]["ret_gs"]
    assert s["seed_macros"][0] is None and s["mean"] is None


def test_decrease_passes_and_increase_is_not_improvement():
    data = rows()
    for r in data:
        if r["arm"] == "kappa02":
            r["es95"] = 0.5
        if r["arm"] == "kappa05":
            r["es95"] = 1.5
    out = check(data)
    assert out["kappa02"]["verdict"] == "declared secondary condition"
    assert out["kappa02"]["robustness_improvement_eligible"]
    assert out["kappa05"]["verdict"] == "declared secondary condition"
    assert not out["kappa05"]["robustness_improvement_eligible"]


def test_retention_and_each_dataset_unseen_are_independent_gates():
    data = rows()
    for r in data:
        if r["arm"] == "kappa02":
            r["es95"] = 0.5
            r["ret_gs"] = 0.77
        if r["arm"] == "kappa05":
            r["es95"] = 0.5
            r["unseen_rate"] = 0.11 if r["dataset"] == "zsre" else 0.0
    out = check(data)
    assert out["kappa02"]["verdict"] == out["kappa05"]["verdict"] == "null result"
    assert not out["kappa02"]["retention_pass"]
    assert not out["kappa05"]["unseen_by_dataset"]["zsre"]["nonincrease"]


@pytest.mark.parametrize("reason", ["missing", "population", "failure", "source"])
def test_unavailable_is_not_null_or_secondary(reason):
    data = rows()
    failures, sources = [], []
    if reason == "missing":
        data[0]["status"] = "unavailable"
    elif reason == "population":
        data[0]["tail_population"] = "different"
    elif reason == "failure":
        failures = [{"arm": "ordinary", "run": "failed", "charged_wall_seconds": 123}]
    else:
        sources = ["changed during read"]
    assert check(data, failures, sources)["kappa02"]["verdict"] == "unavailable"


def test_incomplete_control_does_not_hide_candidate_but_is_unavailable():
    data = rows()
    for r in data:
        if r["arm"] == "clip2":
            r["status"] = "unavailable"
            r["es95"] = None
    out = check(data)
    assert out["clip2"]["verdict"] == "unavailable"
    assert out["kappa02"]["verdict"] == "null result"


def test_extract_rejects_partial_nonfinite_and_wrong_shape():
    obj = {
        "windows": 32,
        "positions_per_window": 127,
        "rule": "0.5:none",
        "policy": "fixed",
        "nll_cap_on": [[0.0] * 127] * 32,
        "nll_cap_off": [[0.0] * 127] * 32,
    }

    class Fake:
        def read(self, path):
            if path.endswith(".positions.json"):
                return copy.deepcopy(obj)
            raise FileNotFoundError(path)

    row = a.extract_row(Fake(), "ordinary", 0, "zsre")
    assert row["status"] == "unavailable" and row["es95"] is None
    obj["nll_cap_on"] = [[math.nan] * 127] * 32
    row = a.extract_row(Fake(), "ordinary", 0, "zsre")
    assert row["es95"] is None and any("nonfinite" in x for x in row["issues"])
    obj["nll_cap_on"] = [[0.0] * 126] * 32
    assert a.extract_row(Fake(), "ordinary", 0, "zsre")["es95"] is None


def test_snapshot_read_tracks_changes(tmp_path):
    path = tmp_path / "data.json"
    path.write_text('{"v": 1}')
    inputs = a.Inputs(tmp_path)
    assert inputs.read("data.json") == {"v": 1}
    assert inputs.unchanged() == []
    path.write_text('{"v": 2}')
    assert inputs.unchanged() == ["data.json"]
