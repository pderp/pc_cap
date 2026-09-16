"""HT-1b: use the unchanged HT-1 auditor on a bound v5/v4 development snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts import ht_audit_existing as ht

CELLS = {
    "v4": "R1_learned_ff-zsre-development-source-9084e84fc6dd00038904",
    "v5_full": "R1_learned_ff-zsre-development-source-d22ce6801209c6184480",
    "v5_incremental": "R1_learned_ff-zsre-development-source-48f8a79c8742635bf611",
}
PATTERNS = tuple(
    f"stage4_dev_cells/{cell}/attempt-0000/checkpoint-{n}.json"
    for cell in CELLS.values()
    for n in (100, 300)
) + ("endpoints/v5_rare1*/*.json", "drift_assay_r1_50_stream_sel6_text_s2_*.json")


def binding(path):
    return {
        "path": str(path.relative_to(ht.ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def comparisons(report):
    root = ht.ROOT / "results/R1/stage4_dev_cells"
    documents = {
        k: json.loads((root / c / "attempt-0000/checkpoint-300.json").read_text())
        for k, c in CELLS.items()
    }
    drift = {k: d["endpoints"]["drift"] for k, d in documents.items()}
    identities = {}
    for k, d in drift.items():
        identities[k] = [
            (d["source_sha256"], r["item_id"], r["capoff"], r["original"]) for r in d["rows"]
        ]
    shared = identities["v4"] == identities["v5_full"] == identities["v5_incremental"]
    data_equal = {
        k: documents["v5_full"][k] == documents["v5_incremental"][k]
        for k in documents["v5_full"]
        if k not in ("mode", "banner")
    }
    positions = {}
    for k in drift:
        source = f"results/R1/stage4_dev_cells/{CELLS[k]}/attempt-0000/checkpoint-300.json"
        positions[k] = {
            s["metric"]: s["statistics"]
            for s in report["series"]
            if s["source"] == source and s["address"] == "$.endpoints.drift.rows"
        }
    paired = {}
    if shared:
        for ref in ("capoff", "original"):
            values = [
                (b["cap"] - b[ref]) - (a["cap"] - a[ref])
                for a, b in zip(drift["v4"]["rows"], drift["v5_full"]["rows"], strict=True)
            ]
            paired[ref] = ht.statistics(values, [r["item_id"] for r in drift["v4"]["rows"]])
    logpaths = sorted(
        set((ht.ROOT / "results/R1").glob("unseen_v5_rare1_*.log"))
        | set((ht.ROOT / "results/R1").glob("drift_assay_v5_*.log"))
        | {(ht.ROOT / "results/R1/endpoints_v5_rare1.log")}
    )
    return {
        "task": "HT-1b",
        "cells": CELLS,
        "drift_statistics": positions,
        "v4_v5_exact_ordered_source_position_and_both_reference_nll_match": shared,
        "v5_full_incremental_checkpoint300_equal_fields": data_equal,
        "paired_v5_minus_v4_signed_harm": paired,
        "log_bindings": [binding(p) for p in logpaths],
        "producer": binding(Path(__file__).resolve()),
        "ht1_engine": binding(Path(ht.__file__).resolve()),
        "limits": [
            "Full/incremental are the same saved scientific observations, not independent runs.",
            "v4/v5 drift pairs share exact source digest, ordered position IDs and both reference NLL vectors.",
            "Different trained-reader families/seeds: this pair is descriptive, not an isolated averaging effect.",
            "32-window drift reports are aggregate-only: no tails or row-level pairing can be recovered.",
            "Unseen outside populations across occupancy differ (see R1-X12), so flatness is not established.",
            "The unchanged HT-1 missing-data inventory includes aggregate-only summaries and unsupported observations.",
            "Top-level endpoint row arrays are exposed by this wrapper; statistics and pair keys remain the original HT-1 implementation.",
            "No inference of a power law; positions within windows are dependent; no iid position intervals.",
        ],
        "model_calls": 0,
        "gpu_seconds": 0,
    }


def run(output):
    output = output.resolve()
    if output.exists() or not output.is_relative_to(ht.ROOT / "logs/heavy_tail"):
        raise ValueError("new directory under logs/heavy_tail required")
    original_patterns, original_rows = ht.PATTERNS, ht.row_sets

    def rows(value, address="$", context=None):
        if (
            isinstance(value, list)
            and value
            and all(isinstance(r, dict) and ("item_id" in r or "case_id" in r) for r in value)
        ):
            yield address, value, context or {}
        else:
            yield from original_rows(value, address, context)

    output.mkdir(parents=True, exist_ok=False)
    try:
        ht.PATTERNS, ht.row_sets = PATTERNS, rows
        report = ht.audit(output)
    finally:
        ht.PATTERNS, ht.row_sets = original_patterns, original_rows
    result = comparisons(report)
    with (output / "v5_comparison.json").open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps(result["drift_statistics"], indent=2))


if __name__ == "__main__":
    main()
