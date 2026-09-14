"""R1-44: read-only unseen-edit-prompt firing and cap-off answer preservation.

The caller supplies the same hash-bound source pool as the edit stream, the full
edit history, and a predeclared list of outside item IDs. This module neither
samples nor reads files. Labels and stored answers never enter the query path.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from collections import Counter

import numpy as np

from pccap.revision_v1.endpoints import EndpointEvaluator, EndpointUnavailable


def _norm(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def _required(row, key):
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("missing or invalid " + key)
    return value


def _unique_ids(values, name):
    values = list(values)
    if any(not isinstance(x, str) or not x.strip() for x in values) or len(set(values)) != len(
        values
    ):
        raise ValueError(name + " must contain unique nonempty item IDs")
    return values


def revision_selection(learner, prompt_ids):
    """Observe the cached decision after predict; never make an extra base pass."""
    if not hasattr(learner, "selection_for"):
        return None
    selection = learner.selection_for(prompt_ids)
    if not hasattr(selection, "hard_null"):
        return None
    null = float(selection.null_mass)
    if not math.isfinite(null) or not 0 <= null <= 1:
        raise RuntimeError("invalid unseen endpoint null mass")
    records = list(selection.record_ids)
    weights = np.asarray(selection.weights, np.float64).reshape(-1)
    if len(weights) != len(records) or not np.all(np.isfinite(weights)) or np.any(weights < 0):
        raise RuntimeError("invalid unseen endpoint selection weights")
    hard = bool(selection.hard_null)
    if not hard and (not records or weights.sum() <= 0):
        raise RuntimeError("accepted unseen query has no selected record")
    return {
        "hard_null": hard,
        "false_fire": not hard,
        "null_mass": null,
        "candidate_record_ids": records,
        "selected_record_ids": [rid for rid, w in zip(records, weights) if not hard and w > 0],
        "definition": "hard-gate acceptance; not proof of nonzero writes or changed generation",
    }


class _ObservedRead:
    def __init__(self, learner, observer):
        self.learner, self.observer = learner, observer
        self.first_selection = None
        self.observed = False

    def predict(self, ids):
        result = self.learner.predict(ids)
        if not self.observed:
            self.first_selection = self.observer(self.learner, ids)
            self.observed = True
        return result

    def reset_queries(self):
        reset = getattr(self.learner, "reset_queries", None)
        if reset:
            reset()


class UnseenPromptEvaluator(EndpointEvaluator):
    """Evaluate explicit outside prompts against the base of this condition.

    pool_rows may include teaching labels; only item/fact/subject/prompt metadata
    is retained. source_sha256 binds the caller's admitted source file; the
    additional query-metadata hash is computed here. Alias equivalence beyond
    the declared normalized subject keys requires upstream population review.

    The default observer supports RevisionCap. Other cap implementations may
    supply a prompt-only observer; otherwise firing is unavailable while answer
    change can still be measured. This evaluator creates no records or files.
    """

    def __init__(
        self,
        learner,
        tokenizer,
        pool_rows,
        *,
        pool_id,
        source_sha256,
        base=None,
        max_new=32,
        ledger=None,
        selection_observer=revision_selection,
    ):
        super().__init__(learner, tokenizer, base=base, max_new=max_new, ledger=ledger)
        if not isinstance(pool_id, str) or not pool_id.strip():
            raise ValueError("pool_id is required")
        if (
            not isinstance(source_sha256, str)
            or len(source_sha256) != 64
            or any(c not in "0123456789abcdef" for c in source_sha256)
        ):
            raise ValueError("source_sha256 must be a lowercase SHA-256 digest")
        self.pool_id, self.source_sha256 = pool_id, source_sha256
        self.observer = selection_observer
        self.pool = {}
        for raw in pool_rows:
            iid = _required(raw, "item_id")
            if iid in self.pool:
                raise ValueError("duplicate pool item ID: " + iid)
            self.pool[iid] = {
                "item_id": iid,
                "fact_id": _required(raw, "fact_id"),
                "subject_key": _norm(_required(raw, "subject")),
                "prompt": _required(raw, "prompt"),
                "dataset": raw.get("dataset", pool_id),
            }
        if not self.pool:
            raise ValueError("empty source pool")
        self.metadata_sha256 = _digest(list(self.pool.values()))

    def evaluate(self, item_ids, *, edited_item_ids, expected_n, checkpoint_id):
        """One equally weighted original prompt per requested source item.

        edited_item_ids is the full history through this checkpoint, including
        failed, evicted and superseded edits. Invalid outside cases are reported,
        never silently replaced. expected_n may exceed the available list to
        represent a shortfall; full-inventory rates then remain null.
        """
        requested = _unique_ids(item_ids, "requested queries")
        edited = _unique_ids(edited_item_ids, "edit history")
        if type(expected_n) is not int or expected_n <= 0 or expected_n < len(requested):
            raise ValueError("expected_n must be positive and at least the requested count")
        if not isinstance(checkpoint_id, str) or not checkpoint_id:
            raise ValueError("checkpoint_id is required")
        missing_edits = set(edited) - set(self.pool)
        if missing_edits:
            raise ValueError("edit history is not contained in the declared pool")
        history = [self.pool[i] for i in edited]
        facts = {r["fact_id"] for r in history}
        subjects = {r["subject_key"] for r in history}
        prompts = {_norm(r["prompt"]) for r in history}
        records = getattr(getattr(self.learner, "store", None), "records", None)
        if records is None:
            raise ValueError("memory fact inventory is required for unseen admission")
        if any(r.fact_id not in facts for r in records):
            raise ValueError("edit history does not cover the current memory")
        state = self.learner.state_hash()
        rows = []
        for iid in requested:
            row = self.pool.get(iid, {"item_id": iid, "dataset": self.pool_id})
            reason = None
            if iid not in self.pool:
                reason = "query_not_in_declared_pool"
            elif iid in edited:
                reason = "item_in_edit_history"
            elif row["fact_id"] in facts:
                reason = "fact_in_edit_history"
            elif row["subject_key"] in subjects:
                reason = "subject_in_edit_history"
            elif _norm(row["prompt"]) in prompts:
                reason = "prompt_matches_edit_history"

            def operation(_cid, row=row, reason=reason):
                if reason:
                    raise EndpointUnavailable(reason)
                ids = np.asarray(self.tok.encode(row["prompt"]), np.int32).reshape(-1)
                limit = int(getattr(getattr(self.base, "cfg", None), "n_pos", 1024))
                if not len(ids) or len(ids) + self.max_new > limit:
                    raise EndpointUnavailable("query_outside_declared_context_limit")
                off, reference = self._read(self.base, row["prompt"])
                observed = _ObservedRead(self.learner, self.observer)
                on, query = self._read(observed, row["prompt"])
                firing = observed.first_selection
                if firing is not None and (
                    type(firing.get("false_fire")) is not bool
                    or type(firing.get("hard_null")) is not bool
                    or firing["false_fire"] == firing["hard_null"]
                ):
                    raise RuntimeError("invalid observer firing decision")
                complete = not off.truncated and not on.truncated
                return {
                    "false_fire": None if firing is None else firing["false_fire"],
                    "firing_status": "unavailable" if firing is None else "ok",
                    "selection": firing,
                    "answer_changed": on.text != off.text,
                    "generated_tokens_changed": not np.array_equal(on.new_ids, off.new_ids),
                    "both_answers_terminated": complete,
                    "complete_answer_preserved": complete and on.text == off.text,
                    "reference": reference,
                    "cap_query": query,
                    "reference_policy": "this condition's actual cap-off greedy answer; no stored labels",
                }

            result = self._case("unseen_edit_prompt", row, operation)
            result.update(
                item_id=iid,
                pool_id=self.pool_id,
                source_sha256=self.source_sha256,
                checkpoint_id=checkpoint_id,
            )
            rows.append(result)
        if self.learner.state_hash() != state:
            raise RuntimeError("unseen endpoint changed checkpoint state")
        return {
            "schema_version": 1,
            "endpoint": "unseen_edit_prompt",
            "checkpoint_id": checkpoint_id,
            "pool_id": self.pool_id,
            "source_sha256": self.source_sha256,
            "pool_query_metadata_sha256": self.metadata_sha256,
            "edit_history_sha256": _digest(edited),
            "edited_items": len(edited),
            "memory_records": len(records),
            "active_memory_records": sum(bool(r.active) for r in records),
            "requested_item_ids_sha256": _digest(requested),
            "max_new_tokens": self.max_new,
            "rows": rows,
            "summary": summarize_unseen(rows, expected_n=expected_n),
            "state_restored": True,
            "population": "one original edit-style prompt per requested item; all edited item/fact/subject/prompt identities excluded",
            "limits": [
                "same-pool source identity is supplied by the admitted caller; no source file opened here",
                "normalized subject identity is not complete alias/entity equivalence",
                "bounded decoded-text change is separate from gate acceptance and complete-answer preservation",
                "shortfalls and unavailable firing observations cannot be counted as non-firing",
            ],
        }


def summarize_unseen(rows, *, expected_n):
    if type(expected_n) is not int or expected_n <= 0 or expected_n < len(rows):
        raise ValueError("invalid planned denominator")
    if len({r["item_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate endpoint item rows")
    scored = [r for r in rows if r["status"] == "ok"]
    if any(
        type(r.get("answer_changed")) is not bool
        or type(r.get("both_answers_terminated")) is not bool
        or type(r.get("complete_answer_preserved")) is not bool
        for r in scored
    ):
        raise ValueError("scored answer metrics must be booleans")
    firing = [r for r in scored if r.get("firing_status") == "ok"]
    if any(type(r.get("false_fire")) is not bool for r in firing):
        raise ValueError("scored firing must be boolean")
    complete = [r for r in scored if r["both_answers_terminated"]]

    def fraction(numerator, denominator):
        return numerator / denominator if denominator else None

    changed = sum(r["answer_changed"] for r in scored)
    fires = sum(r["false_fire"] for r in firing)
    preserved = sum(r["complete_answer_preserved"] for r in scored)
    return {
        "expected_n": expected_n,
        "requested_n": len(rows),
        "source_shortfall": expected_n - len(rows),
        "scored_n": len(scored),
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "coverage": len(scored) / expected_n,
        "false_fires": fires,
        "firing_observed_n": len(firing),
        "false_fire_rate_evaluated": fraction(fires, len(firing)),
        "false_fire_rate_full_inventory": fires / expected_n if len(firing) == expected_n else None,
        "answer_changes": changed,
        "answer_change_rate_evaluated": fraction(changed, len(scored)),
        "answer_change_rate_full_inventory": changed / expected_n
        if len(scored) == expected_n
        else None,
        "both_answers_terminated_n": len(complete),
        "incomplete_answer_pairs_n": len(scored) - len(complete),
        "answer_change_rate_complete_pairs": fraction(
            sum(r["answer_changed"] for r in complete), len(complete)
        ),
        "complete_answer_preservation_rate_evaluated": fraction(preserved, len(scored)),
        "complete_answer_preservation_rate_full_inventory": preserved / expected_n
        if len(scored) == expected_n
        else None,
        "denominator_policy": "one planned prompt per item, unconditional on acquisition/firing; unavailable cases and shortfalls retained; no imputation",
    }
