#!/bin/bash
# After REG-02 completes (terminal state verified by scripts/reg_wait_complete.py, never a log substring):
# REG-03 preflight → S1-01 P1 → ePC rows P2/P3/P5/P6 → S1 report → freeze draft; each step must succeed
# (fail-fast); the success marker is written only when every step passed. Log: results/REG/after_reg02_v2.log
set -uo pipefail
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/after_reg02_v2.log
step() { echo "$(date -u +%FT%TZ) STEP $1" >> $LOG; }
fail() { echo "$(date -u +%FT%TZ) CHAIN_FAILED at $1" >> $LOG; exit 1; }
$P scripts/reg_wait_complete.py --run epc-50m >> $LOG 2>&1 || fail wait
W=/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz
[ -f "$W" ] || fail checkpoint
step preflight; $P -m pccap.distill.preflight --checkpoint /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766 --update-assets >> $LOG 2>&1 || fail preflight
step p1;  $P -m pccap.analysis.s1_p1 --epc-weights $W >> $LOG 2>&1 || fail p1
step p2;  $P -m pccap.analysis.s1_p2 --epc-weights $W >> $LOG 2>&1 || fail p2
step p3;  $P -m pccap.analysis.s1_p3 --epc-weights $W >> $LOG 2>&1 || fail p3
step p5;  $P -m pccap.analysis.s1_p5 --epc-weights $W >> $LOG 2>&1 || fail p5
step p6;  $P -m pccap.analysis.s1_p6 --epc-weights $W >> $LOG 2>&1 || fail p6
step report; $P -m pccap.cli report --stage S1 >> $LOG 2>&1 || fail report
step freeze-draft; $P -m pccap.harness.freeze --draft >> $LOG 2>&1 || fail freeze
echo "$(date -u +%FT%TZ) CHAIN_AFTER_REG02_DONE" >> $LOG
