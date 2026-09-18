# R1-58l — four-donor audit and sampled-rate transfer sensitivity

2026-09-18, Codex. **Partial cost lane, not typed cost v4 or launch admission.**
All four chain-S donors now pass independent receipt, full-vector, overlap and
GNU-command identity checks. Exact immutable bindings:
`logs/r1_round35/chain-s-inventory.json`.

| Development donor (max checkpoint 300) | Full outer seconds | Both sampled checks, seconds | Whole process seconds | Process minus attempt, seconds |
|---|---:|---:|---:|---:|
| Learned MQuAKE | 1,298.987703 | 138.931263 | 1,868.48 | 3.873808 |
| v0 MQuAKE | 1,309.054414 | 170.822729 | 2,962.96 | 2.355279 |
| Learned zsRE | 1,392.939466 | 144.876700 | 1,868.69 | 3.772364 |
| v0 zsRE | 1,310.442814 | 177.750115 | 2,529.40 | 2.325075 |

Full outer time already includes the full assay's integrity wrapper. The sampled
phases are separate work at both checkpoints. Whole-process minus attempt is a
measured envelope difference, not a measurement of every production startup
path or failed attempt. The inventory's historic `remaining` list is a static
template: its four-donor item is resolved by `completed: 4`; the other cost work
listed there remains. No failed benchmark was discarded as invalid cost data.

`scripts/r1_58l_transfer_basis.py` extracts and binds the historical single sampled
phase for **all 27 condition/dataset rows**, including legacy phase records and
verified batched journals. The current result is
`logs/r1_round35/transfer-basis-v2.json`; the earlier `transfer-basis.json` is a
pre-format provenance snapshot, superseded by v2. It is not the requested
receipt/ceiling file. Reproduce into a new log path:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_58l_transfer_basis \
  --inventory logs/r1_round35/chain-s-inventory.json \
  --output logs/r1_round35/transfer-basis-next.json
```

The sensitivity uses measured sampled seconds per scored position, relative to
the selected full donor's sampled rate. Learned-family rows use learned donors;
other rows use v0 donors. Same-dataset donors are used for zsRE/MQuAKE; for
CounterFact the larger full cost among the two eligible datasets is selected.
This is an explicit **unreviewed family/implementation transfer**, not a claim
that all conditions cost the same or that this is a validated upper bound.

For every row the arithmetic is:

```text
full estimate = measured full outer donor seconds
              × (historical sample seconds/position ÷ donor sample seconds/position)
new solo scenario = old v1 solo estimate − its one historical sampled phase
                  + all 2 or 3 planned sampled phases + full estimate
solo ceiling scenario = new solo scenario × 1.5
two-worker ceiling scenario = solo ceiling scenario × 1.15
```

This exposes the old single-sample replacement instead of adding full and
sampled costs twice. The inherited nonvalidation remainder remains a coarse
old-plan estimate; it has **not** been independently remeasured or corrected for
all missing endpoints, startup and 1,000-record state. Negative remainders,
wrong phase cadence, incomplete sampled populations, missing phases, changed
bindings and inconsistent phase/result timers fail instead of becoming zero.

| Unadmitted sensitivity | Core: 360 cells | Optional extension: 45 cells | Combined |
|---|---:|---:|---:|
| Solo process-hours | 385.4425 | 35.1673 | 420.6098 |
| With 1.15 two-worker adjustment | 443.2589 | 40.4424 | 483.7013 |
| With 1.5 solo margin and 1.15 adjustment | 664.8883 | 60.6637 | 725.5519 |

These totals are **sensitivity calculations, not admitted budgets or calendar
forecasts**. The 750-process-hour cap is retained, and failures/retries consume
additional measured process time. The combined margin scenario leaves about
24.45 process-hours below that cap before any corrections; this is insufficient
evidence to declare the schedule safe. Optional extension remains optional and
requires its original admission. October 9 remains the experimental deadline.

The largest transfer warning is learned CounterFact: its historical sampled
phase is **378.6867 s for 16,256 predictions**, versus **72.4384 s** per sampled
checkpoint in the learned zsRE full donor. Blind rate transfer gives **5.228×**
and **7,281.88 s** for full validation. Their execution/integrity profiles differ.
This is a useful signal to measure or explicitly reconcile the current
CounterFact path; it is not evidence that the current full assay will actually
take two hours. Matching the small execution-profile dictionary for another row
does not establish code/base/reference equivalence either.

S1's sampled-rate ratio can already contain work from a distinct original-base
reference. An additional assumed 3/2 multiplier without decomposing those
operations could count that work twice. Its actual full assay cost with the separate
original-base forward remains unmeasured; the model compares cap against two references, with
three forward paths where they differ. Four profiles ending at 300 do not
measure 1,000-record occupancy or memory. Host peaks retain direct GNU-time versus
sampled temporal-attribution qualifications; they cannot silently be copied
across conditions or replace device allocator peaks.

Remaining work is explicit: reviewed transfer/occupancy/reference evidence,
updated 27-row endpoint/host inventory, startup/failure accounting, typed v4
validator and receipt, final ceilings v2 and revised schedule, operator's bound
ceiling integration, then candidate v14/forms v9/X19. HT-4f waits for actual signed
receipt v4. **These are not all signature gaps.** No missing approval was filled
in and no generated scenario was placed into production manifests.

Tests: 13 cost-basis tests in the combined **52-pass** CPU suite
`logs/r1_round35/focused-tests-v2.txt`; successful real four-donor/all27 extraction;
Ruff passes. Fixtures are in assets. GPU/model calls: zero. Done-when for the
full R1-58l lane is not reached; this document records the newly completed basis.
