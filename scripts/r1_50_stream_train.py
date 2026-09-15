"""R1-50: train the reader on stream-scale episodes (recovery plan M1/M2), then evaluate on both development streams.
    python scripts/r1_50_stream_train.py [--pool-items 1000] [--steps 300] [--batch 2] [--n-memory 64] [--tag ...] [--no-lease]
    → results/R1/pilot/<tag>/{metrics.jsonl,summary.json}; weights under assets; bank cached under assets."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
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
    ap.add_argument("--pool", default="manifests/revision_v1/train_pool_counterfact_v1.json", help="one pool, or several separated by ',' (mixed-domain training)")
    ap.add_argument("--pool-items", type=int, default=1000)
    ap.add_argument("--held-out", type=int, default=100, help="last N bank items are held out for dev episodes")
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--n-memory", type=int, default=64)
    ap.add_argument("--n-query-records", type=int, default=8)
    ap.add_argument("--n-out", type=int, default=8)
    ap.add_argument("--kappa", type=float, default=0.0, help="HT-3: coupled-logarithm kappa in the answer and preservation terms (0 = current objective)")
    ap.add_argument("--clip-surprisal", type=float, default=None, help="HT-3 comparator: clip the answer surprisal at this value")
    ap.add_argument("--min-mem-mb", type=int, default=4096, help="R1-69 memory guard: stop (keeping the best checkpoint) when MemAvailable drops below this")
    ap.add_argument("--clear-caches-every", type=int, default=50, help="R1-69: jax.clear_caches() every N steps to bound resident executables")
    ap.add_argument("--out-para-nulls", action="store_true", help="R1-66: also use the question/paraphrase form of out-of-memory items as null queries")
    ap.add_argument("--out-para-prob", type=float, default=1.0, help="R1-66: fraction of out-of-memory items that also contribute a paraphrase-form null")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--dev-every", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="r1_50_stream")
    ap.add_argument("--no-lease", action="store_true")
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json", help="lexical feature stop list (M4); 'none' disables the lexical feature")
    ap.add_argument("--no-query-null", action="store_true", help="null without the query-only linear term (pairwise + lexical only)")
    ap.add_argument("--lex-idf", action="store_true", help="R1-57c: memory-rarity-weighted lexical overlap")
    ap.add_argument("--text-nulls", type=int, default=0, help="ordinary-text null queries per episode (R1-54; OpenWebText training range)")
    ap.add_argument("--text-windows", type=int, default=512)
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.observations import ObservationEncoder
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from pccap.revision_v1.stream_train import (
        add_text_nulls,
        bank_identity,
        build_bank,
        build_text_bank,
        merge_banks,
        stream_episode,
        stream_episode_mixed,
        verify_bank,
    )
    from pccap.revision_v1.train import LossConfig
    from pccap.revision_v1.train_fast import FastTrainer

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))

    def _reader_config(**kw):
        if args.stop_tokens == "none":
            return ReaderConfig(lexical=False, query_null=not args.no_query_null, **kw)
        toks = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
        return ReaderConfig(lexical=True, stop_tokens=toks, query_null=not args.no_query_null, lex_idf=args.lex_idf, **kw)
    rc, cc = _reader_config(), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    OUT = OUT_ROOT / args.tag
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; choose a new tag")
    OUT.mkdir(parents=True)
    pools = [x for x in args.pool.split(",") if x]
    t_start = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:stream_train", stage="R1", projected_seconds=3 * 3600.0)):
        ledger = Ledger()
        base = BPBase(ledger=ledger)
        enc = ObservationEncoder(base, taps=rc.taps)
        t0 = time.time()
        banks, offsets = [], []
        for pool in pools:
            rows = json.loads((ROOT / pool).read_text())["items"][: args.pool_items]
            bank_path = ASSETS / "banks" / f"{Path(pool).stem}_{args.pool_items}.pkl"
            expected = bank_identity(rows, enc.base_hash, enc.encoder_version, rc.taps, 2, 2, np.float16)
            if bank_path.exists():
                b = pickle.loads(bank_path.read_bytes())
                if not getattr(b, "identity", None):  # banks built before R50-06 carry no identity: verify content against the pool, then stamp
                    if b.content_hash() != hashlib.sha256(b"".join(it.item_id.encode() + np.asarray(it.prompt_ids, np.int32).tobytes() + np.asarray(it.answer_ids, np.int32).tobytes() for it in b.items)).hexdigest() or len(b.items) != len(rows) or any(it.item_id != r["item_id"] for it, r in zip(b.items, rows)):
                        raise SystemExit(f"cached bank {bank_path} does not match the pool; delete it")
                    b.identity = dict(expected)
                    bank_path.write_bytes(pickle.dumps(b))
                verify_bank(b, expected)
                print(json.dumps({"bank": "loaded", "pool": pool, "items": len(b.items), "bank_sha256": b.content_hash()}), flush=True)
            else:
                b = build_bank(base, enc, rows, rc, progress=100)
                bank_path.parent.mkdir(parents=True, exist_ok=True)
                bank_path.write_bytes(pickle.dumps(b))
                print(json.dumps({"bank": "built", "pool": pool, "items": len(b.items), "passes": b.cost.extra_pass_forwards, "wall_s": round(time.time() - t0)}), flush=True)
            offsets.append(sum(len(x.items) for x in banks))
            banks.append(b)
        bank = merge_banks(banks)
        text_bank = []
        if args.text_nulls:
            from pccap.distill.data import load_shard
            shard = load_shard(Path("/home/derp/cap/assets/data/raw/openwebtext/openwebtext.bin"))
            text_bank = build_text_bank(base, enc, shard[:50_001_920], rc, n_windows=args.text_windows, seed=args.seed + 7)
            print(json.dumps({"text_bank": len(text_bank), "windows": args.text_windows, "source": "openwebtext training range [0, 50,001,920)"}), flush=True)
        bank_s = time.time() - t0
        # per-pool train/held-out split (the last held_out items of every pool are development)
        train_by_pool, dev_by_pool = [], []
        for off, b in zip(offsets, banks):
            n_b = len(b.items)
            train_by_pool.append(list(range(off, off + n_b - args.held_out)))
            dev_by_pool.append(list(range(off + n_b - args.held_out, off + n_b)))
        train_idx = [i for ix in train_by_pool for i in ix]
        dev_idx = [i for ix in dev_by_pool for i in ix]
        rng = np.random.default_rng(args.seed)
        dev_rng = np.random.default_rng(args.seed + 1000)
        mixed = len(banks) > 1
        dev_eps = [(stream_episode_mixed(dev_by_pool, bank, dev_rng, n_memory=min(args.n_memory, len(dev_idx)), n_query_records=args.n_query_records, n_out=min(args.n_out, 8), episode_id=f"dev-{i}") if mixed
                    else stream_episode(bank, dev_rng, n_memory=min(args.n_memory, len(dev_idx)), n_query_records=args.n_query_records, n_out=min(args.n_out, 8), pool_indices=dev_idx, episode_id=f"dev-{i}")) for i in range(6)]
        dev_eps = [add_text_nulls(e, text_bank, dev_rng, args.text_nulls) for e in dev_eps]
        k1, k2 = jax.random.split(jax.random.PRNGKey(args.seed))
        theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        tr = FastTrainer(rc, cc, base.params, base.cfg, LossConfig(kappa=args.kappa, clip_surprisal=args.clip_surprisal), lr=args.lr, weight_decay=args.weight_decay, ledger=ledger)
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
        def mem_available_mb() -> float:
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024
            return float("inf")

        aborted = None
        for step in range(args.steps):
            if step % 10 == 0:  # R1-69 memory guard: three machine hangs on 2026-09-15 were this trainer exhausting host RAM
                avail = mem_available_mb()
                if avail < args.min_mem_mb:
                    aborted = {"step": step, "mem_available_mb": avail, "reason": f"MemAvailable below {args.min_mem_mb} MB; saved the best checkpoint so far and stopped before the machine thrashed"}
                    print(json.dumps({"memory_guard": aborted}), flush=True)
                    break
            if step and step % args.clear_caches_every == 0:
                jax.clear_caches()  # R1-69: bound the resident compiled-executable set
            batch = [(stream_episode_mixed(train_by_pool, bank, rng, n_memory=args.n_memory, n_query_records=args.n_query_records, n_out=args.n_out, out_paraphrase_nulls=args.out_para_nulls, out_paraphrase_null_prob=args.out_para_prob) if mixed
                      else stream_episode(bank, rng, n_memory=args.n_memory, n_query_records=args.n_query_records, n_out=args.n_out, pool_indices=train_idx, out_paraphrase_nulls=args.out_para_nulls, out_paraphrase_null_prob=args.out_para_prob)) for _ in range(args.batch)]
            batch = [add_text_nulls(b, text_bank, rng, args.text_nulls) for b in batch]
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
        if wdir.exists():
            raise SystemExit(f"{wdir} exists: weights are never overwritten — choose a new tag")
        wdir.mkdir(parents=True)
        np.savez(wdir / "theta.npz", **{jax.tree_util.keystr(path): np.asarray(x) for path, x in jax.tree_util.tree_flatten_with_path(theta)[0]})
        summary = {"args": vars(args), "bank_wall_s": bank_s, "train_wall_s": train_s, "memory_guard_abort": aborted,
                   "banks": [{"pool": pool, "sha256": b.content_hash(), "identity": b.identity, "construction_cost": {"full_forwards": b.cost.full_forwards, "tokens": b.cost.tokens, "accel_seconds": b.cost.accel_seconds}, "shared_cost_policy": "charged once at construction; reuse charges nothing (R50-09)"} for pool, b in zip(pools, banks)], "dev_before": before, "dev_after_best": after, "dev_after_final": evaluate(final_theta),
                   "best_step": best["step"], "theta_hash": params_hash(theta), "theta_path": str(wdir / "theta.npz"), "ledger": ledger.totals(), "total_wall_s": time.time() - t_start}
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
        print(json.dumps({"dev_before": before, "dev_after_best": after, "best_step": best["step"], "train_wall_s": round(train_s)}, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
