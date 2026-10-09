#!/usr/bin/env bash
# ext-20261009 CPU pipeline: assemble -> paired -> tails -> datasets -> nelson -> figures -> report (+ PDF). Rerunnable.
set -u
cd /home/derp/cap/pc_cap
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2
export MPLCONFIGDIR=/tmp/claude-1001/-home-derp-cap/b324c5c1-5355-4ded-9cbd-7fb1da0f4c7a/scratchpad/mpl
PY=/home/derp/cap/venv/bin/python
LOG=results/extremes_analysis/ext-20261009/logs/cpu_pipeline.log
for m in assemble paired tails datasets nelson figures report; do
  echo "$(date -u +%FT%TZ) start $m" >> $LOG
  $PY -m aw.extremes.$m >> $LOG 2>&1; rc=$?; echo "$(date -u +%FT%TZ) end $m exit $rc" >> $LOG
done
