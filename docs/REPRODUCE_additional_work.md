# Reproducing the supplemental experiments and presentation

Capex · October 2, 2026 · REP-1. This supplements [REPRODUCE.md](REPRODUCE.md).
It describes **recomputing reports from saved measurements** separately from
**running new GPU experiments**. The one-command refresh below performs only the
former. Local JAX is the execution stack; no PyTorch or Colab is involved.

## Working trees and required resources

Use `/home/derp/cap/pc_cap` as the working directory, with its populated sibling
`/home/derp/cap/assets` tree and `/home/derp/cap/venv`. Historical records contain
absolute paths, so retaining this layout avoids changing bound metadata. The
read-only `llm-by-neural-predictive-coding` and FabricPC repositories are references,
not destinations for patches. The saved-result refresh does not train through them.

**A Git-only checkout is insufficient.** Bring the raw arrays, large weights,
snapshots and token/data resources named by the manifests; some are intentionally
untracked. In particular, sealed learner snapshots stopped being tracked in the
assets repository on September 26. Their receipts still name their exact hashes.
A missing input is an error or an explicit missing experimental cell; it must not
be replaced by a model call or silently treated as zero. Do not edit paths/hashes
to force a historical source check to pass.

Set the CPU environment in a fresh shell:

```bash
cd /home/derp/cap/pc_cap
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PCCAP_HDPC_PATH=/home/derp/cap/llm-by-neural-predictive-coding
```

The runner uses the interpreter that launches it. Plotting imports project NumPy
first and appends the existing `assets/envs/status-paper-20260911/lib/python3.12/site-packages`
for Matplotlib. It installs nothing. The new figures use a private Matplotlib cache
inside their fresh assets destination. Analysis can import JAX-backed definitions,
but neither instantiates a model nor executes training, acquisition or readout.

Key pinned inputs (full lists accompany each report and the refresh catalog):

| Input | SHA-256 |
| --- | --- |
| `requirements.lock` | `b8bc3a542813e294ece6c9fe6eb957287414d412738e31638dbc69bbcea524bb` |
| `manifests/assets.json` | `c54b97781e0710ef2fc29efb25bc26d23997459cac6e7207dcf874a695b7b1ba` |
| `manifests/datasets.json` | `f0b80aa9a97643752f57d7f79d9ed69c8d45523bf3e6862b2c060caec6b380e0` |
| `manifests/revision_v1/kappa_pilot_v3.json` | `554db1b3462e0dfe6e92cdc4ecf071280b75892a8a4dc561759dcd959fea5747` |
| `manifests/additional_work/run_matrix_R_v1.json` | `4bcb0fab8beadd2f7cb2dead1b81b97d008ce3c0f5151dc7eb77f533fa1b2767` |
| ePC base `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz` | `ea4c561d3963ffd89f866337ef5e789a4ef15b7558b4c717594dbef88cd26f51` |
| Frozen R1 base `model.safetensors`, under the recipe's `stage4_dev_bases/c5b784…` directory | `248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707` |

The complete path of that R1 base, dataset pools, stop list, calibration, chosen
reader and payload hashes are in each bound recipe/reader report; for example
`results/additional_work/PC-reader/train-epc-s1/report.json` → `recipe`.
Parameter-tree hashes (such as `params_sha256`) are not file SHA-256 values.

## One-command CPU refresh

Choose a fresh name; existing destinations, even empty directories, are refused.
The corresponding figure directory is derived automatically in the assets tree.

```bash
../venv/bin/python -m aw.refresh_reports \
  --output logs/additional_work/reproductions/review-20261002
```

This writes reports/documents/logs below that directory and figures plus a draft
deck below `assets/presentation-materials/reproductions/review-20261002/`.
It does not replace any canonical report, manuscript, source slide, result or
queue file. Legacy generators with fixed publication paths are redirected within
their private worker process; an additional write guard rejects writes outside
the two fresh destinations. No live source module is patched.

