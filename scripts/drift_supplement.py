"""Full-validation LM drift supplement (X2-05 / SD-3): the endpoint learner states of the S4 editing runs scored on the
WHOLE validation split (247,289 tokens, 128-token windows, cap-on full recompute per position — the same assay as the runs'
4,064-position drift sample, extended to every window), against the cap-off base. Labelled supplementary: the frozen runs
recorded the 4,064-position assay; this does not change any classification.
    python scripts/drift_supplement.py [--dataset zsre] [--arms C0,C1,C2,CR,B3] [--realizations 0] [--max-tokens N]
    → results/S4/drift_supplement.json"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="zsre")
    ap.add_argument("--arms", default="C0,C1,C2,CR,B3")
    ap.add_argument("--realizations", default="0")
    ap.add_argument("--perms", default="0,1,2,3,4")
    ap.add_argument("--experiment-id", default="frozen-confirmatory-v2-84126123")
    ap.add_argument("--max-tokens", type=int, default=None, help="truncate the split (smoke only)")
    ap.add_argument("--out", default=str(ROOT / "results" / "S4" / "drift_supplement.json"))
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.arms import make_learner
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator
    from pccap.harness.snapshot import load as load_state

    frozen_path = ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json"
    frozen = json.loads(frozen_path.read_text())
    inv = json.loads((ROOT / "manifests" / "dev" / "lm_sets.json").read_text())
    tokens = np.load(inv["files"]["drift_tokens"]["path"])
    if args.max_tokens:
        tokens = tokens[: args.max_tokens + 128]
    n_pos = len(tokens) - 128
    exp = args.experiment_id
    out = {"label": "SUPPLEMENTARY: full-validation drift (SD-3) on endpoint learner states; the frozen runs used a 4,064-position sample", "experiment_id": exp,
           "dataset": args.dataset, "tokens_scored": None, "windows": n_pos // 128, "written": None, "runs": []}
    t0 = time.time()
    with gpu_lease("S4:drift_supplement", stage="S4", projected_seconds=3 * 3600.0):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        ev = Evaluator(base, tok, [], tokens, drift_positions=n_pos, drift_window=128)  # base NLL over the full split, once
        out["tokens_scored"] = sum(len(w) - 1 for w in ev.drift_windows)
        out["base_nll"] = ev.drift_base_nll
        radii = {int(k): float(v) for k, v in frozen["radii"]["bank"][args.dataset].items()}
        b_m = {int(k): float(v) for k, v in frozen["b_m"].items()}
        from pccap.data.confirm import load as load_confirm

        for r in [int(x) for x in args.realizations.split(",")]:
            man_r = load_confirm(Path(frozen["confirm_dir"]) / f"{args.dataset}_r{r}.json", frozen=frozen_path)
            for arm in args.arms.split(","):
                for perm in [int(x) for x in args.perms.split(",")]:
                    seeds = man_r["named_seeds"][str(frozen["order_seeds"][perm])]
                    rd = ROOT / "results" / "S4" / exp / args.dataset / arm / "BP" / "h" / str(r) / str(perm)
                    ck_dir = ROOT.parent / "assets" / "runs" / "S4" / exp / args.dataset / arm / "BP" / "h" / str(r) / str(perm)
                    ck_meta = next(c for c in json.loads((rd / "checkpoints.json").read_text()) if c["tag"] == "end")
                    ck_path = ck_dir / "learner_end.ckpt"
                    assert hashlib.sha256(ck_path.read_bytes()).hexdigest() == ck_meta["checkpoint_sha256"]
                    learner_seed = int(seeds["seed_replay"] if arm == "B3" else seeds["seed_cap_init"])
                    learner = make_learner(arm, base, ledger, radii=radii, bank_scales=b_m, read=frozen["radii"]["read"], seed=learner_seed,
                                           lora_lr=float(frozen["lora"]["lr"]), lora_rank=int(frozen["lora"]["rank"]), lora_steps=int(frozen["lora"]["steps"]))
                    learner.import_state(load_state(ck_path, expected_hash=ck_meta["state_hash"]))
                    assert learner.state_hash() == ck_meta["state_hash"]
                    h0 = base.checksum()
                    t1 = time.time()
                    d = ev.drift(learner)
                    assert base.checksum() == h0
                    rec = json.loads((rd / "metrics.json").read_text())["metrics"]
                    row = {"arm": arm, "realization": r, "perm": perm, "full": {k: d[k] for k in ("nll", "base_nll", "loss_difference", "perplexity_ratio", "positions")},
                           "restricted_4064": {"loss_difference": rec["lm_drift_loss_difference"]["value"], "perplexity_ratio": rec["lm_drift_perplexity_ratio"]["value"], "positions": rec["lm_drift_perplexity_ratio"]["n"]},
                           "seconds": time.time() - t1}
                    out["runs"].append(row)
                    print(json.dumps(row), flush=True)
    per_arm = {}
    for row in out["runs"]:
        per_arm.setdefault(row["arm"], []).append(row)
    out["per_arm"] = {a: {"n": len(v), "full_ratio_mean": float(np.mean([x["full"]["perplexity_ratio"] for x in v])), "full_ratio_max": float(np.max([x["full"]["perplexity_ratio"] for x in v])),
                          "restricted_ratio_mean": float(np.mean([x["restricted_4064"]["perplexity_ratio"] for x in v])), "full_loss_difference_mean": float(np.mean([x["full"]["loss_difference"] for x in v]))} for a, v in per_arm.items()}
    out["written"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["wall_seconds"] = time.time() - t0
    Path(args.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["per_arm"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
