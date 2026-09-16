"""The report watcher only reacts to the bound owner cell or charged failures."""

import json

import pytest
from scripts import ht3d_after_chain as w


def test_pending_completion_failure_and_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(w, "ROOT", tmp_path)
    spec = {
        "failure_receipts": ["pilot/failure_receipt.json"],
        "full_profile_directory": "profile",
        "full_recipe": {"sha256": "a" * 64},
        "cell": {"condition": "primary"},
    }
    assert w.observe(spec) is None
    attempt = tmp_path / "profile/attempt-0000"
    attempt.mkdir(parents=True)
    (attempt / "result.json").write_text(
        json.dumps({"manifest_sha256": "a" * 64, "cell": spec["cell"], "status": "complete"})
    )
    assert w.observe(spec)["trigger"] == "owner_chain_terminal_profile_complete"
    bad = {**spec, "full_recipe": {"sha256": "b" * 64}}
    with pytest.raises(ValueError, match="identity mismatch"):
        w.observe(bad)
    failure = tmp_path / "pilot/failure_receipt.json"
    failure.parent.mkdir()
    failure.write_text('{"charged_wall_s":123}')
    assert w.observe(spec)["trigger"] == "owner_charged_failure"
