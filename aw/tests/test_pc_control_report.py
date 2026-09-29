"""Control reports refuse mixed treatment records and unpaired item streams."""

import json

import pytest

from aw import pc_control_report as report
from aw import pc_random_run as random


def fixture(root):
    plan = random.plan()
    # Tiny synthetic documents exercise admission/reporting, not model efficacy.
    for c in plan["cells"]:
        c["items"] = 2
    (root / "plan.json").write_text(json.dumps(plan))
    source = root / "input.json"
    source.write_text("{}")
    h = report.sha(source)
    for c in plan["cells"]:
        out = root / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        out.mkdir()
        cfg = dict(
            c,
            **plan["credit"][c["arm"]],
            sources=plan["sources"],
            base_hash_before="base",
            item_ids=["a", "b"],
            manifest=str(source),
            manifest_sha256=h,
            drift=dict(path=str(source), sha256=h),
            weights_sha256="w",
            named_seeds={"r": c["realization"]},
            locality_prompts_sha256="l",
        )
        finish = dict(
            plan["credit"][c["arm"]],
            status="complete",
            items_completed=2,
            base_hash_before="base",
            base_hash_after="base",
            elapsed_process_seconds=1,
            ledger={"total": dict(full_forwards=2, partial_forwards=0, reverses=1, settle_iters=0)},
        )
        native = dict(
            status="complete",
            items_completed=2,
            metrics={k: dict(value=0.2) for k in report.METRICS.values()},
        )
        for name, value in (
            ("config.json", cfg),
            ("finish.json", finish),
            ("metrics.json", native),
            ("secondary-summary.json", {k: 0.2 for k in report.SECONDARY}),
        ):
            (out / name).write_text(json.dumps(value))
        (out / "items.jsonl").write_text(
            "\n".join(json.dumps(dict(item_id=x)) for x in cfg["item_ids"]) + "\n"
        )
    return root


def test_report_labels_control_and_rejects_finish_treatment_drift(tmp_path):
    group = tmp_path / "group"
    group.mkdir()
    fixture(group)
    result = report.build(group, tmp_path / "report.md", tmp_path / "report")
    assert len(result["pairs"]) == 6 and result["treatment"]["arm"] == "SE-R"
    assert all(all(v == 0 for v in p["difference"].values()) for p in result["pairs"])
    path = group / "zsre-r0-o100-SE-R/finish.json"
    value = json.loads(path.read_text())
    value["control_treatment"]["role"] = "adjoint_control"
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="mismatch"):
        report.build(group, tmp_path / "invalid.md", tmp_path / "invalid")


def test_report_refuses_changed_item_order(tmp_path):
    group = tmp_path / "group"
    group.mkdir()
    fixture(group)
    p = group / "zsre-r0-o100-SE-R/items.jsonl"
    p.write_text('{"item_id":"b"}\n{"item_id":"a"}\n')
    with pytest.raises(ValueError, match="order/count"):
        report.build(group, tmp_path / "invalid.md", tmp_path / "invalid")
