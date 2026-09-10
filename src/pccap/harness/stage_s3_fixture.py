"""S3-02: constructed-fixture runs on MODULAR-CONTROL (PDF S3, D.10; plan §6.9).

Arms C0/C1/C2/CR/CO on the three variants (useful sharing, no sharing, wrong router): oracle
success (gate), private/shared/mixed acquisition and transfer/harm (held-out combinations and the
other items' outputs), C2 delivery precision/recall against ``R*`` with bootstrap intervals, the
majority-bank baseline, per-latent confusion matrices, multi-cause coverage. CPU only.

    python -m pccap.harness.stage_s3_fixture --n 60      # items per kind
→ results/S3/fixture/<variant>/<arm>/metrics.json and results/S3/fixture/summary.json
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

from pccap.contracts import metric
from pccap.fixtures import modular_control as mc

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "S3" / "fixture"
ARMS = ("C0", "C1", "C2", "CR", "CO")


def routes_from_rows(rows: list[dict]) -> list[list[int]]:
    """Accepted deliveries per item from the ``accepted:<bank>`` codes."""
    out = []
    for r in rows:
        banks = sorted({int(c.split(":")[1]) for c in r["routes"] if ":" in c})
        out.append(banks)
    return out


def precision_recall(items: list[mc.ItemSpec], deliveries: list[list[int]], rng: np.random.Generator, draws: int = 2000) -> dict:
    """Delivery precision = fraction of accepted bank deliveries inside R*; item recall = fraction
    of eligible items with at least one delivery in R*. Bootstrap over items."""
    ok = tot = hit = elig = 0
    per_item = []
    for it, banks in zip(items, deliveries):
        if not it.r_star:
            continue
        elig += 1
        in_r = [b for b in banks if b in it.r_star]
        ok += len(in_r)
        tot += len(banks)
        hit += bool(in_r)
        per_item.append((len(in_r), len(banks), bool(in_r)))
    prec = ok / tot if tot else None
    rec = hit / elig if elig else None
    bp, br = [], []
    n = len(per_item)
    for _ in range(draws if n else 0):
        idx = rng.integers(0, n, n)
        o = sum(per_item[i][0] for i in idx)
        t = sum(per_item[i][1] for i in idx)
        h = sum(per_item[i][2] for i in idx)
        bp.append(o / t if t else np.nan)
        br.append(h / n)
    ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))] if a else None  # noqa: E731
    return {"precision": metric(prec, units="fraction", numerator=ok, denominator=tot, n=elig, status="ok" if tot else "undefined"),
            "recall": metric(rec, units="fraction", numerator=hit, denominator=elig, n=elig, status="ok" if elig else "undefined"),
            "precision_ci95": ci(bp), "recall_ci95": ci(br), "deliveries": tot, "abstained_items": sum(1 for d in deliveries if not d)}


def confusion(items: list[mc.ItemSpec], deliveries: list[list[int]]) -> dict:
    """Per-latent (kind, bank) confusion: which bank received the delivery."""
    conf: dict[str, Counter] = {}
    for it, banks in zip(items, deliveries):
        key = f"{it.kind}-{it.bank}" if it.kind != "shared" else "shared"
        c = conf.setdefault(key, Counter())
        for b in banks:
            c[str(b)] += 1
        if not banks:
            c["none"] += 1
    return {k: dict(v) for k, v in conf.items()}


def majority_bank(items: list[mc.ItemSpec]) -> dict:
    """Baseline: always deliver to the most common R* bank."""
    counts = Counter(b for it in items for b in it.r_star)
    if not counts:
        return {"bank": None}
    bank, _ = counts.most_common(1)[0]
    elig = [it for it in items if it.r_star]
    prec = sum(bank in it.r_star for it in elig) / len(elig)
    return {"bank": bank, "precision": prec, "recall": prec}


def run_variant(variant: str, n: int, arms=ARMS, seed: int = 0) -> dict:
    sharing = "none" if variant == "no_sharing" else "useful"
    wrong = variant == "wrong_router"
    results = {}
    for arm in arms:
        base = mc.ModularControlBase(seed=0, sharing=sharing)
        items = base.make_items(n_private=n, n_shared=n, n_mixed=n, n_heldout=n // 2, wrong_router=wrong)
        unrelated = base.make_items(n_private=0, n_shared=0, n_mixed=0, n_heldout=20, start_index=380)
        t0 = time.time()
        res = mc.learn_and_score(base, [it for it in items if not it.held_out], arm, A=1.0, radius=0.0, seed=seed, unrelated=unrelated)
        # held-out combinations: were they acquired "for free" (transfer) or harmed?
        held = [it for it in items if it.held_out]
        deliveries = routes_from_rows(res["rows"])
        core_items = [it for it in items if not it.held_out]
        rng = np.random.default_rng(seed)
        pr = precision_recall(core_items, deliveries, rng)
        by_kind = {}
        for kind in ("private", "shared", "mixed"):
            rows = [r for r in res["rows"] if r["kind"] == kind]
            by_kind[kind] = {"n": len(rows), "recovered": sum(r["recovered"] for r in rows), "threshold": sum(r["threshold"] for r in rows)}
        # multi-cause coverage: mixed items for bank 3 need bank 3 and a shared-path bank
        cov = []
        for it, banks in zip(core_items, deliveries):
            if it.kind == "mixed" and len(it.r_star) > 1:
                cov.append(all(b in banks for b in it.r_star))
        out_arm = {"arm": arm, "variant": variant, "recovery_rate": res["recovery_rate"], "recovered": res["recovered"], "total": res["total"],
                   "unrelated_max_abs_dp": res["unrelated_max_abs_dp"], "by_kind": by_kind, "delivery": pr, "confusion": confusion(core_items, deliveries),
                   "majority_bank_baseline": majority_bank(core_items), "multi_cause_coverage": {"n": len(cov), "covered": int(sum(cov))},
                   "held_out_pre_learning_note": "held-out combinations are evaluated by S3 transfer runs (not edited here)", "held_out": len(held),
                   "memory_occupied_bytes": res["memory"]["occupied_bytes"], "seconds": time.time() - t0}
        d = OUT / variant / arm
        d.mkdir(parents=True, exist_ok=True)
        (d / "metrics.json").write_text(json.dumps({**out_arm, "rows": res["rows"]}, indent=1, default=float))
        results[arm] = out_arm
        print(f"{variant} {arm}: recovery {res['recovery_rate']:.2f} precision {pr['precision']['value']} recall {pr['recall']['value']} ({out_arm['seconds']:.0f}s)", flush=True)
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--variants", nargs="*", default=["useful_sharing", "no_sharing", "wrong_router"])
    ap.add_argument("--arms", nargs="*", default=list(ARMS))
    args = ap.parse_args(argv)
    summary = {v: run_variant(v, args.n, args.arms) for v in args.variants}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps({"n_per_kind": args.n, "variants": summary, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
