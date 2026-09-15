"""Synthetic v4 exception, exposure and immutable-source tests."""

from copy import deepcopy

import pytest
from scripts.r1_d1g_freeze_register_v4 import policy_view, validate


def item(i, subject, ds):
    return {
        "item_id": i,
        "subject": subject,
        "dataset": ds,
        "prompt": subject + " works at",
        "answer": "new",
        "locality_prompts": [],
    }


def test_exception_waives_only_old_counterfact_reason():
    a, b = item("a", "A", "counterfact"), item("b", "B", "counterfact")
    m = policy_view(
        [],
        [a, b],
        [],
        {"a": {"old_eligible:counterfact"}, "b": {"old_eligible:counterfact", "training"}},
        {},
    )
    assert [r["item_id"] for r in m["candidates"]["counterfact"]] == ["a"]
    assert m["removals"]["counterfact"][0]["reasons"] == ["training"]


def test_exception_does_not_waive_same_reason_for_other_dataset():
    m = policy_view([item("a", "A", "zsre")], [], [], {"a": {"old_eligible:counterfact"}}, {})
    assert not m["candidates"]["zsre"]


def test_zsre_priority_and_all_other_relations_removed_from_mquake():
    z = item("z", "Shared", "zsre")
    mq = [
        item("m1", "shared", "mquake"),
        item("m2", "SHARED", "mquake"),
        item("m3", "fresh", "mquake"),
    ]
    m = policy_view([z], [], mq, {}, {})
    assert len(m["candidates"]["zsre"]) == len(m["candidates"]["mquake"]) == 1
    assert m["cross_dataset_overlap"]["zsre_mquake_subjects"] == 1
    assert m["cross_dataset_overlap"]["mquake_overlap_items"] == 2


def test_declared_queries_override_source_priority_and_remove_subject_everywhere():
    z, train, q = (
        item("z", "shared", "zsre"),
        item("t", "train", "mquake"),
        item("q", "Shared", "mquake"),
    )
    train["locality_prompts"] = [q["prompt"]]
    m = policy_view([z], [], [train, q], {}, {}, train=[train])
    assert not m["candidates"]["zsre"] and not m["candidates"]["mquake"]
    assert (
        m["cross_dataset_overlap"]["shared_subjects_lost_from_zsre_due_to_new_query_exposure"] == 1
    )


def test_unrelated_query_and_primary_union_do_not_double_count():
    a, b = item("a", "A", "mquake"), item("b", "B", "mquake")
    m = policy_view(
        [], [], [a, b], {}, {}, train=[a], unrelated=[a["prompt"], b["prompt"], b["prompt"]]
    )
    assert m["new_exposure_counts"] == {
        "primary": 1,
        "locality": 0,
        "development_unrelated": 2,
        "union": 2,
    }


def test_teacher_pool_is_provenance_not_wholesale_training_exposure():
    row = item("m", "fresh", "mquake")
    pending = policy_view([], [], [row], {}, {})
    present = policy_view([], [], [row], {}, {}, teacher_available=True)
    assert pending["teacher_pool_binding"] == "pending"
    assert present["teacher_pool_binding"] == "present"
    assert len(present["candidates"]["mquake"]) == 1


def test_verified_alias_and_nfkc_exclusions():
    m = policy_view(
        [item("x", " Ａ  B ", "zsre")], [], [], {"canonical": {"old"}}, {"a b": "canonical"}
    )
    assert not m["candidates"]["zsre"]


def test_unknown_query_preserved_and_inputs_not_mutated():
    row = item("a", "A", "mquake")
    before = deepcopy(row)
    m = policy_view([], [], [row], {}, {}, unrelated=["unmapped?"])
    assert row == before
    assert len(m["unmapped_declared_query_prompts"]) == 1


def test_duplicate_source_id_refused():
    r = item("a", "A", "mquake")
    with pytest.raises(ValueError, match="duplicate"):
        policy_view([], [], [r, r], {}, {})


def document():
    result = policy_view([], [], [], {}, {})
    return {
        "name": "exclusions_frozen_v4",
        "policy": {"waived_reason": "old_eligible:counterfact"},
        **result,
        "final_draw_ready": False,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "draws_emitted": 0,
        "seals_emitted": 0,
        "bindings_sha256": {},
    }


@pytest.mark.parametrize("flag", ["final_draw_ready", "draw_authorized", "seals_emitted"])
def test_register_never_admits_draw(flag):
    m = document()
    m[flag] = True
    with pytest.raises(ValueError, match="cannot authorize"):
        validate(m)


def test_child_hash_mismatch_refused(tmp_path):
    p = tmp_path / "source"
    p.write_text("source")
    m = document()
    m["bindings_sha256"] = {str(p): "0" * 64}
    with pytest.raises(ValueError, match="child input changed"):
        validate(m)
