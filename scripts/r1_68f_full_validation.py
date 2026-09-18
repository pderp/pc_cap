"""DEC-063 streaming, recipe-bound full-validation endpoint; no model construction.

Only five scalar float64 vectors survive batches. Logits, hidden states and
selection events are discarded after each bounded batch. Row order is window,
then target position; context starts at zero in every complete window.
"""

from __future__ import annotations

import hashlib
import json
import os
import resource
import time
from datetime import datetime, timezone
from pathlib import Path

# isort: off
import pccap  # noqa: F401 -- determinism before JAX
import jax
import numpy as np
# isort: on

from scripts.r1_68c_batched_drift import PositionBatchReader, _forward_batch
from scripts.r1_68e_batched_drift_v0 import V0PositionBatchReader, _charge

from pccap.bases import gpt2_jax as g
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.learner import RevisionCap

ROOT = Path(__file__).resolve().parents[1]
POLICY = "DEC-063-complete-windows-final-both-references-v1"
FIELDS = ("loss_cap", "loss_capoff", "loss_original", "kl_capoff_to_cap", "kl_original_to_cap")
TAIL = "drop_incomplete_trailing_window"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ref(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path)}


def checked(binding):
    path = Path(binding["path"]).resolve()
    if "confirm" in path.parts or sha(path) != binding["sha256"]:
        raise ValueError("full-validation source binding mismatch or forbidden source")
    return path


def population(source, *, window_tokens=128):
    tokens = np.load(checked(source), mmap_mode="r", allow_pickle=False)
    if tokens.ndim != 1 or tokens.dtype.kind not in "iu":
        raise ValueError("validation tokens must be a one-dimensional integer array")
    if type(window_tokens) is not int or not 2 <= window_tokens <= 128:
        raise ValueError("invalid complete-window length")
    count, tail = divmod(len(tokens), window_tokens)
    if not count:
        raise ValueError("validation source has no complete window")
    windows = tokens[: count * window_tokens].reshape(count, window_tokens)
    # Explicit endian/dtype makes the population identity independent of NPY encoding.
    identity = hashlib.sha256(np.asarray(windows, dtype="<i8").tobytes()).hexdigest()
    return windows, dict(
        source_tokens=len(tokens),
        window_tokens=window_tokens,
        complete_windows=count,
        expected_positions=count * (window_tokens - 1),
        trailing_tokens_dropped=tail,
        windows_int64le_sha256=identity,
    )


def make_spec(*, inventory=None, fixture=False, window_tokens=128):
    inventory = Path(inventory or ROOT / "manifests/dev/lm_sets.json").resolve()
    meta = json.loads(inventory.read_text())
    source = {k: meta["files"]["drift_tokens"][k] for k in ("path", "sha256")}
    _, coverage = population(source, window_tokens=window_tokens)
    return dict(
        schema_version=1,
        policy=POLICY,
        source_inventory=ref(inventory),
        source=source,
        **coverage,
        tail_policy=TAIL,
        context_policy="reset_every_window",
        checkpoint_policy="final_only_plus_sample_at_every_checkpoint",
        references=["own_capoff", "original_base"],
        kl_direction="reference || cap",
        sample_windows=128 if not fixture else None,
    )


def validate_spec(manifest):
    if "full_validation" not in manifest:
        return None
    spec = manifest["full_validation"]
    if not isinstance(spec, dict):
        raise ValueError("full_validation must be an explicit bound contract")
    fixture = manifest.get("test_fixture") is True
    if fixture and manifest.get("adapter_identity", {}).get("base_sha256") != "tiny":
        raise ValueError("full-validation fixture requires TinyBase")
    inventory = checked(spec["source_inventory"])
    if not fixture and inventory != ROOT / "manifests/dev/lm_sets.json":
        raise ValueError("DEC-063 requires the registered ordinary-text validation inventory")
    expected = make_spec(
        inventory=inventory, fixture=fixture, window_tokens=spec.get("window_tokens", 128)
    )
    if digest(spec) != digest(expected):
        raise ValueError("full-validation contract/population mismatch")
    source_meta = json.loads(inventory.read_text())["files"]["drift_tokens"]
    if source_meta["shape"] != [spec["source_tokens"]]:
        raise ValueError("full-validation inventory shape differs")
    if not fixture and (
        spec["window_tokens"],
        spec["complete_windows"],
        spec["expected_positions"],
        spec["trailing_tokens_dropped"],
    ) != (128, 1931, 245237, 121):
        raise ValueError("full-validation population differs from DEC-063")
    return spec


