"""R1-D4: deterministic MQuAKE-CF source preparation; no model, draw or seal.

Only source-derived candidate resources are produced. Locality/near-miss lists
are per-item proposals, not globally disjoint final reservations. Composition
source provenance is preserved separately from final semantic/eligibility admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
SOURCE = ASSETS / "data/raw/mquake/MQuAKE-CF.json"
SOURCE_SHA = "fbf1ab9e5243e52da429f7636990096ae0b5f8fbf60f1d4d3a4bf0c9214cd6ea"


def norm(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def unique(values):
    return list(dict.fromkeys(v.strip() for v in values if isinstance(v, str) and v.strip()))


def pair_key(rewrite):
    return norm(rewrite["subject"]), rewrite["relation_id"]


def item_id(key):
    return "mquake:" + digest(list(key))[:24]


def target_same(a, b):
    # Stable entity identity is required where supplied; spelling alone cannot
    # turn two different Wikidata objects into a matched rewrite.
    return a.get("id") == b.get("id") and norm(a["str"]) == norm(b["str"])


def filled(rewrite):
    if rewrite["prompt"].count("{}") != 1:
        raise ValueError("one cloze subject slot required")
    return rewrite["prompt"].replace("{}", rewrite["subject"])


def prepare(cases, excluded, tokenizer, zsre_subjects=()):
    if len(cases) != len({c["case_id"] for c in cases}):
        raise ValueError("duplicate case_id")
    excluded = {norm(s) for s in excluded}
    ordered = sorted(cases, key=lambda c: c["case_id"])
    groups = defaultdict(list)
    for case in ordered:
        for index, rewrite in enumerate(case["requested_rewrite"]):
            if not rewrite["subject"].strip() or not rewrite["relation_id"]:
                raise ValueError("subject and relation required")
            filled(rewrite)
            groups[pair_key(rewrite)].append((case, index, rewrite))
    chosen = {key: rows[0] for key, rows in groups.items()}
    conflicts, drops, items, invalid = [], [], [], []
    occurrences = sum(len(c["requested_rewrite"]) for c in cases)
    all_subjects = {k[0] for k in groups}
    dropped_subjects = sorted(all_subjects & excluded)
    for key, rows in groups.items():
        first_case, first_index, selected = rows[0]
        for case, index, rewrite in rows[1:]:
            if not target_same(selected["target_new"], rewrite["target_new"]):
                conflicts.append(
                    {
                        "item_id": item_id(key),
                        "subject_key": key[0],
                        "relation_id": key[1],
                        "kept_case_id": first_case["case_id"],
                        "other_case_id": case["case_id"],
                        "other_rewrite_index": index,
                        "kept_target_new": selected["target_new"],
                        "other_target_new": rewrite["target_new"],
                        "kind": "target_new_conflict",
                    }
                )
            if not target_same(selected["target_true"], rewrite["target_true"]):
                conflicts.append(
                    {
                        "item_id": item_id(key),
                        "subject_key": key[0],
                        "relation_id": key[1],
                        "kept_case_id": first_case["case_id"],
                        "other_case_id": case["case_id"],
                        "kind": "target_true_conflict",
                        "kept_target_true": selected["target_true"],
                        "other_target_true": rewrite["target_true"],
                    }
                )
        if key[0] in excluded:
            drops.append(
                {
                    "item_id": item_id(key),
                    "subject_key": key[0],
                    "relation_id": key[1],
                    "first_case_id": first_case["case_id"],
                    "reason": "primary_subject_excluded_v3",
                }
            )
            continue
        prompt, answer = filled(selected), selected["target_new"]["str"]
        aliases, variants, alias_matches = [answer], [selected["question"]], []
        for case, index, rewrite in rows:
            if not target_same(selected["target_new"], rewrite["target_new"]):
                continue
            variants.extend((rewrite["question"], filled(rewrite)))
            anchors = {norm(filled(rewrite)), norm(rewrite["question"])}
            for field, target in (
                ("single_hops", rewrite["target_true"]),
                ("new_single_hops", selected["target_new"]),
            ):
                for hop_index, hop in enumerate(case[field]):
                    if norm(hop["answer"]) != norm(target["str"]):
                        continue
                    if not any(norm(hop.get(k, "")) in anchors for k in ("cloze", "question")):
                        continue
                    variants.extend((hop.get("question", ""), hop.get("cloze", "")))
                    if field == "new_single_hops":
                        aliases.extend(hop.get("answer_alias", []))
                        alias_matches.append(
                            {
                                "case_id": case["case_id"],
                                "rewrite_index": index,
                                "hop_index": hop_index,
                                "field": field,
                            }
                        )
        t = tokenize_pair(tokenizer, prompt, answer)
        paraphrases = [p for p in unique(variants) if norm(p) != norm(prompt)]
        status = "candidate" if not t.excluded else "token_ineligible"
        row = {
            "item_id": item_id(key),
            "fact_id": item_id(key),
            "dataset": "mquake",
            "subject": selected["subject"],
            "subject_key": key[0],
            "relation_id": key[1],
            "prompt": prompt,
            "answer": answer,
            "aliases": unique(aliases),
            "paraphrases": paraphrases,
            "prompt_ids": t.prompt_ids.tolist(),
            "answer_ids": t.answer_ids.tolist(),
            "target_new": selected["target_new"],
            "target_true": selected["target_true"],
            "source_case_id": first_case["case_id"],
            "source_rewrite_index": first_index,
            "source_record_sha256": digest(selected),
            "source_case_sha256": digest(first_case),
            "source_occurrences": [
                {"case_id": c["case_id"], "rewrite_index": i, "rewrite_sha256": digest(r)}
                for c, i, r in rows
            ],
            "alias_provenance": alias_matches,
            "token_status": status,
            "token_reason": t.reason,
            "teacher_eligible": None,
            "context_alias_review_complete": False,
            "version": 1,
            "locality_prompts": [],
            "locality": [],
            "near_miss_candidates": [],
            "digest": hashlib.sha256(f"{item_id(key)}|{prompt}|{answer}".encode()).hexdigest()[:32],
        }
        if not paraphrases:
            raise ValueError("source question paraphrase required")
        items.append(row)
        if t.excluded:
            invalid.append({"item_id": row["item_id"], "reason": t.reason})
    by_relation = defaultdict(list)
    for row in items:
        if row["token_status"] == "candidate":
            by_relation[row["relation_id"]].append(row)
    # Deterministic neighbours from other, unexcluded subjects. Selecting these
    # development-free source annotations is preparation, never a stream draw.
    for relation_rows in by_relation.values():
        relation_rows.sort(key=lambda r: (r["subject_key"], r["item_id"]))
        for i, row in enumerate(relation_rows):
            neighbours, seen = [], {row["subject_key"]}
            for offset in range(1, len(relation_rows)):
                other = relation_rows[(i + offset) % len(relation_rows)]
                if other["subject_key"] in seen:
                    continue
                old = tokenize_pair(tokenizer, other["prompt"], other["target_true"]["str"])
                if old.excluded:
                    continue
                seen.add(other["subject_key"])
                neighbours.append(
                    {
                        "item_id": other["item_id"],
                        "subject_key": other["subject_key"],
                        "relation_id": other["relation_id"],
                        "prompt": other["prompt"],
                        "answer": other["target_true"]["str"],
                        "aliases": [other["target_true"]["str"]],
                        "prompt_ids": old.prompt_ids.tolist(),
                        "answer_ids": old.answer_ids.tolist(),
                        "source_case_id": other["source_case_id"],
                        "source_record_sha256": other["source_record_sha256"],
                        "reference": "source target_true; teacher agreement untested",
                    }
                )
                if len(neighbours) == 4:
                    break
            row["locality"] = neighbours[:2]
            row["locality_prompts"] = [n["prompt"] for n in neighbours[:2]]
            row["near_miss_candidates"] = neighbours[2:4]
    kept = {row["item_id"]: row for row in items}
    compositions = []
    for case in ordered:
        dependencies, reasons = [], set()
        for rewrite in case["requested_rewrite"]:
            key = pair_key(rewrite)
            selected = chosen[key][2]
            rid = item_id(key)
            status = "available_source_item"
            if rid not in kept:
                status = "excluded_subject"
            elif kept[rid]["token_status"] != "candidate":
                status = "token_ineligible"
            elif not target_same(selected["target_new"], rewrite["target_new"]):
                status = "conflicts_with_first_case_target"
            if status != "available_source_item":
                reasons.add(status)
            dependencies.append(
                {
                    "item_id": rid,
                    "subject_key": key[0],
                    "relation_id": key[1],
                    "required_target_new": rewrite["target_new"],
                    "status": status,
                }
            )
        context_subjects = {
            norm(t[0])
            for name in ("triples_labeled", "new_triples_labeled")
            for t in case["orig"].get(name, [])
            if t and isinstance(t[0], str)
        }
        compositions.append(
            {
                "composition_id": f"mquake:case:{case['case_id']}",
                "case_id": case["case_id"],
                "verified_source": "MQuAKE",
                "questions": case["questions"],
                "answer": case["answer"],
                "answer_aliases": unique([case["answer"], *case["answer_alias"]]),
                "new_answer": case["new_answer"],
                "new_answer_aliases": unique([case["new_answer"], *case["new_answer_alias"]]),
                "orig": case["orig"],
                "dependencies": dependencies,
                "source_case_sha256": digest(case),
                "all_rewrite_dependencies_available": not reasons,
                "unavailable_reasons": sorted(reasons),
                "context_subjects_in_exclusions_v3": sorted(context_subjects & excluded),
                "semantic_admission": "source-provided direct questions; final selected-edit compatibility, context and teacher checks pending",
                "final_eligible": None,
            }
        )
    active_comp_counts = Counter()
    all_comp_counts = Counter()
    for case in compositions:
        for rid in {d["item_id"] for d in case["dependencies"]} & kept.keys():
            all_comp_counts[rid] += len(case["questions"])
            if case["all_rewrite_dependencies_available"]:
                active_comp_counts[rid] += len(case["questions"])
    for row in items:
        row["composition_question_count_source"] = all_comp_counts[row["item_id"]]
        row["composition_question_count_available_dependencies"] = active_comp_counts[
            row["item_id"]
        ]
    kept_subjects = {r["subject_key"] for r in items}
    zsre_overlap = sorted(kept_subjects & {norm(s) for s in zsre_subjects})
    summary = {
        "source_cases": len(cases),
        "rewrite_occurrences": occurrences,
        "unique_subject_relation": len(groups),
        "source_subjects": len(all_subjects),
        "excluded_subjects": len(dropped_subjects),
        "excluded_unique_rewrites": len(drops),
        "items": len(items),
        "subjects": len(kept_subjects),
        "relations": len(by_relation),
        "relation_histogram": dict(sorted(Counter(r["relation_id"] for r in items).items())),
        "answer_tokens_including_newline_histogram": dict(
            sorted(Counter(len(r["answer_ids"]) for r in items).items())
        ),
        "token_ineligible": len(invalid),
        "target_new_conflicting_occurrences": sum(
            c["kind"] == "target_new_conflict" for c in conflicts
        ),
        "target_true_conflicting_occurrences": sum(
            c["kind"] == "target_true_conflict" for c in conflicts
        ),
        "locality_coverage_histogram": dict(
            sorted(Counter(len(r["locality"]) for r in items).items())
        ),
        "near_miss_coverage_histogram": dict(
            sorted(Counter(len(r["near_miss_candidates"]) for r in items).items())
        ),
        "composition_cases": len(compositions),
        "composition_questions": sum(len(c["questions"]) for c in compositions),
        "composition_cases_all_dependencies_available": sum(
            c["all_rewrite_dependencies_available"] for c in compositions
        ),
        "composition_cases_with_excluded_context_subjects": sum(
            bool(c["context_subjects_in_exclusions_v3"]) for c in compositions
        ),
        "composition_questions_per_item_histogram": dict(
            sorted(Counter(r["composition_question_count_source"] for r in items).items())
        ),
        "composition_available_questions_per_item_histogram": dict(
            sorted(
                Counter(
                    r["composition_question_count_available_dependencies"] for r in items
                ).items()
            )
        ),
        "zsre_v3_fresh_candidate_subject_overlap": len(zsre_overlap),
    }
    subjects = [
        {
            "subject_key": s,
            "item_ids": sorted(r["item_id"] for r in items if r["subject_key"] == s),
            "preparation_only": True,
            "used_for_training_or_evaluation": False,
        }
        for s in sorted(kept_subjects)
    ]
    return {
        "items": items,
        "composition": compositions,
        "conflicts": conflicts,
        "excluded_items": drops,
        "excluded_subjects": dropped_subjects,
        "subjects": subjects,
        "zsre_overlap_subjects": zsre_overlap,
        "token_ineligible": invalid,
        "summary": summary,
    }


def source_inputs():
    source_sha = file_sha(SOURCE)
    datasets_path = ROOT / "manifests/datasets.json"
    ds = json.loads(datasets_path.read_text())["mquake"]
    if source_sha != SOURCE_SHA or ds["files"]["data/raw/mquake/MQuAKE-CF.json"] != source_sha:
        raise ValueError("pinned MQuAKE source identity mismatch")
    from scripts.r1_58_draw_streams import WRAPPER, WRAPPER_SHA, candidates

    rows, binding = candidates("strict")
    reg_path = Path(json.loads(WRAPPER.read_text())["register"]["path"])
    reg = json.loads(reg_path.read_text())
    excluded = {r["normalized_subject"] for r in reg["exclusions"]}
    tokenizer = GPT2Tokenizer()
    sources = {
        str(SOURCE): source_sha,
        str(datasets_path): file_sha(datasets_path),
        str(reg_path): file_sha(reg_path),
        str(WRAPPER): WRAPPER_SHA,
        str(tokenizer.path): tokenizer.file_sha256(),
        **binding["bindings_sha256"],
    }
    return (
        json.loads(SOURCE.read_text()),
        excluded,
        tokenizer,
        {r["_canonical_subject"] for r in rows["zsre"]},
    ), sources


def write_outputs(result, sources, resource_dir, manifest_path, report_path):
    resource_dir, manifest_path, report_path = (
        Path(p).resolve() for p in (resource_dir, manifest_path, report_path)
    )
    if any(p.exists() for p in (resource_dir, manifest_path, report_path)):
        raise FileExistsError("outputs must all be new")
    if (
        not resource_dir.is_relative_to(ASSETS)
        or not manifest_path.is_relative_to(ROOT / "manifests")
        or not report_path.is_relative_to(ROOT / "logs")
    ):
        raise ValueError("resources under assets; manifest/log under pc_cap")
    for path, expected in sources.items():
        if file_sha(path) != expected:
            raise ValueError("source changed during preparation")
    resource_dir.mkdir(parents=True, exist_ok=False)
    artifacts = {}
    for name in (
        "items",
        "composition",
        "conflicts",
        "excluded_items",
        "excluded_subjects",
        "subjects",
        "zsre_overlap_subjects",
        "token_ineligible",
    ):
        path = resource_dir / f"{name}.jsonl"
        with path.open("x") as f:
            for row in result[name]:
                f.write(
                    json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                )
        artifacts[name] = {
            "path": str(path),
            "sha256": file_sha(path),
            "records": len(result[name]),
        }
    meta = {
        "task": "R1-D4",
        "schema_version": 1,
        "dataset": "mquake",
        "source": "MQuAKE-CF",
        "status": "prepared_source_candidates_not_teacher_eligible",
        "sources_sha256": sources,
        "script_sha256": file_sha(__file__),
        "summary": result["summary"],
        "artifacts": artifacts,
        "gpu_seconds": 0,
        "model_execution": False,
        "draws": 0,
        "seals": 0,
        "policies": {
            "dedup": "NFKC/casefold/whitespace subject plus relation; lowest case_id then rewrite index wins",
            "locality_near": "two plus two distinct other subjects, same relation, source target_true; per-item candidates only",
            "final_split": "global role, subject, alias and context disjointness must be checked after eligibility and training reservation",
            "composition": "verified_source means source-provided direct questions; conflicting or absent dependencies stay unavailable",
            "training": "no training pool selected; preparation exposure inventory is not permission to consume candidates",
            "alias_variants": "merge only same chosen target across occurrences; exact cloze/question anchor and matching hop answer",
        },
        "items": [
            {
                "item_id": r["item_id"],
                "subject_key_sha256": digest(r["subject_key"]),
                "relation_id": r["relation_id"],
                "source_case_id": r["source_case_id"],
                "source_record_sha256": r["source_record_sha256"],
                "prepared_record_sha256": digest(r),
                "answer_tokens": len(r["answer_ids"]),
                "token_status": r["token_status"],
                "locality_n": len(r["locality"]),
                "near_miss_n": len(r["near_miss_candidates"]),
                "composition_question_count_source": r["composition_question_count_source"],
                "composition_question_count_available_dependencies": r[
                    "composition_question_count_available_dependencies"
                ],
            }
            for r in result["items"]
        ],
    }
    with manifest_path.open("x") as f:
        f.write(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    report = {k: v for k, v in meta.items() if k != "items"}
    report["manifest"] = {"path": str(manifest_path), "sha256": file_sha(manifest_path)}
    with report_path.open("x") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--resource-dir", type=Path, default=ASSETS / "data/prepared/revision_v1/r1_d4_v1"
    )
    ap.add_argument(
        "--manifest", type=Path, default=ROOT / "manifests/revision_v1/mquake_items_v1.json"
    )
    ap.add_argument("--report", type=Path, default=ROOT / "logs/r1_round9/mquake_preparation.json")
    args = ap.parse_args()
    if any(p.exists() for p in (args.resource_dir, args.manifest, args.report)):
        ap.error("all outputs must be new")
    inputs, sources = source_inputs()
    result = prepare(*inputs)
    report = write_outputs(result, sources, args.resource_dir, args.manifest, args.report)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
