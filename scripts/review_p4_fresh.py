#!/usr/bin/env python3
"""Lane X: fresh-seed CPU P4 review; never replace the published P4 or coverage."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True

import pccap  # noqa: E402,F401

# isort: split
import numpy as np  # noqa: E402

from pccap.analysis import s1_p4, s1_p6  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/p4_s7_review"
OFFSET = 10_000_000


def main():
    OUT.mkdir(exist_ok=False)
    reference = ROOT / "results/S1/P4_gram.json"
    watched = [reference, Path(s1_p4.__file__), Path(s1_p6.__file__)]
    def hashes():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = hashes()
    policy = {
        "n": 2048, "batch": 64, "seed_offset": OFFSET, "gpu": False,
        "comparison": "Report every metric delta against the existing 8192 run. Estimate a descriptive sampling scale for the three error-overlap means from disjoint 1024-row halves of the fresh sample. This is not a confidence interval or an acceptance threshold.",
        "fixed_auxiliary_counts": {"private_per_context": 2048, "shared_per_context_group": 4096, "heldout_per_switch": 2048},
        "no_scientific_changes": "Unchanged ErrorSampler, solver, weights, ranks and metrics. Only all generator seeds are offset. Redirect the output directory and suppress the shared coverage write.",
        "before": before,
    }
    with (OUT / "p4_policy.json").open("x") as f:
        json.dump(policy, f, indent=2)
    original_batch = s1_p4._batch
    original_sample = s1_p4.ErrorSampler.sample
    saved = []
    seed_ranges = []

    def shifted(gr, kind, contexts, seeds, sw_fn):
        shifted_seeds = seeds + OFFSET
        seed_ranges.append({"kind": kind, "contexts": list(contexts), "min": int(shifted_seeds.min()), "max": int(shifted_seeds.max()), "n": len(seeds)})
        return original_batch(gr, kind, contexts, shifted_seeds, sw_fn)

    def capture(sampler, ids, pos, tgt):
        result = original_sample(sampler, ids, pos, tgt)
        if len(saved) < 3:
            saved.append(result[0])
        print("sampled", len(ids), "sequences", flush=True)
        return result

    start = time.monotonic()
    with patch.object(s1_p4, "S1", OUT), patch.object(s1_p4, "_batch", shifted), patch.object(s1_p4.ErrorSampler, "sample", capture), patch.object(s1_p6, "update_coverage", lambda _: None):
        assert s1_p4.main(["--n", "2048", "--batch", "64"]) == 0
    fresh = json.loads((OUT / "P4_gram.json").read_text())
    old = json.loads(reference.read_text())
    comparisons = {}
    for key, metric in fresh["metrics"].items():
        a, b = old["metrics"][key]["value"], metric["value"]
        comparisons[key] = {"reference": a, "fresh": b, "delta": None if a is None or b is None else b-a}
    pairs = [(0, 1, "error_overlap_private_shared1_mean"), (0, 2, "error_overlap_private_shared2_mean"), (1, 2, "error_overlap_shared1_shared2_mean")]
    halves = []
    for half in (slice(0, 1024), slice(1024, 2048)):
        bases = [[s1_p4.basis(x[half, layer])["basis"] for layer in range(s1_p4.CFG.n_layer)] for x in saved]
        halves.append({key: float(np.mean([s1_p4.overlap(bases[a][l], bases[b][l]) for l in range(s1_p4.CFG.n_layer)])) for a, b, key in pairs})
    for _, _, key in pairs:
        comparisons[key]["fresh_half_means"] = [h[key] for h in halves]
        comparisons[key]["absolute_half_difference"] = abs(halves[0][key] - halves[1][key])
    after = hashes()
    assert before == after, "reviewed P4 source/reference changed during run"
    result = {"before": before, "after": after, "unchanged": True, "weights_agree": old["weights"] == fresh["weights"], "seed_ranges": seed_ranges, "comparisons": comparisons, "wall_seconds": time.monotonic()-start}
    assert result["weights_agree"]
    with (OUT / "p4_comparison.json").open("x") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
