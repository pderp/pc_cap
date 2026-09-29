"""Fill every REV-2 reviewer table from the verified PC-8 artifacts."""

from __future__ import annotations

import json
import re
import statistics

from aw.pc_complete_report import HARM0, HARM1, OUT0, OUT1, ROOT
from aw.pc_v0_report import sha


def value_at(value, path):
    # Preserve decimal-point dictionary keys such as exceedance['0.01'].
    tokens = []
    for token in re.finditer(r"([A-Za-z_][A-Za-z_0-9-]*)|\['([^']+)'\]", path):
        tokens.append(token.group(1) or token.group(2))
    for token in tokens:
        value = value[token]
    return value


def fmt(value):
    return (
        "UNDEFINED (zero positive harm)"
        if value is None
        else f"{value:.8g}"
        if isinstance(value, (float, int))
        else str(value)
    )


def render():
    v0 = json.loads((OUT0 / "report.json").read_text())
    v1 = json.loads((OUT1 / "report.json").read_text())
    h = {
        name: json.loads((out / "harm/report.json").read_text())
        for name, out in (("H0", OUT0), ("H1", OUT1))
    }
    text = (ROOT / "docs/presentation/review-results-pending.md").read_text()
    text = text[text.index("## PC-v0") :].split("## Completion notes for Capstan", 1)[0]

    def substitute(match):
        key = match.group(1).strip()
        m = re.fullmatch(r"V0:aggregates\[([^,]+),([^]]+)\]\.(mean|minimum|maximum)", key)
        if m:
            ds, metric, field = m.groups()
            return fmt(
                next(a for a in v0["aggregates"] if (a["dataset"], a["metric"]) == (ds, metric))[
                    field
                ]
            )
        m = re.fullmatch(
            r"V0:cells\[([^,]+),(\d+),([^]]+)\]\.finish.elapsed_process_seconds \(sum\)", key
        )
        if m:
            ds, r, arm = m.groups()
            return fmt(
                sum(
                    c["finish"]["elapsed_process_seconds"]
                    for c in v0["cells"]
                    if (c["dataset"], c["realization"], c["arm"]) == (ds, int(r), arm)
                )
            )
        m = re.fullmatch(r"V0:([^[]+)\[([^,]+),(\d+)\]", key)
        if m:
            metric, ds, r = m.groups()
            return fmt(
                next(a for a in v0["aggregates"] if (a["dataset"], a["metric"]) == (ds, metric))[
                    "realizations"
                ][int(r)]
            )
        m = re.fullmatch(r"V1/([^-]+)-r0-o100-(SE-[AE])/(.+)\.json:(.+)", key)
        if m:
            ds, arm, file, field = m.groups()
            cell = next(c for c in v1["cells"] if (c["dataset"], c["arm"]) == (ds, arm))
            if file.startswith("checkpoint-"):
                return fmt(value_at(dict(metrics=cell["checkpoints"][file.split("-")[-1]]), field))
            return fmt(value_at(cell[file], field))
        m = re.fullmatch(r"(H[01]):([SP])\[([^,]+),(\d+)(?:,([^]]+))?\]\.(.+)", key)
        if m:
            alias, kind, ds, r, arm, field = m.groups()
            rows = [
                row
                for row in h[alias]["cells" if kind == "S" else "pairs"]
                if (row["dataset"], row["realization"]) == (ds, int(r))
                and (kind == "P" or row["arm"] == arm)
            ]
            values = [
                value_at(row["readout"]["summary"]["original"] if kind == "S" else row, field)
                for row in rows
            ]
            if not values:
                raise ValueError("missing reviewer selector: " + key)
            return (
                fmt(statistics.mean(values))
                if all(x is not None for x in values)
                else "UNDEFINED (one or more zero-harm cells)"
            )
        if key.startswith(("H0/", "H1/")) or key.startswith(("H0:", "H1:")):
            alias = key[:2]
            if "elapsed_process_seconds" in key:
                folder = HARM0 if alias == "H0" else HARM1
                return fmt(
                    json.loads((folder / "cost.json").read_text())["elapsed_process_seconds"]
                )
        raise ValueError("unhandled pending selector: " + key)

    text = re.sub(r"PENDING · ([^|\n]+)", substitute, text)
    if "PENDING" in text:
        raise ValueError("unfilled reviewer slots remain")
    header = "# Corrected predictive-coding results — completed default treatment\n\n2026-09-28, Capex. All 64 cells passed the final integrity audit. All harm vectors and paired statistics were independently reconstructed on CPU. Eight error iterations, learning rate 0.1. These results do not include the later DEC-075 controls.\n\n"
    header += "Sources in pc_cap: `logs/additional_work/PC-v0/report-60-20260927/report.json` and `logs/additional_work/PC-v1/report-4-20260927/report.json`. Canonical reports: `docs/additional_work/PC-v0_report.md` and `PC-v1_report.md`.\n\n"
    header += "H0: `results/additional_work/PC-v0/harm/pc-v0-60-20260927/report.json`. H1: `results/additional_work/PC-v1/harm/pc-v1-4-20260927/report.json`. H1's original cost receipt records a final-table failure; four complete arm receipts, both paired arrays and every statistic pass numerical reconstruction. The wrong original caption is superseded here: H1 has 245,237 positions per cell.\n\n"
    header += "V0 finish time is whole-process time. V1 finish time is stream-engine time; process.json includes it, so never add the two. Harm time is separate. Averages of maxima are labelled as such; tokens and orders do not become independent realizations.\n\n"
    return header + text


def main():
    content = render()
    paths = [
        ROOT / "docs/presentation/review-results.md",
        ROOT.parent / "assets/presentation-materials/review-data/results.md",
    ]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print(json.dumps(dict(paths=list(map(str, paths)), sha256=sha(paths[0]))))


if __name__ == "__main__":
    main()
