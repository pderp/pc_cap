# Final experiments — joint decision form for Tuesday, September 29

Prepared 2026-09-27 by Capex from the reviewer primer §5. **No candidate is
selected, ranked or authorized by this form.** charlie, the human reviewers,
Capex and Capstan fill it together after the completed paired PC reports exist.
Canonical repository copy: `pc_cap/docs/presentation/final-experiments.md`;
identical initial export: `assets/presentation-materials/review-data/final-experiments.md`.
Paths beginning `pc_cap/` or `assets/` are relative to `/home/derp/cap/`.

The presentation connects **active inference, predictive coding and heavy-tailed
distributions**. The current testbed does not implement autonomous expected-free-energy
policy selection, coupled free energy or demonstrated Markov blankets; another
retention/tail result alone would not establish those claims.

## Evidence available at the meeting

| Required input | Result / interpretation to fill | Source |
| --- | --- | --- |
| Corrected PC-v0, all 60 cells and three realization summaries | PENDING | `pc_cap/logs/additional_work/PC-v0/report-60-20260927/report.json` (configured future path) |
| Matched PC-v0 ordinary-text harm and separate cost | PENDING | `pc_cap/results/additional_work/PC-v0/harm/replication-60-20260927/report.json` and sibling `cost.json` (configured future paths) |
| Fixed-v5 credit, all four cells at 100/300 edits | PENDING | `pc_cap/results/additional_work/PC-v1/replication-4-20260927/` (configured future directory) |
| Fixed-v5 final harm and separate cost | PENDING | `pc_cap/results/additional_work/PC-v1/harm/replication-4-20260927/` (configured future directory) |
| Reviewer comments and proposed scientific question | ____________________ | Attach written feedback / meeting notes |
| Actual GPU release and remaining usable wall-hours | ____________________ | Capstan's latest completion/cost records; do not add overlapping process-hours |

The paired effects, preservation, failures and cost jointly inform the entries
below. “Works” is a discussion label to define here, not a new automatic success
threshold or a label inferred from whether a job completed.

**Definition used for “works / transfers,” with the observed trade-offs:**
________________________________________________________________________

## Conditional branches from the primer

| Evidence branch | Candidates named in §5 | Branch selected at meeting |
| --- | --- | --- |
| PC-v0 useful and fixed-v5 transfer useful | A: PC-trained reader | ____________________ |
| PC-v0 useful, fixed-v5 transfer not useful | B: fixed-v5 credit settings; A: PC-trained reader | ____________________ |
| PC-v0 not useful | C: v0 settling-depth study; D: bounded correction/gating | ____________________ |
| Any PC disposition; investigate unintended extremes | D: bounded correction/gating | ____________________ |
| Further population replication is the question | E: one untouched realization of the triplet | ____________________ |
| The upper-layer interface hypothesis is the question | F: read/write interface factorial | ____________________ |
| Memory-size growth is the question | G: 3,000-edit stream | ____________________ |

These branches preserve the primer's possibilities without choosing among them.
A negative v0 result does not cancel the already planned fixed-v5 comparison.
The main studies' original outcomes stay in their own reports even if a tuned
variant later performs differently.

## A. Train the reader with predictive-coding credit

- **Question:** Does training the reader itself with the corrected ePC surrogate
  change retention, unintended loss and computational cost relative to BP?
- **Design:** Three paired training seeds per method, same reader architecture,
  training/development data, budget and checkpoint rule; evaluate 300-edit streams
  with behavior and matched ordinary-text harm. This changes reader training,
  unlike the fixed-reader acquisition-credit comparison already running.
- **Population/exposure:** Existing training and development pools; supplemental
  evaluation on exposed streams unless the joint review explicitly assigns a
  different population. Exact recipes, seeds and evaluation coordinates: **TO FILL**.
- **Cost:** **30–40 GPU wall-hours, planning estimate** from primer §5 and
  `pc_cap/docs/plan_from_saturday.md`; no delivered profile of this full training
  experiment supports a measured runtime. Include cache preparation, six trainings,
  acquisition, endpoints, full harm and failed attempts in a development profile.
