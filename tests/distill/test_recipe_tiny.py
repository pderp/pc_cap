"""REG-00 exactness tests on a tiny GPT-2 (CPU or GPU; seconds).

Independent references written here from the sibling's formulas (hdpc/wrap.py, energy.py, relax.py,
train_distill.py) using only ``pccap.bases.gpt2_jax`` primitives — no FabricPC — so that the FabricPC
graph path (``epc_inference.relax_errors`` + ``KDEnergy`` + ``weight_phase.local_weight_energy``)
is checked against a second implementation.
"""

from __future__ import annotations

import math

import jax
import jax.numpy as jnp
import numpy as np
import optax
import pytest

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.distill import data as D
from pccap.distill import recipe as R
from pccap.distill import schedule as S
from pccap.distill.train import Trainer, batched_logits, load_checkpoint, save_checkpoint
from pccap.pc import epc_inference as epc
from pccap.pc.kd_energy import KDEnergy, kd_kl_loss
from pccap.pc.nodes import graph_params_from_numpy, node_names
from pccap.pc.weight_phase import local_weight_energy

CFG = g.GPT2Config(n_layer=3, n_head=2, d=32, vocab=64, n_pos=16)
L, B, BETA = 8, 4, 2.0


def tiny_params(seed: int) -> dict:
    rng = np.random.default_rng(seed)
    d = CFG.d

    def blk():
        return {"ln_1": {"g": np.ones(d, np.float32), "b": np.zeros(d, np.float32)},
                "c_attn": {"w": (0.2 * rng.standard_normal((d, 3 * d))).astype(np.float32), "b": np.zeros(3 * d, np.float32)},
                "c_proj": {"w": (0.2 * rng.standard_normal((d, d))).astype(np.float32), "b": np.zeros(d, np.float32)},
                "ln_2": {"g": np.ones(d, np.float32), "b": np.zeros(d, np.float32)},
                "c_fc": {"w": (0.2 * rng.standard_normal((d, 4 * d))).astype(np.float32), "b": np.zeros(4 * d, np.float32)},
                "c_proj2": {"w": (0.2 * rng.standard_normal((4 * d, d))).astype(np.float32), "b": np.zeros(d, np.float32)}}

    return {"wte": (0.5 * rng.standard_normal((CFG.vocab, d))).astype(np.float32),
            "wpe": (0.1 * rng.standard_normal((CFG.n_pos, d))).astype(np.float32),
            "ln_f": {"g": np.ones(d, np.float32), "b": np.zeros(d, np.float32)},
            "blocks": [blk() for _ in range(CFG.n_layer)]}


def ids_batch(seed: int, b: int = B) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, CFG.vocab, size=(b, L)).astype(np.int32)


# ------------------------------------------------------------------ independent reference (sibling formulas)
def ref_forward_with_errors(params, ids, errors):
    """hdpc/wrap.py forward_states: h_{l+1} = Block_l(h_l) + e_l; logits = head(h_L)."""
    def one(i, errs):
        h = g.embed(params, i)
        for l, blk in enumerate(params["blocks"]):
            h = g.block(blk, h, CFG) + errs[l]
        return g.head(params, h, CFG)
    return jax.vmap(one)(ids, errors)


def ref_energy(errors, params, ids, teacher_logits, scale):
    """hdpc/energy.py energy(): ½Σ‖e‖² + scale · kd_kl_loss (token mean)."""
    logits = ref_forward_with_errors(params, ids, errors)
    pe = 0.5 * jnp.sum(jnp.square(errors))
    return pe + scale * kd_kl_loss(logits, teacher_logits, BETA)


def ref_relax(params, ids, teacher_logits, T, lr):
    """hdpc/relax.py relax_errors: zero init, T plain SGD steps, energies at e_0..e_T."""
    errors = jnp.zeros((ids.shape[0], CFG.n_layer, L, CFG.d), jnp.float32)
    scale = float(ids.shape[0])
    energies = []
    for _ in range(T):
        E, gr = jax.value_and_grad(ref_energy)(errors, params, ids, teacher_logits, scale)
        energies.append(E)
        errors = errors - lr * gr
    energies.append(ref_energy(errors, params, ids, teacher_logits, scale))
    return errors, jnp.stack(energies)


