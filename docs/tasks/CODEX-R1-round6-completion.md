# Codex round 6 — approved correction and completion

- **Status:** complete for the five assigned CPU lane deliverables; the prior handoff's test-permission hold is resolved.
- **Agent/date:** Codex, 2026-09-14.
- **Authorization:** the user approved the exact two-line test correction with “yes, go ahead.”
- **Existing file changed:** `tests/revision_v1/test_round6_register_matrix.py` only. The normalized-subject assertion now applies to the raw candidate inventory; the clear-survivor inventory retains its source-index exclusion, checksum and count checks.
- **Inputs:** the hash-bound proposal `R1-round6-test-repair.patch` and existing register/matrix artifacts.
- **Outputs:** corrected test; `logs/r1_round6/register_matrix_approved_cpu.txt`; `test_repair_ruff_check.txt` and `test_repair_ruff_format.txt` in that directory; this additive completion and its JSON record.
- **Verify command:** `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= /home/derp/cap/venv/bin/python -m pytest -q -p no:cacheprovider tests/revision_v1/test_round6_register_matrix.py`.
- **Verify output:** **24 passed in 2.29 s**. Ruff check and format check also pass for the corrected file.
- **Done-when:** exact approved patch applied; complete affected suite passes; no other files from the prior owned-file inventory changed.
- **Cost:** GPU 0 s; no base/teacher execution, data draws or sealed-payload reads.
- **Deviations:** none.
- **Unresolved:** none for this correction. Scientific, data, profiling and owner-source gates documented in the prior handoff remain; completing a draft or review does not admit final confirmation.
- **Questions for lead:** none needed for this completion.

## Updated round status

R1-D3 candidate selection, R1-45 lexical analysis, R1-46 training review/recheck, R1-D1e exclusion register v3 and R1-40b matrix v2 are delivered. R1-D3's 12 tests and R1-45's 14 tests passed in the preceding turn; the repaired register/matrix suite now passes all 24. Thus all **50 round-6 tests pass across the recorded lane runs**. Only the affected 24-test suite was rerun for this correction.

This record supersedes the pending-permission and pending-test statements in [the original handoff](CODEX-R1-round6-handoff.md), its JSON inventory, R1-D1e/R1-40b task records and the edit request. Those historical files and their original evidence remain unchanged. The companion completion JSON supplies the updated test-file hash.

The current learned-primary matrix remains unfrozen and unlaunchable. No production code or research artifact was altered for this test correction. No files were staged or committed.
