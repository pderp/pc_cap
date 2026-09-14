"""Conditional correction network (design §controller).

writes = MLP([query; Σ_i w_i code_i]) → [n_banks, d], scaled by the non-null mass, then projected onto the aggregate
bound Σ_m ‖w_m‖ / b_m ≤ A (a differentiable rescale when the bound is exceeded). A hard null (non-null mass exactly 0)
gives exactly zero writes, so the corrected pass equals the cap-off base (gate 4).
"""

from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np

from pccap.revision_v1.reader import _apply_mlp, _mlp


@dataclass(frozen=True)
class ControllerConfig:
    d: int = 768
    n_banks: int = 3
    width: int = 256
    d_code: int = 256
    hidden: int = 512
    A: float = 0.3
    bank_scales: tuple[float, ...] = (1.0, 1.0, 1.0)  # b_m per bank (v0 calibration)


def init_controller(key, cfg: ControllerConfig) -> dict:
    return {"mlp": _mlp(key, (cfg.width + cfg.d_code, cfg.hidden, cfg.hidden, cfg.n_banks * cfg.d))}


def raw_writes(params: dict, cfg: ControllerConfig, q, code):
    return _apply_mlp(params["mlp"], jnp.concatenate([q, code])).reshape(cfg.n_banks, cfg.d)


def bound_writes(W, cfg: ControllerConfig):
    """Project [n_banks, d] onto Σ_m ‖w_m‖ / b_m ≤ A by a single rescale (identity inside the bound)."""
    b = jnp.asarray(cfg.bank_scales, jnp.float32)
    norms = jnp.sqrt(jnp.sum(W * W, axis=1) + 1e-12)  # safe norm: finite gradient at W = 0 (a hard null)
    s = jnp.sum(norms / b)
    scale = jnp.where(s > cfg.A, cfg.A / jnp.maximum(s, 1e-12), 1.0)
    return W * scale, s


def writes(params: dict, cfg: ControllerConfig, q, code, non_null_mass):
    """Writes for one query. ``code`` is the applicability-weighted fact code; ``non_null_mass`` ∈ [0, 1]."""
    W = raw_writes(params, cfg, q, code) * non_null_mass
    W, s = bound_writes(W, cfg)
    return jnp.where(non_null_mass > 0, W, jnp.zeros_like(W)), s


def aggregate(W, cfg: ControllerConfig) -> float:
    b = np.asarray(cfg.bank_scales, np.float32)
    return float(np.sum(np.linalg.norm(np.asarray(W), axis=1) / b))


def writes_with_delta(params: dict, cfg: ControllerConfig, q, code, delta, non_null_mass):
    """Writes for one query when the selected records carry explicit delta writes: (controller + delta) · mass, then the bound."""
    W = (raw_writes(params, cfg, q, code) + delta) * non_null_mass
    W, s = bound_writes(W, cfg)
    return jnp.where(non_null_mass > 0, W, jnp.zeros_like(W)), s
