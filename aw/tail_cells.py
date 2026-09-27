"""HT-15: CPU-only cell tails and realization spread from completed receipts.

No model calls, token-based intervals, or pooling across cells. A frozen list of
queue finishes bounds each snapshot; later arrivals belong to the next refresh.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from aw.pc_v0_report import ROOT, read, sha, verify
from aw.tail_figures import expected_shortfall
from pccap.revision_v1.analysis import digest

FIELDS = ["loss_cap", "loss_capoff", "loss_original", "kl_capoff_to_cap", "kl_original_to_cap"]
METRICS = (
    "mean_signed",
    "es99_positive",
    "maximum",
    "exceed_0.01",
    "exceed_1",
    "exceed_5",
    "half_mass_positions",
)


def statistics(delta):
    d = np.asarray(delta, np.float64)
    if d.ndim != 2 or not d.size or not np.isfinite(d).all():
        raise ValueError("finite, nonempty window-by-target array required")
    flat = d.ravel()
    pos = np.maximum(flat, 0)
    ordered = np.sort(pos)[::-1]
    total = float(ordered.sum())
    half = int(np.searchsorted(np.cumsum(ordered), total / 2) + 1) if total > 0 else None
    idx = int(np.argmax(flat))
    window, column = divmod(idx, d.shape[1])
    result = dict(
        positions=int(flat.size),
        mean_signed=float(flat.mean()),
        es99_positive=expected_shortfall(pos, 0.99),
        maximum=float(flat[idx]),
        maximum_location=dict(
            flat_index=idx,
            window_index=window,
            target_column=column,
            target_token_offset=column + 1,
        ),
        maximum_ties=int(np.count_nonzero(flat == flat[idx])),
        half_mass_positions=half,
        half_mass_fraction=half / flat.size if half is not None else None,
        positive_mass=total,
    )
    for threshold in (0.01, 1, 5):
        key = f"exceed_{threshold:g}"
        result[key + "_count"] = int(np.count_nonzero(flat > threshold))
        result[key] = result[key + "_count"] / flat.size
    return result


def means(rows):
    # A mean concentration is undefined if any contributing cell has zero
    # positive mass. Never average just the nonzero cells without saying so.
    return {
        k: float(np.mean([r[k] for r in rows]))
        if rows and all(r[k] is not None for r in rows)
        else None
        for k in METRICS
    }


def summarize(rows):
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        coord = tuple(row[k] for k in ("condition", "dataset", "realization", "order"))
        if (
            coord in seen
            or row["realization"] not in range(3)
            or row["order"] not in range(100, 105)
        ):
            raise ValueError("duplicate or unexpected cell coordinate")
        seen.add(coord)
        groups[coord[:2]].append(row)
    out = {}
    for key, cells in sorted(groups.items()):
        realizations = []
        for r in range(3):
            selected = [x for x in cells if x["realization"] == r]
            realizations.append(
                dict(
                    realization=r,
                    cells=len(selected),
                    expected_cells=5,
                    complete=len(selected) == 5,
                    means=means(selected),
                )
            )
        complete = all(r["complete"] for r in realizations)
        ranges = {}
        for metric in METRICS:
            values = [r["means"][metric] for r in realizations]
            ranges[metric] = (
                [min(values), max(values)]
                if complete and all(v is not None for v in values)
                else None
            )
        out["|".join(key)] = dict(
            condition=key[0],
            dataset=key[1],
            cells=len(cells),
            expected_cells=15,
            complete=complete,
            observed_cell_means=means(cells),
            realization_means=realizations,
            full_realization_range=ranges,
            zero_positive_mass_cells=sum(x["positive_mass"] == 0 for x in cells),
        )
    return out


def load_cells(receipt_root, *, required_positions=245237):
    bindings, rows, excluded, seen = {}, [], [], {}
    population = None
    finishes = sorted(Path(receipt_root).glob("*/finish.json"))
    if not finishes:
        raise ValueError("no finish receipts; never fall back to unreceipted files")
    for finish_path in finishes:
        finish = read(finish_path, bindings)
        if (
            finish.get("status") != "process_exited"
            or finish.get("exit_code") != 0
            or finish.get("failure_class")
            or finish.get("exception")
        ):
            excluded.append(dict(path=str(finish_path), reason="unsuccessful finish"))
            continue
        recipe_binding = finish["recipe"]
        verify(recipe_binding["path"], recipe_binding["sha256"], bindings)
        recipe = read(recipe_binding["path"], bindings)
        final = max(recipe["checkpoints"])
        spec = recipe["full_validation"]
        for attempt_name in finish["new_attempts"]:
            attempt = Path(attempt_name)
            result = read(attempt / "result.json", bindings)
            if result.get("status") != "complete" or result.get("completed_checkpoint") != final:
                excluded.append(dict(path=str(attempt), reason="not a complete final endpoint"))
                continue
            if (
                result["cell"] != recipe["cell"]
                or result["manifest_sha256"] != recipe_binding["sha256"]
            ):
                raise ValueError("result/recipe mismatch")
            receipt = read(attempt / f"checkpoint-{final}.receipt.json", bindings)
            if (
                receipt["receipt_sha256"]
                != digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
                or receipt["receipt_sha256"] != result["last_receipt_sha256"]
            ):
                raise ValueError("final receipt mismatch")
            if (
                receipt["manifest_sha256"] != recipe_binding["sha256"]
                or receipt["checkpoint"] != final
            ):
                raise ValueError("receipt/recipe mismatch")
            report_path = attempt / f"checkpoint-{final}.json"
            if Path(receipt["report"]["path"]).resolve() != report_path.resolve():
                raise ValueError("receipt points to another checkpoint")
            verify(report_path, receipt["report"]["sha256"], bindings)
            checkpoint = read(report_path, bindings)
            fv = checkpoint["endpoints"]["full_validation"]
            if (
                fv["status"] != "complete"
                or fv["checkpoint"] != final
                or fv["manifest_sha256"] != recipe_binding["sha256"]
                or fv["state_sha256"] != receipt["state_sha256"]
            ):
                raise ValueError("full-validation endpoint mismatch")
            coverage = fv["coverage"]
            if (
                any(coverage[k] != spec[k] for k in coverage)
                or fv["scored_positions"] != required_positions
                or coverage["expected_positions"] != required_positions
            ):
                raise ValueError("full-validation population/coverage mismatch")
            for k in ("source", "source_inventory"):
                if fv[k] != spec[k]:
                    raise ValueError("full-validation source mismatch")
                verify(fv[k]["path"], fv[k]["sha256"], bindings)
            identity = {k: fv[k] for k in ("coverage", "source", "source_inventory")}
            if population is not None and population != identity:
                raise ValueError("different position inventories cannot be aggregated")
            population = identity
            vector = fv["vectors"]
            shape = [coverage["complete_windows"], coverage["window_tokens"] - 1, len(FIELDS)]
            if (
                vector["fields"] != FIELDS
                or vector["shape"] != shape
                or vector["dtype"] != "float64"
                or vector["order"] != "window,target_position,field"
            ):
                raise ValueError("unexpected vector layout")
            if (
                Path(vector["path"]).resolve()
                != (attempt / f"full-validation-{final}.npz").resolve()
            ):
                raise ValueError("vector belongs to another endpoint")
            verify(vector["path"], vector["sha256"], bindings)
            cell = result["cell"]
            coord = tuple(cell[k] for k in ("condition", "dataset", "realization", "order"))
            if coord in seen:
                if seen[coord] == str(attempt.resolve()):
                    continue  # multiple successful queue records pointing to the same attempt
                raise ValueError("multiple complete attempts for one coordinate require review")
            seen[coord] = str(attempt.resolve())
            with np.load(vector["path"], allow_pickle=False) as archive:
                values = archive["values"]
            if (
                list(values.shape) != shape
                or values.dtype != np.float64
                or not np.isfinite(values).all()
            ):
                raise ValueError("invalid validation values")
            rows.append(
                dict(
                    **cell,
                    checkpoint=final,
                    reference="own_capoff",
                    attempt=str(attempt.resolve()),
                    finish_receipt=str(finish_path.resolve()),
                    vector=vector,
                    **statistics(values[:, :, 0] - values[:, :, 1]),
                )
            )
    if not rows:
        raise ValueError("no successful complete cells")
    # Recheck small mutable records, not the multi-GB immutable vector inventory.
    for path, expected in bindings.items():
        if Path(path).suffix == ".json" and sha(path) != expected:
            raise ValueError("input changed during tail snapshot")
    return rows, dict(
        sources_sha256=bindings,
        population=population,
        excluded=excluded,
        finish_receipts_seen=len(finishes),
    )


def format_value(value):
    return "undefined / incomplete" if value is None else f"{value:.6g}"


def render(report):
    lines = [
        "# HT-15 — cell tails and realization spread",
        "",
        f"Snapshot: {report['created_utc']}; {len(report['cells'])} successfully finished cells. CPU analysis of saved vectors.",
        "",
        "Reference: each cap's own cap-off base. S1 base-continuation effects are outside this contrast. "
        "Each cell has 245,237 repeated ordinary-text positions; they are not independent replicates. "
        "ES99+ is the fractional average over the worst 1% of positive-part losses, zeros retained. "
        "Ranges below are descriptive ranges of three realization means, not confidence intervals. "
        "Within each realization five dependent stream orders are averaged. Incomplete groups have no full range. "
        "Zero positive mass leaves half-mass concentration undefined. Cell CSV includes maximum locations; all indices are zero-based, "
        "and target_token_offset starts at 1 because the first token supplies context.",
        "",
        "| Condition | Dataset | Cells / 15 | Metric | Mean over observed cells | r0 (n) | r1 (n) | r2 (n) | Full r range |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for group in report["groups"].values():
        for metric in METRICS:
            rs = [
                f"{format_value(r['means'][metric])} ({r['cells']})"
                for r in group["realization_means"]
            ]
            extent = group["full_realization_range"][metric]
            span = "—" if extent is None else " to ".join(map(format_value, extent))
            lines.append(
                "| "
                + " | ".join(
                    [
                        group["condition"],
                        group["dataset"],
                        str(group["cells"]),
                        metric,
                        format_value(group["observed_cell_means"][metric]),
                        *rs,
                        span,
                    ]
                )
                + " |"
            )
    lines += [
        "",
        "A mean of cell ES99s is not ES99 of pooled positions; a mean of cell maxima is not a pooled maximum. "
        "A mean half-mass count is per cell and cannot be compared directly with a pooled count. "
        "Unavailable condition/dataset groups are not zero-valued observations. No claim of an asymptotic heavy-tail family follows.",
        "",
    ]
    return "\n".join(lines)


def build(receipt_root, output):
    out = Path(output).resolve()
    if out.exists():
        raise ValueError("use a new output directory")
    rows, inventory = load_cells(receipt_root)
    report = dict(
        schema_version=1,
        task="HT-15",
        gpu_seconds=0,
        created_utc=datetime.now(timezone.utc).isoformat(),
        cells=rows,
        groups=summarize(rows),
        scope="descriptive snapshot of successful receipted endpoints, not queue reconciliation",
        code_sha256={str(p): sha(p) for p in (Path(__file__), ROOT / "aw/tail_figures.py")},
        **inventory,
    )
    out.mkdir(parents=True)
    (out / "cell_tails.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (out / "tail_spread.md").write_text(render(report))
    flat = [
        {
            **{
                k: r[k]
                for k in (
                    "condition",
                    "dataset",
                    "realization",
                    "order",
                    "checkpoint",
                    "reference",
                    "positions",
                    *METRICS,
                    "maximum_ties",
                    "half_mass_fraction",
                    "positive_mass",
                    "attempt",
                )
            },
            **r["maximum_location"],
            **{k: v for k, v in r.items() if k.endswith("_count")},
        }
        for r in rows
    ]
    with (out / "cell_tails.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt-root", type=Path, default=ROOT / "logs/R1/final_queue")
    parser.add_argument(
        "--output", type=Path, required=True, help="new directory, canonically under pc_cap/logs"
    )
    args = parser.parse_args()
    report = build(args.receipt_root, args.output)
    print(
        json.dumps(
            dict(
                cells=len(report["cells"]),
                groups=len(report["groups"]),
                incomplete_groups=[k for k, g in report["groups"].items() if not g["complete"]],
                output=str(args.output),
            )
        )
    )


if __name__ == "__main__":
    main()
