"""CPU coverage and separation audit of an explicitly selected R1-20 module.

Uses exclusive output creation. Synthetic oracle correctness is a data-generator
test, not a learned-model efficacy result. Natural scope labels remain unresolved
until a teacher/evaluation adapter supplies them.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--implementation", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--seeds", type=int, default=128)
    args = ap.parse_args()
    out, implementation = args.output_dir.resolve(), args.implementation.resolve()
    if not out.is_relative_to(ROOT) or out.exists() or args.seeds < 1:
        raise ValueError("new output directory inside pc_cap and positive seed count required")
    os.environ["JAX_PLATFORMS"], os.environ["CUDA_VISIBLE_DEVICES"] = "cpu", ""
    started = time.monotonic()
    spec = importlib.util.spec_from_file_location("r1_20_audited", implementation)
    ep = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ep
    spec.loader.exec_module(ep)
    source_hash = hashlib.sha256(implementation.read_bytes()).hexdigest()
    summaries, inventories, samples, hashes = {}, {}, [], {}
    for split in ep.SPLITS:
        entities, facts, families = set(), set(), set()
        roles, history_sizes = Counter(), Counter()
        for seed in range(args.seeds):
            e = ep.synthetic_episode(seed, split, 2+seed % 7, revision=bool(seed % 2))
            ep.validate_episode(e)
            supports = e.inputs.support_history + e.inputs.new_support
            qs = {q.query_id: q for q in e.prediction_inputs()}
            for label in e.query_labels:
                roles[label.role] += 1
                entities.update(label.entity_ids)
                if label.role != "composition":
                    families.add(label.family_id)
                if label.role == "composition":
                    for record in label.supporting_record_ids:
                        fact = next(s.fact_id for s in supports if s.record_id == record)
                        without = tuple(s for s in supports if s.fact_id != fact)
                        if ep.synthetic_oracle(qs[label.query_id], without) == label.target_ids:
                            raise ValueError(f"composition shortcut {split}/{seed}/{fact}")
            for s in supports:
                entities.add(s.entity_id)
                facts.add(s.fact_id)
                families.add(s.family_id)
            changed = replace(e, query_labels=tuple(replace(label, target_ids=(0,), target="POISON") for label in e.query_labels))
            if changed.inputs.input_digest() != e.inputs.input_digest() or changed.inputs.adaptation_batches() != e.inputs.adaptation_batches():
                raise ValueError("held-out labels reached input/support API")
            history_sizes[len(e.inputs.support_history)] += 1
            hashes[e.episode_id] = ep.digest(asdict(e))
            if seed < 2:
                samples.append(asdict(e))
        inventories[split] = (entities, facts, families)
        summaries[split] = {"episodes": args.seeds, "query_roles": dict(roles), "history_sizes": dict(history_sizes),
                            "unique_entities": len(entities), "unique_facts": len(facts), "families": sorted(families)}
    overlaps = {}
    for a, b in (("train", "dev"), ("train", "test"), ("dev", "test")):
        overlaps[f"{a}/{b}"] = {name: sorted(x & y) for name, x, y in zip(("entities", "facts", "noncomposition_families"), inventories[a], inventories[b], strict=True)}
        if any(overlaps[f"{a}/{b}"].values()):
            raise ValueError("synthetic partition overlap")
    rows, source_hashes = ep.load_development(ROOT)
    assignment = ep.partition_dev_records(rows)
    natural = {}
    for dataset in ("zsre", "counterfact"):
        natural[dataset] = {}
        for split in ep.SPLITS:
            selected = [r for r in rows if r["dataset"] == dataset and assignment[r["item_id"]] == split]
            entry = {"source_items": len(selected),
                     "items_with_two_paraphrases": sum(len(ep.usable_paraphrases(r)) >= 2 for r in selected)}
            try:
                e = ep.natural_episode(rows, 42, split, dataset=dataset)
                ep.validate_episode(e)
                entry.update(status="text_episode_constructed", episode_id=e.episode_id,
                             preservation_targets_pending=sum(x.target_source == "teacher_prediction_required" for x in e.query_labels))
                samples.append(asdict(e))
            except ValueError as exc:
                entry.update(status="unavailable", reason=str(exc))
            natural[dataset][split] = entry
    entity_splits, family_splits, fact_splits = {}, {}, {}
    for row in rows:
        split = assignment[row["item_id"]]
        entity_splits.setdefault(ep.normalize(row["subject"]), set()).add(split)
        fact_splits.setdefault(row["fact_id"], set()).add(split)
        for prompt in [row["prompt"], *row.get("paraphrases", [])]:
            family_splits.setdefault(ep.paraphrase_family(row, prompt), set()).add(split)
    natural_overlap = {name: sum(len(v) > 1 for v in mapping.values()) for name, mapping in
                       (("source_entities", entity_splits), ("fact_ids", fact_splits), ("operational_families", family_splits))}
    if any(natural_overlap.values()):
        raise ValueError("natural partition overlap")
    if hashlib.sha256(implementation.read_bytes()).hexdigest() != source_hash:
        raise ValueError("implementation changed during audit")
    for path, expected in source_hashes.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise ValueError("development pool changed during audit")
    report = {"task": "R1-20", "implementation": str(implementation), "implementation_sha256": source_hash,
              "synthetic": summaries, "synthetic_partition_overlaps": overlaps,
              "synthetic_composition_rule": "opcode 1; class-4 result index becomes next class-3 input index; both supporting facts necessary under oracle removal",
              "composition_template_overlap": "one fixed opcode shared deliberately across development splits",
              "synthetic_query_label_poisoning": "inputs and support adaptation batches unchanged for every episode",
              "synthetic_model_performance_tested": False, "natural_development": natural,
              "natural_source_partition_overlap_counts": natural_overlap,
              "development_source_sha256": source_hashes,
              "natural_partition_assignment": assignment, "episode_sha256": hashes,
              "limitations": ["Development fixtures only, including the split named test; no fresh confirmation selection.",
                              "Natural scope labels require separate teacher predictions; no training-ready teacher targets fabricated.",
                              "Natural neighborhood entities unresolved; source entity/family separation is not a complete prompt-entity leakage audit.",
                              "Text tokenization and adaptation/prediction integration wait for the Stage 1 owner.",
                              "Natural two-fact composition is unsupported without a verified relation graph.",
                              "The implementation is staged outside src to protect the v0 queue; installing it requires owner coordination."],
              "gpu_seconds": 0, "wall_seconds": time.monotonic()-started}
    out.mkdir(parents=True, exist_ok=False)
    for name, value in (("audit.json", report), ("sample_episodes.json", samples)):
        with (out / name).open("x") as f:
            json.dump(value, f, indent=2)
            f.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("episode_sha256", "natural_partition_assignment")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