To inspect the plan without writing, add `--plan`. To refresh a subset and all
its prerequisites, add, for example, `--steps pc-reader` or `--steps deck`.
Unknown steps and GPU commands cannot enter the fixed step list. A failed step
stops its dependents, preserves its log and records the failure in `refresh.json`.
Choose another fresh name after a failure; there is no destructive resume flag.

For a later refresh, compare inputs with the previous receipt:

```bash
../venv/bin/python -m aw.refresh_reports \
  --output logs/additional_work/reproductions/review-20261003 \
  --previous logs/additional_work/reproductions/review-20261002/refresh.json
```

`refresh.json` records every exact child command, CPU environment, step duration,
output hash and added/removed/changed input. Live progress logs are excluded from
the change detector; terminal records and authored sources are included. Native
report manifests additionally bind the actual arrays/checkpoints they read. If
inputs change during the run, the receipt says `complete_with_input_changes`:
inspect those changes and refresh again before treating it as a coherent final
snapshot. `catalog.json` indexes full source hashes and measured cost receipts.

The dependency order follows [the freeze checklist](freeze_checklist_20261009.md):
unchanged Stage-4 evidence and completed supplemental studies; saved-vector tail
analysis; reader/extension/interface reports; figures and copied presentation
sources; X25 and X26 checks. HT-17 is run **once** before the reader report, which
then consumes its new vector identities. It is not rerun a second time through
the reader's `--refresh-tail` option.

**Publication still requires reading the result.** Literal speaker/Q&A statements
are copied from the current authored deck; the runner does not invent new
interpretations or convert them automatically into three-seed conclusions. See
`presentation-review-required.json`. Review counts, populations and wording,
then explicitly promote a reviewed snapshot and rerun the audits. X26's numerical
ledger/report matches are contextual review candidates, not semantic proof.

## Every CPU result and figure

In this table `OUT` means the fresh repository output from the command above;
`FIG` is its matching assets directory. To execute a row, use that exact command
with `--steps <step>` and a fresh output name; dependencies are included.
The native producer names explain the calculation, not an instruction to invoke
their historical overwrite-prone defaults. Exact expanded commands are in the
run's `refresh.json` and `commands/<step>.log`.

