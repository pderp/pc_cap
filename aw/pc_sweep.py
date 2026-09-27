"""PC-9 solver settings and CPU-only, development-profile cost projections.

This module never launches experiments. Forecasts do not authorize a run or
replace a profile of the selected settings. Historical profiles are evidence
about costs, not a claim that they were produced by the current source tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def positive_rate(value):
    rate = float(value)
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError("error learning rate must be positive and finite")
    return rate


def settings(arm, credit_iters=8, error_lr=0.1):
    if arm not in ("SE-A", "SE-E") or credit_iters not in (8, 16, 32):
        raise ValueError("expected SE-A/SE-E and 8, 16 or 32 credit iterations")
    rate = positive_rate(error_lr)
    return dict(
        credit_iters=credit_iters if arm == "SE-E" else 8,
        error_lr=rate if arm == "SE-E" else 0.1,
        error_solver_active=arm == "SE-E",
        requested_credit_iters=credit_iters,
        requested_error_lr=rate,
    )


def add_options(parser):
    parser.add_argument("--credit-iters", type=int, choices=(8, 16, 32), default=8)
    parser.add_argument("--error-lr", type=positive_rate, default=0.1)
    parser.add_argument("--sweep-error-lrs", type=positive_rate, nargs="+",
                        help="plan-only rates; defaults to --error-lr; no sweep is launched")


def _read(path, bindings):
    data = path.read_bytes()
    bindings[str(path.resolve())] = hashlib.sha256(data).hexdigest()
    return json.loads(data)


def projected_sweep(profile, cells, rates=(0.1,)):
    """Cost sensitivity, using only COMPLETE development records, never outcomes.

    Learning scales by items and (k+1)/(profile k+1) for SE-E. Startup is fixed.
    Query work is shown both fixed and scaled by items: these are scenarios,
    NOT bounds. Endpoint cadence, memory search and compilation can invalidate
    either extrapolation. Harm readout is outside the forecast.
    """
    rates = list(dict.fromkeys(positive_rate(x) for x in rates))
    if not rates:
        raise ValueError("at least one rate required")
    if profile is None:
        return dict(status="pending", reason="supply --profile with a completed development profile",
                    model_execution=False, variants=[], projected_process_seconds=None)
    profile, refs = Path(profile).resolve(), {}
    plan = _read(profile / "plan.json", refs)
    summary = _read(profile / "summary.json", refs)
    if plan["population"] != "development" or len(plan["cells"]) != 4:
        raise ValueError("four-cell development profile required")
    recorded = summary["finished"]
    if summary["planned"] != 4 or len(recorded) != 4:
        raise ValueError("incomplete development profile")
    records = {}
    for row in recorded:
        c = row["cell"]
        name = f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        folder = profile / name
        f = _read(folder / "finish.json", refs)
        cfg = _read(folder / "config.json", refs)
        coord = cfg.get("cell", cfg)
        if (c not in plan["cells"] or row["exit_code"] != 0 or row["finish"] != f
                or f["status"] != "complete" or f["items_completed"] != c["items"]
                or cfg["population"] != "development"
                or any(coord[k] != c[k] for k in c)
                or cfg["sources"] != plan["sources"]):
            raise ValueError("incomplete or inconsistent development cell")
        if "config_sha256" in f and f["config_sha256"] != refs[str((folder / "config.json").resolve())]:
            raise ValueError("profile config identity differs")
        actual = cfg.get("solver", cfg)
        k = actual.get("credit_iters", plan.get("credit", {}).get("iters"))
        lr = actual.get("error_lr", plan.get("credit", {}).get("error_lr"))
        settings(c["arm"], k, lr)
        process = folder / "process.json"
        elapsed = (_read(process, refs) if process.exists() else f)["elapsed_process_seconds"]
        learning = f["ledger"]["learning"]["wall_seconds"]
        query = f["ledger"]["query"]["wall_seconds"]
        if (c["items"] <= 0 or any(not math.isfinite(v) or v < 0 for v in (elapsed, learning, query))
                or learning + query > elapsed + 0.1):
            raise ValueError("invalid development cost accounting")
        key = (c["dataset"], c["arm"])
        if key in records:
            raise ValueError("duplicate profile coordinate")
        records[key] = dict(items=c["items"], credit_iters=k, error_lr=lr,
                            learning=learning, query=query, overhead=max(0, elapsed-learning-query))
    expected = {(ds, arm) for ds in ("zsre", "counterfact") for arm in ("SE-A", "SE-E")}
    if set(records) != expected:
        raise ValueError("both datasets and both credit arms required")
    variants = []
    for k in (8, 16, 32):
        for lr in rates:
            forecasts = []
            for c in cells:
                source = records[(c["dataset"], c["arm"])]
                factor = c["items"] / source["items"]
                if factor <= 0:
                    raise ValueError("positive planned item count required")
                multiplier = (k + 1) / (source["credit_iters"] + 1) if c["arm"] == "SE-E" else 1
                learning = source["learning"] * factor * multiplier
                forecasts.append(dict(cell=c, learning_seconds=learning,
                                      fixed_query_seconds=source["overhead"]+learning+source["query"],
                                      scaled_query_seconds=source["overhead"]+learning+source["query"]*factor))
            variants.append(dict(credit_iters=k, error_lr=lr, cells=forecasts,
                                 fixed_query_seconds=sum(x["fixed_query_seconds"] for x in forecasts),
                                 scaled_query_seconds=sum(x["scaled_query_seconds"] for x in forecasts)))
    return dict(status="estimated", model_execution=False, profile=str(profile), sources_sha256=refs,
                variants=variants,
                sweep_totals={key: sum(v[key] for v in variants)
                              for key in ("fixed_query_seconds", "scaled_query_seconds")},
                assumptions=[
                    "Each variant repeats both arms on the supplied complete, preselected design; controls are not shared.",
                    "Learning scales with item count; all SE-E learning uses the (k+1) operation proxy, including its fixed overhead.",
                    "Query scenarios keep profile query work fixed or scale it with items; neither is a confidence or safety bound.",
                    "Startup is held fixed; changed memory size, endpoint cadence, convergence and JIT costs are unmodeled.",
                    "Learning rate is assumed cost-neutral; divergence may invalidate this estimate.",
                    "Separate harm readout, new profiling, retries and operator overhead are excluded.",
                    "Cost records retain their historical source hashes; no current-source or execution authorization is implied.",
                ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile")
    parser.add_argument("--design", choices=("development", "v0-12", "v0-60", "v1-4"), default="development")
    parser.add_argument("--error-lrs", type=positive_rate, nargs="+", default=[0.1])
    args = parser.parse_args()
    cells = [dict(dataset=d, realization=r, order=o, arm=a,
                  items=10 if args.design == "development" else 300 if args.design == "v1-4" or d == "counterfact" else 1000)
             for d in ("zsre", "counterfact")
             for r in (range(3) if args.design.startswith("v0") else [0])
             for o in (range(100, 105) if args.design == "v0-60" else [100])
             for a in ("SE-A", "SE-E")]
    print(json.dumps(projected_sweep(args.profile, cells, args.error_lrs), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
