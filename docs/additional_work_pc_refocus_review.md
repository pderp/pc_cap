# Review of "Put predictive coding first after the current run" (`additional_work_pc_refocus.md`)

2026-09-24, Claude (orchestrator), at the lead's request. Read-only; nothing here changes the queue or the standing
plan (`additional_work_plan_final.md`, DEC-073). The pause trigger at the 225th start is armed separately on the lead's
instruction and is independent of this review.

## 1. Verdict

Codex's proposal is scientifically right about the central point and I support it with one change of sequencing and
one framing caveat.

- **Right:** the running study does not test predictive coding at all. Every R1 condition acquires its writes with
  adjoint (backpropagation) credit; the only SE-E result the programme has was produced under the SD-24 defect and is
  not a clean negative. A corrected SE-E versus SE-A replication is cheap (about 3 process-hours for 12 cells at the
  historical costs, at most 15 for all 60) and answers the programme's original question honestly, whichever way it
  falls. I verified the claims it rests on (§2).
- **Change of sequencing:** the trade is not "PC instead of S1". A pause at 225 frees the GPU from about Friday
  morning; the corrected v0 replication needs at most a day; the remaining 105 R1 cells need about three days. Both
  fit before October 6 if the queue is resumed after the v0 replication and the v1 credit experiment is built on the CPU
  meanwhile. I recommend that order (§3) rather than deferring block 5 and the extension outright.
- **Framing caveat:** the talk outline in `assets/presentation-materials/talk_outline_v1.md` does not currently mention
  predictive coding; the refocus adds a result the talk has not promised. That is a reason to do it (the programme is
  named for it and the colleague asked), not a reason to shorten the registered comparators; the lead should decide
  which claim the October 15 slot is for.

## 2. Claims checked

| claim in the proposal | checked | result |
|---|---|---|
| SD-24: site prior evaluated on the post-write latent, fixed 2026-09-13 | `docs/spec_defects.md` row SD-24; DEC-036 | as stated |
| R1 conditions use adjoint credit, not the affected path | `src/pccap/cap/cap.py` (`credit="adjoint"` default), `revision_v1/adapt.py` (calls `base.adjoint` at both delta sites) | as stated |
| regenerated ePC checkpoint and its SHA-256 | `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz`, 498 MB | `ea4c561d…` matches |
| corrected surrogate pilot favoured BP (answer NLL 2.85 vs 4.50) | `docs/R1_stage2_notes.md` rows `bp_500_lr1e-3` / `epc_500_lr1e-3_sd24` | as stated |
| historical S5: SE-E lost acquisition (ES −0.34) with RET-GS +0.019, under the defective energy | `docs/report.md` §S5 with the SD-24 note | as stated |
| pilot cosines / residual 0.350 | `results/R1/pilot/surrogate_check_fixed.json` exists | not re-derived |
| S5 cost records | `results/S5/frozen-confirmatory-v2-84126123/` exists | not re-summed |
| pause at 225 frees "roughly two days" | my forecast: 225 complete ≈ Fri 03:00–05:00 EDT; remaining 105 cells ≈ 65–75 wall-hours | agrees |
| the drain procedure | the block barrier means nothing from block 5 starts before block 4 completes; one SIGINT at the 225th start receipt, as at the block-2 cutover | correct; armed 14:47 EDT |

