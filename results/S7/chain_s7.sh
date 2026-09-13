#!/bin/bash
# S7-01/02 on the committed checkpoints (PDF S7): full E.2 selections; sequential under the lease.
cd /home/derp/cap/pc_cap
OUT=results/S7/logs
echo "start $(date -u +%FT%TZ)" > $OUT/chain_status.txt
for spec in zsre:C2:ckpt300 counterfact:C2:end grammar:C2:ckpt1000 grammar:C2:end; do
  tag=${spec//:/_}
  /home/derp/cap/venv/bin/python -m pccap.analysis.s7_01 --checkpoint $spec > $OUT/$tag.log 2>&1
  echo "$spec exit $? $(date -u +%FT%TZ)" >> $OUT/chain_status.txt
done
echo "end $(date -u +%FT%TZ)" >> $OUT/chain_status.txt
