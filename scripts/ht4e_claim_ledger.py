"""Versioned talk ledger with explicit pending corrected-locality profiles."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from scripts.r1_d9_receipts import ref, sha
from scripts.r1_d10a_review import ROOT, write_new


def profile_inventory():
    receipts_path = ROOT / "docs/tasks/R1-73d-post77d/inspection-receipts.json"
    inspections = json.loads(receipts_path.read_text())
    rows = []
    for r in inspections:
        recipe = json.loads(Path(r["recipe"]["path"]).read_text())
        if ref(r["recipe"]["path"]) != r["recipe"]:
            raise ValueError("profile recipe changed")
        if ref(recipe["payload"]["path"]) != recipe["payload"]:
            raise ValueError("profile payload changed")
        directory = Path(r["expected_result_directory"])
        completed, failures = [], []
        for p in sorted(directory.glob("attempt-*/*.json")):
            if p.name not in ("result.json", "failure.json"):
                continue
            v = json.loads(p.read_text())
            if v.get("manifest_sha256") != r["recipe"]["sha256"]:
                raise ValueError("result belongs to another recipe")
            if p.name == "result.json" and v.get("status") == "complete" and v.get("completed_checkpoint") == 300:
                completed.append((p, v))
            else:
                failures.append(ref(p))
        if len(completed) > 1:
            raise ValueError("multiple completed attempts require explicit selection review")
        row = dict(condition=r["cell"]["condition"], recipe=r["recipe"], payload=recipe["payload"],
                   status="complete" if completed else "pending", failures=failures,
                   locality_overlap_count=r["locality_overlap_count"], result_directory=str(directory))
        if completed:
            p, value = completed[0]
            receipt = json.loads((p.parent / "checkpoint-300.receipt.json").read_text())
            canonical = json.dumps({k: v for k, v in receipt.items() if k != "receipt_sha256"},
                                   sort_keys=True, separators=(",", ":"), allow_nan=False)
            if hashlib.sha256(canonical.encode()).hexdigest() != receipt["receipt_sha256"] or value["last_receipt_sha256"] != receipt["receipt_sha256"]:
                raise ValueError("final receipt chain identity differs")
            if receipt["manifest_sha256"] != r["recipe"]["sha256"] or ref(receipt["report"]["path"]) != receipt["report"]:
                raise ValueError("checkpoint report identity differs")
            checkpoint = json.loads(Path(receipt["report"]["path"]).read_text())
            payload = json.loads(Path(recipe["payload"]["path"]).read_text())
            planned = payload["endpoints"]["locality"]["expected_ids"]
            if checkpoint["locality"]["expected_ids"] != planned:
                raise ValueError("locality population differs")
            retention = checkpoint["retention"]
            ids = [r["item_id"] for r in retention["rows"]]
            if retention["planned"] != 300 or ids != [r["item_id"] for r in payload["items"]]:
                raise ValueError("retention population differs")
            row.update(result=ref(p), checkpoint=receipt["report"], receipt=ref(p.parent / "checkpoint-300.receipt.json"),
                       attempt_wall_seconds=value["attempt_wall_seconds"],
                       locality=checkpoint["locality"]["summary"],
                       retention={"planned": 300, **{k: sum(r[k] for r in retention["rows"])/300
                                  if all(isinstance(r.get(k), (int, float)) for r in retention["rows"]) else None
                                  for k in ("es", "gs")}}, observation=checkpoint["observation"])
        rows.append(row)
    return rows


def build(suffix="v5"):
    if not re.fullmatch(r"v5(?:-[a-z0-9-]+)?", suffix):
        raise ValueError("version must be v5 or v5-<snapshot-name>")
    old_path = ROOT / "logs/r1_round22/talk_evidence_v4.json"
    old = json.loads(old_path.read_text())
    superseded = {"COST-matrix", "MQ-capacity", "O7", "U12-14"}
    rows = []
    for row in old["rows"]:
        if row["id"] in superseded:
            continue
        for b in row["evidence"]:
            if sha(ROOT / b["path"]) != b["sha256"]:
                raise ValueError("historical claim requires new review: " + row["id"])
        rows.append(copy.deepcopy(row))

    def claim(identity, label, statement, limits, paths):
        evidence = [ref(ROOT / p) for p in paths]
        rows.append(dict(id=identity, label=label, statement=statement, limits=limits, evidence=evidence))

    inventory = profile_inventory()
    profile_path = ROOT / f"logs/r1_round25/ht4e-profile-inventory-{suffix}.json"
    profile_ref = write_new(profile_path, dict(profiles=inventory, producer=ref(__file__)))
    for r in inventory:
        complete = r["status"] == "complete"
        measurement = (
            f"bounded locality {r['locality'].get('preserved_n')}/{r['locality'].get('expected_n')}; attempt {r['attempt_wall_seconds']:.3f}s"
            if complete else "no completed result for the corrected recipe at this snapshot"
        )
        claim("MQ-locality-" + r["condition"], "implemented" if complete else "proposed",
              f"MQuAKE {r['condition']}: {measurement}. Payload has zero locality/edit/paraphrase overlaps.",
              "300 attempted development edits, exposed training/development population. Old Chain M locality 0/50 is invalid and is never substituted. Attempt time excludes startup; missing near/revision rows cannot price full final endpoints.",
              [profile_path, r["recipe"]["path"], *([r["result"]["path"], r["checkpoint"]["path"], r["receipt"]["path"]] if complete else [])])
    claim("CONCURRENCY", "implemented",
          "The orchestrator admits two queue workers from two zsRE probes, reporting about 1.65×/1.67× pair throughput. The queue has shared reservations, per-cell locks, a 6 GiB second-launch guard and failure draining.",
          "Two short development pairs do not establish throughput or a 1.10 slowdown bound for all datasets/S1/full endpoints. Queue budget sums overlapping process durations; wall-clock speedup does not discount charged process-hours. X15 flags ceiling-factor terminology and a larger learned-pair slowdown.",
          ["docs/R1_stage2_notes.md", "docs/R1_stage4_queue_concurrency_v1.md", "scripts/r1_77_queue.py", "scripts/r1_77e_workers.py"])
    claim("COST-matrix", "proposed",
          "The provisional plan estimates 235 solo hours for360 core cells,251 including 45 optional cells; claimed two-worker wall projection is about140/150 h, before the October 9 experimental stop.",
          "Planning scenarios, not admitted ceilings or measured whole-matrix times. Corrected MQuAKE, complete challenge/validation costs, startup/failure envelopes and September 20 repricing remain. X15 identifies stale launch steps and the failure-policy mismatch.",
          ["docs/R1_execution_plan_v1.md", "manifests/revision_v1/run_matrix_v5_2_D.json"])
    claim("MQ-capacity", "implemented",
          "Certified teacher plus joint-role clearance gives6,084 zsRE / 6,121 CounterFact / 2,161 MQuAKE subjects against 4,050 / 4,050 / 1,950; margins 2,034 / 2,071 / 211. All 93 Hall subset checks pass.",
          "Named operational entities, not external entity-linking certification. Individual role capacities overlap; teacher/role certification is not signed clearance, a draw, or a guarantee of compatible near pairs. Draw-time exposure attestation remains.",
          ["logs/r1_round25/r1-x15-independent.json", "logs/r1_round25/r1-d9-clearance-dry-post77d.json"])
    claim("ZSRE-empty-baseline", "implemented",
          "6,036 / 6,084 zsRE teacher items pass E.2 because the pinned base emits an immediate newline and no answer; all 6,084 pass the teacher/token checks. CounterFact and MQuAKE have no empty teacher generations.",
          "For almost all this zsRE population, ES/RET-GS measure acquisition/generalization relative to an empty baseline. Do not claim correction of an initially answered fact or infer base knowledge from teacher-incorrect alone.",
          ["logs/r1_round25/r1-x15-independent.json", "logs/r1_round25/r1-d10h-certification.json"])
    claim("DEC060-scale", "implemented",
          "DEC-060 option D retains 360 core cells: zsRE/CF three 1,000-edit realizations; MQuAKE three 300-edit realizations with100/300 checkpoints. No MQuAKE 1,000-record claim is available.",
          "MQuAKE 300 outside rates and paired 100→300 changes require actual occupancy and common outside subjects; descriptive only, with null transferred thresholds. Extra capacity does not authorize a larger edit count.",
          ["docs/decisions.md", "manifests/revision_v1/run_matrix_v5_2_D.json", "scripts/r1_49g_secondary.py"])
    claim("U12-14", "implemented",
          "The primary family remains 63 nominal intervals with 0.05/63 each; seven MQuAKE 1,000 contrasts / 21 intervals remain unavailable. DEC-058 classification and zsRE/CF DEC-059 benchmarks are unchanged.",
          "Three realization clusters provide nominal coverage; no alpha redistribution or orders-as-independent-clusters. Implementation and inventory are available; confirmatory outcome estimates are not.",
          ["docs/decisions.md", "scripts/r1_49g_inference.py", "scripts/r1_49g_secondary.py", "logs/r1_round24/r1-49h-draft-inventory-v2.json"])
    for row in rows:
        for b in row["evidence"]:
            if sha(ROOT / b["path"]) != b["sha256"]:
                raise ValueError("claim binding changed during snapshot")
    report = dict(task="HT-4e", version=suffix, producer=ref(__file__), parent=ref(old_path),
                  rows=rows, framing=old["framing"], profiles=profile_ref,
                  corrected_mquake_complete=sum(r["status"] == "complete" for r in inventory),
                  corrected_mquake_expected=8, gpu_seconds=0,
                  status="complete_snapshot; final_after_chain_P_refresh_pending" if any(r["status"] != "complete" for r in inventory) else "complete_after_chain_P",
                  superseded_historical_rows=sorted(superseded))
    write_new(ROOT / f"logs/r1_round25/talk_evidence_{suffix}.json", report)
    lines = [f"# Talk claim–evidence ledger {suffix}", "",
             "Charlie Derr, Binghamton, October 15. Experiments stop October 9; October 10–14 is for analysis, slides and rehearsal.", "",
             "Current development evidence; no new confirmatory outcomes. Corrected MQuAKE rows explicitly remain pending until their exact recipes have completed.", "",
             old["framing"], "", "| ID | Status | Statement | Limits | Evidence SHA-256 |", "|---|---|---|---|---|"]
    for row in rows:
        references = "; ".join(f"[{Path(b['path']).name}]({Path(b['path']) if Path(b['path']).is_absolute() else '../'+b['path']}) `{b['sha256']}`" for b in row["evidence"])
        fields = [row["id"], row["label"], row["statement"], row["limits"], references]
        lines.append("| " + " | ".join(s.replace("|", "\\|").replace("\n", " ") for s in fields) + " |")
    with (ROOT / f"docs/talk_claim_ledger_{suffix}.md").open("x") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "corrected_mquake_complete", "corrected_mquake_expected")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="v5", help="Use a fresh v5-<name> for a later result snapshot")
    build(parser.parse_args().version)