- **Adds to:** Directly predictive coding; gives the active-inference programme a
  tested learning component; distributional readouts address extreme consequences.
  Does not itself implement action selection or coupled free energy.
- **Ready when:** Corrected training surrogate and the BP comparison have executable
  local JAX recipes, appropriate algorithm tests and a costed development pilot;
  acquisition-driver readiness alone is insufficient.
- **Feedback deadline:** Joint choice Tuesday September 29; detailed design before
  its profile/launch. Apply October 1's planning checkpoint if the measured work
  grows beyond three GPU-days; no new fits after the October 6 line.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## B. Fixed-v5 solver settings

- **Question:** Does settling depth or error learning rate explain a fixed-v5
  credit-transfer limitation?
- **Design:** Adjoint control versus SE-E at declared combinations of 8, 16 or
  32 iterations and positive error learning rates; use the same frozen base,
  selected reader, gates, budgets and freshly acquired memory in each cell.
  Grid and any development-only selection rule: **TO FILL** before comparing variants.
- **Population/exposure:** Development for profiling/selection; the same four
  exposed evaluation cells, zsRE/CounterFact realization 0, order 100, 300 edits,
  with 100/300 behavior and final matched full-validation harm. One realization
  and one order do not supply a population-level replication interval.
- **Cost:** Primer branch **8–40 wall-hours**, an estimate covering alternatives,
  not a measured cost of a particular grid. Fixed-v5 development-profile cost:
  **PENDING** at preparation; use its actual four-cell profile and a selected-setting
  profile before launch. V0 ten-item timings cannot substitute for it.
- **Adds to:** Predictive-coding mechanism sensitivity; whether any change in
  efficacy has a corresponding tail-loss or cost penalty. No evidence of PC
  training of the reader follows from this experiment.
- **Ready when:** PC-9/PC-10 copies are applied at the safe boundary after existing
  source-bound reports finish; selected settings pass a matching development
  profile and snapshots restore with their recorded treatment.
- **Feedback deadline:** Tuesday September 29 for grid/population; exact recipe
  before profiling and launch, with the same October 1 / October 6 schedule limits.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## C. V0 settling depth

- **Question:** Is an unfavorable eight-step result explained by insufficient
  settling, and how does additional settling change useful editing, harm and cost?
- **Design:** Primer proposes 8 versus 32 steps; 16 is also admitted by the
  prepared driver. Exact grid, error rate, datasets, realizations and orders:
  **TO FILL**, with paired adjoint controls and fresh memory.
- **Population/exposure:** Historical S5 streams are exposed. The primer's proposal
  to revisit only failed cells would be **outcome-selected exploratory evidence**;
  if used, preserve that label and the original full result. A full preselected
  paired design or development-only setting selection answers a different question;
  record the chosen estimand and selection rule here before launching.
- **Cost:** Primer **8–15 GPU wall-hours**, a planning estimate without a fixed
  revised cell count. The delivered ten-item v0 development profile took about
  476 process seconds for four cells; PC-9 estimates **1,499.84 process seconds**
  for three four-cell development variants at rate 0.1, including repeated controls.
  That estimate is **not** a full-stream GPU cost or a bound: full-stream query
  cadence, memory size, compilation and harm need separate allowance.
- **Cost sources:** `pc_cap/results/additional_work/PC-v0/dev-profile-20260927/`;
  `pc_cap/logs/additional_work/round50/pc9-development-cost.json` and
  `pc_cap/docs/tasks/PC-9.md`. Do not add the alternative fixed/scaled-query
  scenarios as if they were sequential jobs.
- **Adds to:** A direct predictive-coding solver question with efficacy/tail/cost
  consequences; neither more iterations nor a changed rate guarantees convergence.
- **Ready when:** Variant readers are integrated, scientific scope is specified
  and the actual selected-setting profile fits the remaining wall allowance.
