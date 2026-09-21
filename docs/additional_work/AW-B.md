# AW-B — bounded correction and stricter gating: pre-registration (draft for the lead's review)

Drafted 2026-09-21 by Claude (orchestrator). Binding plan: `docs/additional_work_plan_final.md` (DEC-073). Status:
**draft; no GPU call before the lead's review.** Supplemental, post hoc; nothing here touches the registered study.

## Question

At query time, does bounding how far the selected v5 cap may move the base distribution (or making it fire less
often) reduce the rare extreme harm on ordinary text while retaining useful editing, and does shaping the correction
do better than simply firing less?

## Interventions (all query-time; memory, acquisition and gate unchanged unless stated)

| arm | definition | bound on per-token loss increase vs base |
|---|---|---|
| v5 | the selected artifact, unwrapped | none |
| cap-off | the base | 0 |
| clip b, b ∈ {0.5, 1, 2, 4} | clip the per-token log-ratio to ±b, renormalise over the full vocabulary (`aw/bounded.clip_tilt`; GT report eq. 19) | 2b nats |
| mixture ρ = e^{−2b} | ρ·base + (1−ρ)·v5, one per b | 2b nats |
| shrink α ∈ {0.25, 0.5, 0.75} | base·exp(α·log-ratio), renormalised | none (global weakening control) |
| gate t, t ∈ {t₀ − 0.1, t₀ − 0.2, t₀ − 0.3} | hard null when null mass ≥ t (lower = stricter); t₀ is the selected threshold; other rejection rules unchanged | none |

Thirteen numerical configurations plus three gate settings; b = 0 and b = ∞ are numerical fixtures, not arms.

## Populations (DEC-073, allocation A)

- **Calibration:** the development payloads `r16_zsre_v5` and `r16_counterfact_v5` (300 items each; exposed
  development data), one qualified v5 development memory per dataset.
- **Evaluation:** the sealed realization-0 confirmatory streams of the primary triplet on zsRE and CounterFact (five
  orders each), which the selected artifact has already seen in R1: **post hoc evaluation on exposed confirmatory
  populations**, paired cell for cell with the block-1 report; no selection is performed on them. MQuAKE only if both
  datasets and the primary study are complete.
- Ordinary-text fidelity: the registered full validation split (1,931 windows, 245,237 positions); known, not fresh.

## Endpoints (fixed here, before any scoring)

Fixed-prefix, full-validation split, against both references (cap-off, original), per arm:

1. maximum signed ΔNLL with location and tie count; ES99 of the positive part including zero mass;
2. exceedance proportions at 0.01, 0.1 and 1 nat;
3. mean KL and mean signed ΔNLL, with the frozen 0.001 / 0.01 lines shown and not reinterpreted;
4. changed-distribution fraction and, separately, gate-firing telemetry.

Efficacy at 300 edits per stream, per arm, with the R1 definitions unchanged: ES, RET-ES, RET-GS, LS (bounded text
equality), near-miss, revision. Resource: reconstruction, full-vocabulary scoring, generation and retries charged.

## Selection and success rule

On the calibration split only: among arms whose RET-GS and RET-ES are within 0.02 absolute of v5 on both datasets
and whose LS and near-miss preservation do not decrease, choose at most **one bound** (the largest reduction of the
maximum, ties broken by ES99) and **one comparator** (the best of shrink and gate by the same criterion). Those two,
v5 and cap-off are the final arms: 4 arms × 2 datasets × 5 orders = 40 paired evaluations (plus the fixed-prefix
assay for all 16 configurations, which costs one pass).

A wrapper is reported as useful when, on the evaluation streams, it lowers the paired maximum and ES99 against v5 in
every order and dataset while staying inside the 0.02 retention tolerance; otherwise the result is the operating
curve. Whether shaping beats firing less is the paired comparison of the chosen bound against the chosen gate.
Uncertainty: paired order/dataset differences shown in full; no interval treats positions as independent; any block
resampling of text is over paired contiguous windows and is labelled as conditional on this split.

## Expectations registered

A trade-off between limiting extreme loss and preserving edits is expected. No prediction is registered about whether
any arm meets the 0.001 mean-KL line; the descriptive pre-analysis of finished cells (`additional_work_plan2.md` §3)
is not a prediction of the intervention (`additional_work_plan3.md` §3).

## Implementation and cost

`aw/bounded.py` (oracle, tested), `aw/wrapper.py` (generation-time cap subclass; unrestricted equals v5 to the bit),
`aw/scoring.py` (all configurations from one base/cap pass with the registered metric code). One streamed pass per
(dataset, memory checkpoint) for the fixed-prefix assay; generation per final arm for the efficacy endpoints. Stop
ceiling 24 GPU-hours (target 12); L4-style pilot on one development stream before dispatch; results under
`results/additional_work/B/`, logs under `logs/additional_work/B/`, manifest `manifests/additional_work/AW-B_v1.json`
with data, code, model, wrapper and reference hashes.
