"""FIN-1: copy completed report tables and sum nonoverlapping process receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import defaultdict
from pathlib import Path

from aw.additional_work_content import CLOSING, INTRO, SECTIONS, SOURCES

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def copied_table(text, prefix, occurrence=0):
    """Select an entire table without normalizing its bytes or numeric display."""
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    # The only intentional repeated header is fixed-v5 checkpoint 100 / 300.
    if not matches or occurrence >= len(matches) or (occurrence == 0 and len(matches) != 1):
        raise ValueError(f"missing or ambiguous table: {prefix}")
    start = matches[occurrence]
    end = start + 1
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    if end - start < 3 or "---" not in lines[start + 1]:
        raise ValueError(f"malformed table: {prefix}")
    return "".join(lines[start:end]), start + 1


def finite_seconds(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("duration must be a number, not a string or bool")
    if not math.isfinite(value) or value < 0:
        raise ValueError("duration must be finite and nonnegative")
    return value


def receipt_total(root, entries):
    """Require disjoint enclosing scopes; never silently turn missing time into 0."""
    rows, scopes, paths, groups = [], [], set(), defaultdict(list)
    for entry in entries:
        path = (root / entry["path"]).resolve()
        scope = (root / entry["scope"]).resolve()
        if path in paths or any(scope == p or scope.is_relative_to(p) or p.is_relative_to(scope)
                                for p in scopes):
            raise ValueError(f"duplicate, shared, or nested charge: {path}")
        if not path.is_relative_to(scope):
            raise ValueError(f"receipt outside its enclosing scope: {path}")
        data = json.loads(path.read_text())
        seconds = finite_seconds(data[entry["field"]])
        status = data.get("status")
        if "returncode" in data:
            status = "complete" if data["returncode"] == 0 else "stopped/failed"
        if status is None and isinstance(data.get("complete"), bool):
            status = "complete" if data["complete"] else "incomplete"
        if status is None and "planned" in data and "finished" in data:
            status = "complete" if len(data["finished"]) == data["planned"] and all(
                cell["exit_code"] == 0 for cell in data["finished"]
            ) else "incomplete"
        rows.append(dict(entry, path=str(path), scope=str(scope), sha256=sha(path),
                         seconds=seconds, status=status or "see receipt"))
        paths.add(path)
        scopes.append(scope)
        groups[entry["group"]].append(seconds)
    return dict(receipts=rows, groups={k: math.fsum(v) for k, v in sorted(groups.items())},
                known_process_seconds=math.fsum(r["seconds"] for r in rows))


def portfolio_receipts(root):
    """Closed-portfolio inventory, only outer receipts (no recursive cost sums)."""
    entries = []

    def add(path, group, field="elapsed_process_seconds"):
        entries.append(dict(path=str(path.relative_to(root)), scope=str(path.parent.relative_to(root)),
                            group=group, field=field))

    base = root / "results/additional_work"
    v0 = base / "PC-v0"
    for name, group in (
        ("dev-diagnostic-20260927", "PC-v0 default"),
        ("dev-profile-20260927", "PC-v0 default"),
        ("replication-60-20260927", "PC-v0 default"),
        ("dev-profile-k1-20260928", "PC-v0 depth 1"),
        ("control-k1-20260928", "PC-v0 depth 1"),
        ("dev-profile-k32-20260928", "PC-v0 depth 32"),
        ("control-k32-20260928", "PC-v0 depth 32"),
        ("random-control/profile-20260929", "PC-v0 random"),
        ("random-control/run-20260929", "PC-v0 random"),
        ("matched-control/profile-20260929", "PC-v0 offered-budget"),
        ("matched-control/run-20260929", "PC-v0 offered-budget"),
    ):
        add(v0 / name / "summary.json", group)
    for name, group in (("pc-v0-60-20260927", "PC-v0 default"),
                        ("control-k1-20260928", "PC-v0 depth 1"),
                        ("control-k32-20260928", "PC-v0 depth 32")):
        add(v0 / "harm" / name / "cost.json", group)
    v1 = base / "PC-v1"
    for suffix in ("20260927", "k32-20260929", "lr0.05-20260929", "lr0.2-20260929"):
        group = "Fixed-v5 default" if suffix == "20260927" else "Fixed-v5 settings"
        for name in (f"profile-{suffix}", f"replication-4-{suffix}"):
            add(v1 / name / "summary.json", group)
        add(v1 / "harm" / f"pc-v1-4-{suffix}" / "cost.json", group)
    for name in ("calibration", "evaluation"):
        add(base / "AW-B" / f"{name}-20260929/cost.json", f"AW-B {name}")
    for family, group, count in (("PC-reader", "PC-reader", 24), ("AW-L", "AW-L new work", 28)):
        folders = sorted(p for p in (base / family).iterdir()
                         if p.is_dir() and p.name.startswith(("train-", "eval-", "profile-")))
        if len(folders) != count:
            raise ValueError(f"{family}: closed inventory changed, expected {count}, got {len(folders)}")
        for folder in folders:
            add(folder / "cost.json", group)
    r_path = root / SOURCES["T"]
    r = json.loads(r_path.read_text())
    for cell in r["cells"]:
        for receipt in cell["process_cost"]["process_receipts"]:
            path = Path(receipt["path"])
            if sha(path) != receipt["sha256"]:
                raise ValueError(f"Option R receipt changed: {path}")
            add(path, "Option R", "charged_process_wall_seconds")
    return entries


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *["| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |" for row in rows]])


def build(output, document, *, root=ROOT, sources=None, sections=None, entries=None, gaps=None):
    root, output, document = Path(root).resolve(), Path(output).resolve(), Path(document).resolve()
    if output.exists() or document.exists():
        raise FileExistsError("choose a fresh assembly directory and document")
    sources = SOURCES if sources is None else sources
    sections = SECTIONS if sections is None else sections
    bindings = {key: dict(path=str((root / path).resolve()), sha256=sha(root / path))
                for key, path in sources.items()}
    accounting = receipt_total(root, portfolio_receipts(root) if entries is None else entries)
    if gaps is None:
        gaps = [dict(path=f"logs/additional_work/PC-v1/harm-{setting}.log", seconds=None,
                     reason="failed initial launch; no separate preserved duration receipt")
                for setting in ("k32", "lr0.05", "lr0.2")]
    unknown = [dict(gap, path=str((root / gap["path"]).resolve()), sha256=sha(root / gap["path"]))
               for gap in gaps]
    if any(row["seconds"] is not None for row in unknown):
        raise ValueError("unreceipted attempts must remain unknown")
    selections, parts = [], [INTRO]
    for title, key, requests, prose, groups in sections:
        parts.extend([f"\n## {title}\n", prose])
        content = Path(bindings[key]["path"]).read_text()
        for prefix, occurrence in requests:
            block, line = copied_table(content, prefix, occurrence)
            parts.append(f"\nCopied unchanged from [{key}] (line {line}):\n\n" + block)
            selections.append(dict(source=key, header=prefix, occurrence=occurrence, line=line,
                                   table_sha256=hashlib.sha256(block.encode()).hexdigest()))
        if groups:
            seconds = math.fsum(accounting["groups"][group] for group in groups)
            parts.append(f"\n**Measured cost:** {seconds:,.6f} receipt-backed process seconds "
                         f"({seconds / 3600:.6f} hours), including this group's profiles and separate harm "
                         "where supplied. See the nonoverlapping ledger below; unknown failed attempts are additional.\n")
        else:
            parts.append("\n**Post-halt GPU charge:** none added for this saved-result analysis or historical pilot. "
                         "CPU refresh durations and known historical pilot costs remain separately catalogued in [O] [X].\n")
    if entries is None:
        for key, group, field in (("T", "Option R", "charged_process_seconds"),
                                  ("V", "AW-L new work", "new_process_seconds")):
            native = json.loads(Path(bindings[key]["path"]).read_text())
            # Option R has a named aggregate; AW-L names are checked below by
            # the receipt inventory, not guessed from an attribution total.
            if key == "T" and not math.isclose(accounting["groups"][group], native[field], abs_tol=1e-7):
                raise ValueError("Option R aggregate differs from raw receipts")
    hours = accounting["known_process_seconds"] / 3600
    parts.extend([
        "\n## Measured post-halt compute: receipts, scope and missing costs\n",
        f"**Verified nonoverlapping total: {accounting['known_process_seconds']:,.6f} process seconds = "
        f"{hours:.6f} process-hours across {len(accounting['receipts'])} enclosing receipts.** "
        f"There are {len(unknown)} additional logged failed launches with unknown durations, so this is a "
        "**lower bound on total process spend**, not a complete bill. These are elapsed wall durations of GPU-bound "
        "processes, including compilation/CPU work; they are neither CUDA-kernel time nor elapsed exclusive GPU occupancy.\n",
        table(["Work (profiles included)", "Known process seconds", "Process hours"],
              [[name, f"{seconds:.6f}", f"{seconds / 3600:.6f}"] for name, seconds in accounting["groups"].items()]),
        "\nEach PC driver summary encloses its serial child cells. Each harm receipt encloses its arm readouts. "
        "PC-reader/AW-L training and evaluation receipts include their nested stream/harm durations. "
        "Shared full-read BP controls are charged to PC-reader once; AW-L's attributed total includes them and "
        "is deliberately not summed. Option R charges child dispatch receipts, including the ceiling stop; "
        "closed-session elapsed time and nested driver times are not added. Failed numerical-table formatting "
        "on the default fixed-v5 harm run remains charged and failed.\n",
        "Excluded: the pre-release September-26 diagnostic refused an occupied GPU before model work; "
        "PC12 and named CPU smokes are fixtures; L0/L1/PC-4/PC-6 are CPU checks; the original Stage-4 run and "
        "September-16 κ pilot predate the halt. Repeated reporting/fit/figure refreshes are CPU costs. "
        "The scope is the closed supplemental portfolio's preserved receipts, not every process on the host.\n",
        "**Missing durations:** initial fixed-v5 k32, lr .05 and lr .2 harm launch logs show failures "
        "before their successful retries. k32 failed input validation; the rate variants reached model/readout "
        "setup. The successful retry receipts cannot stand in for those earlier durations. "
        "No estimate or zero has been substituted, and no claimed ceiling overrun follows from the known total alone.\n",
        CLOSING,
        "\n## Reproduction and source registry\n\n"
        "Run `../venv/bin/python -m aw.additional_work_assembly --output NEW_DIRECTORY --document NEW_REPORT.md` "
        "from pc_cap. Both destinations must be new. This uses saved documents/receipts only; no model imports, "
        "scoring or fitting. `assembly.json` binds copied table bytes, the report, producers and receipt ledger. "
        "X25 checks this assembly alongside the native reports. The October-6 full freeze refresh remains a separate task.\n",
    ])
    for key, binding in bindings.items():
        parts.append(f'\n[{key}]: {os.path.relpath(binding["path"], document.parent)} "SHA256 {binding["sha256"]}"')
    text = "\n".join(parts) + "\n"
    # Detect concurrent changes before writing a coherent snapshot.
    for row in [*bindings.values(), *accounting["receipts"], *unknown]:
        if sha(row["path"]) != row["sha256"]:
            raise ValueError(f"source changed during assembly: {row['path']}")
    output.mkdir(parents=True)
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(text)
    record = dict(task="FIN-1", source_bindings=bindings, table_selections=selections,
                  accounting=dict(accounting, unknown_attempts=unknown, lower_bound=bool(unknown)),
                  document=dict(path=str(document), sha256=sha(document)),
                  producers=[dict(path=str(Path(p).resolve()), sha256=sha(p))
                             for p in (__file__, Path(__file__).with_name("additional_work_content.py"))],
                  gpu_seconds=0, model_calls=0, scoring_calls=0)
    (output / "assembly.json").write_text(json.dumps(record, indent=2) + "\n")
    (output / "sources.md").write_text("# FIN-1 source registry\n\n" + table(
        ["ID", "File", "SHA256"], [[key, sources[key], row["sha256"]] for key, row in bindings.items()]
    ) + "\n\nReceipt identities and unknown failed-launch logs are in `assembly.json`.\n")
    (output / "costs.md").write_text("# Nonoverlapping enclosing receipts\n\n" + table(
        ["Group", "Receipt", "Status", "Field", "Seconds"],
        [[r["group"], os.path.relpath(r["path"], root), r["status"], r["field"], r["seconds"]]
         for r in accounting["receipts"]]) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.output, args.document)
    print(json.dumps(dict(document=result["document"]["path"],
                          known_process_hours=result["accounting"]["known_process_seconds"] / 3600,
                          unknown_attempts=len(result["accounting"]["unknown_attempts"]))))


if __name__ == "__main__":
    main()
