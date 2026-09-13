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
import numpy as np

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
    args = ap.parse_args()
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
    rc, cc = ReaderConfig(), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    OUT = OUT_ROOT / (args.tag or args.estimator)
    OUT.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    with gpu_lease("R1:pilot", stage="R1", projected_seconds=3 * 3600.0):
        ledger = Ledger()
        if args.estimator == "epc":
            from pccap.bases.epc import EPCBase
            base = EPCBase(ledger=ledger)
        else:
            base = BPBase(ledger=ledger)
        enc = ObservationEncoder(base, taps=rc.taps)
        t0 = time.time()
        train_eps = [synthetic_episode(1000 + i, "train") for i in range(args.train)]
        dev_eps = [synthetic_episode(5000 + i, "dev") for i in range(args.dev)]
        train_f = [featurize(base, enc, e, rc) for e in train_eps]
        dev_f = [featurize(base, enc, e, rc) for e in dev_eps]
        feat_s = time.time() - t0
        k1, k2 = jax.random.split(jax.random.PRNGKey(args.seed))
        theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        if args.estimator == "epc":
            from pccap.revision_v1.epc_train import EPCTrainer, EPCWriteGradients
            tr = EPCTrainer(rc, cc, EPCWriteGradients(base, iters=args.iters), LossConfig(), lr=args.lr)
        else:
            tr = Trainer(rc, cc, base.params, base.cfg, LossConfig(), lr=args.lr)
        st = tr.init(theta)

        def evaluate(th):
            agg = {}
            for f in dev_f:
                _, m = episode_grads(th, rc, cc, base.params, base.cfg, f, tr.lc)
                for k, v in m.items():
                    agg[k] = agg.get(k, 0.0) + v / len(dev_f)
            return agg

        before = evaluate(theta)
        rng = np.random.default_rng(args.seed)
        log = (OUT / "metrics.jsonl").open("w")
        t0 = time.time()
        for step in range(args.steps):
            idx = rng.choice(len(train_f), size=args.batch, replace=False)
            theta, st, m = tr.outer_step(theta, st, [train_f[i] for i in idx])
            m.update(step=step, wall_s=time.time() - t0)
            log.write(json.dumps(m) + "\n")
            log.flush()
            if step % 10 == 0:
                print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}), flush=True)
        train_s = time.time() - t0
        after = evaluate(theta)
        np.savez(OUT / "theta.npz", **{jax.tree_util.keystr(path): np.asarray(x) for path, x in jax.tree_util.tree_flatten_with_path(theta)[0]})
        # behavioural check: fresh learner per dev episode, adapt on supports (fast_steps = 0: initial codes), greedy answers
        cfg = RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0), tau_edit=float(frozen["tau_edit"]))
        roles: dict[str, list[int]] = {}
        null_rates: dict[str, list[float]] = {}
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
                cur = np.asarray(q.prompt_ids, np.int32)
                ok = True
                for y in lab.target_ids:
                    nxt = int(np.argmax(cap.predict(cur).logits))
                    if nxt != int(y):
                        ok = False
                        break
                    cur = np.concatenate([cur, np.int32([int(y)])])
                roles.setdefault(lab.role, []).append(int(ok))
                null_rates.setdefault(lab.role, []).append(cap.selection_for(np.asarray(q.prompt_ids, np.int32)).null_mass)
        behav = {r: {"exact_or_preserved": float(np.mean(v)), "n": len(v), "null_mass_mean": float(np.mean(null_rates[r]))} for r, v in roles.items()}
        summary = {"args": vars(args), "estimator": args.estimator, "dev_eval": "exact reference losses (train.episode_grads) for both estimators", "n_params": int(sum(int(np.prod(x.shape)) for x in jax.tree_util.tree_leaves(theta))), "theta_hash": params_hash(theta),
                   "featurize_wall_s": feat_s, "train_wall_s": train_s, "dev_before": before, "dev_after": after, "behavioural_dev": behav,
                   "answer_roles": list(ANSWER_ROLES), "ledger": ledger.totals(), "total_wall_s": time.time() - t_start}
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
        print(json.dumps({"dev_before": before, "dev_after": after, "behavioural_dev": behav, "train_wall_s": round(train_s)}, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
