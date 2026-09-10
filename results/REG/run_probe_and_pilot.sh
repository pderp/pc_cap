#!/bin/bash
# REG-01: timing probe then the 100-step pilot (protocol settings, T=1 stage), both under the lease.
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
# probe already done (results/REG/timing_probe.json)
$P - <<'PY' >> results/REG/pilot-100.log 2>&1
import pccap
from pccap.harness.lease import gpu_lease
from pccap.distill.train import parse, run
with gpu_lease("REG-01", stage="REG", projected_seconds=1800, exclusive=True):
    run(parse(["--run-name", "pilot-100", "--pilot", "--chunk-steps", "100", "--micro-batch-size", "5",
               "--checkpoint-every", "50", "--relax-log-every", "1", "--print-every", "5"]))
PY
echo DONE >> results/REG/pilot-100.log
