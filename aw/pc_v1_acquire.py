"""PC-2: replace ONLY v5 delta credit; retain the fixed reader and BP base.

Preparation and ItemOutcome conversion reuse the installed functions with private
global dictionaries. No shared module or base method is monkeypatched. The unused
initial code-gradient calculation of the v5 path remains in both arms for parity;
this is PC-derived delta acquisition, not a backpropagation-free reader.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import json
from functools import partial
from types import FunctionType

import numpy as np

from pccap.contracts import CostRecord, SiteId, Write
from pccap.revision_v1 import adapt as original
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.memory import CapacityError


def _private_binding(fn, **overrides):
    namespace = dict(fn.__globals__)
    namespace.update(overrides)
    return FunctionType(fn.__code__, namespace, fn.__name__, fn.__defaults__, fn.__closure__)


def _failed_credit_cost(base, before):
    """EPCBase charges its ledger even when inference raises for nonfinite energy."""
    after = base.ledger.totals()["learning"]
    return CostRecord(**{k: ("learning" if k == "phase" else
                            after[k] if k == "peak_mem_mib" else after[k] - before[k])
                         for k in CostRecord.__dataclass_fields__})


def _delta_steps(learner, rec, prefixes, q_emb, answer, code, loss0, fast, cost, trace, *, iters):
    """Same arithmetic/acceptance/rollback as adapt._delta_steps, with error credit."""
    base, cc = learner.base, learner.cfg.controller
    b = np.asarray(cc.bank_scales, np.float32)
    n_banks, d = cc.n_banks, cc.d
    deltas = np.zeros((len(prefixes), n_banks, d), np.float32)
    per_after, steps_total = [], 0

    def write_list(w, p):
        return [Write(SiteId(m, learner.blocks[m], p), np.asarray(w[m - 1], np.float32))
                for m in range(1, n_banks + 1)]

    def bounded(dl):
        agg = float(np.sum(np.linalg.norm(dl, axis=1) / b))
        return dl * np.float32(cc.A / agg) if agg > cc.A else dl

    for t, (ids, y) in enumerate(zip(prefixes, answer)):
        p = len(ids) - 1
        loss, fr = base.loss(ids, int(y), [], phase="learning")
        cost.add(fr.cost)
        current_loss = float(loss)
        for _ in range(fast.delta_steps):
            if current_loss <= fast.tau:
                break
            before = base.ledger.totals()["learning"]
            try:
                er = base.infer_errors(ids, int(y), writes=write_list(deltas[t], p),
                                       iters=iters, phase="learning")
            except FloatingPointError:
                cost.add(_failed_credit_cost(base, before))
                trace.rolled_back_reason = "non_finite_credit"
                break
            cost.add(er.cost)  # iters+1 forwards AND reverses; includes terminal residual
            grads = {s: -np.asarray(e, np.float32) for s, e in er.site_errors.items()}
            if any(not np.all(np.isfinite(g)) for g in grads.values()):
                trace.rolled_back_reason = "non_finite_credit"
                break
            for m in range(1, n_banks + 1):
                grad = grads[SiteId(m, learner.blocks[m], p)]
                if grad.shape != (d,):
                    raise ValueError("unexpected PC site-error shape")
                n = float(np.linalg.norm(grad))
                if n > 0:
                    deltas[t, m - 1] -= np.float32(fast.delta_lr * b[m - 1]) * grad / np.float32(n)
            deltas[t] = bounded(deltas[t])
            if not np.all(np.isfinite(deltas[t])):
                trace.rolled_back_reason = "non_finite_delta"
                break
            loss, fr = base.loss(ids, int(y), write_list(deltas[t], p), phase="learning")
            cost.add(fr.cost)
            current_loss = float(loss)  # NEVER the clamped/settled loss
            steps_total += 1
            if not np.isfinite(current_loss):
                trace.rolled_back_reason = "non_finite_loss"
                break
        per_after.append(current_loss)
        if trace.rolled_back_reason is not None:
            break
    trace.steps_used = steps_total
    mean_loss = float(np.mean(per_after)) if per_after else float("nan")
    trace.per_step_loss.append(mean_loss)
    if trace.rolled_back_reason is None and mean_loss < loss0 - fast.improvement_abs:
        try:
            learner.store.set_delta(rec.record_id, deltas)
        except CapacityError:
            learner.store.remove(rec.record_id, restore=trace.superseded)
            trace.rolled_back_reason = "delta_capacity"
            trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
            return trace, cost
        trace.accepted = True
        trace.loss_after, trace.per_prefix_loss_after = mean_loss, per_after
    elif trace.rolled_back_reason is not None:
        learner.store.remove(rec.record_id, restore=trace.superseded)
        trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
    else:
        trace.rolled_back_reason = "no_improvement"
        trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
    return trace, cost


def adapt_record(learner, support, fast, *, credit=None, iters=None):
    """Only the fixed-v5 explicit-delta rule is admitted by this supplemental seam."""
    credit = credit if credit is not None else getattr(learner, "acquisition_credit", "adjoint")
    iters = iters if iters is not None else getattr(learner, "credit_iters", 8)
    if credit not in ("adjoint", "error") or type(iters) is not int or iters < 1:
        raise ValueError("choose adjoint/error credit and a positive integer horizon")
    if fast.steps != 0 or fast.delta_steps <= 0:
        raise ValueError("PC-2 requires the v5 delta-only acquisition rule")
    if credit == "adjoint":
        return original.adapt_record(learner, support, fast)
    if not callable(getattr(learner.base, "infer_errors", None)) or getattr(learner.base, "descent_sign", None) != 1:
        raise ValueError("error credit requires the corrected EPCBase interface with descent_sign=+1")
    kernel = _private_binding(original.adapt_record, _delta_steps=partial(_delta_steps, iters=iters))
    return kernel(learner, support, fast)


class PCRevisionCap(RevisionCap):
    """Prediction is inherited unchanged. Supply the SAME v5 theta in both arms.

    On the real base, construct EPCBase with the original BP parameters/snapshot
    in BOTH arms. Do not load the regenerated ePC checkpoint used by PC-1.
    """

    def __init__(self, *args, acquisition_credit="adjoint", credit_iters=8, **kwargs):
        if acquisition_credit not in ("adjoint", "error") or type(credit_iters) is not int or credit_iters < 1:
            raise ValueError("invalid acquisition credit configuration")
        self.acquisition_credit, self.credit_iters = acquisition_credit, credit_iters
        super().__init__(*args, **kwargs)
        if self.cfg.fast.steps != 0 or self.cfg.fast.delta_steps <= 0:
            raise ValueError("PC-2 requires delta-only v5 acquisition")

    update_item = _private_binding(RevisionCap.update_item, adapt_record=adapt_record)

    def semantic_config(self):
        ordinary = super().semantic_config()
        if self.acquisition_credit == "adjoint":
            return ordinary  # original v5 checkpoint/state identity is preserved
        config = json.loads(ordinary)
        config["pc_acquisition"] = {"credit": "error", "iters": self.credit_iters,
                                     "error_lr": self.base.error_lr, "energy": "SD-24 corrected"}
        return json.dumps(config, default=str, sort_keys=True)
