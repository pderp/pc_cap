#!/bin/bash
# S3-03 development matrix on the grammar (CPU): C0/C1/C2/CR × realization 0 × perms 0,1 × 8 tasks × 16 items; then tracing after learning
# is a later step. Fail-fast; log results/REG/s3_03_dev.log
set -uo pipefail
cd /home/derp/cap/pc_cap
P=/home/derp/cap/venv/bin/python
LOG=results/REG/s3_03_dev.log
export JAX_PLATFORMS=cpu
fail() { echo "$(date -u +%FT%TZ) S3_03_FAILED at $1" >> $LOG; exit 1; }
cat > manifests/dev/s3_grammar_dev.json <<'JSON'
{"name": "s3-grammar-dev", "mode": "dev", "stage": "S3", "seed": 0, "dataset": "grammar", "n_per_task": 16, "locality_prompts": 200, "drift_windows": 64,
 "checkpoints": [32, 64, 128], "notes": "S3-03 development matrix: 8 tasks x 16 items in the committed order; one realization, two orders"}
JSON
for perm in 0 1; do for arm in C0 C1 C2 CR; do
  echo "$(date -u +%FT%TZ) STEP $arm perm $perm" >> $LOG
  $P -m pccap.cli run --stage S3 --arm $arm --dataset grammar --realization 0 --perm $perm --manifest manifests/dev/s3_grammar_dev.json --no-lease --force >> $LOG 2>&1 || fail "$arm-$perm"
done; done
echo "$(date -u +%FT%TZ) S3_03_DEV_DONE" >> $LOG
