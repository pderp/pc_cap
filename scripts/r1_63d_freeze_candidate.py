"""Create freeze candidate v5 as a dry, hash-bound readiness inventory only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts.r1_d1i_register_v6 import REGISTER, verify_register

import pccap  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "results/R1/stage4_dev_cells/R1_learned_ff-zsre-development-source-6e8c802ca0ea802814f8/attempt-0000/result.json"
CLOSURES = {
    "U01": "Lead admits the exact core/extension comparisons and labels the historical v2 package contrast.",
    "U02": "Bind selected v5 and the full selection audit to final source populations, weights and reference conventions.",
    "U03": "Reconcile S1 training budgets with v5, verify continued-base calibration/fidelity, and obtain S1 comparator profiles.",
    "U04": "Complete final zsRE alias/context/teacher eligibility and exposure clearance through draw time.",
    "U05": "Provide final CounterFact source receipt under DEC-042; strict-source count remains zero.",
    "U06": "Verify final joint role allocation/RNG and MQuAKE usable capacity after all exclusions; preserve register v6 policy.",
    "U07": "After approval, materialize final role payloads and seals with complete independent expected IDs; none exist now.",
    "U08": "Bind challenge/full-validation cadence and inventories; execute and review R1-73 MQuAKE calibration.",
    "U09": "Audit alias matching, revision dependencies and endpoint observers; retain unavailable challenge rows explicitly.",
    "U10": "DEC-053 scoring is installed, CPU-tested and bound by the new R1-64c/R1-68d recipes; preserve both equality conventions and truncation counts.",
    "U11": "Complete full/incremental real-base parity and tolerance receipts; integrate a certified sealed R1-68d backend (current backend is development-only).",
    "U12": "Lead binds the multiplicity family/procedure across seven controls, three datasets and the separate extension.",
    "U13": "Lead admits the final classifier/fidelity inequalities and DEC-033 margins with DEC-053 locality semantics.",
    "U14": "Lead supplies numerical secondary thresholds and their interval/multiplicity roles; null values cannot pass.",
    "U15": "Bind final independent populations and test complete/missing/failed analysis against final sealed receipt conventions.",
    "U16": "Execute all 16 R1-64c profiles, R1-73 and applicable MQuAKE profiles; admit heterogeneous ceilings plus failures at the September 20 review.",
    "U17": "Bind final environment, driver, analysis, controls, calibrated recipes and closed gates; candidate v5 alone is not a freeze.",
    "U18": "September 20 cost/capacity decision admits a schedule ending October 9, with DEC-051 order and DEC-052 incomplete reporting.",
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assemble():
    parent_path = ROOT / "manifests/revision_v1/freeze_candidate_v4.json"
    parent = json.loads(parent_path.read_text())
    bindings = {}
    rebindings = []
    permitted = {
        str(ROOT / "src/pccap/revision_v1/stage4_assays.py"),
        str(ROOT / "scripts/r1_68c_dev_cell.py"),
    }
    for name, expected in parent["bindings_sha256"].items():
        observed = sha(name)
        if observed != expected:
            if name not in permitted:
                raise ValueError("unreviewed change to parent binding: " + name)
            rebindings.append(
                {"path": name, "historical_sha256": expected, "current_sha256": observed}
            )
        bindings[name] = observed

    def bind(path, expected=None):
        path = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
        if "confirm" in path.parts or not path.is_relative_to(ROOT.parent):
            raise PermissionError("only unsealed local candidate inputs")
        actual = sha(path)
        if expected is not None and expected != actual:
            raise ValueError("binding mismatch: " + str(path))
        if str(path) in bindings and bindings[str(path)] != actual:
            raise ValueError("input changed during assembly")
        bindings[str(path)] = actual
        return {"path": str(path), "sha256": actual}

    register = verify_register(json.loads(REGISTER.read_text()))
    for path, h in register["bindings_sha256"].items():
        bind(path, h)
    matrix_path = ROOT / "manifests/revision_v1/run_matrix_v5.json"
    matrix = json.loads(matrix_path.read_text())
    for path, h in matrix["sources_sha256"].items():
        bind(path, h)
    if len(matrix["cells"]) != 360 or len(matrix["extension"]["cells"]) != 45:
        raise ValueError("matrix cardinality changed")
    primary_path = ROOT / "manifests/revision_v1/primary_condition_v5.json"
    primary = json.loads(primary_path.read_text())
    bind(primary["weights"]["path"], primary["weights"]["sha256"])
    pilot_path = ROOT / "manifests/revision_v1/kappa_pilot_v3.json"
    pilot = json.loads(pilot_path.read_text())
    for path, h in pilot["training"]["sources_sha256"].items():
        bind(path, h)
    protocol_path = ROOT / "docs/R1_stage4_protocol_draft_v5.md"
    gates = []
    for line in protocol_path.read_text().splitlines():
        match = re.match(r"\| (U\d\d) ([^|]+)\| ([^|]+)\|", line)
        if match:
            g = match[1]
            gates.append(
                {
                    "gate": g,
                    "title": match[2].strip(),
                    "historical_protocol_status": match[3].strip(),
                    "status": "implementation_resolved" if g == "U10" else "open",
                    "closure": CLOSURES[g],
                }
            )
    if [g["gate"] for g in gates] != list(CLOSURES):
        raise ValueError("all eighteen gate rows required")
    decision_text = (ROOT / "docs/decisions.md").read_text()
    decisions = {}
    for line in decision_text.splitlines():
        match = re.match(r"\| (DEC-05[1-4]) \|", line)
        if match:
            decisions[match[1]] = {"row": line, "sha256": hashlib.sha256(line.encode()).hexdigest()}
    if len(decisions) != 4:
        raise ValueError("DEC-051 through DEC-054 required")
    sources = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    for name, h in sources.items():
        bind(name, h)
    refs = {}
    for name in (
        "docs/tasks/R1-74-R1-75-approved-landing.md",
        "logs/r1_round17/scoring_landing_20260916/completion.json",
        "logs/r1_round18/ht3d-pilot-partial-v1.json",
        "logs/r1_round18/r1-64c-inspection-runlist.json",
        "logs/r1_round18/r1-77-final-draft-inventory.json",
        "logs/r1_round18/r1-77-development-inventory.json",
        "scripts/r1_64c_comparator_recipes.py",
        "scripts/r1_77_queue.py",
        "scripts/ht3d_pilot_aggregate.py",
        "scripts/r1_75_analysis_stage4_v1.py",
        "docs/tasks/R1-73-mquake-calibration.spec.json",
        "docs/tasks/R1-76-mquake-occupancy.md",
        "docs/tasks/R1-76.md",
        PROFILE,
    ):
        refs[name] = bind(name)
    recipes = []
    for path in sorted((ROOT / "docs/tasks").glob("R1-64c-*.recipe.json")):
        m = json.loads(path.read_text())
        if m["code_sha256"] != driver.code_identity():
            raise ValueError("comparator recipe not on installed tree")
        recipes.append(bind(path))
    if len(recipes) != 16:
        raise ValueError("sixteen rebound comparator recipes required")
    code = driver.code_identity()
    out = {
        "schema_version": 5,
        "name": "freeze_candidate_v5",
        "task": "R1-63d",
        "status": "dry_candidate_not_frozen",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "producer": bind(__file__),
        "historical_candidate": bind(parent_path),
        "source_rebindings": rebindings,
        "rebinding_authority": "R1-68d reviewed driver repair and lead-approved DEC-053 scoring landing; other parent bindings must still verify.",
        "register": bind(REGISTER),
        "matrix": bind(matrix_path),
        "protocol": bind(protocol_path),
        "primary_condition": bind(primary_path),
        "kappa_pilot": bind(pilot_path),
        "selected_weights": primary["weights"],
        "installed_driver_code_sha256": code,
        "src_pccap_files": sources,
        "src_pccap_tree_sha256": driver.digest(sources),
        "decisions": decisions,
        "decision_snapshot_policy": "Exact decision rows embedded, hashed individually; live decisions file is not a long-term mutable binding.",
        "current_evidence": refs,
        "comparator_recipes": recipes,
        "remaining_gates": [g for g in gates if g["status"] == "open"],
        "gate_inventory": gates,
        "lead_items": {
            "Q4": {
                "status": "approved_DEC054",
                "closure": "Pilot launched; DEC-054 supersedes stale Q4-open wording in matrix/protocol v5.",
            },
            "Q5": {
                "status": "open",
                "closure": "Lead approves scope and separate budget for stress panel; no stress launch here.",
            },
            "Q10": {
                "status": "open",
                "closure": "Lead selects MQuAKE occupancy policy; 700 historically primary-exposed eligible rows cannot supply 1000+100, and 168 nominal fresh subjects are not certified spare capacity.",
            },
        },
        "profile_evidence": {
            "measured_300_edit_zsre_seconds": json.loads((ROOT / PROFILE).read_text())[
                "attempt_wall_seconds"
            ],
            "full_profile": "pending owner chain",
            "heterogeneous_405_cell_cost_admitted": False,
            "remeasure_date": "2026-09-20",
            "experiment_stop": "2026-10-09",
        },
        "historical_reference_policy": "Parent evidence remains historical provenance. Current matrix/protocol/driver/primary/register/pilot bindings are the named v5/v6/v3 fields, not superseded parent references.",
        "confirmation_backend": "R1-77 queue tested for development; R1-68d has no sealed execution entry point. A certified additive backend and final recipe binding are an explicit U11/U17 prerequisite.",
        "bindings_sha256": bindings,
        "core_cells": 360,
        "extension_cells": 45,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "launch_authorized": False,
        "sealed_payloads_opened": 0,
        "gpu_seconds": 0,
    }
    validate(out)
    return out


def validate(candidate):
    for p, h in candidate["bindings_sha256"].items():
        if sha(p) != h:
            raise ValueError("candidate binding changed: " + p)
    actual = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    if (
        actual != candidate["src_pccap_files"]
        or driver.digest(actual) != candidate["src_pccap_tree_sha256"]
    ):
        raise ValueError("source tree mismatch")
    if driver.code_identity() != candidate["installed_driver_code_sha256"]:
        raise ValueError("driver changed")
    if any(
        candidate[k] is not False
        for k in ("confirmation_protocol_frozen", "draw_authorized", "launch_authorized")
    ):
        raise ValueError("dry candidate cannot grant authorization")
    if [g["gate"] for g in candidate["gate_inventory"]] != list(CLOSURES):
        raise ValueError("gate inventory incomplete")
    return {
        "bindings": len(candidate["bindings_sha256"]),
        "source_files": len(actual),
        "open_gates": len(candidate["remaining_gates"]),
        "readiness": False,
        "draw_authorized": False,
        "launch_authorized": False,
    }


def markdown(c):
    rows = [
        "# R1-63d freeze candidate v5 — dry",
        "",
        "No draw, seal, freeze or launch is authorized by this candidate.",
        f"Installed driver identity: `{c['installed_driver_code_sha256']}`.",
        "Matrix v5: 360 core + 45 extension cells. Experiments stop October 9.",
        "",
        "| Gate | Status | What closes it |",
        "|---|---|---|",
    ]
    rows += [
        f"| {g['gate']} {g['title']} | {g['status']} | {g['closure']} |"
        for g in c["gate_inventory"]
    ]
    rows += ["", "## Lead items", ""]
    rows += [f"- {key}: {v['status']}. {v['closure']}" for key, v in c["lead_items"].items()]
    rows += [
        "",
        "## Cost and implementation qualifications",
        "",
        f"Measured zsRE incremental profile: {c['profile_evidence']['measured_300_edit_zsre_seconds']:.3f} s at 300 edits.",
        "This measurement does not admit the 405-cell heterogeneous matrix. The 16 comparator profiles, MQuAKE calibration and September 20 cost review remain necessary.",
        c["confirmation_backend"],
        "",
        "U10's implementation is resolved by the approved scoring landing and recipe rebinding. Final population/admission gates remain open.",
        "Protocol/matrix v5 still contain historical Q4-open wording; the embedded DEC-054 row is authoritative for this candidate.",
        "All prior non-repaired file bindings and current source bindings were rehashed. The companion JSON records every path/hash and the two approved source rebindings.",
        "",
    ]
    return "\n".join(rows) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output", type=Path, default=ROOT / "manifests/revision_v1/freeze_candidate_v5.json"
    )
    p.add_argument(
        "--report", type=Path, default=ROOT / "logs/r1_round18/freeze_candidate_v5_gates.md"
    )
    args = p.parse_args(argv)
    paths = [args.output.resolve(), args.report.resolve()]
    if (
        any(x.exists() for x in paths)
        or not paths[0].is_relative_to(ROOT / "manifests/revision_v1")
        or not paths[1].is_relative_to(ROOT / "logs/r1_round18")
    ):
        p.error("new candidate/report files in their designated directories required")
    c = assemble()
    for path, text in zip(paths, [json.dumps(c, indent=2) + "\n", markdown(c)], strict=True):
        with path.open("x") as f:
            f.write(text)
    print(json.dumps(validate(c), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
