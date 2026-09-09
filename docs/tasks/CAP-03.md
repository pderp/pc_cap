# CAP-03 Byte ceiling and capacity
status: done
agent: orchestrator   started: 2026-09-09T23:30:00Z   finished: 2026-09-09T19:15:32Z
commit: (this commit)
inputs used: PDF App. B "Memory ceiling"; PC-6; plan §6.3 CAP-03
outputs: src/pccap/cap/memory.py, tests/cap/test_memory.py
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/cap/test_memory.py
verify output: (in the 29 passed of tests/cap)
done-when check: nominal upper bounds 6,144 / 2,048 / 1,374 at zero overhead: PASS; actual capacities <= nominal and reported (overhead 10,000 B -> 2,046): PASS; wide keys reduce capacity: PASS; sum of bank ceilings == B_cap for C0/C1/C2/CR/CO: PASS
cost: gpu_seconds=0 wall_seconds=600 peak_mem_mib=0
deviations: none
unresolved: none
questions for lead: none
