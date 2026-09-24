# The plan from Saturday night (2026-09-26) to the October 9 freeze

Consolidated 2026-09-24 by Claude (orchestrator) for external review. One document in place of the discussion trail:
Codex's proposal `additional_work_pc_refocus.md`, Claude's review `additional_work_pc_refocus_review.md`, Codex's
response `additional_work_pc_refocus_response.md`, the options note `additional_work_halt_options.md`, and decisions
DEC-073 / DEC-074 / DEC-074b in `decisions.md`. Where this document and those differ, this one is current.

## 1. Where the confirmatory run stands and where it stops

The Stage-4 confirmatory queue (frozen 2026-09-18, 330 cells) has run without a failure since launch. By decision of the
lead (DEC-074/074b) it halts after **270 of 330 cells**:

| block | contents | status |
|---|---|---|
| 1–3 | primary triplet: learned v5 reader, random-reader control, stable v0 cap × zsRE, CounterFact, MQuAKE × 3 realizations × 5 orders (135 cells) | complete |
| 4 | matched-update adapter and live v0 comparators C1/C2, zsRE + CounterFact (90) | completes ≈ Fri Sep 25 04:00 |
| 5, positions 1–45 | continued-base controls: S1_LM zsRE and CounterFact, S1_literal zsRE (45) | run; halt trigger fires at the 270th start ≈ Sat Sep 26 16:00–20:00 EDT, last cells done ≈ 2 h later |
| 5, positions 46–60 | S1_literal CounterFact (15) | not run; contrasts reported unavailable |
| extension | optional historical v2 reader (45) | not run |

The halt is one SIGINT to the scheduler at the 270th start receipt (the mechanism used at the block-2 cutover); the
two active cells finish; nothing new starts. Reconciliation follows the D13 checklist and produces the block-5
boundary report. Registered analyses are run exactly as frozen on the cells that exist; unrun contrasts are marked
unavailable and never re-selected by outcome. Fresh subjects reserved under DEC-073 stay untouched.

Why stop: the confirmatory study tests a BP-trained feedforward reader on a frozen GPT-2; **no condition in it uses
predictive-coding credit**, and the programme's only SE-E result was produced under the SD-24 energy defect (fixed
September 13). The freed GPU time goes to answering that question directly before the talk.

## 2. What runs after the halt, in order

Budget: Sat ≈ 22:00 → Mon Oct 6 00:00 is ≈ 218 wall-hours; usable ≈ 185 after reconciliation, compilation and
retries. Single GPU (12 GB), JAX only, local only. Ceilings are stop limits, not estimates.

| # | experiment | GPU ceiling | when | owner |
|---|---|---:|---|---|
| 1 | **Corrected SE-E vs SE-A on the original v0 cap** (§3) | 24 h, incl. ≤ 2 h smoke/profile | Sat night → Mon | Codex builds (lane PC-1), Claude dispatches |
| 2 | **PC acquisition credit with the fixed v5 reader** (§4) | 24 h | ≈ Tue Sep 30 → Thu Oct 2, once the seam passes its tests | Codex builds (PC-2), Claude dispatches |
| 3 | **Paired ordinary-text harm readout** for both, same validation positions, both arms | 8 h | with 1 and 2 | Claude |
| 4 | Registered triplet analysis on the 135 complete cells (read-only; no GPU) | 0 | any time | Codex (R1-D14d) |
| — | reserve | 8 h | | |
| | committed total | **64 h** | | |

Stretch, only if 1–3 are done and time remains, in this order: the bounded-correction / stricter-gate readout on the
v5 cap (code exists, ≈ 12 h); a PC-trained reader (v5 recipe trained with the corrected ePC surrogate, 3 seeds vs
BP, ≈ 40 h; the 500-step pilot favoured BP, answer NLL 2.85 vs 4.50); one more untouched realization of the triplet
(prepared, ≈ 30 h). Cut in reverse order. No new fits after October 6; October 7–8 evaluation and figures; freeze
October 9, 17:00 America/New_York; October 10–14 slides and rehearsal.

