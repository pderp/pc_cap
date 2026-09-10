# REG-02 Full regeneration
status: done
agent: orchestrator   started: 2026-09-10T11:03:59Z   finished: 2026-09-10T23:24:23Z
commit: (uncommitted; lead commits)
inputs used: REG-00 driver (with the float32 fix), REG-01 decision (DEC-015), DEC-014 (120 GPU-h bound), OpenWebText shard (byte-exact), sibling protocol (seed 1729, batch 10×512, homotopy T ∈ {1,2,4,8,16,32,64}, AdamW 1e-6)
outputs: assets/models/epc/epc-50m/checkpoints/final-009766/params.npz (sha256 ea4c561d3963ffd8…) + Adam state + state.json; stage checkpoints at 1396/2791/4186/5581/6976/8371; results/REG/epc-50m/{metrics,relaxation,milestones,holds}.csv, summary.json, epc-50m.log; results/REG/run_reg02_v2.sh (chunked, pausable runner); scripts/reg_wait_complete.py
verify command: /home/derp/cap/venv/bin/python scripts/reg_wait_complete.py --once ; /home/derp/cap/venv/bin/python scripts/reg_pilot_compare.py --run epc-50m --steps 9766
verify output: status completed, 9,766 steps, 50,001,920 tokens; GPU 12.18 h (elapsed 12.22 h) in 25 chunks with 18 process restarts (all resumed from checkpoints; contiguous steps); no holds, no subdivisions, no non-finite values; stage boundaries identical to the sibling's realized run; median s/step by T {1: 0.71, 2: 0.94, 4: 1.38, 8: 2.26, 16: 3.99, 32: 7.48, 64: 14.47}; KD-loss mean over steps 2–9765 ours 1.358e-04 vs sibling 1.272e-04 (median per-step ratio 1.029); 51 milestones, prompt KL max 3.23e-05, terminal 6.84e-06 (sibling terminal 5.8e-6), terminal held-out perplexity 92.8612 (sibling 92.8588; teacher 93.3409).
done-when check: the full 9,766-step protocol completed within the DEC-014 bound (12.2 GPU-h of 120): PASS; resumable chunks with the lease released between them: PASS; milestones and stage statistics consistent with the sibling's log: PASS; the checkpoint is a NEW substrate (PA-1; no continuity with the missing original): stated.
cost: gpu_seconds=43858 wall_seconds=44006 peak_mem_mib=7816
deviations: four pause windows for other GPU work (baseline throughput, CR re-profile, learning-rate screen, GPU tests) and deadline-ended chunks in the T = 64 stage; the automatic post-run chain was re-armed once (R2-01) on a terminal-state waiter.
unresolved: none (REG-03 follows in the chain)
questions for lead: none
