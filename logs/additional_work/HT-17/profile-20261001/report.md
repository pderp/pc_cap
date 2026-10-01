# HT-17 — saved harm: frequency, severity, and finite-range fits

Capex · snapshot 2026-10-01T16:10:09.949635+00:00 · 9 completed cells. CPU analysis; zero GPU seconds. Exploratory analysis of exposed results.

Coverage: `{'stage4': 6, 'AW-B': 3}`. Pending reader evaluations: 4. The pending cells are not zeros, and this is not the final three-seed PC reader comparison.

Δ is signed cap NLL minus own cap-off NLL at the identical prefix, in nats. Exact zeros, nonzero changes within ±1e-9, benefits, and positive changes remain distinct in the cell JSON. Gate selection is separate telemetry, unavailable for the Stage-4 full-position assay and legacy pilot. No positive-loss count is called a firing count.

The full assay has 1,931 windows × 127 targets = 245,237 positions per cell. The pilot has 32 × 127 = 4,064 positions and is never joined to it. The legacy files lack token hashes; their ordered cap-off matrices match exactly. Pilot MQuAKE retention and drift use different historical populations, so they are reported alongside each other rather than treated as one joint endpoint population.

Frequency means uniform selection of a cell, then a scored position; conditional severity is mean Δ given Δ > u under that same mixture. Group severity is not an equal-weight average of the per-cell conditional means. ES99+ is the mean of cell-level fractional worst-1% positive-part losses, retaining zeros. Maxima are per-cell ranges.

## Primary threshold: u = 0.01 nat

Brackets are 95% percentile intervals from 20 joint window-identity draws, conditional on these fixed cells. Windows may share documents or neighboring text: their independence is unverified. These are not subject-realization or training-seed confidence intervals. Pilot intervals use only 32 windows and deserve particular caution.

| Study | Dataset | Condition | Cells | P(Δ>.01) [interval] | Mean Δ given >.01 [interval] | Gate-selected fraction | ES99+ | Max range | RET-GS |
|---|---|---|---:|---|---|---:|---:|---|---:|
| AW-B | counterfact | capoff | 1 | 0 [0 to 0] | — [—] | 0.0033437 | 0 | 0 to 0 | 0 |
| AW-B | counterfact | mixture:0.367879 | 1 | 0.0028095 [0.0025099 to 0.0030115] | 0.52533 [0.49869 to 0.55965] | 0.0033437 | 0.14761 | 0.99999 to 0.99999 | 0.795 |
| AW-B | counterfact | v5 | 1 | 0.0028177 [0.002514 to 0.0030198] | 1.6278 [1.5116 to 1.8239] | 0.0033437 | 0.45869 | 11.744 to 11.744 | 0.80667 |
| stage4 | counterfact | R1_learned_ff | 1 | 0.0029808 [0.0026068 to 0.0032579] | 2.0466 [1.9037 to 2.2046] | — | 0.61007 | 15.382 to 15.382 | 0.6915 |
| stage4 | counterfact | R1_nonlearned | 1 | 0.018044 [0.017744 to 0.018475] | 3.334 [3.2811 to 3.3603] | — | 5.0234 | 20.283 to 20.283 | 0.126 |
| stage4 | counterfact | v0_stable | 1 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | zsre | R1_learned_ff | 1 | 0.0016107 [0.001224 to 0.0018593] | 1.6067 [1.3486 to 1.8864] | — | 0.25881 | 9.2623 to 9.2623 | 0.955 |
| stage4 | zsre | R1_nonlearned | 1 | 0.00021612 [0.00018288 to 0.00024894] | 1.5019 [1.2103 to 1.9566] | — | 0.032463 | 5.6608 to 5.6608 | 0.502 |
| stage4 | zsre | v0_stable | 1 | 0.0008033 [0.00069881 to 0.00093695] | 1.3258 [0.95881 to 1.6548] | — | 0.10651 | 25.859 to 25.859 | 0.197 |

## Fit eligibility and threshold sensitivity

Fit Y = Δ−u conditional on Δ>u, location zero. Fewer than 100 excesses or 30 contributing windows means **not identified**. Numerical optimization uses two starts; convergence is recorded, not a proof of a unique/global likelihood maximum. Shape ≤−1 is flagged for endpoint likelihood pathology; shape ≤−1/2 is invalid for this protocol's manuscript-domain mapping (not a claim that every such GPD is mathematically undefined). Diagnostic optimizer output is retained separately.

