"""Pure development-manifest validation and a restricted read-only file adapter (R1-67).
No model, GPU, output writes or confirmation admission. Call before lease/base construction.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from pccap.contracts import EditItem
from pccap.data.tokenize import tokenize_pair

DATASETS = frozenset({"zsre", "counterfact", "mquake"})


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _pin(value, name):
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise ValueError("invalid SHA-256: " + name)
    return value


def _canonical(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _strings(value, name, minimum=1, unique=True):
    if (
        not isinstance(value, list)
        or len(value) < minimum
        or any(not isinstance(x, str) or not x.strip() for x in value)
    ):
        raise ValueError("invalid text inventory: " + name)
    if unique and len(set(value)) != len(value):
        raise ValueError("duplicate text: " + name)
    return value


def _tokens(value, name):
    if (
        not isinstance(value, list)
        or not value
        or any(type(x) is not int or not 0 <= x < 2**31 for x in value)
    ):
        raise ValueError("invalid token vector: " + name)
    return value


def source_requirements(doc):
    """Return source-key -> digest for supported source/derived receipt forms."""
    refs = {}
    for field in ("source", "sources_sha256", "derived_from"):
        value = doc.get(field)
        if value is None:
            continue
        if not isinstance(value, dict) or not value:
            raise ValueError("invalid source binding: " + field)
        if "path" in value or "sha256" in value:
            if not isinstance(value.get("path"), str) or not value["path"]:
                raise ValueError("source path required")
            values = {value["path"]: value.get("sha256")}
        else:
            values = value
        for key, h in values.items():
            if not isinstance(key, str) or not key:
                raise ValueError("source key required")
            _pin(h, key)
            if key in refs and refs[key] != h:
                raise ValueError("conflicting source binding")
            refs[key] = h
    return refs


@dataclass(frozen=True)
class DevelopmentSelection:
    items: tuple[EditItem, ...]
    unrelated_prompts: tuple[str, ...]
    receipt: dict


def validate_development_manifest(
    raw,
    *,
    dataset,
    n,
    seed,
    tokenizer,
    expected_sha256,
    tokenizer_sha256,
    source_blobs=None,
    min_unrelated=50,
    excluded_item_ids=(),
):
    """Validate bytes and supplied bound source bytes without filesystem/model side effects.
    The expected manifest/tokenizer digests are caller pins, not computed authorizations.
    Same sorted PCG64-permutation subset as the previous override; no shortfall fallback.
    """
    if not isinstance(raw, bytes) or _hash(raw) != _pin(expected_sha256, "manifest"):
        raise ValueError("manifest identity mismatch")
    if dataset not in DATASETS or type(n) is not int or n <= 0 or type(seed) is not int or seed < 0:
        raise ValueError("dataset, positive count and nonnegative integer seed required")
    if type(min_unrelated) is not int or min_unrelated < 1:
        raise ValueError("positive unrelated inventory size required")
    if tokenizer.file_sha256() != _pin(tokenizer_sha256, "tokenizer"):
        raise ValueError("tokenizer identity mismatch")
    doc = json.loads(raw)
    if not isinstance(doc, dict) or doc.get("mode") != "dev" or doc.get("dataset") != dataset:
        raise ValueError("development mode and matching dataset required")
    sources = source_blobs or {}
    source_docs = []
    refs = source_requirements(doc)
    for key, h in refs.items():
        data = sources.get(key)
        if not isinstance(data, bytes) or _hash(data) != h:
            raise ValueError("source identity mismatch: " + key)
        src = json.loads(data)
        if not isinstance(src, dict) or src.get("mode") not in (None, "dev"):
            raise ValueError("source must be development/prepared metadata")
        source_docs.append(src)
    rows = doc.get("items")
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty item inventory required")
    # If a bound source contains records, require unchanged core support in at least one source.
    core = ("item_id", "prompt", "answer", "prompt_ids", "answer_ids", "digest", "fact_id")
    source_rows = [r for d in source_docs for r in d.get("items", []) if isinstance(r, dict)]
    by_id = {}
    for row in source_rows:
        by_id.setdefault(row.get("item_id"), []).append(row)
    seen = {key: set() for key in ("item_id", "fact_id", "subject", "digest")}
    checked = []
    for row in rows:
        if not isinstance(row, dict) or row.get("dataset") != dataset:
            raise ValueError("item dataset mismatch")
        for key in ("item_id", "fact_id", "subject", "prompt", "answer"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError("missing item field: " + key)
        if row["answer"] != row["answer"].strip():
            raise ValueError("canonical answer must be stripped")
        expected_digest = (
            hashlib.sha256(f"{row['item_id']}|{row['prompt']}|{row['answer']}".encode())
            .digest()[:16]
            .hex()
        )
        if row.get("digest") != expected_digest:
            raise ValueError("item digest mismatch")
        for key in seen:
            value = _canonical(row[key]) if key == "subject" else row[key]
            if value in seen[key]:
                raise ValueError("duplicate item identity: " + key)
            seen[key].add(value)
        for key in ("aliases", "paraphrases", "locality_prompts"):
            _strings(row.get(key), key)
        if "locality_answers" in row and len(
            _strings(row["locality_answers"], "locality_answers", unique=False)
        ) != len(row["locality_prompts"]):
            raise ValueError("locality prompt/answer length mismatch")
        for key in ("prompt_ids", "answer_ids"):
            _tokens(row.get(key), key)
        pair = tokenize_pair(tokenizer, row["prompt"], row["answer"])
        if (
            pair.excluded
            or pair.prompt_ids.tolist() != row["prompt_ids"]
            or pair.answer_ids.tolist() != row["answer_ids"]
        ):
            raise ValueError("tokenized support mismatch")
        if "answer_tokens" in row and (
            type(row["answer_tokens"]) is not int or row["answer_tokens"] != len(pair.answer_ids)
        ):
            raise ValueError("answer token count mismatch")
        for text in row["paraphrases"] + row["locality_prompts"]:
            if not len(tokenizer.encode(text)):
                raise ValueError("empty query tokens")
        if source_rows and not any(
            all(row.get(k) == r.get(k) for k in core) for r in by_id.get(row["item_id"], [])
        ):
            raise ValueError("support differs from bound source")
        checked.append(row)
    excluded = list(excluded_item_ids)
    if any(not isinstance(x, str) or not x for x in excluded) or len(set(excluded)) != len(
        excluded
    ):
        raise ValueError("unique explicit excluded IDs required")
    pool = [r for r in checked if r["item_id"] not in set(excluded)]
    if n > len(pool):
        raise ValueError("requested count exceeds eligible development inventory")
    unrelated = _strings(doc.get("unrelated_prompts"), "unrelated_prompts", min_unrelated)
    unrelated_tokens = [tuple(int(t) for t in tokenizer.encode(p)) for p in unrelated]
    if any(not t for t in unrelated_tokens) or len(set(unrelated_tokens)) != len(unrelated_tokens):
        raise ValueError("empty or duplicate tokenized unrelated queries")
    rng = np.random.default_rng(seed)
    indices = sorted(int(i) for i in rng.permutation(len(pool))[:n])
    selected = [pool[i] for i in indices]
    answer_queries = {
        tuple(int(t) for t in tokenizer.encode(p))
        for r in selected
        for p in [r["prompt"], *r["paraphrases"]]
    }
    if answer_queries & set(unrelated_tokens):
        raise ValueError("unrelated inventory overlaps selected edit/paraphrase queries")
    items = tuple(
        EditItem(
            item_id=r["item_id"],
            digest=bytes.fromhex(r["digest"]),
            prompt=r["prompt"],
            answer=r["answer"],
            aliases=list(r["aliases"]),
            paraphrases=list(r["paraphrases"]),
            locality_prompts=list(r["locality_prompts"]),
            prompt_ids=np.asarray(r["prompt_ids"], np.int32),
            answer_ids=np.asarray(r["answer_ids"], np.int32),
            dataset=dataset,
            fact_id=r["fact_id"],
        )
        for r in selected
    )
    receipt = {
        "schema_version": 1,
        "mode": "dev",
        "manifest_sha256": expected_sha256,
        "tokenizer_sha256": tokenizer_sha256,
        "source_bindings_sha256": refs,
        "dataset": dataset,
        "requested_n": n,
        "available_n": len(pool),
        "manifest_n": len(rows),
        "seed": seed,
        "rng": "NumPy default_rng (PCG64); sorted selected indices",
        "numpy_version": np.__version__,
        "selected_item_ids": [r["item_id"] for r in selected],
        "selected_fact_ids": [r["fact_id"] for r in selected],
        "selected_subjects": [_canonical(r["subject"]) for r in selected],
        "excluded_item_ids": excluded,
        "unrelated_prompts": list(unrelated),
        "unrelated_prompt_sha256": [_hash(p.encode()) for p in unrelated],
        "unrelated_n": len(unrelated),
        "scope": "development only; no final population admission",
    }
    return DevelopmentSelection(items, tuple(unrelated), receipt)


def load_development_manifest(
    path,
    *,
    dev_root,
    dataset,
    n,
    seed,
    tokenizer,
    expected_sha256,
    tokenizer_sha256,
    source_paths=None,
    min_unrelated=50,
    excluded_item_ids=(),
):
    """Read only a manifest beneath the supplied dev root and bound metadata beneath its sibling
    revision_v1 root. Resolve symlinks and reject other paths before opening any file.
    Named derived_from aliases require explicit source_paths; no filename guessing.
    """
    root = Path(dev_root).resolve(strict=True)

    def allowed(p, roots):
        p = Path(p).resolve(strict=True)
        if not p.is_file() or not any(p.is_relative_to(r) for r in roots):
            raise ValueError("path outside allowed development metadata roots")
        return p

    p = Path(path)
    if not p.is_absolute():
        p = root / p
    p = allowed(p, (root,))
    raw = p.read_bytes()
    if _hash(raw) != _pin(expected_sha256, "manifest"):
        raise ValueError("manifest identity mismatch")
    doc = json.loads(raw)
    if doc.get("mode") != "dev" or doc.get("dataset") != dataset:
        raise ValueError("development mode and matching dataset required")
    mappings = source_paths or {}
    blobs = {}
    roots = (root, root.parent / "revision_v1")
    for key, h in source_requirements(doc).items():
        ref = mappings.get(key, key)
        ref = Path(ref)
        if not ref.is_absolute():
            if key not in mappings:
                raise ValueError("relative/named source requires explicit path: " + key)
            ref = root / ref
        ref = allowed(ref, roots)
        data = ref.read_bytes()
        if _hash(data) != h:
            raise ValueError("source identity mismatch: " + key)
        blobs[key] = data
    result = validate_development_manifest(
        raw,
        dataset=dataset,
        n=n,
        seed=seed,
        tokenizer=tokenizer,
        expected_sha256=expected_sha256,
        tokenizer_sha256=tokenizer_sha256,
        source_blobs=blobs,
        min_unrelated=min_unrelated,
        excluded_item_ids=excluded_item_ids,
    )
    result.receipt["manifest_path"] = str(p)
    return result
