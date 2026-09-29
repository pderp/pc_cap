# Reviewer primer — the pc_cap programme as of Sunday 27 September 2026

Written by Capstan (the Claude orchestrator) for reviewers who have not followed the project. Two more files will
join this folder: `results.md` once the predictive-coding runs finish (Monday), and `final-experiments.md`, an outline
of the last experiments to be drafted together on Tuesday or later. Everything below is checked against the project's
decision record; where a number is quoted, the source file is named. Paths are relative to the two repositories,
`pc_cap` (code, logs, documents) and `assets` (data, models, run outputs, presentation materials).

## 1. The question, in one paragraph

A pretrained transformer is a strong generative prior that fails in the extremes: rare inputs, distribution shift,
non-stationary streams. The July abstract (*Coupled Active Inference on a Frozen Transformer Prior*, Derr & Iklé)
proposes keeping the base frozen and adding a small adaptive agent that learns only the residual, driven by
prediction error, sitting between two interfaces, with a coupled (κ-deformed) objective to survive heavy-tailed
errors. The programme built and tested the parts of that idea that a workstation can test in two months: a small
"cap" that stores factual corrections to a frozen GPT-2, the credit rule that writes them (adjoint, i.e.
backpropagation, versus predictive-coding error inference), and careful measurement of what the corrections do to
unrelated text, including the distribution of rare large losses. The talk on 15 October (Binghamton satellite,
*Active Inference in the Extremes*) is organised around three themes: active inference, predictive coding, and
heavy-tailed distributions.

## 2. Vocabulary

| term | meaning |
|---|---|
| base | the frozen language model: GPT-2 (124M parameters) for the current study; a 50M model trained with an ePC (error-optimization predictive coding) surrogate for the original v0 line |
| cap | the small adaptive module on top of the base; it reads the base's residual stream at three sites (after blocks 4, 8, 12) and writes corrections at the same sites |
| v0 cap | the original design (September, first month): a memory of per-fact records, writes at all three sites, credit for the writes either adjoint (SE-A) or predictive-coding error (SE-E) |
| v1 / v5 reader | the revised design: a small learned "reader" (trained with backpropagation) decides which stored record applies to a query and whether to fire at all (the *null* decision); per-record corrections are acquired with a few adjoint steps. "v5" is the selected, frozen configuration |
| edit / stream | one fact to store ("X's capital is Y"); a stream is a sequence of 1,000 edits (300 on MQuAKE) applied one after another |
| ES, RET-ES, RET-GS, LS | immediate edit success; end-of-stream retention on the original prompt; retention on a paraphrase (generalisation); locality, i.e. unrelated prompts unchanged |
| fidelity / harm | how much the cap changes the base's predictions on ordinary text: mean KL divergence, and the per-token loss change at 245,237 validation positions; the old "critical" benchmark was mean KL ≤ 0.001 nats, now a secondary benchmark, not a veto |
| realization | an independent draw of the edit population from reserved data; the confirmatory study has three; each realization runs five edit orders |
| SE-A vs SE-E | adjoint credit versus eight-step predictive-coding error credit for the cap's writes, everything else identical |
| SD-24 | a defect found on 13 September in the predictive-coding energy (the site prior was evaluated after the write instead of before), fixed the same day; the only earlier SE-E result predates the fix and is therefore not a clean negative |

## 3. What has been done

1. **v0 study (closed).** The original cap on the ePC base; its confirmatory claim was not supported. Its SE-E arm
   was run under the SD-24 defect: lost acquisition (ES −0.34 against SE-A) with slightly better paraphrase
   retention (+0.019). Source: `pc_cap/docs/report.md` §S5 with the SD-24 note.
2. **Revision v1 (the current study).** A learned reader on frozen GPT-2, developed on training pools, then a
   frozen confirmatory matrix of 330 cells (three datasets × three realizations × five orders × several conditions)
   sealed on 18 September and run by a receipted queue with a 750 process-hour cap. The queue was **halted by decision
   at 270 cells** on 26 September (`decisions.md` DEC-074/074b) to free the GPU for the predictive-coding question;
   what was not run is listed with reasons in `pc_cap/logs/R1/reports/comparators-270/unavailable.csv`.
