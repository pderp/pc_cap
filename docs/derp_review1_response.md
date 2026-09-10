# Response to `derp_review1.md` (2026-09-10)

| # | Recommendation | Assessment | Action |
| --- | --- | --- | --- |
| R1 | Consolidate the ongoing logs | Agreed: three files with cross-references were hard to follow. | `docs/ongoing4.md` is the single current log (rules + all open lane specs restated); `ongoing.md`, `ongoing2.md`, `ongoing3.md` moved to `docs/archive/` (history; task records still cite them). |
| R2 | Document venv setup | Agreed. `docs/environment.md` records what the venv contains and `requirements.lock` is a full `pip freeze`, but nothing recreates it. | Lane R in `ongoing4.md`: `scripts/setup_venv.sh` + an "Recreating the environment" section, verified in a scratch venv under `assets/envs/` (ENV-05). DEC-001 stands: the project does not install anything from `pyproject.toml`. |
| R3 | Review spec defects | Partly agreed: the register is meant to grow (PA-4) and is frozen verbatim at S4-01, so rows are never deleted; but statuses had gone stale. | Triaged: 18 rows, 16 committed with the task whose verification closed them, 2 open (S2-05); a triage header states the counts. No consolidation of the spec itself: the PDF is the contract. |
| R4 | Add CONTRIBUTING.md | Agreed. | `CONTRIBUTING.md` written (protocol, commit policy, tests/markers, lease, record format, firewall). |
| R5 | README expansion | There was no README at all. | `README.md` written: what the project is, layout, quick start, where the science lives (PDF, plans, decisions, reports). |
| — | "epc_energy.md indicates attention to energy efficiency" | A misreading worth correcting: the file documents the predictive-coding *energy functional* (½Σ‖e‖² + task loss) and its solver, not power consumption. | Clarified in the README. |
| — | Dependency management "unusual" | Acknowledged; it is a lead directive (DEC-001) for a one-month, one-host study. | Documented in CONTRIBUTING and the environment doc rather than changed. |
