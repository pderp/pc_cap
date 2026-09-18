"""Build the unsigned D.5 package once, with explicit historical provenance.

No signatures, draws, endpoint writes, seals, production publication or launches.
Use --draft NAME for isolated rehearsals; canonical paths are emitted only after
source repairs and tests finish. Never overwrite an existing artifact.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_49o_protocol_matrix as matrix_producer
from scripts import r1_58g_operator as operator
from scripts import r1_58h_cost_contract as costs
from scripts import r1_63j_production_bundle as bundle
from scripts import r1_63o_graph as graph
from scripts import r1_68c_dev_cell as driver
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipts as d9
from scripts.r1_49o_normative_closure import closure
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT
from scripts.r1_d10a_review_core import digest


def build(draft=None):
    if draft and any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in draft):
        raise ValueError("simple draft name required")
    root = ROOT / "docs/tasks/R1-63o-drafts" / draft if draft else ROOT
    report_root = root / "logs/r1_63o" if draft else ROOT / "logs/r1_63o/final"
    resources = ROOT.parent / "assets/runs/pc_cap/R1/r1_63o" / (draft or "v15")
    report_root.mkdir(parents=True, exist_ok=True)
    paths = {}

    def put(relative, value):
        binding = graph.write(root / relative, value)
        paths[relative] = binding
        return binding

    old_spec_ref = d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v10.json")
    spec = d9.read_metadata(old_spec_ref)
    refreshes = []
    for name, row_key, output_name in [
        ("role_plan", "rows", "role-plan-v2.json"),
        ("evidence", "dispositions", "joint-evidence-v7.json"),
    ]:
        parent = spec["d9"]["clearance"][name]
        value = d9.read_resource(parent)
        previous = copy.deepcopy(value)
        changed = []
        for b in value["evidence_bindings"]:
            actual = d9.ref(b["path"])
            if b["sha256"] != actual["sha256"]:
                if not str(Path(b["path"]).resolve()).startswith(str(ROOT / "scripts") + "/"):
                    raise ValueError("non-code clearance evidence changed: " + b["path"])
                changed.append(dict(previous=copy.deepcopy(b), current=actual))
                b["sha256"] = actual["sha256"]
        value["provenance_refresh_D5"] = dict(
            parent=parent,
            producer=d9.ref(__file__),
            changed_bindings=changed,
            row_count=len(value[row_key]),
            rows_sha256=digest(value[row_key]),
            rows_changed=False,
            explanation="Current constructor provenance only; no clearance disposition, role, teacher answer, source, population or exclusion changed. Historical executions retain their original identities.",
        )
        assert value[row_key] == previous[row_key]
        binding = graph.write(resources / output_name, value)
        spec["d9"]["clearance"][name] = binding
        refreshes.append(dict(resource=name, current=binding, **value["provenance_refresh_D5"]))
    matrix = matrix_producer.document()
    matrix_ref = put("manifests/revision_v1/run_matrix_v5_2_D_5.json", matrix)
    norm = closure()
    norm_ref = graph.write(report_root / "normative-closure-D5.json", norm)
    old_cost_ref = spec["cost_admission_source_unsigned"]
    cost = d9.read_metadata(old_cost_ref)
    old_cost = copy.deepcopy(cost)
    cost.update(
        artifact_version=5,
        task="R1-63o",
        matrix=matrix_ref,
        protocol=matrix["protocol"],
        provenance_refresh=dict(
            parent=old_cost_ref,
            producer=d9.ref(__file__),
            numerical_content_changed=False,
            typed_schema_note="Artifact v5 retains receipt_revision=4 and its exact native validator.",
        ),
    )
    cost["bindings"]["matrix"] = matrix_ref
    cost["bindings"]["execution_plan"] = d9.ref(ROOT / "docs/R1_execution_plan_v4.md")
    for b in cost["bindings"].values():
        if Path(b["path"]).suffix == ".py":
            b["sha256"] = d9.sha(b["path"])
    cost["bindings"]["package_producer"] = d9.ref(__file__)
    cost_proof = costs.validate(cost)
    for key in (
        "cells",
        "projection",
        "expected_process_hours",
        "shared_process_hours",
        "failure_policy",
    ):
        assert cost[key] == old_cost[key], key
    cost_ref = put("docs/tasks/R1-cost-admission-receipt-v5.json", cost)
    runtime_dir = root / "docs/tasks/R1-63o-runtime-v3"
    if not runtime_dir.exists():
        bundle.template_catalog(runtime_dir)
    templates_ref = d9.ref(runtime_dir / "catalog.json")
    templates = d9.read_metadata(templates_ref)
    assert len(templates) == 27
    for b in templates.values():
        value = d9.read_metadata(b)
        assert value["producer"] == d9.ref(bundle.__file__)
        driver.profile_config(value)
    spec.update(
        task="R1-63o",
        status="unsigned_D5_review_ready",
        version_note="D.5, provenance v7/role v2, runtime v3, cost artifact v5; fresh session required.",
        matrix=matrix_ref,
        protocol=matrix["protocol"],
        normative_closure=norm,
        cost_admission_source_unsigned=cost_ref,
        runtime_templates=templates_ref,
        production_bundle_producer=d9.ref(bundle.__file__),
        freeze_candidate=None,
    )
    cfg = spec["d9"]["clearance"]["configuration_bindings"]
    cfg.update(
        cost_admission_source_unsigned=cost_ref,
        normative_closure=norm_ref,
        execution_plan=cost["bindings"]["execution_plan"],
    )
    spec["historical_package_v10"] = old_spec_ref
    for stage in ("clearance", "draw", "seal"):
        spec["d9"][stage].update(
            receipt_output=str(root / f"docs/tasks/R1-v15-{stage}.receipt.json"),
            resource_output=str(resources / "d9" / stage),
        )
        spec["intended_outputs"][stage] = [
            spec["d9"][stage][k] for k in ("receipt_output", "resource_output")
        ]
    allocation = d9.read_metadata(spec["near_allocation_decision"])
    allocation.update(lead_approved=False, status="draft")
    spec["near_allocation_decision"] = put(
        "docs/tasks/R1-D9f-allocation-contract-template-v10.json", allocation
    )
    common = operator.common(spec)
    forms = {}
    for key, b in spec["receipts"].items():
        if not isinstance(b, dict) or not b.get("path") or key.endswith("_authorization"):
            continue
        value = d9.read_metadata(b)
        if value.get("lead_approved") is not False:
            raise PermissionError("cannot transform signed receipt: " + key)
        value.update(
            common, candidate_name="v15", lead_approved=False, status="draft", template_only=True
        )
        for field in ("normative_closure", "near_allocation_decision", "configuration_bindings"):
            if field in value:
                value[field] = cfg if field == "configuration_bindings" else spec[field]
        if key == "protocol_admission":
            value.update(full_validation_reviewed=False, cap_fidelity_policy_reviewed=False)
        forms[key] = put(f"docs/tasks/R1-D9-{key.replace('_', '-')}-template-v10.json", value)
    spec["receipts"].update(forms)
    construction = d9.read_metadata(spec["construction_inputs"])
    construction.update(
        matrix=matrix_ref,
        full_validation=spec["full_validation"],
        role_plan=spec["d9"]["clearance"]["role_plan"],
        draw_receipt=dict(path=spec["d9"]["draw"]["receipt_output"], sha256=None),
        output=str(resources / "endpoints"),
        report=str(report_root / "endpoints-written.json"),
    )
    spec["construction_inputs"] = put(
        "docs/tasks/R1-D10c-construction-inputs-template-v10.json", construction
    )
    for stage in ("clearance", "draw", "seal"):
        key = stage + "_authorization"
        value = d9.read_metadata(spec["receipts"][key])
        if value.get("lead_approved") is not False:
            raise PermissionError("cannot transform signed authorization")
        value.update(
            common,
            candidate_name="v15",
            lead_approved=False,
            status="draft",
            request_sha256=None,
            inspection_only_request_sha256=d9.contract(spec, stage),
        )
        forms[key] = put(f"docs/tasks/R1-D9-{stage}-authorization-template-v10.json", value)
        spec["receipts"][key] = forms[key]
    spec_ref = put("docs/tasks/R1-D9-inputs-v11.json", spec)
    parent_ref = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v14.json")
    candidate = d9.read_metadata(parent_ref)
    bindings = {}

    def bind(b):
        actual = d9.ref(b["path"])
        if actual["sha256"] != b["sha256"]:
            raise ValueError("active binding changed: " + b["path"])
        bindings[b["path"]] = b["sha256"]

    # Bind every installed implementation, avoiding an underinclusive imported-code inventory.
    for directory in ("scripts", "src/pccap"):
        for p in sorted((ROOT / directory).rglob("*.py")):
            bind(d9.ref(p))
    bind(d9.ref(ROOT / "requirements.lock"))
    bind(d9.ref(ROOT / "docs/R1_stage4_report_skeleton.md"))
    bind(d9.ref(ROOT / "docs/tasks/R1-D9-operator-sheet-v9.md"))
    for b in [
        *paths.values(),
        parent_ref,
        norm_ref,
        templates_ref,
        *templates.values(),
        *cost["bindings"].values(),
    ]:
        bind(b)
    for value in [spec, matrix, cost]:
        for b, _, _ in graph.edges(value):
            bind(b)
    for which in ("role_plan", "evidence"):
        value = d9.read_resource(spec["d9"]["clearance"][which])
        for b in value["evidence_bindings"]:
            bind(b)
    bindings.update(norm["bindings_sha256"])
    current = {
        str(p.relative_to(ROOT)): d9.sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))
    }
    # Historical candidate is an immutable audit source. Do not relabel its old
    # dry-runs, approvals or observed recipes as active admission evidence.
    historical_fields = (
        "historical_binding_archives",
        "operative_preteacher_v5",
        "historical_roles_v2",
        "clearance_dry_run",
        "analysis_inventory",
        "independent_review",
        "full_endpoint_profiles",
        "requests_requiring_new_approval",
        "dry_reports",
    )
    history = {k: candidate.pop(k) for k in historical_fields if k in candidate}
    candidate.update(
        schema_version=15,
        name="freeze_candidate_v15",
        task="R1-63o",
        status="unsigned_D5_current_implementations_historical_evidence_preserved",
        producer=d9.ref(__file__),
        historical_candidate=parent_ref,
        historical_review_fields=history,
        normative_closure=norm,
        matrix=matrix_ref,
        protocol=spec["protocol"],
        d9_inputs=spec_ref,
        d9_templates=forms,
        construction_inputs=spec["construction_inputs"],
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        operator=d9.ref(operator.__file__),
        runtime_templates=templates_ref,
        production_bundle_producer=spec["production_bundle_producer"],
        cost_admission_source_unsigned=cost_ref,
        cost_admission_receipt=None,
        execution_plan=cost["bindings"]["execution_plan"],
        operative_clearance_evidence=spec["d9"]["clearance"]["evidence"],
        role_plan=spec["d9"]["clearance"]["role_plan"],
        near_allocation_decision=spec["near_allocation_decision"],
        installed_driver_code_sha256=driver.code_identity(),
        sealed_backend_donor_sha256=backend.DONOR_SHA256,
        src_pccap_files=current,
        src_pccap_tree_sha256=digest(current),
        prospective_scope=matrix["prospective_scope"],
        inference_interpretation=matrix["inference_interpretation"],
        bindings_sha256=bindings,
        confirmation_protocol_frozen=False,
        draw_authorized=False,
        launch_authorized=False,
        gpu_seconds=0,
        sealed_payloads_opened=0,
    )
    for gate in candidate["gate_inventory"]:
        if gate["gate"] == "U01":
            gate["closure"] = (
                "Admit D.5: DEC-068 triplet-first, DEC-069 preliminary summaries and t sensitivity; unchanged D.4 scope and DEC-064 cap policy."
            )
        elif gate["gate"] == "U12":
            gate["closure"] = (
                "Unchanged 63 registered intervals and classifier; every realization/order dispersion and assumption-labelled pointwise 95% t sensitivity displayed; no demonstrated familywise coverage or established population effect."
            )
        elif gate["gate"] == "U18":
            gate["closure"] = (
                "D.5 triplet-first execution plan v4; unchanged 750 process-hour cap and October 9 stop; conditional forecasts."
            )
        elif gate["gate"] == "U17":
            gate["closure"] = (
                "Fresh D.5 session, genuine gate closures and authorized draw/endpoints/seal; exact production publication. Content lock is not scientific admission."
            )
    candidate["remaining_gates"] = [g for g in candidate["gate_inventory"] if g["status"] == "open"]
    proof = verify(candidate)
    candidate_ref = put("manifests/revision_v1/freeze_candidate_v15.json", candidate)
    preview, state = d9.prepare(spec, "clearance", evaluate_clearance=True)
    non_approval = [b for b in preview["blocked"] if b["gate"] != "owner_receipts"]
    if non_approval or "clearance" not in state:
        raise ValueError("native clearance failed: " + str(preview["blocked"]))
    proof.update(
        candidate=candidate_ref,
        inputs=spec_ref,
        cost=cost_proof,
        resources=refreshes,
        runtime_templates=len(templates),
        usable_subjects=preview["usable_subjects"],
        unsigned_clearance_blockers=preview["blocked"],
        draws=0,
        seals=0,
        model_calls=0,
        cost_numerical_content_changed=False,
        core_cells=285,
        extension_cells=45,
        caveat="Candidate/native consumer verification is distinct from recursive historical-source review.",
    )
    graph.write(report_root / "package-verification.json", proof)
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--draft")
    args = p.parse_args()
    result = build(args.draft)
    print(json.dumps({k: v for k, v in result.items() if k != "resources"}, indent=2))
