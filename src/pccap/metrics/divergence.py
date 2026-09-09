"""Ordinary next-token KL and JS in nats (PDF D.1, D.7, D.9)."""

import numpy as np

from pccap.contracts import Metric, metric


def _distributions(left, right):
    p, q = np.asarray(left, dtype=np.float64), np.asarray(right, dtype=np.float64)
    if p.shape != q.shape or p.ndim < 1 or p.size == 0 or p.shape[-1] < 1:
        raise ValueError("probabilities need matching nonempty shapes with categories last")
    for x in (p, q):
        if not np.isfinite(x).all() or np.any(x < 0):
            raise ValueError("probabilities must be finite and nonnegative")
        if not np.allclose(x.sum(axis=-1), 1, atol=1e-7, rtol=0):
            raise ValueError("probabilities must sum to one; input is never renormalized")
    return p, q


def _terms(p, q):
    mask = p > 0
    out = np.zeros_like(p)
    out[mask] = p[mask] * (np.log(p[mask]) - np.log(q[mask]))
    return out.sum(axis=-1)


def _result(values, *, bound=None) -> Metric:
    raw = np.asarray(values).reshape(-1)
    if np.any(raw < -1e-7) or (bound is not None and np.any(raw > bound + 1e-7)):
        raise ValueError("divergence outside mathematical bounds")
    clipped = np.maximum(raw, 0) if bound is None else np.clip(raw, 0, bound)
    return metric(
        float(clipped.mean()),
        units="nats",
        numerator=float(clipped.sum()),
        denominator=len(raw),
        n=len(raw),
        strata={
            "per_position": clipped.tolist(),
            "roundoff_clipped": int(np.count_nonzero(raw != clipped)),
        },
    )


def kl(left, right) -> Metric:
    p, q = _distributions(left, right)
    impossible = (p > 0) & (q == 0)
    n = int(np.prod(p.shape[:-1]))
    if impossible.any():
        return metric(
            None,
            units="nats",
            denominator=n,
            n=n,
            status="unreachable",
            strata={
                "reason": "support_mismatch",
                "right_unbounded": True,
                "support_mismatch_cells": int(impossible.sum()),
                "positive_mass_on_zero_support": float(p[impossible].sum()),
            },
        )
    return _result(_terms(p, q))


def js(left, right) -> Metric:
    p, q = _distributions(left, right)
    middle = (p + q) / 2
    return _result((_terms(p, middle) + _terms(q, middle)) / 2, bound=np.log(2))
