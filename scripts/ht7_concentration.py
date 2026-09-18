"""HT-7 descriptive concentration on complete, already audited position vectors."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

CONTRACT = {
    "version": 1,
    "role": "descriptive; no admission or inferential cutoff",
    "near_zero_loss_absolute_tolerance_nats": 1e-6,
    "position_top_fractions": [0.001, 0.01],
    "window_top_fractions": [0.01, 0.05, 0.1],
    "top_share_boundary": "fractional empirical mass including zeros",
    "half_mass_count": "smallest integer count in descending order reaching >= 50%",
    "quantiles": "numpy linear at (N-1)*q",
    "gini": "unadjusted finite-population Gini including zeros",
    "zero_total": "shares, half-mass count/fraction and Gini are null",
    "window_kl_benchmark_nats": 0.001,
    "window_kl_strict_exceedance_nats": [0.01, 0.1],
}


def mass_summary(values, fractions):
    a = np.asarray(values, dtype=np.float64).reshape(-1)
    if not a.size or not np.isfinite(a).all() or np.any(a < 0):
        raise ValueError("finite nonnegative nonempty concentration values required")
    a = np.sort(a)
    total = float(a.sum())
    descending = a[::-1]
    shares = {}
    for fraction in fractions:
        if not 0 < fraction <= 1:
            raise ValueError("top fraction outside (0,1]")
        mass = fraction * len(a)
        whole = int(np.floor(mass))
        subtotal = descending[:whole].sum()
        if whole < len(a):
            subtotal += (mass - whole) * descending[whole]
        shares[str(fraction)] = float(subtotal / total) if total else None
    half = (
        int(np.searchsorted(np.cumsum(descending), total / 2, side="left")) + 1 if total else None
    )
    gini = (
        float(np.dot(2 * np.arange(1, len(a) + 1) - len(a) - 1, a) / (len(a) * total))
        if total
        else None
    )
    return dict(
        n=len(a),
        total=total,
        positive_count=int(np.count_nonzero(a)),
        zero_count=int(np.count_nonzero(a == 0)),
        minimum_count_for_half_mass=half,
        fraction_for_half_mass=half / len(a) if half is not None else None,
        top_shares=shares,
        gini=gini,
    )


def concentration(values):
    a = np.asarray(values)
    if a.ndim != 3 or a.shape[2] != 5 or 0 in a.shape or not np.isfinite(a).all():
        raise ValueError("finite (window,position,5) vectors required")
    if np.any(a < 0):
        raise ValueError("stored NLL and KL must be nonnegative")
    refs = {}
    for name, loss_col, kl_col in (("capoff", 1, 3), ("original", 2, 4)):
        delta = a[:, :, 0] - a[:, :, loss_col]
        kl = a[:, :, kl_col]
        window_kl = kl.mean(axis=1)
        near_zero = int(np.count_nonzero(np.abs(delta) < 1e-6))
        refs[name] = dict(
            near_zero_loss_change=dict(
                count=near_zero, denominator=delta.size, fraction=near_zero / delta.size
            ),
            loss_positive_positions=mass_summary(
                np.maximum(delta, 0), CONTRACT["position_top_fractions"]
            ),
            kl_positions=mass_summary(kl, CONTRACT["position_top_fractions"]),
            kl_windows=mass_summary(window_kl, CONTRACT["window_top_fractions"]),
            window_mean_kl=dict(
                n=len(window_kl),
                benchmark_pass_count=int(np.count_nonzero(window_kl <= 0.001)),
                strict_exceedances={
                    str(t): int(np.count_nonzero(window_kl > t)) for t in (0.01, 0.1)
                },
                quantiles={
                    str(q): float(np.quantile(window_kl, q, method="linear"))
                    for q in (0.5, 0.9, 0.99, 1.0)
                },
            ),
        )
    return dict(
        contract=CONTRACT,
        windows=a.shape[0],
        positions=a.shape[0] * a.shape[1],
        references=refs,
        interpretation="Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.",
    )


def from_binding(binding):
    path = Path(binding["path"])

    def verify():
        if hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]:
            raise ValueError("concentration vector hash changed")

    verify()
    with np.load(path, allow_pickle=False) as archive:
        if archive.files != ["values"]:
            raise ValueError("unexpected concentration vector inventory")
        result = concentration(archive["values"])
    verify()
    return result


def report_lines(value):
    lines = [
        "",
        "HT-7 concentration (descriptive; fractional top shares include zero mass):",
        "",
        "| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, ref in value["references"].items():
        pos, win, means = ref["kl_positions"], ref["kl_windows"], ref["window_mean_kl"]
        near = ref["near_zero_loss_change"]

        def fmt(x):
            return "undefined" if x is None else f"{x:.6g}"

        lines.append(
            f"| {name} | {near['count']} / {near['denominator']} | {fmt(pos['minimum_count_for_half_mass'])} ({fmt(pos['fraction_for_half_mass'])}) | "
            + " / ".join(fmt(x) for x in pos["top_shares"].values())
            + f" | {fmt(pos['gini'])} | {means['benchmark_pass_count']} / {means['n']} | "
            + " / ".join(str(x) for x in means["strict_exceedances"].values())
            + " | "
            + " / ".join(fmt(x) for x in win["top_shares"].values())
            + " | "
            + " / ".join(fmt(x) for x in means["quantiles"].values())
            + " |"
        )
    return [*lines, "", value["interpretation"]]
