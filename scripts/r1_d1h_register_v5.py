"""R1-D1h: DEC-048 MQuAKE query-role waiver, with no draw or seal."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from scripts.r1_d1f_freeze_register import norm, sha
from scripts.r1_d4_prepare_mquake import digest

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("zsre", "counterfact", "mquake")
DEMAND = 3 * (1000 + 350)
# Exact reasons only. Unknown reasons, including unverified/counterfactual near-miss roles, remain.
WAIVABLE = frozenset(
    {
        "mquake_training_locality_query_subject",
        "mquake_development_locality_query_subject",
        "mquake_development_unrelated_query_subject",
    }
)
PROTECTED_NOTE = "Primary training/development, drawn/sealed, conflicts, context, cross-dataset and all other reasons remain."


def capacity(subjects, items, demand=DEMAND):
    if any(type(x) is not int or x < 0 for x in (subjects, items, demand)):
        raise ValueError("nonnegative integer counts required")
    return {
        "candidate_items": items,
        "candidate_subjects": subjects,
        "demand_subjects": demand,
        "headroom_subjects": subjects - demand,
        "nominal_capacity_sufficient": subjects >= demand,
        "pending_clearance_removal_upper_bound_subjects": subjects,
        "pending_clearance_removal_upper_bound_items": items,
        "guaranteed_cleared_subjects": 0,
        "maximum_subject_losses_preserving_demand": max(0, subjects - demand),
        "first_subject_loss_count_causing_shortfall": max(0, subjects - demand + 1),
    }


def apply_policy(parent, source_rows):
    """Only MQ's explicitly enumerated query reasons are waived; original rows retained."""
    pools = copy.deepcopy(parent["candidates"])
    removed = copy.deepcopy(parent["removals"])
    known = {r["item_id"]: r for r in source_rows}
    if len(known) != len(source_rows):
        raise ValueError("duplicate prepared source ID")
    released = []
    remaining = []
    for row in removed["mquake"]:
        waived = set(row["reasons"]) & WAIVABLE
        effective = set(row["reasons"]) - WAIVABLE
        if effective:
            remaining.append(
                {
                    **row,
                    "historical_reasons": row["reasons"],
                    "reasons": sorted(effective),
                    "waived_reasons": sorted(waived),
                }
            )
            continue
        if not waived:
            raise ValueError("removal has no reason")
        src = known[row["item_id"]]
        if norm(src["subject"]) != row["canonical_subject"]:
            raise ValueError("prepared subject identity mismatch")
        candidate = {
            "item_id": src["item_id"],
            "canonical_subject": row["canonical_subject"],
            "source_record_sha256": src.get("source_record_sha256"),
            "payload_sha256": digest({k: v for k, v in src.items() if not k.startswith("_")}),
            "teacher_status": "eligible_receipt_bound",
            "waived_reasons": sorted(waived),
        }
        pools["mquake"].append(candidate)
        released.append(
            {
                "item_id": src["item_id"],
                "canonical_subject": row["canonical_subject"],
                "waived_reasons": sorted(waived),
                "basis": "DEC-048 policy change; not an absence-of-execution certificate",
            }
        )
    removed["mquake"] = remaining
    for ds in DATASETS:
        if len({r["item_id"] for r in pools[ds]}) != len(pools[ds]):
            raise ValueError("duplicate candidate ID")
        if {r["item_id"] for r in pools[ds]} & {r["item_id"] for r in removed[ds]}:
            raise ValueError("candidate/removal overlap")
    counts = {
        ds: capacity(len({r["canonical_subject"] for r in pools[ds]}), len(pools[ds]))
        for ds in DATASETS
    }
    return {
        "candidates": pools,
        "removals": removed,
        "policy_releases": released,
        "counts": counts,
        "released_MQuAKE_subjects": len({r["canonical_subject"] for r in released}),
    }


def require_usable_capacity(register, cleared_subjects, demand=DEMAND):
    """Owner must call after clearance, before RNG or any allocation/write. No waiver is clearance."""
    if set(cleared_subjects) != set(DATASETS) or type(demand) is not int or demand < 1:
        raise ValueError("explicit clearance for every dataset and positive demand required")
    result = {}
    for ds in DATASETS:
        keys = cleared_subjects[ds]
        if not isinstance(keys, (list, tuple, set, frozenset)) or any(
            not isinstance(k, str) for k in keys
        ):
            raise ValueError("cleared canonical subject inventory required")
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate clearance subjects")
        allowed = {r["canonical_subject"] for r in register["candidates"][ds]}
        if not set(keys) <= allowed:
            raise ValueError("clearance includes excluded or unknown subjects")
        result[ds] = len(keys)
    short = {k: v for k, v in result.items() if v < demand}
    if short:
        raise ValueError(f"abort before RNG/draw: usable subjects below {demand}: {short}")
    return result


