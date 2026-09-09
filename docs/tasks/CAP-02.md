# CAP-02 Slot metadata, use-count semantics, byte layout
status: done
agent: orchestrator   started: 2026-09-09T23:20:00Z   finished: 2026-09-09T19:15:32Z
commit: (this commit)
inputs used: PDF F.2; SD-12; plan §6.3 CAP-02
outputs: src/pccap/cap/metadata.py, src/pccap/cap/bank.py (radius/active now read from the 128-byte record), tests/cap/test_metadata.py
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/cap/test_metadata.py
verify output: (in the 29 passed of tests/cap) — layout 128 bytes with documented offsets; use_count once per (slot,item) across 3 prefixes x 5 rounds; inference view has no setters and its array is read-only; on_commit metadata + loss EMA at rate 0.2; memory report == S*(4dk+4d+128) + index bytes
done-when check: multi-prefix multi-round item increments once: PASS; inference never increments: PASS; layout is 128 bytes: PASS; memory report formula: PASS
cost: gpu_seconds=0 wall_seconds=1500 peak_mem_mib=0
deviations: slot ids are implicit indices (0 index bytes) so the plain bank's overhead is exactly zero; the correction index (CAP-04) will report its own bytes.
unresolved: none
questions for lead: none
