"""Render docs/tasks/STATUS.md from manifests/tasks.json (updated_plan2.md §4.4).

A task is ``ready`` when every dependency is ``done``. Usage::

    python -m pccap.harness.status            # regenerate STATUS.md and print a summary
    python -m pccap.harness.status --set ID status=in_progress agent=NAME [key=value ...]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASKS = ROOT / "manifests" / "tasks.json"
STATUS_MD = ROOT / "docs" / "tasks" / "STATUS.md"

TERMINAL = {"done"}
STAGE_ORDER = ["ENV", "DATA", "S0", "REG", "GRAM", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]


def load() -> dict:
    return json.loads(TASKS.read_text())


def save(doc: dict) -> None:
    TASKS.write_text(json.dumps(doc, indent=1) + "\n")


def effective_status(row: dict, by_id: dict[str, dict]) -> str:
    if row["status"] != "pending":
        return row["status"]
    if all(by_id[d]["status"] in TERMINAL for d in row["deps"]):
        return "ready"
    return "pending"


def render(doc: dict) -> str:
    rows = doc["tasks"]
    by_id = {r["id"]: r for r in rows}
    counts: dict[str, int] = {}
    for r in rows:
        s = effective_status(r, by_id)
        counts[s] = counts.get(s, 0) + 1
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [
        "# Task status board",
        "",
        f"Regenerated {now} from `manifests/tasks.json` by `python -m pccap.harness.status`.",
        "Do not edit by hand.",
        "",
        "| status | count |",
        "| --- | ---: |",
    ]
    for s in ["done", "in_progress", "review", "partial", "blocked", "failed", "ready", "pending"]:
        if s in counts:
            out.append(f"| {s} | {counts[s]} |")
    gpu_total = sum(r.get("gpu_seconds", 0.0) for r in rows)
    out += ["", f"GPU seconds charged to tasks so far: {gpu_total:.0f}", ""]
    for stage in STAGE_ORDER:
        srows = [r for r in rows if r["stage"] == stage]
        if not srows:
            continue
        out += [f"## {stage}", "", "| ID | title | status | role | deps | GPU | review | agent | commit | note |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in srows:
            s = effective_status(r, by_id)
            out.append(
                f"| {r['id']} | {r['title']} | **{s}** | {r['role']} | {', '.join(r['deps']) or '—'} | "
                f"{r['gpu']} | {'yes' if r['review'] else 'no'} | {r.get('agent') or ''} | "
                f"{(r.get('commit') or '')[:8]} | {r.get('note') or ''} |"
            )
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs="+", metavar="KV", help="ID key=value ...")
    args = ap.parse_args(argv)
    doc = load()
    if args.set:
        tid, *kvs = args.set
        by_id = {r["id"]: r for r in doc["tasks"]}
        if tid not in by_id:
            raise SystemExit(f"unknown task {tid}")
        row = by_id[tid]
        for kv in kvs:
            k, v = kv.split("=", 1)
            if k in ("gpu_seconds", "wall_seconds"):
                row[k] = float(v)
            elif k == "evidence":
                row[k] = [x for x in v.split(",") if x]
            else:
                row[k] = v
        if row.get("status") == "in_progress" and not row.get("started"):
            row["started"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        if row.get("status") in ("done", "partial", "blocked", "failed") and not row.get("finished"):
            row["finished"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        save(doc)
    STATUS_MD.parent.mkdir(parents=True, exist_ok=True)
    STATUS_MD.write_text(render(doc) + "\n")
    by_id = {r["id"]: r for r in doc["tasks"]}
    ready = [r["id"] for r in doc["tasks"] if effective_status(r, by_id) == "ready"]
    done = [r["id"] for r in doc["tasks"] if r["status"] == "done"]
    print(f"STATUS.md written: {len(done)} done, ready: {', '.join(ready) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
