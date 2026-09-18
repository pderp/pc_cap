"""Assemble unsigned typed costs from bound profile artifacts, retaining evidence gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.r1_49j_normative_closure import PROTOCOL
from scripts.r1_68b_integrity_runtime import DurablePhaseJournal
from scripts.r1_d10a_review import ROOT, write_new


def completed_profiles():
    recipes = {}
    for p in sorted((ROOT / "docs/tasks").rglob("*.recipe.json")):
        m = json.loads(p.read_text())
        if m.get("mode") == "stage4_development_cell" and not m.get("test_fixture"):
            recipes[d9.sha(p)] = (p, m)
    groups = {}
    for p in sorted((ROOT / "results/R1/stage4_dev_cells").glob("*/attempt-*/result.json")):
        value = json.loads(p.read_text())
        identity = value.get("manifest_sha256")
        if (
            identity not in recipes
            or value.get("status") != "complete"
            or value.get("completed_checkpoint") != 300
        ):
            continue
        path, manifest = recipes[identity]
        cell = manifest["cell"]
        if value["cell"] != cell:
            raise ValueError("profile/result coordinates differ")
        receipt_path = p.parent / "checkpoint-300.receipt.json"
        receipt = json.loads(receipt_path.read_text())
        if (
            receipt["receipt_sha256"]
            != d9.core.content_digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
            or value["last_receipt_sha256"] != receipt["receipt_sha256"]
            or receipt["manifest_sha256"] != identity
            or d9.ref(receipt["report"]["path"]) != receipt["report"]
            or d9.ref(manifest["payload"]["path"]) != manifest["payload"]
        ):
            raise ValueError("profile receipt/payload identity differs")
        # Declared provenance precedence, never scores: full endpoint, corrected MQ,
        # latest recipe generations, then lexical recipe identity. Retain alternatives.
        rank = (
            "R1-64f" in str(path),
            "R1-73d-post77d" in str(path),
            "R1-64e" in str(path),
            "R1-64d" in str(path),
            str(path),
            str(p),
        )
        groups.setdefault((cell["condition"], cell["dataset"]), []).append(
            (rank, path, manifest, p, value, receipt_path, receipt)
        )
    return {key: sorted(rows, reverse=True, key=lambda r: r[0]) for key, rows in groups.items()}


def measurements(rows):
    if not rows:
        return dict(
            pending=["completed profile absent"],
            source_bindings=[],
            measured_peak_device_mib=None,
            measured_peak_host_mib=None,
            full_endpoint_evidence_status="pending",
        )
    _, path, manifest, result_path, result, receipt_path, receipt = rows[0]
    payload = json.loads(Path(manifest["payload"]["path"]).read_text())
    sources = [
        d9.ref(path),
        manifest["payload"],
        d9.ref(result_path),
        d9.ref(receipt_path),
        receipt["report"],
    ]
    peak, peak_source, endpoint_seconds, endpoint_sources = 0.0, None, {}, []
    directory = result_path.parent / "phases"
    records = []
    if list(directory.glob("batch-*.receipt.json")):
        verified = DurablePhaseJournal.verify(directory, receipt.get("journal"))
        loaded = []
        for p in sorted(directory.glob("batch-*.receipt.json")):
            closed = json.loads(p.read_text())
            batch = json.loads(Path(closed["batch"]["path"]).read_text())
            sources.extend([d9.ref(p), closed["batch"], closed["intent"]])
            records.extend((Path(closed["batch"]["path"]), value) for value in batch["rows"])
            loaded.extend(batch["rows"])
        if loaded != verified:
            raise ValueError("verified phase inventory differs")
    else:
        records = [(p, json.loads(p.read_text())) for p in sorted(directory.glob("[0-9]*.json"))]
    for p, value in records:
        if value.get("status") != "ok":
            continue
        for event in value.get("returned_events", []):
            memory = event.get("returned_cost", {}).get("peak_mem_mib", 0.0)
            if isinstance(memory, (float, int)) and memory > peak:
                peak, peak_source = memory, d9.ref(p)
        if value.get("phase", "").split(":")[0] in ("near_miss", "revision"):
            endpoint_seconds[value["phase"]] = value.get(
                "phase_wall_seconds", value["wall_seconds"]
            )
            endpoint_sources.append(d9.ref(p))
    if peak_source:
        sources.append(peak_source)
    sources += endpoint_sources
    counts = {
        k: dict(
            planned=len(payload["endpoints"][k]["expected_ids"]),
            supplied=len(payload["endpoints"][k]["rows"]),
        )
        for k in ("near_miss", "revision")
    }
    full = all(
        counts[k] == dict(planned=n, supplied=n) for k, n in (("near_miss", 100), ("revision", 50))
    )
    pending = ["measured host peak absent; MemAvailable floor is not a process peak"]
    if not peak:
        pending.append("measured GPU peak absent")
    if not full or not endpoint_seconds:
        pending.append("full near/revision endpoint measurement pending")
    return dict(
        pending=pending,
        source_bindings=sources,
        measured_peak_device_mib=peak or None,
        measured_peak_host_mib=None,
        device_metric="JAX memory_stats peak_bytes_in_use / 2**20; not nvidia-smi total allocation",
        peak_device_phase=peak_source,
        full_endpoint_evidence_status="complete" if full and endpoint_seconds else "pending",
        endpoint_inventory=counts,
        endpoint_phase_seconds=endpoint_seconds,
        endpoint_phase_seconds_total=sum(endpoint_seconds.values()),
        attempt_wall_seconds=result.get("attempt_wall_seconds"),
        omitted_overhead="outer process startup and validation are not inferred from phase timers",
        recipe=d9.ref(path),
        result=d9.ref(result_path),
        alternative_completed_results=[d9.ref(row[3]) for row in rows[1:]],
        selection_rule="full endpoint, corrected MQ, R1-64e, R1-64d, then lexical recipe/result; no outcome criterion",
    )


def build(output, evidence_dir):
    spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v6.json"))
    sources = {
        "execution_plan": d9.ref(ROOT / "docs/R1_execution_plan_v2.md"),
        "cell_ceilings": d9.ref(ROOT / "manifests/revision_v1/cell_ceilings_v1.json"),
        "concurrency_policy": d9.ref(ROOT / "docs/R1_stage4_queue_concurrency_v2.md"),
        "prior_cost_source": d9.ref(ROOT / "docs/tasks/R1-cost-admission-receipt-v1.json"),
        "producer": d9.ref(__file__),
        "validator": d9.ref(ROOT / "scripts/r1_58h_cost_contract.py"),
        "device_metric_implementation": d9.ref(ROOT / "src/pccap/harness/ledger.py"),
    }
    ceilings = d9.read_metadata(sources["cell_ceilings"])["cells"]
    profiles = completed_profiles()
    cells, pending = [], ["full validation split cost/admission evidence pending"]
    for key, price in sorted(ceilings.items()):
        condition, dataset = key.split(":")
        evidence = measurements(profiles.get((condition, dataset)))
        binding = write_new(evidence_dir / f"{condition}-{dataset}.json", evidence)
        pending += [key + ": " + reason for reason in evidence["pending"]]
        cells.append(
            dict(
                condition=condition,
                dataset=dataset,
                wall_seconds=price["ceiling_seconds"],
                peak_device_mib=(
                    evidence["measured_peak_device_mib"] * 1.5
                    if evidence["measured_peak_device_mib"]
                    else None
                ),
                peak_host_mib=None,
                measurement=binding,
            )
        )
    receipt = {
        k: spec[k]
        for k in ("register", "dataset_layouts", "layout_sha256", "near_miss_family_contract")
    }
    receipt.update(
        cost_schema_version=2,
        contract_version=2,
        task="R1-58h",
        protocol=d9.ref(ROOT / PROTOCOL),
        matrix=d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_1.json"),
        status="pending_evidence" if pending else "unsigned",
        lead_approved=False,
        lead_signature={"name": None, "date": None},
        bindings=sources,
        cells=cells,
        pending_evidence=pending,
        full_validation_evidence_status="pending",
        shared_process_hours=750,
        shared_process_hours_basis="2 workers * 375 h; proposal for explicit lead admission",
        expected_process_hours=254.7825,
        expected_process_hours_basis="(209.4 core + 12.15 extension) solo h * assumed 1.15 concurrent slowdown; projection",
        host_mem_available_floor_mib=6144,
        host_policy_note="host-level available-memory floor per launch, not measured per-process host peak",
        memory_ceiling_factor=1.5,
        two_worker_wall_ceiling_multiplier=1.15,
        startup_validation_seconds_per_cell_estimate=30,
        startup_validation_evidence_status="estimate; not full-validation-split measurement",
        failure_policy="retry once from certified checkpoint; second ordinary failure incomplete and continue; host failure stops dispatch",
        failures_included=True,
        full_endpoint_cost_basis_reviewed=False,
        authority_note="unsigned proposal; absent measurements stay pending even if approval flag is flipped",
    )
    return write_new(output, receipt)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output", type=Path, default=ROOT / "docs/tasks/R1-cost-admission-receipt-v2.json"
    )
    p.add_argument("--evidence-dir", type=Path, default=ROOT / "logs/r1_round28/cost-v2")
    a = p.parse_args()
    if not a.output.resolve().is_relative_to(
        ROOT / "docs/tasks"
    ) or not a.evidence_dir.resolve().is_relative_to(ROOT / "logs"):
        p.error("cost metadata and evidence belong in repo docs/tasks and logs")
    print(json.dumps(build(a.output, a.evidence_dir), indent=2))
