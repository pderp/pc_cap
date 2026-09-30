# PC-15 / AW-L5 — owner commands

All commands run from `/home/derp/cap/pc_cap`. Implementation/tests are CPU-only; the commands below are **for Capstan's GPU dispatch after the existing queue**, under DEC-077. Do not start while this file's task records still say implementation is in progress. Use a new output name for each attempt; failed attempts are retained and charged.

For metadata and tests, use `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2`. For dispatched execution, use `JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:.`; every execution command acquires the exclusive lease and checks occupancy itself. No `--no-lease` option is provided.

## PC-trained reader

First inspect `../venv/bin/python -m aw.pc_reader_train plan` and `docs/additional_work/PC-reader.md`. Profile **both** `--rule bp` and `--rule epc`, seed 0:

```sh
../venv/bin/python -m aw.pc_reader_train profile --rule bp --seed 0 --output results/additional_work/PC-reader/profile-bp-s0 --wall-seconds 14400 --execute
../venv/bin/python -m aw.pc_reader_train profile --rule epc --seed 0 --output results/additional_work/PC-reader/profile-epc-s0 --wall-seconds 14400 --execute
```

For each rule's profile, run the development evaluation on **each dataset**. Example:

```sh
../venv/bin/python -m aw.pc_reader_train evaluate --training results/additional_work/PC-reader/profile-bp-s0 --dataset zsre --development --output results/additional_work/PC-reader/eval-profile-bp-zsre --wall-seconds 7200 --execute
```

Use the four evaluation profiles and two training profiles with `aw.reader_portfolio_cost` (CPU command; repeat `--training-profile` / `--evaluation-profile` for every directory) to obtain the full twelve-cell projection before the six trainings. This includes full harm; a ten-item stream time alone is not the cell forecast. The GPU owner fits it to the remaining schedule, with retry/report allowance and DEC-077's cut order.

For each rule and **each seed 0/1/2**, train from scratch using the matching rule's seed-0 profile. Example:

```sh
../venv/bin/python -m aw.pc_reader_train train --rule bp --seed 0 --profile results/additional_work/PC-reader/profile-bp-s0 --output results/additional_work/PC-reader/train-bp-s0 --wall-seconds 14400 --execute
../venv/bin/python -m aw.pc_reader_train evaluate --training results/additional_work/PC-reader/train-bp-s0 --dataset zsre --evaluation-profile results/additional_work/PC-reader/eval-profile-bp-zsre --output results/additional_work/PC-reader/eval-bp-s0-zsre --wall-seconds 14400 --execute
```

The evaluation command includes acquisition, endpoints at 100/300, snapshots and the final **full** ordinary-text harm readout. Repeat for both datasets and all six trained readers. `report.json` plus `cost.json` must both say complete. Readout cost is a component of that process receipt, not an extra charge to add again. The three BP full-read readers can also supply AW-L's full-read arm under the identical recipe/seeds; charge shared training once across portfolios and identify those shared controls explicitly.

## Upper-layer 2×2

`../venv/bin/python -m aw.aw_l_train plan` declares six readers and 24 evaluations. Profile both read sets, and evaluate development for all **two read × two write × two dataset** combinations. All training uses the full-write objective and `--rule bp`:

```sh
../venv/bin/python -m aw.aw_l_train profile --read upper --seed 0 --output results/additional_work/AW-L/profile-upper-s0 --wall-seconds 14400 --execute
../venv/bin/python -m aw.aw_l_train evaluate --training results/additional_work/AW-L/profile-upper-s0 --dataset zsre --write last --development --output results/additional_work/AW-L/eval-profile-upper-last-zsre --wall-seconds 7200 --execute
```

For `--read all`, the same-recipe PC-15 BP training profile/readers may be referenced with `--training` / `--profile`; new full-read training is also supported but duplicates that work. Evaluation takes read taps from the bound trained artifact, so `--read` does not reinterpret an existing reader. `--write all` and `--write last` **share that exact trained reader**, acquire separate fresh memories and retain dense zero-slot storage costs. Produce the two-training/eight-evaluation profile forecast with `aw.reader_portfolio_cost --study upper`; retain a retry margin inside the **48-hour ceiling**, which execution also enforces conservatively from top-level process receipts in the AW-L namespace.

Then train upper readers for all three seeds; run each of six readers on both datasets and both write masks:

```sh
../venv/bin/python -m aw.aw_l_train train --read upper --seed 0 --profile results/additional_work/AW-L/profile-upper-s0 --output results/additional_work/AW-L/train-upper-s0 --wall-seconds 14400 --execute
../venv/bin/python -m aw.aw_l_train evaluate --training results/additional_work/AW-L/train-upper-s0 --dataset zsre --write last --evaluation-profile results/additional_work/AW-L/eval-profile-upper-last-zsre --output results/additional_work/AW-L/eval-upper-last-s0-zsre --wall-seconds 14400 --execute
```

Before launching another process, inspect the previous exit status and receipt; commands do not resubmit themselves after failure. Material changes to a runner invalidate profiles bound to its old sources. This is a pilot/dispatch gate, not another scientific approval step. All reusable tensors, feature caches and memory snapshots go under `assets/runs/pc_cap/additional_work/`; all code, receipts, metrics and reports stay in `pc_cap`.
