"""REG-01 diagnostic: on the real GPT-2, compare the PC weight gradient (relax T=1 + local energy) with the
BP gradient of the token-mean KD loss at the same state, per layer group (the sibling logs cosine ≈ 0.9999 and
norm ratio pc/(τ·bp) ≈ 1.00 for blocks, ≈ 10 for embedding/readout). Also the BP gradient profile at a
noise-perturbed state (teacher + N(0, σ)). Prints JSON lines."""
from __future__ import annotations

import json
import sys

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.distill import data as D
from pccap.distill import recipe as R
from pccap.distill.train import Trainer, batched_logits
from pccap.harness.lease import gpu_lease
from pccap.pc.kd_energy import kd_kl_loss

micro = 5
r = R.Recipe(micro_batch_size=micro)
cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
params_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
shard = D.load_shard(R.SHARD_PATH)
tr = Trainer(cfg, r)
teacher = jax.tree_util.tree_map(jnp.asarray, params_np)
B = r.batch_size


def groups(tree):
    out = {"embedding": jnp.sqrt(jnp.sum(jnp.square(tree["wte"])) + jnp.sum(jnp.square(tree["wpe"]))),
           "ln_f": jnp.sqrt(jnp.sum(jnp.square(tree["ln_f"]["g"])) + jnp.sum(jnp.square(tree["ln_f"]["b"])))}
    for l, blk in enumerate(tree["blocks"]):
        out[f"block_{l:02d}"] = jnp.sqrt(sum(jnp.sum(jnp.square(v)) for grp in blk.values() for v in grp.values()))
    return {k: float(v) for k, v in out.items()}


def group_cos(a, b):
    def flat(tree, sel):
        return jnp.concatenate([jnp.ravel(v) for v in jax.tree_util.tree_leaves(sel(tree))])
    sels = {"embedding": lambda t: (t["wte"], t["wpe"]), "ln_f": lambda t: t["ln_f"]}
    for l in range(cfg.n_layer):
        sels[f"block_{l:02d}"] = (lambda l: lambda t: t["blocks"][l])(l)
    out = {}
    for k, sel in sels.items():
        x, y = flat(a, sel), flat(b, sel)
        out[k] = float(jnp.dot(x, y) / (jnp.linalg.norm(x) * jnp.linalg.norm(y) + 1e-30))
    return out


@jax.jit
def bp_grad_micro(params, teacher, ids_m):
    def loss(p):
        return kd_kl_loss(batched_logits(p, ids_m, cfg), batched_logits(teacher, ids_m, cfg), r.kd_temperature) * ids_m.shape[0] / B
    return jax.value_and_grad(loss)(params)


def bp_grad(params, ids):
    acc = None
    tot = 0.0
    for j in range(0, B, micro):
        val, gr = bp_grad_micro(params, teacher, ids[j: j + micro])
        acc = gr if acc is None else jax.tree_util.tree_map(jnp.add, acc, gr)
        tot += float(val)
    return tot, acc


with gpu_lease("REG-01", stage="REG", projected_seconds=900):
    params = jax.tree_util.tree_map(jnp.asarray, params_np)
    opt_state = tr.opt.init(params)
    fn = tr.step_fn(1, micro, B, debug_grads=True)
    tau = r.error_lr * 1
    for k in range(3):
        ids = jnp.asarray(D.unlabeled_batch(shard, r.seq_len, r.batch_size, k), jnp.int32)
        kl, bpg = bp_grad(params, ids)
        new_params, opt_state, stats = fn(params, opt_state, teacher, ids)
        pcg = stats["grads"]
        gn_pc, gn_bp = groups(pcg), groups(bpg)
        print(json.dumps({"state": f"trajectory step {k}", "kl_bp": kl, "kl_pc_E0": float(stats["inner_energy_start"]),
                          "norm_ratio_pc_over_tau_bp": {kk: gn_pc[kk] / (tau * gn_bp[kk] + 1e-30) for kk in gn_pc},
                          "cosine": group_cos(pcg, bpg), "bp_group_norms": gn_bp, "pc_group_norms": gn_pc}), flush=True)
        params = new_params
    ids = jnp.asarray(D.unlabeled_batch(shard, r.seq_len, r.batch_size, 1), jnp.int32)
    for sigma in (1e-8, 1e-7, 1e-6):
        key = jax.random.PRNGKey(0)
        leaves, treedef = jax.tree_util.tree_flatten(teacher)
        keys = jax.random.split(key, len(leaves))
        pert = treedef.unflatten([x + sigma * jax.random.normal(kk, x.shape, x.dtype) for x, kk in zip(leaves, keys)])
        kl, bpg = bp_grad(pert, ids)
        print(json.dumps({"state": f"teacher + N(0,{sigma}) all weights", "kl_bp": kl, "bp_group_norms": groups(bpg)}), flush=True)
    # wte-only perturbation (rows of the tokens in batch 0, ±3e-7 like Adam's first update on those rows)
    ids0 = D.unlabeled_batch(shard, r.seq_len, r.batch_size, 0)
    rows = np.unique(ids0)
    key = jax.random.PRNGKey(1)
    pert = dict(teacher)
    delta = jnp.zeros_like(teacher["wte"]).at[jnp.asarray(rows)].set(3e-7 * jnp.sign(jax.random.normal(key, (rows.size, cfg.d))))
    pert = {**teacher, "wte": teacher["wte"] + delta}
    kl, bpg = bp_grad(pert, ids)
    print(json.dumps({"state": "teacher + ±3e-7 on wte rows of batch 0", "kl_bp": kl, "bp_group_norms": groups(bpg)}), flush=True)
