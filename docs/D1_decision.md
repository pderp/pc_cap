# D1 decision memo — validity and feasibility (S2-07)

Written 2026-09-11 11:16 UTC from `results/S2/throughput.json`, `results/S2/projection.json`, `results/S1/report.md`, `results/ENV/kappa.json`.

## 1. Eligibility (from S1-07)

| claim type | status | basis |
| --- | --- | --- |
| BP-only editing programme (C0/C1/C2/CR on zsRE and CounterFact) | **eligible** | S0 controls pass; DATA-01 pools; S2-01 calibration; S2-02 A = 0.3; S3 harness smokes |
| matched-fidelity substrate claims (SB vs SE-A / SE-E) | **unavailable, not failed** | no ePC checkpoint (T1 open; PA-1 clock 2026-09-11 23:59 ET; regeneration needs REG-00 and a ≤ 10 GPU-h pilot verdict) |
| synthetic-only substrate claim | pending | grammar replacement (GRAM-01/02, PA-2) |
| constructed-fixture routing (PR-C) | measured (development) | C2 precision 0.88 [0.83, 0.93], recall 0.89; oracle 1.00; random 0.55; majority-bank 0.67 (S3-02) |

Geometry alerts: none (P2 on one base only). ePC eight-step credit: label 'finite-iteration error credit' (P6 on BP weights). Alerts trigger no number changes.

## 2. κ status

κ = 1.0 (provisional), band [0.5, 2.0]. Local RTX 5070 shared workload: 19.7k tokens/s fwd+bwd (ENV-02). No A100 measurement exists; all ceilings below are read at κ = 1 with the band reported.

## 3. Measured per-edit cost (S2-06, 100 development edits per run, exclusive lease; desktop GPU processes resident and recorded)

| arm | dataset | learning accel s/edit | query accel s/edit | wall s/edit | ES | GS | RET-GS(100) | LS |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | zsre | 0.080 | 0.324 | 0.76 | 0.99 | 0.62 | 0.43 | 1.00 |
| C0 | counterfact | 0.033 | 0.787 | 1.39 | 1.00 | 0.0 | 0.0 | 1.00 |
| C1 | zsre | 0.305 | 0.351 | 1.15 | 1.00 | 0.43 | 0.31 | 1.00 |
| C1 | counterfact | 0.135 | 0.180 | 0.84 | 1.00 | 0.0 | 0.0 | 1.00 |
| C2 | zsre | 0.095 | 0.122 | 0.54 | 0.99 | 0.47 | 0.3 | 1.00 |
| C2 | counterfact | 0.045 | 0.153 | 0.65 | 1.00 | 0.0 | 0.0 | 1.00 |
| CR | zsre | 0.067 | 0.111 | 0.47 | 1.00 | 0.56 | 0.38 | 1.00 |
| CR | counterfact | 0.033 | 0.154 | 0.63 | 1.00 | 0.0 | 0.0 | 1.00 |
| B0 | zsre | 0.000 | 0.090 | 0.10 | 0.00 | 0.0 | 0.0 | 1.00 |
| B0 | counterfact | 0.000 | 0.566 | 0.58 | 0.00 | 0.0 | 0.0 | 1.00 |
| B1 | zsre | 0.102 | 0.563 | 0.72 | 0.08 | 0.04 | 0.15 | 0.00 |
| B1 | counterfact | 0.061 | 0.148 | 0.23 | 0.08 | 0.03 | 0.06 | 0.00 |
| B3 | zsre | 0.092 | 0.150 | 0.27 | 0.10 | 0.07 | 0.13 | 0.00 |
| B3 | counterfact | 0.065 | 0.089 | 0.17 | 0.07 | 0.04 | 0.07 | 0.00 |
| CR_uniform | zsre | 0.142 | 0.262 | 0.78 | 0.99 | 0.41 | 0.18 | 0.93 |
| CR_uniform | counterfact | 0.083 | 0.181 | 0.75 | 0.98 | 0.0 | 0.0 | 1.00 |

Unavailable arms: {'B4': 'S2-05 pending', 'EPC_credit': 'REG-03 pending', 'grammar': 'GRAM-02 pending'}.

