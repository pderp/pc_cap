# CAP-06 Transactional candidate search and budget
status: done
agent: orchestrator   started: 2026-09-10T01:40:00Z   finished: 2026-09-09T19:35:42Z
commit: (this commit)
inputs used: PDF F.3 steps 5-6, PC-5/6; CAP-04/05; contracts.Budget
outputs: src/pccap/cap/learn.py::round_update, tests/controls/test_pc5_search.py, tests/controls/test_pc6_budget.py, tests/cap/mock_base.py (CPU mock base with the Base contract)
verify command: JAX_PLATFORMS=cpu /home/derp/cap/venv/bin/python -m pytest -q tests/controls/test_pc5_search.py tests/controls/test_pc6_budget.py
verify output: 5 passed (in the 200+ of test-fast)
done-when check: non-monotone analytic loss does not crash and does not assume bracketing (picks the minimum of the four candidates): PASS; accepted state equals the evaluated candidate byte-for-byte: PASS; rejected search restores exactly (hash equal, allocations rolled back) and is charged (4 candidates per bank, forwards in the ledger): PASS; aggregate increment <= A on 100 random rounds: PASS; C0/C1/C2/CR share the byte ceiling: PASS
cost: gpu_seconds=0 wall_seconds=3600 peak_mem_mib=0
deviations: candidates are evaluated by setting the slot value from the same snapshot (not cumulatively) inside one open transaction; a bank whose conflict resolution rejects it (ambiguous key) is skipped with its code; the no-op is the implicit baseline.
unresolved: none
questions for lead: none
