"""Jitted, batched form of the episodic reference losses (same objective as train.py; needed at stream scale).

An EpisodeFeatures is packed into stacked arrays: supports [R, taps, d] (key and code observations), queries [Q, taps, d]
with a target index (R = null), and prefixes grouped by (bucket length, kind) so that each group runs one vmapped base
forward. Gradients are computed by one jitted call per group; compilation is per (R, Q, group shape) — fixed in stream
training. The retrieval loss (class-balanced) is added in the first group. Numerically the same loss as train.py's
per-prefix functions (tested on the tiny base).
"""

from __future__ import annotations

from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np
import optax

from pccap.bases import gpt2_jax as g
from pccap.revision_v1.controller import ControllerConfig, writes
from pccap.revision_v1.reader import (
    ReaderConfig,
    initial_code,
    null_score,
    pair_scores,
    query_embedding,
    record_key,
)
from pccap.revision_v1.train import (
    ANSWER_ROLES,
    NULL_ONLY_ROLES,
    PRESERVE_ROLES,
    EpisodeFeatures,
    LossConfig,
    lex_matrix,
)


@dataclass
class PackedEpisode:
    sup_last: np.ndarray
    sup_span: np.ndarray
    code_last: np.ndarray
    code_span: np.ndarray
    q_last: np.ndarray
    q_span: np.ndarray
    q_target: np.ndarray  # [Q] int; R for null
    q_is_null: np.ndarray  # [Q] bool
    q_valid: np.ndarray  # [Q] bool (R1-69: padded query rows are False and carry no loss weight)
    lex: np.ndarray  # [Q, R] lexical overlap features
    groups: list[dict]  # each: kind, ids [P,T], n [P], target [P], last/span [P,taps,d], q_index [P], capoff [P,V] (preserve only)


