"""Sibling-repository reference recorder (ENV-04 under lead directive DEC-003).

The PyTorch sibling ``llm-by-neural-predictive-coding`` is **read-only reference material**: it
is never imported at runtime (no torch in the project environment, DEC-001) and no file is copied
(no licence, plan2 §2). This module pins *which* checkout the re-implemented formulas were read
from, so that every ``# reproduces hdpc/<file>:<lines>`` header in ``pccap`` can be audited.

``record()`` writes the ``sibling`` section of ``manifests/assets.json``:
``{path, commit, dirty, dirty_diff_sha256, licence: "unknown", torch_pin, transformers_pin}``.

``reference(name)`` returns the absolute path of a sibling source file for *reading* (tests
assert it exists) and raises ``SiblingUnavailable`` with a structured payload otherwise.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT.parent / "llm-by-neural-predictive-coding"
PINNED_COMMIT = "298fc719a0bb3e50a2b818990dd61ccca438ee62"
ASSETS_JSON = ROOT / "manifests" / "assets.json"

REFERENCE_FILES = {
    "wrap": "src/hdpc/wrap.py",
    "energy": "src/hdpc/energy.py",
    "relax": "src/hdpc/relax.py",
    "checkpoint": "src/hdpc/checkpoint.py",
    "train_distill": "src/hdpc/train_distill.py",
    "model_source": "src/hdpc/model_source.py",
    "prepare": "src/hdpc/reproduction/prepare.py",
    "fidelity": "src/hdpc/reproduction/fidelity.py",
    "summary_50m": "results/distillation/50m-tokens/summary.json",
    "terminal_fidelity": "results/distillation/terminal-fidelity.json",
}


class SiblingUnavailable(RuntimeError):
    def __init__(self, name: str, path: Path, reason: str):
        super().__init__(f"sibling reference '{name}' unavailable at {path}: {reason}")
        self.payload = {"status": "unavailable", "name": name, "path": str(path), "reason": reason}


def sibling_path() -> Path:
    return Path(os.environ.get("PCCAP_HDPC_PATH", str(DEFAULT_PATH))).resolve()


def _git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def inspect(path: Path | None = None) -> dict:
    p = path or sibling_path()
    if not (p / ".git").exists():
        raise SiblingUnavailable("repo", p, "not a git checkout")
    commit = _git(p, "rev-parse", "HEAD")
    diff = subprocess.check_output(["git", "-C", str(p), "diff", "HEAD"], text=True)
    untracked = _git(p, "ls-files", "--others", "--exclude-standard")
    dirty = bool(diff.strip()) or bool(untracked.strip())
    req = p / "cluster" / "requirements.txt"
    pins = {}
    if req.exists():
        for line in req.read_text().splitlines():
            m = re.match(r"^(torch|transformers|numpy|pytest)==([\w.+]+)", line.strip())
            if m:
                pins[m.group(1)] = m.group(2)
    licence = "unknown"
    for cand in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        if (p / cand).exists():
            licence = cand
    return {
        "path": str(p),
        "commit": commit,
        "pinned_commit": PINNED_COMMIT,
        "commit_matches_pin": commit == PINNED_COMMIT,
        "dirty": dirty,
        "dirty_diff_sha256": hashlib.sha256((diff + untracked).encode()).hexdigest(),
        "licence": licence,
        "pins": pins,
        "usage": "read-only reference; no runtime import; no files copied (DEC-003)",
    }


def record(path: Path | None = None) -> dict:
    info = inspect(path)
    doc = {}
    if ASSETS_JSON.exists():
        doc = json.loads(ASSETS_JSON.read_text())
    doc["sibling"] = info
    ASSETS_JSON.parent.mkdir(parents=True, exist_ok=True)
    ASSETS_JSON.write_text(json.dumps(doc, indent=1) + "\n")
    return info


def reference(name: str) -> Path:
    p = sibling_path()
    rel = REFERENCE_FILES.get(name)
    if rel is None:
        raise SiblingUnavailable(name, p, "no such reference key")
    f = p / rel
    if not f.exists():
        raise SiblingUnavailable(name, f, "file missing")
    return f


def main() -> int:
    info = record()
    print(json.dumps(info, indent=1))
    return 0 if info["commit_matches_pin"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
