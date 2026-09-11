"""Measure the existing evaluator's window coverage, with no model or GPU work.

This is a diagnostic counterexample, not a replacement drift assay or a patch.
Only loss calculation is stubbed; production window selection and reported counts run.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1",
                  OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", HF_HUB_OFFLINE="1")
sys.dont_write_bytecode = True

import pccap  # noqa: E402,F401

# isort: split

import numpy as np  # noqa: E402

from pccap.harness.runs import Evaluator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class CoverageOnly(Evaluator):
    def _drift_nll(self, learner_or_predict):
        return 0.0  # No model forward; never interpret this stub as a measured NLL.


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scenario(n_tokens, *, explicit=False, requested=4096, window=128):
    ids = np.arange(n_tokens, dtype=np.int32)
    args = {"drift_positions": requested} if explicit else {}
    ev = CoverageOnly(None, None, [], ids, drift_window=window, **args)
    spans = [[int(w[0]), int(w[-1])] for w in ev.drift_windows]
    used = sum(len(w) for w in ev.drift_windows)
    return {
        "supplied_tokens": n_tokens, "explicit_count_argument": explicit,
        "requested_count": requested, "window": window, "windows": len(spans),
        "tokens_in_windows": used, "scored_prediction_positions": ev.drift(None)["positions"],
        "window_start_tokens_not_scored": len(spans), "trailing_tokens_outside_windows": n_tokens-used,
        "first_span": spans[0] if spans else None, "last_span": spans[-1] if spans else None,
        "nll_is_stubbed": True,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite evidence")
    inventory = json.loads((ROOT / "manifests/dev/lm_sets.json").read_text())
    entry = inventory["files"]["drift_tokens"]
    n_tokens = int(entry["shape"][0])
    resource = Path(entry["path"])
    assert sha(resource) == entry["sha256"]
    actual = np.load(resource, mmap_mode="r", allow_pickle=False)
    assert actual.shape == (n_tokens,)
    cases = {
        "current_stage_sample": scenario(4096+128),
        "whole_array_with_default_evaluator": scenario(n_tokens),
        "whole_array_with_explicit_evaluator_count": scenario(n_tokens, explicit=True, requested=n_tokens),
        "small_exact_window_control": scenario(16, explicit=True, requested=16, window=8),
        "small_tail_control": scenario(19, explicit=True, requested=19, window=8),
    }
    assert cases["current_stage_sample"]["scored_prediction_positions"] == 4064
    assert cases["whole_array_with_default_evaluator"]["scored_prediction_positions"] == 4064
    full = cases["whole_array_with_explicit_evaluator_count"]
    assert full["windows"] == 1931 and full["scored_prediction_positions"] == 245237
    assert full["trailing_tokens_outside_windows"] == 121
    assert cases["small_exact_window_control"]["scored_prediction_positions"] == 14
    assert cases["small_tail_control"]["trailing_tokens_outside_windows"] == 3
    paths = ["src/pccap/harness/runs.py", "src/pccap/harness/stage_s3.py",
             "src/pccap/harness/stage_s4.py", "src/pccap/harness/stage_s5.py",
             "docs/spec_defects.md", "manifests/dev/lm_sets.json", "manifests/frozen.json"]
    excerpts = []
    for path in paths[:4]:
        text = (ROOT / path).read_text()
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"Evaluator", "drift_sample"}:
                excerpts.append({"path": path, "line": node.lineno, "expression": ast.get_source_segment(text, node)})
    frozen_bytes = (ROOT / "manifests/frozen.json").read_bytes()
    frozen = json.loads(frozen_bytes)
    frozen_sha = hashlib.sha256(frozen_bytes).hexdigest()
    experiment_id = frozen["name"] + "-" + frozen_sha[:8]
    runs, skipped = [], []
    for path in sorted((ROOT / "results/S4" / experiment_id).rglob("config.json")):
        cfg = json.loads(path.read_text())
        if cfg.get("status") != "complete":
            skipped.append(str(path.parent.relative_to(ROOT)))
            continue
        assert cfg.get("experiment_id") == experiment_id
        assert cfg["frozen_manifest_sha256"] == frozen_sha
        metrics_path = path.with_name("metrics.json")
        record = json.loads(metrics_path.read_text())
        metrics = record["metrics"]
        runs.append({"path": str(path.parent.relative_to(ROOT)), "dataset": cfg["dataset"], "arm": cfg["arm"],
                     "realization": cfg["realization"], "perm": cfg["perm"],
                     "drift_positions": metrics["lm_drift_perplexity_ratio"]["n"],
                     "metrics_sha256": sha(metrics_path)})
    sd3 = next(line for line in (ROOT / "docs/spec_defects.md").read_text().splitlines() if line.startswith("| SD-3 |"))
    report = {
        "status": "coverage_gap_reproduced", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "approved_corpus": {"tokens": n_tokens, "path": str(resource), "sha256": entry["sha256"], "sd3": sd3},
        "scenarios": cases, "stage_expressions": excerpts, "completed_runs": runs, "noncomplete_runs_skipped": skipped,
        "sources": {p: sha(ROOT / p) for p in paths}, "gpu_seconds": 0, "model_weights_loaded": False,
        "interpretation": [
            "SD-3 authorizes the entire available validation split, not a one-million-token expansion.",
            "Passing a longer array alone still leaves the evaluator's 4096 default active.",
            "Passing the explicit full count admits 1931 full windows, but omits 121 trailing tokens and the first token of each window.",
            "Any remedy must declare input-token and scored-position denominators, tail/context policy, checkpoint coverage, identity and cost.",
            "No learner accuracy or NLL is measured by the stub, and no production code is changed.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps({"status": report["status"], "completed_runs": len(runs), "approved_tokens": n_tokens,
                      "current_positions": 4064, "explicit_full_window_positions": 245237, "gpu_seconds": 0}))


if __name__ == "__main__":
    main()
