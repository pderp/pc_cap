"""Assemble the existing Stage-4 tables into one report; no new scoring/inference."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = {
    "S": "docs/R1_stage4_report_skeleton.md",
    "T": "docs/R1_stage4_report_triplet.md",
    "C": "docs/R1_stage4_report_comparators.md",
    "P": "logs/R1/reports/comparators-270/appendix/primary.csv",
    "A": "logs/R1/reports/comparators-270/appendix/report.md",
    "U": "logs/R1/reports/comparators-270/unavailable.csv",
    "B": "logs/R1/reports/comparators-270/appendix/blocks.csv",
    "Q": "logs/R1/reports/comparators-270/appendix/secondary_macros.csv",
    "H": "logs/R1/operations/HALT_REPORT/d11-report.json",
    "K": "logs/R1/reports/comparators-270/accounting.json",
    "W": "logs/R1/reports/comparators-270/appendix/watch_summary.csv",
    "R": "logs/R1/operations/Q21_cutover/halt-reconciliation.md",
    "V": "docs/tasks/R1-final-queue-bindings-v2.json",
    "D": "docs/decisions.md",
    "M": "manifests/revision_v1/run_matrix_final.json",
    "F": "logs/additional_work/round48/HT-15b-270/cell_tails.json",
    "G": "logs/R1/reports/comparators-270/report.json",
}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def table(headers, rows):
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |" for row in rows],
        ]
    )


def build(output, document):
    output, document = Path(output).resolve(), Path(document).resolve()
    source_link = os.path.relpath(output / "sources.md", document.parent)
    assembly_link = os.path.relpath(output / "assembly.json", document.parent)
    if output.exists() or document.exists():
        raise FileExistsError("new assembly output and document required")
    bindings = {
        key: dict(path=str(ROOT / name), sha256=sha(ROOT / name)) for key, name in SOURCE.items()
    }

    def value(key):
        return json.loads(Path(bindings[key]["path"]).read_bytes())

    def rows(key):
        with Path(bindings[key]["path"]).open() as f:
            return list(csv.DictReader(f))

    p, u, b, w = rows("P"), rows("U"), rows("B"), rows("W")[0]
    g, k, h, tail = value("G"), value("K"), value("H"), value("F")
    if g["through"] != 270 or g["complete_cells"] != 270 or len(p) != 63:
        raise ValueError("not the reconciled 270-cell/63-slot snapshot")
    if g["unavailable"] != u or len(u) != 11:
        raise ValueError("unavailable inventory differs from published snapshot")
    for binding in (g["analysis"], g["accounting"]):
        if sha(binding["path"]) != binding["sha256"]:
            raise ValueError("published input changed")
    if sha(bindings["K"]["path"]) != g["accounting"]["sha256"]:
        raise ValueError("accounting sources differ")
    halt_cost = {r["cell_id"]: r for r in h["cost_ledger"]["rows"]}
    if len(k["rows"]) != 270 or len(h["complete_cells"]) != 270:
        raise ValueError("halt membership differs")
    class_seconds = defaultdict(list)
    for r in k["rows"]:
        if not math.isclose(
            r["charged_seconds"], halt_cost[r["cell_id"]]["charged_seconds"], abs_tol=1e-7
        ):
            raise ValueError("saved accounting disagrees with halt receipt")
        class_seconds[r["condition"], r["dataset"]].append(r["charged_seconds"])
    if not math.isclose(
        k["charged_hours"] * 3600, h["cost_ledger"]["charged_seconds"], abs_tol=1e-6
    ):
        raise ValueError("process total disagrees")
    available = [r for r in p if r["metric"] == "RET-GS" and r["classification"] != "unavailable"]
    missing = [r for r in p if r["metric"] == "RET-GS" and r["classification"] == "unavailable"]
    labels = Counter(r["classification"] for r in available)
    if len(available) != 13 or len(missing) != 8:
        raise ValueError("primary contrast inventory changed")
    watch_text = f"The journal has {w['events']} observations ({w['queue_observations']} confirmation, four development), {w['breach_entries']} breach entries and {w['creep_alerts']} creep alerts. These totals include development entries; no alert is an admission veto. Watch generation does not certify that a human received a notification. [W]"
    contrast_rows = []
    for r in available:
        rs = ", ".join(f"{x:.6f}" for x in json.loads(r["realizations"]))
        interval = json.loads(r["adjusted_interval"])
        ts = json.loads(r["t_sensitivity"])
        contrast_rows.append(
            [
                r["dataset"],
                r["contrast"].removeprefix("primary-vs-"),
                r["estimate"],
                rs,
                f"{interval['lower']:.6f}, {interval['upper']:.6f}",
                f"{ts['lower']:.6f}, {ts['upper']:.6f}",
                r["classification"],
            ]
        )
    # Receipt arithmetic only. Never add nested driver time to process envelopes.
    cost_rows = []
    for condition in dict.fromkeys(r["condition"] for r in k["rows"]):
        row = [condition]
        for ds in ("zsre", "counterfact", "mquake"):
            times = class_seconds.get((condition, ds))
            row.append(f"{math.fsum(times) / 3600:.6f}" if times else "not run")
        cost_rows.append(row)
    block_rows = [
        [
            r["block_number"],
            r["artifact_complete"] + "/" + r["planned"],
            "complete" if r["complete"] == "True" else "partially/unrun by DEC-074b",
        ]
        for r in b
    ]
    s1 = tail["groups"]["S1_literal|zsre"]
    s1range = s1["full_realization_range"]["es99_positive"]
    text = f"""# Revision v1 Stage 4: correction, interference and concentrated harm

