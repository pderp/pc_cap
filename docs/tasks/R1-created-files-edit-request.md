# R1 — permission request for repairs to files created in this task

The user's current rule requires permission before editing any existing file. Codex has applied that conservatively even to the initial drafts it created during this task. All corrected code was therefore placed in **new candidate files** and tested there. No edits to the five original drafts below have been applied.

**Review/apply this bundle:** `docs/tasks/R1-created-files-repairs-v2.patch`, with exact original and candidate SHA256 values in `R1-created-files-repairs-v2.json`. This supersedes the initial one-line baseline request and the first combined bundle. `git apply --check` succeeds. None of its targets predated this task; none are under `src/pccap` or owned by Claude.

| file | proposed correction |
| --- | --- |
| `scripts/r1_00_baseline.py` | Compare saved learning/query/total ledgers exactly; allow independently captured elapsed-wall envelope timestamps. |
| `scripts/r1_20_episodes.py` | Reserve the composition fallback scope, so an extra support cannot make a required memory unnecessary; identify unknown neighborhood entities as unresolved; require unrelated-control and new-edit source families to differ. |
| `tests/revision_v1/test_episodes.py` | Simplify fresh-process test command construction; add regression coverage for unrelated-control family separation. |
| `scripts/r1_validate_proposed.py` | Use pytest's importlib mode for review test filenames containing a dot. |
| `tests/revision_v1/test_episode_text_adapter.py` | Sort imports to satisfy Ruff. |

Validation of the final candidate bundle: **52 passed in 1.79 s**, Ruff PASS, 384-episode/2,304-query coverage audit PASS. The reconstructed baseline matches all 12 specified values and verifies 20 external assets. Evidence is in `logs/r1_codex_20260913/verification_v2/`, `episodes_v2/`, and `manifests/revision_v1/baseline.json`.

The direct, unpatched drafts are not yet green: the baseline rejects the envelope timestamp difference; the episode tests have the two known composition failures; the text-adapter test has a lint-only import-order issue. The passing result belongs to the explicitly hashed candidates. Applying this bundle makes the direct draft entry points match the reviewed code, after which their focused tests/lint should be run once.

Source installation is a separate coordination gate: `revision_v1_staging/episodes.py` already contains the validated implementation, but no file may be created under `src/pccap` until the orchestrator's `v0 close-out committed` release line. This request does not ask to modify the old frozen manifest, reports, results, source, task board or another agent's files, and does not authorize a commit.
