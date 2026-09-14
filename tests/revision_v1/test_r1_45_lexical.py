"""Exact lexical-span and tie-aware ROC arithmetic for R1-45."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

import pytest
from scripts.r1_45_lexical_separability import (
    common_span,
    recall,
    roc,
    sequence_index,
    symmetric_overlap,
)


@pytest.mark.parametrize(
    "a,b",
    [
        ([], []),
        ([1, 2], [3, 4]),
        ([1, 2, 3], [8, 1, 2, 3, 9]),
        ([1, 2, 1, 2], [2, 1, 2, 1]),
        ([1, 1, 1], [1, 1]),
        ([4], [4]),
    ],
)
def test_contiguous_span_against_brute_force(a, b):
    expected = max(
        [0]
        + [
            n
            for i in range(len(a))
            for j in range(len(b))
            for n in range(1, min(len(a) - i, len(b) - j) + 1)
            if a[i : i + n] == b[j : j + n]
        ]
    )
    assert common_span(sequence_index(a), b) == expected


@pytest.mark.parametrize(
    "positive,negative",
    [
        ([1, 1], [0, 0]),
        ([1, 1], [1, 1]),
        ([0, 0], [1, 1]),
        ([0, 1, 1], [0, 0.5, 1]),
        ([0.1, 0.1, 0.9], [0.1, 0.3, 0.9, 0.9]),
    ],
)
def test_auc_exact_ties_against_pair_count(positive, negative):
    r = roc(Counter(positive), Counter(negative))
    expected = sum(
        float(a > b) + 0.5 * float(a == b) for a, b in itertools.product(positive, negative)
    ) / (len(positive) * len(negative))
    assert r["auc"] == pytest.approx(expected, abs=1e-12)
    assert r["points"][0]["tpr"] == r["points"][0]["fpr"] == 0
    assert r["points"][-1]["tpr"] == pytest.approx(1)
    assert r["points"][-1]["fpr"] == pytest.approx(1)
    for a, b in zip(r["points"], r["points"][1:]):
        assert a["tpr"] <= b["tpr"] and a["fpr"] <= b["fpr"]


def test_weighted_auc_and_missing_class():
    assert roc({1: 0.5, 0: 0.5}, {0: 1})["auc"] == 0.75
    assert roc({}, {0: 1})["auc"] is None


def test_empty_stopped_tokens_are_visible_zero_scores():
    assert recall(set(), {1}) == 0 and symmetric_overlap(set(), {1}) == 0
    assert symmetric_overlap({1, 2}, {2, 3, 4}) == pytest.approx(0.5 * (0.5 + 1 / 3))


def test_full_pool_inventory_and_all_ordered_other_pairs():
    root = Path(__file__).resolve().parents[2]
    doc = json.loads((root / "logs/r1_round6/near_neighbour_separability.json").read_text())
    for name, n in (("counterfact_dev", 300), ("zsre_dev", 300), ("counterfact_train", 3000)):
        r = doc["pools"][name]
        assert r["n_items"] == len(r["records"]) == n
        assert r["query_counts"]["other_prompt"] == n * (n - 1)
        assert all(row["other_prompt_count"] == n - 1 for row in r["records"])
        for comparison in r["comparisons"].values():
            for feature in comparison.values():
                assert 0 <= feature["item_balanced"]["auc"] <= 1 + 1e-12
                assert 0 <= feature["query_weighted"]["auc"] <= 1 + 1e-12
    assert len(doc["stoplist"]["tokens"]) == len(set(doc["stoplist"]["tokens"])) == 200
    assert not doc["model_loaded"] and doc["gpu_seconds"] == 0
