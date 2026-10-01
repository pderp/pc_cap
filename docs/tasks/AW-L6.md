# AW-L6 — upper-layer factorial report generator

Status: done CPU deliverable; experimental report partial. Agent: Capex. Date: October 1, 2026.

Inputs: AW-L5 six-reader/24-evaluation design; current PC-reader BP controls; future AW-L development/production result trees.
Outputs: `aw/aw_l_report.py`, shared `aw/reader_results.py`, synthetic factorial tests, `docs/additional_work/AW-L_report.md`, `logs/additional_work/AW-L/report-round57-final/`. Earlier report-round57-20261001 is intermediate.

Six existing full-read/full-write BP evaluations and three BP trainings are explicitly reused under AW-L5's identical-control rule. They are shared observations/costs, not extra replications. Eighteen evaluation cells and three upper-read trainings remain missing. No complete factorial block exists yet; no read/write/interaction effect is inferred from controls alone. The generator discovers recorded production coordinates, checks common population and reader identity across write arms, and keeps development outputs separate. Marginal read/write effects average the two other-factor settings; interaction is the paired difference of differences. The .02 retention tolerance is descriptive, not inferential noninferiority or a new classifier. All physically allocated dense zero slots remain charged.

Verification: synthetic development and production trees cover exact factorial signs, shared controls, missing arms, mismatched write-arm readers and cost deduplication. Round57's 20 targeted tests and scoped Ruff pass; current real control sources verified. Final generation: 0.24 seconds, peak RSS 40,592 KiB; zero GPU seconds.
Done-when: tested generator, partial current report and owner refresh command delivered. Availability limitation: **no AW-L5 development outputs exist yet**; tests use clearly synthetic fixtures and real full-read controls, with no fabricated profile outcomes. Unresolved: owner development profiles and queued factorial production. Questions for lead: none. No commit by Capex.
