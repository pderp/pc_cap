"""R1-20b: materialize a development corpus and partition/prefix manifests on CPU.

Creates files exclusively. Episode payloads are external data under assets;
identities, policies and the optional teacher request stay in pc_cap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--assets-output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--teacher-request", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    args = ap.parse_args()
    data_dir = args.assets_output.resolve()
    if not data_dir.is_relative_to(ROOT.parent / "assets") or data_dir.exists():
        raise ValueError("a new external assets directory is required")
    for p in (args.manifest, args.teacher_request, args.log):
        if not p.resolve().is_relative_to(ROOT) or p.exists():
            raise ValueError("manifest/log destinations must be new files inside pc_cap")
    os.environ["JAX_PLATFORMS"], os.environ["CUDA_VISIBLE_DEVICES"] = "cpu", ""
    sys.path.insert(0, str(ROOT / "scripts"))
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.revision_v1 import episodes as ep
    from r1_20_text_adapter import tokenize_natural_episode

    source = Path(ep.__file__)
    implementation_sha = sha(source)
    rows, source_hashes = ep.load_development(ROOT)
    assignment = ep.partition_dev_records(rows, seed=91)
    by_id = {r["item_id"]: r for r in rows}
    tok = GPT2Tokenizer()
    corpus, requests, subject_uses, scopes = {}, {}, {}, {}
    settings = {"train": (1000, 128), "dev": (5000, 16), "test": (9000, 16)}
    for split, (seed_start, count) in settings.items():
        episodes, attempted, rejected = [], [], []
        for seed in range(seed_start, seed_start + 4*count):
            attempted.append(seed)
            try:
                episode = ep.natural_episode(rows, seed, split, history_size=4, dataset="counterfact")
                ep.validate_episode(episode)
                episode = tokenize_natural_episode(episode, tok)
            except ValueError as exc:
                rejected.append({"seed": seed, "reason": str(exc)})
                continue
            new_paras = [x for x in episode.query_labels if x.role == "new_paraphrase"]
            qmap = {q.query_id: q for q in episode.inputs.queries}
            if len(new_paras) < 2 or len({qmap[x.query_id].prompt_ids for x in new_paras}) < 2:
                raise ValueError("emitted episode lacks two distinct paraphrases")
            provenance = dict(episode.provenance)
            item_ids = json.loads(provenance["source_items"])
            if any(assignment[i] != split for i in item_ids):
                raise ValueError("cross-partition episode source")
            for item_id in item_ids:
                subject_uses.setdefault(by_id[item_id]["subject"], set()).add(episode.episode_id)
            for label in episode.query_labels:
                q = qmap[label.query_id]
                prefix = list(q.prompt_ids)
                # Teacher-forced prefixes are an optional diagnostic on training/eval
                # containers. Teacher imitation is permitted ONLY for scope roles.
                targets = list(label.target_ids) or [None]
                for index, target in enumerate(targets):
                    key = ep.digest(prefix)
                    request = requests.setdefault(key, {"prefix_sha256": key, "ids": prefix.copy(), "uses": []})
                    request["uses"].append({"episode_id": episode.episode_id, "split_id": split,
                                             "query_id": q.query_id, "role": label.role, "position": index,
                                             "preservation_training_allowed": label.role in ("near_miss", "unrelated")})
                    if target is not None:
                        prefix.append(int(target))
            episodes.append(asdict(episode))
            if len(episodes) == count:
                break
        if len(episodes) != count:
            raise ValueError(f"{split}: requested {count} whole episodes, obtained {len(episodes)}")
        corpus[split] = episodes
        scopes[split] = {"episode_count": count, "generator_seeds": [e["generator_seed"] for e in episodes],
                         "attempted_seeds": attempted, "rejections": rejected,
                         "roles": dict(Counter(l["role"] for e in episodes for l in e["query_labels"]))}
    if sha(source) != implementation_sha or any(sha(p) != h for p, h in source_hashes.items()):
        raise ValueError("generator or development source changed during construction")
    data_dir.mkdir(parents=True, exist_ok=False)
    datasets = {}
    for split, payloads in corpus.items():
        path = data_dir / f"counterfact_{split}.jsonl"
        with path.open("x") as f:
            for payload in payloads:
                f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True)+"\n")
        datasets[split] = {"path": str(path), "sha256": sha(path), **scopes[split]}
    manifest = {"name": "revision-v1-development-episodes", "version": 1, "mode": "development",
                "written_utc": datetime.now(timezone.utc).isoformat(),
                "generator": {"path": str(source.relative_to(ROOT)), "sha256": implementation_sha},
                "text_adapter_sha256": sha(ROOT / "scripts/r1_20_text_adapter.py"),
                "tokenizer_sha256": tok.file_sha256(), "source_sha256": source_hashes,
                "natural": {"partition_seed": 91, "assignment": assignment, "datasets": datasets,
                            "partition_policy": "connected fact/entity/operational-family components across BOTH development pools before episode generation",
                            "zsre": "evaluation streams only, DEC-034(b); no second paraphrase fabricated",
                            "emitted_source_subjects": sorted(subject_uses),
                            "emitted_subject_episode_uses": {s: sorted(v) for s, v in sorted(subject_uses.items())}},
                "synthetic": {"generator_version": "grammar-private-scope-v1", "rule_seed": 7,
                              "entity_contexts": ep.CONTEXT_SPLITS, "surface_initial_classes": ep.FAMILY_SPLITS,
                              "fact_scopes": {s: [[c, v] for c in cs for v in range(9)] for s, cs in ep.CONTEXT_SPLITS.items()},
                              "composition": "fixed opcode 1 shared deliberately; first class-4 output index becomes second class-3 input index",
                              "paraphrase_gate": "at least two distinct queries unseen in support; reject the whole episode on exhaustion",
                              "sequence_seed_formula": "6000000 + episode_seed*100000 + slot*2048 + attempt; support slots 0..10, query slots 20..24; attempts 0..1023",
                              "known_development_episode_seed_reservations": [[0, 999999]],
                              "proposed_final_episode_seed_reservation": [1000000, 1099999],
                              "proposed_final_sequence_seed_envelope": [100006000000, 110005999999],
                              "final_generation_version": "grammar-private-scope-v2-reserved-not-implemented",
                              "final_generation_ready": False,
                              "final_entity_gate": "All 8 v1 contexts and 72 scope facts were exposed by development audit. A new seed alone cannot create entity-disjoint confirmation; implement and freeze a new entity namespace/version before use.",
                              "reservation_status": "proposed for owner approval; no final examples generated or sealed"},
                "teacher_policy": "Installed L3 computes write-free prefix KL on demand. Optional request supplies separate greedy/top-k diagnostics; answer-role teacher outputs never replace revised labels.",
                "limitations": ["Split test is inspected development-audit data, not fresh confirmation.",
                                "Source-subject partitioning does not resolve all entities/aliases in context and neighborhood prompts.",
                                "No E.2 filtering, teacher execution, model training or confirmation selection performed."]}
    write_new(args.manifest, manifest)
    write_new(args.teacher_request, {"name": "revision-v1-optional-teacher-diagnostic-request", "version": 1,
                                    "episode_manifest": str(args.manifest), "episode_manifest_sha256": sha(args.manifest),
                                    "tokenizer_sha256": tok.file_sha256(), "model_identity": "pinned BP teacher in manifests/assets.json",
                                    "blocking_training": False, "gpu_execution_owner": "orchestrator",
                                    "requested_outputs": {"greedy_max_new_tokens": 32, "stop": "newline or EOS; record truncation", "top_k_logits": 32,
                                                          "logits": "raw top-k values plus logsumexp; these do not substitute for full-distribution KL"},
                                    "prefixes": [requests[k] for k in sorted(requests)],
                                    "rule": "No teacher target enters answer-role training. Generation/scoring annotations are never prediction arguments."})
    summary = {"manifest": str(args.manifest), "manifest_sha256": sha(args.manifest),
               "episodes": {s: len(x) for s, x in corpus.items()}, "emitted_source_subjects": len(subject_uses),
               "teacher_prefixes": len(requests), "all_emitted_episodes_have_two_paraphrases": True,
               "final_synthetic_generation_ready": False, "gpu_seconds": 0}
    write_new(args.log, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
