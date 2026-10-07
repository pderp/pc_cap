"""PC-13: paired settling-depth results on a common order, with no depth pooling."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import statistics
from pathlib import Path

import numpy as np

from aw import pc_treatments as treatment
from aw import pc_v0_report as native
from aw.pc_complete_report import HARM0, OUT0, read
from aw.pc_harm_readout import summarize
from aw.pc_historical import ROOT, sha
from aw.reporting_sources import (
    Sources,  # archive-aware (reporting only; runtime resolver unchanged)
)

BASE = ROOT / "results/additional_work/PC-v0"
OUTPUT = ROOT / "logs/additional_work/PC-v0/controls-report-20260929"
DOCUMENT = ROOT / "docs/additional_work/PC-controls_report.md"
COORDS = ("dataset", "realization", "order", "arm")


def coord(c):
    return tuple(c[k] for k in COORDS)


def vector(path, evidence):
    evidence.resolve(path["path"], path["sha256"])
    with np.load(path["path"], allow_pickle=False) as f:
        values = f["values"].copy()
    if values.shape != (32, 127, 5) or not np.isfinite(values).all():
        raise ValueError("complete finite legacy S5 harm inventory required")
    return values


def harm(folder, cells, depth, evidence):
    report = read(folder / "report.json", evidence)
    cost = read(folder / "cost.json", evidence)
    if cost["status"] != "complete" or report.get("smoke"):
        raise ValueError("completed research harm readout required")
    evidence.check(report["sources_sha256"])
    selected = report["selection"]
    expected = {coord(c) for c in cells}
    if (
        selected["positions"] != 4064
        or len(report["cells"]) != len(expected)
        or {coord(c) for c in report["cells"]} != expected
    ):
        raise ValueError("harm design/coverage differs")
    for key in ("source", "inventory"):
        evidence.resolve(selected[key]["path"], selected[key]["sha256"])
    if report.get("treatment", treatment.DEFAULT) != dict(credit_iters=depth, error_lr=0.1):
        raise ValueError("harm treatment differs")
    arrays = {}
    summaries = {}
    for row in report["cells"]:
        key = coord(row)
        r = row["readout"]
        if (
            row.get("treatment", treatment.DEFAULT) != dict(credit_iters=depth, error_lr=0.1)
            or r["selection"] != selected
        ):
            raise ValueError("nested treatment or position inventory differs")
        values = vector(r["vectors"], evidence)
        if summarize(values) != r["summary"]:
            raise ValueError("harm summary does not reproduce from vectors")
        receipt = read(Path(r["vectors"]["path"]).parent / "cost.json", evidence)
        if (
            receipt["status"] != "complete"
            or receipt["positions_completed"] != 4064
            or receipt["state_before"] != r["state_sha256"]
            or receipt["base_before"] != r["base_sha256"]
        ):
            raise ValueError("incomplete or mismatched harm receipt")
        cell = next(c for c in cells if coord(c) == key)
        cp = read(Path(cell["directory"]) / "checkpoints.json", evidence)
        final = [c for c in cp if c["tag"] == "end"]
        if len(final) != 1 or final[0]["state_hash"] != r["state_sha256"]:
            raise ValueError("harm did not use the final editing memory")
        arrays[key] = values
        summaries[key] = r["summary"]["original"]
    pairs = {key[:3] for key in expected}
    if (
        len(report["pairs"]) != len(pairs)
        or {tuple(p[k] for k in COORDS[:3]) for p in report["pairs"]} != pairs
    ):
        raise ValueError("complete harm pairs required")
    for p in report["pairs"]:
        key = tuple(p[k] for k in COORDS[:3])
        a, e = (arrays[(*key, arm)] for arm in ("SE-A", "SE-E"))
        delta = vector(p["vectors"], evidence)
        if (
            not np.array_equal(a[:, :, 1:3], e[:, :, 1:3])
            or not np.array_equal(delta, e - a)
            or summarize(delta) != p["positionwise"]
        ):
            raise ValueError("paired references/vectors/statistics differ")
        for ref in ("original", "capoff"):
            difference = (
                summarize(e)[ref]["loss"]["es99_positive"]
                - summarize(a)[ref]["loss"]["es99_positive"]
            )
            if difference != p["difference_of_arm_es99"][ref]:
                raise ValueError("paired ES99 difference differs")
    return report, cost, arrays, summaries


def summarize_common(reports, harms):
    """Never mix all five k=8 orders with the single-order control design."""
    summary = []
    pairs = []
    equality = []
    for depth, report in sorted(reports.items()):
        cells = [c for c in report["cells"] if c["order"] == 100]
        if len(cells) != 12 or {coord(c) for c in cells} != {
            coord(c) for c in native.expected_cells(1)
        }:
            raise ValueError("exact common order-100 design required")
        if any(c["status"] != "complete" for c in cells):
            raise ValueError("all common cells must be complete")
        _, paired, _ = native.compare(cells, native.expected_cells(1))
        for p in paired:
            a, e = (
                next(c for c in cells if coord(c) == (p["dataset"], p["realization"], 100, arm))
                for arm in ("SE-A", "SE-E")
            )
            ha, he = (harms[depth][3][coord(c)] for c in (a, e))
            pairs.append(
                dict(
                    p,
                    depth=depth,
                    harm_difference={
                        "mean_kl": he["kl"]["mean_signed"] - ha["kl"]["mean_signed"],
                        **{
                            k: he["loss"][k] - ha["loss"][k]
                            for k in ("mean_signed", "es99_positive", "maximum_signed")
                        },
                    },
                    learning_seconds_difference=e["finish"]["ledger"]["learning"]["wall_seconds"]
                    - a["finish"]["ledger"]["learning"]["wall_seconds"],
                )
            )
            if depth == 1:
                av, ev = (harms[depth][2][coord(c)] for c in (a, e))
                efficacy_equal = a["metrics"] == e["metrics"] and a["secondary"] == e["secondary"]
                equality.append(
                    dict(
                        dataset=p["dataset"],
                        realization=p["realization"],
                        order=100,
                        primary_secondary_exact=efficacy_equal,
                        harm_vectors_bitwise_equal=bool(np.array_equal(av, ev)),
                        maximum_absolute_vector_difference=float(np.max(abs(ev - av))),
                    )
                )
        for ds in ("zsre", "counterfact"):
            for arm in ("SE-A", "SE-E"):
                rows = [c for c in cells if c["dataset"] == ds and c["arm"] == arm]
                tails = [harms[depth][3][coord(c)] for c in rows]
                summary.append(
                    dict(
                        depth=depth,
                        dataset=ds,
                        arm=arm,
                        cells=3,
                        order=100,
                        metrics={
                            m: statistics.mean(c["metrics"][m] for c in rows)
                            for m in native.METRICS
                        },
                        secondary={
                            m: statistics.mean(c["secondary"][m] for c in rows)
                            for m in native.SECONDARY
                        },
                        mean_kl=statistics.mean(t["kl"]["mean_signed"] for t in tails),
                        mean_dnll=statistics.mean(t["loss"]["mean_signed"] for t in tails),
                        es99_positive=statistics.mean(t["loss"]["es99_positive"] for t in tails),
                        mean_cell_maximum=statistics.mean(
                            t["loss"]["maximum_signed"] for t in tails
                        ),
                        largest_single_maximum=max(t["loss"]["maximum_signed"] for t in tails),
                        learning_seconds=statistics.mean(
                            c["finish"]["ledger"]["learning"]["wall_seconds"] for c in rows
                        ),
                        process_seconds=statistics.mean(
                            c["finish"]["elapsed_process_seconds"] for c in rows
                        ),
                        learning_counters={
                            k: statistics.mean(c["finish"]["ledger"]["learning"][k] for c in rows)
                            for k in (
                                "full_forwards",
                                "partial_forwards",
                                "reverses",
                                "settle_iters",
                            )
                        },
                    )
                )
    return summary, pairs, equality


def render(result):
    text = "# PC-v0 settling-depth controls: retention, harm and cost\n\n"
    text += "Completed exposed S5 comparison: two datasets × three realizations × **order 100 only** at depths 1, 8 and 32. The eight-step rows are the order-100 subset of the previously published 60-cell experiment. Using its five-order mean beside these single-order controls would compare different populations. The full original experiment remains in PC-v0_report.md. zsRE ends at 1,000 edits; CounterFact at 300. Original S5 primary scoring and bounded-text secondary scoring stay separate.\n\n"
    text += "## Results at the common order\n\nAll rows are means over three realizations. Scores are fractions; loss is in nats. SE-A is the independently executed paired adjoint baseline at each requested depth (it does not itself settle).\n\n"
    text += native.table(
        [
            "Dataset",
            "Depth",
            "Arm",
            "ES",
            "RET-ES",
            "RET-GS",
            "LS",
            "Mean KL",
            "Mean ΔNLL",
            "ES99+",
            "Mean cell max",
            "Largest maximum",
            "Learning s/cell",
            "Process s/cell",
        ],
        [
            [
                r["dataset"],
                r["depth"],
                r["arm"],
                *[r["metrics"][m] for m in native.METRICS],
                r["mean_kl"],
                r["mean_dnll"],
                r["es99_positive"],
                r["mean_cell_maximum"],
                r["largest_single_maximum"],
                r["learning_seconds"],
                r["process_seconds"],
            ]
            for r in result["summary"]
        ],
    )
    text += "\n\n## Paired differences by realization\n\nSE-E minus SE-A. Behavior higher is better; harm and cost lower are better. No pooling across depths, confidence interval, best-depth selection, or treatment-by-depth significance test. The same realizations and facts recur across depths.\n\n"
    text += native.table(
        [
            "Dataset",
            "Depth",
            "r",
            "ΔES",
            "ΔRET-ES",
            "ΔRET-GS",
            "ΔLS",
            "Δmean KL",
            "Δmean NLL",
            "ΔES99+",
            "Δmax",
            "Δlearning seconds",
        ],
        [
            [
                p["dataset"],
                p["depth"],
                p["realization"],
                *p["difference"].values(),
                *p["harm_difference"].values(),
                p["learning_seconds_difference"],
            ]
            for p in result["pairs"]
        ],
    )
    text += "\n\nBounded-text secondary differences:\n\n" + native.table(
        ["Dataset", "Depth", "r", *native.SECONDARY],
        [
            [p["dataset"], p["depth"], p["realization"], *p["secondary_difference"].values()]
            for p in result["pairs"]
        ],
    )
    text += "\n\n## One-step mechanism check\n\nAt zero inferred error, the first gradient step gives e₁ = −η·adjoint; here η=0.1. In exact arithmetic, the unchanged unit-direction transport removes this positive scale. The actual-solver diagnostic verifies this to floating-point tolerance even with nonzero writes. **All recorded primary and bounded-text secondary endpoints match exactly for the six one-step pairs.** This is a mechanism check, not an independent scientific advantage.\n\n"
    text += native.table(
        [
            "Dataset",
            "r",
            "Primary + secondary exact",
            "Harm vectors bitwise equal",
            "Maximum absolute harm-vector difference",
        ],
        [
            [
                r["dataset"],
                r["realization"],
                r["primary_secondary_exact"],
                r["harm_vectors_bitwise_equal"],
                r["maximum_absolute_vector_difference"],
            ]
            for r in result["one_step_check"]
        ],
    )
    text += "\n\nThe zsRE harm vectors are not bitwise equal: small floating-point differences survive despite equal endpoint scores. CounterFact harm is exactly zero for both arms. Rounded summaries do not justify saying all probabilities or final memories are identical. Learning costs differ even at one step because the error path includes its terminal diagnostic.\n\n"
    text += "## Interpretation and limits\n\nOn these zsRE streams, more settling increases own-prompt retention, while 32 steps reduces paraphrase retention. Mean loss increase and ES99+ rise with depth, alongside a much larger learning cost. The maximum does **not** rise monotonically: the eight-step mean of maxima is smaller than at one step, then rises at 32. More retained taught answers therefore do not establish better generalization, lower harm or a net scientific benefit. CounterFact has saturated own-prompt scores and zero paraphrase retention at all depths, limiting its discrimination.\n\n"
    text += "The depth effect alone cannot establish that the content of PC credit, rather than extra computation, causes the gain. The closed direction control and completed offered-budget control below narrow the interpretation without resolving that attribution.\n\n"
    text += "Harm uses the same 32 ordinary-text windows / 4,064 fixed-prefix target positions per cell and the same cap-off/original reference. These dependent positions are not independent experimental replicates and this does not fit a heavy-tail distribution. Learning wall is a ledger subset of whole-process time; do not add them. Full original eight-step acquisition and harm jobs are charged once, not again for this subset analysis.\n\n"
    text += native.table(
        [
            "Depth",
            "Acquisition process seconds (entire source group)",
            "Harm process seconds (entire source group)",
            "Source cells",
        ],
        [
            [r["depth"], r["acquisition_seconds"], r["harm_seconds"], r["cells"]]
            for r in result["costs"]
        ],
    )
    text += "\n\nThe active-inference programme motivates selective correction and the consequences of rare errors. These experiments measure acquisition credit in a frozen model with a cap; they do not implement autonomous expected-free-energy policy selection or establish general PC superiority. Sources and exact numeric tables are in `logs/additional_work/PC-v0/controls-report-20260929/report.json`.\n"
    if "credit_controls" in result:
        from aw.pc_credit_control_review import render as render_controls

        text += render_controls(result["credit_controls"])
    return text


def build(output=OUTPUT, document=DOCUMENT):
    output, document = Path(output), Path(document)
    output.mkdir(parents=True, exist_ok=True)
    evidence = Sources()
    reports = {}
    harms = {}
    for depth in (1, 32):
        child = output / f"k{depth}"
        if (child / "report.json").exists():
            reports[depth] = read(child / "report.json", evidence)
        else:
            reports[depth] = native.build(
                [BASE / f"control-k{depth}-20260928"], child, output / f"k{depth}.md", orders=1
            )
        evidence.check(reports[depth]["sources_sha256"])
        evidence.bindings[str(child / "report.json")] = sha(child / "report.json")
    reports[8] = read(OUT0 / "report.json", evidence)
    evidence.check(reports[8]["sources_sha256"])
    for depth, report in reports.items():
        folder = HARM0 if depth == 8 else BASE / f"harm/control-k{depth}-20260928"
        harms[depth] = harm(folder, report["cells"], depth, evidence)
    if any(h[0]["selection"] != harms[8][0]["selection"] for h in harms.values()):
        raise ValueError("depths have different harm populations")
    summary, pairs, equality = summarize_common(reports, harms)
    # Cross-depth comparability: scientific inputs equal; source provenance and
    # treatment-bearing initial state hashes may differ and are not rewritten.
    for ds in ("zsre", "counterfact"):
        for realization in range(3):
            cells = [
                next(c for c in reports[k]["cells"] if coord(c) == (ds, realization, 100, "SE-A"))
                for k in (1, 8, 32)
            ]
            for key in (
                "weights_sha256",
                "manifest_sha256",
                "item_ids",
                "locality_prompts_sha256",
                "named_seeds",
                "base_hash_before",
                "drift",
            ):
                if any(
                    c["pair_identity"][key] != cells[0]["pair_identity"][key] for c in cells[1:]
                ):
                    raise ValueError("cross-depth input differs: " + key)
            if any(
                c["metrics"] != cells[0]["metrics"] or c["secondary"] != cells[0]["secondary"]
                for c in cells[1:]
            ):
                raise ValueError("repeated adjoint endpoints differ across depths")
    if not all(r["primary_secondary_exact"] for r in equality):
        raise ValueError("one-step endpoint equality does not hold; revise narrative")
    from aw.pc_credit_control_review import build as credit_controls

    controls = credit_controls(evidence)
    result = dict(
        schema="pc-depth-report-v1",
        status="complete",
        population="exposed S5; order100; three realizations; depths1/8/32",
        summary=summary,
        pairs=pairs,
        one_step_check=equality,
        costs=[
            dict(
                depth=k,
                cells=len(reports[k]["cells"]),
                acquisition_seconds=sum(
                    c["finish"]["elapsed_process_seconds"] for c in reports[k]["cells"]
                ),
                harm_seconds=harms[k][1]["elapsed_process_seconds"],
            )
            for k in (1, 8, 32)
        ],
        credit_controls=controls,
        pending_controls=[],
        model_calls=0,
        sources_sha256=evidence.bindings,
        historical_source_substitutions=evidence.substitutions,
    )
    evidence.bindings[str(Path(__file__).resolve())] = sha(__file__)
    evidence.verify_unchanged()
    (output / "report.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    document.write_text(render(result))
    (output / "publication.json").write_text(
        json.dumps(dict(document=str(document), sha256=sha(document)), indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default=str(OUTPUT))
    p.add_argument("--document", default=str(DOCUMENT))
    a = p.parse_args()
    r = build(a.output, a.document)
    print(json.dumps(dict(status=r["status"], rows=len(r["summary"]), pairs=len(r["pairs"]))))