- **Feedback deadline:** Tuesday September 29 for the selection rule and scope;
  before launch for settings and budget, preserving October 9's hard stop.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## D. Bounded correction and stricter gating

- **Question:** Can query-time bounds reduce extreme loss while retaining useful
  corrections, and does shaping corrections add anything beyond weakening them?
- **Design:** `pc_cap/docs/additional_work/AW-B.md`: clip the full-vocabulary
  log-ratio at b ∈ {0.5, 1, 2, 4}; compare matched base mixtures, global shrinkage,
  and three stricter null thresholds with unwrapped v5 and cap-off. The clip and
  matched-mixture constructions have a **2b-nat per-token bound versus their
  specified base**. Calibrate on development, selecting at most one bound and
  one shrink/gate comparator by the existing rule before evaluation.
- **Population/exposure:** Exposed development memories for calibration; exposed
  realization-0 zsRE/CounterFact streams, five orders each, efficacy at 300 edits;
  fixed 245,237-position ordinary-text validation. Keep original and own-cap-off
  references distinct. Any optional MQuAKE expansion needs its own decision.
- **Cost:** Primer **12–24 GPU wall-hours**, estimate; AW-B specifies a **24-hour
  ceiling**, not a measured duration. Profile one development stream and include
  reconstruction, vocabulary scoring, generations, all endpoints and retries.
- **Adds to:** Heavy-tail motivation through measured extreme-loss control;
  bounded behavior for the active-inference testbed, without claiming a preference
  model, a proven heavy-tail family or autonomous policy choice.
- **Ready when:** Lead reviews the existing AW-B draft and development profile;
  bounds and controls pass their numerical checks, and selected arms are fixed
  without looking at the exposed evaluation outcomes.
- **Feedback deadline:** Tuesday September 29 discussion; parameter/selection-rule
  feedback before calibration, reviewed arms before evaluation.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## E. One untouched realization of the primary triplet

- **Question:** Do the package-level retention and preservation differences recur
  in another reserved population?
- **Design:** `pc_cap/docs/additional_work/R.md`: realization 3, learned v5,
  random reader and stable v0, zsRE/CounterFact, five orders, 1,000 edits, 30 cells;
  preserve checkpoints, scoring and full-validation fidelity. No reader retraining.
- **Population/exposure:** Additional subjects reserved under DEC-073, disjoint
  from earlier realizations and development/selection identities, subject to the
  existing allocation and endpoint checks. The artifact has already been selected;
  this is an additional untouched-population replication, not a new frozen primary
  family or a fresh test of interventions tuned on the first three realizations.
- **Cost:** Primer **24–30 GPU wall-hours**, estimate; Option R's **30-hour ceiling**
  and memory/worker policy remain distinct from observed per-cell process costs.
  Recalculate from current condition profiles before dispatch.
- **Adds to:** Replication of the active-inference testbed's correction/preservation
  findings and their uncertainty; these feedforward conditions add no PC treatment.
- **Ready when:** Allocation/payload checks remain valid, the existing supplemental
  design is reviewed, and acquisition plus validation fits. Earlier portfolio
  sequencing is not silently changed by this form; record any approved change.
- **Feedback deadline:** Tuesday September 29 for population/scope, before any
  reserved data use or launch; apply October 1's large-job checkpoint if needed.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## F. Upper-layer read/write interfaces

- **Question:** Does reading upper taps and restricting writes preserve useful
  correction while changing cost or unintended loss? Lower layers are not assumed
  to be noise.
- **Design:** `pc_cap/docs/additional_work/AW-L.md`: read {1,2,3}/{2,3} × write
  {1,2,3}/{3}, three paired training seeds, **six trained readers and 24 evaluations**.
  Keep the full-write training objective; share reader weights across write arms,
  reacquire memories and rebuild keys. Preserve total write budget and endpoint rules.
- **Population/exposure:** Exposed development for preparation; first 300 edits of
  realization 0, order 100, zsRE/CounterFact for post hoc evaluation. Three training
  seeds are not three independent subject realizations.
