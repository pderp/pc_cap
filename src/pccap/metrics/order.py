"""Actual order measurements and the scalar smooth control (PDF 2.5, D.9)."""

import numpy as np

from pccap.contracts import Metric, metric
from pccap.metrics.divergence import js


def scalar_quadratic_reversal(theta: float = 0.0, eta: float = 0.1) -> Metric:
    if not np.isfinite([theta, eta]).all() or eta < 0:
        raise ValueError("theta and nonnegative eta must be finite")
    after_1 = theta - eta * theta
    s12 = after_1 - eta * (after_1 - 1)
    after_2 = theta - eta * (theta - 1)
    s21 = after_2 - eta * after_2
    displacement = s12 - s21
    return metric(
        displacement,
        units="parameter_displacement",
        numerator=displacement,
        denominator=1,
        n=1,
        strata={
            "theta": theta,
            "eta": eta,
            "s12": s12,
            "s21": s21,
            "hessian_commutator": 0.0,
            "expected": eta**2,
        },
    )


def order_divergence(probabilities) -> Metric:
    """Mean JS across every pair of orders on identical fixed-prefix observations."""
    values = np.asarray(probabilities, dtype=np.float64)
    if values.ndim != 3 or min(values.shape) == 0:
        raise ValueError("expected [orders, fixed_prefixes, vocabulary]")
    # Validate even when fewer than two orders makes the pairwise measure undefined.
    js(values, values)
    pairs = [
        js(values[i], values[j])["value"]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    ]
    return metric(
        float(np.mean(pairs)) if pairs else None,
        units="nats",
        numerator=float(np.sum(pairs)),
        denominator=len(pairs),
        n=len(pairs),
        status="ok" if pairs else "undefined",
        strata={"per_pair": pairs, "fixed_prefixes": values.shape[1]},
    )


def damage(before_losses, after_losses) -> Metric:
    before, after = (
        np.asarray(before_losses, dtype=np.float64),
        np.asarray(after_losses, dtype=np.float64),
    )
    if before.shape != after.shape or before.size == 0:
        raise ValueError("loss arrays must have matching nonempty shapes")
    if not np.isfinite(before).all() or not np.isfinite(after).all():
        raise ValueError("loss arrays must be finite")
    delta = (after - before).reshape(-1)
    return metric(
        float(delta.mean()),
        units="nats",
        numerator=float(delta.sum()),
        denominator=delta.size,
        n=delta.size,
        strata={
            "per_item": delta.tolist(),
            "sign": "positive is harmful; negative is helpful transfer",
        },
    )
