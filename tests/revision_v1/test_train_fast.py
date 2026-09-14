"""The jitted batched trainer reproduces the reference gradient on a small episode (tiny CPU base)."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax  # noqa: E402
import numpy as np  # noqa: E402

from pccap.revision_v1.controller import ControllerConfig, init_controller  # noqa: E402
from pccap.revision_v1.episodes import synthetic_episode  # noqa: E402
from pccap.revision_v1.observations import ObservationEncoder  # noqa: E402
from pccap.revision_v1.reader import ReaderConfig, init_reader  # noqa: E402
from pccap.revision_v1.train import LossConfig, episode_grads, featurize  # noqa: E402
from pccap.revision_v1.train_fast import FastTrainer  # noqa: E402
from tests.revision_v1.tiny_base import CFG, TinyBase  # noqa: E402

RC = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
CC = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))


def test_fast_trainer_matches_reference_gradients():
    base = TinyBase()
    enc = ObservationEncoder(base, taps=RC.taps)
    feats = featurize(base, enc, synthetic_episode(7), RC)
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = {"reader": init_reader(k1, RC), "controller": init_controller(k2, CC)}
    lc = LossConfig()
    ref, mref = episode_grads(theta, RC, CC, base.params, base.cfg, feats, lc)
    fast = FastTrainer(RC, CC, base.params, base.cfg, lc, lr=1e-3)
    got, mgot = fast.episode_grads(theta, feats)
    for a, b in zip(jax.tree_util.tree_leaves(ref), jax.tree_util.tree_leaves(got)):
        assert np.allclose(np.asarray(a), np.asarray(b), atol=2e-4, rtol=2e-3)
    assert abs(mref["retrieval"] - mgot["retrieval"]) < 1e-3 and mref["answer_n"] == mgot["answer_n"] and mref["preserve_n"] == mgot["preserve_n"]
    assert abs(mref["answer"] - mgot["answer"]) < 1e-3 and abs(mref["preserve"] - mgot["preserve"]) < 1e-3
