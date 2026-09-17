"""DEC-059 secondary descriptive cell and equal-weight macro benchmarks.

A passing macro never erases cell failures. Unsupported observers, incomplete
inventories, missing actual occupancy and unadmitted ceilings stay unavailable.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
from scripts import r1_75_analysis_stage4_v1 as old
from scripts.r1_49g_inference import finite

THRESHOLDS = {
    "unseen_1000": ("le", 0.15),
    "outside_change_1000_100": ("abs_le", 0.05),
    "revision_latest": ("ge", 0.95),
    "old_alias_reappearance": ("le", 0.02),
    "revision_semantic": ("ge", 0.95),
    "retention_change": ("ge", -0.05),
    "es_change": ("ge", -0.02),
    "ls_change": ("ge", -0.01),
    "state_budget_ratio": ("le", 1.0),
    "peak_budget_ratio": ("le", 1.0),
    "wall_budget_ratio": ("le", 1.0),
}


def benchmark(name, value, *, reason=None, **extra):
    op, threshold = THRESHOLDS[name]
    available = finite(value)
    passes = (
        (
            value <= threshold
            if op == "le"
            else value >= threshold
            if op == "ge"
            else abs(value) <= threshold
        )
        if available
        else None
    )
    return {
        "status": "complete" if available else "unavailable",
        "value": float(value) if available else None,
        "passes": bool(passes) if available else None,
        "operator": op,
        "threshold": threshold,
        "role": "secondary_descriptive",
        "reason": reason,
        **extra,
    }


def _case_rate(rows, expected, field, transform=None):
    by = old.ordered_rows(rows, expected, "item_id")
    values = []
    for identity in expected:
        row = by.get(identity, {})
        value = transform(row) if transform and row.get("status") == "ok" else row.get(field)
        values.append(value if row.get("status") == "ok" and type(value) is bool else None)
    complete = bool(expected) and all(v is not None for v in values)
    count = sum(v is True for v in values)
    return {
        "value": count / len(expected) if complete else None,
        "planned": len(expected),
        "scored": sum(v is not None for v in values),
        "numerator": count,
        "wilson95": old.wilson(count, len(expected)) if complete else None,
    }


def _old_alias(row):
    queries = row.get("after_revision_queries", [])
    if (
        not queries
        or type(row.get("query_n")) is not int
        or row["query_n"] != len(queries)
        or any(type(q.get("old_answer_reappeared")) is not bool for q in queries)
    ):
        return None
    value = sum(q["old_answer_reappeared"] for q in queries)
    if row.get("old_answer_reappearance_n") != value:
        raise ValueError("old-alias query/count mismatch")
    return value > 0


def _semantic(row):
    keys = ("latest_answer_success", "old_record_retired", "new_record_active")
    if any(type(row.get(k)) is not bool for k in keys):
        return None
    return all(row[k] for k in keys)


def _fire_values(report, expected, occupancy):
    observation = report.get("observation", {})
    if (
        observation.get("active_records_status") != "ok"
        or observation.get("active_records") != occupancy
    ):
        return None
    by = old.ordered_rows(report.get("unseen", {}).get("rows", []), expected, "item_id")
    values = []
    for identity in expected:
        row = by.get(identity, {})
        if (
            row.get("status") != "ok"
            or row.get("firing_status") != "ok"
            or type(row.get("false_fire")) is not bool
        ):
            return None
        values.append(int(row["false_fire"]))
    return values if len(expected) == 100 else None


def cell_benchmarks(declared, loaded, reports, *, resources=None):
    population = declared.get("population") or {}
    endpoints = population.get("endpoints", {})
    outside, revisions = endpoints.get("unseen", []), endpoints.get("revision", [])
    final = reports.get(1000, {})
    # Fixed endpoints may be measured at the last declared checkpoint (e.g. 300
    # in development); an occupancy-1000 benchmark still requires its own point.
    terminal = reports.get(max(declared["checkpoints"]), {})
    rows = terminal.get("endpoints", {}).get("revision", {}).get("rows", [])
    out = {}
    for name, field, transform in (
        ("revision_latest", "latest_answer_success", None),
        ("old_alias_reappearance", None, _old_alias),
        ("revision_semantic", None, _semantic),
    ):
        rate = _case_rate(rows, revisions, field, transform)
        value = rate.pop("value") if len(revisions) == 50 else None
        rate.pop("value", None)
        out[name] = benchmark(
            name,
            value,
            reason=None if value is not None else "complete supported 50-case inventory required",
            **rate,
        )
    high = _fire_values(final, outside, 1000)
    low = _fire_values(reports.get(100, {}), outside, 100)
    value = sum(high) / 100 if high is not None else None
    out["unseen_1000"] = benchmark(
        "unseen_1000",
        value,
        reason=None
        if value is not None
        else "complete outside100 at actual occupancy1000 required",
        wilson95=old.wilson(sum(high), 100) if high is not None else None,
    )
    change = (
        math.fsum(b - a for a, b in zip(low, high)) / 100
        if low is not None and high is not None
        else None
    )
    out["outside_change_1000_100"] = benchmark(
        "outside_change_1000_100",
        change,
        reason=None
        if change is not None
        else "same outside100 and both exact actual occupancies required",
        paired_population_sha256=old.digest(outside) if change is not None else None,
        equivalence="unavailable_single_cell_has_no_realization_cluster_interval",
    )
    cp = loaded.get("checkpoints", {})
    for name, metric in (("retention_change", "RET-GS"), ("es_change", "ES"), ("ls_change", "LS")):
        nodes = [cp.get(str(n), {}).get("primary", {}).get(metric, {}) for n in (100, 1000)]
        valid = all(x.get("status") == "complete" and finite(x.get("value")) for x in nodes)
        value = nodes[1]["value"] - nodes[0]["value"] if valid else None
        out[name] = benchmark(
            name,
            value,
            reason=None if valid else "complete 100 and1000 histories required",
            interpretation="descriptive horizon change; retention histories differ",
        )
    resources = resources or {}
    for name in ("state_budget_ratio", "peak_budget_ratio", "wall_budget_ratio"):
        row = resources.get(name, {})
        measured, ceiling = row.get("measured"), row.get("ceiling")
        valid = (
            row.get("admitted") is True
            and row.get("complete") is True
            and finite(measured)
            and measured >= 0
            and finite(ceiling)
            and ceiling > 0
        )
        out[name] = benchmark(
            name,
            measured / ceiling if valid else None,
            measured=measured,
            ceiling=ceiling,
            reason=None
            if valid
            else "complete measurement and September20 admitted ceiling required",
        )
    occupancy = max(declared["checkpoints"])
    actual = _fire_values(terminal, outside, occupancy)
    actual_change = (
        math.fsum(b - a for a, b in zip(low, actual, strict=True)) / 100
        if low is not None and actual is not None
        else None
    )
    descriptive = {
        "attempted_checkpoint": occupancy,
        "required_actual_occupancy": occupancy,
        "status": "complete" if actual is not None else "unavailable",
        "planned": 100,
        "scored": 100 if actual is not None else 0,
        "fires": sum(actual) if actual is not None else None,
        "value": sum(actual) / 100 if actual is not None else None,
        "wilson95": old.wilson(sum(actual), 100) if actual is not None else None,
        "change_from_actual_100": actual_change,
        "paired_population_sha256": old.digest(outside) if actual_change is not None else None,
        "threshold": None,
        "passes": None,
        "role": "descriptive_actual_occupancy; no transfer of the DEC-059 1000-record tolerance",
    }
    return {
        "actual_occupancy_descriptive": descriptive,
        "cell_id": declared["cell_id"],
        "cell": {k: declared[k] for k in old.COORDS},
        "benchmarks": out,
    }


def macro_benchmarks(matrix, cells):
    indexed = {c["cell_id"]: c for c in cells}
    result = []
    for dataset in matrix["axes"]["datasets"]:
        for condition in dict.fromkeys(c["condition"] for c in old.all_cells(matrix)):
            planned = [
                c
                for c in old.all_cells(matrix)
                if c["dataset"] == dataset and c["condition"] == condition
            ]
            bycoord = {(c["realization"], c["order"]): c for c in planned}
            coords = list(itertools.product((0, 1, 2), (100, 101, 102, 103, 104)))
            # Membership independence includes each declared endpoint role.
            groups = []
            independent = len(planned) == 15 and set(bycoord) == set(coords)
            for r in range(3):
                memberships = []
                for o in (100, 101, 102, 103, 104):
                    p = bycoord.get((r, o), {}).get("population")
                    if not p:
                        independent = False
                        continue
                    memberships.append(
                        set(p["item_ids"]) | {x for v in p["endpoints"].values() for x in v}
                    )
                if len(memberships) != 5 or any(x != memberships[0] for x in memberships):
                    independent = False
                groups.append(memberships[0] if memberships else set())
            if any(a & b for a, b in itertools.combinations(groups, 2)):
                independent = False
            for name in THRESHOLDS:
                observations = [
                    indexed.get(bycoord.get(c, {}).get("cell_id"), {})
                    .get("benchmarks", {})
                    .get(name, {})
                    for c in coords
                ]
                values = [x.get("value") for x in observations]
                complete = independent and all(finite(v) for v in values)
                interval, seeds = None, None
                if complete:
                    seeds = np.asarray(values, np.float64).reshape(3, 5).mean(axis=1)
                    indices = np.random.default_rng(0).integers(0, 3, size=(10000, 3))
                    draws = seeds[indices].mean(axis=1)
                    lo, hi = np.quantile(draws, [0.025, 0.975], method="linear")
                    interval = {"lower": float(lo), "upper": float(hi), "confidence": 0.95}
                row = benchmark(
                    name,
                    float(seeds.mean()) if complete else None,
                    dataset=dataset,
                    condition=condition,
                    metric=name,
                    planned_cells=15,
                    available_cells=sum(finite(v) for v in values),
                    failed_cells=[
                        bycoord[c]["cell_id"]
                        for c, x in zip(coords, observations)
                        if x.get("passes") is False
                    ],
                    realization_estimates=seeds.tolist() if complete else None,
                    interval95=interval,
                    uncertainty="nominal three-realization cluster percentile interval, seed0/10000 draws/float64/linear; five orders retained",
                    reason=None
                    if complete
                    else "complete independent three-realization/five-order populations required",
                )
                if name == "outside_change_1000_100":
                    row["equivalence"] = (
                        bool(interval["lower"] >= -0.05 and interval["upper"] <= 0.05)
                        if interval
                        else None
                    )
                result.append(row)
    return result
