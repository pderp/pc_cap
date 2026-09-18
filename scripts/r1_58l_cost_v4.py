"""Typed revision-4 cost preparation and validation; never issue an admission signature.

All timing transfers stay distinct from measured scientific outcomes. Historical
nonvalidation estimates remain estimates. Current process-hour ceilings charge
failed attempts and retries; no expected retry count is invented.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.r1_58i_host_peaks import direct_time, match_monitor
from scripts.r1_58l_transfer_basis import elapsed, sample_basis
from scripts.r1_d10a_review import ROOT, write_new

BASIS = ROOT / "logs/r1_round35/transfer-basis-v2.json"
PRIOR = ROOT / "docs/tasks/R1-cost-after-chain-R.json"
REVIEWS = ROOT / "docs/tasks/R1-58l-reviewed-transfers-v4.json"
MATRIX = ROOT / "manifests/revision_v1/run_matrix_v5_2_D_4.json"
FAILURES = "Charge actual process elapsed for every attempt, including startup, validation, failures, watchdog stops and retries. Retry once from the last certified checkpoint, then incomplete; never subtract failed work or count overlap as free time."


def read(binding):
    path = Path(binding["path"])
    if d9.sha(path) != binding["sha256"]:
        raise ValueError("v4 cost source changed: " + str(path))
    return json.loads(path.read_text())


def sources(basis):
    for path, expected in basis["bindings_sha256"].items():
        if d9.sha(path) != expected:
            raise ValueError("sample/full donor source changed: " + path)


def donor_map(basis):
    inventory = read(basis["donor_inventory"])
    mapped = {}
    if inventory["completed"] != 4:
        raise ValueError("four complete full-validation measurements required")
    for row in inventory["cells"].values():
        recipe = read(row["recipe"])
        key = recipe["cell"]["condition"] + ":" + recipe["cell"]["dataset"]
        result_paths = [p for p in row["bindings_sha256"] if p.endswith("/result.json")]
        if len(result_paths) != 1:
            raise ValueError("unique full donor result required")
        result = read(dict(path=result_paths[0], sha256=row["bindings_sha256"][result_paths[0]]))
        timers = result["phase_timer_summary"]
        if (
            result["manifest_sha256"] != row["recipe"]["sha256"]
            or result["status"] != "complete"
            or timers["full_validation"]["count"] != 1
            or timers["full_validation"]["errors"] != 0
            or timers["full_validation"]["wall_seconds"] != row["full_outer_seconds"]
            or basis["donors"][key]["full_outer_seconds"] != row["full_outer_seconds"]
        ):
            raise ValueError("full donor result and transfer basis disagree")
        timed = direct_time(row["host"]["source"]["path"], row["recipe"], result)
        if timed["measured_peak_host_mib"] != row["host"]["measured_peak_host_mib"]:
            raise ValueError("full donor direct host peak differs")
        if any(
            timers[k]["count"] != 1 or timers[k]["errors"] != 0 for k in ("near_miss", "revision")
        ):
            raise ValueError("measured near/revision phases must occur once at final checkpoint")
        mapped[key] = {
            **row,
            "endpoint_phase_seconds_total_verified": sum(
                timers[k]["wall_seconds"] for k in ("near_miss", "revision")
            ),
        }
    if set(mapped) != set(basis["donors"]):
        raise ValueError("four-donor identity inventory differs")
    return mapped


def full_cost(key, basis):
    condition, dataset = key.split(":")
    row = basis["rows"][key]
    if condition.startswith("S1_"):
        # DEC-065(ii) prices the whole three-forward full phase at 1.5 times
        # the two-forward v0 phase. Do not multiply an S1 sampled-rate ratio too.
        donor_key = "v0_stable:" + dataset
        if dataset == "counterfact":
            seconds, _, _ = full_cost(donor_key, basis)
        else:
            seconds = basis["donors"][donor_key]["full_outer_seconds"]
        return seconds * 1.5, "reviewed_S1_extra_reference_1p5_v0_DEC065ii", donor_key
    if dataset == "counterfact":
        return (
            row["historical_sample"]["seconds_per_position"] * 245237,
            "reviewed_CounterFact_sample_rate_DEC065i",
            key,
        )
    if key in basis["donors"]:
        return basis["donors"][key]["full_outer_seconds"], "measured_full_at_300", key
    donor = row["full_donor"]
    return (
        basis["donors"][donor]["full_outer_seconds"] * row["sampled_rate_ratio"],
        "reviewed_family_sample_rate_scenario_DEC065iv",
        donor,
    )


def calculation(key, basis, evidence, endpoint_seconds, process_floor=0.0):
    row = basis["rows"][key]
    count = row["planned_checkpoint_count"]
    old = row["formula"]["inherited_nonvalidation_seconds"]
    # The v1 estimate included its supplied endpoint work once; replace that
    # component, just as we replace its single sampled phase, instead of hiding
    # missing endpoint work inside the margin. v1 remains a coarse base estimate.
    remainder = old - evidence["endpoint_phase_seconds_total"]
    if remainder < 0:
        raise ValueError("negative inherited nonvalidation remainder: " + key)
    full_seconds, kind, donor = full_cost(key, basis)
    sample = count * row["historical_sample"]["seconds"]
    # The installed backend runs near-miss/revision at the final checkpoint
    # only. Sampled drift has the separate two/three-checkpoint cadence.
    endpoints = endpoint_seconds
    startup = 30.0  # v1 explicit construction/admission estimate, now itemized
    component_solo = remainder + sample + endpoints + full_seconds + startup
    solo = max(component_solo, process_floor)
    return dict(
        historical_solo_seconds=old + row["historical_sample"]["seconds"],
        removed_single_sample_seconds=row["historical_sample"]["seconds"],
        removed_supplied_endpoint_seconds=evidence["endpoint_phase_seconds_total"],
        inherited_nonvalidation_seconds=remainder,
        sampled_checkpoint_count=count,
        sampled_all_checkpoints_seconds=sample,
        endpoint_seconds_per_checkpoint=endpoint_seconds,
        endpoint_checkpoint_count=1,
        endpoint_cadence="final_only; r1_77b_sealed_backend.run_cell",
        endpoints_all_checkpoints_seconds=endpoints,
        startup_validation_seconds_estimate=startup,
        full_outer_seconds=full_seconds,
        full_cost_kind=kind,
        full_donor=donor,
        full_cost_reviewed=True,
        component_solo_seconds=component_solo,
        measured_whole_process_floor_seconds=process_floor,
        measured_floor_adjustment_seconds=solo - component_solo,
        occupancy_transfer_reviewed=True,
        occupancy_rule="DEC-065(iii): full-phase occupancy-independent 300 to 1000; assumption, not measurement",
        solo_seconds=solo,
        ceiling_seconds=solo * 1.5,
        two_worker_ceiling_seconds=solo * 1.5 * 1.15,
    )


def totals(rows, matrix, old):
    result = {}
    for name, cells in (
        ("core", matrix["cells"]),
        ("extension", matrix["extension"]["cells"]),
        ("combined", matrix["cells"] + matrix["extension"]["cells"]),
    ):
        keys = [c["condition"] + ":" + c["dataset"] for c in cells]
        solo = math.fsum(rows[k]["solo_seconds"] for k in keys) / 3600
        without_full = (
            math.fsum(rows[k]["solo_seconds"] - rows[k]["full_outer_seconds"] for k in keys) / 3600
        )
        historical = math.fsum(old["cells"][k]["solo_hours"] for k in keys)
        result[name] = dict(
            cells=len(keys),
            solo_hours=solo,
            two_worker_process_hours=solo * 1.15,
            ceiling_process_hours=solo * 1.5 * 1.15,
            estimated_elapsed_hours_at_1p65_throughput=solo / 1.65,
            revised_without_full_process_hours=without_full * 1.15,
            historical_without_full_process_hours=historical * 1.15,
            headroom_to_750_at_expected_process_hours=750 - solo * 1.15,
            headroom_to_750_at_ceiling_process_hours=750 - solo * 1.5 * 1.15,
        )
    return result


def host_value(key, evidence, hosts, donors):
    host = hosts["rows"][key]
    if host["method"] == "direct_gnu_time":
        for name in ("source", "snapshot"):
            if d9.ref(host[name]["path"]) != host[name]:
                raise ValueError("host time snapshot changed")
        observed = direct_time(host["source"]["path"], host["recipe"], read(host["result"]))
        value = observed["measured_peak_host_mib"]
    elif host["method"] == "monitor_temporal_match":
        observed = match_monitor(host["window"], read(host["monitor_excerpts"]))
        if observed.get("process_key") != host["process_key"]:
            raise ValueError("host temporal attribution differs")
        value = observed.get("measured_peak_host_mib")
    else:
        raise ValueError("unmeasured host source not allowed")
    if value != host["measured_peak_host_mib"] or value != evidence["measured_peak_host_mib"]:
        raise ValueError("host source observation differs")
    device = evidence["measured_peak_device_mib"]
    if key in donors:
        donor = donors[key]
        value = max(value, donor["host"]["measured_peak_host_mib"])
        device = max(device, donor["device_allocator_lifetime_peak_mib"])
    return value, device


def expected_inputs(receipt):
    b = receipt["bindings"]
    basis, prior, reviews, matrix = [
        read(b[k]) for k in ("transfer_basis", "prior_cost_source", "transfer_reviews", "matrix")
    ]
    sources(basis)
    if (
        reviews.get("full_validation_reviewed") is not True
        or reviews.get("endpoint_transfers_reviewed") is not True
        or reviews.get("full_validation_decision") != "DEC-065"
        or not reviews.get("full_validation_decision_row", "").startswith("| DEC-065 |")
        or reviews.get("endpoint_approval_quote") != "Approve these endpoint-cost transfers"
    ):
        raise ValueError("explicit reviewed full/endpoint transfers required")
    old = read(b["historical_ceilings"])
    hosts = read(b["host_peak_evidence"])
    donors = donor_map(basis)
    previous = {c["condition"] + ":" + c["dataset"]: read(c["measurement"]) for c in prior["cells"]}
    expected_keys = {
        c["condition"] + ":" + c["dataset"] for c in matrix["cells"] + matrix["extension"]["cells"]
    }
    if (
        set(previous) != set(basis["rows"])
        or set(previous) != set(old["cells"])
        or len(previous) != 27
        or not expected_keys <= set(previous)
    ):
        raise ValueError("all27 source cost coordinates required")
    calculations = {}
    memory = {}
    for key, evidence in previous.items():
        observed = basis["rows"][key]["historical_sample"]
        recipe_path, result_path = (Path(observed[k]["path"]) for k in ("recipe", "result"))
        receipt_path = result_path.parent / "checkpoint-300.receipt.json"
        reconstructed = sample_basis(
            (
                None,
                recipe_path,
                read(observed["recipe"]),
                result_path,
                read(observed["result"]),
                receipt_path,
                json.loads(receipt_path.read_text()),
            )
        )
        if reconstructed != observed:
            raise ValueError("sampled cost observation differs from its phase journal: " + key)
        value = evidence["endpoint_phase_seconds_total"]
        if key in donors:
            value = max(value, donors[key]["endpoint_phase_seconds_total_verified"])
        if evidence["full_endpoint_evidence_status"] != "complete":
            dataset = key.split(":")[1]
            review = reviews["endpoint_donors"][dataset]
            eligible = {
                k: e
                for k, e in previous.items()
                if k.endswith(":" + dataset) and e["full_endpoint_evidence_status"] == "complete"
            }
            chosen = max(eligible, key=lambda k: eligible[k]["endpoint_phase_seconds_total"])
            value = eligible[chosen]["endpoint_phase_seconds_total"]
            if review != dict(key=chosen, seconds=value):
                raise ValueError("reviewed maximum same-dataset endpoint donor differs")
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError("positive endpoint cost required")
        process_floor = (
            elapsed(donors[key]["host"]["fields"]["Elapsed (wall clock) time (h:mm:ss or m:ss)"])
            if key in donors
            else 0.0
        )
        calculations[key] = calculation(key, basis, evidence, value, process_floor)
        memory[key] = host_value(key, evidence, hosts, donors)
    return calculations, memory, totals(calculations, matrix, old), previous, basis, donors


def validate_supplement(receipt):
    """Recompute every transferred component, memory source, ceiling and projection."""
    required = {
        "transfer_basis",
        "prior_cost_source",
        "transfer_reviews",
        "matrix",
        "historical_ceilings",
        "host_peak_evidence",
        "cell_ceilings",
    }
    if not required <= set(receipt.get("bindings", {})):
        raise ValueError("revision4 requires its explicit transfer/source supplement")
    rows, memory, projection, previous, _, _ = expected_inputs(receipt)
    ceilings = read(receipt["bindings"]["cell_ceilings"])
    if ceilings.get("schema_version") != 2 or set(ceilings["cells"]) != set(rows):
        raise ValueError("v4 requires exact all27 ceilings v2")
    if receipt.get("projection") != projection:
        raise ValueError("v4 process-hour projection differs")
    if (
        receipt.get("failure_policy") != FAILURES
        or receipt.get("failures_included") is not True
        or receipt.get("memory_ceiling_factor") != 1.5
        or receipt.get("two_worker_wall_ceiling_multiplier") != 1.15
    ):
        raise ValueError("cost/failure/concurrency policy differs")
    keys = [c["condition"] + ":" + c["dataset"] for c in receipt["cells"]]
    if len(keys) != len(set(keys)) or set(keys) != set(rows):
        raise ValueError("all27 unique v4 rows required")
    for c, key in zip(receipt["cells"], keys, strict=True):
        e = read(c["measurement"])
        if e["cost_components"] != rows[key] or ceilings["cells"][key] != rows[key]:
            raise ValueError("v4 recomputed cost/ceiling differs: " + key)
        measured = previous[key]["full_endpoint_evidence_status"] == "complete"
        if e.get("endpoint_cost_kind") != (
            "measured" if measured else "reviewed_same_dataset_transfer"
        ):
            raise ValueError("endpoint measurement/transfer label differs: " + key)
        if e.get("endpoint_inventory") != previous[key]["endpoint_inventory"]:
            raise ValueError("cost transfer must not invent endpoint measurements")
        h, d = memory[key]
        if e["measured_peak_host_mib"] != h or e["measured_peak_device_mib"] != d:
            raise ValueError("v4 conservative measured memory inventory differs: " + key)
    return dict(typed_cost_rows=27, transferred_endpoint_rows=14, cost_evidence_complete=True)


def build(output, evidence_dir, ceilings_path):
    previous_ref = d9.ref(PRIOR)
    previous = read(previous_ref)
    receipt = copy.deepcopy(previous)
    receipt.update(
        receipt_revision=4,
        task="R1-58l",
        lead_approved=False,
        lead_signature=dict(name=None, date=None),
        status="unsigned_cost_basis_complete",
        pending_evidence=[],
        full_validation_evidence_status="complete",
        full_endpoint_cost_basis_reviewed=True,
        startup_validation_evidence_status="explicit_estimate",
        startup_validation_seconds_per_cell_estimate=30,
        failure_policy=FAILURES,
        failures_included=True,
        memory_ceiling_factor=1.5,
        two_worker_wall_ceiling_multiplier=1.15,
        prior_receipt=previous_ref,
        authority_note="Reviewed cost estimates only; no admission, experimental outcome, or launch authority.",
        host_policy_note="Maximum measured same-condition host/device observation across historical and chain-S evidence. Temporal monitor RSS is sampled and uniquely matched, not an exact argv attribution or guaranteed true peak. No 1000-state or distinct S1-full memory measurement is invented.",
    )
    receipt.pop("validation_inventory", None)
    receipt["bindings"] = {
        k: d9.ref(p)
        for k, p in dict(
            transfer_basis=BASIS,
            prior_cost_source=PRIOR,
            transfer_reviews=REVIEWS,
            matrix=MATRIX,
            historical_ceilings=ROOT / "manifests/revision_v1/cell_ceilings_v1.json",
            host_peak_evidence=previous["host_peak_evidence"]["path"],
            concurrency_policy=ROOT / "docs/R1_stage4_queue_concurrency_v2.md",
            execution_plan=ROOT / "docs/R1_execution_plan_v3.md",
            historical_execution_plan=ROOT / "docs/R1_execution_plan_v2.md",
            producer=Path(__file__),
            validator=ROOT / "scripts/r1_58h_cost_contract.py",
            host_producer=ROOT / "scripts/r1_58i_host_peaks.py",
            donor_validator=ROOT / "scripts/r1_58l_measurement_inventory.py",
            measurement_parser=ROOT / "scripts/r1_58h_cost_receipt.py",
            endpoint_executor=ROOT / "scripts/r1_77b_sealed_backend.py",
        ).items()
    }
    rows, memory, projection, old_evidence, basis, donors = expected_inputs(receipt)
    receipt["projection"] = projection
    receipt["expected_process_hours"] = projection["combined"]["two_worker_process_hours"]
    receipt["expected_process_hours_basis"] = (
        "Recomputed exact DEC-065 formulas plus all checkpoints/endpoints and explicit startup; 1.15 concurrency once. Older 483.7013h scenario preserved separately."
    )
    receipt["earlier_full_validation_sensitivity"] = basis["scenarios"]
    receipt["full_validation"] = read(d9.ref(MATRIX))["full_validation"]
    receipt.update(matrix=d9.ref(MATRIX), protocol=read(d9.ref(MATRIX))["protocol"])
    receipt["bindings"]["cell_ceilings"] = write_new(
        ceilings_path,
        dict(
            schema_version=2,
            task="R1-58l",
            status="unsigned_cost_estimates",
            definition="ceiling_seconds = 1.5 * solo_seconds; scheduler applies 1.15 once for two workers",
            transfers=receipt["bindings"]["transfer_reviews"],
            cells=rows,
        ),
    )
    directory = Path(evidence_dir)
    directory.mkdir(parents=True, exist_ok=False)
    for c in receipt["cells"]:
        key = c["condition"] + ":" + c["dataset"]
        e = copy.deepcopy(old_evidence[key])
        measured = e["full_endpoint_evidence_status"] == "complete"
        h, d = memory[key]
        e.update(
            pending=[],
            full_endpoint_evidence_status="complete",
            endpoint_cost_kind="measured" if measured else "reviewed_same_dataset_transfer",
            cost_components=rows[key],
            measured_peak_host_mib=h,
            measured_peak_device_mib=d,
            evidence_status_note="Complete costing basis includes reviewed transfers; endpoint_inventory remains actual measured coverage.",
            full_memory_note="300-record observations with 1.5 factor, not a measured full/S1/1000-record upper bound",
        )
        if "endpoint_transfer_proposal" in e:
            e["endpoint_transfer_proposal"].update(
                reviewed=True, review=receipt["bindings"]["transfer_reviews"]
            )
        e["source_bindings"] += [
            receipt["bindings"]["transfer_basis"],
            receipt["bindings"]["transfer_reviews"],
        ]
        e["source_bindings"] += basis["rows"][key]["historical_sample"]["source_bindings"]
        if key in donors:
            e["source_bindings"] += [
                dict(path=p, sha256=h) for p, h in donors[key]["bindings_sha256"].items()
            ]
        c.update(
            wall_seconds=rows[key]["ceiling_seconds"],
            peak_host_mib=h * 1.5,
            peak_device_mib=d * 1.5,
            measurement=write_new(directory / (key.replace(":", "-") + ".json"), e),
        )
    from scripts.r1_58h_cost_contract import validate

    validate(receipt)
    return write_new(output, receipt)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--ceilings", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(build(a.output, a.evidence_dir, a.ceilings), indent=2))


if __name__ == "__main__":
    main()
