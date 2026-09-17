"""Accepted inference boundaries, complete populations, secondary cells/macros and TinyBase."""

from __future__ import annotations

import copy
import json
import uuid
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from scripts import r1_49g_inference as inf
from scripts import r1_49g_secondary as sec
from scripts import r1_75_analysis_stage4_v1 as old

ROOT = Path(__file__).resolve().parents[2]


def stats(g=0.05, e=0.0, l=0.0, gl=0.01, gu=0.10, el=-0.019, eu=0.01, ll=-0.009, lu=0.01):
    return {
        k: {
            "status": "complete",
            "estimate": v,
            "adjusted_interval": {"lower": lo, "upper": hi, "confidence": inf.ADJUSTED_CONFIDENCE},
        }
        for k, v, lo, hi in [("RET-GS", g, gl, gu), ("ES", e, el, eu), ("LS", l, ll, lu)]
    }


@pytest.mark.parametrize(
    "kwargs,verdict",
    [
        ({}, "positive"),
        ({"g": 0.049999}, "inconclusive"),
        ({"gl": 0}, "inconclusive"),
        ({"el": -0.02}, "qualified"),
        ({"ll": -0.01}, "qualified"),
        ({"gu": 0.04999}, "negative"),
        ({"gu": 0.05}, "positive"),
        ({"el": -0.03, "eu": -0.02001}, "negative"),
        ({"el": -0.03, "eu": -0.02, "e": -0.02}, "qualified"),
        ({"ll": -0.03, "lu": -0.01001}, "negative"),
        ({"ll": -0.03, "lu": -0.01, "l": -0.01}, "qualified"),
    ],
)
def test_exact_classifier_boundaries(kwargs, verdict):
    assert inf.classify(stats(**kwargs), admitted=True) == verdict


def test_negative_priority_and_missing_admission():
    # An inconsistent point/bound combination still follows the registered priority.
    assert inf.classify(stats(g=0.1, gu=0.049), admitted=True) == "negative"
    assert inf.classify(stats(), admitted=False) == "unavailable"
    assert inf.classify(stats(), admitted=True, complete=False) == "unavailable"
    m = stats()
    m["ES"]["adjusted_interval"]["confidence"] = 0.975
    assert inf.classify(m, admitted=True) == "unavailable"
    assert inf.fidelity(0.001, 0.01, complete=True)["passes"] is True
    assert inf.fidelity(0.001000001, 0.01, complete=True)["passes"] is False
    assert inf.fidelity(0.001, np.nan, complete=True)["status"] == "unavailable"


def test_bootstrap_matches_independent_enumeration_and_keeps_orders():
    grid = np.array([[0, 1, 2, 3, 4], [1, 2, 3, 4, 5], [2, 3, 4, 5, 6]], np.float64)
    value = inf.cluster_intervals(grid.tolist())
    np.testing.assert_equal(value["realization_estimates"], [2, 3, 4])
    samples = np.random.default_rng(0).integers(0, 3, size=(10000, 3))
    means = np.array([2.0, 3.0, 4.0])[samples].mean(axis=1)
    tail = 0.05 / (2 * 63)
    expected = np.quantile(means, [tail, 1 - tail], method="linear")
    np.testing.assert_equal([value["adjusted_interval"][k] for k in ("lower", "upper")], expected)
    assert value["estimate"] == 3
    grid = grid.tolist()
    grid[0][2] = None
    assert inf.cluster_intervals(grid)["estimate"] is None
    with pytest.raises(ValueError):
        inf.cluster_intervals([[0] * 15])


