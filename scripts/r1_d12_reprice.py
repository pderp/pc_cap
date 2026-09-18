"""Create a versioned block-boundary cost proposal without altering admission.

Extends D11 by composition: frozen producers and active queue ceilings stay fixed.
No signatures, model calls, sealed-payload reads, or lead-queue posts are made.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from scripts import r1_58h_cost_contract as costs
from scripts import r1_d11_block_report as d11

RULE = {
    "version": 1,
    "class": "condition, dataset, attempted edits, checkpoint cadence, full-validation contract",
    "donors": "artifact-complete cells through boundary, including every covered failed/retry process; same configured worker count",
    "expected": "arithmetic mean of comparable completed-cell process envelopes",
    "ceiling": "1.5 times maximum comparable completed-cell process envelope",
    "concurrency": "measured envelopes already include concurrency; do not multiply by 1.15 again",
    "failures": "all failures charged to actual spending; exhausted incomplete cells never become zero-cost donors",
    "scope": "no outcome-based exclusions; no transfer across dataset, condition, occupancy or cadence",
    "authority": "unsigned planning proposal only; versioned admission at an idle boundary required before changing ceilings",
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read_ref(binding):
    require(d11.ref(binding["path"]) == binding, "metadata binding changed")
    return json.loads(Path(binding["path"]).read_bytes())


def digest(doc):
    return d11.watch.full.digest(doc)


def class_spec(cell, matrix):
    return dict(
        condition=cell["condition"], dataset=cell["dataset"],
        attempted_edits=cell.get("attempted_edits", max(cell["checkpoints"])),
        checkpoints=cell["checkpoints"],
        full_validation=cell.get("full_validation", matrix.get("full_validation")),
    )


def verify_snapshot(report):
    """Recheck mutable inputs immediately before emitting a review artifact."""
    snap = report["d11"]
    matrix = read_ref(snap["identity"]["matrix"])
    require(
        snap["accounting_sources_sha256"] == d11.accounting_snapshot(
            d11.queue.ordered(matrix), Path(snap["identity"]["receipt_root"])
        ), "queue changed since boundary snapshot",
    )
    raw, _, _ = d11.read_watch(Path(snap["identity"]["journal"]))
    require(d11.digest(raw) == snap["watch"]["cursor"]["sha256"], "watch changed since snapshot")
    for path, sha in snap["inventory"]["sources_sha256"].items():
        require(d11.ref(path)["sha256"] == sha, "cell evidence changed since snapshot")
    for binding in report["inputs"].values():
        if binding is not None:
            read_ref(binding) if binding["path"].endswith(".json") else require(
                d11.ref(binding["path"]) == binding, "plan source changed"
            )


def build(matrix_path, *, receipt_root, journal, cost_receipt, boundary_block,
          previous_plan=None, previous_report=None, workers=2, synthetic=False):
    cost_ref = d11.ref(cost_receipt)
    cost = read_ref(cost_ref)
    require(type(cost.get("receipt_revision")) is int and cost["receipt_revision"] == 4,
            "typed v4 baseline required")
    costs.validate(cost)
    matrix_ref = d11.ref(matrix_path)
    matrix = read_ref(matrix_ref)
    require(matrix.get("cost_admission") == cost_ref, "queue must bind exact cost receipt")
    require(matrix.get("source_matrix") == cost["matrix"], "queue/source cost matrix differs")
    require(matrix.get("protocol") == cost["protocol"], "queue/cost protocol differs")
    require(matrix.get("shared_process_hours") == cost["shared_process_hours"] == 750,
            "shared 750-hour budget required")
    if not synthetic:
        signature = cost.get("lead_signature", {})
        require(cost.get("lead_approved") is True and cost.get("status") == "closed"
                and bool(str(signature.get("name") or "").strip())
                and bool(cost.get("operator_request_sha256")), "actual signed cost receipt required")
        datetime.fromisoformat(signature["date"])
        # The assembler admits individual cells; the declaration's inherited
        # top-level launch_allowed flag remains false even after publication.
        require(matrix.get("scope") == "confirmatory" and all(
            c.get("admitted") is True and c.get("launch_allowed") is True
            for c in d11.queue.ordered(matrix)), "admitted confirmatory cells required")
        frozen = read_ref(matrix["freeze"])
        require(frozen.get("lead_approved") is True and frozen.get("launch_authorized") is True
                and frozen.get("open_gates") == [] and frozen.get("cost_admission") == cost_ref,
                "published freeze/cost admission required")
        require(d11.queue.validate_watch(matrix), "full-validation fidelity watch required")
    snap = d11.build(matrix_path, receipt_root=receipt_root, journal=journal,
                     previous=previous_report, boundary_block=boundary_block, workers=workers)
    require(snap["boundary_ready"], "block boundary incomplete or has accounting/watch gaps")
    require(not snap["issues"], "queue must be idle with complete accounting and watch evidence")
    baseline = costs.read(cost["bindings"]["cell_ceilings"])["cells"]
    previous_ref, version = None, 4
    if previous_plan is not None:
        previous_ref = d11.ref(previous_plan)
        previous = read_ref(previous_ref)
        require(previous.get("plan_sha256") == digest(
            {k: v for k, v in previous.items() if k != "plan_sha256"}), "previous plan digest differs")
        require(previous.get("rule") == RULE and previous.get("synthetic") == synthetic
                and previous["inputs"]["cost_receipt"] == cost_ref
                and previous["d11"]["identity"] == snap["identity"], "previous plan identity differs")
        require(type(previous.get("plan_version")) is int and previous["plan_version"] >= 4
                and previous["d11"]["boundary_block"] < boundary_block,
                "previous plan must precede this block")
        for path, sha in previous["d11"]["accounting_sources_sha256"].items():
            require(d11.ref(path)["sha256"] == sha, "previous charged evidence changed")
        raw, _, _ = d11.read_watch(Path(snap["identity"]["journal"]))
        cursor = previous["d11"]["watch"]["cursor"]
        prefix = b"".join(raw.splitlines(keepends=True)[:cursor["events"]])
        require(len(prefix) == cursor["bytes"] and d11.digest(prefix) == cursor["sha256"],
                "watch history changed since previous plan")
        require(set(previous["d11"]["complete_cells"]) <= set(snap["complete_cells"]),
                "previously complete evidence regressed")
        version = previous["plan_version"] + 1
    cells = d11.queue.ordered(matrix)
    by_id = {c["cell_id"]: c for c in cells}
    rows = {r["cell_id"]: r for r in snap["inventory"]["queue"]}
    groups, donors, excluded = {}, defaultdict(list), []
    for cell in cells:
        spec = class_spec(cell, matrix)
        key = digest(spec)
        groups.setdefault(key, dict(class_spec=spec, cell_ids=[]))["cell_ids"].append(cell["cell_id"])
        row = rows[cell["cell_id"]]
        if cell["block_number"] > boundary_block or not row["observed"]["artifact_complete"]:
            continue
        envelopes = []
        reason = None
        for ref in row["cost"].get("process_receipts", []):
            end = read_ref(dict(path=ref["path"], sha256=ref["sha256"]))
            if end.get("workers") != workers:
                reason = "different or missing configured worker count"
            if end.get("failure_class") == "host":
                reason = "host failure needs owner reconciliation"
            envelopes.append(dict(source=dict(path=ref["path"], sha256=ref["sha256"]),
                                  seconds=ref["wall_seconds"], failure_class=end.get("failure_class")))
        if not envelopes:
            reason = "no whole-process envelope"
        if reason:
            excluded.append(dict(cell_id=cell["cell_id"], reason=reason))
            continue
        measured = math.fsum(e["seconds"] for e in envelopes)
        require(costs.positive(measured), "positive completed-cell process cost required")
        require(math.isclose(measured, row["cost"]["known_attempt_wall_seconds"], abs_tol=1e-8),
                "donor process total differs from charged cell cost")
        donors[key].append(dict(cell_id=cell["cell_id"], process_seconds=measured, envelopes=envelopes))
    factor = d11.queue.worker_factor(workers)
    updated = []
    for key, group in groups.items():
        spec = group["class_spec"]
        price = baseline[spec["condition"] + ":" + spec["dataset"]]
        old_expected, old_ceiling = price["solo_seconds"] * factor, price["ceiling_seconds"] * factor
        observations = donors[key]
        if observations:
            times = [r["process_seconds"] for r in observations]
            expected, ceiling = math.fsum(times) / len(times), 1.5 * max(times)
            basis = "measured_completed_cell_process_envelopes"
        else:
            expected, ceiling, basis = old_expected, old_ceiling, "retained_plan_v3_estimate"
        require(costs.positive(expected) and costs.positive(ceiling), "positive class prices required")
        remaining = [cid for cid in group["cell_ids"]
                     if not rows[cid]["observed"]["artifact_complete"] and not rows[cid]["retry"]["exhausted"]]
        updated.append(dict(
            class_id=key, **group, basis=basis, measurements=observations,
            measured_cells=len(observations), expected_process_seconds=expected,
            proposed_effective_ceiling_seconds=ceiling,
            proposed_solo_ceiling_seconds=ceiling / factor,
            baseline_expected_process_seconds=old_expected,
            baseline_effective_ceiling_seconds=old_ceiling,
            remaining_cell_ids=remaining,
            under_active_ceiling=all(ceiling <= by_id[cid]["ceilings"]["wall_seconds"] * factor
                                     for cid in group["cell_ids"]),
        ))
    actual = snap["cost_ledger"]["charged_seconds"]
    remaining_expected = math.fsum(len(g["remaining_cell_ids"]) * g["expected_process_seconds"] for g in updated)
    remaining_ceiling = math.fsum(len(g["remaining_cell_ids"]) * g["proposed_effective_ceiling_seconds"] for g in updated)
    old_remaining = math.fsum(len(g["remaining_cell_ids"]) * g["baseline_expected_process_seconds"] for g in updated)
    known = set(snap["complete_cells"])
    exhausted = [r["cell_id"] for r in rows.values() if r["retry"]["exhausted"]]
    plan_ref = d11.ref(d11.ROOT / "docs/R1_execution_plan_v3.md")
    out = dict(
        task="R1-D12", schema_version=1, plan_version=version, rule=RULE,
        status="unsigned_boundary_cost_proposal", synthetic=synthetic,
        generated_utc=snap["generated_utc"], lead_approved=False, launch_authorized=False,
        inputs=dict(cost_receipt=cost_ref, execution_plan_v3=plan_ref,
                    published_freeze=matrix.get("freeze") if not synthetic else None,
                    previous_plan=previous_ref, producer=d11.ref(__file__)),
        d11=snap, classes=updated, excluded_donors=excluded,
        projection=dict(
            actual_process_hours=actual / 3600,
            remaining_expected_process_hours=remaining_expected / 3600,
            expected_total_process_hours=(actual + remaining_expected) / 3600,
            proposed_ceiling_total_process_hours=(actual + remaining_ceiling) / 3600,
            baseline_expected_total_with_actual_spend_hours=(actual + old_remaining) / 3600,
            active_queue_ceiling_projection_hours=snap["inventory"]["cost"]["projected_total_hours"],
            expected_buffer_hours=750 - (actual + remaining_expected) / 3600,
            proposed_ceiling_buffer_hours=750 - (actual + remaining_ceiling) / 3600,
            shared_process_hours=750, workers=workers,
            elapsed_hours=None,
            elapsed_note="Process envelopes do not measure future aggregate throughput; no new elapsed/calendar promise.",
        ),
        dec052_inventory=dict(
            total_cells=len(cells), complete_cells=sorted(known),
            complete_blocks=snap["inventory"]["complete_blocks"],
            incomplete_cells=snap["inventory"]["incomplete_cells"],
            exhausted_incomplete_cells=exhausted,
            prospectively_omitted_cells=matrix.get("prospectively_omitted_cells", []),
            qualification="Exhausted cells remain incomplete and have no additional retry reserved; prospective omissions are not completed outcomes.",
        ),
        limitations=[
            "Rates use only completed comparable chains; failures remain in actual spend and successful retry chains. No fixed future failure allowance is invented.",
            "Few observations and configured workers do not establish throughput, peak memory or a guaranteed upper bound. Keep existing memory ceilings and admission floor.",
            "Different occupancy/cadence/classes keep labelled plan-v3 estimates; measured phase rates are not extrapolated without a separately reviewed transfer.",
            "A quiet snapshot is not a lock or launch permission. Owner must stop dispatch, review the proposal and issue versioned admission before a changed ceiling can take effect.",
            "October 9 experimental stop; DEC-052 incomplete inventory and DEC-064 secondary benchmark reporting remain unchanged.",
        ],
    )
    verify_snapshot(out)
    out["plan_sha256"] = digest(out)
    return out


def text(report):
    p = report["projection"]
    measured = sum(c["basis"] == "measured_completed_cell_process_envelopes" for c in report["classes"])
    lines = [
        f"# Execution plan v{report['plan_version']} — block {report['d11']['boundary_block']} cost proposal",
        "", f"Synthetic rehearsal: {report['synthetic']}. Unsigned; active ceilings are unchanged.", "",
        f"Measured class replacements: {measured}/{len(report['classes'])}; remaining classes retain plan-v3 estimates.",
        f"Actual spend: {p['actual_process_hours']:.6f} process h; expected total: {p['expected_total_process_hours']:.6f}; proposed ceiling total: {p['proposed_ceiling_total_process_hours']:.6f}.",
        f"Buffer against 750 h: expected {p['expected_buffer_hours']:.6f}; proposed ceilings {p['proposed_ceiling_buffer_hours']:.6f}.",
        f"Active admitted ceiling projection (unchanged): {p['active_queue_ceiling_projection_hours']:.6f} h.", "",
        "| Condition / dataset / edits / checkpoints | N measured | Expected process s | Proposed effective ceiling s | Basis |",
        "|---|---:|---:|---:|---|",
    ]
    for c in report["classes"]:
        s = c["class_spec"]
        lines.append(f"| {s['condition']} / {s['dataset']} / {s['attempted_edits']} / {s['checkpoints']} | {c['measured_cells']} | {c['expected_process_seconds']:.3f} | {c['proposed_effective_ceiling_seconds']:.3f} | {c['basis']} |")
    lines += ["", "Re-pricing rule: " + json.dumps(RULE, ensure_ascii=False), ""]
    lines += ["Donor excluded (cost still charged): " + str(e) for e in report["excluded_donors"]]
    lines += ["- " + s for s in report["limitations"]]
    lines += ["", "## D11 accounting, fidelity watch and DEC-052 inventory", "", d11.text(report["d11"]),
              "This text has not been posted to the lead queue. Cost proposals are not signatures.",
              f"Plan digest: {report['plan_sha256']}"]
    return "\n".join(lines) + "\n"


def emit(report, output_dir):
    output = d11.local(output_dir)
    require(output.is_relative_to(d11.ROOT / "logs"), "output must be under repository logs")
    require(report["plan_sha256"] == digest({k: v for k, v in report.items() if k != "plan_sha256"}),
            "plan modified before publication")
    verify_snapshot(report)
    output.mkdir(parents=True, exist_ok=False)
    values = {"plan.json": report, "d11-report.json": report["d11"],
              "fidelity-watch.json": report["d11"]["watch"],
              "dec052-inventory.json": report["dec052_inventory"]}
    for name, value in values.items():
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    rendered = text(report)
    (output / f"execution-plan-v{report['plan_version']}.md").write_text(rendered)
    (output / "lead-queue.txt").write_text(rendered)
    return d11.ref(output / "plan.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("matrix", "receipt-root", "journal", "cost-receipt", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--boundary-block", type=int, required=True)
    parser.add_argument("--previous-plan", type=Path)
    parser.add_argument("--previous-report", type=Path,
                        help="D11 JSON from the last actually posted report, not merely generated")
    parser.add_argument("--workers", type=int, choices=(1, 2), default=2)
    parser.add_argument("--synthetic", action="store_true", help="label fixture evidence; never admission")
    args = vars(parser.parse_args())
    output = args.pop("output_dir")
    matrix = args.pop("matrix")
    print(json.dumps(emit(build(matrix, **args), output), indent=2))


if __name__ == "__main__":
    main()
