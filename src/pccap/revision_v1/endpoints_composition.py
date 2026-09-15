"""R1-60: direct MQuAKE composition on isolated dependency-edit clones.

This module performs no sampling or filesystem reads. Query labels are scoring-only.
Final selection depends solely on predeclared edit membership, never on outcomes.
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter

import numpy as np

from pccap.contracts import EditItem
from pccap.data.decode import score_generation
from pccap.data.tokenize import tokenize_pair
from pccap.metrics.editing import normalize_answer
from pccap.revision_v1.endpoints import (
    EndpointEvaluator,
    EndpointResourceFailure,
    EndpointUnavailable,
    row_hash,
)


def dependency_ids(case):
    deps = case.get("dependencies")
    if not isinstance(deps, list) or not deps:
        raise EndpointUnavailable("missing_dependencies")
    ids = [d.get("item_id") for d in deps]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise EndpointUnavailable("invalid_or_duplicate_dependencies")
    return ids


def structural_reason(case):
    if case.get("verified_source") != "MQuAKE":
        return "missing_direct_source_verification"
    if case.get("all_rewrite_dependencies_available") is not True:
        return "unavailable_or_conflicting_source_dependencies"
    try:
        dependency_ids(case)
    except EndpointUnavailable as e:
        return str(e)
    if any(d.get("status") != "available_source_item" for d in case["dependencies"]):
        return "unavailable_or_conflicting_source_dependencies"
    queries = case.get("questions")
    if (
        not isinstance(queries, list)
        or len(queries) != 3
        or any(not isinstance(q, str) or not q.strip() for q in queries)
    ):
        return "three_nonempty_source_paraphrases_required"
    return None


def as_edit(row, tokenizer):
    if isinstance(row, EditItem):
        return row
    pair = tokenize_pair(tokenizer, row["prompt"], row["answer"])
    if pair.excluded:
        raise EndpointUnavailable("support_tokenization:" + pair.reason)
    if any(
        name in row and not np.array_equal(row[name], ids)
        for name, ids in (("prompt_ids", pair.prompt_ids), ("answer_ids", pair.answer_ids))
    ):
        raise EndpointUnavailable("support_token_identity_mismatch")
    iid = row["item_id"]
    return EditItem(
        item_id=iid,
        digest=hashlib.sha256(f"{iid}|{row['prompt']}|{row['answer']}".encode()).digest()[:16],
        prompt=row["prompt"],
        answer=row["answer"],
        aliases=list(row.get("aliases") or [row["answer"]]),
        paraphrases=list(row.get("paraphrases", [])),
        locality_prompts=list(row.get("locality_prompts", [])),
        prompt_ids=pair.prompt_ids,
        answer_ids=pair.answer_ids,
        dataset=row.get("dataset", "mquake"),
        fact_id=row.get("fact_id", iid),
        version=row.get("version", 1),
    )


class CompositionEvaluator(EndpointEvaluator):
    def __init__(self, learner, tokenizer, *, teaching_state=None, **kwargs):
        super().__init__(learner, tokenizer, **kwargs)
        self.teaching_state = None if teaching_state is None else teaching_state.clone()

    def _teach(self, item):
        out = self.learner.update_item(item)
        event = {
            "phase": "learning",
            "item_id": item.item_id,
            "code": out.code,
            "codes": list(out.codes),
            "returned_cost": out.cost.as_dict(),
        }
        self._events.append(event)
        if out.code == "resource_stop" or any(
            str(c).startswith("resource_failure:") for c in out.codes
        ):
            raise EndpointResourceFailure(";".join(out.codes) or out.code)
        # A behavioral threshold/acquisition miss remains a scored case.
        return event

    def evaluate_case(self, case, edit_items, *, edit_order=None):
        attempted = {"evaluable": False, "dependency_ids": [], "updates": []}

        def operation(_cid):
            reason = structural_reason(case)
            if reason:
                raise EndpointUnavailable(reason)
            ids = dependency_ids(case)
            missing = [i for i in ids if i not in edit_items]
            if missing:
                raise EndpointUnavailable("missing_dependency_items:" + ",".join(missing))
            by_id = {i: as_edit(edit_items[i], self.tok) for i in ids}
            for dep in case["dependencies"]:
                item = by_id[dep["item_id"]]
                required = dep.get("required_target_new", {}).get("str")
                if not isinstance(required, str) or normalize_answer(
                    item.answer
                ) != normalize_answer(required):
                    raise EndpointUnavailable("dependency_target_conflict")
                if item.item_id != dep["item_id"]:
                    raise EndpointUnavailable("dependency_item_identity_mismatch")
            ordered = ids
            if edit_order is not None:
                if len(edit_order) != len(set(edit_order)) or not set(ids) <= set(edit_order):
                    raise EndpointUnavailable("invalid_dependency_edit_order")
                ordered = [i for i in edit_order if i in by_id]
            old = case.get("answer_aliases") or [case.get("answer")]
            new = case.get("new_answer_aliases") or [case.get("new_answer")]
            if any(
                not isinstance(v, list)
                or not v
                or any(not isinstance(s, str) or not normalize_answer(s) for s in v)
                for v in (old, new)
            ):
                raise EndpointUnavailable("missing_answer_aliases")
            if set(map(normalize_answer, old)) & set(map(normalize_answer, new)):
                raise EndpointUnavailable("pre_and_post_aliases_overlap")
            limit = int(getattr(getattr(self.base, "cfg", None), "n_pos", 1024))
            if any(len(self.tok.encode(q)) + self.max_new > limit for q in case["questions"]):
                raise EndpointUnavailable("composition_query_exceeds_context")
            attempted.update(evaluable=True, dependency_ids=list(ordered))
            if self.teaching_state is not None:
                self.learner.import_state(self.teaching_state.clone())
            teaching_start = self.learner.state_hash()
            references = [self._read(self.base, q) for q in case["questions"]]
            for iid in ordered:
                attempted["updates"].append(self._teach(by_id[iid]))
            query_rows = []
            for index, (prompt, (off, ref)) in enumerate(
                zip(case["questions"], references, strict=True)
            ):
                on, trace = self._read(self.learner, prompt)
                exact = not on.truncated and bool(score_generation(on, new)["value"])
                old_again = not on.truncated and bool(score_generation(on, old)["value"])
                query_rows.append(
                    {
                        "paraphrase_index": index,
                        "post_edit_exact": exact,
                        "pre_edit_answer_reappeared": old_again,
                        "cap_off_pre_edit_exact": not off.truncated
                        and bool(score_generation(off, old)["value"]),
                        "cap_off_post_edit_exact": not off.truncated
                        and bool(score_generation(off, new)["value"]),
                        "reference": ref,
                        "cap_query": trace,
                    }
                )
            return {
                "composition_success": all(r["post_edit_exact"] for r in query_rows),
                "paraphrase_successes": sum(r["post_edit_exact"] for r in query_rows),
                "paraphrases_expected": 3,
                "queries": query_rows,
                "pre_edit_answer_reappeared": any(
                    r["pre_edit_answer_reappeared"] for r in query_rows
                ),
                "teaching_start_hash": teaching_start,
                "teaching_policy": "restore independent declared start state; teach all dependencies in declared stream order",
                "interpretation": "isolated direct-question dependency composition; not an in-stream retained-memory result",
            }

        result = self._case("composition_direct", case, operation)
        if result["status"] == "unreachable":
            result["status"] = "unavailable"
        result.update(
            composition_id=case.get(
                "composition_id", str(case.get("case_id", row_hash(case)[:24]))
            ),
            **attempted,
        )
        return result

    def evaluate(self, cases, edit_items, *, expected_n=None, edit_order=None):
        cases = list(cases)
        ids = [c.get("composition_id", str(c.get("case_id"))) for c in cases]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate composition case ID")
        if expected_n is None:
            expected_n = len(cases)
        if type(expected_n) is not int or expected_n < len(cases) or expected_n < 0:
            raise ValueError("planned count must cover source rows before evaluation")
        rows = [self.evaluate_case(c, edit_items, edit_order=edit_order) for c in cases]
        return {
            "schema_version": 1,
            "endpoint": "composition_direct",
            "rows": rows,
            "summary": summarize_composition(rows, expected_n=expected_n),
        }


def summarize_composition(rows, *, expected_n):
    if type(expected_n) is not int or expected_n < len(rows) or expected_n < 0:
        raise ValueError("planned composition count must cover returned rows")
    scored = [r for r in rows if r["status"] == "ok"]
    if any(
        type(r.get("composition_success")) is not bool or len(r.get("queries", [])) != 3
        for r in scored
    ):
        raise ValueError("scored composition rows require three paraphrases")
    successes = sum(r["composition_success"] for r in scored)
    para_hits = sum(r["paraphrase_successes"] for r in scored)
    return {
        "planned": expected_n,
        "available_rows": len(rows),
        "evaluable": sum(r["evaluable"] for r in rows),
        "scored": len(scored),
        "successes": successes,
        "missing_source_rows": expected_n - len(rows),
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "evaluated_fraction": successes / len(scored) if scored else None,
        "full_inventory_fraction": successes / expected_n
        if expected_n and len(scored) == expected_n
        else None,
        "paraphrases_planned": 3 * expected_n,
        "paraphrases_scored": 3 * len(scored),
        "paraphrase_successes": para_hits,
        "paraphrase_fraction_full_inventory": para_hits / (3 * expected_n)
        if expected_n and len(scored) == expected_n
        else None,
        "denominator_policy": "all planned cases retained; resource/unavailable/missing cases never imputed; behavioral acquisition misses remain scored",
        "scope": "secondary descriptive; no registered success margin",
    }


def select_for_realizations(cases, realization_edit_ids):
    """Outcome-independent membership rule; no file read or random selection."""
    streams = {str(r): list(ids) for r, ids in realization_edit_ids.items()}
    if any(len(ids) != len(set(ids)) for ids in streams.values()):
        raise ValueError("duplicate edit ID in realization")
    all_ids = [i for ids in streams.values() for i in ids]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("realizations must have disjoint edit IDs")
    case_ids = [c["composition_id"] for c in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("duplicate source composition ID")
    assigned = {r: [] for r in streams}
    unavailable, outside = [], []
    for case in cases:
        try:
            deps = set(dependency_ids(case))
        except EndpointUnavailable as e:
            unavailable.append({"composition_id": case["composition_id"], "reason": str(e)})
            continue
        owners = [r for r, ids in streams.items() if deps <= set(ids)]
        if owners:
            assigned[owners[0]].append(case)
            if structural_reason(case):
                unavailable.append(
                    {"composition_id": case["composition_id"], "reason": structural_reason(case)}
                )
        else:
            outside.append(case["composition_id"])
    return {
        "cases_by_realization": assigned,
        "expected": {
            r: {"cases": len(cs), "paraphrases": 3 * len(cs)} for r, cs in assigned.items()
        },
        "unavailable_source_cases": unavailable,
        "unattached_case_ids": outside,
        "rule": "all dependency item IDs in exactly one realization; same ordered case inventory for every condition/order; no outcome filtering",
    }


def expected_case_counts(cases, candidates, edit_quotas):
    """Exact expectation under R1-58 fixed stratum slots, not an actual draw.

    candidates: unique item_id/subject/stratum rows after first-subject policy.
    edit_quotas: realization -> stratum -> edit slots within the full permutation.
    Shared-case dependence affects variance, not this linear expectation.
    """
    if len({r["item_id"] for r in candidates}) != len(candidates) or len(
        {r["subject"] for r in candidates}
    ) != len(candidates):
        raise ValueError("unique candidate items and primary subjects required")
    by_id = {r["item_id"]: r for r in candidates}
    totals = Counter(r["stratum"] for r in candidates)
    eligible = []
    for c in cases:
        try:
            ids = dependency_ids(c)
        except EndpointUnavailable:
            continue
        if not structural_reason(c) and set(ids) <= by_id.keys():
            eligible.append(Counter(by_id[i]["stratum"] for i in ids))
    result = {}
    for r, quotas in edit_quotas.items():
        if any(type(n) is not int or n < 0 or n > totals[s] for s, n in quotas.items()):
            raise ValueError("invalid edit-stratum quota")
        mean = 0.0
        for needed in eligible:
            probability = 1.0
            for s, k in needed.items():
                n, total = quotas.get(s, 0), totals[s]
                probability *= math.comb(n, k) / math.comb(total, k) if n >= k else 0.0
            mean += probability
        result[str(r)] = {"expected_cases": mean, "expected_paraphrases": 3 * mean}
    return {
        "by_realization": result,
        "candidate_cases_with_all_dependencies": len(eligible),
        "formula": "sum over source cases of product_s C(edit_slots_rs,k_cs)/C(candidate_count_s,k_cs)",
        "draws": 0,
        "scope": "design expectation conditional on admitted unique-subject candidates and fixed quotas; realized counts come from membership after lead draw",
    }
