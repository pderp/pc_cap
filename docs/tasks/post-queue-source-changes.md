# Source changes queued until the v3 grammar queue finishes (the v3 freeze binds the whole `src/pccap` tree)

1. Re-apply analysis-tree v3: `git checkout 36ede02 -- src/pccap/analysis/s4_06.py` (temporarily reverted in the working
   tree on 2026-09-13 after the code-drift refusal of grammar C1 r0 p1; DEC-031).
2. Apply Codex's harness fix `docs/tasks/P2-s5-dryrun-directory-v3-source.patch` (create `results/<stage>` before writing
   the queue summary in `pccap.harness.execute.main`; found by Lane P2 in a fresh checkout) and add a control.
3. Record both in `manifests/analysis_versions.json` (`source_versions`) — no further confirm-mode job is expected after
   the grammar rerun; any later rerun needs a version-4 manifest.
