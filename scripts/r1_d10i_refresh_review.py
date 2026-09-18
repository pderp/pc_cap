"""Independently review the orchestrator's concurrent clearance provenance refresh.

Read-only inputs, evidence, source history and signatures. No operator invocation,
signing, candidate construction, journal mutation, draw, seal, freeze or launch.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from scripts import r1_58g_operator as operator
from scripts import r1_d9_receipts as d9

ROOT = d9.ROOT


def functions(raw):
    return {
        n.name: ast.dump(n, include_attributes=False)
        for n in ast.parse(raw).body
        if isinstance(n, ast.FunctionDef)
    }


def review():
    old_ref = d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v9.json")
    new_ref = d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v10.json")
    old, new = d9.read_metadata(old_ref), d9.read_metadata(new_ref)
    evidence_ref = new["d9"]["clearance"]["evidence"]
    parent_ref = old["d9"]["clearance"]["evidence"]
    evidence, parent = d9.read_resource(evidence_ref), d9.read_resource(parent_ref)
    changed_keys = sorted(
        k for k in set(parent) | set(evidence) if parent.get(k) != evidence.get(k)
    )
    if evidence["dispositions"] != parent["dispositions"]:
        raise ValueError("clearance dispositions changed")
    unexpected = [
        k
        for k in changed_keys
        if k
        not in (
            "schema_version",
            "status",
            "rebinding_round41",
            "evidence_bindings",
            "provenance_refresh",
            "version_note",
            "binding_refresh",
            "provenance_rebinding",
            "rebound_from",
            "rebound_note",
        )
    ]
    if unexpected:
        raise ValueError("unreviewed evidence fields changed: " + str(unexpected))
    if (
        evidence.get("schema_version") != 6
        or evidence.get("rebinding_round41", {}).get("parent_v5") != parent_ref
        or evidence.get("status")
        != "DEC061_teacher_roles_complete_rebound_round41_owner_signature_and_current_exposure_attestation_pending"
    ):
        raise ValueError("unexpected refresh metadata")
    old_scan, final_scan = [], []
    for b in parent["evidence_bindings"]:
        actual = d9.ref(b["path"])
        old_scan.append(dict(binding=b, current=actual, matches=b["sha256"] == actual["sha256"]))
    for b in evidence["evidence_bindings"]:
        actual = d9.ref(b["path"])
        if b["sha256"] != actual["sha256"]:
            raise ValueError("refreshed evidence binding still differs: " + b["path"])
        final_scan.append(b)
    stale = [r for r in old_scan if not r["matches"]]
    endpoint = ROOT / "scripts/r1_d10c_endpoints.py"
    historical = subprocess.check_output(
        ["git", "show", "9fd9ea4:scripts/r1_d10c_endpoints.py"], cwd=ROOT
    )
    import hashlib

    historical_sha = hashlib.sha256(historical).hexdigest()
    if any(
        r["binding"]["path"] != str(endpoint) or r["binding"]["sha256"] != historical_sha
        for r in stale
    ):
        raise ValueError("stale evidence outside the reviewed D10c change")
    before, after = functions(historical), functions(endpoint.read_bytes())
    changed_functions = [k for k in before if before[k] != after.get(k)]
    if set(changed_functions) != {"construct", "main"} or set(before) != set(after):
        raise ValueError("unexpected endpoint source change")
    if operator.common(old) != operator.common(new) or operator.cost_binding(
        old
    ) != operator.cost_binding(new):
        raise ValueError("protocol or cost basis changed")
    receipts = {}
    for key, filename in (
        ("protocol_admission", "01-protocol-admit.receipt.json"),
        ("chain_i_cell_ceilings", "02-cost-admit.receipt.json"),
    ):
        ref = d9.ref(ROOT / "docs/tasks/R1-58g-operator_v8" / filename)
        receipt = d9.read_metadata(ref)
        d9.check_receipt(key, receipt, new)
        receipts[key] = ref
    preview, state = d9.prepare(new, "clearance", evaluate_clearance=True)
    expected = dict(
        gate="owner_receipts", reason="clearance_authorization: open or unapproved receipt"
    )
    if any(b != expected for b in preview["blocked"]) or "clearance" not in state:
        raise ValueError("exhaustive clearance review blocked: " + str(preview["blocked"]))
    for b in [old_ref, new_ref, parent_ref, evidence_ref, *receipts.values(), *final_scan]:
        if d9.ref(b["path"])["sha256"] != b["sha256"]:
            raise ValueError("source changed during independent review")
    return dict(
        task="R1-D10i-independent-review",
        checked_utc=datetime.now(UTC).isoformat(),
        status="provenance_refresh_and_prior_receipts_verified",
        old_inputs=old_ref,
        new_inputs=new_ref,
        original_evidence=parent_ref,
        evidence=evidence_ref,
        original_binding_entries=len(old_scan),
        stale_entries=len(stale),
        stale_unique_paths=len({r["binding"]["path"] for r in stale}),
        stale_bindings=stale,
        refreshed_binding_entries=len(final_scan),
        evidence_changed_keys=changed_keys,
        unchanged_dispositions=len(evidence["dispositions"]),
        changed_source_functions=changed_functions,
        unchanged_clearance_functions=[k for k in before if k not in changed_functions],
        source_interpretation="DEC-063 checks/propagates the full-validation contract in postdraw construct/main. "
        "Role planning and clearance functions are AST-identical. Existing dispositions and scientific values are unchanged.",
        signed_receipts_valid_under_v10=receipts,
        resign_steps_1_2_required=False,
        fresh_step3_signature_required=True,
        exhaustive_clearance=preview,
        session_cautions=[
            "The installed operator selects the last completed journal inputs, ignoring --inputs after step1. "
            "A v10 CLI argument alone does not rebase operator_v8.",
            "A failed step3 left an authorization receipt at the original output path; original retry refuses overwrite.",
            "Nested dry_run.blocked contains exhaustive failures while the original outer blocked can omit them. "
            "Orchestrator must reconcile the versioned session and propagate nested blockers before resuming.",
        ],
        full_X20_complete=False,
        draws=0,
        seals=0,
        signatures=0,
        gpu_seconds=0,
        producer=d9.ref(__file__),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    path = p.parse_args().output.resolve()
    if not path.is_relative_to(ROOT / "logs") or path.exists():
        p.error("new output path under repository logs required")
    result = review()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(result, indent=2))
