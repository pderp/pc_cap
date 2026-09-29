import json

import pytest

from aw.pc_historical import Sources, sha


def test_only_declared_exact_archive_may_resolve(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "old").mkdir()
    (tmp_path / "aw").mkdir()
    current = tmp_path / "aw/declared.py"
    current.write_text("new version")
    old = stage / "old/declared.py"
    old.write_text("old version")
    (stage / "sources.json").write_text(json.dumps({"aw/declared.py": {"before_sha256": sha(old)}}))
    (stage / "reporting-sources.json").write_text("{}")
    resolver = Sources(tmp_path, stage)
    assert resolver.resolve(current, sha(old)) == old
    resolver.verify_unchanged()
    arbitrary = tmp_path / "aw/arbitrary.py"
    arbitrary.write_text("changed")
    with pytest.raises(ValueError, match="unapproved"):
        resolver.resolve(arbitrary, sha(old))
    old.write_text("tampered")
    with pytest.raises(ValueError, match="missing or changed"):
        resolver.resolve(current, resolver.allowed["aw/declared.py"])
    with pytest.raises(ValueError, match="changed during read"):
        resolver.verify_unchanged()
