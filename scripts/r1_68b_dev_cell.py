"""R1-68b opt-in development driver, with full profile as the default.

The current/sealed drivers are untouched. Recipes bind these additional files
explicitly. Batched accounting refuses an unclosed intent on automatic resume.
"""

from __future__ import annotations

import copy
import json
import os
import time
from pathlib import Path

from scripts.r1_68b_integrity_runtime import (
    DurablePhaseJournal,
    IndexedAdapter,
    durable_directory,
    durable_json,
    phase_summary,
)

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


DRIVER_FILES = ("scripts/r1_68b_dev_cell.py", "scripts/r1_68b_integrity_runtime.py")
UPSTREAM_ENGINE_SHA256 = "5f50698c1c43e2bf218e0d5a9f763e233363623369c4776e3815cccfad5674da"


def driver_bindings(root=ROOT):
    return {name: sha(Path(root) / name) for name in DRIVER_FILES}


def profile_config(manifest, root=ROOT):
    if sha(Path(root) / "src/pccap/revision_v1/development_cell.py") != UPSTREAM_ENGINE_SHA256:
        raise ValueError(
            "upstream development engine changed; reconcile this opt-in fork before use"
        )
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
    return profile, batch


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
    manifest, payload = load_development_cell(
        manifest_path, expected_sha256, code_root=code_root, allow_sealed=allow_sealed
    )
    profile, batch_edits = profile_config(manifest, code_root)
    if profile == "incremental":
        adapter = IndexedAdapter(adapter)
    identity = adapter.identity()
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
    assays = CellAssays(adapter, tokenizer, max_new=manifest["max_new"])
    phase_index = 0

    def verify_inputs():
        load_development_cell(
            manifest_path, expected_sha256, code_root=code_root, allow_sealed=allow_sealed
        )
        if adapter.identity() != identity:
            raise ValueError("immutable adapter identity changed")

    def phase(label, operation, *, learning=False):
        nonlocal phase_index
        phase_started = time.monotonic()
        led0 = _ledger(adapter)
        if journal is not None:
            journal.before_phase(label, led0)
        verify_inputs()
        fast = profile == "incremental" and label.split(":", 1)[0] in ("edit", "immediate")
        before = adapter.root() if fast else adapter.state_hash()
        snapshot = None if fast else adapter.export_state().clone()
        assays.events = []
        operation_started = time.monotonic()
        operation_seconds = 0.0
        result, error = None, None
        try:
            try:
                result = operation()
            finally:
                operation_seconds = time.monotonic() - operation_started
            after = adapter.root() if fast else adapter.state_hash()
            if not learning and after != before:
                raise RuntimeError("endpoint mutated checkpoint state")
            if adapter.identity() != identity:
                raise RuntimeError("endpoint/update mutated immutable parameters")
            return result
        except BaseException as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            observed = adapter.root() if fast else adapter.state_hash()
            restore_required = snapshot is not None and (not learning or error is not None)
            if restore_required:
                adapter.import_state(snapshot)
                if adapter.state_hash() != before:
                    raise RuntimeError("phase restore mismatch")
            else:
                adapter.reset_queries()
            rec = {
                "phase": label,
                "learning": learning,
                "state_before": before,
                "state_after_operation": observed,
                "state_after_restore": adapter.root() if fast else adapter.state_hash(),
                "state_hash_convention": "record-digest-v1" if fast else "legacy-state-sha256",
                "restore_required": restore_required,
                "status": "error" if error else "ok",
                "error": error,
                "ledger_delta": _delta(led0, _ledger(adapter)),
                "returned_events": copy.deepcopy(assays.events),
                "wall_seconds": time.monotonic() - operation_started,
                "phase_wall_seconds": time.monotonic() - phase_started,
                "operation_seconds": operation_seconds,
                "cost_policy": "shared ledger deltas and returned counters separate; failed attempts retained",
                "mutation_inventory": adapter.drain_mutations()
                if profile == "incremental"
                else None,
            }
            if journal is None:
                write_json(events / f"{phase_index:06d}.json", rec)
            else:
                journal.add(rec)
            timed_rows.append(rec)
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
                    f"drift:{n}", lambda ep=ep: assays.drift(ep["drift"])
                )
            cp["observation"] = adapter.observe()
            cp["state_sha256"] = adapter.state_hash()
            verify_inputs()
            if profile == "incremental":
                cp["integrity_root"] = adapter.verify()
            blob = serialize(adapter.export_state())
            restored = restore(blob, expected_hash=cp["state_sha256"])
            adapter.import_state(restored)
            if adapter.state_hash() != cp["state_sha256"]:
                raise RuntimeError("checkpoint serialization/restore mismatch")
            if profile == "incremental" and adapter.verify() != cp["integrity_root"]:
                raise RuntimeError("checkpoint incremental restore mismatch")
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
