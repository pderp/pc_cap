Status: completed — the approved five-file B4 batch integration and test correction are applied.

Agent: Codex. Authorization: the lead's “yes, go ahead please” approved B4-S-batch-edit-request.md. This completion record supersedes that request's pending status and the earlier round record's two failing test controls. Those historical files and their evidence remain unchanged.

Inputs: the four approved patches, their verified source-hash preconditions, the fixed final 20-entry GRACE source codebook, and the existing scalar query implementation.

Changes:

- src/pccap/baselines/grace_jax.py now delegates last_logits_batch to the vmapped helper.
- src/pccap/baselines/grace_adapter.py exposes the canonical GraceLearner import.
- tests/baselines/test_grace_batch.py uses Ledger.totals() and an explicit scalar-predict comparison oracle.
- scripts/grace_batch_smoke.py also retains the independent scalar-predict oracle after integration.
- src/pccap/baselines/grace_batch.py has updated integration docstrings.

The helper preserves ragged sequence order, explicit original-prompt key positions, per-phase ledger charges and the inherited learner state interface. All five pre-edit hashes matched the approved request. Only those five existing files were edited; the verification driver, results and this completion record are new files.

Outputs: [application receipt](../../results/S2/grace_jax/batch_applied/application.json), [tests](../../results/S2/grace_jax/batch_applied/tests.txt), [canonical adapter verification](../../results/S2/grace_jax/batch_applied/canonical_verification.json), [full-size comparison](../../results/S2/grace_jax/batch_applied/canonical_smoke.json), and [lint](../../results/S2/grace_jax/batch_applied/lint.txt). New reproducible driver: scripts/grace_batch_verify_applied.py. SHA256 inventory: B4-S-batch-applied.outputs.json.

Verification:

- Existing GRACE tests, new batch tests and harness boundary controls: 11 passed in 1.65 seconds. The earlier 7-pass/2-failure log is retained as historical evidence.
- Canonical import identity and actual delegation to the batch helper: pass.
- Full-size canonical query path: all 20 cases / 61 teacher-forced answer prefixes pass against direct scalar predict() calls. Maximum summed-answer NLL difference: 1.902733e-7. Teacher-forced argmax agrees throughout; this does not claim free-generation or training parity.
- Maximum logit absolute difference: 0.000457764. Every element passes the declared combined tolerance (absolute 0.0002, relative 0.00002); the maximum absolute gap alone is not the pass criterion. NLL uses the unchanged absolute 0.001 / relative 0.0001 tolerance.
- Base checksum and complete learner state are unchanged by the comparison. Approved source hashes were stable during verification.
- Ruff passes for the five changed files and the new verifier; git diff --check passes. The Git index is unchanged.

Reproduction from pc_cap uses the active ../venv/bin/python -B with PYTHONDONTWRITEBYTECODE=1, CUDA_VISIBLE_DEVICES='', JAX_PLATFORMS=cpu, OPENBLAS_NUM_THREADS=2 and OMP_NUM_THREADS=2. Tests: python -m pytest tests/baselines/test_grace_jax.py tests/baselines/test_grace_batch.py tests/harness/test_b4_wiring.py -q -p no:cacheprovider --basetemp=../assets/tmp/codex_b4_batch_applied. The canonical verification ran scripts/grace_batch_verify_applied.py. Its outputs are exclusive run artifacts; a repeat must select a new output directory. Test fixtures live outside the repository.

Done-when: the approved edits are applied and verified through the canonical adapter. No further approval is needed for this edit set.

Cost: CPU only; GPU seconds = 0. Unit/boundary tests took 1.65 seconds; the full-size smoke took 3.59 seconds. Operations ran concurrently, so these are per-operation elapsed times.

Deviations: none from the approved patches. No staging, commits, environment changes, shared-board edits, manifest edits, or S7 code edits.

Unresolved: DEC-020's sensitivity prerequisite is still unmet. B4 remains unregistered and PC-10 form (b) / S3-01 completion remain blocked. The batched interface completes the engineering integration step; it does not establish the missing scientific condition. The next B4 diagnosis is to localize the first cross-framework gradient difference. Claude retains the S7 repairs documented in logs/review_p4_s7.md.

Questions for lead: none for this completed edit set.
