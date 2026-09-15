"""R1-57b independent inventories: 360 Stage 4 cells and three-dataset development."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
from scripts.r1_57_dev_inventory import build as build_previous

from pccap.revision_v1.analysis import validate_inventory
from pccap.revision_v1.analysis_stage4 import expected_inventory
from pccap.revision_v1.stage4_cell import ROOT, sha, write_json


def build_development():
    inv = build_previous()
    inv["axes"]["datasets"].append("mquake")
    tri_conditions = [f"tri_v3_seed{s}" for s in range(3)]
    inv["axes"]["conditions"].extend(tri_conditions)
    dev_path = ROOT / "manifests/dev/mquake_dev.json"
    s0_path = ROOT / "manifests/dev/s0_sample.json"
    dev = json.loads(dev_path.read_text())
    s0 = {r["item_id"] for r in json.loads(s0_path.read_text())["items"]}
    pool = [r for r in dev["items"] if r["item_id"] not in s0] or dev["items"]
    selected = [pool[i] for i in sorted(np.random.default_rng(21).permutation(len(pool))[:100])]
    ids = [r["item_id"] for r in selected]
    outside = [r["item_id"] for r in dev["items"] if r["item_id"] not in ids][:100]
    inv["populations"].append(
        {
            "dataset": "mquake",
            "realization": "dev21",
            "order": "source_order",
            "item_ids": ids,
            "paraphrase_counts": [len(r["paraphrases"]) for r in selected],
            "locality_ids": [
                hashlib.sha256(q.encode()).hexdigest() for q in dev["unrelated_prompts"][:50]
            ],
            "checkpoints": {"end": 100},
            "endpoints": {
                "unseen_false_fire": {
                    "expected_ids": outside,
                    "id_key": "item_id",
                    "row_metric": "false_fire",
                    "required": False,
                },
                "composition": {
                    "expected_ids": [],
                    "id_key": "composition_id",
                    "row_metric": "composition_success",
                    "required": False,
                },
            },
        }
    )
    # Direct composition has no independently assigned development case set yet.
    # A legacy inventory cannot represent a zero planned endpoint: keep it
    # explicitly unbound in the wrapper, rather than inventing cases.
    inv["populations"][-1]["endpoints"].pop("composition")
    inv["composition_status"] = (
        "unbound development case membership; no direct composition results supplied or inferred"
    )
    inv["source_bindings_sha256"][str(dev_path.relative_to(ROOT))] = sha(dev_path)
    existing = copy.deepcopy(inv["cells"])
    for condition in ("text_null_v2", "rare_gate_v3"):
        template = next(c for c in existing if c["condition"] == condition)
        inv["cells"].append(
            {
                **template,
                "dataset": "mquake",
                "stream_dir": None,
                "stream_summary": None,
                "expected_args": {**template["expected_args"], "dataset": "mquake"},
                "endpoints": {},
            }
        )
    for ds in inv["axes"]["datasets"]:
        for seed, condition in enumerate(tri_conditions):
            tag = f"tri_text_s{seed}_rare1_null0.5" + (f"@{ds}" if ds != "zsre" else "")
            weights = (
                ROOT.parent / f"assets/runs/pc_cap/R1/pilot/r1_50_stream_tri_text_s{seed}/theta.npz"
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
                        "rare_overlap": 1,
                        "theta": str(weights),
                    },
                    "admitted": None,
                    "endpoints": {},
                }
            )
    inv["contrasts"].extend(
        {"id": f"tri_seed{s}_minus_two_source_v3", "treatment": c, "control": "rare_gate_v3"}
        for s, c in enumerate(tri_conditions)
    )
    inv["interpretation"] = (
        "one reused development population per dataset; reader seeds are separate conditions, not independent data replicates; all contrasts descriptive"
    )
    inv["provenance"] += (
        "; MQuAKE follows the same generic load_dev_items seed-21 recipe, not a fresh draw"
    )
    validate_inventory(inv)
    return inv


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", choices=("stage4", "development"), required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT / "logs"):
        ap.error("new inventory file under logs required")
    inv = expected_inventory() if args.kind == "stage4" else build_development()
    write_json(args.output, inv)
    print(
        json.dumps(
            {
                "kind": args.kind,
                "cells": len(inv["cells"]),
                "datasets": inv["axes"]["datasets"],
                "fresh_draws": 0,
                "payload_seals": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