def validate_sample(manifest, definition):
    spec = validate_spec(manifest)
    if spec is None:
        return
    windows, _ = population(spec["source"], window_tokens=spec["window_tokens"])
    sample = np.asarray(definition["windows"])
    if (
        sample.ndim != 2
        or sample.dtype.kind not in "iu"
        or not len(sample)
        or len(sample) > len(windows)
        or (spec["sample_windows"] is not None and len(sample) != spec["sample_windows"])
        or not np.array_equal(sample, windows[: len(sample)])
        or definition["expected_positions"] != sample.shape[0] * (sample.shape[1] - 1)
    ):
        raise ValueError("sampled drift is not the bound complete-window prefix")


def chunks(windows, batch_size):
    """Same bucket/window/position order as the sampled readers, without an inventory list."""
    buckets = {}
    for pos in range(1, windows.shape[1]):
        buckets.setdefault(g.bucket_len(pos), []).append(pos)
    for positions in buckets.values():
        chunk = []
        for wi, window in enumerate(windows):
            for pos in positions:
                chunk.append((wi, pos, window[:pos], int(window[pos])))
                if len(chunk) == batch_size:
                    yield chunk
                    chunk = []
        if chunk:
            yield chunk


def log_probs(logits):
    values = np.asarray(logits, np.float64)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise FloatingPointError("nonfinite or malformed full-validation logits")
    shifted = values - values.max(axis=1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))


def metrics(on, off, original, targets):
    on, off, original = (log_probs(x) for x in (on, off, original))
    if on.shape != off.shape or on.shape != original.shape:
        raise ValueError("reference/cap vocabulary or batch mismatch")
    i = np.arange(len(targets))
    kl_off = np.sum(np.exp(off) * (off - on), axis=1)
    kl_original = np.sum(np.exp(original) * (original - on), axis=1)
    if np.any(kl_off < -1e-10) or np.any(kl_original < -1e-10):
        raise FloatingPointError("negative full-validation KL beyond numerical roundoff")
    return np.stack(
        (
            -on[i, targets],
            -off[i, targets],
            -original[i, targets],
            np.maximum(kl_off, 0),
            np.maximum(kl_original, 0),
        ),
        axis=1,
    )


def tail_statistics(values, width):
    """HT-1 positive harm, strict exceedances, fractional empirical ES95."""
    values = np.asarray(values, np.float64).reshape(-1)
    if not len(values) or not np.isfinite(values).all():
        raise FloatingPointError("nonfinite or empty full-validation vector")
    positive = np.maximum(values, 0)
    descending = np.sort(positive)[::-1]
    mass = 0.05 * len(values)
    whole = int(mass)
    tail = descending[:whole].sum() + (mass - whole) * descending[whole]
    index = int(values.argmax())
    return dict(
        n=len(values),
        mean_signed=float(values.mean()),
        mean_positive=float(positive.mean()),
        ES95_positive=float(tail / mass),
        maximum_signed=float(values[index]),
        maximum_positive=float(positive.max()),
        maximum_location=f"w{index // width}:p{1 + index % width}",
        maximum_tie_count=int(np.count_nonzero(values == values[index])),
        exceedances_nats={
            str(t): dict(count=int(np.count_nonzero(values > t)), denominator=len(values))
            for t in (0.01, 0.1, 1.0)
        },
        tail_definition="fractional empirical top 5% of positive harm; includes zero mass",
    )


def device_memory():
    rows = []
    for device in jax.local_devices():
        stats = device.memory_stats()
        rows.append(
            dict(
                platform=device.platform,
                device_id=device.id,
                bytes_in_use=None if stats is None else stats.get("bytes_in_use"),
                peak_bytes_in_use=None if stats is None else stats.get("peak_bytes_in_use"),
            )
        )
    return rows


def aggregate_events(events, totals):
    for event in events:
        if "returned_cost" not in event:
            continue
        key = event.get("model", "unknown")
        row = totals.setdefault(
            key, dict(phase="query", model=key, batches=0, failed_batches=0, returned_cost={})
        )
        row["batches"] += 1
        row["failed_batches"] += int(event.get("status") == "failed")
        for field, value in event["returned_cost"].items():
            if isinstance(value, (int, float)):
                prior = row["returned_cost"].get(field, 0)
                row["returned_cost"][field] = (
                    max(prior, value) if field == "peak_mem_mib" else prior + value
                )
        row["returned_cost"]["phase"] = "query"


