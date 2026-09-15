"""R1-D4b: versioned, self-contained MQuAKE slices and a no-release supplement."""

from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from pathlib import Path

from scripts.r1_58_draw_streams import WRAPPER, candidates
from scripts.r1_d1g_freeze_register_v4 import ROOT, norm, policy_view, sha

from pccap.revision_v1.stage4_cell import write_json

REPLACED = {"locality_prompts", "locality_answers", "near_miss_candidates"}


def self_contained(rows):
    """Prefer same relation; deterministic source order breaks ties; never self-query."""
    if len(rows) < 2 or len({norm(r["subject"]) for r in rows}) != len(rows):
        raise ValueError("at least two distinct subjects required")
    output = []
    for row in rows:
        others = [r for r in rows if norm(r["subject"]) != norm(row["subject"])]
        others.sort(key=lambda r: (r.get("relation_id") != row.get("relation_id"), r["item_id"]))
        neighbours = others[:2]
        new = copy.deepcopy(row)
        new["locality_prompts"] = [r["prompt"] for r in neighbours]
        new["locality_answers"] = [r["target_true"] for r in neighbours]
        new["near_miss_candidates"] = [
            {
                "item_id": r["item_id"],
                "prompt": r["prompt"],
                "prompt_ids": r["prompt_ids"],
                "answer": r["target_true"],
                "aliases": [r["target_true"]],
                "subject_key": norm(r["subject"]),
                "relation_id": r.get("relation_id"),
                "source_case_id": r.get("source_case_id"),
                "reference": "source target_true; teacher agreement untested",
                "type": "same_relation_other_subject"
                if r.get("relation_id") == row.get("relation_id")
                else "other_relation_in_slice_fallback",
            }
            for r in neighbours
        ]
        output.append(new)
    validate_slice(output, rows)
    return output


def validate_slice(rows, original):
    known = {r["item_id"]: r for r in original}
    prompts = {r["prompt"] for r in rows}
    ids = {r["item_id"] for r in rows}
    if len(ids) != len(rows) or ids != known.keys():
        raise ValueError("slice membership changed")
    for row in rows:
        if {k: v for k, v in row.items() if k not in REPLACED} != {
            k: v for k, v in known[row["item_id"]].items() if k not in REPLACED
        }:
            raise ValueError("teacher-certified support changed")
        if not row["locality_prompts"] or not set(row["locality_prompts"]) <= prompts:
            raise ValueError("locality escapes slice")
        if row["prompt"] in row["locality_prompts"]:
            raise ValueError("self locality")
        if len(row["locality_answers"]) != len(row["locality_prompts"]):
            raise ValueError("unpaired locality")
        for n in row["near_miss_candidates"]:
            source = known.get(n["item_id"])
            if source is None or n["item_id"] == row["item_id"] or n["prompt"] != source["prompt"]:
                raise ValueError("near-miss escapes slice")
            if n["answer"] != source["target_true"] or n["prompt_ids"] != source["prompt_ids"]:
                raise ValueError("incorrect neighbour reference")
    return rows


def slice_documents(train_doc, dev_doc):
    train, dev = self_contained(train_doc["items"]), self_contained(dev_doc["items"][:100])
    if len(train) != 500 or len(dev) != 100:
        raise ValueError("round-11 requires 500 training and 100 development items")
    if {norm(r["subject"]) for r in train} & {norm(r["subject"]) for r in dev}:
        raise ValueError("train/development subject collision")
    policy = (
        "Only locality/near-miss fields replaced; deterministic same-relation preference, "
        "then another in-slice relation if fewer than two neighbours. References are original target_true, "
        "not teacher-agreement certificates. Prior exposure remains excluded."
    )
    td, dd = copy.deepcopy(train_doc), copy.deepcopy(dev_doc)
    td.update(name="train_pool_mquake_v3", items=train, exposure=policy)
    dd.update(
        name="mquake_dev_v3",
        items=dev,
        selection="v1 development first 100, source order retained",
        unrelated_prompts=list(dict.fromkeys(p for r in dev for p in r["locality_prompts"])),
        unrelated_source="deduplicated locality prompts of these same 100 development items",
    )
    for d in (td, dd):
        d["counts"] = {
            "pool": train_doc["counts"]["pool"],
            "train": 500,
            "dev": 100,
            "prospective_primary_subjects": 600,
        }
        d["slice_policy"] = policy
    return td, dd


