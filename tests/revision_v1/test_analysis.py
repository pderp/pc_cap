"""Synthetic, inventory-first tests for revision analysis (CPU, no model)."""

import json

import pytest

from pccap.revision_v1.analysis import analyze, classify, paired_metric, validate_inventory


def fixture(root, gain=0.1, orders=(10, 11), change=None):
    inv = {
        "schema_version": 1,
        "scope": "synthetic",
        "axes": {
            "datasets": ["d"],
            "conditions": ["learned_new", "stable_control"],
            "realizations": [0, 1, 2],
            "orders": list(orders),
        },
        "populations": [],
        "cells": [],
        "contrasts": [
            {"id": "new_minus_stable", "treatment": "learned_new", "control": "stable_control"}
        ],
        "bootstrap": {"seed": 17, "draws": 1000, "confidence": 0.975},
    }
    for r in (0, 1, 2):
        for order in orders:
            ids = [f"r{r}-a", f"r{r}-b"]
            if order == 11:
                ids.reverse()
            pop = {
                "dataset": "d",
                "realization": r,
                "order": order,
                "item_ids": ids,
                "paraphrase_counts": [2, 2],
                "locality_ids": [f"loc{r}-0", f"loc{r}-1"],
                "checkpoints": {"end": 2},
            }
            inv["populations"].append(pop)
            for cond in inv["axes"]["conditions"]:
                g = 0.5 + (gain if cond == "learned_new" else 0)
                path = root / f"{r}-{order}-{cond}"
                cell = {
                    "dataset": "d",
                    "realization": r,
                    "order": order,
                    "condition": cond,
                    "stream_dir": str(path),
                    "stream_summary": str(path / "summary.json"),
                    "admitted": True,
                }
                items = [
                    {
                        "item_id": i,
                        "dataset": "d",
                        "index": j,
                        "es": 1.0,
                        "gs_n": 2,
                        "outcome": "accepted",
                        "threshold": True,
                    }
                    for j, i in enumerate(ids)
                ]
                checks = [
                    {
                        "tag": "end",
                        "items": 2,
                        "rows": [{"item_id": i, "ret_es": 1.0, "ret_gs": g} for i in ids],
                        "locality": {
                            "n": 2,
                            "prompt_ids": pop["locality_ids"],
                            "ls_complete_answer": 1.0,
                        },
                    }
                ]
                vals = {
                    "es_immediate": 1.0,
                    "ret_es_end": 1.0,
                    "ret_gs_end": g,
                    "ls_complete_answer_end": 1.0,
                }
                metrics = {
                    "status": "complete",
                    "metrics": {k: {"n": 2, "value": v} for k, v in vals.items()},
                }
                package = {
                    "items": items,
                    "checkpoints": checks,
                    "metrics": metrics,
                    "summary": {"dataset": "d", "stream_metrics": vals.copy()},
                }
                if change:
                    change(package)
                inv["cells"].append(cell)
                path.mkdir(parents=True)
                for key, name in (
                    ("items", "items.jsonl"),
                    ("checkpoints", "checkpoints.json"),
                    ("metrics", "metrics.json"),
                    ("summary", "summary.json"),
                ):
                    with (path / name).open("x") as f:
                        f.write(
                            "".join(json.dumps(x) + "\n" for x in package[key])
                            if key == "items"
                            else json.dumps(package[key])
                        )
    return inv


def test_positive_known_answers(tmp_path):
    r = analyze(fixture(tmp_path), root=tmp_path)
    c = r["comparisons"][0]
    assert c["classification"] == "positive"
    assert c["metrics"]["RET-GS"]["estimate"] == pytest.approx(0.1)
    assert c["metrics"]["RET-GS"]["planned_pairs"] == 6
    assert c["metrics"]["RET-GS"]["bootstrap"]["orders_kept_together"]
    assert r["gpu_seconds"] == 0


def test_revision_margin_differs_from_v0(tmp_path):
    c = analyze(fixture(tmp_path, gain=0.03), root=tmp_path)["comparisons"][0]
    assert c["metrics"]["RET-GS"]["interval"]["lower"] > 0.02
    assert c["classification"] == "negative"


def test_missing_cell_retains_expected_axis(tmp_path):
    inv = fixture(tmp_path)
    inv["cells"].pop()
    r = analyze(inv, root=tmp_path)
    c = r["comparisons"][0]
    assert len(r["cells"]) == 12
    assert c["classification"] == "incomplete"
    assert c["metrics"]["RET-GS"]["observed_pairs"] == 5
    assert c["metrics"]["RET-GS"]["estimate"] is None
    assert c["metrics"]["RET-GS"]["interval"] is None


