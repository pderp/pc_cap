import json

import pytest

from aw import pc_reader_train as train
from aw import reader_portfolio_cost as cost


def test_projection_scales_stream_retention_fixed_assays_and_harm_separately(tmp_path, monkeypatch):
    monkeypatch.setattr(cost, "sources", lambda: {"fixture": "bound"})
    (tmp_path / "stream").mkdir()
    (tmp_path / "harm").mkdir()
    report = dict(
        status="complete",
        development=True,
        sources_sha256={"fixture": "bound"},
        stream=dict(items_planned=10),
    )
    (tmp_path / "report.json").write_text(json.dumps(report))
    (tmp_path / "cost.json").write_text(
        json.dumps(dict(status="complete", elapsed_process_seconds=100))
    )
    rows = [
        dict(phase=name + ":10", status="complete", elapsed_process_seconds=seconds)
        for name, seconds in (
            ("edit", 10),
            ("immediate", 5),
            ("retention", 2),
            ("near_miss", 20),
            ("revision", 20),
        )
    ]
    (tmp_path / "stream/phases.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    (tmp_path / "harm/cost.json").write_text(
        json.dumps(dict(positions_completed=1016, elapsed_process_seconds=8))
    )
    _, result = cost.evaluation_components(tmp_path)
    parts = result["components"]
    assert parts["acquisition_and_immediate_300"] == 450
    assert parts["retention_at_100_and_300"] == 80
    assert parts["fixed_endpoints_twice"] == 80
    assert parts["full_harm"] == pytest.approx(1931)
    assert parts["construction_and_other"] == 35


def test_upper_ceiling_counts_failed_parent_once_not_again_for_children(tmp_path, monkeypatch):
    monkeypatch.setattr(train, "ROOT", tmp_path)
    root = tmp_path / "results/additional_work/AW-L"
    child = root / "attempt/harm"
    child.mkdir(parents=True)
    (child / "cost.json").write_text(
        json.dumps(dict(status="complete", elapsed_process_seconds=500))
    )
    (child.parent / "cost.json").write_text(
        json.dumps(dict(status="failed", elapsed_process_seconds=1000))
    )
    assert train.remaining_allowance(root, 48 * 3600) == 48 * 3600 - 1000


def test_profile_only_artifact_cannot_enter_exposed_evaluation(tmp_path):
    from types import SimpleNamespace

    from aw.trained_reader_eval import execute_evaluation

    (tmp_path / "report.json").write_text(
        json.dumps(dict(status="complete", recipe=train.recipe(), profile_only=True))
    )
    (tmp_path / "cost.json").write_text(json.dumps(dict(status="complete")))
    with pytest.raises(ValueError, match="profile reader"):
        execute_evaluation(
            SimpleNamespace(
                execute=True, training=str(tmp_path), output="unused", development=False
            )
        )
