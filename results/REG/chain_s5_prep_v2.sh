#!/bin/bash
# S5-01 preparation after the post-REG chain SUCCEEDED (marker written only on full success): error-credit GPU test,
# ePC radius calibration, 20-item SB/SE-A/SE-E development smoke. Fail-fast. Log: results/REG/s5_prep_v2.log
set -uo pipefail
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/s5_prep_v2.log
fail() { echo "$(date -u +%FT%TZ) S5_PREP_FAILED at $1" >> $LOG; exit 1; }
until grep -q "CHAIN_AFTER_REG02_DONE" results/REG/after_reg02_v2.log 2>/dev/null; do
  grep -q "CHAIN_FAILED" results/REG/after_reg02_v2.log 2>/dev/null && fail "upstream chain failed"
  sleep 60
done
$P -m pytest -q tests/cap/test_error_credit_gpu.py -p no:cacheprovider >> $LOG 2>&1 || fail gpu-credit-test
W=$($P -c "import json; a=json.load(open('manifests/assets.json'))['assets']['epc_checkpoint']; assert a['status']=='regenerated', a['status']; print(a['path'])") || fail assets-record
$P -m pccap.cap.calibrate --epc-weights "$W" --label EPC >> $LOG 2>&1 || fail epc-calibration
for arm in SB SE-A SE-E; do
  $P -m pccap.cli run --stage S5 --arm $arm --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s5_smoke.json --mode dev >> $LOG 2>&1 || fail "smoke-$arm"
done
echo "$(date -u +%FT%TZ) S5_PREP_DONE" >> $LOG
