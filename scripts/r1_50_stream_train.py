"""R1-50: train the reader on stream-scale episodes (recovery plan M1/M2), then evaluate on both development streams.
    python scripts/r1_50_stream_train.py [--pool-items 1000] [--steps 300] [--batch 2] [--n-memory 64] [--tag ...] [--no-lease]
    → results/R1/pilot/<tag>/{metrics.jsonl,summary.json}; weights under assets; bank cached under assets."""

from __future__ import annotations

import argparse
import contextlib
import json
import pickle
import time
from pathlib import Path

import jax
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "results" / "R1" / "pilot"
ASSETS = Path("/home/derp/cap/assets/runs/pc_cap/R1")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="manifests/revision_v1/train_pool_counterfact_v1.json")
    ap.add_argument("--pool-items", type=int, default=1000)
    ap.add_argument("--held-out", type=int, default=100, help="last N bank items are held out for dev episodes")
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--n-memory", type=int, default=64)
    ap.add_argument("--n-query-records", type=int, default=8)
    ap.add_argument("--n-out", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--dev-every", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="r1_50_stream")
    ap.add_argument("--no-lease", action="store_true")
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json", help="lexical feature stop list (M4); 'none' disables the lexical feature")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.observations import ObservationEncoder
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from pccap.revision_v1.stream_train import build_bank, stream_episode
    from pccap.revision_v1.train import LossConfig
    from pccap.revision_v1.train_fast import FastTrainer

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))

    def _reader_config(**kw):
        if args.stop_tokens == "none":
            return ReaderConfig(lexical=False, **kw)
        toks = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
        return ReaderConfig(lexical=True, stop_tokens=toks, **kw)
    rc, cc = _reader_config(), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    OUT = OUT_ROOT / args.tag
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; choose a new tag")
    OUT.mkdir(parents=True)
    rows = json.loads((ROOT / args.pool).read_text())["items"][: args.pool_items]
    bank_path = ASSETS / "banks" / f"{Path(args.pool).stem}_{args.pool_items}.pkl"
    t_start = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:stream_train", stage="R1", projected_seconds=3 * 3600.0)):
        ledger = Ledger()
        base = BPBase(ledger=ledger)
        enc = ObservationEncoder(base, taps=rc.taps)
        t0 = time.time()
        if bank_path.exists():
            bank = pickle.loads(bank_path.read_bytes())
            print(json.dumps({"bank": "loaded", "items": len(bank.items), "path": str(bank_path)}), flush=True)
        else:
            bank = build_bank(base, enc, rows, rc, progress=100)
            bank_path.parent.mkdir(parents=True, exist_ok=True)
            bank_path.write_bytes(pickle.dumps(bank))
            print(json.dumps({"bank": "built", "items": len(bank.items), "passes": bank.cost.extra_pass_forwards, "wall_s": round(time.time() - t0)}), flush=True)
        bank_s = time.time() - t0
        n = len(bank.items)
        train_idx = list(range(0, n - args.held_out))
        dev_idx = list(range(n - args.held_out, n))
        rng = np.random.default_rng(args.seed)
        dev_rng = np.random.default_rng(args.seed + 1000)
        dev_eps = [stream_episode(bank, dev_rng, n_memory=min(args.n_memory, len(dev_idx)), n_query_records=args.n_query_records, n_out=min(args.n_out, 8), pool_indices=dev_idx, episode_id=f"dev-{i}") for i in range(6)]
        k1, k2 = jax.random.split(jax.random.PRNGKey(args.seed))
        theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        tr = FastTrainer(rc, cc, base.params, base.cfg, LossConfig(), lr=args.lr, weight_decay=args.weight_decay)
        st = tr.init(theta)

        def evaluate(th):
            agg = {}
            for f in dev_eps:
                _, m = tr.episode_grads(th, f)
                for k, v in m.items():
                    agg[k] = agg.get(k, 0.0) + v / len(dev_eps)
            return agg

        before = evaluate(theta)
        best = {"dev_retrieval": float("inf"), "step": -1, "theta": None}
        log = (OUT / "metrics.jsonl").open("w")
        t0 = time.time()
        for step in range(args.steps):
            batch = [stream_episode(bank, rng, n_memory=args.n_memory, n_query_records=args.n_query_records, n_out=args.n_out, pool_indices=train_idx) for _ in range(args.batch)]
            theta, st, m = tr.outer_step(theta, st, batch)
            m.update(step=step, wall_s=time.time() - t0)
            if args.dev_every and (step + 1) % args.dev_every == 0:
                dv = evaluate(theta)
                m.update({f"dev_{k}": v for k, v in dv.items() if k in ("answer", "retrieval", "preserve")})
                if dv["retrieval"] < best["dev_retrieval"]:
                    best = {"dev_retrieval": dv["retrieval"], "step": step, "theta": jax.tree_util.tree_map(lambda x: np.array(x), theta)}
            log.write(json.dumps(m) + "\n")
            log.flush()
            if step % 10 == 0:
                print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}), flush=True)
        train_s = time.time() - t0
        final_theta = theta
        if best["theta"] is not None:
            theta = jax.tree_util.tree_map(lambda x: jax.numpy.asarray(x), best["theta"])
        after = evaluate(theta)
        wdir = ASSETS / "pilot" / args.tag
        wdir.mkdir(parents=True, exist_ok=True)
        np.savez(wdir / "theta.npz", **{jax.tree_util.keystr(path): np.asarray(x) for path, x in jax.tree_util.tree_flatten_with_path(theta)[0]})
        summary = {"args": vars(args), "bank_wall_s": bank_s, "train_wall_s": train_s, "dev_before": before, "dev_after_best": after, "dev_after_final": evaluate(final_theta),
                   "best_step": best["step"], "theta_hash": params_hash(theta), "theta_path": str(wdir / "theta.npz"), "ledger": ledger.totals(), "total_wall_s": time.time() - t_start}
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
        print(json.dumps({"dev_before": before, "dev_after_best": after, "best_step": best["step"], "train_wall_s": round(train_s)}, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
