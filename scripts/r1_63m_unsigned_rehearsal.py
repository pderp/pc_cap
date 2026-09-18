"""Inspect real unsigned v14 inputs without upgrading any authority or reading payloads."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from scripts import ht4f_claim_ledger as ledger
from scripts import r1_58g_operator as op
from scripts import r1_63j_production_bundle as assembler
from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT, write_new


def run(output=None):
    candidate_ref = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v14.json")
    candidate = d9.read_metadata(candidate_ref)
    proof = verify(candidate)
    spec = d9.read_metadata(candidate["d9_inputs"])
    frozen = ROOT / "manifests/revision_v1/frozen_stage4.json"
    if frozen.exists():
        raise PermissionError("unsigned rehearsal requires no final frozen manifest")
    prefix = ROOT / "logs/r1_round36" / ("unsigned-rehearsal-" + uuid4().hex)
    results = {}
    for step in op.STEPS:
        results[step] = op.run(
            step,
            inputs=candidate["d9_inputs"]["path"],
            candidate=candidate_ref["path"],
            session=prefix,
            form_output=ROOT / "docs/tasks" / prefix.name / f"{step}-v9.json",
        )
        if results[step]["execute"] is not False or results[step].get("status") == "complete":
            raise ValueError("unsigned operator must not execute")

    def forbidden(_):
        raise AssertionError("unsigned preparation opened a resource")

    with patch.object(d9, "read_resource", forbidden):
        stages = {
            stage: d9.prepare(spec, stage, evaluate_clearance=False)[0]
            for stage in ("clearance", "draw", "seal")
        }
        inspected = assembler.inspect(spec)
    if any(not r.get("blocked") for r in stages.values()) or not inspected["blocked"]:
        raise ValueError("unsigned producer unexpectedly ready")
    cost = op.fields_for("cost-admit", spec)
    cost["full_endpoint_cost_basis_reviewed"] = True
    op.check_fields("cost-admit", cost, spec)  # field validation only, no signature/write
    try:
        ledger.build(cost_receipt=candidate["cost_admission_source_unsigned"]["path"])
    except (ValueError, PermissionError) as error:
        claim_gate = dict(status="waiting_for_actual_signed_v4", reason=str(error))
    else:
        raise AssertionError("unsigned receipt produced a final claim ledger")
    if frozen.exists():
        raise AssertionError("dry inspection wrote a frozen manifest")
    for b in spec["receipts"].values():
        if b.get("path") and d9.read_metadata(b).get("lead_approved") is not False:
            raise AssertionError("unsigned source receipt gained approval")
    report = dict(
        task="R1-63m",
        candidate=candidate_ref,
        inputs=candidate["d9_inputs"],
        candidate_verification=proof,
        clearance_review="metadata-only; exhaustive clearance recomputation remains in the authorized operator step",
        operator_steps=results,
        d9_stages=stages,
        assembler_inspection=inspected,
        typed_cost_field_validation="passed_without_signature",
        claim_ledger_gate=claim_gate,
        actual_draws=0,
        actual_seals=0,
        frozen_manifest_written=False,
        launches=0,
        payloads_opened=0,
        model_calls=0,
        gpu_seconds=0,
    )
    return write_new(output or ROOT / "logs/r1_round36/unsigned-rehearsal.json", report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))
