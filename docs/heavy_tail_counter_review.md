# Counter-review of the heavy-tail pivot, and the plan to October 9

Orchestrator (Claude), 2026-09-15, for Charlie Derr. This answers Codex's memo
[heavy_tail_suggested_slight_pivot.md](heavy_tail_suggested_slight_pivot.md) against the presentation target: the
CSS2026 satellite *Thriving in the Extremes: Active Inference in Non-equilibrium Systems* (Binghamton and online,
October 15, 2026; co-chairs Kenric Nelson and André Vilela; technical committee Karl Friston, Ugur Tirnakli, Johan
Medrano) and the July abstract *Coupled Active Inference on a Frozen Transformer Prior: A Risk-Aware Residual Agent for
Non-Equilibrium Regimes* (Derr and Iklé). Hard constraint: **no model-dependent experiment after October 9**; October
10–14 is analysis, figures and rehearsal.

The short version: I agree with Codex's recommendation and with almost all of its cautions. I disagree on two points
of emphasis, add one cheap experiment that gives the talk a real κ axis, and I have to put a feasibility problem in
front of you that no memo can wish away. Nothing already done loses value; every registered goal stays.

## 1. What the event and the abstract ask for, in our vocabulary

The event's two central questions are: how can cognitive agents survive and learn in extreme, non-equilibrium
environments; and how should the mathematics of active inference be generalized for heavy-tailed systems. The
abstract's claims, and what the programme already has for each:

| abstract claim | what exists (development evidence, GPT-2 small) | honest label on a slide |
| --- | --- | --- |
| a frozen generative prior with a much smaller adaptive residual agent | the JAX GPT-2 base (124 M parameters) is fixed; the reader is 3.35 M parameters (2.7 %); records carry per-answer-position **residual-stream deltas** at three sites under a fixed aggregate bound | implemented, small scale — say "residual writes", give the counts |
| learn only the residual R = F* − F0 as prediction error | every delta is taught by normalized adjoint steps on the answer's prediction error; nothing else touches the base | implemented as the support-target approximation of F*; say so |
| two Markov blankets (environment side, prior side) | environment side: the query interface with a learned "none applies" decision; prior side: write-free observations of the base and bounded, reversible writes; the write bound A and the null threshold are the two porosity knobs we actually have | proposed interpretation of two working interfaces; not a proof of conditional independence |
| a coupling κ that keeps precision finite on tail events | none in the loss or the selection rule today | hypothesis — §4 proposes the smallest honest test |
| risk-aware: refuse to act under low evidence; precision as risk sensitivity | the null head and the rare-token gate refuse edits on prompts about absent facts; rejection is measured on the unseen-prompt endpoint | implemented as a hard gate; not an expected-free-energy planner |
| the value of failing: learn where the prior fails | the development history is literally that: the ordinary-text drift (R1-54), the unseen-prompt false fires (R1-56) and the MQuAKE null instability were each found by an assay that looked where the system fails, and each fixed the boundary | true of the investigators, not yet of an agent choosing costly audits |
| forgetting as an auditable geometric invariant | v0 §7 order-reversal damage measurements; revision v1 has state hashes, supersession and isolated restores | operational interference evidence; no holonomy claim |
| heavy-tailed residual errors in the extremes | one saved development profile: 16,256 ordinary-text positions after 300 zsRE edits, mean harm +0.0002 nats, one position at +3.79 nats carrying 99.4 % of all positive harm (§3) | a measured concentration; not a power law |

The last row is the one that makes the pivot worthwhile, and Codex found it. Our own drift assay already stores
per-position losses, so "average versus tail" can be reported from data we have.

## 2. Where I agree with Codex, and where I do not

Agreed, and adopted as written: keep the frozen-base cap experiments as the main contribution; report rare harm
next to average performance; define "extreme" on separate axes (difficult input, rare harmful consequence, temporal
concentration, memory pressure, boundary failure); never fit a line to a log–log plot and call it a power law; keep
the reader-selection criterion fixed and do not let tail diagnostics become a hidden selection rule; freeze bins on
development data; report numerators, denominators and the atom at zero; treat window positions as dependent; and do
not build a majority-vote simulator or an expected-free-energy planner before October 9.

Two disagreements of emphasis:

1. **Codex treats a κ experiment as conditional on a written objective by September 20 and warns against a
   "renamed loss".** I agree a full coupled-free-energy construction is out of reach. But a loss-level coupling is
   not a renamed loss: replacing the logarithm in our two categorical terms with the coupled logarithm is exactly
   the construction Nelson's coupled entropy uses for the surprisal, it has a clean κ → 0 limit that recovers the
   current objective, and it changes precisely the behaviour the abstract talks about (how much a very improbable
   observation is allowed to move the agent). §4 specifies it. It is cheap, it is honest, and it gives the talk an
   actual κ axis with matched controls instead of a diagram.