def ref_local_energy(params, ids, errors, teacher_logits, scale):
    """hdpc/wrap.py local_prediction_pairs + energy.py local_weight_energy."""
    def one(i, errs):
        h = g.embed(params, i)  # not detached
        total = 0.0
        for l, blk in enumerate(params["blocks"]):
            pred = g.block(blk, h, CFG)
            delta = pred - jax.lax.stop_gradient(pred) - errs[l]
            total = total + 0.5 * jnp.sum(jnp.square(delta))
            h = jax.lax.stop_gradient(pred + errs[l])
        return total, g.head(params, jax.lax.stop_gradient(h), CFG)
    totals, logits = jax.vmap(one)(ids, errors)
    return jnp.sum(totals) + scale * kd_kl_loss(logits, teacher_logits, BETA)


def graph_errors_to_array(errors: dict, names) -> jnp.ndarray:
    return jnp.stack([errors[n] for n in names["blocks"]], axis=1)  # [B, n_layer, L, d]


@pytest.fixture(scope="module")
def setup():
    r = R.Recipe(seq_len=L, batch_size=B, micro_batch_size=2)
    tr = Trainer(CFG, r, seq_len=L)
    teacher = jax.tree_util.tree_map(jnp.asarray, tiny_params(0))
    student = jax.tree_util.tree_map(jnp.asarray, tiny_params(1))
    ids = jnp.asarray(ids_batch(2))
    return r, tr, teacher, student, ids


def test_kd_energy_matches_reference(setup):
    r, tr, teacher, student, ids = setup
    tl = batched_logits(teacher, ids, CFG)
    sl = batched_logits(student, ids, CFG)
    per_sample = KDEnergy.energy(tl, sl, {"beta": BETA})
    assert per_sample.shape == (B,)
    # graph_energy sums per-sample energies = B × token-mean loss (scale = micro size)
    np.testing.assert_allclose(float(jnp.sum(per_sample)), float(B * kd_kl_loss(sl, tl, BETA)), rtol=1e-5)
    # zero errors: student == teacher gives zero energy
    assert float(jnp.sum(KDEnergy.energy(tl, tl, {"beta": BETA}))) < 1e-6


@pytest.mark.parametrize("T", [1, 3])
def test_relaxation_matches_reference(setup, T):
    r, tr, teacher, student, ids = setup
    names = node_names(CFG.n_layer)
    tl = batched_logits(teacher, ids, CFG)
    structure = tr.structure(T)
    clamps = {names["ids"]: ids, names["logits"]: tl}
    _, errors, energies, gnorms, _ = epc.relax_errors(graph_params_from_numpy(student, CFG), structure, clamps, None, None, T, r.error_lr)
    ref_err, ref_E = ref_relax(student, ids, tl, T, r.error_lr)
    np.testing.assert_allclose(np.asarray(energies), np.asarray(ref_E), rtol=1e-4, atol=1e-6)
    np.testing.assert_allclose(np.asarray(graph_errors_to_array(errors, names)), np.asarray(ref_err), rtol=1e-4, atol=1e-6)
    assert energies.shape == (T + 1,) and gnorms.shape == (T + 1,)


def test_local_weight_energy_matches_reference_and_is_minus_JTe(setup):
    r, tr, teacher, student, ids = setup
    names = node_names(CFG.n_layer)
    tl = batched_logits(teacher, ids, CFG)
    structure = tr.structure(2)
    clamps = {names["ids"]: ids, names["logits"]: tl}
    _, errors, *_ = epc.relax_errors(graph_params_from_numpy(student, CFG), structure, clamps, None, None, 2, r.error_lr)
    err_arr = graph_errors_to_array(errors, names)

    def ours(p):
        return local_weight_energy(graph_params_from_numpy(p, CFG), structure, clamps, errors)

    def ref(p):
        return ref_local_energy(p, ids, err_arr, tl, float(B))

    E1, g1 = jax.value_and_grad(ours)(student)
    E2, g2 = jax.value_and_grad(ref)(student)
    np.testing.assert_allclose(float(E1), float(E2), rtol=1e-5, atol=1e-6)
    for (k1, a), (k2, b) in zip(g.flatten_named(g1), g.flatten_named(g2)):
        assert k1 == k2
        np.testing.assert_allclose(np.asarray(a), np.asarray(b), rtol=2e-4, atol=5e-6, err_msg=k1)
    # block 1's gradient is −J₁ᵀ e₁ at its detached input (sibling delta trick)
    h0 = jax.vmap(lambda i: g.embed(student, i))(ids)
    x1 = jax.vmap(lambda h: g.block(student["blocks"][0], h, CFG))(h0) + err_arr[:, 0]

    def block1_out(p1):
        return jax.vmap(lambda x: g.block(p1, x, CFG))(x1)

    _, vjp = jax.vjp(block1_out, student["blocks"][1])
    (minus_jte,) = vjp(-err_arr[:, 1])
    for (k1, a), (k2, b) in zip(g.flatten_named({"wte": g1["wte"], "wpe": g1["wpe"], "ln_f": g1["ln_f"], "blocks": [g1["blocks"][1]]}),
                                g.flatten_named({"wte": g1["wte"], "wpe": g1["wpe"], "ln_f": g1["ln_f"], "blocks": [minus_jte]})):
        if k1.startswith("h.0."):
            np.testing.assert_allclose(np.asarray(a), np.asarray(b), rtol=2e-4, atol=5e-6, err_msg=k1)
    # the energy value equals ½Σ‖e‖² + KD (pred − stop(pred) = 0)
    logits = ref_forward_with_errors(student, ids, err_arr)
    expect = 0.5 * float(jnp.sum(jnp.square(err_arr))) + float(B * kd_kl_loss(logits, tl, BETA))
    np.testing.assert_allclose(float(E1), expect, rtol=1e-5, atol=1e-6)


