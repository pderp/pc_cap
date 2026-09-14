"""CPU-only R1-D1 exclusion inventory; no teacher eligibility, sampling or sealing.

Outputs are exclusive-create. Candidate payload contains source indices and subjects,
not answer labels. Lexical mention matches are conservative exclusions, not entity IDs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"


def norm(s):
    return " ".join(unicodedata.normalize("NFKC", s).casefold().split())


def words(s):
    return tuple(re.findall(r"\w+", norm(s), flags=re.UNICODE))


def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def write_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def inventory(output, external):
    if output.exists() or external.exists():
        raise ValueError("outputs must be new")
    if not output.resolve().is_relative_to(ROOT) or not external.resolve().is_relative_to(ASSETS):
        raise ValueError("manifest belongs inside pc_cap; data belongs under assets")
    sources, excluded, by_id, texts = {}, defaultdict(set), {}, []

    def load(p, jsonl=False):
        sources[str(p)] = sha(p)
        return [json.loads(s) for s in p.read_text().splitlines() if s] if jsonl else json.loads(p.read_text())

    def add(s, reason):
        if norm(s):
            excluded[norm(s)].add(reason)

    def scan_texts(obj, origin, field=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                scan_texts(v, origin + "/" + k, k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                scan_texts(v, origin + "/" + str(i), field)
        elif isinstance(obj, str) and ("prompt" in field or "paraphrase" in field or field in ("rephrase", "loc")):
            if obj.strip():
                texts.append((origin, obj))

    pools = load(ROOT / "manifests/dev/pools.json")
    datasets = load(ROOT / "manifests/datasets.json")
    steps = []
    for dataset in ("zsre", "counterfact"):
        p = ASSETS / f"data/prepared/editing/{dataset}_eligible.jsonl"
        rows = load(p, True)
        if sources[str(p)] != pools[dataset]["confirm_pool_sha256"]:
            raise ValueError("old eligible source hash mismatch")
        for row in rows:
            add(row["subject"], "old_eligible:" + dataset)
            by_id[row["item_id"]] = row["subject"]
    steps.append(("all_old_eligible_pools", set(excluded)))
    for name in ("zsre_dev", "counterfact_dev", "s0_sample"):
        obj = load(ROOT / f"manifests/dev/{name}.json")
        for row in obj["items"]:
            add(row["subject"], "v0:" + name)
            by_id[row["item_id"]] = row["subject"]
        scan_texts(obj["items"], name)
    steps.append(("plus_v0_development_and_s0", set(excluded)))
    s7 = load(ROOT / "manifests/dev/s7_pairs.json")
    s7_counts = {}
    for dataset in ("zsre", "counterfact"):
        pairs = s7["pairs"][dataset]
        subjects = set()
        for pair in pairs:
            for which in ("a", "b"):
                row = pair[which]
                add(row["subject"], "s7_all_candidates:" + dataset)
                by_id[row["item_id"]] = row["subject"]
                subjects.add(norm(row["subject"]))
        s7_counts[dataset] = len(subjects)
    assert s7_counts == {"zsre": 496, "counterfact": 141}, s7_counts
    scan_texts(s7["pairs"], "s7_all_candidates")
    steps.append(("plus_all_s7_candidates", set(excluded)))
    challenges = load(ROOT / "manifests/dev/challenges.json")
    unresolved_ids, challenge_counts = [], {}
    for name in ("near_neighbour", "composition", "temporal_correction"):
        rows = challenges[name]["items"]
        challenge_counts[name] = {"listed_rows": len(rows), "source_availability_n": challenges[name]["n"]}
        for i, row in enumerate(rows):
            origin = f"challenge:{name}:{i}"
            if "subject" in row:
                add(row["subject"], origin)
            for k in ("edit_item_id", "first_item_id", "second_item_id"):
                if k in row:
                    if row[k] in by_id:
                        add(by_id[row[k]], origin + ":" + k)
                    else:
                        unresolved_ids.append({"source": origin, "field": k, "item_id": row[k]})
            if name == "composition":
                add(row["o1"], origin + ":intermediate_entity")
        scan_texts(rows, "challenge:" + name)
    steps.append(("plus_challenge_explicit_subjects", set(excluded)))
    partition = load(ROOT / "manifests/revision_v1/episode_partitions.json")
    for s in partition["natural"]["emitted_source_subjects"]:
        add(s, "revision:R1-20b:emitted")
    samples = load(ROOT / "logs/r1_codex_20260913/episodes_v2/sample_episodes.json")
    sample_ids = set()

    def collect_source_ids(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "source_items":
                    for token in re.findall(r"(?:cf-\d+|zsre-(?:eval-|train-)?\d+)", str(v)):
                        sample_ids.add(token)
                collect_source_ids(v)
        elif isinstance(obj, list):
            for v in obj:
                collect_source_ids(v)

    collect_source_ids(samples)
    for item_id in sorted(sample_ids):
        if item_id in by_id:
            add(by_id[item_id], "revision:episodes_v2:source_items")
        else:
            unresolved_ids.append({"source": "episodes_v2", "item_id": item_id})
    scan_texts(samples, "revision:episodes_v2")
    steps.append(("plus_revision_emitted_subjects", set(excluded)))
    # Full raw JSON is decoded for stable record indices and text hashes. Answers
    # never participate in inventory, lexical matching, or candidate selection.
    raw_path = ASSETS / "data/raw/zsre/zsre_mend_train.json"
    raw = load(raw_path)
    if sources[str(raw_path)] != datasets["zsre"]["files"]["data/raw/zsre/zsre_mend_train.json"]:
        raise ValueError("MEND train source hash mismatch")
    raw_subjects = [norm(r["subject"]) for r in raw]
    dictionary = defaultdict(set)
    for s in set(raw_subjects) | set(excluded) | {norm(s) for s in by_id.values()}:
        if words(s):
            dictionary[words(s)].add(s)
    lengths = sorted({len(k) for k in dictionary})
    external.mkdir(parents=True, exist_ok=False)
    mentions_path = external / "exposed_text_entity_review.jsonl"
    match_fields, no_match_fields, ambiguous_fields = 0, 0, 0
    with mentions_path.open("x") as f:
        for origin, txt in texts:
            tokens = words(txt)
            found = set()
            ambiguous = False
            for n in lengths:
                if n > len(tokens):
                    break
                for i in range(len(tokens) - n + 1):
                    matches = dictionary.get(tokens[i:i+n], ())
                    found.update(matches)
                    ambiguous |= len(matches) > 1
            for s in found:
                add(s, "exposed_text_lexical_candidate:" + origin)
            match_fields += bool(found)
            no_match_fields += not found
            ambiguous_fields += ambiguous
            f.write(json.dumps({"source": origin, "text": txt, "normalized_subject_candidates": sorted(found),
                "entity_resolution": "UNRESOLVED: dictionary matches do not identify all mentions or establish entity identity",
                "ambiguous_punctuation_fold": ambiguous}, ensure_ascii=False) + "\n")
    steps.append(("plus_conservative_exposed_text_matches", set(excluded)))
    # Propagate punctuation-only aliases conservatively across every exclusion.
    blocked_words = {words(s) for s in excluded if words(s)}
    for s in set(raw_subjects):
        if words(s) in blocked_words and s not in excluded:
            add(s, "punctuation_fold_alias_candidate:conservative_not_verified")
    steps.append(("plus_conservative_punctuation_aliases", set(excluded)))
    counts = []
    for name, blocked in steps:
        remain = set(raw_subjects) - blocked - {""}
        counts.append({"stage": name, "excluded_subjects_all_sources": len(blocked),
            "candidate_raw_records": sum(s in remain for s in raw_subjects), "candidate_unique_subjects": len(remain)})
    candidates_path = external / "mend_candidate_subjects.jsonl"
    with candidates_path.open("x") as f:
        for i, (row, s) in enumerate(zip(raw, raw_subjects)):
            if s and s not in excluded:
                f.write(json.dumps({"source_record_index": i, "subject": row["subject"], "normalized_subject": s,
                    "entity_review_required": True,
                    "rephrase_sha256": hashlib.sha256(row.get("rephrase", "").encode()).hexdigest(),
                    "locality_text_sha256": hashlib.sha256(row.get("loc", "").encode()).hexdigest()}, ensure_ascii=False) + "\n")
    for path, expected in sources.items():
        if sha(Path(path)) != expected:
            raise RuntimeError(f"source changed during audit: {path}")
    result = {"name": "revision_v1_exclusions", "version": "r1-d1-v1", "status": "candidate_inventory_only_not_sealed",
        "normalization": "Unicode NFKC, casefold, collapse whitespace; punctuation retained in primary subject key",
        "sources_sha256": sources, "raw_mend_records": len(raw), "raw_mend_unique_subjects": len(set(raw_subjects)),
        "raw_mend_empty_subjects": raw_subjects.count(""), "filters": counts, "s7_candidate_subjects": s7_counts,
        "challenges": challenge_counts, "unresolved_source_ids": unresolved_ids,
        "revision_emitted_subjects_R1_20b": len(partition["natural"]["emitted_source_subjects"]),
        "revision_episodes_v2_source_ids": len(sample_ids),
        "exclusions": [{"normalized_subject": s, "reasons": sorted(reasons)} for s, reasons in sorted(excluded.items())],
        "exposed_text_review": {"fields": len(texts), "with_dictionary_match": match_fields, "without_dictionary_match": no_match_fields,
            "ambiguous_punctuation_fold_fields": ambiguous_fields, "all_fields_require_canonical_entity_review": True,
            "path": str(mentions_path), "sha256": sha(mentions_path)},
        "candidates": {"path": str(candidates_path), "sha256": sha(candidates_path), **counts[-1]},
        "entity_policy": ["Lexical matches and punctuation folds are conservative possible aliases; false positives may reduce capacity.",
            "No canonical entity linker or verified alias graph is available. Nicknames, translations, pronouns and unstated entities remain unresolved.",
            "Answer aliases are answer strings, not subject aliases, and were not used as entity equivalences.",
            "Every exposed prompt/paraphrase/locality field is listed for review, including fields with no dictionary match.",
            "Candidate paraphrase/locality text is indexed by immutable source row and hash; every candidate needs entity review before sealing.",
            "All old development subjects are excluded, conservatively covering natural pilots drawn from those pools even if episode logs are incomplete.",
            "Synthetic contexts are a separate namespace: all v1 contexts are development-exposed; see episode_partitions.json."],
        "next_gates": ["Resolve entity/alias and contextual mention overlap; version exclusions again if needed.",
            "Add any later development source exposure, rerun counts, and approve/freeze the register.",
            "Owner runs tokenization/E.2 teacher filtering on GPU; then deduplicate facts and assess independent realization capacity.",
            "Only then draw and seal new confirmation realizations; current counts are not eligible-fact counts."],
        "gpu_seconds": 0, "sealed_realization_payloads_opened": 0}
    write_json(output, result)
    print(json.dumps({"manifest": str(output), "sha256": sha(output), "filters": counts,
        "unresolved_ids": len(unresolved_ids), "text_review_fields": len(texts)}, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--assets-output", type=Path, required=True)
    a = ap.parse_args()
    inventory(a.output.resolve(), a.assets_output.resolve())


if __name__ == "__main__":
    main()
