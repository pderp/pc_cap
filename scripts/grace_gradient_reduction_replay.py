#!/usr/bin/env python3
"""Diagnostic counterfactual head/loss cotangents on the fixed original GRACE graph."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1",
                  HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", WANDB_MODE="disabled")
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT.parent / "assets/reference/grace_diagnostics/gradient_localization_20260911_independent_activations"
OUT = ROOT / "results/S2/grace_jax/gradient_localization"


def driver():
    spec = importlib.util.spec_from_file_location("diagnostic", ROOT / "scripts/grace_gradient_localize.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference():
    import copy

    import torch
    import yaml
    start = time.monotonic()
    diag = driver()
    ref = diag.oracle()
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    sys.path.insert(0, str(ref.CLONE))
    from grace.editors.grace import GRACE
    base, tok, _ = ref.load_base()
    cases = ref.selected_cases(ROOT / "manifests/dev/zsre_dev.json", ROOT / "manifests/dev/s0_sample.json")
    config = {"device": "cpu", "experiment": {"task": "hallucination"},
              "model": {"inner_params": [ref.LAYER + ".weight"], "name": "gpt2"},
              "editor": yaml.safe_load((ref.CLONE / "grace/config/editor/grace.yaml").read_text())}
    rows = []
    for index in (0, 1):
        torch.manual_seed(index)
        model = GRACE(config, SimpleNamespace(model=copy.deepcopy(base), tokenizer=tok)).model
        adapter = model.transformer.h[8].mlp.c_fc
        tokens = ref.make_tokens(cases[index])
        adapter.key_id = (tokens["labels"] == -100).sum()-1
        adapter.training, adapter.iter, adapter.edit_label = True, 0, tokens["labels"]
        captured = {}
        def hook(module, args, output, captured=captured):
            captured["normalized"] = output
        handle = model.transformer.ln_f.register_forward_hook(hook)
        output = model(**tokens)
        handle.remove()
        normalized, value = captured["normalized"], adapter.values
        native_grad, = torch.autograd.grad(output.loss, value, retain_graph=True)
        native_head_cot, = torch.autograd.grad(output.loss, normalized, retain_graph=True)
        native_logits_cot, = torch.autograd.grad(output.loss, output.logits, retain_graph=True)
        with np.load(RESOURCES / f"{index:02d}.npz", allow_pickle=False) as old:
            assert np.array_equal(native_grad.detach().numpy().reshape(-1), old["gradient"])
            assert np.array_equal(output.logits.detach().numpy()[0], old["loss__input"])
        x = output.logits.detach().numpy().astype(np.float64)
        centered = x-x.max(axis=-1, keepdims=True)
        probs = np.exp(centered)
        probs /= probs.sum(axis=-1, keepdims=True)
        labels = tokens["labels"].numpy()[0]
        n_prompt = int(np.sum(labels == -100))
        true_cot = np.zeros_like(probs)
        positions = np.arange(n_prompt-1, len(labels)-1)
        true_cot[:, positions] = probs[:, positions]
        true_cot[0, positions, labels[n_prompt:]] -= 1
        true_cot /= len(positions)
        w64 = model.lm_head.weight.detach().numpy().astype(np.float64)
        head64_native_loss = native_logits_cot.detach().numpy().astype(np.float64) @ w64
        head64_loss64 = true_cot @ w64
        loss64_head_native, = torch.autograd.grad(output.logits, normalized,
                                                torch.from_numpy(true_cot.astype(np.float32)), retain_graph=True)
        cotangents = {"native": native_head_cot, "loss64_only": loss64_head_native,
                      "head64_only": torch.from_numpy(head64_native_loss.astype(np.float32)),
                      "head64_and_loss64": torch.from_numpy(head64_loss64.astype(np.float32))}
        arrays = {"value": value.detach().numpy().reshape(-1)}
        checks = {}
        for name, cot in cotangents.items():
            result, = torch.autograd.grad(normalized, value, cot, retain_graph=True)
            arrays[name] = result.detach().numpy().reshape(-1)
            checks[name] = diag.compare(arrays[name], native_grad.detach().numpy().reshape(-1))
        assert checks["native"]["max_abs"] == 0
        ref.write_npz(RESOURCES / f"reduction_{index:02d}.npz", arrays)
        rows.append({"index": index, "native_first_gradient_exact": True, "counterfactual_gradient_vs_native": checks,
                     "file": ref.record(RESOURCES / f"reduction_{index:02d}.npz")})
    ref.write_json(OUT / "reduction_replay_reference.json", {"cases": rows, "gpu_seconds": 0,
                    "wall_seconds": time.monotonic()-start, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


def candidate():
    import pccap  # noqa: F401

    # isort: split
    import jax
    import jax.numpy as jnp

    from pccap.baselines.grace_jax import hook_prefix, hook_suffix
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import BPBase

    start = time.monotonic()
    diag = driver()
    ref = diag.oracle()
    base = BPBase()
    checksum = base.checksum()
    rows = []
    for index in (0, 1):
        with np.load(RESOURCES / f"{index:02d}.npz", allow_pickle=False) as f:
            a = {k: f[k] for k in f.files}
        with np.load(RESOURCES / f"reduction_{index:02d}.npz", allow_pickle=False) as f:
            b = {k: f[k] for k in f.files}
        ids, labels = a["ids"].astype(np.int32), a["labels"]
        prompt_len = int(np.sum(labels == -100))
        t = np.zeros(len(ids), np.int32)
        m = np.zeros(len(ids), np.float32)
        t[prompt_len-1:len(ids)-1] = labels[prompt_len:]
        m[prompt_len-1:len(ids)-1] = 1
        h, _, projected = hook_prefix(base.params, jnp.asarray(ids), base.cfg, 8)
        def loss(v, h=h, projected=projected, prompt_len=prompt_len, t=t, m=m):
            hidden = hook_suffix(base.params, h, projected, v, prompt_len-1, True, base.cfg, 8)
            logits = g.head(base.params, hidden, base.cfg)
            losses = jax.nn.logsumexp(logits, axis=-1)-jnp.take_along_axis(logits, jnp.asarray(t)[:, None], axis=-1)[:, 0]
            return (losses*jnp.asarray(m)).sum()/m.sum()
        gradient = jax.jit(jax.grad(loss))(jnp.asarray(b["value"]))
        rows.append({"index": index, "jax_vs_backward_replays": {name: diag.compare(gradient, value)
                     for name, value in b.items() if name != "value"}})
    assert base.checksum() == checksum
    ref.write_json(OUT / "reduction_replay_candidate.json", {"cases": rows, "gpu_seconds": 0,
        "base_unchanged": True, "wall_seconds": time.monotonic()-start,
        "qualification": "Two fixed cases; diagnostic cotangents only, no optimizer trajectory or eligibility change."})
    print(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("reference", "candidate"))
    args = parser.parse_args()
    (reference if args.mode == "reference" else candidate)()
