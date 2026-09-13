# Reproducing pc_cap (S8-04 handoff draft; tested commands only)

Host: Fedora 44, RTX 5070 12 GiB, `/home/derp/cap/venv`; `P=/home/derp/cap/venv/bin/python`; working
directory `/home/derp/cap/pc_cap` for every command. Resources live one level up under
`/home/derp/cap/assets/` (written `assets/...` below for brevity). Each command is tagged
**[verified]** (run as recorded in its task record), **[pending]** (not yet run on this host), or
**[illustrative]** (the shape of a command the stage will use). *lease* = holds the GPU lease for
minutes to hours; *GPU short* = needs a free device, no lease.

For a fresh shell or isolated source copy, set:

```bash
P=/home/derp/cap/assets/envs/venv-check-plan6-df/bin/python
export PCCAP_HDPC_PATH=/home/derp/cap/llm-by-neural-predictive-coding
```

P2 verified the CPU commands on snapshot `170fad3`; results are in `logs/reproduce_final.md`. Additional v3 checks at `2b35079` passed 24 affected tests, the 60-job grammar-only preview and one matching-source confirm dry-run; see `logs/p2_x2_v3_transition/review.md`.
Regeneration commands write their destinations and belong in a fresh isolated copy during an audit.
Keep resources outside the repo, and preserve the `../assets` relationship or use explicit absolute paths.
Set `make PY="$P" test-fast` to actually use the chosen recreated environment. For CPU-only checks,
set `JAX_PLATFORMS=cpu` and `CUDA_VISIBLE_DEVICES=` before each fresh shell.

## 1. Environment and assets

```bash
$P -c "import pccap; print(pccap.determinism_report())"      # [verified] determinism flags, versions
$P scripts/fetch_assets.py --verify                              # [verified] datasets/model hashes vs manifests/datasets.json
$P -m pccap.harness.schema validate manifests/frozen.draft.json --kind manifest_frozen   # [verified] frozen draft
make PY="$P" test-fast                                           # [verified] P2: 360 passed, 5 skipped, 52 deselected
make test-gpu                                                    # [verified] short GPU tests, ~2 min (device must be free)
```

## 2. Controls (S0) and substrate properties (S1)

```bash
$P -m pytest -q tests/controls -m gpu            # GPU-marked PC-2/3/8/9; combined coverage is in docs/controls.md (GPU short)
$P -m pccap.cli report --stage S0                # results/S0/report.md
$P -m pccap.analysis.s1_p2 ; $P -m pccap.analysis.s1_p3 ; $P -m pccap.analysis.s1_p5 ; $P -m pccap.analysis.s1_p6   # BP rows (lease)
$P -m pccap.analysis.s1_p1 --epc-weights /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz   # P1 GPU rerun; full H record at git 25c988b (lease)
$P -m pccap.analysis.s1_p3 --epc-weights <same npz>   # ePC rows likewise for p2/p5/p6
$P -m pccap.cli report --stage S1
```

## 3. Data, calibration, screening (DATA-01, S2-01, S2-02, S3-05)

```bash
$P -m pccap.data.streams --build ; $P -m pccap.data.splits --audit        # pools (lease: teacher generations)
$P -m pccap.cap.calibrate                                                # radii/b_m for BP (lease)
$P -m pccap.cap.calibrate --epc-weights <npz> --label EPC                # the same for the ePC base
$P -m pccap.harness.stage_s2 --n 30                                      # A screening (lease)
$P -m pccap.analysis.s3_05                                               # CR distribution from C2 routes
```

## 4. ePC checkpoint regeneration (REG-00…03)

```bash
$P -m pccap.distill.data --parquet ../assets/data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet   # shard, byte-exact (assets/ is a sibling of pc_cap; Lane P found the relative path wrong)
$P scripts/reg_timing_probe.py --micro 5 --timed 2                        # s/step per T (lease)
results/REG/run_reg02_v2.sh 500 5400                                      # full run in resumable chunks (lease, ~12 h)
$P -m pccap.distill.preflight --update-assets                             # [pending] REG-03 (GPU short)
$P scripts/reg_pilot_compare.py --run pilot-100                           # trajectory vs the sibling's log (set PCCAP_HDPC_PATH=<sibling checkout> if it is not at the default location; the sibling is read-only)
```

## 5. Development streams and throughput (S2-06, S3-04)

```bash
$P -m pccap.harness.stage_s2_throughput --n 100 --arms C0 C1 C2 CR --out results/S2/throughput.json          # lease
$P -m pccap.harness.stage_s2_throughput --arms B0 B1 B3 --out results/S2/throughput_baselines.json --tag baselines
$P scripts/merge_throughput.py results/S2/throughput_baselines.json ; $P -m pccap.analysis.d1 ; $P -m pccap.analysis.s3_04 ; $P -m pccap.analysis.s3_06
$P -m pccap.cli run --stage S3 --arm C2 --manifest manifests/dev/s3_smoke.json        # one development stream
```

## 5b. Replacement grammar (GRAM-01/02, DATA-06/07, S3-03) — CPU

