"""Reproduce R1-76 historical MQuAKE metadata capacity without selecting or executing rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.r1_76_unseen_common import ROOT, TRAIN_FILES, keys, norm, rowsets, sha


def audit():
    training = []
    for path in TRAIN_FILES.values():
        training.extend(json.loads(path.read_text())["items"][:1000])
    banned = rowsets(training)
    for row in training:
        for q in [*row.get("paraphrases", []), *row.get("locality_prompts", [])]:
            if isinstance(q, str) and q.strip():
                banned[3].add(norm(q))
    paths = [
        ROOT / "manifests/revision_v1/train_pool_mquake_v2.json",
        ROOT / "manifests/dev/mquake_dev.json",
    ]
    sources = {str(p): sha(p) for p in [*paths, *TRAIN_FILES.values()]}
    used = [set() for _ in range(4)]
    safe = []
    total = []
    excluded = duplicates = 0
    for path in paths:
        rows = json.loads(path.read_text())["items"]
        total.extend(rows)
        for row in rows:
            k = keys(row)
            if any(key in s for key, s in zip(k, banned, strict=True)):
                excluded += 1
                continue
            if any(key in s for key, s in zip(k, used, strict=True)):
                duplicates += 1
                continue
            for key, s in zip(k, used, strict=True):
                s.add(key)
            safe.append(row)
    for path, h in sources.items():
        if sha(path) != h:
            raise ValueError("source changed during capacity audit")
    return {
        "task": "R1-76",
        "mode": "metadata_capacity_audit_only",
        "source_rows": len(total),
        "historical_subjects": len({norm(r["subject"]) for r in total}),
        "reader_training_or_exact_query_excluded_rows": excluded,
        "duplicate_rows": duplicates,
        "eligible_distinct_metadata_rows": len(safe),
        "required_for_100_300_1000_with_outside100": 1100,
        "required_for_100_300_with_outside100": 400,
        "shortfall_full": max(0, 1100 - len(safe)),
        "nominal_168_slack_would_still_leave_shortfall": max(0, 1100 - len(safe) - 168),
        "selected_reader_training_prefixes": {"zsre": 1000, "counterfact": 1000, "mquake": 500},
        "sources_sha256": sources,
        "alias_clearance_certified": False,
        "counterfactual_or_query_execution": False,
        "final_candidate_rows_opened": False,
        "examples_emitted": 0,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT / "logs"):
        ap.error("new output under logs required")
    result = audit()
    with a.output.open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "eligible": result["eligible_distinct_metadata_rows"],
                "full_shortfall": result["shortfall_full"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