def build(root=ROOT, producer=None):
    root = Path(root)
    bindings = {}

    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute():
            p = root / p
        value = sha(p)
        if expected is not None and value != expected:
            raise ValueError("bound source changed: " + str(p))
        bindings[str(p)] = value
        return p

    def read(path, expected=None):
        return json.loads(bind(path, expected).read_text())

    parent_path = "manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json"
    parent = read(parent_path)
    for path, expected in parent["bindings_sha256"].items():
        bind(path, expected)
    prepared = read("manifests/revision_v1/mquake_items_v1.json")
    ref = prepared["artifacts"]["items"]
    rows = [json.loads(line) for line in bind(ref["path"], ref["sha256"]).read_text().splitlines()]
    expected = {r["item_id"]: r["prepared_record_sha256"] for r in prepared["items"]}
    if len(rows) != len(expected) or any(digest(r) != expected.get(r["item_id"]) for r in rows):
        raise ValueError("prepared row identity mismatch")
    teacher = read("manifests/revision_v1/mquake_pool_v1.json")
    eligible = {r["item_id"] for r in teacher["items"]}
    for p, h in teacher["sources_sha256"].items():
        bind(p, h)
    rows = [r for r in rows if r["item_id"] in eligible]
    source_ids = {r["item_id"] for r in rows}
    if source_ids != {
        r["item_id"] for r in parent["candidates"]["mquake"] + parent["removals"]["mquake"]
    }:
        raise ValueError("cumulative source universe differs from teacher/prepared intersection")
    slice_paths = [
        "manifests/revision_v1/train_pool_mquake_v3.json",
        "manifests/dev/mquake_dev_v3.json",
    ]
    slices = [read(p) for p in slice_paths]
    # Bind exposure-neutral v3b if available; membership must agree with the v3 dev slice.
    later = root / "manifests/dev/mquake_dev_v3b.json"
    if later.exists():
        v3b = read(later)
        fields = ("item_id", "subject", "prompt", "answer", "prompt_ids", "answer_ids", "digest")
        if [[r[k] for k in fields] for r in v3b["items"]] != [
            [r[k] for k in fields] for r in slices[1]["items"]
        ]:
            raise ValueError("v3b primary population changed")
        slice_paths.append(str(later))
    primary = {norm(r["subject"]) for d in slices for r in d["items"]}
    historical_primary = {
        r["canonical_subject"]
        for r in parent["additional_exclusions"]
        if any(x.endswith("_reserved_subject") for x in r["reasons"])
    }
    if not primary <= historical_primary:
        raise ValueError("new primary subjects require cumulative exposure update")
    index = read("logs/r1_round11/exposure_audit.index.json")
    for path, ref in index["parts"].items():
        bind(path, ref["sha256"])
    decisions = bind("docs/decisions.md").read_text()
    decision = [s for s in decisions.splitlines() if s.startswith("| DEC-048 |")]
    if len(decision) != 1 or "4,218" not in decision[0]:
        raise ValueError("DEC-048 decision receipt missing or changed")
    view = apply_policy(parent, rows)
    if any(r["canonical_subject"] in historical_primary for r in view["candidates"]["mquake"]):
        raise ValueError("primary subject released")
    for ds in ("zsre", "counterfact"):
        if (
            view["candidates"][ds] != parent["candidates"][ds]
            or view["removals"][ds] != parent["removals"][ds]
        ):
            raise ValueError("DEC-048 may not change other datasets")
    out = {
        "schema_version": 5,
        "name": "exclusions_frozen_v5",
        "task": "R1-D1h",
        "status": "DEC-048 register policy bound; final alias/context/role clearance and draw admission pending",
        "parent": {"path": str(root / parent_path), "sha256": bindings[str(root / parent_path)]},
        "acceptance": {
            "decision": "DEC-048",
            "decision_row": decision[0],
            "decision_row_sha256": hashlib.sha256(decision[0].encode()).hexdigest(),
        },
        "policy": {
            "scope": "MQuAKE only",
            "waived_reasons": sorted(WAIVABLE),
            "rule": "True-fact locality/unrelated presentations are not exposure for a later counterfactual edit.",
            "preserved": PROTECTED_NOTE,
            "normalization": "NFKC/casefold/whitespace; inherited verified aliases",
            "near_miss": "R1-D4b v3 true-fact near-miss candidates share its bound locality neighbours and primary slice reservations; no separate near-miss removal reason occurs in the cumulative parent. Unknown or counterfactual role reasons are never waived by suffix matching.",
            "cross_dataset": "zsRE priority and every cross-dataset reason retained; zsRE query exposures remain excluded",
            "counterfact": "inherited reason-specific old_eligible:counterfact exception; DEC-048 adds no CF waiver",
        },
        "historical_exposure_counts": parent["historical_exposure_counts"],
        "historical_additional_exclusions": parent["additional_exclusions"],
        "cross_dataset_overlap": parent["cross_dataset_overlap"],
        "slice_bindings": [
            {
                "path": str(root / p) if not Path(p).is_absolute() else p,
                "sha256": bindings[str(root / p) if not Path(p).is_absolute() else p],
            }
            for p in slice_paths
        ],
        "audit_index": {
            "path": str(root / "logs/r1_round11/exposure_audit.index.json"),
            "sha256": bindings[str(root / "logs/r1_round11/exposure_audit.index.json")],
        },
        **view,
        "abort_rule": "After all alias/context/role/dependency clearance, abort globally before RNG or writes if any dataset has fewer than 4050 distinct usable subjects. No reuse, replacement, reduced scope or retrospective waiver.",
        "clearance_status": "pending; no nontrivial upper bound on removals established; all candidates may fail",
        "register_policy_frozen": True,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "final_draw_ready": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "sealed_payloads_opened": 0,
        "gpu_seconds": 0,
    }
    bind(Path(producer) if producer else Path(__file__))
    for path, expected in bindings.items():
        if sha(path) != expected:
            raise ValueError("source changed during build: " + path)
    out["bindings_sha256"] = bindings
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    result = build()
    with args.output.open("x") as f:
        json.dump(result, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {
                "counts": result["counts"],
                "released_MQuAKE_subjects": result["released_MQuAKE_subjects"],
                "draw_authorized": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
