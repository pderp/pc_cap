"""DEC-056 bounded historical MQuAKE review; CPU, no model or final payload access."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip
import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

from scripts import r1_76_unseen_common as common

from pccap.bases.gpt2_jax import DEFAULT_SNAPSHOT
from pccap.data.streams import normalize_answer
from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.revision_v1.analysis import digest

ROOT = Path(__file__).resolve().parents[1]
LABEL = "new to the selected reader's training; historically exposed elsewhere"


def words(text):
    return tuple(re.findall(r"[^\W_]+", common.norm(text)))


def texts(row):
    return [row["prompt"], *row.get("paraphrases", []), *row.get("locality_prompts", [])]


def review():
    sources = {}

    def read(path):
        path = Path(path).resolve()
        if "confirm" in path.parts:
            raise PermissionError("no final sealed input")
        sources[str(path)] = common.sha(path)
        return json.loads(path.read_text())

    primary = read(ROOT / "manifests/revision_v1/primary_condition_v5.json")
    summary = read(ROOT / "results/R1/pilot/r1_50_stream_sel6_text_s2/summary.json")
    if (
        summary["args"]["pool_items"] != 1000
        or summary["args"]["seed"] != 2
        or summary.get("memory_guard_abort")
    ):
        raise ValueError("selected training prefix mismatch")
    training = []
    for path in common.TRAIN_FILES.values():
        pool = read(path)
        if sources[str(path)] != primary["pools"][path.stem]:
            raise ValueError("training binding mismatch")
        rows = pool["items"][:1000]
        bank = next(b for b in summary["banks"] if (ROOT / b["pool"]).resolve() == path)
        if bank["identity"]["n_items"] != len(rows):
            raise ValueError("training count mismatch")
        training += rows
    paths = [
        ROOT / "manifests/revision_v1/train_pool_mquake_v2.json",
        ROOT / "manifests/dev/mquake_dev.json",
    ]
    rows = [r for p in paths for r in read(p)["items"]]
    register = read(ROOT / "manifests/revision_v1/exclusions_frozen_v6.json")
    final_subjects = {
        common.norm(r["canonical_subject"]) for rs in register["candidates"].values() for r in rs
    }
    wrapper = read(ROOT / "manifests/revision_v1/exclusions_frozen_v3.json")
    aliases = wrapper["policy"]["verified_alias_pairs"]
    if isinstance(aliases, list):
        raise ValueError("unexpected inherited alias mapping")

    def canonical(s):
        s = common.norm(s)
        seen = set()
        while s in aliases:
            if s in seen:
                raise ValueError("alias cycle")
            seen.add(s)
            s = common.norm(aliases[s])
        return s

    banned = common.rowsets(training)
    query_text = {common.norm(q) for r in training for q in texts(r) if q.strip()}
    banned[3].update(query_text)
    trained_names = {words(canonical(r["subject"])) for r in training}
    final_names = {words(canonical(s)) for s in final_subjects}
    query_words = [words(q) for q in query_text]
    teacher = read(ROOT / "manifests/revision_v1/mquake_pool_v1.json")
    teacher_rows = {r["item_id"]: r for r in teacher["items"]}
    for path, expected in teacher["sources_sha256"].items():
        if common.sha(path) != expected:
            raise ValueError("teacher source mismatch")
        sources[path] = expected
    tok = GPT2Tokenizer()
    sources[str(tok.path)] = tok.file_sha256()
    config = read(Path(DEFAULT_SNAPSHOT) / "config.json")
    limit = config["n_positions"]
    used = [set() for _ in range(4)]
    stages = Counter(input_rows=len(rows))
    reasons = []
    safe = []
    candidate_queries = {}
    alias_names = set()
    for row in rows:
        rid = row["item_id"]
        key = common.keys(row)
        reason = None
        if any(k in b for k, b in zip(key, banned, strict=True)):
            reason = "selected_training_item_subject_or_exact_query"
        elif any(k in b for k, b in zip(key, used, strict=True)):
            reason = "duplicate_historical_identity"
        if reason:
            stages[reason] += 1
            reasons.append({"item_id": rid, "reason": reason})
            continue
        for k, b in zip(key, used, strict=True):
            b.add(k)
        stages["metadata700"] += 1
        name = words(canonical(row["subject"]))
        if name in final_names:
            reason = "final_register_subject_or_punctuation_equivalent"
        elif not name or name in trained_names:
            reason = "selected_training_alias_or_punctuation_equivalent"
        elif any(
            any(q[i : i + len(name)] == name for i in range(len(q) - len(name) + 1))
            for q in query_words
        ):
            reason = "subject_mention_in_selected_training_query_context"
        elif any(common.norm(q) in query_text for q in texts(row)):
            # Historical locality is not executed; only own/paraphrase queries count below.
            if any(
                common.norm(q) in query_text for q in [row["prompt"], *row.get("paraphrases", [])]
            ):
                reason = "own_or_paraphrase_training_query_overlap"
        if reason:
            stages[reason] += 1
            reasons.append({"item_id": rid, "reason": reason})
            continue
        stages["alias_context_role_kept"] += 1
        original = teacher_rows.get(rid)
        fields = [
            "item_id",
            "fact_id",
            "subject",
            "prompt",
            "answer",
            "aliases",
            "paraphrases",
            "prompt_ids",
            "answer_ids",
            "teacher_generation",
            "teacher_stopped_by",
        ]
        if original is None or any(row.get(k) != original.get(k) for k in fields):
            reason = "teacher_row_mismatch"
        elif normalize_answer(row["teacher_generation"]) in {
            normalize_answer(a) for a in [row["answer"], *row["aliases"]]
        }:
            reason = "cached_teacher_already_correct"
        elif not row["paraphrases"] or any(
            not isinstance(a, str) or not normalize_answer(a)
            for a in [row["answer"], *row["aliases"]]
        ):
            reason = "empty_answer_alias_or_paraphrase"
        else:
            pair = tokenize_pair(tok, row["prompt"], row["answer"])
            if (
                pair.excluded
                or list(pair.prompt_ids) != row["prompt_ids"]
                or list(pair.answer_ids) != row["answer_ids"]
            ):
                reason = "token_reconstruction_or_answer_length"
            elif any(len(tok.encode(q)) + 32 > limit for q in [row["prompt"], *row["paraphrases"]]):
                reason = "context_length"
            elif any(
                t < 0 or t >= config["vocab_size"] for t in [*pair.prompt_ids, *pair.answer_ids]
            ):
                reason = "vocabulary"
        if reason:
            stages[reason] += 1
            reasons.append({"item_id": rid, "reason": reason})
            continue
        stages["teacher_token_context_kept"] += 1
        qkeys = {common.norm(q) for q in [row["prompt"], *row["paraphrases"]]}
        if name in alias_names or any(q in candidate_queries for q in qkeys):
            reason = "remaining_candidate_alias_or_query_collision"
            stages[reason] += 1
            reasons.append({"item_id": rid, "reason": reason})
            continue
        alias_names.add(name)
        for q in qkeys:
            candidate_queries[q] = rid
        # Execution uses only support and outside prompts. Drop historical
        # locality/near-miss references, which can escape the reviewed inventory.
        emitted = {
            k: copy.deepcopy(row[k])
            for k in [
                "item_id",
                "fact_id",
                "dataset",
                "subject",
                "prompt",
                "answer",
                "aliases",
                "paraphrases",
                "prompt_ids",
                "answer_ids",
            ]
        }
        emitted["exposure_label"] = LABEL
        emitted["historical_source_row_sha256"] = digest(row)
        safe.append(emitted)
    stages["cleared_historical_rows"] = len(safe)
    if stages["metadata700"] != 700:
        raise ValueError("historical 700 inventory changed")
    population = None
    if len(safe) >= 400:
        population = common.choose_population(
            "mquake", safe, [], training, checkpoints=[100, 300], test_fixture=True
        )
        population["selection"] = {
            "rule": "bound historical v2 training then legacy dev source order; after conservative filters first300 edits, next100 outside",
            "candidate_safe_count": len(safe),
            "outcome_dependent": False,
            "exposure_label": LABEL,
            "limits": "bounded supplied metadata and inherited verified aliases; unknown entity aliases are not globally certified; cached teacher evidence, not a fresh model pass",
        }
        population["missing_checkpoints"] = [1000]
        population["decision"] = "DEC-056"
        population["primary_reference"] = {
            "path": str(ROOT / "manifests/revision_v1/primary_condition_v5.json"),
            "sha256": common.sha(ROOT / "manifests/revision_v1/primary_condition_v5.json"),
        }
        population["sources_sha256"] = sources
        population["training_prefix_counts"] = {"zsre": 1000, "counterfact": 1000, "mquake": 500}
    for p, h in sources.items():
        if common.sha(p) != h:
            raise ValueError("review source changed")
    report = {
        "task": "R1-76b",
        "decision": "DEC-056",
        "counts": dict(stages),
        "exclusions": reasons,
        "population_available": population is not None,
        "needed": 400,
        "checkpoints": [100, 300],
        "absent_checkpoints": [1000],
        "exposure_label": LABEL,
        "final_register_subjects_used": 0,
        "model_calls": 0,
        "gpu_seconds": 0,
        "sources_sha256": sources,
        "teacher_status": "cached historical teacher generation and exact support row checked; original pool does not record base weight hash, so no new final-base teacher certificate",
        "alias_scope": "NFKC/casefold/whitespace, inherited verified aliases, punctuation token equality; conservative subject mentions in exact selected-reader training query text quarantined; no external entity-resolution claim",
        "runner_gate": "existing r1_76_unseen_common production validator rejects 100/300; a versioned DEC056 cadence patch must be approved before execution",
    }
    return report, population


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--population", type=Path, required=True)
    ap.add_argument("--spec", type=Path, required=True)
    args = ap.parse_args(argv)
    for p, parent in [
        (args.report, ROOT / "logs"),
        (args.spec, ROOT / "docs/tasks"),
        (args.population, common.RESOURCE_ROOT),
    ]:
        if p.exists() or not p.resolve().is_relative_to(parent):
            raise ValueError("new correctly located outputs required")
    report, population = review()
    if population is None:
        raise ValueError("clearance leaves fewer than400 rows; do not weaken filters")
    for p, value in [(args.report, report), (args.population, population)]:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("x") as f:
            json.dump(value, f, indent=2, sort_keys=True)
            f.write("\n")
    spec = {
        "task": "R1-76b",
        "status": "prepared_pending_DEC056_runner_patch",
        "population": {
            "path": str(args.population.resolve()),
            "sha256": common.sha(args.population),
        },
        "population_identity": digest(population),
        "primary_reference": population["primary_reference"],
        "dataset": "mquake",
        "checkpoints": [100, 300],
        "outside_n": 100,
        "missing_checkpoints": [1000],
        "decision": "DEC-056",
        "exposure_label": LABEL,
        "report": {"path": str(args.report.resolve()), "sha256": common.sha(args.report)},
        "launch_authorized": False,
        "model_calls": 0,
        "gpu_seconds": 0,
        "runner_bindings": {
            n: common.sha(ROOT / n)
            for n in ["scripts/r1_76_unseen_common.py", "scripts/r1_75_analysis_stage4_v1.py"]
        },
        "runner_status": "current hash bound for inspection; rebind only after approved cadence patch, do not use test_fixture for real-base execution",
    }
    with args.spec.open("x") as f:
        json.dump(spec, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(report["counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
