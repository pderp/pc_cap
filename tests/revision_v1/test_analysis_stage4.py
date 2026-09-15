"""Independent inventory accounting and secondary endpoint denominator tests."""

import copy

import pytest

from pccap.revision_v1.analysis_stage4 import (
    analyze_stage4,
    development_dry_run,
    endpoint_summary,
    expected_inventory,
    summarize_checkpoint,
    validate,
)
from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS, SECONDARY_CONDITION


def test_full_three_dataset_inventory_and_v2_separate():
    inv = expected_inventory()
    assert len(inv["cells"]) == 360 and len(inv["secondary_cells"]) == 45
    assert inv["axes"]["datasets"] == ["zsre", "counterfact", "mquake"]
    assert all(c["checkpoints"] == [100, 300, 1000] for c in inv["cells"])
    assert all(c["condition"] != SECONDARY_CONDITION for c in inv["cells"])
    assert inv["contrasts"][-1]["role"] == "declared_secondary"


def test_missing_controls_never_shrink_expected_inventory():
    result = analyze_stage4(expected_inventory())
    assert result["banner"].startswith("NOT CONFIRMATORY")
    for name in (*CORE_CONDITIONS, SECONDARY_CONDITION):
        row = result["missing_by_condition"][name]
        assert row["planned"] == row["missing"] == 45
        assert row["missing_checkpoints"] == 135 and row["artifact_complete"] == 0
    assert len(result["comparisons"]) == 3 * 8 * 3
    comp = next(c for c in result["comparisons"] if c["contrast"]["id"] == "v3_minus_v2")
    assert comp["classification"] == "secondary_descriptive"
    assert comp["metrics"]["RET-GS"]["observed_pairs"] == 0
    assert comp["metrics"]["RET-GS"]["estimate"] is None


@pytest.mark.parametrize("kind", ["omit", "duplicate", "dataset", "v2", "contrast"])
def test_axis_or_cell_pruning_is_refused(kind):
    inv = expected_inventory()
    if kind == "omit":
        inv["cells"].pop()
    elif kind == "duplicate":
        inv["cells"][1] = inv["cells"][0]
    elif kind == "dataset":
        inv["axes"]["datasets"].pop()
    elif kind == "v2":
        inv["secondary_cells"].pop()
    else:
        inv["contrasts"].pop()
    with pytest.raises(ValueError):
        validate(inv)


def test_unseen_missing_observer_stays_unavailable():
    rows = [
        {"item_id": "a", "status": "ok", "false_fire": None, "firing_status": "unavailable"},
        {"item_id": "b", "status": "ok", "false_fire": False, "firing_status": "ok"},
    ]
    result = endpoint_summary(rows, ["a", "b", "c"], "false_fire", firing=True)
    assert result["planned"] == 3 and result["scored"] == 1
    assert result["value"] is None and result["evaluated_value"] == 0
    assert result["status_counts"] == {"firing_unavailable": 1, "ok": 1, "missing": 1}


def test_composition_conflict_and_failure_both_in_planned_denominator():
    rows = [
        {"composition_id": "a", "status": "ok", "evaluable": True, "composition_success": False},
        {"composition_id": "b", "status": "unavailable", "evaluable": False},
    ]
    out = endpoint_summary(rows, ["a", "b", "c"], "composition_success", id_key="composition_id")
    assert out["planned"] == 3 and out["evaluable"] == 1 and out["scored"] == 1
    assert out["value"] is None and out["evaluated_value"] == 0
    assert (
        endpoint_summary([], [], "composition_success", id_key="composition_id")["status"]
        == "not_applicable"
    )


def population():
    ids = [f"i{i}" for i in range(1000)]
    return {
        "dataset": "mquake",
        "realization": 0,
        "order": 0,
        "item_ids": ids,
        "paraphrase_counts": [2] * 1000,
        "endpoints": {
            "locality": ["loc"],
            "unseen": ["out"],
            "near_miss": ["near"],
            "revision": ["rev"],
            "composition": ["comp"],
        },
    }


def report(n=100):
    rows = [
        {"item_id": f"i{i}", "status": "ok", "es": 1.0, "gs": 0.5, "paraphrase_n": 2}
        for i in range(n)
    ]
    return {
        "history": copy.deepcopy(rows),
        "retention": {"rows": rows},
        "locality": {"rows": [{"item_id": "loc", "status": "ok", "preserved": True}]},
        "unseen": {
            "rows": [
                {
                    "item_id": "out",
                    "status": "ok",
                    "false_fire": False,
                    "firing_status": "ok",
                    "answer_changed": False,
                }
            ]
        },
    }


def test_checkpoint_aggregates_all_items_and_keeps_secondary_descriptive():
    out = summarize_checkpoint(report(), population(), 100)
    assert out["primary"]["RET-GS"]["value"] == 0.5 and out["primary"]["RET-GS"]["planned"] == 100
    assert out["secondary"]["unseen_false_fire"]["value"] == 0
    assert "composition" not in out["secondary"]
    assert "descriptive" in out["secondary"]["unseen_false_fire"]["interpretation"]
    out = summarize_checkpoint(report(1000), population(), 1000)
    assert out["secondary"]["composition"]["planned"] == 1
    assert out["secondary"]["composition"]["value"] is None


def test_paraphrase_denominator_or_reordered_results_refused():
    p = population()
    r = report()
    r["retention"]["rows"][0]["paraphrase_n"] = 1
    with pytest.raises(ValueError, match="paraphrase"):
        summarize_checkpoint(r, p, 100)
    r = report()
    r["history"].reverse()
    with pytest.raises(ValueError, match="order"):
        summarize_checkpoint(r, p, 100)


def test_realizations_cannot_reuse_same_item_population():
    inv = expected_inventory()
    p = population()
    inv["populations"] = [p, {**copy.deepcopy(p), "realization": 1}]
    with pytest.raises(ValueError, match="disjoint"):
        validate(inv)


def test_development_wrapper_refuses_confirmatory_relabeling():
    with pytest.raises(ValueError, match="development"):
        development_dry_run({"scope": "confirmatory"})
