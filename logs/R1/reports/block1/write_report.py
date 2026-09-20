"""Write the readable block-1 report from verified, immutable analysis tables."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from summarize import csv_write

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LINK = "../logs/R1/reports/block1/"
LABELS = {"R1_learned_ff": "Learned v5", "R1_nonlearned": "Random reader", "v0_stable": "Stable v0"}


def number(value, digits=5):
    return "unavailable" if value is None else f"{value:.{digits}g}"


def table(headers, rows):
    return ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers),
            *("| " + " | ".join(map(str, row)) + " |" for row in rows), ""]


def main():
    summary = json.loads((HERE / "summary.json").read_text())
    audit = json.loads((HERE / "receipt-audit.json").read_text())
    analysis = json.loads((HERE / "analysis.json").read_text())
    if audit["status"] != "pass" or audit["cells"] != 45 or analysis["complete_blocks"] != [1]:
        raise ValueError("verified block-1 analysis and audit required")
    groups = summary["groups"]
    lines = ["# Stage 4 block 1: first partial confirmation report", "",
        "September 20, 2026 · R1-D14c / X22 · **One realization; descriptive results only.**", "",
        "The learned v5 memory retained paraphrased edits substantially better than the random-reader and stable-v0 controls in the first reserved realization. It preserved all 50 locality prompts in each dataset, but failed the mean-KL fidelity benchmark in every learned-reader cell. zsRE also shows incomplete near-miss preservation. These are real reserved-data observations, not development or synthetic results. They do not yet support a registered classifier label or a population-level conclusion.", "",
        "## Scope and methods", "",
        "This report includes exactly **45 cells**: three conditions × three datasets × five orders, all realization 0, the registered first block. The process receipts span September 18 21:29 to September 19 21:15 UTC (about 23.77 elapsed hours). Later blocks are outside this snapshot even if they have since completed. The unchanged matrix still contains 330 planned cells; the 285 excluded cells are **not reported as current failures**.", "",
        "A cell applies a stream of supplied factual edits to memory attached to a frozen GPT-2 model. zsRE and CounterFact reach 1,000 edits with checkpoints at 100, 300 and 1,000; MQuAKE reaches 300 with checkpoints at 100 and 300. Five orders permute the same realization's items. They measure sensitivity to order, not five independent experiments. Full fidelity assays score 245,237 token positions in 1,931 windows against both the original model and the same cell with its cap disabled; a fixed 16,256-position prefix is checked at every checkpoint.", "",
        "**ES** measures immediate edit success as edits arrive; **RET-ES** measures original edit-prompt retention at a checkpoint; **RET-GS** measures paraphrase retention; **LS** is bounded decoded-text equality on 50 locality prompts. Keeping those names separate matters: the learned zsRE final RET-ES is 0.977, while its mean immediate ES is 0.9936. Near misses are separately reserved different-subject relation/template pairs, not semantic nearest neighbours. All planned denominators remain in the detailed tables.", "",
        "The locked R1-49g / R1-75 computation runs unchanged. A local reporting wrapper scopes only the cell loader to block 1 while retaining the exact frozen matrix, all 63 registered primary metric slots and all 75 prospective omissions. The native no-result representation is used for later blocks and is explicitly qualified as out of scope here. No observations are imputed; thresholds, populations and model code are unchanged.", "",
        "## Final-checkpoint behavior", "",
        "Values below are descriptive means of five orders within realization 0. All orders and their min/max/sample-SD are retained in [summary.json](" + LINK + "summary.json) and the [checkpoint trajectory table](" + LINK + "appendix/trajectories.csv).", ""]
    lines += table(["Dataset", "Condition", "Edits", "ES", "RET-ES", "RET-GS", "LS"], [
        [g["dataset"], LABELS[g["condition"]], g["checkpoint"], *(number(g["primary"][k]["mean"]) for k in ("ES", "RET-ES", "RET-GS", "LS"))] for g in groups])
    lines += ["![Final behavior](" + LINK + "slide-figures/final-behavior.png)", "",
        "The learned reader's final paraphrase retention is 0.955 for zsRE, 0.6915 for CounterFact and 0.70333 for MQuAKE. Several final summaries are identical across its five orders; that is observed order stability on one population, not evidence of negligible uncertainty across fresh populations. The random reader retains some paraphrases but substantially changes CounterFact/MQuAKE locality and every measured near-miss response. Stable v0 preserves locality, with weaker paraphrase transfer and order-sensitive zsRE retention.", "",
        "## Registered contrasts: realization-0 effects only", "",
        "The table gives learned-v5 minus control at the registered 1,000-edit endpoint. SD and range describe the five paired order differences only. All registered intervals, the secondary t sensitivity, and classifier labels are **unavailable** with one realization. There are 12 observed realization-0 metric estimates; the complete [63-row table](" + LINK + "primary-realization0.csv) retains the other slots. MQuAKE's 21 registered 1,000-edit slots remain unavailable by design; its 300-edit behavior above cannot substitute.", ""]
    lines += table(["Dataset", "Control", "Metric", "Realization-0 mean", "Order minimum", "Order maximum", "Order sample SD"], [
        [r["dataset"], "Random reader" if r["contrast"].endswith("R1_nonlearned") else "Stable v0", r["metric"],
         *(number(r[k], 6) for k in ("mean", "minimum", "maximum", "sample_sd"))]
        for r in summary["primary_realization0"] if r["complete"]])
    lines += ["![Paired order differences](" + LINK + "slide-figures/paired-order-effects.png)", "",
        "The remaining control comparisons and historical-v2 extension have no observations in this block. The original 63-slot multiplicity family is retained. DEC-069 qualifies even the eventual three-realization summaries as preliminary; neither familywise 95% control nor a population effect is established. Five orders must never supply the missing two realizations.", "",
        "## Specificity, revisions and unavailable flags", ""]
    lines += table(["Dataset", "Condition", "Unseen firing", "Near-miss preservation", "Latest revision answer", "Semantic revision"], [
        [g["dataset"], LABELS[g["condition"]], *(number(g["secondary"][k]["mean"]) for k in ("unseen_false_fire", "near_miss_bounded", "revision_latest", "revision_semantic"))] for g in groups])
    lines += ["Unseen firing has 100 planned prompts per cell, near misses 100 planned pairs, and revisions 50 planned cases. **Learned zsRE preserves 86/100 near misses and succeeds on 49/50 revisions in every order**, while locality remains 50/50. CounterFact and MQuAKE learned cells preserve 100/100 near misses and succeed on 50/50 revisions. These endpoints test different demands; perfect locality is not universal preservation.", "",
        "Stable v0's semantic revision, old-record-retired, new-record-active and unseen-firing flag fields are unavailable in the installed analysis: the required adapter flags are absent (scored 0 of 50 revision flags / 100 firing flags). Its latest-answer and observed-answer-change fields are separately measurable. Do not turn absent flags into successful revisions or a zero firing rate. Composition reporting is also unavailable pending the separate X21-G6 adapter, even though composition phases were executed. Resource-ratio benchmarks lack an admitted-ceiling reporting adapter. These limitations do not corrupt the completed primary or fidelity measurements.", "",
        "The [endpoint observations](" + LINK + "appendix/endpoint_observations.csv), [near-family inventory](" + LINK + "appendix/near_miss.csv), and [secondary benchmarks](" + LINK + "appendix/secondary_cells.csv) retain scored/planned counts, missing reasons, descriptive Wilson references and truncation diagnostics. For example, learned zsRE locality is 50/50 bounded-equal but only 49/50 terminated-and-equal; the remaining pair is equally truncated.", "",
        "## Fidelity and concentrated harm", "",
        "A mean KL above 0.001 nats or mean signed loss increase above 0.01 nats fails the secondary cap benchmark. Integrity and numerical fidelity are separate: all 45 cells pass the evidence/admission checks, but **29/45 breach at least one benchmark**. All 15 learned cells breach KL while remaining below the mean-loss bound. The table averages within-realization orders; pass counts use each cell's joint two-reference benchmark. Original and own-cap-off references coincide numerically for this triplet and are still reported separately in the [660-slot fidelity table](" + LINK + "appendix/fidelity.csv), with only 90 observed cell/reference rows.", ""]
    lines += table(["Dataset", "Condition", "Mean KL", "Mean signed ΔNLL", "Joint passes / 5", "Largest positive ΔNLL across orders"], [
        [g["dataset"], LABELS[g["condition"]], number(g["fidelity"]["capoff"]["mean_kl"]["mean"], 7), number(g["fidelity"]["capoff"]["mean_signed_nll"]["mean"], 7), f"{g['passes']}/5", number(g["fidelity"]["capoff"]["maximum_positive_nll"]["maximum"], 7)] for g in groups])
    lines += ["![Concentrated harm](" + LINK + "slide-figures/concentrated-harm.png)", "",
        "For learned zsRE, CounterFact and MQuAKE, respectively, **69, 119 and 182 positions carry half the KL** out of 245,237 scored positions. Their largest positive target-token loss increases are 9.26, 15.38 and 13.14 nats, despite much smaller means. The corresponding near-zero loss fractions and all per-cell concentration statistics are bound in [concentration.csv](" + LINK + "appendix/concentration.csv). This supports discussing concentrated harm at the October satellite session. It does not establish a power law, a tail exponent, a causal reader-firing mechanism or the effectiveness of a κ intervention.", "",
        "The [420 tail rows](" + LINK + "appendix/tails.csv) distinguish full versus fixed-prefix validation and KL versus signed/positive loss. They include ES95/ES99, strict exceedances, maxima and locations, tie/zero-atom information where supplied, and exp(mean signed ΔNLL) with overflow flags. The [standard tail figure](" + LINK + "appendix/figures/full-validation-tails.png) displays per-cell summaries without pooling tokens into independent replicates.", "",
        "## Fidelity watch", "",
        f"The immutable [watch prefix]({LINK}watch-block1.jsonl) contains {audit['watch_events']} observations: four development baselines and all 45 block-1 cells. It yields 31 breach entries in total (two development plus {audit['block1_breach_cells']} block-1 cells) and {audit['block1_creep_alert_cells']} block-1 creep-alert cells. Repeated breaches are not automatically new alerts; the rule compares running maxima and frozen development references. X22 reproduces each observation and the historical entry/alert/document hashes from its original journal prefix. This report does not send or acknowledge notifications.", "",
        "[Watch entries](" + LINK + "appendix/watch_entries.csv), [alert reasons](" + LINK + "appendix/watch_alerts.csv), and [chronological figure](" + LINK + "appendix/figures/watch-sequence.png) retain reference, dataset, condition, realization and order. Later realization-1 watch events are deliberately excluded.", "",
        "## DEC-052 inventory and execution accounting", ""]
    lines += table(["Block", "Planned", "Observed complete in this snapshot", "Interpretation"], [
        [b["block_number"], b["planned"], b["artifact_complete"], "Complete, realization 0" if b["block_number"] == 1 else "Outside block-1 snapshot"] for b in analysis["blocks"]])
    lines += [f"**{audit['process_hours']:.6f} process-hours** were charged for 45 complete child-process envelopes. Every result had one attempt, no failure receipt, no unknown cost and no uncovered driver time. The contained driver times are diagnostics and are not added again. Both concurrent workers count toward process spending; this differs from 23.77 elapsed wall-hours. The block cost exactly reconciles with the saved D11 boundary report.", ""]
    costs = defaultdict(list)
    for row in audit["rows"]:
        costs[(row["cell"]["dataset"], row["cell"]["condition"])].append(row["charged_process_seconds"])
    cost_rows = [dict(dataset=key[0], condition=key[1], processes=len(values), process_hours=math.fsum(values)/3600,
                      mean_process_seconds=math.fsum(values)/len(values), unknown_records=0, failures=0)
                 for key, values in sorted(costs.items())]
    csv_write(HERE / "accounting-block1.csv", cost_rows)
    csv_write(HERE / "accounting-processes.csv", audit["rows"])
    lines += table(["Dataset", "Condition", "Processes", "Charged hours", "Mean seconds / process"], [
        [r["dataset"], LABELS[r["condition"]], r["processes"], number(r["process_hours"], 7), number(r["mean_process_seconds"], 7)] for r in cost_rows])
    lines += ["[Per-process accounting](" + LINK + "accounting-processes.csv) and [X22 audit](" + LINK + "receipt-audit.json) bind every start/finish/decision and checkpoint receipt. X22 checked 120 checkpoint receipts, 15 distinct opaque sealed-payload hashes, checkpoint snapshot hashes, and 69,660 phase records using the declared full or incremental integrity profile. It did not deserialize payloads/snapshots or rerun a model. No receipt defect was found.", "",
        "The native formatter's global accounting field is explicitly unavailable because its D11/D13 adapter demands a replay against the current entire queue and watch. That would mix later blocks into this historical report. The verified block-only accounting above supplies the requested measured values without weakening that adapter or presenting the stale global D11 projection as current. Current global budget forecasts, the later ceiling amendment and cutover authority remain in the owner's operational records.", "",
        "## Remaining work and interpretation", "",
        "Complete realizations 1 and 2 of the triplet before displaying any registered primary classifier. Then retain the matched/live, S1 and historical-v2 comparisons in the adopted block order, subject to the unchanged budget and October 9 experimental stop. No comparison can borrow another arm, checkpoint or dataset to fill missing slots. The October 10–14 period remains reserved for locked-data analysis, figures and rehearsal before the October 15 presentation.", "",
        "The next scientific question is whether the observed retention advantage, the zsRE near-miss weakness, and the mean/tail fidelity tradeoff recur across fresh realizations. Preserve these adverse outcomes alongside gains. Further CPU reporting work can expose composition and resource-ratio evidence once reviewed adapters exist, while keeping absent stable-v0 state flags unavailable. The full experiment has not yet isolated all architectural ingredients or established the broader coupled-free-energy/active-inference programme. The zsRE teacher population is predominantly empty baseline answers, and CounterFact retains its DEC-042 source exception; neither qualification disappears after a successful run.", "",
        "## Complete tables, figures and reproducibility", "",
        "The [filled native skeleton](" + LINK + "appendix/report.md) is the technical appendix. Its 'incomplete' rows for blocks 2–6 mean **not included in this snapshot**, not a statement about the current run. It contains all promised table slots and all six standard figures: [disposition](" + LINK + "appendix/figures/disposition.png), [registered intervals—all unavailable](" + LINK + "appendix/figures/primary-intervals.png), [checkpoint trajectories](" + LINK + "appendix/figures/checkpoint-trajectories.png), [fidelity](" + LINK + "appendix/figures/cap-fidelity.png), [tails](" + LINK + "appendix/figures/full-validation-tails.png), and [watch](" + LINK + "appendix/figures/watch-sequence.png). Three additional descriptive figures appear above; every figure has PNG, PDF and SVG exports. Six selected figures / 18 exports are copied to `assets/presentation-materials/figures/block1/`.", "",
        "[Analysis JSON](" + LINK + "analysis.json) binds the frozen matrix and immutable report/vector sources; [report-data.json](" + LINK + "appendix/report-data.json) binds table fields to JSON pointers. The native outputs are preserved separately from scope annotations. Source and export hashes, tests and the final lock check are recorded in [completion.json](" + LINK + "completion.json). The accompanying [v6/session-v10 ledger supplement](talk_claim_ledger_v6_session_v10.md) preserves the historical development claims and adds the verified current-session signed cost and D.5 interpretation.", "",
        "All work was CPU-only and read-only on the experiment. No model execution, queue control, live-file edit, source-lock change, new signature or commit was performed.", ""]
    with (ROOT / "docs/R1_stage4_report_block1_partial.md").open("x") as stream:
        stream.write("\n".join(lines))
    print(json.dumps(dict(document="docs/R1_stage4_report_block1_partial.md", cells=45, primary_estimates=12, accounting_hours=audit["process_hours"])))


if __name__ == "__main__":
    main()
