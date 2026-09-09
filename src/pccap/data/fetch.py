"""``python -m pccap.data.fetch --verify`` (DATA-00): re-hash every recorded asset file.

Thin wrapper around ``scripts/fetch_assets.py`` so the verify command of the plan works from
the package; it imports nothing from ``pccap.bases`` or ``pccap.harness``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "fetch_assets.py"


def _load():
    spec = importlib.util.spec_from_file_location("fetch_assets", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None) -> int:
    return _load().main(argv)


if __name__ == "__main__":
    sys.exit(main())
