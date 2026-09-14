"""R1-44 unseen-edit-prompt endpoint on the real base: after the 100-edit development stream, query the original prompts
of 100 OTHER items of the same development pool (never edited) and measure firing and cap-off answer change.
    python scripts/r1_44_unseen_run.py --theta <npz> --dataset zsre|counterfact --tag <tag> [--no-lease]"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import sys
import time
from pathlib import Path

import jax

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--dataset", default="zsre", choices=("zsre", "counterfact"))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n-unseen", type=int, default=100)
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json")
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.endpoints_unseen import UnseenPromptEvaluator, summarize_unseen
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from r1_13_stream_eval import load_theta

    out = ROOT / "results" / "R1" / "endpoints" / f"{args.tag}_unseen_{args.dataset}"
    if out.exists():
        raise SystemExit(f"{out} exists; choose a new tag")
    out.mkdir(parents=True)
    frozen = json.loads((ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    stop = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
    rc, cc = ReaderConfig(lexical=True, stop_tokens=stop), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    dev_path = ROOT / "manifests" / "dev" / f"{args.dataset}_dev.json"
    dev = json.loads(dev_path.read_text())
    pool_rows = [{"item_id": it["item_id"], "fact_id": it.get("fact_id", it["item_id"]), "subject": it.get("subject", ""), "prompt": it["prompt"], "dataset": args.dataset} for it in dev["items"]]
    t0 = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1-44:" + args.tag, stage="R1", projected_seconds=3600.0)):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        theta = load_theta(Path(args.theta), {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)})
        cap = RevisionCap(base, RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=float(frozen["tau_edit"])), null_threshold=0.5, tau_edit=float(frozen["tau_edit"])), ledger, params=theta)
        items, _ = load_dev_items(args.dataset, 100, seed=21)
        edited = []
        for it in items:
            cap.update_item(it, None, None)
            edited.append(it.item_id)
        edited_set = set(edited)
        outside = [r["item_id"] for r in pool_rows if r["item_id"] not in edited_set][: args.n_unseen]
        ev = UnseenPromptEvaluator(cap, tok, pool_rows, pool_id=f"{args.dataset}_dev", source_sha256=hashlib.sha256(dev_path.read_bytes()).hexdigest(), base=base, max_new=32, ledger=ledger)
        rows = ev.evaluate(outside, edited_item_ids=edited, expected_n=args.n_unseen, checkpoint_id=f"{args.tag}:{args.dataset}:after100")
        summary = summarize_unseen(rows, expected_n=args.n_unseen)
        record = {"tag": args.tag, "dataset": args.dataset, "theta": {"path": args.theta, "sha256": hashlib.sha256(Path(args.theta).read_bytes()).hexdigest(), "params_hash": params_hash(theta)},
                  "pool": {"path": str(dev_path), "sha256": hashlib.sha256(dev_path.read_bytes()).hexdigest(), "rows": len(pool_rows)}, "edited_item_ids": edited, "outside_item_ids": outside,
                  "summary": summary, "ledger": ledger.totals(), "wall_seconds": time.time() - t0}
        (out / "rows.json").write_text(json.dumps(rows, indent=1, default=str))
        (out / "summary.json").write_text(json.dumps(record, indent=1, default=str))
        print(json.dumps({"dataset": args.dataset, "summary": summary, "wall_s": round(record["wall_seconds"])}, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
