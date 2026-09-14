"""Positive data/update boundary controls complementing r1_23_audit.py (CPU only)."""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.reader import params_hash
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.tiny_base import TinyBase


def main():
    p = Path(sys.argv[1]).resolve()
    if p.exists() or not p.is_relative_to(ROOT):
        raise ValueError("output must be new inside pc_cap")
    cap = RevisionCap(TinyBase(), _cfg(null_threshold=1.01), Ledger())
    frozen = params_hash(cap.params)
    base_hash = params_hash(cap.base.params)
    traces = []
    tr, _ = adapt_record(cap, _support(0), FastConfig(steps=3, lr=.001))
    traces.append(tr)
    key = cap.store.get("s0").key.copy()
    code = cap.store.get("s0").code.copy()
    tr, _ = adapt_record(cap, _support(1), FastConfig(steps=3, lr=.001))
    traces.append(tr)
    assert all(t.accepted for t in traces)
    assert np.array_equal(key, cap.store.get("s0").key)
    assert np.array_equal(code, cap.store.get("s0").code)
    assert params_hash(cap.params) == frozen and params_hash(cap.base.params) == base_hash
    ep = synthetic_episode(3)
    poisoned = replace(ep, query_labels=tuple(replace(l, target_ids=(17, 19), target="wrong audit label",
        target_source="audit_poison", supporting_record_ids=("incorrect-id",), role="unrelated") for l in ep.query_labels))
    assert poisoned.prediction_inputs() == ep.prediction_inputs()
    before = cap.state_hash()

    def predict_inputs(episode):
        values = []
        for q in episode.prediction_inputs():
            cap.reset_queries()  # explicit independent-query boundary required by the current API
            values.append(np.asarray(cap.predict(q.prompt_ids).logits))
        return values

    first, second = predict_inputs(ep), predict_inputs(poisoned)
    assert all(np.array_equal(a, b) for a, b in zip(first, second))
    assert cap.state_hash() == before
    result = {"gpu_seconds": 0, "accepted_support_updates": len(traces),
        "losses": [{"before": t.loss_before, "after": t.loss_after} for t in traces],
        "unrelated_record_key_and_code_unchanged": True, "reusable_and_base_weights_unchanged": True,
        "poisoned_query_label_count": len(ep.query_labels), "predictions_bit_identical_after_label_poisoning": True,
        "persistent_state_unchanged_by_prediction": True,
        "scope": "Label-free public API with explicit query resets. Does not negate missing reset boundaries in the installed harness.",
        "source_sha256": {str(x.relative_to(ROOT)): hashlib.sha256(x.read_bytes()).hexdigest()
            for x in sorted((ROOT / "src/pccap/revision_v1").glob("*.py"))}}
    with p.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "source_sha256"}, indent=2))


if __name__ == "__main__":
    main()
