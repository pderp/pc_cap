"""Learner snapshots: byte-exact serialize / restore / clone, strict resume, resource-stop
rollback (S0-08; PDF Op. rule 9, App. B; plan §4.5 rules 3, 5, 6; CR-6).

``LearnerState`` is the complete future-behaviour-affecting state of a learner:

* ``arrays``: every cap array (per bank ``keys``, ``values``, ``meta``), replay buffers, optimizer
  moments — any NumPy array, keyed by name;
* ``scalars``: JSON-serializable bookkeeping (item index, counters, configuration hash, radii
  defaults, slot capacities, ...);
* ``correction_index``: active fact digests → ``[bank, slot, version]`` (bounded);
* ``use_tracker``: the per-item use set ``(item digest hex | None, [slots])`` (SD-12);
* ``rng``: Python ``random`` state, NumPy ``Generator`` bit-generator state, JAX key (uint32).

``content_hash`` covers every field. ``serialize`` writes a self-describing binary blob
(JSON header + raw array bytes) whose header carries the schema version and the hash;
``restore`` recomputes the hash and refuses on any mismatch (stricter than the sibling's relaxed
resume). Files are written atomically (temp + rename).

Resource-stop semantics (``ItemGuard``): the harness snapshots before each item; if the run is
interrupted mid-item the pre-item state is restored (accepted earlier prefixes of *that* item
are discarded, earlier items are kept) and the outcome is ``resource_stop``. The ledger is a
separate object and keeps every cost incurred.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA_VERSION = 1
MAGIC = b"PCCAPSNAP"


class SnapshotError(RuntimeError):
    pass


def _canon_scalars(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass
class LearnerState:
    arrays: dict[str, np.ndarray] = field(default_factory=dict)
    scalars: dict[str, Any] = field(default_factory=dict)
    correction_index: dict[str, list] = field(default_factory=dict)
    use_tracker: tuple[str | None, list[int]] = (None, [])
    rng: dict[str, Any] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    # ------------------------------------------------------------------ RNG capture helpers
    @staticmethod
    def capture_rng(py_random: random.Random | None = None, np_gen: np.random.Generator | None = None,
                    jax_key: np.ndarray | None = None) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if py_random is not None:
            st = py_random.getstate()
            out["python"] = [st[0], list(st[1]), st[2]]
        if np_gen is not None:
            out["numpy"] = json.loads(json.dumps(np_gen.bit_generator.state))
        if jax_key is not None:
            out["jax"] = np.asarray(jax_key, dtype=np.uint32).tolist()
        return out

    @staticmethod
    def apply_rng(rng: dict[str, Any], py_random: random.Random | None = None,
                  np_gen: np.random.Generator | None = None) -> np.ndarray | None:
        if py_random is not None and "python" in rng:
            v, s, g = rng["python"]
            py_random.setstate((v, tuple(s), g))
        if np_gen is not None and "numpy" in rng:
            np_gen.bit_generator.state = rng["numpy"]
        return np.asarray(rng["jax"], dtype=np.uint32) if "jax" in rng else None

    # ------------------------------------------------------------------ hashing / copying
    def content_hash(self) -> str:
        h = hashlib.sha256()
        h.update(f"schema={self.schema_version}".encode())
        for name in sorted(self.arrays):
            a = np.ascontiguousarray(self.arrays[name])
            h.update(name.encode())
            h.update(str(a.dtype.descr).encode())
            h.update(str(a.shape).encode())
            h.update(a.tobytes())
        h.update(b"scalars" + _canon_scalars(self.scalars).encode())
        h.update(b"cindex" + _canon_scalars(self.correction_index).encode())
        h.update(b"use" + _canon_scalars([self.use_tracker[0], list(self.use_tracker[1])]).encode())
        h.update(b"rng" + _canon_scalars(self.rng).encode())
        return h.hexdigest()

    def clone(self) -> "LearnerState":
        return LearnerState(
            arrays={k: v.copy() for k, v in self.arrays.items()},
            scalars=copy.deepcopy(self.scalars),
            correction_index=copy.deepcopy(self.correction_index),
            use_tracker=(self.use_tracker[0], list(self.use_tracker[1])),
            rng=copy.deepcopy(self.rng),
            schema_version=self.schema_version,
        )


def serialize(state: LearnerState) -> bytes:
    header = {
        "magic": MAGIC.decode(), "schema_version": state.schema_version, "hash": state.content_hash(),
        "arrays": [{"name": n, "dtype": np.lib.format.dtype_to_descr(state.arrays[n].dtype),
                    "shape": list(state.arrays[n].shape), "nbytes": int(np.ascontiguousarray(state.arrays[n]).nbytes)}
                   for n in sorted(state.arrays)],
        "scalars": state.scalars, "correction_index": state.correction_index,
        "use_tracker": [state.use_tracker[0], list(state.use_tracker[1])], "rng": state.rng,
    }
    hb = _canon_scalars(header).encode()
    buf = io.BytesIO()
    buf.write(MAGIC)
    buf.write(len(hb).to_bytes(8, "little"))
    buf.write(hb)
    for n in sorted(state.arrays):
        buf.write(np.ascontiguousarray(state.arrays[n]).tobytes())
    return buf.getvalue()


def restore(blob: bytes, expected_schema: int = SCHEMA_VERSION, expected_hash: str | None = None) -> LearnerState:
    if blob[: len(MAGIC)] != MAGIC:
        raise SnapshotError("not a pccap snapshot")
    off = len(MAGIC)
    hlen = int.from_bytes(blob[off : off + 8], "little")
    off += 8
    header = json.loads(blob[off : off + hlen].decode())
    off += hlen
    if header["schema_version"] != expected_schema:
        raise SnapshotError(f"schema mismatch: {header['schema_version']} != {expected_schema}")
    arrays = {}
    for a in header["arrays"]:
        dt = np.lib.format.descr_to_dtype(a["dtype"])
        n = a["nbytes"]
        arrays[a["name"]] = np.frombuffer(blob[off : off + n], dtype=dt).reshape(a["shape"]).copy()
        off += n
    if off != len(blob):
        raise SnapshotError("trailing bytes in snapshot")
    st = LearnerState(arrays=arrays, scalars=header["scalars"], correction_index=header["correction_index"],
                      use_tracker=(header["use_tracker"][0], list(header["use_tracker"][1])), rng=header["rng"],
                      schema_version=header["schema_version"])
    got = st.content_hash()
    if got != header["hash"]:
        raise SnapshotError("content hash mismatch (corrupt or tampered snapshot)")
    if expected_hash is not None and got != expected_hash:
        raise SnapshotError("snapshot hash does not match the expected state")
    return st


def write_atomic(path: Path | str, blob: bytes) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    with open(tmp, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return hashlib.sha256(blob).hexdigest()


def save(state: LearnerState, path: Path | str) -> str:
    return write_atomic(path, serialize(state))


def load(path: Path | str, expected_schema: int = SCHEMA_VERSION, expected_hash: str | None = None) -> LearnerState:
    return restore(Path(path).read_bytes(), expected_schema, expected_hash)


class Resumable:
    """Protocol a learner implements to take part in snapshots (duck-typed)."""

    def export_state(self) -> LearnerState: ...

    def import_state(self, state: LearnerState) -> None: ...


class ItemGuard:
    """Pre-item snapshot with resource-stop rollback.

    with ItemGuard(learner, ledger) as guard:
        ... run the item ...
        guard.commit()            # normal completion
    # on an exception or a missing commit the pre-item state is restored; ledger untouched
    """

    def __init__(self, learner, ledger=None):
        self.learner = learner
        self.ledger = ledger
        self.before: LearnerState | None = None
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "ItemGuard":
        self.before = self.learner.export_state()
        self.before_hash = self.before.content_hash()
        return self

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.learner.import_state(self.before.clone())
        self.rolled_back = True

    def __exit__(self, exc_type, exc, tb) -> bool:
        if not self.committed:
            self.rollback()
        return False  # never swallow exceptions (Op. rule 8)
