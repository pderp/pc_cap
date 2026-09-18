"""Refill D14b from the existing synthetic 330-cell fixture, never real outcomes.

The small validation contract is substituted only in this isolated rehearsal
process, as in R1-D14. New synthetic process envelopes cover the saved synthetic
one-second driver attempts; they are not measured execution receipts.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
from pathlib import Path
from unittest.mock import patch

from scripts import r1_63l_full_validation_contract as full
from scripts import r1_77f_scheduler as scheduler
from scripts import r1_d11_block_report as d11
from scripts import r1_d14_report as report

ROOT = d11.ROOT


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def verify_bindings(model, analysis):
    documents = dict(analysis=analysis, watch=model["watch"], accounting=model["accounting"])
    checked = 0
    for name, rows in model["tables"].items():
        for row, bindings in zip(rows, model["bindings"][name], strict=True):
            if set(row) != set(bindings):
                raise ValueError("report field missing its binding")
            for key, source in bindings.items():
                if "document" in source:
                    expected = report.resolve(documents[source["document"]], source["pointer"])
                    operation = source.get("operation")
                    if operation == "length":
                        expected = len(expected)
                    elif operation == "exp_below_709":
                        expected = (
                            math.exp(expected) if expected is not None and expected < 709 else None
                        )
                    elif operation == "exp_overflow_at_709":
                        expected = expected >= 709 if expected is not None else None
                    elif operation is not None:
                        raise ValueError("unknown field derivation")
                else:
                    expected = source["literal"]
                if row[key] != expected:
                    raise ValueError("report field differs from its binding")
                checked += 1
    return checked


def run(name):
    if not re.fullmatch(r"rehearsal-[a-z0-9-]+", name):
        raise ValueError("new rehearsal-* name required")
    output = ROOT / "logs/r1_round41" / name
    output.mkdir(exist_ok=False)
    analysis_path = ROOT / "logs/r1_round39/d14-complete-final/analysis.json"
    a = json.loads(analysis_path.read_text())
    matrix_path = Path(a["matrix_file"]["path"])
    matrix = json.loads(matrix_path.read_text())
    if matrix.get("synthetic") is not True or matrix.get("research_results") is not False:
        raise ValueError("explicitly synthetic fixture required")
    receipt_root = output / "synthetic-process-receipts"
    with patch.object(full, "production_contract", lambda: copy.deepcopy(matrix["full_validation"])):
        cells = d11.queue.ordered(matrix)
    for i, cell in enumerate(cells):
        directory = receipt_root / cell["cell_id"]
        start = dict(
            synthetic=True,
            cell_id=cell["cell_id"],
            matrix_sha256=a["matrix_file"]["sha256"],
            retry_policy=scheduler.POLICY,
            synthetic_worker=i % 2,
        )
        put(directory / "start.json", start)
        put(
            directory / "finish.json",
            dict(
                start,
                start_sha256=full.sha(directory / "start.json"),
                charged_process_wall_seconds=1.2,
                new_attempts=[str(Path(cell["result_dir"]) / "attempt-0000")],
                failure_class=None,
                exit_code=0,
            ),
        )
    journal = ROOT / "logs/r1_round39/d14-complete-final-synthetic-watch.jsonl"
    with patch.object(
        full, "production_contract", lambda: copy.deepcopy(matrix["full_validation"])
    ):
        snap = d11.build(
            matrix_path, receipt_root=receipt_root, journal=journal, workers=2, boundary_block=6
        )
        put(output / "synthetic-d11.json", snap)
        complete = report.run(
            analysis_path,
            output / "complete",
            journal=journal,
            accounting_report=output / "synthetic-d11.json",
            accounting_receipt_root=receipt_root,
        )
    data = json.loads((output / "complete/report-data.json").read_text())
    old = json.loads((ROOT / "logs/r1_round39/report-rehearsal-final/report-data.json").read_text())
    if (
        data["tables"]["primary"] != old["tables"]["primary"]
        or data["bindings"]["primary"] != old["bindings"]["primary"]
    ):
        raise ValueError("primary rows or bindings changed")
    if len(data["tables"]["historical_v2"]) != 24:
        raise ValueError("eight historical-v2 contrasts required")
    verified = verify_bindings(data, a)
    if (
        not math.isclose(snap["cost_ledger"]["charged_seconds"], 396)
        or snap["cost_ledger"]["uncovered_driver_seconds"] != 0
    ):
        raise ValueError("synthetic covered process costs should charge 396 seconds once")
    if not snap["boundary_ready"] or len(snap["complete_cells"]) != 330:
        raise ValueError("synthetic accounting boundary incomplete")
    partial_path = ROOT / "logs/r1_round39/d14-partial-v1/analysis.json"
    partial = report.run(partial_path, output / "partial")
    missing = json.loads((output / "partial/report-data.json").read_text())
    old_missing = json.loads(
        (ROOT / "logs/r1_round39/report-partial-final/report-data.json").read_text()
    )
    if missing["tables"]["primary"] != old_missing["tables"]["primary"]:
        raise ValueError("partial primary rows changed")
    verified_partial = verify_bindings(missing, json.loads(partial_path.read_text()))
    if len(missing["tables"]["incomplete"]) != 1:
        raise ValueError("one incomplete synthetic cell required")
    for section in ("complete", "partial"):
        if re.search(r"\{\{[A-Z0-9_]+\}\}", (output / section / "report.md").read_text()):
            raise ValueError("unbound template placeholder")
    result = dict(
        task="R1-D14b",
        synthetic=True,
        research_results=False,
        complete=complete,
        partial=partial,
        primary_rows_and_classifiers_unchanged=True,
        primary_rows=63,
        historical_rows=24,
        checked_complete_fields=verified,
        checked_partial_fields=verified_partial,
        synthetic_charged_seconds=snap["cost_ledger"]["charged_seconds"],
        synthetic_driver_seconds_not_added=330,
        complete_cells=330,
        complete_blocks=snap["inventory"]["complete_blocks"],
        accounting_status=data["accounting"]["status"],
        partial_accounting_status=missing["accounting"]["status"],
        unbound_placeholders=0,
        gpu_seconds=0,
        producer=full.ref(__file__),
    )
    put(output / "verification.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    print(json.dumps(run(parser.parse_args().name), indent=2))
