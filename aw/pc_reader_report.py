"""PC-16: CPU summary of all planned BP/ePC reader seeds, including missing cells."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from aw import reader_results as rr
from aw.reader_interpretation import narrative

DEFAULT_TAIL = rr.ROOT / "logs/additional_work/HT-17/snapshot-20261002-seed1/report.json"
DEFAULT_HISTORY = rr.ROOT / "logs/additional_work/PC-v1/report-4-20260927/report.json"


def build(root, *, tail=None, history=None, positions=245237):
    root, sources = Path(root), {}
    trainings, cells, pairs, spreads = [], [], [], []
    for rule in ("bp", "epc"):
        for seed in range(3):
            tr = rr.training(root / f"train-{rule}-s{seed}", sources)
            if tr["status"] == "complete" and (
                tr["rule"] != rule or tr["seed"] != seed or tr["profile_only"]
            ):
                raise ValueError("training folder/coordinate mismatch")
            trainings.append(dict(tr, planned_rule=rule, planned_seed=seed))
            for ds in rr.DATASETS:
                row = rr.admitted(root / f"eval-{rule}-s{seed}-{ds}", sources, positions=positions)
                if row["status"] == "complete" and (
                    row["rule"],
                    row["seed"],
                    row["dataset"],
                    row["read_taps"],
                    row["write_sites"],
                ) != (rule, seed, ds, [1, 2, 3], [1, 2, 3]):
                    row = dict(
                        path=row["path"], status="invalid", reason="planned coordinate mismatch"
                    )
                cells.append(dict(row, planned_rule=rule, planned_seed=seed, planned_dataset=ds))

    def find(rule, seed, ds):
        return next(
            c
            for c in cells
            if (c["planned_rule"], c["planned_seed"], c["planned_dataset"]) == (rule, seed, ds)
        )

    for ds in rr.DATASETS:
        for seed in range(3):
            a, b = find("bp", seed, ds), find("epc", seed, ds)
            difference = rr.paired(a, b)
            if difference is not None:
                for field in ("initial_reader_sha256", "recipe", "selected_steps"):
                    if a["training"][field] != b["training"][field]:
                        raise ValueError("BP/ePC training pairing mismatch: " + field)
            pairs.append(
                dict(
                    dataset=ds,
                    seed=seed,
                    status="paired" if difference else "missing pair",
                    difference_bp_minus_epc=difference,
                )
            )
        for rule in ("bp", "epc"):
            selected = [find(rule, seed, ds) for seed in range(3)]
            spreads.append(
                dict(
                    dataset=ds,
                    rule=rule,
                    planned=3,
                    metrics={
                        k: rr.spread(rr.values(c)[k] for c in selected if c["status"] == "complete")
                        for k in (*rr.METRICS, *rr.HARM, "fired")
                    },
                )
            )
    pair_spreads = [
        dict(
            dataset=ds,
            planned=3,
            metrics={
                k: rr.spread(
                    p["difference_bp_minus_epc"][k]
                    for p in pairs
                    if p["dataset"] == ds and p["status"] == "paired"
                )
                for k in (*rr.METRICS, *rr.HARM, "fired")
            },
        )
        for ds in rr.DATASETS
    ]
    cost_ratios = []
    for seed in range(3):
        a, b = [
            next(t for t in trainings if t["planned_rule"] == rule and t["planned_seed"] == seed)
            for rule in ("bp", "epc")
        ]
        cost_ratios.append(
            dict(
                seed=seed,
                epc_over_bp=(
                    b["cost"]["seconds"] / a["cost"]["seconds"]
                    if a["status"] == b["status"] == "complete" and a["cost"]["seconds"] > 0
                    else None
                ),
            )
        )
    tail_rows, tail_missing = [], []
    if tail is not None:
        t = rr.read(tail, sources)
        candidates = {
            (c["condition"], c["seed"], c["dataset"]): c
            for c in t["cells"]
            if c["phase"] == "PC-reader"
        }
        for c in cells:
            if c["status"] != "complete":
                continue
            key = c["rule"], c["seed"], c["dataset"]
            r = candidates.get(key)
            if r is None or r["vector"] != c["vector"]:
                tail_missing.append(key)
                continue
            tail_rows.append(
                dict(
                    rule=c["rule"],
                    seed=c["seed"],
                    dataset=c["dataset"],
                    id=r["id"],
                    statistics=r["statistics"],
                )
            )
    historical = []
    if history is not None:
        h = rr.read(history, sources)
        harm = rr.read(h["harm"]["report"], sources)
        for c in h["cells"]:
            if c["arm"] == "SE-A":
                hc = next(
                    x for x in harm["cells"] if x["dataset"] == c["dataset"] and x["arm"] == "SE-A"
                )
                historical.append(
                    dict(
                        dataset=c["dataset"],
                        realization=c["realization"],
                        order=c["order"],
                        metrics=c["checkpoints"]["300"],
                        harm=hc["readout"]["summary"]["capoff"],
                        label="selected original v5, historical same-stream reference, not another training seed",
                    )
                )
    receipts = [rr.cost(p.parent, sources) for p in sorted(root.glob("*/cost.json"))]
    known = [r["seconds"] for r in receipts if r["seconds"] is not None]
    sources[str(rr.ROOT / "aw/reader_interpretation.py")] = rr.sha(
        rr.ROOT / "aw/reader_interpretation.py"
    )
    sources[str(Path(__file__).resolve())] = rr.sha(Path(__file__))
    sources[str(Path(rr.__file__).resolve())] = rr.sha(Path(rr.__file__))
    return dict(
        task="PC-16",
        status="complete" if all(c["status"] == "complete" for c in cells) else "partial",
        planned_trainings=6,
        planned_evaluations=12,
        completed_evaluations=sum(c["status"] == "complete" for c in cells),
        trainings=trainings,
        cells=cells,
        paired_differences=pairs,
        seed_spreads=spreads,
        paired_seed_spreads=pair_spreads,
        training_cost_ratios=cost_ratios,
        cost_inventory=receipts,
        known_process_seconds=sum(known),
        uncosted_directories=[
            str(p) for p in sorted(root.iterdir()) if p.is_dir() and not (p / "cost.json").exists()
        ],
        historical_reference=historical,
        tail_source=str(tail) if tail else None,
        tail_rows=tail_rows,
        tail_stale_or_missing=tail_missing,
        sources_sha256=sources,
        model_calls=0,
        gpu_seconds=0,
    )


def markdown(r, output):
    text = f"""# PC-trained reader — {r["status"]} report

