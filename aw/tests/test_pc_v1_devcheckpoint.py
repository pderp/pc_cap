"""PC-4 real-base development replay; absent local resources skip explicitly.

Run explicitly with CPU and PC4_OUTPUT pointing to a new JSON file. Never GPU.
"""
import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import hashlib
import json
import os
import time
from dataclasses import asdict
from pathlib import Path

import jax
import numpy as np
import pytest

from aw.pc_v1_acquire import PCRevisionCap
from pccap.bases.epc import EPCBase
from pccap.contracts import EditItem
from pccap.harness.ledger import Ledger
from pccap.harness.snapshot import restore

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / 'docs/tasks/R1-post63l-active/R1-64e/R1-64e-zsre-primary-v5.recipe.json'
SNAPSHOT = ROOT.parent / 'assets/runs/pc_cap/R1/stage4_dev_cells/R1_learned_ff-zsre-development_full_endpoints_R164f-seed64028-c84c64b1149e74b70edb/attempt-0000/checkpoint-300.snapshot'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def counts(cost):
    return {k: v for k, v in asdict(cost).items() if k not in ('accel_seconds', 'wall_seconds', 'rebuild_seconds')}


def timed(fn):
    start = time.monotonic()
    result = fn()
    return result, time.monotonic() - start


@pytest.mark.slow
def test_saved_v5_checkpoint_real_base_parity_and_pc_execution():
    if not SNAPSHOT.exists() or not RECIPE.exists():
        pytest.skip('saved v5 development checkpoint/recipe absent')
    assert jax.default_backend() == 'cpu', 'PC-4 is CPU only'
    from scripts.r1_61_cell_driver import construct_owner_adapter

    recipe = json.loads(RECIPE.read_bytes())
    metadata = json.loads(SNAPSHOT.with_suffix('.snapshot.json').read_bytes())
    assert sha(SNAPSHOT) == metadata['snapshot_sha256']
    payload_path = Path(recipe['payload']['path'])
    assert sha(payload_path) == recipe['payload']['sha256']
    rows = json.loads(payload_path.read_bytes())['items']
    started = time.monotonic()
    adapter, _ = construct_owner_adapter(recipe)
    assert adapter.identity() == recipe['adapter_identity']
    original = adapter.learner
    state = restore(SNAPSHOT.read_bytes(), expected_hash=metadata['state_sha256'])
    original.import_state(state)
    # Same BP tensors; EPC merely adds the error-inference interface.
    base = EPCBase(params_np=jax.tree_util.tree_map(np.asarray, original.base.params),
                   cfg=original.base.cfg, ledger=Ledger(), error_lr=.1)
    assert base.checksum(recompute=True) == original.base.checksum(recompute=True)
    adj = PCRevisionCap(base, original.cfg, base.ledger, params=original.params)
    adj.import_state(state)
    predictions = []
    for row in rows[:4]:
        for ids in (np.int32(row['prompt_ids']), np.int32(row['prompt_ids'] + row['answer_ids'][:1])):
            x, tx = timed(lambda ids=ids: original.predict(ids))
            y, ty = timed(lambda ids=ids: adj.predict(ids))
            np.testing.assert_array_equal(x.logits, y.logits)
            assert counts(x.cost) == counts(y.cost)
            predictions.append(dict(item=row['item_id'], length=len(ids), max_abs_difference=0,
                                    original_seconds=tx, adjoint_seconds=ty, counts=counts(x.cost)))
        original.reset_queries()
        adj.reset_queries()
    assert original.state_hash() == adj.state_hash() == state.content_hash()
    assert original.cost_counters == adj.cost_counters
    # First development item with at most two answer tokens, including terminator.
    row = next(r for r in rows if len(r['answer_ids']) <= 2)
    item = EditItem(**{k: row[k] for k in ('item_id', 'fact_id', 'dataset', 'prompt', 'answer', 'aliases', 'paraphrases', 'locality_prompts')},
                    digest=bytes.fromhex(row['digest']), prompt_ids=np.int32(row['prompt_ids']), answer_ids=np.int32(row['answer_ids']))
    before = base.checksum(recompute=True)
    x, tx = timed(lambda: original.update_item(item))
    y, ty = timed(lambda: adj.update_item(item))
    assert x.code == y.code and x.prefix_outcomes == y.prefix_outcomes
    assert counts(x.cost) == counts(y.cost)
    assert original.state_hash() == adj.state_hash()
    assert original.cost_counters == adj.cost_counters
    np.testing.assert_array_equal(original.predict(item.prompt_ids).logits, adj.predict(item.prompt_ids).logits)
    # Explicit in-memory conversion of the saved memory to the PC treatment.
    # This is a smoke replay, not a resumed confirmatory trajectory.
    pc = PCRevisionCap(base, original.cfg, base.ledger, params=original.params, acquisition_credit='error')
    pc_state = copy.deepcopy(state)
    pc_state.scalars['config'] = pc.semantic_config()
    pc.import_state(pc_state)
    assert pc.store.export().content_hash() == copy_store_hash(state, original)
    result, tp = timed(lambda: pc.update_item(item))
    logits = pc.predict(item.prompt_ids).logits
    assert np.all(np.isfinite(logits))
    assert result.cost.settle_iters > 0 and result.cost.settle_iters % 8 == 0
    assert base.checksum(recompute=True) == before
    assert original.base.checksum(recompute=True) == before
    assert pc.params_hash == adj.params_hash == original.params_hash
    data = dict(task='PC-4', device=str(jax.devices()), gpu_seconds=0, predictions=predictions,
                acquisition=dict(item_id=item.item_id, answer_tokens=len(item.answer_ids), original_seconds=tx,
                                 adjoint_seconds=ty, error_seconds=tp, adjoint_counts=counts(y.cost),
                                 error_counts=counts(result.cost), error_outcome=result.code),
                exact_prediction_count=len(predictions)+1, exact_adjoint_state=True, exact_adjoint_counters=True,
                base_unchanged=True, wall_seconds=time.monotonic()-started,
                bindings={str(p):sha(p) for p in (RECIPE, SNAPSHOT, SNAPSHOT.with_suffix('.snapshot.json'), payload_path, Path(__file__), ROOT/'aw/pc_v1_acquire.py')},
                reader_weights=recipe['construction']['weights'], base_hash=before,
                qualification='Sequential CPU timings include compilation and unequal warmup; not GPU forecasts or quality results. PC memory was copied from the same saved development state with an explicit in-memory credit-configuration conversion.')
    dest = os.environ.get('PC4_OUTPUT')
    if dest:
        path = Path(dest)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x') as f:
            json.dump(data, f, indent=2, allow_nan=False)
            f.write('\n')
    print(json.dumps({k:data[k] for k in ('wall_seconds','exact_prediction_count','exact_adjoint_state','exact_adjoint_counters')}))


def copy_store_hash(state, original):
    from pccap.revision_v1.memory import RecordStore
    store = RecordStore.from_state(state)
    store.weights_bytes = 4 * original.n_params
    store.ceiling_bytes = original.cfg.ceiling_bytes
    return store.export().content_hash()