The table gives ranges of eligible **per-cell** estimates, not pooled fits or confidence intervals. Invalid and screened cells remain in the denominator. Primary-threshold shape/scale intervals are in the cell JSON; an interval is withheld if any bootstrap draw is invalid, rather than silently conditioning on successful fits. Thresholds were chosen after seeing preliminary results.

| Study | Dataset | Condition | u | Excesses/cell | Windows/cell | Eligible / all | Shape range | Excess-scale range | CV ΔlogL/excess range (GPD−exp) |
|---|---|---|---:|---|---|---|---|---|---|
| AW-B | counterfact | capoff | 0.01 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| AW-B | counterfact | capoff | 0.1 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| AW-B | counterfact | capoff | 0.5 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| AW-B | counterfact | capoff | 1.0 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 0.01 | 689 to 689 | 386 to 386 | 0 / 1 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 0.1 | 627 to 627 | 370 to 370 | 0 / 1 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 0.5 | 348 to 348 | 246 to 246 | 0 / 1 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 1.0 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| AW-B | counterfact | v5 | 0.01 | 691 to 691 | 387 to 387 | 1 / 1 | 0.14128 to 0.14128 | 1.3918 to 1.3918 | 0.0072571 to 0.0072571 |
| AW-B | counterfact | v5 | 0.1 | 657 to 657 | 378 to 378 | 1 / 1 | 0.15971 to 0.15971 | 1.3566 to 1.3566 | 0.0088661 to 0.0088661 |
| AW-B | counterfact | v5 | 0.5 | 501 to 501 | 317 to 317 | 1 / 1 | 0.20074 to 0.20074 | 1.3294 to 1.3294 | 0.011962 to 0.011962 |
| AW-B | counterfact | v5 | 1.0 | 344 to 344 | 243 to 243 | 1 / 1 | 0.14951 to 0.14951 | 1.5399 to 1.5399 | 0.0017466 to 0.0017466 |
| stage4 | counterfact | R1_learned_ff | 0.01 | 731 to 731 | 363 to 363 | 1 / 1 | 0.097754 to 0.097754 | 1.8404 to 1.8404 | 0.0027649 to 0.0027649 |
| stage4 | counterfact | R1_learned_ff | 0.1 | 699 to 699 | 355 to 355 | 1 / 1 | 0.10449 to 0.10449 | 1.8283 to 1.8283 | 0.0032683 to 0.0032683 |
| stage4 | counterfact | R1_learned_ff | 0.5 | 560 to 560 | 325 to 325 | 1 / 1 | 0.098238 to 0.098238 | 1.8914 to 1.8914 | 0.0023483 to 0.0023483 |
| stage4 | counterfact | R1_learned_ff | 1.0 | 412 to 412 | 271 to 271 | 1 / 1 | -0.0081606 to -0.0081606 | 2.2832 to 2.2832 | -0.0026528 to -0.0026528 |
| stage4 | counterfact | R1_nonlearned | 0.01 | 4425 to 4425 | 1686 to 1686 | 1 / 1 | -0.18418 to -0.18418 | 3.8721 to 3.8721 | — |
| stage4 | counterfact | R1_nonlearned | 0.1 | 4366 to 4366 | 1679 to 1679 | 1 / 1 | -0.18168 to -0.18168 | 3.8146 to 3.8146 | — |
| stage4 | counterfact | R1_nonlearned | 0.5 | 4072 to 4072 | 1653 to 1653 | 1 / 1 | -0.1716 to -0.1716 | 3.5894 to 3.5894 | — |
| stage4 | counterfact | R1_nonlearned | 1.0 | 3621 to 3621 | 1594 to 1594 | 1 / 1 | -0.16444 to -0.16444 | 3.4064 to 3.4064 | 0.019972 to 0.019972 |
| stage4 | counterfact | v0_stable | 0.01 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| stage4 | counterfact | v0_stable | 0.1 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| stage4 | counterfact | v0_stable | 0.5 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| stage4 | counterfact | v0_stable | 1.0 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| stage4 | zsre | R1_learned_ff | 0.01 | 395 to 395 | 181 to 181 | 1 / 1 | 0.048611 to 0.048611 | 1.5196 to 1.5196 | -0.00039403 to -0.00039403 |
| stage4 | zsre | R1_learned_ff | 0.1 | 374 to 374 | 174 to 174 | 1 / 1 | 0.055187 to 0.055187 | 1.5067 to 1.5067 | -0.0014662 to -0.0014662 |
| stage4 | zsre | R1_learned_ff | 0.5 | 280 to 280 | 139 to 139 | 1 / 1 | 0.011773 to 0.011773 | 1.6425 to 1.6425 | -0.0022572 to -0.0022572 |
| stage4 | zsre | R1_learned_ff | 1.0 | 197 to 197 | 104 to 104 | 1 / 1 | -0.067206 to -0.067206 | 1.8767 to 1.8767 | -0.00056943 to -0.00056943 |
| stage4 | zsre | R1_nonlearned | 0.01 | 53 to 53 | 53 to 53 | 0 / 1 | — | — | — |
| stage4 | zsre | R1_nonlearned | 0.1 | 47 to 47 | 47 to 47 | 0 / 1 | — | — | — |
| stage4 | zsre | R1_nonlearned | 0.5 | 38 to 38 | 38 to 38 | 0 / 1 | — | — | — |
| stage4 | zsre | R1_nonlearned | 1.0 | 28 to 28 | 28 to 28 | 0 / 1 | — | — | — |
| stage4 | zsre | v0_stable | 0.01 | 197 to 197 | 189 to 189 | 1 / 1 | 0.59606 to 0.59606 | 0.58028 to 0.58028 | 0.2489 to 0.2489 |
| stage4 | zsre | v0_stable | 0.1 | 173 to 173 | 165 to 165 | 1 / 1 | 0.63262 to 0.63262 | 0.59188 to 0.59188 | 0.26008 to 0.26008 |
| stage4 | zsre | v0_stable | 0.5 | 99 to 99 | 95 to 95 | 0 / 1 | — | — | — |
| stage4 | zsre | v0_stable | 1.0 | 59 to 59 | 58 to 58 | 0 / 1 | — | — | — |

