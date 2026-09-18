"""Unsigned v12/D.1 package with normative closure and honest remaining evidence gates."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.r1_49j_normative_closure import PROTOCOL, closure
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d9f_allocation import CONTRACT
from scripts.r1_d10a_review import ROOT, write_new


def replace_refs(value, replacements):
    if isinstance(value, dict):
        if set(value) == {"path", "sha256"} and value["path"] in replacements:
            return copy.deepcopy(replacements[value["path"]])
        return {k: replace_refs(v, replacements) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_refs(v, replacements) for v in value]
    return value


def build():
    log = ROOT / "logs/r1_round28"
    old_path = ROOT / "manifests/revision_v1/freeze_candidate_v11.json"
    candidate = copy.deepcopy(d9.read_metadata(d9.ref(old_path)))
    snapshots = json.loads((log / "source_snapshot/bindings.json").read_text())
    for path, sha in list(candidate["bindings_sha256"].items()):
        if d9.sha(path) != sha:
            if path not in snapshots or snapshots[path]["sha256"] != sha:
                raise ValueError("unexpected concurrent drift: " + path)
            candidate["bindings_sha256"][snapshots[path]["path"]] = sha
            candidate["bindings_sha256"][path] = d9.sha(path)

    def bind(binding):
        if d9.ref(binding["path"]) != binding:
            raise ValueError("package source changed: " + binding["path"])
        candidate["bindings_sha256"][binding["path"]] = binding["sha256"]
        return binding

    proto = bind(d9.ref(ROOT / PROTOCOL))
    matrix = bind(d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_1.json"))
    cost = bind(d9.ref(ROOT / "docs/tasks/R1-cost-admission-receipt-v2.json"))
    cost_doc = d9.read_metadata(cost)
    for b in cost_doc["bindings"].values():
        bind(b)
    for c in cost_doc["cells"]:
        bind(c["measurement"])
        for b in d9.read_metadata(c["measurement"])["source_bindings"]:
            bind(b)
    norm = closure()
    candidate["bindings_sha256"].update(norm["bindings_sha256"])
    for name in (
        "r1_49j_normative_closure",
        "r1_49j_protocol_matrix",
        "r1_58h_cost_contract",
        "r1_58h_cost_receipt",
        "r1_64f_full_endpoints",
        "r1_63i_freeze_candidate",
        "r1_58g_operator",
    ):
        bind(d9.ref(ROOT / f"scripts/{name}.py"))
    spec = d9.read_metadata(candidate["d9_inputs"])
    replacements = {spec["protocol"]["path"]: proto, spec["matrix"]["path"]: matrix}
    spec = replace_refs(spec, replacements)
    row = next(
        r
        for r in (ROOT / "docs/decisions.md").read_text().splitlines()
        if r.startswith("| DEC-062 |")
    )
    snapshot = log / "source_snapshot/decisions-clarified.md"
    with snapshot.open("xb") as f:
        f.write((ROOT / "docs/decisions.md").read_bytes())
    decision = d9.read_metadata(spec["near_allocation_decision"])
    decision.update(
        decision_source=bind(d9.ref(snapshot)),
        decision_row=row,
        clarification="Lead explicitly allows multiple disjoint pairs per family; exact formal protocol/RNG request still unsigned",
        semantic_clarification=bind(d9.ref(ROOT / "docs/tasks/DEC-062-pair-unit-clarification.md")),
    )
    decision_ref = bind(
        write_new(ROOT / "docs/tasks/R1-D9f-allocation-contract-template-v7.json", decision)
    )
    spec.update(
        status="unsigned_D1_normative_cost_v2_evidence_pending",
        task="R1-63i",
        near_allocation="family_coordinated",
        near_allocation_decision=decision_ref,
        family_pair_unit_policy_reviewed=True,
        cost_admission_source_unsigned=cost,
        normative_closure=norm,
        shared_process_hours_proposed=750,
    )
    spec["d9"]["clearance"]["configuration_bindings"].update(
        cost_admission_source_unsigned=cost,
        normative_closure=bind(write_new(log / "normative-closure-bound.json", norm)),
    )
    templates = {}
    for key, b in spec["receipts"].items():
        if not b.get("path") or key.endswith("_authorization"):
            continue
        value = replace_refs(d9.read_metadata(b), replacements)
        if value.get("lead_approved") is not False:
            raise PermissionError("do not rebind signed receipts")
        value.update(candidate_name="v12")
        if key in ("protocol_admission", "rng_admission"):
            value.update(
                near_allocation="family_coordinated",
                near_allocation_contract=CONTRACT,
                near_allocation_decision=decision_ref,
                family_pair_unit_policy_reviewed=True,
                normative_closure=norm,
            )
        templates[key] = bind(
            write_new(ROOT / f"docs/tasks/R1-D9-{key.replace('_', '-')}-template-v7.json", value)
        )
    spec["receipts"].update(templates)
    for stage in ("clearance", "draw", "seal"):
        key = stage + "_authorization"
        value = replace_refs(d9.read_metadata(spec["receipts"][key]), replacements)
        value.update(
            candidate_name="v12",
            request_sha256=None,
            inspection_only_request_sha256=d9.contract(spec, stage),
        )
        templates[key] = bind(
            write_new(ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-v7.json", value)
        )
        spec["receipts"][key] = templates[key]
    spec_ref = bind(write_new(ROOT / "docs/tasks/R1-D9-inputs-v7.json", spec))
    inspections_path = ROOT / "docs/tasks/R1-64f/inspection-receipts.json"
    bind(d9.ref(inspections_path))
    profiles = []
    for row in json.loads(inspections_path.read_text()):
        bind(row["recipe"])
        bind(row["payload"])
        found = []
        for p in sorted(Path(row["expected_result_directory"]).glob("attempt-*/result.json")):
            v = json.loads(p.read_text())
            if v.get("manifest_sha256") != row["recipe"]["sha256"]:
                raise ValueError("full endpoint result recipe differs")
            if v.get("status") == "complete" and v.get("completed_checkpoint") == 300:
                found.append(bind(d9.ref(p)))
        if len(found) > 1:
            raise ValueError("multiple completed full endpoint attempts require review")
        profiles.append(
            dict(
                cell=row["cell"],
                recipe=row["recipe"],
                status="complete" if found else "pending",
                results=found,
            )
        )
    interface = bind(d9.ref(ROOT / "docs/tasks/R1-63i-production-bundle-interface.md"))
    blockers = list(cost_doc["pending_evidence"])
    blockers += [
        "R1-64f:" + p["cell"]["dataset"] + ":" + p["cell"]["condition"]
        for p in profiles
        if p["status"] != "complete"
    ]
    blockers += [
        "whole production recipe/freeze bundle assembler missing",
        "actual authorized draw/endpoints/seal and final scientific gate evidence required",
    ]
    for gate in candidate["gate_inventory"]:
        if gate["gate"] == "U09":
            gate["closure"] = (
                "DEC-061/062 and repeated-family semantics accepted; D.1 amended/bound; exact formal admission and actual pair missingness remain."
            )
        elif gate["gate"] == "U16":
            gate["closure"] = (
                "Typed cost v2 proposes750 process hours and binds measured GPU peaks; full endpoint/host/full-validation evidence and exact lead approval still pending."
            )
    candidate.update(
        schema_version=12,
        name="freeze_candidate_v12",
        task="R1-63i",
        producer=bind(d9.ref(__file__)),
        historical_candidate=bind(d9.ref(old_path)),
        protocol=proto,
        matrix=matrix,
        normative_closure=norm,
        d9_inputs=spec_ref,
        d9_templates=templates,
        near_allocation_decision=decision_ref,
        operator=bind(d9.ref(ROOT / "scripts/r1_58g_operator.py")),
        cost_admission_source_unsigned=cost,
        cost_admission_receipt=None,
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        full_endpoint_profiles=profiles,
        production_bundle_interface=interface,
        production_bundle_producer=None,
        non_signature_blockers=blockers,
        signatures_only=False,
        status="unsigned_D1_normative_repaired_typed_cost_v2_and_recipes_prepared_evidence_pending",
    )
    candidate["remaining_gates"] = [g for g in candidate["gate_inventory"] if g["status"] == "open"]
    checked = verify(candidate)
    binding = write_new(ROOT / "manifests/revision_v1/freeze_candidate_v12.json", candidate)
    checked.update(
        candidate=binding,
        inputs=spec_ref,
        normative_files=len(norm["bindings_sha256"]),
        signatures_only=False,
        non_signature_blockers=blockers,
        full_endpoint_results_complete=sum(p["status"] == "complete" for p in profiles),
    )
    write_new(log / "r1-63i-verification.json", checked)
    return checked


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