Capex · generated from saved artifacts · {r["completed_evaluations"]}/12 completed evaluations, six planned trainings.
Machine-readable source and input hashes: `{output}/report.json`.

This changes **reader/controller training** (BP versus ePC); acquisition uses adjoint in every arm. Same exposed realization 0, order 100, first 300 edits on each dataset. Three paired training seeds are not three subject realizations. Missing/failed cells remain visible. No superiority claim or new decision threshold is assigned.

{narrative(r)}

## Training and measured costs

The earlier **37×** ratio in lead-queue item 144 was a ten-update profile projection (about 37 minutes BP versus 22.6 hours ePC), not completed-run timing. Actual whole-training ratios below supersede it for measured cost. Components are not added to their parent receipts. Profiles, failed attempts and completed runs remain in the JSON cost inventory; unclosed runs have unknown cost, not zero. Process-hours do not imply elapsed portfolio hours.

"""
    text += rr.table(
        ["Rule", "Seed", "Status", "Steps", "Parameters", "Process seconds", "Hours"],
        [
            [
                t["planned_rule"],
                t["planned_seed"],
                t["status"],
                t.get("steps"),
                t.get("parameter_count"),
                t["cost"]["seconds"],
                t["cost"]["seconds"] / 3600 if t["cost"]["seconds"] is not None else None,
            ]
            for t in r["trainings"]
        ],
    )
    text += rr.table(
        ["Paired seed", "Measured ePC/BP training time"],
        [[x["seed"], x["epc_over_bp"]] for x in r["training_cost_ratios"]],
    )
    text += f"All known top-level process receipts (including profiles): {r['known_process_seconds'] / 3600:.4f} hours; {len(r['uncosted_directories'])} directories have no terminal cost yet.\n\n"
    text += rr.tables(
        r["cells"], lambda c: f"{c['planned_rule']} s{c['planned_seed']} {c['planned_dataset']}"
    )
    text += "## Paired BP minus ePC, by seed\n\nPositive behavior differences favor BP; positive harm differences mean BP has more loss. These are differences of each arm's ES99, not the ES99 of pointwise differences.\n\n"
    text += rr.table(
        ["Dataset", "Seed", "Status", *rr.METRICS, *rr.HARM, "Fired"],
        [
            [
                p["dataset"],
                p["seed"],
                p["status"],
                *[
                    (p["difference_bp_minus_epc"] or {}).get(k)
                    for k in (*rr.METRICS, *rr.HARM, "fired")
                ],
            ]
            for p in r["paired_differences"]
        ],
    )
    text += "## Training-seed spread (descriptive)\n\nSample SD is undefined for one seed; ranges are not confidence intervals. Paired seed spread is in the JSON.\n\n"
    text += rr.table(
        ["Dataset", "Rule", "Metric", "Seeds / 3", "Mean", "Min", "Max", "Sample SD"],
        [
            [
                s["dataset"],
                s["rule"],
                k,
                v["n"],
                v["mean"],
                v["minimum"],
                v["maximum"],
                v["sample_sd"],
            ]
            for s in r["seed_spreads"]
            for k, v in s["metrics"].items()
        ],
    )
    text += "## Historical selected v5 reference\n\nSame exposed streams and adjoint acquisition; the previously selected artifact is not a new paired seed or an unbiased sample of training outcomes. Selection and recipe history differ. Its values do not establish causal superiority over these newly trained readers. The underlying fixed-v5 report includes the independently repaired harm completion record.\n\n"
    text += rr.table(
        ["Dataset", *rr.METRICS, "Mean KL", "ES99+", "Max ΔNLL"],
        [
            [
                c["dataset"],
                *[c["metrics"][k]["value"] for k in rr.METRICS],
                c["harm"]["kl"]["mean_signed"],
                c["harm"]["loss"]["es99_positive"],
                c["harm"]["loss"]["maximum_positive"],
            ]
            for c in r["historical_reference"]
        ],
    )
    text += f"## HT-17 reader rows\n\nSource: `{r['tail_source']}`. Rows below match the exact saved vector hashes. {len(r['tail_stale_or_missing'])} completed reader rows lack a matching tail refresh. Training seeds and repeated ordinary-text positions do not become independent subject samples. Conditional severity is undefined when no position exceeds the threshold.\n\n"
    text += rr.table(
        ["Rule", "Seed", "Dataset", "Frequency Δ>.01", "Conditional severity", "Fit status"],
        [
            [
                c["rule"],
                c["seed"],
                c["dataset"],
                c["statistics"]["thresholds"]["0.01"]["fraction"],
                c["statistics"]["thresholds"]["0.01"]["conditional_mean_loss"],
                c["statistics"]["thresholds"]["0.01"]["fit"]["status"],
            ]
            for c in r["tail_rows"]
        ],
    )
    text += f"""The full [HT-17 report](HT-17_report.md) retains threshold checks, joint-window intervals and invalid fits. This snapshot matches {len(r["tail_rows"])} of {r["completed_evaluations"]} completed reader evaluations; any exceptions are listed above. Rerun into a **new** directory when remaining seeds finish:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \\
