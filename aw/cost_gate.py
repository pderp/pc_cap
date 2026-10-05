"""Validate one reader_portfolio_cost JSON file against an explicit hours gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def hours(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def check(path, gate_hours):
    """No glob, fallback field, estimate substitution, or model execution."""
    path = Path(path)
    data = path.read_bytes()
    projection = json.loads(data, object_pairs_hook=_unique_object)
    if not isinstance(projection, dict) or "projected_process_hours" not in projection:
        raise ValueError("missing exact field: projected_process_hours")
    projected = hours(projection["projected_process_hours"], "projected_process_hours")
    gate = hours(gate_hours, "gate_hours")
    return dict(path=str(path.resolve()), sha256=hashlib.sha256(data).hexdigest(),
                projected_process_hours=projected, gate_hours=gate,
                status="PASS" if projected <= gate else "OVER_GATE",
                gpu_seconds=0, model_calls=0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Exact file path; extension optional")
    parser.add_argument("--gate-hours", type=float, required=True)
    args = parser.parse_args(argv)
    try:
        result = check(args.input, args.gate_hours)
    except (OSError, ValueError) as exc:
        print(json.dumps(dict(status="INVALID", error=str(exc))))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
