# Round 50 — Capex handoff

2026-09-27. **REV-2 and PRES-5 done; PC-9 prepared on tested copies and awaiting
safe integration; PC-8 still pending the complete experiment.**

The live GPU chain, frozen sources and Capstan-owned files were not edited.
No GPU work, queue operation, staging or commit occurred.

1. **[PC-9](PC-9.md):** exact two-runner patch, 8/16/32-step and error-rate
   options, treatment records and profile-derived cost scenarios; **18 CPU tests
   pass**. Apply only after the old source-bound chain and its reports have
   finished, preserving the old code for regeneration. The existing eight-step
   report/readout restrictions need a separate variant-aware integration lane
   before a contingency can be launched and fully reported; details are in PC-9.
2. **[REV-2](REV-2.md):** [reviewer Q&A](../presentation/qa.md) and
   [pending results tables](../presentation/review-results-pending.md), exported
   identically to `assets/presentation-materials/review-data/results.md` outside
   the repo. All numerical results remain PENDING with exact source selectors.
3. **[PRES-5](PRES-5.md):** complete [15-minute](../presentation/deck_v3/speaking-script-15min.md)
   and [25-minute](../presentation/deck_v3/speaking-script-25min.md) scripts, with
   slide clocks, backup cuts and original PC result tokens. charlie reviews the
   final wording and eventual interpretation.
4. **PC-8:** at **09:02 EDT**, 27/60 cells had complete finishes, no failed
   finishes, no group summary and no harm report. No partial effect estimates
   were inspected or published. Readiness: `logs/additional_work/round50/pc8-readiness.json`.

Broader validation: **114 CPU tests passed, two slow tests deselected**, followed
by the final 18-test PC-9 suite including three additional tests; counts overlap.
Lint, patch applicability, unchanged live-runner hashes, claim IDs, two-sentence
answers, source links, pending slots, scaffold copy identity and exact talk-time
sums pass. Logs are in `logs/additional_work/round50/`.

New owned files: `aw/{pc9_stage,pc_sweep,presentation_timing,review_results_scaffold}.py`,
`aw/tests/test_pc9.py`, the candidate directory, reviewer/talk documents, task and
claim/completion records, round-50 logs, and the external reviewer scaffold.
Live PC-v0 result changes and `logs/R1/final_queue_{launch,resume}.log` are
operational outputs, not Capex edits.
