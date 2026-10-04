"""R-3: read-only supplemental realization report; never reissues registered labels."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

from aw import reader_results as rr

CONDITIONS = ("R1_learned_ff", "R1_nonlearned", "v0_stable")
PRIMARY = ("ES", "RET-ES", "RET-GS", "LS")
T3_975 = 3.182446305284263


def segments(session, sources, matrix_binding):
    """Count each closed execution segment once, excluding idle gaps and child times."""
    session = Path(session)
    paths = [session / "session-start.json", *sorted(session.glob("resumes/*/session-start.json"))]
    rows = []
    for p in paths:
        start = rr.read(p, sources)
        if start["matrix"] != matrix_binding:
            raise ValueError("session matrix identity differs")
        stop = p.with_name("session-finish.json")
        finish = rr.read(stop, sources) if stop.exists() else None
        seconds = finish["elapsed_wall_seconds"] if finish else None
        if seconds is not None and rr.finite(seconds) < 0:
            raise ValueError("negative segment cost")
        rows.append(
            dict(
                path=str(p),
                status=finish.get("status", "closed") if finish else "open",
                elapsed_wall_seconds=seconds,
                finish_reason=finish.get("reason") if finish else None,
                observations=finish.get("observations", []) if finish else [],
                completed=finish.get("completed", []) if finish else [],
            )
        )
    return rows


def sensitivity(cells):
    indexed = {}
    for c in cells:
        key = tuple(c["cell"][k] for k in ("dataset", "realization", "order", "condition"))
        if key in indexed:
            raise ValueError("duplicate sensitivity coordinate")
        indexed[key] = c
    output = []
    for ds in rr.DATASETS:
        for n in (100, 300, 1000):
            for metric in PRIMARY:
                means, per_order, missing = [], [], []
                for r in range(4):
                    diffs = []
                    for order in range(100, 105):
                        pair = [
                            indexed.get((ds, r, order, condition)) for condition in CONDITIONS[:2]
                        ]
                        cps = [c.get("checkpoints", {}).get(str(n)) if c else None for c in pair]
                        if any(
                            c is None
                            or not c.get("artifact_complete")
                            or not c.get("endpoint_complete")
                            for c in pair
                        ) or any(
                            cp is None or cp["primary"][metric]["status"] != "complete"
                            for cp in cps
                        ):
                            missing.append(dict(realization=r, order=order))
                            continue
                        if cps[0]["population_identity"] != cps[1]["population_identity"]:
                            raise ValueError("paired realization population differs")
                        diff = (
                            cps[0]["primary"][metric]["value"] - cps[1]["primary"][metric]["value"]
                        )
                        diffs.append(diff)
                        per_order.append(dict(realization=r, order=order, difference=diff))
                    means.append(
                        dict(
                            realization=r,
                            paired_orders=len(diffs),
                            planned_orders=5,
                            mean=statistics.mean(diffs) if len(diffs) == 5 else None,
                            available_order_mean=statistics.mean(diffs) if diffs else None,
                        )
                    )
                complete = all(x["mean"] is not None for x in means)
                est = statistics.mean(x["mean"] for x in means) if complete else None
                se = statistics.stdev(x["mean"] for x in means) / 2 if complete else None
                output.append(
                    dict(
                        dataset=ds,
                        checkpoint=n,
                        metric=metric,
                        status="four-realization sensitivity"
                        if complete
                        else "withheld: incomplete five-order pairing",
                        estimate=est,
                        interval=[est - T3_975 * se, est + T3_975 * se] if complete else None,
                        df=3,
                        critical_value=T3_975,
                        realizations=means,
                        orders=per_order,
                        missing_pairs=missing,
                    )
                )
    return output


def behavior_groups(cells):
    rows = []
    for ds in rr.DATASETS:
        for r in range(4):
            for condition in CONDITIONS:
                group = [
                    c
                    for c in cells
                    if (c["cell"]["dataset"], c["cell"]["realization"], c["cell"]["condition"])
                    == (ds, r, condition)
                ]
                for n in (100, 300, 1000):
                    for metric in PRIMARY:
                        vals = [
                            c["checkpoints"][str(n)]["primary"][metric]["value"]
                            for c in group
                            if str(n) in c.get("checkpoints", {})
                            and c["checkpoints"][str(n)]["primary"][metric]["status"] == "complete"
                        ]
                        rows.append(
                            dict(
                                dataset=ds,
                                realization=r,
                                condition=condition,
                                checkpoint=n,
                                metric=metric,
                                observed_orders=len(vals),
                                planned_orders=5,
                                available_mean=statistics.mean(vals) if vals else None,
                                full_five_order_mean=statistics.mean(vals)
                                if len(vals) == 5
                                else None,
                            )
                        )
    return rows


def build(session, history):
    # Imports only for existing read-only inventory/receipt/summary functions.
    # No engine, dispatch, run, observe/update, classifier or model constructor is called.
    from scripts import r1_75_analysis_stage4_v1 as native

    from aw import r_run as runner

    sources = {}
    matrix = runner.matrix()
    matrix_binding = dict(path=str(runner.MATRIX), sha256=rr.sha(runner.MATRIX))
    rr.read(runner.MATRIX, sources)
    segs = segments(session, sources, matrix_binding)
    states = {c["cell_id"]: runner.status(c, matrix_binding["sha256"]) for c in matrix["cells"]}
    defer = ["v0_stable:zsre", "v0_stable:counterfact"]
    inventory = None
    if all(x["elapsed_wall_seconds"] is not None for x in segs):
        inventory = runner.resume_inventory(defer_classes=defer)
    files, supplemental, population_hashes = native.Files(), [], {}
    for c in matrix["cells"]:
        st = states[c["cell_id"]]
        recipe_path = rr.bound(c["recipe"], sources)
        recipe = rr.read(recipe_path, sources)
        declared = dict(
            recipe,
            **{
                k: c[k]
                for k in (
                    "condition",
                    "dataset",
                    "realization",
                    "order",
                    "cell_id",
                    "block_number",
                    "within_block_order",
                )
            },
            manifest_sha256=c["recipe"]["sha256"],
        )
        row = native.load_cell(declared, files, "supplemental")
        if row.get("mode") not in (None, runner.MODE):
            raise ValueError("wrong supplemental execution mode")
        disposition = (
            "complete"
            if st["complete"]
            else st["terminal"]
            if st["terminal"]
            else "deferred DEC-080"
            if c["condition"] == "v0_stable"
            else "pending"
        )
        if st["complete"] and not all(
            row[k] for k in ("artifact_complete", "primary_metrics_complete", "endpoint_complete")
        ):
            disposition = "invalid: completion/endpoint mismatch"
        row.update(
            disposition=disposition,
            process_cost=st["cost"],
            dispatches=st["dispatches"],
            ceiling_seconds=c["ceilings"]["wall_seconds"],
        )
        supplemental.append(row)
        population_hashes[c["cell_id"]] = native.digest(recipe["population"])
        for binding in st["cost"]["process_receipts"]:
            rr.read(rr.bound(binding, sources), sources)
        rec = runner.OUTPUT / c["cell_id"] / "reconciliation.json"
        if rec.exists():
            rr.read(rec, sources)
    files.verify()
    sources.update(files.sources)
    h = rr.read(history, sources)
    prior = [
        c
        for c in h["cells"]
        if c["cell"]["condition"] in CONDITIONS
        and c["cell"]["dataset"] in rr.DATASETS
        and c["cell"]["realization"] in range(3)
    ]
    if len(prior) != 90:
        raise ValueError("expected 90 historical primary cells")
    all_cells = prior + supplemental

    def watch_key(x):
        return tuple(x["cell"][k] for k in ("condition", "dataset", "realization", "order"))

    observed = {watch_key(x): x for seg in segs for x in seg["observations"]}
    obsfile = runner.OUTPUT / "fidelity_watch/observations.jsonl"
    if obsfile.exists():
        raw = obsfile.read_bytes()
        sources[str(obsfile)] = rr.sha(obsfile)
        for line in raw.decode().splitlines():
            record = json.loads(line)
            x = record["observation"]
            if native.digest(x) != record["observation_sha256"]:
                raise ValueError("watch observation digest mismatch")
            observed[watch_key(x)] = x
    watch = []
    for c in supplemental:
        cp = c["checkpoints"].get("1000", {})
        full = cp.get("secondary", {}).get("full_validation", {})
        if full.get("complete"):
            watch.append(
                dict(
                    cell_id=c["cell_id"],
                    cell=c["cell"],
                    references=full["references"],
                    watch_entry=observed.get(watch_key(c)),
                    admission_veto=False,
                )
            )
    alerts = []
    path = runner.OUTPUT / "fidelity_watch/alerts.jsonl"
    if path.exists():
        sources[str(path)] = rr.sha(path)
        alerts = [json.loads(x) for x in path.read_text().splitlines()]
    for module in (Path(__file__), Path(rr.__file__), Path(runner.__file__), Path(native.__file__)):
        sources[str(module.resolve())] = rr.sha(module)
    return dict(
        task="R-3",
        status="partial"
        if any(c["disposition"] == "pending" for c in supplemental)
        else "closed scope",
        planned_cells=30,
        counts=dict(Counter(c["disposition"] for c in supplemental)),
        cells=supplemental,
        behavior=behavior_groups(all_cells),
        sensitivity=sensitivity(all_cells),
        segments=segs,
        completed_segment_wall_seconds=sum(x["elapsed_wall_seconds"] or 0 for x in segs),
        open_segments=sum(x["elapsed_wall_seconds"] is None for x in segs),
        charged_process_seconds=sum(
            st["cost"]["known_attempt_wall_seconds"] for st in states.values()
        ),
        unknown_attempts=[x for st in states.values() for x in st["cost"]["unknown_attempts"]],
        fidelity=watch,
        watch_alerts=alerts,
        resume_inventory=inventory,
        historical_analysis=str(history),
        population_hashes=population_hashes,
        sources_sha256=sources,
        primary_family_rerun=False,
        classifier_labels_reissued=False,
        gpu_seconds=0,
        model_calls=0,
    )


def markdown(r, output):
    text = f"""# Option R — {r["status"]} extension report

