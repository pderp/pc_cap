"""Read-only review of the genuine first protocol signature, before full X20.

Uses the independently saved reviewed form to reconstruct the operator request.
No operator invocation, journal write, signature, resource draw or launch occurs.
This partial review cannot establish full post-session or launch clearance.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts import r1_58g_operator as op
from scripts import r1_d9_receipts as d9

ROOT = op.ROOT


def review():
    sources = {}

    def read(path_or_binding):
        binding = d9.ref(path_or_binding) if isinstance(path_or_binding, (str, Path)) else path_or_binding
        value = d9.read_metadata(binding)
        sources[binding["path"]] = binding["sha256"]
        return value, binding

    inputs, inputs_ref = read(ROOT / "docs/tasks/R1-D9-inputs-v9.json")
    candidate, candidate_ref = read(ROOT / "manifests/revision_v1/freeze_candidate_v14.json")
    if candidate["d9_inputs"] != inputs_ref:
        raise ValueError("candidate does not bind the initial inputs")
    checked = op.verify_candidate(candidate)
    session = ROOT / "logs/R1/operator_v8"
    journal = session / "receipts.jsonl"
    raw = journal.read_bytes()
    if not raw.endswith(b"\n"):
        raise ValueError("torn operator journal")
    rows = op.journal_read(journal)
    if journal.read_bytes() != raw:
        raise ValueError("journal changed while parsing; retry")
    completed = [r for r in rows if r.get("status") == "complete"]
    if not completed or [r["step"] for r in completed] != list(op.STEPS[:len(completed)]):
        raise ValueError("completed protocol-first operator prefix required")
    row = completed[0]
    form, form_ref = read(ROOT / "docs/tasks/operator-v8/01-protocol-reviewed.json")
    fields = copy.deepcopy(form["fields"])
    op.check_fields("protocol-admit", fields, inputs)
    output = ROOT / "docs/tasks/R1-58g-operator_v8"
    request = dict(version=1, step="protocol-admit", inputs=inputs_ref,
        candidate=candidate_ref, cost_admission_source=op.cost_binding(inputs), fields=fields,
        receipt_output=str(output / "01-protocol-admit.receipt.json"),
        next_inputs=str(output / "01-inputs.json"), producer=d9.ref(op.__file__),
        implementation=d9.implementation_bindings())
    digest = op.validate_signature(form, request)
    if digest != row["request_sha256"]:
        raise ValueError("reviewed form and completed journal request differ")
    if (row["receipt"]["path"] != request["receipt_output"]
            or row["inputs"]["path"] != request["next_inputs"]):
        raise ValueError("journal output paths differ from the reviewed request")
    if not any(r.get("status") == "dry_run" and r.get("step") == "protocol-admit"
               and r.get("request_sha256") == digest and r.get("blocked") == []
               for r in rows[:rows.index(row)]):
        raise ValueError("no unblocked preview of the exact signed request")
    receipt, receipt_ref = read(row["receipt"])
    template, _ = read(inputs["receipts"]["protocol_admission"])
    expected = template | op.common(inputs) | fields | dict(status="closed", lead_approved=True,
        lead_signature=form["lead_signature"], operator_request_sha256=digest)
    decision, decision_ref = read(output / "01-allocation-contract.receipt.json")
    expected_decision = op.protocol_allocation_decision(fields)
    expected_decision.update(lead_signature=form["lead_signature"], operator_request_sha256=digest)
    if decision != expected_decision:
        raise ValueError("allocation receipt differs from exact inherited protocol approval")
    expected["near_allocation_decision"] = decision_ref
    if receipt != expected:
        raise ValueError("signed receipt differs from the full expected template/fields/signature")
    d9.check_receipt("protocol_admission", receipt, inputs)
    after, after_ref = read(row["inputs"])
    expected_after = copy.deepcopy(inputs)
    expected_after["receipts"]["protocol_admission"] = receipt_ref
    expected_after.update(near_allocation=fields["near_allocation"],
                          near_allocation_decision=decision_ref)
    if after != expected_after:
        raise ValueError("operator input transition changed an unrelated field")
    # A stale unsigned seed form is not the approval record. Record its status
    # explicitly so a reviewer cannot mistake it for the matching final preview.
    old_form, old_ref = read(ROOT / "docs/tasks/operator-v8/01-protocol-preview.json")
    for path, expected_hash in {**candidate["bindings_sha256"], **sources}.items():
        if d9.sha(path) != expected_hash:
            raise ValueError("bound evidence changed during review: " + path)
    if journal.read_bytes() != raw:
        raise ValueError("operator session advanced during review; retry the snapshot")
    matrix, _ = read(inputs["matrix"])
    admitted = d9.matrix_cells(dict(document=matrix, binding=inputs["matrix"]), receipt)
    return dict(task="X20-protocol-prefix", status="protocol_signature_verified_only",
        checked_utc=datetime.now(UTC).isoformat(), candidate=candidate_ref,
        candidate_bindings_verified=checked["bindings"], initial_inputs=inputs_ref,
        reviewed_form=form_ref, signed_protocol=receipt_ref, signed_allocation=decision_ref,
        next_inputs=after_ref, request_sha256=digest, signature=form["lead_signature"],
        successful_preview_verified=True, full_receipt_reconstructed=True,
        exact_state_transition=True, extension_admitted=fields["extension_admitted"],
        protocol_selected_cells=len(admitted), core_cells=285, optional_cells=45,
        historical_unsigned_form=dict(binding=old_ref,
            digest_matches_signed_request=old_form.get("request_sha256") == digest,
            lead_approved=old_form.get("lead_approved"),
            interpretation="Earlier seed form retains an older digest; it is not the signed approval or the final unblocked journal preview."),
        journal=dict(path=str(journal), sha256=hashlib.sha256(raw).hexdigest(), rows=len(rows)),
        completed_steps_at_snapshot=[r["step"] for r in completed],
        remaining=["signed typed v4 cost", "current clearance", "signed RNG and reproduced actual draw",
                   "actual endpoints/missingness and seal", "exact publication/freeze and launch clearance"],
        full_X20_complete=False, launch_authorized=False, signed=False,
        payloads_opened=0, gpu_seconds=0,
        implementation=dict(reviewer=d9.ref(__file__), operator=d9.ref(op.__file__)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target = args.output.resolve()
    if not target.is_relative_to(ROOT / "logs") or target.exists():
        parser.error("new report path under repository logs required")
    result = review()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
