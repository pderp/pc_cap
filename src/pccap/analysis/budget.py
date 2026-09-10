"""Stage cost totals against the ceilings (plan §4.7, §9; PA-3).

``python -m pccap.analysis.budget`` sums every ``results/<stage>/**/cost.json`` plus the task
ledger ``results/ledger/tasks.jsonl`` into ``results/ledger/stages.json`` and compares local
accelerator seconds with the A100-equivalent ceilings using κ from ``results/ENV/kappa.json``.
``--project`` (S2-07) is added when throughput exists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "results"
CEILINGS_A100_H = {"S0": 8, "S1": 12, "S2": 12, "S3": 16, "S4": 36, "S5": 24, "S6": 20, "S7": 10, "S8": 16}
STAGE_OF_TASK_PREFIX = {"ENV": "S0", "DATA": "S0", "CAP": "S0", "REF": "S0", "GRAM": "S3", "REG": "S6", "ANA": "S4"}


def kappa() -> dict:
    p = RESULTS / "ENV" / "kappa.json"
    if p.exists():
        return json.loads(p.read_text())
    return {"kappa": 1.0, "kappa_band": [0.5, 2.0], "status": "provisional (kappa.json absent)"}


def run_costs() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for cj in RESULTS.glob("S*/**/cost.json"):
        stage = cj.relative_to(RESULTS).parts[0]
        c = json.loads(cj.read_text())
        s = out.setdefault(stage, {"runs": 0, "accel_seconds": 0.0, "wall_seconds": 0.0, "query_accel_seconds": 0.0,
                                   "learning_accel_seconds": 0.0, "full_forwards": 0, "partial_forwards": 0, "reverses": 0})
        s["runs"] += 1
        s["accel_seconds"] += c["total"]["accel_seconds"]
        s["wall_seconds"] += c["total"]["wall_seconds"]
        s["query_accel_seconds"] += c["query"]["accel_seconds"]
        s["learning_accel_seconds"] += c["learning"]["accel_seconds"]
        for k in ("full_forwards", "partial_forwards", "reverses"):
            s[k] += c["total"][k]
    return out


def task_costs() -> dict[str, float]:
    p = RESULTS / "ledger" / "tasks.jsonl"
    out: dict[str, float] = {}
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        prefix = r["task"].split("-")[0]
        stage = STAGE_OF_TASK_PREFIX.get(prefix, prefix)
        out[stage] = out.get(stage, 0.0) + float(r.get("gpu_seconds", 0.0))
    return out


def stages_summary() -> dict:
    k = kappa()
    kap = float(k["kappa"])
    runs = run_costs()
    tasks = task_costs()
    stages = {}
    for stage, ceiling_h in CEILINGS_A100_H.items():
        local_s = runs.get(stage, {}).get("accel_seconds", 0.0) + tasks.get(stage, 0.0)
        local_h = local_s / 3600.0
        stages[stage] = {
            "ceiling_a100_h": ceiling_h,
            "ceiling_local_h_at_kappa": ceiling_h / kap,
            "local_accel_seconds_runs": runs.get(stage, {}).get("accel_seconds", 0.0),
            "local_gpu_seconds_tasks": tasks.get(stage, 0.0),
            "local_hours_total": local_h,
            "a100_equivalent_hours": local_h * kap,
            "a100_equivalent_band": [local_h * k["kappa_band"][0], local_h * k["kappa_band"][1]],
            "fraction_of_ceiling": (local_h * kap) / ceiling_h if ceiling_h else None,
            "affordable_threshold_fraction": 0.75,
            "runs": runs.get(stage, {}),
        }
    return {"kappa": k, "stages": stages, "total_local_hours": sum(s["local_hours_total"] for s in stages.values()),
            "total_ceiling_a100_h": sum(CEILINGS_A100_H.values())}


def main(argv=None) -> int:
    import sys

    if "--project" in (argv if argv is not None else sys.argv[1:]):
        a = [x for x in (argv if argv is not None else sys.argv[1:]) if x != "--project"]
        return main_project(a)
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(RESULTS / "ledger" / "stages.json"))
    args = ap.parse_args(argv)
    s = stages_summary()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(s, indent=1))
    for st, v in s["stages"].items():
        if v["local_hours_total"] > 0:
            print(f"{st}: {v['local_hours_total']:.3f} local h = {v['a100_equivalent_hours']:.3f} A100-eq h of {v['ceiling_a100_h']} ({100 * v['fraction_of_ceiling']:.1f}%)")
    print("wrote", args.out)
    return 0



# ----------------------------------------------------------------------------- S2-07 projection
SCOPES_ZS = (3000, 1000, 300)
SCOPES_CF = (1000, 300)
SCOPES_GR = (10000, 1024, 256)
CHECKPOINTS = (100, 300, 1000, 3000)
EDIT_ARMS = ("C1", "C2", "CR", "B3", "B4")
REALIZATIONS_X_ORDERS = 15
S4_CEILING_A100_H = 36
HEADROOM = 0.75  # SD-5


def _per_edit(th: dict, arm: str, ds: str) -> dict | None:
    r = th["runs"].get(f"{arm}/{ds}")
    if r is None:
        return None
    # rescoring pass at the checkpoint: query seconds attributable to re-evaluating `n` items at the end of the run
    # (the run includes one checkpoint at 100 = end, so the query column holds immediate evals + one rescore + LS + drift).
    return {"learn_s": r["learning_accel_seconds_per_edit"], "query_s": r["query_accel_seconds_per_edit"],
            "wall_s": r["wall_seconds_per_edit"], "n": r["n_items"]}


def project(th: dict, kappa_value: float, grammar_learn_s: float | None = None, baseline_factor: float = 1.0) -> dict:
    """Section 9 scope-selection algorithm on measured per-edit costs.

    Cost of one editing run of `n` items = n × (learn_s + query_s) [immediate evaluation included]
    + rescoring at checkpoints ≤ n (each ≈ items_so_far × immediate-eval cost, approximated by
    query_s × items_so_far) + endpoint rescore. Arms without a measurement (B3/B4) use the C1 cost ×
    ``baseline_factor`` and are flagged. Grammar cost needs ``grammar_learn_s`` (GRAM-02); if
    absent the grammar term is reported unknown and excluded, and the memo says so.
    """
    ceiling_s = S4_CEILING_A100_H * 3600.0 / kappa_value
    budget_s = HEADROOM * ceiling_s
    assumed = []

    def edit_run_cost(arm: str, ds: str, n: int) -> float:
        pe = _per_edit(th, arm, ds)
        if pe is None:
            pe = _per_edit(th, "C1", ds)
            if pe is None:
                return float("nan")
            pe = {**pe, "learn_s": pe["learn_s"] * baseline_factor}
            assumed.append(f"{arm}/{ds}")
        immediate = n * (pe["learn_s"] + pe["query_s"])
        rescore = sum(c * pe["query_s"] for c in CHECKPOINTS if c < n) + n * pe["query_s"]
        return immediate + rescore

    def total(zs: int, cf: int, gr: int) -> tuple[float, dict]:
        parts = {}
        s = 0.0
        for arm in EDIT_ARMS:
            for ds, n in (("zsre", zs), ("counterfact", cf)):
                c = REALIZATIONS_X_ORDERS * edit_run_cost(arm, ds, n)
                parts[f"{arm}/{ds}"] = c
                s += c
        for ds in ("zsre", "counterfact"):
            c = REALIZATIONS_X_ORDERS * edit_run_cost("C0", ds, 300)
            parts[f"C0/{ds}/initial300"] = c
            s += c
        if grammar_learn_s is not None:
            c = 4 * REALIZATIONS_X_ORDERS * gr * grammar_learn_s
            parts["grammar"] = c
            s += c
        else:
            parts["grammar"] = None
        return s, parts

    table = []
    selected = None
    for zs in SCOPES_ZS:
        for cf in SCOPES_CF:
            for gr in SCOPES_GR:
                s, parts = total(zs, cf, gr)
                row = {"zsre": zs, "counterfact": cf, "grammar": gr, "seconds": s, "local_hours": s / 3600, "a100_eq_hours": s * kappa_value / 3600,
                       "affordable": s <= budget_s, "parts": parts}
                table.append(row)
                if selected is None and s <= budget_s:
                    selected = {"zsre": zs, "counterfact": cf, "grammar": gr, "seconds": s}
    return {"kappa": kappa_value, "ceiling_seconds_local": ceiling_s, "budget_seconds_after_headroom": budget_s, "headroom": HEADROOM,
            "selected": selected, "assumed_arms": sorted(set(assumed)), "baseline_factor": baseline_factor,
            "grammar_included": grammar_learn_s is not None, "table": table,
            "rule": "first affordable (zs, cf, gr) in the order 3000/1000/300 x 1000/300 x 10000/1024/256; scope selection uses pilot throughput only (PDF App. B)"}


def main_project(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--throughput", default=str(RESULTS / "S2" / "throughput.json"))
    ap.add_argument("--baseline-factor", type=float, default=1.0)
    ap.add_argument("--grammar-learn-s", type=float, default=None)
    ap.add_argument("--out", default=str(RESULTS / "S2" / "projection.json"))
    args = ap.parse_args(argv)
    th = json.loads(Path(args.throughput).read_text())
    k = float(kappa()["kappa"])
    p = project(th, k, args.grammar_learn_s, args.baseline_factor)
    Path(args.out).write_text(json.dumps(p, indent=1, default=float))
    print("selected:", p["selected"], "assumed:", p["assumed_arms"], "grammar included:", p["grammar_included"])
    for r in p["table"][:6]:
        print(f"zs {r['zsre']} cf {r['counterfact']} gr {r['grammar']}: {r['local_hours']:.1f} h  affordable={r['affordable']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
