"""CPU statistics for ext-20261009: entropy, divergences, CVaR, GPD tail fits, grouped bootstrap, MQuAKE aggregation.

Every function is pure numpy/scipy and unit-tested in aw/tests/test_extremes_stats.py. Conventions:
natural logarithms (nats); CVaR95 = mean of the largest ceil(0.05 n) values; GPD shape ``kappa`` with
``P(Z > z) = (1 + kappa z / sigma)^(-1/kappa)`` (scipy ``genpareto`` ``c``); ES99+ (project) = mean of the worst 1 % of the
positive part including zero mass, fractional boundary weight.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats as sps


# ----------------------------------------------------------------------------------------------------- entropies
def shannon(p) -> float:
    p = np.asarray(p, float).ravel()
    if p.size == 0 or np.any(p < 0) or not np.isfinite(p).all():
        raise ValueError("nonnegative finite probabilities required")
    s = p.sum()
    if not np.isclose(s, 1.0, atol=1e-9):
        raise ValueError("probabilities must sum to one")
    q = p[p > 0]
    return float(-(q * np.log(q)).sum())


def entropy_of_counts(counts) -> dict:
    c = np.asarray(counts, float).ravel()
    c = c[c > 0]
    K = int(c.size)
    if K == 0:
        return dict(H=None, K=0, H_normalized=None, N_effective=None)
    p = c / c.sum()
    H = shannon(p)
    return dict(H=H, K=K, H_normalized=(H / math.log(K)) if K > 1 else 0.0, N_effective=math.exp(H))


def conditional_entropy(pairs) -> dict:
    """H(Y | R) = sum_r p(r) H(Y | R = r) from a list of (r, y) observations."""
    from collections import Counter, defaultdict

    by_r = defaultdict(Counter)
    for r, y in pairs:
        by_r[r][y] += 1
    n = sum(sum(c.values()) for c in by_r.values())
    if n == 0:
        return dict(H_cond=None, n=0)
    h = 0.0
    for r, c in by_r.items():
        nr = sum(c.values())
        h += nr / n * shannon(np.asarray(list(c.values()), float) / nr)
    return dict(H_cond=h, n=n, n_conditions=len(by_r))


def kl(p, q) -> float:
    p, q = np.asarray(p, float).ravel(), np.asarray(q, float).ravel()
    if p.shape != q.shape:
        raise ValueError("supports differ")
    m = p > 0
    if np.any(q[m] == 0):
        return math.inf
    return float(max(0.0, (p[m] * np.log(p[m] / q[m])).sum()))


def js(p, q) -> float:
    p, q = np.asarray(p, float).ravel(), np.asarray(q, float).ravel()
    if p.shape != q.shape:
        raise ValueError("supports differ")
    if not (np.isclose(p.sum(), 1) and np.isclose(q.sum(), 1)):
        raise ValueError("probability vectors required")
    m = (p + q) / 2
    return float(0.5 * kl(p, m) + 0.5 * kl(q, m))


def categorical_vectors(a: dict, b: dict):
    """Two count dicts -> probability vectors on the union support (same order)."""
    keys = sorted(set(a) | set(b))
    pa = np.asarray([a.get(k, 0) for k in keys], float)
    pb = np.asarray([b.get(k, 0) for k in keys], float)
    return keys, pa / pa.sum(), pb / pb.sum()


def smoothed_kl(a: dict, b: dict, pseudocount: float = 0.5) -> float:
    keys = sorted(set(a) | set(b))
    pa = np.asarray([a.get(k, 0) for k in keys], float) + pseudocount
    pb = np.asarray([b.get(k, 0) for k in keys], float) + pseudocount
    return kl(pa / pa.sum(), pb / pb.sum())


def wasserstein1(x, y) -> float:
    return float(sps.wasserstein_distance(np.asarray(x, float), np.asarray(y, float)))


# ------------------------------------------------------------------------------------------------------- tails
def cvar(values, q: float = 0.95) -> dict:
    """Empirical mean of the worst (1-q) fraction: k = ceil((1-q) n) largest values (larger = worse)."""
    x = np.sort(np.asarray(values, float).ravel())[::-1]
    n = x.size
    if n == 0:
        return dict(value=None, k=0, n=0)
    k = int(math.ceil((1 - q) * n))
    k = max(1, min(k, n))
    return dict(value=float(x[:k].mean()), k=k, n=n)


def es_positive_fractional(values, q: float = 0.99) -> float:
    """Project ES99+: mean of the worst (1-q) fraction of max(x, 0), zero mass retained, fractional boundary."""
    x = np.sort(np.maximum(np.asarray(values, float).ravel(), 0.0))[::-1]
    n = x.size
    if n == 0:
        return float("nan")
    k = (1.0 - q) * n
    if k <= 0:
        return float(x[0])
    whole = int(math.floor(k))
    frac = k - whole
    total = x[:whole].sum() + (frac * x[whole] if whole < n and frac > 0 else 0.0)
    return float(total / k)


def describe(values) -> dict:
    x = np.asarray(values, float).ravel()
    miss = int((~np.isfinite(x)).sum())
    x = x[np.isfinite(x)]
    if x.size == 0:
        return dict(n=0, missing=miss)
    qs = np.percentile(x, [50, 90, 95, 99])
    return dict(n=int(x.size), missing=miss, mean=float(x.mean()), sd=float(x.std(ddof=1)) if x.size > 1 else None, median=float(qs[0]),
                iqr=float(np.subtract(*np.percentile(x, [75, 25]))), p90=float(qs[1]), p95=float(qs[2]), p99=float(qs[3]), max=float(x.max()), min=float(x.min()),
                cvar95=cvar(x, 0.95)["value"])


def gpd_fit(exceedances, min_n: int = 100) -> dict:
    """Fit a GPD to positive exceedances (floc = 0) and compare with its exponential special case on the same sample."""
    z = np.asarray(exceedances, float).ravel()
    z = z[np.isfinite(z) & (z > 0)]
    n = int(z.size)
    out = dict(n=n, status="ok")
    if n < 50:
        return dict(out, status="insufficient", kappa=None, sigma=None)
    if n < min_n:
        out["status"] = "exploratory"
    c, loc, scale = sps.genpareto.fit(z, floc=0)
    ll = float(sps.genpareto.logpdf(z, c, loc=0, scale=scale).sum())
    lam = z.mean()
    ll_exp = float(sps.expon.logpdf(z, loc=0, scale=lam).sum())
    out.update(kappa=float(c), sigma=float(scale), loglik=ll, aic=2 * 2 - 2 * ll, exp_scale=float(lam), exp_loglik=ll_exp, exp_aic=2 * 1 - 2 * ll_exp,
               loglik_gain_per_excess=(ll - ll_exp) / n, support_endpoint=(-scale / c) if c < 0 else None)
    return out


def gpd_bootstrap(exceedances, groups=None, draws: int = 500, seed: int = 0) -> dict:
    """Percentile CI for kappa/sigma by resampling groups (e.g. windows) when given, else observations."""
    z = np.asarray(exceedances, float).ravel()
    rng = np.random.default_rng(seed)
    ks, ss = [], []
    if groups is not None:
        groups = np.asarray(groups)
        uniq = np.unique(groups)
        idx = {g: np.flatnonzero(groups == g) for g in uniq}
        for _ in range(draws):
            pick = rng.choice(uniq, size=uniq.size, replace=True)
            sample = np.concatenate([z[idx[g]] for g in pick])
            f = gpd_fit(sample, min_n=0)
            if f.get("kappa") is not None:
                ks.append(f["kappa"]); ss.append(f["sigma"])
    else:
        for _ in range(draws):
            sample = rng.choice(z, size=z.size, replace=True)
            f = gpd_fit(sample, min_n=0)
            if f.get("kappa") is not None:
                ks.append(f["kappa"]); ss.append(f["sigma"])
    if not ks:
        return dict(draws=draws, valid=0)
    return dict(draws=draws, valid=len(ks), kappa_ci=[float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5))], sigma_ci=[float(np.percentile(ss, 2.5)), float(np.percentile(ss, 97.5))])


def threshold_fits(values, quantiles=(0.90, 0.95, 0.975), groups=None, draws: int = 200, seed: int = 0) -> list[dict]:
    x = np.asarray(values, float).ravel()
    ok = np.isfinite(x)
    x = x[ok]
    g = None if groups is None else np.asarray(groups)[ok]
    rows = []
    for q in quantiles:
        u = float(np.quantile(x, q))
        m = x > u
        z = x[m] - u
        f = gpd_fit(z)
        row = dict(quantile=q, threshold=u, **f)
        if f.get("kappa") is not None and draws:
            row["bootstrap"] = gpd_bootstrap(z, None if g is None else g[m], draws=draws, seed=seed)
        rows.append(row)
    return rows


def informational_scale_check(kappa: float, sigma: float) -> dict:
    """Nelson's informational-scale condition for the GPD density: -sigma d/dz ln f(z) at z = sigma equals 1 + kappa... (see report)."""
    # d/dz ln f = -(1/kappa + 1) * (kappa/sigma) / (1 + kappa z / sigma); at z = sigma: -(1 + kappa)/(sigma (1 + kappa)) = -1/sigma
    z = sigma
    if kappa == 0:
        dlog = -1.0 / sigma
    else:
        dlog = -(1.0 / kappa + 1.0) * (kappa / sigma) / (1.0 + kappa * z / sigma)
    return dict(kappa=kappa, sigma=sigma, minus_sigma_dlogf_at_sigma=float(-sigma * dlog), identity_holds=bool(abs(-sigma * dlog - 1.0) < 1e-9))


