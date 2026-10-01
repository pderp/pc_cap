"""CAL-1: numerical checks of the one-sided alpha=d=1 calibrated GPD.

Synthetic distributions only; no fitted project data, JAX/model or training call.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent / 'NelsonUniqueUnivEntropy2026Sep27.pdf'


def logpdf(x, kappa, sigma):
    if kappa < 0 or sigma <= 0 or x < 0:
        raise ValueError('demo domain: x,kappa >= 0, sigma > 0')
    return -math.log(sigma) - (x / sigma if kappa == 0 else (1 + 1 / kappa) * math.log1p(kappa * x / sigma))


def coupled_log(x, r):
    return math.log(x) if r == 0 else math.expm1(r * math.log(x)) / r


def measure(kappa, sigma):
    r = kappa / (1 + kappa)
    q = 1 + r
    def density(x):
        return math.exp(logpdf(x, kappa, sigma))

    def powered(x):
        return math.exp(q * logpdf(x, kappa, sigma))

    norm, err_n = quad(density, 0, math.inf, epsabs=2e-10)
    z, err_z = quad(powered, 0, math.inf, epsabs=2e-10)
    moment, err_m = quad(lambda x: x * powered(x) / z, 0, math.inf, epsabs=2e-10)

    def integrand(x):
        lf = logpdf(x, kappa, sigma)
        # Algebraic cancellation prevents inf*0 at extreme quadrature points.
        if kappa == 0:
            return -lf * math.exp(lf)
        return (math.exp((q - r) * lf) - math.exp(q * lf)) / (kappa * z)

    entropy, err_h = quad(integrand, 0, math.inf, epsabs=2e-10)
    expected_h = 1 + coupled_log(sigma, r)
    eps = 1e-5
    slope = (logpdf(sigma * math.exp(eps), kappa, sigma) - logpdf(sigma * math.exp(-eps), kappa, sigma)) / (2 * eps)
    ordinary = sigma / (1 - kappa) if kappa < 1 else None
    truncated = [quad(lambda x: x * density(x), 0, limit * sigma)[0] for limit in (10, 100, 1000)]
    errors = {'normalization': abs(norm - 1), 'escort_normalization': abs(z - sigma ** (-r) / (1 + kappa)),
              'log_slope': abs(slope + 1), 'escort_mean': abs(moment - sigma), 'entropy': abs(entropy - expected_h)}
    return dict(kappa=kappa, sigma=sigma, escort_power=q, density_integral=norm,
                escort_normalizer=z, slope_at_sigma=slope, escort_mean=moment,
                ordinary_mean=ordinary, ordinary_mean_status='finite' if ordinary is not None else 'divergent',
                unnormalized_truncated_first_moments=truncated, truncation_in_sigma=[10, 100, 1000],
                entropy_numerical=entropy, entropy_analytic=expected_h, absolute_errors=errors,
                quadrature_error_estimates=[err_n, err_z, err_m, err_h], passed=max(errors.values()) < 1e-7)


def main(output):
    rows = [measure(k, s) for k in (0, .25, 1, 2) for s in (.5, 1, 2)]
    limit = max(abs(logpdf(x, 1e-8, s) - logpdf(x, 0, s)) for s in (.5, 1, 2) for x in (0, .1, 1, 3))
    def sha(p):
        with Path(p).open('rb') as f:
            return hashlib.file_digest(f, 'sha256').hexdigest()
    result = dict(task='CAL-1', passed=all(x['passed'] for x in rows) and limit < 1e-6,
                  rows=rows, kappa_to_zero_max_logdensity_error=limit,
                  scope='Known distributions; no empirical tail-class, entropy-growth, or objective-effectiveness claim.',
                  sources_sha256={str(PAPER): sha(PAPER), str(Path(__file__).resolve()): sha(__file__)}, gpu_seconds=0)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'checks.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    lines=['# CAL-1 — known-distribution calibration', '',
           'Numerical quadrature on [0, infinity); alpha=d=1, location=0. Ordinary means at kappa >= 1 diverge; they are not large finite estimates.', '',
           '| κ | σ | ∫f | slope at σ | escort mean | ordinary mean | calibrated entropy |',
           '| --- | --- | --- | --- | --- | --- | --- |']
    for row in rows:
        lines.append('| ' + ' | '.join(f'{row[k]:.8g}' if isinstance(row[k], (int,float)) else 'divergent' for k in ('kappa','sigma','density_integral','slope_at_sigma','escort_mean','ordinary_mean','entropy_numerical')) + ' |')
    lines += ['', f'All checks pass: {result["passed"]}. Maximum small-κ log-density error: {limit:.3g}.',
              '', 'The integrand is ln_κ(f^(-r)), averaged using f^(1+r)/∫f^(1+r), with r=κ/(1+κ). Its α=1 outer root is the identity. The analytic result is 1+ln_r(σ); the κ=0 limit is ordinary differential entropy.',
              '', 'Input identities and integration errors: checks.json. These checks validate this restricted numerical implementation, not the full manuscript or a coupled free-energy objective.']
    (output / 'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(passed=result['passed'], cases=len(rows), max_error=max(max(r['absolute_errors'].values()) for r in rows))))
    if not result['passed']:
        raise ValueError('calibration checks failed')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