def synthetic_matrix():
    cells, loaded = [], {}
    conditions = ["R1_learned_ff", *inf.CONTROLS]
    for ds in inf.DATASETS:
        for r in range(3):
            pop = {
                "item_ids": [f"{ds}:r{r}:i{i}" for i in range(1000)],
                "paraphrase_counts": [1] * 1000,
                "endpoints": {
                    "locality": [f"{ds}:r{r}:l{i}" for i in range(50)],
                    "unseen": [f"{ds}:r{r}:u{i}" for i in range(100)],
                    "revision": [f"{ds}:r{r}:v{i}" for i in range(50)],
                },
            }
            for o in range(100, 105):
                for condition in conditions:
                    c = {
                        "condition": condition,
                        "dataset": ds,
                        "realization": r,
                        "order": o,
                        "checkpoints": [100, 300, 1000],
                        "population": pop,
                        "block_number": 1,
                        "within_block_order": len(cells) + 1,
                        "admitted": True,
                    }
                    c["cell_id"] = old.coordinate_id(c)
                    cells.append(c)
                    metrics = {
                        k: {
                            "status": "complete",
                            "planned": 50 if k == "LS" else 1000,
                            "scored": 50 if k == "LS" else 1000,
                            "value": (0.9 if condition == "R1_learned_ff" else 0.8)
                            if k == "RET-GS"
                            else 1.0,
                        }
                        for k in inf.METRICS
                    }
                    loaded[c["cell_id"]] = {
                        "scientific_admission": True,
                        "checkpoints": {"1000": {"primary": metrics}},
                    }
    matrix = {
        "name": "synthetic",
        "scope": "confirmatory",
        "cells": cells,
        "axes": {
            "datasets": list(inf.DATASETS),
            "conditions": conditions,
            "realizations": [0, 1, 2],
            "orders": list(range(100, 105)),
        },
        "contrasts": [
            {"id": f"primary-vs-{c}", "control": c, "treatment": "R1_learned_ff", "role": "primary"}
            for c in inf.CONTROLS
        ],
        "multiplicity": copy.deepcopy(inf.FAMILY),
    }
    return matrix, loaded


def test_family_63_complete_missing_and_overlap():
    matrix, loaded = synthetic_matrix()
    out = inf.primary_contrasts(matrix, loaded)
    assert len(out) == 21 and sum(r["interval_count"] for r in out) == 63
    assert all(r["classification"] == "positive" for r in out)
    missing = copy.deepcopy(loaded)
    missing.pop(matrix["cells"][0]["cell_id"])
    out = inf.primary_contrasts(matrix, missing)
    assert sum(r["classification"] == "unavailable" for r in out) == 7
    assert all(r["multiplicity"]["family_size"] == 63 for r in out)
    bad = copy.deepcopy(matrix)
    bad["contrasts"].pop()
    with pytest.raises(ValueError):
        inf.primary_contrasts(bad, loaded)
    bad = copy.deepcopy(matrix)
    for c in bad["cells"]:
        if c["dataset"] == "zsre" and c["realization"] == 1:
            c["population"]["item_ids"] = [f"zsre:r0:i{i}" for i in range(1000)]
    assert all(
        r["classification"] == "unavailable"
        for r in inf.primary_contrasts(bad, loaded)
        if r["dataset"] == "zsre"
    )


def secondary_fixture():
    matrix, loaded = synthetic_matrix()
    c = matrix["cells"][0]
    reports = {}
    for n in (100, 1000):
        reports[n] = {
            "observation": {"active_records_status": "ok", "active_records": n},
            "unseen": {
                "rows": [
                    {
                        "item_id": i,
                        "status": "ok",
                        "firing_status": "ok",
                        "false_fire": j < (10 if n == 100 else 15),
                    }
                    for j, i in enumerate(c["population"]["endpoints"]["unseen"])
                ]
            },
        }
    reports[1000]["endpoints"] = {
        "revision": {
            "rows": [
                {
                    "item_id": i,
                    "status": "ok",
                    "latest_answer_success": j < 48,
                    "old_record_retired": True,
                    "new_record_active": True,
                    "old_answer_acquired_before_revision": False,
                    "query_n": 2,
                    "old_answer_reappearance_n": int(j == 49),
                    "after_revision_queries": [
                        {"old_answer_reappeared": j == 49},
                        {"old_answer_reappeared": False},
                    ],
                }
                for j, i in enumerate(c["population"]["endpoints"]["revision"])
            ]
        }
    }
    l = loaded[c["cell_id"]]
    l["checkpoints"]["100"] = {"primary": copy.deepcopy(l["checkpoints"]["1000"]["primary"])}
    return matrix, loaded, c, l, reports


