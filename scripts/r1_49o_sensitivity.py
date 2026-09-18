"""DEC-069 descriptive order dispersion and assumption-labelled t sensitivity."""

import math

import numpy as np

CONTRACT = dict(
    decision="DEC-069",
    role="preliminary_decision_summaries",
    registered_computation="unchanged_DEC057_DEC058",
    population_effect_established=False,
    demonstrated_familywise_control=False,
    sensitivity=dict(
        method="Student_t",
        confidence=0.95,
        degrees_of_freedom=2,
        critical_value=4.302652729696142,
        family_adjusted=False,
        role="secondary_sensitivity_not_classifier_input",
        assumptions="independent identically distributed normal realization errors; not checked with n=3",
    ),
    order_dispersion="five paired differences per realization; min/max/sample_sd; orders are not independent realizations",
)


def display(grid, *, population_valid=True):
    if len(grid) != 3 or any(len(row) != 5 for row in grid):
        raise ValueError("three realizations with five paired orders required")
    rows = []
    for index, row in enumerate(grid):
        valid = [
            isinstance(v, (float, int, np.floating, np.integer))
            and not isinstance(v, (bool, np.bool_))
            and math.isfinite(v)
            for v in row
        ]
        complete = all(valid)
        rows.append(
            dict(
                realization=index,
                order_values=[float(v) if ok else None for v, ok in zip(row, valid)],
                complete=complete,
                observed_orders=sum(valid),
                mean=float(np.mean(row)) if complete else None,
                minimum=float(min(row)) if complete else None,
                maximum=float(max(row)) if complete else None,
                sample_sd=float(np.std(row, ddof=1)) if complete else None,
            )
        )
    sensitivity = dict(
        CONTRACT["sensitivity"],
        status="unavailable",
        lower=None,
        upper=None,
        between_realization_sample_sd=None,
        zero_variance_caveat=None,
    )
    if population_valid and all(r["complete"] for r in rows):
        means = np.array([r["mean"] for r in rows], dtype=np.float64)
        sd = float(np.std(means, ddof=1))
        half = CONTRACT["sensitivity"]["critical_value"] * sd / math.sqrt(3)
        estimate = float(means.mean())
        sensitivity.update(
            status="complete",
            lower=estimate - half,
            upper=estimate + half,
            between_realization_sample_sd=sd,
            zero_variance_caveat="zero observed variance does not establish certainty"
            if sd == 0
            else None,
        )
    return dict(
        interpretation="preliminary_decision_summary",
        order_dispersion=rows,
        t_sensitivity=sensitivity,
        population_valid=population_valid,
    )
