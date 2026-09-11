"""S7-03: order variation from the committed permutations (plan §6.13 S7-03; PDF S7, PR-E).

For one dataset and arm, over the realizations and their five committed orders (S4 runs):

* ACC std across orders: the endpoint RET-ES / RET-GS (mean over the items of the run) per order,
  its std across the five orders within each realization, and across realizations;
* pairwise disagreement at identical exposure: for two orders of the same realization, the fraction of
  items (present in both endpoint tables) whose retained-ES outcome differs; reported per pair and averaged;
* lost-item sets: items acquired immediately (ES = 1) but not retained at the endpoint, per order, with
  the intersection/union across orders (items lost under every order vs under some);
* JS at identical prefixes needs the saved learner checkpoints and a GPU evaluation set Q; that part
  is ``s7_03_js`` (pending S4-04 checkpoints) and is reported ``unavailable`` here.

    python -m pccap.analysis.s7_03 --dataset zsre --arm C2 [--root results/S4]
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np

from pccap.contracts import metric

ROOT = Path(__file__).resolve().parents[3]


def load_runs(root: Path, dataset: str, arm: str, experiment_id: str | None = None) -> dict[tuple[int, int], dict]:
    """Endpoint tables per (realization, order). A specific ``experiment_id`` selects exactly that experiment; without
    one, all runs must belong to a single experiment and every cell must be unique (V2-02/03)."""
    runs = {}
    ids: set = set()
    for mp in sorted(root.rglob("metrics.json")):
        if ".superseded-" in str(mp):
            continue  # archived attempt (V-03): never collected
        d = mp.parent
        m = json.loads(mp.read_text())
        cfg = m.get("config", {})
        run_id = cfg.get("experiment_id")
        if experiment_id is not None and run_id != experiment_id:
            continue  # V2-02: exact id required under a filter; runs with no id are unknown provenance
        if cfg.get("dataset") != dataset or m.get("arm") != arm:
            continue
        ids.add(run_id)
        if experiment_id is None and len(ids) > 1:
            raise ValueError(f"runs under {root} belong to several experiments {sorted(map(str, ids))}; pass --experiment-id (V2-03)")
        key = (int(cfg["realization"]), int(cfg["perm"]))
        if key in runs:
            raise ValueError(f"two runs for realization/order {key} of {dataset}/{arm} under {root} ({runs[key]['dir']} and {d}); never merged silently (V2-03)")
        items = {json.loads(line)["item_id"]: json.loads(line) for line in (d / "items.jsonl").read_text().splitlines() if line.strip()}
        ck = json.loads((d / "checkpoints.json").read_text()) if (d / "checkpoints.json").exists() else []
        end = next((c for c in ck if c["tag"] == "end"), None)
        if end is None:
            continue
        runs[key] = {"items": items, "end": {r["item_id"]: r for r in end["rows"]}, "status": m.get("status"), "dir": str(d), "experiment_id": run_id}
    return runs


def analyze(runs: dict[tuple[int, int], dict]) -> dict:
    by_real: dict[int, dict[int, dict]] = {}
    for (r, o), run in runs.items():
        by_real.setdefault(r, {})[o] = run
    out = {"realizations": {}, "n_runs": len(runs)}
    acc_es_all, acc_gs_all = [], []
    for r, orders in sorted(by_real.items()):
        acc_es = {o: float(np.mean([x["ret_es"] for x in run["end"].values()])) for o, run in orders.items()}
        acc_gs = {o: float(np.mean([x["ret_gs"] for x in run["end"].values() if x["ret_gs"] is not None])) for o, run in orders.items()}
        lost = {o: sorted(i for i, it in run["items"].items() if it["es"] == 1.0 and run["end"].get(i, {}).get("ret_es", 1.0) < 1.0) for o, run in orders.items()}
        pairs = {}
        for a, b in itertools.combinations(sorted(orders), 2):
            common = set(orders[a]["end"]) & set(orders[b]["end"])
            dis = float(np.mean([(orders[a]["end"][i]["ret_es"] == 1.0) != (orders[b]["end"][i]["ret_es"] == 1.0) for i in common])) if common else None
            pairs[f"{a}-{b}"] = {"common_items": len(common), "retained_es_disagreement": dis}
        sets = [set(v) for v in lost.values()]
        out["realizations"][str(r)] = {
            "acc_ret_es_per_order": acc_es, "acc_ret_gs_per_order": acc_gs,
            "acc_ret_es_std_across_orders": float(np.std(list(acc_es.values()), ddof=1)) if len(acc_es) > 1 else None,
            "acc_ret_gs_std_across_orders": float(np.std(list(acc_gs.values()), ddof=1)) if len(acc_gs) > 1 else None,
            "pairwise": pairs, "mean_pairwise_disagreement": float(np.mean([p["retained_es_disagreement"] for p in pairs.values() if p["retained_es_disagreement"] is not None])) if pairs else None,
            "lost_items_per_order": {str(o): len(v) for o, v in lost.items()},
            "lost_under_every_order": sorted(set.intersection(*sets)) if sets else [], "lost_under_some_order": len(set.union(*sets)) if sets else 0,
        }
        acc_es_all += list(acc_es.values())
        acc_gs_all += list(acc_gs.values())
    out["acc_ret_es_std_all_runs"] = float(np.std(acc_es_all, ddof=1)) if len(acc_es_all) > 1 else None
    out["acc_ret_gs_std_all_runs"] = float(np.std(acc_gs_all, ddof=1)) if len(acc_gs_all) > 1 else None
    out["js_at_identical_prefixes"] = metric(None, units="nats", n=0, status="unavailable")
    out["js_note"] = "needs the saved learner checkpoints and a fixed evaluation set Q on the GPU (s7_03_js, after S4-04)"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--root", default=str(ROOT / "results" / "S4"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--experiment-id", default=None, help="analyse only runs of this frozen experiment id (V2-03)")
    args = ap.parse_args(argv)
    runs = load_runs(Path(args.root), args.dataset, args.arm, args.experiment_id)
    rep = analyze(runs) | {"dataset": args.dataset, "arm": args.arm, "experiment_id": args.experiment_id or next((r["experiment_id"] for r in runs.values()), None), "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "label": "PR-E descriptive"}
    out = Path(args.out) if args.out else ROOT / "results" / "S7" / f"order_variation_{args.dataset}_{args.arm}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1, default=float))
    print(args.dataset, args.arm, "runs", rep["n_runs"], "ACC RET-GS std (all runs)", rep["acc_ret_gs_std_all_runs"], "->", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
