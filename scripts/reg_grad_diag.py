"""REG-01 diagnostic: per-layer gradient and Adam-update norms for the first steps, to compare with the
sibling's layerwise.csv (pc_norm per layer at steps 0, 1, 5). Prints JSON lines; no files written."""
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
from pccap.distill.train import Trainer
from pccap.harness.lease import gpu_lease

steps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
micro = int(sys.argv[2]) if len(sys.argv) > 2 else 5


def group_norms(tree) -> dict:
    out = {"embedding": float(jnp.sqrt(jnp.sum(jnp.square(tree["wte"])) + jnp.sum(jnp.square(tree["wpe"])))),
           "wte": float(jnp.linalg.norm(tree["wte"])), "wpe": float(jnp.linalg.norm(tree["wpe"])),
           "ln_f": float(jnp.sqrt(jnp.sum(jnp.square(tree["ln_f"]["g"])) + jnp.sum(jnp.square(tree["ln_f"]["b"]))))}
    for l, blk in enumerate(tree["blocks"]):
        out[f"block_{l:02d}"] = float(jnp.sqrt(sum(jnp.sum(jnp.square(v)) for grp in blk.values() for v in grp.values())))
    return out


r = R.Recipe(micro_batch_size=micro)
cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
params_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
shard = D.load_shard(R.SHARD_PATH)
tr = Trainer(cfg, r)
teacher = jax.tree_util.tree_map(jnp.asarray, params_np)
with gpu_lease("REG-01", stage="REG", projected_seconds=600):
    params = jax.tree_util.tree_map(jnp.asarray, params_np)
    opt_state = tr.opt.init(params)
    fn = tr.step_fn(1, micro, r.batch_size, debug_grads=True)
    for k in range(steps):
        ids = jnp.asarray(D.unlabeled_batch(shard, r.seq_len, r.batch_size, k), jnp.int32)
        new_params, opt_state, stats = fn(params, opt_state, teacher, ids)
        upd = jax.tree_util.tree_map(lambda a, b: a - b, new_params, params)
        gn = group_norms(stats["grads"])
        un = group_norms(upd)
        # fraction of block elements whose |g| exceeds Adam eps
        blk = stats["grads"]["blocks"][0]
        frac = float(np.mean(np.abs(np.concatenate([np.asarray(v).ravel() for grp in blk.values() for v in grp.values()])) > 1e-8))
        print(json.dumps({"step": k, "bp_loss": float(stats["inner_energy_start"]), "pc_loss": float(stats["pc_loss"]),
                          "grad_norm": float(stats["pc_grad_norm"]), "grad_group_norms": gn, "update_group_norms": un,
                          "block0_frac_abs_g_gt_eps": frac,
                          "err_norms_micro0": np.asarray(stats["error_norms_micro0"]).tolist()}), flush=True)
        params = new_params
