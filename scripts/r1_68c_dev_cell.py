"""R1-68c development driver: measured phase scopes and opt-in read-only/batch path.

Full preserves scalar assays and defensive clones. Incremental removes only
read-only outer clones, retains state/identity checks and batches drift prefixes.
"""

from __future__ import annotations

import copy
import json
import os
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path

from scripts import r1_68f_full_validation as full_validation
from scripts.r1_68b_integrity_runtime import (
    DurablePhaseJournal,
    IndexedAdapter,
    durable_directory,
    durable_json,
    phase_summary,
)
from scripts.r1_68c_batched_drift import batched_drift
from scripts.r1_68e_batched_drift_v0 import CONDITION_CLASSES, IMPLEMENTATION
from scripts.r1_68e_batched_drift_v0 import batched_drift as v0_batched_drift

from pccap.harness.snapshot import restore, serialize
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.endpoints import EndpointResourceFailure
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.stage4_assays import CellAssays
from pccap.revision_v1.stage4_cell import (
    ROOT,
    _delta,
    _ledger,
    cell_name,
    read_binding,
    sha,
    validate_payload,
)
from pccap.revision_v1.stage4_cell import (
    code_identity as core_code_identity,
)

MODE = "stage4_development_cell"
BANNER = "development, not confirmatory"
PAYLOAD_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/stage4_dev_payloads"
OUTPUT_ROOT = ROOT / "results/R1/stage4_dev_cells"
RESOURCE_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/stage4_dev_cells"


DRIVER_FILES = (
    "scripts/r1_68b_dev_cell.py",
    "scripts/r1_68b_integrity_runtime.py",
    "scripts/r1_68c_dev_cell.py",
    "scripts/r1_68c_batched_drift.py",
    "scripts/r1_68e_batched_drift_v0.py",
    "scripts/r1_68f_full_validation.py",
)
PARENT_DRIVER_SHA256 = "a8dca04986085aebb53706439e76bf8ced083b4e86424fbf9965edc4105c9fc5"
UPSTREAM_ENGINE_SHA256 = "5f50698c1c43e2bf218e0d5a9f763e233363623369c4776e3815cccfad5674da"


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


def driver_bindings(root=ROOT):
    return {name: sha(Path(root) / name) for name in DRIVER_FILES}


def profile_config(manifest, root=ROOT):
    if sha(Path(root) / "src/pccap/revision_v1/development_cell.py") != UPSTREAM_ENGINE_SHA256:
        raise ValueError(
            "upstream development engine changed; reconcile this opt-in fork before use"
        )
    if sha(Path(root) / "scripts/r1_68b_dev_cell.py") != PARENT_DRIVER_SHA256:
        raise ValueError("parent driver changed; reconcile R1-68c before use")
    drift_batch = manifest.get("drift_batch_size", 16)
    if type(drift_batch) is not int or not 1 <= drift_batch <= 32:
        raise ValueError("drift_batch_size must be an integer in [1,32]")
    profile = manifest.get("integrity_profile", "full")
    batch = manifest.get("integrity_batch_edits", 16)
    if profile not in ("full", "incremental"):
        raise ValueError("integrity_profile must be full or incremental")
    if type(batch) is not int or not 1 <= batch <= 1000:
        raise ValueError("integrity_batch_edits must be an integer in [1, 1000]")
    if manifest.get("integrity_driver_bindings") != driver_bindings(root):
        raise ValueError("incremental-capable driver source bindings mismatch")
    if profile == "incremental" and not manifest["cell"]["condition"].startswith("R1_"):
        raise ValueError("incremental profile supports only audited RevisionCap conditions")
    implementation = manifest.get("drift_implementation", "profile_default")
    if implementation not in ("profile_default", IMPLEMENTATION):
        raise ValueError("unsupported drift implementation")
    if implementation == IMPLEMENTATION and (
        profile != "full" or manifest["cell"]["condition"] not in CONDITION_CLASSES
    ):
        raise ValueError("v0 batch drift requires a v0-family condition and full integrity")
    full_validation.validate_spec(manifest)
    return profile, batch


def run_drift_assay(assays, definition, manifest, profile):
    implementation = manifest.get("drift_implementation", "profile_default")
    if implementation == IMPLEMENTATION:
        return v0_batched_drift(
            assays, definition, batch_size=manifest.get("drift_batch_size", 16)
        )
    if implementation != "profile_default":
        raise ValueError("unsupported drift implementation")
    if profile == "incremental":
        return batched_drift(
            assays, definition, batch_size=manifest.get("drift_batch_size", 16)
        )
    return assays.drift(definition)


def code_identity(root=ROOT):
    root = Path(root)
    return digest(
        {
            "core": core_code_identity(root),
            "integrity_driver": driver_bindings(root),
            "development_scripts": {
                n: sha(root / n)
                for n in (
                    "scripts/r1_64_dev_payload.py",
                    "scripts/r1_64_dev_cell.py",
                    "scripts/r1_64_materialize_base.py",
                )
            },
        }
    )


def write_json(path, value):
    # Stamp before hashing a receipt; preserve caller's chain hash.
    value.update(mode=MODE, banner=BANNER)
    if "receipt_sha256" in value:
        value["receipt_sha256"] = digest({k: v for k, v in value.items() if k != "receipt_sha256"})
    return durable_json(path, value)