Five fixed folds split whole window identities, shared across all cells. Predictive scores use all held-out excesses. A model giving zero density to any held-out observation has its score marked unavailable/zero predictive density, not evaluated after discarding that observation. A fit failing the eligibility rule in any training fold is also marked. No token-iid p-values are used.

An auxiliary conditional lognormal is evaluated only when both models have invalid held-out predictions or descriptive held-out PIT discrepancies >0.10. This is an explicit exploratory plotting/diagnostic trigger, not a significance test or a selection rule. Its likelihood is normalized above u in the original loss coordinate. All model/fold records are in `report.json`; none of these fits tune the cap.

## Matched contrasts at u = 0.01

These comparisons intersect realization/order/seed coordinates before forming differences and reuse the same window draws on both sides. Efficacy, occupancy, and training costs must still accompany a robustness interpretation.

| Study | Dataset | Left − right | Paired cells | Frequency difference [interval] | Conditional-severity difference [interval] |
|---|---|---|---:|---|---|
| stage4 | zsre | R1_learned_ff − R1_nonlearned | 1 | 0.0013946 [0.0010034 to 0.0016443] | 0.1048 [-0.42242 to 0.45498] |
| stage4 | counterfact | R1_learned_ff − R1_nonlearned | 1 | -0.015063 [-0.015686 to -0.014644] | -1.2874 [-1.4005 to -1.1143] |
| stage4 | zsre | R1_learned_ff − v0_stable | 1 | 0.00080738 [0.00050003 to 0.0010975] | 0.28097 [-0.14439 to 0.79031] |
| stage4 | counterfact | R1_learned_ff − v0_stable | 1 | 0.0029808 [0.0026068 to 0.0032579] | — [—] |
| AW-B | counterfact | mixture:0.367879 − v5 | 1 | -8.1554e-06 [-1.6311e-05 to 0] | -1.1025 [-1.2656 to -1.0009] |

## Between-realization and seed variation

The JSON's `factor_summaries` separates each Stage-4 realization and each reader training seed. `cells.csv` preserves every stream order. These variations are not reduced by treating reused text as new observations. No cross-cell fitted shape is used to assign a complexity class.

AW-B's one-nat upper bound is established analytically at matched prefixes; a failed GPD fit does not weaken that bound. Zero observed harm does not establish zero future risk. A fitted positive shape does not establish an asymptotic law, infinite variance, system temperature, or the growth of microstates W(N).

Reproduce with the command in `report.json` and the bound source hashes in `sources.json`. Only completed output artifacts are admitted. Figures are produced separately from this JSON with `python3 -m aw.tail_class_plot --report ... --out ...`.
