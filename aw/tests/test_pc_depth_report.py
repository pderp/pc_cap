import copy
import json

import numpy as np
import pytest

from aw import pc_depth_report as report
from aw import pc_v0_report as native


def fixture():
    reports = {}
    harms = {}
    for k in (1, 8, 32):
        cells = []
        arrays = {}
        summaries = {}
        for c in native.expected_cells(1):
            key = report.coord(c)
            cell = dict(
                c,
                status="complete",
                metrics={m: 0.5 for m in native.METRICS},
                secondary={m: 0.5 for m in native.SECONDARY},
                treatment=dict(credit_iters=k, error_lr=0.1),
                finish=dict(
                    elapsed_process_seconds=20,
                    ledger={
                        "learning": dict(
                            wall_seconds=10,
                            full_forwards=3,
                            partial_forwards=1,
                            reverses=2,
                            settle_iters=k,
                        )
                    },
                ),
            )
            if c["arm"] == "SE-E":
                cell["metrics"]["RET-ES"] += (k - 1) / 1000
            cells.append(cell)
            a = np.zeros((32, 127, 5))
            a[0, 0, 0] = 1 + (1e-4 if c["arm"] == "SE-E" else 0)
            arrays[key] = a
            summaries[key] = {
                "kl": {"mean_signed": 0},
                "loss": dict(mean_signed=0.1, es99_positive=1, maximum_signed=2),
            }
        reports[k] = {"cells": cells}
        harms[k] = (None, None, arrays, summaries)
    return reports, harms


def test_no_depth_or_order_pooling_and_exact_score_not_vector_equality():
    reports, harms = fixture()
    # Existing k=8 experiment has additional orders; these must not enter the common comparison.
    extra = copy.deepcopy(reports[8]["cells"][0])
    extra["order"] = 101
    extra["metrics"]["RET-ES"] = 100
    reports[8]["cells"].append(extra)
    summary, pairs, equality = report.summarize_common(reports, harms)
    assert len(summary) == 12 and len(pairs) == 18
    assert (
        next(r for r in summary if r["depth"] == 8 and r["arm"] == "SE-A")["metrics"]["RET-ES"]
        == 0.5
    )
    assert all(
        e["primary_secondary_exact"] and not e["harm_vectors_bitwise_equal"] for e in equality
    )
    assert all(e["maximum_absolute_vector_difference"] == pytest.approx(1e-4) for e in equality)
    reports[1]["cells"].pop()
    with pytest.raises(ValueError, match="exact common"):
        report.summarize_common(reports, harms)


def test_completed_actual_report_keeps_common_population_and_numerical_qualification():
    p = report.OUTPUT / "report.json"
    value = json.loads(p.read_bytes())
    assert len(value["pairs"]) == 18 and {p["order"] for p in value["pairs"]} == {100}
    assert {r["depth"] for r in value["summary"]} == {1, 8, 32}
    assert all(r["primary_secondary_exact"] for r in value["one_step_check"])
    assert any(not r["harm_vectors_bitwise_equal"] for r in value["one_step_check"])
