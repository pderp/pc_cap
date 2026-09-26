"""R1-D14f: prepare/execute read-only scientific reports after the 270-cell halt.

Default is a dry run. No scheduler, signal, lease or reconciliation mutation.
The owner supplies the existing D11 block-5 report and their reconciliation note.
The full block has 60 cells: its 15 deliberately unrun CF cells keep D11's
boundary_ready false. Check the exact 270 prefix instead of forging completion.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import os
import site
import sys
from pathlib import Path

from scripts import r1_d11_block_report as d11
from scripts import repo_size_policy

from aw.comparator_report import MATRIX, RECEIPTS, ROOT, analyze, summarize
from aw.pc_v0_report import sha
from aw.presentation_claims import refresh_text

ASSETS = ROOT.parent / "assets"
JOURNAL = ROOT / "results/R1/fidelity_watch/observations.jsonl"
DOCUMENT = ROOT / "docs/R1_stage4_report_comparators.md"
LEDGER = ROOT / "docs/talk_claim_ledger_v7.md"
PREVIOUS = ROOT / "logs/R1/reports/comparators-225/report.json"
TAILS = ASSETS / "presentation-materials/figures/tails"


def validate_boundary(report, cells, matrix_sha):
    selected = {c["cell_id"] for c in cells[:270]}
    intentionally_unrun = {c["cell_id"] for c in cells[270:] if c["block_number"] == 5}
    if (
        len(cells) != 330
        or len(selected) != 270
        or len(intentionally_unrun) != 15
        or report["identity"]["matrix"]["sha256"] != matrix_sha
        or report["boundary_block"] != 5
    ):
        raise ValueError("wrong matrix or block-5 boundary")
    if set(report["complete_cells"]) != selected:
        raise ValueError("requires exactly the completed 270-cell prefix")
    if set(report["boundary_unprocessed"]) != intentionally_unrun or report["boundary_gap_cells"]:
        raise ValueError(
            "unprocessed cells must be precisely the 15 planned S1_literal CounterFact omissions"
        )
    if (
        report["inventory"]["cost"]["unknown_attempts"]
        or report["cost_ledger"]["uncovered_driver_seconds"]
    ):
        raise ValueError("unreconciled process costs")
    if report["watch"]["missing_completed_cells"] or report["issues"]:
        raise ValueError("unresolved report accounting/watch issue")
    if any(r["observed"]["status"] == "invalid" for r in report["inventory"]["queue"]):
        raise ValueError("invalid cell evidence")


def tail_gate():
    """Catch the observed ES99/percentile mix-up before overwriting published figures."""
    import numpy as np

    from aw import tail_figures

    x = np.zeros(1000)
    x[0] = 10
    s = tail_figures.statistics(x)
    if not np.isclose(s.get("es99_positive", float("nan")), 1.0):
        raise ValueError(
            "HT-13 ES99 is still a percentile; Claude must repair tail_figures before refresh publication"
        )
    if "harm is rare and heavy-tailed" in Path(tail_figures.__file__).read_text():
        raise ValueError(
            "HT-13 figure title still asserts an unestablished heavy-tail family; owner correction pending"
        )


def current_inventory():
    cells = d11.queue.ordered(json.loads(MATRIX.read_bytes()))
    inv = d11.queue.inventory(
        json.loads(MATRIX.read_bytes()), receipt_root=RECEIPTS, matrix_hash=sha(MATRIX), workers=2
    )
    complete = [r["cell_id"] for r in inv["queue"] if r["observed"]["artifact_complete"]]
    return cells, inv, complete


def prepare(output, boundary=None, reconciliation=None):
    cells, inv, complete = current_inventory()
    plan = dict(
        mode="dry-run",
        observed_complete_cells=len(complete),
        target_complete_cells=270,
        missing_prefix_cells=[c["cell_id"] for c in cells[:270] if c["cell_id"] not in complete],
        unknown_cost_records=len(inv["cost"]["unknown_attempts"]),
        output=str(Path(output).resolve()),
        writes_performed=False,
        prerequisite="Owner reconciliation note + current verified D11 block-5 report, exact 270 completed; queue remains stopped",
        expected_block5_unprocessed=15,
        reason_note="DEC-074b omits S1_literal CounterFact and extension; DEC-066 already omitted MQuAKE comparators and its 1000-edit endpoint.",
        steps=[
            "analyze comparator prefix 270 into a NEW directory",
            "publish with changes since 225 into staged report",
            "regenerate comparator figures",
            "regenerate HT-13 tails from unchanged full-validation vectors",
            "refresh only comparator-dependent claim rows, preserving PC and conceptual rows",
            "publish comparator document and ledger after validation; split oversized JSON; retain unavailable.csv",
        ],
        commands=dict(tails=[sys.executable, "-m", "aw.tail_figures", "--out", str(TAILS)]),
    )
    try:
        tail_gate()
        plan["tail_helper"] = "ready"
    except ValueError as e:
        plan["tail_helper"] = str(e)
    if boundary:
        report = json.loads(Path(boundary).read_bytes())
        try:
            validate_boundary(report, cells, sha(MATRIX))
            plan["boundary"] = "shape ready; execute revalidates all bindings and current receipts"
        except ValueError as e:
            plan["boundary"] = str(e)
    else:
        plan["boundary"] = "owner report pending"
    plan["reconciliation"] = str(reconciliation) if reconciliation else "owner note pending"
    return plan


def verify_posted(boundary, reconciliation):
    boundary, reconciliation = Path(boundary).resolve(), Path(reconciliation).resolve()
    if not boundary.is_relative_to(ROOT) or not reconciliation.is_relative_to(ROOT):
        raise ValueError("operational records belong in pc_cap")
    if not reconciliation.read_text().strip():
        raise ValueError("empty owner reconciliation note")
    report = json.loads(boundary.read_bytes())
    if report["report_sha256"] != d11.watch.full.digest(
        {k: v for k, v in report.items() if k != "report_sha256"}
    ):
        raise ValueError("posted boundary digest differs")
    if report["identity"]["receipt_root"] != str(RECEIPTS) or report["identity"]["journal"] != str(
        JOURNAL
    ):
        raise ValueError("posted boundary queue/watch identity differs")
    cells = d11.queue.ordered(json.loads(MATRIX.read_bytes()))
    validate_boundary(report, cells, sha(MATRIX))
    if d11.accounting_snapshot(cells, RECEIPTS) != report["accounting_sources_sha256"]:
        raise ValueError("queue changed after posted boundary")
    for p, h in report["inventory"]["sources_sha256"].items():
        if sha(p) != h:
            raise ValueError("boundary cell evidence changed")
    raw = JOURNAL.read_bytes()
    cursor = report["watch"]["cursor"]
    if (
        sha(JOURNAL) != cursor["sha256"]
        or len(raw) != cursor["bytes"]
        or len(raw.splitlines()) != cursor["events"]
    ):
        raise ValueError("watch changed after boundary")
    d11.read_watch(JOURNAL)
    return dict(
        boundary=dict(path=str(boundary), sha256=sha(boundary)),
        reconciliation=dict(path=str(reconciliation), sha256=sha(reconciliation)),
    )


def execute(output, boundary, reconciliation):
    if os.environ.get("JAX_PLATFORMS") != "cpu" or os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("run report refresh in explicit CPU-only environment")
    out = Path(output).resolve()
    if not out.is_relative_to(ROOT / "logs/R1/reports") or out.exists():
        raise ValueError("new report directory required below logs/R1/reports")
    evidence = verify_posted(boundary, reconciliation)
    tail_gate()  # refuse known figure defects before writing any published output
    published_before = {str(p): sha(p) for p in (DOCUMENT, LEDGER)}
    analyze(out, 270)
    summarize(out, out / "staged-comparators.md", previous=PREVIOUS)
    report = json.loads((out / "report.json").read_bytes())
    if report["complete_cells"] != 270:
        raise ValueError("analysis did not produce 270 complete cells")
    ledger_text = refresh_text(LEDGER.read_text(), out / "report.json")
    # Matplotlib from the existing plotting environment, appended after project deps.
    site.addsitedir(str(ASSETS / "envs/status-paper-20260911/lib/python3.12/site-packages"))
    from aw.plot_comparators import render

    render(out, ASSETS / "presentation-materials/figures/comparators-270")
    # Same process imports retain the project NumPy/JAX; invoke the unchanged HT-13 main.
    from aw import tail_figures

    old = sys.argv
    try:
        sys.argv = ["aw.tail_figures", "--out", str(TAILS)]
        tail_figures.main()
    finally:
        sys.argv = old
    if evidence != verify_posted(boundary, reconciliation):
        raise ValueError("owner evidence changed during refresh")
    if any(sha(p) != digest for p, digest in published_before.items()):
        raise ValueError("published document changed concurrently; staged result retained")
    DOCUMENT.write_text((out / "staged-comparators.md").read_text())
    LEDGER.write_text(ledger_text)
    # Preserve hash-bound originals locally. Per-output .gitignore avoids staging >45 MB.
    large = []
    for p in sorted(out.rglob("*.json")):
        if p.stat().st_size > repo_size_policy.LIMIT:
            repo_size_policy.split(p, keep=True)
            large.append("/" + str(p.relative_to(out)))
    if large:
        (out / ".gitignore").write_text("\n".join(large) + "\n")
    result = dict(
        status="complete",
        **evidence,
        complete_cells=270,
        published={str(p): sha(p) for p in (DOCUMENT, LEDGER)},
        unavailable_inventory=dict(
            path=str(out / "unavailable.csv"), sha256=sha(out / "unavailable.csv")
        ),
        scientific_note="No new experimental measurement or operational action; MQuAKE omissions retain DEC-066.",
    )
    (out / "refresh.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--boundary-report")
    p.add_argument("--reconciliation")
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()
    if a.execute:
        if not a.boundary_report or not a.reconciliation:
            p.error("execute requires the posted boundary report and owner reconciliation note")
        r = execute(a.output, a.boundary_report, a.reconciliation)
    else:
        r = prepare(a.output, a.boundary_report, a.reconciliation)
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
