"""Round 14: count-only v5 diagnostics and strict freeze-candidate admission.

No RNG, candidate identities, payloads, seals or models are produced. A hash
mismatch permits a labelled diagnostic report, never an admitted candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.r1_58_draw_streams import capacity, stratum
from scripts.r1_d1f_freeze_register import digest

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def checked_path(name):
    path = Path(name)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if "confirm" in path.parts or not path.is_relative_to(ROOT.parent):
        raise PermissionError("out-of-workspace or sealed resource refused")
    return path


def binding_errors(bindings):
    errors = []
    for name, expected in sorted(bindings.items()):
        path = checked_path(name)
        actual = sha(path) if path.is_file() else None
        if actual != expected:
            errors.append({"path": str(path), "expected": expected, "observed": actual})
    return errors


def source_rows(register):
    wrapper = json.loads((ROOT / "manifests/revision_v1/exclusions_frozen_v3.json").read_text())
    sources = {
        "zsre": wrapper["zsre"]["historical_review_resources"]["clear_candidates"]["path"],
        "counterfact": wrapper["counterfact"]["conditional_old_remainder"]["path"],
        "mquake": str(ROOT.parent / "assets/data/prepared/revision_v1/r1_d4_v1/items.jsonl"),
    }
    result, item_strata = {}, {}
    all_subjects = set()
    for ds, name in sources.items():
        path = checked_path(name)
        expected = register["bindings_sha256"][str(path)]
        if sha(path) != expected:
            raise ValueError("candidate resource mismatch: " + str(path))
        metadata = {r["item_id"]: r for r in register["candidates"][ds]}
        matched = {}
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                key = row["item_id"]
                if key not in metadata:
                    continue
                meta = metadata[key]
                if key in matched or digest(row) != meta["payload_sha256"]:
                    raise ValueError("duplicate or mismatched prepared candidate")
                if row.get("source_record_sha256") != meta["source_record_sha256"]:
                    raise ValueError("source record mismatch")
                matched[key] = {
                    "_stratum": stratum(row),
                    "_canonical_subject": meta["canonical_subject"],
                }
        if set(matched) != set(metadata):
            raise ValueError("incomplete candidate source coverage")
        # Prospective count convention only: first row in the bound register per subject.
        # This does not select a future realization or authorize that draw convention.
        seen, representatives = set(), []
        for meta in register["candidates"][ds]:
            key = meta["canonical_subject"]
            if key in all_subjects:
                raise ValueError("cross-dataset subject collision")
            if key not in seen:
                seen.add(key)
                representatives.append(matched[meta["item_id"]])
        all_subjects.update(seen)
        result[ds] = representatives
        item_strata[ds] = dict(sorted(Counter(r["_stratum"] for r in matched.values()).items()))
        if len(seen) != register["counts"][ds]["candidate_subjects"]:
            raise ValueError("registered subject count differs")
    return result, item_strata


def draw_diagnostic():
    path = ROOT / "manifests/revision_v1/exclusions_frozen_v5.json"
    register = json.loads(path.read_text())
    errors = binding_errors(register["bindings_sha256"])
    rows, item_strata = source_rows(register)
    counts = capacity(rows)
    remaining = {}
    for ds, inventory in rows.items():
        n = len(inventory)
        remaining[ds] = {
            "candidate_subjects": n,
            "candidate_items": len(register["candidates"][ds]),
            "candidate_item_strata": item_strata[ds],
            "representative_subject_strata": dict(
                sorted(Counter(r["_stratum"] for r in inventory).items())
            ),
            "demand": 4050,
            "headroom": n - 4050,
            "first_subject_losses_causing_shortfall": max(0, n - 4049),
            "guaranteed_cleared_subjects": 0,
            "remaining_clearance": [
                {"step": step, "maximum_subjects_removed": n, "certified_losses": None}
                for step in (
                    "canonical alias/entity resolution and cross-dataset alias collisions",
                    "context mentions and cumulative exposure reconciliation through draw time",
                    "teacher E.2 and tokenizer/context-length eligibility against final base",
                    "disjoint role assignment, semantic near-miss pairs and revision feasibility",
                    "composition dependency closure compatible with reserved edit subjects",
                )
            ],
            "joint_removal_upper_bound": n,
            "bounds_note": "Each stage may remove all candidates; bounds overlap and must not be added. MQuAKE already has historical teacher receipts, not final joint clearance.",
        }
    return {
        "task": "R1-58b",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "diagnostic_only_no_draw",
        "register": {"path": str(path), "sha256": sha(path)},
        "binding_errors": errors,
        "bindings_checked": len(register["bindings_sha256"]),
        "admitted": False,
        "abort": True,
        "abort_reasons": ["final joint clearance absent"]
        + (["bound input changed"] if errors else []),
        "datasets": remaining,
        "allocation": counts,
        "near_miss_accounting": "100 supports PLUS 100 neighbour facts per realization: 1350 x 3 = 4050. The ongoing.md shorthand omits the second reserve.",
        "subject_count_convention": "first candidate in bound-register order per canonical subject, for prospective strata counts only; no candidate IDs emitted",
        "draws": 0,
        "seals": 0,
        "gpu_seconds": 0,
        "rng_used": False,
    }


def freeze_diagnostic():
    names = [
        "manifests/revision_v1/exclusions_frozen_v5.json",
        "manifests/revision_v1/run_matrix_draft_v4.json",
        "docs/R1_stage4_protocol_draft_v4.md",
        "docs/decisions.md",
        "manifests/datasets.json",
        "requirements.lock",
        "docs/environment.md",
        "scripts/sysmon.sh",
        "scripts/process_memory_monitor.py",
        "scripts/pccap-process-memory.service",
        "scripts/pccap-monitor-retention.timer",
        "scripts/r1_68b_dev_cell.py",
        "scripts/r1_68b_integrity_runtime.py",
        "scripts/r1_round14_admission_audit.py",
    ]
    refs = {name: sha(ROOT / name) for name in names}
    register = json.loads((ROOT / names[0]).read_text())
    matrix = json.loads((ROOT / names[1]).read_text())
    errors = binding_errors(register["bindings_sha256"])
    errors.extend(binding_errors(matrix["sources_sha256"]))
    declared = {}

    def visit(value):
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                declared[value["path"]] = value["sha256"]
            for v in value.values():
                visit(v)
        elif isinstance(value, list):
            for v in value:
                visit(v)

    visit(matrix)
    errors.extend(binding_errors(declared))
    dataset_manifest = json.loads((ROOT / "manifests/datasets.json").read_text())
    errors.extend(
        binding_errors(
            {
                str(ROOT.parent / "assets" / p): h
                for p, h in dataset_manifest["mquake"]["files"].items()
            }
        )
    )
    protocol = (ROOT / names[2]).read_text()
    gates = []
    for line in protocol.splitlines():
        match = re.match(r"\| (U\d\d) ([^|]+)\| ([^|]+)\|", line)
        if match:
            gate, title, status = match.groups()
            gates.append(
                {
                    "gate": gate,
                    "title": title.strip(),
                    "protocol_status": status.strip(),
                    "admission": "open; independent closure receipt required",
                }
            )
    if [g["gate"] for g in gates] != [f"U{i:02d}" for i in range(1, 19)]:
        raise ValueError("complete U01-U18 inventory required")
    decisions = []
    for line in (ROOT / "docs/decisions.md").read_text().splitlines():
        if re.match(r"\| DEC-04[3-8](?: |\b)", line):
            decisions.append({"row": line, "sha256": hashlib.sha256(line.encode()).hexdigest()})
    if len(decisions) != 6 or len(matrix["cells"]) != 360:
        raise ValueError("six decision rows and 360 core cells required")
    tree = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "src/pccap").rglob("*.py"))}
    errors.extend(binding_errors({**refs, **tree}))
    return {
        "task": "R1-63b",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "refused_hash_mismatch" if errors else "dry_candidate_only",
        "admitted": False,
        "freeze_written": False,
        "draw_authorized": False,
        "bindings_sha256": refs,
        "binding_errors": errors,
        "decisions_043_048": decisions,
        "src_pccap_files": tree,
        "src_pccap_tree_sha256": digest(tree),
        "primary_condition": {
            "expected_version": 5,
            "path": None,
            "sha256": None,
            "status": "open pending common-population selection",
        },
        "matrix": {
            "core_cells": 360,
            "extension_cells": 45,
            "status": "v4 binds historical v4 reader/register; owner must issue final selected-reference matrix",
        },
        "operational_note": "sysmon and per-process memory services active at host verification; hourly 48-hour closed-file retention. This is not a scientific admission gate closure.",
        "gates": gates,
        "gpu_seconds": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    directory = args.output_dir.resolve()
    if not directory.is_relative_to(ROOT / "logs"):
        parser.error("new logs directory required")
    directory.mkdir(parents=True, exist_ok=True)
    for name, fn in (
        ("draw_plan_v5.json", draw_diagnostic),
        ("freeze_candidate_v3_refusal.json", freeze_diagnostic),
    ):
        path = directory / name
        value = fn()
        with path.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        print(
            json.dumps(
                {
                    "path": str(path),
                    "sha256": sha(path),
                    "binding_errors": len(value["binding_errors"]),
                }
            )
        )


if __name__ == "__main__":
    main()
