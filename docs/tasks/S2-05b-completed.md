# S2-05b — GRACE reference fixtures completed

status: done (reference fixture generation; shared board update pending permission)  
agent: codex  
recorded_utc: 2026-09-10T13:58:57+00:00  
commit: none

Inputs: the prepared [selection](../../manifests/dev/grace_parity_selection.json), source/model pins and verified environment described in [S2-05a completion](S2-05a-completed.md).

The unchanged oracle generated the twenty selected cases: ten single-token and ten multi-token answers, excluding S0 items. Each case was edited in isolation; the same cases were then edited in sequence and all twenty evaluated at the final codebook. All twenty isolated and all twenty final sequential evaluations matched their canonical complete answers. Every isolated run and the final sequence preserved the base-parameter hash. The final sequential codebook has twenty entries.

The [final manifest](../../manifests/dev/grace_parity_cases.json) records **63 artifact hashes and sizes**, input hashes, environment/configuration, source script, seeds, command and cost. SHA-256 of that manifest: 05e640c00671449f8d739fc5dbd00431494b7f9e9568001f40776640fac6338a.

Resource artifacts are under /home/derp/cap/assets/reference/grace:

- environment.json;
- twenty isolated result JSON files and twenty matching codebook NPZ files;
- twenty sequential codebook snapshots;
- sequence_final.json with update histories and all final evaluations.

The 63-file inventory additionally includes the project smoke log. NPZ files include keys, values, radii and full labels, load without pickle, and pass fp32/dimension/finiteness checks. No placeholder artifact hashes are present.

Verify command, from /home/derp/cap/pc_cap:

    PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
      /home/derp/cap/venv/bin/python -B scripts/grace_reference_oracle.py --check

Result: verified; 20 cases; 10 single-token; 10 multi-token; 5 smoke successes; 20 final sequential keys; 63 files. [Exact verification log](../../results/grace_lane_d/reference_verification_resumed.txt). Generation exited 0; [generation log](../../results/grace_lane_d/reference_generation_resumed.txt).

Cost: GPU **0 s**; generator **246.166 s** internal wall time, **248.211 s** including launcher overhead, with two CPU threads. This includes the shared S2-05a smoke; count the interval once.

Done-when: all prepared cases have isolated and sequential outputs, full codebooks and greedy/NLL evidence; inputs/outputs rehash correctly. **These are source-reference fixtures, not a completed JAX parity result.** The next owner implements the JAX adapter and runs PC-10 with eviction disabled, then separately tests the declared bounded adaptation.

Unresolved: no reference-generation blocker. Shared task-board status remains partial until the [requested metadata edit](S2-05ab-status-edit-request.md) is approved or mirrored by the orchestrator. Existing source/docs/environments/clones were untouched; all this lane's project changes are new files. No commit.
