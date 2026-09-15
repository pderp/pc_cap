"""HT-3: the coupled logarithm in the trainer's answer and preservation terms — kappa -> 0 recovers the current losses; the
coupled surprisal is bounded by 1/kappa; the clipped comparator is an alternative, not a combination."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402

from pccap.revision_v1.train import LossConfig  # noqa: E402


def _answer_term(lc, logits, target):
    surprisal = float(jnp.log(jnp.sum(jnp.exp(logits))) - logits[target])
    if lc.kappa > 0:
        return (1.0 - np.exp(-lc.kappa * surprisal)) / lc.kappa
    if lc.clip_surprisal is not None:
        return min(surprisal, lc.clip_surprisal)
    return surprisal


def test_kappa_limit_and_bound():
    logits = jnp.asarray([0.0, 0.0, 12.0])
    target = 0  # p(target) ~ 6e-6: an extreme prediction error
    plain = _answer_term(LossConfig(), logits, target)
    near = _answer_term(LossConfig(kappa=1e-4), logits, target)
    assert abs(plain - near) < 1e-2 * plain  # kappa -> 0 recovers the ordinary surprisal
    for k in (0.2, 0.5):
        v = _answer_term(LossConfig(kappa=k), logits, target)
        assert 0 < v < 1.0 / k and v < plain  # bounded by 1/kappa and below the ordinary surprisal
    assert _answer_term(LossConfig(clip_surprisal=2.0), logits, target) == 2.0


def test_config_rules():
    with pytest.raises(ValueError):
        LossConfig(kappa=-0.1)
    with pytest.raises(ValueError):
        LossConfig(kappa=0.2, clip_surprisal=2.0)
    with pytest.raises(ValueError):
        LossConfig(clip_surprisal=0.0)
