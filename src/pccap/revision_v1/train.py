"""Stage 2 — differentiable episodic reference (R1-21; docs/revision_v1_losses.md).

Outer step over the reusable weights θ = {reader, controller} on labelled episodes. The base is frozen; every prefix's
write-free observation (features + cap-off logits) is computed once per episode without gradient (``featurize``), then
the loss terms L1–L3 are pure JAX functions of θ that call the base's jitted forward with the controller's writes, so
``jax.grad`` reaches θ through the base (exact backprop; no surrogate) — one GPT-2 forward/backward per query prefix,
accumulated to bound memory. Fast-step deltas, when supplied, enter as constants (first-order surrogate, declared).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np
import optax

from pccap.bases import gpt2_jax as g
from pccap.revision_v1.contracts import LabeledEpisode, RevisionCost
from pccap.revision_v1.controller import ControllerConfig, writes
from pccap.revision_v1.observations import answer_mask, observation_from_pass, prompt_mask
from pccap.revision_v1.reader import (
    ReaderConfig,
    initial_code,
    null_score,
    obs_arrays,
    pair_scores,
    query_embedding,
    record_key,
)

ANSWER_ROLES = ("new_paraphrase", "old_fact", "own_prompt")
PRESERVE_ROLES = ("near_miss", "unrelated")
NULL_ONLY_ROLES = ("unrelated_no_kl",)  # null target in L2 only (stream episodes: out-of-memory prompts without stored cap-off logits)
SKIPPED_ROLES = ("composition",)


@dataclass
class LossConfig:
    w_answer: float = 1.0
    w_retrieval: float = 1.0
    w_preserve: float = 1.0
    w_code_norm: float = 0.0
    fast_steps: int = 0  # 0 = reference (initial codes from prompt+answer); >0 is NOT implemented in the outer loop (rejected at construction)
    balance_null: bool = True  # L2: null-target and record-target queries carry equal total weight per episode

    def __post_init__(self):
        if self.fast_steps != 0:
            raise NotImplementedError("fast steps inside the outer loop are not implemented; run with fast_steps = 0 (R23-02)")


@dataclass
class PrefixFeat:
    ids: np.ndarray  # padded to the bucket length
    n: int
    target: int
    last: np.ndarray  # [taps, d]
    span: np.ndarray
    capoff_logits: np.ndarray | None  # [V] for preservation roles


@dataclass
class SupportFeat:
    record_id: str
    fact_id: str
    last: np.ndarray  # prompt observation (key)
    span: np.ndarray
    code_last: np.ndarray | None = None  # prompt+answer observation with the answer span (code; R23-02)
    code_span: np.ndarray | None = None
    fast_delta: np.ndarray | None = None


@dataclass
class QueryFeat:
    query_id: str
    role: str
    last: np.ndarray  # prompt observation (selection)
    span: np.ndarray
    prefixes: list[PrefixFeat]
    target_record: int  # index into supports, or -1 for null


@dataclass
class EpisodeFeatures:
    episode_id: str
    supports: list[SupportFeat]
    queries: list[QueryFeat]
    skipped: dict[str, int] = field(default_factory=dict)
    cost: RevisionCost = field(default_factory=lambda: RevisionCost(phase="learning"))


def featurize(base, enc, episode: LabeledEpisode, rc: ReaderConfig, include_own_prompt: bool = True, own_prompt_history: bool = False) -> EpisodeFeatures:
    """Write-free passes for every support prompt and every query prefix (charged to the learning column).

    ``include_own_prompt`` adds, for every support, a query equal to the support prompt with the taught answer as target
    (role ``own_prompt``): the evaluator's ES reads the item's own prompt, and without this role the null never sees an
    exact self-match during training (it then rejects own prompts that look like near-miss prompts)."""
    cost = RevisionCost(phase="learning")

    def observe(ids: np.ndarray, mask=None, want_logits: bool = False):
        fr = base.forward(ids, (), retain_sites=True, phase="learning", last_only=True)
        cost.add(fr.cost)
        cost.extra_pass_forwards += 1
        obs = observation_from_pass(fr, ids, mask, enc.base_hash, enc.encoder_version, rc.taps)
        last, span = obs_arrays(obs, rc)
        return np.asarray(last), np.asarray(span), (np.asarray(fr.logits, np.float32) if want_logits else None)

    supports_in = tuple(episode.inputs.support_history) + tuple(episode.inputs.new_support)
    supports, index = [], {}
    for s in supports_in:
        ids = np.asarray(s.prompt_ids, np.int32)
        last, span, _ = observe(ids)
        full = np.concatenate([ids, np.asarray(s.answer_ids, np.int32)])
        c_last, c_span, _ = observe(full, answer_mask(len(ids), len(full)))
        index[s.record_id] = len(supports)
        supports.append(SupportFeat(record_id=s.record_id, fact_id=s.fact_id, last=last, span=span, code_last=c_last, code_span=c_span))
    labels = {lab.query_id: lab for lab in episode.query_labels}
    queries, skipped = [], {}
    from pccap.revision_v1.contracts import PredictionQuery, QueryLabel
    extra_q, extra_l = [], []
    if include_own_prompt:
        for s in (supports_in if own_prompt_history else tuple(episode.inputs.new_support)):
            qid = f"own:{s.record_id}"
            extra_q.append(PredictionQuery(query_id=qid, prompt_ids=tuple(s.prompt_ids), prompt=s.prompt))
            extra_l.append(QueryLabel(query_id=qid, role="own_prompt", entity_ids=(s.entity_id,), family_id=s.family_id, target_ids=tuple(s.answer_ids), target=s.answer, target_source="support", supporting_record_ids=(s.record_id,)))
    labels.update({lab.query_id: lab for lab in extra_l})
    for q in tuple(episode.inputs.queries) + tuple(extra_q):
        lab = labels[q.query_id]
        if lab.role in SKIPPED_ROLES or lab.role not in ANSWER_ROLES + PRESERVE_ROLES:
            skipped[lab.role] = skipped.get(lab.role, 0) + 1
            continue
        if lab.role in ANSWER_ROLES and len(lab.supporting_record_ids) != 1:
            skipped[f"{lab.role}:multi_support"] = skipped.get(f"{lab.role}:multi_support", 0) + 1
            continue
        prompt = np.asarray(q.prompt_ids, np.int32)
        p_last, p_span, _ = observe(prompt)
        prefixes = []
        cur = prompt
        targets = [int(y) for y in np.asarray(lab.target_ids, np.int32)]
        if lab.role in PRESERVE_ROLES and not targets:
            targets = [-1]  # natural data carries no teacher continuation: preserve the distribution at the prompt's last position
        for y in targets:
            last, span, cl = observe(cur, prompt_mask(len(prompt), len(cur)), want_logits=lab.role in PRESERVE_ROLES)
            T = g.bucket_len(len(cur))
            prefixes.append(PrefixFeat(ids=g.pad_ids(cur, T), n=len(cur), target=int(y), last=last, span=span, capoff_logits=cl))
            if y >= 0:
                cur = np.concatenate([cur, np.int32([int(y)])])
        tgt = index[lab.supporting_record_ids[0]] if lab.role in ANSWER_ROLES else -1
        queries.append(QueryFeat(query_id=q.query_id, role=lab.role, last=p_last, span=p_span, prefixes=prefixes, target_record=tgt))
    return EpisodeFeatures(episode_id=episode.episode_id, supports=supports, queries=queries, skipped=skipped, cost=cost)


# ---------------------------------------------------------------------------------------------- pure-JAX losses
def _records(theta, rc: ReaderConfig, feats: EpisodeFeatures):
    keys = jnp.stack([record_key(theta["reader"], rc, jnp.asarray(s.last), jnp.asarray(s.span)) for s in feats.supports])
    codes = jnp.stack([initial_code(theta["reader"], rc, jnp.asarray(s.code_last if s.code_last is not None else s.last), jnp.asarray(s.code_span if s.code_span is not None else s.span))
                       + (0.0 if s.fast_delta is None else jax.lax.stop_gradient(jnp.asarray(s.fast_delta))) for s in feats.supports])
    return keys, codes


def _selection(theta, rc: ReaderConfig, keys, q_sel):
    scores = pair_scores(rc, q_sel, keys)
    kb = keys[jnp.argmax(scores)] if rc.pairwise_null else None
    null_logit = null_score(theta["reader"], rc, q_sel, kb)
    logits = jnp.concatenate([scores, null_logit[None]])
    probs = jax.nn.softmax(logits)
    return logits, probs[:-1], probs[-1]


def retrieval_loss(theta, rc: ReaderConfig, feats: EpisodeFeatures, balance_null: bool = True):
    """L2: CE over ALL episode records + null, per query; target = supporting record or null. With ``balance_null`` the
    null-target queries and the record-target queries each carry half of the episode's weight (the own-prompt role would
    otherwise outnumber the null targets 4:1)."""
    keys, _ = _records(theta, rc, feats)
    R = keys.shape[0]
    n_null = sum(1 for q in feats.queries if q.target_record < 0)
    n_rec = len(feats.queries) - n_null
    total = 0.0
    for q in feats.queries:
        q_sel = query_embedding(theta["reader"], rc, jnp.asarray(q.last), jnp.asarray(q.span))
        logits, _, _ = _selection(theta, rc, keys, q_sel)
        tgt = R if q.target_record < 0 else q.target_record
        if balance_null and n_null and n_rec:
            wq = 0.5 / (n_null if q.target_record < 0 else n_rec)
        else:
            wq = 1.0 / max(1, len(feats.queries))
        total = total + wq * (jax.nn.logsumexp(logits) - logits[tgt])
    return total


def prefix_loss(theta, rc: ReaderConfig, cc: ControllerConfig, base_params, base_cfg, feats: EpisodeFeatures, qi: int, ti: int):
    """L1 or L3 for one query prefix: corrected logits from the base with the controller's writes."""
    keys, codes = _records(theta, rc, feats)
    q = feats.queries[qi]
    pf = q.prefixes[ti]
    q_sel = query_embedding(theta["reader"], rc, jnp.asarray(q.last), jnp.asarray(q.span))
    _, w, null = _selection(theta, rc, keys, q_sel)
    code_mix = (w @ codes) / jnp.maximum(w.sum(), 1e-12)
    q_t = query_embedding(theta["reader"], rc, jnp.asarray(pf.last), jnp.asarray(pf.span))
    W, _ = writes(theta["controller"], cc, q_t, code_mix, 1.0 - null)
    logits, _, _ = g.forward_jit(base_params, jnp.asarray(pf.ids), jnp.int32(pf.n), W, base_cfg, False, True)
    if q.role in ANSWER_ROLES:
        return jax.nn.logsumexp(logits) - logits[pf.target], "answer"
    p_off = jax.nn.softmax(jnp.asarray(pf.capoff_logits))
    return jnp.sum(p_off * (jnp.log(p_off + 1e-30) - jax.nn.log_softmax(logits))), "preserve"


