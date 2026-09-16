"""Build an independently declared development analysis inventory from bound recipes.

Payloads are read only to copy planned IDs/denominators, never to infer completion.
This helper is not needed to reproduce analysis after the matrix is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.r1_75_analysis_stage4_v1 import ROOT, coordinate_id, validate_matrix

from pccap.revision_v1.endpoints import row_hash


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def population(payload):
    ep = payload["endpoints"]
    drift = ep["drift"]
    return {
        "item_ids": [r["item_id"] for r in payload["items"]],
        "paraphrase_counts": [len(r["paraphrases"]) for r in payload["items"]],
        "endpoints": {k: v["expected_ids"] for k, v in ep.items() if k != "drift"},
        "drift": {
            "expected_positions": drift["expected_positions"],
            "position_ids": [
                f"w{w}:p{p}" for w, row in enumerate(drift["windows"]) for p in range(1, len(row))
            ],
            "source_sha256": row_hash(drift),
        },
    }


def build(pairs):
    cells = []
    sources = {}
    for i, (recipe, directory) in enumerate(pairs, 1):
        recipe = Path(recipe).resolve()
        if not recipe.is_relative_to(ROOT / "docs/tasks"):
            raise PermissionError("development recipe under docs/tasks required")
        raw = recipe.read_bytes()
        sources[str(recipe)] = hashlib.sha256(raw).hexdigest()
        m = json.loads(raw)
        if m.get("mode") != "stage4_development_cell" or "reservations" in m or "protocol" in m:
            raise PermissionError("explicit unsealed development recipe required")
        p = Path(m["payload"]["path"]).resolve()
        if not p.is_relative_to(ROOT.parent / "assets/runs/pc_cap/R1/stage4_dev_payloads"):
            raise PermissionError("unsealed development payload only")
        before = sha(p)
        if before != m["payload"]["sha256"]:
            raise ValueError("payload binding mismatch")
        payload = json.loads(p.read_bytes())
        if sha(p) != before:
            raise ValueError("payload changed during read")
        sources[str(p)] = before
        c = {
            **m["cell"],
            "checkpoints": m["checkpoints"],
            "block_number": 1,
            "within_block_order": i,
            "result_dir": str(Path(directory).resolve()),
            "manifest_sha256": sources[str(recipe)],
            "code_sha256": m["code_sha256"],
            "payload_sha256": before,
            "adapter_identity": m["adapter_identity"],
            "population": population(payload),
            "admitted": False,
        }
        c["cell_id"] = coordinate_id(c)
        cells.append(c)
    out = {
        "schema_version": 1,
        "name": "R1-75_v5_development",
        "scope": "development",
        "cells": cells,
        "axes": {
            k: list(dict.fromkeys(c[k] for c in cells))
            for k in ("condition", "dataset", "realization", "order")
        },
        "contrasts": [],
        "multiplicity": {"status": "unresolved_U12"},
        "inventory_sources_sha256": sources,
    }
    out["axes"] = {
        {
            "condition": "conditions",
            "dataset": "datasets",
            "realization": "realizations",
            "order": "orders",
        }[k]: v
        for k, v in out["axes"].items()
    }
    for p, h in sources.items():
        if sha(p) != h:
            raise ValueError("inventory input changed")
    validate_matrix(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--recipe", type=Path, action="append", required=True)
    ap.add_argument("--cell-dir", type=Path, action="append", required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(argv)
    if len(a.recipe) != len(a.cell_dir):
        ap.error("one directory per recipe required")
    output = a.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "docs/tasks"):
        ap.error("new output under docs/tasks required")
    value = build(zip(a.recipe, a.cell_dir, strict=True))
    with output.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
