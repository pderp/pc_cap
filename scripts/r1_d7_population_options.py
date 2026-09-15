"""R1-D7: deterministic population counts; no sampling, model loading or policy changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERY_REASONS = frozenset(
    {
        "mquake_training_locality_query_subject",
        "mquake_development_locality_query_subject",
        "mquake_development_unrelated_query_subject",
    }
)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def canonical(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def role_capacity(subjects, realizations, edits, reserve=350):
    if (
        any(type(x) is not int or x < 0 for x in (subjects, realizations, edits, reserve))
        or realizations == 0
    ):
        raise ValueError("nonnegative integer counts and positive realizations required")
    demand = realizations * (edits + reserve)
    return {
        "subjects": subjects,
        "realizations": realizations,
        "edits_each": edits,
        "reserve_each": reserve,
        "edit_only_demand": realizations * edits,
        "full_role_demand": demand,
        "remaining": subjects - demand,
        "fits_before_additional_clearance": demand <= subjects,
        "maximum_edits_each_with_reserve": max(0, subjects // realizations - reserve),
    }


def query_exception_view(supplement):
    rows = list(supplement["candidates"]["mquake"])
    rows.extend(
        r for r in supplement["removals"]["mquake"] if not (set(r["reasons"]) - QUERY_REASONS)
    )
    return {
        "items": len(rows),
        "subjects": len({r["canonical_subject"] for r in rows}),
        "policy": "waive query-only reasons; retain historical primary and all independent reasons",
        "adopted": False,
    }


def temporal_inventory(cases, comparison_subjects):
    edits = [e for c in cases for e in c["requested_rewrite"]]
    subjects = {canonical(e["subject"]) for e in edits}
    targets = {}
    for e in edits:
        key = (canonical(e["subject"]), e["relation_id"])
        targets.setdefault(key, set()).add(e["target_new"]["id"])
    return {
        "cases": len(cases),
        "unique_case_ids": len({c["case_id"] for c in cases}),
        "rewrite_occurrences": len(edits),
        "distinct_subject_relation_edits": len(targets),
        "distinct_subjects": len(subjects),
        "distinct_edit_triples": len({tuple(e) for c in cases for e in c["orig"]["edit_triples"]}),
        "conflicting_new_targets_per_subject_relation": sum(len(v) > 1 for v in targets.values()),
        "rewrite_count_histogram": dict(
            sorted(Counter(len(c["requested_rewrite"]) for c in cases).items())
        ),
        "subject_overlap": {k: len(subjects & set(v)) for k, v in comparison_subjects.items()},
        "teacher_eligible_new_subjects": None,
        "admission": "separate temporal population pending decision, preparation and eligibility",
    }


def build(root=ROOT):
    root = Path(root)
    bindings = {}

    def read(path, expected=None, lines=False):
        p = Path(path)
        if not p.is_absolute():
            p = root / p
        raw = p.read_bytes()
        value = hashlib.sha256(raw).hexdigest()
        if expected is not None and value != expected:
            raise ValueError("source hash mismatch: " + str(p))
        bindings[str(p)] = value
        return [json.loads(x) for x in raw.splitlines() if x.strip()] if lines else json.loads(raw)

    supplement = read("manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json")
    bounds = read("logs/r1_round11/exposure_capacity_bounds.json")
    index = read("logs/r1_round11/exposure_audit.index.json")
    if bounds["source_audit_sha256"] != index["original"]["sha256"]:
        raise ValueError("capacity bound does not reference archived audit")
    if bounds["source_supplement_sha256"] != sha(
        root / "manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json"
    ):
        raise ValueError("capacity bound supplement mismatch")
    audit = {}
    for p, ref in index["parts"].items():
        part = read(p, ref["sha256"])
        for key in ref["keys"]:
            if key in audit:
                raise ValueError("duplicate archival key")
            audit[key] = part[key]
    mq_review = set(bounds["counts"]["mquake"]["subjects"])
    classes = Counter(
        tuple(x["current_reasons"])
        for x in audit["supplement_subjects_without_matched_evidence"]
        if x["subject"] in mq_review
    )
    if sum(classes.values()) != len(mq_review):
        raise ValueError("review subject inventory mismatch")
    manifest = read("manifests/revision_v1/mquake_items_v1.json")
    items = read(
        manifest["artifacts"]["items"]["path"], manifest["artifacts"]["items"]["sha256"], lines=True
    )
    all_subjects = {canonical(x["subject"]) for x in items}
    raw = root.parent / "assets/data/raw/mquake"
    checks = {}
    checksum_file = raw / "SHA256SUMS"
    bindings[str(checksum_file)] = sha(checksum_file)
    for line in checksum_file.read_text().splitlines():
        value, name = line.split(maxsplit=1)
        checks[name.lstrip("*")] = value
    temporal = read(raw / "MQuAKE-T.json", checks["MQuAKE-T.json"])
    for name in ("README.md", "LICENSE"):
        if sha(raw / name) != checks[name]:
            raise ValueError("upstream documentation identity mismatch")
        bindings[str(raw / name)] = checks[name]
    primary_subjects = {
        x["canonical_subject"]
        for x in supplement["additional_exclusions"]
        if any(r.endswith("_reserved_subject") for r in x["reasons"])
    }
    result = {
        "task": "R1-D7",
        "status": "count-only proposal; no policy change",
        "sources_sha256": bindings,
        "conservative_counts": supplement["counts"],
        "historical_exposure_counts": supplement["historical_exposure_counts"],
        "executed_only_conditional": {
            k: {a: b for a, b in v.items() if a != "subjects"} for k, v in bounds["counts"].items()
        },
        "executed_only_MQuAKE_review_classes": [
            {"reasons": list(k), "subjects": v} for k, v in sorted(classes.items())
        ],
        "audit_gaps": audit["gaps"],
        "query_exception_with_history": query_exception_view(supplement),
        "prospective_only_without_history": supplement["prospective_only"],
        "temporal": temporal_inventory(
            temporal,
            {
                "prepared_MQuAKE_CF": all_subjects,
                "historical_MQuAKE_primary": primary_subjects,
                "historical_MQuAKE_exposure_union": [
                    x["canonical_subject"] for x in supplement["additional_exclusions"]
                ],
                **{
                    k + "_candidates": [x["canonical_subject"] for x in v]
                    for k, v in supplement["candidates"].items()
                },
            },
        ),
        "capacity_scenarios": [
            role_capacity(n, r, e)
            for n, r, e in [
                (2100, 2, 1000),
                (2100, 3, 650),
                (2100, 3, 350),
                (2100, 3, 300),
                (2100, 2, 700),
                (2829, 3, 593),
                (2829, 2, 1000),
                (4218, 3, 1000),
                (4818, 3, 1000),
            ]
        ],
        "limitations": [
            "Capacities precede additional alias/context and role-compatibility clearance.",
            "No subject release certified; bank and incomplete historical evidence matter.",
            "Local T count differs from README; source bytes govern this inventory.",
            "Temporal exact-label overlaps are not complete alias/context clearance.",
        ],
        "draws": 0,
        "seals": 0,
        "gpu_seconds": 0,
        "released_subjects": [],
    }
    for path, expected in bindings.items():
        if sha(path) != expected:
            raise ValueError("source changed during count: " + path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    result = build()
    with args.output.open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "query_exception": result["query_exception_with_history"],
                "temporal": result["temporal"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