**Assembled confirmatory-study report — reconciled DEC-074b halt, September 27, 2026.** This is the single report entry point, following the registered skeleton [S]; its complete filled tables remain in the [native appendix][A]. Lettered citations identify the source file; full SHA256 hashes and table selections are in the [source registry]({source_link}). This assembly introduces no model execution, re-scoring, inferential calculation or new classifier label. Receipt sums and formatting are the only derived displays.

## Abstract and research question

The learned memory reader improves paraphrase retention over the tested controls, while failing the declared cap-fidelity benchmark. Published final RET-GS means are **0.96033 zsRE, 0.67800 CounterFact and 0.71556 MQuAKE**; the latter ends at 300 edits and is descriptive. All **45 learned-reader cells** exceed mean KL 0.001; their largest positive token loss increase is **17.06053 nats**. Useful editing and concentrated unintended changes coexist. These observations test a BP-trained correction system; predictive-coding credit and active policy choice are separate supplemental/proposed work. [T] [C] [D]

## Methods and populations

The frozen D.5 inventory declares **285 core + 45 optional cells**, three realization clusters and five paired orders per cluster. zsRE/CounterFact use checkpoints 100/300/1,000; MQuAKE uses 100/300. ES measures immediate edit success, RET-GS retained paraphrase answers, and LS exact bounded locality-text agreement with the original base. Near-miss challenges preserve the neighbour's own cap-off response and use distinct-subject relation/template families, not semantic nearest neighbours. The full text assay covers **1,931 windows / 245,237 positions**; the fixed descriptive prefix covers **128 windows / 16,256 positions**. The complete methods, denominators, termination diagnostics and endpoint contracts are retained in [S] [A] [M].

DEC-069 keeps the **63 metric slots** and registered labels, but treats the three-realization ranges as preliminary decision summaries. Orders and tokens are not extra independent realizations; no demonstrated 95% familywise guarantee is claimed. Pointwise Student-t sensitivity assumes independent normal realization errors, has **2 degrees of freedom**, and never changes classification. [P] [D]

## Execution disposition and DEC-052 inventory

**270 completed cells out of 330 declared**, with zero failed attempts and zero retries; **60 scheduled cells** remain unrun by decision, not technical failure. The blocks and all excluded coordinates remain visible. [B] [K] [R]

{table(["Block", "Completed / declared", "Disposition"], block_rows)}

The published omission CSV has **11 rows**: **eight unavailable primary contrasts** (24 metric slots) plus **three dataset entries for the optional extension**. The extension's native secondary table retains eight comparisons / 24 metric rows; these are a different denominator. The **75 prospectively omitted MQuAKE comparator coordinates** under DEC-066 are outside the reduced 330-cell execution matrix and must not be added to its 60 unrun cells. [U] [A] [M]

