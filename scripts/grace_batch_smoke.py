#!/usr/bin/env python3
"""CPU development query comparison on the fixed final 20-entry GRACE codebook."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True

import pccap  # noqa: E402,F401

# isort: split
import numpy as np  # noqa: E402

from pccap.baselines.grace_batch import BatchedGraceLearner  # noqa: E402
from pccap.baselines.grace_jax import GraceLearner  # noqa: E402
from pccap.baselines.grace_parity import to_item  # noqa: E402
from pccap.bases.bp import BPBase  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/S2/grace_jax/batch_smoke.json"


def nll(logits, targets):
    logits = logits.astype(np.float64)
    mx = logits.max(-1)
    return float(np.sum(mx + np.log(np.exp(logits-mx[:, None]).sum(-1)) - logits[np.arange(len(targets)), targets]))


def main():
    assert not OUT.exists()
    started = time.monotonic()
    manifest = json.loads((ROOT / "manifests/dev/grace_parity_cases.json").read_text())
    ref = manifest["files"][manifest["cases"][-1]["sequence_codebook"]]
    path = Path(ref["path"])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == ref["sha256"]
    raw = {r["item_id"]: r for r in json.loads((ROOT / "manifests/dev/zsre_dev.json").read_text())["items"]}
    base = BPBase()
    scalar = GraceLearner(base)
    with np.load(path, allow_pickle=False) as book:
        scalar.keys, scalar.values, scalar.radii = (book[k].reshape((-1, width)).astype(np.float32) if width > 1 else book[k].reshape(-1).astype(np.float32) for k, width in (("keys", 768), ("values", 3072), ("radii", 1)))
        scalar.labels = [book[f"key_label_{i}"].reshape(-1).astype(np.int64) for i in range(len(scalar.keys))]
    scalar.use_counts = np.zeros(len(scalar.keys), np.int64)
    scalar.ages = np.arange(len(scalar.keys), dtype=np.int64)
    scalar.items_seen = scalar.allocations = len(scalar.keys)
    batch = BatchedGraceLearner(base)
    batch.import_state(scalar.export_state())
    seqs, boundaries, spans, targets = [], [], [], []
    for case in manifest["cases"]:
        item = to_item(raw[case["item_id"]])
        start = len(seqs)
        for t in range(len(item.answer_ids)):
            seqs.append(np.concatenate([item.prompt_ids, item.answer_ids[:t]]))
            boundaries.append(len(item.prompt_ids)-1)
        spans.append((case["item_id"], start, len(seqs)))
        targets.extend(item.answer_ids)
    before = batch.state_hash()
    expected = np.stack([scalar.predict(ids, key_position=pos, last_only=True) for ids, pos in zip(seqs, boundaries)])
    actual = batch.last_logits_batch(seqs, key_positions=boundaries)
    rows = []
    for iid, start, stop in spans:
        wanted, got = expected[start:stop], actual[start:stop]
        a, b = nll(wanted, np.asarray(targets[start:stop])), nll(got, np.asarray(targets[start:stop]))
        rows.append({"item_id": iid, "prefixes": stop-start, "max_abs_logit_gap": float(np.max(np.abs(got-wanted))), "all_logits_close": bool(np.allclose(got, wanted, atol=2e-4, rtol=2e-5)), "teacher_forced_argmax_equal": bool(np.array_equal(got.argmax(-1), wanted.argmax(-1))), "scalar_answer_nll": a, "batch_answer_nll": b, "nll_abs_gap": abs(a-b), "nll_pass": bool(np.isclose(a, b, atol=1e-3, rtol=1e-4))})
    unchanged = before == batch.state_hash() == scalar.state_hash()
    result = {"scope": "fixed source codebook, JAX scalar vs vmapped teacher-forced query paths; no training or free-generation parity claim", "cases": rows, "prefixes": len(seqs), "source_codebook_sha256": ref["sha256"], "base_unchanged": base.checksum() == scalar._base_hash, "learner_unchanged": unchanged, "tolerances": {"logits": {"atol": 2e-4, "rtol": 2e-5}, "answer_nll": {"atol": 1e-3, "rtol": 1e-4}}, "wall_seconds": time.monotonic()-started, "gpu_seconds": 0}
    result["pass"] = unchanged and result["base_unchanged"] and all(r["all_logits_close"] and r["teacher_forced_argmax_equal"] and r["nll_pass"] for r in rows)
    with OUT.open("x") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k:v for k,v in result.items() if k != "cases"},indent=2))
    assert result["pass"]


if __name__ == "__main__":
    main()
