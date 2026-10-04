# Round 63 — completed experimental portfolio, Capex handoff

**PC-16b, R-3 and AW-L6 reporting and the presentation refresh are complete.**
No GPU/model calls, runtime changes, raw-result edits, queue operations or commits.
The planned experiments finished October 4; this handoff does not sign the
October 9 scientific freeze or authorize further experiments.

Canonical results:

- [PC-reader](../additional_work/PC-reader_report.md): twelve evaluations, three
  paired seeds. CounterFact paraphrase deficits in every seed; zsRE's third seed
  reverses its deficit. Own-prompt retention nearly equal; CounterFact harm mixed;
  measured training cost about 100× BP. Source `PC-reader/report-round63-final`.
- [Option R](../additional_work/R_report.md): twenty complete, one v0 incomplete
  by ceiling, nine v0 deferred, zero pending. Four-realization learned−random
  RET-GS sensitivity +44.08/+56.20 percentage points on zsRE/CounterFact. The
  t(3) intervals are assumption-labelled and unadjusted; no classifier reissued.
  Source `R/report-round63-final`.
- [Upper-layer factorial](../additional_work/AW-L_report.md): all twenty-four
  cells, six shared controls. Last-only writes increase mean signed loss in
  every write pair (2.64–4.37×), with at most .67-point RET-GS change; upper reads
  lose CounterFact paraphrases in every seed. Source `AW-L/report-round63-final`.
- [HT-17](../additional_work/HT-17_report.md): 303 cells with twelve reader cells;
  all 301 earlier per-cell statistics and non-reader groups unchanged. The
  conditional window intervals retain their fixed-cell/sparse-event caveats.
  Source `HT-17/snapshot-20261004-complete`.

The deck, scripts, Q&A, ledger, numerical prompts and reviewer exports agree.
Canonical pack: `assets/presentation-materials/deck_v3/rehearsal/` (forty exports).
The new upper-layer figure shows each seed's retention and mean loss, with no
confidence-interval implication. Fresh final build: `rehearsal-round63-verified`;
the earlier `rehearsal-round63-final` build is intermediate. Historical October 2
meeting documents are unchanged; reviewer navigation identifies them as historical.

Validation: 31 focused tests, scoped Ruff and whitespace checks pass. X25
`round63-final` passes all 25 groups with 6,158 unique files hashed. X26 has no
source/export issues; three approximate/sign-conversion occurrences are traced
in `logs/additional_work/X26/round63-final/rounding-review.json`. Numerical matches
remain candidate matches, not automatic scientific certification. All 2,294 deck
source bindings and forty exports pass direct checks; scripts allocate exactly
900/1,500 seconds, with implied rates below 150 words/minute (not measured rehearsal).
`logs/additional_work/round63/validation.json` records these checks.

Two qualifications for Capstan's summary:

1. AW-L's actual last-only/all-write harm ratios span **2.64–4.37×**, rather than
   falling strictly within 3–4×. The read effect on zsRE seed 0 with all writes is
   +.013333, or +1.33 percentage points. The report gives all seed values.
2. The cost-gate failure is preserved in the AW-L report and JSON. The projection
   is an extensionless file containing **17.9834 process-hours**; the shell's glob
   finds nothing and defaults to zero. This was below its forty-hour gate, but
   the admission check did not work. A future reuse must read the exact field
   and reject missing/invalid input; scanning all hour fields would also capture
   the unrelated 48-hour ceiling. Original chain/results are unchanged. Actual
   new AW-L cost is **9.6698 process-hours**, versus **13.2489 hours** including
   the already-run shared controls. These cannot both be charged to the portfolio.

Owned changes: reporting helpers and two regression-test files, exact archives
of prior reporting sources, the three reports and HT-17, presentation/reviewer
documents and generators, reproduction guide and freeze-readiness note, fresh
CPU report/audit/task files and assets figures/packs. The reporting archive now
keys by both path and expected hash, so successive source versions remain
verifiable. No frozen `src/` or `scripts/` file changed. Capstan's fidelity-watch
files, untracked Option R outputs and `results/additional_work/PC12/` are untouched.

The full CPU reproduction passed all sixteen steps in **282.12 seconds**, with
unchanged inputs and **198 output hashes verified**; all 29 catalog groups PASS.
Receipt: `logs/additional_work/reproductions/round63-verified/refresh.json`.
The extension process total is **70,447.44 seconds** including the original
20,418.40; the resumed segment adds **50,029.04**, not another 70,447.44.
 All remaining author actions are review of scientific wording, final
talk duration/rehearsal, commits/pushes and the October 9 freeze sign-off.
