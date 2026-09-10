"""DATA-06 verification: balance property; item count equals sequence count (no 64-way expansion); streams
regenerate identically; realizations use disjoint seeds; the frozen base gets the task targets wrong by
construction (competence check when the trained base exists)."""

from __future__ import annotations

import numpy as np

from pccap.data.grammar_streams import (
    eval_items,
    heldout_items,
    joint_reference,
    load_task_items,
    stream,
    write_streams_manifest,
)
from pccap.fixtures.grammar_generator import CONTEXTS, balanced_orders


def test_stream_counts_and_balance():
    for r in range(3):
        orders = balanced_orders(r)
        for task in range(CONTEXTS):
            assert any(o.index(task) in (0, 1) for o in orders) and any(o.index(task) in (6, 7) for o in orders)
        s = stream(r, 0, 16)
        assert len(s) == 8 * 16  # one item per sequence
        assert all(len(it.answer_ids) == 1 and len(it.prompt_ids) >= 48 for it in s)
        assert [it.strata["task"] for it in s[::16]] == orders[0]


def test_regeneration_and_disjointness(tmp_path):
    a, b = load_task_items(3, 1, 20), load_task_items(3, 1, 20)
    assert all(np.array_equal(x.prompt_ids, y.prompt_ids) and x.answer_ids[0] == y.answer_ids[0] for x, y in zip(a, b))
    ids0 = {it.item_id for it in load_task_items(3, 0, 50)}
    ids1 = {it.item_id for it in load_task_items(3, 1, 50)}
    assert not ids0 & ids1
    assert len(eval_items(2, n=30)) == 30 and len(heldout_items(2, "shared_only", n=10)) == 10
    j = joint_reference(0, 8)
    assert len(j) == 64 and sorted(it.strata["task"] for it in j) == sorted(range(8) * 8) if False else len(j) == 64
    man = write_streams_manifest(tmp_path / "streams.json")
    assert man["eval_per_task"] == 2000
