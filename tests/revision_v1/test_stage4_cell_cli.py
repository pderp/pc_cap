"""CLI inspection must not open a payload or construct a model."""

import json

import pytest
import scripts.r1_61_cell_driver as cli

from pccap.revision_v1.stage4_cell import code_identity, sha, write_json


def test_metadata_inspection_does_not_open_missing_payload(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "code_identity", lambda: "a" * 64)
    p = tmp_path / "recipe.json"
    write_json(
        p,
        {
            "cell": {"condition": "R1_learned_ff"},
            "mode": "stage4_sealed_cell",
            "code_sha256": "a" * 64,
            "payload": {"path": str(tmp_path / "not-present"), "sha256": "0" * 64},
        },
    )
    assert cli.main(["--manifest", str(p), "--manifest-sha256", sha(p)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert not out["payload_opened"] and not out["model_constructed"]
    assert out["code_identity_matches"]


def test_base_children_checked_before_model_construction(tmp_path):
    a, b = tmp_path / "config.json", tmp_path / "model.safetensors"
    a.write_text("{}")
    b.write_bytes(b"fixture")
    good = {"path": str(tmp_path), "files": {"config.json": sha(a), "model.safetensors": sha(b)}}
    assert cli._snapshot(good) == tmp_path
    bad = {**good, "files": {**good["files"], "model.safetensors": "0" * 64}}
    with pytest.raises(ValueError, match="child"):
        cli._snapshot(bad)


def test_code_inventory_tracks_new_and_changed_python(tmp_path):
    root = tmp_path / "repo"
    (root / "src/pccap").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "scripts/r1_61_cell_driver.py").write_text("pass\n")
    (root / "src/pccap/a.py").write_text("a=1\n")
    before = code_identity(root)
    (root / "src/pccap/b.py").write_text("b=2\n")
    assert before != code_identity(root)
    assert len(code_identity(root)) == 64
