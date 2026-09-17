"""Prepare candidate v9 and unsigned v4 forms; --preview records external blockers.

No signing, RNG, draw, seal, freeze, GPU execution or modification of predecessors.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipts as d9
from scripts.ht4e_claim_ledger import profile_inventory
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d9e_near_family import CONTRACT
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10a_review_core import digest
from scripts.r1_d10b_teacher_review import verify_bindings

LOG = ROOT / "logs/r1_round26"


def external_dependencies(profiles, plan):
    missing = ["chain_Q:" + r["condition"] for r in profiles if r["status"] != "complete"]
    if len(profiles) != 8:
        raise ValueError("eight corrected profile declarations required")
    if not Path(plan).is_file():
        missing.append("execution_plan_v2")
    return missing


def build(*, preview=False):
    profiles = profile_inventory()
    plan = ROOT / "docs/R1_execution_plan_v2.md"
    pending = external_dependencies(profiles, plan)
    if pending and not preview:
        raise ValueError("Final candidate dependencies still outstanding: " + ", ".join(pending))
    tag, forms = ("v9-preview", "v4-preview") if preview else ("v9", "v4")
    profile_ref = write_new(LOG / f"r1-63h-{tag}-profiles.json", dict(profiles=profiles, producer=d9.ref(__file__)))
    previous = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v3-post77d.json"))
    spec = copy.deepcopy(previous)
    review = d9.read_metadata(d9.ref(LOG / "near_final/r1-d9e-real-pool-review.json"))
    matrix = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_DEC061.json")
    protocol = d9.ref(ROOT / "docs/R1_stage4_protocol_v5_2_D_final.md")
    policy = d9.ref(ROOT / "docs/R1_stage4_queue_concurrency_v2.md")
    spec.update(task="R1-63h/R1-58f", status="unsigned_" + tag,
                matrix=matrix, protocol=protocol, near_miss_family_contract=CONTRACT,
                pending=dict(external_dependencies=pending, cost_admission_receipt=False,
                             current_exposure_attestation=False, actual_draw_endpoints_seal_freeze=False),
                note="No authority. Candidate inventories these inputs; no candidate self-hash in the D9 request graph. Later prerequisite/seed changes require fresh request digests.")
    cfg = spec["d9"]["clearance"]
    cfg.update(evidence=review["evidence"], role_plan=review["role_plan"])
    config = cfg["configuration_bindings"]
    config.update(queue_concurrency=policy, corrected_mquake_profiles=profile_ref,
                  near_family_review=d9.ref(LOG / "near_final/r1-d9e-real-pool-review.json"))
    config.pop("execution_plan", None)
    if plan.is_file():
        config["execution_plan"] = d9.ref(plan)
    spec["d9"]["draw"]["composition_catalog"] = review["composition_catalog"]
    for stage in ("clearance", "draw", "seal"):
        spec["d9"][stage].update(resource_output=str(ROOT.parent / "assets/runs/pc_cap/R1" / ("r1_d9_" + tag) / stage),
                                 receipt_output=str(ROOT / f"docs/tasks/R1-{tag}-{stage}.receipt.json"))
        spec["intended_outputs"][stage] = [spec["d9"][stage][k] for k in ("receipt_output", "resource_output")]
    templates = {}
    for name, binding in list(spec["receipts"].items()):
        if not binding.get("path") or name.endswith("_authorization"):
            continue
        value = d9.read_metadata(binding)
        if value.get("lead_approved") is not False or value.get("status") != "draft":
            raise PermissionError("cannot rewrite completed/signed receipts")
        value.update(matrix=matrix, protocol=protocol, near_miss_family_contract=CONTRACT,
                     candidate_name=tag, template_only=True)
        if name == "protocol_admission":
            value.update(configuration_bindings=copy.deepcopy(config), endpoint_role_plan=review["role_plan"],
                         near_family_reviewed=False, zsre_empty_baseline_reviewed=False,
                         queue_ceiling_and_failure_policy_reviewed=False)
        templates[name] = write_new(ROOT / f"docs/tasks/R1-D9-{name.replace('_', '-')}-template-{forms}.json", value)
        spec["receipts"][name] = templates[name]
    previews = {}
    for stage in ("clearance", "draw", "seal"):
        name = stage + "_authorization"
        value = d9.read_metadata(previous["receipts"][name])
        if value.get("lead_approved") is not False:
            raise PermissionError("signed authorization is immutable")
        previews[stage] = d9.contract(spec, stage)
        value.update(matrix=matrix, protocol=protocol, near_miss_family_contract=CONTRACT,
                     candidate_name=tag, request_sha256=None, inspection_only_request_sha256=previews[stage],
                     lead_approved=False, status="draft", template_only=True)
        templates[name] = write_new(ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-{forms}.json", value)
        spec["receipts"][name] = templates[name]
    spec_ref = write_new(ROOT / f"docs/tasks/R1-D9-inputs-{forms}.json", spec)
    construction = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D10c-construction-inputs-template-v3-post77d.json"))
    construction.update(matrix=matrix, role_plan=review["role_plan"], catalog=review["composition_catalog"],
                        output=str(ROOT.parent / "assets/runs/pc_cap/R1" / ("r1_endpoints_" + tag)),
                        report=str(LOG / f"r1-d9e-{tag}-constructed.json"))
    construction_ref = write_new(ROOT / f"docs/tasks/R1-D10c-construction-inputs-template-{forms}.json", construction)
    dry = {}
    for stage in ("clearance", "draw", "seal"):
        report, state = d9.prepare(spec, stage)
        if any(b["gate"] == "bound_inputs_or_outputs" for b in report["blocked"]):
            raise ValueError(report)
        if stage == "clearance" and "clearance" not in state:
            raise ValueError(report)
        dry[stage] = write_new(LOG / f"r1-d9-{stage}-dry-{tag}.json", report)
    bindings = {}

    def bind(value):
        b = d9.ref(ROOT / value) if isinstance(value, (str, Path)) else value
        verify_bindings([b])
        if b["path"] in bindings and bindings[b["path"]] != b["sha256"]:
            raise ValueError("input changed during candidate build")
        bindings[b["path"]] = b["sha256"]
        return b

    for b in [matrix, protocol, policy, spec_ref, construction_ref, profile_ref, review["evidence"], review["role_plan"],
              review["composition_catalog"], *templates.values(), *dry.values()]:
        bind(b)
    for b in d9.read_resource(review["evidence"])["evidence_bindings"] + d9.read_resource(review["role_plan"])["evidence_bindings"]:
        bind(b)
    for p in sorted((ROOT / "scripts").glob("*.py")):
        bind(p)
    source = {str(p.relative_to(ROOT)): d9.sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    for p in source:
        bind(p)
    for group in ("R1-64e", "R1-73b-post77d", "R1-73d-post77d"):
        for p in sorted((ROOT / "docs/tasks" / group).glob("*.json")):
            bind(p)
    for row in profiles:
        bind(row["recipe"])
        for k in ("result", "checkpoint", "receipt"):
            if k in row:
                bind(row[k])
        for b in row["failures"]:
            bind(b)
    gates = copy.deepcopy(d9.read_metadata(d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v8.json"))["gate_inventory"])
    closures = {
        "U01": "Sign final v5.2-D/DEC-061 text and matrix; decide extension.",
        "U06": "All93 Hall checks pass; sign current-exposure clearance, protocol/RNG and exact draw request.",
        "U09": "DEC-061 adopted and implemented; actual postdraw pairing/missingness, endpoint review and source seals remain.",
        "U11": "Installed cadence and new queue/family CPU tests pass; bind all corrected chainQ results and final backend admission.",
        "U16": "Admit execution plan v2, failure-inclusive full endpoint/process costs, solo ceilings and shared process-hour budget.",
        "U17": "Obtain all exact gate closures and freeze actual populations/recipes/current code after prerequisite completion.",
        "U18": "Admit October9 schedule and full360core/45optional cost inventory; preserve DEC052 partial reporting.",
    }
    for g in gates:
        if g["gate"] in closures:
            g.update(status="open", closure=closures[g["gate"]])
    doc = d9.read_metadata(matrix)
    candidate = dict(schema_version=9, name="freeze_candidate_"+tag, task="R1-63h", option="D",
                     producer=bind(__file__), historical_candidate=bind("manifests/revision_v1/freeze_candidate_v8.json"),
                     status="dry_external_dependencies_pending" if pending else "dry_lead_signatures_cost_receipt_and_actual_population_operations_pending",
                     matrix=matrix, protocol=protocol, register=bind(spec["register"]), calibration=bind(doc["calibration"]),
                     primary_condition=bind(doc["primary_condition"]), dataset_layouts=doc["dataset_layouts"],
                     operative_clearance_evidence=review["evidence"], role_plan=review["role_plan"],
                     near_family_contract=CONTRACT, concurrency_policy=policy,
                     execution_plan=bind(plan) if plan.is_file() else None,
                     corrected_mquake_profiles=profile_ref, external_dependencies=pending,
                     d9_inputs=spec_ref, d9_templates=templates, construction_inputs=construction_ref,
                     d9_request_sha256={s:d9.contract(spec,s) for s in ("clearance","draw","seal")},
                     dry_reports=dry, gate_inventory=gates, remaining_gates=[g for g in gates if g["status"]=="open"],
                     installed_driver_code_sha256=driver.code_identity(), sealed_backend_donor_sha256=backend.DONOR_SHA256,
                     src_pccap_files=source, src_pccap_tree_sha256=digest(source), bindings_sha256=bindings,
                     context_adjudication_admitted=True, confirmation_protocol_frozen=False,
                     draw_authorized=False, launch_authorized=False, cost_admission_receipt=None,
                     core_cells=360, extension_cells=45, accepted_primary_intervals=63, experiment_stop="2026-10-09",
                     gpu_seconds=0, sealed_payloads_opened=0)
    checked = verify(candidate)
    checked.update(task="R1-63h", external_dependencies=pending,
                   corrected_mquake_complete=sum(r["status"]=="complete" for r in profiles),
                   requests_are_unsigned_previews=True, final_cost_admission=False)
    candidate_ref = write_new(ROOT / f"manifests/revision_v1/freeze_candidate_{tag.replace('-', '_')}.json", candidate)
    checked["candidate"] = candidate_ref
    write_new(LOG / f"r1-63h-{tag}-verification.json", checked)
    return checked


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(preview=args.preview), indent=2))
