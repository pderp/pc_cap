# Handoff package (S8-04)

State at 2026-09-13 ≈ 06:00 EDT. Read `docs/report.md` first (the integrated report), then `docs/D3_decision.md`.

## Where everything is

| what | where |
| --- | --- |
| The contract and the executed plan | `docs/pc_cap_month_plan_readable.pdf`; `docs/updated_plan2.md` and deltas `updated_plan3…8.md` |
| Decisions (DEC-000…028) and spec defects (SD-1…22) | `docs/decisions.md`, `docs/spec_defects.md` |
| Lead queue (open items, answered items, freeze commands) | `docs/lead_queue.md` |
| Task board and task records | `docs/tasks/STATUS.md` (generated), `docs/tasks/<ID>.md`, `manifests/tasks.json` |
| Frozen protocol | `manifests/frozen.json` (`frozen-confirmatory-v2`); superseded v1 in `manifests/archive/`; analysis-tree versions in `manifests/analysis_versions.json` |
| Sealed confirmation realizations | `manifests/confirm/` (+ `SHA256SUMS`); opened only by `pccap.data.confirm` |
| Development manifests, grammar manifests, S7 pairs | `manifests/dev/`, `manifests/grammar/`, `manifests/dev/s7_pairs{,_e2}.json` |
| Confirmatory results | `results/S4/frozen-confirmatory-v2-84126123/<dataset>/<arm>/<base>/h/<realization>/<order>/` (config, items, decisions, checkpoints, metrics, cost); `results/S5/…`; learner checkpoints under `/home/derp/cap/assets/runs/S4/…` |
| Frozen analyses | `results/S4/partial/s4_06_{zsre,counterfact,grammar}_complete.json`, `…grammar_supplement.json`, `results/S4/resource_views.json`, `results/S5/paired_*.json`, `results/S7/summary.{json,md}`, `results/S7/order_variation_*` |
| Reports and memos | `docs/report.md`, `docs/D3_decision.md`, `docs/D2_decision.md`, `docs/D1_decision.md`, `results/S5/report.md`, `results/S1/report.md`, `results/S0/report.md`, `docs/controls.md` |
| Reviews and responses | `docs/derp_review{1,2}*.md`, `logs/interim_report*.md`, `logs/review_*.md`, `docs/updated_plan6_review.md`, `logs/grace_*.md`, `logs/reproduce_preaudit.md` |
| Reproduction | `docs/REPRODUCE.md`; environment `docs/environment.md`, `requirements.lock`, `scripts/setup_venv.sh` (ENV-05) |
| Resources (models, data, checkpoints, references) | `/home/derp/cap/assets/` (never inside `pc_cap`); hashes in `manifests/datasets.json`, `manifests/assets.json` |
| Read-only references | `/home/derp/cap/llm-by-neural-predictive-coding` (sibling), `/home/derp/cap/FabricPC`, `/home/derp/cap/assets/third_party/GRACE` |

## How to reproduce the headline numbers (CPU unless stated)

```bash
cd /home/derp/cap/pc_cap; P=/home/derp/cap/venv/bin/python
$P -m pccap.harness.schema validate manifests/frozen.json --kind manifest_frozen
$P scripts/s4_progress.py; $P scripts/s4_progress.py --stage S5             # 210/210 and 60/60
E=frozen-confirmatory-v2-84126123
JAX_PLATFORMS=cpu $P -m pccap.analysis.s4_06 --dataset zsre --experiment-id $E --out /tmp/zsre.json   # negative
JAX_PLATFORMS=cpu $P scripts/s5_paired.py --dataset zsre                                             # SE-A ≈ SB; SE-E trade-off
JAX_PLATFORMS=cpu $P scripts/s4_06_grammar_supplement.py                                             # SD-22 supplement
$P scripts/s7_summary.py                                                                             # damage matrices
$P -m pccap.analysis.s7_01 --checkpoint zsre:C2:ckpt300 --pairs 2      # GPU lease: a two-pair smoke of the S7 runner
```

Rerunning a confirmatory job needs a version-3 manifest (the source tree changed under `src/pccap/analysis/` after the freeze,
DEC-028) — `pccap run --mode confirm` refuses on code drift by design.

## What is not done, and why

| item | state |
| --- | --- |
| B4 (GRACE) contrast | not run: element-wise value parity across frameworks failed; the sensitivity control did not qualify the output-level form; localization points at the reference's fp32 reductions (DEC-020, SD-21, `logs/grace_gradient_localization.md`) |
| Grammar confirmatory row | `incomplete` under the frozen policy (SD-22); labelled supplement provided; a 1-hour rerun with a deterministic paraphrase seed needs a version-3 manifest (lead's option (c)) |
| S6 conditional re-distillation | closed (DEC-022) |
| S8-02 ablation (a) stable keys | not run (needs the optional read variant R-h0, CAP-08) |
| Optional S5-03 repeats / read variants, S7-04 HVP | not run (optional; budget kept) |
| T4 / CP-F | the lead's review of the D3 memo and the report before any external release |

## Rules that still apply

No agent commits without the lead's word; nothing under `src/pccap` changes without a versioned manifest; resources stay
under `assets/`; the sibling and FabricPC are read-only; every result keeps its numerators, denominators, counts and
exclusion reasons (PDF D).
