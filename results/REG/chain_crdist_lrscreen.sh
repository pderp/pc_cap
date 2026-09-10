#!/bin/bash
# pause window 2: CR re-profile (S3-05) + B1 learning-rate screen (PDF: {3e-5, 1e-4, 3e-4}); each profile blocks on the lease
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
$P -m pccap.harness.stage_s2_throughput --arms CR --cr-dist --out results/S2/throughput_crdist.json --tag crdist > results/S2/throughput_crdist.log 2>&1
$P -m pccap.harness.stage_s2_throughput --arms B1 --lora-lr 3e-5 --out results/S2/throughput_lr3e-5.json --tag lr3e-5 > results/S2/throughput_lr3e-5.log 2>&1
$P -m pccap.harness.stage_s2_throughput --arms B1 --lora-lr 3e-4 --out results/S2/throughput_lr3e-4.json --tag lr3e-4 > results/S2/throughput_lr3e-4.log 2>&1
echo WINDOW2_DONE >> results/S2/throughput_lr3e-4.log
rm -f results/REG/reg02.pause
