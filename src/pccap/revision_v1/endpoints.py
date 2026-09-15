"""Isolated development endpoints for preservation, revisions and two-hop queries.

Predictions receive prompt tokens only. Every independent query resets selection;
answer positions within that query share one selection. Each challenge runs on a
restored clone of the caller's starting fast state; the ledger keeps all work.
The two-hop diagnostic is distinct from a verified direct composition question.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

from pccap.contracts import CostRecord, EditItem
from pccap.data.decode import greedy_decode, score_generation
from pccap.data.tokenize import tokenize_pair
from pccap.metrics.editing import normalize_answer
from pccap.revision_v1.contracts import support_from_edit_item
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.selection_trace import selection_trace

ROOT = Path(__file__).resolve().parents[3]
KINDS = ("near_neighbour", "composition", "temporal_correction")


def row_hash(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def challenge_inventory(doc):
    if doc.get("mode") != "dev":
        raise ValueError("this adapter accepts development challenges only")
    inventory = {}
    for kind in KINDS:
        group = doc[kind]
        rows = group["items"]
        expected = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
        if expected != group["sha256_items"]:
            raise ValueError("challenge payload hash mismatch: " + kind)
        inventory[kind] = {"available_rows": len(rows), "source_population_n": group["n"],
                           "required": group["required"], "source_status": group["status"],
                           "shortfall": max(0, group["required"] - len(rows)), "sha256_items": expected}
    return inventory


def load_dev_challenges():
    path = ROOT / "manifests" / "dev" / "challenges.json"
    doc = json.loads(path.read_text())
    return doc, {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                 "inventory": challenge_inventory(doc)}


class EndpointUnavailable(ValueError):
    """Missing or unverified inputs, not a failed model answer."""


class EndpointResourceFailure(RuntimeError):
    """A recorded failed update; failed work remains charged."""


def _text(row, name):
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise EndpointUnavailable("missing_or_invalid_" + name)
    return value


def bridge_template(second_prompt, bridge):
    """Only a single literal bridge occurrence can define this diagnostic.

    No new standalone composed question is manufactured from a stored answer.
    """
    import re
    pattern = re.compile(r"(?<!\w)" + re.escape(bridge.strip()) + r"(?!\w)", re.IGNORECASE)
    matches = list(pattern.finditer(second_prompt))
    if len(matches) != 1:
        raise EndpointUnavailable("bridge_not_uniquely_located_in_second_prompt")
    if "{bridge}" in second_prompt:
        raise EndpointUnavailable("reserved_template_marker_in_source")
    a, b = matches[0].span()
    return second_prompt[:a] + "{bridge}" + second_prompt[b:]


def summarize(rows, success_field):
    statuses = Counter(r["status"] for r in rows)
    scored = [r for r in rows if r["status"] == "ok"]
    if any(type(r.get(success_field)) is not bool for r in scored):
        raise ValueError("successful evaluation rows require a boolean endpoint value")
    n, hits = len(scored), sum(r[success_field] for r in scored)
    return {"planned": len(rows), "scored": n, "successes": hits, "status_counts": dict(statuses),
            "evaluated_fraction": hits / n if n else None,
            "full_inventory_fraction": hits / n if n and n == len(rows) else None,
            "denominator_policy": "all evaluable cases, including unsuccessful acquisition/answers; unreachable and resource failures reported separately, never imputed",
            "coverage": n / len(rows) if rows else None}


class EndpointEvaluator:
    """CPU-testable RevisionCap adapter. Real-base execution belongs to the owner.

    max_new is 32 for ordinary editing. Tests may use shorter finite-vocabulary
    fixtures and must disclose that override. The evaluator does not write files.
    """

    def __init__(self, learner, tokenizer, *, base=None, max_new=32, ledger=None):
        if isinstance(max_new, bool) or not isinstance(max_new, int) or not 1 <= max_new <= 32:
            raise ValueError("max_new must be an integer in [1, 32]")
        self.learner, self.tok = learner, tokenizer
        self.base = base if base is not None else learner.base
        self.max_new = max_new
        self.ledger = ledger if ledger is not None else getattr(learner, "ledger", None)
        self._events = []

    def _immutable(self):
        weights = params_hash(self.learner.params) if hasattr(self.learner, "params") else None
        base = self.base.checksum(recompute=True) if hasattr(self.base, "checksum") else None
        return weights, base

    def _ledger(self):
        if self.ledger is None:
            return None
        totals = self.ledger.totals()
        return {phase: {k: totals[phase][k] for k in ("full_forwards", "partial_forwards", "reverses", "tokens", "accel_seconds")}
                for phase in ("learning", "query", "total")}

    def _read(self, model, prompt):
        ids = np.asarray(self.tok.encode(prompt), np.int32).reshape(-1)
        if not len(ids):
            raise EndpointUnavailable("empty_query_tokens")
        reset = getattr(model, "reset_queries", None)
        if reset:
            reset()
        before = self.learner.state_hash()
        cost = CostRecord(phase="query")
        selection = None
        try:
            def predict(prefix):
                result = model.predict(prefix) if hasattr(model, "predict") else model.forward(prefix, writes=(), phase="query", last_only=True)
                cost.add(result.cost)
                logits = np.asarray(result.logits)
                if not np.all(np.isfinite(logits)):
                    raise FloatingPointError("nonfinite endpoint logits")
                return logits
            decoded = greedy_decode(predict, ids, self.tok, max_new=self.max_new, state_hash=self.learner.state_hash)
            # Reuse the query's cached selection; never pass an answer to it.
            if hasattr(model, "selection_for"):
                sel = model.selection_for(ids)
                try:  # R1-67: legacy fields + hard_null + gate verdict
                    selection = selection_trace(sel, config=getattr(self.learner, "cfg", None))
                except (AttributeError, ValueError):  # a selection object without weights/hard_null (test doubles, v0 caps): legacy fields only
                    selection = {"record_ids": list(sel.record_ids), "null_mass": float(sel.null_mass),
                                 "best_score": float(sel.best_score) if getattr(sel, "best_score", None) is not None and np.isfinite(sel.best_score) else None,
                                 "prompt_len": int(sel.prompt_len), "hard_null": None, "trace": "legacy (selection_trace unavailable for this object)"}
            if self.learner.state_hash() != before:
                raise RuntimeError("endpoint prediction mutated persistent state")
            return decoded, {"prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                             "prompt_tokens": len(ids), "generated": decoded.text, "stopped_by": decoded.stopped_by,
                             "decode_steps": decoded.steps, "truncated": decoded.truncated, "selection": selection,
                             "returned_cost": cost.as_dict()}
        finally:
            self._events.append({"phase": "query", "model": "capoff" if model is self.base else "cap", "returned_cost": cost.as_dict()})
            if reset:
                reset()

    def _active(self, fact_id):
        return [r for r in self.learner.store.active_records() if r.fact_id == fact_id]

    def _item(self, case_id, slot, dataset, fact_id, prompt, answer, version=1, aliases=None, paraphrases=()):
        pair = tokenize_pair(self.tok, prompt, answer)
        if pair.excluded:
            raise EndpointUnavailable("support_tokenization:" + pair.reason)
        iid = f"endpoint-{case_id}-{slot}"
        return EditItem(item_id=iid, digest=hashlib.sha256(f"{iid}|{prompt}|{answer}".encode()).digest()[:16],
                        prompt=prompt, answer=answer.strip(), aliases=list(aliases or [normalize_answer(answer)]),
                        paraphrases=list(paraphrases), locality_prompts=[], prompt_ids=pair.prompt_ids,
                        answer_ids=pair.answer_ids, dataset=dataset, fact_id=fact_id, version=version)

    def _teach(self, item):
        out = self.learner.update_item(item)
        event = {"phase": "learning", "item_id": item.item_id, "code": out.code,
                 "codes": list(out.codes), "returned_cost": out.cost.as_dict()}
        self._events.append(event)
        if any(str(code).startswith("resource_failure:") for code in out.codes) or out.code in ("resource_stop", "acquisition_failure"):
            raise EndpointResourceFailure(";".join(out.codes))
        return event

    def _case(self, kind, row, operation):
        start = time.monotonic()
        snapshot = self.learner.export_state().clone()
        state_before = self.learner.state_hash()
        immutable = self._immutable()
        ledger_before = self._ledger()
        self._events = []
        result = {"schema_version": 1, "endpoint": kind, "case_id": row_hash(row)[:24],
                  "source_row_sha256": row_hash(row), "dataset": row.get("dataset"), "status": "ok",
                  "max_new_tokens": self.max_new, "state_before": state_before}
        try:
            try:
                result.update(operation(result["case_id"]))
            except EndpointUnavailable as e:
                result.update(status="unreachable", reason=str(e))
            except EndpointResourceFailure as e:
                result.update(status="resource_failure", reason=str(e))
        finally:
            self.learner.import_state(snapshot)
            if self.learner.state_hash() != state_before:
                raise RuntimeError("endpoint clone did not restore original state")
            if self._immutable() != immutable:
                raise RuntimeError("endpoint changed base or reusable parameters")
        ledger_after = self._ledger()
        result.update(state_restored=True, events=self._events, wall_seconds=time.monotonic() - start)
        result["ledger_delta"] = None if ledger_before is None else {
            phase: {k: ledger_after[phase][k] - ledger_before[phase][k] for k in ledger_before[phase]}
            for phase in ledger_before}
        result["cost_policy"] = "returned costs and shared-ledger deltas separate; all work including references, rejected updates and clone queries stays charged; no total-compute equivalence asserted"
        return result

    def near_miss(self, row):
        def operation(cid):
            dataset = _text(row, "dataset")
            fact = _text(row, "edit_item_id")
            prompt, answer = _text(row, "edit_prompt"), _text(row, "edit_answer")
            neighbour = _text(row, "neighbour_prompt")
            if self._active(fact):
                raise EndpointUnavailable("target_fact_already_present_in_start_state")
            item = self._item(cid, "edit", dataset, fact, prompt, answer)
            off, off_trace = self._read(self.base, neighbour)
            update = self._teach(item)
            own, own_trace = self._read(self.learner, prompt)
            after, after_trace = self._read(self.learner, neighbour)
            # Match the v0 LS convention: identical decoded cap-off text.
            return {"preserved": after.text == off.text, "edit_exact": bool(score_generation(own, item.aliases)["value"]),
                    "reference": off_trace, "edited_query": own_trace, "neighbour_query": after_trace,
                    "update": update, "reference_policy": "actual cap-off greedy answer, not stored neighbour_answer",
                    "stored_neighbour_answer_used_for_scoring": False}
        return self._case("near_miss_preservation", row, operation)

    def revision(self, row):
        def operation(cid):
            dataset, fact, prompt = _text(row, "dataset"), _text(row, "fact_id"), _text(row, "prompt")
            versions = row.get("versions")
            if not isinstance(versions, list) or len(versions) != 2:
                raise EndpointUnavailable("exactly_two_support_versions_required")
            a, b = versions
            if type(a.get("version")) is not int or type(b.get("version")) is not int or a["version"] >= b["version"]:
                raise EndpointUnavailable("versions_must_strictly_increase")
            answers = [_text(v, "answer") for v in versions]
            aliases = [v.get("aliases") or [normalize_answer(answer)] for v, answer in zip(versions, answers)]
            if any(not isinstance(v, list) or not v or any(not isinstance(s, str) or not normalize_answer(s) for s in v) for v in aliases):
                raise EndpointUnavailable("invalid_aliases")
            if set(map(normalize_answer, aliases[0])) & set(map(normalize_answer, aliases[1])):
                raise EndpointUnavailable("old_and_new_aliases_overlap")
            paras = row.get("paraphrases", [])
            if not isinstance(paras, list) or any(not isinstance(q, str) or not q.strip() for q in paras):
                raise EndpointUnavailable("invalid_paraphrases")
            if self._active(fact):
                raise EndpointUnavailable("target_fact_already_present_in_start_state")
            items = [self._item(cid, f"v{v['version']}", dataset, fact, prompt, answer, v["version"], alias, paras)
                     for v, answer, alias in zip(versions, answers, aliases)]
            first_update = self._teach(items[0])
            first, first_trace = self._read(self.learner, prompt)
            second_update = self._teach(items[1])
            first_id, second_id = [support_from_edit_item(it).record_id for it in items]
            records = {r.record_id: r for r in self.learner.store.records}
            old, new = records.get(first_id), records.get(second_id)
            retired = old is not None and not old.active and old.superseded_by == second_id
            new_active = new is not None and new.active
            queries = []
            for q in [prompt, *paras]:
                dec, trace = self._read(self.learner, q)
                queries.append({**trace, "new_exact": bool(score_generation(dec, aliases[1])["value"]),
                                "old_answer_reappeared": bool(score_generation(dec, aliases[0])["value"])})
            old_acquired = bool(score_generation(first, aliases[0])["value"])
            latest = queries[0]["new_exact"] and not queries[0]["old_answer_reappeared"]
            return {"revision_success": old_acquired and latest and retired and new_active,
                    "latest_answer_success": latest, "old_answer_acquired_before_revision": old_acquired,
                    "old_record_retired": retired, "new_record_active": new_active,
                    "old_record_id": first_id, "new_record_id": second_id,
                    "old_answer_reappearance_n": sum(q["old_answer_reappeared"] for q in queries),
                    "query_n": len(queries), "paraphrase_new_exact_fraction": float(np.mean([q["new_exact"] for q in queries[1:]])) if paras else None,
                    "before_revision": first_trace, "after_revision_queries": queries,
                    "updates": [first_update, second_update]}
        return self._case("revision", row, operation)

    def composition(self, row, *, verification=None, teach=True, composed_prompt=None):
        """Sequential two-hop diagnostic; never substitute the gold bridge at read time.

        verification requires row_sha256 + status='verified' + a nonempty method.
        A direct composition score additionally requires a reviewed composed_prompt.
        Missing records are unreachable; an incorrect generated bridge is a failure.
        """
        def operation(cid):
            if not verification or verification.get("status") != "verified" or verification.get("row_sha256") != row_hash(row) or not verification.get("method"):
                raise EndpointUnavailable("labels_not_verified_for_this_source_row")
            dataset = _text(row, "dataset")
            f1, f2 = _text(row, "first_item_id"), _text(row, "second_item_id")
            p1, p2 = _text(row, "first_prompt"), _text(row, "second_prompt")
            a1, a2 = _text(row, "o1"), _text(row, "o2")
            if f1 == f2:
                raise EndpointUnavailable("distinct_hops_required")
            template = bridge_template(p2, a1)
            if teach:
                if self._active(f1) or self._active(f2):
                    raise EndpointUnavailable("hop_fact_already_present_in_start_state")
                for slot, fact, prompt, answer in (("hop1", f1, p1, a1), ("hop2", f2, p2, a2)):
                    self._teach(self._item(cid, slot, dataset, fact, prompt, answer))
            missing = [fact for fact in (f1, f2) if not self._active(fact)]
            if missing:
                raise EndpointUnavailable("missing_hop:" + ",".join(missing))
            first, trace1 = self._read(self.learner, p1)
            first_ok = bool(score_generation(first, [a1])["value"])
            second_ok, trace2 = False, None
            generated_bridge = first.text.strip()
            if generated_bridge:
                second_prompt = template.replace("{bridge}", generated_bridge)
                second, trace2 = self._read(self.learner, second_prompt)
                second_ok = bool(score_generation(second, [a2])["value"])
            direct = {"status": "unreachable", "reason": "no_verified_standalone_composed_query"}
            if composed_prompt is not None:
                if not isinstance(composed_prompt, str) or not composed_prompt.strip() or verification.get("composed_prompt_sha256") != hashlib.sha256(composed_prompt.encode()).hexdigest():
                    raise EndpointUnavailable("direct_query_not_bound_to_verification")
                dec, trace = self._read(self.learner, composed_prompt)
                direct = {"status": "ok", "exact": bool(score_generation(dec, [a2])["value"]), "query": trace}
            return {"chain_success": first_ok and second_ok, "first_hop_exact": first_ok, "second_hop_exact": second_ok,
                    "first_query": trace1, "second_query": trace2, "bridge_policy": "generated first-hop text only",
                    "support_record_ids": {f: [r.record_id for r in self._active(f)] for f in (f1, f2)},
                    "direct_composition": direct, "verification": dict(verification),
                    "interpretation": "sequential two-hop pipeline diagnostic; not evidence that one cap query jointly reasons over two memories"}
        return self._case("composition_two_hop", row, operation)
