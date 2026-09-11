#!/usr/bin/env python3
"""DEC-020 conditioning control; immutable policy and reference inputs, CPU only."""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import time
from pathlib import Path

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1")
import pccap  # noqa: E402, F401

# isort: split
import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402

from pccap.baselines import grace_jax as gj  # noqa: E402
from pccap.baselines.grace_parity import evaluate, to_item  # noqa: E402
from pccap.bases import gpt2_jax as g  # noqa: E402
from pccap.bases.bp import BPBase  # noqa: E402
from pccap.data.tokenize import GPT2Tokenizer  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs/tasks/B4-S-sensitivity-policy.json"
STEPS = (1, 10, 100)


def associated_suffix(params, residual, projected, value, key_position, active, cfg, block):
    """Only reassociate the hook's two additions; no change across a nonlinearity."""
    selected = (jnp.arange(residual.shape[0]) < key_position)[:, None] & active
    projected = jnp.where(selected, value[None, :], projected)
    p = params["blocks"][block]
    linear_plus_bias = g.gelu_new(projected) @ p["c_proj2"]["w"] + p["c_proj2"]["b"]
    h = residual + jax.lax.optimization_barrier(linear_plus_bias)
    for layer in range(block + 1, cfg.n_layer):
        h = g.block(params["blocks"][layer], h, cfg)
    return h


@functools.partial(jax.jit, static_argnames=("cfg", "block", "steps"))
def optimize_associated(params, h, projected, value, targets, mask, key_position, active, cfg, block, steps, lr):
    """Original Adam expression; only the hook-suffix addition grouping changes."""
    def loss_fn(v):
        hidden = associated_suffix(params, h, projected, v, key_position, active, cfg, block)
        logits = g.head(params, hidden, cfg)
        losses = jax.nn.logsumexp(logits, axis=-1) - jnp.take_along_axis(logits, targets[:, None], axis=-1)[:, 0]
        return jnp.sum(losses * mask) / jnp.sum(mask)

    def body(carry, t):
        v, mean, variance = carry
        loss, grad = jax.value_and_grad(loss_fn)(v)
        mean = mean + np.float32(0.1) * (grad - mean)
        variance = np.float32(0.999) * variance + np.float32(0.001) * grad * grad
        c1 = jnp.asarray([1 - 0.9**i for i in range(1, steps + 1)], jnp.float32)[t]
        c2 = jnp.asarray([(1 - 0.999**i)**0.5 for i in range(1, steps + 1)], jnp.float32)[t]
        denominator = jnp.sqrt(variance) / c2 + np.float32(1e-8)
        v = v - (lr / c1) * mean / denominator
        return (v, mean, variance), loss

    (value, _, _), losses = jax.lax.scan(body, (value, jnp.zeros_like(value), jnp.zeros_like(value)), jnp.arange(steps))
    return value, losses


def compare_evaluation(a, b, tolerance):
    return {"greedy_ids_equal": a["new_ids"] == b["new_ids"],
            "nll_abs_difference": abs(a["answer_nll"] - b["answer_nll"]),
            "nll_pass": bool(np.isclose(a["answer_nll"], b["answer_nll"], **tolerance)),
            "baseline": a, "variant": b}


def verify_inputs():
    raw_policy = POLICY.read_bytes()
    policy = json.loads(raw_policy)
    manifest_path = ROOT / "manifests/dev/grace_parity_cases.json"
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == policy["case_manifest_sha256"]
    source = ROOT / "src/pccap/baselines/grace_jax.py"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == policy["source_sha256"], "candidate source changed after policy"
    manifest = json.loads(manifest_path.read_text())
    for group in ("inputs", "files"):
        for rec in manifest[group].values():
            path = Path(rec["path"])
            assert path.stat().st_size == rec["bytes"] and hashlib.sha256(path.read_bytes()).hexdigest() == rec["sha256"], str(path)
    return policy, raw_policy, manifest