3. **Results that exist** (assembled in one document: `pc_cap/docs/R1_stage4_report.md`; the receipt chain of every
   cell was audited independently, X22 for block 1 and X23 for cells 136–270, both PASS; full 270-cell spend 392.4
   process-hours of the 750 cap) (all descriptive until the registered inference is read; three realizations give wide
   intervals by design, DEC-069):
   - The learned reader keeps paraphrased edits far better than the controls: mean final paraphrase retention 0.960
     on zsRE, 0.678 on CounterFact, 0.716 on MQuAKE (300 edits), recurring in every realization; three of the four
     registered contrasts available are preliminarily positive, one inconclusive. Source:
     `pc_cap/docs/R1_stage4_report_triplet.md`.
   - Every learned-reader cell fails the old mean-KL benchmark. The harm is rare and concentrated: 0.16–0.31 % of
     ordinary-text positions change by more than 0.01 nats, and half of all harm sits in 0.03–0.06 % of positions;
     the worst single tokens lose 11–17 nats. The v0-family comparators disturb fewer positions but their worst
     tokens reach 28–51 nats. Small means conceal these differences in frequency, severity and concentration.
     Source: `assets/presentation-materials/tails_v1.md` and `figures/tails/`.
   - Comparators: a matched-update adapter and two "live" v0 caps harm zsRE text at least as much as the learned
     reader; continued-base controls (the base further trained on OpenWebText, or self-distilled, then evaluated with
     the stable v0 cap) behave like the stable cap. Source: `pc_cap/docs/R1_stage4_report_comparators.md`.
   - A loss-level κ pilot (coupled logarithm on the reader's surprisal): null under its pre-registered rule; bounding
     surprisal lowers the tail and the false-fire rate at the cost of retention, and a plain clip does most of it.
     Source: `assets/presentation-materials/kappa_pilot_v5.md`.
4. **What is running now (the predictive-coding refocus).** The registered study contains no predictive-coding
   condition at all; every arm uses adjoint credit. So, on the freed GPU:
   - **PC-v0**: corrected SE-E versus SE-A on the original v0 cap and ePC base, fresh memories per arm, 60 cells
     (zsRE 1,000 edits and CounterFact 300 edits × three historical realizations × five orders). Pre-run check
     passed: with the corrected energy the one-step site error equals −0.1 × adjoint to 1e-8. Running since 00:05
     Sunday, done about 14:00. Specification: `pc_cap/docs/additional_work/PC-v0.md`.
   - **Fixed-v5 credit**: the selected v5 reader held fixed, only the per-record acquisition credit changed from
     adjoint to corrected PC error, on the exposed realization-0 streams (300 edits, one order, zsRE and CounterFact),
     four cells; runs Sunday evening after its profile.
   - For both, a paired ordinary-text harm readout on the same positions, so efficacy, harm and cost appear together.
   Populations for both are exposed (historical or already-seen confirmatory streams); they are labelled replications
   and transfer tests, not fresh confirmation. The reserved fresh subjects (DEC-073) are untouched.

## 4. What we expect the results to tell us

- **PC-v0.** Whether finite-iteration predictive-coding credit, with the defect fixed, acquires and retains factual
  edits at all, and what it costs (nine forwards and nine reverses per credit against one of each). Three readings
  are possible and each is publishable: PC credit recovers acquisition and matches adjoint (the programme's credit
  rule is viable at this scale); it recovers acquisition but retains less or costs more (viable with a trade-off); it
  still fails to acquire (the defect was not the only problem, and the credit rule needs more than eight steps or a
  different design). Historical reference under the defective energy: ES −0.34.
- **Fixed-v5 credit.** Whether that credit transfers to the reader that works. A negative v0 result does not cancel
  this one, because v0's retrieval was its known bottleneck. Its four cells give a direction, not an interval.
- **Neither result** demonstrates local or biologically plausible learning (the solver uses autodiff through the
  graph), a PC-trained reader, the coupled free energy, expected-free-energy policy choice, or Markov blankets. The
  abstract-to-testbed map (`pc_cap/docs/presentation/abstract_to_testbed.md`) says, idea by idea, what is
  implemented, measured or still proposed.

## 5. Choices after Tuesday

GPU time available: from Monday midday to Monday 6 October (last new fits), about 6 days; 7–8 October for
evaluation and figures; freeze 9 October 17:00 ET; slides and rehearsal 10–14 October. Each candidate below has code
or a pre-registration draft already; costs are single-GPU wall-hours.

| if the PC results say… | natural next experiments | cost |
|---|---|---:|
| PC credit works on v0 and transfers to v5 | **PC-trained reader**: train the v5 reader itself with the corrected ePC surrogate instead of backpropagation, three seeds each, evaluate on 300-edit streams (the pilot at 500 steps favoured BP: answer NLL 2.85 vs 4.50) | 30–40 |
| PC credit works on v0 but not on v5 | more v5 credit settings (iterations, error learning rate) on the same four cells; or the PC-trained reader as above | 8–40 |
| PC credit fails on v0 | a settling-depth study (8 vs 32 iterations) on the v0 cells that failed; and spend the rest on the heavy-tail theme below | 8–15 |
| in every case, for the heavy-tail theme | **bounded correction + stricter gate** on the v5 cap: clip the per-token log-ratio (exact 2b-nat guarantee), matched mixture, global shrinkage, lower null threshold; tail versus efficacy on the same positions; code complete and pre-registered (`pc_cap/docs/additional_work/AW-B.md`) | 12–24 |
| if intervals matter more than new mechanisms | **one more untouched realization** of the primary triplet (zsRE, CounterFact; populations and recipes already built) | 24–30 |
| if the lead's interface hypothesis matters | **upper-layer read/write interface** 2×2 with three seeds (masks and identity audit already delivered) | 24–30 |
| if the tail's growth with memory size matters | 3,000-edit streams on one realization (needs a population check first) | 12–15 |

Not all fit: about 120 usable hours remain after the PC chain, so two or three of these at most. The reviewers'
feedback deadlines (`pc_cap/docs/lead_queue.md` item 120) still apply: anything needing more than three GPU-days
must be chosen by Wednesday 1 October.

## 6. Where to look

- One-page current plan: `pc_cap/docs/plan_from_saturday.md`.
- Decisions, numbered and dated: `pc_cap/docs/decisions.md` (DEC-050 onward is the confirmatory study; DEC-073/074
  the additional work and the halt).
- Presentation direction and deck: `pc_cap/docs/presentation/presentation_brief_2026-09-26.md`,
  `deck_v3_outline.md`, the slide drafts under `deck_v3/`, the claim ledger `pc_cap/docs/talk_claim_ledger_v7.md`,
  exports under `assets/presentation-materials/deck_v3/`.
- The discussion that led to the refocus: `pc_cap/docs/additional_work_pc_refocus.md`, `_review.md`, `_response.md`,
  `additional_work_halt_options.md`.
- Running status: `pc_cap/docs/lead_queue.md` (newest items at the end) and `pc_cap/docs/ongoing.md` §1.