| Step | Saved inputs and native calculation | Fresh outputs |
| --- | --- | --- |
| `ht15` | `logs/R1/final_queue/` successful receipts and final vectors; `aw.tail_cells` | `OUT/ht15/cell_tails.{json,csv}`, `tail_spread.md`; 270-cell coverage, per-cell maxima, ES99 and realization spread |
| `stage4` | Fixed 270-cell comparator/triplet/appendix/receipt reports and freshly reproduced HT-15; `aw.stage4_assembly` | `OUT/stage4/assembly.json`, source index; `OUT/documents/R1_stage4_report.md`; no reclassification |
| `pc-default` | `PC-v0/replication-60-20260927`, `PC-v1/replication-4-20260927`, default harm directories and X24-final; `aw.pc_complete_report` | `OUT/pc-default/{v0,v1}/report.json`, `harm/{report,cost}.json`, original-generator replay, both readable reports |
| `pc-matched` | `PC-v0/matched-control/run-20260929`; `aw.pc_control_report` | `OUT/pc-matched/report.json`, matched-control document; offered/used operations remain distinct |
| `pc-controls` | k1/k32 runs and harm, new default/matched reports, closed partial random run; `aw.pc_depth_report` | `OUT/pc-controls/`, `PC-controls_report.md`; 1/8/32 common-order comparison, 3/993 random successes and missing slots |
| `pc-settings` | `PC-v1/replication-4-{k32,lr0.05,lr0.2}-20260929` plus corresponding harm | `OUT/pc-settings/{report,k32,lr0.05,lr0.2}.json`, setting report; original/current endpoint scoring and harm recomputed; treatment comes from each plan |
| `aw-b` | `AW-B/calibration-20260929` and `evaluation-20260929`; `aw.aw_b_report` | `OUT/aw-b/report.json` and document; 32 calibration and 30 evaluation memory/setting records independently checked |
| `kappa` | Original 36 endpoint rows, pilot v3, bound aliases and stress records; `scripts.ht3e_independent_review` | `OUT/kappa/report.json`; legacy development population, ES95 and declared pilot verdict retained |
| `ht13` | Receipt-filtered Stage-4 `full-validation-*.npz`; `aw.tail_figures` | `FIG/ht13/tails.json`, `table.md`, `survival_by_dataset.png`, `rarity_vs_severity.png` |
| `ht17` | Full saved Stage-4/AW-B/available-reader vectors and 36 legacy pilot rows; `aw.tail_class --bootstrap 200 --secondary` | `OUT/ht17/{report.json,report.md,cells.csv,sources.json}`; finite-range fits, invalid/sparse fits, conditional intervals |
| `pc-reader` | Six planned trainings/twelve evaluations, new HT-17 snapshot, original selected-v5 reference; `aw.pc_reader_report` | `OUT/pc-reader/report.json`, document; partial coverage remains partial, seeds paired by identity |
| `option-r` | `logs/additional_work/R/queue/20260929T174143/` including resume segments, realization-3 cells, original triplet analysis; `aw.r_report` | `OUT/option-r/report.json`, document; completion/deferral costs, four-realization sensitivity only when fully paired |
| `aw-l` | Available `AW-L/` results and explicitly shared BP controls from `PC-reader/`; `aw.aw_l_report` | `OUT/aw-l/report.json`, document; all 24 planned evaluation slots remain visible |
| `figures` | Newly generated PC/default/control/AW-B/HT-17/κ reports; saved triplet retention | Figure outputs listed below |
| `deck` | Copied twelve slide drafts, timing rules, claim ledger, fresh source-slot register/reports/figures; `aw.presentation_timing`, `aw.rehearsal_pack` | `OUT/documents/deck_v3/`, timing record and numerical sheet; `FIG/deck/` with 12 SVG slides, scripts, backups and manifests |
| `audit` | Fresh reports/deck; `aw.supplemental_audit`, `aw.script_numbers_check` | `OUT/audit/X25/` and `X26/`; X25 FAIL stops the refresh; X26 retains explicit literal-review items |

`results/additional_work/` prefixes are omitted in the table's supplemental
input paths. Every binding is in the report's `sources_sha256`, `sources.json`,
`evidence_bindings`, or X25's checked input index. `catalog.json` collects the
resolved file hashes and their artifact membership without confusing model-state
identities with file hashes. Preserved code under `docs/tasks/PC-9-candidate/old/`
and `round58-source-archive/` supplies only explicitly approved historical bytes.

The `figures` step reproduces all figures used by the current main deck/backups:

| Figure / use | Producer | Output under `FIG` |
| --- | --- | --- |
| Slide 5 retention by realization | `aw.presentation_retention` | `retention/paraphrase-retention.{png,pdf,svg}` and manifest |
| Slide 6 frequency versus severity | `aw.ht17_slides` | `ht17-slide/frequency-severity-stage4.{png,pdf,svg}` and manifest |
| HT-17 full frequency/severity and survival backup | `aw.tail_class_plot` | `ht17/frequency_severity.{png,pdf,svg}`, `survival_thresholds.{png,pdf,svg}` |
| Slide 8 bounded-correction survival | `aw.aw_b_tail_figure` | `aw-b/evaluation-survival.{png,pdf,svg}` and manifest |
| Slide 9 settling-depth backup | `aw.pc_depth_figure` | `pc-controls/depth-retention-harm-cost.{png,pdf,svg}` and manifest |
| Default PC efficacy/harm/cost backups | `aw.pc_result_figures` | `pc/pc_v{0,1}/completed-20260928/efficacy-harm-cost.{png,pdf,svg}`; historical suffix retained inside this fresh tree |
| κ trade-off, stress and historical concentration backups | `scripts.ht9_presentation_figures` | `kappa/` figures and source data; freshly checked pilot plus historical `logs/r1_round35/ht6-final/report.json` |
| Conceptual slides, timelines and source-slot text | `aw.presentation_slides` | `deck/slide01.svg` through `slide12.svg`, resolved Markdown and manifest |

