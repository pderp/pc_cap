"""AW-B mathematical oracle: bounded query-time corrections of a cap's output distribution.

Pure NumPy, float64, CPU only. Nothing here touches the R1 implementation tree (``scripts/``, ``src/pccap/``),
which is under the Stage-4 content lock; this package lives outside that inventory on purpose.

Conventions (natural-log units throughout):

* ``logp0`` is the unchanged base log-distribution on one prefix (full vocabulary, normalised).
* ``logp1`` is the unmodified cap log-distribution on the same prefix.
* ``r = logp1 - logp0`` is the cap's log-ratio ("tilt").

Wrappers, each returning a normalised log-distribution:

* ``clip_tilt(logp0, logp1, b)``: ``s_b = clip(r, -b, b)``, ``p_b ∝ p0 · exp(s_b)``.  Because
  ``exp(-b) ≤ Z ≤ exp(b)``, every token's loss increase relative to ``p0`` is at most ``2b`` nats and
  ``KL(p0 ‖ p_b) ≤ 2b`` (Generalized Transformers report, eq. 19, written there in bits with bound ``2a``).
* ``mixture(logp0, logp1, rho)``: ``p = rho·p0 + (1-rho)·p1``; loss increase at most ``-log(rho)``.
  ``rho = exp(-2b)`` matches the clip bound.
* ``shrink(logp0, logp1, alpha)``: ``p ∝ p0 · exp(alpha·r)``; global score shrinkage, no per-token bound
  except ``alpha·(max r - min r)``; the control for "is the benefit just weaker edits".

``b = 0`` (or ``rho = 1``, ``alpha = 0``) returns ``p0``; ``b = inf`` (``rho = 0``, ``alpha = 1``) returns ``p1``.
"""
from __future__ import annotations

import numpy as np

__all__ = ["log_normalise", "clip_tilt", "mixture", "shrink", "kl", "loss_increase", "matched_rho", "WRAPPERS"]


def _as_log(x) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    if a.ndim == 0:
        raise ValueError("log-distribution must be at least one-dimensional")
    if not np.all(np.isfinite(a)):
        raise FloatingPointError("non-finite log-probabilities")
    return a


def log_normalise(logits) -> np.ndarray:
    """Exact log-softmax over the last axis in float64."""
    a = _as_log(logits)
    m = a.max(axis=-1, keepdims=True)
    return a - m - np.log(np.sum(np.exp(a - m), axis=-1, keepdims=True))


def clip_tilt(logp0, logp1, b: float) -> np.ndarray:
    """Bounded tilt: clip the per-token log-ratio to ``[-b, b]`` and renormalise (b ≥ 0; ``inf`` = unclipped)."""
    if b < 0:
        raise ValueError("b must be non-negative")
    lp0, lp1 = _as_log(logp0), _as_log(logp1)
    if lp0.shape != lp1.shape:
        raise ValueError("shape mismatch")
    s = np.clip(lp1 - lp0, -b, b) if np.isfinite(b) else lp1 - lp0
    return log_normalise(lp0 + s)


def mixture(logp0, logp1, rho: float) -> np.ndarray:
    """Convex mixture ``rho·p0 + (1-rho)·p1`` in log space (0 ≤ rho ≤ 1)."""
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0, 1]")
    lp0, lp1 = _as_log(logp0), _as_log(logp1)
    if lp0.shape != lp1.shape:
        raise ValueError("shape mismatch")
    if rho == 1.0:
        return log_normalise(lp0)
    if rho == 0.0:
        return log_normalise(lp1)
    a = np.log(rho) + lp0
    c = np.log1p(-rho) + lp1
    m = np.maximum(a, c)
    return log_normalise(m + np.log(np.exp(a - m) + np.exp(c - m)))


def shrink(logp0, logp1, alpha: float) -> np.ndarray:
    """Global score shrinkage ``p ∝ p0·exp(alpha·r)`` (0 ≤ alpha ≤ 1)."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must lie in [0, 1]")
    lp0, lp1 = _as_log(logp0), _as_log(logp1)
    if lp0.shape != lp1.shape:
        raise ValueError("shape mismatch")
    return log_normalise(lp0 + alpha * (lp1 - lp0))


def matched_rho(b: float) -> float:
    """Mixture weight whose loss bound ``-log(rho)`` equals the clip bound ``2b``."""
    return float(np.exp(-2.0 * b))


def kl(logp, logq) -> np.ndarray:
    """``KL(p ‖ q)`` over the last axis, both inputs normalised log-distributions."""
    lp, lq = _as_log(logp), _as_log(logq)
    return np.sum(np.exp(lp) * (lp - lq), axis=-1)


def loss_increase(logp0, logq, target) -> np.ndarray:
    """``-log q(target) + log p0(target)``: the per-token loss increase relative to the base."""
    lp0, lq = _as_log(logp0), _as_log(logq)
    t = np.asarray(target)
    single = t.ndim == lp0.ndim - 1  # one target per row
    if single:
        t = t[..., None]
    out = np.take_along_axis(lp0, t, axis=-1) - np.take_along_axis(lq, t, axis=-1)
    return out[..., 0] if single else out


WRAPPERS = {"clip": clip_tilt, "mixture": mixture, "shrink": shrink}
