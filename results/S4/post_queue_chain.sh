#!/bin/bash
# After the v3 grammar queue: re-apply analysis-tree v3, run the grammar analyses, then the full-validation drift supplement.
cd /home/derp/cap/pc_cap
OUT=results/S4/post_queue_chain_status.txt
echo "waiting $(date -u +%FT%TZ)" > $OUT
while pgrep -f "pccap.cli queue" >/dev/null; do sleep 60; done
echo "queue ended $(date -u +%FT%TZ)" >> $OUT
git checkout 36ede02 -- src/pccap/analysis/s4_06.py
echo "s4_06 v3 re-applied" >> $OUT
bash scripts/s4_06_grammar_v3.sh > results/S4/post_queue_grammar_v3.log 2>&1
echo "grammar v3 chain exit $?" >> $OUT
echo "drift supplement runs separately (concurrent, --no-lease)" >> $OUT
echo "end $(date -u +%FT%TZ)" >> $OUT
