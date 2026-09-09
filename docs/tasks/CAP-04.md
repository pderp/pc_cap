# CAP-04 Transactions, conflicts, eviction, revisions
status: done
agent: orchestrator   started: 2026-09-10T00:10:00Z   finished: 2026-09-09T19:20:06Z
commit: (this commit)
inputs used: PDF F.2, F.5 PC-4; SD-4; CAP-03; S0-08
outputs: src/pccap/cap/transaction.py, tests/controls/test_pc4_conflict.py
verify command: JAX_PLATFORMS=cpu /home/derp/cap/venv/bin/python -m pytest -q tests/controls/test_pc4_conflict.py
verify output: 7 passed (with tests/cap: 36 passed)
done-when check: distinct-key conflict preserves old key/value, radii >= 0, radii shrunk to 0.49*d_qs, retrieval recomputed: PASS; identical-key ambiguity rejects and logs ambiguous_key_conflict, old memory intact after rollback: PASS; newer version replaces (revision_replaced), same version replays idempotently, same version with a different target is ambiguous, revision metadata ignored off the correction track (SD-4): PASS; failed replacement rolls back values, metadata, radii, ids, index, use set and RNG byte-exactly: PASS; deterministic eviction (lowest use_count, oldest last_use, smallest id): PASS; eviction commits only with a successful write: PASS; RoundContext carries no slot metadata / digest / answer fields: PASS
cost: gpu_seconds=0 wall_seconds=2400 peak_mem_mib=0
deviations: the correction index is per bank (bounded by the bank capacity, 24 bytes/entry, counted in memory); the "same version replayed" code is emitted only for an exact replay (same version and same target); a same-version different-target event is ambiguous by construction.
unresolved: none
questions for lead: none
