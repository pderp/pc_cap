# Round 60 — Capex handoff

**REP-1 complete; PC-16a awaits seed-1 CounterFact.** No GPU use or commits.

- [Reproduction guide](../REPRODUCE_additional_work.md): commands, hashes,
  resources, figures, dependency order and measured costs for all supplemental
  studies. GPU commands are documented only.
- `aw.refresh_reports`: fresh-output CPU runner and two supporting modules,
  with nine passing synthetic tests and clean scoped lint. The delivered run is
  `logs/additional_work/reproductions/round60-verified/`; 16 steps in 262.36 s,
  unchanged inputs, 29 checked groups PASS and 193 hashed generated files.
- [PC-16a](PC-16a.md): the staged report has nine reader evaluations and nine
  matching HT-17 rows, but CounterFact's terminal report/cost are absent as of
  about 08:05. Canonical publication remains pending the prescribed ten-cell
  boundary. No three-seed result is claimed.
- POST-1 and PRES-9 still await the October 2 reviewer feedback. Option R/AW-L
  results and later presentation refreshes remain tied to their owner triggers.

Owned new repository files: the three `aw/` modules, their test file, the guide,
this handoff, REP-1/PC-16a task records, round-60 claim/completion JSONs and
`logs/additional_work/REP-1/` plus `reproductions/` outputs. External resources:
`assets/presentation-materials/reproductions/` only. No existing tracked project
file was edited. Live chain/evaluation logs and `results/additional_work/PC12/`
belong to Capstan and are outside this change.

Use `round60-verified` for review/delivery. `round60-check1` and `round60-final`
are preliminary validation snapshots, not canonical replacements. Publishing a
new deck still includes reading its literal interpretation; the runner records
this in `presentation-review-required.json` and leaves source documents intact.
