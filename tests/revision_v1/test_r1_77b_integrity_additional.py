"""Sealed execution parity and refusal across parameter/configuration identities."""

import json
from pathlib import Path

import pytest

from tests.revision_v1 import test_r1_77b_sealed_backend as cases
from tests.revision_v1.test_r1_68b_incremental_cell import scientific


def reports(result):
    directory = Path(result["run_dir"])
    return [
        scientific(json.loads(p.read_text()))
        for p in sorted(directory.glob("attempt-*/checkpoint-*.json"))
        if not p.name.endswith(".receipt.json")
    ]


@pytest.mark.parametrize("profile", ["full", "incremental"])
def test_uninterrupted_equals_checkpoint_resume(monkeypatch, profile):
    f = cases.make.__wrapped__(monkeypatch)(profile=profile)
    f["execute"](stop_after_checkpoint=1)
    resumed = reports(f["execute"](resume=True))
    g = cases.make.__wrapped__(monkeypatch)(profile=profile)
    uninterrupted = reports(g["execute"]())
    assert resumed == uninterrupted


@pytest.mark.parametrize("field", ["theta_sha256", "config", "budget"])
def test_parameter_configuration_identity_cannot_change(monkeypatch, field):
    def change(m, f, p):
        m["adapter_identity"][field] = {"deliberately_wrong": True}

    f = cases.make.__wrapped__(monkeypatch)(change=change)
    with pytest.raises(ValueError, match="adapter/base/config/parameter"):
        f["execute"]()
