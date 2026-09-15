# Round 11 — prepared import/binding edit request

Status: prepared and tested, not applied. Agent: Codex.

Your standing new-files-only instruction requires permission before editing any existing file, including files created earlier in this turn. Repository `CONTRIBUTING.md` also says: “For any other existing file owned by another lane, write docs/tasks/<ID>-edit-request.md and wait.” Here the user rule is the reason permission is needed: the files are ours, but already exist.

Requested scope is exactly `docs/tasks/R1-round11-import-bindings.patch`:

1. Reorder imports in `scripts/r1_64_dev_cell.py`.
2. Reorder imports in `scripts/r1_64_dev_payload.py`.
3. Update only the code hash in `docs/tasks/R1-64-zsre-v4.recipe.json`.
4. Update corresponding script/recipe hashes in `manifests/revision_v1/freeze_candidate_v1.json`.

Ruff classifies the newly created module differently once installed, so the pre-creation stdin formatting preview did not eliminate these two installed import-order findings. The prepared fix has Ruff exit 0 and preserves both the sorted import AST and all non-import AST. The full installed CPU suite already passes: 479 passed, 8 skipped. `logs/r1_round11/repair_preview.json` records exact before/after hashes for all four files.

No task board, original dataset, sibling repository, sealed runner, freeze authorization or model state changes are included. No commit is requested or performed. An async permission question was sent; the patch remains unapplied until approval. Revalidate the four before-hashes before applying because another agent can change files concurrently. Preserve original generation logs as historical evidence; write new validation/completion records after any approved edit.
