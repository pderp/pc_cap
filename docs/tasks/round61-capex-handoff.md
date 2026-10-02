# Round 61 — Capex handoff

**DOC-2 and the seed-1 PC-16a refresh are done.** CPU only; no model calls, GPU
use, commits, runtime-driver edits or queue changes. Seed 2 remains Capstan's.

- [DOC-2](DOC-2.md): “2 October update: read first” is the first reviewer entry
  link. Both summaries and their exports are current. Delivered folder record:
  `logs/additional_work/DOC-2/round61-delivered/refresh.json`, including 26 checked
  links and file hashes. Capstan's update is unchanged.
- [PC-16a](PC-16a.md): reader report `report-round61-final`, tail snapshot
  `snapshot-20261002-seed1`; **10/12 evaluations, two paired seeds, 301 tail cells**.
  All 299 previous cell statistics and all non-reader groups reproduce exactly.
  Canonical reports, figures, slide drafts, Q&A, ledger, number sheet, timed
  scripts and `assets/presentation-materials/deck_v3/rehearsal/` agree.
- Validation: 33 focused tests and scoped Ruff pass. X25 `round61-final`: all
  25 groups PASS, 4,606 files hashed. X26 has no export/source issue; its five
  exact-match exceptions are traced in `rounding-review.json` (approximate
  one-third, rounded deficit magnitudes 2.7 and 24.2 appearing twice each).
  All 39 canonical pack exports were rechecked. Script allocations remain
  900/1,500 seconds; these are targets, not measured rehearsal times.
- The updated one-command reproduction also passes: all sixteen steps in
  **262.88 seconds**, unchanged inputs, 193 output hashes checked, 29 catalog
  groups PASS. Receipt: `logs/additional_work/reproductions/round61-verified/refresh.json`.

Scientific wording qualifications for Capstan (detailed in DOC-2):

1. CounterFact seed 1 own-prompt retention is ePC 1.00 versus BP .99, so
   “identical” is not exact; the report says nearly equal.
2. The seed-0 CounterFact paraphrase deficit is **24.17 percentage points**,
   substantially larger than the other deficits; they should not all be called small.
3. zsRE seed 0 is −.0266667 (−.027 to three decimals), or a 2.7-point deficit.
4. The third seed can assess within-recipe consistency, not alone establish a
   systematic training-rule effect. Firing and harm reverse direction across
   the two CounterFact seeds; no uniform quietness or safer-learning claim.

The new paired CounterFact conditional-severity difference is +.0357 nats, with
window interval [−.1568,+.2283]; these intervals condition on fixed cells. zsRE's
harmful-change frequency is lower, while conditional severity is higher and its
interval is withheld (2/200 undefined draws). Keep frequency, severity, retention
and cost separate. The three-seed answer remains partial.

Publication generators now use the current reader/tail paths and dynamic reader
counts. Prior report/rendering bytes are preserved in `round61-source-archive`;
reporting resolution accepts only those exact hashes. No experimental algorithm
or frozen `scripts/`/`src/pccap/` file changed. The extra `report-round61-seed1`,
`rehearsal-round61`, initial DOC-2 records and `X25/X26 round61-seed1` outputs
are intermediate validation passes; use the final paths above.

Owned changes: reporting helpers and their tests; archived reporting sources;
the two canonical study documents; reviewer and presentation documents; new
report/audit/validation directories and task records; figures, reviewer exports
and rehearsal resources under assets. `train-epc-s2/metrics.jsonl` and `PC12/`
belong to Capstan and were not edited by Capex. Lead can commit the owned work.

Still waiting: owner-posted seed-2 completion for the next PC-16a refresh;
today's reviewer feedback for POST-1 and PRES-9. No watcher was started.
