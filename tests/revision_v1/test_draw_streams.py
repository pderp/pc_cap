"""R1-58 synthetic reservation and admission tests; no real candidate draws."""

import json

import pytest
from scripts.r1_58_draw_streams import (
    ROLES,
    allocate_records,
    allowed,
    capacity,
    main,
    quotas,
    require_lead,
    write_lead_draw,
)


def rows(n=30):
    return {
        ds: [
            {
                "item_id": f"{ds}-item-{i}",
                "_canonical_subject": f"{ds}-subject-{i}",
                "_stratum": "1-2" if i % 2 else "3-4",
            }
            for i in range(n)
        ]
        for ds in ("zsre", "counterfact")
    }


def counts():
    return dict(zip(ROLES, (3, 1, 1, 1, 1), strict=True))


def test_deterministic_disjoint_synthetic_roles():
    first = allocate_records(rows(), seed=158, counts=counts())
    assert first == allocate_records(rows(), seed=158, counts=counts())
    selected = [r["_canonical_subject"] for g in first["allocations"] for r in g["records"]]
    assert len(selected) == len(set(selected)) == 42
    assert all(len(g["records"]) == g["requested"] for g in first["allocations"])
    assert first != allocate_records(rows(), seed=159, counts=counts())


def test_dry_capacity_uses_no_rng(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("dry capacity must not invoke RNG")

    monkeypatch.setattr("numpy.random.Generator", forbidden)
    plan = capacity(rows(), counts())
    assert plan["complete_capacity"]
    assert len(plan["roles"]) == 30
    assert "subject-" not in json.dumps(plan)
    assert "item-" not in json.dumps(plan)


def test_shortfall_is_atomic_before_rng(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("shortfall must precede RNG")

    monkeypatch.setattr("numpy.random.Generator", forbidden)
    plan = capacity(rows(2), counts())
    assert not plan["complete_capacity"]
    assert all(x["shortfall"] == 19 for x in plan["datasets"])
    with pytest.raises(ValueError, match="no partial draw"):
        allocate_records(rows(2), seed=158, counts=counts())


def test_register_exception_is_reason_specific():
    record = {"dataset": "counterfact", "subject": "Alias Name"}
    aliases = {"alias name": "canonical name"}
    reasons = {"canonical name": {"old_eligible:counterfact"}}
    assert not allowed(record, reasons, aliases, "strict")
    assert allowed(record, reasons, aliases, "exception")
    reasons["canonical name"].add("training_exposure")
    assert not allowed(record, reasons, aliases, "exception")
    record["dataset"] = "zsre"
    assert not allowed(record, reasons, aliases, "exception")


def test_strict_capacity_keeps_zero_counterfact():
    pool = rows()
    pool["counterfact"] = []
    plan = capacity(pool, counts())
    cf = next(d for d in plan["datasets"] if d["dataset"] == "counterfact")
    assert cf["available_candidates"] == 0 and cf["shortfall"] == 21
    assert all(r["capacity"] == 0 for r in plan["roles"] if r["dataset"] == "counterfact")


def test_largest_remainder_exact_and_bounded():
    assert quotas({"a": 1, "b": 1, "c": 1}, 2) == {"a": 1, "b": 1, "c": 0}
    for n in range(12):
        q = quotas({"a": 1, "b": 3, "c": 5}, n)
        assert sum(q.values()) == min(n, 9)
        assert q["a"] <= 1 and q["b"] <= 3 and q["c"] <= 5


def test_duplicate_subjects_refused():
    pool = rows()
    pool["counterfact"][0]["_canonical_subject"] = pool["zsre"][0]["_canonical_subject"]
    with pytest.raises(ValueError, match="unique"):
        allocate_records(pool, seed=1, counts=counts())


@pytest.mark.parametrize(
    "kwargs",
    [{"realizations": 0}, {"realizations": True}, {"counts": {**counts(), "revision": -1}}],
)
def test_invalid_recipe_refused(kwargs):
    with pytest.raises(ValueError):
        capacity(rows(), **kwargs)


def test_lead_guard_without_flag():
    with pytest.raises(PermissionError, match="i-am-the-lead"):
        require_lead(False, {}, {}, "exception")


def test_payload_writer_guard_precedes_mutation(tmp_path):
    target = tmp_path / "manifest.json"
    with pytest.raises(PermissionError):
        write_lead_draw(
            {},
            {"source_reading": "exception"},
            {},
            manifest_path=target,
            payload_dir=tmp_path / "payload",
            seal=True,
        )
    assert not target.exists() and not (tmp_path / "payload").exists()


@pytest.mark.parametrize(
    "extra",
    [
        ["--seal"],
        ["--payload-dir", "/tmp/unused-r1-payload"],
        ["--output-manifest", "/tmp/unused-r1-manifest"],
    ],
)
def test_dry_run_cannot_emit_payload_or_seal(monkeypatch, extra):
    monkeypatch.setattr(
        "sys.argv",
        [
            "r1_58",
            "--dry-run",
            "--counterfact-source",
            "exception",
            "--report",
            "logs/unused-r1-report.json",
            *extra,
        ],
    )
    with pytest.raises(SystemExit) as caught:
        main()
    assert caught.value.code == 2


def test_actual_draw_without_lead_refused(monkeypatch):
    monkeypatch.setattr("sys.argv", ["r1_58", "--counterfact-source", "exception"])
    with pytest.raises(SystemExit) as caught:
        main()
    assert caught.value.code == 2
