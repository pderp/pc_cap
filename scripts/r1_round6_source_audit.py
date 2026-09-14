"""Audit round-6 hash bindings and preserve matching historical repository sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "manifests/revision_v1/train_pool_zsre_candidates_v1.json",
    "logs/r1_round6/near_neighbour_separability.json",
    "logs/r1_round6/stream_review_evidence.json",
    "logs/r1_round6/stream_response_evidence.json",
    "manifests/revision_v1/exclusions_v3.json",
    "manifests/revision_v1/run_matrix_draft_v2.json",
)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def run(output, snapshots):
    if output.exists() or snapshots.exists():
        raise ValueError("new audit and snapshot directory required")
    if not output.resolve().is_relative_to(ROOT) or not snapshots.resolve().is_relative_to(ROOT):
        raise ValueError("all audit artifacts must be in repository")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    refs = {}
    artifact_hashes = {}
    for rel in ARTIFACTS:
        path = ROOT / rel
        artifact_hashes[rel] = sha(path)
        doc = json.loads(path.read_text())
        for source, expected in doc["sources_sha256"].items():
            refs.setdefault((source, expected), []).append(rel)
    rows = []
    snapshots.mkdir(parents=True)
    for (source, expected), consumers in sorted(refs.items()):
        path = Path(source)
        actual = sha(path) if path.exists() else None
        row = {
            "source": source,
            "expected_sha256": expected,
            "current_sha256": actual,
            "consumers": consumers,
            "status": "current_match" if expected == actual else "drift",
        }
        if row["status"] == "drift" and path.resolve().is_relative_to(ROOT):
            rel = str(path.resolve().relative_to(ROOT))
            commits = subprocess.check_output(
                ["git", "log", "--all", "--format=%H", "--", rel], cwd=ROOT, text=True
            ).splitlines()
            for commit in commits:
                result = subprocess.run(
                    ["git", "show", f"{commit}:{rel}"], cwd=ROOT, capture_output=True
                )
                if result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == expected:
                    saved = snapshots / expected / rel
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    with saved.open("xb") as f:
                        f.write(result.stdout)
                    row.update(
                        status="historical_repository_snapshot_preserved",
                        snapshot=str(saved),
                        snapshot_commit=commit,
                    )
                    break
            else:
                row["status"] = "repository_drift_no_matching_commit"
        elif row["status"] == "drift":
            row["status"] = "external_resource_changed_since_earlier_evidence"
            row["note"] = (
                "earlier bank review remains point-in-time evidence; owner stamped banks in place during "
                "R50-06 repairs. The later response audit binds the new bytes. No retroactive reconstruction "
                "of the old serialized resource is claimed."
            )
        rows.append(row)
    result = {
        "task": "CODEX-R1-round6",
        "head": head,
        "artifact_sha256": artifact_hashes,
        "bindings": rows,
        "counts": dict(Counter(r["status"] for r in rows)),
        "interpretation": "Source drift is reported, never fixed by changing a historical manifest; "
        "owner commits proceeded concurrently. Historical source snapshots are read-only evidence.",
        "gpu_seconds": 0,
    }
    for rel, expected in artifact_hashes.items():
        assert sha(ROOT / rel) == expected
    with output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "head": head,
                "artifacts": len(artifact_hashes),
                "counts": result["counts"],
                "noncurrent": [
                    {k: v for k, v in r.items() if k != "consumers"}
                    for r in rows
                    if r["status"] != "current_match"
                ],
            },
            indent=2,
        )
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--snapshots", type=Path, required=True)
    args = ap.parse_args()
    run(args.output.resolve(), args.snapshots.resolve())


if __name__ == "__main__":
    main()
