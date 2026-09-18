"""R1-58c dry metadata preflight; prints intended outputs and never draws/seals/freezes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from scripts import r1_d9_layouts as layouts

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("zsre", "counterfact", "mquake")
ROLES = {
    "edits": 1000,
    "outside": 100,
    "near_miss_support": 100,
    "near_miss_neighbour": 100,
    "revision": 50,
}
REQUIRED = {
    "clearance": ["clearance_authorization", "joint_clearance"],
    "draw": [
        "clearance_authorization",
        "joint_clearance",
        "protocol_admission",
        "rng_admission",
        "draw_authorization",
    ],
    "seal": [
        "joint_clearance",
        "protocol_admission",
        "rng_admission",
        "draw_authorization",
        "draw_receipt",
        "endpoint_construction",
        "seal_authorization",
    ],
    "freeze": [
        "joint_clearance",
        "protocol_admission",
        "rng_admission",
        "draw_receipt",
        "endpoint_construction",
        "seal_receipt",
        "chain_i_cell_ceilings",
        "september20_admission",
        "closed_gate_receipts",
        "freeze_authorization",
    ],
}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read_metadata(binding, *, parse=True):
    p = Path(binding["path"]).resolve()
    if "confirm" in p.parts or not any(
        p.is_relative_to(ROOT / n) for n in ("docs", "manifests/revision_v1", "logs")
    ):
        raise PermissionError("repo admission metadata only; no payload access")
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError("metadata identity mismatch")
    return json.loads(raw) if parse else None


def check_receipt(name, r, spec):
    if r.get("status") != "closed" or r.get("lead_approved") is not True:
        raise ValueError("open or unapproved receipt")
    if r.get("register") != spec["register"]:
        raise ValueError("receipt register identity differs from v6")
    layout = layouts.from_spec(spec)
    if spec.get("schema_version") == 3:
        if (
            r.get("contract_version") != 2
            or layouts.digest(r.get("dataset_layouts")) != layouts.digest(layout)
            or r.get("layout_sha256") != layouts.digest(layout)
            or r.get("matrix") != spec["matrix"]
            or r.get("protocol") != spec["protocol"]
        ):
            raise ValueError("versioned receipt layout/matrix/protocol differs")
    family = spec.get("near_miss_family_contract")
    if family is not None:
        from scripts.r1_d9e_near_family import CONTRACT

        if family != CONTRACT or r.get("near_miss_family_contract") != family:
            raise ValueError("DEC-061 near-miss receipt contract differs")
        if name == "protocol_admission" and r.get("near_family_reviewed") is not True:
            raise ValueError("near-miss family review is not signed")
    if name == "joint_clearance":
        if r.get("policy") != "DEC-048-option-C;DEC-042-CounterFact;zsRE-priority":
            raise ValueError("unapproved exclusion policy")
        if any(
            r.get(k) is not True
            for k in (
                "alias_review_complete",
                "context_review_complete",
                "teacher_token_review_complete",
                "role_compatibility_complete",
                "cross_dataset_disjoint",
                "cumulative_exposure_current",
            )
        ):
            raise ValueError("joint clearance incomplete")
        if any(
            type(r.get("cleared_subjects", {}).get(ds)) is not int
            or r["cleared_subjects"][ds] < layout[ds]["demand_subjects"]
            for ds in DATASETS
        ):
            raise ValueError("joint cleared capacity below admitted per-dataset demand")
    if name in ("draw_receipt", "seal_receipt", "endpoint_construction"):
        if (
            spec.get("schema_version") != 3
            and (r.get("realizations") != 3 or r.get("roles_per_realization") != ROLES)
        ) or r.get("datasets") != list(DATASETS):
            raise ValueError("registered population changed")
        if (
            r.get("all_roles_disjoint") is not True
            or r.get("composition_dependencies_closed") is not True
        ):
            raise ValueError("role/dependency audit unresolved")
    if name == "seal_receipt":
        for k in ("reservations", "payload_inventory", "analysis_population"):
            b = r.get(k, {})
            if not isinstance(b.get("path"), str) or len(b.get("sha256", "")) != 64:
                raise ValueError("missing opaque content seal binding")
    if name == "chain_i_cell_ceilings":
        if r.get("failures_included") is not True or not r.get("cells"):
            raise ValueError("profile costs incomplete")
        for c in r["cells"]:
            if any(
                isinstance(c.get(k), bool)
                or not isinstance(c.get(k), (int, float))
                or not math.isfinite(c[k])
                or c[k] <= 0
                for k in ("wall_seconds", "peak_host_mib", "peak_device_mib")
            ):
                raise ValueError("positive measured ceilings required")
    if name == "september20_admission":
        if (
            r.get("experimental_completion_date") != "2026-10-09"
            or r.get("admission_date") != "2026-09-20"
            or r.get("full_scope_retained") is not True
        ):
            raise ValueError("September20 schedule/ceiling decision unresolved")
    if name == "closed_gate_receipts":
        if set(r.get("gates", {})) != {f"U{i:02}" for i in range(1, 19)}:
            raise ValueError("all18 final gate receipts required")
        for g, b in r["gates"].items():
            q = read_metadata(b)
            if (
                q.get("gate") != g
                or q.get("status") != "closed"
                or q.get("lead_approved") is not True
            ):
                raise ValueError("unapproved gate closure")


def preflight(spec, stage):
    blocked = []
    checked = {}
    for key in ("register", "matrix", "protocol", "freeze_candidate"):
        try:
            read_metadata(spec[key], parse=key != "protocol")
        except (OSError, KeyError, TypeError, ValueError) as e:
            blocked.append({"gate": key, "reason": str(e)})
    for name in REQUIRED[stage]:
        try:
            b = spec["receipts"][name]
            if not b.get("path") or not b.get("sha256"):
                raise ValueError("named owner receipt is not supplied")
            r = read_metadata(b)
            check_receipt(name, r, spec)
            checked[name] = b
        except (OSError, KeyError, TypeError, ValueError) as e:
            blocked.append({"gate": name, "reason": str(e)})
    return {
        "task": "R1-58c",
        "stage": stage,
        "dry_run": True,
        "would_write": spec["intended_outputs"][stage],
        "ready_for_owner_review": not blocked,
        "blocked": blocked,
        "checked_receipts": checked,
        "demand": spec.get("dataset_layouts", layouts.production()),
        "draws_emitted": 0,
        "seals_emitted": 0,
        "freeze_written": False,
        "launch_authorized": False,
        "note": "Readiness is a metadata check only. The lead performs construction, draw, seal and freeze after review; this command has no mutation mode.",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=tuple(REQUIRED), required=True)
    p.add_argument("--inputs", type=Path, required=True)
    a = p.parse_args(argv)
    spec = read_metadata({"path": str(a.inputs.resolve()), "sha256": sha(a.inputs)})
    result = preflight(spec, a.stage)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["ready_for_owner_review"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
