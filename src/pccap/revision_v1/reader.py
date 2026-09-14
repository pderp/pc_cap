"""Learned reader with an explicit null (design §reader; guide §1).

Pure JAX functions over a params pytree. One siamese tap encoder maps an observation (per tap: last-position residual
and prompt-span summary, both 768-d) to a 256-d embedding; separate heads produce the query embedding, the record key
and the initial fact code. Applicability over the top-k candidates is a softmax over k dot-product scores plus one learned
null logit; ``null_mass`` is the probability of "no record applies". A hard null (no candidates, or null chosen at
evaluation) yields zero non-null mass, which the controller turns into exactly zero writes.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np

from pccap.revision_v1.contracts import TAPS, Observation


@dataclass(frozen=True)
class ReaderConfig:
    d: int = 768
    taps: tuple[int, ...] = TAPS
    width: int = 256
    hidden: int = 256
    d_code: int = 256
    top_k: int = 4
    null_bias: float = 0.0
    temperature: float = 1.0
    tie_heads: bool = True  # key head == query head (siamese): an identical observation always scores itself maximally
    cosine: bool = True  # scores on L2-normalized embeddings (self-match = 1 is the maximum; the store retrieves by the same score)
    score_scale: float = 10.0  # inverse temperature for cosine scores (cosine ∈ [-1, 1] needs a scale to be decisive)
    pairwise_null: bool = True  # the null logit sees the query AND the best-matching key (near-neighbour rejection needs a pairwise decision)
    lexical: bool = True  # M4: token overlap between the query and a record's support prompt enters the score and the null
    query_null: bool = True  # query-only linear null term; False = pairwise + lexical terms only (domain-robust null)
    stop_tokens: tuple[int, ...] = ()  # tokens ignored by the overlap (document-frequent); part of the semantic configuration


def _dense(key, n_in: int, n_out: int, scale: float | None = None) -> dict:
    s = (1.0 / np.sqrt(n_in)) if scale is None else scale
    return {"w": jax.random.normal(key, (n_in, n_out), jnp.float32) * s, "b": jnp.zeros((n_out,), jnp.float32)}


def _mlp(key, sizes: tuple[int, ...]) -> list[dict]:
    keys = jax.random.split(key, len(sizes) - 1)
    return [_dense(k, a, b) for k, a, b in zip(keys, sizes[:-1], sizes[1:])]


def _apply_mlp(layers: list[dict], x):
    for i, layer in enumerate(layers):
        x = x @ layer["w"] + layer["b"]
        if i + 1 < len(layers):
            x = jax.nn.gelu(x)
    return x


def init_reader(key, cfg: ReaderConfig) -> dict:
    k_tap, k_q, k_k, k_c, k_n = jax.random.split(key, 5)
    tap_keys = jax.random.split(k_tap, len(cfg.taps))
    return {
        "tap": {str(m): _dense(tk, 2 * cfg.d, cfg.width) for m, tk in zip(cfg.taps, tap_keys)},
        "query_head": _mlp(k_q, (cfg.width, cfg.hidden, cfg.width)),
        **({} if cfg.tie_heads else {"key_head": _mlp(k_k, (cfg.width, cfg.hidden, cfg.width))}),
        "code_head": _mlp(k_c, (cfg.width, cfg.hidden, cfg.d_code)),
        "null": {"w": jax.random.normal(k_n, (cfg.width,), jnp.float32) / np.sqrt(cfg.width), "b": jnp.asarray(cfg.null_bias, jnp.float32)},
        **({"null_pair": _mlp(jax.random.fold_in(k_n, 1), (3 * cfg.width, cfg.hidden, 1))} if cfg.pairwise_null else {}),
        **({"lex": {"score_w": jnp.asarray(5.0, jnp.float32), "null_w": jnp.asarray(5.0, jnp.float32)}} if cfg.lexical else {}),
    }


def _ln(x, eps: float = 1e-5):
    mu = x.mean(-1, keepdims=True)
    c = x - mu
    return c / jnp.sqrt((c * c).mean(-1, keepdims=True) + eps)


def obs_arrays(obs: Observation, cfg: ReaderConfig) -> tuple[jnp.ndarray, jnp.ndarray]:
    """Stack an observation into [n_taps, d] last and span arrays (float32)."""
    last = jnp.asarray(np.stack([obs.last[m] for m in cfg.taps]), jnp.float32)
    span = jnp.asarray(np.stack([obs.span[m] for m in cfg.taps]), jnp.float32)
    return last, span


def embed(params: dict, cfg: ReaderConfig, last, span):
    """Siamese tap embedding: Σ_taps dense(LN[last; span]) → [width]."""
    out = jnp.zeros((cfg.width,), jnp.float32)
    for i, m in enumerate(cfg.taps):
        x = jnp.concatenate([_ln(last[i]), _ln(span[i])])
        layer = params["tap"][str(m)]
        out = out + x @ layer["w"] + layer["b"]
    return jax.nn.gelu(out)


def query_embedding(params: dict, cfg: ReaderConfig, last, span):
    return _apply_mlp(params["query_head"], embed(params, cfg, last, span))


def record_key(params: dict, cfg: ReaderConfig, last, span):
    head = params["query_head"] if cfg.tie_heads or "key_head" not in params else params["key_head"]
    return _apply_mlp(head, embed(params, cfg, last, span))


def initial_code(params: dict, cfg: ReaderConfig, last, span):
    return _apply_mlp(params["code_head"], embed(params, cfg, last, span))


def unit(x):
    return x / jnp.sqrt(jnp.sum(x * x, axis=-1, keepdims=True) + 1e-8)


def pair_scores(cfg: ReaderConfig, q, keys):
    """Scores of a query against keys [k, width]: scaled cosine (default) or dot / sqrt(width)."""
    if cfg.cosine:
        return (unit(keys) @ unit(q)) * cfg.score_scale / cfg.temperature
    return (keys @ q) / (jnp.sqrt(cfg.width) * cfg.temperature)


def null_score(params: dict, cfg: ReaderConfig, q, k_best=None):
    """Null logit: query-only (linear) plus, when configured and a best key exists, a pairwise term on [q̂, k̂, q̂⊙k̂]."""
    qq = unit(q) * jnp.sqrt(cfg.width) if cfg.cosine else q
    out = (qq @ params["null"]["w"] + params["null"]["b"]) if cfg.query_null else params["null"]["b"]
    if cfg.pairwise_null and "null_pair" in params and k_best is not None:
        qn, kn = unit(q), unit(k_best)
        out = out + _apply_mlp(params["null_pair"], jnp.concatenate([qn, kn, qn * kn]) * jnp.sqrt(cfg.width))[0]
    return out / cfg.temperature


def best_key(scores, keys, mask):
    """The key of the best-scoring (unmasked) candidate — a non-differentiable choice; gradients flow through its features."""
    i = jnp.argmax(jnp.where(mask, scores, -jnp.inf))
    return keys[i]


def lexical_overlap(query_ids, record_ids, stop: tuple[int, ...] | frozenset) -> tuple[float, float]:
    """(fraction of the record's non-stop tokens present in the query, fraction of the query's non-stop tokens present in the record)."""
    st = set(stop)
    r = {int(t) for t in np.asarray(record_ids).reshape(-1)} - st
    q = {int(t) for t in np.asarray(query_ids).reshape(-1)} - st
    if not r or not q:
        return 0.0, 0.0
    inter = len(r & q)
    return inter / len(r), inter / len(q)


def lex_feature(query_ids, record_ids, stop) -> float:
    """Scalar overlap feature used by the reader: the mean of the two directional overlaps."""
    a, b = lexical_overlap(query_ids, record_ids, stop)
    return 0.5 * (a + b)


def applicability(params: dict, cfg: ReaderConfig, q, cand_keys, cand_mask, cand_lex=None):
    """Softmax over [k candidate scores, null]. ``cand_mask`` (bool [k]) masks padding; ``cand_lex`` ([k], optional) is the
    lexical overlap feature per candidate. Returns (weights [k], null_mass, logits [k+1])."""
    scores = pair_scores(cfg, q, cand_keys)
    if cfg.lexical and "lex" in params and cand_lex is not None:
        scores = scores + params["lex"]["score_w"] * cand_lex
    scores = jnp.where(cand_mask, scores, -1e9)
    kb = jnp.where(jnp.any(cand_mask), best_key(scores, cand_keys, cand_mask), jnp.zeros_like(q))
    null_logit = null_score(params, cfg, q, kb if cfg.pairwise_null else None)
    if cfg.lexical and "lex" in params and cand_lex is not None:
        best_lex = jnp.max(jnp.where(cand_mask, cand_lex, 0.0))
        null_logit = null_logit - params["lex"]["null_w"] * best_lex
    logits = jnp.concatenate([scores, null_logit[None]])
    probs = jax.nn.softmax(logits)
    weights = probs[:-1] * cand_mask
    return weights, probs[-1], logits


def param_count(params) -> int:
    return int(sum(int(np.prod(x.shape)) for x in jax.tree_util.tree_leaves(params)))


def params_hash(params) -> str:
    h = hashlib.sha256()
    leaves, treedef = jax.tree_util.tree_flatten(params)
    h.update(str(treedef).encode())
    for x in leaves:
        a = np.ascontiguousarray(np.asarray(x, np.float32))
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()
