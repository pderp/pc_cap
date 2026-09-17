"""Dry freeze inventories cannot silently promote evidence or authorize acts."""

import copy

import pytest
from scripts import r1_63f_freeze_candidate as module
from scripts.r1_d10d_options import layouts


@pytest.fixture
def candidate(monkeypatch):
    monkeypatch.setattr(module.driver, "code_identity", lambda: "driver")
    monkeypatch.setattr(module, "sha", lambda p: module.backend.DONOR_SHA256)
    v4 = {"path": "v4", "sha256": "old"}
    return dict(
        option="D",
        dataset_layouts=layouts("D"),
        bindings_sha256={},
        installed_driver_code_sha256="driver",
        confirmation_protocol_frozen=False,
        draw_authorized=False,
        launch_authorized=False,
        context_adjudication_admitted=False,
        operative_clearance_evidence=v4,
        context_review={"v4": v4},
        gate_inventory=[dict(gate=f"U{i:02}") for i in range(1, 19)],
        remaining_gates=[],
    )


@pytest.mark.parametrize(
    "key",
    [
        "confirmation_protocol_frozen",
        "draw_authorized",
        "launch_authorized",
        "context_adjudication_admitted",
    ],
)
def test_refuses_implicit_authority(candidate, key):
    candidate[key] = True
    with pytest.raises(ValueError, match="grants no admission"):
        module.verify(candidate)


def test_refuses_unreviewed_v5_promotion(candidate):
    candidate["operative_clearance_evidence"] = {"path": "v5", "sha256": "new"}
    with pytest.raises(ValueError, match="unreviewed v5"):
        module.verify(candidate)


def test_refuses_binding_tamper_and_wrong_cadence(candidate):
    changed = copy.deepcopy(candidate)
    changed["bindings_sha256"] = {"some-source": "changed"}
    with pytest.raises(ValueError, match="binding changed"):
        module.verify(changed)
    candidate["dataset_layouts"]["mquake"]["checkpoints"].append(1000)
    with pytest.raises(ValueError, match="option D layout"):
        module.verify(candidate)
