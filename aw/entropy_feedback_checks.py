"""Small algebra checks for the 2026-10-01 Nelson manuscript review.

Source: supplied NelsonUniqueUnivEntropy2026Sep27.pdf, equations 24 and 126.
This is a reading aid, not an entropy trainer or an empirical tail estimator.
Only Python's standard library is used; no model, JAX device, or data is loaded.
Run from the repository root and redirect stdout to the review's JSON log.
"""

from __future__ import annotations

import json
import math


def uniform_entropy(w: float, kappa: float, alpha: float, dimension: float) -> float:
    """Uniform discrete entropy, unit conversion factor, supplied Eq. 24/43."""
    if kappa == 0:
        return (alpha * math.log(w)) ** (1 / alpha)
    exponent = alpha * kappa / (alpha + dimension * kappa)
    return (alpha * math.expm1(exponent * math.log(w)) / kappa) ** (1 / alpha)


def scaling_ratio(w: float, kappa: float, alpha: float, dimension: float) -> float:
    """Eq. 126's left side at a=1, before taking the limit."""
    c_tilde = kappa / (alpha + dimension * kappa)
    return (
        uniform_entropy(w * w, kappa, alpha, dimension)
        / uniform_entropy(w, kappa, alpha, dimension)
        * w ** (-c_tilde)
    )


def main() -> None:
    scaling = []
    for w in (1e2, 1e4, 1e8, 1e12):
        ratio = scaling_ratio(w, 1, 1, 1)
        exact = 1 + 1 / math.sqrt(w)
        assert math.isclose(ratio, exact, rel_tol=1e-12)
        scaling.append({"W": w, "equation_126_left_side": ratio, "exact": exact})

    zero_branch = scaling_ratio(1e8, 0, 2, 1)
    assert math.isclose(zero_branch, math.sqrt(2), rel_tol=1e-12)

    # Verify the entropy/state-growth inverse as an identity, not measured growth.
    inverse_checks = []
    for kappa, alpha, dimension in ((0.25, 1, 1), (1, 1, 1), (0.5, 2, 1)):
        n = 10.0
        w = (1 + kappa * n**alpha / alpha) ** (
            (alpha + dimension * kappa) / (alpha * kappa)
        )
        recovered = uniform_entropy(w, kappa, alpha, dimension)
        assert math.isclose(recovered, n, rel_tol=1e-12)
        inverse_checks.append(
            {"kappa": kappa, "alpha": alpha, "d": dimension, "N": n, "H": recovered}
        )

    # Compare pointwise factors only. The second is NOT the full proposed loss:
    # Eq. 24 also has a normalized escort expectation and an outer 1/alpha power.
    factors = []
    kappa = 0.5
    r = kappa / (1 + kappa)  # alpha=d=1
    for surprisal in (1, 5, 10):
        factors.append(
            {
                "surprisal_nats": surprisal,
                "existing_pilot_answer_loss": -math.expm1(-kappa * surprisal) / kappa,
                "manuscript_pointwise_factor_only": math.expm1(r * surprisal) / kappa,
            }
        )

    print(
        json.dumps(
            {
                "scope": "Algebra reading checks only; no experimental results",
                "equation_126": {
                    "parameters": {"alpha": 1, "d": 1, "kappa": 1, "a": 1},
                    "finite_W": scaling,
                    "derived_limit": 1,
                    "printed_limit": 2,
                    "status": "discrepancy under the printed definitions; ask author",
                },
                "kappa_zero_control_alpha_2": zero_branch,
                "constructed_W_inverse_checks": inverse_checks,
                "pointwise_comparison_kappa_0_5_alpha_1_d_1": factors,
                "entropy_domain_alpha_1_d_1": "kappa > -0.5, as stated in manuscript",
                "checks_passed": True,
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