Two things I could not confirm: whether the SD-24 fix has a regression test against the real solver (I found none named
for it under `tests/`; Codex's check 1 would supply it), and the colleague's review itself, which I have not seen.

## 3. Recommended sequencing (the one substantive amendment)

| when | GPU | CPU |
|---|---|---|
| Fri Sep 25, after the drain and reconciliation | v0 solver smoke and profile (≤ 2 h), then the 12-cell corrected SE-E vs SE-A replication (≤ 24 h ceiling; expect far less) | v1 acquisition-credit seam in `aw/`; paired scoring |
| Sat Sep 26 – Mon Sep 29 | **resume the R1 queue** for block 5 and the extension (≈ 65–75 wall-hours) under a new signed resume request | v1 seam tests; v0 replication report |
| Tue Sep 30 – Fri Oct 3 | fixed-v1 acquisition-credit comparison (≤ 24 h); paired ordinary-text tail readout (≤ 8 h) | interpretation, figures |
| Oct 4–6 | reserve; last new fits Oct 6 | |
| Oct 7–8 | evaluation, figures | |
| Oct 9 17:00 | freeze | |

Why this order rather than Codex's: (a) the v0 replication is the cheapest and most decisive item, so it goes first
either way; (b) the v1 experiment cannot start on the GPU until its acquisition variant exists and is tested against
the v5 path, which is CPU work of a few days, so the GPU would otherwise idle or be spent on lower-priority items;
(c) resuming the queue in that gap keeps the registered comparator coverage complete (block 5 is the continuation
control the protocol lists; the extension is optional and can be dropped last). If the v1 seam is ready early, swap
it ahead of the queue resume; the choice is the lead's at that point. Each drain-and-resume costs about an hour of
reconciliation under the existing delegation and no new signing chain.

Fallback: if anything slips, drop the extension (45 cells) first, then block 5, exactly as Codex proposes; unfinished
registered contrasts stay explicitly unavailable, never re-selected by outcome.

## 4. Points I agree with and would keep as written

- The v0 arm is architecture, configuration and base weights fixed with **fresh acquisition** under each credit rule;
  `EPCBase.from_npz` on the regenerated checkpoint, never the default constructor; S5 calibration and stream rules from
  the archived v2 manifest; 12 cells first, 60 only if the profile fits and before any outcome is seen.
- The five checks in §3, especially the first: a one-step site error equal to −0.1 × adjoint from zero error with
  nonzero writes is the test that would have caught SD-24, and it must run against the real solver.
- Old S5 scoring for the replication, modern bounded-text score as an explicitly secondary column; zsRE as the credit
  comparison, CounterFact's zero paraphrase floor stated.
- "Error-optimization predictive coding" as the name, with the disclaimer that the solver uses autodiff and is not a
  local or biologically plausible rule.
- The v1 experiment as a credit-only change with the selected v5 reader held fixed, on the exposed realization-0
  populations, labelled exploratory transfer; the negative-v0-does-not-cancel-v1 rule.
- Option R's fresh subjects left unconsumed; AW-L retraining and the upper-layer hypothesis deferred with their
  artifacts kept; the small paired tail readout retained so efficacy and harm appear together.
- Governance: one specification, one runnable command, raw results with identities, algorithm-focused tests, one
  report. No new signing sessions.

## 5. Smaller corrections

- §1 table: the block-4 comparators are 76 / 90 at the time of writing (now 78); all remaining are v0_live C2
  CounterFact at ≈ 133 process-minutes each, so the 225 boundary is ≈ 03:00–05:00 EDT Friday, not 15–16 hours from the
  snapshot.
- §5 ceilings: 64 single-GPU wall-hours is fine as stop limits; note that the R1 resume in §3 above is charged to the
  R1 budget (750 process-hours, 270 used), not to this 64.
- The historical-v2 extension is "optional" in the protocol (block 6, 285 + 45); say so when listing what a pause
  defers.
- DEC-073 remains in force for populations: the replication uses exposed historical S5 populations, the v1 test uses
  the exposed realization-0 streams already prepared for AW-B/AW-L; nothing draws on the reserved subjects.

## 6. What I need from the lead

1. Confirm the refocus (Codex's plan with §3's sequencing) as the supplemental portfolio, replacing
   `additional_work_plan_final.md` §1; I will record it as DEC-074 and update the lane assignments.
2. Confirm that the queue is to be **resumed** after the v0 replication (my recommendation) rather than left paused.
3. Say whether the October 15 talk should carry the PC result; that decides how much of the tail readout and the
   bounded-output follow-up survive the cut order.
