"""HT-17: conditional excess models and joint-window uncertainty, CPU only.

No model loading or fitting of an entropy objective. GPD ``shape`` is SciPy's
``genpareto.c``; the exponential is its zero-shape restriction. Invalid shapes
remain diagnostic optimizer output, never headline estimates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy import optimize, stats

from aw.tail_figures import expected_shortfall

THRESHOLDS = (0.01, 0.1, 0.5, 1.0)
MIN_EXCESSES = 100
MIN_WINDOWS = 30
SEED = 20261001
NOISE_BAND = 1e-9


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def window_plan(windows, draws=200, seed=SEED):
    """Identical identity weights for every cell on this ordered population."""
    rng = np.random.default_rng(seed)
    weights = rng.multinomial(windows, np.full(windows, 1 / windows), size=draws)
    folds = np.empty(windows, dtype=int)
    folds[np.random.default_rng(seed + 1).permutation(windows)] = np.arange(windows) % 5
    return weights, folds


def interval(values):
    values = np.asarray(values, float)
    values = values[np.isfinite(values)]
    return [float(v) for v in np.quantile(values, [0.025, 0.975])] if len(values) else None


def gpd_nll(parameters, y, weights):
    shape, logscale = parameters
    if not np.isfinite(parameters).all() or abs(logscale) > 40:
        return 1e100
    scale = np.exp(logscale)
    z = y / scale
    if np.any(1 + shape * z <= 0):
        return 1e100
    term = z if shape == 0 else np.log1p(shape * z) * (1 + 1 / shape)
    return float(np.dot(weights, logscale + term))


def fit_gpd(y, weights=None, *, warm=None):
    y = np.asarray(y, float)
    w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
    y, w = y[w > 0], w[w > 0]
    if len(y) < 3 or not np.isfinite(y).all() or np.any(y <= 0):
        return dict(status="not_identified", reason="fewer than three finite positive excesses")
    unit = float(np.average(y, weights=w))
    z = y / unit
    starts = [warm] if warm else [(0.1, 1.0), (-0.25, max(1.0, 0.3 * float(z.max())))]
    candidates = []
    for shape, scale in starts:
        if warm:
            scale /= unit
        result = optimize.minimize(
            gpd_nll, [shape, np.log(scale)], args=(z, w), method="Nelder-Mead",
            options=dict(maxiter=700, xatol=1e-7, fatol=1e-7),
        )
        candidates.append(result)
    best = min(candidates, key=lambda r: r.fun)
    k, scale = float(best.x[0]), float(np.exp(best.x[1]) * unit)
    reason = (
        "endpoint_likelihood_boundary" if k <= -1 else
        "outside_manuscript_entropy_domain" if k <= -0.5 else
        "optimizer_nonconvergence" if not best.success else
        "invalid_support" if np.any(1 + k * y / scale <= 0) else None
    )
    return dict(
        status="invalid" if reason else "eligible", reason=reason,
        shape=k if reason is None else None, scale=scale if reason is None else None,
        optimizer=dict(shape=k, scale=scale, success=bool(best.success),
                       iterations=int(best.nit), starts=len(starts)),
        nll=float(best.fun + w.sum() * np.log(unit)),
        finite_endpoint=(-scale / k) if k < 0 else None,
    )


def fit_lognormal(x, u):
    """Density of original positive loss, conditioned on X>u (not LN excesses)."""
    lx = np.log(x)

    def nll(p):
        mu, logsigma = p
        if abs(logsigma) > 20:
            return 1e100
        sigma = np.exp(logsigma)
        ll = stats.norm.logpdf((lx - mu) / sigma) - logsigma - lx
        ll -= stats.norm.logsf((np.log(u) - mu) / sigma)
        return float(-ll.sum()) if np.isfinite(ll).all() else 1e100

    result = optimize.minimize(
        nll, [float(lx.mean()), np.log(max(float(lx.std()), 0.1))],
        method="Nelder-Mead", options=dict(maxiter=1000, xatol=1e-7, fatol=1e-7),
    )
    return dict(status="eligible" if result.success else "invalid",
                mu=float(result.x[0]), sigma=float(np.exp(result.x[1])),
                optimizer_success=bool(result.success), nll=float(result.fun))


def lognormal_logpdf(x, u, model):
    mu, sigma = model["mu"], model["sigma"]
    return (stats.norm.logpdf((np.log(x) - mu) / sigma) - np.log(sigma) - np.log(x)
            - stats.norm.logsf((np.log(u) - mu) / sigma))


def uniform_discrepancy(pit):
    """Descriptive PIT/CDF discrepancy; no iid Kolmogorov-Smirnov p-value."""
    p = np.sort(pit)
    n = len(p)
    return float(max(np.max(np.arange(1, n + 1) / n - p),
                     np.max(p - np.arange(n) / n))) if n else None


def cross_validate(y, ids, folds, u, *, lognormal=False):
    models = ("gpd", "exponential", "conditional_lognormal") if lognormal else (
        "gpd", "exponential")
    totals = {m: dict(log_likelihood=0.0, scored=0, unsupported=0, failed_folds=0,
                      pit=[]) for m in models}
    fold_rows = []
    for fold in range(5):
        test = folds[ids] == fold
        train = ~test
        row = dict(fold=fold, train=int(train.sum()), test=int(test.sum()), models={})
        if not test.any():
            fold_rows.append(row)
            continue
        if train.sum() < 20 or len(np.unique(ids[train])) < 10:
            for m in models:
                totals[m]["failed_folds"] += 1
            row["status"] = "insufficient_training_excesses_or_windows"
            fold_rows.append(row)
            continue
        fits = dict(gpd=fit_gpd(y[train]),
                    exponential=dict(status="eligible", scale=float(y[train].mean())))
        if lognormal:
            fits["conditional_lognormal"] = fit_lognormal(y[train] + u, u)
        for m, fitted in fits.items():
            row["models"][m] = fitted
            out = totals[m]
            if fitted["status"] != "eligible":
                out["failed_folds"] += 1
                continue
            if m == "conditional_lognormal":
                ll = lognormal_logpdf(y[test] + u, u, fitted)
                a = stats.norm.logsf((np.log(y[test] + u) - fitted["mu"]) / fitted["sigma"])
                b = stats.norm.logsf((np.log(u) - fitted["mu"]) / fitted["sigma"])
                pit = -np.expm1(a - b)
            else:
                k = fitted.get("shape", 0.0)
                ll = stats.genpareto.logpdf(y[test], k, loc=0, scale=fitted["scale"])
                pit = stats.genpareto.cdf(y[test], k, loc=0, scale=fitted["scale"])
            out["unsupported"] += int((~np.isfinite(ll)).sum())
            out["log_likelihood"] += float(ll[np.isfinite(ll)].sum())
            out["scored"] += int(test.sum())
            out["pit"].extend(pit.tolist())
        fold_rows.append(row)
    for out in totals.values():
        out["pit_discrepancy"] = uniform_discrepancy(out.pop("pit"))
        out["status"] = (
            "invalid_fold" if out["failed_folds"] else
            "zero_predictive_density" if out["unsupported"] else "complete"
        )
        if out["status"] != "complete":
            out["log_likelihood"] = None  # never silently drop impossible predictions
        out["mean_log_likelihood"] = (
            out["log_likelihood"] / len(y) if out["log_likelihood"] is not None else None)
    a, b = (totals[m]["mean_log_likelihood"] for m in ("gpd", "exponential"))
    return dict(models=totals, folds=fold_rows,
                gpd_minus_exponential_per_excess=None if a is None or b is None else a - b)


def bootstrap_shape(y, ids, weights, fit):
    estimates, invalid = [], 0
    for multiplicity in weights:
        w = multiplicity[ids]
        result = fit_gpd(y, w, warm=(fit["shape"], fit["scale"]))
        if result["status"] == "eligible":
            estimates.append([result["shape"], result["scale"]])
        else:
            invalid += 1
    enough = invalid == 0  # do not condition a CI on dropping invalid draws
    return dict(draws=len(weights), invalid_draws=invalid,
                status="complete" if enough else "not_identified_bootstrap_invalid",
                shape_interval=interval(np.asarray(estimates)[:, 0]) if enough else None,
                scale_interval=interval(np.asarray(estimates)[:, 1]) if enough else None)


def analyze(delta, *, weights, folds, bootstrap_fits=True):
    d = np.asarray(delta, float)
    if d.ndim != 2 or not d.size or not np.isfinite(d).all():
        raise ValueError("finite nonempty window-by-position deltas required")
    if weights.shape[1] != d.shape[0] or len(folds) != d.shape[0]:
        raise ValueError("window plan differs from position inventory")
    flat = d.ravel()
    result = dict(
        positions=d.size, windows=len(d), mean_signed=float(d.mean()),
        es99_positive=expected_shortfall(np.maximum(flat, 0)), maximum=float(d.max()),
        exact_zero=int((d == 0).sum()), positive_raw=int((d > 0).sum()),
        negative_raw=int((d < 0).sum()),
        nonzero_in_noise_band=int(((d != 0) & (np.abs(d) <= NOISE_BAND)).sum()),
        benefit_beyond_noise_band=int((d < -NOISE_BAND).sum()),
        positive_beyond_noise_band=int((d > NOISE_BAND).sum()), thresholds={},
    )
    window_stats = {}
    for u in THRESHOLDS:
        mask = d > u
        ids = np.nonzero(mask)[0]
        y = d[mask] - u
        counts = mask.sum(axis=1)
        sums = np.where(mask, d, 0).sum(axis=1)
        n, nw = len(y), int((counts > 0).sum())
        bc, bs = weights @ counts, weights @ sums
        severity = np.divide(bs, bc, out=np.full(len(bs), np.nan), where=bc > 0)
        row = dict(count=n, contributing_windows=nw, fraction=n / d.size,
                   conditional_mean_loss=float(y.mean() + u) if n else None,
                   frequency_interval=interval(bc / d.size),
                   conditional_mean_interval=interval(severity) if np.all(bc > 0) else None,
                   empty_bootstrap_draws=int((bc == 0).sum()))
        if n < MIN_EXCESSES or nw < MIN_WINDOWS:
            row["fit"] = dict(status="not_identified", reason="excess_or_window_screen")
        else:
            fit = fit_gpd(y)
            row.update(fit=fit, exponential=dict(scale=float(y.mean())))
            cv = cross_validate(y, ids, folds, u)
            # A descriptive lack-of-fit trigger, not an iid test or model selection rule.
            poor = all(v["status"] != "complete" or v["pit_discrepancy"] > 0.10
                       for v in cv["models"].values())
            if poor:
                cv = cross_validate(y, ids, folds, u, lognormal=True)
                row["conditional_lognormal"] = fit_lognormal(y + u, u)
            row["cross_validation"] = cv
            row["alternative_triggered"] = poor
            if bootstrap_fits and u == THRESHOLDS[0] and fit["status"] == "eligible":
                row["shape_bootstrap"] = bootstrap_shape(y, ids, weights, fit)
        grid = np.geomspace(u, max(u * 1.01, float(d.max())), 100)
        row["survival"] = dict(grid=grid.tolist(), empirical=[
            float(np.count_nonzero(flat > x) / len(flat)) for x in grid])
        result["thresholds"][str(u)] = row
        window_stats[str(u)] = dict(counts=counts, sums=sums)
    return result, window_stats


def main():
    from aw.tail_class_report import build

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--limit", type=int, help="deterministic profiling prefix, not a final analysis")
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--secondary", action="store_true")
    ap.add_argument("--no-shape-bootstrap", action="store_true")
    args = ap.parse_args()
    if args.bootstrap < 20:
        ap.error("at least 20 window draws required (200 for the report)")
    start = time.monotonic()
    report = build(args)
    print(json.dumps(dict(cells=len(report["cells"]), wall_seconds=time.monotonic() - start,
                          output=str(args.output), code_sha256=hashlib.sha256(
                              Path(__file__).read_bytes()).hexdigest())), flush=True)


if __name__ == "__main__":
    main()