def _bucket_len(t: int, step: int = 16) -> int:
    """Prefix-length bucket (R1-69): lengths are padded up to a multiple of ``step`` so at most ~64 distinct shapes exist."""
    return int(-(-t // step) * step)


def _bucket_rows(p: int) -> int:
    """Row-count bucket (R1-69): 1, 2, 4, 8, then multiples of 8."""
    return p if p <= 2 else (4 if p <= 4 else int(-(-p // 8) * 8))


def _pad_rows(a: np.ndarray, rows: int) -> np.ndarray:
    return a if a.shape[0] >= rows else np.concatenate([a, np.zeros((rows - a.shape[0],) + a.shape[1:], a.dtype)])


def pack_episode(feats: EpisodeFeatures, vocab: int, rc_for_lex: ReaderConfig | None = None) -> PackedEpisode:
    R = len(feats.supports)
    sup_last = np.stack([s.last for s in feats.supports]).astype(np.float32)
    sup_span = np.stack([s.span for s in feats.supports]).astype(np.float32)
    code_last = np.stack([(s.code_last if s.code_last is not None else s.last) for s in feats.supports]).astype(np.float32)
    code_span = np.stack([(s.code_span if s.code_span is not None else s.span) for s in feats.supports]).astype(np.float32)
    q_last = np.stack([q.last for q in feats.queries]).astype(np.float32)
    q_span = np.stack([q.span for q in feats.queries]).astype(np.float32)
    q_target = np.asarray([R if q.target_record < 0 else q.target_record for q in feats.queries], np.int32)
    q_is_null = np.asarray([q.target_record < 0 for q in feats.queries], bool)
    Q = len(feats.queries)
    Qp = max(8, int(-(-Q // 8) * 8))  # R1-69: pad the query count to a multiple of 8 so the compiled shape set stays bounded
    q_valid = np.asarray([True] * Q + [False] * (Qp - Q), bool)
    if Qp > Q:
        q_last = np.concatenate([q_last, np.zeros((Qp - Q,) + q_last.shape[1:], q_last.dtype)])
        q_span = np.concatenate([q_span, np.zeros((Qp - Q,) + q_span.shape[1:], q_span.dtype)])
        q_target = np.concatenate([q_target, np.full(Qp - Q, R, np.int32)])
        q_is_null = np.concatenate([q_is_null, np.ones(Qp - Q, bool)])
    buckets: dict[tuple[int, str], list] = {}
    for qi, q in enumerate(feats.queries):
        if q.role in NULL_ONLY_ROLES:
            continue
        kind = "answer" if q.role in ANSWER_ROLES else ("preserve" if q.role in PRESERVE_ROLES else None)
        if kind is None:
            continue
        for pf in q.prefixes:
            buckets.setdefault((_bucket_len(int(pf.ids.shape[0])), kind), []).append((qi, pf))
    groups = []
    for (T, kind), rows in sorted(buckets.items()):
        P = _bucket_rows(len(rows))  # R1-69: pad rows to a bucket so the jitted executable set stays bounded (host memory)
        def padded(arr_list, fill, P=P):
            a = np.stack(arr_list)
            if P > a.shape[0]:
                a = np.concatenate([a, np.full((P - a.shape[0],) + a.shape[1:], fill, a.dtype)], axis=0)
            return a
        ids = np.stack([np.pad(np.asarray(pf.ids, np.int32), (0, T - int(pf.ids.shape[0]))) for _, pf in rows])  # pad token 0; n keeps the valid length
        grp = {"kind": kind, "T": T, "ids": padded(list(ids), 0).astype(np.int32), "n": padded([np.int32(pf.n) for _, pf in rows], 1).astype(np.int32),
               "target": padded([np.int32(max(pf.target, 0)) for _, pf in rows], 0).astype(np.int32), "last": padded([pf.last for _, pf in rows], 0.0).astype(np.float32),
               "span": padded([pf.span for _, pf in rows], 0.0).astype(np.float32), "q_index": padded([np.int32(qi) for qi, _ in rows], 0).astype(np.int32),
               "weight": np.asarray([1.0] * len(rows) + [0.0] * (P - len(rows)), np.float32), "rows_valid": len(rows)}
        if kind == "preserve":
            grp["capoff"] = padded([np.asarray(pf.capoff_logits, np.float32) for _, pf in rows], 0.0)
        groups.append(grp)
    return PackedEpisode(sup_last, sup_span, code_last, code_span, q_last, q_span, q_target, q_is_null, q_valid, _pad_rows(lex_matrix(rc_for_lex, feats) if rc_for_lex is not None else np.zeros((len(feats.queries), R), np.float32), Qp), groups)


def _make_fns(rc: ReaderConfig, cc: ControllerConfig, base_cfg, lc: LossConfig):
    v_key = jax.vmap(lambda p, last, span: record_key(p, rc, last, span), in_axes=(None, 0, 0))
    v_code = jax.vmap(lambda p, last, span: initial_code(p, rc, last, span), in_axes=(None, 0, 0))
    v_query = jax.vmap(lambda p, last, span: query_embedding(p, rc, last, span), in_axes=(None, 0, 0))

    def selection(theta, keys, q, lex_row):
        scores = pair_scores(rc, q, keys)
        if rc.lexical and "lex" in theta["reader"]:
            scores = scores + theta["reader"]["lex"]["score_w"] * lex_row
        kb = keys[jnp.argmax(scores)] if rc.pairwise_null else None
        nl = null_score(theta["reader"], rc, q, kb)
        if rc.lexical and "lex" in theta["reader"]:
            nl = nl - theta["reader"]["lex"]["null_w"] * jnp.max(lex_row)
        logits = jnp.concatenate([scores, nl[None]])
        probs = jax.nn.softmax(logits)
        return logits, probs[:-1], probs[-1]

    def retrieval(theta, keys, q_emb, q_target, q_is_null, lex, q_valid=None):
        logits = jax.vmap(lambda q, lr: selection(theta, keys, q, lr)[0])(q_emb, lex)  # [Q, R+1]
        ce = jax.vmap(lambda lg, t: jax.nn.logsumexp(lg) - lg[t])(logits, q_target)
        valid = jnp.ones(q_is_null.shape, bool) if q_valid is None else q_valid
        n_valid = jnp.maximum(jnp.sum(valid), 1)
        n_null = jnp.sum(q_is_null & valid)
        n_rec = n_valid - n_null
        if lc.balance_null:
            w = jnp.where(q_is_null, 0.5 / jnp.maximum(n_null, 1), 0.5 / jnp.maximum(n_rec, 1))
            w = jnp.where((n_null > 0) & (n_rec > 0), w, 1.0 / n_valid)
        else:
            w = jnp.full(q_is_null.shape, 1.0 / n_valid)
        return jnp.sum(jnp.where(valid, w, 0.0) * ce)

    def group_loss(theta, base_params, packed_sup, q_last, q_span, q_target, q_is_null, q_valid, lex, grp_ids, grp_n, grp_target, grp_last, grp_span, grp_q_index, grp_capoff, grp_weight, kind: str, with_retrieval: bool):
        sup_last, sup_span, code_last, code_span = packed_sup
        keys = v_key(theta["reader"], sup_last, sup_span)
        codes = v_code(theta["reader"], code_last, code_span)
        q_emb = v_query(theta["reader"], q_last, q_span)
        total = 0.0
        if with_retrieval and lc.w_retrieval:
            total = total + lc.w_retrieval * retrieval(theta, keys, q_emb, q_target, q_is_null, lex, q_valid)

        def one(ids, n, target, last, span, qi, capoff_row):
            _, w, null = selection(theta, keys, q_emb[qi], lex[qi])
            code_mix = (w @ codes) / jnp.maximum(w.sum(), 1e-12)
            q_t = query_embedding(theta["reader"], rc, last, span)
            W, _ = writes(theta["controller"], cc, q_t, code_mix, 1.0 - null)
            logits, _, _ = g.forward_jit(base_params, ids, n, W, base_cfg, False, True)
            if kind == "answer":
                surprisal = jax.nn.logsumexp(logits) - logits[target]
                if lc.kappa > 0:  # HT-3 coupled surprisal: -ln_k p = (1 - p^k) / k, bounded by 1/k
                    return (1.0 - jnp.exp(-lc.kappa * surprisal)) / lc.kappa
                if lc.clip_surprisal is not None:
                    return jnp.minimum(surprisal, lc.clip_surprisal)
                return surprisal
            p_off = jax.nn.softmax(capoff_row)
            log_on = jax.nn.log_softmax(logits)
            if lc.kappa > 0:  # HT-3 coupled divergence: sum p_off (ln_k p_off - ln_k p_on)
                lnk = lambda lp: (jnp.exp(lc.kappa * lp) - 1.0) / lc.kappa  # noqa: E731  (ln_k of p from log p)
                return jnp.sum(p_off * (lnk(jnp.log(p_off + 1e-30)) - lnk(log_on)))
            return jnp.sum(p_off * (jnp.log(p_off + 1e-30) - log_on))

        per = jax.vmap(one)(grp_ids, grp_n, grp_target, grp_last, grp_span, grp_q_index, grp_capoff) * grp_weight  # padded rows weigh 0
        weight = lc.w_answer if kind == "answer" else lc.w_preserve
        return total + weight * jnp.sum(per), jnp.sum(per)

    jitted = {}

    def get(kind: str, with_retrieval: bool):
        key = (kind, with_retrieval)
        if key not in jitted:
            jitted[key] = jax.jit(jax.value_and_grad(lambda th, *a: group_loss(th, *a, kind=kind, with_retrieval=with_retrieval), has_aux=True), static_argnums=())
        return jitted[key]

    return get, retrieval, v_key, v_query


class FastTrainer:
    """Drop-in for train.Trainer at stream scale: same losses, jitted per (kind, shapes)."""

    def __init__(self, rc: ReaderConfig, cc: ControllerConfig, base_params, base_cfg, lc: LossConfig | None = None, lr: float = 1e-4, clip: float = 1.0, weight_decay: float = 0.0, ledger=None):
        self.rc, self.cc, self.base_params, self.base_cfg, self.lc = rc, cc, base_params, base_cfg, lc or LossConfig()
        self.ledger = ledger  # R50-09: outer answer/preservation work (one forward + one reverse per prefix) is charged when a ledger is given
        self.vocab = int(base_cfg.vocab)
        self.get, self._retrieval, self._v_key, self._v_query = _make_fns(rc, cc, base_cfg, self.lc)
        self.opt = optax.chain(optax.clip_by_global_norm(clip), optax.adamw(lr, weight_decay=weight_decay))
        self._jit_retrieval = jax.jit(jax.value_and_grad(lambda th, sl, ss, ql, qs, qt, qn, lx, qv: self.lc.w_retrieval * self._retrieval(th, self._v_key(th["reader"], sl, ss), self._v_query(th["reader"], ql, qs), qt, qn, lx, qv)))

    def init(self, theta):
        return self.opt.init(theta)

    def episode_grads(self, theta, feats: EpisodeFeatures):
        pe = pack_episode(feats, self.vocab, self.rc)
        packed_sup = (jnp.asarray(pe.sup_last), jnp.asarray(pe.sup_span), jnp.asarray(pe.code_last), jnp.asarray(pe.code_span))
        q_last, q_span, q_target, q_is_null = (jnp.asarray(pe.q_last), jnp.asarray(pe.q_span), jnp.asarray(pe.q_target), jnp.asarray(pe.q_is_null))
        q_valid = jnp.asarray(pe.q_valid)
        lex = jnp.asarray(pe.lex)
        metrics = {"answer": 0.0, "answer_n": 0, "preserve": 0.0, "preserve_n": 0, "retrieval": 0.0, "code_norm": 0.0}
        grads = jax.tree_util.tree_map(jnp.zeros_like, theta)
        with_ret = bool(self.lc.w_retrieval)
        if not pe.groups and with_ret:
            l, gr = self._jit_retrieval(theta, packed_sup[0], packed_sup[1], q_last, q_span, q_target, q_is_null, lex, q_valid)
            metrics["retrieval"] = float(l) / max(self.lc.w_retrieval, 1e-12)
            return gr, metrics
        for gi, grp in enumerate(pe.groups):
            capoff = jnp.asarray(grp["capoff"]) if grp["kind"] == "preserve" else jnp.zeros((grp["ids"].shape[0], 1), jnp.float32)
            fn = self.get(grp["kind"], with_ret and gi == 0)
            (l, per_sum), gr = fn(theta, self.base_params, packed_sup, q_last, q_span, q_target, q_is_null, q_valid, lex, jnp.asarray(grp["ids"]), jnp.asarray(grp["n"]), jnp.asarray(grp["target"]),
                                  jnp.asarray(grp["last"]), jnp.asarray(grp["span"]), jnp.asarray(grp["q_index"]), capoff, jnp.asarray(grp["weight"]))
            grads = jax.tree_util.tree_map(jnp.add, grads, gr)
            if self.ledger is not None:
                from pccap.contracts import CostRecord
                P = int(grp.get("rows_valid", grp["ids"].shape[0]))  # padded rows are not charged (they are computed but carry no information)
                self.ledger.charge(CostRecord(phase="learning", full_forwards=P, reverses=P, tokens=int(np.sum(grp["n"][:P]))))
            metrics[grp["kind"]] += float(per_sum)
            metrics[f"{grp['kind']}_n"] += int(grp.get("rows_valid", grp["ids"].shape[0]))
            if gi == 0 and with_ret:
                metrics["retrieval"] = float(l - (self.lc.w_answer if grp["kind"] == "answer" else self.lc.w_preserve) * per_sum) / self.lc.w_retrieval
        metrics["answer"] /= max(1, metrics["answer_n"])
        metrics["preserve"] /= max(1, metrics["preserve_n"])
        return grads, metrics

    def outer_step(self, theta, opt_state, episodes: list[EpisodeFeatures]):
        total, agg = None, {}
        for feats in episodes:
            gr, m = self.episode_grads(theta, feats)
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
