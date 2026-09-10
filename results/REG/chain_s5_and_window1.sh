#!/bin/bash
# Combined: S5 preparation (error-credit GPU test, ePC calibration, SB/SE-A/SE-E smoke) then GPU window 1 (GPU test subset,
# re-profile with ledger deltas, merges, D1/S3-04/D2/freeze refresh, resource views). Fail-fast; log results/REG/s5_and_window1.log
set -uo pipefail
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/s5_and_window1.log
step() { echo "$(date -u +%FT%TZ) STEP $1" >> $LOG; }
fail() { echo "$(date -u +%FT%TZ) CHAIN_FAILED at $1" >> $LOG; exit 1; }
step gpu-credit-test; $P -m pytest -q tests/cap/test_error_credit_gpu.py -p no:cacheprovider >> $LOG 2>&1 || fail gpu-credit-test
W=$($P -c "import json; a=json.load(open('manifests/assets.json'))['assets']['epc_checkpoint']; assert a['status']=='regenerated', a['status']; print(a['path'])") || fail assets-record
step epc-calibration; $P -m pccap.cap.calibrate --epc-weights "$W" --label EPC >> $LOG 2>&1 || fail epc-calibration
for arm in SB SE-A SE-E; do
  step "smoke-$arm"; $P -m pccap.cli run --stage S5 --arm $arm --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s5_smoke.json --mode dev >> $LOG 2>&1 || fail "smoke-$arm"
done
echo "$(date -u +%FT%TZ) S5_PREP_DONE" >> $LOG
step gpu-tests; $P -m pytest -q -m "gpu and not slow and not lease" -p no:cacheprovider > results/tests_gpu_subset_2.log 2>&1 || fail gpu-tests
step reprofile-caps; $P -m pccap.harness.stage_s2_throughput --arms C0 C1 C2 CR --cr-dist --out results/S2/throughput_v2.json --tag v2 >> $LOG 2>&1 || fail reprofile-caps
step reprofile-baselines; $P -m pccap.harness.stage_s2_throughput --arms B0 B1 B3 --out results/S2/throughput_v2_baselines.json --tag v2_baselines >> $LOG 2>&1 || fail reprofile-baselines
step merge; $P scripts/merge_throughput.py results/S2/throughput_v2.json >> $LOG 2>&1 && $P scripts/merge_throughput.py results/S2/throughput_v2_baselines.json >> $LOG 2>&1 || fail merge
step refresh; $P -m pccap.analysis.d1 >> $LOG 2>&1 && $P -m pccap.analysis.s3_04 --extra-root results/S2/throughput_v2_baselines results/S2/throughput_v2 >> $LOG 2>&1 && $P -m pccap.analysis.s3_06 >> $LOG 2>&1 && $P -m pccap.harness.freeze --draft >> $LOG 2>&1 || fail refresh
step views; $P -m pccap.analysis.s4_05 --root results/S2/throughput_v2 --root results/S2/throughput_v2_baselines --out results/S3/resource_views_dev_v2.json --label "development v2 (ledger deltas)" >> $LOG 2>&1 || fail views
echo "$(date -u +%FT%TZ) WINDOW1_DONE" >> $LOG
