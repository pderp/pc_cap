"""R1-63e: dry freeze candidate v6 binding protocol v5.1 and DEC-057/058/059."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts.r1_49g_inference import validate_family
from scripts.r1_d1i_register_v6 import REGISTER, verify_register

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assemble():
    parent_path = ROOT / "manifests/revision_v1/freeze_candidate_v5.json"
    parent = json.loads(parent_path.read_text())
    bindings = {}

    def bind(path, expected=None):
        p = (ROOT / Path(path)).resolve()
        if not p.is_relative_to(ROOT.parent) or "confirm" in p.parts:
            raise PermissionError("unsealed local metadata/resources only")
        value = sha(p)
        if expected is not None and value != expected:
            raise ValueError("binding changed: " + str(p))
        if str(p) in bindings and bindings[str(p)] != value:
            raise ValueError("input changed during assembly")
        bindings[str(p)] = value
        return {"path": str(p), "sha256": value}

    rebindings = []
    missing = []
    for name, expected in parent["bindings_sha256"].items():
        if not Path(name).is_file():
            missing.append({"path": name, "historical_sha256": expected})
            continue
        current = bind(name)
        if current["sha256"] != expected:
            rebindings.append(
                {
                    "path": name,
                    "historical_sha256": expected,
                    "current_sha256": current["sha256"],
                    "status": "recorded_for_owner_review_not_a_final_admission",
                }
            )
    register = verify_register(json.loads(REGISTER.read_text()))
    for name, h in register["bindings_sha256"].items():
        bind(name, h)
    matrix_path = ROOT / "manifests/revision_v1/run_matrix_v5_1.json"
    matrix = json.loads(matrix_path.read_text())
    validate_family(matrix)
    for name, h in matrix["sources_sha256"].items():
        bind(name, h)
    gates = copy.deepcopy(parent["gate_inventory"])
    for gate in gates:
        if gate["gate"] in ("U12", "U13", "U14"):
            decision = {"U12": "DEC-057", "U13": "DEC-058", "U14": "DEC-059"}[gate["gate"]]
            gate.update(
                status="open",
                decision_status="accepted_and_implemented",
                decision=decision,
                closure="Bind tested accepted analysis rules to final independent populations and joint admission; accepted decision is no longer pending.",
            )
        if gate["gate"] == "U11":
            gate["closure"] = (
                "Owner real-base R1-68e parity/profile, permitted idle-boundary driver hook, new recipes and explicit sealed donor reconciliation."
            )
        if gate["gate"] == "U16":
            gate["closure"] = (
                "Complete heterogeneous profiles/calibration and September20 cost/capacity admission; no invented ceilings."
            )
    sources = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    scripts = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "scripts").glob("*.py"))}
    for name, h in {**sources, **scripts}.items():
        bind(name, h)
    refs = {}
    for name in (
        "docs/R1_stage4_protocol_draft_v5_1.md",
        "docs/tasks/R1-49f-lead-bindings.md",
        "docs/tasks/R1-68e-driver.patch",
        "docs/tasks/R1-68e-driver-edit-request.md",
        "logs/r1_round20/r1-68e-final-tests.txt",
        "logs/r1_round20/r1-49g-second-tests.txt",
        "tests/revision_v1/test_r1_49g_analysis.py",
        "tests/revision_v1/test_r1_68e_driver_hook.py",
        "tests/revision_v1/test_r1_68e_batched_drift_v0.py",
        "logs/r1_round18/ht3d-pilot-final-aliases.json",
    ):
        refs[name] = bind(name)
    candidate = {
        "schema_version": 6,
        "name": "freeze_candidate_v6",
        "task": "R1-63e",
        "status": "dry_candidate_not_frozen",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "producer": bind(__file__),
        "historical_candidate": bind(parent_path),
        "matrix": bind(matrix_path),
        "protocol": bind("docs/R1_stage4_protocol_draft_v5_1.md"),
        "register": bind(REGISTER),
        "decisions": matrix["accepted_decisions"],
        "decision_snapshot_policy": "exact accepted rows and hashes; no mutable decisions-file binding",
        "primary_condition": bind("manifests/revision_v1/primary_condition_v5.json"),
        "installed_driver_code_sha256": driver.code_identity(),
        "src_pccap_files": sources,
        "src_pccap_tree_sha256": driver.digest(sources),
        "script_sources": scripts,
        "current_evidence": refs,
        "source_rebindings_since_parent": rebindings,
        "missing_historical_inputs": missing,
        "rebinding_policy": "Current files recorded for owner review; this dry inventory grants no approval of any difference from historical evidence.",
        "gate_inventory": gates,
        "remaining_gates": [g for g in gates if g["status"] == "open"],
        "core_cells": 360,
        "extension_cells": 45,
        "accepted_primary_intervals": 63,
        "r1_68e": {
            "cpu_complete": True,
            "driver_hook_applied": "def run_drift_assay("
            in (ROOT / "scripts/r1_68c_dev_cell.py").read_text(),
            "owner_real_base_admission": False,
            "post_hook_comparator_recipes_pending": True,
            "sealed_donor_reconciliation_pending": True,
        },
        "lead_items": {
            "Q4": "accepted_DEC054_pilot_only",
            "Q5": "accepted_DEC055_stress_only",
            "Q10": "accepted_DEC056_historical_diagnostic_only",
            "Q11": "accepted_DEC057",
            "Q12": "accepted_DEC058",
            "Q13": "accepted_DEC059",
        },
        "profile_evidence": {
            "remeasure_date": "2026-09-20",
            "experiment_stop": "2026-10-09",
            "heterogeneous_405_cell_cost_admitted": False,
        },
        "bindings_sha256": bindings,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "launch_authorized": False,
        "sealed_payloads_opened": 0,
        "gpu_seconds": 0,
    }
    validate(candidate)
    return candidate


def validate(candidate):
    for name, h in candidate["bindings_sha256"].items():
        if sha(name) != h:
            raise ValueError("candidate input changed: " + name)
    if driver.code_identity() != candidate["installed_driver_code_sha256"]:
        raise ValueError("installed driver changed")
    if any(
        candidate[k] is not False
        for k in ("confirmation_protocol_frozen", "draw_authorized", "launch_authorized")
    ):
        raise ValueError("dry candidate cannot authorize execution")
    if [g["gate"] for g in candidate["gate_inventory"]] != [f"U{i:02}" for i in range(1, 19)]:
        raise ValueError("complete gate inventory required")
    return {
        "bindings": len(candidate["bindings_sha256"]),
        "open_gates": len(candidate["remaining_gates"]),
        "frozen": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "manifests/revision_v1"):
        raise FileExistsError("new candidate manifest path required")
    value = assemble()
    with output.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {
                "bindings": len(value["bindings_sha256"]),
                "open_gates": len(value["remaining_gates"]),
                "frozen": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
