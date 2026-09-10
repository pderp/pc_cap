"""REF-01 writer and independent HF hook controls (CPU reference environment).

Run with PYTHONDONTWRITEBYTECODE=1 and pytest -p no:cacheprovider; temporary
fixtures live under assets/tmp/ref01, never beside shared source/model files.
"""
import importlib.util
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "make_reference_fixtures.py"
SPEC = importlib.util.spec_from_file_location("ref01_writer", SCRIPT)
ref = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ref)


def test_exclusive_json_and_npz_writers_preserve_existing_files(tmp_path):
    path = tmp_path / "record.json"
    ref.write_json_new(path, {"original": True})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        ref.write_json_new(path, {"original": False})
    assert path.read_bytes() == original
    archive = tmp_path / "arrays.npz"
    with zipfile.ZipFile(archive, "x") as writer:
        ref.npz_add(writer, "ids", np.array([1, 2], dtype=np.int32))
        ref.npz_add(writer, "values", np.eye(3, dtype=np.float32))
    with np.load(archive, allow_pickle=False) as arrays:
        np.testing.assert_array_equal(arrays["ids"], [1, 2])
        assert arrays["values"].dtype == np.float32
    with pytest.raises(FileExistsError):
        with zipfile.ZipFile(archive, "x"):
            pass


def test_npz_writer_rejects_nonfinite_and_object_arrays(tmp_path):
    with zipfile.ZipFile(tmp_path / "reject.npz", "x") as writer:
        for array in (np.array([np.nan]), np.array([object()], dtype=object)):
            with pytest.raises(ValueError, match="nonfinite or object"):
                ref.npz_add(writer, "bad", array)


def test_prompt_selection_is_first_256_with_stable_ids_and_no_answer_dependency(tmp_path):
    path = tmp_path / "source.json"
    rows = [{"src": f"Prompt {i}", "answers": [f"hidden {i}"]} for i in range(260)]
    path.write_text(json.dumps(rows))
    selected = ref.selected_prompts(path)
    assert len(selected) == 256
    assert [row["source_index"] for row in selected] == list(range(256))
    assert selected[0]["item_id"] == "zsre_mend_eval:0"
    assert "answers" not in selected[0]
    altered = [{**row, "answers": ["different hidden label"]} for row in rows]
    alternate_path = tmp_path / "alternate.json"
    alternate_path.write_text(json.dumps(altered))
    assert ref.selected_prompts(alternate_path) == selected
    short_path = tmp_path / "short.json"
    short_path.write_text(json.dumps(rows[:10]))
    with pytest.raises(ValueError, match="at least 256"):
        ref.selected_prompts(short_path)


def test_input_hashes_and_pinned_revision_are_required(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    catalog = {"gpt2": {"revision": ref.REVISION, "files": {}}, "zsre": {"files": {}}}
    for name in ref.MODEL_FILES:
        path = snapshot / name
        path.write_bytes(name.encode())
        catalog["gpt2"]["files"]["models/gpt2/" + name] = ref.sha256(path)
    source = tmp_path / "zsre.json"
    source.write_text("[]")
    catalog["zsre"]["files"]["data/raw/zsre/zsre_mend_eval.json"] = ref.sha256(source)
    registry = tmp_path / "catalog.json"
    registry.write_text(json.dumps(catalog))
    records = ref.source_inputs(snapshot, source, registry)
    assert set(records) == {*ref.MODEL_FILES, "zsre_mend_eval.json", "datasets_manifest"}
    altered = json.loads(json.dumps(catalog))
    altered["gpt2"]["files"]["models/gpt2/model.safetensors"] = "0" * 64
    registry_bad = tmp_path / "catalog_bad.json"
    registry_bad.write_text(json.dumps(altered))
    with pytest.raises(ValueError, match="hash mismatch"):
        ref.source_inputs(snapshot, source, registry_bad)


def test_check_detects_artifact_hash_mismatch_before_loading_arrays(tmp_path):
    fake = tmp_path / "fake"
    fake.write_bytes(b"artifact")
    manifest = {"model_revision": ref.REVISION, "n_prompts": 256,
                "artifacts": {name: {"path": str(fake), "bytes": 8, "sha256": "0" * 64}
                              for name in ("logits_256.npz", "lengths.npz", "greedy_8.json", "ref_env.json")}}
    path = tmp_path / "manifest.json"
    ref.write_json_new(path, manifest)
    with pytest.raises(ValueError, match="artifact hash/size mismatch"):
        ref.check(path)


@pytest.fixture
def tiny_model():
    torch = pytest.importorskip("torch")
    transformers = pytest.importorskip("transformers")
    torch.set_num_threads(2)
    torch.manual_seed(17)
    config = transformers.GPT2Config(n_layer=12, n_embd=16, n_head=2,
                                    vocab_size=32, n_positions=64, eos_token_id=31,
                                    resid_pdrop=0, embd_pdrop=0, attn_pdrop=0)
    config._attn_implementation = "eager"
    return transformers.GPT2LMHeadModel(config).float().eval()


def test_hooks_capture_pre_final_normalization_and_leave_no_handles(tiny_model):
    import torch

    ids = torch.tensor([[2, 3, 4]])
    logits, captured = ref.capture_forward(tiny_model, ids)
    assert all(len(block._forward_hooks) == 0 for block in tiny_model.transformer.h)
    assert not tiny_model.transformer.ln_f._forward_hooks
    with torch.inference_mode():
        independent = tiny_model(ids, use_cache=False, output_hidden_states=True)
        normalized = tiny_model.transformer.ln_f(torch.from_numpy(captured[11])[None])
    np.testing.assert_array_equal(logits, independent.logits[0].numpy())
    np.testing.assert_array_equal(captured[3], independent.hidden_states[4][0].numpy())
    np.testing.assert_array_equal(captured[7], independent.hidden_states[8][0].numpy())
    np.testing.assert_array_equal(captured["ln_f"], independent.hidden_states[-1][0].numpy())
    np.testing.assert_array_equal(normalized[0].numpy(), captured["ln_f"])
    assert not np.allclose(captured[11], captured["ln_f"])
    # Transformers installs its own persistent output-capture hooks above.
    # Our writer must remove its handles and preserve those existing hooks.
    existing_hooks = [dict(block._forward_hooks) for block in tiny_model.transformer.h]
    ref.capture_forward(tiny_model, ids)
    assert [dict(block._forward_hooks) for block in tiny_model.transformer.h] == existing_hooks
    assert not tiny_model.transformer.ln_f._forward_hooks


def test_partial_hook_registration_is_cleaned_up_on_error(tiny_model):
    import torch

    with pytest.raises(IndexError):
        ref.capture_forward(tiny_model, torch.tensor([[1]]), blocks=(0, 99))
    assert not tiny_model.transformer.h[0]._forward_hooks


def test_greedy_has_expected_consumer_keys_and_cache_comparison(tiny_model):
    class Tokenizer:
        eos_token_id = 31

    case = ref.greedy_case(tiny_model, Tokenizer(), [2, 3], {"item_id": "toy", "source_index": 0})
    assert case["prompt_ids"] == [2, 3]
    assert 1 <= len(case["generated_ids_no_cache"]) <= 32
    assert case["generated_ids_cache"] == case["generated_ids_no_cache"]
    assert case["cache_agrees"]
