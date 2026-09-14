"""R1-43 endpoints on the real base with a trained reader: near-miss preservation (100 challenge rows), revision (100
temporal corrections), composition reported unreachable (no verified direct questions). Starting memory state: empty
(each case restores a clone). Persists the manifest binding, identities, rows and summaries.
    python scripts/r1_43_endpoints_run.py --theta <npz> --tag <tag> [--near 100] [--revision 100] [--no-lease]"""

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
    ap.add_argument("--tag", required=True)
    ap.add_argument("--near", type=int, default=100)
    ap.add_argument("--revision", type=int, default=100)
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json")
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.endpoints import EndpointEvaluator, load_dev_challenges, summarize
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from r1_13_stream_eval import load_theta

    out = ROOT / "results" / "R1" / "endpoints" / args.tag
    if out.exists():
        raise SystemExit(f"{out} exists; choose a new tag")
    out.mkdir(parents=True)
    frozen = json.loads((ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    stop = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
    rc, cc = ReaderConfig(lexical=True, stop_tokens=stop), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    t0 = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1-43:" + args.tag, stage="R1", projected_seconds=3600.0)):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        theta = load_theta(Path(args.theta), {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)})
        cap = RevisionCap(base, RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=float(frozen["tau_edit"])), null_threshold=0.5, tau_edit=float(frozen["tau_edit"])), ledger, params=theta)
        doc, binding = load_dev_challenges()
        ev = EndpointEvaluator(cap, tok, base=base, max_new=32, ledger=ledger)
        near_rows = [ev.near_miss(row) for row in doc["near_neighbour"]["items"][: args.near]]
        near_summary = summarize(near_rows, "preserved")
        rev_rows = [ev.revision(row) for row in doc["temporal_correction"]["items"][: args.revision]]
        rev_summary = summarize(rev_rows, "revision_success")
        comp = {"status": "unreachable", "reason": "no verified direct composition questions supplied (R1-43 §composition); two-hop chains are diagnostic only", "rows_available": len(doc["composition"]["items"])}
        record = {"tag": args.tag, "theta": {"path": args.theta, "sha256": hashlib.sha256(Path(args.theta).read_bytes()).hexdigest(), "params_hash": params_hash(theta)},
                  "reader": {"lexical": True, "stop_tokens": args.stop_tokens, "null_threshold": 0.5, "delta_steps": 5, "delta_lr": 0.1}, "base_checksum": base.checksum(recompute=False),
                  "challenge_binding": binding, "starting_state": "empty memory; each case restores a clone",
                  "near_miss": {"n": len(near_rows), "summary": near_summary}, "revision": {"n": len(rev_rows), "summary": rev_summary}, "composition": comp,
                  "ledger": ledger.totals(), "wall_seconds": time.time() - t0}
        (out / "near_miss_rows.json").write_text(json.dumps(near_rows, indent=1, default=str))
        (out / "revision_rows.json").write_text(json.dumps(rev_rows, indent=1, default=str))
        (out / "summary.json").write_text(json.dumps(record, indent=1, default=str))
        print(json.dumps({"near_miss": near_summary, "revision": rev_summary, "wall_s": round(record["wall_seconds"])}, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
