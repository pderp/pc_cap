#!/bin/bash
# REG-02: full regeneration in resumable chunks. Each chunk takes the GPU lease, runs CHUNK steps
# (or until MAX_SECONDS), checkpoints, releases the lease, and the loop continues until the run's
# summary reports "completed" or an abort. Safe to kill between chunks and to restart: the driver
# resumes from assets/models/epc/epc-50m/checkpoints/latest.
#   results/REG/run_reg02.sh [CHUNK_STEPS=500] [MAX_SECONDS_PER_CHUNK=5400]
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
CHUNK=${1:-500}
MAXS=${2:-5400}
RUN=epc-50m
LOG=results/REG/$RUN.log
touch results/REG/reg02.running
while true; do
  if [ -f results/REG/reg02.stop ]; then echo "stop file present; exiting" >> $LOG; break; fi
  $P - "$RUN" "$CHUNK" "$MAXS" <<'PY' >> $LOG 2>&1
import sys, json
import pccap
from pccap.harness.lease import gpu_lease
from pccap.distill.train import parse, run
run_name, chunk, maxs = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
with gpu_lease("REG-02", stage="REG", projected_seconds=maxs, exclusive=False):
    s = run(parse(["--run-name", run_name, "--micro-batch-size", "5", "--chunk-steps", str(chunk), "--max-seconds", str(maxs),
                   "--checkpoint-every", "250", "--print-every", "25"]))
print("CHUNK_STATUS", s["status"], s["global_step"], flush=True)
PY
  st=$(tail -n 5 $LOG | grep CHUNK_STATUS | tail -n 1 | awk '{print $2}')
  echo "$(date -u +%FT%TZ) chunk finished: status=$st" >> $LOG
  case "$st" in
    completed|prompt_kl_abort|relaxation_divergence|unreachable_terminal_tau) break ;;
    paused_chunk|paused_deadline) sleep 5 ;;
    *) echo "unexpected status '$st' (crash?); retrying in 60 s" >> $LOG; sleep 60 ;;
  esac
done
rm -f results/REG/reg02.running
echo "$(date -u +%FT%TZ) REG-02 loop exited" >> $LOG
