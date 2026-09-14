# Round 4: two small script repairs and provenance refresh

Status: proposed, not applied. These are files created by Codex in this round; no tracked source, board, or Claude-owned file is included.

The user's new-files-only rule also prevents revising these files after creation. The exact script patch is `docs/tasks/CODEX-R1-round4-repairs.patch`; its successful in-memory validation is `logs/r1_round4/repair_preview.json`.

1. `scripts/r1_40_matrix.py`: support the complete legacy `bp_100_lr1e-4` pilot, whose summary has no `args.tag`, by using the parent directory basename. No pilot file changes. The proposed source produced the 180-cell core / 660-cell inclusive draft and passed its invariants.
2. `scripts/r1_d1c_candidates.py`: move the `Counter` import to Ruff's required position. No data-selection or tokenization changes.
3. Refresh the changed candidate-script SHA256 in `manifests/revision_v1/zsre_fresh_candidates_v1.json` and `logs/r1_round4/zsre_candidate_review.json`. Preserve all candidate counts, per-record hashes, and external payload hashes; record the import-only provenance change.
4. Refresh the changed source bindings in `manifests/revision_v1/run_matrix_draft.json`, and mark that the tested script repair is now applied. Keep cell definitions and budgets unchanged. The existing draft records that the proposed source was executed in memory; it does not pretend the script repair has landed.

Approval scope: these five files only. No commit, GPU use, board edit, core repair, or change to another agent's outputs. After approval, check the pinned before-hashes, apply the patch, preserve payload identities, run targeted CPU tests and Ruff, and write a new verification record. If the inputs have changed, stop instead of overwriting concurrent work.