def episode_grads(theta, rc, cc, base_params, base_cfg, feats: EpisodeFeatures, lc: LossConfig):
    """Accumulated gradient of the weighted loss over one episode; returns (grads, metrics)."""
    metrics = {"answer": 0.0, "answer_n": 0, "preserve": 0.0, "preserve_n": 0, "retrieval": 0.0, "code_norm": 0.0}
    grads = jax.tree_util.tree_map(jnp.zeros_like, theta)

    def acc(gr, scale):
        return jax.tree_util.tree_map(lambda a, b: a + scale * b, grads, gr)

    if lc.w_retrieval:
        l, gr = jax.value_and_grad(retrieval_loss)(theta, rc, feats, lc.balance_null)
        metrics["retrieval"] = float(l)
        grads = acc(gr, lc.w_retrieval)
    for qi, q in enumerate(feats.queries):
        if q.role in NULL_ONLY_ROLES:
            continue
        for ti in range(len(q.prefixes)):
            (l, kind), gr = jax.value_and_grad(prefix_loss, has_aux=True)(theta, rc, cc, base_params, base_cfg, feats, qi, ti)
            metrics[kind] += float(l)
            metrics[f"{kind}_n"] += 1
            grads = acc(gr, lc.w_answer if kind == "answer" else lc.w_preserve)
    if lc.w_code_norm:
        def cn(th):
            _, codes = _records(th, rc, feats)
            return jnp.mean(jnp.sum(codes * codes, axis=1))
        l, gr = jax.value_and_grad(cn)(theta)
        metrics["code_norm"] = float(l)
        grads = acc(gr, lc.w_code_norm)
    # per-prefix means so that episodes of different sizes weigh equally
    n_ans, n_pre = max(1, metrics["answer_n"]), max(1, metrics["preserve_n"])
    metrics["answer"] = metrics["answer"] / n_ans
    metrics["preserve"] = metrics["preserve"] / n_pre
    return grads, metrics


