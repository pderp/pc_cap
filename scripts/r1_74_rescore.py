"""R1-74: DEC-053 rescoring of stored checkpoints; source files never overwritten."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def preservation_flags(reference, query, *, status="ok"):
    fields = (
        "preserved",
        "preserved_terminated",
        "truncated_pair",
        "reference_truncated",
        "query_truncated",
    )
    if status != "ok":
        return dict.fromkeys(fields)
    if not isinstance(reference, dict) or not isinstance(query, dict):
        raise ValueError("complete generation traces required")
    if any(
        not isinstance(x.get("generated"), str) or type(x.get("truncated")) is not bool
        for x in (reference, query)
    ):
        raise ValueError("generated text and explicit boolean truncation flags required")
    bounded = query["generated"] == reference["generated"]
    truncated = reference["truncated"] or query["truncated"]
    return {
        "preserved": bounded,
        "preserved_terminated": bounded and not truncated,
        "truncated_pair": truncated,
        "reference_truncated": reference["truncated"],
        "query_truncated": query["truncated"],
    }


def preservation_summary(rows, expected_ids):
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("unique planned case IDs required")
    ids = [r["item_id"] for r in rows]
    if len(ids) != len(set(ids)) or not set(ids) <= set(expected_ids):
        raise ValueError("duplicate/unexpected preservation row")
    available = [r for r in rows if r.get("status") == "ok"]
    fields = (
        "preserved",
        "preserved_terminated",
        "truncated_pair",
        "reference_truncated",
        "query_truncated",
    )
    if any(type(r.get(k)) is not bool for r in available for k in fields):
        raise ValueError("available row lacks preservation/truncation verdict")
    n = len(expected_ids)
    counts = {k + "_n": sum(r[k] for r in available) for k in fields}
    return {
        "expected_n": n,
        "scored_n": len(available),
        "unavailable_n": n - len(available),
        **counts,
        "preserved_fraction": counts["preserved_n"] / n if n and len(available) == n else None,
        "preserved_terminated_fraction": counts["preserved_terminated_n"] / n
        if n and len(available) == n
        else None,
        "status": "not_applicable"
        if not n
        else "complete"
        if len(available) == n
        else "incomplete",
        "primary_convention": "DEC-053 bounded exact decoded-text equality, no normalization or termination requirement",
        "secondary_convention": "same decoded text and neither side truncated",
    }


def rescore(report):
    out = copy.deepcopy(report)
    for section, key in (
        (out.get("locality"), "query"),
        (out.get("endpoints", {}).get("near_miss"), "neighbour_query"),
    ):
        if section is None:
            continue
        for row in section.get("rows", []):
            row["stored_preserved"] = row.get("preserved")
            row.update(
                preservation_flags(
                    row.get("reference"), row.get(key), status=row.get("status", "unavailable")
                )
            )
        if "expected_ids" not in section:
            raise ValueError("independent planned preservation IDs required")
        section["summary"] = preservation_summary(section["rows"], section["expected_ids"])
    return out


def audit(paths):
    reports = []
    for path in paths:
        path = Path(path).resolve()
        if not path.is_relative_to(ROOT / "results") or "confirm" in path.parts:
            raise PermissionError("local unsealed result checkpoint required")
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        source = json.loads(raw)
        revised = rescore(source)
        summary = {
            "path": str(path),
            "sha256": h,
            "checkpoint": source["checkpoint"],
            "locality": revised.get("locality", {}).get("summary"),
            "near_miss": revised.get("endpoints", {}).get("near_miss", {}).get("summary"),
            "status": "rescored existing traces; no experiment rerun",
        }
        if hashlib.sha256(path.read_bytes()).hexdigest() != h:
            raise ValueError("checkpoint changed while rescoring")
        reports.append(summary)
    return {
        "task": "R1-74",
        "reports": reports,
        "model_calls": 0,
        "gpu_seconds": 0,
        "existing_files_changed": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=Path, action="append", required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT / "logs"):
        ap.error("new output under logs required")
    result = audit(a.checkpoint)
    with a.output.open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
