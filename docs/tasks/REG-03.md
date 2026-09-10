# REG-03 Load and preflight
status: done
agent: orchestrator (automatic chain)   started: 2026-09-10T23:24:28Z   finished: 2026-09-10T23:24:40Z
commit: (uncommitted; lead commits)
inputs used: REG-02 final checkpoint; S0-06 ePC wrapper; plan §6.4 REG-03; R2-08 validity gate
outputs: results/REG/preflight.json; manifests/assets.json `assets.epc_checkpoint` (status regenerated, sha256 ea4c561d3963ffd8…, provenance); src/pccap/distill/preflight.py
verify command: /home/derp/cap/venv/bin/python -m pccap.distill.preflight --checkpoint /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766 --update-assets
verify output: validity {'params_finite': True, 'config_equal_to_teacher': True, 'capoff_identity_ok': True, 'energy_descent_ok': True, 'prompt_kl_below_abort': True, 'dtype_float32': True} → valid. Parameters finite, float32, config equal to the teacher; relative parameter shift 4.46e-04; cap-off identity of the ePC wrapper (graph derive vs functional forward) max |Δ logit| = 0.0; energy non-increasing over 8 iterations on 8 prompts; prompt KL (β = 2, ×4) 6.84e-06; unseen OpenWebText tail (49,664 positions): KL(teacher‖student) at β = 1 1.41e-05, sibling scaling (β = 2, ×4) 4.60e-05 vs the sibling's inherited 1.24e-4; teacher NLL 3.22637, student NLL 3.22635.
done-when check: results/REG/preflight.json exists and the S1 ePC rows become ready: PASS (S1-01 and the ePC rows run in the same chain).
cost: gpu_seconds=12 wall_seconds=12 peak_mem_mib=0
deviations: the identity criterion is the S0-06 test's 1e-4 (two different code paths), stated in the file; the KL "smoke figure" uses ~50k tail tokens as specified.
unresolved: none
questions for lead: none
