#!/bin/bash
# pause window 3: the short GPU test subset (no lease needed, but the GPU must have memory), run when the lease is free
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
touch results/REG/reg02.pause
# wait until REG-02 released the lease (the pause file holds it between chunks)
$P - <<'PY'
import pccap
from pccap.harness.lease import gpu_lease
with gpu_lease("TESTS-GPU", stage="S3", projected_seconds=900):
    import subprocess
    subprocess.run(["/home/derp/cap/venv/bin/python", "-m", "pytest", "-q", "-m", "gpu and not slow and not lease", "-p", "no:cacheprovider"],
                   stdout=open("results/tests_gpu_subset.log", "w"), stderr=subprocess.STDOUT)
PY
echo GPU_TESTS_DONE >> results/tests_gpu_subset.log
rm -f results/REG/reg02.pause
