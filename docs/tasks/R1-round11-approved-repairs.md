# Round 11 approved repairs — completion

Status: the user-approved five-file repair is applied and verified. Agent: Codex. This record supersedes the pending-repair status in the round-11 handoff, task reports and v2 edit request. No commit was made.

Applied `R1-round11-snapshot-bindings-v2.patch` exactly after checking every approved before-hash. All five resulting hashes match the prepared preview. The payload builder now uses the verified regular-file snapshot and preserves list-indexed checkpoint layers when computing the reader identity. The development code identity includes the materialization helper, and the worked recipe and candidate freeze bindings are refreshed. The existing sealed runner was unchanged.

Installed validation: **484 passed, 8 skipped in 55.15 s**. Ruff passes for all eight production files. Recipe inspection succeeds with 300 development items and checkpoints 100/300. All **225 live candidate bindings** match, and the candidate's complete `src/pccap` inventory/tree hash matches the installed tree. The installed builder's configuration and checkpoint hashes agree with the worked recipe, the owner factory with a metadata-only base stand-in, and the completed training summary. The tokenizer matches, and all bound snapshot children are regular files. Base execution calls and GPU seconds: zero.

Current recipe SHA: `5b9bca5dc360effafadee9a858dd3c1ebc540372f7c763ab33145d570573eb56`. Current candidate SHA: `d263760b97449045575d85f8568a3c1e1964b3974ed6973d9bda8d6d0f4dd8df`.

```bash
cd /home/derp/cap/pc_cap
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  /home/derp/cap/venv/bin/python -m scripts.r1_64_dev_cell \
  --manifest docs/tasks/R1-64-zsre-v4.recipe.json \
  --manifest-sha256 5b9bca5dc360effafadee9a858dd3c1ebc540372f7c763ab33145d570573eb56
```

This command inspects the unsealed development recipe without model execution. Final scientific admission is unchanged: the candidate is not a freeze, U01–U18 admission remains open, and MQuAKE population capacity remains unresolved. No model, teacher, sealed-data, draw, release, freeze or launch action was performed.

One separate lint-only follow-up remains: move a blank line in `tests/revision_v1/test_checkpoint_identity.py` so NumPy is separated from the pccap import group. This test was outside the five-file permission, so it remains unchanged. `R1-round11-test-import-spacing.patch` is prepared; its nonblank lines and AST are identical, its Ruff preview passes, and it does not affect code/recipe/candidate identities. Separate permission was requested under the user's existing-file rule. The full suite passes with the current test file.

Evidence is under `logs/r1_round11/approved_repairs_20260915/`: `application.json`, `installed_cpu.txt`, `production_ruff.txt`, `ruff.txt`, `recipe_inspection.json`, `metadata_validation.json`, `test_spacing_preview.json` and `completion.json`. Original pre-repair records are retained as historical evidence. Shared task-board/lead-queue files and the pre-existing round-8 pytest directory were not changed.
