"""R1-D14d: read-only blocks 1–3 snapshot using unchanged D.5 analysis.

Run ``python -m aw.triplet_report analyze``, then ``... publish``. Native
figures use scripts.r1_d14_figures and the existing plotting environment.
No model, sealed payload, live mutation or new statistical rule is used.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

from scripts import ht8_fidelity_watch as watch
from scripts import r1_49g_analyze as native
from scripts import r1_77_queue as queue
from scripts import r1_d14_report as formatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/R1/reports/triplet"
MATRIX = ROOT / "manifests/revision_v1/run_matrix_final.json"
RECEIPTS = ROOT / "logs/R1/final_queue"
CONDITIONS = ("R1_learned_ff", "R1_nonlearned", "v0_stable")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(p, obj):
    with Path(p).open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def csv_write(p, rows):
    with Path(p).open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()})


@contextmanager
def triplet_view():
    original = native.old.load_cell

    def selected(cell, files, scope):
        if cell["block_number"] <= 3:
            return original(cell, files, scope)
        result = original(dict(cell, result_dir=None), files, scope)
        result["snapshot_exclusion"] = "outside triplet snapshot; consult DEC-074b/current inventory for later blocks"
        return result

    native.old.load_cell = selected
    try:
        yield
    finally:
        native.old.load_cell = original


def analyze():
    matrix = json.loads(MATRIX.read_bytes())
    cells = [c for c in native.old.all_cells(matrix) if c["block_number"] <= 3]
    if len(cells) != 135 or set(c["condition"] for c in cells) != set(CONDITIONS):
        raise ValueError("expected exactly the registered primary triplet")
    OUT.mkdir(parents=True, exist_ok=False)
    with triplet_view():
        report = native.run(MATRIX, OUT / "analysis-native")
    if report["complete_blocks"] != [1, 2, 3] or sum(c["artifact_complete"] for c in report["cells"]) != 135:
        raise ValueError("not all triplet cells pass the registered loader")
    report["snapshot_scope"] = {
        "block_numbers": [1, 2, 3], "included_cell_ids": [c["cell_id"] for c in cells],
        "excluded_planned_cells": 195,
        "interpretation": "Later comparators are outside this snapshot, not a claim that their live results are absent.",
        "decision": "DEC-069: preliminary decision summaries; three independent realization clusters only"}
    report["analysis_source_sha256"][str(Path(__file__).relative_to(ROOT))] = sha(__file__)
    dump(OUT / "analysis.json", report)
    # Watch is a real, unmodified historical journal prefix, not a filtered replay.
    raw = (ROOT / "results/R1/fidelity_watch/observations.jsonl").read_bytes()
    if not raw.endswith(b"\n"):
        raise ValueError("torn live watch read; do not use this snapshot")
    lines = raw.splitlines(keepends=True)
    expected = {watch.full.digest({"mode": "stage4_sealed_cell", "recipe_sha256": c["manifest_sha256"],
                                  "cell": {k: c[k] for k in native.old.COORDS}}) for c in cells}
    ids = [json.loads(line)["observation"]["cell_id"] for line in lines]
    selected = [i for i, identity in enumerate(ids) if identity in expected]
    if len(selected) != 135 or {ids[i] for i in selected} != expected:
        raise ValueError("triplet watch coverage differs")
    prefix = b"".join(lines[:max(selected) + 1])
    watch.replay([json.loads(line) for line in prefix.splitlines()])
    with (OUT / "watch-triplet.jsonl").open("xb") as f:
        f.write(prefix)
    accounting(matrix, cells)
    formatter.run(OUT / "analysis.json", OUT / "appendix", journal=OUT / "watch-triplet.jsonl")
    print(json.dumps({"complete_cells": 135, "complete_blocks": report["complete_blocks"],
                      "classified_contrasts": sum(c["classification"] != "unavailable" for c in report["contrasts"])}))


def accounting(matrix, cells):
    rows, sources = [], {}
    for cell in cells:
        c = queue.charged_cost(cell, queue.cell_cost(cell["result_dir"]), RECEIPTS, sha(MATRIX))
        if c["unknown_attempts"] or len(c["process_receipts"]) != 1 or len(c["attempts"]) != 1:
            raise ValueError("triplet accounting has an unknown cost/retry requiring explicit handling")
        r = c["process_receipts"][0]
        finish_path = Path(r["path"])
        finish = json.loads(finish_path.read_bytes())
        start_path = finish_path.with_name("start.json")
        start = json.loads(start_path.read_bytes())
        recipe = start["recipe"]
        if recipe["sha256"] != cell["manifest_sha256"] or sha(recipe["path"]) != recipe["sha256"]:
            raise ValueError("process recipe mismatch")
        if finish["exit_code"] != 0 or finish.get("failure_class") is not None:
            raise ValueError("unexpected process failure")
        if not math.isclose(c["known_attempt_wall_seconds"], r["wall_seconds"], abs_tol=1e-8):
            raise ValueError("driver time was not fully covered by the process receipt")
        for p in (finish_path, start_path, Path(recipe["path"])):
            sources[str(p)] = sha(p)
        for attempt in c["attempts"]:
            sources[attempt["path"]] = attempt["sha256"]
        decision = finish_path.with_name("decision.json")
        if decision.exists():
            dec = json.loads(decision.read_bytes())
            if dec["finish_sha256"] != r["sha256"] or dec["outcome"] != "complete":
                raise ValueError("parent decision mismatch")
            sources[str(decision)] = sha(decision)
        rows.append({"cell_id": cell["cell_id"], "dataset": cell["dataset"], "condition": cell["condition"],
                     "realization": cell["realization"], "order": cell["order"], "block": cell["block_number"],
                     "charged_process_seconds": r["wall_seconds"], "uncovered_driver_seconds": 0,
                     "failures": 0, "retries": 0, "unknown_cost": False, "parent_decision_present": decision.exists(),
                     "finish": r})
    old_path = ROOT / "logs/R1/operator_reports/20260921-block3-try1/report.json"
    old = json.loads(old_path.read_bytes())
    old_rows = {r["cell_id"]: r for r in old["cost_ledger"]["rows"]}
    for row in rows:
        if not math.isclose(row["charged_process_seconds"], old_rows[row["cell_id"]]["charged_seconds"], abs_tol=1e-8):
            raise ValueError("historical block-3 accounting differs")
    sources[str(old_path)] = sha(old_path)
    dump(OUT / "accounting.json", {"rows": rows, "process_hours": sum(r["charged_process_seconds"] for r in rows) / 3600,
                                   "unknown_costs": 0, "failures": 0, "retries": 0,
                                   "missing_parent_decisions": [r["cell_id"] for r in rows if not r["parent_decision_present"]],
                                   "scope": "blocks 1–3 only; process envelopes replace covered driver cost",
                                   "sources_sha256": sources})
    csv_write(OUT / "accounting.csv", rows)


def summarize(report):
    groups = defaultdict(list)
    for i, c in enumerate(report["cells"]):
        if c["artifact_complete"]:
            if c["block_number"] not in (1, 2, 3):
                raise ValueError("later cell entered triplet report")
            coord = c["cell"]
            groups[coord["dataset"], coord["condition"], coord["realization"]].append((i, c))
    rows = []
    for (dataset, condition, realization), values in sorted(groups.items()):
        values.sort(key=lambda pair: pair[1]["cell"]["order"])
        if [c["cell"]["order"] for _, c in values] != [100, 101, 102, 103, 104]:
            raise ValueError("incomplete order grid")
        n = 300 if dataset == "mquake" else 1000
        cps = [c["checkpoints"][str(n)] for _, c in values]
        row = {"dataset": dataset, "condition": condition, "realization": realization, "checkpoint": n,
               "source_pointers": [f"/cells/{i}/checkpoints/{n}" for i, _ in values],
               "primary": {m: [c["primary"][m]["value"] for c in cps] for m in ("ES", "RET-ES", "RET-GS", "LS")},
               "near_miss": [c["secondary"]["near_miss_bounded"]["value"] for c in cps],
               "revision_semantic": [c["secondary"]["revision_semantic"]["value"] for c in cps],
               "cap_benchmark_passes": sum(c["cap_fidelity_benchmark"]["passes"] is True for _, c in values),
               "fidelity": {}}
        for reference in ("capoff", "original"):
            f = [c["secondary"]["full_validation"] for c in cps]
            row["fidelity"][reference] = {
                "mean_kl": [x["references"][reference]["kl"]["mean_signed"] for x in f],
                "mean_signed_nll": [x["references"][reference]["loss"]["mean_signed"] for x in f],
                "max_positive_nll": [x["references"][reference]["loss"]["maximum_positive"] for x in f],
                "half_kl_positions": [x["concentration"]["references"][reference]["kl_positions"]["minimum_count_for_half_mass"] for x in f]}
        rows.append(row)
    if len(rows) != 27:
        raise ValueError("expected 27 dataset/condition/realization groups")
    return rows


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + [
        "| " + " | ".join(map(str, r)) + " |" for r in rows] + [""]


def fmt(x):
    return "unavailable" if x is None else f"{x:.5f}"


def publish():
    report = json.loads((OUT / "analysis.json").read_bytes())
    groups = summarize(report)
    dump(OUT / "summary.json", {"groups": groups, "scope": report["snapshot_scope"]})
    csv_write(OUT / "realization-summary.csv", groups)
    costs = json.loads((OUT / "accounting.json").read_bytes())
    appendix = json.loads((OUT / "appendix/report-data.json").read_bytes())
    text = ["# R1 Stage 4: complete primary triplet", "", "2026-09-24 — Capex. Read-only snapshot of blocks 1–3: **135 complete cells**, three realizations, five orders, three datasets. Registered D.5 analysis and classifications are unchanged. This report supersedes the realization-0-only tables in the block-1 partial report where all three triplet realizations are now available.", "",
            "The comparison remains a BP-trained feedforward reader study. It does not contain the forthcoming corrected predictive-coding experiments. Current scheduling is DEC-074b: finish through queue position 270, then PC work; later comparator slots below are excluded from this triplet snapshot even where they have since finished.", "",
            "## Final behavior by realization", "", "Each entry averages five orders within one realization. ES is immediate acquisition; RET-ES and RET-GS are end-of-stream own-prompt and paraphrase retention. LS is bounded locality-text equality. zsRE and CounterFact end at 1,000 edits; MQuAKE ends at 300 and remains descriptive at that checkpoint.", ""]
    text += table(["Dataset", "Condition", "Realization", "ES", "RET-ES", "RET-GS", "LS"], [
        [r["dataset"], r["condition"], r["realization"], *[fmt(statistics.mean(r["primary"][m])) for m in ("ES", "RET-ES", "RET-GS", "LS")]] for r in groups])
    text += ["## Registered contrasts: estimates before labels", "",
             "Three realization clusters supply the uncertainty. Orders share subjects and are not extra independent replications. The registered percentile intervals reduce to the observed range of realization means. They are preliminary decision summaries, not demonstrated 95% familywise coverage. The adjacent pointwise t sensitivity uses 2 degrees of freedom and assumes iid normal realization errors, uncheckable with three draws. It neither changes the classifier nor establishes simultaneous coverage. Zero observed variance does not establish certainty.", ""]
    contrast_rows = []
    for c in report["contrasts"]:
        for m, v in c["metrics"].items():
            if v["estimate"] is None:
                continue
            t = v["preliminary"]["t_sensitivity"]
            contrast_rows.append([c["dataset"], c["contrast"]["id"], m, fmt(v["estimate"]),
                                  ", ".join(fmt(x) for x in v["realization_estimates"]),
                                  str(v["adjusted_interval"]), f"[{fmt(t['lower'])}, {fmt(t['upper'])}]", c["classification"]])
    text += table(["Dataset", "Contrast", "Metric", "Mean difference", "r0, r1, r2", "Registered interval", "t sensitivity", "Preliminary class"], contrast_rows)
    text += ["All 63 primary metric slots remain in the [native appendix](../logs/R1/reports/triplet/appendix/report.md). Only triplet contrasts on zsRE/CounterFact are available at checkpoint 1,000. MQuAKE's 21 slots remain unavailable; its 300-edit outcomes are not substituted. Every realization's five paired order differences, minima, maxima and SD are in the appendix and analysis JSON.", "",
             "## What changed from realization 0", ""]
    changes = []
    for ds in ("zsre", "counterfact", "mquake"):
        rows = sorted([r for r in groups if r["dataset"] == ds and r["condition"] == "R1_learned_ff"], key=lambda r: r["realization"])
        means = [statistics.mean(r["primary"]["RET-GS"]) for r in rows]
        changes.append([ds, fmt(means[0]), ", ".join(fmt(x) for x in means[1:]), fmt(statistics.mean(means)),
                        fmt(statistics.mean(means) - means[0])])
    text += table(["Learned reader", "r0 RET-GS", "r1, r2 RET-GS", "Three-realization mean", "Change vs r0-only"], changes)
    text += ["## Fidelity and concentrated harm", "",
             "Per-cell means, tails, concentration, both references and benchmark flags are in the bound appendix. The 0.001 KL / 0.01 signed-NLL limits are secondary cap benchmarks, not an admission veto. The full inventory has 245,237 positions. Large concentrated effects do not establish a power law. The table shows the mean of each realization's five cell means and the largest observed positive token-NLL change within that realization.", ""]
    text += table(["Dataset", "Condition", "r", "Mean KL", "Mean signed ΔNLL", "Largest positive ΔNLL", "Benchmark passes / 5"], [
        [r["dataset"], r["condition"], r["realization"], fmt(statistics.mean(r["fidelity"]["original"]["mean_kl"])),
         fmt(statistics.mean(r["fidelity"]["original"]["mean_signed_nll"])), fmt(max(r["fidelity"]["original"]["max_positive_nll"])), r["cap_benchmark_passes"]] for r in groups])
    ws = appendix["watch"]
    text += [f"Historical watch prefix: {ws['queue_observations']} queue observations, {ws['breach_entries']} breach entries and {ws['creep_alerts']} creep alerts, replayed from the original prefix ending with the triplet. These alerts are descriptive and do not veto admission.", "",
             "## Execution accounting and limits", "",
             f"The 135 enclosing process receipts charge **{costs['process_hours']:.6f} process-hours**, matching the saved block-3 boundary cell by cell. There are zero unknown costs, failures or retries within this snapshot. Covered driver time is not charged again. Process-hours include concurrent workers and are not elapsed GPU wall-hours.", "",
             f"{len(costs['missing_parent_decisions'])} parent decision records are absent at the documented Q21 cutover; their successful start/finish and driver results remain present and charged. This known interruption is disclosed in [accounting.json](../logs/R1/reports/triplet/accounting.json). No missing decision was manufactured. The native global accounting field stays explicitly unavailable: replaying the advancing whole queue would not describe a blocks-1–3 snapshot.", "",
             "The matched/live/S1 controls remain outside this report's scope, and the historical extension is optional. DEC-074b leaves S1_literal CounterFact and the extension unrun. No absent comparison is imputed or removed from the original denominator. The study still does not isolate every architectural ingredient or supply a direct fine-tuning-on-edits baseline. CounterFact's source exception, the predominance of initially unanswered zsRE prompts, and the three-realization uncertainty limits remain relevant.", "",
             "## Tables, figures and reproduction", "",
             "[Native filled skeleton and all tables](../logs/R1/reports/triplet/appendix/report.md); [analysis with source hashes](../logs/R1/reports/triplet/analysis.json); [every realization's five orders](../logs/R1/reports/triplet/realization-summary.csv); [process accounting](../logs/R1/reports/triplet/accounting.csv). Reproducer: `python -m aw.triplet_report analyze`, then `python -m aw.triplet_report publish`, using new output paths rather than overwriting this historical snapshot. Standard plots: `python -m scripts.r1_d14_figures --data logs/R1/reports/triplet/appendix/report-data.json` in the existing plotting environment. Selected exports are copied to `assets/presentation-materials/figures/triplet/`.", "",
             "No models, GPU execution, experimental re-scoring, source-lock edits, queue operations or commits were performed for this report.", ""]
    with (ROOT / "docs/R1_stage4_report_triplet.md").open("x") as f:
        f.write("\n".join(text))
    print(json.dumps({"groups": len(groups), "complete_primary_metric_rows": len(contrast_rows), "process_hours": costs["process_hours"]}))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("analyze", "publish"))
    a = p.parse_args()
    analyze() if a.command == "analyze" else publish()
