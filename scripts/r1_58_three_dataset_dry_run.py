"""R1-58 DEC-045 addendum: count-only three-dataset capacity; never draw or seal."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from scripts.r1_58_draw_streams import ROOT, candidates, capacity, stratum
from scripts.r1_d4_prepare_mquake import digest, file_sha


def merge_subjects(existing, mquake_rows):
    """Count a proposed first-source/first-row subject policy, without RNG."""
    result = {ds: list(rows) for ds, rows in existing.items()}
    seen = {r["_canonical_subject"] for rows in existing.values() for r in rows}
    result["mquake"] = []
    removed = Counter()
    mquake_seen = set()
    for row in mquake_rows:
        key = row["subject_key"]
        if row["token_status"] != "candidate":
            removed["token_ineligible"] += 1
            continue
        if key in seen:
            removed["cross_dataset_subject_overlap"] += 1
            continue
        if key in mquake_seen:
            removed["within_mquake_extra_relation"] += 1
            continue
        mquake_seen.add(key)
        result["mquake"].append(
            {
                **row,
                "_canonical_subject": key,
                "_stratum": stratum(row),
                "_payload_sha256": digest(row),
            }
        )
    return result, dict(removed)


def load_three(source):
    rows, binding = candidates(source)
    manifest_path = ROOT / "manifests/revision_v1/mquake_items_v1.json"
    manifest = json.loads(manifest_path.read_text())
    for artifact in manifest["artifacts"].values():
        if file_sha(artifact["path"]) != artifact["sha256"]:
            raise ValueError("MQuAKE preparation artifact hash mismatch")
    item_path = Path(manifest["artifacts"]["items"]["path"])
    with item_path.open() as f:
        mquake = [json.loads(line) for line in f]
    expected = {r["item_id"]: r["prepared_record_sha256"] for r in manifest["items"]}
    if len(mquake) != len(expected) or {r["item_id"] for r in mquake} != set(expected):
        raise ValueError("MQuAKE inventory coverage mismatch")
    if any(digest(r) != expected[r["item_id"]] for r in mquake):
        raise ValueError("MQuAKE item identity mismatch")
    result, removed = merge_subjects(rows, mquake)
    binding["mquake_manifest"] = {"path": str(manifest_path), "sha256": file_sha(manifest_path)}
    binding["mquake_removed"] = removed
    binding["three_dataset_policy"] = (
        "PROPOSED count-only zsRE then CounterFact then MQuAKE subject precedence; "
        "first prepared MQuAKE row per subject. No final-source or training allocation approval implied."
    )
    return result, binding


def report(source):
    rows, binding = load_three(source)
    result = {
        "task": "R1-58 DEC-045 addendum",
        "mode": "three_dataset_count_only_dry_run",
        "binding": binding,
        **capacity(rows),
        "draws_emitted": 0,
        "rng_used": False,
        "candidate_ids_emitted": 0,
        "payloads_written": 0,
        "seals_written": 0,
        "gpu_seconds": 0,
        "final_eligible_counts": None,
        "new_register_required": True,
        "future_draw_status": "three-dataset admission must bind the next register, training/transfer decision and eligible inventories; this CLI never draws",
    }
    available = len(rows["mquake"])
    result["mquake_training_sensitivity_no_selection"] = {
        "assumed_additional_disjoint_training_subjects": 1000,
        "candidate_subject_capacity_after_reservation": max(0, available - 1000),
        "confirmation_role_demand": 4050,
        "pre_eligibility_surplus_after_training": available - 1000 - 4050,
        "note": "arithmetic only; no training set selected; aliases/context, teacher losses and composition dependency closures can consume this slack",
    }
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--counterfact-source", choices=("strict", "exception"), required=True)
    ap.add_argument("--dry-run", action="store_true", required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.report.exists() or not args.report.resolve().is_relative_to(ROOT / "logs"):
        ap.error("only a new count report under logs may be written")
    result = report(args.counterfact_source)
    with args.report.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "datasets": result["datasets"],
                "mquake_training_sensitivity": result["mquake_training_sensitivity_no_selection"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
