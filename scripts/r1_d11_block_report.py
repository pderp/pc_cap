"""Read-only queue/cost/watch snapshot and text for the orchestrator's lead queue.

No model, sealed payload, watch mutation, notification or GPU lease is used.
Pass the last POSTED report as --previous; generating a report is not delivery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import UTC, datetime
from pathlib import Path

from scripts import ht8_fidelity_watch as watch
from scripts import r1_77_queue as queue

ROOT = Path(__file__).resolve().parents[1]
VERSION = 1


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT) or "confirm" in path.parts:
        raise PermissionError("report inputs must be unsealed repository metadata")
    return path


def ref(path):
    path = local(path)
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def accounting_snapshot(cells, receipt_root):
    """Bind directory membership too: a new attempt/start must invalidate a scan."""
    paths = set(receipt_root.glob("**/*.json"))
    for cell in cells:
        directory = local(cell["result_dir"])
        paths.update(directory.glob("cell.json"))
        paths.update(directory.glob("attempt-*/*.json"))
    return {str(local(p)): digest(p.read_bytes()) for p in sorted(paths)}


def read_watch(path):
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("torn watch journal; retry after writer finishes or reconcile")
    events = [json.loads(line) for line in raw.splitlines()]
    return raw, events, watch.replay(events)


def cost_ledger(inventory):
    """The scheduler's process receipts ARE the launch cost ledger.

    Covered driver costs are diagnostics, not an additional charge. JAX operation
    timers/whole-project historical ledgers must not be added to these envelopes.
    """
    rows = []
    for row in inventory["queue"]:
        cost = row["cost"]
        processes = cost.get("process_receipts", [])
        process_seconds = math.fsum(p["wall_seconds"] for p in processes)
        seconds = cost["known_attempt_wall_seconds"]
        remainder = seconds - process_seconds
        if remainder < -1e-8 or not math.isfinite(seconds) or seconds < 0:
            raise ValueError("inconsistent process/driver cost ledger")
        rows.append(
            dict(
                cell_id=row["cell_id"],
                charged_seconds=seconds,
                process_envelope_seconds=process_seconds,
                uncovered_driver_seconds=max(0.0, remainder),
                process_receipts=processes,
                driver_attempts=cost.get("attempts", []),
                unknown_attempts=cost["unknown_attempts"],
            )
        )
    seconds = math.fsum(r["charged_seconds"] for r in rows)
    if not math.isclose(seconds / 3600, inventory["cost"]["known_attempt_hours"], abs_tol=1e-10):
        raise ValueError("queue inventory and cost ledger disagree")
    return dict(
        rows=rows,
        charged_seconds=seconds,
        uncovered_driver_seconds=math.fsum(r["uncovered_driver_seconds"] for r in rows),
        basis="Process envelopes replace covered driver attempts; overlap and failures charged once each. Uncovered legacy driver times exclude process startup. JAX timers are not added.",
    )


def build(matrix_path, *, receipt_root, journal, previous=None, boundary_block=None, workers=2):
    matrix_path, receipt_root, journal = map(local, (matrix_path, receipt_root, journal))
    if not receipt_root.is_relative_to(ROOT / "logs"):
        raise PermissionError("persistent queue receipt root must be under repository logs")
    matrix_ref = ref(matrix_path)
    matrix = queue.read(matrix_path)
    cells = queue.ordered(matrix)
    if matrix.get("scope") not in ("development", "confirmatory"):
        raise ValueError("explicit development or confirmatory queue scope required")
    watch_required = queue.validate_watch(matrix)
    if boundary_block is not None and boundary_block not in {c["block_number"] for c in cells}:
        raise ValueError("boundary must name a declared block")
    ceiling = matrix.get("shared_process_hours")
    if ceiling is not None and (
        type(ceiling) not in (int, float) or not math.isfinite(ceiling) or ceiling <= 0
    ):
        raise ValueError("invalid declared process-hour budget")
    identity = dict(
        matrix=matrix_ref,
        receipt_root=str(receipt_root),
        journal=str(journal),
        workers=workers,
        ceiling_hours=ceiling,
    )
    before = accounting_snapshot(cells, receipt_root)
    inventory = queue.inventory(
        matrix,
        receipt_root=receipt_root,
        matrix_hash=matrix_ref["sha256"],
        workers=workers,
        ceiling_hours=ceiling,
    )
    ledger = cost_ledger(inventory)
    raw, events, state = read_watch(journal)
    prior_count, previous_ref = 0, None
    if previous is not None:
        previous_ref = ref(previous)
        prior = json.loads(local(previous).read_bytes())
        if prior.get("report_sha256") != watch.full.digest(
            {k: v for k, v in prior.items() if k != "report_sha256"}
        ):
            raise ValueError("previous report digest differs")
        if prior.get("version") != VERSION or prior.get("identity") != identity:
            raise ValueError("previous boundary belongs to a different queue/watch identity")
        cursor = prior["watch"]["cursor"]
        prior_count = cursor["events"]
        prefix = b"".join(raw.splitlines(keepends=True)[:prior_count])
        if (
            type(prior_count) is not int
            or prior_count < 0
            or len(events) < prior_count
            or len(prefix) != cursor["bytes"]
            or digest(prefix) != cursor["sha256"]
        ):
            raise ValueError("watch journal truncated or prefix rewritten since previous boundary")
        old_block = prior.get("boundary_block")
        if boundary_block is not None and old_block is not None and boundary_block < old_block:
            raise ValueError("boundary block cannot move backwards")
    mode = "stage4_development_cell" if matrix["scope"] == "development" else "stage4_sealed_cell"
    expected = {
        watch.full.digest(
            dict(
                mode=mode,
                recipe_sha256=c["manifest_sha256"],
                cell={k: c[k] for k in queue.analysis.COORDS},
            )
        ): c["cell_id"]
        for c in cells
    }
    new_ids = {e["observation"]["cell_id"] for e in events[prior_count:]}
    watched = {expected[cid] for cid in state["seen"] if cid in expected}
    complete = [r["cell_id"] for r in inventory["queue"] if r["observed"]["artifact_complete"]]
    missing_watch = sorted(set(complete) - watched) if watch_required else []
    issues = []
    if inventory["cost"]["unknown_attempts"]:
        issues.append(
            "Live, interrupted or unreadable attempts have unknown costs; known spend is a lower bound and projection is unavailable."
        )
    if ledger["uncovered_driver_seconds"]:
        issues.append(
            "Some driver attempts lack covering process receipts; startup overhead is not fully measured."
        )
    if missing_watch:
        issues.append(
            "Completed cells missing required watch observations: " + ", ".join(missing_watch)
        )
    invalid = [r["cell_id"] for r in inventory["queue"] if r["observed"]["status"] == "invalid"]
    if invalid:
        issues.append("Invalid cell evidence: " + ", ".join(invalid))
    selected = [
        r for r in inventory["queue"] if boundary_block is not None and r["block"] <= boundary_block
    ]
    unprocessed = [
        r["cell_id"]
        for r in selected
        if not r["observed"]["artifact_complete"] and not r["retry"]["exhausted"]
    ]
    selected_ids = {r["cell_id"] for r in selected}
    boundary_gaps = [
        r["cell_id"]
        for r in ledger["rows"]
        if r["cell_id"] in selected_ids and (r["unknown_attempts"] or r["uncovered_driver_seconds"])
    ]
    boundary_gaps = sorted(
        set(boundary_gaps) | (selected_ids & (set(missing_watch) | set(invalid)))
    )
    ready = boundary_block is not None and not boundary_gaps and not unprocessed
    entries = [
        dict(e, queue_cell_id=expected.get(e["cell_id"]))
        for e in state["entries"]
        if e["cell_id"] in new_ids
    ]
    alerts = [
        dict(a, queue_cell_id=expected.get(a["cell_id"]))
        for a in state["alerts"]
        if a["cell_id"] in new_ids
    ]
    # Verify a coherent snapshot. Never lock the GPU queue or hold up its writers.
    if before != accounting_snapshot(cells, receipt_root) or matrix_ref != ref(matrix_path):
        raise ValueError("queue changed during report; retry the read-only snapshot")
    for path, sha in inventory["sources_sha256"].items():
        if digest(Path(path).read_bytes()) != sha:
            raise ValueError("cell evidence changed during report")
    if (journal.read_bytes() if journal.exists() else b"") != raw:
        raise ValueError("watch changed during report; retry the read-only snapshot")
    if previous_ref is not None and previous_ref != ref(previous):
        raise ValueError("previous report changed during read")
    report = dict(
        version=VERSION,
        task="R1-D11",
        generated_utc=datetime.now(UTC).isoformat(),
        identity=identity,
        previous=previous_ref,
        boundary_block=boundary_block,
        boundary_ready=ready,
        boundary_unprocessed=unprocessed,
        boundary_gap_cells=boundary_gaps,
        boundary_known_process_hours=math.fsum(
            r["charged_seconds"] for r in ledger["rows"] if r["cell_id"] in selected_ids
        )
        / 3600
        if boundary_block is not None
        else None,
        complete_cells=complete,
        total_cells=len(cells),
        inventory=inventory,
        cost_ledger=ledger,
        issues=issues,
        watch=dict(
            required=watch_required,
            cursor=dict(events=len(events), bytes=len(raw), sha256=digest(raw)),
            new_observations=len(events) - prior_count,
            new_queue_observations=sum(cid in expected for cid in new_ids),
            entries=entries,
            alerts=alerts,
            missing_completed_cells=missing_watch,
            delta_scope="Global watch since the explicitly supplied previous report (or journal beginning). queue_cell_id identifies this matrix; other observations retain their original scope.",
            delivery="not_sent; use the last actually posted report as --previous",
            admission_veto=False,
        ),
        accounting_sources_sha256=before,
        implementation=dict(
            report=watch.full.ref(__file__),
            queue=watch.full.ref(queue.__file__),
            watch=watch.binding(),
        ),
        scientific_limit="Artifact completeness does not assert benchmark success, effect significance, admission or launch authority.",
    )
    report["report_sha256"] = watch.full.digest(report)
    return report


def text(report):
    inv, cost, state = report["inventory"], report["inventory"]["cost"], report["watch"]

    def hours(value):
        return "unavailable" if value is None else f"{value:.6f}"

    lines = [
        f"R1 {'block ' + str(report['boundary_block']) if report['boundary_block'] is not None else 'daily status'} — {report['generated_utc']}",
        f"Scope: {inv['scope']}; matrix SHA256 {report['identity']['matrix']['sha256']}.",
        f"Artifact-complete cells: {len(report['complete_cells'])}/{report['total_cells']}; complete blocks: {inv['complete_blocks']}.",
        f"Known spend: {hours(cost['known_attempt_hours'])} process-hours; projected total: {hours(cost['projected_total_hours'])}; declared ceiling: {hours(cost['ceiling_hours'])}.",
        "Projection uses the entire matrix, remaining solo ceilings × "
        + str(cost["remaining_cell_ceiling_multiplier"])
        + "; retry-exhausted incomplete cells are not reserved again. It is not an elapsed-time forecast or a guarantee of full completion.",
        "Cost ledger: " + report["cost_ledger"]["basis"],
        "Incomplete cells:",
    ]
    retry = {r["cell_id"]: r["retry"] for r in inv["queue"]}
    lines += [
        f"- {r['cell_id']}: missing checkpoints {r['missing_checkpoints']}; failures {retry[r['cell_id']]['failures']}/2; exhausted={retry[r['cell_id']]['exhausted']}"
        for r in inv["incomplete_cells"]
    ] or ["- none"]
    lines += [
        f"Watch since previous posted snapshot: {state['new_observations']} global observations ({state['new_queue_observations']} in this matrix), {len(state['entries'])} breach entries, {len(state['alerts'])} creep alerts.",
    ]
    for entry in state["entries"]:
        obs = entry["observation"]
        label = entry["queue_cell_id"] or f"outside this matrix/{obs['scope']}/{entry['cell_id']}"
        values = "; ".join(
            f"{refname}: KL={v['mean_kl']:.9g}, signed ΔNLL={v['mean_signed_nll_increase']:.9g}"
            for refname, v in watch.metrics(obs).items()
        )
        lines.append(
            f"- Breach {label} ({obs['cell']['condition']}/{obs['cell']['dataset']}): {values} nats."
        )
    for alert in state["alerts"]:
        label = alert["queue_cell_id"] or f"outside this matrix/{alert['cell_id']}"
        reasons = "; ".join(
            f"{r['reference']}/{r['metric']} {r['kind']}: {r['value']:.9g} > {r['compared_value']:.9g}"
            for r in alert["reasons"]
        )
        lines.append(
            f"- CREEP ALERT {label}: {reasons}. Delivery remains pending orchestrator notification."
        )
    lines += [
        "Checks: "
        + (
            "; ".join(report["issues"])
            if report["issues"]
            else "no snapshot/accounting/watch gaps detected"
        )
    ]
    if report["boundary_block"] is not None:
        lines.append(
            f"Boundary ready: {report['boundary_ready']}; unprocessed cells through boundary: {report['boundary_unprocessed']}; accounting/watch gap cells through boundary: {report['boundary_gap_cells']}."
        )
        lines.append(
            f"Known process-hours through this boundary: {hours(report['boundary_known_process_hours'])}. Later active blocks can leave the whole-matrix spend/projection incomplete without reopening this boundary."
        )
    lines += [
        report["scientific_limit"],
        "This text has not been posted; creep alerts require immediate owner relay, not a wait for the next boundary.",
        f"Report digest: {report['report_sha256']}",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument(
        "--journal", type=Path, default=ROOT / "results/R1/fidelity_watch/observations.jsonl"
    )
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--boundary-block", type=int)
    parser.add_argument("--workers", type=int, choices=(1, 2), default=2)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    output = local(args.output_dir)
    if not output.is_relative_to(ROOT / "logs"):
        parser.error("output must be a new directory under repository logs")
    report = build(
        args.matrix,
        receipt_root=args.receipt_root,
        journal=args.journal,
        previous=args.previous,
        boundary_block=args.boundary_block,
        workers=args.workers,
    )
    output.mkdir(parents=True, exist_ok=False)
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    rendered = text(report)
    (output / "lead-queue.txt").write_text(rendered)
    print(rendered, end="")
    return 2 if args.boundary_block is not None and not report["boundary_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
