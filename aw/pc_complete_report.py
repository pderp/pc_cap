"""PC-8/11: publish both completed default-credit studies with verified harm.

Read-only analysis of existing outcomes. Historical source substitutions are
explicit and hash checked; no running driver, experimental output or scorer is
edited. The original and treatment-aware v0 summaries must agree numerically.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import builtins
import copy
import json
import statistics
from pathlib import Path

import numpy as np

from aw import pc_v0_report as generator
from aw.pc_harm_readout import summarize
from aw.pc_historical import ROOT, Sources, bind, sha
from aw.x24_final import V0, V1

OUT0 = ROOT / "logs/additional_work/PC-v0/report-60-20260927"
OUT1 = ROOT / "logs/additional_work/PC-v1/report-4-20260927"
HARM0 = ROOT / "results/additional_work/PC-v0/harm/pc-v0-60-20260927"
HARM1 = ROOT / "results/additional_work/PC-v1/harm/pc-v1-4-20260927"


def read(path, sources):
    path = Path(path)
    sources.bindings[str(path.resolve())] = sha(path)
    return json.loads(path.read_bytes())


def native_builder(module, sources):
    historical = sources.module("pc_v0")

    def imported(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "aw.pc_v0":
            return historical
        return builtins.__import__(name, globals, locals, fromlist, level)

    def verify(path, expected, bindings):
        resolved = sources.resolve(path, expected)
        bindings[str(resolved)] = expected

    loader = bind(
        module.load_group, verify=verify, __builtins__=dict(vars(builtins), __import__=imported)
    )
    return bind(module.build, load_group=loader)


def validate_harm(folder, sources, study):
    raw = read(folder / "report.json", sources)
    sources.check(raw["sources_sha256"])
    expected = {
        (ds, r, o, a)
        for ds in ("zsre", "counterfact")
        for r in (range(3) if study == 0 else [0])
        for o in (range(100, 105) if study == 0 else [100])
        for a in ("SE-A", "SE-E")
    }
    positions = 4064 if study == 0 else 245237

    def coord(row):
        return tuple(row[k] for k in ("dataset", "realization", "order", "arm"))

    if (
        len(raw["cells"]) != len(expected)
        or {coord(c) for c in raw["cells"]} != expected
        or raw["selection"]["positions"] != positions
    ):
        raise ValueError("harm design/population differs")
    for key in ("source", "inventory"):
        b = raw["selection"][key]
        sources.resolve(b["path"], b["sha256"])
    arrays = {}
    for cell in raw["cells"]:
        row = cell["readout"]
        cost = read(Path(row["vectors"]["path"]).parent / "cost.json", sources)
        if (
            cost["status"] != "complete"
            or cost["positions_completed"] != positions
            or cost["state_before"] != row["state_sha256"]
            or cost["base_before"] != row["base_sha256"]
            or row["selection"] != raw["selection"]
        ):
            raise ValueError("harm cell incomplete or mismatched")
        b = row["vectors"]
        sources.resolve(b["path"], b["sha256"])
        with np.load(b["path"], allow_pickle=False) as data:
            values = data["values"]
        if not np.isfinite(values).all() or summarize(values) != row["summary"]:
            raise ValueError("harm statistics do not reproduce from vectors")
        run = (
            V0 if study == 0 else V1
        ) / f"{cell['dataset']}-r{cell['realization']}-o{cell['order']}-{cell['arm']}"
        if study == 0:
            cp = [c for c in read(run / "checkpoints.json", sources) if c["tag"] == "end"]
            if len(cp) != 1 or cp[0]["state_hash"] != row["state_sha256"]:
                raise ValueError("v0 harm/final memory differs")
        else:
            cp = read(run / "checkpoint-300.json", sources)
            if (
                cp["snapshot"] != cell["binding"]
                or cp["snapshot"]["state_sha256"] != row["state_sha256"]
            ):
                raise ValueError("fixed-v5 harm/final checkpoint differs")
        arrays[coord(cell)] = values
    expected_pairs = {c[:3] for c in expected}
    if (
        len(raw["pairs"]) != len(expected_pairs)
        or {tuple(p[k] for k in ("dataset", "realization", "order")) for p in raw["pairs"]}
        != expected_pairs
    ):
        raise ValueError("harm pair inventory differs")
    for pair in raw["pairs"]:
        key = tuple(pair[k] for k in ("dataset", "realization", "order"))
        a, e = (arrays[(*key, arm)] for arm in ("SE-A", "SE-E"))
        if not np.array_equal(a[:, :, 1:3], e[:, :, 1:3]):
            raise ValueError("paired reference losses differ")
        sources.resolve(pair["vectors"]["path"], pair["vectors"]["sha256"])
        with np.load(pair["vectors"]["path"], allow_pickle=False) as data:
            delta = data["values"]
        if not np.array_equal(delta, e - a) or summarize(delta) != pair["positionwise"]:
            raise ValueError("paired vector or tail statistics differ")
        for ref in ("capoff", "original"):
            difference = (
                summarize(e)[ref]["loss"]["es99_positive"]
                - summarize(a)[ref]["loss"]["es99_positive"]
            )
            if difference != pair["difference_of_arm_es99"][ref]:
                raise ValueError("difference of arm ES99 does not reproduce")
    cost = read(folder / "cost.json", sources)
    if cost["status"] != "complete":
        if study != 1 or cost["status"] != "failed" or cost["completed_arms"] != 4:
            raise ValueError("unexpected incomplete harm readout")
        repair = read(folder / "cost-repair.json", sources)
        completion = dict(
            original_status=cost["status"],
            repair=repair,
            verification="all four arm receipts complete; all vectors, paired deltas and statistics reproduced; only final table failed",
        )
    else:
        completion = dict(original_status="complete")
    result = copy.deepcopy(raw)
    result.update(
        smoke=False,
        completion_review=completion,
        sources_sha256=dict(sources.bindings),
        historical_source_substitutions=dict(sources.substitutions),
    )
    return result, cost


def harm_text(report, cost):
    selection = report["selection"]
    text = "## Ordinary-text harm and cost\n\n"
    text += f"{selection['mode']} inventory: {selection['windows']:,} windows × {selection['window_tokens'] - 1} targets = **{selection['positions']:,} positions per cell**. "
    text += "Original = own cap-off; KL direction is reference to cap. ΔNLL is log(p_reference/p_cap); positive is worse. ES99+ is the fractional mean of the worst 1% of positive loss increases, including zeros. "
    text += "These are fixed, dependent positions, not independent replications. Concentration alone does not establish a power-law or other heavy-tail family.\n\n"
    rows = []
    for ds in ("zsre", "counterfact"):
        for arm in ("SE-A", "SE-E"):
            cells = [c for c in report["cells"] if c["dataset"] == ds and c["arm"] == arm]
            summaries = [c["readout"]["summary"]["original"] for c in cells]

            def mean(fn, summaries=summaries):
                return statistics.mean(fn(s) for s in summaries)

            rows.append(
                [
                    ds,
                    arm,
                    len(cells),
                    mean(lambda s: s["kl"]["mean_signed"]),
                    mean(lambda s: s["loss"]["mean_signed"]),
                    mean(lambda s: s["loss"]["es99_positive"]),
                    mean(lambda s: s["loss"]["maximum_signed"]),
                    max(s["loss"]["maximum_signed"] for s in summaries),
                    *[
                        mean(lambda s, t=t: s["loss"]["exceedance"][t]["fraction"])
                        for t in ("0.01", "0.1", "1.0")
                    ],
                ]
            )
    text += generator.table(
        [
            "Dataset",
            "Arm",
            "Cells",
            "Mean KL",
            "Mean ΔNLL",
            "Mean ES99+",
            "Mean of cell maxima",
            "Largest single maximum",
            "P(>0.01)",
            "P(>0.1)",
            "P(>1)",
        ],
        rows,
    )
    text += "The mean of cell maxima is not the largest observed loss; both are displayed explicitly. Exceedances are fractions, not percentages.\n\n"
    pairrows = []
    for ds in ("zsre", "counterfact"):
        for r in sorted({p["realization"] for p in report["pairs"] if p["dataset"] == ds}):
            pairs = [p for p in report["pairs"] if (p["dataset"], p["realization"]) == (ds, r)]
            pairrows.append(
                [
                    ds,
                    r,
                    statistics.mean(
                        p["positionwise"]["original"]["kl"]["mean_signed"] for p in pairs
                    ),
                    statistics.mean(
                        p["positionwise"]["original"]["loss"]["mean_signed"] for p in pairs
                    ),
                    statistics.mean(p["difference_of_arm_es99"]["original"] for p in pairs),
                    statistics.mean(
                        p["positionwise"]["original"]["loss"]["es99_positive"] for p in pairs
                    ),
                ]
            )
    text += generator.table(
        [
            "Dataset",
            "r",
            "Paired mean ΔKL",
            "Paired mean ΔNLL",
            "Difference of arm ES99+",
            "ES99+ of paired loss differences",
        ],
        pairrows,
    )
    text += f"Separate readout: {cost['elapsed_process_seconds']:.3f} process seconds ({cost['elapsed_process_seconds'] / 3600:.3f} hours), charged once. "
    if cost["status"] != "complete":
        text += "The original cost receipt remains **failed** because final table generation raised KeyError('smoke'); all four arm receipts and both paired vectors pass this independent numerical reconstruction. The original cost-repair.json and wrong-caption table remain preserved. This report supplies the correct full-inventory caption. "
    return (
        text.rstrip()
        + "\n\nAll per-cell tail statistics, maximum locations/ties, exceedances, positive-harm half-mass counts and both references remain in the bound harm JSON and vectors. Zero total positive harm makes half-mass undefined.\n\n"
    )


def fixed_report(sources):
    from aw.pc_v1_run import metrics as current_metrics

    original_metrics = sources.module("pc_v1_run").metrics
    cells = []
    for c in read(V1 / "plan.json", sources)["cells"]:
        folder = V1 / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        cfg = read(folder / "config.json", sources)
        payload_ref = cfg["inputs"]["payload"]
        sources.resolve(payload_ref["path"], payload_ref["sha256"])
        payload = read(payload_ref["path"], sources)
        for n in (100, 300):
            cp = read(folder / f"checkpoint-{n}.json", sources)
            ids = cfg["item_ids"][:n]
            before = original_metrics(cp, ids, payload["endpoints"])
            after = current_metrics(cp, ids, payload["endpoints"])
            if before != after or after != cp["metrics"]:
                raise ValueError("fixed-v5 original/current metrics do not reproduce")
        cells.append(
            dict(
                c,
                finish=read(folder / "finish.json", sources),
                process=read(folder / "process.json", sources),
                checkpoints={
                    str(n): read(folder / f"checkpoint-{n}.json", sources)["metrics"]
                    for n in (100, 300)
                },
            )
        )
    return dict(
        schema="pc-fixed-v5-report-v1",
        cells=cells,
        population="exposed R1 realization 0, order 100, first 300 edits",
        treatment=dict(credit_iters=8, error_lr=0.1),
        sources_sha256={},
    )


def main():
    evidence = Sources()
    audit = read(ROOT / "logs/r1_x24/final/report.json", evidence)
    if (
        audit["status"] != "pass_complete"
        or audit["v0"]["audited"] != 60
        or audit["v1"]["audited"] != 4
    ):
        raise ValueError("complete X24-final audit required")
    evidence.check(audit["sources_sha256"])
    h0, c0 = validate_harm(HARM0, evidence, 0)
    h1, c1 = validate_harm(HARM1, evidence, 1)
    old = evidence.module("pc_v0_report")
    old_build = native_builder(old, evidence)
    diagnostic = ROOT / "results/additional_work/PC-v0/dev-diagnostic-20260927"
    original = old_build(
        [V0],
        ROOT / "logs/additional_work/PC-v0/original-generator-replay-20260928",
        ROOT / "logs/additional_work/PC-v0/original-generator-replay-20260928.md",
        orders=5,
        diagnostics=[diagnostic],
    )
    current = native_builder(generator, evidence)
    doc0 = ROOT / "docs/additional_work/PC-v0_report.md"
    report0 = current([V0], OUT0, doc0, orders=5, diagnostics=[diagnostic])
    if original["pairs"] != report0["pairs"] or original["aggregates"] != report0["aggregates"]:
        raise ValueError("original/treatment-aware numerical results differ")
    report0["numerical_replay"] = "original and treatment-aware pairs/aggregates identical"
    report1 = fixed_report(evidence)
    OUT1.mkdir(parents=True, exist_ok=False)
    for report, out, harm, cost in ((report0, OUT0, h0, c0), (report1, OUT1, h1, c1)):
        evidence.verify_unchanged()
        report["sources_sha256"].update(evidence.bindings)
        report["historical_source_substitutions"] = dict(evidence.substitutions)
        report["harm"] = dict(report=str(out / "harm/report.json"), cost=cost)
        (out / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        (out / "harm").mkdir()
        (out / "harm/report.json").write_text(json.dumps(harm, indent=2, allow_nan=False) + "\n")
        # A separate review receipt, never overwriting the original failed cost record.
        (out / "harm/cost.json").write_text(
            json.dumps(
                dict(
                    cost,
                    status="complete",
                    original_status=cost["status"],
                    completion_basis="independent full-vector reconstruction; original receipts preserved",
                    original_directory=str(HARM0 if out == OUT0 else HARM1),
                ),
                indent=2,
            )
            + "\n"
        )
    text = doc0.read_text().replace(
        "Companion matched-position ordinary-text harm readout: unavailable until separately measured; this generator does not infer it from editing scores.\n\n",
        "",
    )
    text += harm_text(h0, c0)
    text += "## Interpretation\n\nCorrected error credit acquires these edits successfully. On zsRE it improves own-prompt retention by about two percentage points, but paraphrase retention has a small negative mean difference and mixed realization signs. CounterFact's perfect own-prompt scores and zero paraphrase scores do not discriminate these arms. The higher learning cost and ordinary-text loss tails remain part of the result. No equivalence or general PC superiority test was registered here.\n\nThe source archive supports reconstruction after PC-9/10; both generators produce identical paired effects and realization summaries. No experimental outputs were relabelled or overwritten.\n"
    doc0.write_text(text)
    doc1 = ROOT / "docs/additional_work/PC-v1_report.md"
    text = "# Fixed-v5 acquisition-credit transfer\n\nFour completed cells: two datasets, realization 0, order 100, 300 edits. Exposed, post hoc transfer check; no independent realization interval. The BP-trained base and selected v5 reader remain fixed. Only acquisition credit changes: adjoint SE-A versus corrected eight-step/rate-0.1 error credit SE-E. This does not train the reader with PC or implement expected-free-energy policy selection.\n\n"
    for n in (100, 300):
        text += f"## Checkpoint {n}\n\n" + generator.table(
            ["Dataset", "Arm", "ES", "RET-ES", "RET-GS", "LS", "Near miss", "Revision"],
            [
                [
                    c["dataset"],
                    c["arm"],
                    *[
                        c["checkpoints"][str(n)][k]["value"]
                        for k in ("ES", "RET-ES", "RET-GS", "LS", "near_miss", "revision")
                    ],
                ]
                for c in report1["cells"]
            ],
        )
    text += "## Acquisition and evaluation cost\n\nWhole-process time includes construction/lease/startup and contains stream-engine time; do not add them. Learning ledger wall time is a subset, not total cell latency.\n\n"
    text += generator.table(
        [
            "Dataset",
            "Arm",
            "Stream-engine seconds",
            "Whole-process seconds",
            "Learning ledger seconds",
            "Learning reverses",
            "Settling",
        ],
        [
            [
                c["dataset"],
                c["arm"],
                c["finish"]["elapsed_process_seconds"],
                c["process"]["elapsed_process_seconds"],
                *[
                    c["finish"]["ledger"]["learning"][k]
                    for k in ("wall_seconds", "reverses", "settle_iters")
                ],
            ]
            for c in report1["cells"]
        ],
    )
    text += harm_text(h1, c1)
    text += "## Interpretation\n\nThe endpoint differences are small, with one CounterFact paraphrase difference; that is not proof of equivalence. Average harm moves in opposite directions across the two datasets. The SE-E single-position maximum is higher on both datasets, including about 12.27 versus 9.26 nats on zsRE. Neither 'indistinguishable on every endpoint' nor 'unchanged within position noise' is justified by this one-realization design. Positions are paired observations, not an independent noise estimate. The full-inventory and legacy-v0 inventories and base models differ; do not compare their maxima as a causal effect of reader architecture.\n"
    doc1.write_text(text)
    for out, doc in ((OUT0, doc0), (OUT1, doc1)):
        (out / "publication.json").write_text(
            json.dumps(dict(document=str(doc), sha256=sha(doc)), indent=2) + "\n"
        )
    print(json.dumps(dict(v0_cells=60, v1_cells=4, paired_harm=32, numerical_replay="identical")))


if __name__ == "__main__":
    main()
