"""Read completed chain-S evidence without running a model or issuing cost admission.

This is a partial measurement inventory, not the revision-4 cost receipt/validator.
It deliberately leaves missing donors and transfer policies unresolved.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts import r1_63l_full_validation_contract as full
from scripts.r1_58i_host_peaks import direct_time
from scripts.r1_d10a_review import ROOT, write_new


def inspect(recipe_path, result_path):
    bindings = {}

    def read(path):
        path = Path(path).resolve()
        raw = path.read_bytes()
        h = __import__("hashlib").sha256(raw).hexdigest()
        bindings[str(path)] = h
        return json.loads(raw)

    recipe, result = read(recipe_path), read(result_path)
    recipe_binding = full.ref(recipe_path)
    if result.get("status") != "complete" or result["manifest_sha256"] != recipe_binding["sha256"]:
        raise ValueError("complete result bound to exact recipe required")
    spec = full.validate(recipe["full_validation"])
    previous = None
    reports = {}
    for n in recipe["checkpoints"]:
        receipt = read(result_path.parent / f"checkpoint-{n}.receipt.json")
        if (
            full.digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
            != receipt["receipt_sha256"]
            or receipt["manifest_sha256"] != recipe_binding["sha256"]
            or receipt["previous_receipt_sha256"] != previous
        ):
            raise ValueError("checkpoint receipt chain differs")
        report_path = result_path.parent / f"checkpoint-{n}.json"
        report = read(report_path)
        if (
            full.ref(report_path) != receipt["report"]
            or report["state_sha256"] != receipt["state_sha256"]
            or report["checkpoint"] != n
        ):
            raise ValueError("checkpoint report/state differs")
        reports[n] = report
        previous = receipt["receipt_sha256"]
    if result["last_receipt_sha256"] != previous or result["completed_checkpoint"] != max(reports):
        raise ValueError("result does not complete the declared cadence")
    n = max(reports)
    section = reports[n]["endpoints"]["full_validation"]
    summary = full.summary(
        section,
        spec,
        reports[n],
        result_path.parent / f"checkpoint-{n}.json",
        recipe_binding["sha256"],
        recipe["adapter_identity"],
        bindings,
    )
    if not summary["complete"]:
        raise ValueError("complete full-validation vectors required: " + summary["status"])
    time_path = (
        ROOT / f"results/R1/stage4_dev_cell_{recipe_path.name.removesuffix('.recipe.json')}.time"
    )
    host = direct_time(time_path, recipe_binding, result)
    bindings[str(time_path)] = host["source"]["sha256"]
    phases = result["phase_timer_summary"]
    if (
        phases["full_validation"]["count"] != 1
        or phases["full_validation"]["errors"] != 0
        or phases["drift"]["count"] != len(reports)
        or phases["drift"]["errors"] != 0
    ):
        raise ValueError("full/sample phase cadence differs")
    for path, h in bindings.items():
        if full.sha(path) != h:
            raise ValueError("measurement changed during read: " + path)
    return dict(
        status="completed_vector_and_receipt_audit",
        recipe=recipe_binding,
        attempt_wall_seconds=result["attempt_wall_seconds"],
        full_outer_seconds=phases["full_validation"]["wall_seconds"],
        full_inner_seconds=section["wall_seconds"],
        sampled_all_checkpoints_seconds=phases["drift"]["wall_seconds"],
        sampled_checkpoint_count=phases["drift"]["count"],
        full_sample_results=summary,
        host=host,
        device_allocator_lifetime_peak_mib=section["device_peak_mem_mib"],
        telemetry_scope=section["device_peak_scope"],
        bindings_sha256=bindings,
        qualification="development at measured occupancy; no cost transfer, primary inference, or launch admission",
    )


def inventory():
    results = {}
    for path in (ROOT / "results/R1/stage4_dev_cells").glob("*/attempt-*/result.json"):
        # Completed files are immutable. Live phase/report files are not consumed.
        result = json.loads(path.read_text())
        results.setdefault(result.get("manifest_sha256"), []).append(path)
    cells = {}
    for recipe in sorted((ROOT / "docs/tasks/R1-64g").glob("*.recipe.json")):
        matches = results.get(full.sha(recipe), [])
        if not matches:
            cells[recipe.stem] = dict(status="awaiting_completed_result", recipe=full.ref(recipe))
        elif len(matches) != 1:
            cells[recipe.stem] = dict(
                status="requires_attempt_accounting", result_paths=list(map(str, matches))
            )
        else:
            try:
                cells[recipe.stem] = inspect(recipe, matches[0])
            except (OSError, KeyError, TypeError, ValueError) as error:
                cells[recipe.stem] = dict(
                    status="invalid_or_incomplete_evidence", reason=str(error)
                )
    return dict(
        task="R1-58l",
        created_utc=datetime.now(UTC).isoformat(),
        status="partial_inventory_not_cost_admission",
        cells=cells,
        completed=sum(c["status"] == "completed_vector_and_receipt_audit" for c in cells.values()),
        expected_measurements=4,
        gpu_seconds=0,
        model_calls=0,
        producer=full.ref(__file__),
        consumer=full.ref(full.__file__),
        remaining=[
            "all four chain-S donors",
            "CounterFact sampled per-position transfer basis",
            "S1 separate-reference and 1000-state transfer/measurement basis",
            "remaining near-miss/revision gaps",
            "typed revision-4 validator",
            "cell ceilings v2 and process-hour projection",
            "review and exact signatures",
        ],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "logs"):
        parser.error("new repository log path required")
    print(json.dumps(write_new(args.output, inventory()), indent=2))
