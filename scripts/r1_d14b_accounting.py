"""Verify and join a D11/D13 accounting snapshot; no dispatch or state mutation.

A self-digest is insufficient: replay D11's read-only inventory and compare the
entire report except its generation timestamp and digest. Require an explicit
receipt root because the scientific analysis does not declare a queue root.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts import r1_d11_block_report as d11
from scripts import r1_d12_reprice as d12


def unavailable():
    return dict(
        status="unavailable_not_supplied",
        report=None,
        snapshot=None,
        source_bindings_sha256={},
        note="Execution accounting unavailable: no verified D11/D13 report supplied. "
        "Known spend, unknown costs, retries and host failures are not inferred from checkpoint timings.",
    )


def require_digest(document):
    expected = d11.watch.full.digest({k: v for k, v in document.items() if k != "report_sha256"})
    if document.get("report_sha256") != expected:
        raise ValueError("accounting report digest differs")


def references(value):
    if isinstance(value, dict):
        if set(value) == {"path", "sha256"}:
            yield value
        else:
            for item in value.values():
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def load(path, analysis, *, receipt_root=None):
    if path is None:
        if receipt_root is not None:
            raise ValueError("receipt root requires an accounting report")
        return unavailable()
    if receipt_root is None:
        raise ValueError("explicit accounting receipt root required")
    path = d11.local(path)
    binding = d11.ref(path)
    document = json.loads(path.read_bytes())
    require_digest(document)
    sources = {str(path): binding["sha256"]}
    if document.get("task") == "R1-D13" and document.get("mode") == "daily":
        snapshot = document["d11"]
        if d12.read_ref(document["d11_report"]) != snapshot:
            raise ValueError("D13 embedded and saved D11 differ")
        sources[document["d11_report"]["path"]] = document["d11_report"]["sha256"]
    elif document.get("task") == "R1-D11":
        snapshot = document
    else:
        raise ValueError("accounting input must be a D11 or daily D13 report")
    require_digest(snapshot)
    identity = snapshot["identity"]
    if identity["matrix"] != analysis["matrix_file"]:
        raise ValueError("accounting and analysis matrix identity differ")
    if d11.local(receipt_root) != d11.local(identity["receipt_root"]):
        raise ValueError("accounting receipt root differs")
    if set(r["cell_id"] for r in snapshot["inventory"]["queue"]) != set(
        c["cell_id"] for c in analysis["cells"]
    ):
        raise ValueError("accounting and analysis cell inventory differ")
    current_implementation = dict(
        report=d11.watch.full.ref(d11.__file__),
        queue=d11.watch.full.ref(d11.queue.__file__),
        watch=d11.watch.binding(),
    )
    if snapshot["implementation"] != current_implementation:
        raise ValueError("accounting implementation changed")
    for ref in references(current_implementation):
        sources[ref["path"]] = ref["sha256"]
    sources[str(Path(d12.__file__).resolve())] = d11.watch.full.sha(d12.__file__)
    previous = snapshot["previous"]
    if previous is not None:
        d12.read_ref(previous)
        sources[previous["path"]] = previous["sha256"]
    d12.verify_snapshot(dict(d11=snapshot, inputs={}))
    rebuilt = d11.build(
        identity["matrix"]["path"],
        receipt_root=receipt_root,
        journal=identity["journal"],
        previous=previous["path"] if previous else None,
        boundary_block=snapshot["boundary_block"],
        workers=identity["workers"],
    )
    ignore = {"generated_utc", "report_sha256"}
    if {k: v for k, v in rebuilt.items() if k not in ignore} != {
        k: v for k, v in snapshot.items() if k not in ignore
    }:
        raise ValueError("accounting independently replayed snapshot differs")
    sources.update(snapshot["accounting_sources_sha256"])
    sources.update(snapshot["inventory"]["sources_sha256"])
    matrix = identity["matrix"]
    sources[matrix["path"]] = matrix["sha256"]
    journal = Path(identity["journal"])
    if journal.exists():
        sources[str(journal)] = snapshot["watch"]["cursor"]["sha256"]
    for source, sha in sources.items():
        if (
            source in analysis.get("sources_sha256", {})
            and analysis["sources_sha256"][source] != sha
        ):
            raise ValueError("accounting and analysis source snapshot differ")
    result = dict(
        status="verified_independent_D11_replay",
        report=binding,
        snapshot=snapshot,
        source_bindings_sha256=sources,
        note="Known costs are lower bounds when attempts are unknown. Process envelopes "
        "replace covered driver attempts; both workers and failures are charged once. "
        "A processed boundary may contain retry-exhausted incomplete cells. "
        "Host failures below are explicit receipt classifications, not inferred crash causes.",
    )
    # Finish-receipt failure classes are not duplicated into D11's process list.
    # Bind and display them directly from the already verified membership scan.
    processes = []
    charged_finishes = {
        receipt["path"]
        for row in snapshot["cost_ledger"]["rows"]
        for receipt in row["process_receipts"]
    }
    for source in sorted(charged_finishes):
        finish = json.loads(Path(source).read_bytes())
        processes.append(
            dict(
                source=dict(path=source, sha256=sources[source]),
                cell_id=finish["cell_id"],
                failure_class=finish.get("failure_class"),
                failure_class_recorded="failure_class" in finish,
                exit_code=finish.get("exit_code"),
                charged_process_wall_seconds=finish["charged_process_wall_seconds"],
                receipt=finish,
            )
        )
    result["process_finishes"] = processes
    recheck(result)
    return result


def recheck(document):
    if document["snapshot"] is None:
        return
    d12.verify_snapshot(dict(d11=document["snapshot"], inputs={}))
    for source, sha in document["source_bindings_sha256"].items():
        if d11.watch.full.sha(source) != sha:
            raise ValueError("accounting source changed during rendering")


def add_tables(tables, document, at):
    if document is None or document["snapshot"] is None:
        doc = unavailable()
        tables.add(
            "accounting_summary",
            status=doc["status"],
            note=doc["note"],
            known_process_hours=None,
            unknown_cost_records=None,
            retries=None,
            host_failures=None,
            block_reconciliation=None,
        )
        return
    tables.documents["accounting"] = document

    def bound(pointer):
        return at(pointer, "accounting")

    s = "/snapshot"
    snapshot = document["snapshot"]
    tables.add(
        "accounting_summary",
        status=bound("/status"),
        report=bound("/report"),
        identity=bound(s + "/identity"),
        note=bound("/note"),
        **{
            k: bound(s + "/" + k)
            for k in (
                "total_cells",
                "complete_cells",
                "boundary_block",
                "boundary_ready",
                "boundary_unprocessed",
                "boundary_gap_cells",
                "boundary_known_process_hours",
                "issues",
            )
        },
        **{k: bound(s + "/inventory/cost/" + k) for k in snapshot["inventory"]["cost"]},
        ledger_basis=bound(s + "/cost_ledger/basis"),
        charged_seconds=bound(s + "/cost_ledger/charged_seconds"),
        uncovered_driver_seconds=bound(s + "/cost_ledger/uncovered_driver_seconds"),
    )
    for name, rows, pointer in (
        ("accounting_cells", snapshot["inventory"]["queue"], s + "/inventory/queue"),
        ("accounting_blocks", snapshot["inventory"]["blocks"], s + "/inventory/blocks"),
        ("accounting_costs", snapshot["cost_ledger"]["rows"], s + "/cost_ledger/rows"),
        ("accounting_process_finishes", document["process_finishes"], "/process_finishes"),
    ):
        for i, row in enumerate(rows):
            tables.add(name, **{k: bound(f"{pointer}/{i}/{k}") for k in row})
