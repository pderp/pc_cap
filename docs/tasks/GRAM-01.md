# GRAM-01 Grammar generator per E.1
status: done
agent: orchestrator   started: 2026-09-10T14:20:00Z   finished: 2026-09-10T15:05:00Z
commit: (uncommitted; lead commits)
inputs used: PDF E.1 LATENT-GRAMMAR, plan §6.5 GRAM-01; DEC-010/PA-2 (replacement fixture)
outputs: src/pccap/fixtures/grammar_generator.py (vocab 64 = PAD, BOS, 8 context tokens, 54 content tokens in six classes; length 64 with the context token at 0/16/32/48; class chain 0→1→2→3→4→5→0; shared switch 1 = successor permutation on class 1, shared switch 2 = copy at lag 6/12 on class 3, private switch = context-specific permutation on class 4; designated evaluated position sampled in 48–63 where the requested mechanism fires; label (kind, context); `rule_target(prefix)` recomputes the forced token; balanced five orders by rotation-3 of a realization-seeded permutation), manifests/grammar/generator.json (rule tables, seed ranges, orders, sha256 of a 1,000-sequence sample 83e7cdc9d3c6e4ab…), tests/fixtures/test_grammar_generator.py
verify command: /home/derp/cap/venv/bin/python -m pytest -q tests/fixtures/test_grammar_generator.py
verify output: 6 passed — private flip changes only its context (>80/100 sequences of that context, 0 elsewhere); each shared flip changes its mechanism in every context (>50/60); context observable; target at p* equals `rule_target(prefix)` for every kind; orders balanced (each task in positions {0,1} and {6,7} across the five orders, all three realizations); regeneration byte-identical (sample hash).
done-when check: all five verify clauses of plan §6.5: PASS
cost: gpu_seconds=0 wall_seconds=2400 peak_mem_mib=0
deviations: the copy mechanism's first one or two class-3 tokens (no antecedent) are random and not counted as mechanism firings; the flipped private permutation coincides with the default at a few entries, so ~10% of private-labelled sequences are unchanged by the flip (still deterministic).
unresolved: none
questions for lead: none
