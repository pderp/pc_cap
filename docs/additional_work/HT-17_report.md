# HT-17 — what the saved harm distributions support

Capex · 4 October 2026 · all three paired reader seeds complete

**The saved data support a difference in finite-range tail behavior, not three established complexity classes.** Stable v0 on zsRE has a more pronounced tail than an exponential predicts. For the learned reader, the extra generalized-Pareto shape parameter adds little held-out predictive value. Some apparently bounded fitted tails fail to predict held-out extremes. The one-nat mixture remains an analytically bounded intervention, regardless of those fitting failures.

This CPU analysis covers **303 completed cells**: 225 Stage-4 cells on zsRE/CounterFact, including 90 cells in the three primary conditions; 30 AW-B memory/arm combinations; twelve completed BP/ePC reader evaluations; and 36 legacy κ-pilot cells, including MQuAKE. All twelve reader evaluations are complete. Option R and AW-L are reported separately; their vectors have not been added to this predefined tail-fit population. No GPU use or model execution was required.

The canonical numerical record is [snapshot-20261004-complete/report.json](../../logs/additional_work/HT-17/snapshot-20261004-complete/report.json), with [complete tables and methods](../../logs/additional_work/HT-17/snapshot-20261004-complete/report.md), [per-cell/per-threshold CSV](../../logs/additional_work/HT-17/snapshot-20261004-complete/cells.csv), and [input hashes](../../logs/additional_work/HT-17/snapshot-20261004-complete/sources.json). The earlier snapshots are historical; all prior per-cell statistics and non-reader group summaries remain unchanged. This refresh retains the version-2 rule that withholds conditional-severity intervals if any resample has no harmful events; it also shows the number of cells with comparable predictive scores.

## Frequency and severity are different questions

Here harm is Δ = NLL(cap) − NLL(own cap-off), in nats at the same prefix. The primary reporting threshold is 0.01 nat. Frequencies below are percentages of all scored positions, not percentages of gate firings. Conditional severity is the mean loss increase among positions exceeding that threshold. Signed benefits and exact/near-zero changes remain in the saved summaries.

Each Stage-4 row contains fifteen cells: three subject realizations and five orders, at 1,000 edits. Each cell reuses the same 245,237 ordinary-text positions. Those repetitions are not independent text samples.

| Dataset | Cap | Harmful-change frequency | Conditional severity, nats | Mean cell ES99+ | Maximum across cells, nats | Mean RET-GS |
|---|---|---:|---:|---:|---:|---:|
| zsRE | Learned v5 | 0.1594% | 1.630 | 0.260 | 11.05 | 0.960 |
| zsRE | Stable v0 | 0.1041% | 1.716 | 0.179 | 27.68 | 0.186 |
| zsRE | Random reader | 0.0266% | 1.806 | 0.048 | 7.00 | 0.524 |
| CounterFact | Learned v5 | 0.2984% | 1.913 | 0.571 | 15.38 | 0.678 |
| CounterFact | Stable v0 | 0% observed | undefined | 0 | 0 | 0 |
| CounterFact | Random reader | 2.0450% | 3.486 | 5.454 | 20.28 | 0.121 |

RET-GS is retained paraphrase generalization, not an immediate editing score. Stable v0's zero CounterFact harm accompanies zero paraphrase generalization; it is not evidence of a successful safe editor. The learned reader's lower maximum on zsRE also coexists with *higher* average ES99+ than stable v0. Different risk summaries answer different questions.

Group severity refers to a uniform choice of cell followed by a uniform position, conditional on harm. It is not an unweighted average of per-cell conditional means. The technical tables include 95% joint-window bootstrap intervals; realized subject populations, orders, and training seeds are reported separately. These intervals assume the window blocks are adequate, which is not established for neighboring text or shared documents.

## What fitting adds

We fit positive excesses Δ−u at u = 0.01, 0.1, 0.5, and 1 nat. Each fit needs at least 100 excesses in at least 30 distinct windows. Shape estimates below refer to the generalized Pareto, which coincides with the manuscript's one-sided α=1 family; they are not measurements of system state growth W(N).

- **Learned reader:** at u=0.01, per-cell shape estimates span 0.0435–0.0588 on zsRE and 0.0294–0.0978 on CounterFact. However, the fixed illustrative realization-0/order-100 cells have window-bootstrap shape intervals of approximately **−0.097 to 0.177** and **−0.009 to 0.187**, respectively. Both include zero. Across all fifteen cells per dataset, five-fold held-out-window predictive improvements over the exponential range from −0.00039 to +0.00026 nats per excess on zsRE and −0.00104 to +0.00276 on CounterFact. This supports an economical exponential approximation on the measured range; it is not a proof of an exponential asymptotic class or a formal equivalence test.
- **Stable v0, zsRE:** primary-threshold shapes span **0.433–1.029**, and generalized-Pareto predictions improve held-out log likelihood over the exponential by **0.149–0.594 nats per excess** in all fifteen cells. The illustrative cell's shape interval is **0.390–0.779**. This is a useful finite-range tail-shape distinction. It does not measure infinite variance. At u=1, thirteen of fifteen cells fall below the sample-size screen, limiting what can be said about the farthest tail.
- **Random reader, CounterFact:** negative fitted shapes occur in all fifteen cells, but ten cells' held-out comparisons fail because a fitted endpoint excludes at least one held-out observation. The remaining five comparisons improve by about 0.033 nats per excess. A negative fitted shape is therefore not a trustworthy guarantee about unseen extremes. The full diagnostics retain the support failures; they are not silently removed from the likelihood average.
- **Sparse/zero cases:** the random reader on zsRE, stable v0 on CounterFact, and every individual κ-pilot cell are below the agreed screen. Their empirical frequencies and severities remain reportable; headline shape estimates do not. In particular, pooling the pilot's few events across seeds cannot manufacture independent windows or establish a tail class.