{table(["Dataset", "Unavailable inventory entry", "Reason"], [[r["dataset"], r["contrast"], r["reason"]] for r in u])}

## Registered primary comparisons

The following copies the published RET-GS row of each available contrast; values are learned minus control. Every ES/LS row, both registered interval columns, all five order differences within each realization and their dispersion remain in [P] [A]. The jointly classified comparisons comprise **{labels["positive"]} preliminary positive** and **{labels["inconclusive"]} inconclusive**, plus **{len(missing)} unavailable**. A label is not a new efficacy guarantee. [P]

{table(["Dataset", "Control", "RET-GS difference", "r0, r1, r2", "Registered range", "t sensitivity", "Existing joint class"], contrast_rows)}

CounterFact versus stable v0, matched update and both live-v0 arms remains inconclusive because the learned reader's locality reaches **48/50** in realization 2, despite retained paraphrase gains. CounterFact versus S1_LM is positive under the installed classifier because that control also loses locality. All three metrics, rather than RET-GS alone, determine these labels. [T] [C] [P]

## Secondary behavior and specificity

zsRE learned-reader near-miss preservation is **86/100, 92/100 and 87/100** across realizations despite perfect ordinary locality. Its unseen-prompt false-fire rates at 1,000 records are **0.09, 0.13 and 0.16**; the published macro 0.12666667 passes the secondary 0.15 threshold, but that does not erase the failing realization's cells. Revision semantics, planned/scored/missing counts, the historical-v2 table and full checkpoint trajectories remain separate in the appendix; composition and compatible resource-ratio reporting remain unavailable. [T] [Q] [A]

## MQuAKE at 300 edits and prospective omissions

The published learned-reader realization RET-GS values are **0.703333, 0.723333 and 0.720000**. Its actual-occupancy 300-record outside-fire measurements and descriptive Wilson reference intervals are reported in the appendix, without importing a 1,000-record threshold. All **seven registered MQuAKE contrasts / 21 metric slots** at 1,000 stay unavailable: the two triplet controls lack that endpoint, and the five additional controls were prospectively omitted under DEC-066. [T] [P] [U] [A]

## Fidelity benchmarks, watch and concentrated harm

Mean KL **≤0.001** and mean signed ΔNLL **≤0.01 nats** are secondary benchmarks under DEC-064; artifact integrity and scientific admission do not imply benchmark success. Original-base and own-cap-off references remain separate, particularly for continued-base controls. The appendix retains every cell's mean, fractional ES95/ES99, maxima/location/ties, strict exceedances, zero atoms and concentration; no heavy-tail family or power-law exponent is established. [S] [A] [D]

For example, the completed S1_literal zsRE group has positive-harm ES99 mean **{s1["observed_cell_means"]["es99_positive"]:.9f} nats**, with three-realization range **{s1range[0]:.9f}–{s1range[1]:.9f}**; mean per-cell half-mass count is **{s1["observed_cell_means"]["half_mass_positions"]:.6f} positions**. This is the cap-versus-own-cap-off contrast; it does not describe the continued base's change from the original model. Realization ranges are descriptive, and repeated positions are not independent replicates. [F]

{watch_text}

## Execution history and resource accounting

The freeze was published **September 18** (DEC-071); first dispatch followed that day. The **September 20** Q21 drain at the block-2 boundary changed only the effective two-worker ceiling multiplier, **1.15 → 1.7**, preserving solo ceilings, scientific recipes, the **750 process-hour** shared cap and the October 9 stop. Bindings v1 apply to cells 1–90, v2 thereafter. At the approved **270th start**, the September 26 **22:18:59 EDT** halt trigger fired; the two active processes completed and the scheduler exited **23:43:25 EDT**. [D] [V] [R]

Four parent decisions are absent: stable-v0 MQuAKE realization 1 orders 103/104 at Q21, and S1_literal zsRE realization 2 orders 103/104 at the final halt. Their completed starts/finishes and driver outputs remain charged; the owner recorded the missing watch updates after reconciliation. No parent decision was manufactured. [K] [R]