@dataclass
class Trainer:
    rc: ReaderConfig
    cc: ControllerConfig
    base_params: dict
    base_cfg: object
    lc: LossConfig = field(default_factory=LossConfig)
    lr: float = 1e-4
    clip: float = 1.0
    weight_decay: float = 0.0

    def __post_init__(self):
        self.opt = optax.chain(optax.clip_by_global_norm(self.clip), optax.adamw(self.lr, weight_decay=self.weight_decay))

    def init(self, theta):
        return self.opt.init(theta)

    def outer_step(self, theta, opt_state, episodes: list[EpisodeFeatures]):
        """One optimizer step on a batch of featurized episodes (gradients averaged over episodes)."""
        total = None
        agg = {}
        for feats in episodes:
            gr, m = episode_grads(theta, self.rc, self.cc, self.base_params, self.base_cfg, feats, self.lc)
            total = gr if total is None else jax.tree_util.tree_map(jnp.add, total, gr)
            for k, v in m.items():
                agg[k] = agg.get(k, 0.0) + v
        total = jax.tree_util.tree_map(lambda x: x / len(episodes), total)
        gnorm = float(optax.global_norm(total))
        updates, opt_state = self.opt.update(total, opt_state, theta)
        theta = optax.apply_updates(theta, updates)
        metrics = {k: v / len(episodes) for k, v in agg.items()}
        metrics["grad_norm"] = gnorm
        return theta, opt_state, metrics
