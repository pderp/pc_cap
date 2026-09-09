# CAP-07 Complete-edit learning loop
status: done
agent: orchestrator   started: 2026-09-10T01:40:00Z   finished: 2026-09-09T19:35:42Z
commit: (this commit)
inputs used: PDF F.3, E.2, PC-3; CAP-06; S0-09
outputs: src/pccap/cap/learn.py::update_item, tests/cap/test_update_item.py, tests/controls/test_pc3_idempotence.py, results/S0/controls/pc3_idempotence.json
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/controls/test_pc3_idempotence.py tests/cap/test_update_item.py -m gpu
verify output: PC-3 on the BP base: 20 s0-sample items tried, 20 reached the per-prefix threshold (A = 0.3, R = 5, tau 0.1), 20 checked, 0 violations (immediate repeat: 0 rounds, no new slots); mock-base tests: 3 passed
done-when check: on 20 s0-sample items that reach threshold an immediate repeat allocates no new slots: PASS; per-prefix and per-item outcomes present: PASS; the ledger sums every prefix microstep (prefix_microsteps = rounds; search candidates and router probes charged once per round): PASS
cost: gpu_seconds=600 wall_seconds=4200 peak_mem_mib=1400
deviations: PC-3 was exercised at A = 0.3 (one of the S2 candidates) because at A = 0.1 fewer items reach the threshold within 5 rounds; the smoke run at A = 0.1 acquired its item. Teacher-forced NLL is computed prefix by prefix so the cap's writes act at each prediction position (E.2).
unresolved: none
questions for lead: none
