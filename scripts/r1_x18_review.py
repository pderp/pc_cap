"""Recheck current v13 identities, measurements, publication evidence and remaining gates."""

from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

from scripts import r1_58h_cost_contract as costs
from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_75_analysis_stage4_v1 import preservation_section
from scripts.r1_d10a_review import ROOT, write_new


def run():
    candidate_ref = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v13.json")
    candidate = d9.read_metadata(candidate_ref)
    verified = verify(candidate)
    spec = d9.read_metadata(candidate["d9_inputs"])
    cost = d9.read_metadata(candidate["cost_admission_source_unsigned"])
    matrix = d9.read_metadata(candidate["matrix"])
    assert spec["protocol"] == cost["protocol"] == matrix["protocol"]
    assert spec["matrix"] == cost["matrix"] == candidate["matrix"]
    assert candidate["production_bundle_producer"] == d9.ref(
        ROOT / "scripts/r1_63j_production_bundle.py"
    )
    measurements = []
    for c in cost["cells"]:
        e = d9.read_metadata(c["measurement"])
        for field in ("host", "device"):
            value = e[f"measured_peak_{field}_mib"]
            assert c[f"peak_{field}_mib"] == (value * 1.5 if value is not None else None)
        for b in e["source_bindings"]:
            assert d9.sha(b["path"]) == b["sha256"]
        measurements.append(e)
    failures = []
    for strip in (False, True):
        pretend = copy.deepcopy(cost)
        pretend.update(
            status="closed", lead_approved=True, full_validation_evidence_status="complete"
        )
        if strip:
            pretend["pending_evidence"] = []
        try:
            costs.validate(pretend)
        except ValueError as error:
            failures.append(dict(top_pending_erased=strip, error=str(error)))
        else:
            raise AssertionError("missing evidence incorrectly admitted")
    previous = d9.read_metadata(d9.ref(ROOT / "logs/r1_round28/r1-x17-review.json"))
    for row in previous["corrected_profiles"]:
        for field in ("recipe", "result", "checkpoint"):
            assert d9.sha(row[field]["path"]) == row[field]["sha256"]
        checkpoint = json.loads(Path(row["checkpoint"]["path"]).read_text())
        _, bounded, _ = preservation_section(
            checkpoint["locality"], checkpoint["locality"]["expected_ids"], "query"
        )
        assert bounded["numerator"] == row["bounded_locality"]
    prices = d9.read_metadata(cost["bindings"]["cell_ceilings"])["cells"]
    totals = []
    for cells in (matrix["cells"], matrix["extension"]["cells"]):
        totals.append(
            sum(
                Decimal(str(prices[c["condition"] + ":" + c["dataset"]]["solo_hours"]))
                for c in cells
            )
        )
    assert float(sum(totals) * Decimal("1.15")) == cost["expected_process_hours"]
    hosts = d9.read_metadata(cost["host_peak_evidence"])
    validation = d9.read_metadata(cost["validation_inventory"])
    recipes = candidate["full_endpoint_profiles"]
    rehearsal_refs = []
    for p in sorted((ROOT / "logs/r1_round29").glob("assembler-rehearsal-*.json")):
        value = json.loads(p.read_text())
        # A historical passing proof may predate a source edit: only current
        # staged freezes bind this assembler byte-for-byte.
        bundle = d9.read_metadata(value["bundle"])
        freeze = next(
            a for a in bundle["artifacts"] if a["destination"].endswith("/frozen_stage4.json")
        )
        frozen = d9.read_metadata(freeze["source"])
        expected = frozen["bindings_sha256"].get(str(ROOT / "scripts/r1_63j_production_bundle.py"))
        if expected == d9.sha(ROOT / "scripts/r1_63j_production_bundle.py"):
            rehearsal_refs.append(d9.ref(p))
    if not rehearsal_refs:
        raise ValueError("current assembler rehearsal evidence absent")
    report = dict(
        task="X18",
        verdict="NOT_READY_FOR_SIGNATURE_OR_LAUNCH",
        candidate=candidate_ref,
        verification=verified,
        producer=d9.ref(__file__),
        cost_receipt=candidate["cost_admission_source_unsigned"],
        cost_fail_closed_probes=failures,
        assembler_rehearsals=rehearsal_refs,
        closed_findings=[
            "X16-06 missing whole-package producer: implementation and actual queue/backend metadata rehearsal delivered"
        ],
        remaining_non_signature_blockers=candidate["non_signature_blockers"],
        signatures_only=False,
        host_methods=hosts["counts"],
        host_evidence=cost["host_peak_evidence"],
        numeric=dict(
            core_cells=len(matrix["cells"]),
            extension_cells=len(matrix["extension"]["cells"]),
            core_solo_hours=float(totals[0]),
            extension_solo_hours=float(totals[1]),
            expected_process_hours=cost["expected_process_hours"],
            proposed_process_hours=cost["shared_process_hours"],
            worst_two_attempt_padded_process_hours=float(
                sum(totals) * Decimal("1.5") * Decimal("1.15") * 2
            ),
            host_peak_rows=sum(e["measured_peak_host_mib"] is not None for e in measurements),
            device_peak_rows=sum(e["measured_peak_device_mib"] is not None for e in measurements),
            full_endpoint_rows=sum(
                e["full_endpoint_evidence_status"] == "complete" for e in measurements
            ),
            full_endpoint_runs_complete=sum(p["status"] == "complete" for p in recipes),
            full_endpoint_runs_planned=4,
            pending_cost_reasons=len(cost["pending_evidence"]),
            validation_tokens=validation["validation_tokens"],
            prefix_positions=16256,
            complete_window_positions=validation["complete_window_prediction_positions"],
        ),
        full_endpoint_profiles=recipes,
        corrected_profiles=previous["corrected_profiles"],
        validation_inventory=cost["validation_inventory"],
        residual_risks=[
            "Monitor matches use unique driver entry-point and file-mtime windows, not embedded recipe argv/PID; sampled RSS can miss peaks and copied mtimes invalidate attribution.",
            "Extrapolated host and cross-condition endpoint proposals remain unadmitted, not measured.",
            "128-window drift and input validation do not supply full-validation endpoint losses or costs; current revision endpoint run still missing.",
            "Synthetic publication rehearsal does not supply actual authorized draw/seal/gate receipts or a published production freeze.",
            "750 process-hour proposal is below the764.3475 all-cells two-attempt padded bound; preserve explicit incomplete reporting and October9 stop.",
            "Three clusters yield nominal intervals;21 MQuAKE1000 intervals remain unavailable;6036/6084 zsRE baselines empty.",
        ],
        HT4f="blocked: receipt revision3 unsigned and full-validation/evidence pending",
        gpu_seconds=0,
        model_calls=0,
        production_publication=False,
        signatures=0,
        task_list=d9.ref(ROOT / "docs/ongoing.md"),
    )
    write_new(ROOT / "logs/r1_round29/r1-x18-review.json", report)
    print(json.dumps({k: report[k] for k in ("verdict", "numeric", "host_methods")}, indent=2))
    return report


if __name__ == "__main__":
    run()