- **Cost:** Primer **24–30 GPU wall-hours**, planning estimate; AW-L's **48-hour
  ceiling** is an upper stop allowance. Profile both read sets/write masks and
  include all six trainings, 24 evaluations, full harm and retries.
- **Adds to:** The interface hypothesis in the active-inference architecture and
  empirical tail/efficacy trade-offs; the proposed training remains BP-based, so
  this experiment by itself adds no PC learning result.
- **Ready when:** L4 binds the exact training recipe and validates tap-shape
  plumbing, and the lead reviews the population, masks, profile and retained scope.
- **Feedback deadline:** Tuesday September 29 discussion; training recipe and mask
  decisions before fitting, with no new fits after October 6.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## G. Memory-size growth to 3,000 edits

- **Question:** How do retained corrections and the distribution of unintended
  loss change as a memory grows beyond the currently evaluated stream lengths?
- **Design:** One realization and 3,000 edits; dataset, artifact, controls, order
  count and checkpoint cadence **TO FILL** before constructing a stream. Preserve
  behavior and matched-position tail readouts at the chosen checkpoints, and
  report occupancy/capacity and failed edits rather than extending silently.
- **Population/exposure:** **UNRESOLVED** pending a population and endpoint-reservation
  check. Record whether the added subjects are exposed, reserved or newly sourced;
  do not assume availability from the existing 1,000-edit allocation or consume
  Option R's reserved subjects without a portfolio decision.
- **Cost:** Primer **12–15 GPU wall-hours**, unprofiled estimate for an incompletely
  specified scope. Growing memory and repeated endpoint costs require a new profile;
  there is no delivered 3,000-edit cost measurement or approved ceiling here.
- **Adds to:** Empirical memory-size dependence of correction and extreme loss;
  no heavy-tail asymptotics or active-inference policy result is implied.
- **Ready when:** Population allocation, capacity behavior, baseline, checkpoints,
  cost allowance and explicit exposure label have been reviewed.
- **Feedback deadline:** Tuesday September 29 for the question/scope; population
  decision before data use and a complete design before launch.

**Decision / owner / start:** ____________________ / ____________________ / ____________________

## Calendar, cost and feedback fields for the joint decision

Dates refer to **2026, America/New_York**. Tuesday is **September 29**;
**October 1 is Thursday** and **October 6 is Tuesday**, correcting weekday labels
in the earlier primer without changing the dates. Lead-queue item 120 supplies
the October 1 checkpoint for work needing more than three GPU-days; item 121
lifted the earlier Monday hold on the current PC chain. Reviewer feedback does
not itself pause or cancel that authorized chain.

The working plan puts last new fits at the October 6 line and evaluation/figures
on October 7–8. The hard experimental deadline remains **October 9, 17:00 ET**;
October 10–14 is preparation and October 15 is the presentation. Confirm exact
latest-start times from measured jobs, including reporting and retry allowance.
The primer's “about 120 usable hours” is a planning estimate, not a live balance.

| Joint decision field | To fill |
| --- | --- |
| Actual free wall-hours after the current chain | ____________________ |
| Selected candidates, exact scopes and sequence | ____________________ |
| Costed profile(s), uncertainty and retry/report reserve | ____________________ |
| Latest safe start / stop for each selected experiment | ____________________ |
| Exact reviewer feedback cutoff for each selected design | ____________________ |
| Owner of code integration / GPU dispatch / report | ____________________ |
| Approval and date; changes from existing reviewed drafts | ____________________ |
| Interpretation if null, unfavorable, incomplete or unavailable | ____________________ |

Sources: reviewer primer §5; `pc_cap/docs/plan_from_saturday.md`;
`pc_cap/docs/lead_queue.md` items 120–124; AW-B/AW-L/R drafts; PC-9/PC-10 task
records; and `pc_cap/docs/talk_claim_ledger_v7.md`. Exact hashes are recorded in
`pc_cap/logs/additional_work/round51/rev3-sources.json`. None of these estimates
substitutes for a selected experiment's actual profile or changes its scientific scope.
