"""R1-20 controls use the staged module while v0's source identity is frozen."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import asdict, fields, replace
from pathlib import Path

import pytest

ROOT = Path('/home/derp/cap/pc_cap')
MODULE = Path('/home/derp/cap/pc_cap/logs/r1_codex_20260913/proposed/r1_20_episodes.py')
spec = importlib.util.spec_from_file_location("r1_episode_fixture", MODULE)
ep = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ep
spec.loader.exec_module(ep)


@pytest.mark.parametrize("split", ep.SPLITS)
@pytest.mark.parametrize("seed", [0, 19, 109])
@pytest.mark.parametrize("history_size", [2, 8])
@pytest.mark.parametrize("revision", [False, True])
def test_synthetic_semantics_scope_and_composition(split, seed, history_size, revision):
    episode = ep.synthetic_episode(seed, split, history_size, revision=revision)
    assert episode == ep.synthetic_episode(seed, split, history_size, revision=revision)
    supports = episode.inputs.support_history + episode.inputs.new_support
    queries = {q.query_id: q for q in episode.prediction_inputs()}
    assert len(episode.inputs.support_history) == history_size
    assert len(episode.inputs.new_support) == 1
    assert len(episode.inputs.adaptation_batches()) == history_size + 1
    new = episode.inputs.new_support[0]
    old_versions = [s for s in episode.inputs.support_history if s.fact_id == new.fact_id]
    assert bool(old_versions) == revision
    for label in episode.query_labels:
        q = queries[label.query_id]
        assert ep.synthetic_oracle(q, supports) == label.target_ids
        if label.role in ("near_miss", "unrelated"):
            assert ep.synthetic_oracle(q, ()) == label.target_ids
        if label.role in ("new_paraphrase", "old_fact"):
            assert ep.synthetic_oracle(q, ()) != label.target_ids
        if label.role == "composition":
            assert len(label.supporting_record_ids) == 2
            for record_id in label.supporting_record_ids:
                fact_id = next(s.fact_id for s in supports if s.record_id == record_id)
                reduced = tuple(s for s in supports if s.fact_id != fact_id)
                assert ep.synthetic_oracle(q, reduced) != label.target_ids
    if revision:
        query = queries[next(x.query_id for x in episode.query_labels if x.role == "new_paraphrase")]
        assert ep.synthetic_oracle(query, episode.inputs.support_history) == old_versions[0].answer_ids
        assert old_versions[0].answer_ids != new.answer_ids


def test_query_labels_cannot_change_inputs_or_support_state():
    e = ep.synthetic_episode(73, revision=True)
    poisoned = replace(e, query_labels=tuple(replace(label, target_ids=(63,), role="poisoned",
                                                    supporting_record_ids=()) for label in e.query_labels))
    assert e.inputs.input_digest() == poisoned.inputs.input_digest()
    assert e.inputs.adaptation_batches() == poisoned.inputs.adaptation_batches()
    assert e.prediction_inputs() == poisoned.prediction_inputs()
    assert {f.name for f in fields(ep.PredictionQuery)} == {"query_id", "prompt_ids", "prompt"}
    assert "query_labels" not in asdict(e.inputs)
    supports = e.inputs.support_history + e.inputs.new_support
    assert [ep.synthetic_oracle(q, supports) for q in e.prediction_inputs()] == [ep.synthetic_oracle(q, supports) for q in poisoned.prediction_inputs()]


def test_actual_contexts_and_surface_families_are_disjoint():
    sets = {}
    for split in ep.SPLITS:
        entities, facts, families = set(), set(), set()
        for seed in range(12):
            e = ep.synthetic_episode(seed, split)
            for s in e.inputs.support_history + e.inputs.new_support:
                entities.add(s.entity_id)
                facts.add(s.fact_id)
                families.add(s.family_id)
            for label in e.query_labels:
                entities.update(label.entity_ids)
                if label.role != "composition":
                    families.add(label.family_id)
        sets[split] = (entities, facts, families)
    for a, b in (("train", "dev"), ("train", "test"), ("dev", "test")):
        assert all(not x & y for x, y in zip(sets[a], sets[b], strict=True))


def test_seed_determinism_across_fresh_processes():
    code = "import sys; sys.path.insert(0, '/home/derp/cap/pc_cap/logs/r1_codex_20260913/proposed'); import r1_20_episodes as e; print(e.digest(e.asdict(e.synthetic_episode(31, 'dev', revision=True))))"
    # Build the command without relying on this process's module cache/hash seed.
    outputs = []
    for seed in ("0", "713"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONDONTWRITEBYTECODE": "1",
               "JAX_PLATFORMS": "cpu", "CUDA_VISIBLE_DEVICES": ""}
        outputs.append(subprocess.check_output([sys.executable, "-c", code], cwd=ROOT, env=env, text=True))
    assert outputs[0] == outputs[1]


def _rows():
    return [{"item_id": f"cf-{i}", "fact_id": f"fact-{i}", "dataset": "counterfact",
             "subject": f"entity{i}", "relation_id": f"r{i // 10}",
             "prompt": f"entity{i} has role", "answer": f"role{i}",
             "paraphrases": [f"role for entity{i}", f"what is entity{i}'s role"],
             "locality_prompts": [f"past role for entity{i}"]} for i in range(120)]


def test_connected_partition_joins_entities_facts_and_families_before_sampling():
    rows = _rows()
    assignment = ep.partition_dev_records(rows)
    assert assignment == ep.partition_dev_records(list(reversed(rows)))
    for i in range(0, 120, 10):
        assert len({assignment[f"cf-{j}"] for j in range(i, i+10)}) == 1
    duplicate_entity = {**rows[0], "item_id": "zsre-x", "fact_id": "z-x", "relation_id": "unseen"}
    duplicate_fact = {**rows[1], "item_id": "zsre-y", "subject": "newsubject", "relation_id": "unseen-two"}
    assigned = ep.partition_dev_records([*rows, duplicate_entity, duplicate_fact])
    assert assigned["zsre-x"] == assigned["cf-0"]
    assert assigned["zsre-y"] == assigned["cf-1"]


def test_natural_adapter_does_not_fabricate_teacher_answers():
    e = ep.natural_episode(_rows(), 81)
    assert e.domain == "natural-development-v1"
    assert len(e.inputs.support_history) == 4
    for label in e.query_labels:
        if label.role in ("near_miss", "unrelated"):
            assert label.target is None
            assert label.target_source == "teacher_prediction_required"
        else:
            assert label.target is not None
    payload = json.dumps(asdict(e.inputs))
    assert "teacher_prediction_required" not in payload
    assert "supporting_record_ids" not in payload


def test_one_paraphrase_cannot_be_silently_duplicated():
    rows = _rows()
    for row in rows:
        row["paraphrases"] = [row["paraphrases"][0]] * 3 + [row["prompt"]]
    with pytest.raises(ValueError, match=">=2 distinct paraphrases"):
        ep.natural_episode(rows, 81)


@pytest.mark.parametrize("kwargs", [{"history_size": 1}, {"history_size": 9}, {"seed": -1}, {"split": "unknown"}])
def test_bad_generation_requests_refuse(kwargs):
    with pytest.raises(ValueError):
        ep.synthetic_episode(**{"seed": 1, **kwargs})


def test_duplicate_fact_ids_and_malformed_query_containers_refuse():
    with pytest.raises(ValueError, match="duplicate source item"):
        ep.partition_dev_records([_rows()[0], _rows()[0]])
    e = ep.synthetic_episode(2)
    with pytest.raises(ValueError, match="alignment"):
        ep.validate_episode(replace(e, query_labels=e.query_labels[:-1]))
