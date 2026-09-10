#!/bin/bash
# After the post-REG-02 chain: S5-01 preparation on the GPU — error-credit GPU test, ePC radius calibration,
# and a 20-item development smoke of SB / SE-A / SE-E. Logs: results/REG/s5_prep.log
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/s5_prep.log
until grep -q "CHAIN_AFTER_REG02_DONE" results/REG/after_reg02.log 2>/dev/null; do sleep 60; done
$P -m pytest -q tests/cap/test_error_credit_gpu.py -p no:cacheprovider >> $LOG 2>&1 && echo GPU_CREDIT_TEST_DONE >> $LOG
W=$($P -c "import json; print(json.load(open('manifests/assets.json'))['assets']['epc_checkpoint']['path'])")
$P -m pccap.cap.calibrate --epc-weights $W --label EPC >> $LOG 2>&1 && echo EPC_CALIBRATION_DONE >> $LOG
for arm in SB SE-A SE-E; do
  $P -m pccap.cli run --stage S5 --arm $arm --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s5_smoke.json --mode dev >> $LOG 2>&1 && echo "S5_SMOKE_${arm}_DONE" >> $LOG
done
echo "$(date -u +%FT%TZ) S5_PREP_DONE" >> $LOG
