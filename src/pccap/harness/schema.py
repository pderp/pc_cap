"""JSON schemas for configs, decision records, metrics, costs and manifests (S0-03).

Kinds: ``config``, ``decision``, ``metric``, ``metrics``, ``cost``, ``manifest_dev``,
``manifest_frozen`` (requires every S4-01 field), ``assets``, ``tasks``, ``datasets``.

CLI::

    python -m pccap.harness.schema validate <file> [--kind KIND]

The kind is inferred from the file name when not given (``frozen.json`` → manifest_frozen,
``assets.json`` → assets, ``tasks.json`` → tasks, ``datasets.json`` → datasets, anything under
the confirm or dev manifest directories → manifest_frozen / manifest_dev). Validation errors list every
missing required field; the process exits non-zero.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

from pccap.harness.records import ALL_CODES

METRIC_STATUS = ["ok", "undefined", "unreachable", "unsupported", "unavailable"]

METRIC = {
    "type": "object",
    "required": ["value", "status", "units", "numerator", "denominator", "n", "strata", "exclusions"],
    "properties": {
        "value": {"type": ["number", "null"]},
        "status": {"enum": METRIC_STATUS},
        "units": {"type": "string"},
        "numerator": {"type": ["number", "null"]},
        "denominator": {"type": ["number", "null"]},
        "n": {"type": "integer", "minimum": 0},
        "strata": {"type": "object"},
        "exclusions": {"type": "array"},
    },
    "additionalProperties": True,
}

COST_COLUMN = {
    "type": "object",
    "required": ["full_forwards", "partial_forwards", "reverses", "settle_iters", "prefix_microsteps",
                 "router_probes", "search_candidates", "memory_search_seconds", "wall_seconds",
                 "accel_seconds", "peak_mem_mib"],
    "properties": {k: {"type": "number"} for k in [
        "full_forwards", "partial_forwards", "reverses", "settle_iters", "prefix_microsteps",
        "router_probes", "search_candidates", "memory_search_seconds", "wall_seconds",
        "accel_seconds", "peak_mem_mib", "tokens"]},
}

COST = {
    "type": "object",
    "required": ["query", "learning", "total"],
    "properties": {"query": COST_COLUMN, "learning": COST_COLUMN, "total": COST_COLUMN},
}

DECISION = {
    "type": "object",
    "required": ["item_digest", "prefix_index", "round", "candidate_banks", "signed_scores",
                 "chosen_route", "accepted_increment", "loss_before", "loss_after", "codes", "cost"],
    "properties": {
        "item_digest": {"type": "string", "pattern": "^[0-9a-f]{32}$"},
        "prefix_index": {"type": "integer", "minimum": 0},
        "round": {"type": "integer", "minimum": 0},
        "candidate_banks": {"type": "array", "items": {"enum": [1, 2, 3]}},
        "signed_scores": {"type": "object", "additionalProperties": {"type": "number"}},
        "chosen_route": {"type": "array", "items": {"enum": [1, 2, 3]}},
        "accepted_increment": {"type": "object", "additionalProperties": {"type": "number"}},
        "loss_before": {"type": "number"},
        "loss_after": {"type": "number"},
        "codes": {"type": "array", "items": {"enum": list(ALL_CODES)}},
        "cost": {"type": "object"},
        "rule": {"type": "string"},
    },
}

METRICS_FILE = {
    "type": "object",
    "required": ["stage", "metrics"],
    "properties": {
        "stage": {"type": "string"},
        "arm": {"type": "string"},
        "base": {"type": "string"},
        "metrics": {"type": "object", "additionalProperties": METRIC},
    },
}

_COMMON_MANIFEST_PROPS = {
    "name": {"type": "string"},
    "mode": {"enum": ["dev", "confirm"]},
    "stage": {"type": "string"},
    "seed": {"type": "integer"},
    "arms": {"type": "array", "items": {"type": "string"}},
    "bases": {"type": "array", "items": {"enum": ["BP", "EPC", "GRAM"]}},
    "reads": {"type": "array", "items": {"enum": ["h", "h0", "g", "e"]}},
    "items": {"type": ["array", "string"]},
    "budget": {"type": "object"},
    "notes": {"type": "string"},
}

MANIFEST_DEV = {
    "type": "object",
    "required": ["name", "mode", "stage", "seed"],
    "properties": _COMMON_MANIFEST_PROPS,
}

FROZEN_REQUIRED = [
    "code_commit", "env_lock_sha", "pdf_sha", "base_checkpoints", "tokenizer_rev", "bank_sites",
    "radii", "b_m", "A", "epsilon", "R", "tau_edit", "byte_ceiling", "slot_capacities",
    "cr_distribution", "dataset_ids", "realizations", "order_seeds", "cap_seed", "router_seed",
    "replay_seed", "stream_lengths", "arms", "contrasts", "primary_endpoint", "margins", "interval",
    "checkpoints", "challenge_policy", "resource_rules", "analysis_code_commit",
    "negative_case_interpretation", "spec_defect_resolutions",
]

MANIFEST_FROZEN = {
    "type": "object",
    "required": ["name", "mode"] + FROZEN_REQUIRED,
    "properties": {
        **_COMMON_MANIFEST_PROPS,
        "mode": {"const": "confirm"},
        "primary_endpoint": {"const": "RET-GS"},
        "margins": {
            "type": "object",
            "required": ["ret_gs", "es", "ls"],
            "properties": {"ret_gs": {"const": 0.02}, "es": {"const": -0.02}, "ls": {"const": -0.01}},
        },
        "interval": {
            "type": "object",
            "required": ["method", "draws", "level"],
            "properties": {
                "method": {"const": "paired-cluster-bootstrap"},
                "draws": {"const": 10000},
                "level": {"const": 0.975},
            },
        },
        "checkpoints": {"const": [100, 300, 1000, 3000]},
        "resource_rules": {
            "type": "object",
            "required": ["headroom", "kappa", "stop_boundary"],
            "properties": {"headroom": {"const": 0.25}},
        },
        "contrasts": {"type": "array", "minItems": 1},
        "realizations": {"type": "array", "minItems": 3, "maxItems": 3},
        "order_seeds": {"type": "array", "minItems": 5, "maxItems": 5},
        "spec_defect_resolutions": {"type": "array"},
    },
}

CONFIG = {
    "type": "object",
    "required": ["stage", "arm", "base", "read", "realization", "perm", "manifest", "manifest_sha256",
                 "mode", "code_commit", "determinism", "base_hash_before"],
    "properties": {
        "stage": {"type": "string"},
        "arm": {"type": "string"},
        "base": {"type": "string"},
        "read": {"type": "string"},
        "realization": {"type": "integer"},
        "perm": {"type": "integer"},
        "manifest": {"type": "string"},
        "manifest_sha256": {"type": "string"},
        "mode": {"enum": ["dev", "confirm"]},
        "code_commit": {"type": "string"},
        "determinism": {"type": "object"},
        "base_hash_before": {"type": "string"},
        "base_hash_after": {"type": "string"},
        "status": {"enum": ["running", "complete", "resource_stop", "correctness_failure"]},
    },
}

ASSETS = {
    "type": "object",
    "properties": {
        "sibling": {"type": "object", "required": ["path", "commit", "dirty", "licence"]},
        "assets": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {"enum": ["verified", "absent", "regenerable", "unavailable", "regenerated", "replacement"]},
                    "sha256": {"type": ["string", "null"]},
                    "path": {"type": ["string", "null"]},
                    "provenance": {"type": "string"},
                },
            },
        },
    },
}

TASKS = {
    "type": "object",
    "required": ["version", "tasks"],
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "stage", "role", "deps", "status"],
                "properties": {
                    "status": {"enum": ["pending", "ready", "in_progress", "review", "done", "partial", "blocked", "failed"]},
                },
            },
        }
    },
}

DATASETS = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "required": ["status"],
        "properties": {
            "status": {"enum": ["present", "unavailable", "deferred"]},
            "url": {"type": ["string", "array"]},
            "revision": {"type": ["string", "null"]},
            "licence": {"type": "string"},
            "files": {"type": "object"},
            "reason": {"type": "string"},
        },
    },
}

SCHEMAS: dict[str, dict] = {
    "config": CONFIG,
    "decision": DECISION,
    "metric": METRIC,
    "metrics": METRICS_FILE,
    "cost": COST,
    "manifest_dev": MANIFEST_DEV,
    "manifest_frozen": MANIFEST_FROZEN,
    "assets": ASSETS,
    "tasks": TASKS,
    "datasets": DATASETS,
}


class SchemaError(ValueError):
    def __init__(self, kind: str, errors: list[str]):
        super().__init__(f"{kind}: " + "; ".join(errors))
        self.kind, self.errors = kind, errors


def errors(kind: str, obj: Any) -> list[str]:
    v = jsonschema.Draft202012Validator(SCHEMAS[kind])
    out = []
    for e in sorted(v.iter_errors(obj), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
        out.append(f"{loc}: {e.message}")
    return out


def validate(kind: str, obj: Any) -> None:
    errs = errors(kind, obj)
    if errs:
        raise SchemaError(kind, errs)


def missing_frozen_fields(manifest: dict) -> list[str]:
    return [k for k in FROZEN_REQUIRED if k not in manifest]


def infer_kind(path: Path) -> str:
    name = path.name
    parts = path.as_posix()
    if name == "frozen.json":
        return "manifest_frozen"
    if name == "assets.json":
        return "assets"
    if name == "tasks.json":
        return "tasks"
    if name == "datasets.json":
        return "datasets"
    if name == "cost.json":
        return "cost"
    if name == "metrics.json":
        return "metrics"
    if name == "config.json":
        return "config"
    if "/manifests/" in parts and "/confirm/" in parts:
        return "manifest_frozen"
    if "/manifests/" in parts:
        return "manifest_dev"
    raise ValueError(f"cannot infer schema kind for {path}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("file")
    v.add_argument("--kind", default=None, choices=sorted(SCHEMAS))
    args = ap.parse_args(argv)
    path = Path(args.file).resolve()
    kind = args.kind or infer_kind(path)
    obj = json.loads(path.read_text())
    errs = errors(kind, obj)
    if errs:
        print(f"INVALID ({kind}) {path}", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        return 2
    print(f"valid ({kind}) {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
