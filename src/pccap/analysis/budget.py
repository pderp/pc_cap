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


if __name__ == "__main__":
    raise SystemExit(main())
