"""Cost replacement boundary cases and historical sampled-evidence failures."""

import json
from uuid import uuid4

import pytest
from scripts import r1_58l_transfer_basis as basis


@pytest.mark.parametrize("cadence", [2, 3])
def test_old_single_sample_replaced_and_full_only_added_once(cadence):
    value = basis.replacement(1000, 100, 80, cadence, 1300)
    assert value["inherited_nonvalidation_seconds"] == 900
    assert value["sampled_all_checkpoints_seconds"] == 80 * cadence
    assert value["solo_seconds"] == 900 + 80 * cadence + 1300
    assert value["two_worker_ceiling_seconds"] == pytest.approx(value["solo_seconds"] * 1.725)


@pytest.mark.parametrize("bad", [True, None, -1, 0, float("nan"), float("inf")])
def test_invalid_times_are_not_zero_or_valid_cost(bad):
    with pytest.raises(ValueError, match="finite positive"):
        basis.replacement(1000, 100, 80, 3, bad)


def test_wrong_cadence_or_negative_remainder_is_not_clamped():
    with pytest.raises(ValueError, match="replacement/cadence"):
        basis.replacement(50, 100, 80, 3, 1300)
    with pytest.raises(ValueError, match="replacement/cadence"):
        basis.replacement(1000, 100, 80, 1, 1300)


def test_gnu_clock_formats():
    assert basis.elapsed("42:09.40") == pytest.approx(2529.4)
    assert basis.elapsed("1:02:03.5") == pytest.approx(3723.5)
    with pytest.raises(ValueError):
        basis.elapsed("nan:00")


@pytest.fixture
def sample(monkeypatch):
    root = basis.ROOT.parent / "assets/runs/pc_cap/R1/rehearsal_fixtures/round35" / uuid4().hex
    root.mkdir(parents=True)
    monkeypatch.setattr(basis, "ROOT", root)

    def put(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
        return path

    rp = put(root / "recipe.json", {})
    cp = put(
        root / "results/attempt-0000/checkpoint-300.json",
        dict(
            endpoints=dict(
                drift=dict(scored_positions=10, expected_positions=10, status="complete")
            )
        ),
    )
    receipt = dict(report=basis.d9.ref(cp))
    receipt_path = put(cp.with_name("checkpoint-300.receipt.json"), receipt)
    result = dict(
        completed_checkpoint=300,
        phase_timer_summary=dict(drift=dict(count=1, errors=0, wall_seconds=5)),
    )
    result_path = put(cp.with_name("result.json"), result)
    phase = put(
        cp.parent / "phases/000001.json", dict(phase="drift:300", status="ok", wall_seconds=5)
    )
    row = (None, rp, {}, result_path, result, receipt_path, receipt)
    return row, phase, put


def test_sample_rate_uses_scored_positions_and_binds_phase(sample):
    row, phase, _ = sample
    value = basis.sample_basis(row)
    assert value["seconds_per_position"] == 0.5
    assert basis.d9.ref(phase) in value["source_bindings"]


def test_changed_report_and_mismatched_phase_timer_refuse(sample):
    row, phase, put = sample
    put(phase, dict(phase="drift:300", status="ok", wall_seconds=6))
    with pytest.raises(ValueError, match="timer disagree"):
        basis.sample_basis(row)
    put(phase, dict(phase="drift:300", status="ok", wall_seconds=5))
    row[-1]["report"]["sha256"] = "wrong"
    with pytest.raises(ValueError, match="binding changed"):
        basis.sample_basis(row)


def test_extra_sample_phase_requires_new_replacement_model(sample):
    row, phase, put = sample
    put(phase.with_name("000002.json"), dict(phase="drift:100", status="ok", wall_seconds=5))
    with pytest.raises(ValueError, match="exactly one phase"):
        basis.sample_basis(row)
