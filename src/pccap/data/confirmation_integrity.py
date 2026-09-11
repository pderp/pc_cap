"""Freeze-gated integrity checks shared by the confirmation API and sealing writer.

This module has no default data path. Evaluation callers use pccap.data.confirm.load.
Only the explicit data-preparation writer may summarize unsealed input bytes.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from pccap.harness.schema import validate

_SHA256 = re.compile(r"[0-9a-f]{64}")
_FILENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.json")
_SUM_LINE = re.compile(r"([0-9a-f]{64}) [ *](.+)")


class ConfirmationIntegrityError(ValueError):
    """The freeze, digest index, or realization is inconsistent."""


def _filename(name: str) -> bool:
    return bool(_FILENAME.fullmatch(name)) and not name.endswith(".meta.json")


def _object(raw: bytes, description: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        raise ConfirmationIntegrityError(f"{description} is not valid JSON") from None
    if not isinstance(value, dict):
        raise ConfirmationIntegrityError(f"{description} must be a JSON object")
    return value


def _integer(value: Any) -> bool:
    return type(value) is int and value >= 0


def _realization(raw: bytes) -> dict[str, Any]:
    """Check the DATA-02 structure without disclosing item text in errors."""
    data = _object(raw, "realization")
    if data.get("mode") != "confirm":
        raise ConfirmationIntegrityError("realization mode must be confirm")
    for key in ("name", "dataset"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ConfirmationIntegrityError(f"realization requires {key}")
    for key in ("realization", "seed", "n_items"):
        if not _integer(data.get(key)):
            raise ConfirmationIntegrityError(f"realization requires integer {key}")
    items = data.get("items")
    if not isinstance(items, list) or data["n_items"] != len(items):
        raise ConfirmationIntegrityError("realization n_items does not match items")
    if any(
        not isinstance(item, dict)
        or not isinstance(item.get("item_id"), str)
        or not item["item_id"]
        for item in items
    ):
        raise ConfirmationIntegrityError("realization items require nonempty item IDs")
    ids = [item["item_id"] for item in items]
    if len(set(ids)) != len(ids):
        raise ConfirmationIntegrityError("realization contains duplicate item IDs")
    seeds = data.get("order_seeds")
    if (
        not isinstance(seeds, list)
        or not seeds
        or not all(_integer(seed) for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ConfirmationIntegrityError("realization order_seeds must be unique integers")
    expected_keys = {str(seed) for seed in seeds}
    for key in ("orders", "named_seeds"):
        if not isinstance(data.get(key), dict) or set(data[key]) != expected_keys:
            raise ConfirmationIntegrityError(f"realization {key} does not match order_seeds")
    for key in expected_keys:
        order = data["orders"][key]
        if (
            not isinstance(order, list)
            or not all(isinstance(item_id, str) for item_id in order)
            or len(order) != len(ids)
            or set(order) != set(ids)
        ):
            raise ConfirmationIntegrityError("realization order is not an item permutation")
        named = data["named_seeds"][key]
        if not isinstance(named, dict) or not all(
            _integer(named.get(field))
            for field in ("seed_cap_init", "seed_router", "seed_replay")
        ):
            raise ConfirmationIntegrityError("realization named seeds are missing or invalid")
    return data


def _binding(frozen_data: dict[str, Any], filename: str) -> tuple[str, str]:
    datasets = frozen_data.get("dataset_ids")
    if not isinstance(datasets, dict):
        raise ConfirmationIntegrityError("frozen dataset_ids must map datasets to file hashes")
    matches = []
    for dataset, files in datasets.items():
        # The draft uses null for the not-yet-available grammar fixture.
        if files is None:
            continue
        if not isinstance(files, dict):
            raise ConfirmationIntegrityError("frozen dataset binding must be a file-hash mapping")
        for name, digest in files.items():
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                raise ConfirmationIntegrityError("frozen dataset binding has an invalid name or hash")
            if not _filename(name):
                # A resource binding (e.g. the grammar's ``grammar_base.npz``, checked by the stage that loads it), never a
                # realization file: it cannot match a realization name and must not block the editing datasets (CP-E v1 defect).
                if name.endswith(".json"):
                    raise ConfirmationIntegrityError("frozen dataset binding has an invalid name or hash")
                continue
            if name == filename:
                matches.append((dataset, digest))
    if len(matches) != 1:
        raise ConfirmationIntegrityError("realization filename must have exactly one frozen binding")
    return matches[0]


def read_sha256sums(path: Path) -> dict[str, str]:
    """Read the standard DATA-02 '<sha256>  <basename>' index, rejecting ambiguity."""
    result = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        match = _SUM_LINE.fullmatch(line)
        if match is None or not _filename(match[2]):
            raise ConfirmationIntegrityError("SHA256SUMS contains a malformed entry")
        digest, filename = match.groups()
        if filename in result:
            raise ConfirmationIntegrityError("SHA256SUMS contains a duplicate filename")
        result[filename] = digest
    return result


def load_frozen_manifest(manifest_path: str | Path, *, frozen: str | Path) -> dict[str, Any]:
    """Validate the freeze and both digest bindings before parsing the realization.

    The same byte buffer is hashed and decoded, avoiding a second read of a mutable path.
    Missing/invalid freeze records and unbound names fail before the payload is opened.
    """
    frozen_path = Path(frozen)
    if not frozen_path.is_file():
        raise PermissionError("confirmation access requires an existing frozen manifest")
    frozen_data = _object(frozen_path.read_bytes(), "frozen manifest")
    validate("manifest_frozen", frozen_data)

    path = Path(manifest_path)
    dataset, expected = _binding(frozen_data, path.name)
    sums = read_sha256sums(path.parent / "SHA256SUMS")
    if sums.get(path.name) != expected:
        raise ConfirmationIntegrityError("SHA256SUMS binding does not match the frozen manifest")

    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ConfirmationIntegrityError("realization SHA-256 does not match the frozen manifest")
    data = _realization(raw)
    if data["dataset"] != dataset:
        raise ConfirmationIntegrityError("realization dataset does not match its frozen binding")
    if data["realization"] not in frozen_data["realizations"]:
        raise ConfirmationIntegrityError("realization is absent from the frozen realizations")
    if data["order_seeds"] != frozen_data["order_seeds"]:
        raise ConfirmationIntegrityError("realization order_seeds do not match the frozen manifest")
    return data


def manifest_metadata(raw: bytes, filename: str) -> dict[str, Any]:
    """For the sealing writer only: emit DATA-02-compatible aggregate metadata.

    This is a preparation operation, not an evaluation loader. Its output allowlist
    excludes prompts, answers, subject names, item IDs, token IDs, and order contents.
    """
    if not _filename(filename):
        raise ConfirmationIntegrityError("metadata requires a realization JSON basename")
    data = _realization(raw)
    subjects = set()
    strata: Counter[int] = Counter()
    for item in data["items"]:
        subject, length = item.get("subject"), item.get("answer_tokens")
        if not isinstance(subject, str) or not _integer(length):
            raise ConfirmationIntegrityError("metadata requires subject and answer-token count")
        subjects.add(subject)
        strata[length] += 1
    return {
        "file": filename,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "n_items": data["n_items"],
        "subjects": len(subjects),
        "answer_length_strata": {str(k): v for k, v in sorted(strata.items())},
        "orders": {
            seed: hashlib.sha256(json.dumps(order).encode()).hexdigest()[:16]
            for seed, order in data["orders"].items()
        },
    }
