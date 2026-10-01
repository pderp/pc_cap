# HT-17 — saved harm: frequency, severity, and finite-range fits

Capex · snapshot 2026-10-01T16:13:12.529921+00:00 · 299 completed cells. CPU analysis; zero GPU seconds. Exploratory analysis of exposed results.

Coverage: `{'stage4': 225, 'AW-B': 30, 'PC-reader': 8, 'kappa-pilot': 36}`. Pending reader evaluations: 4. The pending cells are not zeros, and this is not the final three-seed PC reader comparison.

Δ is signed cap NLL minus own cap-off NLL at the identical prefix, in nats. Exact zeros, nonzero changes within ±1e-9, benefits, and positive changes remain distinct in the cell JSON. Gate selection is separate telemetry, unavailable for the Stage-4 full-position assay and legacy pilot. No positive-loss count is called a firing count.

The full assay has 1,931 windows × 127 targets = 245,237 positions per cell. The pilot has 32 × 127 = 4,064 positions and is never joined to it. The legacy files lack token hashes; their ordered cap-off matrices match exactly. Pilot MQuAKE retention and drift use different historical populations, so they are reported alongside each other rather than treated as one joint endpoint population.

Frequency means uniform selection of a cell, then a scored position; conditional severity is mean Δ given Δ > u under that same mixture. Group severity is not an equal-weight average of the per-cell conditional means. ES99+ is the mean of cell-level fractional worst-1% positive-part losses, retaining zeros. Maxima are per-cell ranges.

## Primary threshold: u = 0.01 nat

Brackets are 95% percentile intervals from 200 joint window-identity draws, conditional on these fixed cells. Windows may share documents or neighboring text: their independence is unverified. These are not subject-realization or training-seed confidence intervals. Pilot intervals use only 32 windows and deserve particular caution.

