"""R1-63c: strictly verified dry freeze candidate v4, never a launch/freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.r1_d1i_register_v6 import REGISTER, verify_register
from scripts.r1_round14_admission_audit import ROOT, binding_errors, sha

from pccap.revision_v1.analysis import digest


def assemble():
    register = verify_register(json.loads(REGISTER.read_text()))
    bindings = dict(register["bindings_sha256"])
    memo = {}

    def bind(path, expected=None):
        path = Path(path)
        path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
        if "confirm" in path.parts or not path.is_relative_to(ROOT.parent):
            raise PermissionError("sealed or external candidate input refused")
        stat = path.stat()
        fingerprint = (str(path), stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if fingerprint not in memo:
            memo[fingerprint] = sha(path)
        observed = memo[fingerprint]
        if expected is not None and observed != expected:
            raise ValueError("bound file changed: " + str(path))
        if str(path) in bindings and bindings[str(path)] != observed:
            raise ValueError("conflicting binding: " + str(path))
        bindings[str(path)] = observed
        return {"path": str(path), "sha256": observed}

    def declared(obj):
        if isinstance(obj, dict):
            if isinstance(obj.get("path"), str) and isinstance(obj.get("sha256"), str):
                bind(obj["path"], obj["sha256"])
            for value in obj.values():
                declared(value)
        elif isinstance(obj, list):
            for value in obj:
                declared(value)

    matrix_path = ROOT / "manifests/revision_v1/run_matrix_draft_v4.json"
    matrix = json.loads(matrix_path.read_text())
    for name, h in matrix["sources_sha256"].items():
        bind(name, h)
    declared(matrix)
    primary_path = ROOT / "manifests/revision_v1/primary_condition_v5.json"
    primary = json.loads(primary_path.read_text())
    declared(primary)
    selection = bind(primary["selection"]["manifest"], primary["selection"]["sha256"])
    audit_path = ROOT / "logs/r1_round16/selection_audit.json"
    audit = json.loads(audit_path.read_text())
    if (
        not audit["weight_average"]["verified_bitwise"]
        or not audit["winner"]["admissible"]
        or audit["n_candidates"] != 42
        or audit["n_admissible"] != 15
    ):
        raise ValueError("selected-reader audit incomplete")
    if (
        audit["weight_average"]["weights"] != primary["weights"]
        or audit["winner"]["mean_ret_gs"] != primary["selection"]["winner_mean_ret_gs"]
    ):
        raise ValueError("selection review and primary differ")
    for path, h in audit["bindings_sha256"].items():
        bind(path, h)
    datasets_path = ROOT / "manifests/datasets.json"
    datasets = json.loads(datasets_path.read_text())
    for name, h in datasets["mquake"]["files"].items():
        bind(ROOT.parent / "assets" / name, h)
    protocol_path = ROOT / "docs/R1_stage4_protocol_draft_v4.md"
    notes = {
        "U02": "Development winner and R1-X12 review complete; boundary uncertainty, source populations and final reference conventions remain explicit.",
        "U03": "S1 source identities and construction recipes verified; final-reference training-budget and continued-base calibration/profile reconciliation pending.",
        "U08": "R1-73 MQuAKE calibration specification delivered, unexecuted; full-validation/tail and challenge cadence still needs owner binding.",
        "U11": "R1-68c CPU parity and instrumentation delivered; owner real-base re-profile and integration still required.",
        "U16": "R1-64b supplies16 comparator development recipes; condition/dataset cost ceilings remain unmeasured/unadmitted.",
        "U17": "This v4 dry candidate binds v5 selection and register v6; historical matrix v4 still needs a selected-primary successor.",
        "U18": "DEC-051/052 approve order/full scope and honest incomplete reporting; September20 remeasurement and actual capacity remain unresolved.",
    }
    gates = []
    for line in protocol_path.read_text().splitlines():
        match = re.match(r"\| (U\d\d) ([^|]+)\| ([^|]+)\|", line)
        if match:
            gates.append(
                {
                    "gate": match[1],
                    "title": match[2].strip(),
                    "protocol_status": match[3].strip(),
                    "current_evidence": notes.get(
                        match[1], "No new independent closure receipt in this lane."
                    ),
                    "admission": "open; independent owner closure receipt required",
                }
            )
    if [g["gate"] for g in gates] != [f"U{i:02d}" for i in range(1, 19)] or len(
        matrix["cells"]
    ) != 360:
        raise ValueError("complete matrix/gate inventory required")
    schedule_path = ROOT / "manifests/revision_v1/decisions_round16_schedule_snapshot.md"
    schedule_rows = {}
    for line in schedule_path.read_text().splitlines():
        match = re.match(r"\| (DEC-05[12]) \|", line)
        if match:
            schedule_rows[match[1]] = {
                "row": line,
                "sha256": hashlib.sha256(line.encode()).hexdigest(),
            }
    if set(schedule_rows) != {"DEC-051", "DEC-052"}:
        raise ValueError("schedule decision snapshot incomplete")
    source_files = {
        str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))
    }
    for name, h in source_files.items():
        bind(name, h)
    execution_names = (
        "requirements.lock",
        "docs/environment.md",
        "scripts/sysmon.sh",
        "scripts/process_memory_monitor.py",
        "scripts/pccap-monitor-retention.timer",
        "scripts/r1_68b_dev_cell.py",
        "scripts/r1_68b_integrity_runtime.py",
        "scripts/r1_68c_dev_cell.py",
        "scripts/r1_68c_batched_drift.py",
        "scripts/r1_68c_rebind_recipe.py",
        "scripts/r1_64b_comparator_recipes.py",
        "scripts/r1_73_mquake_calibration.py",
        "scripts/ht5_dev_cell.py",
        "scripts/ht5_probe_assays.py",
        "scripts/ht5_recipes.py",
        "scripts/ht5_panel.py",
    )
    for name in execution_names:
        bind(name)
    current_refs = {}
    for name in (
        "logs/review_r1_selection.md",
        "logs/r1_round16/selection_audit.json",
        "logs/r1_round16/selection_retention_rejection.pdf",
        "logs/r1_round16/schedule_options.json",
        "docs/tasks/R1-72-decision-addendum.md",
        "logs/r1_round16/comparator_recipe_inventory.json",
        "docs/tasks/R1-73-mquake-calibration.spec.json",
        "logs/heavy_tail/audit-v5-round16-supplement/audit.json",
        "logs/heavy_tail/audit-v5-round16-supplement/mean_vs_tail_v5.pdf",
        "docs/talk_claim_ledger_v2.md",
        "logs/r1_round16/talk_evidence_v2.json",
        "manifests/revision_v1/kappa_pilot_v2.json",
        "manifests/revision_v1/ht_development_panel_v1.json",
    ):
        current_refs[name] = bind(name)
    # Bind immutable measured source rows for the tail audit; logs/live notes are not evidence substitutes.
    tail = json.loads((ROOT / "logs/heavy_tail/audit-v5-round16-supplement/audit.json").read_text())
    declared(tail["source_inventory"])
    recipe_inventory = json.loads(
        (ROOT / "logs/r1_round16/comparator_recipe_inventory.json").read_text()
    )
    declared(recipe_inventory)
    for entry in recipe_inventory["recipes"]:
        recipe = json.loads(Path(entry["path"]).read_text())
        declared(recipe["construction"])
        declared(recipe["comparator_recipe"]["bindings"])
    for path in sorted((ROOT / "docs/tasks").glob("R1-68c-*.recipe.json")):
        declared(json.loads(path.read_text())["construction"])
        bind(path)
    register_ref = bind(REGISTER)
    primary_ref = bind(primary_path)
    protocol_ref = bind(protocol_path)
    matrix_ref = bind(matrix_path)
    dataset_ref = bind(datasets_path)
    decision_ref = bind(schedule_path)
    producer = bind(__file__)
    historical = bind(ROOT / "manifests/revision_v1/freeze_candidate_v3.json")
    # Rehash every unique bound file without the within-assembly memo.
    errors = binding_errors(bindings)
    if errors:
        raise ValueError("candidate inputs changed during assembly: " + json.dumps(errors))
    return {
        "schema_version": 4,
        "name": "freeze_candidate_v4",
        "task": "R1-63c",
        "status": "dry_candidate_not_frozen",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "producer": producer,
        "historical_candidate": historical,
        "register": register_ref,
        "primary_condition": primary_ref,
        "selection": selection,
        "selected_weights": primary["weights"],
        "selected_parameter_counts": audit["weight_average"]["parameter_counts"],
        "selection_review_status": "completed_with_qualifications; development rule satisfied, not population certification",
        "protocol": protocol_ref,
        "matrix": matrix_ref,
        "datasets": dataset_ref,
        "decisions_snapshot": register["decisions_snapshot"],
        "decisions_043_050": register["decision_rows"],
        "schedule_decisions_snapshot": decision_ref,
        "schedule_decisions": schedule_rows,
        "historical_matrix_note": "v4 binds its historical reader/register; retained as declared provenance. Final selected-v5 matrix successor required, not admitted by this candidate.",
        "historical_evidence_note": "Prior candidate and talk evidence inventory are immutable provenance. Live stage2 notes may advance after a ledger snapshot; the evidence ledger is not a recursively current binding to those notes.",
        "src_pccap_tree_sha256": digest(source_files),
        "src_pccap_files": source_files,
        "current_evidence": current_refs,
        "bindings_sha256": bindings,
        "remaining_gates": gates,
        "core_cells": 360,
        "extension_cells": 45,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "launch_authorized": False,
        "sealed_payloads_opened": 0,
        "gpu_seconds": 0,
    }


def validate(candidate):
    errors = binding_errors(candidate["bindings_sha256"])
    if errors:
        raise ValueError("candidate binding mismatch: " + json.dumps(errors))
    actual = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    if (
        actual != candidate["src_pccap_files"]
        or digest(actual) != candidate["src_pccap_tree_sha256"]
    ):
        raise ValueError("installed source tree changed")
    if any(
        candidate[k] is not False
        for k in ("confirmation_protocol_frozen", "draw_authorized", "launch_authorized")
    ):
        raise ValueError("dry candidate cannot authorize execution")
    if len(candidate["remaining_gates"]) != 18:
        raise ValueError("incomplete gate inventory")
    return {
        "binding_count": len(candidate["bindings_sha256"]),
        "tree_files": len(actual),
        "gates_open": 18,
        "draws": 0,
        "seals": 0,
        "gpu_seconds": 0,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--verify", type=Path)
    a = ap.parse_args()
    if bool(a.output) == bool(a.verify):
        ap.error("choose either --output or --verify")
    if a.verify:
        document = json.loads(a.verify.read_text())
    else:
        if a.output.exists() or not a.output.resolve().is_relative_to(
            ROOT / "manifests/revision_v1"
        ):
            ap.error("new candidate under manifests/revision_v1 required")
        document = assemble()
        with a.output.open("x") as f:
            json.dump(document, f, indent=2, sort_keys=True, allow_nan=False)
            f.write("\n")
    result = validate(document)
    for gate in document["remaining_gates"]:
        print(gate["gate"] + ": " + gate["current_evidence"] + " " + gate["admission"])
    print(json.dumps(result))


if __name__ == "__main__":
    main()
