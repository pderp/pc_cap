"""X22: immutable block-1 execution, checkpoint, cost and watch audit.

Sealed payloads and adapter snapshots are streamed only into SHA256. No model
is loaded and no live file is written. Historical watch views are replayed from
their exact append-only journal prefixes, rather than compared with live views.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts import ht8_fidelity_watch as watch  # noqa: E402
from scripts import r1_77_queue as queue  # noqa: E402
from scripts.r1_68b_integrity_runtime import DurablePhaseJournal  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCES = {}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ref(path):
    path = Path(path).resolve()
    result = dict(path=str(path), sha256=sha(path))
    require(str(path) not in SOURCES or SOURCES[str(path)] == result["sha256"], "source changed")
    SOURCES[str(path)] = result["sha256"]
    return result


def read(binding):
    if not isinstance(binding, dict):
        binding = ref(binding)
    require(ref(binding["path"])["sha256"] == binding["sha256"], "binding changed: " + binding["path"])
    return json.loads(Path(binding["path"]).read_bytes())


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def close(a, b, message):
    require(math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-6), message)


def main():
    bindings_ref = ref(ROOT / "docs/tasks/R1-final-queue-bindings.json")
    bindings = read(bindings_ref)
    matrix = read(bindings["matrix"])
    frozen = read(bindings["freeze"])
    selected = [c for c in queue.analysis.all_cells(matrix) if c["block_number"] == 1]
    require(len(selected) == 45 and {c["realization"] for c in selected} == {0}, "block membership differs")
    native = read(HERE / "analysis.json")
    observed = {c["cell_id"]: c for c in native["cells"]}
    for path, expected in native["sources_sha256"].items():
        require(ref(path)["sha256"] == expected, "native analysis source changed")
    historical = read(ROOT / "logs/R1/operator_reports/20260919-block1-try1/report.json")
    require(watch.full.digest({k: v for k, v in historical.items() if k != "report_sha256"}) == historical["report_sha256"], "D11 digest differs")
    prior_costs = {r["cell_id"]: r for r in historical["cost_ledger"]["rows"]}
    receipt_root = ROOT / "logs/R1/final_queue"
    selected_ids = {c["cell_id"] for c in selected}
    starts = {}
    # Directory membership is restricted by cell identity; later workers are not inputs.
    for path in sorted(receipt_root.glob("*/start.json")):
        start = json.loads(path.read_bytes())
        if start.get("cell_id") in selected_ids:
            starts.setdefault(start["cell_id"], []).append(path)
    require(set(starts) == selected_ids and all(len(v) == 1 for v in starts.values()), "missing or duplicate block-1 process")
    journal_path = ROOT / "results/R1/fidelity_watch/observations.jsonl"
    # Read once; later complete appended events do not change selected prefixes.
    raw = journal_path.read_bytes()
    require(not raw or raw.endswith(b"\n"), "torn live watch read; retry")
    lines = raw.splitlines(keepends=True)
    events = [json.loads(line) for line in lines]
    watch.replay(events)
    prefix_hashes, running = {}, hashlib.sha256()
    for i, line in enumerate(lines, 1):
        running.update(line)
        prefix_hashes[running.hexdigest()] = i
    by_watch_id = {e["observation"]["cell_id"]: e for e in events}
    document_contexts = {}
    commits = subprocess.check_output(
        ["git", "log", "--format=%H", "--", "docs/fidelity_watch.md"], cwd=ROOT, text=True
    ).splitlines()
    for commit in commits:
        document = subprocess.check_output(["git", "show", commit + ":docs/fidelity_watch.md"], cwd=ROOT).decode()
        if watch.BEGIN not in document:
            continue
        before, rest = document.split(watch.BEGIN)
        _, after = rest.split(watch.END)
        context = dict(before=before, after=after.lstrip("\n"))
        document_contexts[watch.full.digest(context)] = dict(context, commit=commit)
    rows, payloads, phases, latest_prefix = [], set(), 0, 0
    for index, cell in enumerate(selected, 1):
        cid = cell["cell_id"]
        item = observed[cid]
        require(item["artifact_complete"] and item["primary_metrics_complete"] and item["scientific_admission"] and item["endpoint_complete"], "native analysis incomplete: " + cid)
        recipe_binding = bindings["recipes"][cid]
        recipe = read(recipe_binding)
        require(recipe_binding["sha256"] == cell["manifest_sha256"], "recipe/matrix SHA differs")
        require(recipe["cell"] == {k: cell[k] for k in queue.analysis.COORDS}, "recipe coordinate differs")
        require(recipe["checkpoints"] == cell["checkpoints"], "recipe cadence differs")
        require(queue.sealed.contract_digest(recipe) == frozen["recipe_contracts"][cid], "frozen recipe contract differs")
        for key in ("code_sha256", "adapter_identity"):
            require(recipe[key] == cell[key], "recipe matrix binding differs: " + key)
        require(recipe["freeze"] == bindings["freeze"], "recipe freeze differs")
        require(recipe["backend"] == queue.sealed.backend_binding(), "backend changed")
        require(recipe["payload"]["sha256"] == cell["payload_sha256"], "payload/matrix SHA differs")
        require(ref(recipe["payload"]["path"])["sha256"] == recipe["payload"]["sha256"], "opaque payload hash differs")
        payloads.add(recipe["payload"]["path"])
        start_path = starts[cid][0]
        start = read(start_path)
        finish_ref = ref(start_path.with_name("finish.json"))
        finish = read(finish_ref)
        decision_ref = ref(start_path.with_name("decision.json"))
        decision = read(decision_ref)
        require(finish["start_sha256"] == ref(start_path)["sha256"] and all(finish.get(k) == v for k, v in start.items()), "start/finish chain differs")
        require(start["recipe"] == recipe_binding and start["bindings_sha256"] == bindings_ref["sha256"] and start["matrix_sha256"] == bindings["matrix_sha256"], "process authority differs")
        require(start["producer_sha256"] == sha(queue.__file__) and start["scheduler_sha256"] == sha(ROOT / "scripts/r1_77f_scheduler.py"), "process code differs")
        require(finish["exit_code"] == 0 and finish["exception"] is None and finish["failure_class"] is None, "process failed")
        require(decision["finish_sha256"] == finish_ref["sha256"] and decision["cell_id"] == cid and decision["matrix_sha256"] == bindings["matrix_sha256"] and decision["outcome"] == "complete" and decision["failed_attempts"] == 0, "decision differs")
        directory = Path(cell["result_dir"])
        endings = sorted(directory.glob("attempt-*/result.json"))
        require(len(endings) == 1 and not list(directory.glob("attempt-*/failure.json")), "result/failure inventory differs")
        result = read(endings[0])
        cost = queue.charged_cost(cell, queue.cell_cost(directory), receipt_root, bindings["matrix_sha256"])
        require(not cost["unknown_attempts"] and len(cost["attempts"]) == len(cost["process_receipts"]) == 1, "unknown or duplicate charges")
        require(finish["new_attempts"] == [str(endings[0].parent)], "covered attempt differs")
        close(cost["known_attempt_wall_seconds"], finish["charged_process_wall_seconds"], "process time double-counted")
        close(cost["known_attempt_wall_seconds"], prior_costs[cid]["charged_seconds"], "historical D11 cost differs")
        receipt_refs = []
        for n in cell["checkpoints"]:
            receipt_path = endings[0].with_name(f"checkpoint-{n}.receipt.json")
            receipt = read(receipt_path)
            receipt_refs.append(ref(receipt_path))
            require(ref(receipt["snapshot"]["path"])["sha256"] == receipt["snapshot"]["sha256"], "opaque snapshot hash differs")
            if recipe["integrity_profile"] == "incremental":
                DurablePhaseJournal.verify(endings[0].parent / "phases", receipt["journal"])
            else:
                require("journal" not in receipt and recipe["integrity_profile"] == "full", "unknown integrity profile")
        if recipe["integrity_profile"] == "incremental":
            phase_rows = DurablePhaseJournal.verify(endings[0].parent / "phases")
        else:
            phase_paths = sorted((endings[0].parent / "phases").glob("*.json"))
            require([p.name for p in phase_paths] == [f"{i:06d}.json" for i in range(len(phase_paths))], "full-profile phase sequence differs")
            phase_rows = [read(p) for p in phase_paths]
        require([p["phase"] for p in phase_rows] == [p["phase"] for p in result["detailed_phase_timers"]], "phase/timing inventory differs")
        for phase in phase_rows:
            require(phase["status"] == "ok" and phase["error"] is None, "failed phase in completed cell")
            if not phase["learning"] or phase["restore_required"]:
                require(phase["state_after_restore"] == phase["state_before"], "read-only/restore phase state differs")
        phases += len(phase_rows)
        for path in sorted((endings[0].parent / "phases").iterdir()):
            ref(path)
        observation = watch.inspect(recipe_binding, endings[0])
        event = by_watch_id[observation["cell_id"]]
        require(event["observation"] == observation and event["implementation"] == watch.binding(), "watch does not reproduce from results")
        w = decision["fidelity_watch"]
        require(w["status"] == "updated" and w["admission_veto"] is False, "watch decision missing/error")
        length = prefix_hashes.get(w["journal"]["sha256"])
        require(length is not None, "watch decision prefix missing")
        latest_prefix = max(latest_prefix, length)
        state = watch.replay(events[:length])
        require(observation["cell_id"] in state["seen"], "decision precedes its own observation")
        require(w["audited_cells"] == length and w["breaches"] == len(state["entries"]) and w["alerts"] == len(state["alerts"]), "watch counts differ")
        for field, state_key in (("entries", "entries"), ("alert_log", "alerts")):
            encoded = "".join(watch.encoded(e) for e in state[state_key]).encode()
            require(hashlib.sha256(encoded).hexdigest() == w[field]["sha256"], "historical watch view differs: " + field)
        matching_contexts = [key for key, context in document_contexts.items()
                             if hashlib.sha256((context["before"] + watch.markdown(state) + context["after"]).encode()).hexdigest() == w["document"]["sha256"]]
        require(bool(matching_contexts), "historical managed watch document differs")
        require(w["new_alerts"] == [a for a in state["alerts"] if a["cell_id"] == observation["cell_id"]], "decision alert reasons differ")
        rows.append(dict(cell_id=cid, cell=recipe["cell"], recipe=recipe_binding, start=ref(start_path), finish=finish_ref,
                         decision=decision_ref, result=ref(endings[0]), checkpoint_receipts=receipt_refs,
                         phase_count=len(phase_rows), charged_process_seconds=cost["known_attempt_wall_seconds"],
                         covered_driver_seconds=result["attempt_wall_seconds"], uncovered_driver_seconds=0,
                         attempts=1, failures=0, unknown_costs=0, watch_id=observation["cell_id"],
                         integrity_profile=recipe["integrity_profile"],
                         watch_prefix_events=length, watch_prefix_sha256=w["journal"]["sha256"], status="pass"))
        rows[-1]["watch_document_context"] = matching_contexts[0]
        print(f"verified {index}/45 {cid}", flush=True)
    prefix = b"".join(lines[:latest_prefix])
    # The block-1 prefix may include development baselines, but no later final cell.
    watched = {r["watch_id"] for r in rows}
    require({e["observation"]["cell_id"] for e in events[:latest_prefix] if e["observation"]["scope"] == "confirmatory"} == watched, "later final cell in block1 watch prefix")
    with (HERE / "watch-block1.jsonl").open("xb") as stream:
        stream.write(prefix)
    state = watch.replay(events[:latest_prefix])
    total = math.fsum(r["charged_process_seconds"] for r in rows) / 3600
    close(total, historical["boundary_known_process_hours"], "D11 block total differs")
    # Verify stable input membership and every immutable file after the audit.
    for path, expected in SOURCES.items():
        require(sha(path) == expected, "source changed during audit: " + path)
    require(journal_path.read_bytes().startswith(prefix), "watch prefix changed")
    out = dict(task="X22", status="pass", generated_utc=datetime.now(timezone.utc).isoformat(), producer=ref(__file__),
               matrix=bindings["matrix"], bindings=bindings_ref, cells=45, rows=rows,
               checkpoint_receipts=sum(len(r["checkpoint_receipts"]) for r in rows),
               opaque_payloads_hashed=len(payloads), phase_rows=phases,
               process_hours=total, process_count=45, failed_attempts=0, unknown_cost_records=0,
               uncovered_driver_seconds=0, watch_prefix=ref(HERE / "watch-block1.jsonl"),
               watch_prefix_original_path=str(journal_path), watch_events=latest_prefix,
               block1_breach_cells=sum(e["cell_id"] in watched for e in state["entries"]),
               block1_creep_alert_cells=sum(e["cell_id"] in watched for e in state["alerts"]),
               historical_watch_document_contexts=document_contexts,
               source_bindings_sha256=SOURCES,
               qualifications=["No payload/snapshot deserialization or model execution; state identity is receipt-bound, not replayed numerically.",
                               "Historical watch view hashes are reproduced from their exact original journal prefixes.",
                               "No inference about current global spend or completion beyond block 1."])
    write(HERE / "receipt-audit.json", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "source_bindings_sha256")}, indent=2))


if __name__ == "__main__":
    main()
