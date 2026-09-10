"""DATA-02a: synthetic-only seal checks; never open the actual confirmation payloads."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from pccap.data.confirmation_integrity import (
    ConfirmationIntegrityError,
    load_frozen_manifest,
)
from pccap.harness.schema import SchemaError

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("seal_confirm_under_test", ROOT / "scripts/seal_confirm.py")
assert _SPEC is not None and _SPEC.loader is not None
SEAL = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(SEAL)

SECRET_STRINGS = ["PRIVATE_PROMPT_ALPHA", "PRIVATE_ANSWER_BETA", "PRIVATE_SUBJECT", "PRIVATE_ITEM"]


def _write(path: Path, raw: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(raw)


def _json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False) + "\n").encode()


def _manifest() -> dict:
    items = [
        {
            "item_id": f"PRIVATE_ITEM_{i}", "subject": "PRIVATE_SUBJECT",
            "prompt": f"PRIVATE_PROMPT_ALPHA_{i}", "answer": f"PRIVATE_ANSWER_BETA_{i}",
            "prompt_ids": [400 + i], "answer_ids": [500 + i, 198],
            "answer_tokens": i + 2,
        }
        for i in range(2)
    ]
    ids = [item["item_id"] for item in items]
    return {
        "name": "zsre_r0", "mode": "confirm", "dataset": "zsre",
        "realization": 0, "seed": 0, "order_seeds": list(range(100, 105)),
        "orders": {str(seed): ids[::1 if seed % 2 == 0 else -1] for seed in range(100, 105)},
        "named_seeds": {
            str(seed): {
                "seed_cap_init": 10 * (seed - 100),
                "seed_router": 10 * (seed - 100) + 1,
                "seed_replay": 10 * (seed - 100) + 2,
            }
            for seed in range(100, 105)
        },
        "n_items": len(items), "items": items,
    }


def _case(
    tmp_path, *, data=None, raw=None, update=None, binding="zsre",
    expected=None, sums=None, frozen_raw=None, with_freeze=True,
):
    data = _manifest() if data is None else data
    raw = _json_bytes(data) if raw is None else raw
    digest = hashlib.sha256(raw).hexdigest() if expected is None else expected
    path = tmp_path / "zsre_r0.json"
    _write(path, raw)
    # Copy the permitted metadata draft into the fresh fixture directory, never the real freeze.
    draft = tmp_path / "frozen.draft.json"
    shutil.copyfile(ROOT / "manifests/frozen.draft.json", draft)
    frozen_data = json.loads(draft.read_bytes())
    frozen_data["dataset_ids"] = {binding: {path.name: digest}, "grammar": None}
    if update is not None:
        update(frozen_data)
    frozen_path = tmp_path / "frozen.json"
    if with_freeze:
        _write(frozen_path, _json_bytes(frozen_data) if frozen_raw is None else frozen_raw)
    _write(
        tmp_path / "SHA256SUMS",
        f"{digest}  {path.name}\n".encode() if sums is None else sums,
    )
    return path, frozen_path, data


def _deny_payload_reads(monkeypatch, path):
    original = Path.read_bytes

    def guarded(self):
        assert self != path, "payload was opened before the freeze and index gates passed"
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", guarded)


def test_valid_frozen_file_returns_manifest_and_reads_payload_once(tmp_path, monkeypatch):
    path, frozen, expected = _case(tmp_path)
    original = Path.read_bytes
    opened = []

    def counting(self):
        opened.append(self)
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", counting)
    assert load_frozen_manifest(path, frozen=frozen) == expected
    assert opened.count(path) == 1


def test_missing_freeze_never_opens_payload(tmp_path, monkeypatch):
    path, frozen, _ = _case(tmp_path, with_freeze=False)
    _deny_payload_reads(monkeypatch, path)
    with pytest.raises(PermissionError, match="existing frozen"):
        load_frozen_manifest(path, frozen=frozen)


def test_invalid_schema_never_opens_payload(tmp_path, monkeypatch):
    path, frozen, _ = _case(tmp_path, update=lambda d: d.pop("code_commit"))
    _deny_payload_reads(monkeypatch, path)
    with pytest.raises(SchemaError):
        load_frozen_manifest(path, frozen=frozen)


@pytest.mark.parametrize("raw", [b"{", b"[]"])
def test_invalid_freeze_json_never_opens_payload(tmp_path, monkeypatch, raw):
    path, frozen, _ = _case(tmp_path, frozen_raw=raw)
    _deny_payload_reads(monkeypatch, path)
    with pytest.raises(ConfirmationIntegrityError, match="frozen manifest"):
        load_frozen_manifest(path, frozen=frozen)


@pytest.mark.parametrize(
    "bindings",
    [
        {"zsre": {"different_r0.json": "0" * 64}},
        {"zsre": "0" * 64},
        {"zsre": {"zsre_r0.json": "not-a-sha256"}},
        {"zsre": {"../zsre_r0.json": "0" * 64}},
        {
            "zsre": {"zsre_r0.json": "0" * 64},
            "counterfact": {"zsre_r0.json": "0" * 64},
        },
        [],
    ],
)
def test_unbound_or_invalid_frozen_mapping_never_opens_payload(tmp_path, monkeypatch, bindings):
    path, frozen, _ = _case(tmp_path, update=lambda d: d.update(dataset_ids=bindings))
    _deny_payload_reads(monkeypatch, path)
    with pytest.raises(ConfirmationIntegrityError):
        load_frozen_manifest(path, frozen=frozen)


@pytest.mark.parametrize(
    "sums",
    [
        b"",
        b"malformed\n",
        ("0" * 64 + "  zsre_r0.json\n").encode(),
        ("0" * 64 + "  ../zsre_r0.json\n").encode(),
        (("0" * 64 + "  zsre_r0.json\n") * 2).encode(),
    ],
)
def test_invalid_sums_never_opens_payload(tmp_path, monkeypatch, sums):
    path, frozen, _ = _case(tmp_path, sums=sums)
    _deny_payload_reads(monkeypatch, path)
    with pytest.raises(ConfirmationIntegrityError, match="SHA256SUMS"):
        load_frozen_manifest(path, frozen=frozen)


def test_payload_hash_checked_before_json_decode(tmp_path):
    path, frozen, _ = _case(tmp_path, raw=b"PRIVATE_PROMPT_ALPHA invalid JSON", expected="0" * 64)
    with pytest.raises(ConfirmationIntegrityError, match="SHA-256") as exc:
        load_frozen_manifest(path, frozen=frozen)
    assert not any(secret in str(exc.value) for secret in SECRET_STRINGS)


def test_dataset_must_match_frozen_binding(tmp_path):
    path, frozen, _ = _case(tmp_path, binding="counterfact")
    with pytest.raises(ConfirmationIntegrityError, match="dataset"):
        load_frozen_manifest(path, frozen=frozen)


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda d: d.update(mode="dev"), "mode"),
        (lambda d: d.update(n_items=99), "n_items"),
        (lambda d: d.update(realization=99), "realizations"),
        (lambda d: d["orders"].update({"100": ["PRIVATE_ITEM_0"] * 2}), "permutation"),
        (lambda d: d["named_seeds"]["100"].pop("seed_router"), "named seeds"),
        (lambda d: d["items"][1].update(item_id="PRIVATE_ITEM_0"), "duplicate"),
    ],
)
def test_self_consistent_hash_does_not_hide_invalid_layout(tmp_path, change, message):
    data = _manifest()
    change(data)
    path, frozen, _ = _case(tmp_path, data=data)
    with pytest.raises(ConfirmationIntegrityError, match=message) as exc:
        load_frozen_manifest(path, frozen=frozen)
    assert not any(secret in str(exc.value) for secret in SECRET_STRINGS)


def test_order_seeds_must_match_freeze(tmp_path):
    path, frozen, _ = _case(
        tmp_path, update=lambda d: d.update(order_seeds=list(range(200, 205))),
    )
    with pytest.raises(ConfirmationIntegrityError, match="order_seeds"):
        load_frozen_manifest(path, frozen=frozen)


def test_sealer_metadata_is_aggregate_only_and_matches_data02_format(tmp_path, capsys):
    data = _manifest()
    raw = _json_bytes(data)
    _write(tmp_path / "zsre_r0.json", raw)
    aggregate = b'{"existing": "aggregate metadata is preserved"}\n'
    _write(tmp_path / "DATA-02.meta.json", aggregate)
    assert SEAL.main(["--directory", str(tmp_path)]) == 0
    sidecar_raw = (tmp_path / "zsre_r0.meta.json").read_bytes()
    sidecar = json.loads(sidecar_raw)
    digest = hashlib.sha256(raw).hexdigest()
    assert sidecar == {
        "file": "zsre_r0.json", "sha256": digest, "n_items": 2, "subjects": 1,
        "answer_length_strata": {"2": 1, "3": 1},
        "orders": {
            seed: hashlib.sha256(json.dumps(order).encode()).hexdigest()[:16]
            for seed, order in data["orders"].items()
        },
    }
    combined = sidecar_raw.decode() + capsys.readouterr().out
    assert not any(secret in combined for secret in SECRET_STRINGS)
    assert (tmp_path / "SHA256SUMS").read_text() == f"{digest}  zsre_r0.json\n"
    assert (tmp_path / "zsre_r0.json").read_bytes() == raw
    assert (tmp_path / "DATA-02.meta.json").read_bytes() == aggregate


@pytest.mark.parametrize("existing", ["SHA256SUMS", "zsre_r0.meta.json"])
def test_sealer_refuses_existing_output_before_reading_payload(tmp_path, monkeypatch, existing):
    path = tmp_path / "zsre_r0.json"
    _write(path, _json_bytes(_manifest()))
    original = b"existing content must survive\n"
    _write(tmp_path / existing, original)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    _deny_payload_reads(monkeypatch, path)
    with pytest.raises(FileExistsError):
        SEAL.seal(tmp_path)
    assert {p.name for p in tmp_path.iterdir()} == set(before)
    assert (tmp_path / existing).read_bytes() == original


def test_invalid_second_input_creates_no_partial_seal(tmp_path):
    _write(tmp_path / "a_r0.json", _json_bytes(_manifest()))
    _write(tmp_path / "b_r0.json", b'{"mode": "dev"}')
    with pytest.raises(ConfirmationIntegrityError):
        SEAL.seal(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a_r0.json", "b_r0.json"]


def test_sealer_index_lists_multiple_realizations_in_filename_order(tmp_path):
    for name in ["zsre_r1.json", "zsre_r0.json"]:
        _write(tmp_path / name, _json_bytes(_manifest()))
    outputs = SEAL.seal(tmp_path)
    assert [p.name for p in outputs] == ["zsre_r0.meta.json", "zsre_r1.meta.json", "SHA256SUMS"]
    assert [line.split()[1] for line in (tmp_path / "SHA256SUMS").read_text().splitlines()] == [
        "zsre_r0.json", "zsre_r1.json",
    ]


def test_empty_sealer_input_creates_nothing(tmp_path):
    with pytest.raises(ValueError, match="no realization"):
        SEAL.seal(tmp_path)
    assert list(tmp_path.iterdir()) == []
