# PC-16a — conditional seed-1 reader/tail/presentation refresh

Status: seed-1 refresh done, October 2, 2026, Round 61. Seed-2 refresh awaits the
owner's completion trigger. Agent: Capex. No GPU use, model calls or commits.

Inputs: both seed-1 terminal report/cost pairs complete; all BP seeds, ePC seeds
0–1, saved stream and harm vectors, original selected-v5 reference. The earlier
Round-60 wait ended at Capstan's explicit go in ongoing.md/lead queue 155.

Outputs: `logs/additional_work/PC-reader/report-round61-final/` and
`logs/additional_work/HT-17/snapshot-20261002-seed1/`; both canonical readable
reports; figures under `assets/presentation-materials/figures/tails_ht17/` in
`snapshot-20261002-seed1/` and `round61-seed1/`; revised slide drafts, 15/25-minute
scripts, Q&A, ledger, number sheet and canonical `deck_v3/rehearsal/` export.
The fresh `rehearsal-round61-final/` export is retained alongside it.

The reader report has **10/12 evaluations and seeds 0–1 paired**; all ten reader
vectors match HT-17. The tail snapshot has **301 cells**, with exactly unchanged
statistics for the preceding 299 and unchanged non-reader groups. Two seed-2
evaluations remain explicit. Costs are 102.1×/95.8× BP for the completed training
pairs, not the historical 37× forecast.

Scientific reading: all four paired paraphrase-retention differences favor BP,
but magnitudes vary (2.00–24.17 percentage points). Own-prompt retention is nearly
equal, not identical. CounterFact firing and mean/ES99 harm reverse direction
between the two seeds. In the paired-seed HT-17 contrast, CounterFact conditional
severity differs by +.0357 nats, with a conditional window interval spanning zero;
zsRE has lower harmful-change frequency but greater conditional severity, with
the latter interval withheld for sparse-event resamples. No uniform quietness,
safer-learning, systematic-effect or three-seed claim. See DOC-2 for precise
qualifications to Capstan's unchanged reviewer update.

Verification: 33 focused tests pass, including new seed-reversal/partial-pair
wording fixtures; scoped Ruff passes. X25 `round61-final` passes all 25 groups
and hashes 4,606 files. X26 `round61-final` has no export/source issues or spoken
placeholders. Its five unmatched occurrences are explicitly reviewed in
`rounding-review.json`: “roughly one-third,” plus rounded positive deficit
magnitudes 2.7/24.2 in the script and slide. All are sourced; no audit criterion
was relaxed. Canonical pack's 39 exports and source hashes were rechecked.
Validation: `logs/additional_work/PC-16a/round61/validation.json`.

Reproduction: first ran `aw.pc_reader_report --refresh-tail
logs/additional_work/HT-17/snapshot-20261002-seed1 --output
logs/additional_work/PC-reader/report-round61-seed1`. The final prose was emitted
with the same saved tail snapshot and `--output .../report-round61-final`; the
first reader directory is intermediate. Tail fitting took 91.36 CPU wall seconds.
Historical report/rendering sources are preserved at their exact hashes under
`docs/tasks/round61-source-archive/`; only reporting resolution changed, with no
runtime trainer, numerical algorithm or GPU-queue edit.

Done-when met for seed 1: reports, tail coverage, deck and number sheet agree on
the available seeds and denominators. The three-seed answer stays partial.
No active watcher was started. Seed 2 and meeting feedback remain outstanding.
