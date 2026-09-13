"""X0-12 planted-fact mechanics check on the real base: can the reference trainer drive ONE synthetic episode's answer
loss to near zero and make the learner answer that episode's paraphrase queries exactly? A capacity/plumbing check, not a
generalization result. Runs without the GPU lease when --no-lease (small memory footprint).
    python scripts/r1_21_overfit_check.py [--steps 60] [--lr 1e-3] [--seed 11] [--no-lease] → results/R1/pilot/overfit_check.json"""

from __future__ import annotations

import argparse
import contextlib
import json
import time
from pathlib import Path

import jax
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1" / "pilot"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--no-lease", action="store_true")
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
    from pccap.revision_v1.reader import ReaderConfig, init_reader
    from pccap.revision_v1.train import LossConfig, Trainer, featurize

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    rc, cc = ReaderConfig(), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    OUT.mkdir(parents=True, exist_ok=True)
    lease = contextlib.nullcontext() if args.no_lease else gpu_lease("R1:overfit_check", stage="R1", projected_seconds=1800.0)
    with lease:
        ledger = Ledger()
        base = BPBase(ledger=ledger)
        enc = ObservationEncoder(base, taps=rc.taps)
        ep = synthetic_episode(args.seed, "train")
        feats = featurize(base, enc, ep, rc)
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        tr = Trainer(rc, cc, base.params, base.cfg, LossConfig(), lr=args.lr)
        st = tr.init(theta)
        traj = []
        t0 = time.time()
        for step in range(args.steps):
            theta, st, m = tr.outer_step(theta, st, [feats])
            traj.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()})
            if step % 10 == 0 or step == args.steps - 1:
                print(json.dumps({"step": step, **traj[-1]}), flush=True)
        cfg = RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0), tau_edit=float(frozen["tau_edit"]))
        cap = RevisionCap(base, cfg, ledger, params=theta)
        for s in tuple(ep.inputs.support_history) + tuple(ep.inputs.new_support):
            adapt_record(cap, s, cfg.fast)
        cap.reset_queries()
        labels = {lab.query_id: lab for lab in ep.query_labels}
        res = {}
        for q in ep.inputs.queries:
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
            sel = cap.selection_for(np.asarray(q.prompt_ids, np.int32))
            res[q.query_id] = {"role": lab.role, "exact": ok, "null_mass": sel.null_mass, "hard_null": sel.hard_null, "top": sel.record_ids[:2], "expected": list(lab.supporting_record_ids)}
        out = {"args": vars(args), "episode": ep.episode_id, "trajectory": traj, "final": traj[-1], "queries": res, "wall_s": time.time() - t0}
        (OUT / "overfit_check.json").write_text(json.dumps(out, indent=1, default=float))
        print(json.dumps({"final": traj[-1], "queries": {k: (v["role"], v["exact"], round(v["null_mass"], 3)) for k, v in res.items()}}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
