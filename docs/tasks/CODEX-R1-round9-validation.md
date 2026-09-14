# Codex round 9 — authorized repairs and final validation

Recorded 2026-09-14T23:19:35.916024+00:00.

This addendum supersedes the **pending test repairs and validation status** in the earlier
[handoff](CODEX-R1-round9-handoff.md), completion JSON, task records and protocol/report cutoff.
The user replied “go ahead and commit your work please” to the request to apply the three prepared test fixes.
The approved scope was applied exactly:

- Remove the obsolete strict xfail from the orphan-checkpoint regression test.
- Validate live source hashes against a freshly built draft while preserving the stored historical matrix.
- Insert the missing import-group blank line in the analysis test.

The cache repair in R1-X8-cache-repair.patch remains an **unapplied owner proposal**.
No model code, scientific thresholds, dataset resources or historical logs were changed by these repairs.

## Validation

- Full CPU revision suite: **320 passed, 8 skipped**, no failures, 47.86 s.
  [Log](../../logs/r1_round9/revision_tests_after_approval_cpu.txt).
- Ruff check: **passed** for all eleven new Python files.
- Ruff formatting: **all eleven already formatted**.
  [Log](../../logs/r1_round9/new_files_lint_after_approval.txt).
- Earlier package-layout check: **59 passed**, still applicable; these repairs change only tests.
  [Log](../../logs/r1_round9/package_layout_tests_cpu.txt).
- Every file in the prior 73-file delivery inventory retained its recorded hash except the analysis test's
  approved import-spacing change. Historical integrity receipts remain unchanged.

Tests used the existing venv, CPU-only JAX, CUDA hidden, bytecode writes disabled and a fresh test directory
under assets/test_tmp. No GPU/base/teacher execution or actual draw/seal occurred.

## Post-repair test identities

| File | SHA-256 |
| --- | --- |
| tests/revision_v1/test_r1_27_superseding_cpu.py | 01055cd3fbab4c3434ba4247747d6aa383d4e1f3bef7a8bf36936fa15965db13 |
| tests/revision_v1/test_round4_data_matrix_cpu.py | 5224b18c727d56410af54fb92cf2608f00c87297fcb4cb5f7c33a4b8dfb2d6d1 |
| tests/revision_v1/test_analysis.py | dbcf05e5113b49f77e4137be224dc96104766b368de0273fe3048db07a0e22d6 |

## Commit scope

The user's instruction authorizes staging and committing this round's deliverables and these three repairs.
The commit includes the five lanes, source evidence, MQuAKE metadata manifest, reports, tests and this validation
addendum. Prepared MQuAKE payload resources stay outside the repository under assets.
The pre-existing untracked logs/r1_round8/pytest_tmp directory is excluded. No push is requested or performed.
Final hash/status is reported in the assistant response after git confirms the commit.
