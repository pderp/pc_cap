"""S2-03 numerical, state, accounting, and full GPT-2 learning controls.

CPU controls: JAX_PLATFORMS=cpu pytest ... -m 'not gpu'. GPU control prints
development diagnostics; the caller captures stdout into a fresh report.
"""

import copy
import json
from dataclasses import asdict

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from pccap.baselines import lora_forward as lf
from pccap.baselines.b0 import B0
from pccap.baselines.lora import LoRALearner
from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.cap.memory import b_cap
from pccap.contracts import EditItem
from pccap.data.decode import greedy_decode, teacher_forced_nll
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.snapshot import ItemGuard, SnapshotError, restore, serialize


def small_base():
    cfg = g.GPT2Config(n_layer=2, n_head=2, d=16, vocab=32, n_pos=64)
    rng = np.random.default_rng(19)

    def normal(shape):
        return rng.normal(0, 0.1, shape).astype(np.float32)

    def norm():
        return {"g": np.ones(cfg.d, np.float32), "b": np.zeros(cfg.d, np.float32)}

    def linear(n, m):
        return {"w": normal((n, m)), "b": np.zeros(m, np.float32)}

    params = {"wte": normal((cfg.vocab, cfg.d)), "wpe": normal((cfg.n_pos, cfg.d)),
              "ln_f": norm(), "blocks": [
                  {"ln_1": norm(), "ln_2": norm(), "c_attn": linear(cfg.d, 3 * cfg.d),
                   "c_proj": linear(cfg.d, cfg.d), "c_fc": linear(cfg.d, 4 * cfg.d),
                   "c_proj2": linear(4 * cfg.d, cfg.d)} for _ in range(cfg.n_layer)
              ]}
    return BPBase(params_np=params, cfg=cfg)


def item(index=0):
    return EditItem(str(index), index.to_bytes(16, "little"), "toy", "answer", [], [], [],
                    np.array([2, 3, 4], np.int32), np.array([7, 8, 9], np.int32))


def test_qv_factor_layout_dense_forward_parity_and_zero_k_gradient():
    base = small_base()
    learner = LoRALearner(base, rank=3)
    before = base.checksum()
    expected = {f"lora.{i}.{p}.{f}" for i in range(2) for p in ("q", "v") for f in ("A", "B")}
    assert set(learner.trainable_tensors()) == expected
    ids = np.array([2, 5, 7], np.int32)
    np.testing.assert_allclose(learner.predict(ids), base.forward(ids).logits, atol=1e-6)
    adapters = copy.deepcopy(learner.adapters)
    dense = jax.tree_util.tree_map(np.array, base.params)
    for i, a in enumerate(adapters):
        for p in ("q", "v"):
            a[p]["B"] = jnp.full((base.d, 3), 0.04 * (i + 1))
        delta = np.asarray(lf.attention_delta(a))
        np.testing.assert_array_equal(delta[:, base.d:2 * base.d], 0)
        np.testing.assert_allclose(delta[:, :base.d], np.asarray(a["q"]["B"]) @ np.asarray(a["q"]["A"]), atol=1e-8)
        gradients = jax.grad(lambda x: lf.attention_delta(x)[:, base.d:2 * base.d].sum())(a)
        assert all(np.count_nonzero(x) == 0 for x in jax.tree_util.tree_leaves(gradients))
        dense["blocks"][i]["c_attn"]["w"] += delta
    learner.adapters = adapters
    reference = BPBase(params_np=dense, cfg=base.cfg)
    np.testing.assert_allclose(learner.predict(ids), reference.forward(ids).logits, atol=2e-6)
    assert base.checksum() == before


def test_whole_answer_mask_matches_sequential_scoring_and_excludes_padding():
    learner = LoRALearner(small_base(), rank=2)
    edit = item()
    pair = learner.prepare_item(edit)
    (ids, targets, mask), tokens = learner._batch([pair])
    loss = lf.answer_loss(learner.base.params, learner.adapters, ids[0], targets[0], mask[0], learner.base.cfg)
    sequential = teacher_forced_nll(learner.predict, *pair)
    assert tokens == 5 and int(mask.sum()) == len(edit.answer_ids)
    np.testing.assert_allclose(loss, sequential["value"] / len(edit.answer_ids), atol=1e-6)
    changed = targets.at[0, 0].set(31).at[0, -1].set(30)
    masked_loss = lf.answer_loss(learner.base.params, learner.adapters, ids[0], changed[0], mask[0], learner.base.cfg)
    np.testing.assert_array_equal(loss, masked_loss)


