"""R1-77b sealed owner backend; inspect metadata by default, execute explicitly.

The admission path is stage4_cell.load_cell(allow_sealed=True), never a
 development loader. R1-68e's execution body is copied with a pinned source hash;
 sealed admission, output namespaces and deadline checks are the only changes.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip
# pccap initializes determinism before the following JAX dependencies.

import argparse
import copy
import fcntl
import hashlib
import json
import os
import time
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts import r1_68c_dev_cell as donor
from scripts import r1_68f_full_validation as full_validation
from scripts.r1_68b_integrity_runtime import (
    DurablePhaseJournal,
    IndexedAdapter,
    durable_directory,
    durable_json,
    phase_summary,
)

from pccap.harness.snapshot import restore, serialize
from pccap.revision_v1 import stage4_cell as core
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.endpoints import EndpointResourceFailure, row_hash
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.stage4_assays import CellAssays
from pccap.revision_v1.stage4_cell import _delta, _ledger, cell_name, read_binding

ROOT = Path(__file__).resolve().parents[1]
MODULE = "scripts.r1_77b_sealed_backend"
MODE = "stage4_sealed_cell"
BANNER = "sealed Stage 4; scientific admission also requires complete declared populations"
OUTPUT_ROOT = ROOT / "results/R1/stage4_sealed_cells"
RESOURCE_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/stage4_sealed_cells"
RECEIPT_ROOT = ROOT / "logs/r1_77b_execution"
FROZEN_RELATIVE = "manifests/revision_v1/frozen_stage4.json"
DONOR_SHA256 = "895094861ac5d40a440b56c65589a1b37380c8bee4d21b180b0d806994cdcc24"
GATES = tuple(f"U{i:02}" for i in range(1, 19))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def backend_binding():
    return {"module": MODULE, "path": str(Path(__file__).resolve()), "sha256": sha(__file__)}


def contract_digest(manifest):
    """Freeze excludes only its own binding, avoiding a circular file hash."""
    return core.content_digest({k: v for k, v in manifest.items() if k != "freeze"})


def deadline_check(now=None):
    now = time.time() if now is None else now
    deadline = datetime(2026, 10, 10, tzinfo=ZoneInfo("America/New_York")).timestamp()
    if now >= deadline:
        raise TimeoutError("October 9 experimental deadline passed")


def metadata(binding):
    path = Path(binding["path"]).resolve()
    allowed = (ROOT / "manifests/revision_v1", ROOT / "docs/tasks")
    if "confirm" in path.parts or not any(path.is_relative_to(p) for p in allowed):
        raise PermissionError(
            "sealed backend admission metadata must be in revision_v1 or docs/tasks"
        )
    return read_binding(binding)


def inspect_manifest(path, expected_sha256, *, code_root=None):
    """Verify final authority and code without opening payload or reservations."""
    code_root = ROOT if code_root is None else Path(code_root)
    m = metadata({"path": str(path), "sha256": expected_sha256})
    if m.get("schema_version") != 1 or m.get("mode") != MODE or m.get("test_fixture"):
        raise PermissionError(
            "actual sealed-mode recipe required; no development/test admission flag"
        )
    if m.get("backend") != backend_binding():
        raise ValueError("sealed backend module/file identity mismatch")
    if sha(code_root / "scripts/r1_68c_dev_cell.py") != DONOR_SHA256:
        raise ValueError("R1-68e donor changed; reconcile the sealed fork")
    donor.profile_config(m, code_root)
    if m.get("code_sha256") != core.code_identity(code_root):
        raise ValueError("installed sealed code identity mismatch")
    if any(
        m.get("admission", {}).get(k) is not True
        for k in ("lead_approved", "protocol_frozen", "condition_admitted", "launch_authorized")
    ):
        raise PermissionError("unresolved sealed launch admission")
    if Path(m["freeze"]["path"]).resolve() != ROOT / FROZEN_RELATIVE:
        raise PermissionError("R1 final frozen manifest required; historical v0/candidates refused")
    frozen = metadata(m["freeze"])
    if (
        frozen.get("schema_version") != 1
        or frozen.get("mode") != "stage4_final_freeze"
        or frozen.get("lead_approved") is not True
        or frozen.get("launch_authorized") is not True
        or frozen.get("open_gates") != []
        or set(frozen.get("closed_gates", {})) != set(GATES)
    ):
        raise PermissionError("final freeze has unresolved gates")
    for gate in GATES:
        receipt = metadata(frozen["closed_gates"][gate])
        if (
            receipt.get("gate") != gate
            or receipt.get("status") != "closed"
            or receipt.get("lead_approved") is not True
        ):
            raise PermissionError("gate closure receipt not approved: " + gate)
    if (
        frozen.get("backend") != m["backend"]
        or frozen.get("code_sha256") != m["code_sha256"]
        or frozen.get("integrity_driver_bindings") != m["integrity_driver_bindings"]
    ):
        raise ValueError("freeze/backend/code identity mismatch")
    for key in ("protocol", "reservations", "population"):
        if frozen.get(key) != m.get(key):
            raise ValueError("freeze/recipe binding mismatch: " + key)
    if not frozen.get("bindings_sha256"):
        raise PermissionError("freeze requires provenance/code/environment bindings")
    for name, expected in frozen["bindings_sha256"].items():
        p = Path(name).resolve()
        if not p.is_relative_to(code_root) or "confirm" in p.parts:
            raise PermissionError("freeze metadata/code binding path refused")
        if p in [Path(m[k]["path"]).resolve() for k in ("payload", "reservations", "population")]:
            raise ValueError(
                "opaque payload/reservation/population hashes belong in dedicated bindings"
            )
        if sha(p) != expected:
            raise ValueError("freeze provenance binding mismatch: " + name)
    from scripts.r1_75_analysis_stage4_v1 import coordinate_id

    cid = coordinate_id(m["cell"])
    if frozen.get("recipe_contracts", {}).get(cid) != contract_digest(m):
        raise ValueError("recipe not in final frozen contract inventory")
    protocol = metadata(m["protocol"])
    if (
        protocol.get("schema_version") not in (1, 2)
        or protocol.get("mode") != "stage4_final_protocol"
        or protocol.get("lead_approved") is not True
        or protocol.get("open_gates") != []
        or protocol.get("max_new") != 32
        or protocol.get("locality_score") != "bounded_text_equality_DEC053"
        or protocol.get("experiment_deadline") != "2026-10-09"
    ):
        raise PermissionError("final executable protocol not admitted")
    cadence = core.registered_checkpoints(m, protocol)
    if protocol.get("schema_version") == 1 and protocol.get("checkpoints") != cadence:
        raise ValueError("legacy protocol cadence differs")
    if m["checkpoints"] != cadence or m["max_new"] != protocol["max_new"]:
        raise ValueError("recipe/protocol cadence mismatch")
    return m


def planned_population(payload):
    ep = payload["endpoints"]
    drift = ep["drift"]
    return {
        "item_ids": [r["item_id"] for r in payload["items"]],
        "paraphrase_counts": [len(r["paraphrases"]) for r in payload["items"]],
        "endpoints": {k: v["expected_ids"] for k, v in ep.items() if k != "drift"},
        "drift": {
            "expected_positions": drift["expected_positions"],
            "position_ids": [
                f"w{w}:p{p}" for w, row in enumerate(drift["windows"]) for p in range(1, len(row))
            ],
            "source_sha256": row_hash(drift),
        },
    }


def load_sealed_cell(path, expected_sha256, *, code_root=None, allow_sealed=False):
    if allow_sealed is not True:
        raise PermissionError("payload access requires explicit owner execution")
    m = inspect_manifest(path, expected_sha256, code_root=code_root)
    code_root = ROOT if code_root is None else Path(code_root)
    # The installed sealed loader verifies reservation membership, row payload
    # hashes, admitted endpoint bundle and exact item ordering.
    loaded, payload = core.load_cell(path, expected_sha256, code_root=code_root, allow_sealed=True)
    if loaded != m:
        raise ValueError("recipe changed across admission")
    declared = read_binding(m["population"])
    from scripts.r1_75_analysis_stage4_v1 import coordinate_id

    pop = declared["cells"][coordinate_id(m["cell"])]
    if pop != planned_population(payload):
        raise ValueError("payload differs from independently frozen analysis population")
    # Observed rows may be a subset: analysis must retain missing denominators.
    return m, payload


def profile_config(manifest, root=None):
    return donor.profile_config(manifest, ROOT if root is None else root)


def write_json(path, value):
    value.update(mode=MODE, banner=BANNER)
    if "receipt_sha256" in value:
        value["receipt_sha256"] = digest({k: v for k, v in value.items() if k != "receipt_sha256"})
    return durable_json(path, value)


def memory_identity(adapter):
    """Check immutable object structure without transferring or hashing arrays.

    JAX arrays are immutable: replacing a leaf changes its object identity. A
    mutable NumPy leaf changed in place is caught by the next full boundary
    rehash, before any checkpoint receipt can be issued.
    """

    def tree(value):
        if isinstance(value, dict):
            return (id(value), tuple((k, tree(v)) for k, v in sorted(value.items())))
        if isinstance(value, (list, tuple)):
            return (id(value), tuple(tree(v) for v in value))
        return (id(value), str(getattr(value, "dtype", "")), getattr(value, "shape", None))

    learner = adapter.learner
    configurations = [
        getattr(learner, "cfg", None),
        getattr(learner, "rule", None),
        adapter.budget,
        getattr(adapter.base, "cfg", None),
        getattr(adapter.locality_base, "cfg", None),
    ]
    return (
        adapter.condition,
        id(learner),
        type(learner),
        id(adapter.base),
        id(learner.base),
        id(adapter.locality_base),
        tree(getattr(learner, "params", None)),
        tree(getattr(adapter.base, "params", None)),
        tree(getattr(adapter.locality_base, "params", None)),
        digest([asdict(c) if is_dataclass(c) else c for c in configurations]),
    )


def _run_sealed_cell(
    manifest_path,
    expected_sha256,
    adapter,
    tokenizer,
    *,
    output_root,
    resource_root,
    code_root=None,
    resume=False,
    allow_sealed=False,
    stop_after_checkpoint=None,
):
    """Run one cell; each attempt/phase/checkpoint is a new file, never appended.

    A complete checkpoint receipt is written last and binds both the report and
    snapshot. Interrupted work remains in its attempt directory and stays in
    resource accounting. Resume restores only a contiguous verified prefix.
    """
    code_root = ROOT if code_root is None else Path(code_root)
    admission_started = time.monotonic()
    manifest, payload = load_sealed_cell(
        manifest_path, expected_sha256, code_root=code_root, allow_sealed=allow_sealed
    )
    profile, batch_edits = profile_config(manifest, code_root)
    full_validation.validate_sample(manifest, payload["endpoints"]["drift"])
    if profile == "incremental":
        adapter = IndexedAdapter(adapter)
    identity = adapter.identity()
    boundary_identity_checks = [
        {
            "boundary": "attempt_start",
            "kind": "full_recipe_and_adapter_rehash",
            "seconds": time.monotonic() - admission_started,
        }
    ]
    memory_fingerprint = memory_identity(adapter)
    if (
        identity != manifest["adapter_identity"]
        or adapter.condition != manifest["cell"]["condition"]
    ):
        raise ValueError("adapter/base/config/parameter identity mismatch")
    if stop_after_checkpoint is not None and stop_after_checkpoint not in manifest["checkpoints"]:
        raise ValueError("stop must be a declared checkpoint")
    root, assets = Path(output_root).resolve(), Path(resource_root).resolve()
    if not root.is_relative_to(OUTPUT_ROOT) or not assets.is_relative_to(ROOT.parent / "assets"):
        raise ValueError("outputs belong in pc_cap; snapshot resources belong in assets")
    name = cell_name(manifest, expected_sha256)
    run, resources = root / name, assets / name
    if (
        not hasattr(tokenizer, "file_sha256")
        or tokenizer.file_sha256() != manifest["tokenizer_sha256"]
    ):
        raise ValueError("tokenizer identity mismatch")
    items = [as_edit(r, tokenizer) for r in payload["items"]]
    max_context = int(getattr(getattr(adapter.base, "cfg", None), "n_pos", 1024))
    vocabulary = int(
        getattr(adapter.base, "vocab", getattr(getattr(adapter.base, "cfg", None), "vocab", 50257))
    )
    for item in items:
        if any(int(t) < 0 or int(t) >= vocabulary for t in [*item.prompt_ids, *item.answer_ids]):
            raise ValueError("support token outside vocabulary")
        if len(item.prompt_ids) + max(len(item.answer_ids), manifest["max_new"]) > max_context:
            raise ValueError("edit outside model context")
    if any(
        t
        >= int(
            getattr(
                adapter.base, "vocab", getattr(getattr(adapter.base, "cfg", None), "vocab", 50257)
            )
        )
        for w in payload["endpoints"]["drift"]["windows"]
        for t in w
    ):
        raise ValueError("drift token outside vocabulary")
    fresh_state = adapter.export_state().clone()
    initial_hash = fresh_state.content_hash()
    meta = {
        "schema_version": 1,
        "cell": manifest["cell"],
        "manifest_sha256": expected_sha256,
        "code_sha256": manifest["code_sha256"],
        "payload_sha256": manifest["payload"]["sha256"],
        "adapter_identity": identity,
        "initial_state_sha256": initial_hash,
        "checkpoints": manifest["checkpoints"],
        "mode": manifest["mode"],
        "banner": BANNER,
        "backend": manifest["backend"],
        "freeze": manifest["freeze"],
        "population": manifest["population"],
    }
    meta.update(
        integrity_profile=profile,
        integrity_batch_edits=batch_edits,
        integrity_driver_bindings=manifest["integrity_driver_bindings"],
    )
    history, completed, previous = [], 0, None
    if not resume:
        durable_directory(run)
        durable_directory(resources)
        blob = serialize(fresh_state)
        with (resources / "initial.snapshot").open("xb") as f:
            f.write(blob)
            f.flush()
            os.fsync(f.fileno())
        write_json(
            resources / "initial.snapshot.json",
            {"snapshot_sha256": sha(resources / "initial.snapshot"), "state_sha256": initial_hash},
        )
        write_json(run / "cell.json", meta)
    else:
        if not run.is_dir() or json.loads((run / "cell.json").read_text()) != meta:
            raise ValueError("resume cell identity or initial state mismatch")
        fresh_state = restore(
            (resources / "initial.snapshot").read_bytes(), expected_hash=initial_hash
        )
        # Verify every prior attempt, including failed/unreceipted work, before
        # constructing a new attempt or doing model work. Unknown spend refuses.
        if profile == "incremental":
            for prior_attempt in sorted(run.glob("attempt-*")):
                if prior_attempt.is_dir():
                    DurablePhaseJournal.verify(prior_attempt / "phases")
        receipts = []
        for path in run.glob("attempt-*/checkpoint-*.receipt.json"):
            rec = json.loads(path.read_text())
            if rec["receipt_sha256"] != digest(
                {k: v for k, v in rec.items() if k != "receipt_sha256"}
            ):
                raise ValueError("checkpoint receipt hash mismatch")
            receipts.append(rec)
        receipts.sort(key=lambda r: r["checkpoint"])
        if [r["checkpoint"] for r in receipts] != manifest["checkpoints"][: len(receipts)]:
            raise ValueError("resume checkpoints are not a unique contiguous prefix")
        for rec in receipts:
            if (
                rec["manifest_sha256"] != expected_sha256
                or rec["previous_receipt_sha256"] != previous
            ):
                raise ValueError("checkpoint chain identity mismatch")
            report_path, snapshot_path = (
                Path(rec["report"]["path"]).resolve(),
                Path(rec["snapshot"]["path"]).resolve(),
            )
            if not report_path.is_relative_to(run) or not snapshot_path.is_relative_to(resources):
                raise ValueError("checkpoint path escapes cell")
            report = read_binding(rec["report"])
            full_validation.verify_report(
                report, manifest, report_path, expected_sha256
            )
            if profile == "incremental":
                journal_directory = report_path.parent / "phases"
                if Path(rec["journal"]["directory"]).resolve() != journal_directory:
                    raise ValueError("checkpoint journal escapes its report attempt")
                DurablePhaseJournal.verify(journal_directory, rec["journal"])
                if report.get("integrity_root") != rec.get("integrity_root"):
                    raise ValueError("checkpoint incremental root differs from receipt")

            if sha(snapshot_path) != rec["snapshot"]["sha256"]:
                raise ValueError("checkpoint snapshot file mismatch")
            state = restore(snapshot_path.read_bytes(), expected_hash=rec["state_sha256"])
            if (
                report["checkpoint"] != rec["checkpoint"]
                or report["state_sha256"] != rec["state_sha256"]
            ):
                raise ValueError("checkpoint report differs from receipt")
            history, completed, previous = (
                report["history"],
                rec["checkpoint"],
                rec["receipt_sha256"],
            )
            if [r["item_id"] for r in history] != [it.item_id for it in items[:completed]]:
                raise ValueError("resume attempted history mismatch")
        if receipts:
            adapter.import_state(state)
            if adapter.state_hash() != receipts[-1]["state_sha256"]:
                raise RuntimeError("resume restore mismatch")
            if profile == "incremental" and adapter.verify() != receipts[-1]["integrity_root"]:
                raise RuntimeError("resume incremental inventory differs from receipt")

    attempts = [p for p in run.glob("attempt-*") if p.is_dir()]
    attempt = run / f"attempt-{len(attempts):04d}"
    durable_directory(attempt)
    durable_directory(attempt / "phase-timings")
    resource_attempt = resources / attempt.name
    durable_directory(resource_attempt)
    events = attempt / "phases"
    journal = (
        DurablePhaseJournal(events, batch_edits=batch_edits) if profile == "incremental" else None
    )
    if journal is None:
        durable_directory(events)
    attempt_started = time.monotonic()
    timed_rows = []
    detailed_timers = []
    assays = CellAssays(adapter, tokenizer, max_new=manifest["max_new"])
    phase_index = 0

    def verify_inputs():
        load_sealed_cell(
            manifest_path, expected_sha256, code_root=code_root, allow_sealed=allow_sealed
        )
        if adapter.identity() != identity:
            raise ValueError("immutable adapter identity changed")
        if memory_identity(adapter) != memory_fingerprint:
            raise ValueError("immutable in-memory identity changed")

    def verify_boundary(label):
        deadline_check()
        started = time.monotonic()
        verify_inputs()
        boundary_identity_checks.append(
            {
                "boundary": label,
                "kind": "full_recipe_and_adapter_rehash",
                "seconds": time.monotonic() - started,
            }
        )

    def verify_memory():
        if memory_identity(adapter) != memory_fingerprint:
            raise RuntimeError("endpoint/update mutated immutable in-memory parameters")

    def phase(label, operation, *, learning=False):
        nonlocal phase_index
        deadline_check()
        phase_started = time.monotonic()
        timers = {
            "recipe_verification_seconds": 0.0,
            "identity_verification_seconds": 0.0,
            "identity_check_seconds": 0.0,
            "state_hash_seconds": 0.0,
            "clone_seconds": 0.0,
            "restore_seconds": 0.0,
            "file_write_seconds": 0.0,
            "operation_seconds": 0.0,
        }

        def timed(key, fn):
            start = time.monotonic()
            try:
                return fn()
            finally:
                timers[key] += time.monotonic() - start

        led0 = _ledger(adapter)
        if journal is not None:
            timed("file_write_seconds", lambda: journal.before_phase(label, led0))
        timed("identity_check_seconds", verify_memory)
        kind = label.split(":", 1)[0]
        borrowed = profile == "incremental" and kind in (
            "immediate",
            "retention",
            "locality",
            "unseen",
            "drift",
            "full_validation",
        )
        # Only edits use the incremental digest. Read-only phases use a full state
        # hash so an uninstrumented in-place mutation cannot escape the check.
        fast = profile == "incremental" and kind == "edit"
        state = adapter.root if fast else adapter.state_hash
        before = timed("state_hash_seconds", state)
        snapshot = (
            None
            if fast or borrowed
            else timed("clone_seconds", lambda: adapter.export_state().clone())
        )
        assays.events = []
        operation_started = time.monotonic()
        result, error = None, None
        try:
            result = timed("operation_seconds", operation)
            after = timed("state_hash_seconds", state)
            if not learning and after != before:
                raise RuntimeError("endpoint mutated checkpoint state")
            timed("identity_check_seconds", verify_memory)
            return result
        except BaseException as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            observed = timed("state_hash_seconds", state)
            restore_required = snapshot is not None and (not learning or error is not None)
            if restore_required:
                timed("restore_seconds", lambda: adapter.import_state(snapshot))
                if timed("state_hash_seconds", state) != before:
                    raise RuntimeError("phase restore mismatch")
            else:
                adapter.reset_queries()
            rec = {
                "phase": label,
                "learning": learning,
                "identity_check_kind": "in_memory_structure_and_configuration",
                "identity_check_seconds": timers["identity_check_seconds"],
                "state_before": before,
                "state_after_operation": observed,
                "state_after_restore": timed("state_hash_seconds", state),
                "state_hash_convention": "record-digest-v1" if fast else "legacy-state-sha256",
                "restore_required": restore_required,
                "borrowed_readonly_state": borrowed,
                "failure_recovery": "abort; resume only from the last verified durable checkpoint",
                "status": "error" if error else "ok",
                "error": error,
                "ledger_delta": _delta(led0, _ledger(adapter)),
                "returned_events": copy.deepcopy(assays.events),
                "wall_seconds": time.monotonic() - operation_started,
                "phase_wall_seconds": time.monotonic() - phase_started,
                "operation_seconds": timers["operation_seconds"],
                "cost_policy": "shared ledger and returned counters separate; all failed work retained",
                "mutation_inventory": adapter.drain_mutations()
                if profile == "incremental"
                else None,
            }
            if journal is None:
                timed(
                    "file_write_seconds",
                    lambda: write_json(events / f"{phase_index:06d}.json", rec),
                )
            else:
                timed("file_write_seconds", lambda: journal.add(rec))
            # A separate new file can record the completed phase-file write cost.
            timing = {
                "phase": label,
                "identity_check_kind": "in_memory_structure_and_configuration",
                **timers,
                "total_phase_seconds": time.monotonic() - phase_started,
                "scope": "file writes include journal intent/add/flush; excludes this timing receipt and checkpoint writes",
            }
            write_json(attempt / "phase-timings" / f"{phase_index:06d}.json", timing)
            timed_rows.append(rec)
            detailed_timers.append(timing)
            phase_index += 1

    def update(item):
        out = adapter.update_item(item)
        assays.events.append(
            {
                "phase": "learning",
                "item_id": item.item_id,
                "code": out.code,
                "original_code": adapter.last_original_outcome,
                "codes": list(out.codes),
                "returned_cost": out.cost.as_dict(),
            }
        )
        if out.code == "resource_stop" or any(
            str(c).startswith("resource_failure:") for c in out.codes
        ):
            raise EndpointResourceFailure(";".join(out.codes))
        return {
            "code": out.code,
            "original_code": adapter.last_original_outcome,
            "codes": list(out.codes),
        }

    try:
        if resume:
            verify_boundary("resume_after_restore")
        for n, item in enumerate(items[completed:], start=completed + 1):
            outcome = phase(f"edit:{n}", lambda item=item: update(item), learning=True)
            row = phase(f"immediate:{n}", lambda item=item: assays.item(item))
            history.append({**row, "outcome": outcome, "index": n})
            if n not in manifest["checkpoints"]:
                continue
            if journal is not None:
                journal.flush()
                adapter.verify()
            cp = {"checkpoint": n, "history": list(history), "endpoints": {}}

            cp["retention"] = phase(f"retention:{n}", lambda n=n: assays.retention(items[:n]))
            ep = payload["endpoints"]
            cp["locality"] = phase(f"locality:{n}", lambda ep=ep: assays.locality(ep["locality"]))
            cp["unseen"] = phase(
                f"unseen:{n}",
                lambda ep=ep, n=n: assays.unseen(
                    ep["unseen"],
                    payload["pool_rows"],
                    items[:n],
                    str(n),
                    manifest["payload"]["sha256"],
                ),
            )
            if n != len(items) and "full_validation" in manifest:
                cp["endpoints"]["drift"] = phase(
                    f"drift:{n}",
                    lambda ep=ep: donor.run_drift_assay(assays, ep["drift"], manifest, profile),
                )
            if n == len(items):
                for kind in ("near_miss", "revision"):
                    cp["endpoints"][kind] = phase(
                        f"{kind}:{n}",
                        lambda kind=kind, ep=ep: assays.challenges(kind, ep[kind], items),
                    )
                cp["endpoints"]["composition"] = phase(
                    f"composition:{n}",
                    lambda ep=ep: assays.composition(ep["composition"], items, fresh_state),
                )
                cp["endpoints"]["drift"] = phase(
                    f"drift:{n}",
                    # R1-77c review: the signed recipe field alone opts into
                    # v0 batching; no condition-based inference or reduced integrity.
                    lambda ep=ep: donor.run_drift_assay(assays, ep["drift"], manifest, profile),
                )
                if "full_validation" in manifest:
                    cp["endpoints"]["full_validation"] = phase(
                        f"full_validation:{n}",
                        lambda n=n, ep=ep, cp=cp: full_validation.run(
                            assays, manifest, ep["drift"], cp["endpoints"]["drift"],
                            attempt / f"full-validation-{n}.npz",
                            checkpoint=n, manifest_sha256=expected_sha256,
                        ),
                    )
            cp["observation"] = adapter.observe()
            cp["state_sha256"] = adapter.state_hash()
            if profile == "incremental":
                cp["integrity_root"] = adapter.verify()
            blob = serialize(adapter.export_state())
            restored = restore(blob, expected_hash=cp["state_sha256"])
            adapter.import_state(restored)
            if adapter.state_hash() != cp["state_sha256"]:
                raise RuntimeError("checkpoint serialization/restore mismatch")
            if profile == "incremental" and adapter.verify() != cp["integrity_root"]:
                raise RuntimeError("checkpoint incremental restore mismatch")
            verify_boundary(f"checkpoint:{n}")
            journal_receipt = journal.receipt() if journal is not None else None
            snapshot = resource_attempt / f"checkpoint-{n}.snapshot"
            with snapshot.open("xb") as f:
                f.write(blob)
                f.flush()
                os.fsync(f.fileno())
            write_json(
                resource_attempt / f"checkpoint-{n}.snapshot.json",
                {"snapshot_sha256": sha(snapshot), "state_sha256": cp["state_sha256"]},
            )
            report = write_json(attempt / f"checkpoint-{n}.json", cp)
            receipt = {
                "checkpoint": n,
                "manifest_sha256": expected_sha256,
                "previous_receipt_sha256": previous,
                "state_sha256": cp["state_sha256"],
                "report": report,
                "snapshot": {"path": str(snapshot), "sha256": sha(snapshot)},
            }
            if profile == "incremental":
                receipt.update(integrity_root=cp["integrity_root"], journal=journal_receipt)
            receipt["receipt_sha256"] = digest(receipt)
            write_json(attempt / f"checkpoint-{n}.receipt.json", receipt)
            previous, completed = receipt["receipt_sha256"], n
            if stop_after_checkpoint == n:
                break
        verify_boundary("completion" if completed == len(items) else "pause")
        result = {
            "status": "complete" if completed == len(items) else "paused_at_checkpoint",
            "completed_checkpoint": completed,
            "cell": manifest["cell"],
            "run_dir": str(run),
            "attempt_dir": str(attempt),
            "last_receipt_sha256": previous,
            "banner": meta["banner"],
            "manifest_sha256": expected_sha256,
            "integrity_profile": profile,
            "phase_timer_summary": phase_summary(timed_rows),
            "phase_timer_scope": "this attempt, verification/clone/operation/restore; excludes phase-file writes and admission/resume",
            "attempt_wall_seconds": time.monotonic() - attempt_started,
            "prior_attempt_timer_summary": prior_timer_summary(run, exclude=attempt),
            "detailed_phase_timers": detailed_timers,
            "boundary_identity_checks": boundary_identity_checks,
            "boundary_identity_seconds": sum(row["seconds"] for row in boundary_identity_checks),
            "identity_policy": "full rehash at attempt start, resume after restore, every checkpoint before receipt, and completion; cheap immutable memory check each phase",
        }
        write_json(attempt / "result.json", result)
        return result
    except BaseException as exc:
        if journal is not None:
            journal.flush()
        write_json(
            attempt / "failure.json",
            {
                "status": "error",
                "error_type": type(exc).__name__,
                "reason": str(exc),
                "last_completed_checkpoint": completed,
                "last_receipt_sha256": previous,
                "attempted_item_ids": [r["item_id"] for r in history],
                "ledger_at_failure": _ledger(adapter),
                "integrity_profile": profile,
                "boundary_identity_checks": boundary_identity_checks,
                "phase_timer_summary": phase_summary(timed_rows),
                "attempt_wall_seconds": time.monotonic() - attempt_started,
                "recovery": "resume from last complete receipt; retain this attempt's charged work",
            },
        )
        raise


def prior_timer_summary(run, *, exclude):
    rows = []
    for attempt in sorted(Path(run).glob("attempt-*")):
        if attempt == exclude or not attempt.is_dir():
            continue
        phases = attempt / "phases"
        if list(phases.glob("*.intent.json")):
            rows.extend(DurablePhaseJournal.verify(phases))
        else:
            rows.extend(json.loads(path.read_text()) for path in sorted(phases.glob("[0-9]*.json")))
    return phase_summary(rows)


def construct_owner_adapter(m):
    """Preserve the continued-NPZ S1 path without any development admission."""
    from scripts.r1_61_cell_driver import _snapshot
    from scripts.r1_61_cell_driver import construct_owner_adapter as standard

    spec = m["construction"]
    if "continued_weights" not in spec:
        return standard(m)
    if m["cell"]["condition"] not in ("S1_LM", "S1_literal"):
        raise ValueError("continued NPZ permitted only for S1")
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import BPBase
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.stage4_adapters import build_adapter

    base_path, original_path = _snapshot(spec["base"]), _snapshot(spec["original_base"])
    weight = Path(spec["continued_weights"]["path"]).resolve()
    if (
        not weight.is_relative_to(ROOT.parent / "assets")
        or sha(weight) != spec["continued_weights"]["sha256"]
    ):
        raise ValueError("continued base NPZ identity/location mismatch")
    if sha(original_path / "tokenizer.json") != m["tokenizer_sha256"]:
        raise ValueError("tokenizer identity mismatch")
    params = g.load_params_npz(weight)
    ledger = Ledger()
    base = BPBase(snapshot=base_path, params_np=params, ledger=ledger)
    original = BPBase(snapshot=original_path, ledger=ledger)
    tok = GPT2Tokenizer(snapshot=original_path)
    adapter = build_adapter(
        m["cell"]["condition"],
        base,
        ledger,
        calibration=spec["calibration"],
        seed=spec["seed"],
        budget=Budget(**spec["budget"]),
        locality_base=original,
    )
    if adapter.identity() != m["adapter_identity"]:
        raise ValueError("constructed S1 identity mismatch")
    return adapter, tok


def execute(
    path,
    expected_sha256,
    *,
    resume=False,
    factory=None,
    code_root=None,
    output_root=None,
    resource_root=None,
    receipt_root=None,
    stop_after_checkpoint=None,
):
    """All construction/admission/failure time is inside a durable envelope.

    The queue charges its larger child-process envelope instead, never both.
    An unfinished envelope means unknown spend and blocks automatic resume.
    """
    output_root = OUTPUT_ROOT if output_root is None else Path(output_root).resolve()
    resource_root = RESOURCE_ROOT if resource_root is None else Path(resource_root).resolve()
    receipt_root = RECEIPT_ROOT if receipt_root is None else Path(receipt_root).resolve()
    if output_root != OUTPUT_ROOT or resource_root != RESOURCE_ROOT:
        raise PermissionError("canonical sealed output/resource roots required")
    if not receipt_root.is_relative_to(ROOT / "logs"):
        raise PermissionError("execution cost receipts belong in repo logs")
    receipt_root.mkdir(parents=True, exist_ok=True)
    folder = receipt_root / uuid.uuid4().hex
    durable_directory(folder)
    start = {
        "recipe": {"path": str(Path(path).resolve()), "sha256": expected_sha256},
        "resume": resume,
        "backend": backend_binding(),
        "started_unix": time.time(),
    }
    begun = time.monotonic()
    durable_json(folder / "start.json", start)
    fd = None
    status, error, result = "failed", None, None
    try:
        deadline_check()
        m = inspect_manifest(path, expected_sha256, code_root=code_root)
        from scripts.r1_75_analysis_stage4_v1 import coordinate_id

        locks = ROOT / "logs/r1_77b_locks"
        locks.mkdir(parents=True, exist_ok=True)
        fd = os.open(locks / (coordinate_id(m["cell"]) + ".lock"), os.O_RDONLY | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for prior in receipt_root.glob("*/start.json"):
            if prior.parent == folder:
                continue
            old = json.loads(prior.read_text())
            if old.get("recipe") == start["recipe"] and not (prior.parent / "finish.json").exists():
                raise ValueError("unknown prior execution cost requires owner reconciliation")
        m, _ = load_sealed_cell(path, expected_sha256, code_root=code_root, allow_sealed=True)
        run = output_root / cell_name(m, expected_sha256)
        if resume and any(run.glob("attempt-*/result.json")):
            if any(
                json.loads(p.read_text()).get("status") == "complete"
                for p in run.glob("attempt-*/result.json")
            ):
                raise ValueError("already complete; duplicate completed attempt refused")
        adapter, tok = (construct_owner_adapter if factory is None else factory)(m)
        result = _run_sealed_cell(
            path,
            expected_sha256,
            adapter,
            tok,
            output_root=output_root,
            resource_root=resource_root,
            code_root=code_root,
            resume=resume,
            allow_sealed=True,
            stop_after_checkpoint=stop_after_checkpoint,
        )
        status = result["status"]
        return result
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        if fd is not None:
            os.close(fd)
        durable_json(
            folder / "finish.json",
            {
                **start,
                "status": status,
                "error": error,
                "start_sha256": sha(folder / "start.json"),
                "charged_process_wall_seconds": time.monotonic() - begun,
                "cost_scope": "backend admission, construction, resume and all successful/failed execution; queue envelope supersedes this",
                "attempt_dir": None if result is None else result["attempt_dir"],
            },
        )


def inspect(path, expected_sha256, *, code_root=None):
    m = inspect_manifest(path, expected_sha256, code_root=code_root)
    name = cell_name(m, expected_sha256)
    return {
        "mode": MODE,
        "cell": m["cell"],
        "backend": m["backend"],
        "freeze": m["freeze"],
        "payload_read": False,
        "model_constructed": False,
        "result_dir": str(OUTPUT_ROOT / name),
        "resource_dir": str(RESOURCE_ROOT / name),
        "recipe_contract_sha256": contract_digest(m),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    if args.resume and not args.execute:
        parser.error("--resume requires --execute")
    result = (
        execute(args.manifest, args.manifest_sha256, resume=args.resume)
        if args.execute
        else inspect(args.manifest, args.manifest_sha256)
    )
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
