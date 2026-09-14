"""R1-D1e: additive exclusion register v3 and unsealed candidate-count refresh."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def fold(prior, reservation):
    old = {r["normalized_subject"]: copy.deepcopy(r) for r in prior["exclusions"]}
    if len(old) != len(prior["exclusions"]):
        raise ValueError("duplicate old exclusion subjects")
    items = reservation["items"]
    if len(items) != 6000 or digest(items) != reservation["items_sha256"]:
        raise ValueError("reservation count/hash mismatch")
    subjects = {r["normalized_subject"] for r in items}
    if len(subjects) != 6000 or subjects != set(reservation["drawn_subjects_normalized"]):
        raise ValueError("reservation subject coverage mismatch")
    additions = reservation["exclusion_register"]["additions"]
    if {r["normalized_subject"] for r in additions} != subjects or len(additions) != 6000:
        raise ValueError("incomplete register additions")
    for row in items:
        if (
            digest({k: v for k, v in row.items() if k != "candidate_sha256"})
            != row["candidate_sha256"]
        ):
            raise ValueError("candidate identity mismatch")
        if (
            row["exclusion_reasons"] != ["train_pool_zsre_v1"]
            or row["confirmatory_eligible"] is not False
        ):
            raise ValueError("candidate must remain reserved")
    for add in additions:
        key = add["normalized_subject"]
        if add["reasons"] != ["train_pool_zsre_v1"]:
            raise ValueError("incorrect reservation reason")
        if key in old:
            old[key]["reasons"] = sorted(set(old[key]["reasons"]) | set(add["reasons"]))
        else:
            old[key] = {
                "normalized_subject": key,
                "canonical_subject_key": add["canonical_subject_key"],
                "reasons": list(add["reasons"]),
            }
    return [old[key] for key in sorted(old)], subjects


def prepare(output, external):
    if (
        output.exists()
        or external.exists()
        or not output.resolve().is_relative_to(ROOT)
        or not external.resolve().is_relative_to(ASSETS)
    ):
        raise ValueError("new repository register and new assets directory required")
    paths = {
        k: ROOT / rel
        for k, rel in {
            "prior": "manifests/revision_v1/exclusions_v2.json",
            "reservation": "manifests/revision_v1/train_pool_zsre_candidates_v1.json",
            "clear": "manifests/revision_v1/zsre_fresh_candidates_v1.json",
            "training": "manifests/revision_v1/train_pool_zsre_v1.json",
        }.items()
    }
    sources = {str(p): sha(p) for p in paths.values()}
    sources[str(Path(__file__).resolve())] = sha(__file__)
    docs = {k: json.loads(p.read_text()) for k, p in paths.items()}
    prior, reservation = docs["prior"], docs["reservation"]
    exclusions, reserved = fold(prior, reservation)
    source_candidates = Path(prior["candidates"]["path"])
    if sha(source_candidates) != prior["candidates"]["sha256"]:
        raise ValueError("prior candidate artifact changed")
    sources[str(source_candidates)] = sha(source_candidates)
    raw_candidates = [json.loads(line) for line in source_candidates.read_text().splitlines()]
    survivors = [r for r in raw_candidates if r["normalized_subject"] not in reserved]
    reserved_indices = {r["source_record_index"] for r in reservation["items"]}
    original_clear = [r for r in docs["clear"]["records"] if not r["review_flags"]]
    clear_survivors = [
        r for r in original_clear if r["source_record_index"] not in reserved_indices
    ]
    if len(original_clear) != 58498 or len(clear_survivors) != 52498:
        raise ValueError("direct clear-candidate arithmetic mismatch")
    if (
        len({r["normalized_subject"] for r in raw_candidates})
        - len({r["normalized_subject"] for r in survivors})
        != 6000
    ):
        raise ValueError("raw subject reservation does not remove exactly 6000 identities")
    trained = {r["subject"] for r in docs["training"]["items"]}
    selected = {r["subject"] for r in reservation["items"]}
    if not trained <= selected:
        raise ValueError("training pool contains an unreserved primary subject")
    excluded_subjects = {r["normalized_subject"] for r in exclusions}
    if any(r["normalized_subject"] in excluded_subjects for r in survivors):
        raise ValueError("excluded subject survives in candidate inventory")
    for old in prior["exclusions"]:
        new = next(r for r in exclusions if r["normalized_subject"] == old["normalized_subject"])
        if new["canonical_subject_key"] != old["canonical_subject_key"] or not set(
            old["reasons"]
        ) <= set(new["reasons"]):
            raise ValueError("prior exclusion or canonicalization lost")
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("source changed: " + path)
    external.mkdir(parents=True)
    candidate_path = external / "mend_candidate_subjects.jsonl"
    clear_path = external / "prior_clear_subject_survivors.jsonl"
    for path, rows in ((candidate_path, survivors), (clear_path, clear_survivors)):
        with path.open("x") as f:
            for row in rows:
                f.write(
                    json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                )
    result = copy.deepcopy(prior)
    result.update(
        name="revision_v1_exclusions",
        version="r1-d1e-v3",
        task="R1-D1e",
        status="training_reservations_folded_nonfinal",
        supersedes_sha256=sources[str(paths["prior"])],
        exclusions=exclusions,
        sources_sha256=sources,
        candidates={
            "path": str(candidate_path),
            "sha256": sha(candidate_path),
            "raw_records": len(survivors),
            "unique_subjects": len({r["normalized_subject"] for r in survivors}),
            "scope": "primary-subject exclusions only; contextual/entity review and E.2 still required",
        },
        clear_candidate_subject_survivors={
            "path": str(clear_path),
            "sha256": sha(clear_path),
            "records": len(clear_survivors),
            "scope": "prior lexical-clear representatives after removing newly reserved primary subjects; NOT re-certified clear under all new contextual mentions",
        },
        reservation={
            "manifest": str(paths["reservation"]),
            "sha256": sources[str(paths["reservation"])],
            "reason": "train_pool_zsre_v1",
            "subjects": len(reserved),
            "accepted_training_items": len(docs["training"]["items"]),
            "all_candidates_excluded": True,
            "unused_and_teacher_rejected_candidates_remain_excluded": True,
        },
        counts_v3={
            "exclusion_subjects_before": len(prior["exclusions"]),
            "exclusion_subjects_after": len(exclusions),
            "new_training_subjects": len(reserved),
            "raw_candidate_records_before": len(raw_candidates),
            "raw_candidate_records_after": len(survivors),
            "candidate_unique_subjects_before": len(
                {r["normalized_subject"] for r in raw_candidates}
            ),
            "candidate_unique_subjects_after": len({r["normalized_subject"] for r in survivors}),
            "prior_clear_representatives_before": len(original_clear),
            "prior_clear_primary_subject_survivors": len(clear_survivors),
            "confirmed_context_clear_after_new_exposure": None,
            "teacher_eligible_fresh_candidates": None,
            "final_realizations_emitted": 0,
        },
        final_sealing_ready=False,
        sealed_realization_payloads_opened=0,
        gpu_seconds=0,
        freeze_scope="v3 exposure update only; no final freeze, data draw or revised alias/context acceptance",
        prior_policy_review_report=prior.get("review_report"),
        review_report=str(ROOT / "docs/tasks/R1-D1e.md"),
        prior_review_counts=copy.deepcopy(prior.get("review_counts")),
        next_gates=[
            "all future candidate/teacher/final planners must use v3 rather than the historical v2 inventory",
            "recheck contextual/entity/alias overlap against the newly exposed training texts; 52498 is the direct primary-subject ceiling, not certified context-clear capacity",
            "owner E.2 over remaining candidates with versioned hashes/order and stated reserve; no teacher work in this task",
            "lead-approved final population and independent sealing after all data/implementation/cost gates",
        ],
    )
    payload = (
        json.dumps(result, indent=1, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    )
    with output.open("x") as f:
        f.write(payload)
    print(json.dumps({"output": str(output), "sha256": sha(output), "counts": result["counts_v3"]}))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--assets-output", type=Path, required=True)
    args = ap.parse_args()
    prepare(args.output.resolve(), args.assets_output.resolve())


if __name__ == "__main__":
    main()
