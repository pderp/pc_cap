"""REG-01 timing/memory probe: one compile step + ``--timed`` measured steps per relaxation horizon T
of the production schedule on the real GPT-2 and real OpenWebText batches (not part of the protocol
run; weights are discarded). Writes results/REG/timing_probe.json.

    python scripts/reg_timing_probe.py --micro 5 --timed 2
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.distill import data as D
from pccap.distill import recipe as R
from pccap.distill.train import Trainer, _peak_mib
from pccap.harness.lease import gpu_lease

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--micro", type=int, default=5)
    ap.add_argument("--timed", type=int, default=2)
    ap.add_argument("--schedule", type=int, nargs="*", default=None)
    ap.add_argument("--out", default=str(ROOT / "results" / "REG" / "timing_probe.json"))
    args = ap.parse_args()
    r = R.Recipe(micro_batch_size=args.micro)
    cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
    params_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
    shard = D.load_shard(R.SHARD_PATH)
    tr = Trainer(cfg, r)
    teacher = jax.tree_util.tree_map(jnp.asarray, params_np)
    rows = []
    with gpu_lease("REG-01", stage="REG", projected_seconds=1800, exclusive=True) as lease:
        params = jax.tree_util.tree_map(jnp.asarray, params_np)
        opt_state = tr.opt.init(params)
        for T in (args.schedule or r.schedule()):
            fn = tr.step_fn(T, args.micro, r.batch_size)
            times = []
            for k in range(1 + args.timed):
                ids = jnp.asarray(D.unlabeled_batch(shard, r.seq_len, r.batch_size, 5000 + k), jnp.int32)
                t0 = time.time()
                params, opt_state, stats = fn(params, opt_state, teacher, ids)
                jax.block_until_ready(params)
                times.append(time.time() - t0)
            row = {"T": T, "micro": args.micro, "compile_plus_first_step_s": times[0], "step_s": times[1:],
                   "mean_step_s": float(np.mean(times[1:])), "peak_mem_mib": _peak_mib(),
                   "bp_loss": float(stats["inner_energy_start"]), "pc_loss": float(stats["pc_loss"])}
            rows.append(row)
            print(json.dumps(row), flush=True)
        report = lease.report
    total_steps = r.total_steps
    per_stage = [1396] + [1395] * 6
    proj = sum(s * rw["mean_step_s"] for s, rw in zip(per_stage, rows)) if len(rows) == 7 else None
    out = {"rows": rows, "micro": args.micro, "projected_seconds_full_run": proj,
           "projected_hours_full_run": proj / 3600 if proj else None, "steps_per_stage": per_stage, "total_steps": total_steps,
           "lease": report, "determinism": pccap.determinism_report()}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1, default=float))
    print("projected hours:", out["projected_hours_full_run"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
