# REF-01 — new-file-only reference fixture preparation

status: partial — paused for permission to edit the newly added test file
agent: codex
started: 2026-09-09T23:27:39.452885+00:00
paused: 2026-09-09T23:41:03.405118+00:00
commit: none; no commits, staging, merges, pushes or worktrees created

Inputs used: ongoing2.md REF-01; ongoing.md REF-01 specification and DEC-001–005; read-only DATA-00 manifest and local GPT-2/zsRE assets; existing oracle consumers in tests/bases/test_bp_base.py and tests/data/test_decode.py.

New files added:

- `scripts/make_reference_fixtures.py`: standalone CPU HF generator, streaming non-pickled NPZ, existing-consumer-compatible keys, exact input hashes, pre-ln_f hooks, raw greedy cache/no-cache comparison, and read-only verification; refuses output overwrite.
- `tests/reference/test_reference_fixtures.py`: eight CPU controls, seven passing and one cleanup assertion requiring correction.
- `docs/tasks/REF-01.claim.json`: additive task claim instead of modifying the shared board.
- `docs/tasks/REF-01-test-correction.patch`: exact proposed test edit, not applied.
- `results/REF-01/hook_diagnostic.json`: isolated diagnostic establishing the cause.
- `results/REF-01/verification_attempt_1.txt`: command, observed failure, lint and dependency-install results.
- This task record.

External resources created: `assets/envs/ref-torch-cpu/` (Python 3.12.14, torch 2.11.0+cpu, Transformers 5.13.1, NumPy 2.5.3, pytest 9.1.1); isolated temporary install/test files under `assets/tmp/ref01/`. The existing JAX/FabricPC venv and both reference repositories were not modified.

Verify command: see `results/REF-01/verification_attempt_1.txt`. Result: **7 passed, 1 failed**. The failing assertion checks that no block hooks remain *after* the independent Transformers `output_hidden_states=True` call. Diagnostic evidence shows our capture leaves none; Transformers itself subsequently installs persistent output-capture hooks. The proposed patch checks immediate cleanup and preservation of third-party hooks on a second capture. It changes only the newly added test; the generator needs no corresponding edit.

Done-when: script and CPU environment exist; production fixture generation, hashes/manifest and final verification remain pending. No 256-prompt oracle or `manifests/reference.json` has been produced yet. No HF/JAX parity claim is made.

Cost: gpu_seconds=0. This is CPU implementation and testing only, no scientific stage run. No GPU lease was touched. Existing reports, shared task/status manifests, source files and git index were not intentionally written by this lane.

Permission requested: apply `docs/tasks/REF-01-test-correction.patch` to `tests/reference/test_reference_fixtures.py`, rerun the controls, and continue producing the new REF-01 artifacts. The user requested permission before any existing-file edit, so no correction has been applied. All subsequent logs/reports can use new filenames; existing reports need not be overwritten.

## Orchestrator integration note (2026-09-10)

Fixtures are present at `assets/reference/gpt2/` (`logits_256.npz` 598 MB, `lengths.npz`, `greedy_8.json`, `ref_env.json`; torch 2.11.0+cpu, transformers 5.13.1, fp32, eager attention, deterministic) with `manifests/reference.json` recording input hashes. The consumer tests in the main tree pass against them: `tests/bases/test_bp_base.py::test_a_hf_oracle` (max |Δlogit| 3.97e-4, argmax 2,802/2,802, sites 2.48e-4) and `tests/data/test_decode.py::test_bp_decode_vs_hf_oracle` (8/8 token-for-token). Codex's own controls `tests/reference/` pass 8/8 in the reference env, so `REF-01-test-correction.patch` is superseded (it no longer applies) and was not needed. Status set to done on the board. No commits made.
