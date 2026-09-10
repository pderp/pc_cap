# Response to `derp_review2.md` (2026-09-10)

Checked against the tree at the time of this response (the review appears to have read a snapshot from
before the review-1 actions landed, about 08:45–09:00 EDT).

| # | Review-2 statement | Finding | Action |
| --- | --- | --- | --- |
| 1 | Ongoing logs "not addressed, worsened"; no archive | `docs/archive/` already held `ongoing.md`, `ongoing2.md`, `ongoing3.md` (moved 08:45 EDT) and `ongoing4.md` was the single current log. The naming was the residual issue. | Adopted the recommendation: the current log is now `docs/ongoing.md` (renamed from `ongoing4.md`; a dated snapshot sits in `docs/archive/`). Policy in `CONTRIBUTING.md`: one current `docs/ongoing.md`; superseded versions go to `docs/archive/` with a date. |
| 2 | venv setup addressed | Documented, yes; the recreation script is still Lane R (ENV-05) — `updated_plan4.md` §2. | none |
| 3 | `spec_defects.md` has no status markers | Inaccurate for the current file: every SD row has a Status column (committed/open with the verifying task) and a triage header with counts (R3, 08:40 EDT). | none |
| 4/5 | CONTRIBUTING/README addressed | agreed | none |
| N2 | `requirements.lock` "at venv root, not in repo" | Inaccurate: `pc_cap/requirements.lock` is in the repository (151 lines, `pip freeze`). | none |
| N3 | Decisions log has no index | Agreed. | `docs/decisions.md` now opens with an index by type (environment/stack, budget/clock, protocol/analysis, scientific regime). |
| N4 | Multi-lane complexity | Acknowledged; the lanes are independent by construction and the board (`docs/tasks/STATUS.md`) is the single source of claims. | none beyond the single-log policy |
| N5 | REG-02 resumability should be tested with forced interruption | Tested before the run (`tests/distill/test_recipe_tiny.py::test_checkpoint_roundtrip_and_resume`: a resumed step is bitwise equal to the uninterrupted one) and exercised by the run itself: it executes in ≤ 500-step chunks, each a separate process that exits and resumes from the checkpoint — 15 process restarts so far (steps 0, 500, 1000, 1396, 1500, 2000, 2500, 2791, 3000, 3500, 4000, 4186, 4500, 5000, 5500), contiguous step indices, stage boundaries identical to the sibling's run, no holds or non-finite values. | Evidence recorded in `docs/tasks/REG-02.md` when the run completes. |
| N6 | D1/D2 scope margin (1.6 h) fragile | Agreed; interim report 2 R2-07 says the same. | Re-profile with reconcilable costs and a complete cost table before the freeze (`updated_plan4.md` §2); reduced-programme rule stated. |
| N7 | No coverage report | `coverage`/`pytest-cov` are not in the frozen venv (DEC-001). | Listed as a lead decision in `updated_plan5.md` §4 (adding a package to the venv is an environment change); until then `make test-fast`/`test-gpu` counts are the coverage evidence. |
| N8 | Determinism config implicit/fragile | Agreed. | `pccap.assert_determinism()` verifies the flags/config at runtime; `pccap run` calls it after taking the lease and records the report; importing `pccap` after a JAX backend is already initialized now raises. Tests in `tests/test_determinism_guard.py`. |
