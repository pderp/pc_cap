#!/bin/bash
# Capstan 2026-10-03: AW-L5 upper-layer 2x2 chain (DEC-077 item 5): profiles -> 6 development evaluations -> CPU cost
# projection (gate) -> 3 upper trainings -> 18 evaluations. Each GPU command takes the exclusive lease itself.
cd /home/derp/cap/pc_cap
L=logs/additional_work/PC-v0/chain.log
E="JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:."
R=results/additional_work/AW-L; P=results/additional_work/PC-reader
mkdir -p logs/additional_work/AW-L $R
run() { local name=$1; shift
  echo "AW-L5 $name start $(date -Is)" >> $L
  env $E ../venv/bin/python -m aw.aw_l_train "$@" > logs/additional_work/AW-L/$name.log 2>&1; local rc=$?
  echo "AW-L5 $name exit $rc $(date -Is)" >> $L
  if [ $rc -ne 0 ]; then echo "AW-L5 $name failed (rc $rc)"; tail -8 logs/additional_work/AW-L/$name.log | cut -c1-300; exit $rc; fi; }
run profile-upper-s0 profile --read upper --seed 0 --output $R/profile-upper-s0 --wall-seconds 14400 --execute
for ds in zsre counterfact; do
  for w in last all; do run eval-profile-upper-$w-$ds evaluate --training $R/profile-upper-s0 --dataset $ds --read upper --write $w --development --output $R/eval-profile-upper-$w-$ds --wall-seconds 7200 --execute; done
  run eval-profile-all-last-$ds evaluate --training $P/profile-bp-s0 --dataset $ds --read all --write last --development --output $R/eval-profile-all-last-$ds --wall-seconds 7200 --execute
done
echo "AW-L5 portfolio-cost start $(date -Is)" >> $L
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. ../venv/bin/python -m aw.reader_portfolio_cost --study upper \
  --training-profile $R/profile-upper-s0 --training-profile $P/profile-bp-s0 \
  --evaluation-profile $R/eval-profile-upper-last-zsre --evaluation-profile $R/eval-profile-upper-all-zsre \
  --evaluation-profile $R/eval-profile-upper-last-counterfact --evaluation-profile $R/eval-profile-upper-all-counterfact \
  --evaluation-profile $R/eval-profile-all-last-zsre --evaluation-profile $R/eval-profile-all-last-counterfact \
  --evaluation-profile $P/eval-profile-bp-zsre --evaluation-profile $P/eval-profile-bp-counterfact \
  --output logs/additional_work/AW-L/portfolio-cost-20261003 > logs/additional_work/AW-L/portfolio-cost.log 2>&1; rc=$?
echo "AW-L5 portfolio-cost exit $rc $(date -Is)" >> $L
[ $rc -ne 0 ] && { echo "AW-L5 portfolio cost failed"; tail -8 logs/additional_work/AW-L/portfolio-cost.log | cut -c1-300; exit $rc; }
H=$(../venv/bin/python - <<'PY'
import json,glob,re
vals=[]
for f in glob.glob("logs/additional_work/AW-L/portfolio-cost-20261003/*.json")+glob.glob("logs/additional_work/AW-L/portfolio-cost-20261003.json"):
    def walk(o,k=""):
        if isinstance(o,dict):
            for kk,v in o.items(): walk(v,kk)
        elif isinstance(o,(int,float)) and re.search("hour",k): vals.append((k,float(o)))
    walk(json.load(open(f)))
print(max([v for k,v in vals] or [0.0]))
PY
)
echo "AW-L5 projected hours (max hour-valued field) $H $(date -Is)" >> $L
if [ "$(echo "$H > 40" | bc -l 2>/dev/null)" = "1" ]; then echo "AW-L5 projection $H h exceeds the 40 h gate; stopping before training"; exit 7; fi
for s in 0 1 2; do run train-upper-s$s train --read upper --seed $s --profile $R/profile-upper-s0 --output $R/train-upper-s$s --wall-seconds 14400 --execute; done
for s in 0 1 2; do for ds in zsre counterfact; do
  for w in last all; do run eval-upper-$w-s$s-$ds evaluate --training $R/train-upper-s$s --dataset $ds --read upper --write $w --evaluation-profile $R/eval-profile-upper-$w-$ds --output $R/eval-upper-$w-s$s-$ds --wall-seconds 14400 --execute; done
  run eval-all-last-s$s-$ds evaluate --training $P/train-bp-s$s --dataset $ds --read all --write last --evaluation-profile $R/eval-profile-all-last-$ds --output $R/eval-all-last-s$s-$ds --wall-seconds 14400 --execute
done; done
echo "AW-L5 chain done $(date -Is)" >> $L
