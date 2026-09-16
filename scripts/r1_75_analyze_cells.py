"""Reproduce Stage-4 cell-directory JSON and Markdown analysis from a declared matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.r1_75_analysis_stage4_v1 import ROOT, analyze, markdown


def run(matrix_path, output_prefix):
    matrix_path = Path(matrix_path).resolve()
    if not (
        matrix_path.is_relative_to(ROOT / "docs/tasks")
        or matrix_path.is_relative_to(ROOT / "manifests/revision_v1")
    ):
        raise PermissionError("analysis matrix must be explicit repo metadata")
    prefix = Path(output_prefix).resolve()
    targets = [Path(str(prefix) + s) for s in (".json", ".md")]
    if any(p.exists() or not p.is_relative_to(ROOT / "logs") for p in targets):
        raise FileExistsError("both outputs must be new paths under logs")
    raw = matrix_path.read_bytes()
    value = analyze(json.loads(raw))
    value["matrix_file"] = {"path": str(matrix_path), "sha256": hashlib.sha256(raw).hexdigest()}
    value["analysis_source_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (
            Path(__file__),
            ROOT / "scripts/r1_75_analysis_stage4_v1.py",
            ROOT / "scripts/r1_74_rescore.py",
            ROOT / "src/pccap/revision_v1/analysis.py",
            ROOT / "scripts/ht_audit_existing.py",
        )
    }
    if matrix_path.read_bytes() != raw:
        raise ValueError("matrix changed during analysis")
    rendered = markdown(value)
    encoded = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    prefix.parent.mkdir(parents=True, exist_ok=True)
    targets[0].open("x").write(encoded)
    targets[1].open("x").write(rendered)
    return value


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--output-prefix", type=Path, required=True)
    a = ap.parse_args(argv)
    r = run(a.matrix, a.output_prefix)
    print(
        json.dumps(
            {
                "cells": len(r["cells"]),
                "complete_blocks": r["complete_blocks"],
                "incomplete_cells": len(r["incomplete_cells"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