def test_training_cost_snapshot_future_equivalence_and_rollback():
    base = small_base()
    learner = LoRALearner(base, rank=2, lr=0.01, steps=2)
    edit = item()
    before_base = base.checksum()
    initial = learner.state_hash()
    result = learner.update_item(edit)
    assert result.code == "accepted" and result.rounds_used == 2
    assert result.cost.full_forwards == result.cost.reverses == 2
    assert result.cost.tokens == 2 * 5
    assert learner.state_hash() != initial
    saved = restore(serialize(learner.export_state()))
    fork = LoRALearner(base, rank=2, lr=0.01, steps=2, seed=999)
    fork.import_state(saved)
    assert fork.state_hash() == learner.state_hash()
    learner.update_item(edit)
    fork.update_item(edit)
    assert fork.state_hash() == learner.state_hash()
    saved_hash = learner.state_hash()
    counters = base.ledger.learning.reverses
    with ItemGuard(learner):
        learner.update_item(edit)
    assert learner.state_hash() == saved_hash
    assert base.ledger.learning.reverses == counters + 2
    assert base.checksum() == before_base
    query_before = base.ledger.query.full_forwards
    prediction = learner.predict(edit.prompt_ids)
    assert prediction.shape == (3, 32) and prediction.logits is prediction
    assert learner.state_hash() == saved_hash
    assert base.ledger.query.full_forwards == query_before + 1


def test_memory_reports_adapters_adam_and_snapshot_metadata():
    learner = LoRALearner(small_base(), rank=2)
    state = learner.export_state()
    report = learner.memory_bytes()
    params = sum(a.nbytes for a in learner.trainable_tensors().values())
    assert report.per_bank[0]["adapter_bytes"] == params
    assert report.per_bank[0]["optimizer_bytes"] == 2 * params + 4
    assert report.allocated_bytes == len(serialize(state)) == report.occupied_bytes
    assert report.allocated_bytes == 3 * params + 4 + report.index_bytes
    assert report.ceiling_bytes == b_cap(learner.base.d)


def test_invalid_inputs_and_snapshot_refusal_are_atomic():
    learner = LoRALearner(small_base(), rank=2)
    saved = learner.export_state()
    for prompt, answer in (([], [1]), ([1.5], [1]), ([1], [-1]), ([1], [32]), ([1] * 65, [1])):
        with pytest.raises(ValueError):
            learner.prepare_tokens(prompt, answer)
    bad = saved.clone()
    bad.arrays["adam_count"] = np.array(7, np.int32)
    with pytest.raises(SnapshotError):
        learner.import_state(bad)
    bad = saved.clone()
    bad.scalars["lr"] = 0.2
    with pytest.raises(SnapshotError):
        learner.import_state(bad)
    assert learner.state_hash() == saved.content_hash()


def test_b0_no_op_query_cost_and_snapshot_contract():
    base = small_base()
    learner = B0(base)
    before = learner.state_hash()
    out = learner.update_item(item())
    assert out.code == "accepted" and out.rounds_used == 0
    assert out.cost.full_forwards == out.cost.reverses == 0
    assert base.ledger.events == 0
    values = learner.predict(item().prompt_ids)
    assert values.shape == (3, 32) and values.logits is values
    assert base.ledger.query.full_forwards == 1 and base.ledger.learning.full_forwards == 0
    learner.import_state(restore(serialize(learner.export_state())))
    assert learner.state_hash() == before
    assert learner.memory_bytes().per_bank[0]["optimizer_bytes"] == 0


@pytest.mark.gpu
def test_gpt2_ten_step_edit_reduces_nll_and_reports_greedy():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("pinned GPT-2 checkpoint is unavailable")
    assert jax.default_backend() == "gpu", "run the gpu control on the GPU backend"
    from pccap.harness.stage_s0 import load_items

    base = BPBase()
    tok = GPT2Tokenizer()
    edit = load_items(["s0_sample[0]"], tok)[0]
    learner = LoRALearner(base)
    frozen = base.checksum()
    expected = {f"lora.{i}.{p}.{f}" for i in range(12) for p in ("q", "v") for f in ("A", "B")}
    assert set(learner.trainable_tensors()) == expected
    for layer in learner.adapters:
        grad = jax.grad(lambda a: lf.attention_delta(a)[:, base.d:2 * base.d].sum())(layer)
        assert all(np.count_nonzero(a) == 0 for a in jax.tree_util.tree_leaves(grad))
    before = teacher_forced_nll(learner.predict, edit.prompt_ids, edit.answer_ids)["value"]
    decoded_before = greedy_decode(learner.predict, edit.prompt_ids, tok, state_hash=learner.state_hash)
    result = learner.update_item(edit)
    after = teacher_forced_nll(learner.predict, edit.prompt_ids, edit.answer_ids)["value"]
    decoded_after = greedy_decode(learner.predict, edit.prompt_ids, tok, state_hash=learner.state_hash)
    assert after < before
    assert result.cost.full_forwards == result.cost.reverses == result.rounds_used == 10
    assert result.cost.tokens == 10 * (len(edit.prompt_ids) + len(edit.answer_ids) - 1)
    assert base.checksum() == frozen
    print(json.dumps({"task": "S2-03", "item_id": edit.item_id, "nll_before": before,
                      "nll_after": after, "greedy_before": decoded_before.text,
                      "greedy_after": decoded_after.text,
                      "greedy_changed": decoded_before.text != decoded_after.text,
                      "token_ids_before": decoded_before.new_ids.tolist(),
                      "token_ids_after": decoded_after.new_ids.tolist(),
                      "base_checksum": frozen, "trainable_tensors": len(expected),
                      "memory": asdict(learner.memory_bytes()), "update_cost": result.cost.as_dict(),
                      "ledger": base.ledger.totals()}, sort_keys=True))
