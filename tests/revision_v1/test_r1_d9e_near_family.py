"""Adopted source family, fixed missing slots and baseline equality."""
import copy

import pytest
from scripts.r1_49g_analyze import near_family_summary
from scripts.r1_d9e_near_family import near_key, pair_reserved, validate_section


def row(i, ds="counterfact", relation="P1", subject=None):
    subject = subject or i
    return dict(item_id=i, dataset=ds, subject=subject, prompt=f"Where does {subject} live?",
                answer="stored source answer", relation_id=relation)


def test_deterministic_matching_and_fixed_missing_slots():
    supports = [row("b"), row("a"), row("c", relation="P2")]
    neighbours = [row("y"), row("x"), row("z", relation="P3")]
    ids = ["slot0", "slot1", "slot2"]
    section = pair_reserved(supports, neighbours, ids, dataset="counterfact")
    assert [(r["edit_item_id"], r["neighbour_item_id"]) for r in section["rows"]] == [("a", "x"), ("b", "y")]
    assert section["missing"] == [dict(item_id="slot2", edit_item_id="c", reason="no_compatible_reserved_neighbour")]
    validate_section(section, supports, neighbours, ids, dataset="counterfact")
    for mutate in [lambda s: s["rows"].pop(), lambda s: s["missing"].clear(),
                   lambda s: s["rows"][0].update(neighbour_answer="fabricated"),
                   lambda s: s["rows"][0].update(family_key="relation:P2")]:
        broken = copy.deepcopy(section)
        mutate(broken)
        with pytest.raises(ValueError, match="DEC-061"):
            validate_section(broken, supports, neighbours, ids, dataset="counterfact")


def test_same_subject_and_different_family_cannot_fill_slot():
    own = row("a", subject="Paris")
    for neighbour in [row("b", subject=" PARIS "), row("b", relation="P2"), row("b", relation="")]:
        section = pair_reserved([own], [neighbour], ["slot"], dataset="counterfact")
        assert len(section["missing"]) == 1 and not section["rows"]


def test_zsre_exact_template_requires_single_whole_subject():
    assert near_key(row("Alice", "zsre")) == near_key(row("Bob", "zsre"))
    assert near_key({**row("Al", "zsre"), "prompt": "Where does Alice live?"}) is None
    assert near_key({**row("Al", "zsre"), "prompt": "Al or Al?"}) is None
    assert near_key(row("Alice", "zsre")) != near_key({**row("Bob", "zsre"), "prompt": "Where was Bob born?"})


def test_bounded_neighbour_baseline_equality_ignores_spoofed_flags_and_edit_failure():
    section = {"rows": [dict(item_id="a", status="ok", edit_exact=False, preserved=True,
                              reference=dict(generated="", truncated=False),
                              neighbour_query=dict(generated="changed", truncated=False)),
                        dict(item_id="b", status="ok", edit_exact=False, preserved=False,
                              reference=dict(generated="same", truncated=True),
                              neighbour_query=dict(generated="same", truncated=True))]}
    summary = near_family_summary(section, ["a", "b", "missing"])
    assert summary["preserved"] == 1 and summary["evaluated"] == 2
    assert summary["observed_case_rate"] == .5 and summary["full_inventory_rate"] is None
    assert summary["planned"] == 3 and summary["missing"] == 1
    assert summary["terminated"]["numerator"] == 0
