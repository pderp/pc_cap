"""R1-72 deterministic scheduling arithmetic; no jobs, scope changes or advice."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo("America/New_York")
START = datetime(2026, 9, 21, tzinfo=ZONE)
CUTOFF = datetime(2026, 10, 8, tzinfo=ZONE)
STOP = datetime(2026, 10, 10, tzinfo=ZONE)
AVAILABILITY = 0.75
PRIMARY = ("R1_learned_ff", "R1_nonlearned", "v0_stable")
OTHER = ("matched_update", "v0_live_C1", "v0_live_C2")
FIRST_SIX = PRIMARY + OTHER
S1 = ("S1_LM", "S1_literal")
LIVE = {"v0_live_C1", "v0_live_C2"}
SCENARIOS = (
    ("measured_48", "measured-profile extrapolation: 48 min for every cell", 48, 48),
    ("measured_66", "measured-profile extrapolation: 66 min for every cell", 66, 66),
    ("target_20", "R1-68c target: 20 min for every cell; UNMEASURED", 20, 20),
    ("live80_other48", "pessimistic live controls: 80 min live; 48 min others", 48, 80),
    ("live80_other66", "pessimistic live controls: 80 min live; 66 min others", 66, 80),
)


def timestamp(gpu_hours):
    return (START + timedelta(hours=gpu_hours / AVAILABILITY)).isoformat()


def blocks(matrix, norders):
    orders = set(matrix["axes"]["order_seeds"][:norders])
    core = [c for c in matrix["cells"] if c["order_seed"] in orders]
    extension = [c for c in matrix["extension"]["cells"] if c["order_seed"] in orders]

    def choose(conditions, realizations):
        rows = [
            c
            for c in core
            if c["condition_id"] in conditions and c["realization_seed"] in realizations
        ]
        return sorted(
            rows,
            key=lambda c: (
                matrix["axes"]["datasets"].index(c["dataset"]),
                conditions.index(c["condition_id"]),
                c["realization_seed"],
                c["order_seed"],
            ),
        )

    out = [
        ("B1", "primary + random + v0-stable, realization 0", choose(PRIMARY, (0,))),
        ("B2", "matched + v0-live C1/C2, realization 0", choose(OTHER, (0,))),
        ("B3", "first six conditions, realization 1", choose(FIRST_SIX, (1,))),
        ("HT", "reserved kappa 3h + stress 4h before realization 2", []),
        ("B4", "first six conditions, realization 2", choose(FIRST_SIX, (2,))),
        ("B5", "two S1 conditions, all realizations", choose(S1, (0, 1, 2))),
        ("B6", "secondary v2 extension, all realizations", extension),
    ]
    ids = [c["cell_id"] for _, _, rows in out for c in rows]
    assert len(ids) == len(set(ids)) == 81 * norders
    assert len(core) == 72 * norders and len(extension) == 9 * norders
    return out


def schedule(matrix, norders, normal, live, accepted_incomplete=False):
    cumulative = 0.0
    output = []
    eligible = []
    missed = []
    cutoff_gpu = (CUTOFF - START).total_seconds() / 3600 * AVAILABILITY
    for block, label, cells in blocks(matrix, norders):
        start = cumulative
        done = 0
        row_costs = []
        if block == "HT":
            cumulative += 7
        else:
            for c in cells:
                hours = (live if c["condition_id"] in LIVE else normal) / 60
                cumulative += hours
                record = {
                    "cell_id": c["cell_id"],
                    "condition": c["condition_id"],
                    "dataset": c["dataset"],
                    "realization": c["realization_seed"],
                    "order_seed": c["order_seed"],
                    "hours": hours,
                    "hypothetical_completion": timestamp(cumulative),
                }
                row_costs.append(record)
                if cumulative <= cutoff_gpu + 1e-9:
                    done += 1
                    eligible.append(record)
                else:
                    missed.append(record)
        output.append(
            {
                "block": block,
                "description": label,
                "cells": len(cells),
                "gpu_hours": round(cumulative - start, 9),
                "cumulative_gpu_hours": round(cumulative, 9),
                "calendar_start": timestamp(start),
                "hypothetical_calendar_finish": timestamp(cumulative),
                "complete_by_oct8_start": cumulative <= cutoff_gpu + 1e-9,
                "cells_complete_by_oct8_start": done,
                "cell_costs": row_costs,
            }
        )
    core_done = sum(not r["condition"].endswith("_v2") for r in eligible)
    ext_done = len(eligible) - core_done
    return {
        "order_count": norders,
        "scope": "accepted incomplete, full target retained"
        if accepted_incomplete
        else "full"
        if norders == 5
        else "three-order amendment arithmetic only",
        "planned_core": 72 * norders,
        "planned_extension": 9 * norders,
        "total_cells": 81 * norders,
        "total_gpu_hours_with_HT_reservation": round(cumulative, 9),
        "core_plus_HT_gpu_hours": round(
            sum(r["gpu_hours"] for r in output if r["block"] != "B6"), 9
        ),
        "hypothetical_full_finish": timestamp(cumulative),
        "fits_before_oct8": cumulative <= cutoff_gpu + 1e-9,
        "prefix_by_oct8": {
            "core_cells": core_done,
            "extension_cells": ext_done,
            "total_cells": len(eligible),
            "missing_cells": len(missed),
            "last_completed_cell": eligible[-1] if eligible else None,
        },
        "accepted_incomplete_policy": "If approved, stop the new-cell queue at Oct8 start and retain identities of the unrun suffix; Oct8–9 remains failed-cell rerun reserve."
        if accepted_incomplete
        else None,
        "missing_cell_ids_at_cutoff": [r["cell_id"] for r in missed],
        "blocks": output,
    }


def build():
    path = ROOT / "manifests/revision_v1/run_matrix_draft_v4.json"
    matrix = json.loads(path.read_text())
    results = []
    for key, label, normal, live in SCENARIOS:
        results.append(
            {
                "scenario": key,
                "label": label,
                "other_minutes": normal,
                "v0_live_minutes": live,
                "scope_options": {
                    "full": schedule(matrix, 5, normal, live),
                    "three_orders": schedule(matrix, 3, normal, live),
                    "accepted_incomplete": schedule(matrix, 5, normal, live, True),
                },
            }
        )
    return {
        "task": "R1-72",
        "mode": "arithmetic_only_no_schedule_approval",
        "start": START.isoformat(),
        "new_cell_cutoff": CUTOFF.isoformat(),
        "experimental_hard_stop": STOP.isoformat(),
        "availability": AVAILABILITY,
        "wall_hours_before_oct8": 408,
        "usable_gpu_hours_before_oct8": 306,
        "rerun_reserve_oct8_oct9_gpu_hours": 36,
        "HT_reservation_hours": 7,
        "HT_reservation_requires_Q4_Q5": True,
        "matrix": {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        "measured_anchor": {
            "300_edit_full_cell_seconds": 1262,
            "300_edit_incremental_seconds": 1246,
            "note": "48/66 min are 1000-edit extrapolations, not measured universal cell costs",
        },
        "assumptions": [
            "75% availability is a continuously spread average, not an hourly booking",
            "no unpriced additional shared training/setup/retries inside the 306h window",
            "7h reserved before realization2 whether or not pilots ultimately approved",
            "three-order arithmetic uses first three existing order labels only for identity counting, not a proposed order choice",
            "unprofiled controls inherit scenario costs; only pessimistic v0-live costs are overridden to 80min",
            "dates after Oct9 are counterfactual feasibility outputs, never execution authorization",
        ],
        "scenarios": results,
        "recommendation": None,
        "gpu_seconds": 0,
    }


def markdown(doc):
    lines = [
        "# R1-72 — execution schedule arithmetic",
        "",
        "Status: complete; no schedule/scope recommendation. Agent: Codex.",
        "",
        "Inputs: matrix v4 (360 core +45 extension), measured v5 300-edit profile, counter-review §5.1, Q6/Q7. Outputs: this memo, logs/r1_round16/schedule_options.json, scripts/r1_72_schedule_options.py.",
        "",
        "Assume a September 21, 00:00 EDT start and 75% continuously averaged availability. The new-cell window closes October 8, 00:00 EDT: 408 wall hours × .75 = **306 usable GPU hours**. October 8–9 reserves another 36 usable GPU hours for failed-cell reruns; all experiments stop before October 10. Dates after that stop are counterfactual arithmetic, not permission to run late.",
        "",
        "Every schedule includes a conditional **7h reservation** (κ3h + stress4h) before realization2; Q4/Q5 still control execution. No other extra training/retry cost is invented. Additional work reduces the displayed capacity.",
        "",
        "The 48/66-minute costs are extrapolations from the measured 1,262s/300-edit v5 cell: final-only versus every-checkpoint drift assumptions. Applying them across unprofiled controls is a scenario, not a measurement. The ~20-minute target is unmeasured. The pessimistic family applies 80 minutes only to the two v0-live conditions, retaining the 48/66-minute range elsewhere.",
        "",
        "| Cost scenario | Scope | Core + extension | Total GPU h incl. HT | Hypothetical full finish (EDT) | Core / extension complete by Oct8 |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    for scenario in doc["scenarios"]:
        for key in ("full", "three_orders"):
            r = scenario["scope_options"][key]
            prefix = r["prefix_by_oct8"]
            finish = datetime.fromisoformat(r["hypothetical_full_finish"]).strftime("%b %d %H:%M")
            lines.append(
                f"| {scenario['scenario']} | {key} | {r['planned_core']} + {r['planned_extension']} | {r['total_gpu_hours_with_HT_reservation']:.1f} | {finish} | {prefix['core_cells']} / {prefix['extension_cells']} |"
            )
    lines += [
        "",
        "**Accepted incomplete** retains the full 360+45 target and uses the full-scope completed prefix in the table, with every missing cell ID explicitly recorded in JSON. It is an acknowledgement of missing planned evidence, not another faster design. Three orders changes scope to 216+27 cells; choosing which three orders and amending inference remain the lead's decisions.",
        "",
        "Block order: B1 primary/random/v0-stable at r0; B2 matched/two live at r0; B3 first six at r1; HT reservation; B4 first six at r2; B5 both S1 across all realizations; B6 extension. Within core blocks, dataset, listed condition, realization and order provide a deterministic arithmetic ordering.",
    ]
    for scenario in doc["scenarios"]:
        lines += [
            "",
            f"## {scenario['label']}",
            "",
            "| Scope | Block | Cells | Block GPU h | Cumulative GPU h | Hypothetical finish (EDT) | Complete by Oct8? |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
        for key in ("full", "three_orders"):
            for r in scenario["scope_options"][key]["blocks"]:
                finish = datetime.fromisoformat(r["hypothetical_calendar_finish"]).strftime(
                    "%b %d %H:%M"
                )
                status = (
                    "yes"
                    if r["complete_by_oct8_start"]
                    else f"no ({r['cells_complete_by_oct8_start']}/{r['cells']} cells)"
                )
                lines.append(
                    f"| {key} | {r['block']} | {r['cells']} | {r['gpu_hours']:.1f} | {r['cumulative_gpu_hours']:.1f} | {finish} | {status} |"
                )
    lines += [
        "",
        "Verify command: ../venv/bin/python -B -m scripts.r1_72_schedule_options (exclusive creation; use build() for read-only recalculation). Verification asserts every matrix cell appears once, full totals 360+45, reduced totals 216+27, and the 17-day ×18h/day capacity. JSON includes costs and completion times for every cell and identifies the unrun suffix at cutoff.",
        "",
        "Done-when: requested block/scope/date arithmetic delivered. Cost: GPU0; CPU arithmetic only. Deviations: three requested cost families are expanded into five rows to show both ends of the measured range and the live-control pessimistic range. Unresolved: owner re-profiles all controls and the new driver, then the lead decides Q6/Q7 by September20. No recommendation, board edit, new execution, or commit.",
    ]
    return "\n".join(lines) + "\n"


def main():
    doc = build()
    paths = [
        (
            ROOT / "logs/r1_round16/schedule_options.json",
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
        ),
        (ROOT / "docs/tasks/R1-72.md", markdown(doc)),
    ]
    if any(p.exists() for p, _ in paths):
        raise FileExistsError("schedule outputs already exist")
    for p, text in paths:
        with p.open("x") as f:
            f.write(text)
    for s in doc["scenarios"]:
        print(
            s["scenario"],
            [
                (k, v["total_gpu_hours_with_HT_reservation"], v["prefix_by_oct8"]["total_cells"])
                for k, v in s["scope_options"].items()
            ],
        )


if __name__ == "__main__":
    main()
