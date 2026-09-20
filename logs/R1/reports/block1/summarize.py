"""Descriptive block-1 tables; retain orders and never construct an interval."""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def stats(values):
    complete = bool(values) and all(v is not None for v in values)
    return dict(values=values, complete=complete, mean=statistics.mean(values) if complete else None,
                minimum=min(values) if complete else None, maximum=max(values) if complete else None,
                sample_sd=statistics.stdev(values) if complete and len(values) > 1 else None)


def csv_write(path, rows):
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def build(report):
    groups = defaultdict(list)
    pointers = {}
    for i, cell in enumerate(report["cells"]):
        if cell["artifact_complete"]:
            if cell["cell"]["realization"] != 0 or cell["block_number"] != 1:
                raise ValueError("later realization entered block-1 summary")
            groups[(cell["cell"]["dataset"], cell["cell"]["condition"])].append(cell)
            pointers[cell["cell_id"]] = f"/cells/{i}"
    rows, per_cell = [], []
    for (dataset, condition), cells in sorted(groups.items()):
        cells.sort(key=lambda c: c["cell"]["order"])
        if [c["cell"]["order"] for c in cells] != [100, 101, 102, 103, 104]:
            raise ValueError("all five paired orders required")
        n = 300 if dataset == "mquake" else 1000
        final = [c["checkpoints"][str(n)] for c in cells]
        row = dict(dataset=dataset, condition=condition, realization=0, checkpoint=n, orders=5,
                   cell_ids=[c["cell_id"] for c in cells], source_pointers=[pointers[c["cell_id"]] for c in cells],
                   primary={k: stats([f["primary"][k]["value"] for f in final]) for k in ("ES", "RET-ES", "RET-GS", "LS")},
                   secondary={k: stats([f["secondary"][k]["value"] for f in final]) for k in (
                       "unseen_false_fire", "near_miss_bounded", "near_miss_terminated", "revision_latest", "revision_semantic", "LS_terminated")},
                   fidelity={}, passes=sum(c["cap_fidelity_benchmark"]["passes"] is True for c in cells))
        for reference in ("capoff", "original"):
            f = [x["secondary"]["full_validation"] for x in final]
            row["fidelity"][reference] = dict(
                mean_kl=stats([x["references"][reference]["kl"]["mean_signed"] for x in f]),
                mean_signed_nll=stats([x["references"][reference]["loss"]["mean_signed"] for x in f]),
                maximum_positive_nll=stats([x["references"][reference]["loss"]["maximum_positive"] for x in f]),
                es95_positive_nll=stats([x["references"][reference]["loss"]["ES95_positive"] for x in f]),
                half_kl_positions=stats([x["concentration"]["references"][reference]["kl_positions"]["minimum_count_for_half_mass"] for x in f]),
                near_zero_loss_fraction=stats([x["concentration"]["references"][reference]["near_zero_loss_change"]["fraction"] for x in f]))
        rows.append(row)
        for cell, f in zip(cells, final, strict=True):
            per_cell.append(dict(cell_id=cell["cell_id"], **cell["cell"], checkpoint=n,
                                 source_pointer=pointers[cell["cell_id"]], primary=f["primary"],
                                 secondary={k: v for k, v in f["secondary"].items() if k != "full_validation"},
                                 full_validation=f["secondary"]["full_validation"],
                                 cap_fidelity_benchmark=cell["cap_fidelity_benchmark"]))
    primary = []
    for i, contrast in enumerate(report["contrasts"]):
        if contrast["classification"] != "unavailable":
            raise ValueError("classifier available without three realizations")
        for metric, data in contrast["metrics"].items():
            if data["adjusted_interval"] is not None or data["unadjusted_interval"] is not None:
                raise ValueError("interval available in one-realization snapshot")
            dispersion = data["preliminary"]["order_dispersion"][0]
            primary.append(dict(dataset=contrast["dataset"], contrast=contrast["contrast"]["id"], metric=metric,
                                checkpoint=1000, realization=0, **{k: v for k, v in dispersion.items() if k != "realization"},
                                classifier=None, interval=None,
                                role="realization_0_descriptive_only",
                                source_pointer=f"/contrasts/{i}/metrics/{metric}/preliminary/order_dispersion/0"))
    return dict(groups=rows, per_cell=per_cell, primary_realization0=primary,
                inference="Five orders share one realization. Min/max/SD describe order dispersion only; no confidence intervals or classifier.")


def main():
    result = build(json.loads((HERE / "analysis.json").read_text()))
    with (HERE / "summary.json").open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    csv_write(HERE / "primary-realization0.csv", result["primary_realization0"])
    csv_write(HERE / "group-summary.csv", result["groups"])
    print(json.dumps(dict(groups=len(result["groups"]), per_cell=len(result["per_cell"]), primary_rows=len(result["primary_realization0"]))))


if __name__ == "__main__":
    main()
