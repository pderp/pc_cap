"""Publish unsigned option-D operator inputs; never draw, seal, approve or launch."""

from __future__ import annotations

import argparse
import copy
import json

from scripts import r1_d9_layouts as layouts
from scripts import r1_d9_receipts as d9

ROOT = d9.ROOT
REFRESH_DRAFTS = False


def read(name):
    return json.loads((ROOT / name).read_text())


def publish(name, value):
    path = ROOT / name
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text() != raw:
            existing = json.loads(path.read_text())
            if (
                not REFRESH_DRAFTS
                or any(
                    existing.get(k) is True
                    for k in ("lead_approved", "launch_allowed", "draw_authorized")
                )
                or existing.get("status") == "closed"
            ):
                raise FileExistsError("version changed input instead of overwriting: " + str(path))
            # Only the enumerated unsigned drafts and dry reports below are refreshable.
            path.write_text(raw)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as f:
            f.write(raw)
    return d9.ref(path)


def main():
    global REFRESH_DRAFTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-drafts", action="store_true")
    REFRESH_DRAFTS = parser.parse_args().refresh_drafts
    promoted = read("logs/r1_round24/r1-d10g-promotion-v2.json")
    roles = read("logs/r1_round24/r1-d10g-roles-v2.json")
    parent = ROOT / "manifests/revision_v1/run_matrix_v5_2_option_D.json"
    matrix = json.loads(parent.read_text())
    protocol = d9.ref(ROOT / "docs/R1_stage4_protocol_draft_v5_2_D.md")
    layout = layouts.production("D")
    matrix.update(
        scope="confirmation_draft",
        task="R1-49h/R1-58e",
        status="operative_context_review; teacher_roles_admission_and_idle_patch_pending",
        producer=d9.ref(__file__),
        parent_option_matrix=d9.ref(parent),
        protocol=protocol,
        preteacher_evidence=promoted["evidence"],
        context_adoption=promoted["adoption"],
        calibration=d9.ref(ROOT / "manifests/revision_v1/calibration_v3.json"),
        analysis_implementation={
            n: d9.ref(ROOT / f"scripts/{n}.py")
            for n in (
                "r1_49g_analyze",
                "r1_49g_inference",
                "r1_49g_secondary",
                "r1_75_analysis_stage4_v1",
            )
        },
    )
    matrix["secondary_benchmarks"]["implementation"] = d9.ref(ROOT / "scripts/r1_49g_secondary.py")
    d9.check_matrix_layout(matrix)
    matrix_ref = publish("manifests/revision_v1/run_matrix_v5_2_D.json", matrix)
    spec = read("docs/tasks/R1-D9-inputs-v2.json")
    spec.update(
        schema_version=3,
        contract_version=2,
        task="R1-D9d/R1-58e",
        status="unsigned_pending_final_teacher_roles_and_owner_admissions",
        dataset_layouts=layout,
        layout_sha256=layouts.digest(layout),
        matrix=matrix_ref,
        protocol=protocol,
        freeze_candidate={"path": None, "sha256": None},
        historical_freeze_candidate=d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v7.json"),
        note="Preteacher evidence is inspection-only. Bind merged certified teacher/role evidence before clearance. Freeze v8 must be rebuilt after idle-boundary patches.",
        pending={
            "final_teacher_evidence": None,
            "joint_role_merged_evidence": None,
            "actual_draw_and_endpoint_resources": None,
            "exposure_after_commit": promoted["exposure_as_of_commit"],
            "near_family_admission": "zsRE same-template/different-subject; explicit review required",
            "idle_boundary_patches_and_freeze_v8": None,
        },
    )
    spec["d9"]["clearance"].update(evidence=promoted["evidence"], role_plan=roles["role_plan"])
    spec["d9"]["clearance"]["configuration_bindings"]["comparator_development_recipes"] = [
        d9.ref(p) for p in sorted((ROOT / "docs/tasks/R1-73d").glob("*.recipe.json"))
    ]
    spec["d9"]["draw"]["composition_catalog"] = roles["composition_catalog"]
    for stage in ("clearance", "draw", "seal"):
        spec["d9"][stage]["resource_output"] = str(
            ROOT.parent / "assets/runs/pc_cap/R1/r1_d9_final_v3" / stage
        )
    spec["intended_outputs"] = {
        **spec["intended_outputs"],
        **{
            s: [spec["d9"][s]["receipt_output"], spec["d9"][s]["resource_output"]]
            for s in ("clearance", "draw", "seal")
        },
    }
    common = dict(
        contract_version=2,
        dataset_layouts=layout,
        layout_sha256=layouts.digest(layout),
        matrix=matrix_ref,
        protocol=protocol,
        register=spec["register"],
        status="draft",
        lead_approved=False,
        template_only=True,
    )
    for name in ("protocol_admission", "rng_admission", "endpoint_construction"):
        stem = name.replace("_", "-")
        template = read(f"docs/tasks/R1-D9-{stem}-template-v2.json")
        template.update(copy.deepcopy(common))
        template.pop("roles_per_realization", None)
        template.pop("realizations", None)
        if name == "protocol_admission":
            template["endpoint_role_plan"] = roles["role_plan"]
            template["configuration_bindings"] = copy.deepcopy(
                spec["d9"]["clearance"]["configuration_bindings"]
            )
        spec["receipts"][name] = publish(f"docs/tasks/R1-D9-{stem}-template-v3.json", template)
    for stage in ("clearance", "draw", "seal"):
        template = read(f"docs/tasks/R1-D9-{stage}-authorization-template-v2.json")
        template.update(copy.deepcopy(common))
        template.update(
            request_sha256=None, inspection_only_request_sha256=d9.contract(spec, stage)
        )
        spec["receipts"][stage + "_authorization"] = publish(
            f"docs/tasks/R1-D9-{stage}-authorization-template-v3.json", template
        )
    inputs = publish("docs/tasks/R1-D9-inputs-v3.json", spec)
    construction = read("docs/tasks/R1-D10c-construction-inputs-template-v1.json")
    construction.update(
        matrix=matrix_ref,
        role_plan=roles["role_plan"],
        catalog=roles["composition_catalog"],
        dataset_layouts=layout,
        layout_sha256=layouts.digest(layout),
        output=str(ROOT.parent / "assets/runs/pc_cap/R1/r1_d10c/final_endpoints_v3"),
        report=str(ROOT / "logs/r1_round24/r1-d10c-final-construction.json"),
    )
    publish("docs/tasks/R1-D10c-construction-inputs-template-v3.json", construction)
    for stage in ("clearance", "draw", "seal"):
        report, _ = d9.prepare(spec, stage)
        if any(b["gate"] == "bound_inputs_or_outputs" for b in report["blocked"]):
            raise ValueError(report)
        if report["ready_for_owner_execution"]:
            raise AssertionError("unsigned templates unexpectedly admitted")
        publish(f"logs/r1_round24/r1-d9-{stage}-dry-v3.json", report)
    publish(
        "logs/r1_round24/r1-58e-operator-inputs.json",
        {
            "task": "R1-58e",
            "inputs": inputs,
            "matrix": matrix_ref,
            "protocol": protocol,
            "status": "dry_inputs_valid_unsigned_prerequisites_refused",
            "draws": 0,
            "seals": 0,
            "gpu_seconds": 0,
            "launch_authorized": False,
        },
    )


if __name__ == "__main__":
    main()