2. **Codex proposes a 4-GPU-hour stress panel of clustered versus shuffled schedules.** I agree with the design but
   would run it only after the confirmatory blocks are safe (§5), because the schedule is the binding constraint,
   and I would shrink it to one reader candidate (the selected primary), two schedules, three datasets: six cells.

One addition Codex did not make: the reader's own history should be on a slide. Three boundary failures were found
by looking at the extremes, and each was a discrete change to where the boundary sits. That is the abstract's
"value of failing" told with numbers we have.

## 3. Priority 1 — the distributional audit (CPU; Codex; this week)

Verified from the saved checkpoint (`results/R1/stage4_dev_cells/R1_learned_ff-zsre-development_profile-*/attempt-0000/checkpoint-300.json`,
recomputed by me from `endpoints.drift.rows`, no model execution): 16,256 positions; mean signed Δ +0.000233 nats;
maximum +3.79 nats at one position (cap 15.26 vs base 11.47); positions with Δ > 0.01: 1; empirical worst-5 % mean
harm (ES95) 0.0047 nats; the worst 1 % of positions carry 99.4 % of all positive harm. Codex's numbers reproduce.

What the audit adds, for every population we already have per-item or per-position records for (drift rows from
the driver runs; per-item retention rows; unseen-prompt rows; the near-miss and revision rows): mean signed harm,
mean positive harm, median, 95th and 99th percentiles, ES95, maximum, exceedance counts at pre-declared thresholds
(0.01, 0.1, 1 nat), the share of positive harm in the worst 1 %, the atom at zero, and the counts of windows and
items. Per reader condition and per dataset, paired on identical windows and items where the runs share them. A
missing-data inventory for the aggregate-only historical assays. This is Codex's `scripts/ht_audit_existing.py` and
`logs/heavy_tail/`; I add one requirement: the audit must also run on the final selected reader's development cells
before any freeze, so that "average versus tail" is a pre-registered secondary outcome of Stage 4, not an afterthought.

## 4. Priority 2 — a loss-level κ pilot (the smallest honest test of the abstract's conjecture)

**Objective.** Our reader is trained with two categorical terms (answer cross-entropy on the taught targets;
retrieval/null cross-entropy) and one divergence term (preservation KL to the cap-off distribution). Replace the
logarithm in the answer term and in the preservation term by the coupled logarithm

    ln_κ(p) = (p^κ − 1) / κ,   κ > 0;   ln_0(p) = ln p,

so the answer loss becomes the coupled surprisal −ln_κ p(target) and the preservation term the coupled divergence
Σ p_off (ln_κ p_off − ln_κ p_on). For κ > 0 the surprisal of a very improbable observation is bounded above by 1/κ:
extreme prediction errors move the agent by a bounded amount instead of an unbounded one. This is the sense in which
the abstract says the coupling "keeps precision finite on tail events". The retrieval/null term keeps its ordinary
logarithm, so the boundary decision is not changed by κ; only how hard the agent learns from surprising targets is.
Reference for the construction: Nelson and Umarov (2010), Nelson (2023/2024) as cited in the abstract; the exact
paper version and the convention above are pinned in the manifest before the first run.

**Design.** κ ∈ {0, 0.2, 0.5}; three training seeds; everything else identical to the selected primary reader
(pools, episodes, nulls, gate, threshold, steps, optimizer, populations). Outcomes: the standard stream metrics on the
three development streams, the unseen-prompt endpoint at 100 records, and the §3 tail statistics of the drift rows and
of per-item preservation harm. Comparator: κ = 0 is the current objective; a clipped-surprisal control
(min(−ln p, c)) at matched c runs alongside so a gain is not attributed to the coupled form merely for being robust.
Cost: 9 + 3 trainings ≈ 1.5 GPU hours plus ≈ 1 hour of evaluation. Decision rule, fixed now: κ enters the Stage 4
protocol as a declared secondary condition only if, on development streams, it does not lower mean RET-GS by more than
0.02 or raise unseen false fires, and it changes at least one pre-registered tail statistic by more than its
seed spread. Otherwise it is reported as a null result on the slide — which is still a κ result.

**What it is not.** It is not the coupled free energy of Nelson et al. (no coupled expectation, no changed
inference distribution), not a coupled Markov blanket, and not a test of the one-κ conjecture that porosity and
interference are the same parameter. It is the first controlled measurement of what a loss-level coupling does on
this substrate, which is the honest thing to bring to a session chaired by the people who defined κ.

## 5. The feasibility problem you have to decide

Measured (clean profile, 15 September): a learned 1,000-edit cell with every endpoint costs 49–66 minutes as the driver
stands, about two thirds of it driver overhead. The registered matrix is 360 cells at 1,000 edits (DEC-044 keeps the
full scope). From September 21 to October 8 there are ≈ 408 wall-clock hours; at 75 % usable GPU time ≈ 306 hours. The
matrix therefore needs ≤ 42 minutes per cell with reserve, before the control conditions (unprofiled through the
driver), the κ pilot and the stress panel are charged. The R1-68b driver rewrite may bring the learned cell to
20–30 minutes; that is an estimate, not a measurement, and the trainer's memory failure cost two days of GPU work
this week.

