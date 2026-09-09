"""Transport: credit signal -> unit descent direction at a site (S0-05; PDF F.3 step 2).

* adjoint credit: ``d = -g / ||g||`` where ``g = dL/dh`` at the site;
* ePC credit: the wrapper's documented descent sign applied to the error field, then normalized
  (``EPCBase`` exposes ``descent_sign``; the default here is the adjoint convention);
* optional projection onto an allowed subspace (fixture use, PDF E.1) **before** normalization;
* ``||signal|| < 1e-12`` (after projection) -> explicit ``no_direction``; nothing is manufactured;
* the sign is never flipped per example. The sign convention is verified once on a 1-D analytic
  control (``sign_convention_control``) and recorded in ``results/S0/controls/sign_convention.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from pccap.contracts import DirectionResult, SiteId, Tensor

ZERO_NORM = 1e-12


class Transport:
    """Turns a credit signal into a unit direction. ``sign=-1.0`` is the adjoint convention
    (descend the gradient); an ePC wrapper passes its own documented sign."""

    def __init__(self, sign: float = -1.0):
        if sign not in (-1.0, 1.0):
            raise ValueError("sign must be +1 or -1 and is fixed for the run")
        self.sign = float(sign)

    def direction(self, signal: Tensor, site: SiteId, allowed_subspace: Tensor | None = None) -> DirectionResult:
        s = jnp.asarray(signal, dtype=jnp.float32)
        projected = False
        if allowed_subspace is not None:
            Q = jnp.asarray(allowed_subspace, dtype=jnp.float32)  # [d, r] orthonormal columns
            s = Q @ (Q.T @ s)
            projected = True
        norm = float(jnp.linalg.norm(s))
        if not np.isfinite(norm):
            raise FloatingPointError("non-finite credit signal norm")  # Op. rule 8: no silent fallback
        if norm < ZERO_NORM:
            return DirectionResult(site=site, direction=None, status="no_direction", signal_norm=norm, projected=projected)
        return DirectionResult(site=site, direction=self.sign * s / norm, status="ok", signal_norm=norm, projected=projected)


def sign_convention_control(out_path: Path | None = None, seed: int = 0) -> dict:
    """1-D differentiable toy: ``loss(h) = (w·h − y)²``. The returned direction must reduce the
    loss for a small step. Recorded once (plan S0-05); never re-run per example."""
    rng = np.random.default_rng(seed)
    w = jnp.asarray(rng.standard_normal(8), dtype=jnp.float32)
    h0 = jnp.asarray(rng.standard_normal(8), dtype=jnp.float32)
    y = jnp.float32(3.0)

    def loss(h):
        return (jnp.dot(w, h) - y) ** 2

    g = jax.grad(loss)(h0)
    tr = Transport(sign=-1.0)
    d = tr.direction(g, SiteId(1, 3, 0))
    step = 1e-2
    l0 = float(loss(h0))
    l1 = float(loss(h0 + step * d.direction))
    wrong = float(loss(h0 - step * d.direction))
    rec = {
        "control": "sign_convention", "loss": "(w.h - y)^2", "step": step,
        "loss_before": l0, "loss_after_direction": l1, "loss_after_flipped": wrong,
        "descent_reduces_loss": l1 < l0, "flipped_increases_loss": wrong > l0,
        "transport_sign": tr.sign, "seed": seed,
    }
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(rec, indent=1))
    return rec
