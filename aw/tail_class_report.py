"""HT-17 snapshot and descriptive report; no writes to experimental results."""

from __future__ import annotations

import csv
import json
import resource
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import scipy

from aw.tail_class import SEED, THRESHOLDS, analyze, dump, interval, window_plan
from aw.tail_class_sources import ROOT, inventory, load_delta, sha


def group_summary(entries, weights):
    """Uniform cell then uniform position estimand; paired window draws throughout."""
    cells = [e[0] for e in entries]
    nc, nw = len(cells), cells[0]["windows"]
    out = dict(cells=nc, windows=nw, thresholds={})
    for u in map(str, THRESHOLDS):
        counts = sum(e[1][u]["counts"] for e in entries)
        sums = sum(e[1][u]["sums"] for e in entries)
        bc, bs = weights @ counts, weights @ sums
        severity = np.divide(bs, bc, out=np.full(len(bs), np.nan), where=bc > 0)
        rows = [c["statistics"]["thresholds"][u] for c in cells]
        fits = [r["fit"] for r in rows if r["fit"]["status"] == "eligible"]
        cv = [r["cross_validation"]["gpd_minus_exponential_per_excess"] for r in rows
              if "cross_validation" in r]
        cv = [v for v in cv if v is not None]
        out["thresholds"][u] = dict(
            frequency=float(counts.sum() / (nc * nw * 127)),
            conditional_mean_loss=float(sums.sum() / counts.sum()) if counts.sum() else None,
            frequency_interval=interval(bc / (nc * nw * 127)),
            conditional_mean_interval=interval(severity) if np.all(bc > 0) else None,
            empty_bootstrap_draws=int((bc == 0).sum()),
            frequency_draws=(bc / (nc * nw * 127)).tolist(),
            conditional_mean_draws=[float(v) if np.isfinite(v) else None for v in severity],
            excess_count_range=[min(r["count"] for r in rows), max(r["count"] for r in rows)],
            window_count_range=[min(r["contributing_windows"] for r in rows),
                                max(r["contributing_windows"] for r in rows)],
            fit_status_counts=dict(Counter(r["fit"]["status"] for r in rows)),
            invalid_reasons=dict(Counter(r["fit"].get("reason") for r in rows
                                        if r["fit"]["status"] == "invalid")),
            eligible_shape_range=[min(f["shape"] for f in fits), max(f["shape"] for f in fits)]
            if fits else None,
            eligible_scale_range=[min(f["scale"] for f in fits), max(f["scale"] for f in fits)]
            if fits else None,
            predictive_difference_range=[min(cv), max(cv)] if cv else None,
            comparable_predictive_cells=len(cv),
        )
    out["mean_es99_positive"] = float(np.mean([c["statistics"]["es99_positive"] for c in cells]))
    out["maximum_range"] = [min(c["statistics"]["maximum"] for c in cells),
                            max(c["statistics"]["maximum"] for c in cells)]
    out["mean_ret_gs"] = float(np.mean([c["efficacy"]["RET-GS"] for c in cells]))
    gates = [c["gate"]["selected"] / c["statistics"]["positions"] for c in cells if c["gate"]]
    out["mean_gate_selected_fraction"] = float(np.mean(gates)) if len(gates) == nc else None
    out["individual_factors"] = [dict(realization=c["realization"], order=c["order"], seed=c["seed"],
                                       id=c["id"]) for c in cells]
    return out


def matched_contrasts(groups, plans):
    result = []
    for phase, left, right in (("stage4", "R1_learned_ff", "R1_nonlearned"),
                               ("stage4", "R1_learned_ff", "v0_stable"),
                               ("AW-B", "mixture:0.367879", "v5"),
                               ("PC-reader", "epc", "bp")):
        for ds in ("zsre", "counterfact"):
            a, b = groups.get((phase, ds, left), []), groups.get((phase, ds, right), [])
            def coord(e):
                return tuple(e[0][k] for k in ("realization", "order", "seed"))

            aa, bb = {coord(e): e for e in a}, {coord(e): e for e in b}
            common = sorted(aa.keys() & bb.keys(), key=str)
            if not common:
                continue
            pops = {e[0]["population"] for e in [*a, *b]}
            if len(pops) != 1:
                raise ValueError("paired contrast has unequal window identities")
            w = plans[next(iter(pops))][0]
            ag = group_summary([aa[k] for k in common], w)
            bg = group_summary([bb[k] for k in common], w)
            contrasts = {}
            for u in map(str, THRESHOLDS):
                at, bt = ag["thresholds"][u], bg["thresholds"][u]
                row = {}
                for metric, draws in (("frequency", "frequency_draws"),
                                      ("conditional_mean_loss", "conditional_mean_draws")):
                    x, y = np.asarray(at[draws], float), np.asarray(bt[draws], float)
                    row[metric] = dict(
                        difference=at[metric] - bt[metric] if at[metric] is not None
                        and bt[metric] is not None else None,
                        paired_window_interval=interval(x - y)
                        if np.isfinite(x - y).all() else None,
                        undefined_draws=int((~np.isfinite(x - y)).sum()),
                    )
                contrasts[u] = row
            result.append(dict(phase=phase, dataset=ds, left=left, right=right,
                               paired_cells=len(common), coordinates=common, thresholds=contrasts))
    return result


