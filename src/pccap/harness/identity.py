"""V2-01: the loaded resources are compared with the frozen identities at stage entry (confirm mode).

Immutability of the base during a run (``assert_frozen``) is a different property from *which* base was
loaded; the freeze binds the BP parameter digest, the tokenizer file hash, the grammar weights file hash and
the ePC checkpoint hash, and every confirmatory stage must refuse — before any edit or evaluation — when the
runtime artifact does not carry the frozen identity. Refusals raise ``PreflightRefusal`` (exit code 2).
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class PreflightRefusal(ValueError):
    """A confirm-mode precondition failed before any model work; the runner maps it to exit code 2."""


def file_sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _identity_of(obj, method: str, attr: str) -> str | None:
    fn = getattr(obj, method, None)
    if callable(fn):
        return fn()
    return getattr(obj, attr, None)


def check_frozen_identity(frozen: dict, *, base=None, base_kind: str | None = None, tokenizer=None, weights_path: Path | str | None = None) -> dict:
    """Compare the runtime artifacts with the frozen manifest; return the verified identities.

    * ``base_kind == "BP"``: ``base.checksum()`` must equal ``base_checkpoints.bp.param_digest``;
    * ``base_kind == "GRAM"``: the weights file's sha256 must equal ``dataset_ids.grammar["grammar_base.npz"]``;
    * ``base_kind == "EPC"``: the checkpoint file's sha256 must equal ``base_checkpoints.epc.sha256``;
    * ``tokenizer``: ``tokenizer.file_sha256()`` (or ``.sha256``) must equal ``tokenizer_rev.tokenizer_json_sha256``.
    A frozen identity that is absent, or a runtime artifact that cannot report one, is a refusal too.
    """
    out: dict = {}
    if base_kind == "BP":
        want = ((frozen.get("base_checkpoints") or {}).get("bp") or {}).get("param_digest")
        got = _identity_of(base, "checksum", "param_digest")
        if not want or not got:
            raise PreflightRefusal("frozen BP parameter digest or the loaded base's checksum is unavailable")
        if got != want:
            raise PreflightRefusal(f"loaded BP base digest {got[:12]} differs from the frozen base_checkpoints.bp.param_digest {want[:12]}")
        out["bp_param_digest"] = got
    elif base_kind == "GRAM":
        want = ((frozen.get("dataset_ids") or {}).get("grammar") or {}).get("grammar_base.npz")
        if not want or weights_path is None or not Path(weights_path).exists():
            raise PreflightRefusal("frozen grammar weights hash (dataset_ids.grammar[grammar_base.npz]) or the weights file is unavailable")
        got = file_sha256(weights_path)
        if got != want:
            raise PreflightRefusal(f"grammar weights file sha256 {got[:12]} differs from the frozen {want[:12]}")
        out["grammar_weights_sha256"] = got
    elif base_kind == "EPC":
        ck = (frozen.get("base_checkpoints") or {}).get("epc") or {}
        if not ck.get("path") or not ck.get("sha256"):
            raise PreflightRefusal("frozen ePC checkpoint identity is missing (base_checkpoints.epc)")
        got = file_sha256(ck["path"])
        if got != ck["sha256"]:
            raise PreflightRefusal(f"ePC checkpoint at {ck['path']} has sha256 {got[:12]} but the freeze binds {ck['sha256'][:12]}")
        out["epc_checkpoint_sha256"] = got
    elif base_kind is not None:
        raise PreflightRefusal(f"unknown base kind {base_kind!r}")
    if tokenizer is not None:
        want = (frozen.get("tokenizer_rev") or {}).get("tokenizer_json_sha256")
        got = _identity_of(tokenizer, "file_sha256", "sha256")
        if not want or not got:
            raise PreflightRefusal("frozen tokenizer hash or the loaded tokenizer's file hash is unavailable")
        if got != want:
            raise PreflightRefusal(f"loaded tokenizer file sha256 {got[:12]} differs from the frozen tokenizer_rev {want[:12]}")
        out["tokenizer_json_sha256"] = got
    return out
