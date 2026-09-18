"""Rebind the unsigned D.4/v4 package; preserve historical bytes and open gates."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

from scripts import r1_58g_operator as operator
from scripts import r1_58h_cost_contract as cost_contract
from scripts import r1_63j_production_bundle as bundle
from scripts import r1_68c_dev_cell as driver
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipts as d9
from scripts.r1_49n_normative_closure import closure
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10a_review_core import digest

LOG = ROOT / "logs/r1_round36"


def archive_source(path, expected):
    """Recover the exact parent-bound source, never relabel present bytes as old."""
    p = Path(path)
    relative = p.relative_to(ROOT)
    target = LOG / "source_snapshot" / relative
    if target.exists():
        if d9.sha(target) != expected:
            raise ValueError("source snapshot identity collision")
        return d9.ref(target)
    commits = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", str(relative)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for commit in commits:
        raw = subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=ROOT, capture_output=True)
        if raw.returncode == 0 and hashlib.sha256(raw.stdout).hexdigest() == expected:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as f:
                f.write(raw.stdout)
            return d9.ref(target)
    raise ValueError("cannot recover exact historical source bytes: " + path)


def build():
    parent = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v13.json")
    candidate = copy.deepcopy(d9.read_metadata(parent))
    bindings = {}
    archives = {}
    for path, expected in candidate["bindings_sha256"].items():
        if d9.sha(path) != expected:
            archived = archive_source(path, expected)
            archives[path] = archived
            bindings[archived["path"]] = archived["sha256"]
        bindings[path] = d9.sha(path)

    def bind(b):
        if d9.sha(b["path"]) != b["sha256"]:
            raise ValueError("candidate source changed: " + b["path"])
        bindings[b["path"]] = b["sha256"]
        return b

    def nested(value):
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                bind(value)
            else:
                for v in value.values():
                    nested(v)
        elif isinstance(value, list):
            for v in value:
                nested(v)

    cost_ref = bind(d9.ref(ROOT / "docs/tasks/R1-cost-admission-receipt-v4.json"))
    cost = d9.read_metadata(cost_ref)
    cost_contract.validate(cost)
    nested(cost["bindings"])
    for c in cost["cells"]:
        bind(c["measurement"])
        nested(d9.read_metadata(c["measurement"])["source_bindings"])
    for p in sorted((ROOT / "docs/tasks/R1-post63l-active").rglob("*.json")):
        bind(d9.ref(p))
    for p in sorted((ROOT / "docs/tasks/R1-64g-post63l").glob("*.json")):
        bind(d9.ref(p))
    runtime = ROOT / "docs/tasks/R1-63m-runtime-v2"
    if not runtime.exists():
        bundle.template_catalog(runtime)
    templates_ref = bind(d9.ref(runtime / "catalog.json"))
    templates = d9.read_metadata(templates_ref)
    for b in templates.values():
        bind(b)
        bind(d9.read_metadata(b)["source_recipe"])
    norm = closure()
    bindings.update(norm["bindings_sha256"])
    norm_ref = bind(write_new(LOG / "normative-closure-D4.json", norm))
    spec = d9.read_metadata(candidate["d9_inputs"])
    spec.update(
        task="R1-63m/R1-58l",
        status="unsigned_D4_cost_v4_review_ready",
        matrix=cost["matrix"],
        protocol=cost["protocol"],
        full_validation=cost["full_validation"],
        normative_closure=norm,
        cost_admission_source_unsigned=cost_ref,
        runtime_templates=templates_ref,
        shared_process_hours_proposed=750,
        production_bundle_producer=bind(d9.ref(bundle.__file__)),
    )
    cfg = spec["d9"]["clearance"]["configuration_bindings"]
    cfg.update(
        cost_admission_source_unsigned=cost_ref,
        execution_plan=cost["bindings"]["execution_plan"],
        normative_closure=norm_ref,
        final_base_recipe=d9.ref(
            ROOT / "docs/tasks/R1-post63l-active/R1-64e/R1-64e-zsre-primary-v5.recipe.json"
        ),
        comparator_development_recipes=[
            d9.ref(p)
            for p in sorted(
                (ROOT / "docs/tasks/R1-post63l-active/R1-73d-post68f").glob("*.recipe.json")
            )
        ],
        zsre_counterfact_development_recipes=[
            d9.ref(p)
            for p in sorted((ROOT / "docs/tasks/R1-post63l-active/R1-64e").glob("*.recipe.json"))
        ],
        full_validation_measurements=d9.ref(ROOT / "logs/r1_round35/chain-s-inventory.json"),
        continuation_gate_evidence=d9.ref(LOG / "U03-continuation-evidence.json"),
    )
    for stage in ("clearance", "draw", "seal"):
        spec["d9"][stage].update(
            receipt_output=str(ROOT / f"docs/tasks/R1-v14-{stage}.receipt.json"),
            resource_output=str(ROOT.parent / f"assets/runs/pc_cap/R1/r1_d9_v14/{stage}"),
        )
        spec["intended_outputs"][stage] = [
            spec["d9"][stage][k] for k in ("receipt_output", "resource_output")
        ]
    # DEC-062's accepted row is stable although its original whole decisions file
    # may have gained subsequent decisions. Bind the exact accepted row snapshot.
    decision = d9.read_metadata(spec["near_allocation_decision"])
    source = Path(decision["decision_source"]["path"])
    if decision["decision_row"] not in source.read_text().splitlines():
        raise ValueError("accepted DEC-062 row changed")
    snapshot = LOG / "DEC-062-decision-source.md"
    if snapshot.exists():
        if snapshot.read_text() != decision["decision_row"] + "\n":
            raise ValueError("DEC-062 decision snapshot changed")
    else:
        with snapshot.open("x") as f:
            f.write(decision["decision_row"] + "\n")
    decision.update(decision_source=d9.ref(snapshot), lead_approved=False, status="draft")
    spec["near_allocation_decision"] = bind(
        write_new(ROOT / "docs/tasks/R1-D9f-allocation-contract-template-v9.json", decision)
    )
    forms = {}
    common = operator.common(spec)
    for key, b in spec["receipts"].items():
        if not b.get("path") or key.endswith("_authorization"):
            continue
        value = d9.read_metadata(b)
        if value.get("lead_approved") is not False:
            raise PermissionError("cannot refresh a signed receipt")
        value.update(
            common, candidate_name="v14", lead_approved=False, status="draft", template_only=True
        )
        for k in ("normative_closure", "near_allocation_decision", "configuration_bindings"):
            if k in value:
                value[k] = cfg if k == "configuration_bindings" else spec[k]
        if key == "protocol_admission":
            value.update(full_validation_reviewed=False, cap_fidelity_policy_reviewed=False)
        forms[key] = bind(
            write_new(ROOT / f"docs/tasks/R1-D9-{key.replace('_', '-')}-template-v9.json", value)
        )
    spec["receipts"].update(forms)
    construction = d9.read_metadata(
        d9.ref(ROOT / "docs/tasks/R1-D10c-construction-inputs-template-v4.json")
    )
    construction.update(
        matrix=spec["matrix"],
        full_validation=spec["full_validation"],
        draw_receipt=dict(path=spec["d9"]["draw"]["receipt_output"], sha256=None),
        output=str(ROOT.parent / "assets/runs/pc_cap/R1/r1_endpoints_v14"),
        report=str(LOG / "endpoints-written.json"),
    )
    spec["construction_inputs"] = bind(
        write_new(ROOT / "docs/tasks/R1-D10c-construction-inputs-template-v9.json", construction)
    )
    for stage in ("clearance", "draw", "seal"):
        key = stage + "_authorization"
        value = d9.read_metadata(spec["receipts"][key])
        if value.get("lead_approved") is not False:
            raise PermissionError("cannot refresh signed authorization")
        value.update(
            common,
            candidate_name="v14",
            lead_approved=False,
            status="draft",
            request_sha256=None,
            inspection_only_request_sha256=d9.contract(spec, stage),
        )
        forms[key] = bind(
            write_new(ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-v9.json", value)
        )
        spec["receipts"][key] = forms[key]
    spec_ref = bind(write_new(ROOT / "docs/tasks/R1-D9-inputs-v9.json", spec))
    nested(cfg)
    nested({k: spec[k] for k in ("matrix", "protocol", "near_allocation_decision")})
    for name in (
        "r1_63m_candidate",
        "r1_63g_freeze_candidate",
        "r1_58g_operator",
        "r1_58l_cost_v4",
        "r1_49n_protocol_matrix",
        "r1_49n_normative_closure",
        "r1_49n_scope",
        "r1_d9_receipts",
    ):
        bind(d9.ref(ROOT / f"scripts/{name}.py"))
    matrix = d9.read_metadata(spec["matrix"])
    for b in matrix["analysis_implementation"].values():
        bind(b)
    current = {
        str(p.relative_to(ROOT)): d9.sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))
    }
    gates = candidate["gate_inventory"]
    updates = {
        "U01": "Sign D.4/DEC-066 scope and unchanged DEC-064 cap policy; choose optional extension.",
        "U03": "DEC-047 continuation certification and retained checkpoint identities are bound; final calibration/identity admission and historical-vs-v5 training-budget interpretation remain explicit in D.4.",
        "U08": "DEC-063 full and sampled contracts present in every retained recipe; admit actual postdraw independent endpoint populations.",
        "U09": "DEC-061/062 family semantics bound; sign exact requests and review actual postdraw pair missingness.",
        "U11": "Current post-63l identities rebuilt; D.4 whole-package metadata rehearsal tested before publication; actual signed backend admission required.",
        "U12": "Unchanged 63-interval family; MQ checkpoint1000 unavailable and five arms prospectively not run, never imputed.",
        "U13": "DEC-064 cap benchmark labels do not veto primary comparisons; DEC-047 continued-base certification remains required.",
        "U16": "Typed v4 costs/ceilings v2 and reviewed transfers complete, unsigned; lead reviews D.4 budget, sampled memory qualifications and failure charging.",
        "U17": "Sign genuine gate closures and perform authorized draw/endpoints/seal before exact production-bundle freeze publication.",
        "U18": "Review plan v3: D.4 431.307 expected/646.960 ceiling process h, 750 cap, October9 stop; sign schedule admission.",
    }
    for g in gates:
        if g["gate"] in updates:
            g["closure"] = updates[g["gate"]]
    non_signature = [
        "Authorized draw, deterministic endpoints, actual missingness review and independent seals must be produced after exact signatures; synthetic receipts are not real evidence.",
        "U03 final scientific admission must explicitly resolve retained historical continuation-budget interpretation versus primary v5; this package does not claim newly matched training compute.",
    ]
    candidate.update(
        schema_version=14,
        name="freeze_candidate_v14",
        task="R1-63m",
        status="unsigned_D4_v4_cost_basis_complete_admissions_and_postsignature_operations_pending",
        producer=bind(d9.ref(__file__)),
        historical_candidate=bind(parent),
        normative_closure=norm,
        matrix=bind(spec["matrix"]),
        protocol=bind(spec["protocol"]),
        d9_inputs=spec_ref,
        d9_templates=forms,
        construction_inputs=spec["construction_inputs"],
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        operator=bind(d9.ref(operator.__file__)),
        runtime_templates=templates_ref,
        production_bundle_producer=spec["production_bundle_producer"],
        cost_admission_source_unsigned=cost_ref,
        cost_admission_receipt=None,
        execution_plan=cost["bindings"]["execution_plan"],
        core_cells=285,
        extension_cells=45,
        accepted_primary_intervals=63,
        full_validation=spec["full_validation"],
        prospective_scope=matrix["prospective_scope"],
        fidelity_watch=bundle.watch.binding(),
        installed_driver_code_sha256=driver.code_identity(),
        sealed_backend_donor_sha256=backend.DONOR_SHA256,
        src_pccap_files=current,
        src_pccap_tree_sha256=digest(current),
        gate_inventory=gates,
        remaining_gates=[g for g in gates if g["status"] == "open"],
        non_signature_blockers=non_signature,
        cost_nonsignature_gaps=[],
        signatures_only=False,
        historical_binding_archives=archives,
        bindings_sha256=bindings,
        confirmation_protocol_frozen=False,
        draw_authorized=False,
        launch_authorized=False,
        gpu_seconds=0,
        sealed_payloads_opened=0,
    )
    nested(candidate["fidelity_watch"])
    proof = verify(candidate)
    binding = write_new(ROOT / "manifests/revision_v1/freeze_candidate_v14.json", candidate)
    proof.update(
        candidate=binding,
        inputs=spec_ref,
        core_cells=285,
        extension_cells=45,
        cost_nonsignature_gaps=[],
        signatures_only=False,
        non_signature_blockers=non_signature,
    )
    write_new(LOG / "candidate-v14-verification.json", proof)
    return proof


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
