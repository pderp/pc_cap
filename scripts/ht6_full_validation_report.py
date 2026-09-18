"""Descriptive chain-S full/sample tail report; no classifier or threshold changes.

Requires all four audited measurements by default. --allow-partial produces an
explicitly incomplete preview, keeping every pending cell visible.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from scripts import ht7_concentration as ht7
from scripts import r1_49m_fidelity_policy as fidelity_policy
from scripts import r1_58l_measurement_inventory as measured
from scripts import r1_63l_full_validation_contract as full
from scripts.ht_audit_existing import statistics, tail_sum
from scripts.r1_d10a_review import ROOT, write_new


def stats(values, locations):
    values = np.asarray(values, np.float64).reshape(-1)
    result = statistics(values.tolist(), locations)
    result["ES99_positive"] = tail_sum(np.maximum(values, 0).tolist(), 0.01) / (0.01 * len(values))
    return result


def sample_statistics(values, rows, *, width, sample_windows):
    values = np.asarray(values)
    if values.ndim != 3 or values.shape[1:] != (width - 1, 5) or not np.isfinite(values).all():
        raise ValueError("finite full vectors of declared shape required")
    if not 0 < sample_windows < len(values):
        raise ValueError("sample and nonempty remainder required")
    n = sample_windows * (width - 1)
    locations = [f"w{i // (width - 1)}:p{1 + i % (width - 1)}" for i in range(n)]
    if len(rows) != n or [r["item_id"] for r in rows] != locations:
        raise ValueError("sample coverage/order differs")
    losses = np.asarray([[r[k] for k in ("cap", "capoff", "original")] for r in rows], np.float64)
    prefix = values[:sample_windows].reshape(-1, 5)
    remainder = values[sample_windows:].reshape(-1, 5)
    max_error = float(np.max(np.abs(losses - prefix[:, :3])))
    if not np.isfinite(losses).all() or max_error > 0.001:
        raise ValueError("sample/full prefix loss parity failed")
    references = {}
    for name, loss_col, kl_col in (("capoff", 1, 3), ("original", 2, 4)):
        loss = losses[:, 0] - losses[:, loss_col]
        prefix_loss = prefix[:, 0] - prefix[:, loss_col]
        if any(
            np.count_nonzero(loss > t) != np.count_nonzero(prefix_loss > t)
            for t in (0.01, 0.1, 1.0)
        ):
            raise ValueError("sample/full prefix exceedance counts differ")
        references[name] = dict(
            loss=stats(loss, locations),
            kl=stats(prefix[:, kl_col], locations),
            loss_measurement="independently saved sampled drift rows",
            kl_measurement="prefix slice of full-validation KL vectors; no separate sampled KL measurement exists",
            full_prefix_loss_mean=float(prefix_loss.mean()),
            remainder_loss_mean=float((remainder[:, 0] - remainder[:, loss_col]).mean()),
            remainder_kl_mean=float(remainder[:, kl_col].mean()),
            remainder_positions=len(remainder),
        )
    return dict(
        population="first_128_windows_descriptive",
        positions=n,
        windows=sample_windows,
        references=references,
        overlap=dict(
            status="pass",
            max_abs_loss_error_nats=max_error,
            tolerance_nats=0.001,
            exceedance_counts_identical=True,
        ),
        interpretation="fixed ordered prefix, not random sample; overlap agreement is numerical consistency, not statistical representativeness",
    )


def survival(values):
    """Exact strict empirical P(positive harm > x), including ties and zero mass."""
    a = np.maximum(np.asarray(values, np.float64).reshape(-1), 0)
    if not len(a) or not np.isfinite(a).all():
        raise ValueError("finite nonempty observations required")
    x, counts = np.unique(a, return_counts=True)
    y = (len(a) - np.cumsum(counts)) / len(a)
    if x[0] > 0:
        x, y = np.r_[0.0, x], np.r_[1.0, y]
    return x, y


def build(*, allow_partial=False):
    inventory = measured.inventory()
    if len(inventory["cells"]) != 4 or (inventory["completed"] != 4 and not allow_partial):
        raise ValueError("HT-6 final report requires all four completed, audited chain-S cells")
    rows, curves = {}, {}
    for key, record in inventory["cells"].items():
        if record["status"] != "completed_vector_and_receipt_audit":
            rows[key] = record
            continue
        recipe = json.loads(Path(record["recipe"]["path"]).read_text())
        contract = recipe["full_validation"]
        result = record["full_sample_results"]
        vector_path = Path(result["vectors"]["path"])
        checkpoint = max(recipe["checkpoints"])
        report_path = vector_path.parent / f"checkpoint-{checkpoint}.json"
        report = json.loads(report_path.read_text())
        if full.sha(report_path) != record["bindings_sha256"][str(report_path)]:
            raise ValueError("checkpoint changed after measurement audit")
        with np.load(vector_path, allow_pickle=False) as archive:
            values = archive["values"]
        if full.sha(vector_path) != result["vectors"]["sha256"]:
            raise ValueError("vectors changed after measurement audit")
        drift = report["endpoints"]["drift"]["rows"]
        sample = sample_statistics(
            values,
            drift,
            width=contract["window_tokens"],
            sample_windows=contract["sample_windows"],
        )
        comparisons = {}
        for name in ("capoff", "original"):
            f, s = result["references"][name], sample["references"][name]
            comparisons[name] = {
                metric: {
                    stat: s[metric][stat] - f[metric][stat]
                    for stat in (
                        "mean_signed",
                        "ES95_positive",
                        "ES99_positive",
                        "maximum_positive",
                    )
                }
                for metric in ("loss", "kl")
            }
        rows[key] = dict(
            status="complete_development_measurement",
            recipe=record["recipe"],
            cell=recipe["cell"],
            checkpoint=checkpoint,
            full=result,
            sample=sample,
            cap_fidelity_benchmark=fidelity_policy.benchmark(result),
            concentration=dict(
                full=ht7.concentration(values),
                sample=ht7.concentration(values[: contract["sample_windows"]]),
            ),
            sample_minus_full=comparisons,
            cost={
                k: record[k]
                for k in (
                    "attempt_wall_seconds",
                    "full_outer_seconds",
                    "full_inner_seconds",
                    "sampled_all_checkpoints_seconds",
                    "sampled_checkpoint_count",
                    "device_allocator_lifetime_peak_mib",
                    "telemetry_scope",
                )
            },
            coverage=result["coverage"],
            bindings_sha256=record["bindings_sha256"],
            admission_interpretation="DEC-064: cap fidelity is a labelled secondary benchmark without an admission veto. These remain development cells, not confirmatory admissions.",
        )
        curves[key] = dict(
            full=(values[:, :, 0] - values[:, :, 2]).ravel(),
            sample=np.asarray([r["cap"] - r["original"] for r in drift]),
        )
    return dict(
        task="HT-6",
        status="complete_descriptive_report"
        if inventory["completed"] == 4
        else "partial_preview_waiting_for_chain_S",
        completed=inventory["completed"],
        expected=4,
        cells=rows,
        created_utc=inventory["created_utc"],
        model_calls=0,
        gpu_seconds=0,
        producer=full.ref(__file__),
        dependencies=[
            full.ref(measured.__file__),
            full.ref(full.__file__),
            full.ref(ROOT / "scripts/ht_audit_existing.py"),
            full.ref(ROOT / "scripts/ht6_plot.py"),
            full.ref(ht7.__file__),
            full.ref(fidelity_policy.__file__),
        ],
        framing="DEC-054: preliminary hints at what the architecture could provide; not the coupled free energy, not a test of the one-kappa conjecture; these cells do not compare kappa treatments",
        limits=[
            "development only",
            "fixed dependent positions; no iid confidence interval",
            "no power-law or population-tail inference",
            "full-population and fixed-prefix descriptions remain separate",
            "no classifier or threshold changes",
        ],
    ), curves


def markdown(report):
    lines = [
        "# HT-6 — full-validation and sampled development tails",
        "",
        f"Status: **{report['status']}**; {report['completed']}/4 completed measurements.",
        "",
        "DEC-064 labels cap fidelity as a secondary benchmark without a primary-comparison veto. This development report makes no confirmatory classifier decision. Both references remain visible even when their numerical results coincide.",
        "",
        "Full validation is 1,931 complete 128-token windows / 245,237 predictions; 121 trailing tokens are dropped. The first 128 windows / 16,256 predictions are the fixed descriptive sample. Sample loss statistics use its separately saved rows; sample KL is derived from the matching full-vector prefix, not an independent sampled KL assay.",
    ]
    for key, cell in report["cells"].items():
        lines += ["", f"## {key}", ""]
        if cell["status"] != "complete_development_measurement":
            lines += [f"Unavailable: {cell['status']}. {cell.get('reason', '')}"]
            continue
        lines += [
            f"Checkpoint {cell['checkpoint']}; overlap **{cell['sample']['overlap']['status']}**, maximum loss difference {cell['sample']['overlap']['max_abs_loss_error_nats']:.4g} nats. Full coverage verified.",
            "",
            "| Population | Reference | Measure (nats) | N | Mean signed | ES95 positive | ES99 positive | Max positive | >.01 | >.1 | >1 |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for population in ("full", "sample"):
            for reference, ref in cell[population]["references"].items():
                for measure in ("loss", "kl"):
                    s = ref[measure]
                    counts = [s["exceedances_nats"][str(x)]["count"] for x in (0.01, 0.1, 1.0)]
                    lines.append(
                        f"| {population} | {reference} | {'NLL increase' if measure == 'loss' else 'KL(ref || cap)'} | {s['n']} | {s['mean_signed']:.8g} | {s['ES95_positive']:.8g} | {s['ES99_positive']:.8g} | {s['maximum_positive']:.8g} | {counts[0]} | {counts[1]} | {counts[2]} |"
                    )
        original = cell["full"]["references"]["original"]["loss"]
        sample = cell["sample"]["references"]["original"]["loss"]
        share = original["worst_1pct_share_positive"]
        lines += [
            "",
            f"Against the original base, full mean signed NLL increase is {original['mean_signed']:.8g}, versus {sample['mean_signed']:.8g} in the fixed prefix. The full maximum positive increase is {original['maximum_positive']:.8g}. The worst 1% of positions contain {100 * share:.5g}% of positive loss harm."
            if share is not None
            else "No positive loss harm; its concentration share is undefined.",
            "Overlap agreement checks the same positions. The prefix and complete population have different denominators and can legitimately have different means and tails; this is not a representativeness test.",
            f"Full original-reference loss has {original['atom_zero_signed']['count']:,} exact zeros, {original['negative_count']:,} negative changes, and {original['n'] - original['atom_zero_positive']['count']:,} positive changes. The positive-harm zero atom includes zero and negative loss changes.",
            "",
            f"Costs: full outer phase {cell['cost']['full_outer_seconds']:.3f} s; all {cell['cost']['sampled_checkpoint_count']} sampled phases combined {cell['cost']['sampled_all_checkpoints_seconds']:.3f} s; attempt {cell['cost']['attempt_wall_seconds']:.3f} s. Allocator peak {cell['cost']['device_allocator_lifetime_peak_mib']} MiB is a lifetime high-water observation.",
        ]
        lines += fidelity_policy.report_lines([dict(cell_id=key, **cell)])
        for population in ("full", "sample"):
            lines += [
                "",
                f"Population: **{population}**.",
                *ht7.report_lines(cell["concentration"][population]),
            ]
    lines += [
        "",
        "## Reading for the talk",
        "",
        report["framing"],
        "",
        "The result describes how ordinary-text harm is distributed after factual edits. Report the mean beside the tail, denominators and zero mass; a low average does not bound rare consequences. These are fixed development populations with dependent positions. No power-law exponent, iid uncertainty or kappa benefit is inferred.",
        "",
        "The figure shows strict empirical exceedance P(positive NLL increase > x) against the original base. Its vertical axis is logarithmic; zero survival falls below the plot. Steps use the count strictly above each observed x; no fitted line is shown. Missing panels remain unavailable.",
        "",
        "![Full and sampled exceedance curves](tail-survival.png)",
        "",
    ]
    return "\n".join(lines)


def plot(report, curves, output, python):
    panels = []
    for key in report["cells"]:
        series = []
        for name, values in curves.get(key, {}).items():
            x, y = survival(values)
            series.append(dict(name=name, n=len(values), x=x.tolist(), y=y.tolist()))
        panels.append(
            dict(title=key.removeprefix("R1-64g-").removesuffix(".recipe"), series=series)
        )
    data = output / "curve-series.json"
    write_new(data, dict(completed=report["completed"], panels=panels))
    subprocess.run(
        [
            str(python),
            "-B",
            str(ROOT / "scripts/ht6_plot.py"),
            "--input",
            str(data),
            "--output",
            str(output),
        ],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument(
        "--plot-python",
        type=Path,
        default=ROOT.parent / "assets/envs/status-paper-20260911/bin/python",
    )
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT / "logs"):
        parser.error("new repository log directory required")
    report, curves = build(allow_partial=args.allow_partial)
    args.output.mkdir(parents=True)
    write_new(args.output / "report.json", report)
    (args.output / "report.md").write_text(markdown(report))
    plot(report, curves, args.output, args.plot_python)
    print(
        json.dumps(
            dict(output=str(args.output), status=report["status"], completed=report["completed"])
        )
    )