```bash
JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_generator                # [verified] manifests/grammar/generator.json (rule tables, sample hash)
JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_model --steps 3000 --no-lease   # [verified] trains the base (~10 s), assets/models/grammar/grammar_base.npz
JAX_PLATFORMS=cpu $P scripts/grammar_competence.py                       # [verified] results/GRAM/competence.json
JAX_PLATFORMS=cpu $P -m pccap.data.grammar_streams                       # [verified] manifests/grammar/streams.json
JAX_PLATFORMS=cpu $P -m pccap.fixtures.tracing                           # [verified] manifests/grammar/tracing.json, results/GRAM/tracing.json
JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_eval                      # [verified] grammar calibration (SD-20: exact keys)
JAX_PLATFORMS=cpu $P -m pccap.cli run --stage S3 --arm C2 --dataset grammar --manifest manifests/dev/s3_grammar_dev.json --no-lease   # [verified] one development run
JAX_PLATFORMS=cpu $P -m pccap.analysis.s3_03                             # [verified] results/S3/grammar_dev_matrix.md (matrix + routing vs tracing)
```

## 6. Freeze and confirmatory runs (S4)

```bash
$P scripts/sample_confirm.py                      # DATA-02 sealed realizations/orders
$P -m pccap.harness.freeze --draft --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800   # manifests/frozen.draft.json (proposal)
$P -m pccap.harness.freeze --final --i-am-the-lead --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800   # the lead's CP-E act → manifests/frozen.json (current default frozen-confirmatory-v3, DEC-030; v3 supersedes grammar only)
$P -m pccap.harness.schedule                      # results/S4/jobs.json (fixed order: 210 S4 jobs, then 60 S5; B4 unavailable, SB reused)
$P -m pccap.cli queue --dataset grammar --dry-run  # active v3 CPU preview: requires final freeze and matching schedule
mkdir -p results/S5                              # needed on a fresh copy before an S5 dry-run (P2 finding)
$P -m pccap.cli queue --stage S5 --dry-run          # CPU preview; creates queue_summary_dryrun.json
# The run owner may execute a version-authorized queue without --dry-run; --max-jobs N bounds a session.
# Stop file: results/S4/queue.stop. The active v3 queue is grammar-only (--dataset grammar); other results retain v2.
$P -m pccap.cli run --stage S4 --mode confirm --dataset grammar --arm C0 --base GRAM --realization 0 --perm 0 --manifest manifests/grammar/streams.json --dry-run   # P2 v3 delta: exit 0 with matching source; no override or experiment execution
$P scripts/s7_summary.py                         # CPU; rewrites results/S7/summary.json and summary.md (use isolated copy)
$P scripts/s4_progress.py                         # read-only progress and ETA
$P -m pccap.analysis.s4_05 --experiment-id <id> ; $P -m pccap.analysis.s4_06 --dataset zsre --experiment-id <id> ; $P -m pccap.analysis.s7_03 --dataset zsre --arm C2 --experiment-id <id>   # as pairs complete (the id is the frozen name + hash prefix, e.g. frozen-confirmatory-v2-84126123)
```

`<id>`, `<npz>`, `<same npz>` and `N` are placeholders, not literal shell arguments. Supply actual values.
`s4_05`, `s4_06` and `s7_03` accept `--out` to preserve existing reports. The final freeze remains the lead's act;
sampling sealed realizations is not part of the reproduction audit. Queue dry-run writes a summary but executes no jobs.
P2 exactly reproduced the numerical sections of the saved zsRE paired analysis, resource views, zsRE C2 order summary
and all four S7 summaries. Its historical frozen-source positive control resolved one confirm dry-run without GPU or
sealed-payload access; that historical control does not authorize bypassing a source mismatch. The current matching-source v3 dry-run also passes, as recorded in the transition addendum.

### Reruns

Every `pccap run` refuses (exit 4) when its run directory already holds a complete result; pass `--force` only for a
deliberate rerun — it archives the previous result and checkpoint directories as `*.superseded-<stamp>` (never deletes
them). Confirm-mode jobs additionally refuse on any change under `src/pccap` since the freeze (exit 2, code drift) and on
frozen-identity mismatches; after v2 execution the analysis tree was versioned separately
(`manifests/analysis_versions.json`, DEC-028); later ablation knobs and the deterministic grammar seed/filter are bound by the lead's v3 freeze (DEC-029/030). The queue (`pccap queue`) applies these rules automatically.

## 7. Artifact index

| artifact | location | provenance |
| --- | --- | --- |
| GPT-2 small (teacher) | `assets/models/gpt2` | HF snapshot `607a30d7…`, hashes in `manifests/datasets.json` |
| ePC checkpoint | `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz` | REG-02 (this repository; DEC-014/015), `manifests/assets.json` |
| OpenWebText shard | `assets/data/raw/openwebtext/openwebtext.bin` | sha256 `ae5b795a…` = the sibling's pinned value |
| editing pools, LM sets | `assets/data/prepared/{editing,lm}/` | DATA-01/04; manifests under `manifests/dev/` |
| sealed confirmation manifests | `manifests/confirm/` | DATA-02; `SHA256SUMS` |
| results and logs | `results/`, `logs/`, `docs/tasks/` | per task record |

Licences: GPT-2 (modified MIT), zsRE/CounterFact (MIT via ROME), OpenWebText (CC0), WikiText-103
(CC BY-SA), UD-EWT (CC BY-SA), FabricPC (MIT), GRACE clone (no licence file; reference use only),
sibling repository (no licence; read-only reference).

Remaining work in priority order: see `docs/ongoing.md` §2–§3 and `docs/tasks/STATUS.md`.