def validate_development_payload(manifest, payload):
    if manifest.get("mode") != MODE or manifest.get("schema_version") != 1:
        raise ValueError("development recipe required")
    if "reservations" in manifest or "protocol" in manifest:
        raise PermissionError(
            "development cannot reference a sealed reservation or frozen protocol"
        )
    if any(v is not False for v in manifest.get("admission", {}).values()):
        raise PermissionError("development refuses every true or ambiguous admission flag")
    fixture = manifest.get("test_fixture", False)
    if type(fixture) is not bool:
        raise ValueError("test_fixture must be boolean")
    if fixture:
        if manifest["adapter_identity"]["base_sha256"] != "tiny":
            raise ValueError("test fixture requires the TinyBase identity")
    else:
        count = len(payload["items"])
        expected = [n for n in (100, 300, 1000) if n <= count]
        if (
            count not in (100, 300, 1000)
            or manifest["checkpoints"] != expected
            or manifest["max_new"] != 32
        ):
            raise ValueError(
                "development checkpoints must be 100, 100/300, or 100/300/1000 with max_new=32"
            )
        if any(not r.get("paraphrases") for r in payload["items"]):
            raise ValueError("development RET-GS requires paraphrases")
    if payload.get("mode") != MODE or payload.get("banner") != BANNER:
        raise ValueError("unsealed development payload stamp required")
    # Only reuse common inventory checks. The synthetic branch is the existing
    # validator's public way to omit sealed allocations and fixed 1000 cadence.
    validate_payload({**manifest, "mode": "synthetic"}, payload)
    full_validation.validate_sample(manifest, payload["endpoints"]["drift"])
    return payload


def load_development_cell(manifest_path, expected_sha256, *, code_root=ROOT, allow_sealed=False):
    if allow_sealed:
        raise PermissionError("development never allows sealed payloads")
    m = read_binding({"path": str(manifest_path), "sha256": expected_sha256})
    profile_config(m, code_root)
    if (
        m.get("mode") != MODE
        or any(v is not False for v in m.get("admission", {}).values())
        or "reservations" in m
        or "protocol" in m
    ):
        raise PermissionError("development only, with all admission flags absent or false")
    if m["code_sha256"] != code_identity(code_root):
        raise ValueError("installed development code identity mismatch")
    p = Path(m["payload"]["path"]).resolve()
    if not p.is_relative_to(PAYLOAD_ROOT):
        raise PermissionError(
            "payload must be in the explicit unsealed development resource directory"
        )
    for name, expected in m.get("source_bindings_sha256", {}).items():
        source = Path(name).resolve()
        allowed = (
            source.is_relative_to(ROOT / "manifests/dev")
            or source.is_relative_to(ROOT / "manifests/revision_v1")
            or source.is_relative_to(ROOT.parent / "assets/data/prepared")
        )
        if not allowed or "confirm" in source.parts or sha(source) != expected:
            raise ValueError("development source path/hash mismatch")
    payload = read_binding(m["payload"])
    validate_development_payload(m, payload)
    return m, payload


def run_development_cell(
    manifest_path,
    expected_sha256,
    adapter,
    tokenizer,
    *,
    output_root,
    resource_root,
    code_root=ROOT,
    resume=False,
    allow_sealed=False,
    stop_after_checkpoint=None,
):
    """Run one cell; each attempt/phase/checkpoint is a new file, never appended.

    A complete checkpoint receipt is written last and binds both the report and
    snapshot. Interrupted work remains in its attempt directory and stays in
    resource accounting. Resume restores only a contiguous verified prefix.
    """
    admission_started = time.monotonic()
    manifest, payload = load_development_cell(
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
    if not root.is_relative_to(ROOT / "results/R1/stage4_dev_cells") or not assets.is_relative_to(
        ROOT.parent / "assets"
    ):
        raise ValueError("outputs belong in pc_cap; snapshot resources belong in assets")
    name = cell_name(manifest, expected_sha256)
    run, resources = root / name, assets / name
    if not manifest.get("test_fixture", False) and (
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
        load_development_cell(
            manifest_path, expected_sha256, code_root=code_root, allow_sealed=allow_sealed
        )
        if adapter.identity() != identity:
            raise ValueError("immutable adapter identity changed")
        if memory_identity(adapter) != memory_fingerprint:
            raise ValueError("immutable in-memory identity changed")

    def verify_boundary(label):
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
                    lambda ep=ep: run_drift_assay(assays, ep["drift"], manifest, profile),
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
                    lambda ep=ep: run_drift_assay(assays, ep["drift"], manifest, profile),
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


def main(argv=None):
    import argparse

    from scripts.r1_61_cell_driver import construct_owner_adapter

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    manifest, payload = load_development_cell(args.manifest, args.manifest_sha256)
    if args.resume and not args.execute:
        parser.error("--resume requires --execute")
    if not args.execute:
        print(
            json.dumps(
                {
                    "mode": MODE,
                    "cell": manifest["cell"],
                    "integrity_profile": profile_config(manifest)[0],
                    "items": len(payload["items"]),
                    "model_constructed": False,
                },
                indent=2,
            )
        )
        return 0
    if manifest.get("test_fixture"):
        parser.error("TinyBase fixtures use the Python API")
    adapter, tokenizer = construct_owner_adapter(manifest)
    result = run_development_cell(
        args.manifest,
        args.manifest_sha256,
        adapter,
        tokenizer,
        output_root=OUTPUT_ROOT,
        resource_root=RESOURCE_ROOT,
        resume=args.resume,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
