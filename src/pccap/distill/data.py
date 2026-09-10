"""OpenWebText shard preparation and batch indexing (REG-00).

``prepare_shard`` rebuilds the sibling's ``openwebtext.bin`` byte-for-byte
(# reproduces hdpc/reproduction/prepare.py:21-91 ``build_shards``): documents in parquet row order,
GPT-2 BPE without special tokens, one EOS (50256) appended per document, the stream cut at
52,500,000 tokens, little-endian uint16, sha256 checked against the pinned value. Tokenization
uses the ``tokenizers`` runtime of the pinned GPT-2 snapshot (identical ids to the HF fast
tokenizer with ``add_special_tokens=False``; the snapshot is the same revision the sibling pins).

Batches: # reproduces hdpc/data.py:113-145 —
``needed = B·L; max_start = N − needed; start = (index · needed) % max(max_start, 1)``.
Training reads positions ``[0, total_steps · B · L)`` = ``[0, 50,001,920)`` only (no wrap), so the
tail ``tokens[50,001,920:]`` is untouched and serves as the held-out fidelity window (REG-03).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np

from pccap.distill import recipe as R

EOS_ID = 50256
VOCAB = 50257


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def download_parquet(out_dir: Path = R.OWT_DIR / "hf") -> Path:
    os.environ.setdefault("HF_HOME", str(Path(R.ASSETS_ROOT) / "hf_cache"))
    from huggingface_hub import hf_hub_download

    p = Path(hf_hub_download(R.OWT_REPO, R.OWT_FILE, repo_type="dataset", revision=R.OWT_REVISION, local_dir=str(out_dir)))
    got = file_sha256(p)
    if got != R.OWT_PARQUET_SHA256:
        raise RuntimeError(f"parquet sha256 {got} != pinned {R.OWT_PARQUET_SHA256}")
    return p


def iter_documents(parquet_path: Path, batch_rows: int = 1024):
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(parquet_path)
    for rb in pf.iter_batches(batch_size=batch_rows, columns=["text"]):
        for text in rb.column("text").to_pylist():
            yield text


def prepare_shard(parquet_path: Path | None = None, out_path: Path = R.SHARD_PATH, tokens: int = R.OWT_TOKENS,
                  expected_sha256: str | None = R.OWT_SHARD_SHA256, docs_per_batch: int = R.DOCS_PER_BATCH) -> dict:
    from pccap.bases.gpt2_jax import load_tokenizer

    parquet_path = parquet_path or download_parquet()
    tok = load_tokenizer()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".bin.partial")
    t0 = time.time()
    count = documents = scanned = 0
    pending: list[str] = []
    with open(tmp, "wb") as fh:
        def flush():
            nonlocal count, documents
            if not pending or count >= tokens:
                pending.clear()
                return
            encoded = tok.encode_batch(pending, add_special_tokens=False)
            pending.clear()
            for enc in encoded:
                if count >= tokens:
                    break
                ids = enc.ids + [EOS_ID]
                values = np.asarray(ids[: tokens - count])
                if values.min() < 0 or values.max() >= VOCAB:
                    raise ValueError("out-of-vocabulary token")
                values.astype("<u2").tofile(fh)
                count += len(values)
                documents += 1

        for text in iter_documents(parquet_path):
            scanned += 1
            if count >= tokens:
                break
            if not text:
                continue
            if not isinstance(text, str):
                raise ValueError("dataset text must be a string")
            pending.append(text)
            if len(pending) >= docs_per_batch:
                flush()
        flush()
    if count != tokens:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"dataset ended before {tokens} tokens: {count}")
    sha = file_sha256(tmp)
    if expected_sha256 is not None and sha != expected_sha256:
        raise RuntimeError(f"shard sha256 {sha} != pinned {expected_sha256} (kept at {tmp})")
    tmp.replace(out_path)
    return {"path": str(out_path), "tokens": count, "documents": documents, "documents_scanned": scanned,
            "sha256": sha, "seconds": time.time() - t0, "parquet": str(parquet_path)}


def load_shard(path: Path, min_tokens: int | None = None, vocab_size: int = VOCAB) -> np.ndarray:
    """# reproduces hdpc/data.py:69-100 (uint16 LE; a shard shorter than min_tokens is tiled)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size % 2:
        raise ValueError("incomplete uint16 token")
    raw = np.fromfile(path, dtype="<u2")
    if raw.size < 2:
        raise ValueError("fewer than two tokens")
    if int(raw.max()) >= vocab_size:
        raise ValueError("token id out of vocabulary")
    tokens = raw.astype(np.int32)
    if min_tokens is not None:
        tokens = tile_tokens(tokens, min_tokens)
    return tokens


