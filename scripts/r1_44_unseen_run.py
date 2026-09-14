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
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _digest(it: dict) -> bytes:
    """Owner-edit digest as in the dev manifests (pccap.data.splits): sha256(item_id|prompt|answer)[:32 hex]."""
    return bytes.fromhex(it["digest"]) if it.get("digest") else hashlib.sha256(f"{it['item_id']}|{it['prompt']}|{it['answer']}".encode()).digest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--dataset", default="zsre", choices=("zsre", "counterfact", "mquake"))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n-unseen", type=int, default=100)
    ap.add_argument("--n-edits", type=int, default=100, help="edits before the checkpoint; above 300 the dev stream is extended with labelled training-pool rows beyond index 1000")
    ap.add_argument("--outside-from-pool", action="store_true", help="draw the outside (un-edited) prompts from training-pool rows beyond index 1000 instead of the dev remainder")
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json")
    ap.add_argument("--rare-overlap", type=int, default=None, help="R1-56 gate: minimum memory-rare tokens shared with the selected record")
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.contracts import EditItem
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
    train_pool_path = ROOT / "manifests" / "revision_v1" / f"train_pool_{args.dataset}_v1.json"
    extra_rows = json.loads(train_pool_path.read_text())["items"][1000:] if (args.n_edits > 300 or args.outside_from_pool) else []
    dev_ids = {it["item_id"] for it in dev["items"]}
    extra_rows = [it for it in extra_rows if it["item_id"] not in dev_ids]
    source_rows = dev["items"] + extra_rows
    pool_rows = [{"item_id": it["item_id"], "fact_id": it.get("fact_id", it["item_id"]), "subject": it.get("subject", ""), "prompt": it["prompt"], "dataset": args.dataset} for it in source_rows]
    t0 = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1-44:" + args.tag, stage="R1", projected_seconds=3600.0)):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        theta = load_theta(Path(args.theta), {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)})
        cap = RevisionCap(base, RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=float(frozen["tau_edit"])), null_threshold=0.5, rare_overlap_min=args.rare_overlap, tau_edit=float(frozen["tau_edit"])), ledger, params=theta)
        items, _ = load_dev_items(args.dataset, min(args.n_edits, 300), seed=21)
        n_fill = args.n_edits - len(items)
        filler_rows, extra_iter = [], iter(extra_rows)
        while len(filler_rows) < n_fill:
            filler_rows.append(next(extra_iter))
        items = list(items) + [EditItem(item_id=it["item_id"], digest=_digest(it), prompt=it["prompt"], answer=it["answer"], aliases=it["aliases"],
                                        paraphrases=it["paraphrases"], locality_prompts=it["locality_prompts"], prompt_ids=np.asarray(it["prompt_ids"], np.int32),
                                        answer_ids=np.asarray(it["answer_ids"], np.int32), dataset=args.dataset, fact_id=it["fact_id"]) for it in filler_rows]
        outside_source = [it["item_id"] for it in (extra_rows if args.outside_from_pool else dev["items"])]
        edited = []
        for it in items:
            cap.update_item(it, None, None)
            edited.append(it.item_id)
        edited_set = set(edited)
        outside = [i for i in outside_source if i not in edited_set][: args.n_unseen]
        if len(outside) < args.n_unseen:
            raise SystemExit(f"only {len(outside)} outside items available")
        ev = UnseenPromptEvaluator(cap, tok, pool_rows, pool_id=f"{args.dataset}_dev" + ("+train_pool_v1[1000:]" if extra_rows else ""), source_sha256=hashlib.sha256(dev_path.read_bytes() + (train_pool_path.read_bytes() if extra_rows else b"")).hexdigest(), base=base, max_new=32, ledger=ledger)
        report = ev.evaluate(outside, edited_item_ids=edited, expected_n=args.n_unseen, checkpoint_id=f"{args.tag}:{args.dataset}:after{args.n_edits}")
        rows = report["rows"]
        summary = summarize_unseen(rows, expected_n=args.n_unseen)
        assert summary == report["summary"]
        record = {"tag": args.tag, "dataset": args.dataset, "n_edits": args.n_edits, "memory_content": {"dev_items": min(args.n_edits, 300), "training_pool_fillers": len(filler_rows), "filler_policy": "pool rows beyond index 1000 (unseen by reader training); profiling only"},
                  "outside_source": "training_pool_remainder" if args.outside_from_pool else "dev_remainder", "theta": {"path": args.theta, "sha256": hashlib.sha256(Path(args.theta).read_bytes()).hexdigest(), "params_hash": params_hash(theta)},
                  "pool": {"path": str(dev_path), "sha256": hashlib.sha256(dev_path.read_bytes()).hexdigest(), "rows": len(pool_rows)}, "edited_item_ids": edited, "outside_item_ids": outside,
                  "summary": summary, "ledger": ledger.totals(), "wall_seconds": time.time() - t0}
        (out / "report.json").write_text(json.dumps(report, indent=1, default=str))
        (out / "summary.json").write_text(json.dumps(record, indent=1, default=str))
        print(json.dumps({"dataset": args.dataset, "summary": summary, "wall_s": round(record["wall_seconds"])}, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
