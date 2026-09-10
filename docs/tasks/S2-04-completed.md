# S2-03 / S2-04 — implementation completion addendum

status: implemented and verified; ready for owner review
agent: codex
completed_utc: 2026-09-10T10:06:54.436059+00:00
worktree: `/home/derp/cap/pc_cap`
commit: none

This new addendum supersedes the formatting-related pause in `docs/tasks/S2-04.md`. The user explicitly approved the exact import-order correction in `docs/tasks/S2-04-import-order.patch`. It was applied to `tests/baselines/test_replay.py`; it moves one import into the group required by Ruff and changes no test logic or baseline behavior. The earlier task record and proposed patch remain unchanged as history.

Validation after the correction: **7 replay tests passed in 1.59 seconds**; Ruff passed across all four baseline implementation files and both baseline test files; the three approved baseline modules passed `git diff --check`. Evidence is in `results/baselines_lane_f/replay_verification_approved.txt`. The earlier **6 LoRA/B0 CPU controls** and **1 full GPT-2 GPU control** remain applicable because no implementation or GPU-test code changed in this continuation. No GPU run was repeated for an import-order correction.

The full lane has 13 passing CPU controls and one passing full-model GPU control. That GPT-2 test reduced summed teacher-forced answer NLL from 23.720344990 to 22.762440757 nats after ten LoRA steps, with all base weights unchanged. The free greedy answer remained an immediate newline; this is an implementation check, not an efficacy claim. Source hashes and verification provenance are in `results/baselines_lane_f/completion_verification.json`.

Available imports:

```python
from pccap.baselines.b0 import B0
from pccap.baselines.lora import LoRALearner
from pccap.baselines.replay import ReplayLearner

# Each independent arm should receive its own learner state and the intended ledger.
b1 = LoRALearner(base, rank=8, lr=1e-4, steps=10, seed=0)
b3 = ReplayLearner(LoRALearner(base, rank=8, lr=1e-4, steps=10, seed=0), seed=0)
```

Both baseline classes provide update, prediction, state/snapshot, checksum and memory interfaces required by Lane F. The detailed implementation, accounting and validation records are `docs/tasks/S2-03.md` and `docs/tasks/S2-04.md`.

B3's sampling interpretation still requires the orchestrator's review before scientific comparisons or freezing: its growing-capacity reservoir obeys the floor-rounded 5% and byte limits, but is not a uniform sample of all prior edits. The first 19 edits cannot enter its buffer, and capacity growth favors the item present at a growth boundary. That limitation is recorded in snapshots and outcomes. Approval of this import patch does not resolve that separate scientific interpretation. Arm registration, development screening, throughput and shared stage-report updates remain the orchestrator's tasks.

Only the approved replay test file was edited in this continuation. New files created:

- `results/baselines_lane_f/replay_verification_approved.txt`
- `results/baselines_lane_f/completion_verification.json`
- `docs/tasks/S2-04-completed.md` (this addendum)

No shared board/status/ledger files, existing reports, environments, or reference repositories were changed by this continuation. No staging, commits, merges, or pushes were performed. No jobs or GPU leases remain held by this lane.
