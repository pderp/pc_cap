# Round-6 test correction — approval requested

The newly added test incorrectly expects the clear-survivor provenance inventory to contain normalized subjects. That inventory deliberately stores source indices and hashes; only the raw candidate inventory contains subject keys. The artifacts themselves passed their generation checks.

Proposed change: move the normalized-subject assertion into the raw-candidate branch. Keep the clear-survivor index exclusion, hash and count checks. This is a two-line relocation in `tests/revision_v1/test_round6_register_matrix.py`; no production or manifest changes.

- Exact patch: `docs/tasks/R1-round6-test-repair.patch`.
- Original test SHA-256: `689b15049586515d335931ce9e811754b6d377b2b820ac52cd5dc71f4cd36d68`.
- Proposed corrected assertion passed against the actual artifacts in memory: `logs/r1_round6/proposed_test_repair_validation.txt`.
- Initial suite: 23 passed, 1 failed because of this test's schema assumption. Full rerun follows approval.
- Permission reason: the user's new-files-only rule requires permission to edit an existing file, including this test already created during the round.
