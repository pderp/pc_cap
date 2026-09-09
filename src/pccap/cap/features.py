"""Key features (CAP-01; PDF F.1).

``LN0`` is parameter-free centring and variance normalization with ε = 1e-5 (biased variance);
``z(h) = LN0(h) / √d`` so that keys have unit scale at every width. One implementation is used
for learning and inference (same function, same dtype: float32).

A zero vector maps to the zero key (variance 0 → division by √ε of a zero numerator); no NaN.
"""

from __future__ import annotations

import numpy as np

EPS = 1e-5


def ln0(h: np.ndarray, eps: float = EPS) -> np.ndarray:
    h = np.asarray(h, dtype=np.float32)
    mu = h.mean(axis=-1, keepdims=True, dtype=np.float32)
    c = h - mu
    var = np.mean(c * c, axis=-1, keepdims=True, dtype=np.float32)
    return (c / np.sqrt(var + np.float32(eps))).astype(np.float32)


def z(h: np.ndarray) -> np.ndarray:
    """Unit-scale key feature ``LN0(h)/√d`` (last axis is the feature axis)."""
    h = np.asarray(h, dtype=np.float32)
    d = h.shape[-1]
    return (ln0(h) / np.float32(np.sqrt(d))).astype(np.float32)


def concat_keys(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """``[z(a); z(b)] / √2`` for the two-part read variants R-g / R-e (PDF F.4), dk = 2d."""
    return (np.concatenate([z(a), z(b)], axis=-1) / np.float32(np.sqrt(2.0))).astype(np.float32)
