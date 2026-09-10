"""General stream runner for cap arms (S3/S4; PDF D.8, E.2, App. B).

``run_stream`` learns an ordered item stream with one learner (a ``Cap`` for C0/C1/C2/CR/CO;
any object with ``update_item``/``predict``/``export_state``/``state_hash``/``memory_bytes`` for
baselines) and records, per item: immediate ES (exact complete-answer match), GS (mean over the
item's paraphrases), teacher-forced NLL, the routing/decision records; at checkpoints
{100, 300, 1000, 3000} ∩ stream and at the end: RET-ES / RET-GS on all items so far (unconditional
and conditional on immediate acquisition), LS on the locality prompts (complete-answer agreement
with the cap-disabled base, first-token agreement, fixed-prefix KL), LM drift on a fixed
sequential drift sample (perplexity ratio and mean loss difference vs the cap-disabled base) and
the learner checkpoint under ``assets/runs/…``. Costs come from the shared ledger; every
evaluation is ``query`` phase and read-only (state hash asserted). A resource stop rolls the
incomplete item back (``ItemGuard``) and is charged.

Outputs in ``run_dir``: ``decisions.jsonl``, ``items.jsonl``, ``checkpoints.json``,
``metrics.json`` (schema ``metrics``), ``cost.json``; checkpoints in ``assets/runs/<run>/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from pccap import ASSETS_ROOT
from pccap.contracts import Budget, EditItem, metric
from pccap.data.decode import (
    _last_logits,
    greedy_decode,
    greedy_decode_batch_cap,
    score_generation,
)
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.records import OutcomeCode, append_jsonl
from pccap.harness.snapshot import ItemGuard, save
from pccap.metrics.divergence import kl
from pccap.transport.transport import Transport

ROOT = Path(__file__).resolve().parents[3]
CHECKPOINTS = (100, 300, 1000, 3000)


def _softmax(row: np.ndarray) -> np.ndarray:
    r = np.asarray(row, np.float64)
    r = r - r.max()
    e = np.exp(r)
    return e / e.sum()


class Evaluator:
    """Read-only evaluation against the cap-disabled base (LS references cached once)."""

    def __init__(self, base, tok: GPT2Tokenizer, locality_prompts: list[str], drift_tokens: np.ndarray | None,
                 drift_positions: int = 4096, drift_window: int = 128):
        self.base, self.tok = base, tok
        self.loc_ids = [tok.encode(s) for s in locality_prompts]
        self.loc_ref = []
        if self.loc_ids:
            from pccap.data.decode import greedy_decode_batch

            decs = greedy_decode_batch(base, self.loc_ids, tok)
            rows = np.concatenate([np.asarray(base.forward_batch(self.loc_ids[k : k + 64], None, phase="query")[0]) for k in range(0, len(self.loc_ids), 64)])
            for dec, row in zip(decs, rows):
                self.loc_ref.append((dec.text, int(dec.new_ids[0]) if len(dec.new_ids) else -1, _softmax(row)))
        self.drift_windows = None
        if drift_tokens is not None:
            n_win = max(1, drift_positions // drift_window)
            wins = [drift_tokens[i * drift_window : (i + 1) * drift_window] for i in range(n_win)]
            self.drift_windows = [w for w in wins if len(w) == drift_window]
            self.drift_base_nll = self._drift_nll(base)

    @staticmethod
    def _batch_last(learner, seqs: list[np.ndarray]) -> np.ndarray:
        """Last-row logits for many prefixes in one batched cap-on call (HARN-BATCH; parity-tested),
        falling back to sequential predict for learners without the batched method."""
        if hasattr(learner, "edited_forward_batch"):
            return learner.edited_forward_batch(seqs, phase="query")[0]
        if hasattr(learner, "last_logits_batch"):  # baseline arms (harness.arms adapters) and the bare base
            return np.asarray(learner.last_logits_batch(seqs, phase="query"))
        if hasattr(learner, "forward_batch"):
            return np.asarray(learner.forward_batch(seqs, None, phase="query")[0])
        return np.stack([_last_logits(learner.predict(x).logits) for x in seqs])

    @staticmethod
    def _decode_many(learner, prompts: list[np.ndarray], tok: GPT2Tokenizer):
        if hasattr(learner, "edited_forward_batch"):
            return greedy_decode_batch_cap(learner, prompts, tok)
        if hasattr(learner, "last_logits_batch"):
            from pccap.data.decode import greedy_decode_batch

            return greedy_decode_batch(learner, prompts, tok)
        return [greedy_decode(lambda ids: learner.predict(ids).logits, p, tok) for p in prompts]

    @staticmethod
    def _nll_rows(logits: np.ndarray, targets: np.ndarray) -> np.ndarray:
        L = logits.astype(np.float64)
        m = L.max(axis=-1)
        return m + np.log(np.exp(L - m[:, None]).sum(-1)) - L[np.arange(len(targets)), targets]

    def _drift_nll(self, learner_or_predict) -> float:
        """Full-recompute NLL over the drift windows (positions 1..T-1), batched across windows per step."""
        total, n = 0.0, 0
        T = len(self.drift_windows[0])
        for t in range(1, T):
            seqs = [w[:t] for w in self.drift_windows]
            tg = np.asarray([int(w[t]) for w in self.drift_windows])
            logits = self._batch_last(learner_or_predict, seqs) if not callable(learner_or_predict) else np.stack([_last_logits(learner_or_predict(x)) for x in seqs])
            total += float(self._nll_rows(logits, tg).sum())
            n += len(seqs)
        return total / n

    def items(self, learner, items: list[EditItem]) -> list[dict]:
        """Immediate/retained evaluation of many items in batched calls: one decode batch for all
        prompts and paraphrases, one last-logits batch for all teacher-forced prefixes."""
        before = learner.state_hash()
        prompts, owners = [], []
        for i, it in enumerate(items):
            prompts.append(it.prompt_ids)
            owners.append((i, "es"))
            for p in it.paraphrases:
                prompts.append(self.tok.encode(p))
                owners.append((i, "gs"))
        decs = self._decode_many(learner, prompts, self.tok)
        prefixes, targets, owner_nll = [], [], []
        for i, it in enumerate(items):
            ids = np.asarray(it.prompt_ids, np.int32)
            for y in np.asarray(it.answer_ids, np.int32):
                prefixes.append(ids)
                targets.append(int(y))
                owner_nll.append(i)
                ids = np.concatenate([ids, np.int32([y])])
        nll_rows = np.zeros(0)
        if prefixes:
            logits = np.concatenate([self._batch_last(learner, prefixes[k : k + 64]) for k in range(0, len(prefixes), 64)])
            nll_rows = self._nll_rows(logits, np.asarray(targets))
        out = [{"es": None, "gs": None, "gs_n": 0, "generated": "", "stopped_by": "", "nll": 0.0, "_gs": []} for _ in items]
        for (i, kind), dec in zip(owners, decs):
            sc = score_generation(dec, items[i].aliases)["value"]
            if kind == "es":
                out[i].update(es=sc, generated=dec.text, stopped_by=dec.stopped_by)
            else:
                out[i]["_gs"].append(sc)
        for i, v in zip(owner_nll, nll_rows):
            out[i]["nll"] += float(v)
        for o in out:
            g = o.pop("_gs")
            o["gs"] = float(np.mean(g)) if g else None
            o["gs_n"] = len(g)
        if learner.state_hash() != before:
            raise RuntimeError("evaluation mutated learner state (PC-8)")
        return out

    def item(self, learner, it: EditItem) -> dict:
        return self.items(learner, [it])[0]

    def locality(self, learner) -> dict:
        agree = first = 0
        kls = []
        decs = self._decode_many(learner, self.loc_ids, self.tok)
        logits = np.concatenate([self._batch_last(learner, self.loc_ids[k : k + 64]) for k in range(0, len(self.loc_ids), 64)]) if self.loc_ids else np.zeros((0, 1))
        for (_ids, (ref_text, ref_first, ref_p)), dec, row in zip(zip(self.loc_ids, self.loc_ref), decs, logits):
            agree += int(dec.text == ref_text)
            first += int(len(dec.new_ids) > 0 and int(dec.new_ids[0]) == ref_first)
            kls.append(kl(ref_p, _softmax(row))["value"])
        n = len(self.loc_ids)
        return {"ls_complete_answer": agree / n if n else None, "ls_first_token": first / n if n else None,
                "ls_kl_mean": float(np.mean(kls)) if kls else None, "n": n}

    def drift(self, learner) -> dict | None:
        if self.drift_windows is None:
            return None
        nll = self._drift_nll(learner)
        return {"nll": nll, "base_nll": self.drift_base_nll, "loss_difference": nll - self.drift_base_nll,
                "perplexity_ratio": float(np.exp(nll - self.drift_base_nll)), "positions": sum(len(w) - 1 for w in self.drift_windows),
                "note": "sequential full-recompute on a fixed drift sample (subset of the validation split)"}


def run_stream(learner, items: list[EditItem], router, budget: Budget, evaluator: Evaluator, run_dir: Path, ledger,
               checkpoints=CHECKPOINTS, seed: int = 0, correction_track: bool = False, permitted=None,
               resource_stop_seconds: float | None = None, arm: str = "") -> dict:
    from pccap.cap.learn import update_item

    run_dir.mkdir(parents=True, exist_ok=True)
    dec_path, items_path = run_dir / "decisions.jsonl", run_dir / "items.jsonl"
    for p in (dec_path, items_path):
        p.unlink(missing_ok=True)
    ckpt_dir = Path(ASSETS_ROOT) / "runs" / run_dir.relative_to(ROOT / "results")
    t0 = time.time()
    history: list[dict] = []
    acquired_ids: list[str] = []
    status = "complete"
    completed = 0
    ckpt_records = []

    def ledger_snapshot() -> dict:
        t = ledger.totals()
        return {k: float(t[k]["accel_seconds"]) for k in ("learning", "query", "total")}

    def rescore(tag: str):
        rows = []
        led0 = ledger_snapshot()
        evs = evaluator.items(learner, items[:completed])
        for it, e in zip(items[:completed], evs):
            rows.append({"item_id": it.item_id, "ret_es": e["es"], "ret_gs": e["gs"]})
        acq = {h["item_id"] for h in history if h["es"] == 1.0}
        ret_es = [r["ret_es"] for r in rows]
        ret_gs = [r["ret_gs"] for r in rows if r["ret_gs"] is not None]
        cond = [r["ret_es"] for r in rows if r["item_id"] in acq]
        loc = evaluator.locality(learner)
        dr = evaluator.drift(learner)
        sha = save(learner.export_state(), ckpt_dir / f"learner_{tag}.ckpt")
        led1 = ledger_snapshot()
        rec = {"tag": tag, "items": completed, "ret_es": float(np.mean(ret_es)) if ret_es else None,
               "ledger_accel_seconds_at_checkpoint": led1, "rescoring_accel_seconds": {k: led1[k] - led0[k] for k in led1},
               "ret_gs": float(np.mean(ret_gs)) if ret_gs else None, "ret_gs_n": len(ret_gs),
               "survival_conditional_on_immediate": float(np.mean(cond)) if cond else None, "acquired_immediate": len(acq),
               "locality": loc, "drift": dr, "memory": learner.memory_bytes().__dict__, "checkpoint_sha256": sha,
               "state_hash": learner.state_hash(), "rows": rows, "wall_seconds": time.time() - t0}
        ckpt_records.append(rec)
        return rec

    for idx, it in enumerate(items):
        if resource_stop_seconds is not None and ledger.totals()["total"]["accel_seconds"] > resource_stop_seconds:
            status = OutcomeCode.resource_stop.value
            break
        led_before = ledger_snapshot()
        with ItemGuard(learner, ledger) as guard:
            kw = {"on_decision": lambda r: append_jsonl(dec_path, r), "seed": seed, "correction_track": correction_track}
            if permitted is not None:
                kw["permitted_banks"] = permitted(it)
            # baseline learners charge the shared ledger inside their own ledger.call blocks (Lane F)
            out = update_item(learner, it, router, budget, Transport(), **kw) if hasattr(learner, "banks") else learner.update_item(it)
            guard.commit()
        completed = idx + 1
        led_after_update = ledger_snapshot()
        e = evaluator.item(learner, it)
        led_after_eval = ledger_snapshot()
        # R2-06: the item's own cost record (learner-internal counters) plus the shared-ledger deltas, which include every
        # base call the learner made (adjoints, probes, searches) and the immediate evaluation, so resource views can
        # reconcile with the final ledger exactly.
        row = {"index": idx, "item_id": it.item_id, "dataset": it.dataset, "outcome": out.code, "rounds": out.rounds_used,
               "threshold": out.acquired_threshold_all_prefixes, **e, "answer_tokens": int(len(it.answer_ids)),
               "cost": out.cost.as_dict(),
               "ledger_delta": {"update": {k: led_after_update[k] - led_before[k] for k in led_before},
                                "immediate_eval": {k: led_after_eval[k] - led_after_update[k] for k in led_before},
                                "cumulative": led_after_eval}}
        history.append(row)
        append_jsonl(items_path, row)
        if e["es"] == 1.0:
            acquired_ids.append(it.item_id)
        if completed in checkpoints:
            rescore(f"ckpt{completed}")
        if resource_stop_seconds is not None and ledger.totals()["total"]["accel_seconds"] > resource_stop_seconds:
            status = OutcomeCode.resource_stop.value  # exceeded after a committed item: the completed prefix is exact
            break
    final = rescore("end")
    n = completed
    es = [h["es"] for h in history]
    gs = [h["gs"] for h in history if h["gs"] is not None]
    metrics = {
        "stage": run_dir.relative_to(ROOT / "results").parts[0], "arm": arm, "base": getattr(getattr(learner, "base", None), "name", "?"),
        "status": status, "items_completed": n, "items_planned": len(items),
        "metrics": {
            "es_immediate": metric(float(np.mean(es)) if es else None, units="fraction", n=n, status="ok" if es else "undefined"),
            "gs_immediate": metric(float(np.mean(gs)) if gs else None, units="fraction", n=len(gs), status="ok" if gs else "undefined"),
            "threshold_acquisition": metric(float(np.mean([h["threshold"] for h in history])) if history else None, units="fraction", n=n, status="ok" if history else "undefined"),
            "ret_es_end": metric(final["ret_es"], units="fraction", n=n, status="ok" if final["ret_es"] is not None else "undefined"),
            "ret_gs_end": metric(final["ret_gs"], units="fraction", n=final["ret_gs_n"], status="ok" if final["ret_gs"] is not None else "undefined"),
            "survival_conditional_end": metric(final["survival_conditional_on_immediate"], units="fraction", n=final["acquired_immediate"],
                                               status="ok" if final["survival_conditional_on_immediate"] is not None else "undefined"),
            "ls_complete_answer_end": metric(final["locality"]["ls_complete_answer"], units="fraction", n=final["locality"]["n"]),
            "ls_first_token_end": metric(final["locality"]["ls_first_token"], units="fraction", n=final["locality"]["n"]),
            "ls_kl_end": metric(final["locality"]["ls_kl_mean"], units="nats", n=final["locality"]["n"]),
            "lm_drift_loss_difference": metric(final["drift"]["loss_difference"] if final["drift"] else None, units="nats",
                                               n=final["drift"]["positions"] if final["drift"] else 0, status="ok" if final["drift"] else "unsupported"),
            "lm_drift_perplexity_ratio": metric(final["drift"]["perplexity_ratio"] if final["drift"] else None, units="ratio",
                                                n=final["drift"]["positions"] if final["drift"] else 0, status="ok" if final["drift"] else "unsupported"),
            "memory_occupied_bytes": metric(final["memory"]["occupied_bytes"], units="bytes", n=1),
        },
        "strata": {"answer_length": {str(k): int(sum(1 for h in history if h["answer_tokens"] == k)) for k in sorted({h["answer_tokens"] for h in history})}},
        "base_hash_before": None, "base_hash_after": None, "wall_seconds": time.time() - t0,
        "ledger_totals": ledger.totals(), "resource_stop_seconds": resource_stop_seconds,
    }
    (run_dir / "checkpoints.json").write_text(json.dumps(ckpt_records, indent=1, default=float))
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=1, default=float))
    ledger.write(run_dir)
    return metrics
