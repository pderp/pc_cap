"""R1-21 bounded pilot: train the reader/controller on synthetic episodes (train split) with the differentiable reference,
evaluate loss terms on held-out dev-split episodes before/after, then the behavioural check (gate 7, synthetic domain):
a fresh RevisionCap adapts on each dev episode's supports and answers its queries by greedy decoding.
    python scripts/r1_21_pilot.py [--train 64] [--dev 16] [--steps 100] [--batch 4] [--lr 1e-4]
    → results/R1/pilot/{metrics.jsonl,summary.json,theta.npz}"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np


def jnp_asarray(x):
    return jnp.asarray(x)

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "results" / "R1" / "pilot"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", type=int, default=64)
    ap.add_argument("--dev", type=int, default=16)
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--estimator", choices=("bp", "epc"), default="bp", help="bp = differentiable reference; epc = alternating ePC surrogate (matched schedule)")
    ap.add_argument("--iters", type=int, default=8, help="ePC settling iterations")
    ap.add_argument("--tag", default=None, help="output subfolder (default: the estimator name)")
    ap.add_argument("--domain", choices=("synthetic", "counterfact"), default="synthetic", help="episode source: synthetic generator or CounterFact natural episodes (tokenized by Codex's adapter)")
    ap.add_argument("--history", type=int, default=4)
    ap.add_argument("--no-lease", action="store_true", help="run beside another lease holder (small footprint; development pilots only)")
    ap.add_argument("--fresh-episodes", action="store_true", help="draw a new batch of training episodes (new seeds) at every step instead of cycling a fixed set")
    ap.add_argument("--dev-every", type=int, default=0, help="evaluate the dev losses every N steps (0 = only before/after) and keep the best-dev weights")
    ap.add_argument("--weight-decay", type=float, default=0.0)
    ap.add_argument("--mix-synthetic", type=float, default=0.0, help="fraction of each batch drawn from synthetic episodes when --domain counterfact")
    ap.add_argument("--pool", default=None, help="natural rows source: a train_pool manifest (DEC-037) instead of the development pools")
    ap.add_argument("--eval-theta", default=None, help="skip training: load these weights and run the dev + behavioural evaluation only")
    ap.add_argument("--eval-fast-steps", type=int, default=0, help="fast steps in the behavioural check (default 0 = initial codes only)")
    ap.add_argument("--eval-fast-lr", type=float, default=1e-2)
    ap.add_argument("--eval-delta-steps", type=int, default=0, help="v0-style delta-write steps per support in the behavioural check")
    ap.add_argument("--eval-delta-lr", type=float, default=0.1)
    ap.add_argument("--no-pairwise-null", action="store_true", help="reader without the pairwise null head (weights trained before it existed)")
    ap.add_argument("--locality-queries", action="store_true", help="natural episodes: add the new support row's locality prompts as null-target queries (role 'unrelated'; the streams' LS prompts are exactly these near-neighbours)")
    args = ap.parse_args()
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.adapt import FastConfig, adapt_record
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.episodes import synthetic_episode
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.observations import ObservationEncoder
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from pccap.revision_v1.train import ANSWER_ROLES, LossConfig, Trainer, episode_grads, featurize

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    rc, cc = ReaderConfig(pairwise_null=not args.no_pairwise_null), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    OUT = OUT_ROOT / (args.tag or args.estimator)
    OUT.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    import contextlib
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:pilot", stage="R1", projected_seconds=3 * 3600.0)):
        ledger = Ledger()
        if args.estimator == "epc":
            from pccap.bases.epc import EPCBase
            base = EPCBase(ledger=ledger)
        else:
            base = BPBase(ledger=ledger)
        enc = ObservationEncoder(base, taps=rc.taps)
        t0 = time.time()
        if args.domain == "synthetic":
            train_eps = [synthetic_episode(1000 + i, "train", history_size=args.history) for i in range(args.train)]
            dev_eps = [synthetic_episode(5000 + i, "dev", history_size=args.history) for i in range(args.dev)]
        else:
            from pccap.data.tokenize import GPT2Tokenizer
            from pccap.revision_v1.episodes import load_development, natural_episode
            from r1_20_text_adapter import (
                tokenize_natural_episode,  # Codex R1-20: project tokenization convention
            )
            if args.pool:
                pool = json.loads(Path(args.pool).read_text())
                assert pool.get("mode") == "train_pool", "only a declared training pool may replace the development pools"
                rows = pool["items"]
            else:
                rows, _ = load_development(ROOT)
            tok = GPT2Tokenizer()

            by_item = {r["item_id"]: r for r in rows}

            def with_locality(ep):
                if not args.locality_queries:
                    return ep
                from dataclasses import replace as _replace

                from pccap.revision_v1.contracts import PredictionQuery, QueryLabel
                qs, ls = list(ep.inputs.queries), list(ep.query_labels)
                for sup in ep.inputs.new_support:
                    row = by_item.get(sup.record_id.split(":")[0])
                    for i, lp in enumerate((row or {}).get("locality_prompts", [])[:2]):
                        qid = f"loc:{sup.record_id}:{i}"
                        qs.append(PredictionQuery(query_id=qid, prompt_ids=tuple(int(x) for x in tok.encode(lp)), prompt=lp))
                        ls.append(QueryLabel(query_id=qid, role="unrelated", entity_ids=(), family_id=sup.family_id, target_ids=(), target=None, target_source="teacher_prediction_required", supporting_record_ids=()))
                return _replace(ep, inputs=_replace(ep.inputs, queries=tuple(qs)), query_labels=tuple(ls))

            def natural(seeds, split, want):
                out, skipped = [], 0
                for sd in seeds:
                    try:
                        out.append(with_locality(tokenize_natural_episode(natural_episode(rows, sd, split, history_size=args.history, dataset="counterfact"), tok)))
                    except ValueError:
                        skipped += 1
                    if len(out) == want:
                        break
                print(json.dumps({"split": split, "episodes": len(out), "skipped": skipped}), flush=True)
                return out

            train_eps = natural(range(1000, 1000 + 4 * args.train), "train", args.train)
            dev_eps = natural(range(5000, 5000 + 4 * args.dev), "dev", args.dev)
        train_f = [featurize(base, enc, e, rc) for e in train_eps]
        dev_f = [featurize(base, enc, e, rc) for e in dev_eps]
        feat_s = time.time() - t0
        k1, k2 = jax.random.split(jax.random.PRNGKey(args.seed))
        theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        if args.estimator == "epc":
            from pccap.revision_v1.epc_train import EPCTrainer, EPCWriteGradients
            tr = EPCTrainer(rc, cc, EPCWriteGradients(base, iters=args.iters), LossConfig(), lr=args.lr, weight_decay=args.weight_decay)
        else:
            tr = Trainer(rc, cc, base.params, base.cfg, LossConfig(), lr=args.lr, weight_decay=args.weight_decay)
        st = tr.init(theta)

        def evaluate(th):
            agg = {}
            for f in dev_f:
                _, m = episode_grads(th, rc, cc, base.params, base.cfg, f, tr.lc)
                for k, v in m.items():
                    agg[k] = agg.get(k, 0.0) + v / len(dev_f)
            return agg

        if args.eval_theta:
            from r1_13_stream_eval import load_theta  # keystr-named npz → pytree
            theta = load_theta(Path(args.eval_theta), theta)
            args.steps = 0
        before = evaluate(theta)
        rng = np.random.default_rng(args.seed)
        log = (OUT / "metrics.jsonl").open("w")
        t0 = time.time()
        best = {"dev_answer": float("inf"), "step": -1, "theta": None}
        fresh_seed = 20000
        for step in range(args.steps):
            if args.fresh_episodes:
                batch = []
                n_syn = int(round(args.batch * args.mix_synthetic)) if args.domain == "counterfact" else 0
                for b in range(args.batch):
                    fresh_seed += 1
                    if b < n_syn or args.domain == "synthetic":
                        ep = synthetic_episode(fresh_seed, "train", history_size=args.history)
                    else:
                        ep = None
                        while ep is None:
                            try:
                                ep = with_locality(tokenize_natural_episode(natural_episode(rows, fresh_seed, "train", history_size=args.history, dataset="counterfact"), tok))
                            except ValueError:
                                fresh_seed += 1
                    batch.append(featurize(base, enc, ep, rc))
            else:
                idx = rng.choice(len(train_f), size=args.batch, replace=False)
                batch = [train_f[i] for i in idx]
            theta, st, m = tr.outer_step(theta, st, batch)
            m.update(step=step, wall_s=time.time() - t0)
            if args.dev_every and (step + 1) % args.dev_every == 0:
                dv = evaluate(theta)
                m.update({f"dev_{k}": v for k, v in dv.items() if k in ("answer", "retrieval", "preserve")})
                if dv["answer"] < best["dev_answer"]:
                    best = {"dev_answer": dv["answer"], "step": step, "theta": jax.tree_util.tree_map(lambda x: np.array(x), theta)}
            log.write(json.dumps(m) + "\n")
            log.flush()
            if step % 10 == 0:
                print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}), flush=True)
        train_s = time.time() - t0
        final_theta = theta
        if best["theta"] is not None:
            theta = jax.tree_util.tree_map(jnp_asarray, best["theta"])
            print(json.dumps({"best_dev_answer": best["dev_answer"], "best_step": best["step"]}), flush=True)
        after = evaluate(theta)
        wdir = Path("/home/derp/cap/assets/runs/pc_cap/R1/pilot") / OUT.name  # weights live under assets/, not in the repo
        wdir.mkdir(parents=True, exist_ok=True)
        np.savez(wdir / "theta.npz", **{jax.tree_util.keystr(path): np.asarray(x) for path, x in jax.tree_util.tree_flatten_with_path(theta)[0]})
        # behavioural check: fresh learner per dev episode, adapt on supports (fast_steps = 0: initial codes), greedy answers
        cfg = RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=args.eval_fast_steps, lr=args.eval_fast_lr, delta_steps=args.eval_delta_steps, delta_lr=args.eval_delta_lr, tau=float(frozen["tau_edit"])), tau_edit=float(frozen["tau_edit"]))
        roles: dict[str, list[int]] = {}
        sel_hit: dict[str, list[int]] = {}
        preserved: dict[str, list[int]] = {}
        null_rates: dict[str, list[float]] = {}

        def greedy(predict, prompt_ids, n_tokens):
            cur = np.asarray(prompt_ids, np.int32)
            out = []
            for _ in range(n_tokens):
                nxt = int(np.argmax(predict(cur)))
                out.append(nxt)
                cur = np.concatenate([cur, np.int32([nxt])])
            return out

        for e in dev_eps:
            cap = RevisionCap(base, cfg, ledger, params=theta)
            for s in tuple(e.inputs.support_history) + tuple(e.inputs.new_support):
                adapt_record(cap, s, cfg.fast)
            cap.reset_queries()
            labels = {lab.query_id: lab for lab in e.query_labels}
            for q in e.inputs.queries:
                lab = labels[q.query_id]
                if lab.role == "composition":
                    continue
                n_t = len(lab.target_ids) or 3  # preserve roles without a teacher continuation: compare three greedy tokens
                ans = greedy(lambda ids, cap=cap: cap.predict(ids).logits, q.prompt_ids, n_t)
                roles.setdefault(lab.role, []).append(int(bool(lab.target_ids) and ans == [int(y) for y in lab.target_ids]))
                sel_q = cap.selection_for(np.asarray(q.prompt_ids, np.int32))
                top1 = sel_q.record_ids[int(np.argmax(sel_q.weights))] if len(sel_q.record_ids) else None
                sel_hit.setdefault(lab.role, []).append(int(bool(lab.supporting_record_ids) and top1 == lab.supporting_record_ids[0] and not sel_q.hard_null))
                if lab.role in ("near_miss", "unrelated"):
                    off = greedy(lambda ids: base.forward(ids, (), phase="query", last_only=True).logits, q.prompt_ids, n_t)
                    preserved.setdefault(lab.role, []).append(int(ans == off))
                null_rates.setdefault(lab.role, []).append(cap.selection_for(np.asarray(q.prompt_ids, np.int32)).null_mass)
        behav = {r: {"label_exact": float(np.mean(v)), "n": len(v), "null_mass_mean": float(np.mean(null_rates[r])),
                     "top1_is_supporting_record": float(np.mean(sel_hit[r])) if r in sel_hit else None,
                     "unchanged_from_capoff": (float(np.mean(preserved[r])) if r in preserved else None)} for r, v in roles.items()}
        summary = {"args": vars(args), "estimator": args.estimator, "domain": args.domain, "pool": args.pool, "dev_eval": "exact reference losses (train.episode_grads) for both estimators", "n_params": int(sum(int(np.prod(x.shape)) for x in jax.tree_util.tree_leaves(theta))), "theta_hash": params_hash(theta), "theta_path": str(wdir / "theta.npz"),
                   "featurize_wall_s": feat_s, "train_wall_s": train_s, "best_dev": {"answer": best["dev_answer"], "step": best["step"]}, "final_after": (evaluate(final_theta) if best["theta"] is not None else None), "dev_before": before, "dev_after": after, "behavioural_dev": behav,
                   "answer_roles": list(ANSWER_ROLES), "ledger": ledger.totals(), "total_wall_s": time.time() - t_start}
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
        print(json.dumps({"dev_before": before, "dev_after": after, "behavioural_dev": behav, "train_wall_s": round(train_s)}, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
