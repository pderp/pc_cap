"""R1-D1g: register v4 source/exception/exposure binding; never draw or seal."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from scripts.r1_58_draw_streams import WRAPPER, WRAPPER_SHA, candidates
from scripts.r1_d1f_freeze_register import norm, sha, verify
from scripts.r1_d4_prepare_mquake import digest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"


def policy_view(
    zsre,
    counterfact,
    mquake,
    old_reasons,
    aliases,
    *,
    train=(),
    dev=(),
    unrelated=(),
    teacher_available=False,
):
    """Pure deterministic policy transform; no RNG, final role assignment or model."""

    def canonical(s):
        return aliases.get(norm(s), norm(s))

    reasons = defaultdict(set)
    for key, values in old_reasons.items():
        reasons[canonical(key)].update(values)
    zs_subjects = {canonical(r["subject"]) for r in zsre}
    mq_subjects = {canonical(r["subject"]) for r in mquake}
    overlap = zs_subjects & mq_subjects
    prompt_subjects = defaultdict(set)
    for row in mquake:
        prompt_subjects[norm(row["prompt"])].add(canonical(row["subject"]))
    primary, local, outside = set(), set(), set()
    unknown = []
    for role, records in (("training", train), ("development", dev)):
        for row in records:
            key = canonical(row["subject"])
            primary.add(key)
            reasons[key].add("mquake_" + role + "_reserved_subject")
            for prompt in row.get("locality_prompts", []):
                keys = prompt_subjects.get(norm(prompt), set())
                if not keys:
                    unknown.append({"role": role + "_locality", "prompt_sha256": digest(prompt)})
                local.update(keys)
                for key in keys:
                    reasons[key].add("mquake_" + role + "_locality_query_subject")
    for prompt in unrelated:
        keys = prompt_subjects.get(norm(prompt), set())
        if not keys:
            unknown.append({"role": "development_unrelated", "prompt_sha256": digest(prompt)})
        outside.update(keys)
        for key in keys:
            reasons[key].add("mquake_development_unrelated_query_subject")
    pools = {}
    removals = {}
    source_rows = {"zsre": zsre, "counterfact": counterfact, "mquake": mquake}
    for ds, records in source_rows.items():
        pools[ds], removals[ds] = [], []
        seen_ids = set()
        for row in records:
            if row["item_id"] in seen_ids:
                raise ValueError("duplicate source item ID")
            seen_ids.add(row["item_id"])
            key = canonical(row["subject"])
            active = reasons[key] - ({"old_eligible:counterfact"} if ds == "counterfact" else set())
            why = sorted(active)
            if ds == "mquake" and key in overlap:
                why.append("cross_dataset_priority:zsre")
            if why:
                removals[ds].append(
                    {"item_id": row["item_id"], "canonical_subject": key, "reasons": why}
                )
            else:
                pools[ds].append(
                    {
                        "item_id": row["item_id"],
                        "canonical_subject": key,
                        "source_record_sha256": row.get("source_record_sha256"),
                        "payload_sha256": digest(
                            {k: v for k, v in row.items() if not k.startswith("_")}
                        ),
                        "teacher_status": "eligible_receipt_bound"
                        if ds == "mquake" and teacher_available
                        else "not_certified_here",
                    }
                )
    counts = {}
    for ds, records in source_rows.items():
        original = {canonical(r["subject"]) for r in records}
        kept = {r["canonical_subject"] for r in pools[ds]}
        counts[ds] = {
            "source_items": len(records),
            "source_subjects": len(original),
            "candidate_items": len(pools[ds]),
            "candidate_subjects": len(kept),
            "removed_items": len(removals[ds]),
            "new_primary_exposure_subject_overlap": len(original & primary),
            "new_locality_exposure_subject_overlap": len(original & local),
            "new_unrelated_exposure_subject_overlap": len(original & outside),
            "new_exposure_union_subject_overlap": len(original & (primary | local | outside)),
            "role_demand_proposal": 4050,
            "subject_shortfall": max(0, 4050 - len(kept)),
        }
    return {
        "candidates": pools,
        "removals": removals,
        "additional_exclusions": [
            {"canonical_subject": k, "reasons": sorted(v)}
            for k, v in sorted(reasons.items())
            if any(r.startswith("mquake_") for r in v)
        ],
        "cross_dataset_overlap": {
            "zsre_mquake_subjects": len(overlap),
            "mquake_overlap_items": sum(canonical(r["subject"]) in overlap for r in mquake),
            "shared_subjects_lost_from_zsre_due_to_new_query_exposure": len(
                overlap & (local | outside)
            ),
            "rule": "zsRE priority over MQuAKE; independent exposure exclusions override priority",
        },
        "counts": counts,
        "new_exposure_counts": {
            "primary": len(primary),
            "locality": len(local),
            "development_unrelated": len(outside),
            "union": len(primary | local | outside),
        },
        "primary_only_mquake_subject_ceiling": len(mq_subjects - overlap - primary),
        "unmapped_declared_query_prompts": unknown,
        "teacher_pool_binding": "present" if teacher_available else "pending",
    }


def build():
    wrapper = verify(WRAPPER, WRAPPER_SHA)
    bindings = {str(WRAPPER): WRAPPER_SHA, **wrapper["bindings_sha256"]}

    def read(p):
        p = Path(p)
        if not p.is_absolute():
            p = ROOT / p
        bindings[str(p)] = sha(p)
        return json.loads(p.read_text())

    reg = read(wrapper["register"]["path"])
    rows, _ = candidates("exception")
    prepared = read("manifests/revision_v1/mquake_items_v1.json")
    for ref in prepared["artifacts"].values():
        if sha(ref["path"]) != ref["sha256"]:
            raise ValueError("MQuAKE prepared child identity mismatch")
        bindings[ref["path"]] = ref["sha256"]
    with Path(prepared["artifacts"]["items"]["path"]).open() as f:
        mq = [json.loads(line) for line in f]
    expected = {r["item_id"]: r["prepared_record_sha256"] for r in prepared["items"]}
    if len(mq) != len(expected) or any(digest(r) != expected.get(r["item_id"]) for r in mq):
        raise ValueError("MQuAKE prepared row identity mismatch")
    pool_path = ROOT / "manifests/revision_v1/mquake_pool_v1.json"
    pool = read(pool_path) if pool_path.exists() else None
    if pool:
        for p, h in pool["sources_sha256"].items():
            if sha(p) != h:
                raise ValueError("teacher pool input identity mismatch")
            bindings[p] = h
        teacher_ids = {r["item_id"] for r in pool["items"]}
        if len(teacher_ids) != len(pool["items"]) or not teacher_ids <= expected.keys():
            raise ValueError("teacher pool coverage/identity mismatch")
        mapped = {r["item_id"]: r for r in mq}
        if any(
            r["prompt"] != mapped[r["item_id"]]["prompt"]
            or r["answer"] != mapped[r["item_id"]]["answer"]
            or r["prompt_ids"] != mapped[r["item_id"]]["prompt_ids"]
            or r["answer_ids"] != mapped[r["item_id"]]["answer_ids"]
            for r in pool["items"]
        ):
            raise ValueError("teacher pool changed support labels/tokens")
        mq = [r for r in mq if r["item_id"] in teacher_ids]
    split = {}
    for role, path in (
        ("training", "manifests/revision_v1/train_pool_mquake_v1.json"),
        ("development", "manifests/dev/mquake_dev.json"),
    ):
        if (ROOT / path).exists():
            split[role] = read(path)
            source = split[role].get("source", split[role].get("sources_sha256"))
            if pool is None or source != {
                "path": str(pool_path),
                "sha256": bindings[str(pool_path)],
            }:
                raise ValueError("split does not bind current teacher pool")
    train, dev = (
        split.get("training", {}).get("items", []),
        split.get("development", {}).get("items", []),
    )
    known = {r["item_id"]: r for r in (pool["items"] if pool else mq)}
    for row in train + dev:
        if row != known.get(row["item_id"]):
            raise ValueError("split item differs from teacher pool")
    train_keys, dev_keys = ({norm(r["subject"]) for r in part} for part in (train, dev))
    if len(train_keys) != len(train) or len(dev_keys) != len(dev) or train_keys & dev_keys:
        raise ValueError("training/development primary subjects not disjoint")
    reasons = defaultdict(set)
    for r in reg["exclusions"]:
        reasons[r["canonical_subject_key"]].update(r["reasons"])
    result = policy_view(
        rows["zsre"],
        rows["counterfact"],
        mq,
        reasons,
        wrapper["policy"]["verified_alias_pairs"],
        train=train,
        dev=dev,
        unrelated=split.get("development", {}).get("unrelated_prompts", []),
        teacher_available=pool is not None,
    )
    decisions = (ROOT / "docs/decisions.md").read_text()
    decision_rows = [
        line
        for line in decisions.splitlines()
        if any(line.startswith("| " + d) for d in ("DEC-041", "DEC-042", "DEC-045", "DEC-046"))
    ]
    task_text = (ROOT / "docs/ongoing.md").read_text()
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    m = {
        "schema_version": 1,
        "name": "exclusions_frozen_v4",
        "task": "R1-D1g",
        "status": "versioned_exposure_binding_not_draw_admission",
        "parent": {"path": str(WRAPPER), "sha256": WRAPPER_SHA},
        "policy": {
            "counterfact_selected_reading": "exception",
            "waived_reason": "old_eligible:counterfact",
            "waiver_scope": "CounterFact candidate view only; no other reason waived",
            "normalization": "NFKC, casefold, whitespace; verified aliases only",
            "teacher_preparation": "eligible/source subject inventory is bound provenance, not wholesale training exposure",
            "actual_exposure": "reserve all selected training/development primary subjects and every declared locality/unrelated query subject",
            "query_exposure": "exact prepared cloze-to-subject mapping; unknown contexts/aliases remain a further review gate",
            "split_proposal": "DEC-046 proposed status does not release already used/reserved development/training queries",
        },
        "decisions": [
            {"row": line, "sha256": hashlib.sha256(line.encode()).hexdigest()}
            for line in decision_rows
        ],
        "task_authority": {
            "path": "docs/ongoing.md",
            "sha256_at_creation": hashlib.sha256(task_text.encode()).hexdigest(),
            "scope": "R1-D1g directs applying the CounterFact exception; no new lead acceptance fabricated",
        },
        "mquake_source_inventory": prepared["artifacts"]["subjects"],
        "mquake_teacher_pool": {
            "path": str(pool_path),
            "sha256": bindings.get(str(pool_path)),
            "status": "present" if pool else "pending",
        },
        "mquake_split_sources": {
            role: {"items": len(doc["items"]), "decision": doc["decision"]}
            for role, doc in split.items()
        },
        **result,
        "bindings_sha256": bindings,
        "final_draw_ready": False,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "gpu_seconds": 0,
        "limits": [
            "candidate views are metadata, not a final sample or semantic/context certification",
            "all teacher-eligible subjects are not automatically training-exposed",
            "remaining ordinary-text and alias/context exposure can only reduce current candidate ceilings",
            "v4 subject shortfalls cannot be repaired by silently reducing scope or reusing exposed subjects",
            "bind this wrapper externally and validate all children before downstream use",
        ],
    }
    return validate(m)


def validate(m, *, check_sources=True):
    if (
        m.get("name") != "exclusions_frozen_v4"
        or m["policy"]["waived_reason"] != "old_eligible:counterfact"
    ):
        raise ValueError("register version/exception changed")
    if any(
        m[k]
        for k in (
            "final_draw_ready",
            "confirmation_protocol_frozen",
            "draw_authorized",
            "draws_emitted",
            "seals_emitted",
        )
    ):
        raise ValueError("register binding cannot authorize a draw or seal")
    all_keys = {}
    for ds, rows in m["candidates"].items():
        ids = [r["item_id"] for r in rows]
        keys = {r["canonical_subject"] for r in rows}
        if (
            len(set(ids)) != len(ids)
            or len(rows) != m["counts"][ds]["candidate_items"]
            or len(keys) != m["counts"][ds]["candidate_subjects"]
        ):
            raise ValueError("candidate counts or identities invalid")
        for other, seen in all_keys.items():
            if seen & keys:
                raise ValueError("cross-dataset candidate subject collision: " + other + "/" + ds)
        all_keys[ds] = keys
    if check_sources:
        for p, h in m["bindings_sha256"].items():
            if sha(p) != h:
                raise ValueError("v4 child input changed: " + p)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    if args.output.exists() or args.report.exists():
        ap.error("new output files required")
    if not args.output.resolve().is_relative_to(
        ROOT / "manifests"
    ) or not args.report.resolve().is_relative_to(ROOT / "logs"):
        ap.error("manifest/log paths must remain under pc_cap")
    m = build()
    with args.output.open("x") as f:
        f.write(json.dumps(m, indent=2, sort_keys=True, allow_nan=False) + "\n")
    report = {
        k: v for k, v in m.items() if k not in ("candidates", "removals", "additional_exclusions")
    }
    report["manifest"] = {"path": str(args.output.resolve()), "sha256": sha(args.output)}
    with args.report.open("x") as f:
        f.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "counts": m["counts"],
                "new_exposure": m["new_exposure_counts"],
                "overlap": m["cross_dataset_overlap"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