def test_secondary_denominators_boundary_and_semantics():
    _, _, c, l, reports = secondary_fixture()
    result = sec.cell_benchmarks(c, l, reports)["benchmarks"]
    assert result["unseen_1000"]["value"] == 0.15 and result["unseen_1000"]["passes"]
    assert (
        result["outside_change_1000_100"]["value"] == 0.05
        and result["outside_change_1000_100"]["passes"]
    )
    assert result["revision_latest"]["value"] == 48 / 50 and result["revision_latest"]["passes"]
    assert (
        result["old_alias_reappearance"]["value"] == 1 / 50
        and result["old_alias_reappearance"]["passes"]
    )
    assert (
        result["revision_semantic"]["value"] == 48 / 50
    )  # old acquisition is not an admitted condition
    assert result["wall_budget_ratio"]["status"] == "unavailable"
    for name in ("retention_change", "es_change", "ls_change"):
        assert sec.benchmark(name, sec.THRESHOLDS[name][1])["passes"]
    r = copy.deepcopy(reports)
    r[1000]["observation"]["active_records"] = 999
    assert sec.cell_benchmarks(c, l, r)["benchmarks"]["unseen_1000"]["status"] == "unavailable"
    r = copy.deepcopy(reports)
    r[1000]["endpoints"]["revision"]["rows"].pop()
    assert sec.cell_benchmarks(c, l, r)["benchmarks"]["revision_latest"]["status"] == "unavailable"
    r = copy.deepcopy(reports)
    r[1000]["endpoints"]["revision"]["rows"][0]["old_record_retired"] = None
    assert (
        sec.cell_benchmarks(c, l, r)["benchmarks"]["revision_semantic"]["status"] == "unavailable"
    )
    r = copy.deepcopy(reports)
    r.pop(1000)
    assert (
        sec.cell_benchmarks(c, l, r)["benchmarks"]["outside_change_1000_100"]["status"]
        == "unavailable"
    )
    resources = {
        "wall_budget_ratio": {"complete": True, "admitted": True, "measured": 10.0, "ceiling": 10.0}
    }
    assert sec.cell_benchmarks(c, l, reports, resources=resources)["benchmarks"][
        "wall_budget_ratio"
    ]["passes"]


def test_macros_keep_cell_failure_and_missingness():
    m, _, _, _, _ = secondary_fixture()
    cells = []
    for c in m["cells"]:
        values = {
            name: sec.benchmark(name, 0.0 if op != "ge" else 1.0)
            for name, (op, _) in sec.THRESHOLDS.items()
        }
        values["unseen_1000"] = sec.benchmark(
            "unseen_1000", 0.2 if c["order"] == 100 and c["realization"] == 0 else 0.0
        )
        cells.append({"cell_id": c["cell_id"], "benchmarks": values})
    macros = sec.macro_benchmarks(m, cells)
    row = next(x for x in macros if x["metric"] == "unseen_1000")
    assert row["passes"] and len(row["failed_cells"]) == 1
    assert row["realization_estimates"] == [0.04, 0.0, 0.0]
    cells[0]["benchmarks"]["unseen_1000"] = sec.benchmark("unseen_1000", None)
    assert (
        next(x for x in sec.macro_benchmarks(m, cells) if x["metric"] == "unseen_1000")["status"]
        == "unavailable"
    )


def test_tinybase_complete_cell_does_not_fill_1000_or_50_case_requirements():
    from scripts import r1_68c_dev_cell as driver

    from tests.revision_v1.test_r1_68c_driver import DriverTests
    from tests.revision_v1.test_r1_75_analysis import matrix, plan

    project = ROOT / "logs/r1_round20/synthetic_tests" / uuid.uuid4().hex
    real_root = driver.ROOT

    class IsolatedOutputRoot:
        # Test-only path routing keeps logs in this test project and payloads /
        # snapshots in the actual assets root. No production source is changed.
        parent = real_root.parent

        def __truediv__(self, relative):
            return (project if str(relative).startswith("results") else real_root) / relative

    with (
        patch.object(driver, "ROOT", IsolatedOutputRoot()),
        patch.object(driver, "OUTPUT_ROOT", project / "results/R1/stage4_dev_cells"),
        patch.object(old, "ROOT", project),
    ):
        case = DriverTests()
        case.setUp()
        try:
            fixture = case.fixture("incremental")
            result = case.run_cell(fixture)
            recipe = json.loads(fixture[0].read_text())
            payload = json.loads(Path(recipe["payload"]["path"]).read_text())
            c = {
                **recipe["cell"],
                "cell_id": old.coordinate_id(recipe["cell"]),
                "block_number": 1,
                "within_block_order": 1,
                "checkpoints": [1, 2],
                "result_dir": result["run_dir"],
                "manifest_sha256": driver.sha(fixture[0]),
                "population": plan(payload),
            }
            analyzed = old.analyze(matrix([c]))
            assert analyzed["cells"][0]["artifact_complete"]
            rows = sec.cell_benchmarks(c, analyzed["cells"][0], case.reports(result))["benchmarks"]
            assert all(v["status"] == "unavailable" for v in rows.values())
        finally:
            case.doCleanups()
