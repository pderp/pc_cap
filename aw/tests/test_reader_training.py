import pccap  # noqa: F401 # isort: skip

# isort: split

import dataclasses
import json
from types import SimpleNamespace

import jax
import numpy as np
import pytest
from tests.revision_v1.test_epc_surrogate import CC, RC

from aw import aw_l_train as upper
from aw import pc_reader_train as r
from aw.tests.test_pc_v0 import TinyEPC
from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.observations import ObservationEncoder
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.train import featurize


def test_declared_design_recipe_and_execution_gate():
    p, u = r.plan(), upper.plan()
    assert len(p["trainings"]) == 6 and len(p["evaluations"]) == 12
    assert len(u["trainings"]) == 6 and len(u["evaluations"]) == 24
    assert p["recipe"] == u["recipe"]
    assert p["recipe"]["checkpoint_steps"] == [150, 200, 250, 300]
    assert not p["model_execution"] and not u["model_execution"]
    with pytest.raises(ValueError, match="execute"):
        r.execute_training(SimpleNamespace(execute=False))
    with pytest.raises(ValueError, match="profile"):
        r.validate_profile(None, "epc", r.ALL, p["recipe"])


def test_tap_projection_preserves_shared_seed_tensors_and_all_prefix_targets():
    full = r.initial_theta(2, RC, CC)
    rc = dataclasses.replace(RC, taps=(2, 3))
    reduced = r.initial_theta(2, rc, CC)
    assert set(reduced["reader"]["tap"]) == {"2", "3"}
    for a, b in zip(
        jax.tree_util.tree_leaves(r.prune_reader(full, (2, 3))), jax.tree_util.tree_leaves(reduced)
    ):
        np.testing.assert_array_equal(a, b)
    base = TinyEPC()
    feats = featurize(base, ObservationEncoder(base), synthetic_episode(4), RC)
    projected = r.project_episode(feats, (2, 3))
    assert r.episode_identity([projected]) == r.episode_identity([feats])
    for a, b in zip(feats.queries, projected.queries):
        np.testing.assert_array_equal(a.last[1:], b.last)
        for ap, bp in zip(a.prefixes, b.prefixes):
            np.testing.assert_array_equal(ap.span[1:], bp.span)
            np.testing.assert_array_equal(ap.ids, bp.ids)
    assert feats.supports[0].last.shape[0] == 3


def test_actual_bp_and_epc_training_share_initialization_episodes_and_freeze_base(tmp_path):
    reports = []
    for rule in ("bp", "epc"):
        base = TinyEPC()
        feats = featurize(base, ObservationEncoder(base), synthetic_episode(4), RC)
        # One answer and one preservation prefix exercise both native PC heads;
        # full profile retains the original 64-memory training population.
        answer = next(q for q in feats.queries if q.role == "new_paraphrase")
        preserve = next(q for q in feats.queries if q.role == "unrelated")
        feats = dataclasses.replace(
            feats,
            queries=[dataclasses.replace(q, prefixes=q.prefixes[:1]) for q in (answer, preserve)],
        )
        out, assets = tmp_path / rule, tmp_path / (rule + "-assets")
        out.mkdir()
        assets.mkdir()
        before = base.checksum(recompute=True)
        report = r.train_loop(
            base,
            RC,
            CC,
            rule,
            0,
            r.recipe(),
            lambda feats=feats: [feats],
            [feats],
            out,
            assets,
            steps=2,
            guard=lambda: None,
        )
        assert report["status"] == "complete" and report["profile_only"]
        assert report["base_sha256"] == before == base.checksum(recompute=True)
        assert report["reader"]["params_sha256"] != report["initial_reader_sha256"]
        recovered = r.load_theta(report["reader"], r.initial_theta(0, RC, CC))
        assert params_hash(recovered) == report["reader"]["params_sha256"]
        rows = [json.loads(s) for s in (out / "metrics.jsonl").read_text().splitlines()]
        assert all(np.isfinite(v) for v in rows[-1]["metrics"].values())
        if rule == "epc":
            assert base.ledger.totals()["learning"]["settle_iters"] > 0
            assert rows[-1]["metrics"]["settle_n"] == 2
        reports.append(report)
    assert reports[0]["initial_reader_sha256"] == reports[1]["initial_reader_sha256"]
    assert reports[0]["trajectory"] == reports[1]["trajectory"]


def test_checkpoint_mean_is_fixed_and_missing_steps_are_rejected():
    trees = [dict(x=np.array([n], np.float32)) for n in (1, 2, 3, 6)]
    np.testing.assert_array_equal(r.average_thetas(trees)["x"], [3])
    with pytest.raises(ValueError, match="four"):
        r.average_thetas(trees[:3])