| Study | Dataset | Condition | Cells | P(Δ>.01) [interval] | Mean Δ given >.01 [interval] | Gate-selected fraction | ES99+ | Max range | RET-GS |
|---|---|---|---:|---|---|---:|---:|---|---:|
| AW-B | counterfact | capoff | 5 | 0 [0 to 0] | — [—] | 0.0034978 | 0 | 0 to 0 | 0 |
| AW-B | counterfact | mixture:0.367879 | 5 | 0.0030517 [0.0027963 to 0.003307] | 0.58109 [0.56386 to 0.60015] | 0.0034978 | 0.17735 | 0.99999 to 1 | 0.757 |
| AW-B | counterfact | v5 | 5 | 0.0030583 [0.0028028 to 0.0033121] | 1.9252 [1.8199 to 2.0498] | 0.0034978 | 0.5888 | 11.744 to 15.382 | 0.767 |
| AW-B | zsre | capoff | 5 | 0 [0 to 0] | — [—] | 0.0014362 | 0 | 0 to 0 | 0 |
| AW-B | zsre | mixture:0.367879 | 5 | 0.0011809 [0.0010243 to 0.0013532] | 0.54217 [0.518 to 0.56501] | 0.0014362 | 0.064035 | 0.99957 to 0.99999 | 0.984 |
| AW-B | zsre | v5 | 5 | 0.0011874 [0.0010323 to 0.0013584] | 1.6189 [1.5083 to 1.7592] | 0.0014362 | 0.19224 | 8.3038 to 12.293 | 0.984 |
| PC-reader | counterfact | bp | 3 | 0.0012668 [0.0011075 to 0.0014354] | 2.313 [2.1342 to 2.4936] | 0.0014476 | 0.29301 | 8.5193 to 12.502 | 0.815 |
| PC-reader | counterfact | epc | 1 | 0.00066059 [0.00047689 to 0.00087313] | 2.0047 [1.7153 to 2.312] | 0.00075437 | 0.13243 | 7.706 to 7.706 | 0.56833 |
| PC-reader | zsre | bp | 3 | 6.2525e-05 [4.3461e-05 to 8.434e-05] | 2.28 [1.6698 to 2.9691] | 7.068e-05 | 0.014255 | 6.5063 to 10.576 | 0.98 |
| PC-reader | zsre | epc | 1 | 0 [0 to 0] | — [—] | 0 | 0 | 0 to 0 | 0.94667 |
| kappa-pilot | counterfact | clip2 | 3 | 0.0054134 [0.0019685 to 0.0098487] | 2.4857 [1.7126 to 3.4442] | — | 1.3457 | 6.4299 to 6.5609 | 0.75333 |
| kappa-pilot | counterfact | kappa02 | 3 | 0.0042651 [0.00065617 to 0.0080565] | 2.4632 [1.8862 to 3.4358] | — | 1.0507 | 5.0747 to 6.4554 | 0.76667 |
| kappa-pilot | counterfact | kappa05 | 3 | 0.0027067 [0.00073204 to 0.0056656] | 2.773 [1.7023 to 4.4671] | — | 0.75066 | 4.4563 to 6.4554 | 0.71 |
| kappa-pilot | counterfact | ordinary | 3 | 0.0082841 [0.0021305 to 0.016412] | 2.2162 [1.6933 to 2.8086] | — | 1.713 | 5.491 to 6.4554 | 0.775 |
| kappa-pilot | mquake | clip2 | 3 | 0.0011483 [0 to 0.0025529] | 1.7604 [0.62038 to 5.9933] | — | 0.20226 | 1.1538 to 6.9388 | 0.66667 |
| kappa-pilot | mquake | kappa02 | 3 | 0.0023786 [8.2021e-05 to 0.0054318] | 0.85218 [0.24038 to 1.2599] | — | 0.2028 | 1.2338 to 2.9896 | 0.57 |
| kappa-pilot | mquake | kappa05 | 3 | 0.0018865 [0 to 0.0041872] | 1.0619 [0.90589 to 2.0828] | — | 0.20042 | 1.0783 to 3.7785 | 0.61667 |
| kappa-pilot | mquake | ordinary | 3 | 0.0058235 [0.0015563 to 0.010343] | 1.2272 [0.76366 to 2.0118] | — | 0.71437 | 2.0764 to 6.9388 | 0.64667 |
| kappa-pilot | zsre | clip2 | 3 | 0 [0 to 0] | — [—] | — | 0.00012318 | 0.00016735 to 0.00016735 | 0.91667 |
| kappa-pilot | zsre | kappa02 | 3 | 0 [0 to 0] | — [—] | — | 0.00012318 | 0.00016735 to 0.00016735 | 0.92667 |
| kappa-pilot | zsre | kappa05 | 3 | 0 [0 to 0] | — [—] | — | 0.00012318 | 0.00016735 to 0.00016735 | 0.91667 |
| kappa-pilot | zsre | ordinary | 3 | 0.0027067 [0.0011483 to 0.0042671] | 2.9261 [2.0577 to 3.7217] | — | 0.7921 | 0.00016735 to 8.686 | 0.96667 |
| stage4 | counterfact | R1_learned_ff | 15 | 0.0029835 [0.0026987 to 0.0033119] | 1.9125 [1.7877 to 2.0385] | — | 0.57061 | 11.366 to 15.382 | 0.678 |
| stage4 | counterfact | R1_nonlearned | 15 | 0.02045 [0.019808 to 0.021014] | 3.4865 [3.4311 to 3.5434] | — | 5.4537 | 16.299 to 20.283 | 0.1205 |
| stage4 | counterfact | S1_LM | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | matched_update | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | v0_live_C1 | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | v0_live_C2 | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | counterfact | v0_stable | 15 | 0 [0 to 0] | — [—] | — | 0 | 0 to 0 | 0 |
| stage4 | zsre | R1_learned_ff | 15 | 0.0015944 [0.001366 to 0.0018256] | 1.6295 [1.4921 to 1.7773] | — | 0.25982 | 8.954 to 11.048 | 0.96033 |
| stage4 | zsre | R1_nonlearned | 15 | 0.00026641 [0.00021476 to 0.00031677] | 1.8062 [1.5691 to 2.0404] | — | 0.048119 | 5.6608 to 7.001 | 0.524 |
| stage4 | zsre | S1_LM | 15 | 0.0010493 [0.00096798 to 0.0011211] | 1.7202 [1.5195 to 1.9585] | — | 0.18051 | 19.362 to 27.605 | 0.1866 |
| stage4 | zsre | S1_literal | 15 | 0.0010409 [0.00096228 to 0.0011117] | 1.7238 [1.5254 to 1.9448] | — | 0.17944 | 19.344 to 27.688 | 0.18873 |
| stage4 | zsre | matched_update | 15 | 0.0010531 [0.00097558 to 0.0011195] | 1.6772 [1.4921 to 1.8631] | — | 0.17664 | 17.085 to 33.767 | 0.18367 |
| stage4 | zsre | v0_live_C1 | 15 | 0.0009588 [0.00088046 to 0.0010298] | 2.1876 [2.0116 to 2.3972] | — | 0.20976 | 10.426 to 27.684 | 0.1304 |
| stage4 | zsre | v0_live_C2 | 15 | 0.00018676 [0.00016011 to 0.0002175] | 17.203 [15.705 to 18.744] | — | 0.32128 | 38.755 to 50.597 | 0.10727 |
| stage4 | zsre | v0_stable | 15 | 0.0010409 [0.0009596 to 0.0011103] | 1.7163 [1.519 to 1.9331] | — | 0.17865 | 19.339 to 27.684 | 0.1856 |

