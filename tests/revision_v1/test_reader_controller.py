"""Stage 1 gates for the reader and controller on CPU JAX (shapes, null → exact zeros, bound, determinism, budget)."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402

from pccap.revision_v1.controller import (  # noqa: E402
    ControllerConfig,
    aggregate,
    bound_writes,
    init_controller,
    writes,
)
from pccap.revision_v1.reader import (  # noqa: E402
    ReaderConfig,
    applicability,
    init_reader,
    initial_code,
    param_count,
    params_hash,
    query_embedding,
    record_key,
)

RC = ReaderConfig()
CC = ControllerConfig(bank_scales=(0.9, 1.1, 1.0))


def _obs(seed: int):
    r = np.random.default_rng(seed)
    return jnp.asarray(r.normal(size=(3, 768)), jnp.float32), jnp.asarray(r.normal(size=(3, 768)), jnp.float32)


def test_parameter_budget_and_determinism():
    rp = init_reader(jax.random.PRNGKey(0), RC)
    cp = init_controller(jax.random.PRNGKey(1), CC)
    n = param_count(rp) + param_count(cp)
    assert n <= 5_000_000, n
    assert params_hash(rp) == params_hash(init_reader(jax.random.PRNGKey(0), RC))
    assert params_hash(rp) != params_hash(init_reader(jax.random.PRNGKey(2), RC))


def test_shapes_and_applicability_masking():
    rp = init_reader(jax.random.PRNGKey(0), RC)
    last, span = _obs(1)
    q = query_embedding(rp, RC, last, span)
    k = record_key(rp, RC, last, span)
    c = initial_code(rp, RC, last, span)
    assert q.shape == (256,) and k.shape == (256,) and c.shape == (256,)
    keys = jnp.stack([record_key(rp, RC, *_obs(s)) for s in range(4)])
    mask = jnp.asarray([True, True, False, False])
    w, null, logits = applicability(rp, RC, q, keys, mask)
    assert logits.shape == (5,) and float(w[2]) == 0.0 and float(w[3]) == 0.0
    assert abs(float(w.sum() + null) - 1.0) < 1e-5
    # no candidates: all mass on the null
    w0, null0, _ = applicability(rp, RC, q, keys, jnp.zeros(4, bool))
    assert float(w0.sum()) == 0.0 and abs(float(null0) - 1.0) < 1e-5


def test_hard_null_gives_exact_zero_writes_and_bound_holds():
    cp = init_controller(jax.random.PRNGKey(1), CC)
    q = jnp.ones(256) * 0.1
    code = jnp.ones(256) * 3.0
    W0, _ = writes(cp, CC, q, code, jnp.asarray(0.0))
    assert np.all(np.asarray(W0) == 0.0)
    W1, s_raw = writes(cp, CC, q, code * 50.0, jnp.asarray(1.0))  # large raw writes → projected onto the bound
    assert aggregate(W1, CC) <= CC.A + 1e-5 and float(s_raw) > CC.A
    W_small = jnp.full((3, 768), 1e-4)  # inside the bound → untouched
    W2, s2 = bound_writes(W_small, CC)
    assert float(s2) < CC.A and np.allclose(np.asarray(W2), np.asarray(W_small))
    # a hard null (mass exactly 0) must give finite gradients (the bound's norm at W = 0)
    g0 = jax.grad(lambda c, m: jnp.sum(writes(cp, CC, q, c, m)[0] ** 2), argnums=(0, 1))(code, jnp.asarray(0.0))
    assert np.all(np.isfinite(np.asarray(g0[0]))) and np.isfinite(float(g0[1]))
    # gradients flow to the code and to the null mass
    g = jax.grad(lambda c, m: jnp.sum(writes(cp, CC, q, c, m)[0] ** 2), argnums=(0, 1))(code, jnp.asarray(0.7))
    assert np.all(np.isfinite(np.asarray(g[0]))) and np.isfinite(float(g[1]))
