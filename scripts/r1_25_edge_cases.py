"""Supplementary CPU-only R1-X2 controls and development token-length inventory."""
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
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.memory import CapacityError, RecordStore
from pccap.revision_v1.reader import pair_scores


def main(dest):
    dest = Path(dest).resolve()
    if dest.exists() or not dest.is_relative_to(ROOT):
        raise ValueError("new repository output required")
    cfg = _cfg(null_threshold=1.01)
    q = np.zeros(8, np.float32); q[:2] = [1,1]
    k1, k2 = np.zeros(8,np.float32), np.zeros(8,np.float32)
    k1[0], k2[0], k2[1] = 10, 1, .1
    store = RecordStore(8,6)
    for rid,k in (("large",k1),("aligned",k2)):
        store.add(MemoryRecord(rid,rid,1,-1,k,np.zeros(6,np.float32)))
    scores = np.asarray(pair_scores(replace(cfg.reader, cosine=False), q, np.stack([k1,k2])))
    out = {"noncosine_ranking": {"training_scores": scores.tolist(), "training_best": ["large","aligned"][int(scores.argmax())],
        "deployed_best": store.retrieve(q,1)[0].record_id, "store_metric": store.metric}}
    cap = RevisionCap(TinyBase(),cfg,Ledger())
    adapt_record(cap,_support(0),FastConfig(steps=0))
    before = cap.state_hash()
    # Enough for the inserted replacement's key/code/tokens, not its delta array.
    cap.store.ceiling_bytes = cap.store.bytes()["total"] + 212 + 1
    original_hash = cap.state_hash()
    try:
        trace,_ = adapt_record(cap,_support(1,fact="f0",rev=2),FastConfig(steps=0,delta_steps=5,delta_lr=.1))
        error = None
    except CapacityError as exc:
        error = str(exc)
    out["delta_capacity_direct_api"] = {"error": error, "state_changed": cap.state_hash()!=original_hash,
        "old_active": cap.store.get("s0").active, "replacement_present": "s1" in cap.store._by_id,
        "scope": "direct adapt_record, no ItemGuard; generic harness exception rollback is a separate boundary"}
    # Controlled loss oracle isolates WHICH baseline gates delta acceptance.
    b = TinyBase()
    real_adjoint = b.adjoint
    def adjoint(*a,**kw):
        result = real_adjoint(*a,**kw)
        if kw.get("return_loss"):
            return result[0],100.0,result[2]
        return result
    real_loss = b.loss
    def loss(ids,target,writes=(),**kw):
        _,fr = real_loss(ids,target,writes,**kw)
        return (2.0 if any(np.any(w.vector) for w in writes) else 1.0),fr
    b.adjoint, b.loss = adjoint, loss
    c = RevisionCap(b,cfg,Ledger())
    trace,_ = adapt_record(c,_support(0),FastConfig(steps=0,delta_steps=1,delta_lr=.1))
    out["delta_acceptance_comparator_controlled_oracle"] = {"controller_initial_loss":trace.loss_before,
        "delta_initial_capoff_loss":1.0,"delta_final_loss":trace.loss_after,"accepted":trace.accepted,
        "scope":"controlled loss oracle, demonstrates comparison rule; not a measured GPT-2 loss trajectory"}
    c2 = RevisionCap(TinyBase(),cfg,Ledger())
    trace,_ = adapt_record(c2,_support(0),FastConfig(steps=1,delta_steps=5))
    out["mixed_fast_config"]={"code_steps":1,"delta_steps_requested":5,"delta_stored":c2.store.get("s0").delta is not None,
        "configuration_rejected":False,"actual_steps":trace.steps_used}
    out["development_delta_sizes"]={}
    for ds in ("zsre","counterfact"):
        rows=json.loads((ROOT/f"manifests/dev/{ds}_dev.json").read_text())["items"]
        lengths=np.array([len(r["answer_ids"]) for r in rows])
        out["development_delta_sizes"][ds]={"items":len(rows),"mean_answer_tokens":float(lengths.mean()),
            "max_answer_tokens":int(lengths.max()),"median_answer_tokens":float(np.median(lengths)),
            "delta_bytes_per_answer_prefix":3*768*4,"mean_delta_bytes_per_record":float(lengths.mean()*3*768*4),
            "max_delta_bytes_per_record":int(lengths.max()*3*768*4),
            "scope":"all existing development rows, not a sampled/final stream; predictions before overhead/revisions"}
    out["gpu_seconds"]=0
    with dest.open("x") as f:json.dump(out,f,indent=2,allow_nan=False)
    print(json.dumps(out,indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
