"""R1-67: render an already computed Selection; no model/store calls or mutation."""

from __future__ import annotations

import math

import numpy as np


def selection_trace(selection, *, config=None):
    """Preserve legacy candidate fields and disclose the final hard gate.
    With RevisionConfig, infer the rare-gate verdict from the registered ordering:
    empty -> null/cosine thresholds -> rare-token gate. No DF or selection recomputation.
    Without config the rare-gate cause is unavailable, even when hard_null is known.
    """
    ids = list(selection.record_ids)
    weights = np.asarray(selection.weights)
    if weights.ndim != 1 or len(weights) != len(ids) or len(set(ids)) != len(ids):
        raise ValueError("candidate/weight inventory mismatch")
    if (
        any(not isinstance(x, str) or not x for x in ids)
        or not np.all(np.isfinite(weights))
        or np.any(weights < 0)
    ):
        raise ValueError("invalid candidates/weights")
    if not isinstance(selection.hard_null, (bool, np.bool_)):
        raise ValueError("explicit boolean hard_null required")
    null = float(selection.null_mass)
    if not math.isfinite(null) or not 0 <= null <= 1:
        raise ValueError("invalid null mass")
    length = selection.prompt_len
    if (
        not isinstance(length, (int, np.integer))
        or isinstance(length, (bool, np.bool_))
        or length < 1
    ):
        raise ValueError("positive prompt length required")
    score = float(selection.best_score) if selection.best_score is not None else None
    if score is not None and not math.isfinite(score):
        score = None
    hard = bool(selection.hard_null)
    index = int(np.argmax(weights)) if ids and weights.sum() > 0 else None
    rid = ids[index] if index is not None else None
    weight = float(weights[index]) if index is not None else None
    verdict = "unavailable"
    basis = "Selection does not store a separate rare-gate event; configuration not supplied"
    if config is not None:
        minimum = config.rare_overlap_min
        prior = null >= config.null_threshold
        if config.min_score is not None:
            if score is None:
                verdict = "unavailable"
                basis = "best score unavailable for configured cosine gate"
                return _render(ids, weights, length, score, null, hard, rid, weight, verdict, basis)
            prior = prior or score < config.min_score
        if not minimum:
            verdict = "disabled"
        elif not ids:
            verdict = "not_evaluated_empty_memory"
        elif prior:
            verdict = "not_evaluated_prior_gate"
        else:
            verdict = "rejected" if hard else "accepted"
        basis = "inferred from final Selection and registered RevisionConfig gate ordering; no recomputation"
    return _render(ids, weights, length, score, null, hard, rid, weight, verdict, basis)


def _render(ids, weights, length, score, null, hard, rid, weight, verdict, basis):
    return {
        "record_ids": ids,
        "null_mass": null,
        "best_score": score,
        "prompt_len": int(length),
        "hard_null": hard,
        "gate_accepted": not hard,
        "weights": [float(x) for x in weights],
        "selected_record_id": rid,
        "selected_weight": weight,
        "applied_record_ids": [] if hard else [r for r, w in zip(ids, weights) if w > 0],
        "applied_selected_weight": 0.0 if hard else weight,
        "rare_gate_verdict": verdict,
        "rare_gate_basis": basis,
        "definition": "selected_record_id is the pre-veto highest-weight candidate; gate acceptance is not proof of nonzero writes or changed generation",
    }
