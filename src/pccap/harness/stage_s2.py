"""S2-02: aggregate step screening (PDF S2 "Update numerics"; plan §6.8).

A ∈ {0.03, 0.1, 0.3} only; arm C1; calibrated radii and ``b_m`` from S2-01; ε = 0.01, R = 5,
stop 0.1. On ``n`` development edits per dataset (default 100, disjoint from the S0 sample where
possible) score, per candidate A: immediate free-generation ES (common decoder) and the locality
criterion — the false-fire rate of the learned cap on the development unrelated prompts (fraction
of unrelated prompts on which any bank fires) must be ≤ 1%. Choose one shared A: highest ES
among candidates meeting locality; tie → 0.1. Every configuration is logged. If none functions:
≤ 3 diagnoses with the cheapest discriminating test, no new sweep (Op. rule 5).

    python -m pccap.harness.stage_s2 --n 100           # runs under the GPU lease
Outputs ``results/S2/A_screening.json`` (+ per-A run directories under results/S2/screen/).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from pccap.bases.bp import BPBase
from pccap.cap.cap import Cap, CapConfig
from pccap.cap.learn import update_item
from pccap.contracts import Budget, EditItem
from pccap.data.decode import greedy_decode, score_generation
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.ledger import Ledger
from pccap.harness.records import append_jsonl
from pccap.routers import make_router
from pccap.transport.transport import Transport

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "manifests" / "dev"
S2 = ROOT / "results" / "S2"
A_CANDIDATES = (0.03, 0.1, 0.3)


def load_dev_items(ds: str, n: int, seed: int = 21, exclude_s0: bool = True) -> tuple[list[EditItem], list[str]]:
    man = json.loads((DEV / f"{ds}_dev.json").read_text())
    s0 = {it["item_id"] for it in json.loads((DEV / "s0_sample.json").read_text())["items"]}
    pool = [it for it in man["items"] if not (exclude_s0 and it["item_id"] in s0)] or man["items"]
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(pool))[:n]
    items = []
    for i in sorted(idx):
        it = pool[i]
        items.append(EditItem(item_id=it["item_id"], digest=bytes.fromhex(it["digest"]), prompt=it["prompt"], answer=it["answer"],
                              aliases=it["aliases"], paraphrases=it["paraphrases"], locality_prompts=it["locality_prompts"],
                              prompt_ids=np.asarray(it["prompt_ids"], np.int32), answer_ids=np.asarray(it["answer_ids"], np.int32),
                              dataset=ds, fact_id=it["fact_id"]))
    return items, man["unrelated_prompts"]


def calibration() -> tuple[dict[int, float], dict[int, float]]:
    rs = json.loads((S2 / "residual_scales.json").read_text())
    rc = json.loads((S2 / "radius_calibration.json").read_text())
    b_m = {int(k): float(v) for k, v in rs["pooled_b_m"].items()}
    radii = {int(k): float(v) for k, v in rc["pooled_radii_min_over_datasets"].items()}
    return b_m, radii


def false_fire_rate(cap: Cap, tok: GPT2Tokenizer, unrelated: list[str], n: int = 1000) -> dict:
    fired = 0
    total = 0
    for s in unrelated[:n]:
        ep = cap.edited_forward(tok.encode(s), phase="query")
        fired += any(v >= 0 for v in ep.fired.values())
        total += 1
    return {"fired": fired, "n": total, "rate": fired / total if total else None}


def screen_one(A: float, items: list[EditItem], unrelated: list[str], b_m, radii, tok, out_dir: Path, arm: str = "C1",
               seed: int = 0) -> dict:
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    cap = Cap(base, CapConfig(arm=arm, radii=radii, bank_scales=b_m, seed=seed), ledger)
    router = make_router(arm)
    budget = Budget(A=A, epsilon=0.01, R=5, tau_edit=0.1)
    out_dir.mkdir(parents=True, exist_ok=True)
    dec_path = out_dir / "decisions.jsonl"
    dec_path.unlink(missing_ok=True)
    es_hits = 0
    acquired = 0
    rows = []
    t0 = time.time()
    for it in items:
        out = update_item(cap, it, router, budget, Transport(), on_decision=lambda r: append_jsonl(dec_path, r), seed=seed)
        dec = greedy_decode(lambda ids: cap.edited_forward(ids, phase="query").logits, it.prompt_ids, tok)
        es = score_generation(dec, it.aliases)["value"]
        es_hits += int(es == 1.0)
        acquired += int(out.acquired_threshold_all_prefixes)
        rows.append({"item_id": it.item_id, "threshold": out.acquired_threshold_all_prefixes, "es": es, "rounds": out.rounds_used,
                     "generated": dec.text})
    ff = false_fire_rate(cap, tok, unrelated)
    mem = cap.memory_bytes()
    res = {"A": A, "arm": arm, "n_items": len(items), "es_immediate": es_hits / len(items), "threshold_acquisition": acquired / len(items),
           "false_fire": ff, "locality_ok": ff["rate"] is not None and ff["rate"] <= 0.01, "seconds": time.time() - t0,
           "memory_occupied_bytes": mem.occupied_bytes, "slots_active": {str(m): v["active"] for m, v in mem.per_bank.items()},
           "ledger": ledger.totals(), "rows": rows}
    (out_dir / "metrics.json").write_text(json.dumps(res, indent=1, default=float))
    ledger.write(out_dir)
    return res


def main(argv=None) -> int:
    from pccap.harness.lease import gpu_lease

    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--datasets", nargs="*", default=["zsre", "counterfact"])
    ap.add_argument("--A", nargs="*", type=float, default=list(A_CANDIDATES))
    args = ap.parse_args(argv)
    for a in args.A:
        if a not in A_CANDIDATES:
            raise SystemExit(f"A={a} is not one of the contract candidates {A_CANDIDATES} (Op. rule 3)")
    b_m, radii = calibration()
    tok = GPT2Tokenizer()
    results = {"candidates": {}, "b_m": b_m, "radii": radii, "n_per_dataset": args.n}
    with gpu_lease("S2-02", stage="S2", projected_seconds=3 * 3600) as lease:
        for A in args.A:
            per_ds = {}
            for ds in args.datasets:
                items, unrelated = load_dev_items(ds, args.n)
                per_ds[ds] = screen_one(A, items, unrelated, b_m, radii, tok, S2 / "screen" / f"A{A}" / ds)
                print(f"A={A} {ds}: ES {per_ds[ds]['es_immediate']:.3f} thr {per_ds[ds]['threshold_acquisition']:.3f} "
                      f"false-fire {per_ds[ds]['false_fire']['rate']:.4f} ({per_ds[ds]['seconds']:.0f}s)", flush=True)
            es = float(np.mean([per_ds[ds]["es_immediate"] for ds in args.datasets]))
            loc = all(per_ds[ds]["locality_ok"] for ds in args.datasets)
            results["candidates"][str(A)] = {"es_mean": es, "locality_ok": loc, "per_dataset": {ds: {k: v for k, v in per_ds[ds].items() if k != "rows"} for ds in per_ds}}
        ok = [(float(a), c["es_mean"]) for a, c in results["candidates"].items() if c["locality_ok"]]
        if ok:
            best_es = max(e for _, e in ok)
            tied = [a for a, e in ok if e == best_es]
            chosen = 0.1 if 0.1 in tied else tied[0]
            results["chosen_A"] = chosen
            results["rule"] = "highest immediate ES among candidates meeting the <= 1% false-fire criterion; tie -> 0.1"
        else:
            results["chosen_A"] = None
            results["rule"] = "no candidate functions; diagnoses required (Op. rule 5), no new sweep"
        results["lease"] = lease.report
        results["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (S2 / "A_screening.json").write_text(json.dumps(results, indent=1, default=float))
    print("chosen A:", results["chosen_A"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
