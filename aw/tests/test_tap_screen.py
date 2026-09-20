"""Small probe checks independent of large caches or base-model execution."""

import numpy as np
import pytest

from aw.tap_screen import fit_probe, group_split, normalized, probe_scores, summarize_predictions


def test_split_unions_subjects_and_families_transitively():
    rows = [
        dict(item_id="a", dataset="counterfact", subject="Alice", relation_id="P1"),
        dict(item_id="b", dataset="counterfact", subject="Bob", relation_id="P1"),
        dict(item_id="c", dataset="counterfact", subject="Bob", relation_id="P2"),
        dict(item_id="d", dataset="counterfact", subject="David", relation_id="P3"),
    ]
    labels, report = group_split(rows)
    assert labels[0] == labels[1] == labels[2]
    assert report["components"] == 2
    assert report["subject_overlap"] == report["family_overlap"] == 0
    reverse, _ = group_split(list(reversed(rows)))
    assert all(labels[i] == reverse[len(rows) - i - 1] for i in labels)


def test_unknown_family_refused():
    with pytest.raises(ValueError):
        group_split([dict(item_id="a", dataset="counterfact", subject="Alice")])


def test_probe_learns_separable_fixture_and_no_prediction_refit():
    x = np.array([[-2], [-1], [1], [2]], float)
    y = np.array([0, 0, 1, 1])
    model = fit_probe(x, y)
    before = {k: v.copy() for k, v in model.items()}
    assert np.array_equal(probe_scores(model, x) >= 0, y > 0)
    probe_scores(model, np.array([[1e9]]))
    assert all(np.array_equal(v, before[k]) for k, v in model.items())


def test_normalization_is_per_component_and_zero_safe():
    a = np.arange(12).reshape(3, 4).astype(float)
    b = a[::-1].copy()
    x = normalized(a, b)
    assert np.isfinite(normalized(a * 0, b * 0)).all()
    assert np.allclose(x, normalized(a + 100, b - 200))
    assert np.allclose(np.linalg.norm(x, axis=-1), 1.0)


def test_retrieval_requires_correct_firing_and_null_denominators_separate():
    q = [
        dict(id="positive", kind="paraphrase", target=0),
        dict(id="wrong", kind="paraphrase", target=1),
        dict(id="null", kind="outside", target=-1),
    ]
    summary, rows = summarize_predictions(q, np.array([[2, 1], [2, 1], [1, -1]]))
    assert summary["gated_retrieval"] == 0.5
    assert summary["false_fire"] == 1
    assert rows[1]["fires"] and not rows[1]["retrieved"]
