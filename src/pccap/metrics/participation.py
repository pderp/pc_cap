"""Participation and active fraction of squared vector masses (PDF D.3).

Pass m[layer, token] = sum_feature(error**2), not individual feature cells.
"""

import numpy as np

from pccap.contracts import Metric, metric


def _mass(masses):
    x = np.asarray(masses, dtype=np.float64)
    if x.size == 0 or not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError("mass must be nonempty, finite and nonnegative")
    return x


def pr(masses, *, normalized: bool = False) -> Metric:
    x = _mass(masses)
    maximum = float(x.max())
    if maximum == 0:
        return metric(
            None,
            units="fraction" if normalized else "cells",
            n=x.size,
            numerator=0,
            denominator=0,
            status="undefined",
            strata={"reason": "zero_mass", "normalized": normalized},
        )
    scaled = x / maximum
    numerator = float(scaled.sum() ** 2)
    denominator = float(np.sum(scaled**2)) * (x.size if normalized else 1)
    return metric(
        numerator / denominator,
        units="fraction" if normalized else "cells",
        numerator=numerator,
        denominator=denominator,
        n=x.size,
        strata={
            "mass_scale": maximum,
            "normalized": normalized,
            "operand_meaning": "scale-cancelled squared mass sums",
        },
    )


def active_fraction(masses, *, threshold: float = 0.01) -> Metric:
    x = _mass(masses)
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold must lie in [0, 1]")
    maximum = float(x.max())
    count = int(np.count_nonzero(x > threshold * maximum))
    return metric(
        count / x.size if maximum else None,
        units="fraction",
        numerator=count,
        denominator=x.size,
        n=x.size,
        status="ok" if maximum else "undefined",
        strata={"threshold": threshold, "maximum_mass": maximum, "zero_field": maximum == 0},
    )
