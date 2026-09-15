"""R1-60 on the real base (development): direct MQuAKE composition questions on isolated dependency-edit clones, for the
cases whose dependency edits all lie in a named MQuAKE pool (development or training items; never confirmatory).
    python scripts/r1_60_composition_run.py --theta <npz> --pool manifests/revision_v1/train_pool_mquake_v2.json --tag <tag> [--max-cases 300] [--rare-overlap 1] [--no-lease]
    → results/R1/endpoints/<tag>_composition/{report,summary}.json"""

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
COMPOSITION = Path("/home/derp/cap/assets/data/prepared/revision_v1/r1_d4_v1/composition.jsonl")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--pool", default="manifests/revision_v1/train_pool_mquake_v2.json")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--max-cases", type=int, default=300)
    ap.add_argument("--rare-overlap", type=int, default=None)
    ap.add_argument("--lex-idf", action="store_true")
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
    from pccap.revision_v1.endpoints_composition import (
        CompositionEvaluator,
        select_for_realizations,
    )
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from r1_13_stream_eval import load_theta

    out = ROOT / "results" / "R1" / "endpoints" / f"{args.tag}_composition"
    if out.exists():
        raise SystemExit(f"{out} exists; choose a new tag")
    out.mkdir(parents=True)
    frozen = json.loads((ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    stop = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
    rc, cc = ReaderConfig(lexical=True, stop_tokens=stop, lex_idf=args.lex_idf), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    pool_path = ROOT / args.pool
    pool = json.loads(pool_path.read_text())["items"]
    edit_items = {it["item_id"]: it for it in pool}
    cases = [json.loads(line) for line in COMPOSITION.read_text().splitlines() if line.strip()]
    sel = select_for_realizations(cases, {0: list(edit_items)})
    attached = sel["cases_by_realization"]["0"]
    unavailable_ids = {u["composition_id"] for u in sel["unavailable_source_cases"]}
    chosen = [c for c in attached if c["composition_id"] not in unavailable_ids][: args.max_cases]
    t0 = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1-60:" + args.tag, stage="R1", projected_seconds=3600.0)):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        theta = load_theta(Path(args.theta), {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)})
        cap = RevisionCap(base, RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=float(frozen["tau_edit"])), null_threshold=0.5,
                                                rare_overlap_min=args.rare_overlap, tau_edit=float(frozen["tau_edit"])), ledger, params=theta)
        ev = CompositionEvaluator(cap, tok, teaching_state=cap.export_state(), base=base, max_new=32, ledger=ledger)
        report = ev.evaluate(chosen, edit_items, expected_n=len(chosen))
    summary = {"tag": args.tag, "theta": {"path": args.theta, "sha256": hashlib.sha256(Path(args.theta).read_bytes()).hexdigest(), "params_hash": params_hash(theta)},
               "pool": {"path": str(pool_path), "sha256": hashlib.sha256(pool_path.read_bytes()).hexdigest(), "items": len(pool)},
               "composition_source": {"path": str(COMPOSITION), "sha256": hashlib.sha256(COMPOSITION.read_bytes()).hexdigest(), "cases": len(cases)},
               "selection": {"attached_to_pool": len(attached), "unavailable_attached": sum(1 for c in attached if c["composition_id"] in unavailable_ids), "unattached": len(sel["unattached_case_ids"]), "evaluated": len(chosen), "rule": sel["rule"]},
               "semantic_config": json.loads(cap.semantic_config()), "summary": report["summary"],
               "dependency_count_hist": {str(k): sum(1 for c in chosen if len(c["dependencies"]) == k) for k in (1, 2, 3)},
               "ledger": ledger.totals(), "wall_seconds": time.time() - t0, "scope": "development (pool items are exposed); not confirmatory"}
    (out / "report.json").write_text(json.dumps(report, indent=1, default=str))
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({"tag": args.tag, "summary": report["summary"], "selection": summary["selection"], "wall_s": round(summary["wall_seconds"])}, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
