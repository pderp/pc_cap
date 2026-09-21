"""AW-B fixed-prefix scoring: every wrapper configuration from one base/cap logit pair per position.

The full-validation producer (``scripts/r1_68f_full_validation.py``, read-only import) computes, per window
position, the cap logits ``on``, the cap-off logits ``off`` (the same base with the cap disabled) and the original-base
logits ``original``, then ``metrics(on, off, original, targets)`` in the layout

    loss_cap, loss_capoff, loss_original, kl_capoff_to_cap, kl_original_to_cap.

A query-time wrapper changes only ``on``; ``off`` and ``original`` are references. So one streamed pass that yields
``(on, off, original, targets)`` per batch can score the unwrapped cap and every wrapper at once, with exactly the
same metric code the registered assay used. ``score_configs`` does that for a batch; ``Accumulator`` keeps per-config
running sums and per-position vectors in the 68f layout for the tail statistics.

Configurations are ``("v5", None)`` (unwrapped), ``("capoff", None)`` (the base), ``("clip", b)``, ``("mixture", rho)``
and ``("shrink", alpha)``. A stricter null threshold is not a configuration here: it changes ``on`` at the source and
needs its own pass (the gate decides before logits exist).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from aw import bounded
from scripts import r1_68f_full_validation as fv

Config = tuple[str, float | None]
FIELDS = fv.FIELDS


def config_key(config: Config) -> str:
    kind, param = config
    return kind if param is None else f"{kind}:{float(param):g}"


def wrapped_logits(on, off, config: Config) -> np.ndarray:
    """The logits the wrapper returns for this batch (normalised log-probabilities, a valid ``on`` replacement)."""
    kind, param = config
    if kind == "v5":
        return np.asarray(on, np.float64)  # raw, so ``fv.metrics`` normalises exactly as the registered assay did
    if kind == "capoff":
        return np.asarray(off, np.float64)
    lp0, lp1 = fv.log_probs(off), fv.log_probs(on)
    return bounded.WRAPPERS[kind](lp0, lp1, float(param))


def score_configs(on, off, original, targets, configs: list[Config]) -> dict[str, np.ndarray]:
    """Per-position metric rows (68f layout) for every configuration, from one batch of logits."""
    on, off, original = (np.asarray(x, np.float64) for x in (on, off, original))
    targets = np.asarray(targets)
    out = {}
    for config in configs:
        out[config_key(config)] = fv.metrics(wrapped_logits(on, off, config), off, original, targets)
    return out


@dataclass
class Accumulator:
    """Running sums and retained per-position vectors per configuration."""

    configs: list[Config]
    rows: dict[str, list[np.ndarray]] = field(default_factory=dict)

    def add(self, on, off, original, targets) -> None:
        for key, values in score_configs(on, off, original, targets, self.configs).items():
            self.rows.setdefault(key, []).append(values)

    def vectors(self) -> dict[str, np.ndarray]:
        return {k: np.concatenate(v, axis=0) for k, v in self.rows.items()}

    def summary(self) -> dict[str, dict[str, float]]:
        """Means, positive-part tails and exceedances per configuration (signed loss deltas against cap-off)."""
        out = {}
        for key, v in self.vectors().items():
            d = v[:, 0] - v[:, 1]
            pos = np.maximum(d, 0)
            out[key] = dict(
                positions=int(len(v)),
                mean_kl_capoff=float(v[:, 3].mean()),
                mean_kl_original=float(v[:, 4].mean()),
                mean_signed_delta_capoff=float(d.mean()),
                max_delta=float(d.max()),
                es99=float(np.quantile(pos, 0.99)),
                exceed_0_01=float((d > 0.01).mean()),
                exceed_0_1=float((d > 0.1).mean()),
                exceed_1=float((d > 1.0).mean()),
                changed_fraction=float((v[:, 3] > 1e-9).mean()),
            )
        return out