## Fit eligibility and threshold sensitivity

Fit Y = Δ−u conditional on Δ>u, location zero. Fewer than 100 excesses or 30 contributing windows means **not identified**. Numerical optimization uses two starts; convergence is recorded, not a proof of a unique/global likelihood maximum. Shape ≤−1 is flagged for endpoint likelihood pathology; shape ≤−1/2 is invalid for this protocol's manuscript-domain mapping (not a claim that every such GPD is mathematically undefined). Diagnostic optimizer output is retained separately.

The table gives ranges of eligible **per-cell** estimates, not pooled fits or confidence intervals. Invalid and screened cells remain in the denominator. Primary-threshold shape/scale intervals are in the cell JSON; an interval is withheld if any bootstrap draw is invalid, rather than silently conditioning on successful fits. Thresholds were chosen after seeing preliminary results.

| Study | Dataset | Condition | u | Excesses/cell | Windows/cell | Eligible / all | Shape range | Excess-scale range | CV ΔlogL/excess range (GPD−exp) |
|---|---|---|---:|---|---|---|---|---|---|
| AW-B | counterfact | capoff | 0.01 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | counterfact | capoff | 0.1 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | counterfact | capoff | 0.5 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | counterfact | capoff | 1.0 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 0.01 | 613 to 930 | 386 to 475 | 0 / 5 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 0.1 | 566 to 863 | 370 to 461 | 0 / 5 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 0.5 | 348 to 525 | 246 to 358 | 0 / 5 | — | — | — |
| AW-B | counterfact | mixture:0.367879 | 1.0 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | counterfact | v5 | 0.01 | 613 to 933 | 387 to 476 | 5 / 5 | -0.057533 to 0.14128 | 1.3918 to 2.2523 | -0.0023193 to 0.0072571 |
| AW-B | counterfact | v5 | 0.1 | 589 to 892 | 378 to 466 | 5 / 5 | -0.051754 to 0.15971 | 1.3566 to 2.2258 | -0.0033433 to 0.0088661 |
| AW-B | counterfact | v5 | 0.5 | 477 to 718 | 317 to 421 | 5 / 5 | -0.08816 to 0.20074 | 1.3294 to 2.3388 | -0.0047739 to 0.011962 |
| AW-B | counterfact | v5 | 1.0 | 344 to 518 | 243 to 353 | 5 / 5 | -0.1851 to 0.14951 | 1.5399 to 2.7032 | -0.0017044 to 0.011973 |
| AW-B | zsre | capoff | 0.01 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | zsre | capoff | 0.1 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | zsre | capoff | 0.5 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | zsre | capoff | 1.0 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | zsre | mixture:0.367879 | 0.01 | 230 to 349 | 147 to 175 | 0 / 5 | — | — | — |
| AW-B | zsre | mixture:0.367879 | 0.1 | 215 to 318 | 138 to 164 | 0 / 5 | — | — | — |
| AW-B | zsre | mixture:0.367879 | 0.5 | 124 to 167 | 92 to 113 | 0 / 5 | — | — | — |
| AW-B | zsre | mixture:0.367879 | 1.0 | 0 to 0 | 0 to 0 | 0 / 5 | — | — | — |
| AW-B | zsre | v5 | 0.01 | 231 to 353 | 147 to 178 | 5 / 5 | 0.0029586 to 0.11397 | 1.2976 to 1.6953 | -0.0085026 to 0.0033147 |
| AW-B | zsre | v5 | 0.1 | 223 to 334 | 142 to 168 | 5 / 5 | 0.024691 to 0.13127 | 1.2653 to 1.6223 | -0.0066587 to 0.0066546 |
| AW-B | zsre | v5 | 0.5 | 172 to 242 | 119 to 135 | 5 / 5 | 0.008174 to 0.12947 | 1.3322 to 1.7205 | -0.017919 to 0.0086229 |
| AW-B | zsre | v5 | 1.0 | 123 to 165 | 91 to 112 | 5 / 5 | -0.079166 to 0.096679 | 1.3788 to 1.9824 | -0.016661 to 5.1354e-05 |
| PC-reader | counterfact | bp | 0.01 | 138 to 567 | 101 to 305 | 3 / 3 | -0.23704 to -0.016963 | 2.1725 to 2.7695 | -0.0025404 to 0.017682 |
| PC-reader | counterfact | bp | 0.1 | 136 to 548 | 100 to 298 | 3 / 3 | -0.25181 to 0.019053 | 2.0376 to 2.8155 | -0.0033988 to 0.020364 |
| PC-reader | counterfact | bp | 0.5 | 116 to 463 | 88 to 268 | 3 / 3 | -0.29785 to 0.098474 | 1.8059 to 2.9253 | -0.0024487 to 0.030159 |
| PC-reader | counterfact | bp | 1.0 | 83 to 363 | 69 to 230 | 2 / 3 | -0.31784 to -0.16288 | 2.858 to 2.8698 | 0.0056572 to 0.034532 |
| PC-reader | counterfact | epc | 0.01 | 162 to 162 | 82 to 82 | 1 / 1 | -0.26158 to -0.26158 | 2.5091 to 2.5091 | -0.011961 to -0.011961 |
| PC-reader | counterfact | epc | 0.1 | 156 to 156 | 80 to 80 | 1 / 1 | -0.26311 to -0.26311 | 2.4927 to 2.4927 | 0.0048107 to 0.0048107 |
| PC-reader | counterfact | epc | 0.5 | 136 to 136 | 72 to 72 | 1 / 1 | -0.23079 to -0.23079 | 2.2538 to 2.2538 | 0.0053155 to 0.0053155 |
| PC-reader | counterfact | epc | 1.0 | 112 to 112 | 62 to 62 | 1 / 1 | -0.19208 to -0.19208 | 1.9981 to 1.9981 | -0.010256 to -0.010256 |
| PC-reader | zsre | bp | 0.01 | 12 to 19 | 12 to 17 | 0 / 3 | — | — | — |
| PC-reader | zsre | bp | 0.1 | 12 to 19 | 12 to 17 | 0 / 3 | — | — | — |
| PC-reader | zsre | bp | 0.5 | 10 to 17 | 10 to 15 | 0 / 3 | — | — | — |
| PC-reader | zsre | bp | 1.0 | 9 to 15 | 9 to 13 | 0 / 3 | — | — | — |
| PC-reader | zsre | epc | 0.01 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| PC-reader | zsre | epc | 0.1 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| PC-reader | zsre | epc | 0.5 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| PC-reader | zsre | epc | 1.0 | 0 to 0 | 0 to 0 | 0 / 1 | — | — | — |
| kappa-pilot | counterfact | clip2 | 0.01 | 14 to 26 | 5 to 9 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | clip2 | 0.1 | 14 to 25 | 5 to 9 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | clip2 | 0.5 | 12 to 23 | 4 to 8 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | clip2 | 1.0 | 11 to 19 | 4 to 8 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa02 | 0.01 | 12 to 28 | 4 to 7 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa02 | 0.1 | 12 to 28 | 4 to 7 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa02 | 0.5 | 11 to 26 | 4 to 7 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa02 | 1.0 | 7 to 21 | 3 to 7 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa05 | 0.01 | 8 to 15 | 4 to 4 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa05 | 0.1 | 8 to 15 | 4 to 4 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa05 | 0.5 | 8 to 14 | 4 to 4 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | kappa05 | 1.0 | 6 to 11 | 3 to 4 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | ordinary | 0.01 | 12 to 60 | 6 to 10 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | ordinary | 0.1 | 12 to 57 | 6 to 10 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | ordinary | 0.5 | 11 to 55 | 5 to 10 | 0 / 3 | — | — | — |
| kappa-pilot | counterfact | ordinary | 1.0 | 8 to 47 | 5 to 9 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | clip2 | 0.01 | 2 to 7 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | clip2 | 0.1 | 2 to 7 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | clip2 | 0.5 | 1 to 7 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | clip2 | 1.0 | 1 to 3 | 1 to 2 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa02 | 0.01 | 8 to 12 | 2 to 4 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa02 | 0.1 | 8 to 12 | 2 to 4 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa02 | 0.5 | 5 to 9 | 2 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa02 | 1.0 | 1 to 4 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa05 | 0.01 | 2 to 16 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa05 | 0.1 | 2 to 16 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa05 | 0.5 | 2 to 13 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | kappa05 | 1.0 | 1 to 7 | 1 to 3 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | ordinary | 0.01 | 12 to 43 | 4 to 8 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | ordinary | 0.1 | 11 to 40 | 4 to 8 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | ordinary | 0.5 | 9 to 31 | 4 to 7 | 0 / 3 | — | — | — |
| kappa-pilot | mquake | ordinary | 1.0 | 4 to 19 | 3 to 6 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | clip2 | 0.01 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | clip2 | 0.1 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | clip2 | 0.5 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | clip2 | 1.0 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa02 | 0.01 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa02 | 0.1 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa02 | 0.5 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa02 | 1.0 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa05 | 0.01 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa05 | 0.1 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa05 | 0.5 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | kappa05 | 1.0 | 0 to 0 | 0 to 0 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | ordinary | 0.01 | 0 to 26 | 0 to 9 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | ordinary | 0.1 | 0 to 25 | 0 to 9 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | ordinary | 0.5 | 0 to 23 | 0 to 9 | 0 / 3 | — | — | — |
| kappa-pilot | zsre | ordinary | 1.0 | 0 to 18 | 0 to 8 | 0 / 3 | — | — | — |
| stage4 | counterfact | R1_learned_ff | 0.01 | 646 to 818 | 352 to 388 | 15 / 15 | 0.029391 to 0.097754 | 1.7383 to 1.8404 | -0.0010405 to 0.0027649 |
| stage4 | counterfact | R1_learned_ff | 0.1 | 621 to 791 | 344 to 384 | 15 / 15 | 0.051585 to 0.10449 | 1.6925 to 1.8283 | -0.00097093 to 0.0032683 |
| stage4 | counterfact | R1_learned_ff | 0.5 | 487 to 626 | 290 to 339 | 15 / 15 | 0.048926 to 0.098238 | 1.7414 to 1.8914 | -0.0010451 to 0.0023483 |
| stage4 | counterfact | R1_learned_ff | 1.0 | 357 to 446 | 232 to 271 | 15 / 15 | -0.046005 to -0.0017658 | 1.914 to 2.2832 | -0.0026528 to -0.0019765 |
| stage4 | counterfact | R1_nonlearned | 0.01 | 4425 to 5743 | 1686 to 1767 | 15 / 15 | -0.26215 to -0.18412 | 3.8712 to 4.603 | 0.032535 to 0.032535 |
| stage4 | counterfact | R1_nonlearned | 0.1 | 4366 to 5701 | 1679 to 1765 | 15 / 15 | -0.25878 to -0.18162 | 3.8137 to 4.5224 | 0.030306 to 0.030306 |
| stage4 | counterfact | R1_nonlearned | 0.5 | 4072 to 5405 | 1653 to 1744 | 15 / 15 | -0.24858 to -0.1716 | 3.5894 to 4.2515 | 0.024532 to 0.024532 |
| stage4 | counterfact | R1_nonlearned | 1.0 | 3621 to 4975 | 1594 to 1713 | 15 / 15 | -0.23842 to -0.16444 | 3.4064 to 3.9673 | 0.019972 to 0.022034 |
| stage4 | counterfact | S1_LM | 0.01 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | S1_LM | 0.1 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | S1_LM | 0.5 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | S1_LM | 1.0 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | matched_update | 0.01 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | matched_update | 0.1 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | matched_update | 0.5 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | matched_update | 1.0 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C1 | 0.01 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C1 | 0.1 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C1 | 0.5 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C1 | 1.0 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C2 | 0.01 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C2 | 0.1 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C2 | 0.5 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_live_C2 | 1.0 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_stable | 0.01 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_stable | 0.1 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_stable | 0.5 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | counterfact | v0_stable | 1.0 | 0 to 0 | 0 to 0 | 0 / 15 | — | — | — |
| stage4 | zsre | R1_learned_ff | 0.01 | 376 to 402 | 181 to 208 | 15 / 15 | 0.043513 to 0.058756 | 1.5196 to 1.5526 | -0.00039403 to 0.00025948 |
| stage4 | zsre | R1_learned_ff | 0.1 | 358 to 388 | 174 to 204 | 15 / 15 | 0.055187 to 0.076556 | 1.4616 to 1.5218 | -0.0014662 to 0.0014706 |
| stage4 | zsre | R1_learned_ff | 0.5 | 268 to 299 | 139 to 174 | 15 / 15 | 0.011773 to 0.11363 | 1.414 to 1.7088 | -0.0042467 to 0.0028666 |
| stage4 | zsre | R1_learned_ff | 1.0 | 189 to 200 | 104 to 128 | 15 / 15 | -0.067206 to -0.038071 | 1.8293 to 1.958 | -0.01449 to -0.00056943 |
| stage4 | zsre | R1_nonlearned | 0.01 | 46 to 97 | 43 to 93 | 0 / 15 | — | — | — |
| stage4 | zsre | R1_nonlearned | 0.1 | 46 to 94 | 43 to 91 | 0 / 15 | — | — | — |
| stage4 | zsre | R1_nonlearned | 0.5 | 38 to 83 | 38 to 81 | 0 / 15 | — | — | — |
| stage4 | zsre | R1_nonlearned | 1.0 | 28 to 61 | 28 to 59 | 0 / 15 | — | — | — |
| stage4 | zsre | S1_LM | 0.01 | 197 to 477 | 187 to 427 | 15 / 15 | 0.41536 to 1.0422 | 0.3236 to 0.9273 | 0.14735 to 0.59186 |
| stage4 | zsre | S1_LM | 0.1 | 173 to 403 | 165 to 369 | 15 / 15 | 0.46785 to 1.1188 | 0.31881 to 0.8603 | 0.16269 to 0.64297 |
| stage4 | zsre | S1_LM | 0.5 | 97 to 165 | 91 to 158 | 13 / 15 | 0.39342 to 1.265 | 0.53721 to 2.4744 | 0.041366 to 0.45198 |
| stage4 | zsre | S1_LM | 1.0 | 54 to 112 | 53 to 110 | 2 / 15 | 0.6095 to 0.63405 | 1.4459 to 1.4874 | 0.065032 to 0.096318 |
| stage4 | zsre | S1_literal | 0.01 | 196 to 475 | 186 to 426 | 15 / 15 | 0.44164 to 1.0211 | 0.32847 to 0.95205 | 0.14199 to 0.58393 |
| stage4 | zsre | S1_literal | 0.1 | 171 to 405 | 163 to 371 | 15 / 15 | 0.48096 to 1.096 | 0.31432 to 0.8771 | 0.15742 to 0.64503 |
| stage4 | zsre | S1_literal | 0.5 | 93 to 162 | 88 to 155 | 12 / 15 | 0.36575 to 1.1607 | 0.58234 to 2.5184 | 0.034368 to 0.42464 |
| stage4 | zsre | S1_literal | 1.0 | 54 to 112 | 53 to 110 | 2 / 15 | 0.58309 to 0.62046 | 1.4535 to 1.5508 | 0.059946 to 0.09753 |
| stage4 | zsre | matched_update | 0.01 | 184 to 455 | 175 to 413 | 15 / 15 | 0.40643 to 1.0354 | 0.32848 to 0.90783 | 0.14261 to 0.66752 |
| stage4 | zsre | matched_update | 0.1 | 166 to 382 | 157 to 352 | 15 / 15 | 0.43483 to 1.1935 | 0.30633 to 0.94262 | 0.13573 to 0.71131 |
| stage4 | zsre | matched_update | 0.5 | 98 to 165 | 92 to 159 | 14 / 15 | 0.39727 to 1.427 | 0.57578 to 1.9864 | 0.03085 to 0.40846 |
| stage4 | zsre | matched_update | 1.0 | 57 to 122 | 57 to 118 | 3 / 15 | 0.19461 to 0.42475 | 1.7816 to 3.0956 | 0.0030264 to 0.048295 |
| stage4 | zsre | v0_live_C1 | 0.01 | 151 to 304 | 145 to 254 | 15 / 15 | -0.27971 to 0.96089 | 0.44582 to 3.7004 | -0.010759 to 0.46027 |
| stage4 | zsre | v0_live_C1 | 0.1 | 136 to 284 | 131 to 224 | 15 / 15 | -0.30258 to 1.0827 | 0.46817 to 3.9298 | -0.00058049 to 0.49703 |
| stage4 | zsre | v0_live_C1 | 0.5 | 82 to 232 | 79 to 178 | 11 / 15 | -0.39526 to 0.4431 | 1.3664 to 4.3833 | -0.032363 to 0.092753 |
| stage4 | zsre | v0_live_C1 | 1.0 | 48 to 206 | 47 to 154 | 8 / 15 | -0.39765 to 0.21973 | 2.761 to 4.2775 | -0.024657 to 0.084807 |
| stage4 | zsre | v0_live_C2 | 0.01 | 26 to 80 | 24 to 66 | 0 / 15 | — | — | — |
| stage4 | zsre | v0_live_C2 | 0.1 | 25 to 80 | 23 to 66 | 0 / 15 | — | — | — |
| stage4 | zsre | v0_live_C2 | 0.5 | 23 to 79 | 22 to 65 | 0 / 15 | — | — | — |
| stage4 | zsre | v0_live_C2 | 1.0 | 21 to 78 | 20 to 64 | 0 / 15 | — | — | — |
| stage4 | zsre | v0_stable | 0.01 | 197 to 476 | 185 to 427 | 15 / 15 | 0.43349 to 1.0286 | 0.3253 to 0.92521 | 0.14859 to 0.59354 |
| stage4 | zsre | v0_stable | 0.1 | 173 to 403 | 164 to 369 | 15 / 15 | 0.47413 to 1.094 | 0.31778 to 0.8839 | 0.15796 to 0.64822 |
| stage4 | zsre | v0_stable | 0.5 | 95 to 163 | 90 to 155 | 12 / 15 | 0.39401 to 1.1942 | 0.57249 to 2.4643 | 0.040213 to 0.43039 |
| stage4 | zsre | v0_stable | 1.0 | 54 to 111 | 53 to 109 | 2 / 15 | 0.57777 to 0.6346 | 1.4282 to 1.5744 | 0.056282 to 0.097451 |

