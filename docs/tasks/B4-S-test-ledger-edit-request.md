Status: prepared; awaiting permission.

The newly added batch test used Ledger.report() in three places; the actual API is Ledger.totals(). Two controls fail before exercising the ledger assertions. The two numerical/state batch cases and five existing GRACE controls passed.

Proposed edit: apply B4-S-test-ledger-fix.patch to tests/baselines/test_grace_batch.py only. No production code, tolerance or model changes.

Pre-edit SHA256: a814bd42c89a734dcf98ec98c81f53ccd8b432ef2112490bd12a1e2786bd3f72

Verify: rerun both GRACE test files on CPU with an external fresh pytest fixture root.
