"""Validate R1 fixes in new candidate files without editing the staged originals.

This is a temporary review harness, not a second episode implementation. Candidate
hashes and original hashes must match the prepared edit-request inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("baseline", "tests"))
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError("output must be a new file in pc_cap")
    inventory = json.loads((ROOT / "docs/tasks/R1-created-files-repairs.json").read_text())
    for original, rec in inventory.items():
        for name, expected in ((original, rec["original_sha256"]), (rec["candidate"], rec["candidate_sha256"])):
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"prepared source changed: {name}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.action == "baseline":
        original = "scripts/r1_00_baseline.py"
        path = ROOT / inventory[original]["candidate"]
        spec = importlib.util.spec_from_file_location("r1_proposed_baseline", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        # Logical destination determines ROOT/default arguments. No file is changed.
        mod.__file__ = str(ROOT / original)
        exec(compile(path.read_text(), str(path), "exec"), mod.__dict__)
        sys.argv = [str(Path(__file__)), "--output", str(output)]
        return mod.main()
    rec = inventory["tests/revision_v1/test_episodes.py"]
    test_source = (ROOT / rec["candidate"]).read_text()
    candidate = ROOT / inventory["scripts/r1_20_episodes.py"]["candidate"]
    test_source = test_source.replace("ROOT = Path(__file__).resolve().parents[2]", f"ROOT = Path({str(ROOT)!r})")
    test_source = test_source.replace('MODULE = ROOT / "scripts/r1_20_episodes.py"', f"MODULE = Path({str(candidate)!r})")
    test_source = test_source.replace("sys.path.insert(0, 'scripts')", f"sys.path.insert(0, {str(candidate.parent)!r})")
    test_path = output.with_suffix(".test.py")
    with test_path.open("x") as f:
        f.write(test_source)
    env = {**os.environ, "JAX_PLATFORMS": "cpu", "CUDA_VISIBLE_DEVICES": "",
           "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2"}
    with output.open("x") as f:
        result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--import-mode=importlib", "-p", "no:cacheprovider", str(test_path)],
                                cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
    print(output.read_text())
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
