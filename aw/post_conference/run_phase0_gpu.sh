#!/usr/bin/env bash
# Phase 0 GPU work (forward-only, frozen base + restored 300-edit memories), run serially under the exclusive lease.
set -euo pipefail
cd /home/derp/cap/pc_cap
export PYTHONPATH=src:. JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0
PY=/home/derp/cap/venv/bin/python
LOG=logs/post_conference/phase0/gpu_run.log
mkdir -p logs/post_conference/phase0
{
  echo "=== $(date -Is) composition"; $PY -m aw.post_conference.phase0_composition --execute --assemble
  echo "=== $(date -Is) incontext";   $PY -m aw.post_conference.phase0_incontext --execute --assemble
  echo "=== $(date -Is) frontier";    $PY -m aw.post_conference.phase0_frontier --execute --assemble
  echo "=== $(date -Is) done"
} >> "$LOG" 2>&1
