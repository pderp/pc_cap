"""Strict JSON export for the Stage 2 recount, including nonfinite source sentinels.

Zero-training-step pilot summaries use Infinity for best-dev loss. Preserve that
provenance as an explicit nonfinite-source record, never a measured finite loss.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from r1_stage2_recount import ROOT, recount, sha


def finite_export(value):
    nonfinite = []

    def visit(obj, path):
        if isinstance(obj, float) and not math.isfinite(obj):
            nonfinite.append(
                {
                    "path": path,
                    "source_value": repr(obj),
                    "status": "nonfinite_source_value_not_a_measurement",
                }
            )
            return None
        if isinstance(obj, dict):
            return {k: visit(v, path + [k]) for k, v in obj.items()}
        if isinstance(obj, list):
            return [visit(v, path + [i]) for i, v in enumerate(obj)]
        return obj

    output = visit(value, [])
    output["nonfinite_source_fields"] = nonfinite
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    output = finite_export(recount())
    output["sources_sha256"][str(Path(__file__).resolve())] = sha(Path(__file__))
    payload = json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x") as f:
        f.write(payload)
    print(
        json.dumps(
            {
                **output["summary"],
                "nonfinite_source_fields": len(output["nonfinite_source_fields"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
