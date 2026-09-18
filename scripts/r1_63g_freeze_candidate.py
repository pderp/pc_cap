"""Post-R1-77d dry freeze candidate v8; no signing, draw, seal, or freezing."""

from __future__ import annotations

import copy
import json

from scripts import r1_68c_dev_cell as driver
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipts as d9
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10a_review_core import digest


def verify(candidate):
    if candidate.get("schema_version", 0) >= 12:
        if candidate.get("schema_version", 0) >= 15:
            from scripts.r1_49o_normative_closure import verify as verify_normative
        elif candidate.get("schema_version", 0) >= 14:
            from scripts.r1_49n_normative_closure import verify as verify_normative
        else:
            from scripts.r1_49j_normative_closure import verify as verify_normative

        verify_normative(candidate)
    for name, expected in candidate["bindings_sha256"].items():
        if d9.sha(name) != expected:
            raise ValueError("candidate binding changed: " + name)
    if candidate["installed_driver_code_sha256"] != driver.code_identity():
        raise ValueError("driver identity changed")
    if backend.DONOR_SHA256 != d9.sha(ROOT / "scripts/r1_68c_dev_cell.py"):
        raise ValueError("sealed donor differs")
    current = {str(p.relative_to(ROOT)): d9.sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    if current != candidate["src_pccap_files"] or digest(current) != candidate["src_pccap_tree_sha256"]:
        raise ValueError("installed source tree differs")
    if any(candidate[k] is not False for k in (
        "confirmation_protocol_frozen", "draw_authorized", "launch_authorized")):
        raise ValueError("dry candidate must grant no authority")
    matrix = d9.read_metadata(candidate["matrix"])
    if d9.check_matrix_layout(matrix) != candidate["dataset_layouts"]:
        raise ValueError("matrix/layout mismatch")
    spec = d9.read_metadata(candidate["d9_inputs"])
    for stage, value in candidate["d9_request_sha256"].items():
        if d9.contract(spec, stage) != value:
            raise ValueError("D9 request changed: " + stage)
    if [g["gate"] for g in candidate["gate_inventory"]] != [f"U{i:02}" for i in range(1, 19)]:
        raise ValueError("complete gate inventory required")
    return dict(task="R1-63g", bindings=len(candidate["bindings_sha256"]),
                open_gates=[g["gate"] for g in candidate["remaining_gates"]],
                context_adjudication_admitted=candidate["context_adjudication_admitted"],
                teacher_roles_complete=True, frozen=False, launch_authorized=False)


def assemble():
    bindings = {}

    def bind(path, expected=None):
        p = (ROOT / path).resolve()
        if not p.is_relative_to(ROOT.parent) or "confirm" in p.parts or "stage4_sealed_payloads" in p.parts:
            raise PermissionError("unsealed local metadata/code only")
        b = d9.ref(p)
        if expected is not None and b["sha256"] != expected:
            raise ValueError("input changed: " + str(p))
        if str(p) in bindings and bindings[str(p)] != b["sha256"]:
            raise ValueError("input changed during build")
        bindings[str(p)] = b["sha256"]
        return b

    def checked(b):
        return bind(b["path"], b["sha256"])

    def read(path):
        return json.loads((ROOT / path).read_text())

    parent = read("manifests/revision_v1/freeze_candidate_v7.json")
    spec_path = ROOT / "docs/tasks/R1-D9-inputs-v3-post77d.json"
    spec = read(spec_path)
    matrix = d9.read_metadata(spec["matrix"])
    layout = d9.check_matrix_layout(matrix)
    evidence = d9.read_resource(spec["d9"]["clearance"]["evidence"])
    if not evidence["context_adjudication_admitted"] or not evidence["teacher_token_review_complete"] or not evidence["role_compatibility_complete"]:
        raise ValueError("adopted context, certified teacher and merged roles required")
    for b in evidence["evidence_bindings"]:
        checked(b)
    role_plan = d9.read_resource(spec["d9"]["clearance"]["role_plan"])
    for b in role_plan["evidence_bindings"]:
        checked(b)
    templates = {name: checked(b) for name, b in spec["receipts"].items() if b.get("path")}
    current = {str(p.relative_to(ROOT)): d9.sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    for name, sha in current.items():
        bind(name, sha)
    for p in sorted((ROOT / "scripts").glob("*.py")):
        bind(p)
    for directory in ("R1-64e", "R1-73b-post77d", "R1-73d-post77d"):
        for p in sorted((ROOT / "docs/tasks" / directory).glob("*.json")):
            bind(p)
    gates = copy.deepcopy(parent["gate_inventory"])
    closures = {
        "U01": "Adopt corrected v5.2-D protocol/matrix; explicit optional-extension decision. X15 document corrections remain owner work.",
        "U02": "Bind primary v5 weights, selection audit and reference conventions to final populations; disclose zsRE empty baseline.",
        "U03": "Reconcile S1 budget with v5 and final continued-base calibration/fidelity; bind measured S1 costs.",
        "U04": "Teacher/role checks now complete; lead signs current zsRE clearance and attests exposure through draw.",
        "U05": "Bind CounterFact DEC-042 source exception and signed final clearance; no claim of a strict-source fresh remainder.",
        "U06": "Context adjudication admitted; teacher and all93 joint-role capacity checks pass. Sign exact clearance, protocol/RNG and draw requests plus current exposure.",
        "U07": "Actual authorized draw, deterministic endpoints and seals with independent expected populations; no synthetic receipt substitutes.",
        "U08": "R1-77d variable cadence is installed and tested. Bind final full challenge/validation inventory and costs at 100/300/1000 or MQ100/300.",
        "U09": "Q15 NM-template-v1 semantics need lead admission; postdraw paired availability and fixed missing slots still required.",
        "U11": "Patched source, R1-68e driver and reconciled sealed backend are bound. Current recipes inspect; owner real-base corrected MQ profiles and final backend admission remain.",
        "U12": "DEC-05763-interval family and R1-49h implementation bound; MQ1000 remains unavailable. Final independent populations and admission required.",
        "U13": "Accepted DEC-058 classifier unchanged; bind final full fidelity/admission receipts.",
        "U14": "DEC-059 retained for zsRE/CF; MQactual300 descriptive with no transferred thresholds. Final resource ceilings/endpoint inventories required.",
        "U15": "Bind actual independent sealed populations and results; preserve incomplete/missing populations in final analysis.",
        "U16": "Owner prices full endpoints and process envelopes, resolves single application of concurrency ceiling factor, admits per-cell and shared process-hour budgets on September20.",
        "U17": "Close scientific and operational gates; apply reviewed document corrections; rebuild affected requests and final code/backend/environment bindings before owner freeze.",
        "U18": "Reprice admitted option-D360core/45optional inventory; distinguish process-hours from wall hours; preserve October9 stop and DEC-051/052 reporting.",
    }
    for gate in gates:
        if gate["gate"] in closures:
            gate.update(status="open", closure=closures[gate["gate"]])
    refresh = read("logs/r1_round25/r1-d10h-operator-refresh.json")
    candidate = dict(
        schema_version=8, name="freeze_candidate_v8", task="R1-63g", option="D",
        status="dry_postpatch_teacher_roles_complete_owner_admissions_pending",
        producer=bind(__file__), historical_candidate=bind("manifests/revision_v1/freeze_candidate_v7.json"),
        matrix=checked(spec["matrix"]), protocol=checked(spec["protocol"]),
        calibration=checked(matrix["calibration"]), primary_condition=checked(matrix["primary_condition"]),
        register=checked(spec["register"]), dataset_layouts=layout,
        operative_clearance_evidence=checked(spec["d9"]["clearance"]["evidence"]),
        operative_preteacher_v5=checked(read("logs/r1_round24/r1-d10g-promotion-v2.json")["evidence"]),
        role_plan=checked(spec["d9"]["clearance"]["role_plan"]),
        historical_roles_v2=checked(read("logs/r1_round24/r1-d10g-roles-v2.json")["role_plan"]),
        context_adoption=checked(evidence["orchestrator_review_receipt"]),
        teacher_certification=bind("logs/r1_round25/r1-d10h-certification.json"),
        clearance_dry_run=bind("logs/r1_round25/r1-d9-clearance-dry-post77d.json"),
        near_family_proposal=bind("docs/R1_near_miss_family_v5_2_proposal.md"),
        concurrency_policy=bind("docs/R1_stage4_queue_concurrency_v1.md"),
        execution_plan=bind("docs/R1_execution_plan_v1.md"),
        analysis_inventory=bind("logs/r1_round24/r1-49h-draft-inventory-v2.json"),
        independent_review=bind("logs/r1_round25/r1-x15-independent.json"),
        d9_inputs=bind(spec_path), d9_templates=templates,
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        requests_requiring_new_approval=refresh["stage_request_changes"],
        d9_binding_note="Candidate inventories D9; D9 does not hash this candidate, avoiding a dependency cycle. Final owner freeze consumes completed receipts.",
        installed_driver=bind("scripts/r1_68c_dev_cell.py"),
        installed_driver_code_sha256=driver.code_identity(),
        sealed_backend=bind("scripts/r1_77b_sealed_backend.py"),
        sealed_backend_donor_sha256=backend.DONOR_SHA256,
        src_pccap_files=current, src_pccap_tree_sha256=digest(current),
        gate_inventory=gates, remaining_gates=[g for g in gates if g["status"] == "open"],
        core_cells=360, extension_cells=45, accepted_primary_intervals=63,
        context_adjudication_admitted=True, confirmation_protocol_frozen=False,
        draw_authorized=False, launch_authorized=False, experiment_stop="2026-10-09",
        bindings_sha256=bindings, gpu_seconds=0, sealed_payloads_opened=0)
    verify(candidate)
    return candidate


if __name__ == "__main__":
    candidate = assemble()
    binding = write_new(ROOT / "manifests/revision_v1/freeze_candidate_v8.json", candidate)
    report = dict(verify(candidate), candidate=binding)
    write_new(ROOT / "logs/r1_round25/r1-63g-verification.json", report)
    print(json.dumps(report, indent=2))
