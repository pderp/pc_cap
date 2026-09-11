"""Progress of the confirmatory queue (read-only; CPU): completed runs per dataset/arm, failures, resource stops, wall-clock
per job and the ETA for the remaining scheduled jobs from the observed per-arm wall times (projection fallback).
    python scripts/s4_progress.py [--stage S4] [--json]"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="S4")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    jobs = json.loads((ROOT / "results" / "S4" / "jobs.json").read_text())["jobs"]
    scheduled = [j for j in jobs if j["stage"] == args.stage and j["status"] == "scheduled"]
    qpath = ROOT / "results" / args.stage / "queue.jsonl"
    attempts = [json.loads(line) for line in qpath.read_text().splitlines() if line.strip()] if qpath.exists() else []
    done = {}
    for a in attempts:
        j = a["job"]
        key = (j["dataset"], j["arm"], j["realization"], j["perm"])
        done[key] = a  # the last attempt per cell wins
    by_arm = collections.defaultdict(lambda: {"complete": 0, "resource_stop": 0, "failed": 0, "wall": []})
    for key, a in done.items():
        row = by_arm[(key[0], key[1])]
        st = a.get("status")
        if st == "complete":
            row["complete"] += 1
            row["wall"].append(a.get("wall_seconds", 0.0))
        elif st == "resource_stop":
            row["resource_stop"] += 1
            row["wall"].append(a.get("wall_seconds", 0.0))
        else:
            row["failed"] += 1
    total = len(scheduled)
    finished = sum(1 for j in scheduled if done.get((j["dataset"], j["arm"], j["realization"], j["perm"]), {}).get("status") in ("complete", "resource_stop"))
    remaining = [j for j in scheduled if done.get((j["dataset"], j["arm"], j["realization"], j["perm"]), {}).get("status") not in ("complete", "resource_stop")]
    proj = json.loads((ROOT / "results" / "S2" / "projection.json").read_text())
    sel = proj["selected"]
    row = next(r for r in proj["table"] if all(r[k] == sel[k] for k in ("zsre", "counterfact", "grammar")))
    eta = 0.0
    basis = collections.Counter()
    for j in remaining:
        obs = by_arm.get((j["dataset"], j["arm"], ), {}).get("wall", [])
        if obs:
            eta += statistics.median(obs)
            basis["observed"] += 1
        else:
            part = row["parts"].get(f"{j['arm']}/{j['dataset']}") or row["parts"].get(f"C0/{j['dataset']}/initial300") or row["parts"].get("grammar")
            per = (part / 15 if j["dataset"] != "grammar" else part / 60) if part else 600.0
            eta += 2.5 * per  # wall ≈ 2.5 × accelerator on this host
            basis["projected"] += 1
    out = {"stage": args.stage, "now": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "scheduled": total, "finished": finished, "remaining": len(remaining),
           "per_arm": {f"{d}/{a}": {k: (round(statistics.median(v), 1) if k == "wall" and v else v if k != "wall" else None) for k, v in r.items()} for (d, a), r in sorted(by_arm.items())},
           "failed_cells": [k for k, a in done.items() if a.get("status") not in ("complete", "resource_stop")],
           "eta_hours_remaining": eta / 3600, "eta_basis": dict(basis),
           "queue_summary": json.loads((ROOT / "results" / args.stage / "queue_summary.json").read_text()) if (ROOT / "results" / args.stage / "queue_summary.json").exists() else None}
    if out["queue_summary"]:
        out["queue_summary"] = {k: v for k, v in out["queue_summary"].items() if k != "attempts"}
    if args.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"{args.stage}: {finished}/{total} finished, {len(remaining)} remaining, ETA ≈ {eta / 3600:.1f} h ({dict(basis)})")
        for k, r in out["per_arm"].items():
            print(f"  {k:22s} complete {r['complete']:2d}  resource_stop {r['resource_stop']}  failed {r['failed']}  median wall s {r['wall']}")
        if out["failed_cells"]:
            print("  FAILED:", out["failed_cells"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