Regenerated numeric tables should agree for unchanged inputs. PDF/SVG timestamps,
source paths and metadata can change file hashes without changing their plotted
values; new manifests describe the new files. Costs of CPU regeneration are
recorded separately from the original GPU measurements.

## Measured costs and what they count

These are seconds from recorded enclosing processes, not estimates of future
GPU time. Do not add parent receipts to their children. Shared BP reader controls
are charged once across PC-reader/AW-L. Option R's parallel process charges differ
from elapsed session time. The catalog gives every receipt's path, SHA-256, field,
status and cost, including unavailable costs and the original failed caption run.

| Work | Measured seconds / scope |
| --- | --- |
| Default PC-v0, 60-cell driver | 49,524.45; separate harm 1,364.03 |
| Depth k1, 12-cell driver | 9,007.37; separate harm 277.07 |
| Depth k32, 12-cell driver | 13,017.39; separate harm 276.46 |
| Random control, stopped partial driver | 4,721.20; not a complete twelve-cell cost |
| Offered-budget adjoint, 12-cell driver | 8,575.71; no separate measured control-harm result |
| Default fixed-v5, four-cell driver | 1,401.87; separate harm 5,004.20, with original final-table failure preserved and numerical completion independently verified |
| Fixed-v5 k32 / lr .05 / lr .2 drivers | 1,787.77 / 1,408.07 / 1,400.67; separate harms 4,956.84 / 4,967.56 / 5,000.56 |
| AW-B calibration / evaluation | 19,467.92 / 21,083.17; endpoints and harm included |
| BP reader training seeds 0/1/2 | 866.58 / 906.53 / 872.04; evaluation is separate |
| ePC reader training seeds 0/1 | 88,483.01 / 86,801.75; seed 2 unfinished at this document's initial snapshot |
| Option R, initial segment | 20,418.40 charged process seconds versus 10,527.93 elapsed closed-segment seconds; contains the ceiling-stopped cell; later resumes add separate closed segments |
| AW-L | No new completed AW-L process cost at the initial snapshot; available full-read controls reuse PC-reader costs |
| κ pilot added nine trainings | Individual enclosing training receipts about 1,022–1,121 s; ordinary trainings reused. The manifest's 21,600 s is an estimate including evaluation, not a measured enclosing total |
| κ pilot retention / unseen evaluations | Each of the 36 bound retention summaries records `wall_seconds` (25.36–31.29 s); each of the 36 bound unseen summaries records it (68.31–75.86 s). The exact source paths and hashes are in `kappa/report.json` → `evidence_bindings`, including the approved ordinary-seed aliases |
| κ pilot historical drift assays | Their saved numeric JSONs do not record enclosing process seconds. The manifest's ≈180 s per assay is a projection; a measured aggregate GPU cost is unavailable from those assay records, not zero |
| Original HT-17 CPU snapshot | 88.92 s; current regeneration time is in its new receipt |

The delivered [REP-1 refresh receipt](../logs/additional_work/reproductions/round60-verified/refresh.json)
records all sixteen steps complete in **262.36 seconds**, with no input changes
during the run. Its [catalog](../logs/additional_work/reproductions/round60-verified/catalog.json)
contains 29 checked report groups, 4,828 unique source bindings and 58 process-cost
entries; the legacy κ endpoint costs described above remain in their bound source
summaries. Nine reader evaluations and their nine matching HT-17 rows are included;
seed 1 CounterFact was still running. All 193 generated outputs are hashed.
This is a host measurement with these saved inputs, not a deadline promise or a
GPU cost. The `round60-check1` and `round60-final` directories are development
checks; `round60-verified` is the delivered reproduction snapshot. Canonical talk
documents have not been promoted from this partial refresh.

## GPU recipes — documentation only

These commands explain how measurements were generated. **The refresh runner
does not execute them.** Fresh GPU results are a new execution, not recovery of
the original trajectory or a replacement for missing evidence. Use fresh output
names, the original scientific recipes/seeds and a free authorized GPU lease.
The owner controls the current queue. No new model fits start on/after October 6;
experimental completion remains October 9 at 17:00 EDT.