There is no pooled-cell estimate with a falsely enlarged sample size. Every cell retains its coordinates. Identical window identities receive identical bootstrap multiplicities across paired conditions. Shape intervals are withheld if a bootstrap draw produces an invalid fit; empty-event resamples also cause severity intervals to be withheld. No ordinary token-iid significance tests are reported.

## The bound and the PC reader

For AW-B's ten exposed memories at 300 edits, the mixture leaves the frequency above 0.01 almost unchanged, while reducing conditional severity from **1.619 to 0.542 nats** on zsRE and **1.925 to 0.581 nats** on CounterFact. The paired window intervals for the severity differences are **−1.197 to −0.979** and **−1.456 to −1.251** nats. The mixture's generalized-Pareto optimizer reaches an endpoint pathology in every memory at this threshold. Those outputs are labelled invalid and have no published shape estimate. The separate mathematical one-nat ceiling remains valid at the shared prefix. See the [AW-B report](AW-B_report.md) for retention changes and the original success rule.

For the **three completed paired PC reader seeds**, CounterFact ePC/BP firing counts are 185/256, 720/660 and 353/149, each on 245,237 positions. Combining the paired seeds, ePC-minus-BP harmful-change frequency above .01 nat is **+0.02134 percentage points**, with conditional window interval **+0.00569 to +0.03363**. Conditional severity differs by **−0.1066 nats**, interval **−0.3214 to +0.0840**. These fixed-reader window intervals exclude uncertainty over training seeds and subjects; a frequency interval excluding zero here does not establish a population-level training-rule effect.

On zsRE, ePC seeds 0 and 2 have no observed harmful events above .01; seed 1 has a few. The three-seed harmful-change frequency difference is **−0.005709 percentage points**, interval **−0.008019 to −0.003802**. Conditional severity is **0.6910 nats higher** among the remaining events; its interval is withheld because 2 of 200 joint-window draws have undefined severity. Lower frequency does not imply lower conditional severity, and these sparse events do not identify a tail family.

The [reader report](PC-reader_report.md) gives every seed's retention, firing, harm and costs. ePC paraphrase retention is lower on CounterFact in all three seeds (−24.17/−2.17/−17.50 percentage points); zsRE has −2.67/−2.00/+0.33. Own-prompt retention is nearly equal, with CounterFact seed 1 ePC 1.00 versus BP .99. The completed groups now contain the same three seeds; matched contrasts still check identities before calculation. No uniform quieter-reader or safer-learning interpretation follows.

The practical connection to the conference is now more precise: predictive-coding experiments test the learning rule; tail analysis asks how errors are distributed; active inference motivates a future controller that weighs the consequences of intervening. None of these fits demonstrate an expected-free-energy policy or a coupled-entropy training objective.

## Figures, validation, and the remaining handoff

- [Frequency versus conditional severity — PDF](../../../assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/frequency_severity.pdf), with separate Stage-4, AW-B, and reader panels.
- [Survival and threshold sensitivity — PDF](../../../assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.pdf), using the outcome-independent illustrative choice realization 0/order 100. Every other cell remains in the tables. PNG and SVG versions accompany both PDFs.

The implementation is in `aw/tail_class.py`, `aw/tail_class_sources.py`, `aw/tail_class_report.py`, and `aw/tail_class_plot.py`. It reuses the receipt-filtered Stage-4 collector and fractional expected-shortfall function. The supplemental adapters admit completed reports and costs, check coordinate/population identities, and hash the vectors they read. They never load a model. Invalid support, nonconvergence, insufficient data, and the manuscript-domain exclusion are distinct outputs. A conditional-lognormal diagnostic is tried if both primary models fail the declared exploratory predictive-fit check; no entropy column or free-α sweep is included.

**Validation:** 21 targeted tests pass, including known-distribution parameter recovery, likelihood agreement with SciPy, conditional-density normalization, signed/strict-threshold bookkeeping, hash tampering, whole-window held-out scoring, support failures, and duplicate-cell bootstrap invariance. Ruff passes. The nine-cell profile took 30.84 seconds including input admission, peaking at 352.6 MiB host RSS; the first complete pass took 89.23 seconds and 358.1 MiB. Final pass resources are recorded in its JSON. Zero GPU seconds are charged.

To reproduce the completed snapshot, run the same CPU command into a **new output directory**:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ../venv/bin/python -m aw.tail_class \
  --output logs/additional_work/HT-17/reader-complete-NEW --bootstrap 200 --secondary

MPLCONFIGDIR=/home/derp/cap/assets/presentation-materials/.matplotlib \
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m aw.tail_class_plot \
  --report logs/additional_work/HT-17/reader-complete-NEW/report.json \
  --out /home/derp/cap/assets/presentation-materials/figures/tails_ht17/reader-complete-NEW
```

`NEW` denotes a fresh snapshot name. The October 4 CPU refresh took 89.93 seconds; no GPU or model call was used. The reader, presentation and receipt-check refreshes now use this complete snapshot. October 9 remains the experimental freeze review; no extra fits or entropy-class claims are introduced. The known-distribution CAL-1 checks and POST-1 collaboration proposal remain separate from these measured tails.
