# S2-03 / S2-04 — existing-file permission request

status: paused before implementation, pending user permission
agent: codex
recorded_utc: 2026-09-10T01:16:36.821798+00:00
source: `docs/ongoing3.md`, Lane F; `docs/ongoing2.md`, Lane F; PDF Baselines and S2
commit: none

Lane F is the highest-priority available lane; both task-board rows were pending and unassigned when inspected. The prescribed public modules already exist as one-line ENV-03 placeholders. Implementing the specified imports therefore requires changing existing files. The user's latest instruction requires a pause before any such edit. No task-board or source change has been made. This new record records the intended lane without altering the shared board.

## Requested edit scope

- `src/pccap/baselines/lora.py`: replace the placeholder with the specified `LoRALearner`, using JAX/optax; rank-8 Q/V adapters at every layer, 10 whole-answer teacher-forced Adam steps, query and learning cost accounting, full optimizer snapshots and rollback support, state/base checksums, and actual adapter-plus-optimizer memory reporting.
- `src/pccap/baselines/b0.py`: replace the placeholder with frozen `B0`; query evaluation charged through the base ledger, no-op accepted updates, and compatible state/checksum/memory interfaces.
- `src/pccap/baselines/replay.py`: replace the placeholder with `ReplayLearner`, after S2-03 validation; reservoir sampling constrained by the item fraction and byte ceiling, one replay item per new item per step, explicit rounding and storage accounting, and exact restoration of buffer/optimizer/RNG state.

Only these three existing source files are requested. Their current contents are placeholders, with hashes below to detect concurrent changes before applying any authorized work.

| Existing file | SHA-256 at inspection |
| --- | --- |
| `src/pccap/baselines/lora.py` | `510a21cb4e1068856f8fd7b9e87e47d7131dca4127279c3057393f2976d96922` |
| `src/pccap/baselines/b0.py` | `bd059c0509baad20632eb04e879c49f0683948bbe5880574ca50eb71b8c9379d` |
| `src/pccap/baselines/replay.py` | `a986c3331ca9edd3194f988ec93f41ec918b7a4330d94323931049b61f6c33a1` |

## Additive work accompanying the implementation

New `src/pccap/baselines/lora_forward.py` will implement Q/V-only weight deltas using the existing functional GPT-2 primitives, leaving the base weights immutable. New baseline tests, task records, and uniquely named logs will accompany the implementation. Large or binary resources and temporary test fixtures will live under `assets/`; the existing JAX environment and read-only reference repositories remain outside this edit scope. No change to package `__init__.py`, contracts, base code, harness, shared task/status manifests, or existing reports is requested.

## Verification checkpoints

1. Validate LoRA parameter inventory and Q/V slice placement, including zero K-slice adapter gradient and frozen base checksums.
2. Verify B0 no-op behavior, ledger separation, complete memory accounting, and learner serialization/restoration with future update equivalence.
3. Run the specified GPT-2 development-item test: a 10-step edit must reduce whole-answer teacher-forced NLL; record the before/after greedy answer without requiring it to change. Coordinate GPU use with the orchestrator; any existing lease/report write that requires additional permission must be raised separately.
4. Verify replay reservoir statistics, rounding and byte limits, previous-item-only replay selection, charged replay costs, and snapshot/RNG restoration.
5. Record validation evidence and changed files in new task records for the orchestrator's review. No staging, commits, merges, or pushes.

Any implementation refinement within the three named files is part of the requested task scope. Any other existing-file edit or append will require a separate permission request. No implementation has been written or tested at this pause.