def fmt(x):
    if x is None:
        return "—"
    if isinstance(x, (list, tuple)):
        return " to ".join(fmt(v) for v in x)
    return f"{x:.5g}" if isinstance(x, float) else str(x)


def render(report):
    lines = [
        "# HT-17 — saved harm: frequency, severity, and finite-range fits", "",
        f"Capex · snapshot {report['created_utc']} · {len(report['cells'])} completed cells. "
        "CPU analysis; zero GPU seconds. Exploratory analysis of exposed results.", "",
        f"Coverage: `{report['coverage']}`. Pending reader evaluations: "
        f"{len(report['pending_reader_cells'])}. The pending cells are not zeros, and this is not "
        "the final three-seed PC reader comparison.", "",
        "Δ is signed cap NLL minus own cap-off NLL at the identical prefix, in nats. "
        "Exact zeros, nonzero changes within ±1e-9, benefits, and positive changes remain distinct "
        "in the cell JSON. Gate selection is separate telemetry, unavailable for the Stage-4 "
        "full-position assay and legacy pilot. No positive-loss count is called a firing count. "
        "AW-B cap-off telemetry describes the underlying selector, not an applied correction.", "",
        "The full assay has 1,931 windows × 127 targets = 245,237 positions per cell. "
        "The pilot has 32 × 127 = 4,064 positions and is never joined to it. "
        "The legacy files lack token hashes; their ordered cap-off matrices match exactly. "
        "Pilot MQuAKE retention and drift use different historical populations, so they are "
        "reported alongside each other rather than treated as one joint endpoint population.", "",
        "Frequency means uniform selection of a cell, then a scored position; conditional severity "
        "is mean Δ given Δ > u under that same mixture. Group severity is not an equal-weight "
        "average of the per-cell conditional means. ES99+ is the mean of cell-level fractional "
        "worst-1% positive-part losses, retaining zeros. Maxima are per-cell ranges.", "",
        "## Primary threshold: u = 0.01 nat", "",
        f"Brackets are 95% percentile intervals from {report['bootstrap_draws']} joint window-identity draws, conditional "
        "on these fixed cells. Windows may share documents or neighboring text: their independence "
        "is unverified. These are not subject-realization or training-seed confidence intervals. "
        "Pilot intervals use only 32 windows and deserve particular caution. If any resample "
        "has no excesses, its severity is undefined and the severity interval is withheld; "
        "the count of such draws remains in the JSON.", "",
        "| Study | Dataset | Condition | Cells | P(Δ>.01) [interval] | Mean Δ given >.01 [interval] "
        "| Gate-selected fraction | ES99+ | Max range | RET-GS |",
        "|---|---|---|---:|---|---|---:|---:|---|---:|",
    ]
    for g in report["groups"]:
        t = g["thresholds"]["0.01"]
        values = [g["phase"], g["dataset"], g["condition"], g["cells"],
                  f"{fmt(t['frequency'])} [{fmt(t['frequency_interval'])}]",
                  f"{fmt(t['conditional_mean_loss'])} [{fmt(t['conditional_mean_interval'])}]",
                  fmt(g["mean_gate_selected_fraction"]), fmt(g["mean_es99_positive"]),
                  fmt(g["maximum_range"]), fmt(g["mean_ret_gs"])]
        lines.append("| " + " | ".join(map(str, values)) + " |")
    lines += ["", "## Fit eligibility and threshold sensitivity", "",
              "Fit Y = Δ−u conditional on Δ>u, location zero. Fewer than 100 excesses or 30 "
              "contributing windows means **not identified**. Numerical optimization uses two "
              "starts; convergence is recorded, not a proof of a unique/global likelihood maximum. "
              "Shape ≤−1 is flagged for endpoint likelihood pathology; shape ≤−1/2 is invalid "
              "for this protocol's manuscript-domain mapping (not a claim that every such GPD "
              "is mathematically undefined). Diagnostic optimizer output is retained separately.", "",
              "The table gives ranges of eligible **per-cell** estimates, not pooled fits or "
              "confidence intervals. Invalid and screened cells remain in the denominator. "
              "Primary-threshold shape/scale intervals are in the cell JSON; an interval is "
              "withheld if any bootstrap draw is invalid, rather than silently conditioning "
              "on successful fits. Thresholds were chosen after seeing preliminary results.", "",
              "| Study | Dataset | Condition | u | Excesses/cell | Windows/cell | Eligible / all "
              "| Shape range | Excess-scale range | CV ΔlogL/excess range (GPD−exp; comparable cells) |",
              "|---|---|---|---:|---|---|---|---|---|---|"]
    for g in report["groups"]:
        for u, t in g["thresholds"].items():
            vals = [g["phase"], g["dataset"], g["condition"], u,
                    fmt(t["excess_count_range"]), fmt(t["window_count_range"]),
                    f"{t['fit_status_counts'].get('eligible', 0)} / {g['cells']}",
                    fmt(t["eligible_shape_range"]), fmt(t["eligible_scale_range"]),
                    f"{fmt(t['predictive_difference_range'])} ({t['comparable_predictive_cells']}/{g['cells']})"]
            lines.append("| " + " | ".join(vals) + " |")
    lines += ["", "Five fixed folds split whole window identities, shared across all cells. "
              "Predictive scores use all held-out excesses. A model giving zero density to any "
              "held-out observation has its score marked unavailable/zero predictive density, "
              "not evaluated after discarding that observation. A fit failing the eligibility "
              "rule in any training fold is also marked. No token-iid p-values are used.", "",
              "An auxiliary conditional lognormal is evaluated only when both models have invalid "
              "held-out predictions or descriptive held-out PIT discrepancies >0.10. This is an "
              "explicit exploratory plotting/diagnostic trigger, not a significance test or a "
              "selection rule. Its likelihood is normalized above u in the original loss coordinate. "
              "All model/fold records are in `report.json`; none of these fits tune the cap.", "",
              "## Matched contrasts at u = 0.01", "",
              "These comparisons intersect realization/order/seed coordinates before forming "
              "differences and reuse the same window draws on both sides. Efficacy, occupancy, "
              "and training costs must still accompany a robustness interpretation.", "",
              "| Study | Dataset | Left − right | Paired cells | Frequency difference [interval] "
              "| Conditional-severity difference [interval] |",
              "|---|---|---|---:|---|---|"]
    for r in report["contrasts"]:
        t = r["thresholds"]["0.01"]
        values = [r["phase"], r["dataset"], r["left"] + " − " + r["right"], r["paired_cells"]]
        values += [f"{fmt(t[m]['difference'])} [{fmt(t[m]['paired_window_interval'])}]"
                   for m in ("frequency", "conditional_mean_loss")]
        lines.append("| " + " | ".join(map(str, values)) + " |")
    lines += ["", "## Between-realization and seed variation", "",
              "The JSON's `factor_summaries` separates each Stage-4 realization and each reader "
              "training seed. `cells.csv` preserves every stream order. These variations are "
              "not reduced by treating reused text as new observations. No cross-cell fitted "
              "shape is used to assign a complexity class.", "",
              "AW-B's one-nat upper bound is established analytically at matched prefixes; "
              "a failed GPD fit does not weaken that bound. Zero observed harm does not establish "
              "zero future risk. A fitted positive shape does not establish an asymptotic law, "
              "infinite variance, system temperature, or the growth of microstates W(N).", "",
              "Reproduce with the command in `report.json` and the bound source hashes in "
              "`sources.json`. Only completed output artifacts are admitted. Figures are produced "
              "separately from this JSON with `python3 -m aw.tail_class_plot --report ... --out ...`.", ""]
    return "\n".join(lines)