In an owner-dispatch shell, use `JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0` with the
same local venv. The commands below are concrete rerun recipes with fresh `repro-`
names; they are not claims to preserve every historical shell argument. Recorded
`plan.json`, `config.json`, training `recipe`/`args` and source hashes settle the
scientific inputs; strict source checks may require a fresh profile after a
runtime change. GPU recipes are documented from existing drivers/receipts and
were **not rerun by REP-1**.

Default PC-v0 and its 1/32-step studies (eight iterations, rate .1 for the default):

```bash
../venv/bin/python -m aw.pc_v0 diagnose --execute --output results/additional_work/PC-v0/repro-diagnostic --wall-seconds 1800
../venv/bin/python -m aw.pc_v0 profile --execute --items 10 --orders 1 --output results/additional_work/PC-v0/repro-profile --wall-seconds 5400
../venv/bin/python -m aw.pc_v0 run --execute --orders 5 --output results/additional_work/PC-v0/repro-default --wall-seconds 86400
../venv/bin/python -m aw.pc_harm_readout --execute --run results/additional_work/PC-v0/repro-default --output results/additional_work/PC-v0/harm/repro-default
../venv/bin/python -m aw.pc_v0 run --execute --orders 1 --credit-iters 1 --output results/additional_work/PC-v0/repro-k1 --wall-seconds 28800
../venv/bin/python -m aw.pc_v0 run --execute --orders 1 --credit-iters 32 --output results/additional_work/PC-v0/repro-k32 --wall-seconds 28800
```

Profile each changed depth first with the matching `--credit-iters`, then use
`aw.pc_harm_readout` on each new run into a separate fresh harm directory. Inputs
are the frozen ePC checkpoint, archived S5 calibration/stream rules and final
snapshot identities; v0 harm has 4,064 positions, not the R1 full inventory.

Direction and offered-budget controls use `aw.pc_random_run` and
`aw.pc_matched_run`: for each module, `profile --execute --output <fresh-profile>`,
then `run --execute --output <fresh-run>`. The exact twelve-cell plans are in
their saved `plan.json` files; matched item budgets come from the completed
eight-step SE-E reference. **Do not resume the published random arm**: DEC-079
closed its resource-stopped result. The CPU control report explicitly retains
the 993 attempted random items and ten unstarted cells.

Fixed-v5 acquisition, followed by a separate full-inventory harm run:

```bash
../venv/bin/python -m aw.pc_v1_run profile --execute --output results/additional_work/PC-v1/repro-profile --wall-seconds 14400
../venv/bin/python -m aw.pc_v1_run run --execute --profile results/additional_work/PC-v1/repro-profile --output results/additional_work/PC-v1/repro-default --wall-seconds 28800
../venv/bin/python -m aw.pc_v1_harm --execute --run results/additional_work/PC-v1/repro-default --output results/additional_work/PC-v1/harm/repro-default --wall-seconds 14400
```

Repeat profile/run with distinct names and respectively `--credit-iters 32`,
`--error-lr .05`, `--error-lr .2`; the harm adapter reads the bound treatment from
the completed run. The selected BP-trained v5 reader, populations and endpoints
stay fixed. Original result directories are the three `replication-4-*` paths in
the CPU table. A small descriptive difference is not an equivalence test.

AW-B's development selection and exposed evaluation:

```bash
../venv/bin/python -m aw.aw_b_calibrate calibrate --execute --ranking minimum --output results/additional_work/AW-B/repro-calibration --wall-seconds 28800
../venv/bin/python -m aw.aw_b_calibrate evaluate --execute --selection results/additional_work/AW-B/repro-calibration/selection.json --output results/additional_work/AW-B/repro-evaluation --wall-seconds 57600
```

Use the saved memories' actual full-endpoint payloads and the approved minimum
across-dataset reduction rule. The selected exp(−1) mixture has an analytic
same-prefix, per-token one-nat bound; selection is not rerun by the CPU refresh.

PC-reader training/evaluation (repeat both rules, seeds 0/1/2 and both datasets):

