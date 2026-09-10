# HARN-C2 C2 probe binding and general stream runner
status: done
agent: orchestrator   started: 2026-09-10T06:00:00Z   finished: 2026-09-10T01:19:57Z
commit: (uncommitted; lead commits)
inputs used: CAP-05 Measured router, CAP-07 update_item, S0-08 ItemGuard, S2-01/S2-02 calibration, DATA-01 pools, DATA-04 drift tokens; PDF D.8, E.2, App. B, SD-4
outputs: src/pccap/routers/measured.py (bind_probe), src/pccap/cap/learn.py (binds the probe per round), src/pccap/harness/runs.py (Evaluator, run_stream), src/pccap/harness/stage_s3.py (registered "S3"), manifests/dev/s3_smoke.json, results/S3/{C2,C0,C1,CR}/BP/h/0/0/
verify command: /home/derp/cap/venv/bin/python -m pccap.cli run --stage S3 --arm C2 --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s3_smoke.json
verify output: complete; 20 zsRE dev edits, C2 A=0.3 zsRE radii: ES 1.00, GS 0.80, threshold 1.00, RET-ES(end) 0.95, RET-GS(end) 0.70, LS complete-answer 1.00 (50 prompts), LM drift perplexity ratio 1.000 on a 512-position sequential sample, 92 rounds, routes bank3 88 / bank1 2 / bank2 2, 0 abstentions, 276 probes charged, 108 s wall (15 s learning + 9 s query accelerator time)
done-when check: the C2 router receives its probe loss oracle from round_update (labels enter credit during learning; RoundContext still carries no target/digest; PC-4 router test unchanged): PASS; all four routing arms run through pccap run --stage S3: PASS (C0/C1/CR smoke in results/S3); per-item ES/GS/NLL, checkpoint rescoring (RET-ES/RET-GS, conditional survival), LS (complete-answer, first-token, fixed-prefix KL), LM drift (perplexity ratio, mean loss difference), memory, checkpoints under assets/runs, ledger cost.json: PASS; resource-stop rollback path via ItemGuard: implemented (exercised by the S0-08 test)
cost: gpu_seconds=60 wall_seconds=3600 peak_mem_mib=1500
deviations: LM drift per run uses a fixed sequential full-recompute sample (default 4,096 positions) of the validation split rather than the whole 247k-token split, because the exact E.2 semantics (full recompute per position, cap at the current position) cost one forward per token; a parallel per-position variant for the whole split will be added only after parity with the sequential semantics is verified (E.2 allows this).
unresolved: S2-06 must measure the true per-item cost: at this evaluation density the 20-item smoke took ~5 s per item wall, dominated by evaluation.
questions for lead: none
