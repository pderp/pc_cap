# pc_cap — primer for the Friday 2 October 2026 review

Written 1 October 2026 by Capstan (the Claude orchestrator of this project) for two reviewers who know mathematics,
neural networks and active inference well but have not followed the project. It explains what was built, what was
measured, what is running on the GPU right now, and what remains before the talk on 15 October. Every number below is
copied from a project file named in the text; nothing here is new analysis. Paths are relative to `/home/derp/cap/`,
which holds two repositories: `pc_cap` (code, logs, documents) and `assets` (data, models, run outputs, figures,
presentation materials). The figures referenced as `figures/NN-*.png` are copies placed in this folder.

Reading order if you have twenty minutes: §1, §4, §5 and §8. The rest is reference.

> **Update, 2 October:** everything since Kenric Nelson's feedback (the tail analysis of record, the revised talk
> wording, two of three ePC reader seeds, Option R's resume, the calibration checks and the questions for the meeting)
> is in `UPDATE-2026-10-02.md` in this folder. Numbers in this primer that it supersedes: the ePC training cost (≈ 100×
> measured, not 37×) and §6.5's one-seed reading of the ePC reader.

---

## 1. The project in one page

**The question.** A pretrained transformer is a strong generative prior that fails in the extremes: rare inputs,
distribution shift, facts that change. The July abstract by Charlie Derr and Matthew Iklé (*Coupled Active Inference
on a Frozen Transformer Prior: A Risk-Aware Residual Agent for Non-Equilibrium Regimes*) proposes keeping the base
frozen and adding a small adaptive agent that learns only the residual, driven by prediction error, sitting between
two interfaces (one to the environment, one to the transformer), with a coupled (κ-deformed) objective meant to keep
precision finite on heavy-tailed errors. The talk on 15 October (Binghamton satellite of CCS 2026, *Thriving in the
Extremes: Active Inference in Non-equilibrium Systems*, session 3, 14:45–16:15; the lead's heading for our talk is
**Active Inference in the Extremes**) is organised around three themes: active inference, predictive coding,
heavy-tailed distributions.

**What was built in two months on one workstation GPU.** A "cap": a small module that reads the residual stream of a
frozen GPT-2 (124M parameters) at three sites and adds correction vectors at the same sites, storing one record per
factual edit. Two generations: the **v0 cap** (a radius-gated memory with writes taught by gradient steps) and the
**v1 learned reader** (a trained retrieval-and-null network, about 3.3M parameters, deciding which stored record
applies to a query, or that none does). The credit rule that teaches each stored correction can be the **adjoint**
(ordinary backpropagation to the site, "SE-A") or **predictive-coding error inference** (an energy relaxed over
per-layer error variables, the settled error at the site used as the direction, "SE-E"). Around this sits heavy
measurement machinery: pre-registered protocols, sealed populations, receipted queues, independent audits, and a
per-token readout of what every correction does to 245,237 positions of ordinary text.

**What was found.**

1. The learned reader keeps paraphrased edits far better than every control (mean paraphrase retention after 1,000
   edits 0.96 on zsRE, 0.68 on CounterFact; 0.72 on MQuAKE after 300), recurring in all three independent populations.
2. Every such cell fails the project's old fidelity benchmark (mean KL ≤ 0.001 nats on ordinary text). The harm is
   **rare and concentrated**: 0.16–0.31 % of ordinary-text positions change by more than 0.01 nats, half of all harm
   sits in 0.03–0.06 % of positions, and single tokens lose up to 17 nats. Means hide this. The older v0-family caps
   disturb fewer positions but their worst tokens lose 28–51 nats.
3. **Corrected predictive-coding credit works.** After fixing a defect in the energy (SD-24), eight-step error credit
   acquires and generalises exactly like adjoint on the v0 cap, retains own-prompt answers slightly better (+0.02),
   costs about 2.2× in learning compute, and does not reduce harm. Controls show this is a dose–response in the
   settling depth (1 step = adjoint exactly; 32 steps = +0.05 retention, +52 % harm, 5.4× cost), that random credit
   acquires nothing, and that adjoint cannot use extra compute. On the reader that works (v5), the credit rule and its
   settings change neither efficacy nor harm, only cost.
4. **Bounding the correction at query time** by mixing the cap's distribution with the base's (ρ = e⁻¹ of the base)
   caps every token's loss increase at 1 nat by construction, leaves every efficacy endpoint unchanged on zsRE and within
   0.012 on CounterFact, and cuts mean KL and the worst-1 % loss by 3.2–3.5× on all ten sealed streams. A loss-level
   κ-coupling pilot was null under its pre-registered rule: bounding surprisal lowers the tail but costs retention, and a
   plain clip does most of it.
5. **Training the reader itself with the predictive-coding surrogate** (running now; one of three seeds done) gives a
   quieter reader: identical own-prompt retention, lower paraphrase generalisation (0.95 vs 0.97 on zsRE, 0.57 vs 0.81
   on CounterFact), and zero firings on zsRE ordinary text. Training costs about 100× the backpropagation run
   (measured: 24.6 h against 14 min for seed 0; the earlier 37× was a profile projection).

**What the testbed does not do.** It does not implement expected-free-energy policy selection, the coupled free energy
of the abstract, precision as risk sensitivity, autonomous epistemic audits, or Markov blankets in the formal sense.
Section 8 maps each idea of the abstract to implemented / measured / proposed.

---

## 2. Timeline and where the project stands

