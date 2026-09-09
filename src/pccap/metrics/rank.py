"""Centered feature effective rank (PDF D.2), accumulated in NumPy float64."""

import numpy as np

from pccap.contracts import Metric, metric


def effective_rank(features) -> Metric:
    """Rows are observations; return entropy rank with the spectrum as operands.

    The contract helper nulls undefined values. A zero matrix therefore records
    its defined rank of zero in ``strata.effective_rank`` alongside undefined
    normalized-spectrum status, as requested by S0-07.
    """
    x = np.asarray(features, dtype=np.float64)
    if x.ndim != 2 or min(x.shape) == 0 or not np.isfinite(x).all():
        raise ValueError("features must be a nonempty finite [observations, features] matrix")
    x = x - x.mean(axis=0)
    singular = np.linalg.svd(x, compute_uv=False)
    details = {"singular_values": singular.tolist(), "centered": True}
    if singular[0] == 0:
        return metric(
            None,
            units="effective_dimensions",
            numerator=0,
            denominator=0,
            n=len(x),
            status="undefined",
            strata={**details, "effective_rank": 0.0, "reason": "zero_matrix"},
        )
    squared = (singular / singular[0]) ** 2
    total = squared.sum()
    p = squared / total
    positive = p > 0
    entropy = float(-np.sum(p[positive] * np.log(p[positive])))
    return metric(
        np.exp(entropy),
        units="effective_dimensions",
        n=len(x),
        numerator=entropy,
        denominator=1,
        strata={
            **details,
            "spectrum_probabilities": p.tolist(),
            "effective_rank": float(np.exp(entropy)),
            "operand_meaning": "exp(numerator / denominator)",
        },
    )
