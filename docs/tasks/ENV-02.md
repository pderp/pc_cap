# ENV-02 Shared-workload benchmark and kappa
status: done
agent: orchestrator   started: 2026-09-10T00:05:00Z   finished: 2026-09-09T19:20:06Z
commit: (this commit)
inputs used: ENV-01 venv; DATA-00 GPT-2; PA-3; plan §6.1 ENV-02
outputs: scripts/bench_shared_workload.py, results/ENV/bench.json, results/ENV/kappa.json
verify command: /home/derp/cap/venv/bin/python scripts/bench_shared_workload.py --check
verify output: (both files reload and print; numbers below)
done-when check:
- both files exist: PASS
- bench ran with the GPU lease held (exclusive) and nvidia-smi compute apps captured before/after: PASS — but NOT with "no other CUDA process": the desktop processes kwin_wayland (70 MiB), Chrome GPU process (244 MiB) and swipl (1,526 MiB) were resident throughout (plan §2 and §11 anticipate this). They are recorded in bench.json lease.compute_apps_{before,after}; the measurement is labelled "shared desktop" and kappa stays provisional (PA-3).
- measured: fp32 forward+backward batch 8x128 steady state 19747 tokens/s (0.0519 s/step, 1158 steps in 60 s); batch-1 forward latency median/p95 ms: 16 tok: 1.60/1.70, 32 tok: 1.75/1.83, 64 tok: 2.12/2.22; peak device memory 2585 MiB.
- kappa = 1.0, band [0.5, 2.0], status provisional (PA-3); no A100 measurement.
cost: gpu_seconds=110 wall_seconds=600 peak_mem_mib=2585
deviations: forward+backward is a full-parameter gradient of the mean next-token CE (the "shared workload"); desktop GPU processes could not be evicted (not ours to kill); recorded rather than hidden.
unresolved: none
questions for lead: none
