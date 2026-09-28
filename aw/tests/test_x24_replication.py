"""Audit projections never deserialize efficacy, and reject identity/cost drift."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import json

import pytest

from aw import x24_replication as x


def test_projection_skips_nested_scores_and_strings_without_decoding(monkeypatch):
    source = r'{"item_id":"same", "es":{"SECRET_METRIC":[1.234, {"text":"quote\" }, ["}]}, "index":0, "bounded_es":987.654, "cost":{"reverses":9}}'
    actual = json.loads

    def guarded(text, *a, **kw):
        assert "SECRET_METRIC" not in text and "987.654" not in text
        return actual(text, *a, **kw)

    monkeypatch.setattr(x.json, "loads", guarded)
    result = x.project(source, {"item_id", "index", "cost"})
    assert result == dict(item_id="same", index=0, cost=dict(reverses=9))
    assert set(k for k, _ in x.fields(source)) == {"item_id", "es", "index", "bounded_es", "cost"}


def test_checkpoint_array_projection_keeps_only_identifiers():
    text = '[{"tag":"end", "items":2, "ret_es":0.125, "rows":[{"ret_gs":0.75}]}, {"tag":"c1", "items":1, "drift":{"mean":0.33}}]'
    assert [x.project(row, {"tag", "items"}) for row in x.objects(text)] == [
        dict(tag="end", items=2),
        dict(tag="c1", items=1),
    ]
    with pytest.raises(ValueError, match="duplicate"):
        x.project('{"item_id":"one","item_id":"two"}', {"item_id"})


def cost():
    value = {k: 0 for k in x.COUNTS}
    value.update(full_forwards=31, reverses=27, settle_iters=24)
    return value


def test_credit_accounting_rejects_wrong_horizon_missing_forward_and_adjoint_settling():
    x.operation_check(cost(), "SE-E")
    bad = cost()
    bad["reverses"] = 24
    with pytest.raises(ValueError, match="nine-reverse"):
        x.operation_check(bad, "SE-E")
    bad = cost()
    bad["full_forwards"] = 26
    with pytest.raises(ValueError, match="missing full"):
        x.operation_check(bad, "SE-E")
    with pytest.raises(ValueError, match="SE-A unexpectedly"):
        x.operation_check(cost(), "SE-A")
    bad = cost()
    bad["settle_iters"] = 23
    with pytest.raises(ValueError, match="eight-step"):
        x.operation_check(bad, "SE-E")


def test_tampered_fresh_state_rejected_before_opening_any_result_scores(monkeypatch):
    from pathlib import Path

    from aw.pc_v0 import archive, design

    c = design(5)[0]
    group = x.OUTPUT / "replication-60-20260927"
    folder = group / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
    if not (folder / "finish.json").exists():
        pytest.skip("completed replication metadata absent")
    original = Path.read_text

    def altered(path, *args, **kwargs):
        if path == folder / "config.json":
            cfg = json.loads(original(path, *args, **kwargs))
            cfg["initial_state"] = "tampered"
            return json.dumps(cfg)
        assert path.name not in (
            "metrics.json",
            "secondary-summary.json",
            "items.jsonl",
            "decisions.jsonl",
        )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", altered)
    plan = json.loads(original(group / "plan.json"))
    with pytest.raises(ValueError, match="initial memory"):
        x.cell(folder, c, plan, archive(), 768, {}, {})
