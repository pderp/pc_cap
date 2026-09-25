"""Acceptance checks on the real, read-only three-realization report."""

import json
import math
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "logs/R1/reports/triplet"


@pytest.fixture(scope="module")
def report():
    return json.loads((OUT / "analysis.json").read_text())


def test_complete_triplet_and_no_later_results_enter_snapshot(report):
    assert len(report["cells"]) == 330
    assert report["complete_blocks"] == [1, 2, 3]
    included = [c for c in report["cells"] if c["artifact_complete"]]
    assert len(included) == 135
    assert {c["block_number"] for c in included} == {1, 2, 3}
    assert {c["cell_id"] for c in included} == set(report["snapshot_scope"]["included_cell_ids"])
    assert all(not c["checkpoints"] for c in report["cells"] if c["block_number"] > 3)


def test_registered_family_and_three_cluster_uncertainty(report):
    assert sum(len(c["metrics"]) for c in report["contrasts"]) == 63
    complete = 0
    for c in report["contrasts"]:
        for v in c["metrics"].values():
            if v["estimate"] is None:
                assert v["adjusted_interval"] is None
                continue
            complete += 1
            assert c["dataset"] != "mquake"
            rows = v["preliminary"]["order_dispersion"]
            assert len(rows) == 3 and all(len(r["order_values"]) == 5 for r in rows)
            means = np.array([np.mean(r["order_values"]) for r in rows])
            np.testing.assert_allclose(means, v["realization_estimates"], rtol=0, atol=1e-14)
            assert v["estimate"] == pytest.approx(float(means.mean()), abs=1e-14)
            interval = v["adjusted_interval"]
            assert interval["lower"] == pytest.approx(float(min(means)), abs=1e-14)
            assert interval["upper"] == pytest.approx(float(max(means)), abs=1e-14)
            t = v["preliminary"]["t_sensitivity"]
            delta = 4.302652729696142 * np.std(means, ddof=1) / math.sqrt(3)
            assert t["lower"] == pytest.approx(float(means.mean() - delta), abs=1e-14)
            assert t["upper"] == pytest.approx(float(means.mean() + delta), abs=1e-14)
            assert not t["family_adjusted"]
    assert complete == 12
    assert sum(c["classification"] == "positive" for c in report["contrasts"]) == 3
    assert sum(c["classification"] == "inconclusive" for c in report["contrasts"]) == 1


def test_recurrence_and_adverse_outcomes_are_not_hidden():
    groups = json.loads((OUT / "summary.json").read_text())["groups"]
    learned = [g for g in groups if g["condition"] == "R1_learned_ff"]
    assert len(learned) == 9 and sum(g["cap_benchmark_passes"] for g in learned) == 0
    assert all(min(g["fidelity"]["original"]["mean_kl"]) > 0.001 for g in learned)
    zsre = sorted([g for g in learned if g["dataset"] == "zsre"], key=lambda g: g["realization"])
    assert [g["near_miss"] for g in zsre] == [[x] * 5 for x in (.86, .92, .87)]
    cf2 = next(g for g in learned if g["dataset"] == "counterfact" and g["realization"] == 2)
    assert cf2["primary"]["LS"] == [.96] * 5


def test_process_cost_and_watch_scopes_are_complete():
    c = json.loads((OUT / "accounting.json").read_text())
    assert len(c["rows"]) == 135 and c["unknown_costs"] == c["failures"] == c["retries"] == 0
    assert sum(r["charged_process_seconds"] for r in c["rows"]) / 3600 == pytest.approx(c["process_hours"])
    assert all(r["uncovered_driver_seconds"] == 0 for r in c["rows"])
    assert len(c["missing_parent_decisions"]) == 2
    appendix = json.loads((OUT / "appendix/report-data.json").read_text())
    assert appendix["watch"]["queue_observations"] == 135
    assert not appendix["watch"]["admission_veto"]
