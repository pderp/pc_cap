#!/bin/bash
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
$P -m pccap.harness.stage_s2_throughput --arms B0 B1 B3 --out results/S2/throughput_baselines.json --tag baselines > results/S2/throughput_baselines.log 2>&1
$P scripts/merge_throughput.py results/S2/throughput_baselines.json >> results/S2/throughput_baselines.log 2>&1
$P -m pccap.analysis.d1 >> results/S2/throughput_baselines.log 2>&1
echo BASELINES_DONE >> results/S2/throughput_baselines.log
nohup results/REG/run_reg02_v2.sh 500 5400 > /dev/null 2>&1 &
