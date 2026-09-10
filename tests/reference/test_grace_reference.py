"""S2-05 reference writer controls and direct tests of the read-only GRACE source."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("grace_reference_oracle", ROOT / "scripts/grace_reference_oracle.py")
oracle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oracle)


def test_development_selection_is_balanced_deterministic_and_excludes_s0():
    dev, s0 = ROOT / "manifests/dev/zsre_dev.json", ROOT / "manifests/dev/s0_sample.json"
    rows = oracle.selected_cases(dev, s0)
    excluded = {i["item_id"] for i in json.loads(s0.read_text())["items"]}
    assert len(rows) == len({i["item_id"] for i in rows}) == 20
    assert not excluded & {i["item_id"] for i in rows}
    assert all(i["lexical_answer_tokens"] == 1 for i in rows[:10])
    assert all(i["lexical_answer_tokens"] > 1 for i in rows[10:])
    assert rows == oracle.selected_cases(dev, s0)
    assert all(i["answer_ids"][-1] == 198 for i in rows)


def test_writers_are_exclusive_and_roundtrip_without_pickle(tmp_path):
    path = tmp_path / "value.json"
    oracle.write_json(path, {"value": 3})
    with pytest.raises(FileExistsError):
        oracle.write_json(path, {"value": 4})
    assert json.loads(path.read_text()) == {"value": 3}
    path = tmp_path / "book.npz"
    oracle.write_npz(path, {"keys": np.eye(2, dtype=np.float32)})
    before = oracle.sha256(path)
    with pytest.raises(FileExistsError):
        oracle.write_npz(path, {"keys": np.ones((2, 2), np.float32)})
    assert oracle.sha256(path) == before
    with np.load(path, allow_pickle=False) as arrays:
        np.testing.assert_array_equal(arrays["keys"], np.eye(2))
    for i, values in enumerate((np.array([np.nan]), np.array([object()], dtype=object))):
        with pytest.raises(ValueError):
            oracle.write_npz(tmp_path / f"bad{i}.npz", {"values": values})


def test_insufficient_strata_are_rejected(tmp_path):
    dev = tmp_path / "dev.json"
    s0 = tmp_path / "s0.json"
    oracle.write_json(dev, {"mode": "dev", "dataset": "zsre", "items": []})
    oracle.write_json(s0, {"items": []})
    with pytest.raises(ValueError, match="ten non-S0"):
        oracle.selected_cases(dev, s0)


def test_checker_refuses_artifact_hash_mismatch(tmp_path):
    dev, s0 = ROOT / "manifests/dev/zsre_dev.json", ROOT / "manifests/dev/s0_sample.json"
    artifact = tmp_path / "fake.json"
    oracle.write_json(artifact, {"value": 3})
    manifest = {"grace_revision": oracle.REVISION, "model_revision": oracle.MODEL_REVISION,
                "cases": oracle.selected_cases(dev, s0),
                "inputs": {"zsre_dev.json": oracle.record(dev), "s0_sample.json": oracle.record(s0)},
                "files": {"fake.json": {**oracle.record(artifact), "sha256": "0" * 64}}}
    path = tmp_path / "manifest.json"
    oracle.write_json(path, manifest)
    with pytest.raises(ValueError, match="hash/size mismatch"):
        oracle.check(path)


def make_source_adapter(replacement="replace_last"):
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    sys.path.insert(0, str(oracle.CLONE))
    from grace.editors.grace import GRACEAdapter

    config = {"editor": {"eps": 1.0, "dist_fn": "euc", "replacement": replacement,
                         "num_pert": 8, "val_init": "cold", "eps_expand": "coverage",
                         "val_train": "sgd"}}
    layer = torch.nn.Linear(3, 4, bias=False)
    layer.requires_grad_(False)
    adapter = GRACEAdapter(config, layer, transpose=True)
    adapter.key_id = 1
    adapter.iter = 0
    adapter.training = True
    adapter.edit_label = torch.tensor([[7]])
    return torch, adapter


def test_source_radius_expansion_split_and_far_query_deferral():
    torch, adapter = make_source_adapter()
    original = torch.zeros((1, 3, 3))
    adapter(original)
    assert len(adapter.keys) == 1
    near = original.clone()
    near[:, 1, 0] = 1.5
    adapter(near)
    assert len(adapter.keys) == 1
    np.testing.assert_allclose(adapter.epsilons.detach().numpy().ravel(), [1.5], atol=1e-6)
    adapter.edit_label = torch.tensor([[8]])
    conflicting = original.clone()
    conflicting[:, 1, 0] = 1.0
    adapter(conflicting)
    assert len(adapter.keys) == 2
    np.testing.assert_allclose(adapter.epsilons.detach().numpy().ravel(), [0.5 - 1e-5, 0.5], atol=1e-6)
    adapter.training, adapter.iter = False, 99
    far = original.clone()
    far[:, 1, 0] = 10
    np.testing.assert_array_equal(adapter(far).detach().numpy(), adapter.layer(far).detach().numpy())


def test_source_prompt_replacement_excludes_key_position_and_eval_restores_rng():
    torch, adapter = make_source_adapter("replace_prompt")
    adapter.key_id = 2
    inputs = torch.zeros((1, 4, 3))
    adapter(inputs)
    with torch.no_grad():
        adapter.values.fill_(2.0)
    adapter.training, adapter.iter = False, 99
    rng_before = torch.random.get_rng_state().clone()
    key_before = adapter.key_id
    with oracle.evaluation_state(adapter):
        output = adapter(inputs)
        np.testing.assert_array_equal(output[:, :2].detach().numpy(), np.full((1, 2, 4), 2.0))
        np.testing.assert_array_equal(output[:, 2:].detach().numpy(), np.zeros((1, 2, 4)))
        torch.rand(10)
    assert torch.equal(torch.random.get_rng_state(), rng_before)
    assert adapter.key_id == key_before
