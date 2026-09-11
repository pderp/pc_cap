B4-S batch integration — prepared, awaiting lead permission

This request covers five existing files. The standing new-files-only rule prevents applying these edits without permission. The earlier narrow three-line test-fix request remains valid on its own; approving this full request also includes that correction.

| File | Exact change |
| --- | --- |
| src/pccap/baselines/grace_jax.py | Delegate last_logits_batch to the tested vmapped helper; replace the stale placeholder note |
| src/pccap/baselines/grace_adapter.py | Replace the assigned placeholder with a canonical GraceLearner re-export, explicitly conditional on DEC-020 eligibility |
| tests/baselines/test_grace_batch.py | Correct three Ledger.report() calls to Ledger.totals(); make the comparison oracle explicitly loop over scalar predict(), so integration cannot make the comparison self-referential |
| scripts/grace_batch_smoke.py | Likewise retain the direct scalar predict() oracle after integration |
| src/pccap/baselines/grace_batch.py | Update two prototype docstrings to describe the integrated surface; no algorithm change |

The four exact patches are [batch integration](B4-S-batch-integration.patch), [ledger API correction](B4-S-test-ledger-fix.patch), [independent scalar oracle](B4-S-scalar-oracle.patch), and [docstrings](B4-S-batch-docstrings.patch). All pass git apply --check. Source hashes are in [preconditions](B4-S-batch-integration-preconditions.json) and the complete source_before table in results/S2/grace_jax/batch_candidate_check.json. Recheck these hashes before application because Claude is also active.

The helper groups ragged sequences by the existing scalar padding width, vmaps the unchanged GRACE query/lookup/suffix kernel, restores row order, and charges every sequence and token to the requested ledger phase. Original prompt key positions remain explicit. Learning, optimizer state, eviction, snapshot format and reference fixtures are unchanged.

Validation completed before requesting the edit:

- Two new numerical/state cases and the five existing GRACE controls passed.
- Two new controls initially failed because I called the nonexistent Ledger.report() API. Their failure log is preserved in results/S2/grace_jax/batch_tests.txt. This is my test error, not a production failure.
- The prepared test corrections and canonical delegation were exercised in memory, without editing files, by scripts/grace_batch_candidate_check.py. All four new cases passed, including phase accounting and validation. Before/after file hashes agree.
- The full-size CPU query control passed on all 20 cases / 61 answer prefixes using the fixed final reference codebook. Learner/base states stayed unchanged; NLL and teacher-forced argmax agreed. The independent scalar-oracle candidate passed again with the canonical delegation active in memory. These controls do not claim free-generation or training parity.
- New Python files pass Ruff. Both original and candidate smoke evidence remain in results/S2/grace_jax/.

After permission: apply only these patches, run the existing plus new GRACE tests, check the canonical import/delegation, and rerun the full-size query smoke into a fresh result filename. Preserve the original failed-test evidence. Do not commit or change shared board/manifests.

This approval does not register B4, change PC-10, adopt a new tolerance, or waive the failed sensitivity prerequisite. The scientific disposition is logs/grace_sensitivity_round3.md. S7 fixes remain Claude's lane.