../venv/bin/python -m aw.pc_reader_report \\
  --refresh-tail logs/additional_work/HT-17/reader-complete-NEW \\
  --output logs/additional_work/PC-reader/report-NEW
```

This runs the CPU HT-17 refresh (200 joint-window draws, secondary conditions included), then reads its newly matched reader rows and refreshes this document. The figure refresh command is in HT-17_report.md. No model is loaded and no GPU work is scheduled. Experimental cutoff remains October 9 at 17:00 EDT.
"""
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=rr.ROOT / "results/additional_work/PC-reader")
    p.add_argument("--tail", type=Path, default=DEFAULT_TAIL)
    p.add_argument("--refresh-tail", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--document", type=Path, default=rr.ROOT / "docs/additional_work/PC-reader_report.md"
    )
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError("new report output directory required")
    if a.refresh_tail:
        if a.refresh_tail.exists():
            raise FileExistsError("new tail output directory required")
        env = dict(
            os.environ,
            JAX_PLATFORMS="cpu",
            CUDA_VISIBLE_DEVICES="",
            OPENBLAS_NUM_THREADS="1",
            OMP_NUM_THREADS="1",
            PYTHONDONTWRITEBYTECODE="1",
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "aw.tail_class",
                "--output",
                str(a.refresh_tail),
                "--bootstrap",
                "200",
                "--secondary",
            ],
            cwd=rr.ROOT,
            env=env,
            check=True,
        )
        a.tail = a.refresh_tail / "report.json"
    r = build(a.root, tail=a.tail, history=DEFAULT_HISTORY)
    rr.write_outputs(r, markdown(r, a.output), a.output, a.document)
    print(
        json.dumps({k: r[k] for k in ("status", "completed_evaluations", "tail_stale_or_missing")})
    )


if __name__ == "__main__":
    main()
