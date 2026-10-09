"""Paths, hashing, atomic writes and status bookkeeping shared by the ext-20261009 study."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # pc_cap
ASSETS = ROOT.parent / "assets"
RUN_ID = "ext-20261009"
OUT = ROOT / "results" / "extremes_analysis" / RUN_ID  # text: tables, audit, validation, reports, logs
DATA = ASSETS / "extremes_analysis" / RUN_ID  # parquet, vectors, figures, checkpoints
VENV_PYTHON = ROOT.parent / "venv" / "bin" / "python"
MPL_SITE = ASSETS / "envs" / "status-paper-20260911" / "lib" / "python3.12" / "site-packages"

FAMILIES = {
    "PCR": "PC-reader study: ePC-trained vs BP-trained reader, 3 paired seeds, realization 0 order 100, 300 edits, adjoint acquisition (GPT-2 small)",
    "FROZEN": "Frozen GPT-2 small without any cap (new direct evaluation in this study)",
    "S4": "Stage-4 confirmatory R1_learned_ff: selected v5 BP-trained reader, 3 realizations x 5 orders, 1,000 edits (300 MQuAKE)",
    "FV5": "Fixed-v5 acquisition credit: adjoint (SE-A) vs error inference (SE-E), realization 0 order 100, 300 edits (GPT-2 small)",
    "PCV0": "PC-v0 corrected credit on the regenerated ePC 50M base with the v0 live cap (NOT GPT-2 small)",
    "EXT": "New supplemental evaluations of this study (own manifest and run id)",
}

MODELS = {
    "frozen": dict(family="FROZEN", label="Frozen GPT-2 small (no cap)"),
    "bp_reader_s0": dict(family="PCR", label="GPT-2 + BP-trained reader, seed 0", rule="bp", seed=0),
    "bp_reader_s1": dict(family="PCR", label="GPT-2 + BP-trained reader, seed 1", rule="bp", seed=1),
    "bp_reader_s2": dict(family="PCR", label="GPT-2 + BP-trained reader, seed 2", rule="bp", seed=2),
    "epc_reader_s0": dict(family="PCR", label="GPT-2 + ePC-trained reader, seed 0", rule="epc", seed=0),
    "epc_reader_s1": dict(family="PCR", label="GPT-2 + ePC-trained reader, seed 1", rule="epc", seed=1),
    "epc_reader_s2": dict(family="PCR", label="GPT-2 + ePC-trained reader, seed 2", rule="epc", seed=2),
    "v5_stage4": dict(family="S4", label="GPT-2 + selected v5 reader (Stage 4, BP-trained)"),
    "v5_fixed_adjoint": dict(family="FV5", label="GPT-2 + v5 reader, adjoint credit (SE-A)"),
    "v5_fixed_error": dict(family="FV5", label="GPT-2 + v5 reader, error-inference credit (SE-E)"),
}

DATASETS = ("zsre", "counterfact", "mquake")


def sha(path: Path | str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def git_head(repo: Path = ROOT) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - provenance only
        return "unknown"


def atomic_write_bytes(path: Path | str, blob: bytes) -> str:
    """Temporary file then rename, so a crash never leaves a half-written artifact."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    with tmp.open("wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return sha_bytes(blob)


def atomic_json(path: Path | str, obj, *, indent: int = 2) -> str:
    return atomic_write_bytes(path, (json.dumps(obj, indent=indent, allow_nan=False, sort_keys=False) + "\n").encode())


def read_json(path: Path | str):
    return json.loads(Path(path).read_bytes())


def atomic_parquet(path: Path | str, frame) -> str:
    """Write a pandas frame as parquet atomically (pyarrow engine)."""
    import io

    buf = io.BytesIO()
    frame.to_parquet(buf, engine="pyarrow", index=False)
    return atomic_write_bytes(path, buf.getvalue())


def atomic_csv(path: Path | str, frame) -> str:
    return atomic_write_bytes(path, frame.to_csv(index=False).encode())


class Status:
    """STATUS.md and manifest.json bookkeeping; every stage appends, nothing is overwritten silently."""

    def __init__(self, out: Path = OUT):
        self.out = out
        self.manifest_path = out / "manifest.json"
        self.manifest = read_json(self.manifest_path) if self.manifest_path.exists() else dict(run_id=RUN_ID, created=now(), artifacts={}, stages={}, warnings=[])

    def artifact(self, key: str, path: Path | str, **meta):
        path = Path(path)
        rec = dict(path=str(path), sha256=sha(path) if path.exists() and path.is_file() else None, recorded=now(), **meta)
        self.manifest["artifacts"][key] = rec
        atomic_json(self.manifest_path, self.manifest)
        return rec

    def stage(self, name: str, status: str, **meta):
        rec = self.manifest["stages"].get(name, {})
        rec.update(status=status, updated=now(), code_sha=git_head(), **meta)
        self.manifest["stages"][name] = rec
        atomic_json(self.manifest_path, self.manifest)

    def warn(self, text: str):
        self.manifest["warnings"].append(dict(time=now(), text=text))
        atomic_json(self.manifest_path, self.manifest)


def log_line(name: str, text: str):
    p = OUT / "logs" / f"{name}.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(f"{now()} {text}\n")


def elapsed(t0: float) -> float:
    return time.monotonic() - t0
