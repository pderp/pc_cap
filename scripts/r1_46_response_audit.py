"""Read-only CPU recheck of the owner's R1-46 response, pinned to source hashes."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pickle
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np
from scripts.r1_46_stream_audit import fixture_bank

from pccap.revision_v1.stream_train import (
    bank_identity,
    merge_banks,
    stream_episode_mixed,
    verify_bank,
)

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def run():
    paths = [
        "src/pccap/revision_v1/stream_train.py",
        "src/pccap/revision_v1/train_fast.py",
        "scripts/r1_50_stream_train.py",
        "scripts/r1_52_operating_point.py",
        "docs/tasks/R1-46-response.md",
        "scripts/r1_46_response_audit.py",
        "scripts/r1_46_stream_audit.py",
    ]
    sources = {str(ROOT / p): sha(ROOT / p) for p in paths}
    bank = fixture_bank(4)
    rows = [
        {
            "item_id": it.item_id,
            "prompt_ids": it.prompt_ids.tolist(),
            "answer_ids": it.answer_ids.tolist(),
            "paraphrases": ["paraphrase"],
            "locality_prompts": ["locality"],
            "subject": it.subject,
        }
        for it in bank.items
    ]
    expected = bank_identity(rows, "base-A", 1, (2, 5, 8), 2, 2, np.float16)
    bank.identity = copy.deepcopy(expected)
    verify_bank(bank, expected)
    altered_rows = copy.deepcopy(rows)
    altered_rows[0]["paraphrases"] = ["entirely different paraphrase"]
    altered_rows[0]["locality_prompts"] = ["entirely different locality"]
    altered_rows[0]["subject"] = "different subject"
    unchanged_pool_identity = expected == bank_identity(
        altered_rows, "base-A", 1, (2, 5, 8), 2, 2, np.float16
    )
    original_hash = bank.content_hash()
    bank.items[0].key_last[:] = 9999
    feature_corruption_unhashed = bank.content_hash() == original_hash
    verify_bank(bank, expected)
    bank.items[0].prompt_ids[0] = 777
    verify_bank(bank, expected)
    prompt_mutation_still_admitted = bank.content_hash() != original_hash

    # This is exactly the migration's alleged content check: both sides read the bank.
    bank_side_digest = hashlib.sha256(
        b"".join(
            it.item_id.encode()
            + np.asarray(it.prompt_ids, np.int32).tobytes()
            + np.asarray(it.answer_ids, np.int32).tobytes()
            for it in bank.items
        )
    ).hexdigest()
    migration_rejects = (
        bank.content_hash() != bank_side_digest
        or len(bank.items) != len(rows)
        or any(it.item_id != r["item_id"] for it, r in zip(bank.items, rows))
    )
    legacy = fixture_bank(4)
    del legacy.identity
    legacy = pickle.loads(pickle.dumps(legacy))
    try:
        _ = legacy.identity
        legacy_access = "success"
    except AttributeError as error:
        legacy_access = type(error).__name__

    real_legacy = {}
    for dataset in ("counterfact", "zsre"):
        path = ROOT.parent / "assets/runs/pc_cap/R1/banks" / f"train_pool_{dataset}_v1_1000.pkl"
        before = sha(path)
        obj = pickle.loads(path.read_bytes())
        real_legacy[dataset] = {
            "path": str(path),
            "sha256": before,
            "items": len(obj.items),
            "identity_attribute_present": hasattr(obj, "identity"),
            "identity_in_instance_state": "identity" in vars(obj),
        }
        assert sha(path) == before
        sources[str(path)] = before
        del obj

    mixed = merge_banks([fixture_bank(100, "a"), fixture_bank(100, "b")])
    ix = [list(range(100)), list(range(100, 200))]
    missed_own, missed_out, counts = [], [], Counter()
    for seed in range(512):
        episode = stream_episode_mixed(
            ix, mixed, np.random.default_rng(seed), n_memory=64, n_query_records=8, n_out=8
        )
        own = [q for q in episode.queries if q.role == "own_prompt"]
        out = [q for q in episode.queries if q.role == "unrelated_no_kl"]
        if len({q.query_id.split(":", 1)[1][0] for q in own}) < 2:
            missed_own.append(seed)
        if len({q.query_id.split(":", 1)[1][0] for q in out}) < 2:
            missed_out.append(seed)
        counts[len(own)] += 1
    short = stream_episode_mixed(
        [[0, 1], [100, 101]],
        mixed,
        np.random.default_rng(0),
        n_memory=4,
        n_query_records=2,
        n_out=8,
    )
    odd = stream_episode_mixed(
        ix, mixed, np.random.default_rng(0), n_memory=5, n_query_records=1, n_out=0
    )
    assert unchanged_pool_identity and feature_corruption_unhashed
    assert prompt_mutation_still_admitted and not migration_rejects
    assert legacy_access == "AttributeError"
    assert not missed_own
    assert len(odd.supports) == 5
    for path, expected_sha in sources.items():
        if sha(path) != expected_sha:
            raise RuntimeError("review source changed during audit: " + path)
    return {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "sources_sha256": sources,
        "cache": {
            "paraphrase_locality_subject_changes_do_not_change_identity": unchanged_pool_identity,
            "cached_feature_change_does_not_change_content_hash": feature_corruption_unhashed,
            "recorded_identity_verification_accepts_prompt_mutation": prompt_mutation_still_admitted,
            "migration_self_comparison_rejects_changed_prompt": migration_rejects,
            "legacy_pickle_identity_access": legacy_access,
            "actual_existing_banks": real_legacy,
            "scope": "in-memory mutations only; no cache migration, model inference, or disk mutation",
        },
        "mixed": {
            "episodes": 512,
            "own_query_domain_missing_seeds": missed_own,
            "out_of_memory_domain_missing_seeds": missed_out,
            "own_query_count_histogram": dict(counts),
            "odd_requested_memory": 5,
            "odd_actual_memory": len(odd.supports),
            "short_pool_requested_out": 8,
            "short_pool_actual_out": sum(q.role == "unrelated_no_kl" for q in short.queries),
            "short_pool_refused": False,
        },
        "gpu_seconds": 0,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    evidence = run()
    with args.output.open("x") as f:
        f.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in evidence.items() if k != "sources_sha256"}, indent=2))


if __name__ == "__main__":
    main()
