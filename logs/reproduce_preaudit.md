# Reproduction pre-audit (Lane P)

Status: done for the CPU pre-audit. Agent: Codex. Date: 2026-09-11. GPU seconds: **0**.

All **27 CPU commands** in the current REPRODUCE document were attempted from fresh Bash shells in the recreated ENV-05 environment. The initial sequence returned zero for **24/27** commands. The three nonzero results were resolved in isolated follow-ups: explicit sibling location, the correct asset path, and deliberate archiving of an already complete copied grammar run. These are not 27 newly reproduced experiments: several commands render existing evidence, and post-confirmation analyses intentionally have no production inputs.

## Environment and isolation

- Source snapshot: file copy of the checkout at `0d6e8d0a9f513ba7813b86074093b2bf26db9626`; copied-file hashes are recorded in [setup.json](reproduce_round4/setup.json). It predates concurrent later changes by the orchestrator.
- Source/code copy: `/home/derp/cap/pc_cap/.worktrees/reproduce_round4` (ignored). Logs and selected generated evidence are retained under `pc_cap/logs/reproduce_round4/`.
- Environment: `/home/derp/cap/assets/envs/venv-check-plan6-df/bin/python`; no installation or environment edit.
- Resource copy: `/home/derp/cap/assets/tmp/reproduce_round4`. Weights, raw data, shard outputs, fixtures and checkpoints remain outside the repository. Copies are independent files, not shared writable hard links.
- Every command forces `CUDA_VISIBLE_DEVICES` empty and `JAX_PLATFORMS=cpu`; BLAS/OpenMP threads are 2. PYTHONPATH points at the copied source, because the scratch environment has an editable install pointing at the live checkout. `make` receives an explicit `PY` override. Bytecode and pytest caches are disabled; temporary test resources use the isolated assets directory.
- Shells use `bash --noprofile --norc -c`: no inherited interactive aliases or functions. Existing approved read-only sibling access is used for reference metadata and pilot comparison.
- Sealed realization payloads, the production final freeze and production S4/S5/S7 results were excluded from the copy. Only the existing sealed checksum listing was available to the draft builder. No sealed realization was sampled or opened by this audit.

## Commands and outcomes

The exact invocations, exit codes and durations are in [summary.json](reproduce_round4/summary.json); every row below links its own stdout/stderr log. Supplemental invocations and their scope are in [followup.json](reproduce_round4/followup.json).

