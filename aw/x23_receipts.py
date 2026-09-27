"""X23: read-only extension of X22 over ordered cells 136–270.

Uses the installed receipt/watch verifiers; payloads and snapshots are opaque
SHA256 inputs. Never restores a model, writes a queue file or dispatches work.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "logs/R1/reports/block1/audit_receipts.py"
spec = importlib.util.spec_from_file_location("x22_helpers", LEGACY)
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
require, sha, ref, read, write, close = x.require, x.sha, x.ref, x.read, x.write, x.close
queue, watch, DurablePhaseJournal = x.queue, x.watch, x.DurablePhaseJournal

# The only known missing parent decisions. Their start/finish and scientific
# artifacts still have to pass; this exception cannot admit an extra absence.
KNOWN_MISSING = {
    ("v0_stable", "mquake", 1, 103),
    ("v0_stable", "mquake", 1, 104),
    ("S1_literal", "zsre", 2, 103),
    ("S1_literal", "zsre", 2, 104),
}


def coordinate(cell):
    return tuple(cell[k] for k in ("condition", "dataset", "realization", "order"))


def authority(start, ordinal, v1ref, v1, v2ref, v2):
    amended = ordinal > 90
    expected = v2ref if amended else v1ref
    require(start["bindings_sha256"] == expected["sha256"], "wrong bindings version")
    require(start["matrix_sha256"] == v1["matrix_sha256"], "wrong matrix")
    require(start["recipe"] == v1["recipes"][start["cell_id"]], "wrong process recipe")
    ratio = 1.7 if amended else 1.15
    require(start["workers"] == 2, "unexpected worker count")
    close(
        start["effective_wall_ceiling_seconds"],
        ratio * start["solo_wall_ceiling_seconds"],
        "wrong ceiling factor",
    )
    require(
        start["scheduler_sha256"] == sha(ROOT / "scripts/r1_77f_scheduler.py"), "scheduler changed"
    )
    if amended:
        require(start["producer_sha256"] == v2["consumer"]["sha256"], "consumer changed")
        require(start["ceiling_amendment"] == v2ref, "amendment binding differs")
        require(
            read(start["resume_authorization"])["status"] == "authorized", "resume not authorized"
        )
        require(
            ref(start["base_queue_producer"]["path"])["sha256"]
            == start["base_queue_producer"]["sha256"]
            == sha(queue.__file__),
            "base queue differs",
        )
    else:
        require(start["producer_sha256"] == sha(queue.__file__), "queue producer differs")
    return ratio


def contexts():
    result = {}
    commits = subprocess.check_output(
        ["git", "log", "--format=%H", "--", "docs/fidelity_watch.md"], cwd=ROOT, text=True
    ).splitlines()
    for commit in commits:
        doc = subprocess.check_output(
            ["git", "show", commit + ":docs/fidelity_watch.md"], cwd=ROOT
        ).decode()
        if watch.BEGIN not in doc:
            continue
        before, rest = doc.split(watch.BEGIN)
        _, after = rest.split(watch.END)
        context = dict(before=before, after=after.lstrip("\n"))
        result[watch.full.digest(context)] = dict(context, commit=commit)
    return result


def decision_watch(decision, observation, events, prefixes, document_contexts):
    w = decision["fidelity_watch"]
    require(
        w["status"] == "updated" and w["admission_veto"] is False, "watch decision missing/error"
    )
    length = prefixes.get(w["journal"]["sha256"])
    require(length is not None, "watch prefix missing")
    state = watch.replay(events[:length])
    require(observation["cell_id"] in state["seen"], "decision precedes observation")
    require(
        w["audited_cells"] == length
        and w["breaches"] == len(state["entries"])
        and w["alerts"] == len(state["alerts"]),
        "watch counts differ",
    )
    for field, key in (("entries", "entries"), ("alert_log", "alerts")):
        encoded = "".join(watch.encoded(e) for e in state[key]).encode()
        require(
            hashlib.sha256(encoded).hexdigest() == w[field]["sha256"],
            "historical watch view differs",
        )
    matches = [
        key
        for key, c in document_contexts.items()
        if hashlib.sha256((c["before"] + watch.markdown(state) + c["after"]).encode()).hexdigest()
        == w["document"]["sha256"]
    ]
    require(bool(matches), "historical watch document differs")
    require(
        w["new_alerts"] == [a for a in state["alerts"] if a["cell_id"] == observation["cell_id"]],
        "alert reasons differ",
    )
    return dict(events=length, journal_sha256=w["journal"]["sha256"], document_context=matches[0])


def audit(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    x.SOURCES.clear()
    ref(__file__)
    ref(LEGACY)
    v1ref = ref(ROOT / "docs/tasks/R1-final-queue-bindings.json")
    v1 = read(v1ref)
    v2ref = ref(ROOT / "docs/tasks/R1-final-queue-bindings-v2.json")
    v2 = read(v2ref)
    require(v2["base_bindings"] == v1ref, "v2 parent differs")
    require(
        ref(v2["consumer"]["path"])["sha256"] == v2["consumer"]["sha256"], "consumer bytes differ"
    )
    matrix = read(v1["matrix"])
    frozen = read(v1["freeze"])
    all_cells = queue.analysis.all_cells(matrix)
    selected = all_cells[135:270]
    require(len(selected) == 135, "audit inventory differs")
    ordinal = {c["cell_id"]: i for i, c in enumerate(all_cells, 1)}
    native = read(ROOT / "logs/R1/reports/comparators-270/analysis.json")
    observed = {c["cell_id"]: c for c in native["cells"]}
    for name, h in native["analysis_source_sha256"].items():
        require(ref(ROOT / name)["sha256"] == h, "analysis producer differs")
    for name, h in native["sources_sha256"].items():
        # Check all saved analysis inputs: no live PC outputs are included.
        require(ref(name)["sha256"] == h, "saved analysis input changed: " + name)
    halt = read(ROOT / "logs/R1/operations/HALT_REPORT/d11-report.json")
    require(
        watch.full.digest({k: v for k, v in halt.items() if k != "report_sha256"})
        == halt["report_sha256"],
        "halt report digest differs",
    )
    costs = {r["cell_id"]: r for r in halt["cost_ledger"]["rows"]}
    ref(ROOT / "logs/R1/operations/Q21_cutover/halt-reconciliation.md")
    starts = {}
    receipt_root = ROOT / "logs/R1/final_queue"
    for path in sorted(receipt_root.glob("*/start.json")):
        r = read(path)
        require(
            r["cell_id"] in ordinal and ordinal[r["cell_id"]] <= 270, "unexpected dispatched cell"
        )
        starts.setdefault(r["cell_id"], []).append(path)
    require(
        set(starts) == {c["cell_id"] for c in all_cells[:270]}
        and all(len(v) == 1 for v in starts.values()),
        "missing or duplicate process",
    )
    missing = []
    version_counts = {"v1": 0, "v2": 0}
    all_process_seconds = []
    for c in all_cells[:270]:
        p = starts[c["cell_id"]][0]
        start = read(p)
        finish = read(p.with_name("finish.json"))
        authority(start, ordinal[c["cell_id"]], v1ref, v1, v2ref, v2)
        version_counts["v1" if ordinal[c["cell_id"]] <= 90 else "v2"] += 1
        require(
            finish["start_sha256"] == sha(p) and all(finish.get(k) == v for k, v in start.items()),
            "start/finish chain differs",
        )
        require(
            finish["exit_code"] == 0
            and finish["exception"] is None
            and finish["failure_class"] is None,
            "failed process",
        )
        close(
            finish["charged_process_wall_seconds"],
            costs[c["cell_id"]]["charged_seconds"],
            "D11 process charge differs",
        )
        all_process_seconds.append(finish["charged_process_wall_seconds"])
        if not p.with_name("decision.json").exists():
            require(coordinate(c) in KNOWN_MISSING, "undisclosed missing decision")
            missing.append(
                dict(
                    cell_id=c["cell_id"],
                    cell={k: c[k] for k in queue.analysis.COORDS},
                    ordinal=ordinal[c["cell_id"]],
                    path=str(p.with_name("decision.json")),
                )
            )
    require(
        {coordinate(m["cell"]) for m in missing} == KNOWN_MISSING,
        "disclosed missing-decision inventory differs",
    )
    close(
        math.fsum(all_process_seconds),
        halt["cost_ledger"]["charged_seconds"],
        "global process total differs",
    )
    journal_path = ROOT / "results/R1/fidelity_watch/observations.jsonl"
    raw = journal_path.read_bytes()
    require(raw.endswith(b"\n"), "torn watch read")
    lines = raw.splitlines(keepends=True)
    events = [json.loads(line) for line in lines]
    state = watch.replay(events)
    prefixes = {}
    running = hashlib.sha256()
    for i, line in enumerate(lines, 1):
        running.update(line)
        prefixes[running.hexdigest()] = i
    by_watch_id = {e["observation"]["cell_id"]: e for e in events}
    document_contexts = contexts()
    rows = []
    payloads = set()
    phases = 0
    for i, c in enumerate(selected, 1):
        cid = c["cell_id"]
        item = observed[cid]
        require(
            all(
                item[k]
                for k in (
                    "artifact_complete",
                    "primary_metrics_complete",
                    "scientific_admission",
                    "endpoint_complete",
                )
            ),
            "incomplete native evidence",
        )
        binding = v1["recipes"][cid]
        recipe = read(binding)
        require(binding["sha256"] == c["manifest_sha256"], "recipe matrix identity differs")
        require(
            recipe["cell"] == {k: c[k] for k in queue.analysis.COORDS}
            and recipe["checkpoints"] == c["checkpoints"],
            "recipe coordinate/cadence differs",
        )
        require(
            queue.sealed.contract_digest(recipe) == frozen["recipe_contracts"][cid],
            "frozen recipe contract differs",
        )
        for key in ("code_sha256", "adapter_identity"):
            require(recipe[key] == c[key], "recipe matrix binding differs")
        require(
            recipe["freeze"] == v1["freeze"]
            and recipe["backend"] == queue.sealed.backend_binding(),
            "recipe backend/freeze differs",
        )
        require(recipe["payload"]["sha256"] == c["payload_sha256"], "payload matrix differs")
        require(
            ref(recipe["payload"]["path"])["sha256"] == recipe["payload"]["sha256"],
            "opaque payload changed",
        )
        payloads.add(recipe["payload"]["path"])
        start_path = starts[cid][0]
        finish_ref = ref(start_path.with_name("finish.json"))
        finish = read(finish_ref)
        decision_path = start_path.with_name("decision.json")
        decision = read(decision_path) if decision_path.exists() else None
        if decision is not None:
            require(
                decision["finish_sha256"] == finish_ref["sha256"]
                and decision["cell_id"] == cid
                and decision["matrix_sha256"] == v1["matrix_sha256"]
                and decision["outcome"] == "complete"
                and decision["failed_attempts"] == 0,
                "decision chain differs",
            )
        directory = Path(c["result_dir"])
        endings = sorted(directory.glob("attempt-*/result.json"))
        require(
            len(endings) == 1 and not list(directory.glob("attempt-*/failure.json")),
            "attempt inventory differs",
        )
        result = read(endings[0])
        cost = queue.charged_cost(c, queue.cell_cost(directory), receipt_root, v1["matrix_sha256"])
        require(
            not cost["unknown_attempts"]
            and len(cost["attempts"]) == len(cost["process_receipts"]) == 1,
            "unknown or duplicated charges",
        )
        require(finish["new_attempts"] == [str(endings[0].parent)], "covered attempt differs")
        close(
            cost["known_attempt_wall_seconds"],
            finish["charged_process_wall_seconds"],
            "driver time double-counted",
        )
        receipts = []
        for n in c["checkpoints"]:
            p = endings[0].with_name(f"checkpoint-{n}.receipt.json")
            receipt = read(p)
            receipts.append(ref(p))
            require(
                ref(receipt["snapshot"]["path"])["sha256"] == receipt["snapshot"]["sha256"],
                "opaque snapshot changed",
            )
            if recipe["integrity_profile"] == "incremental":
                DurablePhaseJournal.verify(endings[0].parent / "phases", receipt["journal"])
            else:
                require(
                    "journal" not in receipt and recipe["integrity_profile"] == "full",
                    "unknown integrity profile",
                )
        if recipe["integrity_profile"] == "incremental":
            phase_rows = DurablePhaseJournal.verify(endings[0].parent / "phases")
        else:
            paths = sorted((endings[0].parent / "phases").glob("*.json"))
            require(
                [p.name for p in paths] == [f"{j:06d}.json" for j in range(len(paths))],
                "phase sequence differs",
            )
            phase_rows = [read(p) for p in paths]
        require(
            [p["phase"] for p in phase_rows]
            == [p["phase"] for p in result["detailed_phase_timers"]],
            "phase/timing inventory differs",
        )
        for phase in phase_rows:
            require(
                phase["status"] == "ok" and phase["error"] is None, "failed phase in complete cell"
            )
            if not phase["learning"] or phase["restore_required"]:
                require(
                    phase["state_after_restore"] == phase["state_before"],
                    "read-only/restore phase differs",
                )
        phases += len(phase_rows)
        for p in sorted((endings[0].parent / "phases").iterdir()):
            ref(p)
        observation = watch.inspect(binding, endings[0])
        event = by_watch_id[observation["cell_id"]]
        require(
            event["observation"] == observation and event["implementation"] == watch.binding(),
            "watch observation differs",
        )
        w = (
            decision_watch(decision, observation, events, prefixes, document_contexts)
            if decision
            else None
        )
        rows.append(
            dict(
                cell_id=cid,
                ordinal=ordinal[cid],
                cell=recipe["cell"],
                recipe=binding,
                start=ref(start_path),
                finish=finish_ref,
                decision=ref(decision_path) if decision else None,
                result=ref(endings[0]),
                checkpoint_receipts=receipts,
                phase_count=len(phase_rows),
                charged_process_seconds=cost["known_attempt_wall_seconds"],
                covered_driver_seconds=result["attempt_wall_seconds"],
                uncovered_driver_seconds=0,
                watch_id=observation["cell_id"],
                watch=w,
                integrity_profile=recipe["integrity_profile"],
                status="pass",
            )
        )
        print(f"verified {i}/135 (ordinal {ordinal[cid]}) {cid}", flush=True)
    require(journal_path.read_bytes() == raw, "watch changed during audit")
    close(
        math.fsum(r["charged_process_seconds"] for r in rows),
        math.fsum(costs[c["cell_id"]]["charged_seconds"] for c in selected),
        "selected charge total differs",
    )
    for p, h in x.SOURCES.items():
        require(sha(p) == h, "input changed during audit: " + p)
    snapshot = output / "watch-snapshot.jsonl"
    snapshot.write_bytes(raw)
    source_items = list(x.SOURCES.items())
    parts = []
    for offset in range(0, len(source_items), 10000):
        p = output / f"sources-{offset // 10000:03d}.json"
        write(p, dict(source_items[offset : offset + 10000]))
        parts.append(dict(path=str(p), sha256=sha(p)))
    watched = {r["watch_id"] for r in rows}
    report = dict(
        task="X23",
        status="pass_with_disclosed_parent_decision_gaps",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        cells=135,
        scope="full evidence audit cells 136-270; all 270 process version/charge and missing-decision inventory checked",
        rows=rows,
        checkpoint_receipts=sum(len(r["checkpoint_receipts"]) for r in rows),
        phase_rows=phases,
        opaque_payloads_hashed=len(payloads),
        process_hours=math.fsum(r["charged_process_seconds"] for r in rows) / 3600,
        whole_queue_process_hours=math.fsum(all_process_seconds) / 3600,
        uncovered_driver_seconds=0,
        failed_attempts=0,
        unknown_cost_records=0,
        bindings_version_counts=version_counts,
        missing_parent_decisions=missing,
        watch_events=len(events),
        watch_breach_entries=len(state["entries"]),
        watch_creep_alerts=len(state["alerts"]),
        audited_breach_cells=sum(e["cell_id"] in watched for e in state["entries"]),
        audited_creep_alert_cells=sum(e["cell_id"] in watched for e in state["alerts"]),
        watch_snapshot=dict(path=str(snapshot), sha256=sha(snapshot)),
        source_bindings_parts=parts,
        source_bindings_count=len(source_items),
        historical_watch_document_contexts=document_contexts,
        qualifications=[
            "No numeric state replay or model execution; this is artifact integrity, not experimental replication.",
            "Four absent parent decisions remain absent: two outside this full-audit range, two inside. All four process chains are verified.",
            "Current halt has no unobserved completed cell; decisionless halt observations are independently reproduced, not backfilled.",
        ],
    )
    write(output / "report.json", report)
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ("rows", "historical_watch_document_contexts", "source_bindings_parts")
            }
        ),
        flush=True,
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    audit(args.output)


if __name__ == "__main__":
    main()
