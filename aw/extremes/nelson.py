"""Stage 7 (CPU, supplementary): Nelson informational-scale identity on fitted GPDs and an exploratory coupled-entropy
sensitivity profile of the categorical dataset distributions.

    JAX_PLATFORMS=cpu python -m aw.extremes.nelson

(1) For every eligible generalized-Pareto fit in this study (HT-17 PC-reader rows at u = 0.01, new MQuAKE harm fits,
per-probe loss fits) the informational-scale condition  -sigma * d/dz ln f(z) |_{z=sigma} = 1  is checked numerically
from the fitted (kappa, sigma). The GPD scale is the scale of exceedances above the chosen threshold, not a
threshold-free scale of the full distribution; shape and scale are tabulated separately.
(2) Discrete coupled entropy, one-dimensional case alpha = 1, k = 1:  q(kappa) = (1 + 2 kappa)/(1 + kappa),
H_kappa(p) = [1 / sum_j p_j^{q(kappa)} - 1] / kappa, with H_0 = Shannon in the limit, for kappa in {0, 0.1, 0.25, 0.5, 1}
on the relation / new-target / subject frequency vectors of each population. This is a parameter-sensitivity study of
an empirical categorical distribution, not a calibrated entropy of the system and not a test of the paper's theorem.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd

from aw.extremes import stats as S
from aw.extremes.common import DATA, OUT, Status, atomic_csv, atomic_json

KAPPAS = (0.0, 0.1, 0.25, 0.5, 1.0)


def coupled_entropy(p, kappa: float) -> float:
    p = np.asarray(p, float).ravel()
    if np.any(p < 0) or not np.isclose(p.sum(), 1.0, atol=1e-9):
        raise ValueError("normalized nonnegative probabilities required")
    p = p[p > 0]
    if abs(kappa) < 1e-8:
        return float(-(p * np.log(p)).sum())
    q = (1 + 2 * kappa) / (1 + kappa)
    s = float((p ** q).sum())
    return (1.0 / s - 1.0) / kappa


def uniform_closed_form(W: int, kappa: float) -> float:
    return math.log(W) if abs(kappa) < 1e-8 else (W ** (kappa / (1 + kappa)) - 1) / kappa


def self_tests() -> dict:
    out = {}
    out["point_mass_zero"] = all(abs(coupled_entropy([1.0, 0.0, 0.0], k)) < 1e-12 for k in KAPPAS)
    out["shannon_at_zero"] = abs(coupled_entropy([0.2, 0.3, 0.5], 0.0) - S.shannon([0.2, 0.3, 0.5])) < 1e-12
    out["uniform_closed_form"] = all(abs(coupled_entropy(np.full(W, 1 / W), k) - uniform_closed_form(W, k)) < 1e-9 for W in (2, 7, 50) for k in KAPPAS)
    p = np.array([0.1, 0.2, 0.3, 0.4])
    out["convergence_to_shannon"] = all(abs(coupled_entropy(p, k) - S.shannon(p)) < 5 * k for k in (1e-2, 1e-3, 1e-4)) and abs(coupled_entropy(p, 1e-4) - S.shannon(p)) < 1e-3
    try:
        coupled_entropy([0.5, 0.6], 0.1)
        out["rejects_unnormalized"] = False
    except ValueError:
        out["rejects_unnormalized"] = True
    return out


def profiles() -> pd.DataFrame:
    rows = []
    for f in sorted((DATA / "data" / "frequency").glob("*.csv")):
        ds, rest = f.stem.split("_", 1)
        pop, var = rest.rsplit("_", 1) if rest.endswith(("relation_id", "target_new", "target_true", "subject")) else (rest, "")
        for v in ("relation_id", "target_new", "target_true", "subject"):
            if rest.endswith("_" + v):
                pop, var = rest[: -len(v) - 1], v
        t = pd.read_csv(f)
        p = t["count"].to_numpy(float)
        p = p / p.sum()
        row = dict(dataset=ds, population=pop, variable=var, K=int(len(p)))
        for k in KAPPAS:
            row[f"H_kappa_{k}"] = coupled_entropy(p, k)
        row["uniform_reference_H_kappa_1"] = uniform_closed_form(len(p), 1.0)
        rows.append(row)
    return pd.DataFrame(rows)


def scale_checks() -> pd.DataFrame:
    rows = []
    p = OUT / "tables" / "ht17_pcreader_rows.csv"
    if p.exists():
        t = pd.read_csv(p)
        for _, r in t[t["shape_0p01"].notna()].iterrows():
            rows.append(dict(source="HT-17 PC-reader cell, u=0.01", dataset=r["dataset"], model=f"{r['rule']}_s{int(r['seed'])}", **S.informational_scale_check(float(r["shape_0p01"]), float(r["scale_0p01"]))))
    p = OUT / "tables" / "mquake_pcreader_harm_tails.csv"
    if p.exists():
        t = pd.read_csv(p)
        for _, r in t[t["shape"].notna() & (t["threshold"] == 0.01)].iterrows():
            rows.append(dict(source="ext-20261009 MQuAKE PC-reader harm, u=0.01", dataset="mquake", model=f"{r['rule']}_s{int(r['seed'])}", **S.informational_scale_check(float(r["shape"]), float(r["scale"]))))
    p = OUT / "tables" / "probe_loss_tail_fits.csv"
    if p.exists():
        t = pd.read_csv(p)
        for _, r in t[t["kappa"].notna() & (t["quantile"] == 0.95) & (t["family"] == "edit")].iterrows():
            rows.append(dict(source="per-probe target loss, edit, P95", dataset=r["dataset"], model=r["model"], **S.informational_scale_check(float(r["kappa"]), float(r["sigma"]))))
    return pd.DataFrame(rows)


def main():
    tests = self_tests()
    prof = profiles()
    sc = scale_checks()
    atomic_csv(OUT / "tables" / "coupled_entropy_profiles.csv", prof)
    atomic_csv(OUT / "tables" / "informational_scale_checks.csv", sc)
    atomic_json(OUT / "validation" / "coupled_entropy_tests.json", tests)
    st = Status()
    st.stage("7_nelson", "complete", tests=tests, profiles=int(len(prof)), scale_checks=int(len(sc)), identity_all_hold=bool(sc["identity_holds"].all()) if len(sc) else None)
    print(json.dumps(dict(tests=tests, profiles=len(prof), scale_checks=len(sc), identity_all=bool(sc["identity_holds"].all()) if len(sc) else None)))


if __name__ == "__main__":
    main()