# ------------------------------------------------------------------------------------------------- bootstrap
def grouped_bootstrap(statistic, groups, draws: int = 2000, seed: int = 20261009, ci=(2.5, 97.5)):
    """Resample whole groups with replacement; ``statistic(indices)`` receives the concatenated member indices.

    ``groups`` is an array of group labels per observation. Pairing across models is preserved by construction
    because the statistic sees the same observation indices for every model.
    """
    groups = np.asarray(groups)
    uniq = np.unique(groups)
    members = {g: np.flatnonzero(groups == g) for g in uniq}
    rng = np.random.default_rng(seed)
    point = statistic(np.arange(groups.size))
    reps = []
    for _ in range(draws):
        pick = rng.choice(uniq, size=uniq.size, replace=True)
        idx = np.concatenate([members[g] for g in pick])
        reps.append(statistic(idx))
    reps = np.asarray(reps, float)
    lo, hi = np.nanpercentile(reps, ci[0], axis=0), np.nanpercentile(reps, ci[1], axis=0)
    return dict(point=point, ci_low=lo.tolist() if np.ndim(lo) else float(lo), ci_high=hi.tolist() if np.ndim(hi) else float(hi), draws=draws, n_groups=int(uniq.size), seed=seed)


# ------------------------------------------------------------------------------------------------ aggregation
def mquake_aggregate(rows) -> dict:
    """rows: dicts with case_id, question_index, correct(bool). Returns question accuracy, any-/all-question success."""
    from collections import defaultdict

    by_case = defaultdict(list)
    for r in rows:
        by_case[r["case_id"]].append(bool(r["correct"]))
    nq = sum(len(v) for v in by_case.values())
    q_correct = sum(sum(v) for v in by_case.values())
    return dict(cases=len(by_case), questions=nq, question_accuracy=(q_correct / nq) if nq else None, question_correct=q_correct,
                any_question_success=(sum(any(v) for v in by_case.values()) / len(by_case)) if by_case else None,
                all_question_success=(sum(all(v) for v in by_case.values()) / len(by_case)) if by_case else None,
                any_numerator=sum(any(v) for v in by_case.values()), all_numerator=sum(all(v) for v in by_case.values()))


def rate(num, den) -> dict:
    return dict(value=(num / den) if den else None, numerator=num, denominator=den)