def build(args):
    started = time.monotonic()
    args.output.mkdir(parents=True, exist_ok=False)
    cells, meta = inventory(args.secondary)
    print(f"Admitted {len(cells)} cells; {len(meta['pending_reader_cells'])} reader cells pending", flush=True)
    if args.limit:
        # One deterministic member of each phase/dataset/condition before additional orders.
        by = defaultdict(list)
        for c in cells:
            by[(c["phase"], c["dataset"], c["condition"])].append(c)
        priority = {"stage4": 0, "AW-B": 1, "PC-reader": 2, "kappa-pilot": 3}
        cells = [by[k][0] for k in sorted(by, key=lambda k: (priority[k[0]], k))][:args.limit]
    plans, groups, entries, analyzed = {}, defaultdict(list), [], []
    for i, cell in enumerate(cells):
        begin = time.monotonic()
        d = load_delta(cell, meta["sources_sha256"])
        pop = cell["population"]
        if pop not in plans:
            plans[pop] = window_plan(cell["windows"], args.bootstrap)
        w, folds = plans[pop]
        stat, ws = analyze(d, weights=w, folds=folds,
                           bootstrap_fits=not args.no_shape_bootstrap)
        cell["statistics"] = stat
        entry = (cell, ws)
        entries.append(entry)
        groups[tuple(cell[k] for k in ("phase", "dataset", "condition"))].append(entry)
        analyzed.append(cell)
        record = dict(index=i, cell=cell["id"], seconds=time.monotonic() - begin,
                      fit_statuses={u: r["fit"]["status"] for u, r in stat["thresholds"].items()})
        with (args.output / "progress.jsonl").open("a") as f:
            f.write(json.dumps(record) + "\n")
        if i % 10 == 0:
            print(f"Analyzed {i + 1}/{len(cells)}: {cell['id']}", flush=True)
    summary = []
    for key, group in sorted(groups.items()):
        summary.append(dict(zip(("phase", "dataset", "condition"), key, strict=True))
                       | group_summary(group, plans[group[0][0]["population"]][0]))
    factors = []
    for key, group in sorted(groups.items()):
        which = "realization" if key[0] == "stage4" else "seed"
        if key[0] not in ("stage4", "PC-reader", "kappa-pilot"):
            continue
        for value in sorted({e[0][which] for e in group}):
            subset = [e for e in group if e[0][which] == value]
            factors.append(dict(phase=key[0], dataset=key[1], condition=key[2],
                                factor=which, level=value,
                                **group_summary(subset, plans[group[0][0]["population"]][0])))
    result = dict(
        task="HT-17", schema=1, created_utc=datetime.now(timezone.utc).isoformat(),
        gpu_seconds=0, bootstrap_draws=args.bootstrap, seed=SEED,
        bootstrap_shape_threshold=0.01, partial_profile=bool(args.limit),
        coverage=dict(Counter(c["phase"] for c in cells)),
        pending_reader_cells=meta["pending_reader_cells"],
        cells=analyzed, groups=summary, factor_summaries=factors,
        contrasts=matched_contrasts(groups, plans),
        versions=dict(numpy=np.__version__, scipy=scipy.__version__),
        code_sha256={str(p.relative_to(ROOT)): sha(p) for p in (
            ROOT / "aw/tail_class.py", ROOT / "aw/tail_class_sources.py",
            ROOT / "aw/tail_class_report.py")},
        command=f"JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 "
                f"../venv/bin/python -m aw.tail_class --output {args.output} "
                f"--bootstrap {args.bootstrap}" + (" --secondary" if args.secondary else "")
                + (f" --limit {args.limit}" if args.limit else "")
                + (" --no-shape-bootstrap" if args.no_shape_bootstrap else ""),
    )
    for path, digest in meta["sources_sha256"].items():
        if path.endswith(".json") and sha(path) != digest:
            raise ValueError(f"input changed during analysis: {path}")
    result["wall_seconds"] = time.monotonic() - started
    result["peak_host_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    dump(args.output / "sources.json", meta)
    result["source_inventory_sha256"] = sha(args.output / "sources.json")
    dump(args.output / "report.json", result)
    (args.output / "report.md").write_text(render(result))
    with (args.output / "cells.csv").open("w") as f:
        names = ("id", "phase", "dataset", "condition", "realization", "order", "seed", "u",
                 "count", "contributing_windows", "fraction", "conditional_mean_loss",
                 "fit_status", "shape", "scale", "reason", "ret_gs", "es99_positive", "maximum")
        writer = csv.DictWriter(f, fieldnames=names)
        writer.writeheader()
        for c in analyzed:
            for u, t in c["statistics"]["thresholds"].items():
                row = {k: c[k] for k in names[:7]}
                row.update({k: t[k] for k in names[8:12]})
                row.update(u=u, fit_status=t["fit"]["status"],
                           shape=t["fit"].get("shape"), scale=t["fit"].get("scale"),
                           reason=t["fit"].get("reason"), ret_gs=c["efficacy"]["RET-GS"],
                           es99_positive=c["statistics"]["es99_positive"],
                           maximum=c["statistics"]["maximum"])
                writer.writerow(row)
    return result