@pytest.mark.parametrize("micro", [1, 2, 4])
def test_micro_batching_is_exact(setup, micro):
    r, tr, teacher, student, ids = setup
    opt_state = tr.opt.init(student)
    p_full, _, st_full = tr.step_fn(2, B, B, debug_grads=True)(student, opt_state, teacher, ids)
    p_m, _, st_m = tr.step_fn(2, micro, B, debug_grads=True)(student, opt_state, teacher, ids)
    assert_same_grads(st_full["grads"], st_m["grads"])
    assert_same_update(student, p_full, p_m)
    for k in ("pc_loss", "inner_energy_start", "inner_energy_end", "pc_grad_norm"):
        np.testing.assert_allclose(float(st_full[k]), float(st_m[k]), rtol=1e-4, atol=1e-7, err_msg=k)
    # the update equals Adam on the reference gradient (1/B) Σ_samples ∇ local energy
    tl = batched_logits(teacher, ids, CFG)
    names = node_names(CFG.n_layer)
    structure = tr.structure(2)
    _, errors, *_ = epc.relax_errors(graph_params_from_numpy(student, CFG), structure, {names["ids"]: ids, names["logits"]: tl},
                                     None, None, 2, r.error_lr)
    grad = jax.grad(lambda p: ref_local_energy(p, ids, graph_errors_to_array(errors, names), tl, float(B)) / B)(student)
    assert_same_grads(grad, st_m["grads"])
    upd, _ = tr.opt.update(grad, opt_state, student)
    p_ref = optax.apply_updates(student, upd)
    assert_same_update(student, p_ref, p_m)


def assert_same_grads(ga, gb):
    for (k, a), (_, b) in zip(g.flatten_named(ga), g.flatten_named(gb)):
        a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
        np.testing.assert_allclose(a, b, rtol=1e-4, atol=1e-6 * max(1.0, np.abs(b).max()), err_msg=k)


def assert_same_update(p0, pa, pb):
    """Compare Adam updates (≤ lr each). The key-slice of ``c_attn.b`` has a mathematically zero
    gradient (a constant added to every key leaves the softmax unchanged); Adam normalizes its
    round-off-level gradient to an O(lr) step whose sign depends on reduction order, in JAX and in
    the sibling alike, and it has no effect on the function — it is excluded."""
    d = CFG.d
    for (k, x0), (_, a), (_, b) in zip(g.flatten_named(p0), g.flatten_named(pa), g.flatten_named(pb)):
        ua = (np.asarray(a, np.float64) - np.asarray(x0, np.float64)).reshape(-1)
        ub = (np.asarray(b, np.float64) - np.asarray(x0, np.float64)).reshape(-1)
        if k.endswith("c_attn.b"):
            ua, ub = np.delete(ua, np.s_[d:2 * d]), np.delete(ub, np.s_[d:2 * d])
        x = np.asarray(x0, np.float32).reshape(-1)
        if k.endswith("c_attn.b"):
            x = np.delete(x, np.s_[d:2 * d])
        # Adam's per-element normalization amplifies round-off for gradient entries near its ε (1e-8); the
        # gradients are compared exactly above, the parameters here only up to a few ulps / 10% of lr.
        tol = 1e-1 * np.abs(ub) + 4.0 * np.spacing(np.abs(x)).astype(np.float64)
        bad = np.abs(ua - ub) > tol
        assert not bad.any(), f"{k}: {bad.sum()} elements differ; max {np.abs(ua - ub).max():.3e}"