def test_common_missing_item_not_complete(tmp_path):
    def change(p):
        p["items"].pop()
        p["checkpoints"][0]["rows"].pop()

    r = analyze(fixture(tmp_path, change=change), root=tmp_path)
    assert r["comparisons"][0]["classification"] == "incomplete"
    assert all(
        c["metrics"]["RET-GS"]["planned"] == 2 and c["metrics"]["RET-GS"]["scored"] == 1
        for c in r["cells"]
    )


def test_failed_acquisition_retained(tmp_path):
    def change(p):
        p["items"][0].update(es=0.0, threshold=False, outcome="rejected_no_improvement")
        p["checkpoints"][0]["rows"][0].update(ret_es=0.0, ret_gs=0.0)
        for k in ("es_immediate", "ret_es_end", "ret_gs_end"):
            p["metrics"]["metrics"][k]["value"] /= 2
            p["summary"]["stream_metrics"][k] /= 2

    r = analyze(fixture(tmp_path, change=change), root=tmp_path)
    for c in r["cells"]:
        assert c["metrics"]["ES"]["value"] == 0.5
        assert c["metrics"]["ES"]["planned"] == c["metrics"]["ES"]["scored"] == 2
        assert c["failed_acquisition_count"] == c["behavioral_rejections_retained"] == 1


@pytest.mark.parametrize("kind", ["duplicate", "reordered", "dataset", "nonfinite", "paraphrase"])
def test_invalid_observed_identity_refused(tmp_path, kind):
    def change(p):
        if kind == "duplicate":
            p["items"][1]["item_id"] = p["items"][0]["item_id"]
        elif kind == "reordered":
            p["items"].reverse()
        elif kind == "dataset":
            p["items"][0]["dataset"] = "wrong"
        elif kind == "nonfinite":
            p["checkpoints"][0]["rows"][0]["ret_gs"] = float("nan")
        else:
            p["items"][0]["gs_n"] = 1

    with pytest.raises(ValueError):
        analyze(fixture(tmp_path, change=change), root=tmp_path)


def test_missing_required_endpoint(tmp_path):
    inv = fixture(tmp_path)
    for p in inv["populations"]:
        p["endpoints"] = {
            "composition": {
                "expected_ids": ["case-a", "case-b"],
                "row_metric": "direct_composition_success",
                "required": True,
            }
        }
    r = analyze(inv, root=tmp_path)
    assert r["comparisons"][0]["classification"] == "incomplete"
    assert r["cells"][0]["endpoints"]["composition"]["planned"] == 2
    assert r["cells"][0]["endpoints"]["composition"]["value"] is None


def test_fidelity_blocks_favorable_metrics(tmp_path):
    inv = fixture(tmp_path)
    for c in inv["cells"]:
        if c["condition"] == "stable_control":
            c["admitted"] = False
    assert analyze(inv, root=tmp_path)["comparisons"][0]["classification"] == "ineligible"


def test_single_order_keeps_three_clusters(tmp_path):
    m = analyze(fixture(tmp_path, orders=(10,)), root=tmp_path)["comparisons"][0]["metrics"][
        "RET-GS"
    ]
    assert m["clusters"] == 3
    assert m["bootstrap"]["orders_kept_together"]
    assert m["planned_pairs"] == 3


def test_repeated_realization_refused(tmp_path):
    inv = fixture(tmp_path)
    for p in inv["populations"]:
        p["item_ids"] = ["same-a", "same-b"] if p["order"] == 10 else ["same-b", "same-a"]
    with pytest.raises(ValueError, match="share items"):
        validate_inventory(inv)


def test_cluster_bootstrap_and_single_realization():
    grid = [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]
    a = paired_metric(grid, seed=9, draws=1000)
    assert a == paired_metric(grid, seed=9, draws=1000)
    assert a["interval"]["lower"] == a["interval"]["upper"] == 0.5
    assert paired_metric([[0.2]])["interval"] is None


def test_classifier_boundaries():
    def m(point, lo, hi):
        return {"status": "complete", "estimate": point, "interval": {"lower": lo, "upper": hi}}

    values = {"ES": m(0, -0.04, 0.04), "RET-GS": m(0.1, 0.05, 0.15), "LS": m(0, 0, 0)}
    assert classify(values) == "qualified"
    values["ES"] = m(-0.03, -0.04, -0.025)
    assert classify(values) == "negative"
    values["ES"] = m(0, -0.02, 0.02)
    assert classify(values) == "qualified"
    values["RET-GS"] = m(0.05, 0, 0.1)
    assert classify(values) == "inconclusive"
