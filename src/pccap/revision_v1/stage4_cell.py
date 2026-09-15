"""R1-61: one immutable-output Stage 4 cell, with checkpoint-prefix resume.

Model construction is separate from admission. This module never draws or seals
data. The caller supplies an already constructed, identity-bound adapter.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import time
from pathlib import Path

from pccap.harness.snapshot import restore, serialize
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.endpoints import EndpointResourceFailure
from pccap.revision_v1.endpoints_composition import as_edit, dependency_ids
from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS, SECONDARY_CONDITION
from pccap.revision_v1.stage4_assays import CellAssays

ROOT = Path(__file__).resolve().parents[3]
CHECKPOINTS = (100, 300, 1000)
KINDS = ("locality", "unseen", "near_miss", "revision", "composition")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def code_identity(root=ROOT):
    root = Path(root)
    paths = list((root / "src/pccap").rglob("*.py")) + [root / "scripts/r1_61_cell_driver.py"]
    if not paths or any(not p.is_file() for p in paths):
        raise ValueError("incomplete installed code inventory")
    return digest({str(p.relative_to(root)): sha(p) for p in sorted(paths)})


def read_binding(binding):
    p = Path(binding["path"])
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError("bound input hash mismatch: " + str(p))
    return json.loads(raw)


def write_json(path, value):
    path = Path(path)
    with path.open("x") as f:
        f.write(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    return {"path": str(path.resolve()), "sha256": sha(path)}


def _unique(ids, name, *, allow_empty=False):
    if (
        not isinstance(ids, list)
        or (not ids and not allow_empty)
        or any(not isinstance(i, str) or not i for i in ids)
        or len(set(ids)) != len(ids)
    ):
        raise ValueError("unique explicit identities required: " + name)
    return ids


def validate_payload(manifest, payload):
    cell = manifest["cell"]
    if set(cell) != {"condition", "dataset", "realization", "order"}:
        raise ValueError("four cell axes required")
    if cell["condition"] not in (*CORE_CONDITIONS, SECONDARY_CONDITION) or cell["dataset"] not in (
        "zsre",
        "counterfact",
        "mquake",
        "synthetic",
    ):
        raise ValueError("unknown cell condition/dataset")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", str(v)) for v in cell.values()):
        raise ValueError("unsafe cell label")
    items = payload["items"]
    ids = _unique([r["item_id"] for r in items], "edit stream")
    if any(r["dataset"] != cell["dataset"] for r in items):
        raise ValueError("cross-dataset item in stream")
    if len({r["fact_id"] for r in items}) != len(items):
        raise ValueError("fresh stream must contain unique facts")
    subjects = [" ".join(r["subject"].casefold().split()) for r in items]
    if len(set(subjects)) != len(subjects):
        raise ValueError("fresh stream must contain unique subjects")
    cps = manifest["checkpoints"]
    if (
        not isinstance(cps, list)
        or any(type(n) is not int or not 0 < n <= len(ids) for n in cps)
        or cps != sorted(set(cps))
        or not cps
        or cps[-1] != len(ids)
    ):
        raise ValueError("checkpoints must be increasing and end at the full stream")
    if type(manifest["max_new"]) is not int or not 1 <= manifest["max_new"] <= 32:
        raise ValueError("invalid greedy token limit")
    real = manifest["mode"] != "synthetic"
    if real and (cps != list(CHECKPOINTS) or manifest["max_new"] != 32):
        raise ValueError("registered checkpoints and 32-token decoder required")
    if real and any(not r.get("paraphrases") for r in items):
        raise ValueError("registered RET-GS requires paraphrases for every item")
    eps = payload["endpoints"]
    for kind in KINDS:
        ep = eps[kind]
        expected = _unique(ep["expected_ids"], kind, allow_empty=kind == "composition")
        key = "composition_id" if kind == "composition" else "item_id"
        observed = _unique([r[key] for r in ep["rows"]], kind + " rows", allow_empty=True)
        if observed != [i for i in expected if i in set(observed)]:
            raise ValueError(
                "endpoint identities/order differ from independently planned inventory"
            )
    pool = {r["item_id"]: r for r in payload["pool_rows"]}
    if len(pool) != len(payload["pool_rows"]) or any(i not in pool for i in ids):
        raise ValueError("unique pool must cover every attempted edit")
    for row in items:
        if any(pool[row["item_id"]][k] != row[k] for k in ("fact_id", "subject", "prompt")):
            raise ValueError("pool metadata differs from stream payload")
    outside = eps["unseen"]["expected_ids"]
    if set(outside) & set(ids) or any(i not in pool for i in outside):
        raise ValueError("outside inventory must exclude the entire edit stream")
    for row in eps["unseen"]["rows"]:
        if row["prompt"] != pool[row["item_id"]]["prompt"]:
            raise ValueError("outside query differs from bound pool")
    for case in eps["composition"]["rows"]:
        if not set(dependency_ids(case)) <= set(ids):
            raise ValueError("composition dependency outside this realization")
    drift = eps["drift"]
    if type(drift["expected_positions"]) is not int or drift["expected_positions"] < 1:
        raise ValueError("positive drift position denominator required")
    if any(
        not isinstance(w, list) or len(w) < 2 or any(type(t) is not int or t < 0 for t in w)
        for w in drift["windows"]
    ):
        raise ValueError("invalid drift token windows")
    if sum(len(w) - 1 for w in drift["windows"]) > drift["expected_positions"]:
        raise ValueError("drift exceeds planned positions")
    if real:
        res = read_binding(manifest["reservations"])
        if res.get("mode") != "content_sealed_fact_reservations":
            raise ValueError("sealed R1-58 fact reservations required")
        groups = [
            g
            for g in res["allocations"]
            if g["dataset"] == cell["dataset"] and str(g["realization"]) == str(cell["realization"])
        ]
        roles = {g["role"]: g for g in groups}
        if len(roles) != len(groups) or not {"edits", "outside"} <= set(roles):
            raise ValueError("missing or duplicate reservation roles")
        reserved = {r["item_id"]: r for r in roles["edits"]["items"]}
        if set(reserved) != set(ids):
            raise ValueError("stream differs from reserved edit membership")
        if any(content_digest(r) != reserved[r["item_id"]]["payload_sha256"] for r in items):
            raise ValueError("reserved edit payload identity mismatch")
        if set(outside) != {r["item_id"] for r in roles["outside"]["items"]}:
            raise ValueError("outside inventory differs from reserved membership")
        if content_digest(payload["endpoints"]) != manifest["admission"]["endpoint_bundle_sha256"]:
            raise ValueError("constructed endpoint bundle not independently admitted")
        if digest(ids) != manifest["admission"]["ordered_item_ids_sha256"]:
            raise ValueError("order not independently admitted")
    return payload


def load_cell(manifest_path, expected_sha256, *, code_root=ROOT, allow_sealed=False):
    manifest = read_binding({"path": str(manifest_path), "sha256": expected_sha256})
    if manifest.get("schema_version") != 1 or manifest.get("mode") not in (
        "synthetic",
        "stage4_sealed_cell",
    ):
        raise ValueError(
            "Stage 4 cell recipe required; fact reservations alone are not a launch seal"
        )
    if manifest["code_sha256"] != code_identity(code_root):
        raise ValueError("installed code identity mismatch")
    if manifest["mode"] != "synthetic":
        if not allow_sealed:
            raise PermissionError("sealed payload access requires owner execution")
        admission = manifest.get("admission", {})
        if any(
            admission.get(k) is not True
            for k in ("lead_approved", "protocol_frozen", "condition_admitted", "launch_authorized")
        ):
            raise PermissionError("unresolved scientific launch admission")
        read_binding(manifest["protocol"])
    payload = read_binding(manifest["payload"])
    validate_payload(manifest, payload)
    return manifest, payload


def cell_name(manifest, manifest_sha256):
    c = manifest["cell"]
    key = digest({"manifest_sha256": manifest_sha256, "cell": c})
    return (
        "-".join(str(c[k]) for k in ("condition", "dataset", "realization", "order"))
        + "-"
        + key[:20]
    )


def _ledger(adapter):
    return adapter.ledger.totals() if adapter.ledger is not None else None


def _delta(before, after):
    if before is None:
        return None
    return {
        p: {
            k: after[p][k] - v
            for k, v in before[p].items()
            if isinstance(v, (int, float)) and k != "peak_mem_mib"
        }
        for p in ("learning", "query", "total")
    }


def run_cell(
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
    manifest, payload = load_cell(
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
    if not root.is_relative_to(ROOT) or not assets.is_relative_to(ROOT.parent / "assets"):
        raise ValueError("outputs belong in pc_cap; snapshot resources belong in assets")
    name = cell_name(manifest, expected_sha256)
    run, resources = root / name, assets / name
    if manifest["mode"] != "synthetic" and (
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
        "banner": "NOT CONFIRMATORY — synthetic execution"
        if manifest["mode"] == "synthetic"
        else "admitted Stage 4 cell",
    }
    history, completed, previous = [], 0, None
    if not resume:
        run.mkdir(parents=True, exist_ok=False)
        resources.mkdir(parents=True, exist_ok=False)
        blob = serialize(fresh_state)
        with (resources / "initial.snapshot").open("xb") as f:
            f.write(blob)
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
        load_cell(manifest_path, expected_sha256, code_root=code_root, allow_sealed=allow_sealed)
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
