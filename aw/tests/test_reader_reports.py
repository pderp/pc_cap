"""Synthetic result trees: partial seeds, identity drift, pairing, and factorial cost."""

from __future__ import annotations

import copy
import json

import pytest

from aw import aw_l_report as upper
from aw import pc_reader_report as pc
from aw import reader_results as rr


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))
    return dict(path=str(path), sha256=rr.sha(path))


def make_training(root, rule="bp", seed=0, read=(1, 2, 3), profile=False, name=None):
    d = root / (name or f"train-{rule}-s{seed}")
    d.mkdir(parents=True, exist_ok=True)
    reader = dump(d / "reader.fixture", {"rule": rule, "seed": seed, "read": read})
    reader["params_sha256"] = f"params-{rule}-{seed}-{read}"
    report = dict(
        status="complete",
        rule=rule,
        seed=seed,
        read_taps=list(read),
        steps=10 if profile else 300,
        profile_only=profile,
        reader=reader,
        parameter_count=10,
        initial_reader_sha256=f"initial-{seed}",
        base_sha256="base",
        recipe={"training": "same"},
        selected_steps=[150, 200, 250, 300],
    )
    dump(d / "report.json", report)
    dump(
        d / "cost.json",
        dict(status="complete", elapsed_process_seconds=10 if rule == "bp" else 1000),
    )
    return d


def make_eval(
    root, tr, dataset="zsre", *, write=(1, 2, 3), score=0.9, name=None, development=False
):
    trd = json.loads((tr / "report.json").read_text())
    rule, seed, read = trd["rule"], trd["seed"], trd["read_taps"]
    d = root / (name or f"eval-{rule}-s{seed}-{dataset}")
    n = 10 if development else 300
    common = root.parent / f"{dataset}-shared-input.json"
    binding = dump(common, {"population": dataset})
    train = dict(path=str(tr / "report.json"), sha256=rr.sha(tr / "report.json"))
    finish = dict(
        status="complete",
        items_completed=n,
        items_planned=n,
        checkpoints_completed=[n],
        elapsed_process_seconds=8,
        state_sha256=f"state-{rule}-{seed}-{write}",
        base_sha256="base",
        reader_sha256=trd["reader"]["params_sha256"],
    )
    config = dict(
        item_ids=list(range(n)),
        endpoints_sha256="endpoints-" + dataset,
        reader_sha256=finish["reader_sha256"],
        acquisition="adjoint",
        interface=dict(read_taps=read, write_sites=list(write)),
    )
    fields = dict(
        positions=4,
        mean_signed=0.1,
        es99_positive=2.0,
        maximum_positive=3.0,
        exceedance={k: dict(count=1, fraction=0.25) for k in ("0.01", "0.1", "1.0")},
    )
    harm = dict(
        selection=dict(positions=4, windows=2, window_tokens=3, windows_sha256="windows"),
        summary={ref: dict(loss=fields, kl=fields) for ref in ("capoff", "original")},
        state_sha256=finish["state_sha256"],
        base_sha256="base",
        treatment=dict(acquisition="adjoint", read_taps=read, write_sites=list(write)),
        vectors=dump(d / "harm/vectors.fixture", [0, 1, 2, 3]),
    )
    metrics = {
        k: dict(planned=n, scored=n, numerator=score * n, value=score, status="complete")
        for k in rr.METRICS
    }
    cp = dict(
        checkpoint=n,
        snapshot={k: finish[k] for k in ("state_sha256", "base_sha256", "reader_sha256")},
        metrics=metrics,
        unseen=dict(
            summary=dict(
                expected_n=3,
                firing_observed_n=3,
                false_fires=1,
                false_fire_rate_full_inventory=1 / 3,
            )
        ),
    )
    doc = dict(
        training=train,
        dataset=dataset,
        rule=rule,
        seed=seed,
        development=development,
        population="fixture",
        payload=binding,
        payload_recipe=binding,
        source_recipe=binding,
        status="complete",
        read_taps=read,
        write_sites=list(write),
        stream=finish,
        harm=harm,
        gate_telemetry=dict(logical_positions=4, selected=1, hard_null=3),
        interface_accounting=dict(
            parameters=10,
            delta_allocated_bytes=100,
            delta_active_coordinate_bytes=40 if write == (3,) else 100,
            total_allocated_bytes=200,
        ),
    )
    for path, value in [
        ("report.json", doc),
        ("stream/finish.json", finish),
        ("stream/config.json", config),
        (f"stream/checkpoint-{n}.json", cp),
        ("harm/summary.json", harm),
        ("harm/cost.json", dict(status="complete", elapsed_process_seconds=12)),
        ("cost.json", dict(status="complete", elapsed_process_seconds=25)),
    ]:
        dump(d / path, value)
    return d


