"""R1-D1b: reproducible, text-only v2 exclusion decisions; exclusive outputs.

Source-subject keys are operational identities, not a knowledge-graph linker.
Ambiguous mentions remain explicitly quarantined instead of being merged.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from r1_d1_exclusions import ASSETS, ROOT, norm, sha, words, write_json

# Reviewed against every v1 occurrence AND the candidate's MEND identity question.
# A newly encountered occurrence invalidates this release and causes quarantine.
RELEASE = {
    "this time...": "album versus ordinary temporal phrase",
    "dumped": "TV programme versus substring of Jessie episode Punch Dumped Love",
    "ball": "BALL software versus cricket/cue ball",
    "the following": "TV series versus question determiner",
    "around the sun": "album versus orbital motion",
    "endurance": "named vessel versus endurance exercise",
    "they live": "film versus ordinary sentence about living together",
    "a night in": "episode versus distinct full title A Night in Heaven",
    "whos": "radio station versus misspelling of who is",
    "what work is": "book versus interrogative question stem",
    "cold turkey": "recording versus origin of ordinary idiom",
    "time was": "TV programme versus interrogative time phrase",
    "cares": "river versus ordinary verb",
    "the bill": "TV series versus Bill of Rights",
    "the dollar": "recording versus currency/gold standard",
    "for men": "magazine versus clothing requirement",
    "in orange": "named work/place versus substring of Orange Is the New Black",
    "great scott!!": "recording versus exclamation",
    "brink!": "TV film versus PAM Brink Stadium",
    "i love": "recording versus distinct full title i hate u i love u",
    "live-in": "TV programme versus ordinary verb/preposition or different song title",
    "the returning": "film versus returning soldiers",
    "the league": "TV series versus sporting leagues",
}
VERIFIED_ALIASES = {
    "claude joseph dorat": "claude-joseph dorat",
    "desi arnaz jr.": "desi arnaz, jr.",
}


def context_only(reasons):
    return all(r.startswith(("exposed_text_lexical_candidate:", "punctuation_fold_alias_candidate:")) for r in reasons)


def collect_texts(obj, origin, field=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from collect_texts(v, origin + "/" + k, k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from collect_texts(v, origin + "/" + str(i), field)
    elif isinstance(obj, str) and ("prompt" in field or "paraphrase" in field or field in ("rephrase", "loc")) and obj.strip():
        yield origin, obj


def build(output, external, review_output):
    for p in (output, review_output):
        if p.exists() or not p.resolve().is_relative_to(ROOT):
            raise ValueError("repository outputs must be new files inside pc_cap")
    if external.exists() or not external.resolve().is_relative_to(ASSETS):
        raise ValueError("data output must be a new directory under assets")
    inputs = {}
    def read(p, lines=False):
        inputs[str(p)] = sha(p)
        return [json.loads(x) for x in p.read_text().splitlines()] if lines else json.loads(p.read_text())

    old = read(ROOT / "manifests/revision_v1/exclusions.json")
    review = read(Path(old["exposed_text_review"]["path"]), True)
    pool = read(ROOT / "manifests/revision_v1/train_pool_counterfact_v1.json")
    raw_path = ASSETS / "data/raw/zsre/zsre_mend_train.json"
    raw = read(raw_path)
    if inputs[str(raw_path)] != old["sources_sha256"][str(raw_path)]:
        raise ValueError("MEND identity changed")
    subjects = [norm(r["subject"]) for r in raw]
    identities = defaultdict(list)
    for i, r in enumerate(raw):
        identities[norm(r["subject"])].append({"source_record_index": i, "identity_question": r["src"]})
    excluded = {r["normalized_subject"]: set(r["reasons"]) for r in old["exclusions"]}
    before = set(excluded)
    contextual = {s for s, reasons in excluded.items() if context_only(reasons)}
    contexts = defaultdict(list)
    for row in review:
        for s in row["normalized_subject_candidates"]:
            contexts[s].append({"source": row["source"], "text": row["text"]})
    drawn = set(pool["drawn_subjects_normalized"])
    if len(drawn) != 3000 or any(norm(s) != s for s in drawn):
        raise ValueError("DEC-037 must contain exactly 3000 normalized subjects")
    for s in drawn:
        excluded.setdefault(s, set()).add("train_pool_counterfact_v1")

    dictionary = defaultdict(set)
    for s in set(subjects) | set(excluded):
        if words(s):
            dictionary[words(s)].add(s)
    lengths = sorted({len(k) for k in dictionary})
    new_contexts = defaultdict(list)
    new_review = []
    for origin, txt in collect_texts(pool["items"], "train_pool_counterfact_v1"):
        tokens = words(txt)
        found = set()
        for n in lengths:
            if n > len(tokens):
                break
            for i in range(len(tokens) - n + 1):
                found.update(dictionary.get(tokens[i:i+n], ()))
        new_review.append({"source": origin, "text": txt, "normalized_subject_candidates": sorted(found)})
        for s in found:
            new_contexts[s].append({"source": origin, "text": txt})
            excluded.setdefault(s, set()).add("context_quarantine:train_pool_counterfact_v1")

    decisions = []
    released = []
    for s in sorted(contextual | (set(new_contexts) - before)):
        known_texts = {norm(x["text"]) for x in contexts[s]}
        unseen = [x for x in new_contexts[s] if norm(x["text"]) not in known_texts]
        if s in RELEASE and s not in drawn and not unseen:
            decision, reason = "release_verified_identity_mismatch", RELEASE[s]
            del excluded[s]
            released.append(s)
        elif s in VERIFIED_ALIASES:
            decision, reason = "exclude_verified_name_alias", "same personal name, punctuation-only local variant"
            excluded[s].add("verified_alias:" + VERIFIED_ALIASES[s])
        else:
            decision = "exclude_conservative_context_quarantine"
            reason = "literal or punctuation-fold mention; identity not proven equivalent; retain exclusion without merging entities"
            if s in RELEASE and unseen:
                reason += "; reviewed v1 mismatch does not authorize release of new contexts"
            excluded[s].add("v2_decision:conservative_context_quarantine")
        decisions.append({"subject": s, "canonical_subject_key": VERIFIED_ALIASES.get(s, s),
            "decision": decision, "reason": reason, "identity_questions": identities[s][:3],
            "v1_contexts": contexts[s], "new_contexts": new_contexts[s],
            "v1_reasons": next((r["reasons"] for r in old["exclusions"] if r["normalized_subject"] == s), [])})
    for alias, canonical in VERIFIED_ALIASES.items():
        if alias not in excluded or canonical not in excluded:
            raise ValueError("verified alias endpoints must remain excluded")
    # Do not recursively propagate arbitrary punctuation aliases: Dawn! (film)
    # and Dawn are a concrete counterexample to canonical equivalence by folding.
    for s in drawn:
        assert "train_pool_counterfact_v1" in excluded[s]
    after = set(excluded)
    def count(blocked):
        remaining = set(subjects) - blocked - {""}
        return {"raw_records": sum(s in remaining for s in subjects), "unique_subjects": len(remaining)}
    external.mkdir(parents=True, exist_ok=False)
    paths = {"candidate_subjects": external / "mend_candidate_subjects.jsonl",
             "new_context_review": external / "train_pool_context_review.jsonl",
             "entity_decisions": external / "entity_decisions.jsonl"}
    with paths["candidate_subjects"].open("x") as f:
        for i, r in enumerate(raw):
            if subjects[i] and subjects[i] not in after:
                f.write(json.dumps({"source_record_index": i, "subject": r["subject"],
                    "normalized_subject": subjects[i], "preseal_entity_review_required": True}, ensure_ascii=False) + "\n")
    for key, records in (("new_context_review", new_review), ("entity_decisions", decisions)):
        with paths[key].open("x") as f:
            for row in records:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = {"schema_version": 1, "version": "r1-d1b-v2", "sources_sha256": inputs,
        "bounded_review": {"v1_context_only_subjects": len(contextual),
            "v1_classes_with_decisions": sum(d["subject"] in contextual for d in decisions),
            "verified_v1_lexical_overexclusion_lower_bound": len(RELEASE),
            "released_after_new_exposure_check": len(released), "released_subjects": released,
            "verified_alias_pairs": VERIFIED_ALIASES,
            "new_explicit_subjects_missing_v1": len(drawn - before),
            "required_reason_additions": 3000,
            "new_context_subjects_missing_v1_conservative_underexclusion_count": len(set(new_contexts) - before),
            "unknown_global_underexclusion_count": None,
            "decision_counts": dict(Counter(d["decision"] for d in decisions))},
        "candidate_counts": {"v1": count(before), "after_releases_only": count(before-set(released)),
            "after_explicit_3000_only": count(before|drawn), "v2": count(after)},
        "exclusion_count_v1": len(before), "exclusion_count_v2": len(after),
        "added_exclusion_subjects": sorted(after-before), "released_exclusion_subjects": sorted(before-after),
        "data_artifacts": {k: {"path": str(p), "sha256": sha(p)} for k, p in paths.items()},
        "limitations": ["Decided conservative exclusion policy, not globally certified canonical entity resolution.",
            "Quarantined homonyms/substrings are NOT asserted to be the same entity and may over-exclude.",
            "Missed nicknames, diacritics, translations, pronouns and unlisted entities are not measured; under-exclusion is not zero.",
            "23 v1 identity mismatches were text-reviewed; any new distinct exposure forces quarantine again.",
            "Candidate-level source/alias review and eligibility remain required before final sealing."],
        "gpu_seconds": 0, "sealed_realization_payloads_opened": 0}
    result = {"name": "revision_v1_exclusions", "version": "r1-d1b-v2", "status": "decided_policy_candidate_not_final_sealed",
        "normalization": old["normalization"], "sources_sha256": inputs,
        "supersedes_sha256": sha(ROOT / "manifests/revision_v1/exclusions.json"),
        "canonicalization": "verified local alias pairs only; all other source-subject identities remain separate",
        "verified_alias_pairs": VERIFIED_ALIASES,
        "exclusions": [{"normalized_subject": s, "canonical_subject_key": VERIFIED_ALIASES.get(s, s),
            "reasons": sorted(rs)} for s, rs in sorted(excluded.items())],
        "candidates": {**report["candidate_counts"]["v2"], **report["data_artifacts"]["candidate_subjects"]},
        "review_report": str(review_output), "review_counts": report["bounded_review"],
        "freeze_scope": "immutable v2 text-review policy proposal; lead must approve its residual conservative/unknown-entity risk",
        "final_sealing_ready": False, "next_gates": ["lead acceptance of exclusion policy", "candidate-level alias/context review",
            "GPU teacher eligibility and unique-fact capacity", "independent realization draw and seal"],
        "gpu_seconds": 0, "sealed_realization_payloads_opened": 0}
    for p, digest in inputs.items():
        if sha(Path(p)) != digest:
            raise RuntimeError("input changed during review: " + p)
    write_json(review_output, report)
    write_json(output, result)
    print(json.dumps({"manifest": str(output), **report["bounded_review"], "candidate_counts": report["candidate_counts"]}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--assets-output", type=Path, required=True)
    ap.add_argument("--review-output", type=Path, required=True)
    a = ap.parse_args()
    build(a.output.resolve(), a.assets_output.resolve(), a.review_output.resolve())
