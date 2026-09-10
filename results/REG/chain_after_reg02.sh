#!/bin/bash
# After REG-02 completes: REG-03 preflight (records the checkpoint in manifests/assets.json), S1-01 P1, the ePC rows of
# P2/P3/P5/P6 on the regenerated weights, then the S1 report. Each step takes the lease itself. Logs: results/REG/after_reg02.log
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/after_reg02.log
until grep -q "REG-02 loop exited" results/REG/epc-50m.log 2>/dev/null; do sleep 60; done
st=$($P -c "import json; print(json.load(open('results/REG/epc-50m/summary.json'))['status'])")
echo "$(date -u +%FT%TZ) REG-02 status=$st" >> $LOG
if [ "$st" != "completed" ]; then echo "not completed; stopping chain" >> $LOG; exit 0; fi
W=/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz
$P -m pccap.distill.preflight --checkpoint /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766 --update-assets >> $LOG 2>&1 && echo "PREFLIGHT_DONE" >> $LOG
$P -m pccap.analysis.s1_p1 --epc-weights $W >> $LOG 2>&1 && echo "S1_P1_DONE" >> $LOG
$P -m pccap.analysis.s1_p2 --epc-weights $W >> $LOG 2>&1 && echo "S1_P2_DONE" >> $LOG
$P -m pccap.analysis.s1_p3 --epc-weights $W >> $LOG 2>&1 && echo "S1_P3_DONE" >> $LOG
$P -m pccap.analysis.s1_p5 --epc-weights $W >> $LOG 2>&1 && echo "S1_P5_DONE" >> $LOG
$P -m pccap.analysis.s1_p6 --epc-weights $W >> $LOG 2>&1 && echo "S1_P6_DONE" >> $LOG
$P -m pccap.cli report --stage S1 >> $LOG 2>&1
$P -m pccap.harness.freeze --draft >> $LOG 2>&1
echo "$(date -u +%FT%TZ) CHAIN_AFTER_REG02_DONE" >> $LOG
