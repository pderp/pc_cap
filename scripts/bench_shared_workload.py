"""ENV-02: shared-workload benchmark and the provisional conversion factor kappa (PA-3).

(a) GPT-2 small fp32 (TF32 off), batch 8 x 128 tokens, forward+backward w.r.t. all parameters,
    30 s warmup then 60 s steady state -> tokens/s;
(b) batch-1 forward latency for prefixes of 16/32/64 tokens, 500 calls each, median and p95;
(c) peak device memory.
Run under the exclusive GPU lease (nvidia-smi compute apps captured before/after).

    python scripts/bench_shared_workload.py           # run (writes results/ENV/bench.json, kappa.json)
    python scripts/bench_shared_workload.py --check   # reload and print both files
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import pccap  # noqa: F401  (determinism flags first)

_ = pccap.__version__
import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402

from pccap.bases import gpt2_jax as g  # noqa: E402
from pccap.bases.bp import BPBase  # noqa: E402
from pccap.harness.lease import gpu_lease  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "ENV"


def env_hash() -> str:
    return hashlib.sha256((ROOT / "requirements.lock").read_bytes()).hexdigest()[:16]


def bench_train_step(params, cfg, B=8, T=128, warmup_s=30.0, steady_s=60.0, seed=0):
    def loss_fn(p, ids):
        def one(seq):
            h = g.embed(p, seq)
            h, _, _ = g.run_blocks(p, h, jnp.int32(T - 1), jnp.zeros((3, cfg.d), jnp.float32), cfg, 0)
            logits = g.head(p, h, cfg)
            lp = jax.nn.log_softmax(logits[:-1], axis=-1)
            return -jnp.mean(jnp.take_along_axis(lp, seq[1:, None], axis=-1))

        return jnp.mean(jax.vmap(one)(ids))

    step = jax.jit(jax.value_and_grad(loss_fn))
    rng = np.random.default_rng(seed)

    def batch():
        return jnp.asarray(rng.integers(0, cfg.vocab, size=(B, T), dtype=np.int32))

    t0 = time.perf_counter()
    n = 0
    while time.perf_counter() - t0 < warmup_s:
        loss, grads = step(params, batch())
        jax.block_until_ready(grads)
        n += 1
    warm = {"steps": n, "seconds": time.perf_counter() - t0}
    t1 = time.perf_counter()
    n = 0
    while time.perf_counter() - t1 < steady_s:
        loss, grads = step(params, batch())
        jax.block_until_ready(grads)
        n += 1
    dt = time.perf_counter() - t1
    return {"batch": B, "tokens_per_step": B * T, "steps": n, "seconds": dt,
            "tokens_per_second": n * B * T / dt, "seconds_per_step": dt / n, "warmup": warm,
            "last_loss": float(loss)}


def bench_latency(base: BPBase, lengths=(16, 32, 64), calls=500, seed=1):
    rng = np.random.default_rng(seed)
    out = {}
    for n in lengths:
        ids = rng.integers(0, base.vocab, size=n).astype(np.int32)
        for _ in range(20):  # compile + warm
            jax.block_until_ready(base.forward(ids, phase="query").logits)
        ts = []
        for _ in range(calls):
            t0 = time.perf_counter()
            jax.block_until_ready(base.forward(ids, phase="query").logits)
            ts.append(time.perf_counter() - t0)
        ts = np.asarray(ts)
        out[str(n)] = {"calls": calls, "median_ms": float(np.median(ts) * 1e3), "p95_ms": float(np.percentile(ts, 95) * 1e3),
                       "mean_ms": float(ts.mean() * 1e3), "bucket": g.bucket_len(n)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--warmup", type=float, default=30.0)
    ap.add_argument("--steady", type=float, default=60.0)
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.check:
        for f in ("bench.json", "kappa.json"):
            print(f, json.dumps(json.loads((OUT / f).read_text()), indent=1))
        return 0
    with gpu_lease("ENV-02", stage="ENV", projected_seconds=180, exclusive=True) as lease:
        base = BPBase()
        params_np = jax.tree_util.tree_map(np.asarray, base.params)
        dev = jax.devices()[0]
        train = bench_train_step(base.params, base.cfg, warmup_s=args.warmup, steady_s=args.steady)
        lat = bench_latency(base)
        stats = dev.memory_stats() or {}
        bench = {
            "device": dev.device_kind, "compute_capability": getattr(dev, "compute_capability", None),
            "env_lock_sha16": env_hash(), "determinism": pccap.determinism_report(), "python": platform.python_version(),
            "train_step": train, "forward_latency": lat,
            "peak_bytes_in_use": stats.get("peak_bytes_in_use"), "peak_mib": (stats.get("peak_bytes_in_use") or 0) / 2**20,
            "params_bytes": int(sum(a.nbytes for _, a in g.flatten_named(params_np))),
            "lease": lease.report, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    (OUT / "bench.json").write_text(json.dumps(bench, indent=1))
    kappa = {"kappa": 1.0, "kappa_band": [0.5, 2.0], "status": "provisional",
             "definition": "one local RTX 5070 hour = kappa A100-equivalent hours (PA-3)",
             "local_measurement": {"train_tokens_per_second": train["tokens_per_second"], "env_lock_sha16": env_hash()},
             "a100_measurement": None, "timestamp": bench["timestamp"]}
    (OUT / "kappa.json").write_text(json.dumps(kappa, indent=1))
    print(json.dumps({"tokens_per_second": train["tokens_per_second"], "latency": lat, "peak_mib": bench["peak_mib"],
                      "other_cuda_processes": lease.other_cuda_processes()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
