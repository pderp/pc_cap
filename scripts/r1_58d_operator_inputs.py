"""Populate reviewable D9 inputs and unsigned approval templates; never execute D9."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scripts import r1_d9_receipt_core as core
from scripts.r1_d9_receipts import contract, prepare, ref
from scripts.r1_d10a_review import ASSETS, ROOT, write_new


def build():
    template = ROOT / "docs/tasks/R1-D9-inputs-template-v1.json"
    spec = json.loads(template.read_text())
    review = json.loads((ROOT / "logs/r1_round22/r1-d10a-review-v4.json").read_text())
    endpoints = json.loads((ROOT / "logs/r1_round22/r1-d10c-prepare-v2.json").read_text())
    spec.update(
        task="R1-58d",
        status="populated CPU evidence; capacity, final teacher and lead admissions remain open",
    )
    spec["note"] = (
        "Clearance currently binds partial D10a evidence for inspection. Replace with teacher+role merged evidence after policy/context resolution. No supplied template is an approval."
    )
    for name in ("register", "matrix", "protocol", "freeze_candidate"):
        spec[name] = ref(spec[name]["path"])
    configs = {
        "calibration_v3": ref(ROOT / "manifests/revision_v1/calibration_v3.json"),
        "primary_v5": ref(ROOT / "manifests/revision_v1/primary_condition_v5.json"),
        "final_base_recipe": ref(ROOT / "docs/tasks/R1-68c-zsre-v5-full.recipe.json"),
        "comparator_development_recipes": [
            ref(p) for p in sorted((ROOT / "docs/tasks/R1-73b").glob("*.recipe.json"))
        ],
    }
    spec["d9"]["clearance"].update(
        evidence=review["evidence"],
        role_plan=endpoints["role_plan"],
        configuration_bindings=configs,
    )
    spec["d9"]["draw"]["composition_catalog"] = endpoints["composition_catalog"]
    spec["pending"] = {
        "final_teacher_evidence": None,
        "joint_role_merged_evidence": None,
        "capacity_resolution": ref(ROOT / "logs/r1_round22/r1-d10a-capacity-diagnostics-v2.json"),
        "exposure_supplement_after_round21": None,
        "near_family_admission": "zsRE source-masked question template differs from historical same-subject family",
        "actual_draw_and_endpoint_resources": None,
    }
    templates = {}
    for stage in ("clearance", "draw", "seal"):
        path = ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-v2.json"
        value = {
            "template_only": True,
            "operation": stage,
            "status": "draft",
            "lead_approved": False,
            "register": spec["register"],
            "request_sha256": None,
            "instructions": "Resolve review/prerequisite blockers; rerun this stage's dry-run; copy its current request_sha256, review concrete outputs, then the lead changes status to closed and lead_approved to true. Bind the completed file's SHA in inputs.",
        }
        if stage == "draw":
            value.update(master_seed=None, cumulative_exposure_current=False)
        templates[stage] = value
        spec["receipts"][stage + "_authorization"] = {"path": str(path), "sha256": None}
    # The own authorization binding is excluded from its request digest. Future
    # prerequisite approvals necessarily change downstream request digests.
    for stage, value in templates.items():
        value["inspection_only_request_sha256"] = contract(spec, stage)
        path = Path(spec["receipts"][stage + "_authorization"]["path"])
        spec["receipts"][stage + "_authorization"] = write_new(path, value)
    input_ref = write_new(ROOT / "docs/tasks/R1-D9-inputs-v2.json", spec)
    for stage in templates:
        report, _ = prepare(spec, stage)
        report["inputs"] = input_ref
        write_new(ROOT / f"logs/r1_round22/r1-d9-{stage}-dry.json", report)
    common = {
        "template_only": True,
        "status": "draft",
        "lead_approved": False,
        "register": spec["register"],
    }
    rng = {
        **common,
        "master_seed": None,
        "rng_rule": core.RNG_RULE,
        "numpy_version": np.__version__,
        "paired_order_rule": "R1-D9-order-v1; orders100..104; same order for every condition",
        "composition_rule": "all bound catalog cases with every dependency in the realization edit set",
    }
    protocol = {
        **common,
        "matrix": spec["matrix"],
        "protocol": spec["protocol"],
        "extension_admitted": None,
        "configuration_bindings": configs,
        "endpoint_role_plan": endpoints["role_plan"],
        "near_family_reviewed": False,
    }
    endpoint = {
        **common,
        "draw_receipt": None,
        "reservations": None,
        "bundle": None,
        "independent_population": None,
        "realizations": 3,
        "datasets": list(core.DATASETS),
        "roles_per_realization": core.ROLES,
        "all_roles_disjoint": False,
        "composition_dependencies_closed": False,
        "missing_endpoint_review_complete": False,
    }
    for name, value in (
        ("rng-admission", rng),
        ("protocol-admission", protocol),
        ("endpoint-construction", endpoint),
    ):
        write_new(ROOT / f"docs/tasks/R1-D9-{name}-template-v2.json", value)
    construction = {
        "draw_receipt": {"path": spec["d9"]["draw"]["receipt_output"], "sha256": None},
        "matrix": spec["matrix"],
        "extension_admitted": None,
        "catalog": endpoints["composition_catalog"],
        "role_plan": endpoints["role_plan"],
        "drift": ref(ASSETS / "data/prepared/lm/drift_tokens.npy"),
        "output": str(ASSETS / "runs/pc_cap/R1/r1_d10c/final_endpoints_v1"),
        "report": str(ROOT / "logs/r1_round22/r1-d10c-final-construction.json"),
        "status": "draw receipt/extension admission pending; no construction executed",
    }
    write_new(ROOT / "docs/tasks/R1-D10c-construction-inputs-template-v1.json", construction)
    print(
        json.dumps({"inputs": input_ref, "approvals_emitted": 0, "draws": 0, "seals": 0}, indent=2)
    )


if __name__ == "__main__":
    build()
