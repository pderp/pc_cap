"""R1-D1g additive exposure supplement for pools created after the v4 snapshot."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from scripts.r1_58_draw_streams import WRAPPER, candidates
from scripts.r1_d1g_freeze_register_v4 import ROOT, norm, policy_view, sha, validate

from pccap.revision_v1.stage4_cell import write_json


def union_training(documents, known, teacher_binding):
    union = {}
    for doc in documents:
        if doc.get("sources_sha256") != teacher_binding:
            raise ValueError("training version binds a different teacher pool")
        for row in doc["items"]:
            if row != known.get(row["item_id"]):
                raise ValueError("training row differs from teacher pool")
            union[row["item_id"]] = row
    return list(union.values())


def current_sources():
    return sorted(ROOT.glob("manifests/revision_v1/train_pool_mquake_v*.json")) + sorted(
        ROOT.glob("manifests/dev/mquake_dev*.json")
    )


def build(parent_path):
    parent_path = Path(parent_path).resolve()
    parent = validate(json.loads(parent_path.read_text()))
    bindings = {**parent["bindings_sha256"], str(parent_path): sha(parent_path)}

    def read(path):
        path = Path(path).resolve()
        bindings[str(path)] = sha(path)
        return json.loads(path.read_text())

    teacher_path = ROOT / "manifests/revision_v1/mquake_pool_v1.json"
    teacher = read(teacher_path)
    teacher_binding = {"path": str(teacher_path), "sha256": sha(teacher_path)}
    known = {r["item_id"]: r for r in teacher["items"]}
    sources = current_sources()
    docs = {str(p): read(p) for p in sources}
    train_docs = [docs[str(p)] for p in sources if p.parent.name == "revision_v1"]
    dev_docs = [docs[str(p)] for p in sources if p.parent.name == "dev"]
    train = union_training(train_docs, known, teacher_binding)
    dev, unrelated = {}, []
    for doc in dev_docs:
        if doc["source"] != teacher_binding:
            raise ValueError("development version binds a different teacher pool")
        for row in doc["items"]:
            if row != known.get(row["item_id"]):
                raise ValueError("development row differs from teacher pool")
            dev[row["item_id"]] = row
        unrelated.extend(doc["unrelated_prompts"])
    train_keys = {norm(r["subject"]) for r in train}
    dev_keys = {norm(r["subject"]) for r in dev.values()}
    if train_keys & dev_keys:
        raise ValueError("training/development subject collision across versions")
    wrapper = read(WRAPPER)
    register = read(wrapper["register"]["path"])
    reasons = defaultdict(set)
    for row in register["exclusions"]:
        reasons[row["canonical_subject_key"]].update(row["reasons"])
    original, _ = candidates("exception")
    prepared = read(ROOT / "manifests/revision_v1/mquake_items_v1.json")
    source = prepared["artifacts"]["items"]
    if sha(source["path"]) != source["sha256"]:
        raise ValueError("prepared items changed")
    mq = [json.loads(line) for line in Path(source["path"]).read_text().splitlines()]
    mq = [r for r in mq if r["item_id"] in known]
    view = policy_view(
        original["zsre"],
        original["counterfact"],
        mq,
        reasons,
        wrapper["policy"]["verified_alias_pairs"],
        train=train,
        dev=list(dev.values()),
        unrelated=unrelated,
        teacher_available=True,
    )
    parent_sets = {ds: {r["item_id"] for r in rows} for ds, rows in parent["candidates"].items()}
    for ds, rows in view["candidates"].items():
        if not {r["item_id"] for r in rows} <= parent_sets[ds]:
            raise ValueError("exposure supplement must never release parent exclusions")
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    result = {
        "name": "exclusions_frozen_v4_supplement_v1",
        "task": "R1-D1g",
        "schema_version": 1,
        "parent": {"path": str(parent_path), "sha256": sha(parent_path)},
        "status": "additive exposure snapshot; not a protocol freeze or final population admission",
        "policy": parent["policy"],
        "bindings_sha256": bindings,
        "source_inventory": [str(p) for p in sources],
        **view,
        "final_draw_ready": False,
        "draw_authorized": False,
        "confirmation_protocol_frozen": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "gpu_seconds": 0,
        "incremental_candidate_removals": {
            ds: len(parent_sets[ds] - {r["item_id"] for r in rows})
            for ds, rows in view["candidates"].items()
        },
        "training_union": {
            "version_count": len(train_docs),
            "items": len(train),
            "subjects": len(train_keys),
        },
        "limits": [
            *parent["limits"],
            "v4 remains a historical snapshot; current planning must also use this supplement",
            "all declared query lists are reserved conservatively; these counts do not assert every query was actually executed",
            "additional pool versions require a new supplement; never silently rebind an existing file",
        ],
    }
    validate_supplement(result)
    return result


def validate_supplement(result):
    if result["source_inventory"] != [str(p) for p in current_sources()]:
        raise ValueError("a pool version appeared/disappeared after this supplement")
    for path, expected in result["bindings_sha256"].items():
        if sha(path) != expected:
            raise ValueError("supplement child identity mismatch: " + path)
    if any(
        result[k]
        for k in (
            "final_draw_ready",
            "draw_authorized",
            "confirmation_protocol_frozen",
            "draws_emitted",
            "seals_emitted",
        )
    ):
        raise ValueError("exposure supplement cannot authorize a draw or seal")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--parent", type=Path, default=ROOT / "manifests/revision_v1/exclusions_frozen_v4.json"
    )
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args(argv)
    if (
        args.output.exists()
        or args.report.exists()
        or not args.output.resolve().is_relative_to(ROOT / "manifests")
        or not args.report.resolve().is_relative_to(ROOT / "logs")
    ):
        ap.error("new repository manifest and report required")
    result = build(args.parent)
    binding = write_json(args.output, result)
    report = {
        k: v
        for k, v in result.items()
        if k not in ("candidates", "removals", "additional_exclusions")
    }
    report["manifest"] = binding
    write_json(args.report, report)
    print(
        json.dumps(
            {
                "counts": result["counts"],
                "incremental_candidate_removals": result["incremental_candidate_removals"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
