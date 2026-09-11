#!/usr/bin/env python3
"""B4 CPU numerical trace; original reference and JAX candidate remain unchanged."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1",
                  HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", WANDB_MODE="disabled")
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
TRACE = ASSETS / "reference/grace_diagnostics/first_steps_20260911"
OUT = ROOT / "results/S2/grace_jax"
STEPS = (1, 10, 100)


def oracle():
    spec = importlib.util.spec_from_file_location("grace_reference_oracle", ROOT / "scripts/grace_reference_oracle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference():
    import copy
    from types import SimpleNamespace
    from unittest.mock import patch
    import torch
    import yaml
    ref = oracle()
    assert not TRACE.exists()
    TRACE.mkdir(parents=True)
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
    manifest = json.loads((ROOT / "manifests/dev/grace_parity_cases.json").read_text())
    summary = []
    for case_index in (0, 1):
        torch.manual_seed(case_index)
        model = copy.deepcopy(base)
        editor = GRACE(config, SimpleNamespace(model=model, tokenizer=tok))
        arrays = {}
        class TraceAdam(torch.optim.Adam):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.index = 0
            def step(self, closure=None):
                self.index += 1
                trainable = [p for group in self.param_groups for p in group["params"] if p.grad is not None]
                assert len(trainable) == 1
                value = trainable[0]
                if self.index in STEPS:
                    arrays[f"before_{self.index}"] = value.detach().numpy().copy().reshape(-1)
                    arrays[f"gradient_{self.index}"] = value.grad.detach().numpy().copy().reshape(-1)
                result = super().step(closure)
                if self.index in STEPS:
                    arrays[f"after_{self.index}"] = value.detach().numpy().copy().reshape(-1)
                return result
        with patch.object(torch.optim, "Adam", TraceAdam):
            editor.edit(config, ref.make_tokens(cases[case_index]), [])
        arrays["losses"] = np.asarray(editor.losses, np.float32)
        ref.write_npz(TRACE / f"{case_index:02d}.npz", arrays)
        bookpath = manifest["files"][manifest["cases"][case_index]["isolated_codebook"]]["path"]
        with np.load(bookpath, allow_pickle=False) as saved:
            difference = float(np.max(np.abs(saved["values"].reshape(-1) - arrays["after_100"])))
        summary.append({"index": case_index, "item_id": cases[case_index]["item_id"],
                        "reference_final_max_abs": difference, "trace": ref.record(TRACE / f"{case_index:02d}.npz")})
    ref.write_json(OUT / "trace_reference.json", {"backend": "cpu", "cases": summary,
                   "note": "Read-only original GRACE; optimizer subclass only observes before/gradient/after arrays."})


def candidate():
    import jax
    import jax.numpy as jnp
    from pccap.baselines.grace_jax import cold_uniform, hook_prefix, hook_suffix, optimize_value
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import BPBase
    ref = oracle()
    cases = ref.selected_cases(ROOT / "manifests/dev/zsre_dev.json", ROOT / "manifests/dev/s0_sample.json")
    base = BPBase()
    summary = []
    for index in (0, 1):
        item = cases[index]
        prompt, answer = item["prompt_ids"], item["answer_ids"]
        ids = np.asarray(prompt + answer, np.int32)
        padded = np.pad(ids, (0, g.bucket_len(len(ids)) - len(ids)))
        targets = np.zeros(len(padded), np.int32)
        mask = np.zeros(len(padded), np.float32)
        targets[len(prompt)-1:len(ids)-1] = answer
        mask[len(prompt)-1:len(ids)-1] = 1
        h, _, projected = hook_prefix(base.params, jnp.asarray(padded), base.cfg, 8)
        initial = cold_uniform(np.random.RandomState(index), 3072)
        def loss(value):
            hidden = hook_suffix(base.params, h, projected, value, len(prompt)-1, True, base.cfg, 8)
            logits = g.head(base.params, hidden, base.cfg)
            losses = jax.nn.logsumexp(logits, axis=-1)-jnp.take_along_axis(logits, jnp.asarray(targets)[:, None], axis=-1)[:, 0]
            return jnp.sum(losses*jnp.asarray(mask))/jnp.sum(mask)
        first_loss, gradient = jax.jit(jax.value_and_grad(loss))(jnp.asarray(initial))
        with np.load(TRACE / f"{index:02d}.npz", allow_pickle=False) as trace:
            diff = np.asarray(gradient)-trace["gradient_1"]
            result = {"index": index, "item_id": item["item_id"],
                      "initial_value_exact": bool(np.array_equal(initial, trace["before_1"])),
                      "first_loss_jax": float(first_loss), "first_loss_reference": float(trace["losses"][0]),
                      "first_gradient_max_abs": float(np.max(np.abs(diff))),
                      "first_gradient_relative_l2": float(np.linalg.norm(diff)/np.linalg.norm(trace["gradient_1"])),
                      "gradient_sign_disagreements": int(np.sum(np.sign(gradient)!=np.sign(trace["gradient_1"]))),
                      "steps": []}
            for steps in STEPS:
                value, losses = optimize_value(base.params, h, projected, jnp.asarray(initial), jnp.asarray(targets),
                                               jnp.asarray(mask), jnp.int32(len(prompt)-1), jnp.bool_(True),
                                               base.cfg, 8, steps, jnp.float32(1.0))
                result["steps"].append({"step": steps,
                     "value_max_abs": float(np.max(np.abs(np.asarray(value)-trace[f"after_{steps}"]))),
                     "loss_before_step_jax": float(losses[-1]), "loss_before_step_reference": float(trace["losses"][steps-1])})
            summary.append(result)
    ref.write_json(OUT / "trace_comparison.json", {"backend": jax.default_backend(), "cases": summary,
        "candidate_source_sha256": hashlib.sha256((ROOT / "src/pccap/baselines/grace_jax.py").read_bytes()).hexdigest(),
        "scope": "Two predetermined cases: first case and largest isolated value mismatch; no parameter/tolerance changes."})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("reference", "candidate"))
    args = parser.parse_args()
    (reference if args.mode == "reference" else candidate)()