```bash
../venv/bin/python -m aw.pc_reader_train profile --rule epc --seed 0 --output results/additional_work/PC-reader/repro-profile-epc --wall-seconds 14400 --execute
../venv/bin/python -m aw.pc_reader_train evaluate --training results/additional_work/PC-reader/repro-profile-epc --dataset zsre --development --output results/additional_work/PC-reader/repro-eval-profile-epc-zsre --wall-seconds 7200 --execute
../venv/bin/python -m aw.pc_reader_train train --rule epc --seed 0 --profile results/additional_work/PC-reader/repro-profile-epc --output results/additional_work/PC-reader/repro-train-epc-s0 --wall-seconds 108000 --execute
../venv/bin/python -m aw.pc_reader_train evaluate --training results/additional_work/PC-reader/repro-train-epc-s0 --dataset zsre --evaluation-profile results/additional_work/PC-reader/repro-eval-profile-epc-zsre --output results/additional_work/PC-reader/repro-eval-epc-s0-zsre --wall-seconds 14400 --execute
```

Before full evaluations, complete matching `evaluate --development` profiles
for each rule/dataset and supply `--evaluation-profile <directory>` for every
full evaluation. The full dispatch sequence is in
[reader-runners-owner-commands.md](tasks/reader-runners-owner-commands.md).
The ePC training ceiling above accommodates the observed 24-hour runs; the old
generic four-hour example is not suitable for them. Training uses 300 updates,
identical per-seed initialization/episodes, and the fixed mean of checkpoints
150/200/250/300. Acquisitions remain adjoint; this is distinct from PC-v1.

AW-L uses `aw.aw_l_train profile/train/evaluate` with `--read upper` for new
readers and `--write all` or `--write last` for each evaluation. Reuse the exact
same-recipe PC-reader BP artifacts for `read all`; do not charge/retrain them
again. The linked owner document gives the full commands, matching development
profiles, two read × two write × two dataset × three seed design and 48-hour
portfolio ceiling. No factorial result is inferred from those reused controls.

For example, this new upper-read/last-write seed-0 cell needs its own matching
development profile (repeat evaluation profiles for both write masks/datasets):

```bash
../venv/bin/python -m aw.aw_l_train profile --read upper --seed 0 --output results/additional_work/AW-L/repro-profile-upper --wall-seconds 14400 --execute
../venv/bin/python -m aw.aw_l_train evaluate --training results/additional_work/AW-L/repro-profile-upper --dataset zsre --write last --development --output results/additional_work/AW-L/repro-eval-profile-upper-last-zsre --wall-seconds 7200 --execute
../venv/bin/python -m aw.aw_l_train train --read upper --seed 0 --profile results/additional_work/AW-L/repro-profile-upper --output results/additional_work/AW-L/repro-train-upper-s0 --wall-seconds 14400 --execute
../venv/bin/python -m aw.aw_l_train evaluate --training results/additional_work/AW-L/repro-train-upper-s0 --dataset zsre --write last --evaluation-profile results/additional_work/AW-L/repro-eval-profile-upper-last-zsre --output results/additional_work/AW-L/repro-eval-upper-last-s0-zsre --wall-seconds 14400 --execute
```

Option R uses the frozen realization-3 matrix/recipes and the approved decision:

```bash
../venv/bin/python -m aw.r_run status --resume logs/additional_work/R/queue/20260929T174143
```

The active authorized resume uses `aw.r_run run --resume` with
`--defer-class v0_stable:zsre --defer-class v0_stable:counterfact`, `--execute`
and the bound approved-decision file described in `docs/additional_work/R_decision.md`.
This is an operational continuation owned by Capstan, **not a reproduction
command to paste during an independent audit**. For new execution, construct a
separate authorized session with that same frozen matrix. Do not raise the
ceiling or relabel the killed v0 attempt as completed. CPU `option-r` reads all
closed resume segments and preserves missing/deferred coverage.

For the historical κ pilot, the exact training argument dictionaries are in
`results/R1/pilot/{ht3_kappa02_s*,ht3_kappa05_s*,ht3_clip2_s*}/summary.json` → `args`.
The shared ordinary arms are `r1_50_stream_sel6_text_s{0,1,2}`. The common recipe is:

