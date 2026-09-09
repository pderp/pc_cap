"""Overlap of supplied orthonormal equal-rank bases (PDF D.4)."""

import numpy as np

from pccap.contracts import Metric, metric


def subspace_overlap(left, right, *, atol: float = 1e-8) -> Metric:
    a, b = np.asarray(left, dtype=np.float64), np.asarray(right, dtype=np.float64)
    if a.ndim != 2 or b.ndim != 2 or a.shape != b.shape or a.shape[0] == 0:
        raise ValueError("bases must have matching [coordinates, rank] shapes")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("bases must be finite")
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    r = a.shape[1]
    if r == 0:
        return metric(
            None,
            units="fraction",
            numerator=0,
            denominator=0,
            status="unsupported",
            strata={"reason": "insufficient_rank"},
        )
    for basis in (a, b):
        if not np.allclose(basis.T @ basis, np.eye(r), atol=atol, rtol=0):
            raise ValueError("columns must be orthonormal; no silent QR/rank substitution")
    squared_cosines = np.linalg.svd(a.T @ b, compute_uv=False) ** 2
    numerator = float(squared_cosines.sum())
    raw = numerator / r
    if raw > 1 + 4 * atol:
        raise ValueError("overlap exceeds one beyond declared roundoff tolerance")
    return metric(
        min(1.0, raw),
        units="fraction",
        numerator=numerator,
        denominator=r,
        n=r,
        strata={
            "rank": r,
            "squared_principal_cosines": squared_cosines.tolist(),
            "roundoff_clipped": raw > 1,
        },
    )
