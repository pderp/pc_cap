#!/bin/bash
# Post-run steps for the version-3 grammar rerun (DEC-029/030): paired analysis, order variation, checkpoint reversals, summary.
cd /home/derp/cap/pc_cap
E=frozen-confirmatory-v3-163d04e2
export JAX_PLATFORMS=cpu
/home/derp/cap/venv/bin/python -m pccap.analysis.s4_06 --dataset grammar --experiment-id $E --out results/S4/partial/s4_06_grammar_v3.json 2>&1 | grep -v Warning | tail -1
for arm in C2 C1 CR C0; do /home/derp/cap/venv/bin/python -m pccap.analysis.s7_03 --dataset grammar --arm $arm --root results/S4/$E --experiment-id $E --out results/S7/order_variation_grammar_${arm}_v3.json 2>&1 | grep -v Warning | tail -1 | cut -c1-100; done
/home/derp/cap/venv/bin/python -m pccap.analysis.s4_05 --root results/S4/$E --experiment-id $E --out results/S4/resource_views_grammar_v3.json --label "confirmatory grammar v3 (60 runs)" 2>&1 | grep -v Warning | tail -1
unset JAX_PLATFORMS
for spec in grammar:C2:ckpt1000 grammar:C2:end; do /home/derp/cap/venv/bin/python -m pccap.analysis.s7_01 --checkpoint $spec 2>&1 | grep -v Warning | tail -1 | cut -c1-120; done
JAX_PLATFORMS=cpu /home/derp/cap/venv/bin/python scripts/s7_summary.py 2>&1 | grep -v Warning | tail -3
