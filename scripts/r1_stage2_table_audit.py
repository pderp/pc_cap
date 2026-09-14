"""R1-X4 supplemental audit of all 30 rows in results/R1/stream_eval.md."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from r1_stage2_recount import METRICS, ROOT, cell_check, sha


def audit(snapshot):
    snapshot = Path(snapshot)
    saved = json.loads(snapshot.read_text())
    sources = dict(saved["sources_sha256"])
    sources[str(snapshot.resolve())] = sha(snapshot)
    sources[str(Path(__file__).resolve())] = sha(__file__)
    for path, expected in sources.items():
        if sha(path) != expected:
            raise ValueError("audit source changed: " + path)
    rows = []
    for table in saved["raw_stream_markdown_tables"]:
        for row in table["rows"]:
            c = row["cells"]
            candidates = [s for s in saved["streams"] if s["tag"] == c[0]]
            compared = []
            for s in candidates:
                checks = [
                    cell_check(c[i + 3], s["summary_metrics"][k]) for i, k in enumerate(METRICS)
                ]
                checks += [
                    cell_check(c[2], s["args"]["null_threshold"]),
                    cell_check(
                        c[7],
                        [
                            s["null_mass"][k + "_mean"]
                            for k in ("prompt", "paraphrase", "unrelated")
                        ],
                    ),
                    cell_check(
                        c[8],
                        [
                            s["null_mass"][k + "_hard_null_rate"]
                            for k in ("prompt", "paraphrase", "unrelated")
                        ],
                    ),
                    cell_check(c[9], s["wall_seconds"]),
                ]
                a = s["args"]
                step_string = (
                    str(a["fast_steps"])
                    if "c/" not in c[1]
                    else str(a["fast_steps"]) + "c/" + str(a.get("delta_steps", 0)) + "d"
                )
                checks.append(
                    {
                        "printed": c[1],
                        "source_value": step_string,
                        "status": "agrees" if c[1] == step_string else "mismatch",
                    }
                )
                compared.append(
                    {
                        "tag": s["tag"],
                        "dataset": s["dataset"],
                        "source": s["path"],
                        "checks": checks,
                        "matches": all(
                            x["status"] in ("agrees", "agrees_at_printed_precision") for x in checks
                        ),
                    }
                )
            matches = [x for x in compared if x["matches"]]
            rows.append(
                {
                    "line": row["line"],
                    "cells": c,
                    "status": "unique_match"
                    if len(matches) == 1
                    else "ambiguous"
                    if matches
                    else "mismatch",
                    "attribution_method": "tag candidates then displayed numeric values; historical table omits dataset",
                    "matches": matches,
                    "candidates": compared,
                }
            )
    return {
        "task": "R1-X4",
        "rows": rows,
        "rows_checked": len(rows),
        "unique_matches": sum(r["status"] == "unique_match" for r in rows),
        "numeric_cells_checked": sum(
            len(r["matches"][0]["checks"]) - 1 for r in rows if len(r["matches"]) == 1
        ),
        "sources_sha256": sources,
        "gpu_seconds": 0,
        "model_queries_executed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", type=Path, default=ROOT / "logs/r1_round5/stage2_recount_v2.json")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    result = audit(a.snapshot)
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with a.output.open("x") as f:
        f.write(payload)
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "sources_sha256")}))


if __name__ == "__main__":
    main()
