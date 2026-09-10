"""Freeze-gated confirmation loader (DATA-02a; PDF Appendix A, rule 4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pccap.data.confirmation_integrity import load_frozen_manifest

ROOT = Path(__file__).resolve().parents[3]


def load(
    manifest_path: str | Path,
    frozen: str | Path = ROOT / "manifests" / "frozen.json",
) -> dict[str, Any]:
    """Return one realization only after schema and frozen hash checks pass."""
    return load_frozen_manifest(manifest_path, frozen=frozen)
