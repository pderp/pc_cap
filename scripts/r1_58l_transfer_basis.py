"""Measured four-donor and all27 sampled-cost basis; unsigned sensitivity only.

This is deliberately not typed cost v4 or an admission/ceiling producer. It
exposes the arithmetic and provenance that must be reviewed before either.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from scripts import r1_58h_cost_receipt as profiles
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_d9_receipts as d9
from scripts.r1_d10a_review import ROOT, write_new


def seconds(value):
    if type(value) not in (float, int) or not math.isfinite(value) or value <= 0:
        raise ValueError("finite positive measured seconds required")
    return float(value)


def elapsed(text):
    parts = [float(p) for p in text.split(":")]
    if len(parts) not in (2, 3) or any(not math.isfinite(p) or p < 0 for p in parts):
        raise ValueError("invalid GNU elapsed time")
    return seconds(sum(p * 60**i for i, p in enumerate(reversed(parts))))


def sample_basis(row):
    _, recipe_path, manifest, result_path, result, receipt_path, receipt = row
    path = Path(receipt["report"]["path"]).resolve()
    if not path.is_relative_to(ROOT / "results") or "confirm" in path.parts:
        raise PermissionError("sample basis reads only unsealed result metadata")
    raw = path.read_bytes()
    if full.sha(path) != receipt["report"]["sha256"]:
        raise ValueError("sample report binding changed")
    report = json.loads(raw)
    drift = report["endpoints"]["drift"]
    positions = drift["scored_positions"]
    if (
        drift["status"] != "complete"
        or type(positions) is not int
        or positions <= 0
        or positions != drift["expected_positions"]
    ):
        raise ValueError("complete positive sampled population required")
    sources = [d9.ref(recipe_path), d9.ref(result_path), d9.ref(receipt_path), receipt["report"]]
    measured = []
    directory = result_path.parent / "phases"
    batches = sorted(directory.glob("batch-*.receipt.json"))
    if batches:
        verified = profiles.DurablePhaseJournal.verify(directory, receipt.get("journal"))
        records = []
        for path in batches:
            closed = json.loads(path.read_text())
            batch = json.loads(Path(closed["batch"]["path"]).read_text())
            sources.extend([d9.ref(path), closed["batch"], closed["intent"]])
            records.extend((Path(closed["batch"]["path"]), value) for value in batch["rows"])
        if [value for _, value in records] != verified:
            raise ValueError("verified phase inventory differs")
    else:
        records = [
            (path, json.loads(path.read_text())) for path in sorted(directory.glob("[0-9]*.json"))
        ]
    for path, value in records:
        if value.get("phase", "").startswith("drift:"):
            if value.get("status") != "ok":
                raise ValueError("failed sampled drift is not a successful cost donor")
            measured.append(seconds(value.get("phase_wall_seconds", value["wall_seconds"])))
            sources.append(d9.ref(path))
    if len(measured) != 1:
        raise ValueError("historical one-sampled-phase replacement needs exactly one phase")
    summary = result.get("phase_timer_summary", {}).get("drift")
    if summary and (
        summary["count"] != 1
        or summary["errors"] != 0
        or not math.isclose(summary["wall_seconds"], measured[0], abs_tol=1e-6)
    ):
        raise ValueError("sampled phase and result timer disagree")
    return dict(
        recipe=d9.ref(recipe_path),
        result=d9.ref(result_path),
        seconds=measured[0],
        positions=positions,
        seconds_per_position=measured[0] / positions,
        checkpoint=result["completed_checkpoint"],
        execution_profile={
            k: manifest.get(k)
            for k in (
                "integrity_profile",
                "integrity_batch_edits",
                "drift_implementation",
                "drift_batch_size",
            )
        },
        source_bindings=sources,
        qualification="SHA-bound historical phase observation; legacy phase files are not upgraded to modern process receipts",
    )


def replacement(old_solo, old_sample, new_sample, cadence, full_outer):
    """Replace the old single sample, retain all new samples, add full-only once."""
    old_solo, old_sample, new_sample, full_outer = map(
        seconds, (old_solo, old_sample, new_sample, full_outer)
    )
    if type(cadence) is not int or cadence not in (2, 3) or old_sample > old_solo:
        raise ValueError("invalid legacy single-sample replacement/cadence")
    nonvalidation = old_solo - old_sample
    solo = nonvalidation + cadence * new_sample + full_outer
    return dict(
        inherited_nonvalidation_seconds=nonvalidation,
        sampled_all_checkpoints_seconds=cadence * new_sample,
        full_outer_seconds=full_outer,
        solo_seconds=solo,
        solo_ceiling_seconds=1.5 * solo,
        two_worker_ceiling_seconds=1.15 * 1.5 * solo,
    )


def build(inventory_path):
    inventory_ref = d9.ref(inventory_path)
    inventory = d9.read_metadata(inventory_ref)
    if inventory.get("completed") != 4 or len(inventory["cells"]) != 4:
        raise ValueError("all four independently audited chain-S donors required")
    source_refs = {inventory_ref["path"]: inventory_ref["sha256"]}
    donors = {}
    for measured in inventory["cells"].values():
        if measured["status"] != "completed_vector_and_receipt_audit":
            raise ValueError("incomplete donor audit")
        for path, sha in measured["bindings_sha256"].items():
            if d9.sha(path) != sha:
                raise ValueError("chain-S donor changed: " + path)
            source_refs[path] = sha
        manifest = d9.read_metadata(measured["recipe"])
        key = manifest["cell"]["condition"] + ":" + manifest["cell"]["dataset"]
        cp = measured["sampled_checkpoint_count"]
        if cp != 2:
            raise ValueError("chain-S requires two sampled phases")
        process = elapsed(measured["host"]["fields"]["Elapsed (wall clock) time (h:mm:ss or m:ss)"])
        if process < measured["attempt_wall_seconds"]:
            raise ValueError("process wall cannot be shorter than its contained attempt")
        spec = manifest["full_validation"]
        sample_positions = spec["sample_windows"] * (spec["window_tokens"] - 1)
        donors[key] = dict(
            recipe=measured["recipe"],
            checkpoints=manifest["checkpoints"],
            measured_max_checkpoint=max(manifest["checkpoints"]),
            full_outer_seconds=measured["full_outer_seconds"],
            sampled_all_checkpoints_seconds=measured["sampled_all_checkpoints_seconds"],
            sampled_per_checkpoint_seconds=measured["sampled_all_checkpoints_seconds"] / cp,
            sampled_positions_per_checkpoint=sample_positions,
            full_positions=spec["expected_positions"],
            attempt_seconds=measured["attempt_wall_seconds"],
            process_seconds=process,
            process_minus_attempt_seconds=process - measured["attempt_wall_seconds"],
            measured_peak_host_mib=measured["host"]["measured_peak_host_mib"],
            measured_device_allocator_lifetime_peak_mib=measured[
                "device_allocator_lifetime_peak_mib"
            ],
            execution_profile={
                k: manifest.get(k)
                for k in (
                    "integrity_profile",
                    "integrity_batch_edits",
                    "drift_implementation",
                    "drift_batch_size",
                )
            },
        )
    if set(donors) != {
        f"{c}:{d}" for c in ("R1_learned_ff", "v0_stable") for d in ("mquake", "zsre")
    }:
        raise ValueError("wrong four-donor coordinate inventory")
    old_ref = d9.ref(ROOT / "manifests/revision_v1/cell_ceilings_v1.json")
    matrix_ref = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_3.json")
    old = d9.read_metadata(old_ref)
    matrix = d9.read_metadata(matrix_ref)
    source_refs.update({b["path"]: b["sha256"] for b in (old_ref, matrix_ref)})
    groups = profiles.completed_profiles()
    rows = {}
    for key, prior in sorted(old["cells"].items()):
        condition, dataset = key.split(":")
        sample = sample_basis(groups[(condition, dataset)][0])
        for b in sample["source_bindings"]:
            source_refs[b["path"]] = b["sha256"]
        family = "R1_learned_ff" if condition.startswith("R1_") else "v0_stable"
        eligible = [
            k
            for k in donors
            if k.startswith(family + ":")
            and (dataset == "counterfact" or k.endswith(":" + dataset))
        ]
        chosen = max(eligible, key=lambda k: donors[k]["full_outer_seconds"])
        donor = donors[chosen]
        rate = donor["sampled_per_checkpoint_seconds"] / donor["sampled_positions_per_checkpoint"]
        ratio = sample["seconds_per_position"] / rate
        # This scenario transfers total measured sampled-rate ratios, including
        # differences in implementation/reference work. Do not multiply S1 by
        # an additional assumed 3/2: that could count reference work twice.
        full_estimate = donor["full_outer_seconds"] * ratio
        cadence = 2 if dataset == "mquake" else 3
        calc = replacement(
            prior["solo_hours"] * 3600, sample["seconds"], sample["seconds"], cadence, full_estimate
        )
        rows[key] = dict(
            condition=condition,
            dataset=dataset,
            historical_sample=sample,
            full_donor=chosen,
            sampled_rate_ratio=ratio,
            execution_profiles_equal=sample["execution_profile"] == donor["execution_profile"],
            planned_checkpoint_count=cadence,
            formula=calc,
            reviewed=False,
            transfer_scope="sampled-rate ratio applied to full outer cost; proposal, not measured full cost",
            separate_reference_forward_unmeasured=condition.startswith("S1_"),
            thousand_record_state_unmeasured=dataset != "mquake",
        )
    totals = {}
    for name, cells in (("core", matrix["cells"]), ("extension", matrix["extension"]["cells"])):
        byrow = [rows[c["condition"] + ":" + c["dataset"]] for c in cells]
        solo = math.fsum(r["formula"]["solo_seconds"] for r in byrow) / 3600
        totals[name] = dict(
            cells=len(cells),
            solo_hours=solo,
            two_worker_process_hours=solo * 1.15,
            solo_ceiling_process_hours=solo * 1.5,
            two_worker_ceiling_process_hours=solo * 1.5 * 1.15,
        )
    for path, sha in source_refs.items():
        if d9.sha(path) != sha:
            raise ValueError("source changed during basis extraction: " + path)
    return dict(
        task="R1-58l",
        status="unsigned_transfer_sensitivity_not_cost_admission",
        lead_approved=False,
        producer=d9.ref(__file__),
        donor_inventory=inventory_ref,
        donors=donors,
        rows=rows,
        scenarios=totals,
        bindings_sha256=source_refs,
        formula="(historical solo - historical single sampled phase) + every planned sampled phase + transferred full outer phase; then 1.5 solo margin, 1.15 concurrency once",
        nonsignature_gaps=[
            "Transfer compatibility review: code/integrity profiles and sample/full reference work differ; sampled-rate scaling is a sensitivity, not a measured full assay.",
            "Four measured max-checkpoint-300 profiles do not measure 1000-record occupancy or its memory.",
            "S1's distinct original-base full forward is not measured; do not apply an extra multiplier on top of a ratio already containing reference work without decomposing it.",
            "Historical v1 solo costs are coarse estimates; their nonvalidation remainder is inherited, not remeasured. Startup, endpoint completeness, failed attempts and durable-write accounting must be reconciled before a new total is admitted.",
            "Refresh all27 host/endpoint evidence: temporal RSS attribution and remaining near/revision gaps persist; donor peaks cannot silently replace another condition's peak.",
            "Typed v4 validator/receipt, reviewed transfer evidence, final ceilings v2 and revised schedule remain to be constructed.",
            "Operator cost-admit still selects ceilings v1; final bundle requires scheduler matrix_sha256 field.",
        ],
        budget_process_hours=750,
        experimental_completion_date="2026-10-09",
        gpu_seconds=0,
        model_calls=0,
        qualification="No final receipt, approved transfer, production ceiling, launch authority or calendar-time guarantee is issued. Failure retries are additional charged process time, not included as a fixed expected count in this sensitivity.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "logs"):
        parser.error("new repository log path required")
    print(json.dumps(write_new(args.output, build(args.inventory)), indent=2))


if __name__ == "__main__":
    main()