## 3. Experiment 1 — corrected SE-E vs SE-A on v0

**Question.** With the same frozen base and cap, does finite-iteration predictive-coding credit acquire useful factual
edits and retain them, and what does it cost, relative to ordinary adjoint (backpropagation) credit?

| fixed | SE-A | SE-E (corrected) |
|---|---|---|
| base | regenerated ePC 50M checkpoint (`final-009766/params.npz`, SHA-256 `ea4c561d…`), loaded explicitly; never the default BP teacher | same |
| cap | original v0 C1, live keys, writes at all three banks | same |
| credit | negative normalised adjoint | normalised site error after 8 inference steps, corrected energy `½‖e‖² + task`, error lr 0.1 |
| memory | fresh and empty per arm; same stream, calibration, inventory, budgets | same |

Scope: **12 cells** first (2 credit rules × zsRE 1,000 edits / CounterFact 300 edits × 3 historical realizations × 1
preselected order); all 60 (five orders) only if the timing profile fits the 24-hour ceiling, decided before any
outcome is seen. Populations are the exposed historical S5 ones; the study is labelled a supplemental
defect-correction replication, not fresh confirmation.

Checks before the paired run, against the real solver: with nonzero writes, the one-step site error from zero error
equals −0.1 × adjoint (the test that would have caught SD-24); zero-error forward identity; unchanged base weights;
independent empty memories; the target clamped only for the taught support answer, never at evaluation; the
1/8/32-iteration energy / residual / cosine diagnostic on a fixed development sample (8 stays the treatment); cost
charged as nine forwards and nine reverses per credit.

Endpoints per paired stream: ES, RET-ES, RET-GS, LS with the old S5 scoring; the modern bounded-text score as a
separate secondary column; cost. zsRE is the credit comparison (CounterFact's paraphrase floor was zero for every
historical arm). Every realization and order difference shown; no token-level independence claims. Historical
reference: under the defective energy SE-E lost acquisition (ES −0.34) with RET-GS +0.019.

## 4. Experiment 2 — PC credit with the fixed v5 reader

Hold the selected v5 reader, its BP-trained weights, gate, calibration and memory policy fixed; change only the
direction used to acquire the per-position deltas: adjoint (the registered path) versus the corrected eight-step error
credit. Memories re-acquired independently on paired streams: the exposed realization-0 zsRE / CounterFact
confirmatory streams, 300 edits, one order; labelled an exploratory transfer test, no new-population inference.
Implementation is an isolated acquisition variant in `aw/` (the registered code calls `base.adjoint` directly and is
under a content lock); its adjoint mode must reproduce the registered path to the bit before its PC mode is used.
A negative result in experiment 1 does not cancel this one (v0's retrieval bottleneck is documented).

Naming: "error-optimization predictive coding"; the solver uses autodiff through the graph and is neither a local
learning rule nor a biologically plausible one; neither experiment demonstrates the coupled free energy, active
policy selection, or PC inference inside the reader.

## 5. Reporting and governance

For each experiment: one specification, one runnable command, raw results with data / code / model identities, the
algorithm-focused tests above, one comparison report showing efficacy, harm and cost together. Negative results are
reported as answers. No new signing chains; the existing GPU lease, memory floor, per-cell timeouts and the October 9
stop apply. The talk (October 15) carries the corrected PC results as a measured step toward the programme's
original question, beside the confirmatory triplet and the concentrated-harm findings.

## 6. Questions on which review would help most

1. Is the corrected SE-E design (§3) the right first replication, or is there a control you would add before we
   commit the 60-cell scope?
2. For experiment 2, is "credit only, reader fixed" the transfer test you would run first, or would you rather see
   the PC-trained reader (stretch item) promoted despite its cost?
3. Are the endpoints and the zsRE emphasis adequate to state a PC result honestly, positive or negative?
4. Anything in the halt at 270 (S1_literal CounterFact and the extension unrun) that you consider necessary for the
   talk's claims?
