# Additional experiments before October 9 — orchestrator's review and amendments

Written 2026-09-20 (Claude, orchestrator) after reading everything in `docs/gen-trans/` (the 54-page GT/CD report, the
14-slide deck and its presenter notes, the H3 architecture report, the H3 distillation report of September 19, and the
H2 enwik8 Colab notebook) and Codex's `docs/additional_work_plan.md` (unmodified). Everything here is a proposal for
the lead; nothing has been launched, and no file under the R1 content lock was touched.

## 1. Verdict in brief

Codex's plan is sound where it matters: it keeps R1 and its lock untouched, it separates supplemental arms from the
registered matrix, it names the right controls, and its two priority lanes (AW-L upper-layer interface, AW-B bounded
correction) are the two additions that speak to our actual talk. I would keep both. My amendments are:

1. **Add a third candidate Codex did not list: extra realizations of the registered primary triplet (Option R).**
   The talk's weakest point is inference on three realizations (DEC-069); two more realizations of the 45-cell triplet
   halve the interval widths and cost about one GPU-day each. Entry condition: unused reserved items exist.
2. **Re-scope AW-B around the tail, not the mean, and run it first on the GPU.** A zero-GPU pre-analysis of the 84
   finished cells (§3) shows that no bound compatible with successful edits brings mean KL under the old 0.001 benchmark
   on CounterFact or MQuAKE; what bounding buys is the maximum and ES99. AW-B costs about 12 GPU-hours, not 24,
   because one streamed base/cap pass scores every wrapper at once.
3. **Enlarge AW-L slightly and start it now.** Reader training is about six minutes per reader (§3), so the full 2×2
   with three seeds plus the last-block-only read set is cheap; the cost is evaluation streams. Implementation can start
   before the lock is released by living in a new top-level directory (`aw/`) that the lock does not inventory.
4. **Defer AW-G and AW-D as Codex does, and note the cheaper route for the H3 question:** the supplied notebook is a
   finished Colab experiment that needs none of our GPU. Whether to run it there is the lead's call and outside pc_cap.
5. **Use the remaining calendar honestly.** The queue should release the GPU around September 26–27; that leaves about
   twelve GPU-days before October 9. Codex's 120-hour ceiling uses under half of it. I propose a 200-hour portfolio with
   explicit cut lines (§6). Human review time, not GPU time, is the binding constraint.

## 2. What the supplied documents add, in one paragraph each

