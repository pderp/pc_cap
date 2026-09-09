# CAP-05 Routers
status: done
agent: orchestrator   started: 2026-09-10T01:10:00Z   finished: 2026-09-09T19:27:40Z
commit: (this commit)
inputs used: PDF F.3 steps 3-4, PC-5, SD-4, SD-11; S0-05 transport; CAP-04
outputs: src/pccap/routers/{__init__,_common,last,full,measured,random_,supplied}.py, src/pccap/cap/cap.py (cap core: sequential live-retrieval edited forward, predict, state, memory), bases: forward_from now returns retained residuals, tests/controls/test_pc5_probe.py, tests/routers/test_routers.py, tests/cap/test_cap_core.py
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/controls/test_pc5_probe.py tests/routers/ tests/cap/test_cap_core.py -m gpu
verify output: 8 passed (analytic probe, ties, no_direction logging, CR item-keyed replay, Last/Full/Supplied, real-cap probe read-only and charged, cap-off identity exact, predict read-only/clone/serialize)
done-when check: helpful probe positive / harmful negative on an analytic loss: PASS; abstention below threshold: PASS; CR reproduces the same choice for the same key across reversed-order replays: PASS; no learner state change after a probe (hash equal): PASS; ledger records the probe forwards (partial forwards + router_probes): PASS
cost: gpu_seconds=15 wall_seconds=3000 peak_mem_mib=1300
deviations: the probe function is injected into Measured by the cap (the RoundContext stays free of state, SD-4); tie rule "ties by depth" read as smallest bank index (SD-16, both readings recorded in docs/spec_defects.md). Cap core (cap.py) landed here because Measured needs live downstream retrieval.
unresolved: none
questions for lead: none