def build_supplement(train_path, dev_path, producer=__file__):
    historical_path = ROOT / "manifests/revision_v1/exclusions_frozen_v4_supplement_v1_rebound.json"
    historical = json.loads(historical_path.read_text())
    for path, expected in historical["bindings_sha256"].items():
        if sha(path) != expected:
            raise ValueError("historical binding mismatch: " + path)
    bindings = {**historical["bindings_sha256"], str(historical_path): sha(historical_path)}

    def read(path):
        path = Path(path).resolve()
        bindings[str(path)] = sha(path)
        return json.loads(path.read_text())

    td, dd = read(train_path), read(dev_path)
    old_train = read(ROOT / "manifests/revision_v1/train_pool_mquake_v1.json")
    old_dev = read(ROOT / "manifests/dev/mquake_dev.json")
    validate_slice(td["items"], old_train["items"])
    validate_slice(dd["items"], old_dev["items"][:100])
    if set(dd["unrelated_prompts"]) != {p for r in dd["items"] for p in r["locality_prompts"]}:
        raise ValueError("development unrelated inventory differs from slice locality")
    wrapper = read(WRAPPER)
    register = read(wrapper["register"]["path"])
    reasons = defaultdict(set)
    for r in register["exclusions"]:
        reasons[r["canonical_subject_key"]].update(r["reasons"])
    original, _ = candidates("exception")
    prepared = read(ROOT / "manifests/revision_v1/mquake_items_v1.json")
    ref = prepared["artifacts"]["items"]
    if sha(ref["path"]) != ref["sha256"]:
        raise ValueError("prepared MQuAKE hash mismatch")
    bindings[ref["path"]] = ref["sha256"]
    teacher = read(ROOT / "manifests/revision_v1/mquake_pool_v1.json")
    known = {r["item_id"] for r in teacher["items"]}
    mq = [json.loads(s) for s in Path(ref["path"]).read_text().splitlines()]
    mq = [r for r in mq if r["item_id"] in known]

    def view(rs):
        return policy_view(
            original["zsre"],
            original["counterfact"],
            mq,
            rs,
            wrapper["policy"]["verified_alias_pairs"],
            train=td["items"],
            dev=dd["items"],
            unrelated=dd["unrelated_prompts"],
            teacher_available=True,
        )

    prospective = view(reasons)
    for r in historical["additional_exclusions"]:
        reasons[r["canonical_subject"]].update(r["reasons"])
    cumulative = view(reasons)
    for ds, rows in cumulative["candidates"].items():
        if not {r["item_id"] for r in rows} <= {r["item_id"] for r in historical["candidates"][ds]}:
            raise ValueError("supplement released historical exclusions")
    bindings[str(Path(producer).resolve())] = sha(producer)
    inventory = sorted(ROOT.glob("manifests/revision_v1/train_pool_mquake_v*.json")) + sorted(
        ROOT.glob("manifests/dev/mquake_dev*.json")
    )
    for p in inventory:
        bindings[str(p)] = sha(p)
    return {
        "name": "exclusions_frozen_v4_supplement_v2",
        "task": "R1-D4b",
        "schema_version": 2,
        "status": "cumulative exclusions retained; prospective capacity is a counterfactual only",
        "parent": {"path": str(historical_path), "sha256": sha(historical_path)},
        "policy": historical["policy"],
        "bindings_sha256": bindings,
        "source_inventory": [str(p) for p in inventory],
        **cumulative,
        "new_exposure_counts_scope": "new v3 slices only; cumulative reasons/candidates retain all historical exposure",
        "historical_exposure_counts": historical["new_exposure_counts"],
        "prospective_only": {
            "status": "NOT ADMITTED; assumes historical MQuAKE work never happened",
            "counts": prospective["counts"],
            "new_exposure_counts": prospective["new_exposure_counts"],
        },
        "final_draw_ready": False,
        "draw_authorized": False,
        "confirmation_protocol_frozen": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "gpu_seconds": 0,
        "released_subjects": 0,
        "limits": [
            "Retraining on smaller slices cannot erase earlier development/training exposure.",
            "R1-X9 may identify reservation-only candidates; only the lead can adopt a release.",
            "Near-miss candidates are self-contained; scarce relations use labelled cross-relation fallback.",
            "Primary-only accounting does not certify incidental context/entity or alias independence.",
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="create new v3 slices and supplement v2")
    args = ap.parse_args(argv)
    if not args.write:
        ap.error("--write required; this creates no draws or seals")
    tp = ROOT / "manifests/revision_v1/train_pool_mquake_v3.json"
    dp = ROOT / "manifests/dev/mquake_dev_v3.json"
    sp = ROOT / "manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json"
    if any(p.exists() for p in (tp, dp, sp)):
        raise FileExistsError("versioned outputs already exist")
    td, dd = slice_documents(
        json.loads((ROOT / "manifests/revision_v1/train_pool_mquake_v1.json").read_text()),
        json.loads((ROOT / "manifests/dev/mquake_dev.json").read_text()),
    )
    for d, p in (
        (td, ROOT / "manifests/revision_v1/train_pool_mquake_v1.json"),
        (dd, ROOT / "manifests/dev/mquake_dev.json"),
    ):
        d["derived_from"] = {"path": str(p), "sha256": sha(p)}
    write_json(tp, td)
    write_json(dp, dd)
    result = build_supplement(tp, dp)
    write_json(sp, result)
    print(
        json.dumps(
            {"cumulative": result["counts"], "prospective_only": result["prospective_only"]},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
