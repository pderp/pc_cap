"""CPU-only, outcome-independent review of an exhaustive candidate register.

Entity IDs describe the bound name-equivalence policy, not inferred Wikidata IDs.
Answer aliases and object identifiers never become subject aliases.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict

DATASETS = ("zsre", "counterfact", "mquake")
POLICY = "DEC-048-option-C;DEC-042-CounterFact;zsRE-priority"
QUERY_WAIVERS = frozenset(
    {
        "mquake_training_locality_query_subject",
        "mquake_development_locality_query_subject",
        "mquake_development_unrelated_query_subject",
    }
)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def words(text):
    return tuple(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def presented_texts(row):
    """Explicit support/query fields, including constructed endpoint variants."""
    texts = [
        row.get(k)
        for k in (
            "prompt",
            "answer",
            "edit_prompt",
            "edit_answer",
            "neighbour_prompt",
            "new_answer",
        )
    ]
    texts += row.get("paraphrases", []) + row.get("questions", [])
    texts += [v.get("answer") for v in row.get("versions", [])]
    return [text for text in texts if isinstance(text, str) and text]


class Entities:
    """Transitive verified aliases plus conservative punctuation equivalence."""

    def __init__(self, aliases):
        self.parent = {}
        for left, right in aliases.items():
            a, b = self.key(left), self.key(right)
            if not a or not b:
                raise ValueError("empty verified subject alias")
            a, b = self.find(a), self.find(b)
            self.parent[max(a, b)] = min(a, b)

    @staticmethod
    def key(text):
        return " ".join(words(text))

    def find(self, key):
        while key in self.parent and self.parent[key] != key:
            key = self.parent[key]
        return key

    def identity(self, text):
        key = self.find(self.key(text))
        return "name-v1:" + digest(key), key


class Matcher:
    """Token trie: complete bounded-word name matches, including verified aliases."""

    def __init__(self, names, entities):
        self.trie = {}
        for name in names:
            key = words(name)
            if not key:
                continue
            node = self.trie
            for word in key:
                node = node.setdefault(word, {})
            node.setdefault(None, set()).add(entities.identity(name)[0])

    def matches(self, text):
        tokens, found = words(text), set()
        for start in range(len(tokens)):
            node = self.trie
            for token in tokens[start:]:
                node = node.get(token)
                if node is None:
                    break
                found.update(node.get(None, ()))
        return found


def effective_reason(dataset, reason):
    if dataset == "mquake" and reason in QUERY_WAIVERS:
        return False
    return not (dataset == "counterfact" and reason == "old_eligible:counterfact")


def event_blocks(dataset, event, identity, entities):
    if dataset == "mquake" and event["reason"] in QUERY_WAIVERS:
        subjects = event.get("waiver_subjects", [event.get("subject", "")])
        # Only the known subject of a true-fact query receives the waiver.
        # Incidental entities elsewhere in its context retain context quarantine.
        return identity not in {entities.identity(s)[0] for s in subjects if s}
    return effective_reason(dataset, event["reason"])


def token_review(row, tokenizer, limits):
    """Retokenize source IDs and every paraphrase using the final tokenizer."""
    from pccap.data.tokenize import tokenize_pair

    failures = []
    try:
        pair = tokenize_pair(tokenizer, row["prompt"], row["answer"])
        if pair.excluded:
            failures.append(pair.reason)
        if pair.prompt_ids.tolist() != row.get("prompt_ids"):
            failures.append("prepared_prompt_ids_differ")
        if pair.answer_ids.tolist() != row.get("answer_ids"):
            failures.append("prepared_answer_ids_differ")
        prompts = [pair.prompt_ids.tolist()]
        if not row.get("paraphrases"):
            failures.append("no_paraphrase")
        prompts.extend(tokenizer.encode(p).tolist() for p in row.get("paraphrases", []))
        all_ids = pair.answer_ids.tolist() + [t for ids in prompts for t in ids]
        if any(type(t) is not int or not 0 <= t < limits["vocabulary"] for t in all_ids):
            failures.append("token_out_of_vocabulary")
        if any(not ids or len(ids) + 32 > limits["max_context"] for ids in prompts):
            failures.append("prompt_or_paraphrase_context_limit")
        return {
            "pass": not failures,
            "reasons": sorted(set(failures)),
            "prompt_lengths": [len(p) for p in prompts],
            "answer_length": len(pair.answer_ids),
        }
    except (ValueError, TypeError, KeyError) as error:
        return {"pass": False, "reasons": ["tokenization_error:" + str(error)]}


def review(register, sources, inputs, tokenizer, limits, *, target=6075):
    if register.get("schema_version") != 6 or type(target) is not int or target < 1:
        raise ValueError("register v6 and positive bounded policy target required")
    aliases = inputs["verified_alias_pairs"]
    entities = Entities(aliases)
    names = [r["canonical_subject"] for ds in DATASETS for r in register["candidates"][ds]]
    matcher = Matcher(names + list(aliases) + list(aliases.values()), entities)
    by_entity = defaultdict(list)
    for index, event in enumerate(inputs["events"]):
        matched = set()
        if event.get("subject"):
            matched.add(entities.identity(event["subject"])[0])
        if event.get("text"):
            matched.update(matcher.matches(event["text"]))
        for identity in matched:
            by_entity[identity].append(index)
    dispositions, evidence, counts, claimed = [], [], {}, set()
    for ds in DATASETS:
        source = {r["item_id"]: r for r in sources[ds]}
        expected = {m["item_id"] for m in register["candidates"][ds]}
        if len(source) != len(sources[ds]) or set(source) != expected:
            raise ValueError("source/register coverage mismatch: " + ds)
        cleared, reasons_count, reviewed = set(), Counter(), 0
        for meta in register["candidates"][ds]:
            row = source[meta["item_id"]]
            if (
                row["dataset"] != ds
                or digest(row) != meta["payload_sha256"]
                or row["source_record_sha256"] != meta["source_record_sha256"]
            ):
                raise ValueError("candidate source identity mismatch: " + meta["item_id"])
            entity_id, entity_key = entities.identity(meta["canonical_subject"])
            disp = {
                "dataset": ds,
                "item_id": meta["item_id"],
                "canonical_subject": meta["canonical_subject"],
                "payload_sha256": meta["payload_sha256"],
                "entity_id": entity_id,
                "decision": "exclude",
                "reasons": [],
                "alias_clear": None,
                "context_clear": None,
                "exposure_clear": None,
                "teacher_pass": None,
                "tokens_pass": None,
                "preteacher_eligible": False,
                "roles": [],
            }
            detail = {"dataset": ds, "item_id": meta["item_id"], "entity_key": entity_key}
            if len(cleared) >= target:
                disp["reasons"] = ["not_reviewed_bounded_policy"]
            else:
                reviewed += 1
                matches = by_entity.get(entity_id, [])
                blocked = [
                    i for i in matches if event_blocks(ds, inputs["events"][i], entity_id, entities)
                ]
                alias_blocked = [
                    i
                    for i in blocked
                    if inputs["events"][i].get("subject")
                    and entities.identity(inputs["events"][i]["subject"])[0] == entity_id
                ]
                context_blocked = [i for i in blocked if inputs["events"][i].get("text")]
                tokens = token_review(row, tokenizer, limits)
                disp.update(
                    alias_clear=bool(entity_key) and not alias_blocked,
                    exposure_clear=not blocked,
                    context_clear=not context_blocked and tokens["pass"],
                )
                detail.update(
                    blocking_event_indices=blocked,
                    waived_event_indices=[i for i in matches if i not in blocked],
                    token_context_check=tokens,
                )
                reasons = []
                if not entity_key:
                    reasons.append("empty_subject_identity")
                if alias_blocked:
                    reasons.append("exposed_subject_alias")
                if context_blocked:
                    reasons.append("exposed_context_name_match")
                if not tokens["pass"]:
                    reasons.append("token_context_check_failed")
                if entity_id in claimed:
                    reasons.append("cross_dataset_entity_collision")
                if not reasons:
                    cleared.add(entity_id)
                    disp["preteacher_eligible"] = True
                    reasons = ["pending_final_teacher_token_and_role_review"]
                disp["reasons"] = reasons
            reasons_count.update(disp["reasons"])
            dispositions.append(disp)
            evidence.append(detail)
        claimed.update(cleared)
        counts[ds] = {
            "candidate_items": len(expected),
            "reviewed_items": reviewed,
            "preteacher_items": sum(
                d["preteacher_eligible"] for d in dispositions if d["dataset"] == ds
            ),
            "preteacher_subjects": len(cleared),
            "demand_subjects": 4050,
            "preteacher_headroom": len(cleared) - 4050,
            "reasons": dict(reasons_count),
        }
    return {
        "schema_version": 1,
        "mode": "unsealed_partial_clearance_evidence",
        "policy": POLICY,
        "alias_review_complete": True,
        "context_review_complete": True,
        "cumulative_exposure_current": True,
        "cross_dataset_disjoint": True,
        "teacher_token_review_complete": False,
        "role_compatibility_complete": False,
        "model_limits": limits,
        "bounded_policy": {
            "target_unique_subjects": target,
            "order": "register order, datasets zsre/counterfact/mquake; stop before next row after target",
            "unreviewed": "exclude:not_reviewed_bounded_policy",
            "selection_uses_teacher_outputs": False,
        },
        "entity_policy": "NFKC/casefold, punctuation-to-word boundaries, transitive bound verified subject aliases; dataset-independent name-v1 hash",
        "limits": [
            "No external entity linking or unrecorded alias discovery; IDs denote name equivalence under this bound policy, not independently certified real-world identity.",
            "Punctuation/homonym context matches are quarantined conservatively; historical homonym releases do not extend to new contexts.",
            "Exposure scope is the bound repository snapshot and its declared unsealed resources; later activity requires a supplement.",
            "Teacher, final token certification and endpoint role compatibility remain unresolved; this resource cannot pass D9 clearance.",
        ],
        "dispositions": dispositions,
        "counts": counts,
    }, evidence
