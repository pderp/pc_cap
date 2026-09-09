"""Accuracy continual-learning matrix; row zero is the frozen base (PDF D.7)."""

import numpy as np

from pccap.contracts import Metric, metric


def _matrix(scores):
    a = np.asarray(scores, dtype=np.float64)
    if a.ndim != 2 or a.shape[1] < 1 or a.shape[0] != a.shape[1] + 1:
        raise ValueError("completed matrix must have [T+1, T] shape including base row")
    if not np.isfinite(a).all() or np.any((a < 0) | (a > 1)):
        raise ValueError("accuracy entries must be finite fractions in [0, 1]")
    return a


def _mean(values, name) -> Metric:
    values = np.asarray(values, dtype=np.float64)
    return metric(
        float(values.mean()) if values.size else None,
        units="accuracy_fraction",
        numerator=float(values.sum()),
        denominator=values.size,
        n=values.size,
        status="ok" if values.size else "undefined",
        strata={"measure": name, "per_task": values.tolist()},
    )


def acc(scores) -> Metric:
    return _mean(_matrix(scores)[-1], "ACC")


def bwt(scores) -> Metric:
    a = _matrix(scores)
    return _mean([a[-1, i] - a[i + 1, i] for i in range(a.shape[1] - 1)], "BWT")


def fwt(scores) -> Metric:
    a = _matrix(scores)
    return _mean([a[i, i] - a[0, i] for i in range(1, a.shape[1])], "FWT")


def forgetting(scores) -> Metric:
    a = _matrix(scores)
    return _mean([a[i + 1 :, i].max() - a[-1, i] for i in range(a.shape[1] - 1)], "F")


def late_acquisition_gain(scores, *, task_indices=None) -> Metric:
    """Mean post-minus-pre task gain; indices are explicit zero-based order positions.

    To compare late/early across orders the caller must match actual task IDs.
    No task grouping is inferred from scores.
    """
    a = _matrix(scores)
    indices = list(range(a.shape[1])) if task_indices is None else list(task_indices)
    if len(set(indices)) != len(indices) or any(
        not isinstance(i, (int, np.integer)) or not 0 <= i < a.shape[1] for i in indices
    ):
        raise ValueError("task_indices must be unique valid zero-based indices")
    out = _mean([a[i + 1, i] - a[i, i] for i in indices], "acquisition_gain")
    out["strata"]["task_indices"] = indices
    return out


def summarize(scores) -> dict[str, Metric]:
    return {
        "ACC": acc(scores),
        "BWT": bwt(scores),
        "FWT": fwt(scores),
        "F": forgetting(scores),
        "acquisition_gain": late_acquisition_gain(scores),
    }