def test_partial_seed_grid_intersects_seeds_not_unequal_means(tmp_path):
    root = tmp_path / "PC-reader"
    for rule, seed, value in [("bp", 0, 0.9), ("bp", 1, 0.99), ("epc", 0, 0.5)]:
        tr = make_training(root, rule, seed)
        make_eval(root, tr, score=value)
    r = pc.build(root, positions=4)
    assert r["completed_evaluations"] == 3 and len(r["cells"]) == 12
    pairs = [p for p in r["paired_differences"] if p["status"] == "paired"]
    assert len(pairs) == 1 and pairs[0]["difference_bp_minus_epc"]["RET-GS"] == pytest.approx(0.4)
    epc = next(s for s in r["seed_spreads"] if s["dataset"] == "zsre" and s["rule"] == "epc")
    assert epc["metrics"]["RET-GS"]["sample_sd"] is None
    assert r["training_cost_ratios"][0]["epc_over_bp"] == 100
    # Parent process receipts only; stream=8 and harm=12 must not be added again.
    assert r["known_process_seconds"] == 1020 + 3 * 25


def test_invalid_binding_and_failed_process_remain_visible(tmp_path):
    tr = make_training(tmp_path)
    ev = make_eval(tmp_path, tr)
    (tr / "report.json").write_text((tr / "report.json").read_text() + " ")
    row = rr.admitted(ev, {}, positions=4)
    assert row["status"] == "invalid" and "hash mismatch" in row["reason"]
    dump(ev / "cost.json", dict(status="failed", elapsed_process_seconds=7))
    row = rr.admitted(ev, {}, positions=4)
    assert row["status"] == "failed" and row["cost"]["seconds"] == 7
    assert rr.values(row) == {}


def test_profile_cannot_enter_production(tmp_path):
    tr = make_training(tmp_path, profile=True)
    ev = make_eval(tmp_path, tr, development=True)
    assert rr.admitted(ev, {}, positions=4)["status"] == "invalid"
    assert rr.admitted(ev, {}, positions=4, checkpoint=10, development=True)["status"] == "complete"


def test_changed_endpoint_population_refuses_paired_inference(tmp_path):
    tr = make_training(tmp_path)
    a = rr.admitted(make_eval(tmp_path, tr), {}, positions=4)
    b = copy.deepcopy(a)
    b["pairing"]["endpoints"] = "different"
    with pytest.raises(ValueError, match="populations differ"):
        rr.paired(a, b)


def factorial_tree(tmp_path):
    shared, root = tmp_path / "PC-reader", tmp_path / "AW-L"
    tr_all = make_training(shared)
    make_eval(shared, tr_all, score=0.4)
    make_eval(root, tr_all, name="eval-all-last-s0-zsre", write=(3,), score=0.5)
    tr_upper = make_training(root, read=(2, 3), name="train-upper-s0")
    make_eval(root, tr_upper, name="eval-upper-all-s0-zsre", score=0.7)
    make_eval(root, tr_upper, name="eval-upper-last-s0-zsre", write=(3,), score=0.9)
    profile = make_training(root, read=(2, 3), name="profile-upper-s0", profile=True)
    make_eval(
        root, profile, name="eval-profile-upper-last-zsre", write=(3,), score=0.99, development=True
    )
    return root, shared


def test_factorial_signs_reuse_and_dense_zero_accounting(tmp_path):
    root, shared = factorial_tree(tmp_path)
    r = upper.build(root, shared, positions=4)
    e = next(x for x in r["effects"] if x["dataset"] == "zsre" and x["seed"] == 0)["effects"][
        "RET-GS"
    ]
    assert e == pytest.approx(dict(read=0.35, write=0.15, interaction=0.1))
    assert r["completed_evaluations"] == 4 and r["reused_evaluations"] == 1
    assert len(r["development_profiles"]) == 1 and len(r["cells"]) == 24
    assert r["attributed_process_seconds"] == 3 * 10 + 5 * 25
    assert r["incremental_aw_l_process_seconds"] == 2 * 10 + 4 * 25
    last = next(c for c in r["cells"] if c["status"] == "complete" and c["planned_write"] == "last")
    assert last["interface"]["delta_allocated_bytes"] == 100
    assert last["interface"]["delta_active_coordinate_bytes"] == 40


def test_no_complete_factorial_no_effect_and_write_reader_mismatch(tmp_path):
    root, shared = factorial_tree(tmp_path)
    r = upper.build(root, shared, positions=4)
    block = {
        (c["planned_read"], c["planned_write"]): c
        for c in r["cells"]
        if c["planned_seed"] == 0 and c["planned_dataset"] == "zsre"
    }
    block["upper", "last"]["training"]["reader_sha256"] = "different"
    with pytest.raises(ValueError, match="share the same trained reader"):
        upper.factorial(block)
    block["upper", "last"]["status"] = "missing"
    assert upper.factorial(block) is None


def test_denominator_and_gate_coverage_mismatch_not_admitted(tmp_path):
    tr = make_training(tmp_path)
    ev = make_eval(tmp_path, tr)
    path = ev / "stream/checkpoint-300.json"
    cp = json.loads(path.read_text())
    cp["metrics"]["RET-GS"]["planned"] = 301
    dump(path, cp)
    row = rr.admitted(ev, {}, positions=4)
    assert row["status"] == "invalid" and "denominator" in row["reason"]
    cp["metrics"]["RET-GS"]["planned"] = 300
    dump(path, cp)
    path = ev / "report.json"
    doc = json.loads(path.read_text())
    doc["gate_telemetry"]["hard_null"] = 4
    dump(path, doc)
    assert "denominator" in rr.admitted(ev, {}, positions=4)["reason"]