Five fixed folds split whole window identities, shared across all cells. Predictive scores use all held-out excesses. A model giving zero density to any held-out observation has its score marked unavailable/zero predictive density, not evaluated after discarding that observation. A fit failing the eligibility rule in any training fold is also marked. No token-iid p-values are used.

An auxiliary conditional lognormal is evaluated only when both models have invalid held-out predictions or descriptive held-out PIT discrepancies >0.10. This is an explicit exploratory plotting/diagnostic trigger, not a significance test or a selection rule. Its likelihood is normalized above u in the original loss coordinate. All model/fold records are in `report.json`; none of these fits tune the cap.

## Matched contrasts at u = 0.01

These comparisons intersect realization/order/seed coordinates before forming differences and reuse the same window draws on both sides. Efficacy, occupancy, and training costs must still accompany a robustness interpretation.

| Study | Dataset | Left − right | Paired cells | Frequency difference [interval] | Conditional-severity difference [interval] |
|---|---|---|---:|---|---|
| stage4 | zsre | R1_learned_ff − R1_nonlearned | 15 | 0.001328 [0.0010982 to 0.0015645] | -0.17664 [-0.44595 to 0.082613] |
| stage4 | counterfact | R1_learned_ff − R1_nonlearned | 15 | -0.017466 [-0.018099 to -0.016791] | -1.574 [-1.7003 to -1.4265] |
| stage4 | zsre | R1_learned_ff − v0_stable | 15 | 0.00055348 [0.00032389 to 0.00078666] | -0.08674 [-0.32236 to 0.12449] |
| stage4 | counterfact | R1_learned_ff − v0_stable | 15 | 0.0029835 [0.0026987 to 0.0033119] | — [—] |
| AW-B | zsre | mixture:0.367879 − v5 | 5 | -6.5243e-06 [-1.47e-05 to -1.6107e-06] | -1.0767 [-1.1968 to -0.97938] |
| AW-B | counterfact | mixture:0.367879 − v5 | 5 | -6.5243e-06 [-1.2233e-05 to -1.6311e-06] | -1.3441 [-1.4556 to -1.2509] |
| PC-reader | zsre | epc − bp | 1 | -6.1165e-05 [-9.7865e-05 to -2.8544e-05] | — [—] |
| PC-reader | counterfact | epc − bp | 1 | -0.00026505 [-0.00045273 to -8.9709e-05] | -0.2316 [-0.52725 to 0.089358] |

## Between-realization and seed variation

The JSON's `factor_summaries` separates each Stage-4 realization and each reader training seed. `cells.csv` preserves every stream order. These variations are not reduced by treating reused text as new observations. No cross-cell fitted shape is used to assign a complexity class.

AW-B's one-nat upper bound is established analytically at matched prefixes; a failed GPD fit does not weaken that bound. Zero observed harm does not establish zero future risk. A fitted positive shape does not establish an asymptotic law, infinite variance, system temperature, or the growth of microstates W(N).

Reproduce with the command in `report.json` and the bound source hashes in `sources.json`. Only completed output artifacts are admitted. Figures are produced separately from this JSON with `python3 -m aw.tail_class_plot --report ... --out ...`.
