#!/usr/bin/env bash
# ext-20261009 GPU chain: frozen baseline scoring -> reader scoring (zsRE, CounterFact) -> MQuAKE supplemental
# evaluations -> reader scoring on MQuAKE. Idempotent: scoring resumes by chunk hash; evaluations are skipped when
# their report.json exists (a partial directory is moved aside and rerun).
set -u
cd /home/derp/cap/pc_cap
export PYTHONDONTWRITEBYTECODE=1
PY=/home/derp/cap/venv/bin/python
RUN=results/extremes_analysis/ext-20261009
LOG=$RUN/logs/gpu_chain.log
log(){ echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }
score(){ # model dataset [horizon]
  local m=$1 d=$2 h=${3:-}
  local dir=/home/derp/cap/assets/extremes_analysis/ext-20261009/checkpoints/scores/$m/$d/h${h:-0}
  if [ -f "$dir/chunks.json" ] && grep -q '"status": "complete"' "$dir/chunks.json"; then log "skip score $m $d $h"; return 0; fi
  log "start score $m $d $h"
  if [ -n "$h" ]; then $PY -m aw.extremes.score --model "$m" --dataset "$d" --horizon "$h" --execute >> "$LOG" 2>&1; else $PY -m aw.extremes.score --model "$m" --dataset "$d" --execute >> "$LOG" 2>&1; fi
  log "end score $m $d $h exit $?"
}
mq(){ # rule seed
  local dir=$RUN/mquake_eval/eval-$1-s$2-mquake
  if [ -f "$dir/report.json" ]; then log "skip mquake_eval $1 $2"; return 0; fi
  if [ -d "$dir" ]; then mv "$dir" "$dir.failed-$(date -u +%Y%m%dT%H%M%SZ)"; mv /home/derp/cap/assets/extremes_analysis/ext-20261009/checkpoints/mquake_eval/eval-$1-s$2-mquake /home/derp/cap/assets/extremes_analysis/ext-20261009/checkpoints/mquake_eval/eval-$1-s$2-mquake.failed-$(date -u +%Y%m%dT%H%M%SZ) 2>/dev/null; fi
  log "start mquake_eval $1 $2"
  $PY -m aw.extremes.mquake_eval --rule "$1" --seed "$2" --execute >> "$LOG" 2>&1
  log "end mquake_eval $1 $2 exit $?"
}
log "chain start"
for d in zsre counterfact mquake; do score frozen $d; done
for d in zsre counterfact; do for h in 300 100; do for r in bp epc; do for s in 0 1 2; do score ${r}_reader_s$s $d $h; done; done; done; done
for s in 0 1 2; do for r in bp epc; do mq $r $s; done; done
for h in 300 100; do for r in bp epc; do for s in 0 1 2; do score ${r}_reader_s$s mquake $h; done; done; done
log "chain end"
