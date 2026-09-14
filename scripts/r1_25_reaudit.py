"""CPU-only R1-X2 controls for the installed R1-25/delta redesign; no core edits."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import numpy as np
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.tiny_base import TinyBase

from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.contracts import MemoryRecord
from pccap.revision_v1.epc_train import EPCTrainer
from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.memory import RecordStore
from pccap.revision_v1.reader import obs_arrays, pair_scores, params_hash, record_key
from pccap.revision_v1.train import LossConfig, _records, featurize


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def attempt(fn):
    try:
        fn()
        return {"raised": None}
    except Exception as e:
        return {"raised": type(e).__name__, "message": str(e)}


def main():
    dest = Path(sys.argv[1]).resolve()
    if dest.exists() or not dest.is_relative_to(ROOT):
        raise ValueError("new output inside pc_cap required")
    paths = sorted((ROOT / "src/pccap/revision_v1").glob("*.py"))
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    base, cfg = TinyBase(), _cfg(null_threshold=1.01)
    cap = RevisionCap(base, cfg, Ledger())
    frozen = params_hash(cap.params)
    ep = synthetic_episode(3)
    feats = featurize(base, cap.enc, ep, cfg.reader)
    altered = replace(ep, inputs=replace(ep.inputs,
        support_history=tuple(replace(s, answer_ids=tuple((x+7)%64 for x in s.answer_ids)) for s in ep.inputs.support_history),
        new_support=tuple(replace(s, answer_ids=tuple((x+7)%64 for x in s.answer_ids)) for s in ep.inputs.new_support)))
    changed = featurize(base, cap.enc, altered, cfg.reader)
    keys, codes = _records(cap.params, cfg.reader, feats)
    keys2, codes2 = _records(cap.params, cfg.reader, changed)
    out = {"support_answer_path": {"keys_equal": bool(np.array_equal(keys, keys2)),
        "codes_changed": bool(not np.array_equal(codes, codes2)),
        "own_prompt_queries": sum(q.role == "own_prompt" for q in feats.queries)},
        "unsupported_fast_unroll": attempt(lambda: LossConfig(fast_steps=1)),
        "unsupported_epc_penalty": attempt(lambda: EPCTrainer(cfg.reader, cfg.controller, None, LossConfig(w_code_norm=1)))}
    tr, _ = adapt_record(cap, _support(0), FastConfig(steps=0))
    state0 = cap.state_hash()
    tr, _ = adapt_record(cap, replace(_support(1), record_id="failed", fact_id="f0", revision=2), FastConfig(steps=1, lr=float("nan")))
    out["nonfinite_revision"] = {"reason": tr.rolled_back_reason, "state_restored": cap.state_hash() == state0,
        "new_removed": "failed" not in cap.store._by_id, "old_active": cap.store.get("s0").active}
    snapshot = cap.export_state()
    out["snapshot_configuration"] = {}
    for key, value in (("single_site", True), ("null_threshold", .1), ("binary_mass", False), ("hard_top1", False)):
        other = RevisionCap(base, replace(cfg, **{key:value}), Ledger(), params=cap.params)
        out["snapshot_configuration"][key] = attempt(lambda: other.import_state(snapshot))
    restored = RevisionCap(base, cfg, Ledger(), params=cap.params)
    old_bytes = restored.store.bytes()
    restored.import_state(snapshot)
    out["resume_weight_accounting"] = {"original": cap.store.bytes(), "restored": restored.store.bytes(),
        "same_state_hash": restored.state_hash() == cap.state_hash(), "weights_before_import": old_bytes["weights"]}
    tiny = RevisionCap(base, replace(cfg, ceiling_bytes=1), Ledger(), params=cap.params)
    out["constructor_ceiling"] = {"ceiling": 1, "reported_bytes": tiny.store.bytes()["total"], "accepted": True}
    long_store = RecordStore(8, 6, ceiling_bytes=256)
    long_store.add(MemoryRecord("x"*10000, "f", 1, -1, np.ones(8, np.float32), np.ones(6, np.float32)))
    st = long_store.export()
    out["metadata_ceiling"] = {"reported": long_store.bytes()["total"],
        "serialized_lower_bound": sum(a.nbytes for a in st.arrays.values()) + len(st.scalars["records"].encode())}
    # A nonselected delta must not suppress the selected record's controller.
    c = RevisionCap(base, cfg, Ledger(), params=cap.params)
    ids = np.int32([5, 6])
    obs, _ = c.enc.observe(ids)
    key = np.asarray(record_key(c.params["reader"], cfg.reader, *obs_arrays(obs, cfg.reader)))
    c.store.add(MemoryRecord("selected", "f", 1, -1, key, np.ones(6, np.float32)))
    logits_one = c.predict(ids).logits
    c.store.add(MemoryRecord("not-selected", "g", 1, -1, -key, np.ones(6, np.float32), delta=np.ones((1,3,16), np.float32)*.02))
    c.reset_queries()
    selected = c.selection_for(ids)
    logits_two = c.predict(ids).logits
    out["zero_weight_delta_candidate"] = {"ids": selected.record_ids, "weights": selected.weights.tolist(),
        "selected_record_has_delta": c.store.get(selected.record_ids[int(np.argmax(selected.weights))]).delta is not None,
        "selection_delta_present": selected.delta is not None,
        "selection_delta_norm": None if selected.delta is None else float(np.linalg.norm(selected.delta)),
        "logits_max_abs_change": float(np.max(np.abs(logits_one-logits_two)))}
    c.reset_queries()
    c.selection_for(ids)
    longer = np.int32([5,6,7])
    inherited = c.selection_for(longer).prompt_len
    c.reset_queries()
    out["independent_query_boundary"] = {"inherited_prompt_len": inherited, "fresh_prompt_len": c.selection_for(longer).prompt_len}
    empty = RevisionCap(base, cfg, Ledger(), params=cap.params)
    calls = base.calls["forward"]
    fr = empty.predict(ids)
    out["returned_cost"] = {"actual_full_forwards": base.calls["forward"]-calls, "returned_full_forwards": fr.cost.full_forwards}
    # Nondefault geometry and near-zero cosine implementations.
    k1, k2 = np.zeros(8,np.float32), np.zeros(8,np.float32)
    k1[0], k2[0], k2[1] = 10, 1, .1
    store = RecordStore(8,6)
    for rid,k in (("large",k1),("aligned",k2)):
        store.add(MemoryRecord(rid,rid,1,-1,k,np.ones(6,np.float32)))
    q=np.zeros(8,np.float32);q[0]=1
    scores=np.asarray(pair_scores(replace(cfg.reader,cosine=False),q,np.stack([k1,k2])))
    out["noncosine_config"]={"store_metric":store.metric,"dot_training_scores":scores.tolist(),"retrieved":store.retrieve(q,1)[0].record_id}
    k1[0],k2[0],k2[1]=1e-6,1e-4,1e-4
    store.records[0].key=k1;store.records[1].key=k2
    scores=np.asarray(pair_scores(cfg.reader,q,np.stack([k1,k2])))
    out["nearzero_cosine"]={"training_scores":scores.tolist(),"retrieved":store.retrieve(q,1)[0].record_id}
    out["base_and_reusable_weights_frozen"] = params_hash(cap.params) == frozen
    result={"task":"R1-X2","source_sha256_before":before,"source_sha256_after":{str(p.relative_to(ROOT)):sha(p) for p in paths},
        "controls":out,"gpu_seconds":0}
    with dest.open("x") as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps(out,indent=2))


if __name__ == "__main__":
    main()
