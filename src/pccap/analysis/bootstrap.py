"""Paired realization-cluster bootstrap (PDF D.11), using CPU float64.

Inputs are already paired differences. Each row is an independent realization;
all committed orders in that row travel together in every resample.
"""

import numpy as np

from pccap.contracts import metric


def cluster_bootstrap(
    differences,
    *,
    seed: int = 0,
    draws: int = 10_000,
    confidence: float = 0.975,
    expected_realizations: int = 3,
    expected_orders: int = 5,
) -> dict:
    values = np.asarray(differences, dtype=np.float64)
    if values.shape != (expected_realizations, expected_orders):
        raise ValueError(
            "complete [realizations, orders] matrix required; no missing-pair imputation"
        )
    if not np.isfinite(values).all():
        raise ValueError("all paired differences must be finite")
    if expected_realizations < 1 or expected_orders < 1:
        raise ValueError("realization and order counts must be positive")
    if not isinstance(draws, int) or isinstance(draws, bool) or draws < 1:
        raise ValueError("draws must be a positive integer")
    if not np.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence must lie strictly between zero and one")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    realization_means = values.mean(axis=1)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, expected_realizations, size=(draws, expected_realizations))
    samples = realization_means[indices].mean(axis=1)
    tail = (1 - confidence) / 2
    lower, upper = np.quantile(samples, [tail, 1 - tail], method="linear")
    return {
        "status": "complete",
        "estimate": metric(
            float(realization_means.mean()),
            units="accuracy_fraction",
            numerator=float(realization_means.sum()),
            denominator=expected_realizations,
            n=expected_realizations,
        ),
        "interval": {
            "lower": float(lower),
            "upper": float(upper),
            "confidence": confidence,
            "sides": 2,
            "method": "percentile_linear",
        },
        "seed": seed,
        "draws": draws,
        "unit": "stream_realization",
        "orders_kept_together": True,
        "realization_means": realization_means.tolist(),
        "paired_differences": values.tolist(),
        "order_min": values.min(axis=1).tolist(),
        "order_max": values.max(axis=1).tolist(),
        "small_sample_note": "Three realizations give descriptive small-sample uncertainty; orders are not independent datasets.",
    }
