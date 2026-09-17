"""R1-D1i: decisions-snapshot rebinding, strict dry plan and freeze candidate.

Only new files are created. Candidate membership/policy remain exactly v5's.
A candidate is not a freeze, draw approval, seal, or execution authorization.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.r1_58_draw_streams import capacity
from scripts.r1_round14_admission_audit import ROOT, binding_errors, sha, source_rows

from pccap.revision_v1.analysis import digest

LIVE = ROOT / "docs/decisions.md"
REGISTER = ROOT / "manifests/revision_v1/exclusions_frozen_v6.json"
SNAPSHOT = ROOT / "manifests/revision_v1/decisions_snapshot_v6.md"
PARENT = ROOT / "manifests/revision_v1/exclusions_frozen_v5.json"


def decision_rows(text):
    rows = {}
    for line in text.splitlines():
        match = re.match(r"\| (DEC-\d{3})(?= |\|)", line)
        if match and 43 <= int(match[1][-3:]) <= 50:
            if match[1] in rows:
                raise ValueError("duplicate decision row")
            rows[match[1]] = {"row": line, "sha256": hashlib.sha256(line.encode()).hexdigest()}
    if set(rows) != {f"DEC-{n:03d}" for n in range(43, 51)}:
        raise ValueError("DEC-043 through DEC-050 required")
    return rows


def rebind(parent, parent_ref, snapshot_ref, snapshot_bytes, *, live_path, producer_ref):
    """Pure transformation; only identity/binding metadata changes."""
    if parent["schema_version"] != 5:
        raise ValueError("v5 parent required")
    if hashlib.sha256(snapshot_bytes).hexdigest() != snapshot_ref["sha256"]:
        raise ValueError("snapshot bytes mismatch")
    rows = decision_rows(snapshot_bytes.decode())
    if rows["DEC-048"]["row"] != parent["acceptance"]["decision_row"]:
        raise ValueError("DEC-048 policy changed; rebinding cannot change policy")
    out = copy.deepcopy(parent)
    old = out["bindings_sha256"].pop(str(live_path))
    out["bindings_sha256"].update(
        {
            snapshot_ref["path"]: snapshot_ref["sha256"],
            parent_ref["path"]: parent_ref["sha256"],
            producer_ref["path"]: producer_ref["sha256"],
        }
    )
    out.update(
        schema_version=6,
        name="exclusions_frozen_v6",
        task="R1-D1i",
        status="v5 membership and policy unchanged; decisions snapshot bound; clearance pending",
        decisions_snapshot=snapshot_ref,
        decision_rows=rows,
        rebinding={
            "parent_v5": parent_ref,
            "historical_live_decisions_path": str(live_path),
            "historical_live_decisions_sha256": old,
            "rule": "Only the live decisions binding is replaced by this immutable snapshot. The original v5 file is historical provenance; its superseded live-file binding is not a current requirement.",
            "producer": producer_ref,
        },
    )
    unchanged = set(parent) - {"schema_version", "name", "task", "status", "bindings_sha256"}
    if any(out[k] != parent[k] for k in unchanged):
        raise ValueError("scientific register content changed")
    return out


def create_register():
    snapshot_bytes = LIVE.read_bytes()
    parent = json.loads(PARENT.read_text())
    errors = binding_errors({p: h for p, h in parent["bindings_sha256"].items() if p != str(LIVE)})
    if errors:
        raise ValueError("non-decision parent binding mismatch: " + json.dumps(errors))
    source = {"path": str(Path(__file__).resolve()), "sha256": sha(__file__)}
    out = rebind(
        parent,
        {"path": str(PARENT), "sha256": sha(PARENT)},
        {"path": str(SNAPSHOT), "sha256": hashlib.sha256(snapshot_bytes).hexdigest()},
        snapshot_bytes,
        live_path=LIVE,
        producer_ref=source,
    )
    if REGISTER.exists() or SNAPSHOT.exists():
        raise FileExistsError("v6 outputs already exist; never overwrite")
    with SNAPSHOT.open("xb") as f:
        f.write(snapshot_bytes)
    write_new(REGISTER, out)
    verify_register(out)
    return out


def verify_register(register):
    errors = binding_errors(register["bindings_sha256"])
    if errors:
        raise ValueError("register binding mismatch: " + json.dumps(errors))
    historical = register["rebinding"]["parent_v5"]
    parent = json.loads(Path(historical["path"]).read_text())
    expected = rebind(
        parent,
        historical,
        register["decisions_snapshot"],
        Path(register["decisions_snapshot"]["path"]).read_bytes(),
        live_path=register["rebinding"]["historical_live_decisions_path"],
        producer_ref=register["rebinding"]["producer"],
    )
    if register != expected:
        raise ValueError("v6 differs from approved metadata-only transformation")
    return register


def draw_plan(register):
    verify_register(register)
    rows, item_strata = source_rows(register)
    allocation = capacity(rows)
    datasets = {}
    for ds, inventory in rows.items():
        n = len(inventory)
        datasets[ds] = {
            **register["counts"][ds],
            "candidate_item_strata": item_strata[ds],
            "representative_subject_strata": dict(
                sorted(Counter(r["_stratum"] for r in inventory).items())
            ),
            "pending_clearance": [
                {"step": s, "maximum_subjects_removed": n, "certified_removals": None}
                for s in (
                    "alias/entity equivalence including cross-dataset collisions",
                    "context and cumulative exposure through draw time",
                    "final-base E.2 teacher and token/context eligibility",
                    "disjoint roles and compatible near-miss/revision cases",
                    "composition dependency closure",
                )
            ],
            "joint_removal_upper_bound": n,
            "bound_note": "Individual trivial upper bounds overlap; do not sum them. No nonzero guaranteed usable count is certified.",
        }
    return {
        "task": "R1-D1i",
        "mode": "strict_count_only_no_draw",
        "register": {"path": str(REGISTER), "sha256": sha(REGISTER)},
        "bindings_verified": len(register["bindings_sha256"]),
        "binding_errors": [],
        "datasets": datasets,
        "allocation": allocation,
        "admitted": False,
        "draw_authorized": False,
        "abort_before_draw": True,
        "abort_reasons": ["final joint clearance absent"],
        "demand_note": "3 x (1000 edits +100 outside +100 near supports +100 near neighbours +50 revision) =4050 distinct subjects per dataset.",
        "representative_policy": "First v6 candidate in bound-register order per subject; count-only prospective stratum convention, not an admitted draw.",
        "rng_used": False,
        "candidate_ids_emitted": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "gpu_seconds": 0,
    }


def freeze_candidate(register):
    verify_register(register)
    bindings = dict(register["bindings_sha256"])

    def bind(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        if "confirm" in path.parts or not path.is_relative_to(ROOT.parent):
            raise PermissionError("sealed or external candidate input refused")
        observed = sha(path)
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
    datasets_path = ROOT / "manifests/datasets.json"
    datasets = json.loads(datasets_path.read_text())
    for name, h in datasets["mquake"]["files"].items():
        bind(ROOT.parent / "assets" / name, h)
    protocol_path = ROOT / "docs/R1_stage4_protocol_draft_v4.md"
    gates = []
    for line in protocol_path.read_text().splitlines():
        match = re.match(r"\| (U\d\d) ([^|]+)\| ([^|]+)\|", line)
        if match:
            gates.append(
                {
                    "gate": match[1],
                    "title": match[2].strip(),
                    "protocol_status": match[3].strip(),
                    "admission": "open; independent closure receipt required",
                }
            )
    if [g["gate"] for g in gates] != [f"U{i:02d}" for i in range(1, 19)] or len(
        matrix["cells"]
    ) != 360:
        raise ValueError("complete matrix/gate inventory required")
    source_files = {
        str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))
    }
    for name, h in source_files.items():
        bind(name, h)
    for name in (
        "requirements.lock",
        "docs/environment.md",
        "scripts/sysmon.sh",
        "scripts/process_memory_monitor.py",
        "scripts/pccap-monitor-retention.timer",
        "scripts/r1_68b_dev_cell.py",
        "scripts/r1_68b_integrity_runtime.py",
        "scripts/ht5_dev_cell.py",
        "scripts/ht5_probe_assays.py",
        "scripts/ht5_recipes.py",
        "scripts/ht5_panel.py",
    ):
        bind(name)
    register_ref = bind(REGISTER)
    protocol_ref = bind(protocol_path)
    matrix_ref = bind(matrix_path)
    dataset_ref = bind(datasets_path)
    errors = binding_errors(bindings)
    if errors:
        raise ValueError("candidate inputs changed during assembly: " + json.dumps(errors))
    return {
        "schema_version": 3,
        "name": "freeze_candidate_v3",
        "task": "R1-D1i",
        "status": "dry_candidate_not_frozen",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "register": register_ref,
        "protocol": protocol_ref,
        "matrix": matrix_ref,
        "datasets": dataset_ref,
        "decisions_snapshot": register["decisions_snapshot"],
        "decisions_043_050": register["decision_rows"],
        "primary_condition": {
            "expected_version": 5,
            "path": None,
            "sha256": None,
            "status": "open pending selected-primary manifest",
        },
        "historical_matrix_note": "v4's embedded historical reader/register remain historical; a final selected-primary matrix successor is required.",
        "src_pccap_tree_sha256": digest(source_files),
        "src_pccap_files": source_files,
        "bindings_sha256": bindings,
        "remaining_gates": gates,
        "core_cells": 360,
        "extension_cells": 45,
        "monitoring_note": "sysmon plus per-process memory monitoring; hourly48h closed-file retention. Operational aids, not scientific gate closures.",
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "launch_authorized": False,
        "sealed_payloads_opened": 0,
        "gpu_seconds": 0,
    }


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--create-register", action="store_true")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()
    if not args.create_register and not args.audit:
        ap.error("choose --create-register and/or --audit")
    register = (
        create_register()
        if args.create_register
        else verify_register(json.loads(REGISTER.read_text()))
    )
    if args.audit:
        directory = ROOT / "logs/r1_round15"
        directory.mkdir(parents=True, exist_ok=True)
        draw = draw_plan(register)
        candidate = freeze_candidate(register)
        write_new(directory / "draw_plan_v6.json", draw)
        write_new(ROOT / "manifests/revision_v1/freeze_candidate_v3.json", candidate)
        for g in candidate["remaining_gates"]:
            print(g["gate"] + ": " + g["protocol_status"])
        print("MQuAKE nominal slack:", draw["datasets"]["mquake"]["headroom_subjects"])
    print("v6 policy/membership verified; no draw or freeze")


if __name__ == "__main__":
    main()
