"""Audit consumed metadata and lock installed implementations, preserving history.

An immutable observation or predecessor is verified as a file, not recursively
reinterpreted as an instruction to execute its historical implementation today.
The unrestricted syntactic scan is retained separately with all its findings.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import r1_63o_graph as graph
from scripts import r1_d9_receipts as d9

ROOT = graph.ROOT
HISTORY_FIELDS = {
    "historical_candidate",
    "historical_freeze_candidate",
    "historical_package_v10",
    "historical_matrix",
    "historical_review_fields",
    "historical_binding_archives",
    "historical_source_relocations_round26",
    "rebinding_round41",
    "parent_v4",
    "provenance_refresh_D5",
    "provenance_refresh",
}


def audit(inputs, candidate):
    inputs_ref, candidate_ref = d9.ref(inputs), d9.ref(candidate)
    spec = d9.read_metadata(inputs_ref)
    # These are the versioned control documents the live workflow interprets.
    expanded = {inputs_ref["path"], candidate_ref["path"]}
    active_refs = [
        spec[k]
        for k in (
            "matrix",
            "register",
            "construction_inputs",
            "runtime_templates",
            "cost_admission_source_unsigned",
            "near_allocation_decision",
        )
    ]
    active_refs += [b for b in spec["receipts"].values() if isinstance(b, dict) and b.get("path")]
    active_refs += [spec["d9"]["clearance"][k] for k in ("role_plan", "evidence")]
    active_refs += list(d9.read_metadata(spec["runtime_templates"]).values())
    expanded.update(b["path"] for b in active_refs)
    queue = [inputs_ref, candidate_ref]
    visited = set()
    bindings = {}
    snapshots = []
    history = []
    errors = []
    while queue:
        b = queue.pop()
        path = graph.local(b["path"])
        key = (str(path), b["sha256"])
        if key in visited:
            continue
        visited.add(key)
        actual = graph.sha(path)
        if actual != b["sha256"]:
            errors.append(dict(binding=b, current=actual))
            continue
        bindings[str(path)] = actual
        if str(path) not in expanded:
            if path.suffix == ".json":
                snapshots.append(
                    dict(
                        binding=b,
                        role="immutable_input_snapshot",
                        rule="Exact bytes required; historical producer ancestry is not a current executable dependency. Native register/cost/recipe validation remains required.",
                    )
                )
            continue
        value = json.loads(path.read_bytes())
        for edge, pointer, _kind in graph.edges(value):
            first = pointer.split("/")[1] if pointer else ""
            if first in HISTORY_FIELDS:
                history.append(
                    dict(
                        container=str(path),
                        pointer=pointer,
                        binding=edge,
                        role="historical_identity_not_current_execution",
                    )
                )
                continue
            # Candidate's broad lock map includes immutable historical evidence;
            # all files are checked, but only control documents are interpreted.
            queue.append(edge)
    return dict(
        schema_version=1,
        inputs=inputs_ref,
        candidate=candidate_ref,
        method="explicit consumer graph, not unrestricted historical ancestry",
        expanded_control_documents=sorted(expanded),
        checked_resources=len(bindings),
        active_binding_errors=errors,
        bindings_sha256=bindings,
        immutable_input_boundaries=snapshots,
        historical_identity_edges=history,
        native_checks_required=[
            "candidate.verify",
            "cost_contract.validate",
            "register.verify_register",
            "d9.prepare clearance with exhaustive evaluation",
            "runtime profile_config",
            "endpoint constructor dry run",
            "synthetic whole-package assembly",
        ],
        scripts_locked={p: h for p, h in bindings.items() if p.endswith(".py")},
        authorization="No signatures, draw, seal, freeze publication or launch granted",
    )


def verify_lock(path):
    value = json.loads(Path(path).read_text())
    if value["active_binding_errors"]:
        raise ValueError("lock was not clean at creation")
    changed = [
        p for p, h in value["bindings_sha256"].items() if not Path(p).is_file() or graph.sha(p) != h
    ]
    if changed:
        raise ValueError("locked dependency changed: " + str(changed))
    current = {
        str(p.resolve())
        for directory in ("scripts", "src/pccap")
        for p in (ROOT / directory).rglob("*.py")
    }
    if current != set(value["scripts_locked"]):
        raise ValueError("installed implementation inventory changed")
    return dict(
        resources=len(value["bindings_sha256"]), scripts=len(current), content_lock_verified=True
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path)
    p.add_argument("--candidate", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--verify-lock", type=Path)
    args = p.parse_args()
    if args.verify_lock:
        print(json.dumps(verify_lock(args.verify_lock), indent=2))
    else:
        value = audit(args.inputs, args.candidate)
        graph.write(args.output, value)
        print(
            json.dumps(
                dict(
                    resources=value["checked_resources"],
                    active_binding_errors=value["active_binding_errors"],
                    scripts=len(value["scripts_locked"]),
                ),
                indent=2,
            )
        )
        raise SystemExit(1 if value["active_binding_errors"] else 0)
