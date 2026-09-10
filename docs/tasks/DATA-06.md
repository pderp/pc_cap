# DATA-06 Grammar task streams
status: done
agent: orchestrator   started: 2026-09-10T15:20:00Z   finished: 2026-09-10T15:45:00Z
commit: (uncommitted; lead commits)
inputs used: GRAM-01/02; plan §6.6 DATA-06; PDF E.1
outputs: src/pccap/data/grammar_streams.py (tasks = context i with private + both shared switches flipped; three realizations × five balanced orders; training counts {256, 1024, 10000} addressable by seed; evaluation 2,000 per task; held-out private-only / shared-only combinations 1,000 per task; joint-training reference with the same total count; one sequence/target pair per item), manifests/grammar/streams.json, tests/data/test_grammar_streams.py
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/data/test_grammar_streams.py
verify output: 2 passed — balance property; item count equals sequence count (no 64-way expansion); regeneration identical; realizations seed-disjoint.
done-when check: plan verify clauses: PASS
cost: gpu_seconds=0 wall_seconds=900 peak_mem_mib=0
deviations: items are addressed by generator seeds (regenerated on load) rather than materialized token files.
unresolved: none
questions for lead: none
