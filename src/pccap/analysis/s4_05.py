"""S4-05: resource views over completed runs (plan §6.10 S4-05; PDF App. B).

For a set of runs (directories with ``items.jsonl``, ``checkpoints.json``, ``metrics.json``):

* **exposure-matched** table: per arm, retention/ES/LS at the checkpoints every arm completed (items);
* **time-matched** table: retention versus cumulative accelerator seconds (learning + immediate query)
  read from the per-item cost records, at fixed accelerator budgets;
* **longest common completed prefix** per contrast (min items completed across the two arms of a
  contrast for the same dataset/realization/order);
* **comparable-compute eligibility**: mean learning accelerator seconds per edit within 20% of the
  reference arm (C2) or a resource-matched support statement.

    python -m pccap.analysis.s4_05 --root results/S4 [--root results/S2/throughput --root results/S2/throughput_baselines]
                                   --out results/S4/resource_views.json --label development

Development runs (one order) give a descriptive table; the confirmatory call runs on ``results/S4``.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CONTRASTS = (("C2", "C1"), ("C2", "CR"), ("C2", "C0"), ("C2", "B3"), ("C2", "B4"))
BUDGETS_S = (10, 30, 60, 120, 300, 600, 1800, 3600)


def discover(roots: list[Path], experiment_id: str | None = None) -> list[dict]:
    runs = []
    for rt in roots:
        for mp in sorted(rt.rglob("metrics.json")):
            if ".superseded-" in str(mp):
                continue  # archived attempt (V-03)
            d = mp.parent
            if d.name == "warmup" or not (d / "items.jsonl").exists():
                continue
            m = json.loads(mp.read_text())
            run_id = m.get("config", {}).get("experiment_id")
            if experiment_id is not None and run_id != experiment_id:
                continue  # V2-02: a specific filter requires the exact id; runs with no id are unknown provenance
            rel = d.relative_to(rt).parts
            arm = m.get("arm") or rel[0]
            ds = m.get("config", {}).get("dataset") or (rel[1] if len(rel) > 1 else "?")
            real = m.get("config", {}).get("realization", 0)
            perm = m.get("config", {}).get("perm", 0)
            items = [json.loads(line) for line in (d / "items.jsonl").read_text().splitlines() if line.strip()]
            ck = json.loads((d / "checkpoints.json").read_text()) if (d / "checkpoints.json").exists() else []
            runs.append({"dir": str(d), "arm": arm, "dataset": ds, "realization": real, "perm": perm, "items": items, "checkpoints": ck,
                         "status": m.get("status"), "metrics": {k: v["value"] for k, v in m["metrics"].items()}, "experiment_id": run_id})
    return runs


def require_one_experiment(runs: list[dict]) -> str | None:
    """V2-03: views over runs of several experiments (or of unknown provenance mixed with identified runs) are refused;
    select one with ``discover(..., experiment_id=...)``."""
    ids = {r.get("experiment_id") for r in runs}
    if len(ids) > 1:
        raise ValueError(f"runs belong to several experiments {sorted(map(str, ids))}; pass --experiment-id (V2-03)")
    return next(iter(ids)) if ids else None


def item_seconds(it: dict, phase: str = "total", part: str = "update+eval") -> float:
    """Accelerator seconds attributable to one item from the shared-ledger delta (R2-06). ``part`` selects
    ``"update"`` (the learner's update only — the PDF App. B comparable-compute quantity), ``"eval"`` (the
    immediate evaluation) or ``"update+eval"``; ``phase`` selects the ledger column (total/learning/query).
    Falls back to the learner-internal cost record (learning only, incomplete for cap arms) with a flag."""
    ld = it.get("ledger_delta")
    if ld:
        u, e = float(ld["update"][phase]), float(ld["immediate_eval"][phase])
        return u if part == "update" else e if part == "eval" else u + e
    return float(it["cost"]["accel_seconds"])


def cumulative_accel(items: list[dict], phase: str = "total") -> np.ndarray:
    """Cumulative accelerator seconds after each item from the recorded ledger snapshots (setup, immediate
    evaluations and intermediate rescoring included — V-05); falls back to summed item deltas."""
    if items and all(it.get("ledger_delta") for it in items):
        return np.array([float(it["ledger_delta"]["cumulative"][phase]) for it in items])
    return np.cumsum([item_seconds(it, phase) for it in items])


def checkpoint_seconds(c: dict, cum: np.ndarray) -> float:
    led = c.get("ledger_accel_seconds_at_checkpoint")
    if led:
        return float(led["total"])  # includes evaluation setup, immediate evaluations and every rescoring pass so far
    return float(cum[c["items"] - 1]) if c["items"] else 0.0


def views(runs: list[dict]) -> dict:
    out = {"experiment_id": require_one_experiment(runs), "exposure_matched": {}, "time_matched": {}, "longest_common_prefix": {}, "comparable_compute": {}, "per_run": []}
    by = {}
    for r in runs:
        key = (r["dataset"], r["realization"], r["perm"])
        by.setdefault(key, {})[r["arm"]] = r
        cum = cumulative_accel(r["items"])
        es_cum = np.cumsum([it["es"] for it in r["items"]]) / np.arange(1, len(r["items"]) + 1)
        tm = {}
        for b in BUDGETS_S:
            k = int(np.searchsorted(cum, b, side="right"))
            tm[str(b)] = {"items_within_budget": k, "es_running_mean": float(es_cum[k - 1]) if k else None}
        rets = {c["tag"]: {"items": c["items"], "ret_es": c["ret_es"], "ret_gs": c["ret_gs"], "ls": c["locality"]["ls_complete_answer"], "accel_seconds_at": checkpoint_seconds(c, cum)} for c in r["checkpoints"]}
        learn = [it["ledger_delta"]["update"]["total"] if it.get("ledger_delta") else it["cost"]["accel_seconds"] for it in r["items"]]
        complete = all(it.get("ledger_delta") for it in r["items"])
        out["per_run"].append({"dir": r["dir"], "arm": r["arm"], "dataset": r["dataset"], "realization": r["realization"], "perm": r["perm"], "status": r["status"],
                               "items_completed": len(r["items"]), "accel_seconds_total": float(cum[-1]) if len(cum) else 0.0,
                               "cost_source": "ledger deltas (update + immediate evaluation)" if complete else "learner cost record only (incomplete for cap arms; pre-R2-06 run)",
                               "mean_update_accel_s": float(np.mean(learn)) if learn else None, "retention_vs_items": rets, "es_vs_accel_budget": tm,
                               "retained_vs_accel_budget": {c["tag"]: {"accel_seconds_at": checkpoint_seconds(c, cum), "ret_es": c["ret_es"], "ret_gs": c["ret_gs"]} for c in r["checkpoints"]}})
    # exposure-matched per CONTRAST PAIR (R2-06): checkpoints both arms of the pair completed, never intersected over all arms
    for key, arms in by.items():
        table = {}
        for a, b in CONTRASTS:
            if a in arms and b in arms:
                common = {c["items"] for c in arms[a]["checkpoints"]} & {c["items"] for c in arms[b]["checkpoints"]}
                table[f"{a}-{b}"] = {str(n): {arm: next(({"ret_es": c["ret_es"], "ret_gs": c["ret_gs"], "ls": c["locality"]["ls_complete_answer"]} for c in arms[arm]["checkpoints"] if c["items"] == n), None) for arm in (a, b)} for n in sorted(common)}
        out["exposure_matched"]["/".join(map(str, key))] = table
        # time-matched: ES running mean at accelerator budgets
        out["time_matched"]["/".join(map(str, key))] = {str(b): {arm: next(p for p in out["per_run"] if p["dir"] == r["dir"])["es_vs_accel_budget"][str(b)] for arm, r in arms.items()} for b in BUDGETS_S}
        # longest common completed prefix per contrast
        lcp = {}
        for a, b in CONTRASTS:
            if a in arms and b in arms:
                lcp[f"{a}-{b}"] = min(len(arms[a]["items"]), len(arms[b]["items"]))
        out["longest_common_prefix"]["/".join(map(str, key))] = lcp
        # comparable compute vs C2
        if "C2" in arms:
            ref = np.mean([item_seconds(it, part="update") for it in arms["C2"]["items"]])  # update time only (PDF App. B)
            ref_total = np.mean([item_seconds(it) for it in arms["C2"]["items"]])
            cc = {}
            for arm, r in arms.items():
                m = float(np.mean([item_seconds(it, part="update") for it in r["items"]]))
                mt = float(np.mean([item_seconds(it) for it in r["items"]]))
                cc[arm] = {"mean_update_accel_s": m, "ratio_to_C2_update": m / ref if ref else None, "within_20pct_update": bool(ref and abs(m - ref) / ref <= 0.2),
                           "mean_update_plus_eval_accel_s": mt, "ratio_to_C2_update_plus_eval": mt / ref_total if ref_total else None,
                           "support": "comparable-compute (update time within 20%)" if ref and abs(m - ref) / ref <= 0.2 else "resource-matched view required (time-matched table)"}
            out["comparable_compute"]["/".join(map(str, key))] = cc
    return out


def render(v: dict, label: str) -> str:
    L = [f"# Resource views ({label})", "", f"Rendered {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} by `python -m pccap.analysis.s4_05`.", "",
         "## Comparable-compute eligibility (mean update accelerator seconds per edit vs C2; within 20% → comparable)", "",
         "| stream | arm | mean update s | ratio to C2 | eligible |", "| --- | --- | ---: | ---: | --- |"]
    for key, cc in v["comparable_compute"].items():
        for arm, c in cc.items():
            L.append(f"| {key} | {arm} | {c['mean_update_accel_s']:.3f} | {c['ratio_to_C2_update']:.2f} | {'yes' if c['within_20pct_update'] else 'no'} |")
    L += ["", "## Exposure-matched retention per contrast (checkpoints both arms completed)", ""]
    for key, table in v["exposure_matched"].items():
        for pair, per_n in table.items():
            for n, row in per_n.items():
                L.append(f"- {key} {pair} @ {n} items: " + "; ".join(f"{arm}: RET-ES {c['ret_es']:.2f} RET-GS {c['ret_gs'] if c['ret_gs'] is None else round(c['ret_gs'], 2)} LS {c['ls']:.2f}" for arm, c in row.items() if c))
    L += ["", "## Time-matched (items completed and running immediate-ES acquisition curve within an accelerator budget; retained performance at checkpoints is `retained_vs_accel_budget` in the JSON)", ""]
    for key, tm in v["time_matched"].items():
        for b in ("30", "120", "600"):
            L.append(f"- {key} @ {b} s: " + "; ".join(f"{arm}: {c['items_within_budget']} items, ES {c['es_running_mean'] if c['es_running_mean'] is None else round(c['es_running_mean'], 2)}" for arm, c in tm[b].items()))
    L += ["", "## Longest common completed prefix per contrast", ""]
    for key, lcp in v["longest_common_prefix"].items():
        L.append(f"- {key}: {lcp}")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=None)
    ap.add_argument("--out", default=str(ROOT / "results" / "S4" / "resource_views.json"))
    ap.add_argument("--label", default="confirmatory")
    ap.add_argument("--experiment-id", default=None)
    args = ap.parse_args(argv)
    roots = [Path(r) for r in (args.root or [str(ROOT / "results" / "S4")])]
    runs = discover(roots, args.experiment_id)
    v = views(runs) | {"label": args.label, "roots": [str(r) for r in roots], "n_runs": len(runs)}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(v, indent=1, default=float))
    Path(args.out).with_suffix(".md").write_text(render(v, args.label))
    print(len(runs), "runs ->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
