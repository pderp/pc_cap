#!/usr/bin/env python3
"""Observe first-step GRACE boundaries and compare common-input CPU VJPs.

Original Torch is used only by the reference mode in the approved oracle environment.
This diagnostic neither changes the learner nor makes an eligibility decision.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1",
                  HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", WANDB_MODE="disabled")
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT.parent / "assets/reference/grace_diagnostics/gradient_localization_20260911"
OUT = ROOT / "results/S2/grace_jax/gradient_localization"
OLD = RESOURCES.parent / "first_steps_20260911"
INDICES = (0, 1)


def oracle():
    spec = importlib.util.spec_from_file_location("reference_oracle", ROOT / "scripts/grace_reference_oracle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(actual, expected):
    a, b = np.asarray(actual, np.float64), np.asarray(expected, np.float64)
    delta = a - b
    return {"max_abs": float(np.max(np.abs(delta))), "relative_l2": float(np.linalg.norm(delta) / max(np.linalg.norm(b), 1e-30)),
            "sign_disagreements": int(np.sum(np.sign(a) != np.sign(b))), "reference_l2": float(np.linalg.norm(b))}


def reference():
    import torch
    import torch.nn.functional as F
    import yaml

    start = time.monotonic()
    ref = oracle()
    assert not RESOURCES.exists()
    RESOURCES.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)
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
    config["editor"]["n_iter"] = 1
    reports = []
    for index in INDICES:
        torch.manual_seed(index)
        model = copy.deepcopy(base)
        editor = GRACE(config, SimpleNamespace(model=model, tokenizer=tok))
        blocks = model.transformer.h
        modules = {"hook_gelu": blocks[8].mlp.act, "hook_projection": blocks[8].mlp.c_proj}
        for layer in (9, 10, 11):
            block = blocks[layer]
            modules.update({f"block{layer}": block, f"block{layer}_ln1": block.ln_1,
                            f"block{layer}_attention": block.attn, f"block{layer}_ln2": block.ln_2,
                            f"block{layer}_fc": block.mlp.c_fc, f"block{layer}_gelu": block.mlp.act,
                            f"block{layer}_projection": block.mlp.c_proj})
        modules.update(ln_f=model.transformer.ln_f, head=model.lm_head)
        observed, prefix, arrays, handles = {}, {}, {}, []
        def capture(name, observed=observed):
            def hook(module, args, result):
                tensor = result[0] if isinstance(result, tuple) else result
                tensor.retain_grad()
                observed[name] = (args[0].detach().clone(), tensor.detach().clone(), tensor)
            return hook
        for name, module in modules.items():
            handles.append(module.register_forward_hook(capture(name)))
        def save_prefix(name, prefix=prefix):
            def hook(module, args, result):
                prefix[name] = result.detach().clone()
                if name == "normalized":
                    prefix["residual"] = args[0].detach().clone()
            return hook
        handles.append(blocks[8].ln_2.register_forward_hook(save_prefix("normalized")))
        handles.append(blocks[8].mlp.c_fc.layer.register_forward_hook(save_prefix("projected")))
        class TraceAdam(torch.optim.Adam):
            def step(self, closure=None, *, arrays=arrays):
                trainable = [p for group in self.param_groups for p in group["params"] if p.grad is not None]
                assert len(trainable) == 1
                value = trainable[0]
                arrays["value"] = value.detach().numpy().copy().reshape(-1)
                arrays["gradient"] = value.grad.detach().numpy().copy().reshape(-1)
                result = super().step(closure)
                arrays["after"] = value.detach().numpy().copy().reshape(-1)
                return result
        tokens = ref.make_tokens(cases[index])
        with patch.object(torch.optim, "Adam", TraceAdam):
            editor.edit(config, tokens, [])
        for handle in handles:
            handle.remove()
        replay = {}
        for name, module in modules.items():
            x, native_y, tensor = observed[name]
            cot = tensor.grad.detach().clone()
            inp = x.detach().requires_grad_(True)
            output = module(inp)
            y = output[0] if isinstance(output, tuple) else output
            vjp, = torch.autograd.grad(y, inp, cot)
            for key, value in (("input", x), ("output", native_y), ("cotangent", cot), ("vjp", vjp)):
                arrays[name + "__" + key] = value.detach().numpy()[0].copy()
            replay[name] = compare(y.detach().numpy(), native_y.numpy())
        # The residual fork and loss reduction are explicit functional boundaries.
        projected = observed["hook_projection"][1]
        residual = prefix["residual"]
        post_add = observed["block9"][0]
        # Loss gradient at block9 input includes both its residual and transformed paths.
        inp = post_add.detach().requires_grad_(True)
        hidden = inp
        for layer in (9, 10, 11):
            hidden = blocks[layer](hidden)[0]
        logits = model.lm_head(model.transformer.ln_f(hidden))
        loss = F.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]), tokens["labels"][:, 1:].reshape(-1))
        add_cot, = torch.autograd.grad(loss, inp)
        arrays["residual_add__input"] = np.stack([residual.numpy()[0], projected.numpy()[0]])
        arrays["residual_add__output"] = post_add.numpy()[0]
        arrays["residual_add__cotangent"] = add_cot.numpy()[0]
        arrays["residual_add__vjp"] = np.stack([add_cot.numpy()[0], add_cot.numpy()[0]])
        replay["residual_add"] = compare((residual + projected).numpy(), post_add.numpy())
        x = observed["head"][1].detach().requires_grad_(True)
        loss = F.cross_entropy(x[:, :-1].reshape(-1, x.shape[-1]), tokens["labels"][:, 1:].reshape(-1))
        grad, = torch.autograd.grad(loss, x)
        arrays.update(loss__input=x.detach().numpy()[0], loss__output=np.asarray(loss.detach().numpy()),
                      loss__cotangent=np.asarray(1.0, np.float32), loss__vjp=grad.numpy()[0],
                      labels=tokens["labels"].numpy()[0], ids=tokens["input_ids"].numpy()[0],
                      first_loss=np.asarray(editor.losses[0]))
        arrays.update({"prefix_" + key: value.numpy()[0] for key, value in prefix.items()})
        with np.load(OLD / f"{index:02d}.npz", allow_pickle=False) as old:
            trace_checks = {key: compare(arrays[new], old[key]) for new, key in
                            (("value", "before_1"), ("gradient", "gradient_1"), ("after", "after_1"))}
            assert all(v["max_abs"] == 0 for v in trace_checks.values())
        ref.write_npz(RESOURCES / f"{index:02d}.npz", arrays)
        reports.append({"index": index, "item_id": cases[index]["item_id"], "first_step_exact_to_prior_trace": trace_checks,
                        "replay_output": replay, "file": ref.record(RESOURCES / f"{index:02d}.npz")})
        print("reference case", index, "complete", flush=True)
        del editor, model
    ref.write_json(OUT / "reference.json", {"cases": reports, "torch": torch.__version__, "gpu_seconds": 0,
        "wall_seconds": time.monotonic() - start, "script_sha256": digest(Path(__file__))})


def candidate():
    import pccap  # noqa: F401

    # isort: split
    import jax
    import jax.numpy as jnp

    from pccap.baselines.grace_jax import hook_prefix, hook_suffix
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import BPBase

    start = time.monotonic()
    ref = oracle()
    base = BPBase()
    checksum = base.checksum()
    params, cfg = base.params, base.cfg
    reports = []
    for index in INDICES:
        with np.load(RESOURCES / f"{index:02d}.npz", allow_pickle=False) as file:
            a = {k: file[k] for k in file.files}
        blocks = params["blocks"]
        functions = {
            "hook_gelu": g.gelu_new,
            "hook_projection": lambda x, blocks=blocks: x @ blocks[8]["c_proj2"]["w"] + blocks[8]["c_proj2"]["b"],
            "ln_f": lambda x: g.layer_norm(x, params["ln_f"]["g"], params["ln_f"]["b"], cfg.eps),
            "head": lambda x: x @ params["wte"].T,
            "residual_add": lambda x: x[0] + x[1],
        }
        for layer in (9, 10, 11):
            p = blocks[layer]
            functions.update({
                f"block{layer}": lambda x, p=p: g.block(p, x, cfg),
                f"block{layer}_ln1": lambda x, p=p: g.layer_norm(x, p["ln_1"]["g"], p["ln_1"]["b"], cfg.eps),
                f"block{layer}_attention": lambda x, p=p: g.attention(p, x, cfg),
                f"block{layer}_ln2": lambda x, p=p: g.layer_norm(x, p["ln_2"]["g"], p["ln_2"]["b"], cfg.eps),
                f"block{layer}_fc": lambda x, p=p: x @ p["c_fc"]["w"] + p["c_fc"]["b"],
                f"block{layer}_gelu": g.gelu_new,
                f"block{layer}_projection": lambda x, p=p: x @ p["c_proj2"]["w"] + p["c_proj2"]["b"],
            })
        labels, ids = a["labels"], a["ids"].astype(np.int32)
        prompt_len = int(np.sum(labels == -100))
        targets = np.zeros(len(ids), np.int32)
        mask = np.zeros(len(ids), np.float32)
        targets[prompt_len-1:len(ids)-1] = labels[prompt_len:]
        mask[prompt_len-1:len(ids)-1] = 1
        def loss_fn(logits, targets=targets, mask=mask):
            losses = jax.nn.logsumexp(logits, axis=-1) - jnp.take_along_axis(logits, jnp.asarray(targets)[:, None], axis=-1)[:, 0]
            return jnp.sum(losses * jnp.asarray(mask)) / jnp.sum(mask)
        functions["loss"] = loss_fn
        components = {}
        for name, fn in functions.items():
            x, cot = jnp.asarray(a[name + "__input"]), jnp.asarray(a[name + "__cotangent"])
            def evaluate(x, cot, fn=fn):
                y, pullback = jax.vjp(fn, x)
                return y, pullback(cot)[0]
            y, vjp = jax.jit(evaluate)(x, cot)
            components[name] = {"output": compare(y, a[name + "__output"]), "vjp": compare(vjp, a[name + "__vjp"])}
        # Cross-replay reference prefix into the unchanged candidate suffix. Also
        # compare its actual padded execution shape with a true-length diagnostic.
        replay = []
        for padded in (False, True):
            length = g.bucket_len(len(ids)) if padded else len(ids)
            input_ids = np.pad(ids, (0, length-len(ids)))
            h, normalized, projected = hook_prefix(params, jnp.asarray(input_ids), cfg, 8)
            t = np.pad(targets, (0, length-len(ids)))
            m = np.pad(mask, (0, length-len(ids)))
            for prefix_kind in ("candidate", "reference"):
                rh = h if prefix_kind == "candidate" else jnp.asarray(np.pad(a["prefix_residual"], ((0, length-len(ids)), (0, 0))))
                rp = projected if prefix_kind == "candidate" else jnp.asarray(np.pad(a["prefix_projected"], ((0, length-len(ids)), (0, 0))))
                def whole(value, rh=rh, rp=rp, t=t, m=m, prompt_len=prompt_len):
                    hidden = hook_suffix(params, rh, rp, value, prompt_len-1, True, cfg, 8)
                    logits = g.head(params, hidden, cfg)
                    losses = jax.nn.logsumexp(logits, axis=-1) - jnp.take_along_axis(logits, jnp.asarray(t)[:, None], axis=-1)[:, 0]
                    return jnp.sum(losses * jnp.asarray(m)) / jnp.sum(m)
                loss, grad = jax.jit(jax.value_and_grad(whole))(jnp.asarray(a["value"]))
                replay.append({"padded": padded, "length": length, "prefix": prefix_kind,
                               "loss": compare(loss, a["first_loss"]), "gradient": compare(grad, a["gradient"])})
            if not padded:
                prefix_checks = {name: compare(value, a["prefix_" + name]) for name, value in
                                 (("residual", h), ("normalized", normalized), ("projected", projected))}
        replaced = a["hook_gelu__input"]
        selected = np.arange(len(ids)) < prompt_len-1
        replacement_exact = bool(np.array_equal(replaced[selected], np.broadcast_to(a["value"], replaced[selected].shape)))
        unchanged_exact = bool(np.array_equal(replaced[~selected], a["prefix_projected"][~selected]))
        assert replacement_exact and unchanged_exact
        assert np.array_equal(targets[mask.astype(bool)], labels[labels != -100])
        reports.append({"index": index, "tokens": len(ids), "prompt_tokens": prompt_len, "answer_tokens": int(mask.sum()),
                        "key_position": prompt_len-1, "replaced_positions": np.flatnonzero(selected).tolist(),
                        "replacement_values_exact": replacement_exact, "unselected_projection_exact": unchanged_exact,
                        "shifted_loss_targets_match": True, "prefix": prefix_checks,
                        "common_input_components": components, "whole_gradient_replay": replay})
        print("candidate case", index, json.dumps({"whole_gradient": replay, "components": components}), flush=True)
    assert base.checksum() == checksum
    ref.write_json(OUT / "candidate.json", {"cases": reports, "backend": jax.default_backend(), "jax": jax.__version__,
        "matmul_precision": str(jax.config.jax_default_matmul_precision), "base_unchanged": True,
        "gpu_seconds": 0, "wall_seconds": time.monotonic()-start,
        "sources": {str(p.relative_to(ROOT)): digest(p) for p in
                    (Path(__file__), ROOT / "src/pccap/baselines/grace_jax.py", ROOT / "src/pccap/bases/gpt2_jax.py")},
        "interpretation": "Diagnostic measurements only. No tolerance, optimizer, control or eligibility change."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("reference", "candidate"))
    args = parser.parse_args()
    (reference if args.mode == "reference" else candidate)()