I will not silently cut the scope, and I will not present a partial matrix as complete. What I will do, and what I
need you to confirm by **September 20**:

1. **Block order.** Cells run in blocks that keep every interruption interpretable: for each dataset, the primary
   reader (v3 or its successor), the random-reader control and the v0-stable control on realization 0 across all
   five orders first; then matched-update and the two v0 live conditions; then realizations 1 and 2; then the two S1
   continuation conditions; then the 45-cell no-gate extension. Whatever the October 9 stop leaves complete is a
   coherent subset with its own analysis; the incomplete cells are listed by identity.
2. **The κ pilot and the stress panel run before realization 2**, not after everything, because they are what the
   talk is about; each has its own hard ceiling (κ pilot 3 GPU hours, stress panel 4 GPU hours) and stops at it.
3. **If the September 20 timing check (driver re-profiled, controls profiled) shows the full matrix cannot fit**, you
   choose between (a) a documented scope amendment (fewer update orders is the least damaging cut: three of five
   keeps every condition, dataset and realization), (b) more execution capacity, or (c) the block order above with an
   accepted incomplete matrix. I will bring the measured numbers, not a proposal to cut.

## 6. What stays exactly as it is

Every registered goal and every artifact stands: the v0 negative result and its report; the revision-v1 primary
condition and its controls; the three-dataset run matrix at 1,000 edits with the 100/300/1,000 checkpoints; the
endpoints (retention, locality, unseen prompt, near-miss, revision, composition, drift); the exclusion register and
DEC-048; the freeze as your act; the pre-registered contrasts and margins; Codex's rounds of audit and review. The
heavy-tail work is additive: two new secondary outcome families (tail statistics; κ), one small stress panel, and a
talk narrative. No new architecture, no planner, no simulator before October 15.

## 7. Calendar (experiments end October 9)

| dates | gate |
| --- | --- |
| Sep 15–17 | trainer memory fix validated on a short guarded run (your go-ahead needed); Codex: distributional audit of stored results (P1); κ objective pinned in a manifest; common-population selection of the primary reader |
| Sep 18–20 | driver re-profiled (R1-68b); controls profiled through the driver; register v5 clearance and draw plan; **your feasibility decision (§5.3)**; κ pilot go/no-go on its manifest |
| Sep 21–Oct 3 | confirmatory blocks in the §5.1 order; κ pilot and stress panel inserted before realization 2; running spend table |
| Oct 4–7 | complete inventory, replications, predefined diagnostics; no new treatments |
| Oct 8–9 | reruns of failed cells only; **hard stop** |
| Oct 10–14 | locked data: analysis, figures, limitations, slides, rehearsal |
| Oct 15 | the talk |

## 8. What to show on October 15 (a proposed shape)

Opening (Codex's wording is good): a small adaptive memory on a frozen transformer as a controlled substrate for the
coupled active-inference programme; what it preserves, where it intervenes wrongly, and why the average is not enough
to judge that boundary. Then: (1) the two-interface diagram with implemented and proposed parts labelled and the
parameter counts; (2) retention versus unintended intervention on common populations, with the controls; (3) mean
versus local harm — the one-position tail, then the audit across conditions; (4) the boundary's history: three
failures found in the extremes and what each changed; (5) the κ panel, positive or null, with its matched control;
(6) the recovery curve if the stress panel completed; (7) the confirmatory matrix as far as it got, with the
incomplete cells named; (8) the question for the room: can a correctly specified coupled objective improve the
correction-versus-tail-harm trade-off under correlated regime change beyond ordinary robust losses and better
rejection training — and what the expected-free-energy audit policy would need to be to test the "value of failing"
as an agent's choice rather than an investigator's.

## 9. Immediate actions

- Orchestrator: this document; the κ objective as a manifest and a `--kappa` option in the trainer (CPU-tested);
  the guarded validation run of the memory fix when you allow the GPU; the common-population selection; R1-68b
  review when it lands. No GPU job before your word.
- Codex (round 15 lanes, posted with this document): `scripts/ht_audit_existing.py` over all stored per-item and
  per-position results with hashes and a missing-data inventory; the stress-panel contract and manifest
  (`docs/tasks/HT-evaluation-contract.md`, `manifests/revision_v1/ht_development_panel_v1.json`, six cells); the
  clipped-surprisal comparator and κ unit tests on TinyBase; a claim–evidence ledger for the talk
  (`docs/talk_claim_ledger.md`) that every slide statement must trace to a file.
- You: the September 20 decisions (§5.3, κ go/no-go), the GPU go-ahead for the guarded validation run, and whether
  Matthew wants to review the κ definition before it is pinned.
