"""Versioned corrected-profile claims; final v6 requires chain Q and signed costs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.ht4e_claim_ledger import profile_inventory
from scripts.r1_63h_refresh import external_dependencies
from scripts.r1_d10a_review import ROOT, write_new


def build(*, preview=False, cost_receipt=None):
    profiles = profile_inventory()
    plan = ROOT / "docs/R1_execution_plan_v2.md"
    pending = external_dependencies(profiles, plan)
    cost = None
    if cost_receipt is not None:
        cost = d9.ref(Path(cost_receipt).resolve())
        spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v4.json"))
        d9.check_receipt("chain_i_cell_ceilings", d9.read_metadata(cost), spec)
    else:
        pending.append("signed_full_endpoint_process_cost_admission")
    if pending and not preview:
        raise ValueError("Final ledger dependencies pending: " + ", ".join(pending))
    tag = "v6-preview" if preview else "v6"
    prefix = ROOT / "logs/r1_round26"
    inventory = write_new(prefix / f"ht4f-profiles-{tag}.json", dict(profiles=profiles, producer=d9.ref(__file__)))
    rows = []

    def claim(identity, status, statement, limits, evidence):
        rows.append(dict(id=identity, status=status, statement=statement, limits=limits,
                         evidence=[d9.ref(ROOT / p) if isinstance(p, (str, Path)) else p for p in evidence]))

    for row in profiles:
        complete = row["status"] == "complete"
        claim("MQ-" + row["condition"], "development_measured" if complete else "pending",
              f"MQuAKE {row['condition']}: " + (f"RET-ES {row['retention']['es']}; RET-GS {row['retention']['gs']}; bounded locality {row['locality']['preserved_n']}/{row['locality']['expected_n']}; driver attempt {row['attempt_wall_seconds']:.3f} seconds." if complete else "No completed result for this exact corrected recipe."),
              "300 attempted development edits; exposed population. Attempt timing excludes outer process startup; these runs do not establish full final endpoint costs. Chain M locality0/50 is an invalid payload artifact and is never substituted. Missing near/revision endpoints stay unavailable.",
              [inventory, row["recipe"], *([row[k] for k in ("result", "checkpoint", "receipt")] if complete else [])])
    review_path = prefix / "near_final/r1-d9e-real-pool-review.json"
    review = d9.read_metadata(d9.ref(review_path))
    claim("DEC061", "adopted_and_CPU_validated",
          "Exact different-subject relation/template family is implemented in constructor, seal validator and bounded neighbour-baseline analysis. Missing planned slots are retained.",
          "Different-subject template specificity, not semantic nearest-neighbour robustness. Historical development near cases are a different family. No final drawn population or confirmatory outcome exists.",
          ["docs/R1_stage4_protocol_v5_2_D_final.md", "scripts/r1_d9e_near_family.py", review_path])
    counts = "; ".join(f"{ds}: {r['matched']}/300 matched, {r['missing']} missing" for ds, r in review["diagnostic"].items())
    claim("NEAR-dry-availability", "diagnostic_only", counts + ".",
          review["limitation"], [review_path])
    claim("CAPACITY", "CPU_verified",
          "Usable subjects: zsRE6084, CounterFact6121, MQuAKE2161; all93 role-subset Hall checks pass at demand4050/4050/1950.",
          "Operational entity policy and fixed source exposure snapshot; no final signature/draw and no guarantee of matching near families. Lead attests current exposure at draw.", [review_path])
    claim("ZSRE-empty-baseline", "development_baseline_characterization",
          "6036 of6084 zsRE teacher items emit immediate newline/empty text. All6084 pass the declared E.2/token checks.",
          "Most zsRE results measure acquisition/generalization from an empty baseline; teacher-incorrect does not establish correction of an initially answered fact.", ["logs/r1_round25/r1-x15-independent.json"])
    claim("QUEUE", "CPU_validated",
          "The admitted solo ceiling already includes1.5× measured cost; two workers apply1.15 once. Ordinary failures retry once, then remain incomplete while dispatch continues; host failures stop dispatch.",
          "Probes do not establish every full-endpoint slowdown. Sum process envelopes including overlap/failures; keep elapsed wall planning separate. No new GPU throughput measurement.", ["docs/R1_stage4_queue_concurrency_v2.md", "scripts/r1_77f_scheduler.py", "logs/r1_round26/regression-tests.txt"])
    claim("COST", "signed_cost_receipt_bound" if cost else "pending",
          "Execution plan v2 is bound." if plan.is_file() else "Execution plan v2 and full endpoint/process cost admission remain pending.",
          "Do not promote the older provisional235/251 solo-hour or140/150 elapsed-hour scenarios into admitted costs. A plan file alone is not a signed ceiling receipt.", [*([d9.ref(plan)] if plan.is_file() else []), *([cost] if cost else [])])
    claim("SCOPE", "adopted",
          "360core cells plus45optional; zsRE/CounterFact1000 edits per realization, MQuAKE300. The63-interval primary family is unchanged; its21 MQuAKE1000 intervals are unavailable.",
          "No extrapolation from300 to1000, alpha redistribution or orders-as-independent-clusters. No confirmatory outcome has been produced by this work.", ["manifests/revision_v1/run_matrix_v5_2_D_DEC061.json"])
    parent = d9.ref(ROOT / "logs/r1_round25/talk_evidence_v5.json")
    framing = d9.read_metadata(parent)["framing"]
    for row in rows:
        for b in row["evidence"]:
            if d9.ref(b["path"]) != b:
                raise ValueError("claim source changed during snapshot")
    report = dict(task="HT-4f", version=tag, producer=d9.ref(__file__), parent=parent,
                  inherited_history="v5 retains the prior tail/kappa/stress development claims and evidence; those experiments are not rerun or reclassified here",
                  rows=rows, profiles=inventory, framing=framing, pending=pending,
                  cost_admission=cost, corrected_mquake_complete=sum(r["status"]=="complete" for r in profiles),
                  corrected_mquake_expected=8, gpu_seconds=0,
                  experiment_deadline="2026-10-09", presentation="2026-10-15")
    write_new(prefix / f"talk_evidence_{tag}.json", report)
    lines = [f"# Talk claim ledger {tag}", "", "Experiments stop October9; presentation October15. Current development evidence only.", "",
             "This refresh supersedes v5's queue, near-family and corrected-profile snapshot. Prior tail/κ/stress evidence remains in [v5](talk_claim_ledger_v5.md); no new conclusion about those experiments is inferred.", "",
             "Pending: " + (", ".join(pending) or "none of this refresh's input dependencies; final confirmatory signatures remain separate"), "",
             "| Claim | Status | Statement | Limits |", "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['id']} | {row['status']} | {row['statement']} | {row['limits']} |")
    lines += ["", "All evidence paths and hashes are in the accompanying JSON. The κ pilot remains preliminary hints, not the coupled free energy and not a test of the one-κ conjecture.", ""]
    path = ROOT / f"docs/talk_claim_ledger_{tag.replace('-', '_')}.md"
    with path.open("x") as f:
        f.write("\n".join(lines))
    return dict(version=tag, pending=pending, corrected_mquake_complete=report["corrected_mquake_complete"], claims=len(rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--cost-receipt", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(preview=args.preview, cost_receipt=args.cost_receipt), indent=2))