| when | what |
|---|---|
| August–13 Sep | v0 study: cap design, ePC infrastructure on FabricPC, a 50M ePC-distilled base, frozen confirmatory protocol, 210 runs. Primary claim (a routing variant beats the fixed schedule by 0.02 paraphrase retention) **not supported**. SD-24 found and fixed 13 Sep. |
| 13–18 Sep | Revision v1: diagnosis of v0 (it stored usable values but read the wrong record), the learned reader, development on training pools, Stage-4 protocol frozen 18 Sep (DEC-071): 330 cells, 750 process-hour cap. |
| 18–26 Sep | Stage-4 confirmatory queue runs; halted by decision at 270 cells (DEC-074/074b) to free the GPU for predictive coding. Audits X22/X23/X24 pass. |
| 26–30 Sep | PC refocus: PC-v0 (60 cells), fixed-v5 credit (4 cells), three controls, credit settings, bounded correction (calibration + sealed evaluation), PC-trained reader (BP arm), Option R started and stalled. |
| 1 Oct (today) | ePC-trained reader seed 1 training (seed 0 done). |
| 2–4 Oct | ePC seeds 1–2 and their evaluations (to ≈ 3 Oct 10:30); then the upper-layer interface 2×2 (≈ 30 h, to ≈ 4 Oct evening). Option R continuation if its reconciliation allows. |
| 6 Oct | last new fits. 7–8 Oct: evaluation, reports, figures. |
| **9 Oct 17:00 EDT** | experimental freeze (the lead's act). 10–14 Oct: slides and rehearsal. |
| **15 Oct** | the talk. |

Two agents do the work under the lead: Capstan (this document's author; orchestration, GPU dispatch, decisions
record, lead-facing status) and Capex (a Codex instance; implementation lanes, reports, deck). The lead decides; every
decision is a numbered entry in `pc_cap/docs/decisions.md` (DEC-001 … DEC-079).

---

## 3. The testbed, mathematically

### 3.1 Base and interface

The base is GPT-2 small (12 blocks, d = 768, 124M parameters), a deterministic JAX re-implementation checked against
the PyTorch reference (max |Δlogit| ≤ 1e-3). It is frozen throughout: no base weight ever receives a gradient. Let
h_l(t) ∈ ℝ^d be the residual stream after block l at position t. The cap's three **sites** are the residual stream
after blocks 4, 8 and 12 (zero-indexed 3, 7, 11; the last site before the final layer norm). At each site m the cap may
**read** (the last-position residual and a mean over the prompt span, both 768-d) and **write**: h_m(t) ← h_m(t) + w_m
for the positions being corrected. Writes are bounded by one aggregate budget

  Σ_m ‖w_m‖ / b_m ≤ A,  A = 0.3,

where b_m are calibrated per-bank scales (typical residual norms at each site) and the projection is a single rescale
when the bound is exceeded. A zero write reproduces the base exactly, which is what every "cap-off" reference below
means.

For the v0 line the base is different: a **50M-parameter GPT-2-shaped model distilled from GPT-2 with an ePC
training procedure** (50M tokens, 12.2 GPU-hours, mean KL to the teacher 2.9e-5 nats/token), so that
predictive-coding credit could be tested on a base trained the same way. Sites are the same.

### 3.2 Memory and records

A record stores: a **key** (an embedding of the support prompt's observation, taken with writes disabled so that key
and query share one stable representation), a **payload** (the write vectors that produce the new answer), and
metadata. Records are append-only; a revision supersedes an older record without overwriting it. Retrieval is
deterministic. Memory bytes are counted against a ceiling.

In v0 the payload is a write per site taught by gradient steps; in v1 it is a **per-answer-position delta**: for each
token position of the answer, one [3 × d] write, taught at edit time by **five normalised adjoint steps** (learning rate
0.1 in bank-scale units, stop when the support loss falls below τ = 0.1, accepted only if the final loss is below the
initial loss, otherwise rolled back). This "delta rule" is the acquisition step; its direction is the **credit**.

### 3.3 The two credit rules

For a support example with target answer y, write vectors W = (w_1, w_2, w_3) and the loss L(W) = cross-entropy of the
base's next-token prediction under the writes, the update direction at site m is:

- **Adjoint (SE-A):** g_m = −∂L/∂h_m, the ordinary backpropagated gradient at the site, normalised, step of size
  lr · b_m.
- **Predictive-coding error (SE-E):** introduce one error tensor e_l ∈ ℝ^{T×d} per block, added to the block's output
  residual, and relax the energy

    E(e; x, y) = ½ Σ_{l=0}^{11} ‖e_l‖²_F + Σ_t CE(softmax f(x; e)_t, y_t)

  by k steps of plain gradient descent on the errors from zero, e ← e − η ∂E/∂e, η = 0.1, identity precision, no
  stopping rule (FabricPC graph; this is the "error-optimisation" form of predictive coding, the sibling repository's
  recipe re-implemented line by line). The settled error at site m is the direction: at a stationary point
  e_m = −∂CE/∂h_m, so e_m points from the feedforward state toward the target-conditioned state. The credit uses
  +e_m/‖e_m‖ with the same step size. Cost: an eight-step credit is nine forwards and nine reverses against one of each.

  Two facts fix the reading of every PC result. (i) **One step from zero gives e_m = −η ∂CE/∂h_m exactly**, so after
  normalisation one-step error credit *is* adjoint credit; whatever eight or thirty-two steps add is the content of
  the settling (the error at upper layers propagating through the energy's quadratic coupling across layers). (ii)
  The solver uses autodiff through the graph to compute ∂E/∂e; this is not a local or biologically plausible learning
  rule, and the project never claims it is.

- **SD-24.** In the first month's implementation the quadratic term at the cap sites was evaluated *after* the write
  was added instead of before, so the energy penalised the write itself. The only SE-E result from that period
  (acquisition −0.34 against adjoint) is therefore not a clean negative; every PC result below uses the corrected
  energy, and the pre-run check that would have caught the defect (one-step error = −0.1 × adjoint to 1e-8) is now
  part of the runner.

### 3.4 The v0 cap (first month)

Three **radius-gated banks** at the three sites. A query fires bank m when its observation key is within a
calibrated radius (set at 1 % false-fire rate on development text) of a stored key; the stored write is added. Routing
variants: C1 writes at all three banks every round with the aggregate bound divided among them; C2 chooses one bank
per round by the best positive probe; CR chooses randomly. The confirmatory question was C2 vs C1 on paraphrase
retention; it was not supported (C2 retained about three points *less* than C1 on zsRE). The diagnosis that led to v1:
v0 **stored** usable corrections (an oracle read gives 0.94 paraphrase success) but **read the wrong record** (live
C1/C2 paraphrase 0.24/0.29), because edited observations drift from the stored keys and because radius gating cannot
tell a paraphrase of a stored fact from a prompt about a neighbouring fact.

### 3.5 The v1 learned reader (the current study)

Pure JAX functions over a parameter tree, about 3.3M parameters:

- **Tap encoder** (siamese, shared between support and query): for each of the three taps, LayerNorm of the
  concatenated [last-position residual; prompt-span mean] (1,536-d) → dense → 256-d; summed over taps. Separate heads
  produce the query embedding q, the record key k and an initial fact code.
- **Scoring:** tied cosine between q̂ and the keys k̂ of the top-4 nearest records (scaled), plus one **null logit**
  composed of a query-only linear term, a pairwise term on [q̂, k̂*, q̂ ⊙ k̂*] for the best candidate, and a lexical
  overlap feature (IDF-weighted token overlap between query and record text, stop list applied). Softmax over the
  4 + 1 logits gives applicability weights and a **null mass**.
- **Decision:** once per query, from the prompt alone, held for every generated answer token. Null mass ≥ 0.5 → **hard
  null** → exactly zero writes → the output equals the base to the bit. Otherwise the best record's per-position deltas
  are written with mass 1. ("Firing" below means the non-null branch was taken.)
- **Training** (backpropagation, the "BP" rule): stream-scale episodes mirroring deployment, a 64-record memory mixed
  from zsRE and CounterFact training pools, eight queried records (own prompt → answer target; paraphrase → answer
  target; a locality near-neighbour prompt → null target), eight out-of-memory prompts (null) and eight **ordinary-text
  prefixes** from OpenWebText (null target plus a preservation KL to the cap-off logits; this last ingredient took the
  reader's firing rate on ordinary text from 37–49 % to 0 at the probe lengths). Loss = answer cross-entropy +
  class-balanced retrieval/null cross-entropy + preservation KL, unit weights. AdamW 1e-3, weight decay 0.01, gradient
  clip 1.0, 300 updates of two episodes. The **selected v5 artifact** is the unweighted average of checkpoints 150,
  200, 250, 300 of one training (seed 2 of a 42-candidate development selection on retention), frozen by DEC-049/050
  before the confirmatory study. Training uses soft applicability over all episode records while deployment uses hard
  top-1 selection and the per-position deltas, so the reader is empirical for this package, not a meta-gradient through
  the deployed update.

### 3.6 The ePC training surrogate (used for the "PC-trained reader", §6.5)

`revision_v1/epc_train.py`: same episodes, seeds, losses, weights and optimiser schedule as the BP trainer; only the
gradient estimator of the two base-dependent terms (answer CE and preservation KL) differs. The gradient of the loss
with respect to the three write vectors is read from the ePC base's settled site errors (eight steps, η = 0.1) and
passed to the reader's parameters θ through the local loss Σ_m ⟨stop_grad(g_m), w_m(θ)⟩, a VJP through the controller
and reader only. The retrieval loss involves no base pass and is exact in both trainers. Finite settling changes
gradient *magnitudes* as well as directions; no renormalisation or learning-rate compensation was added, by design.

---

## 4. How things are measured

### 4.1 Edit streams and endpoints

An **edit** is one fact to store (a zsRE question with a new answer; a CounterFact subject–relation–object statement
with its paraphrases; a MQuAKE multi-hop fact). A **stream** applies 1,000 edits one after another (300 on MQuAKE), with
checkpoints at 100, 300 and 1,000 edits where everything is scored by ordinary greedy generation (≤ 32 tokens, alias
match):

| endpoint | meaning |
|---|---|
| ES | immediate edit success: the answer is produced right after the edit |
| RET-ES | retention: the original prompt still yields the edited answer at the end of the stream |
| RET-GS | **generalisation**: a held-out paraphrase yields the edited answer at the end of the stream (the primary endpoint) |
| LS | locality: 50 unrelated prompts decode to identical text cap-on and cap-off |
| near-miss | 100 prompts about a *neighbouring* fact (same relation/template family, different subject) still give the cap-off answer |
| revision | 50 records superseded mid-stream: the newer answer wins |
| unseen false fire | fraction of never-stored questions on which the reader fires |

### 4.2 Fidelity and harm on ordinary text

After the last edit, the cap is run over the registered **full validation split**: 1,931 reset-context windows of 128
tokens of OpenWebText, 127 scored positions each, **245,237 positions**. For each position the quantity is the per-token
loss change Δ = NLL_cap − NLL_capoff in nats (and the KL between the two next-token distributions). Summaries: mean
KL, mean signed ΔNLL, exceedance fractions P(Δ > 0.01), P(Δ > 0.1), P(Δ > 1), the maximum, **ES99+** (the expected
shortfall: the mean of the worst 1 % of positions, zero mass included) and the smallest number of positions carrying
half of the total positive loss. The old project benchmark, mean KL ≤ 0.001 and mean ΔNLL ≤ 0.01, is shown but no
longer a veto (DEC-064a). Positions are not independent draws: the same 245,237 positions recur in every cell.

### 4.3 Populations, realizations and the frozen study

Confirmatory items come from reserved pools disjoint from everything used in development. A **realization** is one
independent draw of a 1,000-edit population plus all its endpoint rows (paraphrases, locality prompts, near-miss pairs,
revisions); the confirmatory study has three per dataset, each run in **five edit orders**. Orders share subjects and
are not independent replications; **three realizations are the unit of inference**, so intervals are wide by design
(DEC-069: ranges of realization means as preliminary summaries; a pointwise t with 2 degrees of freedom as a
sensitivity).

The **Stage-4 matrix** (frozen 18 Sep, DEC-071): 330 cells = 3 datasets × 3 realizations × 5 orders × conditions
{learned reader v5 (`R1_learned_ff`), random-geometry reader with the same gate and deltas (`R1_nonlearned`), stable
v0 cap (`v0_stable`), matched-update adapter, two live v0 caps (C1, C2), two continued-base controls (base further
trained on OpenWebText, or self-distilled, then evaluated with the stable cap: `S1_LM`, `S1_literal`)} and an optional
45-cell historical extension. Receipted two-worker queue, 750 process-hour cap, every cell's inputs hash-bound. The lead
**halted the queue at 270 cells** (26 Sep) to give the remaining GPU time to the predictive-coding question: blocks 1–4
complete (the triplet on all realizations and the matched/live comparators) plus 45 of block 5; S1_literal CounterFact
(15) and the extension (45) were not run and their contrasts are reported unavailable, never selected by outcome. Spend
392.4 process-hours; three independent audits of the receipt chain pass.

**Exposure.** Everything run after the halt is **post hoc work on exposed populations** (the realization-0 streams the
selected reader had already seen, or historical v0 populations) and is labelled so throughout; the fresh subjects
reserved for a fourth realization (Option R) are untouched by any selection.

---

## 5. Results: the confirmatory study (BP-trained reader)

Sources: `pc_cap/docs/R1_stage4_report.md` (entry point), `R1_stage4_report_triplet.md`, `R1_stage4_report_comparators.md`,
`assets/presentation-materials/tails_v1.md`. Figures `03`, `04`, `05`, `01`, `02`.

### 5.1 Behaviour at the end of 1,000 edits (300 on MQuAKE), mean over realizations

| dataset | condition | ES | RET-ES | RET-GS | LS |
|---|---|---:|---:|---:|---:|
| zsRE | learned reader v5 | 0.994 | 0.982 | **0.960** (0.955 / 0.965 / 0.961) | 1.00 |
| zsRE | random reader + gate | 1.00 | 1.00 | 0.524 | 0.99 |
| zsRE | stable v0 cap | 1.00 | 0.667 | 0.186 | 0.97 |
| CounterFact | learned reader v5 | 0.993 | 0.977 | **0.678** (0.692 / 0.666 / 0.677) | 0.99 (0.96 in r2) |
| CounterFact | random reader + gate | 1.00 | 1.00 | 0.121 | 0.01 |
| CounterFact | stable v0 cap | 1.00 | 1.00 | 0.000 | 1.00 |
| MQuAKE (300) | learned reader v5 | 1.00 | 0.999 | **0.716** | 1.00 |
| MQuAKE (300) | random reader + gate | 1.00 | 1.00 | 0.000 | 0.00 |

Registered contrasts (learned minus control, RET-GS): zsRE +0.44 vs the random reader, +0.77 vs stable v0, +0.78 vs
matched update, +0.83/+0.85 vs live C1/C2; CounterFact +0.56 vs random, +0.68 vs stable v0. Nine of thirteen available
contrasts receive the preliminary label *positive*; four (CounterFact vs the v0-family caps) are *inconclusive*
because the learned reader's locality falls to 48/50 in realization 2. Specificity is imperfect: zsRE near-miss
preservation 86/100, 92/100, 87/100; unseen-question false fires 0.09, 0.13, 0.16 at 1,000 records.

The two readings that matter for the talk: the random-geometry reader shows that a fixed cosine geometry plus the gate
already solves half of zsRE but destroys CounterFact locality (fires on relation neighbours); the learned null
decision is what buys CounterFact. And the stable v0 cap's zero paraphrase retention on CounterFact/MQuAKE is a
calibration floor (it matches exact prompts only), not a measurement of its storage.

### 5.2 Fidelity: rare, severe, concentrated harm (figures 01, 02, 04)

All 45 learned-reader cells exceed mean KL 0.001 (zsRE ≈ 0.0015–0.0020, CounterFact 0.004–0.007). Pooled over 15 cells
per condition and dataset (own cap-off reference):

| condition | dataset | P(Δ > 0.01) | P(Δ > 1 nat) | max (nats) | ES99+ | half of all harm in |
|---|---|---:|---:|---:|---:|---|
| learned reader v5 | zsRE | 0.159 % | 0.080 % | 11.1 | 0.26 | 1,024 positions (0.03 %) |
| learned reader v5 | CounterFact | 0.298 % | 0.165 % | 15.4 | 0.57 | 1,900 (0.05 %) |
| learned reader v5 | MQuAKE | 0.313 % | 0.194 % | 17.1 | 0.62 | 2,336 (0.06 %) |
| random reader | CounterFact | 2.05 % | 1.70 % | 20.3 | 5.53 | 18,856 (0.5 %) |
| stable v0 cap | zsRE | 0.104 % | 0.034 % | 27.7 | 0.18 | 262 |
| live v0 C2 | zsRE | 0.019 % | 0.016 % | 50.6 | 0.32 | 175 |
| every v0-family cap | CounterFact, MQuAKE | 0 | 0 | 0 | 0 | never fires on ordinary text |

Three statements the figures support: harm is rare and concentrated for every condition that writes; small means
conceal differences in frequency, severity and concentration (the learned reader disturbs more positions, mildly; the
v0 caps disturb fewer, catastrophically); mean drift of 0.002–0.007 nats is the average of a few large losses. What
they do not establish: a heavy-tailed distribution *class*, a power law or any asymptotic tail (finite data; −log p is
not bounded by vocabulary size), independence of positions, robustness to unobserved inputs, temporal clustering.

### 5.3 The κ pilot (development, DEC-054; figure 06)

Replacing the reader's answer surprisal −ln p by the coupled logarithm −ln_κ p (κ = 0.2, 0.5) during training lowers
the drift tail (ES95 0.223 → 0.084/0.063 nats; max 5.26 → 2.70/2.60) and the false-fire rate (11.7 % → 5.0/4.0 %) but
costs retention beyond the pre-registered floor (RET-GS 0.796 → 0.754/0.748; floor 0.776), and a plain clipped
surprisal min(−ln p, 2) gets most of the tail reduction (0.103; 3.62; RET-GS 0.779). Null under the rule fixed before
the runs; descriptively, bounding surprisal shifts the porosity/interference trade-off rather than improving it. It is
not the coupled free energy of Nelson et al. (no coupled expectation, no changed inference distribution), not a coupled
Markov blanket, and not a test of the one-κ conjecture.

---

## 6. Results: the predictive-coding refocus and the supplemental work (26 Sep – today)

Sources: lead-queue items 126–146 in `pc_cap/docs/lead_queue.md`; reports `pc_cap/docs/additional_work/{PC-v0_report,
PC-v1_report, PC-controls_report, AW-B_report}.md`; `assets/presentation-materials/review-data/results.md`.

### 6.1 PC-v0: corrected SE-E vs SE-A on the original v0 cap (figure 07)

Design: same ePC base and v0 C1 cap, fresh empty memory per arm, historical S5 populations (zsRE 1,000 edits,
CounterFact 300), three realizations × five orders = 60 cells, eight-step error credit (η = 0.1) vs adjoint; paired
harm readout on a 4,064-position legacy subset.

| zsRE, means over 15 cells per arm | SE-A | SE-E | paired difference |
|---|---:|---:|---|
| ES | 0.9985 | 0.9991 | +0.0006 |
| RET-ES | 0.522 | 0.542 | **+0.020 in every realization** (+0.022 / +0.020 / +0.019) |
| RET-GS | 0.138 | 0.135 | −0.003, mixed signs |
| LS | 0.963 | 0.983 | +0.02 (−0.006 … +0.038) |
| learning wall per cell | 276 s | 619 s | 2.2× (11k vs 98k reverses) |
| harm: mean ΔNLL / ES99+ / max | 0.00160 / 0.173 / 3.67 | 0.00176 / 0.189 / 3.49 | same order; slightly more frequent small harm |

CounterFact is saturated and identical in both arms (ES = RET-ES = 1, RET-GS = 0, LS = 1): the v0 calibration floor,
no discrimination. Reading: with SD-24 fixed, the defective-energy loss of acquisition (ES −0.34) is gone; PC credit
acquires and generalises like adjoint, retains own-prompt answers a little better, costs twice as much, and does not
reduce harm.

### 6.2 Controls on that result (DEC-075; figure 08)

At the common order (order 100 × three realizations × two datasets):

| zsRE | ES | RET-ES | RET-GS | LS | mean ΔNLL | ES99+ | learning s/cell |
|---|---:|---:|---:|---:|---:|---:|---:|
| adjoint (SE-A) | 0.998 | 0.515 | 0.131 | 0.970 | 0.00145 | 0.156 | 281 |
| SE-E, 1 step | 0.998 | 0.515 | 0.131 | 0.970 | 0.00145 | 0.156 | 341 |
| SE-E, 8 steps | 0.999 | 0.534 | 0.131 | 0.977 | 0.00157 | 0.167 | 614 |
| SE-E, 32 steps | 0.999 | 0.565 | 0.122 | 0.997 | 0.00221 | 0.236 | 1,525 |

- **Settling depth is a dose–response.** One step reproduces adjoint *exactly* on every endpoint (as §3.3 predicts), so
  the eight-step gain is not a step-size artefact. Thirty-two steps buy +0.050 own-prompt retention and +0.027
  locality, lose 0.009 paraphrase retention, raise harm 52 % and cost 5.4×. More settling buys own-prompt retention,
  not generalisation, and the price grows faster than the gain.
- **Random-direction credit** (a vector of the true credit's norm, random orientation): stopped by the historical
  compute allowance at 993/1,000 items with ES 0.003 (adjoint pair 0.998), having spent 4.6× the forwards: the
  acceptance-by-loss rule rejects almost every random direction. Closed after its first pair (DEC-079). The credit
  direction is doing the work.
- **Compute-matched adjoint** (adjoint offered the operation budget the eight-step credit spent): adjoint does not use
  it; it reaches its acceptance threshold within the ordinary rounds, so its ledger equals plain adjoint. The control is
  weak by construction (budget offered, not consumed) and the report says so.

### 6.3 Fixed-v5 acquisition credit (figure 09)

The selected v5 reader, base, gate, calibration and seeds held fixed; only the per-record delta acquisition credit
changed (adjoint vs corrected eight-step error); four exposed cells (zsRE and CounterFact, realization 0, order 100,
300 edits); full 245,237-position harm readout. **Indistinguishable on every endpoint**: zsRE ES 1.0/1.0, RET-ES
1.0/1.0, RET-GS 0.983/0.983, LS 1.0/1.0, near-miss 76/76, revision 50/50; CounterFact identical except RET-GS 0.807 vs
0.803 (one paraphrase of 300). Harm: zsRE mean KL 0.00186 vs 0.00170, ES99+ 0.196 vs 0.182, max 9.3 vs 12.3; paired
mean changes −0.00016 (zsRE) and +0.00013 (CounterFact) nats, within position noise. Cost 1.2–1.35×. Credit settings
(32 iterations; error rate 0.05 and 0.2) change nothing but cost (673 s vs 422 vs 312 adjoint per zsRE cell). Reading:
on the reader that works, the five-step delta acquisition reaches the same accepted corrections under either credit
rule; the credit rule is not where this system's behaviour is decided.

### 6.4 Bounded correction at query time (AW-B, pre-registered DEC-076/076a; figure 10)

Thirteen numerical wrappers and three stricter gate thresholds applied to the selected v5 cap at query time: clip the
per-token log-ratio log(p_cap/p_base) to ±b (bound 2b nats) and renormalise; **mixture** ρ·p_base + (1−ρ)·p_cap with
ρ = e^{−2b} (same bound); global shrinkage p_base·exp(α·log-ratio); gate thresholds 0.4/0.3/0.2 instead of 0.5. Selection
rule fixed before scoring: among arms whose RET-ES and RET-GS stay within 0.02 of v5 on both development datasets
without losing LS or near-miss, pick the largest reduction of the maximum token loss (worst dataset), ties by ES99+.

- **Calibration (development memories):** every clip destroys editing (RET-ES −0.63 … −1.0) because it bounds how far
  the *answer* token may rise; shrinkage and stricter gates lose paraphrase retention. The rule selected the mixture
  ρ = e⁻¹ (bound 1 nat) and no comparator. Mechanism: the mixture keeps ≥ 1 − ρ = 0.63 of the cap's mass on its answer,
  so greedy decoding is unchanged, while the base's 0.37 share bounds every token's loss increase at −log ρ = 1 nat.
- **Evaluation on the ten sealed realization-0 streams** (five orders × two datasets, full inventory): in every one,
  efficacy endpoints unchanged on zsRE; CounterFact RET-GS −0.007 to −0.012; maximum token loss 9.3–15.4 → 1.00 nats;
  ES99+ and mean KL both cut 3.2–3.5× (zsRE mean KL 0.0015–0.0020 → 0.00045–0.00065, under the old 0.001 line in all five
  orders; CounterFact 0.0042–0.0069 → 0.0013–0.0019). The pre-registered success rule is met in all ten.
- Framing fixed by the lead (DEC-078): an intervention experiment beside the κ pilot ("what bounding does to the tail
  and what it does not do"), not a recommended cap configuration. It is a bound on per-token loss at a fixed prefix;
  it does not promise unchanged greedy answers in general, and the CounterFact KL stays above 0.001.

### 6.5 PC-trained reader (running; lead-queue items 144–146)

The v5 training recipe (same pools, episodes, optimiser, 300 updates, checkpoint average 150–300) re-run under two
gradient estimators, backpropagation vs the ePC surrogate of §3.6, three paired seeds each; every reader evaluated on
the exposed realization-0 streams at 300 edits (acquisition adjoint in every arm; fresh memory per reader) with the
full harm readout. Training cost (measured on seed 0): BP 14 min; **ePC 24.6 h per seed**, about 100× (eight-step error inference inside
every training step). Done so far: all three BP seeds, ePC seed 0.

| reader | dataset | ES | RET-ES | RET-GS | LS | near-miss | fired positions (of 245,237) | mean ΔNLL | ES99+ | max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BP s0 / s1 / s2 | zsRE | 1.00 | 1.00 | 0.973 / 0.990 / 0.977 | 1.00 | 0.85 / 0.67 / 0.73 | 18 / 13 / 21 | 0.0001–0.0002 | 0.012–0.018 | 6.5–10.6 |
| **ePC s0** | zsRE | 1.00 | 1.00 | **0.947** | 1.00 | 0.91 | **0** | 0 | 0 | 0 |
| BP s0 / s1 / s2 | CounterFact | 1.00 / 0.99 / 1.00 | 1.00 / 0.99 / 1.00 | 0.810 / 0.800 / 0.835 | 1.00 | 1.00 / 0.99 / 1.00 | 256 / 660 / 149 | 0.0012–0.0054 | 0.12–0.55 | 8.5–12.5 |
| **ePC s0** | CounterFact | 1.00 | 1.00 | **0.568** | 1.00 | 0.98 | 185 | 0.00128 | 0.132 | 7.7 |

Two observations. (1) The BP re-trainings reproduce the selected v5's retention (zsRE 0.983, CounterFact 0.807 on the
same streams) but fire on 13–21 zsRE ordinary-text positions against ≈ 350 for the selected v5 artifact, with ten
times less mean harm: the 42-candidate selection on retention appears to have picked a reader that fires more on
ordinary text than a typical re-training. (2) The ePC-trained reader (one seed) edits and retains its own prompts
exactly like BP but generalises less to paraphrases (0.24 below BP on CounterFact, outside the BP seed spread) and
never fires on zsRE ordinary text: a quieter, more conservative reader. Whether that is the surrogate's finite
settling (gradient magnitudes differ by construction) or a seed effect waits on seeds 1 and 2 (≈ 3 Oct 10:30).

### 6.6 Option R: a fourth realization of the primary triplet (stalled, partially complete)

The one item that would strengthen the registered claims themselves: realization 3 on zsRE and CounterFact (30 cells,
1,000 edits, frozen recipes, fresh reserved subjects). Started 29 Sep through a supplemental consumer; four cells
complete (learned and random reader, zsRE, orders 100–101), one `v0_stable` zsRE cell killed at its 8,002 s ceiling.
Capex's reconciliation (R-2, delivered this morning) diagnoses the cause: the extension recipes omitted the batched
drift-assay implementation their frozen parent specifies, so the v0 cells run the slow scalar path (drift phases of
2,000 s against 290 s in the donor cell). Recommendation on the table: defer the v0 class, continue the learned and
random reader cells, and do not repair sealed recipes silently. Remaining portfolio 27 h; whether to spend it here or
on the interface study (§7) is a decision for today or tomorrow.

### 6.7 Cut

The 3,000-edit scaling study (does the tail grow with memory size?) is infeasible: only 684 certified zsRE subjects
remain after every reservation (HT-16).

---

## 7. Running now and planned to the freeze

| job | status | ends (EDT) |
|---|---|---|
| ePC-trained reader, seed 1: training then two evaluations with harm | running since 1 Oct 07:08 | ≈ 2 Oct 08:45 |
| ePC-trained reader, seed 2 | chained automatically | ≈ 3 Oct 10:30 |
| **Upper-layer read/write interface 2×2** (AW-L5): read taps {1,2,3} vs {2,3} × write sites {1,2,3} vs {3}, three paired training seeds (six readers), 24 evaluations on the exposed realization-0 streams at 300 edits with full harm. Tests the lead's interface hypothesis (upper taps may suffice; writing only at the last site may reduce harm or cost). Runner CPU-validated; ≈ 30 h | queued after seed 2 | ≈ 4 Oct evening |
| Option R continuation (learned/random cells; v0 class deferred) | decision pending (see §6.6) | would need ≈ 15–20 h |
| Harm readout for the compute-matched control group | low priority, ≈ 25 min | if idle time |
| 6 Oct | last new fits | |
| 7–8 Oct | evaluation, reports, figures; Stage-4 report limitations (GPT-2-small caveat) | |
| 9 Oct 17:00 | experimental freeze | |
| 10–14 Oct | slides (deck v3, `pc_cap/docs/presentation/deck_v3/`, 15- and 25-minute speaking scripts exist) and rehearsal | |

Not everything fits: Option R's remaining cells and AW-L together exceed the time before 6 Oct. The default order on
record (DEC-077) runs the ePC seeds, then AW-L, and gives Option R what is left.

---

## 8. From the abstract to the testbed: implemented, measured, proposed

Source: `pc_cap/docs/presentation/abstract_to_testbed.md`. **Implemented** = a working component exists in code that
ran; **measured** = a result exists on a named population; **proposed** = in the abstract, not built.

| abstract idea | status | what exists | what it is not |
|---|---|---|---|
| frozen pretrained transformer as generative prior | implemented, measured | GPT-2 124M frozen throughout; a 50M ePC-distilled base for the v0 line | not frontier scale |
| small adaptive agent learning only the residual | implemented, measured | the cap: ≈ 10⁴–10⁵ (v0) to 3.3M (v1) parameters against 124M; per-fact corrections retrieved by a gate | not a general residual network trained on the whole stream |
| "sparse columnar residual network" | partly | sparse per-record memory with bank-wise writes | no column formation, growth policy or core–periphery scales |
| prior-side interface (blanket to the transformer) | implemented | read taps and write sites after blocks 4, 8, 12; the AW-L study varies them | not shown to be a Markov blanket formally; "κ-porous" is a label |
| environment-side interface | implemented as the edit stream and the null decision | fire or withhold a correction per query | no environment model, no other action |
| prediction error as the learning signal | implemented, measured | adjoint or ePC site-error credit for the writes; the ePC surrogate for reader training | error-optimisation PC here is autodiff through the graph, not a local rule |
| coupled, κ-deformed free energy | measured as a loss-level pilot only | κ pilot on the reader's answer surprisal; null under its rule | no coupled expectation, no changed inference distribution |
| interference as a geometric invariant; one κ governing separation, forgetting and robustness | proposed | the pilot shows bounding surprisal shifts a trade-off | untested |
| expected-free-energy policy selection with a risk term | proposed | routing is a fixed rule | no preferences, no risk term |
| precision weighting as risk sensitivity | proposed | the ePC solver has per-site error scaling, unused as policy | — |
| epistemic value; uncertainty-triggered audits | proposed | our probes (locality, near-miss, revision, tail) are investigator-selected | not autonomous |
| learning from failure ("the regime that threatens the agent carries what it can learn") | measured in one sense | the tail exists and is where the cap's errors live (§5.2) | no agent uses that signal yet |
| coupled free energy keeps precision finite on tail events | proposed | — | no evidence either way |
| nested Markov blankets | proposed | — | — |

The honest one-paragraph version: we built the frozen prior, the small residual agent between two interfaces,
prediction error as its learning signal, and the audit machinery around it; we measured editing, retention, locality
and the distribution of unintended harm on three datasets across three populations; we tested the one piece of the
active-inference loop this testbed can test now, the credit rule, under predictive coding, and found it viable and
not decisive; and we measured what two kinds of bounding (κ-coupling of the surprisal; a mixture bound on the output
distribution) do to the tail. Policy choice, the coupled objective, precision as risk, epistemic action and blankets
remain proposed.

---

## 9. What we would value from you on Friday

1. **The predictive-coding story.** Is "one-step error credit equals adjoint exactly; deeper settling buys own-prompt
   retention at the price of harm and compute; on the reader that works the credit rule is immaterial" the right
   reading of §6.1–6.3? Is there a cleaner way to say what the settling adds (the cross-layer coupling of the
   quadratic term) for an audience that knows predictive coding well?
2. **The PC-trained reader.** If seeds 1–2 confirm a quieter reader (less paraphrase generalisation, fewer false
   fires), is that a property of finite-settling gradients (magnitude shrinkage acting as a regulariser) or an
   artefact of not compensating the learning rate? What control would you want, given that no GPU time remains for
   one?
3. **Heavy tails.** We claim rare, severe, concentrated harm and refuse to claim a tail class. Is that the right line
   for a session on extremes, and does the 1-nat mixture bound (§6.4) belong beside the κ pilot as "two kinds of
   bounding", as decided, or elsewhere?
4. **Active inference.** The abstract promises an agent; the testbed delivers a credit rule, a gate and measurement.
   How should the talk present the path from here to expected-free-energy policy choice without over-claiming?
5. **Last GPU days.** Interface 2×2 (new mechanism, the lead's hypothesis) versus the fourth realization (narrower
   intervals on the registered claims): which serves the talk better?
6. **Anything that looks wrong.** Every number is traceable; tell us where to look.

---

## 10. Glossary

| term | meaning |
|---|---|
| base | the frozen language model (GPT-2 small; or the 50M ePC-distilled model for the v0 line) |
| cap | the adaptive module reading and writing the base's residual stream at three sites |
| site / bank / tap | a residual-stream location after block 4, 8 or 12; "bank" is the v0 name for the write slot there, "tap" the read |
| record, memory, stream | one stored edit; the set of records; a sequence of 1,000 (or 300) edits applied in order |
| v0, C1/C2/CR | the first-month cap and its routing variants |
| v1 / v5 reader, `R1_learned_ff` | the trained retrieval-and-null network; v5 is the selected frozen artifact |
| `R1_nonlearned` | the same gate and deltas with a random-geometry reader (control) |
| `v0_stable`, matched update, live C1/C2, S1_LM, S1_literal | comparator conditions of the confirmatory matrix (§4.3) |
| SE-A / SE-E / SE-R / SE-AM | adjoint credit / predictive-coding error credit / random-direction credit / compute-matched adjoint |
| ePC | error-optimisation predictive coding: energy relaxed over per-layer error variables by gradient descent |
| SD-24 | the energy defect fixed on 13 Sep (site prior evaluated after the write) |
| ES, RET-ES, RET-GS, LS | edit success, own-prompt retention, paraphrase retention (generalisation), locality |
| fidelity / harm / drift | the cap's effect on ordinary text, per token, in nats; ES99+ is the expected shortfall of the worst 1 % |
| realization / order | an independent population draw / a permutation of its edits |
| exposed / sealed / reserved | data already seen by selection / drawn and hashed before any outcome / set aside for a future draw |
| DEC-nnn | a numbered decision of the lead in `pc_cap/docs/decisions.md` |
| Capstan / Capex | the two agents (Claude orchestrator / Codex implementer) |

## 11. Where to look

- Decisions, numbered and dated: `pc_cap/docs/decisions.md`. Running status: `pc_cap/docs/lead_queue.md` (newest at the
  end) and `pc_cap/docs/ongoing.md` §1.
- Confirmatory study: `pc_cap/docs/R1_stage4_report.md`, `_triplet.md`, `_comparators.md`; protocol
  `R1_stage4_protocol_v5_2_D_final.md`; the Stage-2 design report `R1_stage2_report.md` (§2 architecture, §3 why the
  design changed).
- v0 study and the energy: `pc_cap/docs/report.md`, `pc_cap/docs/epc_energy.md`.
- PC refocus: `pc_cap/docs/additional_work/PC-v0.md` (specification), `PC-v0_report.md`, `PC-v1_report.md`,
  `PC-controls_report.md`, `PC-reader.md`; the plan discussion `pc_cap/docs/additional_work_pc_refocus*.md`.
- Bounded correction: `pc_cap/docs/additional_work/AW-B.md` (pre-registration), `AW-B_report.md`. Interface study:
  `AW-L.md`. Fourth realization: `R.md`, `R_decision.md`, `pc_cap/docs/tasks/R-2.md`.
- Tails and κ: `assets/presentation-materials/tails_v1.md`, `kappa_pilot_v5.md`, `figures/`.
- Presentation: `pc_cap/docs/presentation/presentation_brief_2026-09-26.md`, `abstract_to_testbed.md`,
  `deck_v3_outline.md`, `deck_v3/`, `final-experiments.md`; exports under `assets/presentation-materials/deck_v3/`.
- Code: base and v0 under `pc_cap/src/pccap/`, the v1 reader under `pc_cap/src/pccap/revision_v1/`, all post-halt work
  under `pc_cap/aw/`. Everything runs locally in JAX; predictive coding is built on FabricPC.
