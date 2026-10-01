"""Actual finished/partial evidence must keep the registered populations distinct."""

import json

import pytest

from aw import pc_credit_control_review as c
from aw.pc_depth_report import OUTPUT
from aw.pc_historical import ROOT, Sources
from aw.presentation_followup import values


def test_control_partial_count_common_prefix_and_offered_budget():
    evidence = Sources()
    r = c.build(evidence)
    assert r["unstarted_cells"] == 10
    assert r["random"][1]["status"] == "resource_stop"
    assert r["common_prefix_es"][1] == 3 / 993
    assert r["common_prefix_es"][0] > 0.99
    assert len(r["matched"]["pairs"]) == 6
    budgets = [x["budget"] for x in r["matched"]["cells"] if "budget" in x]
    assert all(x["used"] < x["offered"] for x in budgets)
    assert "unresolved" in c.render(r)
    evidence.verify_unchanged()


def test_followup_slots_keep_dataset_kl_and_partial_control_qualifications():
    slots = {}
    report = json.loads(
        (ROOT / "logs/additional_work/AW-B/report-20260929/report.json").read_bytes()
    )
    assert values("aw_b", report, slots, {}).startswith("measured")
    assert slots["awb.counterfact.gs_change"].startswith("-0.01167")
    assert float(slots["awb.counterfact.mixture.kl"].split("–")[0]) > 0.001
    assert float(slots["awb.zsre.mixture.kl"].split("–")[1]) < 0.001
    report["status"] = "incomplete"
    with pytest.raises(ValueError, match="completed"):
        values("aw_b", report, {}, {})
    depth = json.loads((OUTPUT / "report.json").read_bytes())
    assert "partial" in values("depth_controls", depth, slots, {})
    assert slots["control.random.n"] == "993"
