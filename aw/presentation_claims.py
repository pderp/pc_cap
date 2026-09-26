"""Refresh only comparator-derived ledger rows; preserve PC results and conceptual claims."""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

from aw.pc_v0_report import sha, table

COLUMNS = [
    "ID",
    "theme",
    "status",
    "measured result",
    "population",
    "control",
    "supports",
    "does not support",
    "source",
]


def render_rows(rows):
    return table(
        COLUMNS, [[str(c).replace("|", "\\|").replace("\n", " ") for c in row] for row in rows]
    )


def read_rows(text):
    result = []
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| ID ") or line.startswith("| ---"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) != len(COLUMNS):
            raise ValueError("claim ledger table shape changed")
        result.append(cells)
    if len({r[0] for r in result}) != len(result):
        raise ValueError("duplicate claim IDs")
    return result


def refresh_text(existing, report_path):
    report = json.loads(Path(report_path).read_bytes())
    if (
        sha(report["analysis"]["path"]) != report["analysis"]["sha256"]
        or sha(report["accounting"]["path"]) != report["accounting"]["sha256"]
    ):
        raise ValueError("comparator analysis/accounting binding differs")
    native = json.loads(Path(report["analysis"]["path"]).read_bytes())
    account = json.loads(Path(report["accounting"]["path"]).read_bytes())
    replacements = {}
    for ds in ("zsre", "counterfact", "mquake"):
        groups = [
            r for r in report["groups"] if r["dataset"] == ds and r["condition"] == "R1_learned_ff"
        ]
        if len(groups) != 3 or not all(g["full_order_grid"] for g in groups):
            raise ValueError("incomplete primary realization grid")
        means = [statistics.mean(g["primary"]["RET-GS"]) for g in groups]
        replacements[f"R1-retention-{ds}"] = (
            f"RET-GS mean {statistics.mean(means):.6f}; realization means {means}"
        )
    learned = [r for r in report["groups"] if r["condition"] == "R1_learned_ff"]
    losses = [v for r in learned for v in r["fidelity"]["original"]["max_positive_nll"]]
    kl = [v for r in learned for v in r["fidelity"]["original"]["mean_kl"]]
    replacements["R1-fidelity"] = (
        f"{sum(v > 0.001 for v in kl)}/{len(kl)} learned-reader cells exceed mean KL .001; largest positive token ΔNLL {max(losses):.6f} nats"
    )
    replacements["resources"] = (
        f"{report['complete_cells']} cells; {account['charged_hours']:.6f} charged process-hours"
    )
    old = read_rows(existing)
    rows = []
    for row in old:
        if row[0].startswith("comparator-"):
            continue
        row = list(row)
        if row[0] in replacements:
            row[3] = replacements[row[0]]
            row[8] = report["analysis"]["path"]
        if row[0] == "resources":
            row[4] = f"Reconciled snapshot through queue cell {report['through']}"
            row[5] = "Verified start/finish/driver receipts; completed DEC-074b prefix"
            row[7] = (
                "Process-hours can overlap across workers; excludes separate PC acquisition and readout"
            )
            row[8] = report["accounting"]["path"]
        if row[0] == "unavailable":
            row[3] = (
                f"{len(report['unavailable'])} unavailable contrast/dataset entries; see exact inventory"
            )
            row[8] = str(Path(report_path).parent / "unavailable.csv")
        rows.append(row)
    for c in native["contrasts"]:
        control = c["contrast"]["control"]
        if c["classification"] == "unavailable" or control not in (
            "matched_update",
            "v0_live_C1",
            "v0_live_C2",
            "S1_LM",
            "S1_literal",
        ):
            continue
        v = c["metrics"]["RET-GS"]
        rows.append(
            [
                f"comparator-{c['dataset']}-{control}",
                "Active inference testbed / PC context",
                "measured",
                f"Paired RET-GS difference {v['estimate']:.6f}; r means {v['realization_estimates']}; preliminary label {c['classification']}",
                f"{c['dataset']}; 3 realizations × 5 orders at 1000 edits",
                control,
                "Declared package comparison; S1 controls continued-base training, not factual-stream fine-tuning",
                "Three clusters do not establish familywise coverage; not an ingredient-level factorial or a PC credit result",
                report["analysis"]["path"],
            ]
        )
    header = existing.split("| ID |", 1)[0]
    return header + render_rows(rows)


def append_concepts(existing, rows):
    old = read_rows(existing)
    ids = {r[0] for r in old}
    if any(r[0] in ids or len(r) != 9 for r in rows):
        raise ValueError("duplicate or malformed conceptual claim row")
    return (existing.rstrip() + "\n" + render_rows(rows).split("\n", 2)[2]).rstrip() + "\n"
