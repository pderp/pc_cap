"""Tail boundaries, missing realizations, and receipt/vector integrity."""

import json

import numpy as np
import pytest

from aw import tail_cells as t


def test_fractional_tail_zero_mass_and_maximum_location():
    d = np.ones((5, 41))
    d[3, 4] = 100
    r = t.statistics(d)
    assert r["es99_positive"] == pytest.approx(101.05 / 2.05)
    assert r["maximum_location"] == dict(
        flat_index=127, window_index=3, target_column=4, target_token_offset=5
    )
    assert r["half_mass_positions"] == 53
    assert r["exceed_1_count"] == 1  # strict threshold; the other 204 are equal to 1
    z = t.statistics(np.zeros((2, 3)))
    assert z["es99_positive"] == 0 and z["half_mass_positions"] is None
    assert z["maximum_ties"] == 6
    with pytest.raises(ValueError, match="finite"):
        t.statistics([[float("nan")]])


def cells():
    return [
        dict(
            condition="reader",
            dataset="zsre",
            realization=r,
            order=o,
            **t.statistics(np.full((2, 3), r + 1.0)),
        )
        for r in range(3)
        for o in range(100, 105)
    ]


def test_spread_uses_cells_and_keeps_partial_realizations_visible():
    rows = cells()
    group = t.summarize(rows)["reader|zsre"]
    assert group["observed_cell_means"]["es99_positive"] == 2
    assert group["full_realization_range"]["es99_positive"] == [1, 3]
    partial = t.summarize(rows[:-1])["reader|zsre"]
    assert partial["realization_means"][2]["cells"] == 4
    assert partial["realization_means"][2]["means"]["es99_positive"] == 3
    assert partial["full_realization_range"]["es99_positive"] is None
    missing = t.summarize(rows[:5])["reader|zsre"]
    assert missing["realization_means"][1]["means"]["maximum"] is None
    with pytest.raises(ValueError, match="duplicate"):
        t.summarize(rows + rows[:1])


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))
    return dict(path=str(path), sha256=t.sha(path))


def receipt_fixture(tmp_path):
    queue, attempt = tmp_path / "queue", tmp_path / "attempt"
    attempt.mkdir()
    source = put(tmp_path / "source.json", {"test": True})
    cell = dict(condition="reader", dataset="zsre", realization=0, order=100)
    coverage = dict(
        complete_windows=2, window_tokens=4, expected_positions=6, windows_int64le_sha256="fixture"
    )
    spec = dict(**coverage, source=source, source_inventory=source)
    recipe = put(
        tmp_path / "recipe.json", dict(cell=cell, full_validation=spec, checkpoints=[1000])
    )
    values = np.zeros((2, 3, 5), np.float64)
    values[1, 2, 0] = 5
    vector_path = attempt / "full-validation-1000.npz"
    np.savez(vector_path, values=values)
    vector = dict(
        path=str(vector_path),
        sha256=t.sha(vector_path),
        fields=t.FIELDS,
        dtype="float64",
        shape=list(values.shape),
        order="window,target_position,field",
    )
    fv = dict(
        status="complete",
        checkpoint=1000,
        manifest_sha256=recipe["sha256"],
        state_sha256="state",
        coverage=coverage,
        scored_positions=6,
        source=source,
        source_inventory=source,
        vectors=vector,
    )
    report = put(attempt / "checkpoint-1000.json", dict(endpoints=dict(full_validation=fv)))
    receipt = dict(
        report=report, checkpoint=1000, manifest_sha256=recipe["sha256"], state_sha256="state"
    )
    receipt["receipt_sha256"] = t.digest(receipt)
    put(attempt / "checkpoint-1000.receipt.json", receipt)
    put(
        attempt / "result.json",
        dict(
            cell=cell,
            status="complete",
            completed_checkpoint=1000,
            manifest_sha256=recipe["sha256"],
            last_receipt_sha256=receipt["receipt_sha256"],
        ),
    )
    finish = dict(status="process_exited", exit_code=0, recipe=recipe, new_attempts=[str(attempt)])
    put(queue / "success-1" / "finish.json", finish)
    put(queue / "failed-1" / "finish.json", dict(status="process_exited", exit_code=1))
    return queue, vector_path, finish


def test_completed_inventory_vector_binding_and_no_unreceipted_fallback(tmp_path):
    queue, vector, finish = receipt_fixture(tmp_path)
    put(queue / "duplicate-1" / "finish.json", finish)
    rows, inventory = t.load_cells(queue, required_positions=6)
    assert len(rows) == 1 and len(inventory["excluded"]) == 1
    assert rows[0]["maximum_location"]["target_token_offset"] == 3
    assert rows[0]["exceed_5"] == 0
    vector.write_bytes(vector.read_bytes() + b"altered")
    with pytest.raises(ValueError, match="identity mismatch"):
        t.load_cells(queue, required_positions=6)
    with pytest.raises(ValueError, match="no finish receipts"):
        t.load_cells(tmp_path / "empty")


def test_receipt_hash_and_coverage_are_required(tmp_path):
    queue, _, finish = receipt_fixture(tmp_path)
    with pytest.raises(ValueError, match="coverage mismatch"):
        t.load_cells(queue, required_positions=245237)
    receipt_path = next((tmp_path / "attempt").glob("*.receipt.json"))
    data = json.loads(receipt_path.read_bytes())
    data["state_sha256"] = "changed"
    put(receipt_path, data)
    with pytest.raises(ValueError, match="receipt mismatch"):
        t.load_cells(queue, required_positions=6)
