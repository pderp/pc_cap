"""Read-only checkpoint assays used by the one-cell Stage 4 runner."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from pccap.data.decode import score_generation
from pccap.metrics.editing import normalize_answer
from pccap.revision_v1.endpoints import EndpointEvaluator, EndpointUnavailable, row_hash
from pccap.revision_v1.endpoints_composition import CompositionEvaluator
from pccap.revision_v1.endpoints_unseen import UnseenPromptEvaluator, summarize_unseen


class _MemoryView:
    """Audit-only inventory for unseen admission; predictions delegate unchanged."""

    def __init__(self, adapter, records):
        self.adapter = adapter
        self.store = SimpleNamespace(records=records)

    def __getattr__(self, name):
        return getattr(self.adapter, name)


class _Challenges(EndpointEvaluator):
    def __init__(self, *args, history=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.history = history

    def _active(self, fact_id):
        records = self.learner.memory_inventory(self.history)
        if records is None:
            raise EndpointUnavailable("memory_fact_inventory_unavailable")
        return [r for r in records if r.fact_id == fact_id and r.active]

    def near_miss(self, row):
        out = super().near_miss(row)
        if out["status"] == "ok":
            out["preserved"] = (
                out["preserved"]
                and not out["reference"]["truncated"]
                and not out["neighbour_query"]["truncated"]
            )
            out["edit_exact"] = out["edit_exact"] and not out["edited_query"]["truncated"]
        return out

    def revision(self, row):
        if hasattr(self.learner.learner, "store"):
            return super().revision(row)

        # v0 has no declared RevisionCap record supersession semantics. Measure
        # its answers but do not manufacture a record-retirement success/failure.
        def operation(cid):
            versions = row.get("versions", [])
            if (
                len(versions) != 2
                or any(type(v.get("version")) is not int for v in versions)
                or versions[0]["version"] >= versions[1]["version"]
            ):
                raise EndpointUnavailable("two_increasing_versions_required")
            aliases = [v.get("aliases") or [v["answer"]] for v in versions]
            if set(map(normalize_answer, aliases[0])) & set(map(normalize_answer, aliases[1])):
                raise EndpointUnavailable("old_and_new_aliases_overlap")
            if self._active(row["fact_id"]):
                raise EndpointUnavailable("target_fact_already_present")
            items = [
                self._item(
                    cid,
                    f"v{v['version']}",
                    row["dataset"],
                    row["fact_id"],
                    row["prompt"],
                    v["answer"],
                    v["version"],
                    a,
                )
                for v, a in zip(versions, aliases, strict=True)
            ]
            first_update = self._teach(items[0])
            first, trace = self._read(self.learner, row["prompt"])
            second_update = self._teach(items[1])
            queries = []
            for prompt in [row["prompt"], *row.get("paraphrases", [])]:
                dec, tr = self._read(self.learner, prompt)
                queries.append(
                    {
                        **tr,
                        "new_exact": not dec.truncated
                        and bool(score_generation(dec, aliases[1])["value"]),
                        "old_answer_reappeared": not dec.truncated
                        and bool(score_generation(dec, aliases[0])["value"]),
                    }
                )
            return {
                "revision_success": None,
                "revision_observer_status": "unavailable",
                "latest_answer_success": queries[0]["new_exact"]
                and not queries[0]["old_answer_reappeared"],
                "old_answer_acquired_before_revision": not first.truncated
                and bool(score_generation(first, aliases[0])["value"]),
                "old_record_retired": None,
                "new_record_active": None,
                "before_revision": trace,
                "after_revision_queries": queries,
                "old_answer_reappearance_n": sum(q["old_answer_reappeared"] for q in queries),
                "updates": [first_update, second_update],
            }

        return self._case("revision", row, operation)


class CellAssays:
    def __init__(self, adapter, tokenizer, *, max_new=32):
        self.adapter, self.tok, self.max_new = adapter, tokenizer, max_new
        self.events = []

    def evaluator(self, **kwargs):
        return EndpointEvaluator(self.adapter, self.tok, max_new=self.max_new, **kwargs)

    def item(self, item):
        ev = self.evaluator()
        try:
            es, trace = ev._read(self.adapter, item.prompt)
            gs = []
            for prompt in item.paraphrases:
                dec, tr = ev._read(self.adapter, prompt)
                gs.append(
                    {
                        **tr,
                        "exact": not dec.truncated
                        and bool(score_generation(dec, item.aliases)["value"]),
                    }
                )
            return {
                "item_id": item.item_id,
                "status": "ok",
                "es": float(not es.truncated and bool(score_generation(es, item.aliases)["value"])),
                "gs": sum(r["exact"] for r in gs) / len(gs) if gs else None,
                "paraphrase_n": len(gs),
                "paraphrases": gs,
                "query": trace,
            }
        finally:
            self.events.extend(ev._events)

    def retention(self, items):
        return {"rows": [self.item(it) for it in items], "planned": len(items)}

    def locality(self, definition):
        ev = self.evaluator()
        rows = []
        try:
            for row in definition["rows"]:
                off, ref = ev._read(self.adapter.locality_base, row["prompt"])
                on, query = ev._read(self.adapter, row["prompt"])
                rows.append(
                    {
                        "item_id": row["item_id"],
                        "status": "ok",
                        "preserved": not off.truncated and not on.truncated and on.text == off.text,
                        "reference": ref,
                        "query": query,
                    }
                )
            return {
                "rows": rows,
                "expected_ids": definition["expected_ids"],
                "reference_base_sha256": self.adapter.locality_base.checksum(recompute=True),
                "reference_policy": "original base for S1 and original-base conditions",
            }
        finally:
            self.events.extend(ev._events)

    def unseen(self, definition, pool, history, checkpoint_id, pool_sha256):
        records = self.adapter.memory_inventory(history)
        if records is None:
            rows = [
                {
                    "item_id": r["item_id"],
                    "status": "unavailable",
                    "reason": "memory_fact_inventory_unavailable",
                }
                for r in definition["rows"]
            ]
            return {
                "rows": rows,
                "summary": summarize_unseen(rows, expected_n=len(definition["expected_ids"])),
            }
        view = _MemoryView(self.adapter, records)
        ev = UnseenPromptEvaluator(
            view,
            self.tok,
            pool,
            pool_id=self.adapter.condition,
            source_sha256=pool_sha256,
            max_new=self.max_new,
            selection_observer=lambda _model, ids: self.adapter.observe_firing(ids),
        )
        out = ev.evaluate(
            [r["item_id"] for r in definition["rows"]],
            edited_item_ids=[it.item_id for it in history],
            expected_n=len(definition["expected_ids"]),
            checkpoint_id=checkpoint_id,
        )
        for row in out["rows"]:
            self.events.extend(row.get("events", []))
        out["memory_inventory_unit"] = (
            "records" if hasattr(self.adapter.learner, "store") else "observed_slots"
        )
        return out

    def challenges(self, kind, definition, history):
        ev = _Challenges(self.adapter, self.tok, max_new=self.max_new, history=history)
        rows = []
        for source in definition["rows"]:
            result = getattr(ev, kind)(source)
            result["item_id"] = source["item_id"]
            rows.append(result)
            self.events.extend(result.get("events", []))
        return {"rows": rows, "expected_ids": definition["expected_ids"]}

    def composition(self, definition, items, initial_state):
        ev = CompositionEvaluator(
            self.adapter, self.tok, max_new=self.max_new, teaching_state=initial_state
        )
        out = ev.evaluate(
            definition["rows"],
            {it.item_id: it for it in items},
            edit_order=[it.item_id for it in items],
            expected_n=len(definition["expected_ids"]),
        )
        for row in out["rows"]:
            self.events.extend(row.get("events", []))
        return out

    def drift(self, definition):
        rows = []
        for wi, window in enumerate(definition["windows"]):
            w = np.asarray(window, np.int32)
            for position in range(1, len(w)):
                values = {}
                for kind, model in (
                    ("capoff", self.adapter.base),
                    ("original", self.adapter.locality_base),
                    ("cap", self.adapter),
                ):
                    if kind == "original" and model is self.adapter.base:
                        values[kind] = values["capoff"]
                        continue
                    self.adapter.reset_queries()
                    before = self.adapter.state_hash()
                    try:
                        out = (
                            model.predict(w[:position])
                            if hasattr(model, "predict")
                            else model.forward(
                                w[:position], writes=(), phase="query", last_only=True
                            )
                        )
                        self.events.append(
                            {"phase": "query", "model": kind, "returned_cost": out.cost.as_dict()}
                        )
                        logits = np.asarray(out.logits, np.float64).reshape(
                            -1, np.asarray(out.logits).shape[-1]
                        )[-1]
                        if not np.all(np.isfinite(logits)):
                            raise FloatingPointError("nonfinite drift logits")
                        peak = logits.max()
                        values[kind] = float(
                            peak + np.log(np.exp(logits - peak).sum()) - logits[int(w[position])]
                        )
                        if self.adapter.state_hash() != before:
                            raise RuntimeError("drift query mutated state")
                    finally:
                        self.adapter.reset_queries()
                rows.append({"item_id": f"w{wi}:p{position}", **values})

        def mean(key):
            return float(np.mean([r[key] for r in rows])) if rows else None

        original, off, on = mean("original"), mean("capoff"), mean("cap")
        complete = len(rows) == definition["expected_positions"]
        return {
            "rows": rows,
            "scored_positions": len(rows),
            "expected_positions": definition["expected_positions"],
            "status": "complete" if complete else "incomplete",
            "delta_capoff_nats": on - off if rows and complete else None,
            "delta_original_nats": on - original if rows and complete else None,
            "query_boundary_policy": "reset at every scored ordinary-text prefix",
            "source_sha256": row_hash(definition),
        }
