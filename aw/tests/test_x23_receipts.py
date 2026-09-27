"""Reject altered authority and watch evidence, using real completed receipts."""

import copy
import hashlib
import json

import pytest

from aw import x23_receipts as a


@pytest.fixture(scope="module")
def inputs():
    v1ref = a.ref(a.ROOT / "docs/tasks/R1-final-queue-bindings.json")
    v2ref = a.ref(a.ROOT / "docs/tasks/R1-final-queue-bindings-v2.json")
    v1, v2 = a.read(v1ref), a.read(v2ref)
    cells = a.queue.analysis.all_cells(a.read(v1["matrix"]))
    paths = {
        json.loads(p.read_bytes())["cell_id"]: p
        for p in (a.ROOT / "logs/R1/final_queue").glob("*/start.json")
    }
    return v1ref, v1, v2ref, v2, cells, paths


def test_receipts_require_the_original_or_amended_ceiling_at_the_right_boundary(inputs):
    v1ref, v1, v2ref, v2, cells, paths = inputs
    for ordinal in (90, 91, 136, 270):
        start = json.loads(paths[cells[ordinal - 1]["cell_id"]].read_bytes())
        expected = 1.15 if ordinal <= 90 else 1.7
        assert a.authority(start, ordinal, v1ref, v1, v2ref, v2) == expected
        altered = copy.deepcopy(start)
        altered["effective_wall_ceiling_seconds"] = start["solo_wall_ceiling_seconds"] * (
            1.7 if ordinal <= 90 else 1.15
        )
        with pytest.raises(ValueError, match="ceiling factor"):
            a.authority(altered, ordinal, v1ref, v1, v2ref, v2)
        altered = copy.deepcopy(start)
        altered["bindings_sha256"] = (v2ref if ordinal <= 90 else v1ref)["sha256"]
        with pytest.raises(ValueError, match="bindings version"):
            a.authority(altered, ordinal, v1ref, v1, v2ref, v2)


def test_changed_bound_receipt_is_rejected(tmp_path):
    p = tmp_path / "receipt.json"
    p.write_text('{"status":"original"}')
    binding = a.ref(p)
    p.write_text('{"status":"altered"}')
    with pytest.raises(ValueError, match="source changed|binding changed"):
        a.read(binding)


def test_historical_watch_is_verified_from_its_exact_prefix(inputs):
    _, _, _, _, cells, paths = inputs
    p = paths[cells[135]["cell_id"]].with_name("decision.json")
    decision = json.loads(p.read_bytes())
    lines = (
        (a.ROOT / "logs/R1/reports/comparators-270/watch-prefix.jsonl")
        .read_bytes()
        .splitlines(keepends=True)
    )
    events = [json.loads(line) for line in lines]
    running = hashlib.sha256()
    prefixes = {}
    for i, line in enumerate(lines, 1):
        running.update(line)
        prefixes[running.hexdigest()] = i
    recipe = json.loads(paths[cells[135]["cell_id"]].read_bytes())["recipe"]
    watch_id = a.watch.full.digest(
        dict(
            mode="stage4_sealed_cell",
            recipe_sha256=recipe["sha256"],
            cell={k: cells[135][k] for k in a.queue.analysis.COORDS},
        )
    )
    observation = next(e["observation"] for e in events if e["observation"]["cell_id"] == watch_id)
    contexts = a.contexts()
    checked = a.decision_watch(decision, observation, events, prefixes, contexts)
    assert checked["events"] < len(events)
    altered = copy.deepcopy(decision)
    altered["fidelity_watch"]["breaches"] += 1
    with pytest.raises(ValueError, match="watch counts"):
        a.decision_watch(altered, observation, events, prefixes, contexts)
    altered = copy.deepcopy(decision)
    altered["fidelity_watch"]["journal"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="prefix missing"):
        a.decision_watch(altered, observation, events, prefixes, contexts)
    altered = copy.deepcopy(decision)
    altered["fidelity_watch"]["document"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="document differs"):
        a.decision_watch(altered, observation, events, prefixes, contexts)
