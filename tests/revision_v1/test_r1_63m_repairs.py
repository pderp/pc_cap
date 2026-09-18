"""Current installed identities remain strict; no textual patch applied twice."""

import pytest
from scripts import r1_63l_prepare_backend as preparation
from scripts import r1_64g_full_validation_recipes as rebinder


def test_already_installed_backend_is_recognized():
    old, proposed = preparation.proposed()
    assert old == proposed
    assert old.count("full_contract.admit(m, protocol, frozen)") == 1
    rebinder.require_installed()


def test_unknown_backend_drift_is_refused(tmp_path, monkeypatch):
    path = tmp_path / preparation.NAME
    path.parent.mkdir(parents=True)
    path.write_text((preparation.ROOT / preparation.NAME).read_text() + "\n# unreviewed drift\n")
    target = tmp_path / "logs/r1_round31/r1-63l-backend-patch.json"
    target.parent.mkdir(parents=True)
    target.write_text((preparation.ROOT / "logs/r1_round31/r1-63l-backend-patch.json").read_text())
    monkeypatch.setattr(preparation, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="both reviewed identities"):
        preparation.proposed()


def test_reviewed_successor_cadence_helper(monkeypatch):
    from tests.revision_v1.r1_77d_patch_support import install

    assert install(monkeypatch) == "installed"
