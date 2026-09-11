#!/usr/bin/env python3
"""Diagnostic-only head reduction and stable-loss probes; no learner changes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1")
sys.dont_write_bytecode = True
import pccap  # noqa: E402,F401

# isort: split
import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402

from pccap.baselines.grace_jax import hook_prefix, hook_suffix  # noqa: E402
from pccap.bases import gpt2_jax as g  # noqa: E402
from pccap.bases.bp import BPBase  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    start = time.monotonic()
    spec = importlib.util.spec_from_file_location("localize", ROOT / "scripts/grace_gradient_localize.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    resources = driver.RESOURCES.with_name(driver.RESOURCES.name + "_independent_activations")
    base = BPBase()
    checksum = base.checksum()
    w = np.asarray(base.params["wte"])
    rows = []
    for index in (0, 1):
        with np.load(resources / f"{index:02d}.npz", allow_pickle=False) as f:
            a = {k: f[k] for k in f.files}
        cot = a["head__cotangent"]
        double_reference = cot.astype(np.float64) @ w.astype(np.float64)
        jax_result = np.asarray(jax.jit(lambda c: c @ base.params["wte"])(jnp.asarray(cot)))
        torch_result = a["head__vjp"]
        numpy_single = cot @ w
        head = {"torch_vs_float64": driver.compare(torch_result, double_reference),
                "jax_vs_float64": driver.compare(jax_result, double_reference),
                "numpy_float32_vs_float64": driver.compare(numpy_single, double_reference),
                "torch_vs_jax": driver.compare(torch_result, jax_result),
                "incoming_cotangent_l2": float(np.linalg.norm(cot)),
                "head_vjp_fp64_l2": float(np.linalg.norm(double_reference)),
                "forward_logits_range": [float(a["head__output"].min()), float(a["head__output"].max())]}
        ids, labels = a["ids"].astype(np.int32), a["labels"]
        prompt_len = int(np.sum(labels == -100))
        targets = np.zeros(len(ids), np.int32)
        mask = np.zeros(len(ids), np.float32)
        targets[prompt_len-1:len(ids)-1] = labels[prompt_len:]
        mask[prompt_len-1:len(ids)-1] = 1
        def loss_original(logits, targets=targets, mask=mask):
            v = jax.nn.logsumexp(logits, axis=-1) - jnp.take_along_axis(logits, jnp.asarray(targets)[:, None], axis=-1)[:, 0]
            return (v*jnp.asarray(mask)).sum()/mask.sum()
        def loss_logsoftmax(logits, targets=targets, mask=mask):
            v = -jnp.take_along_axis(jax.nn.log_softmax(logits, axis=-1), jnp.asarray(targets)[:, None], axis=-1)[:, 0]
            return (v*jnp.asarray(mask)).sum()/mask.sum()
        # Float64 analytic reference for the exact float32 logit matrix.
        x64 = a["loss__input"].astype(np.float64)
        centered = x64 - x64.max(axis=-1, keepdims=True)
        ex = np.exp(centered)
        probs = ex/ex.sum(axis=-1, keepdims=True)
        true_grad = probs.copy()
        true_grad[np.arange(len(ids)), targets] -= 1
        true_grad *= mask[:, None]/mask.sum()
        true_loss = float(((-centered[np.arange(len(ids)), targets] + np.log(ex.sum(axis=-1)))*mask).sum()/mask.sum())
        losses, whole = {}, {}
        h, _, projected = hook_prefix(base.params, jnp.asarray(ids), base.cfg, 8)
        for name, loss_fn in (("original", loss_original), ("log_softmax", loss_logsoftmax)):
            val, grad = jax.jit(jax.value_and_grad(loss_fn))(jnp.asarray(a["loss__input"]))
            losses[name] = {"loss_vs_torch": driver.compare(val, a["loss__output"]),
                            "gradient_vs_torch": driver.compare(grad, a["loss__vjp"]),
                            "loss_vs_float64": driver.compare(val, true_loss),
                            "gradient_vs_float64": driver.compare(grad, true_grad)}
            def value_loss(v, loss_fn=loss_fn, h=h, projected=projected, prompt_len=prompt_len):
                hidden = hook_suffix(base.params, h, projected, v, prompt_len-1, True, base.cfg, 8)
                return loss_fn(g.head(base.params, hidden, base.cfg))
            value, grad = jax.jit(jax.value_and_grad(value_loss))(jnp.asarray(a["value"]))
            whole[name] = {"loss_vs_torch": driver.compare(value, a["first_loss"]),
                           "gradient_vs_torch": driver.compare(grad, a["gradient"])}
        losses["torch"] = {"loss_vs_float64": driver.compare(a["loss__output"], true_loss),
                           "gradient_vs_float64": driver.compare(a["loss__vjp"], true_grad)}
        rows.append({"index": index, "head": head, "loss": losses, "whole_value_gradient": whole})
    assert base.checksum() == checksum
    report = {"cases": rows, "base_unchanged": True, "gpu_seconds": 0, "wall_seconds": time.monotonic()-start,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "qualification": "Float64 calculations are diagnostic NumPy references. Production remains JAX fp32. Neither test changes the preregistered sensitivity control or qualifies B4."}
    with (driver.OUT / "head_loss_probes.json").open("x") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
