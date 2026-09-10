#!/bin/bash
# GPU window 1 (plan 4 §2): after the S5 prep chain — GPU test subset, re-profile with ledger deltas (cap arms with the
# learned CR, baselines), merge, D1/S3-04/S3-06/freeze-draft refresh. Fail-fast; log results/REG/window1.log
set -uo pipefail
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/window1.log
fail() { echo "$(date -u +%FT%TZ) WINDOW1_FAILED at $1" >> $LOG; exit 1; }
until grep -q "S5_PREP_DONE\|S5_PREP_FAILED" results/REG/s5_prep_v2.log 2>/dev/null; do sleep 60; done
$P -m pytest -q -m "gpu and not slow and not lease" -p no:cacheprovider > results/tests_gpu_subset_2.log 2>&1 || fail gpu-tests
$P -m pccap.harness.stage_s2_throughput --arms C0 C1 C2 CR --cr-dist --out results/S2/throughput_v2.json --tag v2 >> $LOG 2>&1 || fail reprofile-caps
$P -m pccap.harness.stage_s2_throughput --arms B0 B1 B3 --out results/S2/throughput_v2_baselines.json --tag v2_baselines >> $LOG 2>&1 || fail reprofile-baselines
$P scripts/merge_throughput.py results/S2/throughput_v2.json >> $LOG 2>&1 && $P scripts/merge_throughput.py results/S2/throughput_v2_baselines.json >> $LOG 2>&1 || fail merge
$P -m pccap.analysis.d1 >> $LOG 2>&1 && $P -m pccap.analysis.s3_04 --extra-root results/S2/throughput_v2_baselines results/S2/throughput_v2 >> $LOG 2>&1 && $P -m pccap.analysis.s3_06 >> $LOG 2>&1 && $P -m pccap.harness.freeze --draft >> $LOG 2>&1 || fail refresh
$P -m pccap.analysis.s4_05 --root results/S2/throughput_v2 --root results/S2/throughput_v2_baselines --out results/S3/resource_views_dev_v2.json --label "development v2 (ledger deltas)" >> $LOG 2>&1 || fail views
echo "$(date -u +%FT%TZ) WINDOW1_DONE" >> $LOG
