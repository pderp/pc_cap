#!/usr/bin/env python3
"""CPU GRACE reference fixtures (S2-05a/b); no JAX adapter or clone modifications.

Generate in assets/envs/grace with the pinned legacy dependencies. --check
uses only NumPy. All output creation is exclusive; an existing run is never
overwritten. The reference editor is imported directly from the pinned clone.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
CLONE = ASSETS / "third_party" / "GRACE"
SNAPSHOT = ASSETS / "models" / "gpt2"
REVISION = "f674183f17a995d109e10ee6140d4c3e6d016115"
MODEL_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"
LAYER = "transformer.h[8].mlp.c_fc"
NEWLINE, EOS = 198, 50256


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def write_npz(path, arrays):
    if any(np.asarray(a).dtype.hasobject or not np.isfinite(a).all() for a in arrays.values()):
        raise ValueError("codebook arrays must be finite and non-object")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        np.savez(stream, **arrays)


def record(path):
    return {"path": str(Path(path).absolute()), "bytes": Path(path).stat().st_size,
            "sha256": sha256(path)}


def selected_cases(dev, s0):
    data = json.loads(Path(dev).read_text())
    if data["mode"] != "dev" or data["dataset"] != "zsre":
        raise ValueError("GRACE cases require the zsRE development manifest")
    excluded = {row["item_id"] for row in json.loads(Path(s0).read_text())["items"]}
    groups = {"single": [], "multi": []}
    used = set()
    for row in data["items"]:
        if row["item_id"] in excluded:
            continue
        answer = row["answer_ids"]
        if not row["prompt_ids"] or len(answer) < 2 or answer[-1] != NEWLINE:
            raise ValueError("expected complete answer IDs including newline")
        if row["item_id"] in used:
            raise ValueError("duplicate development item ID")
        used.add(row["item_id"])
        stratum = "single" if len(answer) - 1 == 1 else "multi"
        if len(groups[stratum]) < 10:
            groups[stratum].append({**row, "stratum": stratum,
                                    "lexical_answer_tokens": len(answer) - 1})
    if any(len(rows) != 10 for rows in groups.values()):
        raise ValueError("need ten non-S0 items in each answer-length stratum")
    return groups["single"] + groups["multi"]


def canonical(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def reference_inputs():
    catalog = json.loads((ROOT / "manifests/datasets.json").read_text())
    revision = subprocess.check_output(
        ["git", "-C", str(CLONE), "rev-parse", "HEAD"], text=True,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    ).strip()
    if revision != REVISION or catalog["grace"]["revision"] != REVISION:
        raise ValueError("GRACE revision differs from DATA-00 pin")
    if catalog["gpt2"]["revision"] != MODEL_REVISION:
        raise ValueError("GPT-2 revision differs from DATA-00 pin")
    inputs = {}
    for name in ("config.json", "model.safetensors", "tokenizer.json", "merges.txt", "vocab.json"):
        path = SNAPSHOT / name
        if sha256(path) != catalog["gpt2"]["files"]["models/gpt2/" + name]:
            raise ValueError("GPT-2 input hash mismatch: " + name)
        inputs["gpt2/" + name] = record(path)
    tracked = subprocess.check_output(
        ["git", "-C", str(CLONE), "ls-files"], text=True,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    ).splitlines()
    for name in tracked:
        inputs["grace/" + name] = record(CLONE / name)
    for name in ("zsre_dev.json", "s0_sample.json"):
        inputs[name] = record(ROOT / "manifests/dev" / name)
    return inputs


def load_base():
    import torch
    from safetensors.torch import load_file
    from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer

    config = GPT2Config.from_json_file(str(SNAPSHOT / "config.json"))
    if (config.n_layer, config.n_embd, config.vocab_size) != (12, 768, 50257):
        raise ValueError("expected pinned GPT-2 small architecture")
    config.use_cache = False
    config.resid_pdrop = config.embd_pdrop = config.attn_pdrop = 0.0
    model = GPT2LMHeadModel(config).float().eval()
    # Transformers 4.20 predates the safetensors loader. Load the same tensors
    # directly; only deterministic legacy attention mask buffers may be absent.
    tensors = load_file(str(SNAPSHOT / "model.safetensors"), device="cpu")
    state = {"transformer." + k: v for k, v in tensors.items()}
    state["lm_head.weight"] = tensors["wte.weight"]
    result = model.load_state_dict(state, strict=False)
    allowed = {f"transformer.h.{i}.attn.{name}" for i in range(12)
               for name in ("bias", "masked_bias")}
    if result.unexpected_keys or not set(result.missing_keys) <= allowed:
        raise ValueError(f"unexpected checkpoint load result: {result}")
    for name, value in model.named_parameters():
        if not torch.equal(value.detach(), state[name]) or value.dtype != torch.float32:
            raise ValueError("checkpoint parameter differs: " + name)
    tokenizer = GPT2Tokenizer(vocab_file=str(SNAPSHOT / "vocab.json"),
                             merges_file=str(SNAPSHOT / "merges.txt"))
    tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer, list(result.missing_keys)


def named_hash(named):
    h = hashlib.sha256()
    for name, tensor in named:
        a = tensor.detach().cpu().numpy()
        h.update(name.encode())
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


def codebook(adapter):
    arrays = {"keys": adapter.keys.detach().cpu().numpy().copy(),
              "values": adapter.values.detach().cpu().numpy().copy(),
              "radii": adapter.epsilons.detach().cpu().numpy().copy()}
    for i, labels in enumerate(adapter.key_labels):
        arrays[f"key_label_{i}"] = labels.detach().cpu().numpy().copy()
    return arrays


def book_hash(adapter):
    h = hashlib.sha256()
    for name, a in sorted(codebook(adapter).items()):
        h.update(name.encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


@contextmanager
def evaluation_state(adapter):
    """Preserve unused cold-init RNG draws and transient query bookkeeping."""
    import torch

    key_id = adapter.key_id
    chosen = adapter.chosen_key
    before = book_hash(adapter)
    try:
        with torch.random.fork_rng(devices=[]), torch.inference_mode():
            yield
    finally:
        adapter.key_id, adapter.chosen_key = key_id, chosen
        if book_hash(adapter) != before:
            raise RuntimeError("reference evaluation changed the codebook")


def make_tokens(item):
    import torch

    prompt, answer = item["prompt_ids"], item["answer_ids"]
    return {"input_ids": torch.tensor([prompt + answer], dtype=torch.long),
            "attention_mask": torch.ones((1, len(prompt) + len(answer)), dtype=torch.long),
            "labels": torch.tensor([[-100] * len(prompt) + answer], dtype=torch.long),
            "use_cache": False}


def greedy(model, tokenizer, prompt_ids):
    """Shared full-prefix, no-cache, newline/EOS decoder; no target argument."""
    import torch

    ids = list(prompt_ids)
    new = []
    stop = "max"
    for _ in range(32):
        output = model(input_ids=torch.tensor([ids]), use_cache=False)
        nxt = int(output.logits[0, -1].argmax())
        new.append(nxt)
        ids.append(nxt)
        if nxt in (NEWLINE, EOS):
            stop = "newline" if nxt == NEWLINE else "eos"
            break
    body = new[:-1] if stop != "max" else new
    return {"new_ids": new, "text": tokenizer.decode(body),
            "stopped_by": stop, "truncated": stop == "max"}


def evaluate(editor, adapter, tokenizer, item):
    with evaluation_state(adapter):
        adapter.key_id = len(item["prompt_ids"]) - 1
        decoded = greedy(editor.model, tokenizer, item["prompt_ids"])
        nll = float(editor.model(**make_tokens(item)).loss) * len(item["answer_ids"])
    return {"item_id": item["item_id"], "target": item["answer"], "greedy": decoded,
            "target_match": canonical(decoded["text"]) == canonical(item["answer"]),
            "teacher_forced_answer_nll": nll, "answer_tokens": len(item["answer_ids"])}


def check(manifest_path):
    m = json.loads(Path(manifest_path).read_text())
    if m["grace_revision"] != REVISION or m["model_revision"] != MODEL_REVISION:
        raise ValueError("unexpected reference revision")
    cases = selected_cases(Path(m["inputs"]["zsre_dev.json"]["path"]),
                           Path(m["inputs"]["s0_sample.json"]["path"]))
    if [c["item_id"] for c in cases] != [c["item_id"] for c in m["cases"]]:
        raise ValueError("case inventory differs from deterministic selection")
    for group in ("inputs", "files"):
        for name, rec in m[group].items():
            if record(rec["path"]) != rec:
                raise ValueError(f"hash/size mismatch: {group}/{name}")
    if m["environment_sha256"] != m["files"]["environment.json"]["sha256"]:
        raise ValueError("environment hash differs")
    if len(m["cases"]) != 20 or m["smoke_successes"] < 1:
        raise ValueError("incomplete cases or no successful smoke edit")
    for name, rec in m["files"].items():
        if name.endswith(".npz"):
            with np.load(rec["path"], allow_pickle=False) as z:
                n = len(z["keys"])
                if z["keys"].shape != (n, 768) or z["values"].shape != (n, 3072):
                    raise ValueError("codebook shape mismatch")
                if z["radii"].size != n:
                    raise ValueError("radius count mismatch")
                if len([k for k in z.files if k.startswith("key_label_")]) != n:
                    raise ValueError("label count mismatch")
                if any(not np.isfinite(z[k]).all() or z[k].dtype.hasobject for k in z.files):
                    raise ValueError("invalid codebook array")
                if any(z[k].dtype != np.float32 for k in ("keys", "values", "radii")):
                    raise ValueError("codebook must use fp32")
    final = json.loads(Path(m["files"]["sequence_final.json"]["path"]).read_text())
    if [r["item_id"] for r in final["evaluations"]] != [c["item_id"] for c in cases]:
        raise ValueError("final sequence evaluation inventory mismatch")
    for case in m["cases"]:
        for key in ("isolated_output", "isolated_codebook", "sequence_codebook"):
            if case[key] not in m["files"]:
                raise ValueError("missing referenced case file")
        result = json.loads(Path(m["files"][case["isolated_output"]]["path"]).read_text())
        if result["evaluation"]["item_id"] != case["item_id"]:
            raise ValueError("isolated evaluation item mismatch")
    return {"status": "verified", "tasks": ["S2-05a", "S2-05b"], "cases": 20,
            "single_token": 10, "multi_token": 10, "smoke_successes": m["smoke_successes"],
            "sequence_final_keys": final["codebook_entries"], "files": len(m["files"])}


def generate(args):
    os.environ.update({"CUDA_VISIBLE_DEVICES": "", "HF_HUB_OFFLINE": "1",
                       "TRANSFORMERS_OFFLINE": "1", "WANDB_MODE": "disabled",
                       "TOKENIZERS_PARALLELISM": "false"})
    import torch
    import transformers
    import yaml

    if torch.version.cuda is not None:
        raise ValueError("run the reference in the CPU-only auxiliary environment")
    if args.output.exists() or args.manifest.exists() or args.smoke.exists():
        raise FileExistsError("refusing to replace an existing reference run")
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)
    sys.path.insert(0, str(CLONE))
    from grace.editors.grace import GRACE

    started = time.monotonic()
    inputs = reference_inputs()
    cases = selected_cases(ROOT / "manifests/dev/zsre_dev.json", ROOT / "manifests/dev/s0_sample.json")
    config = {"device": "cpu", "experiment": {"task": "hallucination"},
              "model": {"inner_params": [LAYER + ".weight"], "name": "gpt2"},
              "editor": yaml.safe_load((CLONE / "grace/config/editor/grace.yaml").read_text())}
    base, tokenizer, missing_buffers = load_base()
    for item in cases:
        sep = "" if item["prompt"][-1:].isspace() else " "
        if tokenizer.encode(item["prompt"]) != item["prompt_ids"]:
            raise ValueError("prompt tokenization differs from shared manifest")
        if tokenizer.encode(sep + item["answer"].strip() + "\n") != item["answer_ids"]:
            raise ValueError("answer tokenization differs from shared manifest")
    base_hash = named_hash(list(base.named_parameters()))
    env = {"python": platform.python_version(), "executable": sys.executable,
           "torch": torch.__version__, "transformers": transformers.__version__,
           "numpy": np.__version__, "package_versions": dict(sorted(
               (d.metadata["Name"], d.version) for d in importlib.metadata.distributions())),
           "device": "cpu", "torch_cuda_build": torch.version.cuda, "threads": args.threads,
           "interop_threads": 1, "dtype": "float32", "deterministic_algorithms": True,
           "created_utc": datetime.now(timezone.utc).isoformat(), "grace_revision": REVISION,
           "config": config, "model_revision": MODEL_REVISION, "base_parameter_hash": base_hash,
           "checkpoint_loader": "safetensors tensors mapped directly into legacy GPT2LMHeadModel",
           "initialized_attention_buffers": missing_buffers,
           "layer_note": "No GPT-2-small default exists in clone; XL h[35]/48 maps by relative depth to h[8]/12.",
           "tokenization_note": "Shared development prompt IDs and answer IDs including newline; no upstream EOS suffix.",
           "evaluation_note": "Full-prefix decode, no KV cache, newline/EOS stop, fixed prompt key position; RNG/transient query fields restored.",
           "eviction": "disabled; exact unbounded reference codebook"}
    write_json(args.output / "environment.json", env)
    files = {"environment.json": record(args.output / "environment.json")}
    case_records, successes = [], 0

    def fresh(seed):
        torch.manual_seed(seed)
        model = copy.deepcopy(base)
        original = list(model.named_parameters())
        editor = GRACE(config, SimpleNamespace(model=model, tokenizer=tokenizer))
        adapter = model.transformer.h[8].mlp.c_fc
        return editor, adapter, original

    args.smoke.parent.mkdir(parents=True, exist_ok=True)
    with args.smoke.open("x") as smoke:
        smoke.write(json.dumps({"command": args.command, "environment": files["environment.json"],
                                "config": config, "smoke_ids": [c["item_id"] for c in cases[:5]]}) + "\n")
        smoke.flush()
        for i, item in enumerate(cases):
            editor, adapter, original = fresh(i)
            editor.edit(config, make_tokens(item), [])
            result = {"item_id": item["item_id"], "seed": i,
                      "losses": [float(loss) for loss in editor.losses],
                      "evaluation": evaluate(editor, adapter, tokenizer, item),
                      "codebook_entries": len(adapter.keys),
                      "base_unchanged": named_hash(original) == base_hash}
            if not result["base_unchanged"]:
                raise RuntimeError("GRACE modified a frozen base parameter")
            name = f"isolated/{i:02d}.json"
            book = f"isolated/{i:02d}.codebook.npz"
            write_json(args.output / name, result)
            write_npz(args.output / book, codebook(adapter))
            files[name], files[book] = record(args.output / name), record(args.output / book)
            case_records.append({"item_id": item["item_id"], "stratum": item["stratum"],
                                 "lexical_answer_tokens": item["lexical_answer_tokens"],
                                 "isolated_seed": i, "isolated_output": name,
                                 "isolated_codebook": book,
                                 "sequence_codebook": f"sequence/{i:02d}.codebook.npz"})
            print(json.dumps({"phase": "isolated", "completed": i + 1,
                              "target_match": result["evaluation"]["target_match"],
                              "wall_seconds": time.monotonic() - started}), flush=True)
            if i < 5:
                successes += int(result["evaluation"]["target_match"])
                smoke.write(json.dumps(result, allow_nan=False) + "\n")
                smoke.flush()
            if i == 4:
                smoke.write(json.dumps({"smoke_successes": successes, "attempted": 5}) + "\n")
                smoke.flush()
                if successes == 0:
                    raise RuntimeError("none of the five preselected smoke edits matched its target")
            del editor, adapter, original

    editor, adapter, original = fresh(0)
    sequence_updates = []
    for i, item in enumerate(cases):
        editor.edit(config, make_tokens(item), [])
        sequence_updates.append({"item_id": item["item_id"], "losses": [float(x) for x in editor.losses],
                                 "codebook_entries": len(adapter.keys)})
        name = f"sequence/{i:02d}.codebook.npz"
        write_npz(args.output / name, codebook(adapter))
        files[name] = record(args.output / name)
        print(json.dumps({"phase": "sequence", "completed": i + 1, "keys": len(adapter.keys),
                          "wall_seconds": time.monotonic() - started}), flush=True)
    final = {"seed": 0, "updates": sequence_updates, "codebook_entries": len(adapter.keys),
             "evaluations": [evaluate(editor, adapter, tokenizer, item) for item in cases],
             "base_unchanged": named_hash(original) == base_hash}
    if not final["base_unchanged"]:
        raise RuntimeError("sequential GRACE edits modified a base parameter")
    write_json(args.output / "sequence_final.json", final)
    files["sequence_final.json"] = record(args.output / "sequence_final.json")
    files["smoke_log"] = record(args.smoke)
    manifest = {"tasks": ["S2-05a", "S2-05b"], "status": "reference_generated",
                "grace_revision": REVISION, "model_revision": MODEL_REVISION,
                "inputs": inputs, "files": files, "cases": case_records, "command": args.command,
                "environment_sha256": files["environment.json"]["sha256"],
                "source_script": record(Path(__file__)), "smoke_successes": successes,
                "wall_seconds": time.monotonic() - started, "gpu_seconds": 0,
                "eviction": "disabled", "scope": "CPU source-reference fixtures; JAX adapter parity not yet tested"}
    write_json(args.manifest, manifest)
    return check(args.manifest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=ASSETS / "reference/grace")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifests/dev/grace_parity_cases.json")
    parser.add_argument("--smoke", type=Path, default=ROOT / "results/S2/grace_reference_smoke.txt")
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args(argv)
    if args.threads < 1:
        parser.error("--threads must be positive")
    args.command = [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:]]
    print(json.dumps(check(args.manifest) if args.check else generate(args), indent=2))


if __name__ == "__main__":
    main()