def tile_tokens(tokens: np.ndarray, min_tokens: int) -> np.ndarray:
    repeats = max(1, math.ceil(min_tokens / tokens.size))
    return np.tile(tokens, repeats)[: max(min_tokens, tokens.size)]


def batch_start(numel: int, needed: int, index: int) -> int:
    if numel < needed:
        raise ValueError("token stream is too short for the requested batch")
    max_start = numel - needed
    return (index * needed) % max(max_start, 1)


def unlabeled_batch(tokens: np.ndarray, seq_len: int, batch_size: int, index: int) -> np.ndarray:
    needed = batch_size * seq_len
    s = batch_start(tokens.size, needed, index)
    return tokens[s: s + needed].reshape(batch_size, seq_len)


def labeled_batch(tokens: np.ndarray, seq_len: int, batch_size: int, index: int) -> tuple[np.ndarray, np.ndarray]:
    if seq_len < 2:
        raise ValueError("seq_len must be at least 2")
    needed = batch_size * (seq_len + 1)
    s = batch_start(tokens.size, needed, index)
    chunk = tokens[s: s + needed].reshape(batch_size, seq_len + 1)
    return np.ascontiguousarray(chunk[:, :-1]), np.ascontiguousarray(chunk[:, 1:])


def probe_token_count(r: R.Recipe) -> int:
    """# reproduces hdpc/train_distill.py:1152-1163 with the pinned probe arguments (probe/pc-consistency
    windows: seq 128, batch 1, 3 batches, start 1 and 4)."""
    largest_batch_tokens = max(r.eval_batch_size * (r.eval_seq_len + 1), 1 * (128 + 1), 1 * (128 + 1))
    largest_index = max(r.eval_start_index + r.eval_batches, 1 + 3, 4 + 3)
    return max(4096, 2 * (largest_index + 1) * largest_batch_tokens)


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Prepare the pinned OpenWebText shard under assets/")
    ap.add_argument("--parquet", type=Path, default=None, help="already-downloaded parquet (else download)")
    ap.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[3] / "manifests" / "datasets.json")
    args = ap.parse_args(argv)
    info = prepare_shard(args.parquet)
    print(json.dumps(info, indent=1))
    m = json.loads(args.manifest.read_text())
    m["openwebtext"] = {
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "status": "present",
        "url": [f"https://huggingface.co/datasets/{R.OWT_REPO}/resolve/{R.OWT_REVISION}/{R.OWT_FILE}"],
        "revision": R.OWT_REVISION, "licence": "OpenWebText: CC0 (dataset card)",
        "reason": "REG-00 only: the sibling's 50M-token distillation corpus (DEC-014)",
        "files": {"data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet": R.OWT_PARQUET_SHA256,
                  "data/raw/openwebtext/openwebtext.bin": info["sha256"],
                  "data/raw/openwebtext/distillation-probes.bin": file_sha256(R.PROBES_PATH) if R.PROBES_PATH.exists() else None},
        "tokens": info["tokens"], "documents": info["documents"], "documents_scanned": info["documents_scanned"],
        "recipe": "pccap.distill.data.prepare_shard (reproduces hdpc/reproduction/prepare.py build_shards)",
        "sibling_shard_sha256_matched": info["sha256"] == R.OWT_SHARD_SHA256,
    }
    args.manifest.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
