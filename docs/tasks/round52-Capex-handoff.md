# Round 52 — Capex handoff

2026-09-28. All six assigned CPU lanes are delivered. No GPU job was launched, no frozen source was changed, and Capstan's live settling-depth runners/results were left untouched. No commit was requested from Capex this turn; Capstan separately committed the approved AW-B specification amendments as DEC-076a.

| Lane | Delivered | Remaining operational step |
|---|---|---|
| AW-B3 | Qualified both development memories and ten evaluation memories; all sixteen wrappers, native efficacy, approved mechanical selection, evaluation success table and cost accounting | Capstan profiles/runs calibration after the settling-depth controls; then selected evaluation |
| PC-12 | Seeded random-direction and additional-useful-update adjoint controls; private current-runner integration, treatment-aware report, tiny native smoke | Capstan profiles and runs each 12-cell paired experiment |
| X24-final | PASS for 60 v0 + four fixed-v5 cells, 32 pairs | None for this completed experiment |
| PC-8 | Both measured reports, verified harm, updated claims, reviewer tables, figures and resolved slide export | Speaker review of presentation |
| PC-11 | Applied-state regression tests; exact old/new v0 numerical agreement and all eight fixed-v5 checkpoint metric dictionaries reproduced | None for assigned remainder |
| R-1 | Supplemental 30-cell consumer, two-worker schedule, native checkpoints/full validation/watch, receipts, memory/deadline/retry controls | Tuesday's explicit lead decision; no automatic launch |

Start with `docs/tasks/AW-B3.md` and `PC-12.md` for exact owner commands. Other records: `X24-final.md`, `PC-8.md`, `PC-11.md`, `R-1.md`. The prepared AW-B identities are in `manifests/additional_work/AW-B_v1.json`. These are execution-ready CPU deliverables, not claims that the future GPU jobs have passed.

Scientific decisions recorded from charlie this turn: additional acquisition updates for the matched control; AW-B ranks by the smaller dataset reduction in maximum, then the smaller ES99 reduction; calibration uses the actual full-endpoint zsRE payload behind the saved AW-L0/PC-4 memory. No unresolved scientific question from this round remains.

The matched control provides equal **offered per-item operation budget**. Threshold stopping may leave unused budget; unfinished rounds roll back while retaining actual compute charges. It is not a FLOP or wall-time match. Option R's two-worker schedule estimates 20.285 elapsed hours at donor means but 34.485 at ceilings; the 30-hour portfolio budget stays fixed, so full completion is uncertain.

Completed scientific reports: `docs/additional_work/PC-v0_report.md` and `PC-v1_report.md`. Reviewer tables: `docs/presentation/review-results.md`. The v0 result is +2.033 points own-prompt retention on zsRE, −0.28 points paraphrase retention on average, and more compute. Fixed-v5 does not establish equivalence: CounterFact loses one paraphrase under SE-E and maximum ordinary-text harm is larger on both datasets. These are exposed supplemental comparisons, with explicit limits; reader/base training remains BP. The original v5 harm final-table failure is retained in its original cost record and explained in the independently reconstructed report.

Figure exports: `assets/presentation-materials/figures/pc_v0/completed-20260928/` and `pc_v1/completed-20260928/`. Final resolved slide export: `assets/presentation-materials/deck_v3/completed-pc-final-20260928/` (27 files). Earlier export directories are superseded snapshots, not the final handoff. Numerical figures were visually reviewed. The corrected eight-step acquisition result, extreme-harm analysis, and limits on active-inference claims remain distinct in the talk material.

Validation: **59 targeted CPU tests passed**, with a subsequent seven-test Option R check after correcting the watch output namespace to the installed writer's required results tree. Scoped lint and whitespace checks pass. Exact logs, plans and verification receipts are in `logs/additional_work/round52/`; final audit in `logs/r1_x24/final/`. Native tiny controls completed and round-tripped their snapshots. No real-model GPU validation was attempted by Capex.
