"""Strict prospective DEC-066 scope; omitted cells are not observed zero results."""

from __future__ import annotations

from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS

MQUAKE_CORE = ("R1_learned_ff", "R1_nonlearned", "v0_stable")
OMITTED = tuple(c for c in CORE_CONDITIONS if c not in MQUAKE_CORE)
CONTRACT = dict(
    decision="DEC-066",
    core_conditions_by_dataset={
        d: list(MQUAKE_CORE if d == "mquake" else CORE_CONDITIONS)
        for d in ("zsre", "counterfact", "mquake")
    },
    omitted_mquake_conditions=list(OMITTED),
    omission_status="prospectively_not_run_calibration_v3_radius_zero; not measured results",
    extension="unchanged_45_cells",
    draw_demand="unchanged_per_dataset_per_realization",
    primary_interval_family=63,
)


def conditions(matrix):
    reduced = matrix.get("policy_revision") == "DEC066_D4" or "prospective_scope" in matrix
    if not reduced:
        return {d: list(CORE_CONDITIONS) for d in ("zsre", "counterfact", "mquake")}
    if (
        matrix.get("policy_revision") != "DEC066_D4"
        or matrix.get("prospective_scope") != CONTRACT
        or matrix["axes"].get("core_conditions_by_dataset")
        != CONTRACT["core_conditions_by_dataset"]
    ):
        raise ValueError("exact DEC-066 prospective scope required")
    return CONTRACT["core_conditions_by_dataset"]
