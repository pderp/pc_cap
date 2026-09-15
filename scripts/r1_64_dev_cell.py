"""Execute or inspect an explicitly unsealed development cell; never a confirmation launcher."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.r1_61_cell_driver import construct_owner_adapter

from pccap.revision_v1.development_cell import (
    BANNER,
    MODE,
    OUTPUT_ROOT,
    RESOURCE_ROOT,
    load_development_cell,
    run_development_cell,
)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--manifest-sha256", required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args(argv)
    m, p = load_development_cell(a.manifest, a.manifest_sha256)
    if a.resume and not a.execute:
        ap.error("--resume requires --execute")
    if not a.execute:
        print(
            json.dumps(
                {
                    "mode": MODE,
                    "banner": BANNER,
                    "cell": m["cell"],
                    "checkpoints": m["checkpoints"],
                    "items": len(p["items"]),
                    "model_constructed": False,
                    "payload_opened": True,
                },
                indent=2,
            )
        )
        return 0
    if m.get("test_fixture"):
        ap.error("TinyBase fixtures run through the Python API only")
    adapter, tok = construct_owner_adapter(m)
    result = run_development_cell(
        a.manifest,
        a.manifest_sha256,
        adapter,
        tok,
        output_root=OUTPUT_ROOT,
        resource_root=RESOURCE_ROOT,
        resume=a.resume,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
