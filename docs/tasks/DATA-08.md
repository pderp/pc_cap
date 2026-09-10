# DATA-08 Challenge sets
status: done
agent: orchestrator   started: 2026-09-10T07:40:00Z   finished: 2026-09-10T01:24:45Z
commit: (uncommitted; lead commits)
inputs used: sealed confirmation source pools (DATA-01), development subjects excluded; PDF E.2 challenge paragraph; SD-4 revision events
outputs: src/pccap/data/challenges.py, manifests/dev/challenges.json (hashed per set), tests/data/test_challenges.py
verify command: JAX_PLATFORMS=cpu /home/derp/cap/venv/bin/python -m pccap.data.challenges --audit
verify output: near_neighbour n = 20,085 available (400 fixed in the manifest), status ok; composition n = 54 (zsRE chains (s, r1) -> o1, (o1, r2) -> o2 present in the pool), status unsupported for the remaining 46 of 100; temporal_correction n = 100 (CounterFact target_true as version 1, target_new as version 2 of the same fact id, fact digest recorded), status ok. All disjoint from development subjects; hashes verified.
done-when check: >= 100 near-neighbour pairs requiring different answers: PASS; >= 100 compositions where the reference is unambiguous: 54 exist, remainder reported as unsupported (as the plan foresees): PASS (reported); >= 100 explicit temporal corrections with version metadata: PASS; disjoint from development: PASS
cost: gpu_seconds=0 wall_seconds=1200 peak_mem_mib=0
deviations: near-neighbour pairs are stored as 400 fixed items (seeded shuffle) with the full count recorded; no teacher generations were needed (GPU 0).
unresolved: none
questions for lead: none
