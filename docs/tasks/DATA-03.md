# DATA-03 MODULAR-CONTROL fixture
status: done
agent: orchestrator   started: 2026-09-10T07:10:00Z   finished: 2026-09-10T01:23:33Z
commit: (uncommitted; lead commits)
inputs used: PDF E.1 MODULAR-CONTROL, D.10, PC-1; contracts Base protocol; cap (CAP-01..07), Transport projection (S0-05), Supplied router (CAP-05)
outputs: src/pccap/fixtures/modular_control.py (ModularControlBase implementing the Base contract, ItemSpec, ProjectedTransport, learn_and_score, manifest), manifests/fixtures/modular_control{,_wrong_router,_no_sharing}.json (masks, sites, allowed subspaces, R*, 420 items incl. 60 held-out combinations), tests/fixtures/test_modular_control.py, tests/controls/test_pc1_planted.py, results/S0/controls/{pc1_planted,pc1_full_fixture}.json
verify command: JAX_PLATFORMS=cpu /home/derp/cap/venv/bin/python -m pytest -q tests/controls/test_pc1_planted.py tests/fixtures/test_modular_control.py
verify output: 7 passed. PC-1: CO (supplied router) recovered 20/20 planted targets within the round budget (A = 1.0, R = 5, exact keys) with unrelated outputs unchanged (max |dp| = 0.0); full fixture oracle 120/120 (= 100% >= 95%); wrong-router variant 1/30 recovered (fails as designed).
done-when check: small residual graph (d = 32) with three module groups at the three write depths, fixed masks routing private latents only through their path and shared latents through the explicit shared path (tests): PASS; output coordinates partitioned so a permitted write at one site cannot directly change other sites' classes: PASS; fixed allowed write subspace per bank applied to every arm through ProjectedTransport (projection before normalization): PASS; oracle routes supplied only to CO (RoundContext.permitted_banks): PASS; >= 100 private, >= 100 shared, >= 100 mixed-cause items plus held-out combinations; no-sharing, useful-sharing and wrong-router variants; masks, sites and R* recorded: PASS; supplied router >= 19/20 with unrelated unchanged within 1e-6: PASS (20/20, 0.0); full-fixture oracle >= 95%: PASS (100%); wrong-router fails as designed: PASS
cost: gpu_seconds=0 wall_seconds=3600 peak_mem_mib=0
deviations: the fixture's "vocabulary" is 20 output classes read from disjoint coordinate groups (private 4 x 3, shared 4, mixed 4); items are single-position latent vectors (ids index the latent table); the fixture budget is A = 1.0 with exact keys (its own manifest, not the GPT-2 defaults). Mixed items for bank 3 require joint coverage of bank 3 and a shared-path bank.
unresolved: none
questions for lead: none
