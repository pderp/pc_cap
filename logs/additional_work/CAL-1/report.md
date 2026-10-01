# CAL-1 — known-distribution calibration

Numerical quadrature on [0, infinity); alpha=d=1, location=0. Ordinary means at kappa >= 1 diverge; they are not large finite estimates.

| κ | σ | ∫f | slope at σ | escort mean | ordinary mean | calibrated entropy |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.5 | 1 | -1 | 0.5 | 0.5 | 0.30685282 |
| 0 | 1 | 1 | -1 | 1 | 1 | 1 |
| 0 | 2 | 1 | -1 | 2 | 2 | 1.6931472 |
| 0.25 | 0.5 | 1 | -1 | 0.5 | 0.66666667 | 0.35275282 |
| 0.25 | 1 | 1 | -1 | 1 | 1.3333333 | 1 |
| 0.25 | 2 | 1 | -1 | 2 | 2.6666667 | 1.7434918 |
| 1 | 0.5 | 1 | -1 | 0.5 | divergent | 0.41421356 |
| 1 | 1 | 1 | -1 | 1 | divergent | 1 |
| 1 | 2 | 1 | -1 | 2 | divergent | 1.8284271 |
| 2 | 0.5 | 1 | -1 | 0.5 | divergent | 0.44494079 |
| 2 | 1 | 1 | -1 | 1 | divergent | 1 |
| 2 | 2 | 1 | -1 | 2 | divergent | 1.8811016 |

All checks pass: True. Maximum small-κ log-density error: 1.2e-07.

The integrand is ln_κ(f^(-r)), averaged using f^(1+r)/∫f^(1+r), with r=κ/(1+κ). Its α=1 outer root is the identity. The analytic result is 1+ln_r(σ); the κ=0 limit is ordinary differential entropy.

Input identities and integration errors: checks.json. These checks validate this restricted numerical implementation, not the full manuscript or a coupled free-energy objective.
