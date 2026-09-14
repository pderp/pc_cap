"""CPU candidate-level zsRE review; never selects by teacher or emits final draws.

Ordered payloads/review text live under assets; the repository manifest carries
counts and per-record source hashes. Exclusion matches are conservative flags,
not assertions that a substring identifies the same real-world entity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from r1_d1_exclusions import ASSETS, ROOT, norm, sha, words, write_json


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


class ExclusionMatcher:
    def __init__(self, subjects):
        self.trie = {}
        for subject in subjects:
            key = words(subject)
            if not key:
                continue
            node = self.trie
            for token in key:
                node = node.setdefault(token, {})
            node.setdefault(None, []).append(subject)

    def matches(self, text):
        tokens = words(text)
        found = set()
        for i in range(len(tokens)):
            node = self.trie
            for token in tokens[i:]:
                if token not in node:
                    break
                node = node[token]
                found.update(node.get(None, ()))
        return sorted(found)


def structural_reasons(row):
    reasons = []
    for k in ("subject", "src", "rephrase", "loc", "loc_ans"):
        if not isinstance(row.get(k), str) or not norm(row[k]):
            reasons.append("missing_or_invalid_" + k)
    answers = row.get("answers")
    if not isinstance(answers, list) or not answers or any(not isinstance(a, str) or not norm(a) for a in answers):
        reasons.append("missing_or_invalid_answers")
    if reasons:
        return reasons
    if norm(row["rephrase"]) == norm(row["src"]):
        reasons.append("rephrase_equals_prompt")
    if norm(row["loc"]) in (norm(row["src"]), norm(row["rephrase"])):
        reasons.append("locality_equals_edit_query")
    if any("\n" in a.strip() or "\r" in a.strip() for a in answers):
        reasons.append("embedded_answer_terminator")
    if any("\x00" in row[k] for k in ("subject", "src", "rephrase", "loc", "loc_ans")):
        reasons.append("nul_in_text")
    return reasons


def map_item(index, row, tokenizer):
    # Same target and delimiter convention as data.splits.zsre_item and
    # data.tokenize.tokenize_pair, with TRAIN-specific IDs (never eval IDs).
    answer = row["answers"][0].strip()
    sep = "" if row["src"][-1].isspace() else " "
    answer_text = sep + answer + "\n"
    encoded = tokenizer.encode_batch([row["src"], answer_text, row["rephrase"], row["loc"]], add_special_tokens=False)
    prompt_ids, answer_ids, para_ids, loc_ids = [e.ids for e in encoded]
    reasons = []
    if not answer_ids or len(answer_ids) > 32:
        reasons.append("answer_tokens_outside_1_32")
    if tokenizer.decode(answer_ids, skip_special_tokens=False) != answer_text:
        reasons.append("answer_roundtrip_failure")
    if any(not ids or len(ids) > 992 for ids in (prompt_ids, para_ids, loc_ids)):
        reasons.append("query_tokens_outside_1_992")
    if para_ids == prompt_ids:
        reasons.append("rephrase_token_identical_to_prompt")
    item_id = f"zsre-train-{index}"
    item = {"item_id": item_id, "dataset": "zsre", "source_split": "mend_train", "source_record_index": index,
        "subject": row["subject"], "normalized_subject": norm(row["subject"]), "prompt": row["src"],
        "answer": answer, "aliases": sorted({norm(a) for a in row["answers"]}),
        "paraphrases": [row["rephrase"]], "locality_prompts": [row["loc"]], "locality_answers": [row["loc_ans"]],
        "prompt_ids": prompt_ids, "answer_ids": answer_ids, "answer_tokens": len(answer_ids),
        "paraphrase_token_lengths": [len(para_ids)], "locality_token_lengths": [len(loc_ids)],
        "fact_id": "zsre-train-fact-" + digest((norm(row["src"]), norm(answer)))[:24],
        "digest": hashlib.sha256(f"{item_id}|{row['src']}|{answer}".encode()).hexdigest()[:32],
        "target_policy": "first answers[] entry, aliases from answers[]; alt/pred are not substituted",
        "teacher_eligible": None, "final_assignment": None}
    return item, reasons


def review(output, external, report_path):
    for p in (output, report_path):
        if p.exists() or not p.resolve().is_relative_to(ROOT):
            raise ValueError("manifest/report must be new repository files")
    if external.exists() or not external.resolve().is_relative_to(ASSETS):
        raise ValueError("candidate data must be a new assets directory")
    inputs = {}
    def bind(p, expected=None):
        p = Path(p).resolve()
        h = sha(p)
        if expected and h != expected:
            raise ValueError("source hash mismatch: " + str(p))
        inputs[str(p)] = h
        return p
    ep = bind(ROOT / "manifests/revision_v1/exclusions_v2.json")
    exclusions = json.loads(ep.read_text())
    blocked = {r["normalized_subject"]: r for r in exclusions["exclusions"]}
    raw_path = ASSETS / "data/raw/zsre/zsre_mend_train.json"
    bind(raw_path, exclusions["sources_sha256"][str(raw_path)])
    raw = json.loads(raw_path.read_text())
    cp = bind(exclusions["candidates"]["path"], exclusions["candidates"]["sha256"])
    inventory = [json.loads(s) for s in cp.read_text().splitlines()]
    indices = [r["source_record_index"] for r in inventory]
    expected = [i for i, r in enumerate(raw) if norm(r["subject"]) and norm(r["subject"]) not in blocked]
    if indices != expected or any(norm(raw[i]["subject"]) != row["normalized_subject"] for i, row in zip(indices, inventory)):
        raise ValueError("v2 candidate inventory does not match source indices and exclusions")
    reference = json.loads(bind(ROOT / "manifests/reference.json").read_text())
    tr = reference["inputs"]["tokenizer.json"]
    tok_path = bind(tr["path"], tr["sha256"])
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(tok_path))
    for name in ("scripts/r1_d1c_candidates.py", "scripts/r1_d1_exclusions.py", "src/pccap/data/splits.py", "src/pccap/data/tokenize.py", "src/pccap/metrics/editing.py"):
        bind(ROOT / name)
    matcher = ExclusionMatcher(blocked)
    external.mkdir(parents=True, exist_ok=False)
    paths = {"ordered_candidates": external / "ordered_candidates.jsonl", "flagged_candidates": external / "flagged_candidates.jsonl",
        "clear_candidates": external / "clear_candidates.jsonl", "record_review": external / "record_review.jsonl"}
    counters = Counter(raw_records=len(raw), after_v2_exclusions=len(indices))
    exclusion_counts, flags_count = Counter(), Counter()
    seen_fact, seen_subject, prompt_answers = {}, {}, {}
    manifest_rows, chosen, clear_lengths = [], [], []
    handles = {k: p.open("x") for k, p in paths.items()}
    try:
        for i in indices:
            row = raw[i]
            detail = {"source_record_index": i, "source_record_sha256": digest(row), "subject_key": norm(row["subject"]),
                "field_sha256": {k: digest(row.get(k)) for k in ("subject", "src", "answers", "rephrase", "loc", "loc_ans")}}
            reasons = structural_reasons(row)
            if not reasons:
                counters["after_field_validation"] += 1
                item, reasons = map_item(i, row, tok)
                if not reasons:
                    counters["after_token_validation"] += 1
            if reasons:
                detail.update(status="rejected_structural", reasons=reasons)
                exclusion_counts.update(reasons)
            else:
                fk = (norm(row["src"]), norm(item["answer"]))
                sk = norm(row["subject"])
                if fk in seen_fact:
                    counters["duplicate_fact"] += 1
                    detail.update(status="duplicate_fact", representative_source_index=seen_fact[fk])
                else:
                    counters["after_fact_dedup"] += 1
                    seen_fact[fk] = i
                    if sk in seen_subject:
                        counters["duplicate_subject"] += 1
                        detail.update(status="duplicate_subject", representative_source_index=seen_subject[sk])
                    else:
                        seen_subject[sk] = i
                        matches = {k: matcher.matches(row[k]) for k in ("subject", "src", "rephrase", "loc")}
                        flags = [k + "_exclusion_mention" for k, v in matches.items() if v]
                        # Additional semantics/locality flags do not pretend to establish
                        # a correct paraphrase or unrelatedness from lexical tests alone.
                        subject_words = words(sk)
                        for k in ("src", "rephrase"):
                            tokens = words(row[k])
                            if subject_words and not any(tokens[j:j+len(subject_words)] == subject_words for j in range(len(tokens))):
                                flags.append(k + "_subject_not_literal")
                        if subject_words:
                            lt = words(row["loc"])
                            if any(lt[j:j+len(subject_words)] == subject_words for j in range(len(lt))):
                                flags.append("locality_mentions_edit_subject")
                        if norm(item["answer"]) == norm(row["loc_ans"]):
                            flags.append("locality_answer_equals_edit_answer")
                        prior_answers = prompt_answers.setdefault(norm(row["src"]), set())
                        if prior_answers and norm(item["answer"]) not in prior_answers:
                            flags.append("prompt_with_distinct_source_answers")
                        prior_answers.add(norm(item["answer"]))
                        flags = sorted(set(flags))
                        detail.update(status="flagged_review_required" if flags else "clear_pre_e2_candidate", flags=flags,
                            exclusion_matches={k:v for k,v in matches.items() if v},
                            excluded_canonical_keys={k:sorted({blocked[s]["canonical_subject_key"] for s in v}) for k,v in matches.items() if v})
                        item["review_flags"] = flags
                        item["source_record_sha256"] = detail["source_record_sha256"]
                        payload_hash = digest(item)
                        detail["mapped_item_sha256"] = payload_hash
                        counters["after_subject_dedup"] += 1
                        counters["flagged" if flags else "clear_pre_e2"] += 1
                        flags_count.update(flags)
                        if not flags:
                            clear_lengths.append((len(item["prompt_ids"]), item["answer_tokens"], item["paraphrase_token_lengths"][0], item["locality_token_lengths"][0]))
                        manifest_rows.append({"source_record_index": i, "source_record_sha256": detail["source_record_sha256"],
                            "mapped_item_sha256": payload_hash, "review_flags": flags})
                        chosen.append(sk)
                        line = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
                        handles["ordered_candidates"].write(line)
                        handles["flagged_candidates" if flags else "clear_candidates"].write(line)
            handles["record_review"].write(json.dumps(detail, ensure_ascii=False, separators=(",", ":")) + "\n")
    finally:
        for h in handles.values():
            h.close()
    assert len(chosen) == len(set(chosen)) == counters["after_subject_dedup"]
    assert counters["clear_pre_e2"] + counters["flagged"] == counters["after_subject_dedup"]
    for p, h in inputs.items():
        if sha(Path(p)) != h:
            raise RuntimeError("input changed during candidate review: " + p)
    token_summary = {name: {"sum": sum(v[k] for v in clear_lengths), "mean": sum(v[k] for v in clear_lengths)/len(clear_lengths) if clear_lengths else None,
        "max": max((v[k] for v in clear_lengths), default=None)} for k, name in enumerate(("prompt", "answer_including_newline", "rephrase", "locality"))}
    summary = {"task": "R1-D1c", "schema_version": 1, "status": "candidate_review_only_no_teacher_or_draw", "sources_sha256": inputs,
        "counts": dict(counters), "structural_rejection_reasons_overlapping": dict(exclusion_counts), "review_flag_counts_overlapping": dict(flags_count),
        "requested_final_capacity": {"realizations": 3, "unique_subjects_per_realization": 1000, "total": 3000,
            "clear_text_capacity_at_least_3000": counters["clear_pre_e2"] >= 3000,
            "minimum_E2_retention_fraction_of_clear_candidates": 3000/counters["clear_pre_e2"] if counters["clear_pre_e2"] else None,
            "teacher_eligible_count": None, "final_realizations_assigned": 0},
        "clear_candidate_token_summary": token_summary,
        "artifacts": {k: {"path": str(p), "sha256": sha(p)} for k, p in paths.items()},
        "policies": {"ordering": "ascending immutable source index; deterministic first structurally valid fact/subject representative, not a random draw",
            "fact_dedup": "NFKC/casefold/whitespace-normalized prompt plus canonical answer; operational fact identity, not a relation/entity graph",
            "subject_dedup": "same primary normalized subject keys as exclusions v2; known v2 aliases already excluded",
            "flags": "any word-boundary/punctuation-fold exclusion mention in subject, prompt, rephrase or locality is flagged; flags are conservative, not proven entity identity",
            "rephrase": "one source paraphrase for zsRE evaluation; nonempty, distinct text/tokens, within context; semantic equivalence NOT certified",
            "locality": "source loc/loc_ans required; loc must differ from edit/rephrase; source nq prefix preserved; no new teacher labels manufactured",
            "E2": "keep complete BP-teacher greedy answers outside source answer aliases; run only after review by owner, not here",
            "access": "all payloads are pre-final source candidates reviewed only for data preparation; no pilot/training use authorized by this artifact"},
        "limitations": ["Lexical clear does not prove complete canonical entity disjointness or correct rephrase semantics.",
            "Flagged candidates need a documented disposition before teacher filtering/final use.",
            "First representative per subject may fail E.2 even if an alternate row would pass; no outcome-based substitution is authorized.",
            "Candidate cross-realization contextual entity overlap must be checked after E.2; distinct primary subjects alone do not establish independent contexts.",
            "If later training uses any candidate, register that exposure and regenerate candidates before a fresh draw."],
        "gpu_seconds": 0, "sealed_payloads_opened": 0}
    write_json(report_path, summary)
    manifest = {**summary, "name": "zsre_fresh_candidates_v1", "version": 1,
        "records": manifest_rows, "records_scope": "one fact and subject representative after text/token checks, including explicitly flagged rows",
        "per_record_hashes": "source canonical JSON and mapped item canonical JSON; complete field hashes/statuses in record_review artifact"}
    write_json(output, manifest)
    print(json.dumps({"manifest": str(output), "counts": summary["counts"], "capacity": summary["requested_final_capacity"], "flags": dict(flags_count)}, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--assets-output", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()
    review(a.output.resolve(), a.assets_output.resolve(), a.report.resolve())


if __name__ == "__main__":
    main()
