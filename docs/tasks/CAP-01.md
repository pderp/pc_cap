# CAP-01 Key features and deterministic retrieval
status: done
agent: orchestrator   started: 2026-09-09T22:50:00Z   finished: 2026-09-09T19:12:03Z
commit: (this commit)
inputs used: PDF F.1; plan §6.3 CAP-01; contracts v0
outputs: src/pccap/cap/{features,bank}.py, tests/cap/{test_features,test_retrieve}.py
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/cap/test_features.py tests/cap/test_retrieve.py
verify output: 13 passed in 0.30s
done-when check: unit-scale keys at widths 32/768/1024: PASS; boundary inclusive: PASS; tie -> smallest id: PASS; zero radius exact only: PASS; zero vector handled (zero key, no NaN): PASS; retrieval identical across 100 insertion-order shuffles: PASS
cost: gpu_seconds=0 wall_seconds=900 peak_mem_mib=0
deviations: bank arrays are host-side float32 NumPy (byte-exact snapshots); radii/active will move into the 128-byte metadata record in CAP-02 so there is one source of truth.
unresolved: none
questions for lead: none
