"""HT-16: conservative capacity check; no draw, model call or reserved-data use."""

from __future__ import annotations

import json
from pathlib import Path

from aw.r_extension import (
    ROOT,
    clearance_value,
    exclude_reserved,
    load_bound,
    ref,
    source_rows,
)


def audit():
    preparation = ROOT / "logs/additional_work/R/preparation-v1.json"
    record = json.loads(preparation.read_bytes())
    spec = load_bound(record["input_spec"])
    previous = load_bound(record["original_reservations"])
    option_r = load_bound(record["reservations"])
    register = load_bound(spec["register"])
    evidence = load_bound(record["evidence"])
    cleared = clearance_value(spec, register, evidence, source_rows(register))["candidates"]
    blocked = dict(allocations=previous["allocations"] + option_r["allocations"])
    remaining = exclude_reserved(cleared, blocked)
    r0 = [g for g in previous["allocations"] if g["dataset"] == "zsre" and g["realization"] == 0]
    all_r0 = sum(len(g["items"]) for g in r0)
    edits_r0 = sum(len(g["items"]) for g in r0 if g["role"] == "edits")
    fresh = len(remaining["zsre"])
    if (all_r0, edits_r0, fresh) != (1350, 1000, 684):
        raise ValueError("capacity changed; review the scoped conclusion before publication")
    report = dict(
        status="closed_population_infeasible",
        task="HT-16",
        model_calls=0,
        gpu_seconds=0,
        dataset="zsre",
        wanted=3000,
        retained_r0_edits=edits_r0,
        retained_r0_all_roles=all_r0,
        remaining_after_all_primary_and_R_reservations=fresh,
        capacity_preserving_r0_endpoints=edits_r0 + fresh,
        generous_upper_bound_even_repurposing_r0_endpoints=all_r0 + fresh,
        minimum_shortfall_even_with_endpoint_repurposing=3000 - all_r0 - fresh,
        identity_exclusions=["item", "fact", "global entity", "canonical subject"],
        population_scope="existing certified universe; all roles of other primary realizations and Option R excluded",
        note="Later exposures can only reduce this upper bound. No repeated subjects, endpoint cannibalization or new source acquisition is authorized as a substitute.",
        sources=[
            ref(preparation),
            record["input_spec"],
            record["original_reservations"],
            record["reservations"],
            record["evidence"],
            spec["register"],
            ref(Path(__file__)),
        ],
    )
    out = ROOT / "logs/additional_work/round54/HT-16-population.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    (ROOT / "docs/tasks/HT-16.md").write_text(
        "# HT-16 — 3,000-edit population check\n\n"
        "2026-09-29, Capex. **Closed: infeasible within the admitted population.** Replaying the certified clearance "
        "and excluding every reserved item/fact/entity/canonical subject in primary realizations 0–2 and Option R "
        "leaves **684 zsRE subjects**. Adding these to realization 0's 1,000 edit subjects gives at most **1,684 edits** "
        "while preserving its endpoints. Even the impermissibly generous bound that repurposes all 350 realization-0 "
        "endpoint subjects reaches only **2,034**, still 966 short of 3,000. Later exposures can only reduce this "
        "bound. No recipe or GPU job is produced; Option R and other realizations remain untouched. Additional "
        "data clearance or a changed population would be a different study. Inputs/counts are in "
        "`logs/additional_work/round54/HT-16-population.json`; replay with the CPU environment and "
        "`../venv/bin/python -m aw.ht16_population`. CPU metadata only, zero GPU/model calls.\n"
    )
    (ROOT / "docs/tasks/HT-16.completion.json").write_text(
        json.dumps(
            dict(
                task="HT-16",
                status="complete_population_infeasible",
                agent="Capex",
                date="2026-09-29",
                task_record="docs/tasks/HT-16.md",
                gpu_seconds=0,
                remaining=None,
            ),
            indent=2,
        )
        + "\n"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