- **GT/CD report (54 pp.).** A framework (six jobs per layer; reconciliation is the empty slot where predictive coding
  goes), a toy working system (H2: 120k-parameter byte transformer on Tiny Shakespeare, 13 readers, 1,521-parameter
  gate), and honest numbers: most of the gain is the count dictionary; structure search adds 0.010 bpb; PC as a learning
  rule ties BP; prediction-time settling adds about 0.0025 bpb; forgetting is drift of the gate, not loss of memory.
  It contains no GPT-2, no factual editing, no enwik8, no deadline. Two constructions are directly usable by us: the
  bounded bit-tilt correction with the |gain| ≤ 2a guarantee (report eq. 19, Codex's AW-B) and the protected-mixture
  bound (§9.4). Its staged plan puts "gain over a strong ordinary adapter at matched memory and compute on a 10M–100M
  base" as stage B; **R1 on GPT-2 with matched_update and the S1 adapters is exactly a stage-B-type test**, which the
  talk can say.
- **Deck and presenter notes.** The same content for a PC audience; the useful distinctions for us are stored versus
  reachable knowledge, and temporary inference versus weight learning versus structural change.
- **H3 report.** Generated readers (including one parent–child composition) beat a fixed bank in 5/5 seeds; nonlinear
  versus linear is unsettled; 32-step settling is far from equilibrium (PC/BP cosine 0.94). It specifies a 6.5-hour
  Colab experiment whose notebook is not in the supplied set.
- **H3 distillation report.** Joint read-only fitting of a compressed upper block with the cap beats staged fitting
  (0.008 bpb, all seeds); the writable-PC branch fails; the 32-step estimator has cosine 0.27 to the equilibrium gradient.
  This is already the experiment AW-D would replicate.
- **Colab notebook.** An H2-style (not H3) enwik8 run: PyTorch, 7.56M-parameter base, 21 fits, 7.5-hour budget,
  restartable on Drive. It is a specification for Colab, not a port target, and it has never been executed.

## 3. Facts I checked before amending

**Run forecast** (read at 14:44 EDT today; 86 started, 84 finished, 45.3 wall-hours since launch):

| quantity | value |
|---|---:|
| cells per wall-hour (two workers) | 1.86 |
| charged process-hours so far / projected total | 87 / ≈ 340 of 750 |
| remaining cells | 246 |
| projected last finish | 2026-09-26, early morning |
| GPU wall-hours from release to the October 9 cutoff (17:00) | ≈ 290 |

**Reader training cost.** The v5 recipe is 300 steps × 2 episodes; the stage-2 notes record 351 s and 368 s per seed
(`docs/R1_stage2_notes.md`, text-null reader table). AW-L's trained arms are therefore dominated by evaluation, not
training; Codex's L5 is not the expensive step.

**Code claims in Codex's plan.** Verified: banks read after blocks 4, 8 and 12 (bank 3 before `ln_f`),
`single_site` in `learner.py` is a deployment-time path that starts the corrected pass at bank 3, and `adapt.py` still
optimises all bank deltas. So a bank-3-only write is applied just before the final layer norm and the unembedding:
**it is an output-adjacent tilt, the same object AW-B bounds, and it cannot propagate through any transformer block.**
A bank-1 write passes through eight blocks. That is the mechanism AW-L actually varies.

**Zero-GPU pre-analysis of the saved full-validation vectors** (`full-validation-1000.npz`, layout cap NLL /
cap-off NLL / original NLL / KL cap-off→cap / KL original→cap, 1,931 windows × 127 positions), all completed cells,
realizations 0–1, means over cells. "fired" = positions where the cap changed the distribution at all. The clip
columns are the mean of min(KL, 2b): a heuristic proxy for what a bound of b nats on the log-ratio would leave, not a
bound and not a measurement of the wrapper.

| condition · dataset | cells | mean KL | fired | max ΔNLL | P(ΔNLL > 1) | proxy b=0.25 | b=0.5 | b=1 | b=2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| learned · zsRE | 10 | 0.00241 | 0.19 % | 9.1 | 0.08 % | 0.00075 | 0.00118 | 0.00173 | 0.00223 |
| learned · CounterFact | 10 | 0.00525 | 0.32 % | 13.4 | 0.16 % | 0.00131 | 0.00217 | 0.00329 | 0.00450 |
| learned · MQuAKE | 10 | 0.00703 | 0.40 % | 15.1 | 0.22 % | 0.00166 | 0.00286 | 0.00460 | 0.00632 |
| nonlearned · CounterFact | 10 | 0.07456 | 2.19 % | 18.9 | 1.75 % | 0.01053 | 0.01980 | 0.03569 | 0.05836 |
| v0_stable · zsRE | 10 | 0.00162 | 0.18 % | 26.6 | 0.03 % | 0.00036 | 0.00051 | 0.00072 | 0.00098 |
| v0_stable · CounterFact, MQuAKE | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Two consequences. First, harm lives entirely at the 0.2–0.4 % of positions where the gate fires, so every query-time
wrapper (clip, mixture, shrinkage, threshold) is free at 99.7 % of positions and the fixed-prefix assay can score all
of them from one pass. Second, a successful edit needs to move roughly one nat of displacement at the answer position
(raising an answer to probability 0.5 costs every other token about 0.7 nats), so bounds below b ≈ 1 will start to
kill edits; at b = 1–2 the proxy says mean KL falls by 10–35 % and stays above 0.001 on every dataset, while the
maximum falls from 9–15 nats to 2–4. **AW-B is a tail experiment with an efficacy cost, not a route back under the old
benchmark.** Codex's text allows for this; its endpoint list should lead with the tail.

## 4. Amendments to the lanes

### 4.1 Option R — two more realizations of the primary triplet (new)

- **What.** Realizations 3 and 4 of `R1_learned_ff`, `R1_nonlearned`, `v0_stable` × zsRE, CounterFact (and MQuAKE only
  if reserved items exist) × five orders: 60–90 cells, built with the existing Codex builders from a separate extension
  matrix, same recipes, same scoring, own receipt root under `logs/additional_work/R/`. Labelled a post-hoc extension;
  the registered decision (DEC-069) is not re-run.
- **Why.** With three realizations the t-interval uses t(2) = 4.30; with five, t(4) = 2.78 and √(5/3) more
  precision: widths halve. Nothing else on this list improves the primary claims themselves.
- **Cost.** Block 1 (45 cells) took 23.8 wall-hours under two workers, so ≈ 24 wall-hours per realization for the
  two-dataset triplet plus about six minutes of reader training per realization.
- **Entry conditions.** (a) unused reserved items after the frozen exclusions: from the exclusion counts zsRE is
  plentiful, CounterFact probably sufficient, MQuAKE probably not (169 eligible remainder); Codex should verify with the
  population constructor before anything is promised. (b) fresh question-null family and locality selection under
  DEC-061/070 rules for the new realizations. (c) the fidelity watch runs on these cells too.
- **Cut line.** If either lane in §4.2–4.3 slips, R is what I would cut first, because it strengthens rather than
  adds a claim.

### 4.2 AW-B — bounded correction (re-scoped, first on the GPU)

Keep Codex's mathematics (clip to ±b, mixture with ρ = e^{−2b}, global shrinkage α) and its 13-configuration
calibration. Change:

1. **Primary endpoint: maximum ΔNLL, ES99 and exceedance at 1 nat on the full validation split, paired with RET-GS and
   RET-ES at 300 edits.** Mean KL and the 0.001 line are reported, with the pre-analysis above as the registered
   expectation that they will not be met at any efficacy-preserving b.
2. **Add the cheapest comparator: a stricter null threshold at deployment** (the selected artifact's gate fires less
   often). The κ pilot (DEC-054) already showed that bounding the reader's surprisal buys tail reduction with retention
   loss and that a plain clip took most of the κ gain; the natural question for the talk is whether shaping the output
   beats simply firing less. Two or three threshold values, same streams, same pass.
3. **Cost.** One streamed full-vocabulary pass per (dataset, memory checkpoint) computes base and cap logits once and
   scores every wrapper and threshold at the same time; generation for the efficacy endpoints is per wrapper but small
   (a few hundred prompts). Twelve GPU-hours for the calibration grid and the four final arms on three paired streams
   per dataset, zsRE and CounterFact; MQuAKE adds four.
4. **Success rule, fixed before scoring:** a wrapper is "useful" if it reduces the maximum and ES99 by more than the
   seed spread observed in the κ pilot (max 4.4 nats, ES95 0.39) while RET-GS stays within 0.02 of the unwrapped cap.
   Otherwise the result is the trade-off curve, which is still a slide.

### 4.3 AW-L — upper-layer interface (enlarged slightly, framed by mechanism)

1. **Run the full 2×2 with three seeds and add the last-block-only read set {3} and the middle set {2}** as Codex's
   optional arms, since each extra trained reader is six minutes. That is nine trained readers, 300-edit streams on
   zsRE and CounterFact, one order each: 36 arm × dataset × seed evaluations at roughly 0.6 h each ≈ 24 GPU-hours plus
   the frozen diagnostics. Codex's 48-hour ceiling holds with margin.
2. **State the mechanism up front.** The read set decides *whether* the gate fires (false-fire rate, retrieval); the
   write set decides *how far* a fired correction travels (bank 3: through the head only; bank 1: through eight
   blocks). The 2×2 therefore separates "where harm is decided" from "how severe it is", and the L-AU/L-UU arms are the
   trained cousins of AW-B's output tilt. Plot AW-B and AW-L on one efficacy-versus-tail figure.
3. **Do L2 (frozen diagnostics) on the sealed R1 memories** for the triplet at realization 0: `single_site=True`
   deployment on the existing artifacts is a query-time change, needs no training, and answers the lead's question in
   its cheapest form (does discarding the bank-1/2 writes at deployment cut the tail, and what does it cost?). Two
   GPU-hours. It is an ablation of a system trained for three sites, and the report must say so, as Codex notes.
4. **Query-cost accounting.** Report the corrected-pass cost per fired query for each write set; the observation pass
   is unchanged. A bank-3-only cap should make the corrected pass nearly free, which is the practical half of the
   lead's hypothesis.

### 4.4 Implementation can start now, lock-safe

Codex proposes waiting for lock release before writing supplemental code. The lock inventories `scripts/` and
`src/pccap/` (446 scripts; the resume consumer re-verifies it), so any new file there would break the R1 resume path.
A new top-level directory `aw/` (package `aw`, tests under `aw/tests`, manifests under `manifests/additional_work/`,
results under `results/additional_work/`, logs under `logs/additional_work/`, large artefacts under
`/home/derp/cap/assets/pc_cap/additional_work/`) is outside the inventory, keeps R1's provenance story clean, and lets
the CPU-side work (AW-B's float64 oracle and its tests, AW-L's masks and their zero-write tests, the R extension matrix
and population check) happen during the five days the queue is still running. GPU use waits for release, as Codex says.
Each lane gets a one-page pre-registration in `docs/additional_work/<lane>.md` (hypothesis, arms, endpoints, success
rule, ceiling) reviewed by the lead before its first GPU call; no signing machinery.

### 4.5 AW-G and AW-D — defer, and one option for the lead

I agree with deferral. Two additions: (a) the H3 distillation report already contains the joint-versus-staged result
AW-D would produce, so AW-D would be a JAX replication of a colleague's CPU result, of little value for October 15;
(b) the H2 enwik8 notebook is designed to run on Colab with Drive persistence and needs none of our GPU or code. If the
lead wants that result for context, running it there as written is a decision outside pc_cap and outside our JAX rule;
the H3 report says its own 6.5-hour notebook was never executed either, so the outputs would be new evidence for the
GT programme rather than for our talk. Not recommended for our budget; listed so it is not mistaken for a porting job.

### 4.6 Talk framing from the GT documents (no experiments)

- R1 is a stage-B-type test in the GT programme's own staging: a cap on a 124M base against matched-update and the S1
  adapters at declared memory and compute. Quote the report's caution that a stronger base leaves smaller, noisier
  residual gains, which is what our fidelity results look like.
- Our cap-fidelity benchmark is a behavioral-distance measurement on declared continuations (ordinary text), which is
  the report's §4 notion applied to a real base. The concentration result (harm at 0.2–0.4 % of positions) is the
  empirical shape of that distance.
- The report's forgetting finding (memory intact, gate drifts) is the same family as our false-fire and creep
  observations: what needs protecting is the decision to fire, not the stored record. One sentence, not a claim.
- The 2b guarantee in AW-B is the report's eq. 19; say so, and say that the guarantee is per token on a fixed prefix.

### 4.7 Small corrections to Codex's text

- §1: the notebook is H2-style, as Codex says; the seven-hour figure is a Colab budget, not a runtime.
- §5.1: 24 GPU-hours for AW-B is an overestimate given shared logits; 12 is enough, MQuAKE included at 16.
- §10: the 120-hour ceiling is well under the available ≈ 290 wall-hours; the binding constraint is review time.
- §11: the lead has said Codex's next task will be assigned directly, so the two-agent split there is for the lead to
  decide; the orchestrator can own R (it is queue work of the kind already running) and either of L or B.

## 5. Proposed portfolio and calendar

| priority | lane | GPU wall-hours | earliest GPU start | cut line |
|---|---|---:|---|---|
| 1 | AW-B calibration + final arms (zsRE, CF; MQuAKE if cheap) | 12–16 | release + 0 d | never; ≤ 8 h exploratory version if late |
| 2 | AW-L frozen diagnostics (L2) on sealed memories | 2 | release + 0 d | never |
| 3 | AW-L trained 2×2 (+ {3}, {2}) | 24–30 | release + 1 d | drop {2}, then seeds 3 → 2, then write factor |
| 4 | Option R, realization 3 | 24 | release + 2 d | first cut if anything slips |
| 5 | Option R, realization 4 | 24 | after 4 | second cut |
| — | reserve for retries and re-runs | 30 | — | — |
| | total | ≈ 120–130 of ≈ 290 | | |

Dates, assuming release on September 26–27: September 21–25 CPU implementation and pre-registrations in `aw/`;
September 26–27 release, D13 reconciliation, final R1 report inputs, then AW-B and L2 on the GPU; September 28–October 2
AW-L trained arms; October 1–5 Option R; October 6 last new fits; October 7–8 evaluation and figures; October 9 17:00
freeze. Every lane keeps the rule: conservative projected completion plus validation time must precede the cutoff before
dispatch.

## 6. Decisions the lead is asked for

1. Adopt the portfolio and priorities in §5, or reorder (in particular AW-L before AW-B if the upper-layer question is
   the one the talk must answer).
2. Approve Option R in principle, subject to the reserved-item check.
3. Approve the `aw/` namespace and CPU-side implementation starting now.
4. Say whether the Colab notebook should be run on Colab by anyone; my recommendation is no for our budget.
5. Say whether the H3 sandbox archive and the H3 enwik8 notebook exist somewhere we can read; nothing here depends on
   them, but AW-G/AW-D stay closed without them.
