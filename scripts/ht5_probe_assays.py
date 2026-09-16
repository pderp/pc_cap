"""Fixed HT-2 old-fact assays; no learning, no outcome-dependent filtering."""

from __future__ import annotations

import numpy as np

from pccap.data.tokenize import tokenize_pair
from pccap.revision_v1.analysis import digest

CADENCE = [20, 60, 70, 80, 100]


def nll(logits, target):
    values = np.asarray(logits, np.float64)
    values = values.reshape(-1, values.shape[-1])[-1]
    if not np.all(np.isfinite(values)) or not 0 <= int(target) < len(values):
        raise FloatingPointError("nonfinite logits or invalid target")
    peak = values.max()
    return float(peak + np.log(np.exp(values - peak).sum()) - values[int(target)])


def probe(assays, items):
    """One query boundary per complete teacher-forced answer, including terminal."""
    if len(items) != 20 or len({it.item_id for it in items}) != 20:
        raise ValueError("exactly twenty fixed old facts required")
    adapter = assays.adapter
    rows, facts = [], []
    context = int(getattr(getattr(adapter.base, "cfg", None), "n_pos", 1024))
    for item in items:
        if not item.paraphrases:
            raise ValueError("fixed old facts require their paraphrases")
        facts.append(assays.item(item))
        for qi, prompt in enumerate([item.prompt, *item.paraphrases]):
            pair = tokenize_pair(assays.tok, prompt, item.answer)
            if pair.excluded:
                raise ValueError("excluded fixed probe answer")
            support, target = pair.prompt_ids, pair.answer_ids
            if not len(support) or not len(target) or len(support) + len(target) > context:
                raise ValueError("invalid fixed probe context")
            query_id = digest([item.item_id, qi, list(map(int, support)), list(map(int, target))])
            measurements = {}
            for label, model in (("cap", adapter), ("original", adapter.locality_base)):
                adapter.reset_queries()
                try:
                    values = []
                    for ti, token in enumerate(target):
                        prefix = np.asarray([*support, *target[:ti]], np.int32)
                        out = (
                            model.predict(prefix)
                            if hasattr(model, "predict")
                            else model.forward(prefix, writes=(), phase="query", last_only=True)
                        )
                        assays.events.append(
                            {
                                "phase": "query",
                                "model": label,
                                "item_id": item.item_id,
                                "prompt_index": qi,
                                "target_index": ti,
                                "returned_cost": out.cost.as_dict(),
                            }
                        )
                        values.append(nll(out.logits, token))
                    measurements[label] = values
                finally:
                    adapter.reset_queries()
            for ti, token in enumerate(target):
                rows.append(
                    {
                        "key": f"{query_id}:{ti}",
                        "item_id": item.item_id,
                        "prompt_index": qi,
                        "target_index": ti,
                        "target_token": int(token),
                        "cap_nll": measurements["cap"][ti],
                        "original_nll": measurements["original"][ti],
                    }
                )
    if len({r["key"] for r in rows}) != len(rows):
        raise ValueError("duplicate probe position")
    return {
        "status": "complete",
        "facts": facts,
        "tokens": rows,
        "planned_facts": 20,
        "scored_positions": len(rows),
        "query_boundary": "once per complete answer",
        "nll_weighting": "pooled target tokens including terminal, canonical plus all paraphrases",
        "failed_acquisitions_included": True,
    }


def relative(current, baseline):
    """Strict pairing; never discard a missing, failed, or nonfinite measurement."""
    for value in (current, baseline):
        if value.get("status") != "complete" or len(value["facts"]) != 20:
            raise ValueError("incomplete fixed probe assay")
        if len({r["item_id"] for r in value["facts"]}) != 20:
            raise ValueError("duplicate probe fact")
        if any(
            r["status"] != "ok" or r["es"] not in (0, 1) or not np.isfinite(r["gs"])
            for r in value["facts"]
        ):
            raise ValueError("failed fact probe")
    before = {r["key"]: r for r in baseline["tokens"]}
    after = {r["key"]: r for r in current["tokens"]}
    if (
        not before
        or len(before) != len(baseline["tokens"])
        or len(after) != len(current["tokens"])
        or before.keys() != after.keys()
        or [r["item_id"] for r in current["facts"]] != [r["item_id"] for r in baseline["facts"]]
    ):
        raise ValueError("fixed probe population changed")
    changes = []
    for key, row in after.items():
        old = before[key]
        if any(
            row[k] != old[k] for k in ("item_id", "prompt_index", "target_index", "target_token")
        ):
            raise ValueError("fixed probe token identity changed")
        if not all(np.isfinite(r[k]) for r in (row, old) for k in ("cap_nll", "original_nll")):
            raise FloatingPointError("nonfinite probe measurement")
        if row["original_nll"] != old["original_nll"]:
            raise ValueError("original base probe changed")
        changes.append(
            {
                **row,
                "delta_from_edit20": row["cap_nll"] - old["cap_nll"],
                "delta_from_original": row["cap_nll"] - row["original_nll"],
            }
        )
    values = np.asarray([r["delta_from_edit20"] for r in changes])
    exact = sum(r["es"] for r in current["facts"])
    mean_positive = float(np.maximum(values, 0).mean())
    fact_rows = []
    for fact in current["facts"]:
        local = [r["delta_from_edit20"] for r in changes if r["item_id"] == fact["item_id"]]
        fact_rows.append(
            {
                "item_id": fact["item_id"],
                "es": fact["es"],
                "gs": fact["gs"],
                "mean_delta_nats": float(np.mean(local)),
                "mean_positive_delta_nats": float(np.maximum(local, 0).mean()),
            }
        )
    return {
        "token_rows": changes,
        "fact_rows": fact_rows,
        "exact_answer_count": int(exact),
        "baseline_exact_answer_count": int(sum(r["es"] for r in baseline["facts"])),
        "paraphrase_retention_macro": float(np.mean([r["gs"] for r in current["facts"]])),
        "mean_delta_nats": float(values.mean()),
        "mean_positive_delta_nats": mean_positive,
        "max_positive_delta_nats": float(max(0, values.max())),
        "within_recovery_band": bool(
            mean_positive <= 0.01 and exact >= sum(r["es"] for r in baseline["facts"])
        ),
    }


def recovery(history):
    points = sorted(history)
    if not points:
        return {"status": "unmeasured"}
    if points != CADENCE[: len(points)]:
        raise ValueError("probe checkpoints must form the declared contiguous prefix")
    summaries = {t: relative(history[t], history[20]) for t in points}
    if points != CADENCE:
        return {
            "status": "provisional",
            "observed_checkpoints": points,
            "band_by_checkpoint": {str(t): r["within_recovery_band"] for t, r in summaries.items()},
            "recovered": None,
        }
    for i, t in enumerate(CADENCE[1:], 1):
        if all(summaries[later]["within_recovery_band"] for later in CADENCE[i:]):
            return {
                "status": "complete",
                "recovered": True,
                "first_sustained_checkpoint": t,
                "lag_interval_updates": [0 if t == 60 else CADENCE[i - 1] - 60, t - 60],
                "interval": "[0,0]" if t == 60 else "(lower,upper]",
                "right_censored": False,
            }
    return {
        "status": "complete",
        "recovered": False,
        "right_censored": True,
        "censor_after_updates": 40,
        "interval": "(40,infinity)",
    }