Capex · saved CPU analysis · {r["counts"]} out of 30 original planned cells.
Numerical record, per-order metrics/denominators and source hashes: `{output}/report.json`.

Realization 3 adds reserved subjects for the unchanged learned and random readers, five orders each on zsRE and CounterFact. It is supplemental to realizations 0–2. **DEC-080 defers the nine unrun stable-v0 cells; the earlier ceiling-killed stable-v0 cell remains incomplete by ceiling.** Its receipted intermediate checkpoints are descriptive evidence, not completion. No substituted condition or raised ceiling is introduced.

## Inventory, ceilings and charged attempts

"""
    text += rr.table(
        [
            "Dataset",
            "Condition",
            "Order",
            "Disposition",
            "Saved checkpoints",
            "Dispatches",
            "Charged process s",
            "Ceiling s",
        ],
        [
            [
                c["cell"]["dataset"],
                c["cell"]["condition"],
                c["cell"]["order"],
                c["disposition"],
                ",".join(c["checkpoints"]),
                c["dispatches"],
                c["process_cost"]["known_attempt_wall_seconds"],
                c["ceiling_seconds"],
            ]
            for c in r["cells"]
        ],
    )
    text += f"Closed execution segments total {r['completed_segment_wall_seconds'] / 3600:.4f} wall-hours of the existing 30-hour ceiling; {r['open_segments']} segments are open and have unclosed cost. Dispatch receipts total {r['charged_process_seconds'] / 3600:.4f} process-hours. Overlapping workers explain the difference; do not add these totals or charge idle time between resumes. Parent process envelopes already include driver work, including the killed attempt; the reconciliation adds no charge. Unknown attempts: {len(r['unknown_attempts'])}.\n\n"
    text += rr.table(
        ["Segment", "Status", "Wall s", "Finish reason"],
        [
            [x["path"], x["status"], x["elapsed_wall_seconds"], x["finish_reason"]]
            for x in r["segments"]
        ],
    )
    text += "## Behavior at 100, 300 and 1,000 edits\n\nEach value averages the available receipted orders within one subject realization. The fraction is available orders / five planned; an incomplete row is not the planned five-order mean. Denominators and raw order values remain in JSON. Intermediate checkpoints from the ceiling-killed cell are retained here only; no incomplete cell enters the four-realization sensitivity.\n\n"
    grouped = {}
    for x in r["behavior"]:
        key = tuple(x[k] for k in ("dataset", "realization", "condition", "checkpoint"))
        grouped.setdefault(key, {})[x["metric"]] = x
    text += rr.table(
        ["Dataset", "r", "Condition", "Edits", "Orders/5 (ES,RET-ES,RET-GS,LS)", *PRIMARY],
        [
            [
                *key,
                "/".join(str(v[k]["observed_orders"]) for k in PRIMARY),
                *[v[k]["available_mean"] for k in PRIMARY],
            ]
            for key, v in grouped.items()
        ],
    )
    text += "## Learned minus random: four-realization sensitivity\n\nFirst average the five paired order differences within each realization; then average four realization means. Display estimate ± t(3, .975) × sample SD / √4, with t=3.1824463. Orders are dependent and are not 20 independent replications. The interval is a small-cluster sensitivity, not newly established coverage. **No registered family is rerun and no classifier labels are reissued.** Until all five pairs in all four realizations are complete, the t(3) estimate and interval are withheld; available-order differences stay in JSON.\n\n"
    text += rr.table(
        [
            "Dataset",
            "Edits",
            "Metric",
            "Paired orders per r0/r1/r2/r3",
            "Estimate",
            "95% t(3) display",
            "Status",
        ],
        [
            [
                x["dataset"],
                x["checkpoint"],
                x["metric"],
                "/".join(str(v["paired_orders"]) for v in x["realizations"]),
                x["estimate"],
                x["interval"],
                x["status"],
            ]
            for x in r["sensitivity"]
        ],
    )
    text += "## Fidelity watch\n\nFinal full ordinary-text assay: 245,237 positions per completed cell. Mean KL .001 is a labelled secondary benchmark, not an integrity veto; original and own-cap-off references remain separate. The watch observations and all alert records are retained in JSON.\n\n"
    text += rr.table(
        [
            "Dataset",
            "Condition",
            "Order",
            "Reference",
            "Mean KL",
            "Mean ΔNLL",
            "KL≤.001",
            "Watch recorded",
        ],
        [
            [
                x["cell"]["dataset"],
                x["cell"]["condition"],
                x["cell"]["order"],
                ref,
                v["kl"]["mean_signed"],
                v["loss"]["mean_signed"],
                v["kl"]["mean_signed"] <= 0.001,
                x["watch_entry"] is not None,
            ]
            for x in r["fidelity"]
            for ref, v in x["references"].items()
        ],
    )
    text += f"Historical comparison source: `{r['historical_analysis']}`. The extension does not test PC credit or interventions developed from earlier populations. It supplies one additional subject realization, not extra independent evidence from every order/token.\n\n"
    text += """Refresh after the owner's resumed queue finishes (new report directory):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \\
../venv/bin/python -m aw.r_report --output logs/additional_work/R/report-NEW
```

The generator uses the existing read-only `status`/`resume_inventory` and native receipt/checkpoint summarizer. It never dispatches, repairs a run, writes watch state or calls a model. Unclosed segments remain unknown. Original 30-hour ceiling, one retry, fixed scientific recipes and October 9 at 17:00 EDT cutoff remain unchanged.
"""
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--session", type=Path, default=rr.ROOT / "logs/additional_work/R/queue/20260929T174143"
    )
    p.add_argument(
        "--history", type=Path, default=rr.ROOT / "logs/R1/reports/triplet/analysis.json"
    )
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--document", type=Path, default=rr.ROOT / "docs/additional_work/R_report.md")
    a = p.parse_args()
    r = build(a.session, a.history)
    rr.write_outputs(r, markdown(r, a.output), a.output, a.document)
    print(json.dumps(dict(status=r["status"], counts=r["counts"], model_calls=0)))


if __name__ == "__main__":
    main()
