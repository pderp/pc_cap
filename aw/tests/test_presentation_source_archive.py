"""Approved publication archives work; arbitrary drift remains an error."""

import json

import pytest

from aw import presentation_pc as pc
from aw.reporting_sources import Sources, sha


def test_exact_archive_recorded_instead_of_mislabelled_live_source(tmp_path, monkeypatch):
    stage = tmp_path / "stage"
    stage.mkdir()
    for name in ("sources.json", "reporting-sources.json"):
        (stage / name).write_text("{}")
    live = tmp_path / "aw/scoring.py"
    live.parent.mkdir()
    live.write_text("new import ordering")
    archive = tmp_path / "docs/tasks/round65-source-archive"
    archive.mkdir(parents=True)
    original = archive / "scoring.py"
    original.write_text("original import ordering")
    expected = sha(original)
    (archive / "manifest.json").write_text(json.dumps({"aw/scoring.py": {
        "sha256": expected, "archive": str(original.relative_to(tmp_path))}}))
    monkeypatch.setattr(pc, "ROOT", tmp_path)
    monkeypatch.setattr(pc, "Sources", lambda: Sources(root=tmp_path, stage=stage))
    bindings = {}
    pc.verify_sources({"sources_sha256": {"aw/scoring.py": expected}}, bindings)
    assert bindings[str(original)] == expected
    assert str(live) not in bindings
    with pytest.raises(ValueError, match="presentation source differs"):
        pc.verify_sources({"sources_sha256": {"aw/scoring.py": "0" * 64}}, {})
    original.write_text("tampered archive")
    with pytest.raises(ValueError, match="presentation source differs"):
        pc.verify_sources({"sources_sha256": {"aw/scoring.py": expected}}, {})
