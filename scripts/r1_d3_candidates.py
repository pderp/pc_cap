"""R1-D3: reserve text-only zsRE training candidates; no tokenizer or teacher."""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manifests/revision_v1/zsre_fresh_candidates_v1.json"


def norm(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def select_rows(clear, inventory, blocked, *, n=6000, seed=139):
    if type(n) is not int or not 1 <= n <= len(clear):
        raise ValueError("candidate count outside clear inventory")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    by_index = {r["source_record_index"]: r for r in inventory}
    if len(by_index) != len(inventory):
        raise ValueError("duplicate source indices in manifest")
    seen_indices, seen_subjects, seen_facts = set(), set(), set()
    for item in clear:
        index, subject, fact = item["source_record_index"], norm(item["subject"]), item["fact_id"]
        old = by_index[index]
        if item.get("review_flags") or old["review_flags"]:
            raise ValueError("flagged item in clear inventory")
        if (
            old["mapped_item_sha256"] != digest(item)
            or old["source_record_sha256"] != item["source_record_sha256"]
        ):
            raise ValueError("per-record provenance mismatch")
        if not subject or subject in blocked or item["normalized_subject"] != subject:
            raise ValueError("invalid or previously excluded subject")
        if index in seen_indices or subject in seen_subjects or fact in seen_facts:
            raise ValueError("clear candidates must be unique by index, subject and fact")
        seen_indices.add(index)
        seen_subjects.add(subject)
        seen_facts.add(fact)
        for key in ("prompt", "answer"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError("missing required text: " + key)
        for key in ("paraphrases", "aliases", "locality_prompts", "locality_answers"):
            if (
                not isinstance(item.get(key), list)
                or not item[key]
                or any(not isinstance(s, str) or not s.strip() for s in item[key])
            ):
                raise ValueError("missing required text list: " + key)
        if len(item["paraphrases"]) != 1 or len(item["locality_prompts"]) != len(
            item["locality_answers"]
        ):
            raise ValueError("unexpected rephrase/locality cardinality")
    if [r["source_record_index"] for r in clear] != sorted(seen_indices):
        raise ValueError("clear source must be in ascending immutable source order")
    picked = np.random.Generator(np.random.PCG64(seed)).permutation(len(clear))[:n]
    rows = []
    for rank, offset in enumerate(picked):
        item = clear[int(offset)]
        row = {
            k: item[k]
            for k in (
                "item_id",
                "dataset",
                "source_split",
                "source_record_index",
                "subject",
                "normalized_subject",
                "prompt",
                "answer",
                "aliases",
                "paraphrases",
                "locality_prompts",
                "locality_answers",
                "fact_id",
                "digest",
                "target_policy",
                "source_record_sha256",
            )
        }
        row.update(
            rephrase=item["paraphrases"][0],
            locality_prompt=item["locality_prompts"][0],
            locality_answer=item["locality_answers"][0],
            draw_rank=rank,
            source_mapped_item_sha256=digest(item),
            field_sha256={
                k: digest(item[k])
                for k in (
                    "subject",
                    "prompt",
                    "answer",
                    "aliases",
                    "paraphrases",
                    "locality_prompts",
                    "locality_answers",
                )
            },
            exclusion_reasons=["train_pool_zsre_v1"],
            reservation_scope="all selected candidates, including teacher-rejected or unused candidates",
            teacher_eligible=None,
            confirmatory_eligible=False,
        )
        row["candidate_sha256"] = digest(row)
        rows.append(row)
    return rows


def prepare(source=SOURCE, *, n=6000, seed=139):
    source = Path(source).resolve()
    doc = json.loads(source.read_text())
    artifact = doc["artifacts"]["clear_candidates"]
    data_path = Path(artifact["path"])
    if sha(data_path) != artifact["sha256"]:
        raise ValueError("clear candidate artifact changed")
    register_path = ROOT / "manifests/revision_v1/exclusions_v2.json"
    if sha(register_path) != doc["sources_sha256"][str(register_path)]:
        raise ValueError("upstream exclusion register changed")
    register = json.loads(register_path.read_text())
    blocked = {r["normalized_subject"] for r in register["exclusions"]}
    clear = [json.loads(line) for line in data_path.read_text().splitlines()]
    if len(clear) != doc["counts"]["clear_pre_e2"]:
        raise ValueError("clear count mismatch")
    sources = {
        str(p): sha(p)
        for p in (
            source,
            data_path,
            register_path,
            Path(__file__).resolve(),
            ROOT / "scripts/r1_d3_e2_filter.py",
            ROOT / "docs/ongoing.md",
            ROOT / "docs/lead_queue.md",
        )
    }
    rows = select_rows(clear, doc["records"], blocked, n=n, seed=seed)
    additions = [
        {
            "normalized_subject": r["normalized_subject"],
            "canonical_subject_key": r["normalized_subject"],
            "reasons": r["exclusion_reasons"],
            "source_record_index": r["source_record_index"],
            "candidate_sha256": r["candidate_sha256"],
        }
        for r in rows
    ]
    result = {
        "schema_version": 1,
        "name": "train_pool_zsre_candidates_v1",
        "task": "R1-D3",
        "mode": "training_candidates",
        "dataset": "zsre",
        "decision": "DEC-039 (default yes in current lead directive; formal register update is owner-managed)",
        "status": "reserved_pre_teacher_candidates",
        "seed": seed,
        "requested_candidates": n,
        "selection": {
            "algorithm": "NumPy Generator(PCG64(seed)).permutation over ascending clear source indices; take first n",
            "numpy_version": np.__version__,
            "output_order": "random draw order retained for first-eligible E.2 selection; not sorted after draw",
            "independent_of_teacher": True,
            "target": "source answers[0]; never substitute alt or pred",
        },
        "counts": {
            "clear_before": len(clear),
            "reserved_candidates": len(rows),
            "reserved_unique_subjects": len(additions),
            "direct_clear_remainder": len(clear) - len(rows),
            "teacher_eligible": None,
            "intended_teacher_survivors": 3000,
        },
        "capacity": {
            "teacher_survival_required_for_3000": 3000 / len(rows),
            "survivors_guaranteed": False,
            "remainder_note": "58,498 -> 52,498 under this 6,000-subject reservation alone; contextual/alias review and future exposure can reduce it further",
        },
        "exclusion_register": {
            "target_version": 3,
            "reason": "train_pool_zsre_v1",
            "register_written": False,
            "required_scope": "all 6000 selected subjects leave confirmatory candidates now, not only the first 3000 teacher survivors",
            "additions": additions,
        },
        "drawn_subjects_normalized": sorted(r["normalized_subject"] for r in rows),
        "items_sha256": digest(rows),
        "items": rows,
        "sources_sha256": sources,
        "hash_convention": "SHA256 of UTF-8 json.dumps(sort_keys=True,ensure_ascii=False,separators=(',',':')); candidate hash excludes its own candidate_sha256 field",
        "tokenization_executed": False,
        "teacher_executed": False,
        "gpu_seconds": 0,
        "sealed_payloads_opened": 0,
        "next_steps": [
            "owner adds every reserved subject/reason to exclusions v3 before fresh candidate draws",
            "owner verifies input hashes and runs scripts/r1_d3_e2_filter.py under the GPU lease",
            "if fewer than 3000 survive, stop and version an additional reservation; do not silently draw extra candidates",
            "register new text/alias/context exposure and refresh fresh-candidate inventory before final sealing",
        ],
        "limitations": [
            "one source rephrase per item; no semantic re-verification in this draw",
            "preexisting token checks are provenance only; this file intentionally contains no token ID arrays",
            "v2 exclusions and lexical clear flags do not prove complete entity/context disjointness",
            "six thousand candidates improve reserve capacity but do not guarantee three thousand teacher-incorrect items",
        ],
    }
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("input changed while selecting: " + path)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository manifest required")
    result = prepare(args.source)
    payload = (
        json.dumps(result, indent=1, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as f:
        f.write(payload)
    print(
        json.dumps(
            {"output": str(args.output), "counts": result["counts"], "sha256": sha(args.output)}
        )
    )


if __name__ == "__main__":
    main()