| CPU command | Initial exit | Wall seconds | Interpretation |
| --- | ---: | ---: | --- |
| [$P -c "import pccap; print(pccap.__file__); print(pccap.determinism_report())"](reproduce_round4/01_environment.txt) | 0 | 1.05 | CPU; JAX 0.11.1, highest precision; imported the isolated source path. |
| [$P scripts/fetch_assets.py --verify](reproduce_round4/02_assets.txt) | 0 | 0.60 | 15/15 committed asset hashes verified. |
| [$P -m pccap.harness.schema validate manifests/frozen.draft.json --kind manifest_frozen](reproduce_round4/03_schema.txt) | 0 | 0.89 | Copied frozen draft validates. |
| [make PY="$P" test-fast](reproduce_round4/04_test_fast.txt) | 2 | 58.36 | 6 sibling-location failures; 350 passed, 5 skipped. With explicit PCCAP_HDPC_PATH: 356 passed, 5 skipped, 52 deselected (see follow-up). |
| [$P -m pccap.cli report --stage S0](reproduce_round4/05_report_s0.txt) | 0 | 0.87 | Rendered from copied historical inputs; no S0 experiment rerun. |
| [$P -m pccap.cli report --stage S1](reproduce_round4/06_report_s1.txt) | 0 | 0.88 | Rendered from copied historical inputs; no substrate experiment rerun. |
| [$P -m pccap.data.splits --audit](reproduce_round4/07_splits_audit.txt) | 0 | 0.86 | Audits S0 sample metadata; it is not the teacher-selected pool rebuild. |
| [$P -m pccap.analysis.s3_05](reproduce_round4/08_cr_distribution.txt) | 0 | 0.86 | Recomputed from the documented default historical throughput root. |
| [$P -m pccap.distill.data --parquet assets/data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet](reproduce_round4/09_distill_data.txt) | 1 | 0.99 | Relative assets/ path fails from the documented cwd. Absolute isolated path succeeds; 52.5M tokens and pinned shard hash reproduced. |
| [$P scripts/reg_pilot_compare.py --run pilot-100](reproduce_round4/10_pilot_compare.txt) | 0 | 0.15 | Historical pilot-100/sibling log comparison succeeds; this is not REG-02 regeneration. |
| [$P scripts/merge_throughput.py results/S2/throughput_baselines.json](reproduce_round4/11_merge_throughput.txt) | 0 | 0.02 | Succeeds using historical profile; printed unavailable labels still say EPC_credit/grammar pending. |
| [$P -m pccap.analysis.d1](reproduce_round4/12_d1.txt) | 0 | 0.85 | Re-renders D1 from copied inputs; do not promote its historical wording automatically. |
| [$P -m pccap.analysis.s3_04](reproduce_round4/13_short_editing.txt) | 0 | 0.91 | Summarizes existing development results; preserves old/default roots. |
| [$P -m pccap.analysis.s3_06](reproduce_round4/14_d2.txt) | 0 | 0.85 | Re-renders D2 from copied inputs; not a new scientific decision. |
| [JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_generator](reproduce_round4/15_grammar_generator.txt) | 0 | 0.92 | Regenerated generator manifest in the copy. |
| [JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_model --steps 3000 --no-lease](reproduce_round4/16_grammar_training.txt) | 0 | 9.41 | CPU training completes in 9.41 s wall; early-stop at step 100, held-out accuracy 0.986328125. |
| [JAX_PLATFORMS=cpu $P scripts/grammar_competence.py](reproduce_round4/17_grammar_competence.txt) | 0 | 35.42 | 35.42 s; base accuracy 0.981; joint reference 1.0 on each task. |
| [JAX_PLATFORMS=cpu $P -m pccap.data.grammar_streams](reproduce_round4/18_grammar_streams.txt) | 0 | 0.88 | Grammar stream manifest regenerated in the copy. |
| [JAX_PLATFORMS=cpu $P -m pccap.fixtures.tracing](reproduce_round4/19_grammar_tracing.txt) | 0 | 2.37 | Tracing regenerated on CPU. |
| [JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_eval](reproduce_round4/20_grammar_calibration.txt) | 0 | 3.33 | Grammar calibration regenerated on CPU. |
| [JAX_PLATFORMS=cpu $P -m pccap.cli run --stage S3 --arm C2 --dataset grammar --manifest manifests/dev/s3_grammar_dev.json --no-lease](reproduce_round4/21_grammar_run.txt) | 4 | 0.93 | Exit 4 refuses a complete copied run. Supplemental --force archives only that isolated run and succeeds. |
| [JAX_PLATFORMS=cpu $P -m pccap.analysis.s3_03](reproduce_round4/22_grammar_analysis.txt) | 0 | 0.98 | Summarizes the copied development matrix; original attempt preceded the successful supplemental C2 rerun. |
| [$P -m pccap.harness.freeze --draft](reproduce_round4/23_draft.txt) | 0 | 1.77 | Isolated draft only: no schema errors, no pending inputs. Not a production freeze validation. |
| [$P -m pccap.harness.schedule](reproduce_round4/24_schedule.txt) | 0 | 0.86 | Draft preview only: scheduled 270, unavailable 30, reused 30; S4 scheduled 210, S5 60. |
| [$P -m pccap.analysis.s4_05](reproduce_round4/25_resource_analysis.txt) | 0 | 0.85 | Zero confirmation runs; empty output is not evidence of completed S4 analysis. |
| [$P -m pccap.analysis.s4_06 --dataset zsre](reproduce_round4/26_paired_analysis.txt) | 0 | 0.91 | Zero rows; classification incomplete. |
| [$P -m pccap.analysis.s7_03 --dataset zsre --arm C2](reproduce_round4/27_order_analysis.txt) | 0 | 0.86 | Zero runs; variation unavailable; checkpoint JS remains a GPU task. |

## Corrections established by the follow-ups

1. **Sibling location in an isolated checkout.** The default is relative to the source checkout. Setting `PCCAP_HDPC_PATH=/home/derp/cap/llm-by-neural-predictive-coding` removes the six environment-location failures. The complete CPU suite then reports **356 passed, 5 skipped, 52 deselected**, with one existing multiprocessing/JAX fork warning, in **66.40 s**. No reference code was imported as a runtime dependency or edited. [Log](reproduce_round4/04b_test_fast_explicit_sibling.txt).
2. **The asset abbreviation is not executable.** From pc_cap, `assets/data/...` points inside the repo; resources actually live one level up. The corrected command using the copied absolute parquet path rebuilt **52,500,000 tokens**, with SHA256 `ae5b795aadcd3ef8990826c1ef37661b53b216e962e3bec8510a8758fecf540d`, the pinned value. Tokenization took **22.82 s** with two Rayon threads. The corrected literal production-document path would be `/home/derp/cap/assets/data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet`, or an explicitly defined assets-root variable. This audit wrote only the isolated copy. [Log](reproduce_round4/09b_distill_data_absolute_path.txt).
3. **A repeated development run is intentionally refused.** The documented grammar run returns exit 4 when the target directory already has a complete run, as it does in this checkout. The isolated follow-up with `--force` archives that copied result and completes the C2 run; base hashes before/after agree. The run metrics report **35.88 s**. The documentation should distinguish first execution from a deliberate rerun, and should explain the archive behavior. This is not a reason to add `--force` silently to production commands. [Log](reproduce_round4/21b_grammar_run_isolated_force.txt).

## Commands requiring a different lane or authority

The following 21 invocations were classified rather than executed. They are also individually recorded in setup.json. None was silently claimed as a CPU success.

