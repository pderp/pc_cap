"""DEC-057/058: fixed 63-interval family and priority-ordered classifier.

Three realization clusters, all five orders retained per cluster; nominal
bootstrap multiplicity adjustment, not an exact finite-sample coverage claim.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
from scripts import r1_75_analysis_stage4_v1 as old

DATASETS = ("zsre", "counterfact", "mquake")
CONTROLS = (
    "R1_nonlearned",
    "v0_stable",
    "matched_update",
    "v0_live_C1",
    "v0_live_C2",
    "S1_LM",
    "S1_literal",
)
METRICS = ("RET-GS", "ES", "LS")
ADJUSTED_CONFIDENCE = 1 - 0.05 / 63
FAMILY = {
    "decision": "DEC-057",
    "status": "admitted",
    "method": "Bonferroni_percentile_realization_clusters",
    "family_size": 63,
    "family_alpha": 0.05,
    "adjusted_confidence": ADJUSTED_CONFIDENCE,
    "pointwise_confidence": 0.975,
    "checkpoint": 1000,
    "seed": 0,
    "draws": 10000,
    "dtype": "float64",
    "quantile_method": "linear",
    "clusters": 3,
    "orders_per_cluster": 5,
    "coverage": "nominal approximate bootstrap; three clusters do not establish exact familywise coverage",
}


def finite(value):
    return (
        isinstance(value, (float, int, np.floating, np.integer))
        and not isinstance(value, (bool, np.bool_))
        and math.isfinite(value)
    )


def cluster_intervals(grid, *, adjusted=True):
    if len(grid) != 3 or any(len(row) != 5 for row in grid):
        raise ValueError("exactly three realization clusters with five paired orders required")
    means = [
        float(np.mean(row, dtype=np.float64)) if all(finite(v) for v in row) else None
        for row in grid
    ]
    out = {
        "status": "incomplete",
        "estimate": None,
        "realization_estimates": means,
        "interval": None,
        "unadjusted_interval": None,
        "adjusted_interval": None,
        "cluster_n": 3,
        "order_n": 5,
        "seed": 0,
        "draws": 10000,
    }
    if any(v is None for v in means):
        return out
    values = np.asarray(means, np.float64)
    indices = np.random.default_rng(0).integers(0, 3, size=(10000, 3))
    draws = values[indices].mean(axis=1, dtype=np.float64)

    def interval(confidence):
        lo, hi = np.quantile(draws, [(1 - confidence) / 2, (1 + confidence) / 2], method="linear")
        return {"lower": float(lo), "upper": float(hi), "confidence": confidence}

    out.update(
        status="complete",
        estimate=float(values.mean(dtype=np.float64)),
        unadjusted_interval=interval(0.975),
    )
    if adjusted:
        out["adjusted_interval"] = interval(ADJUSTED_CONFIDENCE)
    out["interval"] = out["adjusted_interval"] if adjusted else out["unadjusted_interval"]
    return out


def classify(metrics, *, admitted, complete=True):
    if not complete or admitted is not True:
        return "unavailable"
    for metric in METRICS:
        m = metrics.get(metric, {})
        bound = m.get("adjusted_interval")
        if (
            m.get("status") != "complete"
            or not finite(m.get("estimate"))
            or not isinstance(bound, dict)
            or any(not finite(bound.get(k)) for k in ("lower", "upper"))
            or bound["lower"] > bound["upper"]
            or bound.get("confidence") != ADJUSTED_CONFIDENCE
        ):
            return "unavailable"
    gs, es, ls = (metrics[k] for k in METRICS)
    g, e, l = (m["estimate"] for m in (gs, es, ls))
    gb, eb, lb = (m["adjusted_interval"] for m in (gs, es, ls))
    if gb["upper"] < 0.05 or eb["upper"] < -0.02 or lb["upper"] < -0.01:
        return "negative"
    if g >= 0.05 and gb["lower"] > 0 and eb["lower"] > -0.02 and lb["lower"] > -0.01:
        return "positive"
    if (
        g >= 0.05
        and gb["lower"] > 0
        and e >= -0.02
        and l >= -0.01
        and (eb["lower"] <= -0.02 or lb["lower"] <= -0.01)
    ):
        return "qualified"
    return "inconclusive"


def fidelity(mean_kl, mean_signed_loss, *, complete):
    available = complete is True and finite(mean_kl) and finite(mean_signed_loss)
    return {
        "status": "complete" if available else "unavailable",
        "passes": bool(mean_kl <= 0.001 and mean_signed_loss <= 0.01) if available else None,
        "reference": "complete fixed validation inventory; mean signed loss, not positive-part harm",
    }


def validate_family(matrix):
    axes = matrix["axes"]
    reduced = matrix.get("option") == "D" or "dataset_layouts" in matrix
    if reduced:
        from scripts.r1_d9_layouts import from_matrix

        layout = from_matrix(matrix)
        if axes.get("realizations_by_dataset") != {d: x["realizations"] for d, x in layout.items()}:
            raise ValueError("option-D realization inventory differs")
        if any(
            c["checkpoints"] != layout[c["dataset"]]["checkpoints"] for c in old.all_cells(matrix)
        ):
            raise ValueError("option-D execution cadence differs")
    if (
        axes["datasets"] != list(DATASETS)
        or (not reduced and axes["realizations"] != [0, 1, 2])
        or axes["orders"] != [100, 101, 102, 103, 104]
        or set(axes["conditions"]) != {"R1_learned_ff", *CONTROLS}
        or len(axes["conditions"]) != 8
    ):
        raise ValueError("DEC-057 axes required; family cannot shrink to observed cells")
    primary = [c for c in matrix["contrasts"] if c["role"] == "primary"]
    if (
        len(primary) != 7
        or {c["control"] for c in primary} != set(CONTROLS)
        or any(c["treatment"] != "R1_learned_ff" for c in primary)
        or len({c["id"] for c in primary}) != 7
    ):
        raise ValueError("exact seven registered primary contrasts required")
    if matrix.get("multiplicity") != FAMILY:
        raise ValueError("exact DEC-057 family binding required")
    old.validate_matrix(matrix)
    coordinates = {old.coordinate(c) for c in matrix["cells"]}
    expected = set(itertools.product(axes["conditions"], DATASETS, [0, 1, 2], axes["orders"]))
    if coordinates != expected or len(matrix["cells"]) != 360:
        raise ValueError("complete independently declared 360-cell primary inventory required")
    return primary


def _population_ok(population):
    if not population or len(population.get("item_ids", [])) != 1000:
        return False
    return len(population.get("endpoints", {}).get("locality", [])) > 0


def primary_contrasts(matrix, loaded):
    contrasts = validate_family(matrix)
    indexed = {old.coordinate(c): c for c in matrix["cells"]}
    output = []
    for dataset in DATASETS:
        for contrast in contrasts:
            if dataset == "mquake" and matrix.get("option") == "D":
                output.append(
                    {
                        "dataset": dataset,
                        "checkpoint": 1000,
                        "contrast": contrast,
                        "metrics": {
                            m: cluster_intervals([[None] * 5 for _ in range(3)]) for m in METRICS
                        },
                        "classification": "unavailable",
                        "scientific_admission": False,
                        "pairing_issues": [
                            {
                                "reason": "DEC-060 option D has no MQuAKE 1000-edit population; 300 cannot substitute"
                            }
                        ],
                        "multiplicity": FAMILY,
                        "interval_count": 3,
                    }
                )
                continue
            grids = {metric: [] for metric in METRICS}
            issues, populations = [], []
            admitted = matrix.get("scope") == "confirmatory"
            for realization in (0, 1, 2):
                values = {metric: [] for metric in METRICS}
                order_pops = []
                for order in matrix["axes"]["orders"]:
                    declared = [
                        indexed[(contrast[k], dataset, realization, order)]
                        for k in ("treatment", "control")
                    ]
                    observed = [loaded.get(c["cell_id"], {}) for c in declared]
                    pop = [c.get("population") for c in declared]
                    common = all(_population_ok(p) for p in pop) and pop[0] == pop[1]
                    if not common:
                        issues.append(
                            {
                                "realization": realization,
                                "order": order,
                                "reason": "missing or unequal complete planned populations",
                            }
                        )
                    else:
                        order_pops.append(
                            (set(pop[0]["item_ids"]), set(pop[0]["endpoints"]["locality"]))
                        )
                    admitted = (
                        admitted
                        and all(c.get("admitted") is True for c in declared)
                        and all(c.get("scientific_admission") is True for c in observed)
                    )
                    for metric in METRICS:
                        nodes = [
                            c.get("checkpoints", {})
                            .get("1000", {})
                            .get("primary", {})
                            .get(metric, {})
                            for c in observed
                        ]
                        expected_n = (
                            (len(pop[0]["endpoints"]["locality"]) if metric == "LS" else 1000)
                            if common
                            else None
                        )
                        valid = common and all(
                            node.get("status") == "complete"
                            and node.get("planned") == expected_n
                            and node.get("scored") == expected_n
                            and finite(node.get("value"))
                            and 0 <= node["value"] <= 1
                            for node in nodes
                        )
                        values[metric].append(
                            nodes[0]["value"] - nodes[1]["value"] if valid else None
                        )
                for metric in METRICS:
                    grids[metric].append(values[metric])
                if len(order_pops) != 5 or any(p != order_pops[0] for p in order_pops):
                    issues.append(
                        {
                            "realization": realization,
                            "reason": "incomplete or different memberships across five orders",
                        }
                    )
                populations.append(order_pops[0] if order_pops else None)
            if all(p is not None for p in populations):
                for a, b in itertools.combinations(populations, 2):
                    if (a[0] | a[1]) & (b[0] | b[1]):
                        issues.append({"reason": "overlapping realization populations"})
            stats = {m: cluster_intervals(grids[m]) for m in METRICS}
            if issues:
                for result in stats.values():
                    result.update(
                        status="population_unavailable",
                        interval=None,
                        adjusted_interval=None,
                        unadjusted_interval=None,
                    )
            output.append(
                {
                    "dataset": dataset,
                    "checkpoint": 1000,
                    "contrast": contrast,
                    "metrics": stats,
                    "classification": classify(stats, admitted=admitted, complete=not issues),
                    "scientific_admission": admitted,
                    "pairing_issues": issues,
                    "multiplicity": FAMILY,
                    "interval_count": 3,
                }
            )
    return output