Measured execution charges total **{k["charged_hours"]:.9f} process-hours**, matching the halt ledger, with **{k["unknown_attempts"]} unknown-cost records** and zero uncovered driver time. Concurrent process envelopes are summed once; nested driver timings are not added. These are not GPU elapsed hours and exclude development, continuation training and the separate PC supplement. The halt report's **308.369269 boundary hours** cover the last *complete block* (block 4), not the whole 270-cell spend; block 5 is intentionally partial. Repricing proposals in that report are not new measured costs or launch approvals. [H] [K]

{table(["Condition", "zsRE process-hours", "CounterFact process-hours", "MQuAKE process-hours"], cost_rows)}

The table groups the existing per-cell charges by condition/dataset, with only summation and seconds-to-hours conversion. Full process records, coverage of driver attempts, failures and missing decisions are in [H] [K].

## Continued-base controls and interpretation

S1_LM was measured for both main datasets; S1_literal only for zsRE. These are package comparisons, not a factorial isolation of every cap component, and there is no direct fine-tuning-on-edits control. CounterFact retains its approved source exception. The predominance of initially unanswered zsRE prompts limits an interpretation solely as correction of answered facts. The κ pilot, PC refocus and coupled-free-energy/active-inference programme do not become confirmatory arms by being discussed alongside this report. [C] [S] [D]

## Figure inventory and complete tables

The native filled skeleton [A] supplies all registered table categories and figure-data pointers. Existing comparator and triplet figures are linked in [C] [T]; the updated per-cell tail table [F] adds descriptive realization spread. No fresh plot or experimental measurement is required for this assembly. In the historical native appendix the generic execution-accounting adapter still says unavailable because it was not supplied there; the verified halt and selected-process records [H] [K] above explicitly supply that section for this assembled report.

## Completion, limitations and reproducibility

The main run is complete to the lead's reduced halt scope, while omitted comparisons remain unavailable. Experiments stop **October 9 at 17:00 ET**, with the **October 15** presentation later; preparation time is not experimental time. Development selection, three realization clusters, dependent orders, source-population exceptions and incomplete architectural/control coverage constrain generalization. PC-v0 and fixed-v5 supplemental findings are outside this main-study report until independently completed. [D] [T] [R]

Reproduce this assembly with `python -m aw.stage4_assembly --output NEW_ASSEMBLY_DIRECTORY --document NEW_REPORT.md` (explicit new-path placeholders). The [source registry]({source_link}) and [assembly record]({assembly_link}) bind all cited files, unchanged copied primary rows and accounting arithmetic. The original registered analyzer and classifier were not rerun or altered.
"""
    output.mkdir(parents=True)
    source_table = []
    for key, binding in bindings.items():
        name = SOURCE[key]
        relative = os.path.relpath(ROOT / name, document.parent)
        text += f'\n[{key}]: {relative} "SHA256 {binding["sha256"]}"\n'
        source_table.append([key, name, binding["sha256"]])
    for binding in bindings.values():
        if sha(binding["path"]) != binding["sha256"]:
            raise ValueError("source changed during assembly")
    document.write_text(text)
    (output / "sources.md").write_text(
        "# Stage-4 assembly sources\n\nEach lettered report citation names the file and full SHA256 below.\n\n"
        + table(["ID", "File", "SHA256"], source_table)
        + "\n"
    )
    record = dict(
        task="R1-D14g",
        source_bindings=bindings,
        producer=dict(path=str(Path(__file__).resolve()), sha256=sha(__file__)),
        document=dict(path=str(document), sha256=sha(document)),
        primary_rows=p,
        unavailable_inventory=u,
        existing_labels=dict(labels),
        cost_rows=cost_rows,
        charged_hours=k["charged_hours"],
        checks=dict(
            primary_slots=len(p),
            available_contrasts=len(available),
            unavailable_primary_contrasts=len(missing),
            unavailable_inventory_rows=len(u),
            source_and_halt_costs_match=True,
        ),
        new_scoring_or_inference=False,
        gpu_seconds=0,
    )
    (output / "assembly.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record["checks"]))
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--document", required=True)
    a = p.parse_args()
    build(a.output, a.document)


if __name__ == "__main__":
    main()