| Documented invocation | Why deferred |
| --- | --- |
| `make test-gpu` | GPU subset; not executed in this CPU lane |
| `$P -m pytest -q tests/controls -m gpu` | GPU controls; selector excludes CPU PC-1/4/5/6/7 and PC-10 |
| `$P -m pccap.analysis.s1_p2` | BP substrate GPU lease |
| `$P -m pccap.analysis.s1_p3` | BP substrate GPU lease |
| `$P -m pccap.analysis.s1_p5` | BP substrate GPU lease |
| `$P -m pccap.analysis.s1_p6` | BP substrate GPU lease |
| `$P -m pccap.analysis.s1_p1 --epc-weights /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz` | ePC substrate GPU lease |
| `$P -m pccap.analysis.s1_p3 --epc-weights <same npz>` | Illustrative placeholder; GPU ePC rows |
| `$P -m pccap.data.streams --build` | Teacher generations under GPU lease; regenerates reserved pools |
| `$P -m pccap.cap.calibrate` | BP calibration GPU lease |
| `$P -m pccap.cap.calibrate --epc-weights <npz> --label EPC` | Illustrative placeholder; ePC calibration GPU lease |
| `$P -m pccap.harness.stage_s2 --n 30` | GPU A screening |
| `$P scripts/reg_timing_probe.py --micro 5 --timed 2` | GPU timing lease |
| `results/REG/run_reg02_v2.sh 500 5400` | REG-02 GPU run; owned by orchestrator |
| `$P -m pccap.distill.preflight --update-assets` | GPU preflight and production manifest update |
| `$P -m pccap.harness.stage_s2_throughput --n 100 --arms C0 C1 C2 CR --out results/S2/throughput.json` | GPU throughput lease |
| `$P -m pccap.harness.stage_s2_throughput --arms B0 B1 B3 --out results/S2/throughput_baselines.json --tag baselines` | GPU throughput lease |
| `$P -m pccap.cli run --stage S3 --arm C2 --manifest manifests/dev/s3_smoke.json` | Real-base development GPU lease |
| `$P scripts/sample_confirm.py` | Sealed realization creation is outside this development pre-audit |
| `$P -m pccap.harness.freeze --final --i-am-the-lead [--accept-unavailable <pending…>]` | Lead-only act; illustrative optional syntax |
| `$P -m pccap.cli run --stage S4 --mode confirm --dataset zsre --arm C2 --realization 0 --perm 0 --manifest manifests/confirm/zsre_r0.json` | Production confirmation execution; GPU and lead freeze required |

## Documentation and interpretation changes suggested

- Replace the shorthand asset path inside executable commands and show the explicit environment/sibling variables for worktrees or fresh source copies.
- Correct the comment that `pytest tests/controls -m gpu` runs PC-1 through PC-9. It selects PC-2/3/8/9; CPU PC-1/4/5/6/7 require separate coverage, and PC-10 is slow CPU. `make test-fast` also excludes the slow full PC-1 fixture. The new [control register](../docs/controls.md) explains combined coverage.
- Separate regeneration, report rendering, first execution, intentional reruns, draft preview and the lead-only final freeze. Exit zero from an empty post-confirmation report must remain distinct from a completed analysis.
- Review stale defaults and generated language before promoting regenerated D1/D2/S3 reports. The documented merge prints historical EPC_credit/grammar pending labels; its default inputs are historical throughput profiles. A command can execute correctly and still render stale status.
- Retain the conditional B4 status and optional-key control limits. This pre-audit does not qualify a baseline, repair the scientific gate or change scope.
- S8-01 should repeat the audit on the final tree and validate GPU commands with the execution owner. The live final freeze appeared during this work; it was never injected into this isolated audit.

## Limits and retained evidence

The source copy has no independent Git metadata. Code that invokes Git can discover the parent live checkout; a generated draft from this copy is therefore **not** a reproducible final freeze artifact. The draft builder also has hard-coded read-only paths for some production model identities. These limits are recorded in setup.json and require attention in the final portability audit; no production freeze was made here.

The initial sequence took **127.89 s**, including the source/resource setup. Supplemental tests, the deliberate grammar rerun and the shard rebuild are additional and partly concurrent, so their durations should not be summed as a single sequential wall time. Every execution used the CPU. The initial source-stability check detected only an orchestrator update to ongoing.md; further changes in the live tree after this snapshot are outside this test claim.

The ignored source copy contains all regenerated artifacts. Selected report/metric files are additionally retained in [generated_evidence](reproduce_round4/generated_evidence/) with hashes in followup.json. These are explicitly pre-audit evidence, not replacements for the production reports. The driver is [reproduce_preaudit_round4.py](../scripts/reproduce_preaudit_round4.py); it refuses reuse of its initial destinations.

No existing live repository file, task board or REPRODUCE document was edited, and no commit was made. The stale-document corrections above are recommendations for the documentation owner; applying them to the existing document requires the lead's permission under the standing rule.
