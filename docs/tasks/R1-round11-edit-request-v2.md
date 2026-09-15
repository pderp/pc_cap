# Round 11 — final five-file repair request

Status: prepared and tested, not applied. This request supersedes `R1-round11-edit-request.md` and the import-only patch. Use only `R1-round11-snapshot-bindings-v2.patch`.

The user requires permission to edit any existing file, including files created earlier in this turn. No existing file has been edited. Two final integration checks found concrete defects in the new worked recipe, in addition to the two import-order findings:

1. The default Hugging Face snapshot is a symlink directory whose file links resolve into the cache's sibling blobs directory. The existing owner loader correctly rejects children resolving outside the snapshot directory. `scripts/r1_64_materialize_base.py` now provides a new, hash-verified regular-file copy under assets; it never overwrites an existing copy, and exact-content reuse is verified. Three files consume about 0.5 GB. Their bytes, tokenizer and base tensor digest match the original.
2. The draft metadata parser dropped numeric list indices from checkpoint paths, collapsing distinct MLP layers when computing the recipe's parameter hash. No model weights were changed or executed. New `src/pccap/revision_v1/checkpoint_identity.py` preserves dictionary and list structure, refuses malformed paths/gaps/nonfinite arrays, and reproduces the actual training and owner-factory hash: `a02e4560d27dac3a984618c4caf056adb49cc8ef525a771857282f8186663029`.

The prepared patch edits exactly five files:

- `scripts/r1_64_dev_cell.py`: import ordering.
- `scripts/r1_64_dev_payload.py`: import ordering, use the verified materialized base, and use the corrected checkpoint-tree reader.
- `src/pccap/revision_v1/development_cell.py`: include the new materialization script in its code identity.
- `docs/tasks/R1-64-zsre-v4.recipe.json`: correct parameter hash, materialized snapshot path, and current code identity.
- `manifests/revision_v1/freeze_candidate_v1.json`: refresh corresponding script/source-tree/recipe/resource bindings.

All new helpers and their five regression tests already exist. The proposed builder was loaded in memory and compared with the owner factory using a metadata-only base stand-in. Every adapter identity field and tokenizer hash matches; the reader parameter hash also matches the completed training summary. Base execution calls: zero. All candidate bindings were checked against current or proposed file bytes. `git apply --check` passes. Evidence: `logs/r1_round11/repair_v2_preview.json`; full in-memory repair test output: `logs/r1_round11/proposed_repairs_cpu.txt`.

The original installed suite passed 479 tests with 8 skipped before the five added helper tests. The installed recipe/candidate are intentionally not rebound until approval; their earlier inspection/generation logs are historical. The new checkpoint helper also changes the installed code tree, so the current recipe must not be executed before the rebinding repair. No actual protocol freeze, dataset release, model parameter change, source rewrite or commit is included.

After approval: compare the five before-hashes with `repair_v2_preview.json`, apply the v2 patch only, verify installed Ruff and the new CPU tests, re-inspect the recipe and validate all candidate bindings, and write new completion evidence. Expected patched recipe SHA: `5b9bca5dc360effafadee9a858dd3c1ebc540372f7c763ab33145d570573eb56`; expected candidate SHA: `d263760b97449045575d85f8568a3c1e1964b3974ed6973d9bda8d6d0f4dd8df`. Check actual hashes rather than assuming them if another agent changes the tree.
