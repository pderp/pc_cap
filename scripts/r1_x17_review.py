"""Re-review the repaired unsigned package from current bindings and raw profile traces."""

from __future__ import annotations

import copy
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.ht4e_claim_ledger import profile_inventory
from scripts.r1_49j_normative_closure import verify as verify_normative
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_75_analysis_stage4_v1 import preservation_section
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_x16_review import TRACE


def run():
    cp = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v12.json")
    candidate = d9.read_metadata(cp)
    proof = verify(candidate)
    verify_normative(candidate)
    spec = d9.read_metadata(candidate["d9_inputs"])
    cost = d9.read_metadata(candidate["cost_admission_source_unsigned"])
    matrix = d9.read_metadata(candidate["matrix"])
    prices = d9.read_metadata(cost["bindings"]["cell_ceilings"])["cells"]
    old = d9.read_metadata(d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_DEC061.json"))
    assert [matrix["cells"], matrix["extension"]["cells"]] == [
        old["cells"],
        old["extension"]["cells"],
    ]
    text = Path(candidate["protocol"]["path"]).read_text()
    assert "No family-coordinated\nallocation" not in text
    assert "Several pairs may share a family" in text
    assert cost["protocol"] == spec["protocol"] == matrix["protocol"]
    cells = matrix["cells"] + matrix["extension"]["cells"]
    core = sum(
        Decimal(str(prices[c["condition"] + ":" + c["dataset"]]["solo_hours"]))
        for c in matrix["cells"]
    )
    extension = sum(
        Decimal(str(prices[c["condition"] + ":" + c["dataset"]]["solo_hours"]))
        for c in matrix["extension"]["cells"]
    )
    assert float((core + extension) * Decimal("1.15")) == cost["expected_process_hours"]
    measurements = [d9.read_metadata(c["measurement"]) for c in cost["cells"]]
    for c, e in zip(cost["cells"], measurements, strict=True):
        measured = e["measured_peak_device_mib"]
        assert c["peak_device_mib"] == (measured * 1.5 if measured else None)
        assert c["peak_host_mib"] is None
        for b in e["source_bindings"]:
            assert d9.ref(b["path"])["sha256"] == b["sha256"]
    pretended = copy.deepcopy(cost)
    pretended.update(lead_approved=True, status="closed")
    try:
        d9.check_receipt("chain_i_cell_ceilings", pretended, spec)
    except ValueError as exc:
        cost_error = str(exc)
    else:
        raise AssertionError("unsigned/pending cost was incorrectly admissible")
    profiles = []
    for r in profile_inventory():
        assert r["status"] == "complete"
        checkpoint = json.loads(Path(r["checkpoint"]["path"]).read_text())
        _, bounded, _ = preservation_section(
            checkpoint["locality"], checkpoint["locality"]["expected_ids"], "query"
        )
        assert bounded["numerator"] == r["locality"]["preserved_n"]
        unseen = checkpoint["unseen"]["rows"]
        scored = [
            x
            for x in unseen
            if type(x.get("false_fire")) is bool and x.get("firing_status") == "ok"
        ]
        profiles.append(
            dict(
                condition=r["condition"],
                bounded_locality=bounded["numerator"],
                locality_planned=bounded["planned"],
                RET_GS=r["retention"]["gs"],
                unseen_scored=len(scored),
                unseen_planned=len(unseen),
                unseen_fires=sum(x["false_fire"] for x in scored)
                if len(scored) == len(unseen)
                else None,
                recipe=r["recipe"],
                result=r["result"],
                checkpoint=r["checkpoint"],
            )
        )
    report = dict(
        task="X17",
        verdict="NOT_READY_FOR_SIGNATURE_OR_LAUNCH",
        candidate=cp,
        verification=proof,
        normative_closure=candidate["normative_closure"],
        protocol=candidate["protocol"],
        cost_receipt=candidate["cost_admission_source_unsigned"],
        cost_gate_error=cost_error,
        signature_flag_alone_refused=True,
        signatures_only=False,
        closed_X16_findings=[
            "X16-01 normative closure",
            "X16-04 pair-unit semantics",
            "X16-07 notes arithmetic",
            "X16-09 unavailable firing notes",
            "X16-10 protocol contradiction",
        ],
        partial_X16_findings=[
            "X16-02 typed schema fixed; evidence and lead approval pending",
            "X16-05 refreshed package; subsequent evidence requires successor bindings",
        ],
        open_X16_findings=[
            "X16-03 complete cost evidence",
            "X16-06 whole publication producer missing",
            "X16-08 substantive gates and actual population operations",
        ],
        numeric=dict(
            core_cells=len(matrix["cells"]),
            extension_cells=len(matrix["extension"]["cells"]),
            block_counts=dict(Counter(c["block_number"] for c in cells)),
            core_solo_hours=float(core),
            extension_solo_hours=float(extension),
            projected_total_process_hours=float((core + extension) * Decimal("1.15")),
            proposed_process_budget=cost["shared_process_hours"],
            core_wall_projection=float(core / Decimal("1.65")),
            full_two_attempt_padded_total=float(
                (core + extension) * Decimal("1.5") * Decimal("1.15") * 2
            ),
            primary_intervals=63,
            unavailable_mquake_intervals=21,
            confidence=1 - 0.05 / 63,
            gpu_peak_rows=sum(e["measured_peak_device_mib"] is not None for e in measurements),
            host_peak_rows=0,
            endpoint_complete_rows=sum(
                e["full_endpoint_evidence_status"] == "complete" for e in measurements
            ),
        ),
        full_endpoint_profiles=candidate["full_endpoint_profiles"],
        corrected_profiles=profiles,
        decision_trace=[
            dict(
                decision=f"DEC-{n:03}",
                status=s,
                text_trace=t.replace(
                    "Q16 allocation is a separate pending decision.",
                    "Allocation adopted by DEC-062 and incorporated into D.1.",
                ),
            )
            for n, (s, t) in TRACE.items()
        ],
        DEC062="adopted B; repeated disjoint pairs per family explicitly approved and amended",
        non_signature_blockers=candidate["non_signature_blockers"],
        risks=[
            "Four R1-64f runs remain unexecuted; no numerical endpoint costs inferred from recipe completeness.",
            "Four representative runs do not measure every other condition; any cost transfer across conditions needs explicit reviewed assumptions.",
            "Host MemAvailable6144MiB is enforced by the operator's signed-cost launch floor, but is not a measured host peak.",
            "30s startup/validation is an estimate;128 drift windows do not replace the full validation split.",
            "750 process hours is a proposed shared budget;764.3475h is the all-cells-two-full-ceilings bound, so budget exhaustion can leave cells incomplete.",
            "Development pools are historically exposed, including legacy MQuAKE training; not the independent DEC-056 occupancy diagnostic.",
            "New recipe declarations must enter current exposure attestation before actual draw; normalized-subject intersection was zero but is not a new clearance receipt.",
            "Whole final-recipe/freeze bundle assembler remains missing; interface documentation is not executable production assembly.",
            "Three-cluster inference remains nominal; MQuAKE1000 claims stay unavailable;6036/6084 zsRE baselines are empty.",
        ],
        notes=d9.ref(ROOT / "docs/R1_stage2_notes.md"),
        decisions=d9.ref(ROOT / "docs/decisions.md"),
        task_list=d9.ref(ROOT / "docs/ongoing.md"),
        producer=d9.ref(__file__),
        gpu_seconds=0,
        actual_draws=0,
        seals=0,
        signatures=0,
        HT4f="blocked; cost v2 unsigned and evidence pending",
    )
    write_new(ROOT / "logs/r1_round28/r1-x17-review.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "verdict",
                    "numeric",
                    "closed_X16_findings",
                    "partial_X16_findings",
                    "open_X16_findings",
                )
            },
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    run()
