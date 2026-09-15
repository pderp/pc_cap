"""Materialize hash-bound Hugging Face snapshot symlinks as immutable development resources."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from pccap.revision_v1.analysis import digest
from pccap.revision_v1.stage4_cell import ROOT, sha

RESOURCE_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/stage4_dev_bases"


def materialize_base(binding, output_root=RESOURCE_ROOT):
    """Read exact bound source bytes, copy once, reuse only an identical regular-file snapshot."""
    source = Path(binding["path"]).resolve()
    files = binding["files"]
    if not {"config.json", "model.safetensors", "tokenizer.json"} <= files.keys():
        raise ValueError("complete base/tokenizer file inventory required")
    target_root = Path(output_root).resolve()
    if not target_root.is_relative_to(ROOT.parent / "assets"):
        raise PermissionError("base resources belong under assets")
    for name, expected in files.items():
        if Path(name).name != name or name in (".", "..") or sha(source / name) != expected:
            raise ValueError("invalid source file name/hash")
    target = target_root / digest(files)
    if target.exists():
        if not target.is_dir() or set(p.name for p in target.iterdir()) != set(files):
            raise ValueError("incomplete materialized snapshot")
    else:
        target.mkdir(parents=True, exist_ok=False)
        for name in files:
            with (source / name).open("rb") as src, (target / name).open("xb") as dst:
                shutil.copyfileobj(src, dst)
    for name, expected in files.items():
        p = target / name
        if p.is_symlink() or not p.resolve().is_relative_to(target.resolve()) or sha(p) != expected:
            raise ValueError("materialized snapshot child mismatch")
    return {"path": str(target), "files": dict(files)}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--recipe", type=Path, required=True)
    a = ap.parse_args()
    m = json.loads(a.recipe.read_text())
    if m.get("mode") != "stage4_development_cell" or any(
        v is not False for v in m.get("admission", {}).values()
    ):
        ap.error("development recipe with no admission required")
    print(json.dumps(materialize_base(m["construction"]["base"]), indent=2))