def test_adam_matches_torch_adamw_formula():
    """optax.adam(lr, b1, b2, eps) == torch.optim.AdamW(lr, weight_decay=0) update rule."""
    rng = np.random.default_rng(0)
    p = rng.standard_normal(50).astype(np.float32)
    grads = [rng.standard_normal(50).astype(np.float32) for _ in range(4)]
    lr, b1, b2, eps = 1e-2, 0.9, 0.999, 1e-8  # scale-free formula check (float32 params)
    opt = optax.adam(lr, b1=b1, b2=b2, eps=eps)
    st = opt.init(jnp.asarray(p))
    pj = jnp.asarray(p)
    pt, m, v = p.astype(np.float64).copy(), np.zeros(50), np.zeros(50)
    for t, gr in enumerate(grads, 1):
        upd, st = opt.update(jnp.asarray(gr), st, pj)
        pj = optax.apply_updates(pj, upd)
        m = b1 * m + (1 - b1) * gr
        v = b2 * v + (1 - b2) * gr * gr
        mhat, vhat = m / (1 - b1 ** t), v / (1 - b2 ** t)
        pt = pt - lr * mhat / (np.sqrt(vhat) + eps)
    np.testing.assert_allclose(np.asarray(pj, np.float64) - p, pt - p, rtol=1e-4, atol=1e-6)


def test_checkpoint_roundtrip_and_resume(setup, tmp_path):
    r, tr, teacher, student, ids = setup
    fn = tr.step_fn(1, 2, B)
    p, st = student, tr.opt.init(student)
    for k in range(2):
        p, st, _ = fn(p, st, teacher, jnp.asarray(ids_batch(10 + k)))
    state = {"global_step": 2, "protocol_hash": r.protocol_hash()}
    d = save_checkpoint(tmp_path, "step", 3, p, st, state)
    p2, st2, s2 = load_checkpoint(d, tr.opt)
    p2 = jax.tree_util.tree_map(jnp.asarray, p2)
    assert s2["global_step"] == 2 and s2["params_sha256"]
    for (k1, a), (k2, b) in zip(g.flatten_named(p), g.flatten_named(p2)):
        assert np.array_equal(np.asarray(a), np.asarray(b)), k1
    assert int(st2[0].count) == int(st[0].count)
    pa, sta, _ = fn(p, st, teacher, jnp.asarray(ids_batch(12)))
    pb, stb, _ = fn(p2, st2, teacher, jnp.asarray(ids_batch(12)))
    for (k1, a), (k2, b) in zip(g.flatten_named(pa), g.flatten_named(pb)):
        assert np.array_equal(np.asarray(a), np.asarray(b)), k1


def test_schedule_and_batches():
    r = R.Recipe()
    assert r.schedule() == [1, 2, 4, 8, 16, 32, 64] and r.total_steps == 9766 and r.training_tokens == 50_001_920
    ends, c = [], 0
    for i in range(7):
        c = S.next_stage_end_step(c, r.total_steps, i, 7)
        ends.append(c)
    assert ends == [1396, 2791, 4186, 5581, 6976, 8371, 9766]  # sibling metrics.csv stage boundaries
    toks = np.arange(100_000, dtype=np.int32)
    b = D.unlabeled_batch(toks, 512, 10, 3)
    assert b.shape == (10, 512) and b[0, 0] == 3 * 5120
    x, y = D.labeled_batch(np.arange(4096, dtype=np.int32), 32, 1, 1)
    assert x[0, 0] == 33 and y[0, 0] == 34 and x.shape == (1, 32)
    assert D.probe_token_count(r) == 4096
    assert D.tile_tokens(np.arange(903), 4096).size == 4096
    m = S.TrackingResidualMonitor(0.99, 64)
    assert not any(m.update(0.9) for _ in range(70))
    m2 = S.TrackingResidualMonitor(0.99, 8)
    for _ in range(8):
        m2.update(0.5)
    assert m2.baseline == 0.5 and m2.hold_threshold == 0.75
    assert m2.update(1.1) is False  # EMA moves slowly
    assert m2.update(60.0) is True  # EMA 0.99·0.506 + 0.01·60 > 1.02


def test_last_step_uses_max_start_formula():
    numel = R.OWT_TOKENS
    r = R.Recipe()
    s = D.batch_start(numel, r.tokens_per_step, r.total_steps - 1)
    assert s == (r.total_steps - 1) * r.tokens_per_step  # no wrap: tail beyond 50,001,920 untouched
