"""Version the unsigned package after cost/assembler evidence; never close absent gates."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT, write_new


def build(cost_path, templates_path):
    log = ROOT / "logs/r1_round29"
    parent = ROOT / "manifests/revision_v1/freeze_candidate_v12.json"
    candidate = copy.deepcopy(d9.read_metadata(d9.ref(parent)))
    snapshots = json.loads((log / "source_snapshot/bindings.json").read_text())
    for path, expected in list(candidate["bindings_sha256"].items()):
        if d9.sha(path) != expected:
            if path not in snapshots or snapshots[path]["sha256"] != expected:
                raise ValueError("unexpected concurrent source change: " + path)
            candidate["bindings_sha256"][snapshots[path]["path"]] = expected
            candidate["bindings_sha256"][path] = d9.sha(path)

    def bind(b):
        if d9.sha(b["path"]) != b["sha256"]:
            raise ValueError("binding changed: " + b["path"])
        candidate["bindings_sha256"][b["path"]] = b["sha256"]
        return b

    cost_ref = bind(d9.ref(cost_path))
    cost = d9.read_metadata(cost_ref)
    for b in cost["bindings"].values():
        bind(b)
    for cell in cost["cells"]:
        bind(cell["measurement"])
        for b in d9.read_metadata(cell["measurement"])["source_bindings"]:
            bind(b)
    host = d9.read_metadata(cost["host_peak_evidence"])
    for b in host["driver_entry_points"].values():
        bind(b)
    templates_ref = bind(d9.ref(templates_path))
    for b in d9.read_metadata(templates_ref).values():
        bind(b)
        bind(d9.read_metadata(b)["source_recipe"])
    for name in (
        "r1_63j_production_bundle",
        "r1_63j_candidate",
        "r1_58i_host_peaks",
        "r1_58j_cost_receipt",
        "r1_58j_validation_inventory",
        "r1_x18_review",
    ):
        bind(d9.ref(ROOT / f"scripts/{name}.py"))
    spec = d9.read_metadata(candidate["d9_inputs"])
    spec.update(
        task="R1-63j/R1-58j",
        status="unsigned_cost_v3_and_assembler_evidence_pending",
        cost_admission_source_unsigned=cost_ref,
        production_bundle_producer=bind(d9.ref(ROOT / "scripts/r1_63j_production_bundle.py")),
        runtime_templates=templates_ref,
    )
    spec["d9"]["clearance"]["configuration_bindings"].update(
        cost_admission_source_unsigned=cost_ref
    )
    forms = {}
    for key, b in spec["receipts"].items():
        if not b.get("path") or key.endswith("_authorization"):
            continue
        value = d9.read_metadata(b)
        if value.get("lead_approved") is not False:
            raise PermissionError("cannot rebind a signed receipt")
        value.update(candidate_name="v13")
        forms[key] = bind(
            write_new(ROOT / f"docs/tasks/R1-D9-{key.replace('_', '-')}-template-v8.json", value)
        )
    spec["receipts"].update(forms)
    for stage in ("clearance", "draw", "seal"):
        key = stage + "_authorization"
        value = d9.read_metadata(spec["receipts"][key])
        if value.get("lead_approved") is not False:
            raise PermissionError("cannot rebind signed authorization")
        value.update(
            candidate_name="v13",
            request_sha256=None,
            inspection_only_request_sha256=d9.contract(spec, stage),
        )
        forms[key] = bind(
            write_new(ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-v8.json", value)
        )
        spec["receipts"][key] = forms[key]
    spec_ref = bind(write_new(ROOT / "docs/tasks/R1-D9-inputs-v8.json", spec))
    profiles = []
    for row in json.loads((ROOT / "docs/tasks/R1-64f/inspection-receipts.json").read_text()):
        found = []
        for p in sorted(Path(row["expected_result_directory"]).glob("attempt-*/result.json")):
            result = json.loads(p.read_text())
            if result["manifest_sha256"] != row["recipe"]["sha256"]:
                raise ValueError("R1-64f result identity differs")
            if result.get("status") == "complete" and result.get("completed_checkpoint") == 300:
                found.append(bind(d9.ref(p)))
        if len(found) > 1:
            raise ValueError("multiple successful attempts require reconciliation")
        profiles.append(
            dict(
                cell=row["cell"],
                recipe=row["recipe"],
                results=found,
                status="complete" if found else "pending",
            )
        )
    blockers = list(cost["pending_evidence"])
    blockers += [
        "R1-64f pending: " + p["cell"]["dataset"] + ":" + p["cell"]["condition"]
        for p in profiles
        if p["status"] != "complete"
    ]
    blockers += [
        "actual authorized draw/endpoints/seal and final scientific gate evidence required",
        "assemble actual admitted production bundle after those prerequisites; only synthetic rehearsal exists",
    ]
    for gate in candidate["gate_inventory"]:
        if gate["gate"] == "U16":
            gate["closure"] = (
                "Typed cost revision3 binds direct/monitor/extrapolated host evidence and completed full-endpoint profiles; full-validation/remaining measurements or reviewed transfers and admission remain."
            )
        if gate["gate"] == "U17":
            gate["closure"] = (
                "Whole bundle assembler delivered/tested; actual admitted receipt set, scientific gates, complete costs and exact signed publication still required."
            )
    candidate.update(
        schema_version=13,
        name="freeze_candidate_v13",
        task="R1-63j/R1-58j",
        producer=bind(d9.ref(__file__)),
        historical_candidate=bind(d9.ref(parent)),
        d9_inputs=spec_ref,
        d9_templates=forms,
        operator=bind(d9.ref(ROOT / "scripts/r1_58g_operator.py")),
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        cost_admission_source_unsigned=cost_ref,
        cost_admission_receipt=None,
        production_bundle_producer=spec["production_bundle_producer"],
        runtime_templates=templates_ref,
        production_bundle_interface=bind(
            d9.ref(ROOT / "docs/tasks/R1-63j-production-interface.md")
        ),
        full_endpoint_profiles=profiles,
        non_signature_blockers=blockers,
        signatures_only=False,
        status="unsigned_assembler_delivered_host_evidence_bound_cost_and_scientific_gates_pending",
    )
    candidate["remaining_gates"] = [g for g in candidate["gate_inventory"] if g["status"] == "open"]
    proof = verify(candidate)
    b = write_new(ROOT / "manifests/revision_v1/freeze_candidate_v13.json", candidate)
    proof.update(
        candidate=b,
        inputs=spec_ref,
        signatures_only=False,
        non_signature_blockers=blockers,
        full_endpoint_results_complete=sum(p["status"] == "complete" for p in profiles),
    )
    write_new(log / "r1-63j-verification.json", proof)
    return proof


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cost", type=Path, required=True)
    ap.add_argument("--templates", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(build(args.cost, args.templates), indent=2))
