"""R1-40c P1-edit-memory profile on the real base: warm per-edit cost by occupancy bucket, query cost at declared occupancies,
persistent-state bytes (weights + keys/codes + every retained answer-position delta + support tokens), device/RSS peaks and
export/import restore equality. Memory content: the dev stream (300 real items, seed 21) followed by labelled fillers from the
training pool beyond the 1,000 items the reader was trained on (never fresh candidates). Profiling only: no scientific outcome
is claimed from the fillers.
    python scripts/r1_55_p1_profile.py --theta <npz|random> --dataset zsre --tag <tag> [--occupancies 100,300,1000] [--no-lease]
    → results/R1/p1_profile/<tag>_<dataset>/{summary,edits,queries}.json"""

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
DELTA_D = 768


def _pct(xs):
    if not xs:
        return None
    a = np.asarray(xs, np.float64)
    return {"n": int(a.size), "mean": float(a.mean()), "p50": float(np.percentile(a, 50)), "p95": float(np.percentile(a, 95)), "max": float(a.max())}


def _diff(before: dict, after: dict) -> dict:
    return {k: after[k] - before[k] for k in after if isinstance(after[k], (int, float)) and k in before and k != "peak_mem_mib"}


def _rss_mib() -> float:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return float("nan")


def _digest(it: dict) -> bytes:
    """Owner-edit digest as in the dev manifests (pccap.data.splits): sha256(item_id|prompt|answer)[:32 hex]."""
    return bytes.fromhex(it["digest"]) if it.get("digest") else hashlib.sha256(f"{it['item_id']}|{it['prompt']}|{it['answer']}".encode()).digest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True, help="reader weights .npz, or 'random' for the non-learned control (cosine gate 0.93)")
    ap.add_argument("--dataset", default="zsre", choices=("zsre", "counterfact"))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--occupancies", default="100,300,1000")
    ap.add_argument("--queries", type=int, default=100)
    ap.add_argument("--max-new", type=int, default=32)
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json")
    ap.add_argument("--rare-overlap", type=int, default=None, help="R1-56 gate: minimum memory-rare tokens shared with the selected record")
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.contracts import EditItem
    from pccap.data.decode import greedy_decode
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from r1_13_stream_eval import load_theta

    occupancies = [int(x) for x in args.occupancies.split(",")]
    out = ROOT / "results" / "R1" / "p1_profile" / f"{args.tag}_{args.dataset}"
    if out.exists():
        raise SystemExit(f"{out} exists; choose a new tag")
    out.mkdir(parents=True)
    frozen = json.loads((ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    stop = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
    rc, cc = ReaderConfig(lexical=True, stop_tokens=stop), ControllerConfig(A=float(frozen["A"]), bank_scales=b_m)
    nonlearned = args.theta == "random"
    pool_path = ROOT / "manifests" / "revision_v1" / f"train_pool_{args.dataset}_v1.json"
    pool_rows = json.loads(pool_path.read_text())["items"]
    t0 = time.time()
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1-55:" + args.tag, stage="R1", projected_seconds=1800.0)):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        k1, k2 = jax.random.split(jax.random.PRNGKey(0))
        init = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        theta = init if nonlearned else load_theta(Path(args.theta), init)
        cfg = RevisionConfig(reader=rc, controller=cc, fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=float(frozen["tau_edit"])),
                             null_threshold=0.5, tau_edit=float(frozen["tau_edit"]), min_score=0.93 if nonlearned else None, rare_overlap_min=args.rare_overlap)
        cap = RevisionCap(base, cfg, ledger, params=theta)
        dev_items, _ = load_dev_items(args.dataset, 300, seed=21)
        dev_ids = {it.item_id for it in dev_items}
        n_fill = max(0, max(occupancies) - len(dev_items))
        fillers = []
        for it in pool_rows[1000:]:  # beyond the 1,000 items the reader saw in training
            if len(fillers) >= n_fill:
                break
            if it["item_id"] in dev_ids:
                continue
            fillers.append(EditItem(item_id=it["item_id"], digest=_digest(it), prompt=it["prompt"], answer=it["answer"], aliases=it["aliases"],
                                    paraphrases=it["paraphrases"], locality_prompts=it["locality_prompts"], prompt_ids=np.asarray(it["prompt_ids"], np.int32),
                                    answer_ids=np.asarray(it["answer_ids"], np.int32), dataset=args.dataset, fact_id=it["fact_id"]))
        stream = list(dev_items) + fillers
        if len(stream) < max(occupancies):
            raise SystemExit(f"only {len(stream)} items available for occupancy {max(occupancies)}")
        rng = np.random.default_rng(55)
        edits, queries, checkpoints = [], [], []
        edges = [0] + occupancies
        bucket_of = {}

        def profile_queries(label: str):
            active = cap.store.active_records()
            by_id = {it.fact_id: it for it in stream}
            own_ids = [r.fact_id for r in active if r.fact_id in by_id]
            own_pick = rng.choice(own_ids, size=min(args.queries // 2, len(own_ids)), replace=False)
            prompts = [("own", by_id[i].prompt_ids) for i in own_pick]
            loc_pool = [lp for it in stream[: len(active)] for lp in it.locality_prompts[:1]]
            for i in rng.choice(len(loc_pool), size=min(args.queries - len(prompts), len(loc_pool)), replace=False):
                prompts.append(("locality", np.asarray(tok.encode(loc_pool[i]), np.int32)))
            rows = []
            for role, ids in prompts:
                cap.reset_queries()
                q0, w0 = ledger.query.as_dict(), time.perf_counter()
                dec = greedy_decode(lambda x: cap.predict(x).logits, ids, tok, max_new=args.max_new)
                wall = time.perf_counter() - w0
                sel = cap.selection_for(ids)
                rows.append({"checkpoint": label, "role": role, "prompt_tokens": int(ids.size), "decode_steps": dec.steps, "stopped_by": dec.stopped_by, "wall_s": wall,
                             "wall_per_step_s": wall / max(1, dec.steps), "fired": not sel.hard_null,  # the deployed decision (null threshold and, for the non-learned control, the cosine gate)
                             "ledger_delta": _diff(q0, ledger.query.as_dict())})
            queries.extend(rows)
            b = cap.store.bytes()
            st = cap.export_state()
            h1 = st.content_hash()
            w0 = time.perf_counter()
            cap.import_state(st)
            restore_s = time.perf_counter() - w0
            h2 = cap.export_state().content_hash()
            deltas = [r.delta for r in active if r.delta is not None]
            positions = [int(d.shape[0]) for d in deltas]
            return {"occupancy": len(active), "records_total": len(cap.store.records), "label": label,
                    "query_wall_s": _pct([r["wall_s"] for r in rows]), "query_wall_per_step_s": _pct([r["wall_per_step_s"] for r in rows]),
                    "query_full_forwards": _pct([r["ledger_delta"].get("full_forwards", 0) for r in rows]),
                    "query_partial_forwards": _pct([r["ledger_delta"].get("partial_forwards", 0) for r in rows]),
                    "fired_by_role": {role: sum(r["fired"] for r in rows if r["role"] == role) / max(1, sum(r["role"] == role for r in rows)) for role in ("own", "locality")},
                    "bytes": b, "ceiling_bytes": cfg.ceiling_bytes, "ceiling_fraction": b["total"] / cfg.ceiling_bytes,
                    "delta_positions": _pct(positions), "delta_bytes_total": int(sum(int(d.size) * 4 for d in deltas)),
                    "worst_case_32_position_delta_bytes": 32 * 3 * DELTA_D * 4,
                    "restore": {"hash_equal": h1 == h2, "bytes_equal": cap.store.bytes() == b, "seconds": restore_s, "state_hash": h2},
                    "rss_mib": _rss_mib(), "device_peak_mib": ledger.totals()["total"]["peak_mem_mib"]}

        cold = None
        next_ck = 0
        for i, it in enumerate(stream):
            if next_ck >= len(occupancies):
                break
            occ = len(cap.store.active_records())
            l0, w0 = ledger.learning.as_dict(), time.perf_counter()
            outcome = cap.update_item(it, None, None)
            wall = time.perf_counter() - w0
            row = {"i": i, "item_id": it.item_id, "source": "dev" if it.item_id in dev_ids else "training_pool_filler", "occupancy_before": occ,
                   "code": outcome.code, "codes": outcome.codes, "answer_positions": int(it.answer_ids.size), "wall_s": wall,
                   "ledger_delta": _diff(l0, ledger.learning.as_dict()), "bytes_total_after": cap.store.bytes()["total"]}
            if i == 0:
                cold = row
            edits.append(row)
            bucket_of[i] = next(j for j in range(len(edges) - 1) if edges[j] <= occ < edges[j + 1]) if occ < edges[-1] else len(edges) - 2
            if len(cap.store.active_records()) >= occupancies[next_ck]:
                checkpoints.append(profile_queries(f"occ{occupancies[next_ck]}"))
                print(json.dumps({"checkpoint": checkpoints[-1]["label"], "occupancy": checkpoints[-1]["occupancy"], "bytes_total": checkpoints[-1]["bytes"]["total"],
                                  "ceiling_fraction": round(checkpoints[-1]["ceiling_fraction"], 3), "q_p50": round(checkpoints[-1]["query_wall_s"]["p50"], 4),
                                  "restore_ok": checkpoints[-1]["restore"]["hash_equal"], "wall_s": round(time.time() - t0)}), flush=True)
                next_ck += 1
        warm = [r for r in edits[1:]]
        by_bucket = {}
        for j in range(len(edges) - 1):
            rows = [r for k, r in enumerate(edits) if k > 0 and bucket_of[k] == j]
            by_bucket[f"[{edges[j]},{edges[j + 1]})"] = {"edit_wall_s": _pct([r["wall_s"] for r in rows]), "full_forwards": _pct([r["ledger_delta"].get("full_forwards", 0) for r in rows]),
                                                        "reverses": _pct([r["ledger_delta"].get("reverses", 0) for r in rows]), "tokens": _pct([r["ledger_delta"].get("tokens", 0) for r in rows]),
                                                        "codes": {c: sum(r["code"] == c for r in rows) for c in sorted({r["code"] for r in rows})}, "n": len(rows)}
        by_len = {}
        for lo, hi in ((1, 2), (2, 4), (4, 8), (8, 33)):
            rows = [r for r in warm if lo <= r["answer_positions"] < hi]
            by_len[f"[{lo},{hi})"] = {"n": len(rows), "edit_wall_s": _pct([r["wall_s"] for r in rows]), "reverses": _pct([r["ledger_delta"].get("reverses", 0) for r in rows])}
        summary = {"tag": args.tag, "dataset": args.dataset, "condition": "R1_nonlearned (random tied reader, cosine gate 0.93)" if nonlearned else "R1_learned_ff (primary reader)",
                   "theta": None if nonlearned else {"path": args.theta, "sha256": hashlib.sha256(Path(args.theta).read_bytes()).hexdigest(), "params_hash": params_hash(theta)},
                   "base_checksum": cap.base_checksum(), "semantic_config": json.loads(cap.semantic_config()),
                   "memory_content": {"dev_items": len(dev_items), "dev_seed": 21, "training_pool_fillers": len(fillers), "filler_source": str(pool_path.relative_to(ROOT)),
                                      "filler_policy": "pool rows beyond index 1000 (unseen by reader training); profiling fillers only, no scientific outcome claimed"},
                   "weights_bytes": 4 * cap.n_params, "cold_first_edit": cold, "warm_edit_by_occupancy_bucket": by_bucket, "warm_edit_by_answer_positions": by_len,
                   "edit_codes": {c: sum(r["code"] == c for r in edits) for c in sorted({r["code"] for r in edits})}, "checkpoints": checkpoints,
                   "ledger": ledger.totals(), "wall_seconds": time.time() - t0}
        (out / "edits.json").write_text(json.dumps(edits, indent=1, default=str))
        (out / "queries.json").write_text(json.dumps(queries, indent=1, default=str))
        (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
        print(json.dumps({"dataset": args.dataset, "edit_codes": summary["edit_codes"], "warm": {k: round(v["edit_wall_s"]["p50"], 4) for k, v in by_bucket.items() if v["edit_wall_s"]},
                          "wall_s": round(summary["wall_seconds"])}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
