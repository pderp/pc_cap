# Reproducing pc_cap (S8-04 handoff draft; tested commands only)

Host: Fedora 44, RTX 5070 12 GiB, `/home/derp/cap/venv`; `P=/home/derp/cap/venv/bin/python`; working
directory `/home/derp/cap/pc_cap` for every command. Resources live one level up under
`/home/derp/cap/assets/` (written `assets/...` below for brevity). Each command is tagged
**[verified]** (run as recorded in its task record), **[pending]** (not yet run on this host), or
**[illustrative]** (the shape of a command the stage will use). *lease* = holds the GPU lease for
minutes to hours; *GPU short* = needs a free device, no lease.

## 1. Environment and assets

```bash
$P -c "import pccap; print(pccap.determinism_report())"      # [verified] determinism flags, versions
$P scripts/fetch_assets.py --verify                              # [verified] datasets/model hashes vs manifests/datasets.json
$P -m pccap.harness.schema validate manifests/frozen.draft.json --kind manifest_frozen   # [verified] frozen draft
make test-fast                                                   # [verified] CPU tests, ~1 min
make test-gpu                                                    # [verified] short GPU tests, ~2 min (device must be free)
```

## 2. Controls (S0) and substrate properties (S1)

```bash
$P -m pytest -q tests/controls -m gpu            # PC-1…PC-9 on the real base (GPU short)
$P -m pccap.cli report --stage S0                # results/S0/report.md
$P -m pccap.analysis.s1_p2 ; $P -m pccap.analysis.s1_p3 ; $P -m pccap.analysis.s1_p5 ; $P -m pccap.analysis.s1_p6   # BP rows (lease)
$P -m pccap.analysis.s1_p1 --epc-weights /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz   # [pending] P1 (lease)
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
$P -m pccap.distill.data --parquet assets/data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet   # shard, byte-exact
$P scripts/reg_timing_probe.py --micro 5 --timed 2                        # s/step per T (lease)
results/REG/run_reg02_v2.sh 500 5400                                      # full run in resumable chunks (lease, ~12 h)
$P -m pccap.distill.preflight --update-assets                             # [pending] REG-03 (GPU short)
$P scripts/reg_pilot_compare.py --run pilot-100                           # trajectory vs the sibling's log
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
$P -m pccap.harness.freeze --final --i-am-the-lead --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800   # the lead's CP-E act → manifests/frozen.json (frozen-confirmatory-v2, DEC-027; v1 superseded by DEC-026)
$P -m pccap.harness.schedule                      # results/S4/jobs.json (fixed order: 210 S4 jobs, then 60 S5; B4 unavailable, SB reused)
$P -m pccap.cli queue [--stage S5] [--max-jobs N] [--dry-run]   # S4-04: runs the list in order, one subprocess per job under the lease; resumable; stops on refusals and systematic failures; stop file results/S4/queue.stop
$P scripts/s4_progress.py                         # read-only progress and ETA
$P -m pccap.analysis.s4_05 --experiment-id <id> ; $P -m pccap.analysis.s4_06 --dataset zsre --experiment-id <id> ; $P -m pccap.analysis.s7_03 --dataset zsre --arm C2 --experiment-id <id>   # as pairs complete (the id is the frozen name + hash prefix, e.g. frozen-confirmatory-v2-84126123)
```

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
