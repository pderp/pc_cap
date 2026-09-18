"""Typed cost evidence checks; a lead flag cannot turn missing measurements into data."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


def read(binding):
    p = Path(binding["path"])
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError("cost evidence identity changed: " + str(p))
    return json.loads(raw)


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def validate(receipt):
    if receipt.get("cost_schema_version") != 2:
        raise ValueError("typed cost schema v2 required")
    # Original schema-v2 receipts predate the revision field. Never route a new
    # revision through the old generic validator just because its fields fit.
    revision = receipt.get("receipt_revision", 2)
    if type(revision) is not int or revision not in (2, 3, 4):
        raise ValueError("unsupported typed cost receipt revision; explicit validator required")
    if receipt.get("pending_evidence"):
        raise ValueError("cost evidence pending: " + "; ".join(receipt["pending_evidence"]))
    if revision == 3:
        from scripts.r1_58j_cost_receipt import validate_supplement

        validate_supplement(receipt)
    if revision == 4:
        from scripts.r1_58l_cost_v4 import validate_supplement

        validate_supplement(receipt)
    sources = receipt["bindings"]
    for name, b in sources.items():
        if name == "cell_ceilings":
            continue
        path = Path(b["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != b["sha256"]:
            raise ValueError("cost source changed: " + name)
    ceilings = read(sources["cell_ceilings"])["cells"]
    cells = receipt.get("cells", [])
    keys = [c["condition"] + ":" + c["dataset"] for c in cells]
    if len(keys) != len(set(keys)) or set(keys) != set(ceilings):
        raise ValueError("all27 unique cost rows required")
    if (
        receipt.get("shared_process_hours") != 750
        or receipt.get("host_mem_available_floor_mib") != 6144
    ):
        raise ValueError("declared process budget or host launch floor differs")
    for c, key in zip(cells, keys, strict=True):
        evidence = read(c["measurement"])
        if evidence.get("pending") or evidence.get("full_endpoint_evidence_status") != "complete":
            raise ValueError("pending measured cost row: " + key)
        if c["wall_seconds"] != ceilings[key]["ceiling_seconds"]:
            raise ValueError("wall ceiling differs: " + key)
        for field in ("peak_host_mib", "peak_device_mib"):
            measured = evidence.get(field.replace("peak_", "measured_peak_"))
            if not positive(measured) or not positive(c.get(field)) or c[field] != measured * 1.5:
                raise ValueError("measured memory ceiling differs: " + key + ":" + field)
        for b in evidence["source_bindings"]:
            p = Path(b["path"])
            if hashlib.sha256(p.read_bytes()).hexdigest() != b["sha256"]:
                raise ValueError("measurement source changed: " + str(p))
    if receipt.get("full_validation_evidence_status") != "complete":
        raise ValueError("full validation cost evidence pending")
    return {"typed_cost_rows": len(cells), "evidence_complete": True}
