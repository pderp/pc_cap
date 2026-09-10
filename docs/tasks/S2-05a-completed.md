# S2-05a — GRACE reference preparation and smoke completed

status: done (completion evidence; shared board update pending permission)  
agent: codex  
recorded_utc: 2026-09-10T13:58:57+00:00  
source_tree: 80a7c9bc3c6c35e9327a689cf8cde6df2e9ddcd3  
commit: none

## Inputs and completed work

This addendum supersedes the dependency-blocked status in [S2-05a.md](S2-05a.md). The lead-approved Setuptools 78.1.0 pin was already applied by the orchestrator. No dependency was installed or replaced during this resumed work.

Used the pinned read-only GRACE clone f674183f17a995d109e10ee6140d4c3e6d016115, pinned GPT-2 snapshot 607a30d783dfa663caf39e06633721c8d4cfcd7e, and the existing development-only selection. Source/model input hashes, selection-manifest hashes and exact twenty-case order were rechecked before generation. Source GRACE/GRACEAdapter imports succeed.

All six existing reference controls passed in **1.65 s**. The five preselected smoke cases all matched the canonical target by complete greedy-answer decoding (**5/5**). No case selection, layer, radius, optimizer, evaluation convention or threshold was changed after observing results.

The environment is the existing assets/envs/grace auxiliary Python 3.10 environment, torch 2.0.0+cpu (no CUDA build), Transformers 4.20.1, NumPy 1.24.3 and wandb 0.13.2. The production environment remains JAX. The CPU reference used two intra-op threads and one inter-op thread, offline model loading and disabled tracking.

## Outputs and verification

- [Resumed input/source preflight](../../results/grace_lane_d/resumed_preflight.json).
- [Six-control result and exact command](../../results/grace_lane_d/source_controls_resumed.txt).
- [Five-case smoke log](../../results/S2/grace_reference_smoke.txt).
- [Generation log](../../results/grace_lane_d/reference_generation_resumed.txt).
- [Independent manifest verification](../../results/grace_lane_d/reference_verification_resumed.txt).
- [Twenty-case fixture completion](S2-05b-completed.md).

Verification used the existing scripts/grace_reference_oracle.py unchanged. Its --check command was run in the project environment with CUDA hidden and JAX_PLATFORMS=cpu; it reported verified, 20 cases, 10 single-token, 10 multi-token, 5 smoke successes, 20 final sequential keys and 63 files.

Done-when: source import, six controls, successful predetermined smoke and reference-environment/provenance record are complete.

## Cost, deviations and remaining coordination

GPU seconds: **0**. No lease acquired or REG pause/stop file touched. Full fixture generation, including this smoke gate, took **246.166 s internally / 248.211 s including launcher overhead**. Charge that shared generation interval once under S2-05b; do not add it again for S2-05a. Source controls took 1.65 s.

No new protocol deviation. Previously documented port conventions remain: GPT-2-small relative-depth binding at h[8].mlp.c_fc, shared answer newline terminator, legacy attention buffers, and evaluation RNG/transient-state preservation. This is the unbounded source reference, not the bounded JAX adapter.

The adapter owner must retain the distinction between pure LRU wording and SD-8's lowest-use-count/oldest wording; this reference implements neither eviction adaptation. JAX B4 and PC-10 remain the orchestrator's work.

Only new logs/artifacts/completion records were created. Existing task records, task board, STATUS.md, shared sources, environments and repositories were not edited. The board changes are specified in [the status edit request](S2-05ab-status-edit-request.md); the user's new-files-only rule requires permission before applying them. No staging or commit.