def parity(values, sampled):
    rows = sampled["rows"]
    if sampled["status"] != "complete" or not rows:
        raise ValueError("complete sampled drift required for full-validation parity")
    count = len(rows)
    width = values.shape[1]
    if [r["item_id"] for r in rows] != [f"w{i // width}:p{1 + i % width}" for i in range(count)]:
        raise ValueError("sample drift row order/coverage differs")
    a = values.reshape(-1, len(FIELDS))[:count, :3]
    b = np.asarray([[r[k] for k in ("cap", "capoff", "original")] for r in rows])
    error = float(np.max(np.abs(a - b)))
    counts = {}
    for index, reference in ((1, "capoff"), (2, "original")):
        counts[reference] = {
            str(t): [
                int(np.count_nonzero(a[:, 0] - a[:, index] > t)),
                int(np.count_nonzero(b[:, 0] - b[:, index] > t)),
            ]
            for t in (0.01, 0.1, 1.0)
        }
    if (
        not np.isfinite(b).all()
        or error > 1e-3
        or any(left != right for d in counts.values() for left, right in d.values())
    ):
        raise ValueError("sample/full drift parity failed")
    return dict(
        status="pass",
        positions=count,
        max_abs_loss_error_nats=error,
        tolerance_nats=1e-3,
        exceedance_counts_full_sample=counts,
        sampled_source_sha256=sampled["source_sha256"],
    )


def run(assays, manifest, definition, sampled, output, *, checkpoint, manifest_sha256):
    started, started_utc = time.monotonic(), datetime.now(timezone.utc).isoformat()
    validate_sample(manifest, definition)
    spec = manifest["full_validation"]
    if checkpoint != manifest["checkpoints"][-1]:
        raise ValueError("full validation only at the final declared checkpoint")
    windows, coverage = population(spec["source"], window_tokens=spec["window_tokens"])
    base = assays.adapter.base
    if (
        windows.shape[1] > base.cfg.n_pos
        or np.any(windows < 0)
        or np.any(windows >= base.cfg.vocab)
    ):
        raise ValueError("full-validation token/context outside model bounds")
    batch_size = manifest.get("drift_batch_size", 16)
    reader_type = (
        PositionBatchReader
        if type(assays.adapter.learner) is RevisionCap
        else V0PositionBatchReader
    )
    reader = reader_type(assays.adapter, batch_size=batch_size)
    values = np.full((len(windows), windows.shape[1] - 1, len(FIELDS)), np.nan, np.float64)
    state = assays.adapter.state_hash()
    references = dict(
        own_capoff=base.checksum(recompute=True),
        original_base=assays.adapter.locality_base.checksum(recompute=True),
    )
    memory_before, totals, scored, batch_count = device_memory(), {}, 0, 0
    try:
        for chunk in chunks(windows, batch_size):
            seqs = [row[2] for row in chunk]
            try:
                on = reader.last_logits_batch(seqs)
                off = reader.last_capoff
                if assays.adapter.locality_base is base:
                    original = off
                else:
                    physical = seqs + [seqs[-1]] * (batch_size - len(seqs))
                    original = _charge(
                        reader.events,
                        "original_batch",
                        physical,
                        len(seqs),
                        lambda physical=physical: _forward_batch(
                            assays.adapter.locality_base, physical
                        ),
                    )[0][: len(seqs)]
                rows = metrics(on, off, original, np.asarray([r[3] for r in chunk]))
                for value, (wi, pos, _, _) in zip(rows, chunk, strict=True):
                    values[wi, pos - 1] = value
                scored += len(chunk)
                batch_count += 1
            finally:
                aggregate_events(reader.events, totals)
                reader.events.clear()
        if scored != coverage["expected_positions"] or not np.isfinite(values).all():
            raise FloatingPointError("incomplete/nonfinite full-validation coverage")
        if assays.adapter.state_hash() != state:
            raise RuntimeError("full-validation query mutated checkpoint state")
        sample_parity = parity(values, sampled)
        # Rehash source after use: a concurrent change cannot acquire a receipt.
        validate_spec(manifest)
        summary = {
            "loss_delta_capoff": tail_statistics(
                values[:, :, 0] - values[:, :, 1], values.shape[1]
            ),
            "loss_delta_original": tail_statistics(
                values[:, :, 0] - values[:, :, 2], values.shape[1]
            ),
            "kl_capoff_to_cap": tail_statistics(values[:, :, 3], values.shape[1]),
            "kl_original_to_cap": tail_statistics(values[:, :, 4], values.shape[1]),
        }
        output = Path(output).resolve()
        if not output.is_relative_to(ROOT) or output.suffix != ".npz":
            raise ValueError("full-validation result vectors belong in pc_cap as NPZ")
        with output.open("xb") as stream:
            np.savez_compressed(stream, values=values)
            stream.flush()
            os.fsync(stream.fileno())
        directory_fd = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        memory_after = device_memory()
        peaks = [r["peak_bytes_in_use"] for r in memory_after if r["peak_bytes_in_use"] is not None]
        return dict(
            schema_version=1,
            status="complete",
            policy=POLICY,
            checkpoint=checkpoint,
            manifest_sha256=manifest_sha256,
            state_sha256=state,
            reference_base_sha256=references,
            source=spec["source"],
            source_inventory=spec["source_inventory"],
            contract_sha256=digest(spec),
            coverage=coverage,
            scored_positions=scored,
            vectors={
                **ref(output),
                "fields": list(FIELDS),
                "shape": list(values.shape),
                "dtype": "float64",
                "uncompressed_bytes": values.nbytes,
                "storage_bytes": output.stat().st_size,
                "order": "window,target_position,field",
            },
            statistics=summary,
            sample_parity=sample_parity,
            context_policy="reset_every_window",
            tail_policy=TAIL,
            kl_direction="reference || cap; tiny negative roundoff clipped at zero (1e-10 tolerance)",
            batch_audit=dict(
                batch_size=batch_size,
                batches=batch_count,
                selection_count=scored,
                hidden_state_retention="one physical batch only",
                selection_event_retention="aggregate each batch then discard",
                physical_padding_charged=True,
            ),
            device_memory_before=memory_before,
            device_memory_after=memory_after,
            device_peak_mem_mib=max(peaks) / 2**20 if peaks else None,
            device_peak_scope="process allocator lifetime high-water, not reset at phase start; null if unavailable",
            host_max_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            host_peak_scope="process lifetime high-water (Linux)",
            started_utc=started_utc,
            finished_utc=datetime.now(timezone.utc).isoformat(),
            wall_seconds=time.monotonic() - started,
            wall_scope="source/state checks, batches, reductions and durable vector write; outer phase receipt adds integrity overhead",
        )
    finally:
        assays.adapter.reset_queries()
        assays.events.extend(totals.values())
        assays.events.append(
            dict(
                phase="query",
                model="full_validation_coverage",
                completed_positions=scored,
                expected_positions=coverage["expected_positions"],
                wall_seconds=time.monotonic() - started,
            )
        )


