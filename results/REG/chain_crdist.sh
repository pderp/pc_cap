#!/bin/bash
# after the baseline throughput: CR re-profile with the S3-05 distribution, then release the REG-02 pause
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
until grep -q "BASELINES_DONE\|Traceback" results/S2/throughput_baselines.log 2>/dev/null; do sleep 10; done
$P -m pccap.harness.stage_s2_throughput --arms CR --cr-dist --out results/S2/throughput_crdist.json --tag crdist > results/S2/throughput_crdist.log 2>&1
echo CRDIST_DONE >> results/S2/throughput_crdist.log
rm -f results/REG/reg02.pause