def run(out):
    if out.exists():
        raise FileExistsError(out)
    policy, raw_policy, manifest = verify_inputs()
    out.parent.mkdir(parents=True, exist_ok=True)
    tolerance = policy["equality"]["answer_nll"]
    base, tokenizer = BPBase(), GPT2Tokenizer()
    base_before = base.checksum()
    raw = json.loads((ROOT / "manifests/dev/zsre_dev.json").read_text())
    by_id = {r["item_id"]: r for r in raw["items"]}
    previous = json.loads((ROOT / "results/S2/grace_jax/pc10.json").read_text())
    previous_gaps = {r["item_id"]: r["codebook"]["values"]["max_abs"] for r in previous["isolated"]}
    started = time.monotonic()
    records = []
    for index, case in enumerate(manifest["cases"]):
        item = to_item(by_id[case["item_id"]])
        learner = gj.GraceLearner(base, seed=case["isolated_seed"])
        prompt, answer = item.prompt_ids, item.answer_ids
        ids = np.concatenate([prompt, answer])
        padded, n = learner._padded(ids)
        with base.ledger.call("learning", partial_forwards=1, tokens=n) as rec:
            h, normalized, projected = gj.hook_prefix(base.params, jnp.asarray(padded), base.cfg, 8)
            rec.outputs = (h, normalized, projected)
        initial = gj.cold_uniform(learner.rng, 3072)
        labels = np.concatenate([np.full(len(prompt), -100, np.int64), answer.astype(np.int64)])
        _, active = learner._admit(np.asarray(normalized[len(prompt)-1]), labels, initial)
        assert active and len(learner.keys) == 1
        targets, mask = np.zeros(len(padded), np.int32), np.zeros(len(padded), np.float32)
        targets[len(prompt)-1:n-1] = answer
        mask[len(prompt)-1:n-1] = 1
        row = {"index": index, "item_id": item.item_id, "answer_tokens": len(answer),
               "cross_framework_step100_max_abs": previous_gaps[item.item_id], "steps": []}
        for steps in STEPS:
            values, losses, evals = {}, {}, {}
            for variant in ("baseline", "initial_perturbation", "associated_additions"):
                kernel = optimize_associated if variant == "associated_additions" else gj.optimize_value
                init = initial + np.float32(1e-7) if variant == "initial_perturbation" else initial
                with base.ledger.call("learning", partial_forwards=steps, reverses=steps, tokens=n*steps) as rec:
                    value, ls = kernel(base.params, h, projected, jnp.asarray(init), jnp.asarray(targets),
                                       jnp.asarray(mask), jnp.int32(len(prompt)-1), jnp.bool_(active),
                                       base.cfg, 8, steps, jnp.float32(1.0))
                    rec.outputs = (value, ls)
                assert np.isfinite(value).all() and np.isfinite(ls).all()
                values[variant], losses[variant] = np.asarray(value), float(ls[-1])
                learner.values[0] = values[variant]
                # Use the common unchanged decoder for all value states, isolating
                # the learned state from inference-kernel numerical differences.
                evals[variant] = evaluate(learner, item, tokenizer)
            step = {"step": steps, "loss_before_step_baseline": losses["baseline"], "variants": {}}
            for variant in ("initial_perturbation", "associated_additions"):
                delta = abs(losses[variant] - losses["baseline"])
                gap = float(np.max(np.abs(values[variant] - values["baseline"])))
                step["variants"][variant] = {
                    "value_max_abs": gap, "value_gap_ratio_to_cross_framework_final": gap / previous_gaps[item.item_id],
                    "loss_before_step_variant": losses[variant], "loss_abs_difference": delta,
                    "loss_relative_difference": delta / max(abs(losses["baseline"]), np.finfo(np.float32).tiny),
                    "summed_answer_loss_pass": bool(np.isclose(losses[variant]*len(answer), losses["baseline"]*len(answer), **tolerance)),
                    "evaluation": compare_evaluation(evals["baseline"], evals[variant], tolerance)}
            row["steps"].append(step)
        records.append(row)
        print(json.dumps({"case": index+1, "item_id": item.item_id,
                          "final_value_gaps": {k: v["value_max_abs"] for k, v in row["steps"][-1]["variants"].items()}}), flush=True)

    summaries = {}
    for variant in ("initial_perturbation", "associated_additions"):
        final = [r["steps"][-1]["variants"][variant] for r in records]
        all_steps = [s["variants"][variant] for r in records for s in r["steps"]]
        summaries[variant] = {
            "max_step100_value_gap": max(r["value_max_abs"] for r in final),
            "median_step100_value_gap": float(np.median([r["value_max_abs"] for r in final])),
            "median_case_ratio_to_cross_framework": float(np.median([r["value_gap_ratio_to_cross_framework_final"] for r in final])),
            "trajectory_comparisons": len(all_steps), "trajectory_passes": sum(r["summed_answer_loss_pass"] for r in all_steps),
            "final_greedy_passes": sum(r["evaluation"]["greedy_ids_equal"] for r in final),
            "final_nll_passes": sum(r["evaluation"]["nll_pass"] for r in final),
            "maximum_loss_absolute_difference": max(r["loss_abs_difference"] for r in all_steps),
            "maximum_loss_relative_difference": max(r["loss_relative_difference"] for r in all_steps)}
    association = summaries["associated_additions"]
    equal = association["trajectory_passes"] == 60 and association["final_greedy_passes"] == 20 and association["final_nll_passes"] == 20
    threshold = 0.1 * max(previous_gaps.values())
    if equal and association["max_step100_value_gap"] >= threshold:
        verdict = "divergence_class_reproduced"
    elif all(r["max_step100_value_gap"] <= 1e-3 for r in summaries.values()):
        verdict = "insensitive"
    else:
        verdict = "inconclusive_or_equality_failure"
    unchanged = base.checksum() == base_before
    assert unchanged and POLICY.read_bytes() == raw_policy
    result = {"task": "B4-S", "backend": jax.default_backend(), "policy": policy,
              "policy_sha256": hashlib.sha256(raw_policy).hexdigest(),
              "source_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "verdict": verdict, "association_gap_threshold": threshold, "summary": summaries,
              "cases": records, "base_unchanged": unchanged, "wall_seconds": time.monotonic()-started,
              "ledger": base.ledger.totals(), "gpu_seconds": 0,
              "interpretation": "Conditioning evidence only. Does not exclude a coexisting adapter defect; no oracle/tolerance changes."}
    with out.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(verdict, flush=True)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "results/S2/grace_jax/sensitivity.json")
    args = parser.parse_args(argv)
    return run(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
