#!/usr/bin/env python3
"""REF-01: CPU-only Hugging Face GPT-2 oracles, stored outside the repository.

Run generation with assets/envs/ref-torch-cpu/bin/python. --check needs only
NumPy and can run in the project JAX environment. Existing output files are
never overwritten. The model and tokenizer load locally, without downloads.

The NPZ keys match tests/bases/test_bp_base.py. The greedy JSON matches
 tests/data/test_decode.py. No pccap runtime or reference repository is imported.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"
BANK_BLOCKS = (3, 7, 11)
LENGTHS = (1, 2, 3, 5, 8, 16, 64, 128)
MODEL_FILES = ("config.json", "model.safetensors", "tokenizer.json", "merges.txt", "vocab.json")
PROMPT_COUNT = 256
VOCAB = 50257
WIDTH = 768


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_new(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write("\n")


def npz_add(archive, name: str, value) -> None:
    """Stream one array into an NPZ instead of retaining all 256 logits tensors."""
    value = np.asarray(value)
    if value.dtype.hasobject or not np.isfinite(value).all():
        raise ValueError(f"nonfinite or object array: {name}")
    with archive.open(name + ".npy", "w", force_zip64=True) as stream:
        np.lib.format.write_array(stream, value, allow_pickle=False)


def source_inputs(snapshot: Path, source: Path, datasets: Path) -> dict:
    """Require the already-recorded DATA-00 hashes and the immutable model revision."""
    catalog = json.loads(datasets.read_text())
    if catalog["gpt2"]["revision"] != REVISION:
        raise ValueError("DATA-00 model revision differs from REF-01")
    records = {}
    for name in MODEL_FILES:
        path = snapshot / name
        expected = catalog["gpt2"]["files"]["models/gpt2/" + name]
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"model/tokenizer input hash mismatch: {path}")
        records[name] = {"path": str(path.absolute()), "sha256": actual}
    actual = sha256(source)
    expected = catalog["zsre"]["files"]["data/raw/zsre/zsre_mend_eval.json"]
    if actual != expected:
        raise ValueError("zsRE input hash mismatch")
    records["zsre_mend_eval.json"] = {"path": str(source.absolute()), "sha256": actual}
    records["datasets_manifest"] = {"path": str(datasets.absolute()), "sha256": sha256(datasets)}
    return records


def selected_prompts(source: Path) -> list[dict]:
    rows = json.loads(source.read_text())
    if not isinstance(rows, list) or len(rows) < PROMPT_COUNT:
        raise ValueError("zsRE source needs at least 256 records")
    selected = []
    for index, row in enumerate(rows[:PROMPT_COUNT]):
        prompt = row.get("src")
        if not isinstance(prompt, str) or not prompt:
            raise ValueError(f"missing/nontext source prompt at row {index}")
        selected.append({"source_index": index, "item_id": f"zsre_mend_eval:{index}",
                         "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                         "prompt": prompt})
    return selected


def capture_forward(model, input_ids, blocks=BANK_BLOCKS):
    """Capture post-block residuals by hooks, including pre-ln_f last block.

    Supported HF versions may return a tensor or a tuple from a block. Hooks
    copy immediately to isolate the saved value from any later in-place change.
    """
    import torch

    captured = {}
    handles = []

    def hook_for(name):
        def hook(_module, _inputs, output):
            tensor = output[0] if isinstance(output, (tuple, list)) else output
            if tensor.dtype != torch.float32 or tensor.device.type != "cpu":
                raise ValueError("reference activations must be fp32 CPU tensors")
            captured[name] = tensor.detach().cpu().numpy()[0].copy()
        return hook

    try:
        for block in blocks:
            handles.append(model.transformer.h[block].register_forward_hook(hook_for(block)))
        handles.append(model.transformer.ln_f.register_forward_hook(hook_for("ln_f")))
        with torch.inference_mode():
            output = model(input_ids=input_ids, use_cache=False, return_dict=True)
        logits = output.logits.detach().cpu().numpy()[0].copy()
    finally:
        for handle in handles:
            handle.remove()
    if set(captured) != {*blocks, "ln_f"}:
        raise ValueError("not all reference hook sites fired")
    return logits, captured


def greedy_case(model, tokenizer, prompt_ids, item) -> dict:
    import torch

    ids = torch.tensor(prompt_ids, dtype=torch.long).unsqueeze(0)
    sequences = {}
    for use_cache in (False, True):
        with torch.inference_mode():
            generated = model.generate(
                input_ids=ids, attention_mask=torch.ones_like(ids), do_sample=False,
                max_new_tokens=32, use_cache=use_cache,
                pad_token_id=tokenizer.eos_token_id, eos_token_id=tokenizer.eos_token_id,
            )
        sequences[use_cache] = generated[0, len(prompt_ids):].tolist()
    return {"item_id": item["item_id"], "source_index": item["source_index"],
            "prompt_ids": list(prompt_ids), "generated_ids_no_cache": sequences[False],
            "generated_ids_cache": sequences[True], "cache_agrees": sequences[False] == sequences[True]}


def generate(args) -> dict:
    # CPU-only auxiliary reference process. Never initialize CUDA or import JAX.
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch
    import transformers
    from tokenizers import Tokenizer
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started = time.monotonic()
    output = args.output.absolute()
    manifest_path = args.manifest.absolute()
    # Fail before expensive work if any existing artifact would need replacement.
    names = ("logits_256.npz", "lengths.npz", "greedy_8.json", "ref_env.json")
    for path in [manifest_path, *(output / name for name in names)]:
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"refusing to overwrite existing file: {path}")
    input_records = source_inputs(args.snapshot, args.source, args.datasets)
    prompts = selected_prompts(args.source)
    if args.threads < 1:
        raise ValueError("thread count must be positive")
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision("highest")
    model = AutoModelForCausalLM.from_pretrained(
        str(args.snapshot), local_files_only=True, dtype=torch.float32,
        attn_implementation="eager",
    ).to("cpu").eval()
    model.requires_grad_(False)
    config = model.config
    if (config.n_layer, config.n_embd, config.vocab_size) != (12, WIDTH, VOCAB):
        raise ValueError("REF-01 requires the specified full 12-layer GPT-2 small checkpoint")
    if any(parameter.dtype != torch.float32 or parameter.device.type != "cpu" for parameter in model.parameters()):
        raise ValueError("model is not uniformly fp32 on CPU")
    tokenizer = AutoTokenizer.from_pretrained(str(args.snapshot), local_files_only=True)
    raw_tokenizer = Tokenizer.from_file(str(args.snapshot / "tokenizer.json"))
    ids_by_prompt = []
    for item in prompts:
        ids = tokenizer.encode(item["prompt"], add_special_tokens=False)
        if ids != raw_tokenizer.encode(item["prompt"], add_special_tokens=False).ids:
            raise ValueError("HF and project tokenizer.json disagree on prompt boundaries")
        if not ids or len(ids) + 32 > config.n_positions:
            raise ValueError("prompt length violates model context budget")
        ids_by_prompt.append(ids)
    output.mkdir(parents=True, exist_ok=True)
    # ZIP_STORED avoids expensive float compression and permits a bounded RAM footprint.
    with zipfile.ZipFile(output / "logits_256.npz", "x", compression=zipfile.ZIP_STORED) as archive:
        npz_add(archive, "n_prompts", np.array(PROMPT_COUNT, dtype=np.int64))
        for index, ids in enumerate(ids_by_prompt):
            logits, hidden = capture_forward(model, torch.tensor([ids], dtype=torch.long))
            npz_add(archive, f"ids_{index}", np.asarray(ids, dtype=np.int32))
            npz_add(archive, f"logits_{index}", logits)
            for block in BANK_BLOCKS:
                npz_add(archive, f"hidden_{index}_{block}", hidden[block])
            npz_add(archive, f"post_ln_f_{index}", hidden["ln_f"])
            if index % 16 == 15:
                print(json.dumps({"phase": "forward", "completed": index + 1,
                                  "wall_seconds": time.monotonic() - started}), flush=True)
    greedy = {"policy": {"do_sample": False, "max_new_tokens": 32,
                         "eos_token_id": tokenizer.eos_token_id,
                         "newline_stopping": False,
                         "note": "Raw HF generation; consumers apply the common newline/EOS scoring policy."},
              "cases": []}
    for index in range(8):
        greedy["cases"].append(greedy_case(model, tokenizer, ids_by_prompt[index], prompts[index]))
        print(json.dumps({"phase": "greedy", "completed": index + 1,
                          "cache_agrees": greedy["cases"][-1]["cache_agrees"]}), flush=True)
    write_json_new(output / "greedy_8.json", greedy)
    rng = np.random.default_rng(0)
    with zipfile.ZipFile(output / "lengths.npz", "x", compression=zipfile.ZIP_STORED) as archive:
        npz_add(archive, "lengths", np.asarray(LENGTHS, dtype=np.int32))
        for length in LENGTHS:
            ids = rng.integers(0, VOCAB, size=length, dtype=np.int32)
            logits, _ = capture_forward(model, torch.tensor(ids[None], dtype=torch.long))
            npz_add(archive, f"ids_{length}", ids)
            npz_add(archive, f"logits_{length}", logits)
    artifact_records = {
        name: {"path": str(output / name), "sha256": sha256(output / name),
               "bytes": (output / name).stat().st_size} for name in names if name != "ref_env.json"
    }
    cpuinfo = Path("/proc/cpuinfo").read_text() if Path("/proc/cpuinfo").exists() else ""
    cpu_model = next((line.split(":", 1)[1].strip() for line in cpuinfo.splitlines()
                      if line.startswith("model name")), platform.processor())
    environment = {
        "python": platform.python_version(), "python_executable": os.sys.executable,
        "torch": torch.__version__, "transformers": transformers.__version__,
        "numpy": np.__version__, "threads": torch.get_num_threads(),
        "interop_threads": torch.get_num_interop_threads(), "cpu_model": cpu_model,
        "torch_cuda_build": torch.version.cuda, "device": "cpu", "dtype": "float32",
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "attention_implementation": config._attn_implementation,
        "wall_seconds": time.monotonic() - started, "gpu_seconds": 0,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "package_versions": dict(sorted((d.metadata["Name"], d.version)
                                        for d in importlib.metadata.distributions())),
        "files": artifact_records,
        "hash_note": "This file cannot contain its own hash; manifests/reference.json hashes ref_env.json.",
    }
    write_json_new(output / "ref_env.json", environment)
    artifact_records = {**artifact_records, "ref_env.json": {
        "path": str(output / "ref_env.json"), "sha256": sha256(output / "ref_env.json"),
        "bytes": (output / "ref_env.json").stat().st_size}}
    manifest = {
        "task": "REF-01", "status": "generated", "model_revision": REVISION,
        "source": "first 256 src records of zsre_mend_eval.json; no answer labels used",
        "inputs": input_records, "n_prompts": PROMPT_COUNT, "bank_blocks": list(BANK_BLOCKS),
        "hidden_convention": "post-block outputs, block 11 before ln_f; separate post_ln_f arrays",
        "vocab_size": VOCAB, "width": WIDTH, "lengths": list(LENGTHS), "length_seed": 0,
        "prompt_inventory": [{**{k: v for k, v in item.items() if k != "prompt"},
                              "tokens": len(ids_by_prompt[i])} for i, item in enumerate(prompts)],
        "artifacts": artifact_records,
        "script": {"path": str(Path(__file__).resolve()), "sha256": sha256(Path(__file__))},
        "reference_only": True,
        "scope_note": "Generation is not JAX/HF parity or scientific confirmation; existing consumers must verify comparisons separately.",
    }
    write_json_new(manifest_path, manifest)
    return check(manifest_path)


def _array(array, *, shape, dtype, label):
    if array.shape != shape or array.dtype != np.dtype(dtype) or not np.isfinite(array).all():
        raise ValueError(f"invalid shape/dtype/nonfinite values in {label}")


def check(manifest_path: Path) -> dict:
    """Read-only hash, inventory, shape, dtype, finite-value and decode checks."""
    manifest = json.loads(manifest_path.read_text())
    if manifest["model_revision"] != REVISION or manifest["n_prompts"] != PROMPT_COUNT:
        raise ValueError("unexpected oracle revision or prompt count")
    artifacts = manifest["artifacts"]
    if set(artifacts) != {"logits_256.npz", "lengths.npz", "greedy_8.json", "ref_env.json"}:
        raise ValueError("incomplete artifact inventory")
    for name, record in artifacts.items():
        path = Path(record["path"])
        if sha256(path) != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError(f"artifact hash/size mismatch: {name}")
    for name, record in manifest["inputs"].items():
        # The shared dataset registry may acquire unrelated entries after this run.
        # The immutable source files themselves must continue to match.
        if name == "datasets_manifest":
            continue
        if sha256(Path(record["path"])) != record["sha256"]:
            raise ValueError(f"reference input changed: {name}")
    inventory = manifest["prompt_inventory"]
    if len(inventory) != PROMPT_COUNT or [p["source_index"] for p in inventory] != list(range(PROMPT_COUNT)):
        raise ValueError("unexpected prompt inventory")
    with np.load(artifacts["logits_256.npz"]["path"], allow_pickle=False) as arrays:
        expected = {"n_prompts"}
        if int(arrays["n_prompts"]) != PROMPT_COUNT:
            raise ValueError("NPZ prompt count mismatch")
        for index, item in enumerate(inventory):
            n = item["tokens"]
            _array(arrays[f"ids_{index}"], shape=(n,), dtype="int32", label=f"ids_{index}")
            if np.any((arrays[f"ids_{index}"] < 0) | (arrays[f"ids_{index}"] >= VOCAB)):
                raise ValueError("prompt token outside vocabulary")
            _array(arrays[f"logits_{index}"], shape=(n, VOCAB), dtype="float32", label=f"logits_{index}")
            expected.update({f"ids_{index}", f"logits_{index}", f"post_ln_f_{index}"})
            for block in BANK_BLOCKS:
                _array(arrays[f"hidden_{index}_{block}"], shape=(n, WIDTH), dtype="float32", label=f"hidden_{index}_{block}")
                expected.add(f"hidden_{index}_{block}")
            _array(arrays[f"post_ln_f_{index}"], shape=(n, WIDTH), dtype="float32", label=f"post_ln_f_{index}")
        if set(arrays.files) != expected:
            raise ValueError("unexpected NPZ array inventory")
    with np.load(artifacts["lengths.npz"]["path"], allow_pickle=False) as arrays:
        if arrays["lengths"].tolist() != list(LENGTHS):
            raise ValueError("length fixture schedule mismatch")
        rng = np.random.default_rng(0)
        for length in LENGTHS:
            expected_ids = rng.integers(0, VOCAB, size=length, dtype=np.int32)
            if not np.array_equal(arrays[f"ids_{length}"], expected_ids):
                raise ValueError("length fixture seed/input mismatch")
            _array(arrays[f"logits_{length}"], shape=(length, VOCAB), dtype="float32", label=f"length_{length}")
    greedy = json.loads(Path(artifacts["greedy_8.json"]["path"]).read_text())
    if len(greedy["cases"]) != 8:
        raise ValueError("expected eight generation cases")
    with np.load(artifacts["logits_256.npz"]["path"], allow_pickle=False) as arrays:
        for index, case in enumerate(greedy["cases"]):
            if case["prompt_ids"] != arrays[f"ids_{index}"].tolist():
                raise ValueError("generation prompt differs from forward fixture")
            for key in ("generated_ids_no_cache", "generated_ids_cache"):
                ids = case[key]
                if not 1 <= len(ids) <= 32 or any(type(i) is not int or not 0 <= i < VOCAB for i in ids):
                    raise ValueError("invalid generated token sequence")
            if case["cache_agrees"] != (case["generated_ids_cache"] == case["generated_ids_no_cache"]):
                raise ValueError("cache agreement record mismatch")
    return {"task": "REF-01", "status": "verified", "prompts": PROMPT_COUNT,
            "lengths": list(LENGTHS), "generation_cases": 8,
            "cache_agreement_cases": sum(c["cache_agrees"] for c in greedy["cases"]),
            "artifact_bytes": sum(r["bytes"] for r in artifacts.values())}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--snapshot", type=Path, default=ASSETS / "models" / "gpt2")
    parser.add_argument("--source", type=Path, default=ASSETS / "data" / "raw" / "zsre" / "zsre_mend_eval.json")
    parser.add_argument("--datasets", type=Path, default=ROOT / "manifests" / "datasets.json")
    parser.add_argument("--output", type=Path, default=ASSETS / "reference" / "gpt2")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifests" / "reference.json")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args(argv)
    report = check(args.manifest) if args.check else generate(args)
    print(json.dumps(report, indent=2, allow_nan=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
