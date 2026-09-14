"""Support-only fast adaptation of one record's fact code (design §adapt; guide §1 "fast rule").

The fast rule may change exactly one thing: the code of the record being taught (a new record, or the revision that
supersedes an older record of the same fact). Loss = teacher-forced NLL of the support answer under the controller's
writes with the record forced (applicability 1, non-null mass 1), summed over the answer prefixes. Gradients reach the
code through the base's adjoint (dL/d writes, one reverse pass per prefix and step) and a VJP through the controller.
Accepted-step rule: the code is kept only if the final loss is below the initial loss; non-finite → rollback; optional
norm bound. Every base call is charged to the learning column; counts are returned for the item record.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import jax.numpy as jnp
import numpy as np

from pccap.contracts import SiteId, Write
from pccap.revision_v1.contracts import MemoryRecord, RevisionCost, SupportExample, support_prefix
from pccap.revision_v1.observations import answer_mask, observation_from_pass, prompt_mask
from pccap.revision_v1.reader import initial_code, obs_arrays, record_key


@dataclass
class FastConfig:
    steps: int = 3  # gradient steps on the record CODE (through the controller)
    lr: float = 1e-2
    code_norm_max: float | None = None  # bound on ‖code‖ (None: unbounded)
    improvement_abs: float = 1e-8
    delta_steps: int = 0  # v0-style steps on the record's explicit DELTA write (base adjoint, normalized per site)
    delta_lr: float = 0.1  # step size in units of b_m along the normalized site gradient (one step = v0's per-bank share at A/3)
    tau: float = 0.1  # stop the delta steps once the mean support loss is below tau


@dataclass
class AdaptTrace:
    record_id: str
    superseded: str | None
    loss_before: float
    loss_after: float
    per_step_loss: list[float] = field(default_factory=list)
    per_prefix_loss_after: list[float] = field(default_factory=list)
    accepted: bool = False
    rolled_back_reason: str | None = None
    steps_used: int = 0
    reverses: int = 0
    forwards: int = 0


def adapt_record(learner, support: SupportExample, fast: FastConfig) -> tuple[AdaptTrace, RevisionCost]:
    """Teach one support example. Mutates only ``learner.store`` (one new record; one supersession at most)."""
    base, params, rc = learner.base, learner.params, learner.cfg.reader
    cost = RevisionCost(phase="learning")
    prompt = np.asarray(support.prompt_ids, np.int32)
    answer = np.asarray(support.answer_ids, np.int32)
    if prompt.size == 0 or answer.size == 0:
        raise ValueError("support needs a prompt and an answer")
    # record key from the support PROMPT observation; initial code from the full support (prompt + answer) observation with the
    # answer span as the summary mask, so the taught answer enters memory even with zero fast steps (R23-02)
    fr0 = base.forward(prompt, (), retain_sites=True, phase="learning", last_only=True)
    cost.add(fr0.cost)
    cost.extra_pass_forwards += 1
    obs0 = observation_from_pass(fr0, prompt, None, learner.enc.base_hash, learner.enc.encoder_version, rc.taps)
    last0, span0 = obs_arrays(obs0, rc)
    key = np.asarray(record_key(params["reader"], rc, last0, span0), np.float32)
    full = np.concatenate([prompt, answer])
    fr_full = base.forward(full, (), retain_sites=True, phase="learning", last_only=True)
    cost.add(fr_full.cost)
    cost.extra_pass_forwards += 1
    obs_full = observation_from_pass(fr_full, full, answer_mask(len(prompt), len(full)), learner.enc.base_hash, learner.enc.encoder_version, rc.taps)
    code0 = np.asarray(initial_code(params["reader"], rc, *obs_arrays(obs_full, rc)), np.float32)
    rec = MemoryRecord(record_id=support.record_id, fact_id=support.fact_id, revision_id=int(support.revision), created_order=-1,
                       key=key, code=code0.copy(), provenance=(support.record_id,), source_ids=prompt.copy())
    older = [r for r in learner.store.active_records() if r.fact_id == support.fact_id]
    superseded = None
    if older:
        old = max(older, key=lambda r: r.revision_id)
        if rec.revision_id <= old.revision_id:
            rec.revision_id = old.revision_id + 1
        learner.store.supersede(old.record_id, rec)
        superseded = old.record_id
    else:
        learner.store.add(rec)
    cost.records_touched += 1
    # answer-prefix observations (write-free passes) and query embeddings
    prefixes = [support_prefix(support, t) for t in range(len(answer))]
    qs = []
    for ids in prefixes:
        fr = base.forward(ids, (), retain_sites=True, phase="learning", last_only=True)
        cost.add(fr.cost)
        cost.extra_pass_forwards += 1
        obs = observation_from_pass(fr, ids, prompt_mask(len(prompt), len(ids)), learner.enc.base_hash, learner.enc.encoder_version, rc.taps)
        qs.append(tuple(obs_arrays(obs, rc)))
    q_emb = [learner.jit_query(params["reader"], last, span) for last, span in qs]

    def write_list(W: np.ndarray, p: int) -> list[Write]:
        return [Write(SiteId(m, learner.blocks[m], p), np.asarray(W[m - 1], np.float32)) for m in (1, 2, 3)]

    def losses_and_grad(code: np.ndarray) -> tuple[float, list[float], np.ndarray]:
        total, per, g_code = 0.0, [], np.zeros_like(code)
        for ids, q, y in zip(prefixes, q_emb, answer):
            W, vjp = learner.vjp_writes(params["controller"], q, jnp.asarray(code))
            grads, loss, _ = base.adjoint(ids, int(y), write_list(np.asarray(W), len(ids) - 1), phase="learning", return_loss=True)
            cost.reverses += 1
            cost.full_forwards += 1
            dW = jnp.asarray(np.stack([np.asarray(grads[SiteId(m, learner.blocks[m], len(ids) - 1)], np.float32) for m in (1, 2, 3)]))
            g_code = g_code + np.asarray(vjp(dW)[0], np.float32)
            total += float(loss)
            per.append(float(loss))
        return total / len(prefixes), per, g_code

    def losses_only(code: np.ndarray) -> tuple[float, list[float]]:
        total, per = 0.0, []
        for ids, q, y in zip(prefixes, q_emb, answer):
            W = learner.jit_writes(params["controller"], q, jnp.asarray(code), jnp.asarray(1.0))
            loss, fr = base.loss(ids, int(y), write_list(np.asarray(W), len(ids) - 1), phase="learning")
            cost.add(fr.cost)
            total += float(loss)
            per.append(float(loss))
        return total / len(prefixes), per

    trace = AdaptTrace(record_id=rec.record_id, superseded=superseded, loss_before=float("nan"), loss_after=float("nan"))
    code = code0.copy()
    loss0, _, g = losses_and_grad(code)
    trace.loss_before = loss0
    trace.per_step_loss.append(loss0)
    if fast.steps == 0 and fast.delta_steps > 0:
        return _delta_steps(learner, rec, prefixes, q_emb, answer, code, loss0, fast, cost, trace)
    for step in range(fast.steps):
        new = code - np.float32(fast.lr) * g
        if fast.code_norm_max is not None:
            n = float(np.linalg.norm(new))
            if n > fast.code_norm_max:
                new = new * np.float32(fast.code_norm_max / n)
        if not np.all(np.isfinite(new)):
            trace.rolled_back_reason = "non_finite_code"
            break
        code = new
        trace.steps_used = step + 1
        if step + 1 < fast.steps:
            loss_s, _, g = losses_and_grad(code)
            trace.per_step_loss.append(loss_s)
    loss_after, per_after = losses_only(code)
    trace.per_step_loss.append(loss_after)
    if trace.rolled_back_reason is None and np.isfinite(loss_after) and loss_after < loss0 - fast.improvement_abs:
        learner.store.set_code(rec.record_id, code)
        trace.accepted = True
        trace.loss_after, trace.per_prefix_loss_after = loss_after, per_after
    elif trace.rolled_back_reason == "non_finite_code" or not np.isfinite(loss_after):
        # R23-04: a non-finite update is a failed edit — remove the record and restore the superseded one
        learner.store.remove(rec.record_id, restore=superseded)
        trace.rolled_back_reason = trace.rolled_back_reason or "non_finite_loss"
        trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
    else:
        # no improvement from the fast steps: the record stays with its initial (answer-derived) code; the supersession stands
        trace.rolled_back_reason = "no_improvement"
        trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
    return trace, cost


def _delta_steps(learner, rec, prefixes, q_emb, answer, code, loss0, fast, cost, trace):
    """v0-style acquisition on the record's explicit delta write: at every step, evaluate the base adjoint at the bounded
    total write (controller + delta) for each support prefix, step the delta along the normalized site gradient (size
    delta_lr·b_m per site), then project the total write back onto the aggregate bound. Accept if the support loss fell."""
    base, params, cc = learner.base, learner.params, learner.cfg.controller
    b = np.asarray(cc.bank_scales, np.float32)
    n_banks, d = cc.n_banks, cc.d
    delta = np.zeros((n_banks, d), np.float32)

    def total_write(q, dl):
        W = np.asarray(learner.jit_writes_with_delta(params["controller"], q, jnp.asarray(code), jnp.asarray(dl), jnp.asarray(1.0)), np.float32)
        return W

    def write_list(W, p):
        return [Write(SiteId(m, learner.blocks[m], p), np.asarray(W[m - 1], np.float32)) for m in range(1, n_banks + 1)]

    def losses_only(dl):
        per = []
        for ids, q, y in zip(prefixes, q_emb, answer):
            loss, fr = base.loss(ids, int(y), write_list(total_write(q, dl), len(ids) - 1), phase="learning")
            cost.add(fr.cost)
            per.append(float(loss))
        return float(np.mean(per)), per

    L = loss0
    for step in range(fast.delta_steps):
        g_sum = np.zeros_like(delta)
        for ids, q, y in zip(prefixes, q_emb, answer):
            grads = base.adjoint(ids, int(y), write_list(total_write(q, delta), len(ids) - 1), phase="learning")
            cost.reverses += 1
            cost.full_forwards += 1
            for m in range(1, n_banks + 1):
                g_sum[m - 1] += np.asarray(grads[SiteId(m, learner.blocks[m], len(ids) - 1)], np.float32)
        for m in range(n_banks):
            n = float(np.linalg.norm(g_sum[m]))
            if n > 0:
                delta[m] -= np.float32(fast.delta_lr * b[m]) * g_sum[m] / np.float32(n)
        # keep the delta itself inside the aggregate bound (the read applies the bound to the total write again)
        agg = float(np.sum(np.linalg.norm(delta, axis=1) / b))
        if agg > cc.A:
            delta *= np.float32(cc.A / agg)
        if not np.all(np.isfinite(delta)):
            trace.rolled_back_reason = "non_finite_delta"
            break
        L, per = losses_only(delta)
        trace.per_step_loss.append(L)
        trace.steps_used = step + 1
        if not np.isfinite(L):
            trace.rolled_back_reason = "non_finite_loss"
            break
        if L <= fast.tau:
            break
    if trace.rolled_back_reason is None and L < loss0 - fast.improvement_abs:
        learner.store.set_delta(rec.record_id, delta)
        trace.accepted = True
        trace.loss_after, trace.per_prefix_loss_after = L, per
    elif trace.rolled_back_reason is not None:
        learner.store.remove(rec.record_id, restore=trace.superseded)
        trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
    else:
        trace.rolled_back_reason = "no_improvement"
        trace.loss_after, trace.per_prefix_loss_after = loss0, [float("nan")] * len(prefixes)
    return trace, cost