```bash
../venv/bin/python scripts/r1_50_stream_train.py --pool manifests/revision_v1/train_pool_counterfact_v1.json,manifests/revision_v1/train_pool_zsre_v1.json,manifests/revision_v1/train_pool_mquake_v3.json --pool-items 1000 --steps 300 --batch 2 --n-memory 64 --text-nulls 8 --text-windows 512 --save-every 50 --out-para-nulls --out-para-prob 1.0 --seed 0 --tag repro_ht3_kappa02_s0 --kappa .2
../venv/bin/python scripts/r1_71_average_checkpoints.py --run repro_ht3_kappa02_s0 --steps 150,200,250,300
```

Repeat for seeds 0/1/2 and κ .5 or `--clip-surprisal 2` as specified in pilot v3.
Retention uses `scripts/r1_13_stream_eval.py --delta-steps 5 --delta-lr .1
--null-threshold .5 --rare-overlap 1 --stream-seed 21`; unseen evaluation uses
`scripts/r1_44_unseen_run.py --n-edits 100 --rare-overlap 1`; the tail assay uses
`scripts/r1_54_drift_assay.py --windows 32 --window 128 --rules 0.5:none
--rare-overlap 1 --save-positions`. Each also requires the averaged `--theta`,
dataset and fresh tag; use the recorded evaluation arguments/population in the
pilot's bound aliases, including MQuAKE's v3b retention manifest. These saved
populations differ from the main 245,237-position assay. KP-1 found no saved
identity for the old drift memory, so a new assay is not an exact continuation.
The optional expanded κ readout remains default no.

An explicit zsRE example for the new reader above is:

```bash
../venv/bin/python scripts/r1_13_stream_eval.py --theta /home/derp/cap/assets/runs/pc_cap/R1/pilot/repro_ht3_kappa02_s0/theta_avg150-300.npz --dataset zsre --n 100 --delta-steps 5 --delta-lr .1 --null-threshold .5 --rare-overlap 1 --stream-seed 21 --tag repro_ht3_kappa02_s0
../venv/bin/python scripts/r1_44_unseen_run.py --theta /home/derp/cap/assets/runs/pc_cap/R1/pilot/repro_ht3_kappa02_s0/theta_avg150-300.npz --dataset zsre --n-edits 100 --n-unseen 100 --rare-overlap 1 --tag repro_ht3_kappa02_s0
../venv/bin/python scripts/r1_54_drift_assay.py --theta /home/derp/cap/assets/runs/pc_cap/R1/pilot/repro_ht3_kappa02_s0/theta_avg150-300.npz --dataset zsre --windows 32 --window 128 --rules 0.5:none --rare-overlap 1 --save-positions --tag repro_ht3_kappa02_s0
```

The new paths are `results/R1/stream_eval_repro_ht3_kappa02_s0.json`,
`results/R1/endpoints/repro_ht3_kappa02_s0_unseen_zsre/` and
`results/R1/drift_assay_repro_ht3_kappa02_s0_zsre{,.positions}.json`.
The historical stream evaluator also appends to `results/R1/stream_eval.md`;
the drift script does not refuse an existing tag. These are owner-run historical
recipes, so select unused tags and an appropriate execution workspace. The CPU
refresh never calls these scripts.

## Interpretation and remaining refreshes

The talk connects a proposed active-inference policy loop, measured corrected-PC
learning components and empirical extremes. Neither source integrity nor a fitted
finite-range shape establishes active-inference action selection, an asymptotic
tail class or a coupled-free-energy mechanism. Main Stage-4 GPT-2-small results
do not establish production-scale transfer. Keep exposed populations, dependent
orders, the two harm inventories, partial reader seeds and DEC-074b/080 omissions
visible. After new reader/Option R/AW-L results land, regenerate into new outputs,
revise literal presentation claims, then repeat X25/X26 and the reviewer export.
POST-1 and PRES-9 await the October 2 reviewer feedback.
