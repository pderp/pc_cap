"""HT-3 actual trainer gates and explicit regressions documenting known defects.

The controlled-logit tests execute train_fast's real group loss while replacing
only the base forward. A separate test executes an actual TinyBase episode.
No optimizer step, real base, dataset payload or GPU is used.
"""

from dataclasses import replace
from unittest.mock import patch

import jax
import jax.numpy as jnp
import numpy as np
import pytest

import pccap  # noqa: F401 -- determinism before JAX
from pccap.bases import gpt2_jax as g
from pccap.revision_v1.controller import init_controller
from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.observations import ObservationEncoder
from pccap.revision_v1.reader import init_reader
from pccap.revision_v1.train import (
    ANSWER_ROLES,
    PRESERVE_ROLES,
    LossConfig,
    episode_grads,
    featurize,
)
from pccap.revision_v1.train_fast import FastTrainer
from tests.revision_v1.test_train_fast import CC, RC
from tests.revision_v1.tiny_base import CFG, TinyBase


def theta():
    a, b = jax.random.split(jax.random.PRNGKey(303))
    return {"reader": init_reader(a, RC), "controller": init_controller(b, CC)}


def actual_group_loss(lc, kind="answer", reference=None):
    """Exercise the installed nested objective, with logits exposed for gradient tests."""
    th = theta()
    obs = jnp.ones((1, len(RC.taps), CFG.d), jnp.float32)
    valid = jnp.asarray([True])
    target = jnp.asarray([0], jnp.int32)
    ref = (
        jnp.zeros((1, CFG.vocab), jnp.float32)
        if reference is None
        else jnp.asarray(reference)[None, :]
    )
    trainer = FastTrainer(RC, CC, {}, CFG, lc)
    fn = trainer.get(kind, False)

    def loss(logits):
        with patch.object(g, "forward_jit", lambda params, *a: (params["test_logits"], {}, {})):
            ((value, _), _) = fn(
                th,
                {"test_logits": logits},
                (obs, obs, obs, obs),
                obs,
                obs,
                target,
                ~valid,
                valid,
                jnp.zeros((1, 1)),
                jnp.zeros((1, 16), jnp.int32),
                jnp.ones(1, jnp.int32),
                target,
                obs,
                obs,
                target,
                ref,
                jnp.ones(1),
            )
        return value

    return loss


def test_actual_zero_is_exact_default_and_near_zero_limit():
    x = jnp.linspace(-3, 3, CFG.vocab)
    for kind in ("answer", "preserve"):
        reference = jnp.linspace(-2, 2, CFG.vocab)
        plain = actual_group_loss(LossConfig(), kind, reference)
        zero = actual_group_loss(LossConfig(kappa=0), kind, reference)
        np.testing.assert_array_equal(plain(x), zero(x))
        near = actual_group_loss(LossConfig(kappa=1e-4), kind, reference)
        assert float(near(x)) == pytest.approx(float(plain(x)), abs=5e-3)


@pytest.mark.parametrize("kappa", [0.2, 0.5])
def test_actual_surprisal_bound_and_finite_logit_gradient(kappa):
    fn = actual_group_loss(LossConfig(kappa=kappa))
    x = jnp.zeros(CFG.vocab).at[0].set(-10000)
    value, grad = jax.value_and_grad(fn)(x)
    assert float(value) == pytest.approx(1 / kappa)
    assert np.isfinite(np.asarray(grad)).all()
    assert float(jnp.linalg.norm(grad)) == 0
    # Non-saturated inputs retain informative, finite gradients.
    assert float(jnp.linalg.norm(jax.grad(fn)(jnp.zeros(CFG.vocab)))) > 0


def test_actual_clip_comparator_bound_gradient_and_unchanged_preservation():
    x = jnp.zeros(CFG.vocab).at[0].set(-10000)
    fn = actual_group_loss(LossConfig(clip_surprisal=2))
    value, grad = jax.value_and_grad(fn)(x)
    assert float(value) == 2 and np.isfinite(grad).all() and float(jnp.linalg.norm(grad)) == 0
    easy = jnp.zeros(CFG.vocab).at[0].set(10)
    assert float(fn(easy)) == pytest.approx(float(actual_group_loss(LossConfig())(easy)), abs=1e-6)
    x = jnp.linspace(-1, 1, CFG.vocab)
    ref = jnp.linspace(-2, 2, CFG.vocab)
    np.testing.assert_array_equal(
        actual_group_loss(LossConfig(), "preserve", ref)(x),
        actual_group_loss(LossConfig(clip_surprisal=2), "preserve", ref)(x),
    )


def test_repaired_coupled_preservation_is_nonnegative_and_stationary_at_match():
    """Repaired after the HT-3 review: the preservation term is the f-divergence sum p ln_k(p/q) (Codex's counterexample
    p=(.9,.1), q=(.99,.01), k=.5 was -0.0401 under the first form); it is >= 0, zero at q = p, with zero gradient there."""
    p = jnp.full(CFG.vocab, 1e-30).at[0].set(0.9).at[1].set(0.1)
    q = jnp.full(CFG.vocab, 1e-30).at[0].set(0.99).at[1].set(0.01)
    fn = actual_group_loss(LossConfig(kappa=0.5), "preserve", jnp.log(p))
    assert float(fn(jnp.log(q))) > 0.0
    value, grad = jax.value_and_grad(fn)(jnp.log(p))
    assert abs(float(value)) < 1e-6
    assert float(jnp.linalg.norm(grad)) < 1e-4


def test_repaired_small_kappa_is_stable():
    x = jnp.zeros(CFG.vocab)
    normal = float(actual_group_loss(LossConfig())(x))
    near = float(actual_group_loss(LossConfig(kappa=1e-10))(x))
    assert normal > 4 and near == pytest.approx(normal, rel=1e-4)  # expm1-based positive branch


def test_repaired_config_rejects_nonfinite_values():
    with pytest.raises(ValueError):
        LossConfig(kappa=float("nan"))
    with pytest.raises(ValueError):
        LossConfig(clip_surprisal=float("inf"))


def test_tinybase_parity_at_zero_and_positive_kappa():
    base = TinyBase()
    feats = featurize(
        base, ObservationEncoder(base, taps=RC.taps), synthetic_episode(7, history_size=2), RC
    )
    selected = []
    for roles in (ANSWER_ROLES, PRESERVE_ROLES):
        q = next(q for q in feats.queries if q.role in roles)
        selected.append(replace(q, prefixes=q.prefixes[:1]))
    feats = replace(feats, queries=selected)
    th = theta()
    for lc in (LossConfig(), LossConfig(kappa=0.5)):
        ref, mref = episode_grads(th, RC, CC, base.params, base.cfg, feats, lc)
        fast, mfast = FastTrainer(RC, CC, base.params, base.cfg, lc).episode_grads(th, feats)
        for a, b in zip(jax.tree_util.tree_leaves(ref), jax.tree_util.tree_leaves(fast), strict=True):
            np.testing.assert_allclose(a, b, atol=2e-4, rtol=2e-3)
        assert mfast["answer"] == pytest.approx(mref["answer"], abs=1e-3)
    _, plain = episode_grads(th, RC, CC, base.params, base.cfg, feats, LossConfig())
    _, coupled = episode_grads(th, RC, CC, base.params, base.cfg, feats, LossConfig(kappa=0.5))
    assert coupled["answer"] < plain["answer"]  # the coupled surprisal is below the ordinary one
