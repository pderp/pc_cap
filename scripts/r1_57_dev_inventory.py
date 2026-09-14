"""Independent R1-57 development inventory; never discover cells from outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def build():
    sources = {}

    def read(name):
        p = ROOT / name
        raw = p.read_bytes()
        sources[name] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    s0 = {r["item_id"] for r in read("manifests/dev/s0_sample.json")["items"]}
    primary = read("manifests/revision_v1/primary_condition_v3.json")
    read("manifests/revision_v1/primary_condition_v2.json")
    challenge = read("manifests/dev/challenges.json")
    inv = {
        "schema_version": 1,
        "scope": "development",
        "axes": {
            "datasets": ["zsre", "counterfact"],
            "conditions": ["text_null_v2", "rare_gate_v3"],
            "realizations": ["dev21"],
            "orders": ["source_order"],
        },
        "populations": [],
        "cells": [],
        "contrasts": [
            {
                "id": "rare_gate_minus_no_gate",
                "treatment": "rare_gate_v3",
                "control": "text_null_v2",
            }
        ],
        "provenance": "predeclared dev manifest, S0 exclusion, seed-21 subset sorted into source order; no observed-result-derived expected items",
        "interpretation": "one overlapping-development population per dataset, seed-0 reader; no cluster CI or confirmation claim",
        "multiplicity": "descriptive dry run only",
    }
    for ds in inv["axes"]["datasets"]:
        dev = read(f"manifests/dev/{ds}_dev.json")
        pool = [r for r in dev["items"] if r["item_id"] not in s0] or dev["items"]
        selected = [pool[i] for i in sorted(np.random.default_rng(21).permutation(len(pool))[:100])]
        ids = [r["item_id"] for r in selected]
        outside = [r["item_id"] for r in dev["items"] if r["item_id"] not in ids][:100]
        endpoints = {
            "unseen_false_fire": {
                "expected_ids": outside,
                "id_key": "item_id",
                "row_metric": "false_fire",
                "summary_path": ["summary"],
                "summary_metric": "false_fire_rate_full_inventory",
                "required": False,
            }
        }
        if ds == "counterfact":
            for name, source_key, field in (
                ("near_miss", "near_neighbour", "preserved"),
                ("revision", "temporal_correction", "revision_success"),
            ):
                endpoints[name] = {
                    "expected_ids": [
                        hashlib.sha256(
                            json.dumps(r, sort_keys=True, ensure_ascii=False).encode()
                        ).hexdigest()
                        for r in challenge[source_key]["items"][:100]
                    ],
                    "row_metric": field,
                    "summary_path": [name, "summary"],
                    "required": False,
                }
        inv["populations"].append(
            {
                "dataset": ds,
                "realization": "dev21",
                "order": "source_order",
                "item_ids": ids,
                "paraphrase_counts": [len(r["paraphrases"]) for r in selected],
                "locality_ids": [
                    hashlib.sha256(x.encode()).hexdigest() for x in dev["unrelated_prompts"][:50]
                ],
                "checkpoints": {"end": 100},
                "endpoints": endpoints,
            }
        )
        for condition, stream_tag, endpoint_tag, gate in (
            ("text_null_v2", "mixed_text_null0.5", "text_s0_v1", None),
            ("rare_gate_v3", "mixed_text_rare1_null0.5", "text_s0_rare1_v1", 1),
        ):
            tag = stream_tag + (f"@{ds}" if ds != "zsre" else "")
            outside_tag = "text_s0_v1" if gate is None else "text_s0_rare1_n100"
            ep_root = f"results/R1/endpoints/{endpoint_tag}"
            unseen_root = f"results/R1/endpoints/{outside_tag}_unseen_{ds}"
            ep_paths = {
                "unseen_false_fire": {
                    "summary": unseen_root + "/summary.json",
                    "rows": unseen_root + "/report.json",
                }
            }
            if ds == "counterfact":
                ep_paths.update(
                    {
                        name: {
                            "summary": ep_root + "/summary.json",
                            "rows": ep_root + f"/{name}_rows.json",
                        }
                        for name in ("near_miss", "revision")
                    }
                )
            inv["cells"].append(
                {
                    "dataset": ds,
                    "condition": condition,
                    "realization": "dev21",
                    "order": "source_order",
                    "stream_dir": f"results/R1/streams_revision/{tag}",
                    "stream_summary": f"results/R1/stream_eval_{tag}.json",
                    "expected_args": {
                        "dataset": ds,
                        "stream_seed": 21,
                        "n": 100,
                        "delta_steps": 5,
                        "fast_steps": 0,
                        "rare_overlap": gate,
                        "theta": primary["weights"]["seed0"]["path"],
                    },
                    "admitted": None,
                    "endpoints": ep_paths,
                }
            )
    inv["source_bindings_sha256"] = sources
    return inv


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT / "logs"):
        raise ValueError("new inventory under logs required")
    result = build()
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        "Independent development inventory: 4 declared cells, 1 realization/order per dataset; no draw."
    )


if __name__ == "__main__":
    main()