## 4. Scope selection (Section 9 algorithm; SD-5 headroom 0.75; accelerator seconds)

S4 ceiling 36 A100-h → budget after headroom 27.0 local h at κ = 1.0. Baseline arms B3/B4 are not measured yet: their cost is assumed = C1 × 1.0 (flagged `assumed_arms`). Grammar cost: included.

| zsRE | CounterFact | grammar | local h | affordable |
| ---: | ---: | ---: | ---: | --- |
| 3000 | 1000 | 10000 | 282.5 | False |
| 3000 | 300 | 10000 | 275.9 | False |
| 1000 | 1000 | 10000 | 252.7 | False |
| 1000 | 300 | 10000 | 246.1 | False |
| 1000 | 300 | 256 | 26.3 | True |
| 300 | 1000 | 10000 | 242.5 | False |
| 300 | 1000 | 256 | 22.7 | True |
| 300 | 300 | 10000 | 235.9 | False |
| 300 | 300 | 256 | 16.1 | True |

**Selected scope: zsRE 1000, CounterFact 300, grammar 256** (26.3 local h of the 27.0 h budget). This is written into the frozen manifest at S4-02; the C0 initial scope is 300 with its extension optional.

## 5. Wall-clock feasibility (calendar, not the ceiling)

Wall time per edit exceeds accelerator time by 1.0–3.4× (host dispatch and per-token decode loops of the E.2 protocol). At the selected scope the confirmatory editing core (5 arms × 15 runs per dataset + C0 initial 300) is ≈ 22 wall hours on this host serialized on the GPU lease.

HARN-BATCH (2026-09-10): batched cap-on evaluation with token-for-token parity to the sequential reference decoder (`results/S0/controls/harn_batch_parity.json`) and the last-row logits path — measured first pass (sequential evaluator) → batched:

| run | wall s/edit before | after | query accel s/edit |
| --- | ---: | ---: | --- |
| C0/zsre | 3.71 | 0.76 | 0.157 → 0.324 |
| C0/counterfact | 8.65 | 1.39 | 0.384 → 0.787 |
| C1/zsre | 3.56 | 1.15 | 0.199 → 0.351 |
| C1/counterfact | 8.52 | 0.84 | 0.411 → 0.180 |
| C2/zsre | 3.08 | 0.54 | 0.148 → 0.122 |
| C2/counterfact | 8.20 | 0.65 | 0.385 → 0.153 |
| CR/zsre | 3.71 | 0.47 | 0.186 → 0.111 |
| CR/counterfact | 8.45 | 0.63 | 0.398 → 0.154 |

**Engineering already applied (no protocol change):** HARN-BATCH batches the cap-on evaluation (decode steps across prompts with per-sequence host retrieval; rescoring, LS and drift batched) and was reported only after token-for-token parity with the sequential reference decoder (E.2). Learning itself remains per item and sequential. **Fallback if HARN-BATCH does not land before S4-01:** scope zsRE 300 / CounterFact 300 / grammar 256 (16.1 accelerator h; ≈ 10 wall h), then the §10 drop order (HVP → R-e/R-g → S6 → ablations → C0 extension → T3); never the endpoint, margins, realizations or orders.

## 6. Open items with owners

- B1/B3 (S2-03/S2-04): BASELINES lane (ongoing3.md Lane F) — required for the projection to stop assuming baseline cost = C1 and for S3-04.
- B4 (S2-05a/b → S2-05): GRACE lane D — PA-6 bound.
- Grammar (GRAM-01/02, DATA-06/07): Lane G′ — PA-2 clock.
- ePC checkpoint: T1 / REG-00 (Lane E) — BP-only month otherwise.
- DATA-02 sealed realizations/orders: orchestrator after DATA-02a (Lane H).

## 7. Week-2 queue

S3-01 (CP-D: controls.md + development matrix, done except PC-10) → S3-04 short editing checks with baselines as they land → S3-03 grammar runs (after GRAM-02) → S3-05 CR distribution from development C2 routes → S3-06 D2 memo → S4-01 freeze (frozen.json incl. DEC-009 policy text, SD-13..17) → S4-02 scope → S4-03/04 confirmatory queue.
