"""REG-01 dissection on the real GPT-2 (micro of 2, T=1): compare the FabricPC-path errors and local
weight gradient with plain functional-JAX references built only from gpt2_jax primitives."""
from __future__ import annotations

import json

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.distill import data as D
from pccap.distill import recipe as R
from pccap.distill.train import Trainer, batched_logits
from pccap.harness.lease import gpu_lease
from pccap.pc import epc_inference as epc
from pccap.pc.kd_energy import kd_kl_loss
from pccap.pc.nodes import graph_params_from_numpy, node_names
from pccap.pc.weight_phase import local_weight_energy

r = R.Recipe(micro_batch_size=2)
cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
params_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
shard = D.load_shard(R.SHARD_PATH)
names = node_names(cfg.n_layer)
BETA = r.kd_temperature


def norms(x):  # x: [B, n_layer, L, d]
    return [float(v) for v in jnp.sqrt(jnp.sum(jnp.square(x), axis=(0, 2, 3)))]


def cos(a, b):
    a, b = jnp.ravel(a), jnp.ravel(b)
    return float(jnp.dot(a, b) / (jnp.linalg.norm(a) * jnp.linalg.norm(b) + 1e-30))


def ref_forward_with_errors(params, ids, errors):
    def one(i, errs):
        h = g.embed(params, i)
        for l, blk in enumerate(params["blocks"]):
            h = g.block(blk, h, cfg) + errs[l]
        return g.head(params, h, cfg)
    return jax.vmap(one)(ids, errors)


def ref_energy(errors, params, ids, tl):
    return 0.5 * jnp.sum(jnp.square(errors)) + ids.shape[0] * kd_kl_loss(ref_forward_with_errors(params, ids, errors), tl, BETA)


def ref_local_energy(params, ids, errors, tl):
    def one(i, errs):
        h = g.embed(params, i)
        total = 0.0
        for l, blk in enumerate(params["blocks"]):
            pred = g.block(blk, h, cfg)
            total = total + 0.5 * jnp.sum(jnp.square(pred - jax.lax.stop_gradient(pred) - errs[l]))
            h = jax.lax.stop_gradient(pred + errs[l])
        return total, g.head(params, jax.lax.stop_gradient(h), cfg)
    totals, logits = jax.vmap(one)(ids, errors)
    return jnp.sum(totals) + ids.shape[0] * kd_kl_loss(logits, tl, BETA)


def blocks_norms(tree):
    return [float(jnp.sqrt(sum(jnp.sum(jnp.square(v)) for grp in blk.values() for v in grp.values()))) for blk in tree["blocks"]]


def blocks_cos(a, b):
    out = []
    for x, y in zip(a["blocks"], b["blocks"]):
        fx = jnp.concatenate([jnp.ravel(v) for v in jax.tree_util.tree_leaves(x)])
        fy = jnp.concatenate([jnp.ravel(v) for v in jax.tree_util.tree_leaves(y)])
        out.append(float(jnp.dot(fx, fy) / (jnp.linalg.norm(fx) * jnp.linalg.norm(fy) + 1e-30)))
    return out


with gpu_lease("REG-01", stage="REG", projected_seconds=600):
    teacher = jax.tree_util.tree_map(jnp.asarray, params_np)
    # perturbed student: teacher + N(0, 1e-7) on every weight (a step-1-like state)
    leaves, treedef = jax.tree_util.tree_flatten(teacher)
    keys = jax.random.split(jax.random.PRNGKey(0), len(leaves))
    student = treedef.unflatten([x + 1e-7 * jax.random.normal(k, x.shape, x.dtype) for x, k in zip(leaves, keys)])
    ids = jnp.asarray(D.unlabeled_batch(shard, r.seq_len, 2, 1), jnp.int32)
    tl = jax.jit(lambda p, i: batched_logits(p, i, cfg))(teacher, ids)
    tr = Trainer(cfg, r)
    structure = tr.structure(1)
    clamps = {names["ids"]: ids, names["logits"]: tl}
    gparams = graph_params_from_numpy(student, cfg)
    _, errors, energies, gnorms, _ = jax.jit(lambda gp, cl: epc.relax_errors(gp, structure, cl, None, None, 1, r.error_lr))(gparams, clamps)
    e_fab = jnp.stack([errors[n] for n in names["blocks"]], axis=1)
    zero = jnp.zeros_like(e_fab)
    E0, gref = jax.jit(jax.value_and_grad(ref_energy))(zero, student, ids, tl)
    e_ref = -r.error_lr * gref
    print(json.dumps({"E0_fab": float(energies[0]), "E0_ref": float(E0), "E1_fab": float(energies[1]),
                      "E1_ref": float(ref_energy(e_ref, student, ids, tl)),
                      "err_norms_fab": norms(e_fab), "err_norms_ref": norms(e_ref),
                      "err_cos_per_layer": [cos(e_fab[:, l], e_ref[:, l]) for l in range(cfg.n_layer)]}), flush=True)
    # local weight gradient: FabricPC path vs reference, both at the reference errors and at the fabric errors
    err_dict = {n: e_ref[:, l] for l, n in enumerate(names["blocks"])}
    g_fab = jax.jit(jax.grad(lambda p: local_weight_energy(graph_params_from_numpy(p, cfg), structure, clamps, err_dict)))(student)
    g_ref = jax.jit(jax.grad(lambda p: ref_local_energy(p, ids, e_ref, tl)))(student)
    g_bp = jax.jit(jax.grad(lambda p: ids.shape[0] * kd_kl_loss(batched_logits(p, ids, cfg), tl, BETA)))(student)
    print(json.dumps({"at_ref_errors": {"blocks_norm_fab": blocks_norms(g_fab), "blocks_norm_ref": blocks_norms(g_ref),
                                        "blocks_norm_tau_bp": [0.1 * v for v in blocks_norms(g_bp)],
                                        "cos_fab_ref": blocks_cos(g_fab, g_ref), "cos_ref_bp": blocks_cos(g_ref, g_bp),
                                        "wte_norm_fab_ref_bp": [float(jnp.linalg.norm(x["wte"])) for x in (g_fab, g_ref, g_bp)]}}), flush=True)
