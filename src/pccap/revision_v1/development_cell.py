"""R1-64 development runner. Explicit fork of the R1-61 checkpoint engine.

The local engine retains receipt/resume and cost semantics without changing the
sealed runner. Structural validation is shared; admission is separate. Future
engine changes should be reconciled in both modules with explicit permission.
"""

from __future__ import annotations

import copy
import json
import time
from pathlib import Path

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
from pccap.revision_v1.stage4_cell import (
    write_json as plain_write_json,
)

MODE = "stage4_development_cell"
BANNER = "development, not confirmatory"
PAYLOAD_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/stage4_dev_payloads"
OUTPUT_ROOT = ROOT / "results/R1/stage4_dev_cells"
RESOURCE_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/stage4_dev_cells"


def code_identity(root=ROOT):
    root = Path(root)
    return digest(
        {
            "core": core_code_identity(root),
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
    return plain_write_json(path, value)


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
    history, completed, previous = [], 0, None
    if not resume:
        run.mkdir(parents=True, exist_ok=False)
        resources.mkdir(parents=True, exist_ok=False)
        blob = serialize(fresh_state)
        with (resources / "initial.snapshot").open("xb") as f:
            f.write(blob)
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
    attempts = [p for p in run.glob("attempt-*") if p.is_dir()]
    attempt = run / f"attempt-{len(attempts):04d}"
    attempt.mkdir(exist_ok=False)
    resource_attempt = resources / attempt.name
    resource_attempt.mkdir(exist_ok=False)
    events = attempt / "phases"
    events.mkdir(exist_ok=False)
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
        verify_inputs()
        before = adapter.state_hash()
        snapshot = adapter.export_state().clone()
        led0 = _ledger(adapter)
        assays.events = []
        start = time.monotonic()
        result, error = None, None
        try:
            result = operation()
            after = adapter.state_hash()
            if not learning and after != before:
                raise RuntimeError("endpoint mutated checkpoint state")
            if adapter.identity() != identity:
                raise RuntimeError("endpoint/update mutated immutable parameters")
            return result
        except BaseException as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            observed = adapter.state_hash()
            if not learning or error is not None:
                adapter.import_state(snapshot)
                if adapter.state_hash() != before:
                    raise RuntimeError("phase restore mismatch")
            rec = {
                "phase": label,
                "learning": learning,
                "state_before": before,
                "state_after_operation": observed,
                "state_after_restore": adapter.state_hash(),
                "restore_required": not learning or error is not None,
                "status": "error" if error else "ok",
                "error": error,
                "ledger_delta": _delta(led0, _ledger(adapter)),
                "returned_events": copy.deepcopy(assays.events),
                "wall_seconds": time.monotonic() - start,
                "cost_policy": "shared ledger deltas and returned counters are separate, never summed together; failed attempts retained",
            }
            write_json(events / f"{phase_index:06d}.json", rec)
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
            blob = serialize(adapter.export_state())
            snapshot = resource_attempt / f"checkpoint-{n}.snapshot"
            with snapshot.open("xb") as f:
                f.write(blob)
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
        }
        write_json(attempt / "result.json", result)
        return result
    except BaseException as exc:
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
                "recovery": "resume from last complete receipt; retain this attempt's charged work",
            },
        )
        raise