def verify_report(report, manifest, report_path, manifest_sha256):
    """Resume rechecks the external vector dependency, not just its JSON pointer."""
    if "full_validation" not in manifest:
        return
    endpoint = report["endpoints"].get("full_validation")
    if report["checkpoint"] != manifest["checkpoints"][-1]:
        if endpoint is not None:
            raise ValueError("unexpected intermediate full-validation report")
        return
    if (
        not endpoint
        or endpoint["status"] != "complete"
        or endpoint["checkpoint"] != report["checkpoint"]
        or endpoint["state_sha256"] != report["state_sha256"]
        or endpoint["manifest_sha256"] != manifest_sha256
        or endpoint["contract_sha256"] != digest(manifest["full_validation"])
    ):
        raise ValueError("missing or mismatched final full-validation report")
    binding = endpoint["vectors"]
    path = Path(binding["path"]).resolve()
    if path.parent != Path(report_path).resolve().parent or sha(path) != binding["sha256"]:
        raise ValueError("full-validation vectors escaped report attempt or changed")
    spec = manifest["full_validation"]
    expected_shape = (spec["complete_windows"], spec["window_tokens"] - 1, len(FIELDS))
    with np.load(path, allow_pickle=False) as stored:
        values = stored["values"]
        if (
            values.shape != expected_shape
            or values.dtype != np.float64
            or not np.isfinite(values).all()
            or binding["fields"] != list(FIELDS)
            or binding["shape"] != list(expected_shape)
            or endpoint["scored_positions"] != spec["expected_positions"]
        ):
            raise ValueError("full-validation vector coverage/type differs")
