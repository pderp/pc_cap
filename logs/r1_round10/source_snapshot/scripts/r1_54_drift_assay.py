"""R1-54: ordinary-text drift of the learned cap after a 100-edit stream — firing rate on OpenWebText prefixes and the
drift NLL delta (fixed-prefix windows, cap-on vs cap-off), for a set of deployment rules (null threshold, cosine floor).
    python scripts/r1_54_drift_assay.py --theta <npz> [--dataset zsre] [--rules "0.5:none,0.5:0.3,0.5:0.5"] [--windows 64]
    → results/R1/drift_assay_<tag>.json"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jax
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--dataset", default="zsre")
    ap.add_argument("--rules", default="0.5:none,0.5:0.3,0.5:0.5")
    ap.add_argument("--windows", type=int, default=64)
    ap.add_argument("--window", type=int, default=128)
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json")
    ap.add_argument("--no-query-null", action="store_true")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader
    from r1_13_stream_eval import load_theta

    frozen = json.loads((ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    stop = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
    rc, cc = ReaderConfig(lexical=True, stop_tokens=stop, query_null=not args.no_query_null), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    base = BPBase(ledger=Ledger())
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = load_theta(Path(args.theta), {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)})
    items, unrelated = load_dev_items(args.dataset, 100, seed=21)
    drift = np.load("/home/derp/cap/assets/data/prepared/lm/drift_tokens.npy")
    windows = [np.asarray(drift[i * args.window : (i + 1) * args.window], np.int32) for i in range(args.windows)]
    from pccap.data.tokenize import GPT2Tokenizer
    tok = GPT2Tokenizer()
    out = {"theta": args.theta, "dataset": args.dataset, "windows": args.windows, "window": args.window, "rules": {}}
    for rule in args.rules.split(","):
        th, gate = rule.split(":")
        cfg = RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=float(frozen["tau_edit"])), null_threshold=float(th),
                             min_score=None if gate == "none" else float(gate), tau_edit=float(frozen["tau_edit"]))
        cap = RevisionCap(base, cfg, Ledger(), params=theta)
        for it in items:
            cap.update_item(it, None, None)
        fired = []
        for w in windows:
            for L in (16, 48, 96):
                cap.reset_queries()
                fired.append(int(not cap.selection_for(w[:L]).hard_null))
        ev = Evaluator(base, tok, unrelated[:50], drift, drift_positions=args.windows * args.window, drift_window=args.window)

        class PerPositionCap:
            """Ordinary text has no query boundary: every prefix is its own query (the R1-24 boundary evaluator's policy)."""

            def __init__(self, learner):
                self.learner = learner
                self.fired = self.n = 0

            def predict(self, ids):
                self.learner.reset_queries()
                self.fired += int(not self.learner.selection_for(np.asarray(ids, np.int32)).hard_null)  # every scored position counts
                self.n += 1
                return self.learner.predict(ids)

            def last_logits_batch(self, seqs, phase="query"):
                return np.stack([self.predict(s).logits for s in seqs])

        ppc = PerPositionCap(cap)
        nll_on = ev._drift_nll(ppc)
        nll_off = ev._drift_nll(base)
        out["rules"][rule] = {"fire_rate_on_ordinary_prefixes": float(np.mean(fired)), "fire_rate_all_scored_positions": ppc.fired / max(1, ppc.n), "scored_positions": ppc.n, "drift_nll_cap_on": nll_on, "drift_nll_cap_off": nll_off, "delta_nats": nll_on - nll_off, "ppl_ratio": float(np.exp(nll_on - nll_off))}
        print(json.dumps({rule: {k: round(v, 4) for k, v in out["rules"][rule].items()}}), flush=True)
    tag = args.tag or Path(args.theta).parent.name
    (ROOT / "results" / "R1" / f"drift_assay_{tag}_{args.dataset}.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
