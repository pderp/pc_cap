"""Independent numerical/decision audit of the unsigned signature package.

Writes only new review reports; no fixes, signature, model, draw, seal or freeze.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.ht4e_claim_ledger import profile_inventory
from scripts.r1_58g_operator import cost_source
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_75_analysis_stage4_v1 import preservation_section
from scripts.r1_d10a_review import ROOT, write_new

TRACE = {
    33: (
        "adopted; budget superseded by044",
        "Final text opening + v5.1 §§2,5,6: margins, fidelity, fresh roles; plan9/guide remain specification.",
    ),
    34: (
        "adopted delegated amendment",
        "v5.1 §2 conditions/control table, §4 exclusion register, §§5–7 full-episode/cost/restoration requirements; Stage3 coupling remains conditional.",
    ),
    35: (
        "adopted delegated control",
        "v5.1 §2 v0_stable row; matrix includes45 cells of this condition.",
    ),
    36: (
        "historical correction; outside eight core arms",
        "spec_defects SD-24 and stage2 notes preserve ePC energy correction; historical v0 SE-E is not rerun or silently relabelled.",
    ),
    37: (
        "training-only source decision",
        "v5.1 §4/current evidence exclude CF training exposures; train_pool_counterfact_v1 records3000; no reuse as confirmatory observations.",
    ),
    38: (
        "withdrawn proposal; no accepted decision row",
        "lead_queue items11/recovery and stage2_report: dropping learned reader was withdrawn. Primary v5 remains learned.",
    ),
    39: (
        "training-only source decision",
        "v5.1 §4/current evidence reserve all6000 zsRE candidates, including the3000 training subset; E.2 is unchanged.",
    ),
    40: (
        "adopted two S1 treatments",
        "v5.1 §2 S1_LM/S1_literal and §3 fidelity; both conditions are in block5. Final-v5 budget matching still U03.",
    ),
    41: (
        "adopted exclusion policy with later versions",
        "v5.1 §4 + final Population and exposure; operative v6 policy includes all later declaration snapshots.",
    ),
    42: (
        "accepted exception",
        "Final population and v5.1 §4: CounterFact old-pool-membership-only exception; not a wholly fresh external source.",
    ),
    43: (
        "accepted rare-token gate",
        "v5.1 §1/2 and primary_condition_v5; ungatedv2 is the optional45-cell package contrast.",
    ),
    44: (
        "accepted full scope",
        "Final Receipt contract:360core+45optional; 15h envelope superseded, no scope cut.",
    ),
    45: (
        "accepted third dataset",
        "Final layout: zsRE, CounterFact, MQuAKE-CF; only MQ cadence later changed by060.",
    ),
    46: (
        "training/split proposal superseded by operational v3 slices",
        "v5.1 §1/4 and primaryv5 source bindings identify actual self-contained MQ train/dev versions; initial proposed counts not final capacity.",
    ),
    47: (
        "accepted LM fidelity result",
        "v5.1 §1/3 identifies lr1e-8 LM continuation, KL.0004736076 and loss-.0088596493; failed lr1e-6 remains historical.",
    ),
    48: (
        "accepted source-query exemption; scope later060",
        "Final Population and exposure + v5.1 §4: true-fact query roles exempt for later counterfactual edits, other exclusions retained.",
    ),
    49: (
        "accepted three-dataset selection",
        "v5.1 §2 reference selection and primary_condition_v5; exact weight average is bound, not reselected.",
    ),
    50: (
        "accepted selection gate",
        "v5.1 §2: maximize mean RET-GS with zsRE unseen≤.10 at100 and LS≥.98; distinct from confirmatory unseen≤.15.",
    ),
    51: (
        "accepted execution order",
        "Final block inventory plus matrix queue fields:45,45,90,90,90 then optional45; all coordinates reproduced.",
    ),
    52: (
        "accepted complete-or-explicitly-incomplete reporting",
        "Final Costs/inventory: October9stop, DEC052 inventory and full scope; earlier cost review is delegated but future schedule receipt still needed.",
    ),
    53: (
        "accepted bounded equality",
        "Final near family/scoring + v5.1 §5; raw corrected MQ locality traces independently rescored, termination diagnostics retained.",
    ),
    54: (
        "accepted exploratory κ pilot",
        "v5.1 §6 side-panel scheduling + kappa_pilot_v3 + heavy_tail_counter_review §4; preliminary hints, not coupled free energy or one-κ test.",
    ),
    55: (
        "accepted development stress panel",
        "v5.1 §6 + ht_development_panel_v1: six cells,100edits,20/60/70/80/100 probes,4GPUh ceiling; never a confirmatory replacement.",
    ),
    56: (
        "accepted MQ occupancy diagnostic",
        "R1-76b artifacts and final actual300 caveat: historically exposed700-row review, common outside100/300, no1000claim.",
    ),
    57: (
        "accepted63-interval family",
        "Final analysis + incorporated v5.1 §5.3:7×3×3, .05/63, 10000draws, seed0, float64, linear quantiles, three realization clusters.",
    ),
    58: (
        "accepted classifier",
        "Incorporated v5.1 §5.3 + r1_49g_inference; strict bounds, negative priority, unchanged .05/-.02/-.01 margins.",
    ),
    59: (
        "accepted secondary thresholds",
        "Incorporated v5.1 §5.1 and matrix secondary_benchmarks; MQ1000 thresholds unavailable, no transferred300pass.",
    ),
    60: (
        "accepted optionD",
        "Final population/cadence:1000/1000/300, demands4050/4050/1950, three realizations; MQ21 primary intervals unavailable.",
    ),
    61: (
        "accepted NM-template-v1",
        "Final adopted-family section and shared source validator: different subjects/exact family, neighbour baseline equality, planned100 fixed. Q16 allocation is a separate pending decision.",
    ),
}


def run():
    log = ROOT / "logs/r1_round27"
    paths = [
        "docs/decisions.md",
        "docs/R1_stage4_protocol_v5_2_D_final.md",
        "docs/R1_stage4_protocol_draft_v5_1.md",
        "docs/R1_execution_plan_v2.md",
        "docs/R1_stage4_queue_concurrency_v2.md",
        "docs/tasks/R1-cost-admission-receipt-v1.json",
        "manifests/revision_v1/cell_ceilings_v1.json",
        "manifests/revision_v1/run_matrix_v5_2_D_DEC061.json",
        "manifests/revision_v1/freeze_candidate_v9.json",
        "manifests/revision_v1/freeze_candidate_v10.json",
        "docs/tasks/R1-D9-inputs-v4.json",
        "docs/tasks/R1-D9-inputs-v5.json",
        "docs/R1_stage2_notes.md",
        "docs/lead_queue.md",
    ]
    bindings = {p: d9.ref(ROOT / p) for p in paths}

    def read(p):
        return d9.read_metadata(bindings[p])

    matrix = read("manifests/revision_v1/run_matrix_v5_2_D_DEC061.json")
    prices = read("manifests/revision_v1/cell_ceilings_v1.json")["cells"]
    cost = cost_source()
    blocks = defaultdict(lambda: defaultdict(Decimal))
    for key, row in prices.items():
        assert Decimal(str(row["solo_hours"])) * 3600 * Decimal("1.5") == row["ceiling_seconds"], (
            key
        )
    all_cells = matrix["cells"] + matrix["extension"]["cells"]
    for c in all_cells:
        blocks[c["block_number"]][c["dataset"]] += Decimal(
            str(prices[c["condition"] + ":" + c["dataset"]]["solo_hours"])
        )
    core = sum(sum(v.values()) for k, v in blocks.items() if k <= 5)
    extra = sum(blocks[6].values())
    numeric = dict(
        core_cells=len(matrix["cells"]),
        extension_cells=len(matrix["extension"]["cells"]),
        block_counts=dict(Counter(c["block_number"] for c in all_cells)),
        blocks={
            k: dict(
                by_dataset={d: float(v) for d, v in values.items()},
                total=float(sum(values.values())),
            )
            for k, values in blocks.items()
        },
        core_solo_hours=float(core),
        extension_solo_hours=float(extra),
        total_solo_hours=float(core + extra),
        core_wall_projection_at_1_65=float(core / Decimal("1.65")),
        total_wall_projection_at_1_65=float((core + extra) / Decimal("1.65")),
        core_effective_ceiling_process_hours=float(core * Decimal("1.5") * Decimal("1.15")),
        total_effective_ceiling_process_hours=float(
            (core + extra) * Decimal("1.5") * Decimal("1.15")
        ),
        max_two_attempt_core_ceiling_process_hours=float(
            core * Decimal("1.5") * Decimal("1.15") * 2
        ),
        max_two_attempt_total_ceiling_process_hours=float(
            (core + extra) * Decimal("1.5") * Decimal("1.15") * 2
        ),
        primary_intervals=7 * 3 * 3,
        unavailable_mquake_intervals=7 * 3,
        adjusted_confidence=1 - 0.05 / 63,
        bootstrap=matrix["multiplicity"],
        ceiling_rows=len(prices),
        finite_positive_ceilings=True,
    )
    assert numeric["core_solo_hours"] == cost["admitted"]["core_solo_hours"] == 209.4
    assert numeric["block_counts"] == {1: 45, 2: 45, 3: 90, 4: 90, 5: 90, 6: 45}
    profiles = []
    for row in profile_inventory():
        assert row["status"] == "complete"
        assert d9.ref(row["checkpoint"]["path"]) == row["checkpoint"]
        checkpoint = json.loads(Path(row["checkpoint"]["path"]).read_text())
        summary, bounded, terminated = preservation_section(
            checkpoint["locality"], checkpoint["locality"]["expected_ids"], "query"
        )
        assert summary["preserved_n"] == row["locality"]["preserved_n"]
        unseen = checkpoint["unseen"]["rows"]
        profiles.append(
            dict(
                condition=row["condition"],
                attempt_wall_seconds=row["attempt_wall_seconds"],
                ES=row["retention"]["es"],
                RET_GS=row["retention"]["gs"],
                locality_preserved=bounded["numerator"],
                locality_planned=bounded["planned"],
                locality_terminated_preserved=terminated["numerator"],
                unseen_fires=(
                    sum(r["false_fire"] for r in unseen)
                    if all(
                        type(r.get("false_fire")) is bool and r.get("firing_status") == "ok"
                        for r in unseen
                    )
                    else None
                ),
                unseen_scored=sum(
                    type(r.get("false_fire")) is bool and r.get("firing_status") == "ok"
                    for r in unseen
                ),
                unseen_planned=len(unseen),
                references={k: row[k] for k in ("recipe", "result", "checkpoint", "receipt")},
            )
        )
    pool = d9.read_metadata(d9.ref(log / "r1-d9f-real-pool.json"))
    old = read("manifests/revision_v1/freeze_candidate_v9.json")
    current = read("manifests/revision_v1/freeze_candidate_v10.json")
    current_verification = verify(current)
    inherited = str(ROOT / "docs/R1_stage4_protocol_draft_v5_1.md")
    inherited_bound = {c["name"]: inherited in c["bindings_sha256"] for c in (old, current)}
    assert all(not v for v in inherited_bound.values())
    old_drift = [p for p, h in old["bindings_sha256"].items() if d9.sha(p) != h]
    spec = read("docs/tasks/R1-D9-inputs-v5.json")
    pretend = copy_json(cost)
    pretend["lead_approved"] = True  # in-memory schema probe only; never written as approval
    try:
        d9.check_receipt("chain_i_cell_ceilings", pretend, spec)
        shape_error = None
    except (ValueError, KeyError, TypeError) as e:
        shape_error = str(e)
    assert shape_error
    decisions = (ROOT / "docs/decisions.md").read_text().splitlines()
    trace = []
    for n, (status, target) in TRACE.items():
        identity = f"DEC-{n:03d}"
        row = next(
            (
                r
                for r in decisions
                if r.startswith("| " + identity + " ") or r.startswith("| " + identity + "(")
            ),
            None,
        )
        if n != 38:
            assert row is not None, identity
        trace.append(
            dict(
                decision=identity,
                status=status,
                text_trace=target,
                decision_row=row,
                decision_row_sha256=d9.core.content_digest(row) if row else None,
            )
        )
    report = dict(
        task="X16",
        verdict="NOT_READY_FOR_LEAD_SIGNATURE_OR_LAUNCH",
        incoming_v9_verification=d9.ref(log / "incoming-candidate-verification.json"),
        current_v10_verification=current_verification,
        v9_drift_from_authorized_hook=old_drift,
        inherited_protocol_bound=inherited_bound,
        cost_lead_approved=cost["lead_approved"],
        signed_flag_only_cost_schema_probe_error=shape_error,
        numeric=numeric,
        corrected_profiles=profiles,
        allocation_diagnostic=pool["modes"],
        decision_trace=trace,
        bindings=bindings,
        findings=[
            "X16-01 inherited normative v5.1 text is not hash-bound in either candidate",
            "X16-02 cost receipt v1 is unsigned and not the typed schema accepted by freeze/HT-4f",
            "X16-03 memory ceilings, explicit process-hour budget, full validation/endpoint cost evidence are absent",
            "X16-04 Q16 is not DEC-062; multiple pairs/family and unchanged-backbone algorithm require explicit admission",
            "X16-05 old v9/form digests changed under authorized draw hook; use new unsigned operator package after review",
            "X16-06 no production final-freeze/recipe publication bundle exists yet; operator validates/publishes but cannot invent it",
            "X16-07 notes206/125/+16 are stale; authoritative table gives209.4/126.91/+12.15",
            "X16-08 signature readiness still includes17open gates plus actual population operations",
            "X16-09 six v0/S1 corrected profiles have100unavailable firing rows, not the0/100reported in ChainQ notes",
        ],
        not_reproduced_as_measurements=[
            "full-final-endpoint process times for all conditions/datasets",
            "peak-host/device ceilings",
            "whole-matrix throughput",
            "future final near availability",
            "full validation split admission",
        ],
        gpu_seconds=0,
        actual_draws=0,
        seals=0,
        signatures=0,
        review_fixes_applied=False,
        producer=d9.ref(__file__),
    )
    for b in bindings.values():
        assert d9.ref(b["path"]) == b
    write_new(log / "r1-x16-audit.json", report)
    print(
        json.dumps(
            dict(
                verdict=report["verdict"],
                numeric=numeric,
                cost_schema_error=shape_error,
                inherited_protocol_bound=inherited_bound,
            ),
            indent=2,
        )
    )


def copy_json(value):
    return json.loads(json.dumps(value))


if __name__ == "__main__":
    run()
