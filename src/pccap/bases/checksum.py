"""Base checksums (PDF Op. rule 10): SHA-256 over every parameter tensor in a fixed order.

Both wrappers use ``pccap.bases.bp._digest`` semantics through ``base.checksum()``; this module
exposes the run-level helper that records ``base_hash_before``/``base_hash_after``.
"""

from __future__ import annotations

import json
from pathlib import Path


def record_hash(run_dir: Path | str, base, when: str) -> str:
    """Write ``base_hash_<when>`` into ``config.json`` of ``run_dir`` and return the hash."""
    run_dir = Path(run_dir)
    h = base.checksum()
    cfg_path = run_dir / "config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg[f"base_hash_{when}"] = h
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg, indent=1))
    return h


def assert_frozen(before: str, after: str) -> None:
    if before != after:
        raise RuntimeError(f"base parameters changed during the run: {before[:12]} != {after[:12]}")
