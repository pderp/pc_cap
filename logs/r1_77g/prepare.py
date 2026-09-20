"""Verify immutable block-1 cost records and emit an unsigned amendment once."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCES = {}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def ref(path):
    path = str(Path(path).resolve())
    SOURCES[path] = sha(path)
    return dict(path=path,sha256=SOURCES[path])


def read(path_or_binding):
    binding = path_or_binding if isinstance(path_or_binding,dict) else ref(path_or_binding)
    if ref(binding["path"])["sha256"] != binding["sha256"]:
        raise ValueError("source hash mismatch: " + binding["path"])
    return json.loads(Path(binding["path"]).read_bytes())


def require(ok, message):
    if not ok:
        raise ValueError(message)


def close(a,b,message):
    require(math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-6),message)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def write(path,value):
    with Path(path).open("x") as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write("\n")
    return dict(path=str(Path(path).resolve()),sha256=sha(path))


def main():
    base_ref = ref(ROOT / "docs/tasks/R1-final-queue-bindings.json")
    base = read(base_ref)
    matrix = read(base["matrix"])
    cost = read(base["cost_admission"])
    require(cost["shared_process_hours"] == 750 and cost["cost_schema_version"] == 2
            and cost["receipt_revision"] == 4 and cost["lead_approved"] is True,
            "signed typed cost admission and unchanged 750-hour cap required")
    report_ref = ref(ROOT / "logs/R1/operator_reports/20260919-block1-try1/report.json")
    report = read(report_ref)
    require(digest({k:v for k,v in report.items() if k != "report_sha256"}) == report["report_sha256"], "D11 self digest mismatch")
    require(report["boundary_block"] == 1 and report["boundary_ready"], "completed block-1 snapshot required")
    require(report["identity"]["matrix"] == base["matrix"] and report["identity"]["workers"] == 2, "D11 matrix/worker identity differs")
    cells = {c["cell_id"]:c for c in matrix["cells"]+matrix["extension"]["cells"]}
    block = {cid:c for cid,c in cells.items() if c["block_number"] == 1}
    require(len(cells)==330 and len(block)==45, "wrong matrix scope")
    inventory = {r["cell_id"]:r for r in report["inventory"]["queue"]}
    ledger = {r["cell_id"]:r for r in report["cost_ledger"]["rows"]}
    classes = defaultdict(list)
    evidence_rows = []
    seen_receipts = set()
    for cid, cell in block.items():
        row, inv = ledger[cid], inventory[cid]
        require(inv["observed"]["artifact_complete"] and not inv["retry"]["failures"], "block 1 not wholly successful")
        require(not row["unknown_attempts"] and row["uncovered_driver_seconds"] == 0 and
                len(row["process_receipts"]) == len(row["driver_attempts"]) == 1,
                "uncovered, unknown, or non-single-attempt block-1 cost")
        process_ref = row["process_receipts"][0]
        require(process_ref["path"] not in seen_receipts, "duplicate process charge")
        seen_receipts.add(process_ref["path"])
        finish = read(process_ref)
        start_ref = dict(path=str(Path(process_ref["path"]).with_name("start.json")),sha256=finish["start_sha256"])
        start = read(start_ref)
        require(all(finish.get(k)==v for k,v in start.items()),"finish/start mismatch")
        require(finish["cell_id"]==cid and finish["matrix_sha256"]==base["matrix_sha256"]
                and finish["bindings_sha256"]==base_ref["sha256"] and finish["workers"]==2
                and finish["exit_code"]==0 and finish["exception"] is None and finish["failure_class"] is None,
                "finish execution identity/failure mismatch")
        require(finish["recipe"] == base["recipes"][cid], "executed recipe differs from bindings")
        require(len(finish["new_attempts"])==1 and str(Path(row["driver_attempts"][0]["path"]).parent) in finish["new_attempts"], "driver not covered by process envelope")
        measured = read(row["driver_attempts"][0])
        require(measured["status"]=="complete" and measured["manifest_sha256"]==cell["manifest_sha256"], "result identity differs")
        basis = read(cell["ceilings"]["measurement"])["cost_components"]
        solo = basis["solo_seconds"]
        close(cell["ceilings"]["wall_seconds"], 1.5*solo, "signed solo safety factor differs")
        close(finish["solo_wall_ceiling_seconds"],cell["ceilings"]["wall_seconds"],"process solo ceiling differs")
        close(finish["effective_wall_ceiling_seconds"],1.15*cell["ceilings"]["wall_seconds"],"old concurrency factor differs")
        charge = finish["charged_process_wall_seconds"]
        close(charge,row["charged_seconds"],"ledger charge differs")
        close(charge,process_ref["wall_seconds"],"process reference charge differs")
        close(measured["attempt_wall_seconds"],row["driver_attempts"][0]["wall_seconds"],"driver diagnostic differs")
        phases = [p for p in measured["detailed_phase_timers"] if p["phase"].startswith("full_validation:")]
        require(len(phases)==1,"one final full-validation phase required")
        record = dict(cell_id=cid,condition=cell["condition"],dataset=cell["dataset"],realization=cell["realization"],order=cell["order"],
                      start=start_ref,finish={k:process_ref[k] for k in ("path","sha256")},
                      result={k:row["driver_attempts"][0][k] for k in ("path","sha256")},
                      solo_cost_evidence=cell["ceilings"]["measurement"],charged_process_seconds=charge,
                      solo_estimate_seconds=solo,process_to_solo_estimate_ratio=charge/solo,
                      old_effective_ceiling_seconds=finish["effective_wall_ceiling_seconds"],
                      old_ceiling_used_fraction=charge/finish["effective_wall_ceiling_seconds"],
                      proposed_effective_ceiling_seconds=1.7*cell["ceilings"]["wall_seconds"],
                      full_phase_seconds=phases[0]["total_phase_seconds"],full_phase_solo_estimate_seconds=basis["full_outer_seconds"],
                      full_phase_to_solo_estimate_ratio=phases[0]["total_phase_seconds"]/basis["full_outer_seconds"])
        evidence_rows.append(record)
        classes[cell["condition"]+":"+cell["dataset"]].append(record)
    totals = []
    for key, rows in sorted(classes.items()):
        totals.append(dict(condition_dataset=key,cells=len(rows),solo_estimate_seconds=rows[0]["solo_estimate_seconds"],
                           mean_process_seconds=statistics.mean(r["charged_process_seconds"] for r in rows),
                           max_process_seconds=max(r["charged_process_seconds"] for r in rows),
                           max_process_to_solo_estimate_ratio=max(r["process_to_solo_estimate_ratio"] for r in rows),
                           max_old_ceiling_used_fraction=max(r["old_ceiling_used_fraction"] for r in rows),
                           mean_full_phase_to_solo_estimate_ratio=statistics.mean(r["full_phase_to_solo_estimate_ratio"] for r in rows)))
    spent = math.fsum(r["charged_process_seconds"] for r in evidence_rows)/3600
    close(spent,report["boundary_known_process_hours"],"block total differs")
    affected = [c for c in cells.values() if c.get("full_validation") == matrix["full_validation"]]
    require(len(affected)==330,"scope ambiguity: some cells lack full validation")
    remaining = [c for c in affected if c["block_number"]>1]
    # Historical boundary scenario only; later completed/active work is not recosted.
    solo_remaining = math.fsum(c["ceilings"]["wall_seconds"] for c in remaining)/3600
    targeted = {"R1_learned_ff:zsre","v0_stable:counterfact"}
    target_hours = spent + math.fsum(c["ceilings"]["wall_seconds"] *
        (1.7 if c["condition"]+":"+c["dataset"] in targeted else 1.15) for c in remaining)/3600
    scenarios = dict(boundary="historical end of block 1; not current live spend",completed_cells=45,remaining_cells=285,
                     actual_block1_process_hours=spent,
                     remaining_all_cell_ceilings_old_total_hours=spent+1.15*solo_remaining,
                     remaining_all_cell_ceilings_proposed_total_hours=spent+1.7*solo_remaining,
                     proposed_headroom_to_750_hours=750-spent-1.7*solo_remaining,
                     targeted_two_classes_total_hours=target_hours,
                     targeted_alternative_scope="30 cells total / 20 after block 1; NOT the requested all-full-validation proposal",
                     fresh_matrix_all_proposed_ceiling_hours=math.fsum(c["ceilings"]["wall_seconds"] for c in affected)*1.7/3600,
                     shared_cap_process_hours=750,
                     interpretation="ceiling reservations, not expected or measured runtime; no guarantee all cells finish under the unchanged cap")
    max_ratio = max(r["process_to_solo_estimate_ratio"] for r in evidence_rows)
    evidence = dict(task="R1-77g",status="verified_block1_cost_evidence",generated_utc=datetime.now(timezone.utc).isoformat(),
                    producer=ref(__file__),block_report=report_ref,matrix=base["matrix"],base_bindings=base_ref,
                    source_bindings_sha256=dict(SOURCES),rows=evidence_rows,classes=totals,scenarios=scenarios,
                    max_measured_process_to_solo_estimate_ratio=max_ratio,
                    proposed_factor_margin_above_observed_max_fraction=1.7/max_ratio-1,
                    qualifications=["Solo denominators include registered estimates and reviewed transfers, not paired one-worker repeats of these confirmation cells.",
                                    "1.64 rounds the v0_stable CounterFact mean ratio; maximum is about 1.657.",
                                    "A global 1.6–2.4 full-phase slowdown is not supported for every class; no isolated causal concurrency estimate.",
                                    "Only nine condition/dataset classes were observed in block 1; remaining classes inherit an unmeasured allowance proposal.",
                                    "No outcome or fidelity metric enters this cost selection; all 45 block-1 finishes are included."])
    for path,h in SOURCES.items():
        require(sha(path)==h,"source changed during preparation: "+path)
    evidence_ref=write(HERE/"block1-evidence.json",evidence)
    implementations={name:ref(ROOT/path) for name,path in dict(queue="scripts/r1_77_queue.py",scheduler="scripts/r1_77f_scheduler.py",
        operator="scripts/r1_58g_operator.py",accounting="scripts/r1_d11_block_report.py",repricing="scripts/r1_d12_reprice.py").items()}
    proposal=dict(format="R1-77g-ceiling-amendment-v2",schema_version=2,status="unsigned_proposal",lead_approved=False,
                  activation_requires="Q21 approval plus new exact signed resume request, globally idle reconciliation and the bound consumer; legacy queue intentionally refuses this schema",
                  base_bindings=base_ref,matrix=base["matrix"],matrix_sha256=base["matrix_sha256"],freeze=base["freeze"],
                  cost_admission=base["cost_admission"],receipt_root=str(ROOT/"logs/R1/final_queue"),
                  shared_process_hours=750,experiment_deadline="2026-10-09",evidence=evidence_ref,
                  consumer=ref(HERE/"consumer.py"),implementation_bindings=implementations,
                  ceiling_amendment=dict(previous_workers_2_factor=1.15,workers_1_factor=1.0,workers_2_factor=1.7,
                      application="replace_two_worker_factor_once_on_frozen_solo_whole_cell_ceiling",
                      scope="every frozen full-validation-bearing cell; all 330 in this matrix; future dispatch only",
                      affected_cell_ids=sorted(c["cell_id"] for c in affected),
                      preserved="frozen matrix, recipes, destinations, solo ceilings/safety factor, populations, model/scoring, retry history, actual prior charges, total cap and deadline"),
                  block1_scenarios=scenarios,legacy_recipes_key_deliberately_absent=True)
    binding=write(ROOT/"docs/tasks/R1-final-queue-bindings-v2.json",proposal)
    write(HERE/"preparation.json",dict(status="prepared_not_applied",evidence=evidence_ref,proposal=binding,
                                      classes=9,measured_cells=45,affected_cells=330,live_queue_changed=False,launch_authorized=False))
    print(json.dumps(dict(status="prepared_not_applied",max_ratio=max_ratio,scenarios=scenarios,proposal=binding),indent=2))


if __name__=="__main__":
    main()
