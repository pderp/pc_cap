"""Gate 7 on the real edit stream: RevisionCap with trained reader/controller weights on the Stage 0 zsRE development
stream (same 100 edits, order and evaluator as the diagnostics and the controls), reported next to v0 live and the
non-learned controls. Domain transfer from synthetic training is NOT expected to be complete; this is the first
end-to-end number and an exercise of the harness path with trained weights.
    python scripts/r1_13_stream_eval.py --theta /home/derp/cap/assets/runs/pc_cap/R1/pilot/<tag>/theta.npz [--tag <tag>]
        [--n 100] [--fast-steps 0] [--null-threshold 0.5] [--no-lease] → results/R1/stream_eval_<tag>.json, results/R1/stream_eval.md"""

from __future__ import annotations

import argparse
import contextlib
import json
import time
from pathlib import Path

import jax
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1"


def load_theta(path: Path, template: dict) -> dict:
    """Rebuild the params pytree from the keystr-named npz written by the pilot script."""
    z = np.load(path)
    leaves_with_path, treedef = jax.tree_util.tree_flatten_with_path(template)
    leaves = []
    for p, x in leaves_with_path:
        k = jax.tree_util.keystr(p)
        arr = np.asarray(z[k])
        assert arr.shape == tuple(x.shape), (k, arr.shape, x.shape)
        leaves.append(arr)
    return jax.tree_util.tree_unflatten(treedef, leaves)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--dataset", default="zsre", choices=("zsre", "counterfact"))
    ap.add_argument("--stream-seed", type=int, default=21, help="which 100 development items form the stream (21 = the Stage 0 stream)")
    ap.add_argument("--fast-steps", type=int, default=0)
    ap.add_argument("--fast-lr", type=float, default=1e-2)
    ap.add_argument("--delta-steps", type=int, default=0)
    ap.add_argument("--delta-lr", type=float, default=0.1)
    ap.add_argument("--null-threshold", type=float, default=0.5)
    ap.add_argument("--no-lease", action="store_true")
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json", help="lexical feature stop list (M4); 'none' disables the lexical feature")
    ap.add_argument("--no-query-null", action="store_true", help="null without the query-only linear term (pairwise + lexical only)")
    ap.add_argument("--min-score", type=float, default=None, help="cosine firing threshold (non-learned gate)")
    ap.add_argument("--no-pairwise-null", action="store_true", help="reader without the pairwise null head (weights trained before it existed)")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash

    tag = args.tag or Path(args.theta).parent.name
    tag = tag if args.dataset == "zsre" else f"{tag}@{args.dataset}"  # X25-06: the run identity (incl. dataset) is fixed before ANY path is chosen
    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))

    def _reader_config(**kw):
        if args.stop_tokens == "none":
            return ReaderConfig(lexical=False, query_null=not args.no_query_null, **kw)
        toks = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
        return ReaderConfig(lexical=True, stop_tokens=toks, query_null=not args.no_query_null, **kw)
    rc, cc = _reader_config(pairwise_null=not args.no_pairwise_null), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    rd = OUT / "streams_revision" / tag
    destinations = [OUT / f"stream_eval_{tag}.json", rd, Path("/home/derp/cap/assets/runs") / rd.relative_to(ROOT / "results")]  # X4-10: the harness's own checkpoint-root expression
    taken = [str(d) for d in destinations if d.exists()]
    if taken:
        raise SystemExit(f"run identity {tag!r} already has artifacts (never overwritten; choose a new tag): {taken}")  # X26-03: before any setup
    items, unrelated = load_dev_items(args.dataset, args.n, seed=args.stream_seed)
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:stream_eval", stage="R1", projected_seconds=3600.0)):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        template = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        theta = load_theta(Path(args.theta), template)
        cfg = RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=args.fast_steps, lr=args.fast_lr, delta_steps=args.delta_steps, delta_lr=args.delta_lr, tau=float(frozen["tau_edit"])), null_threshold=args.null_threshold, min_score=args.min_score, tau_edit=float(frozen["tau_edit"]))
        cap = RevisionCap(base, cfg, ledger, params=theta)
        ph = cap.params_hash
        ev = Evaluator(base, tok, unrelated[:50], None)
        t0 = time.time()
        m = run_stream(cap, items, None, Budget(A=float(frozen["A"]), R=max(1, args.fast_steps, args.delta_steps), tau_edit=float(frozen["tau_edit"])), ev, rd, ledger, checkpoints=(), seed=1, arm="R1")
        assert params_hash(cap.params) == ph, "reusable weights changed during the stream (gate 2)"
        sm = {k: v["value"] for k, v in m["metrics"].items() if k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")}
        # null-mass profile on the items' own prompts and paraphrases at the endpoint
        cap.reset_queries()
        nulls = {"prompt": [], "paraphrase": []}
        scores = {"prompt": [], "paraphrase": [], "unrelated": []}
        for it in items:
            sp = cap.selection_for(np.asarray(it.prompt_ids, np.int32))
            nulls["prompt"].append(sp.null_mass)
            scores["prompt"].append(sp.best_score)
            for p_ in it.paraphrases:
                sq = cap.selection_for(np.asarray(tok.encode(p_), np.int32))
                nulls["paraphrase"].append(sq.null_mass)
                scores["paraphrase"].append(sq.best_score)
        unrel_sel = [cap.selection_for(np.asarray(tok.encode(u), np.int32)) for u in unrelated[:200]]
        unrel = [x.null_mass for x in unrel_sel]
        scores["unrelated"] = [x.best_score for x in unrel_sel]
        sc = {k: [x for x in v if x is not None] for k, v in scores.items()}
        best_scores = {k: {"mean": float(np.mean(v)), "p10": float(np.percentile(v, 10)), "p90": float(np.percentile(v, 90))} for k, v in sc.items() if v}
        summary = {"tag": tag, "theta": args.theta, "theta_hash": ph, "args": vars(args), "stream_metrics": sm, "records": len(cap.store.records), "bytes": cap.store.bytes(),
                   "null_mass": {"prompt_mean": float(np.mean(nulls["prompt"])), "paraphrase_mean": float(np.mean(nulls["paraphrase"])), "unrelated_mean": float(np.mean(unrel)),
                                 "prompt_hard_null_rate": float(np.mean([x >= args.null_threshold for x in nulls["prompt"]])), "paraphrase_hard_null_rate": float(np.mean([x >= args.null_threshold for x in nulls["paraphrase"]])),
                                 "unrelated_hard_null_rate": float(np.mean([x >= args.null_threshold for x in unrel]))},
                   "best_scores": best_scores, "read_counters": cap.cost_counters, "wall_seconds": time.time() - t0, "ledger": ledger.totals()}
        summary["dataset"] = args.dataset
        summary["stream_seed"] = args.stream_seed
        (OUT / f"stream_eval_{tag}.json").write_text(json.dumps(summary, indent=1, default=float))
        md_path = OUT / "stream_eval.md"
        if not md_path.exists():
            md_path.write_text("# Revision v1 learner on the Stage 0 zsRE development stream (100 edits)\n\nReference rows: v0 live C1/C2 RET-GS 0.24/0.29; v0-stable and matched-update RET-GS 0.44, RET-ES 0.99, LS 1.00.\n\n| tag | fast steps | null thr | ES | RET-ES | RET-GS | LS | null mass prompt / paraphrase / unrelated | hard-null rate prompt / para / unrel | wall |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |\n")
        nm = summary["null_mass"]
        with md_path.open("a") as f:
            f.write(f"| {tag} | {args.fast_steps}c/{args.delta_steps}d | {args.null_threshold} | {sm['es_immediate']:.3f} | {sm['ret_es_end']:.3f} | {sm['ret_gs_end']:.3f} | {sm['ls_complete_answer_end']:.3f} | {nm['prompt_mean']:.2f} / {nm['paraphrase_mean']:.2f} / {nm['unrelated_mean']:.2f} | {nm['prompt_hard_null_rate']:.2f} / {nm['paraphrase_hard_null_rate']:.2f} / {nm['unrelated_hard_null_rate']:.2f} | {summary['wall_seconds']:.0f} s |\n")
        print(json.dumps({"tag": tag, "stream": sm, "best_scores": best_scores, "wall_s": round(summary["wall_seconds"])}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
