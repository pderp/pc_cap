# Task status board

Regenerated 2026-09-09 19:27 UTC from `manifests/tasks.json` by `python -m pccap.harness.status`.
Do not edit by hand.

| status | count |
| --- | ---: |
| done | 19 |
| ready | 11 |
| pending | 55 |

GPU seconds charged to tasks so far: 0

## ENV

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENV-01 | Python environment (JAX venv) verified and completed | **done** | INTEGRATOR | — | short | no | orchestrator | pending |  |
| ENV-02 | Shared-workload benchmark and kappa | **done** | INTEGRATOR | ENV-01, DATA-00 | lease | no | orchestrator |  |  |
| ENV-03 | Package scaffold, contracts v0, Makefile, docs skeleton | **done** | INTEGRATOR | ENV-01 | none | yes | orchestrator | pending |  |
| ENV-04 | Sibling reference recorder (read-only sibling, DEC-003) | **done** | INTEGRATOR | ENV-03 | none | no | orchestrator | pending |  |

## DATA

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DATA-00 | Fetch and hash public assets into assets/ | **done** | DATA | ENV-01 | none | no | orchestrator |  |  |
| REF-01 | Reference oracle fixtures from HF PyTorch (CPU env under assets/) | **ready** | DATA | DATA-00 | none | no |  |  |  |
| DATA-01 | Editing pools | **ready** | DATA | S0-09 | lease | yes |  |  |  |
| DATA-02 | Realizations, orders, sealed confirmation manifests | **pending** | DATA | DATA-01, DATA-08 | none | yes |  |  |  |
| DATA-03 | MODULAR-CONTROL fixture | **ready** | DATA+MEMORY | ENV-03, CAP-05 | none | yes |  |  |  |
| DATA-04 | LM, probe and property sets with inventory | **ready** | DATA+METRICS | DATA-00 | none | no |  |  |  |
| DATA-06 | Grammar task streams | **pending** | DATA | GRAM-02 | none | no |  |  |  |
| DATA-08 | Challenge sets | **pending** | DATA+BASELINES | DATA-01 | short | no |  |  |  |

## S0

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S0-01 | Asset inventory and lead queue (T1) | **ready** | INTEGRATOR+BASE | ENV-04, DATA-00 | none | no |  |  |  |
| S0-03 | Schemas, outcome codes, CLI skeleton, ledger, records | **done** | INTEGRATOR | ENV-03 | none | yes | orchestrator |  |  |
| S0-04 | BP base wrapper (GPT-2 small in JAX) | **done** | BASE | ENV-01, ENV-03, DATA-00 | short | yes | orchestrator |  | HF-oracle rows pending REF-01 |
| S0-05 | Hidden-site adjoints and forced interventions | **done** | BASE | S0-04 | short | yes | orchestrator |  |  |
| S0-06 | ePC base wrapper on FabricPC and declared energy (BP weights first) | **done** | BASE | S0-04, ENV-04 | short | yes | orchestrator |  |  |
| S0-07 | Metric library with known-answer tests | **done** | METRICS | ENV-03 | none | yes | codex | a39be6b | Implementation verified (33 tests); awaiting Claude control review and merge. Do not overwrite owned paths. |
| S0-07b | HVP small-matrix controls (optional) | **done** | METRICS | S0-07 | none | no | codex | 65ffe84 | 6 small-matrix controls plus all 33 metric controls pass. Based on task/S0-07. Awaiting Claude integration; no real HVP runs. |
| S0-08 | Snapshot, clone, strict resume, resource-stop rollback | **done** | INTEGRATOR | S0-03, CAP-02 | none | yes | orchestrator |  |  |
| S0-09 | Development reservation, tokenization helper, reference decoder | **done** | DATA | DATA-00, S0-03 | short | yes | orchestrator |  | HF decode parity pending REF-01 |
| CAP-01 | Key features and deterministic retrieval | **done** | MEMORY | ENV-03 | none | no | orchestrator |  |  |
| CAP-02 | Slot metadata, use-count semantics, byte layout | **done** | MEMORY | CAP-01 | none | no | orchestrator |  |  |
| CAP-03 | Byte ceiling and capacity | **done** | MEMORY | CAP-02 | none | no | orchestrator |  |  |
| CAP-04 | Transactions, conflicts, eviction, revisions | **done** | MEMORY | CAP-03, S0-08 | none | yes | orchestrator |  |  |
| CAP-05 | Routers | **done** | MEMORY+BASE | CAP-04, S0-05 | short | yes | orchestrator |  |  |
| CAP-06 | Transactional candidate search and budget | **ready** | MEMORY | CAP-05 | short | yes |  |  |  |
| CAP-07 | Complete-edit learning loop | **pending** | MEMORY+DATA | CAP-06, S0-09 | short | yes |  |  |  |
| S0-10 | Minimal cap integration smoke and the four pre-run invariants | **pending** | MEMORY | CAP-07, S0-08, S0-04 | short | yes |  |  |  |
| S0-11 | S0 stage report and CP-C | **pending** | INTEGRATOR | S0-10, S0-06, S0-07, S0-09 | none | yes |  |  |  |

## REG

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REG-00 | JAX distillation driver for ePC regeneration (PA-1 enabler) | **ready** | BASE | DATA-00 | short | no |  |  |  |
| REG-01 | Cost pilot (100 steps) | **pending** | BASE | ENV-04, S0-01, REG-00, S0-06 | lease | no |  |  |  |
| REG-02 | Full regeneration (<= 10 GPU-h) | **pending** | BASE | REG-01 | lease | no |  |  |  |
| REG-03 | Load and preflight | **pending** | BASE | REG-02, S0-06 | short | yes |  |  |  |

## GRAM

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GRAM-01 | Grammar generator per E.1 | **ready** | DATA | ENV-03 | none | yes |  |  |  |
| GRAM-02 | Train the six-layer replacement grammar base | **pending** | DATA+BASE | GRAM-01 | lease | no |  |  |  |
| DATA-07 | Causal tracing pairs on the grammar | **pending** | DATA+METRICS | GRAM-02 | short | no |  |  |  |

## S1

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1-01 | P1 fidelity | **pending** | METRICS+BASE | REG-03, DATA-04, S0-11 | lease | yes |  |  |  |
| S1-02 | P2 geometry | **pending** | METRICS | S0-07, DATA-04, S0-04 | short | no |  |  |  |
| S1-03 | P3 localization and coverage | **pending** | METRICS+BASE | S0-05, S0-06, DATA-04 | short | no |  |  |  |
| S1-04 | P4 separability | **pending** | METRICS | DATA-04, GRAM-02 | short | no |  |  |  |
| S1-05 | P5 write locality | **pending** | BASE+METRICS | S0-10, S2-01, DATA-01 | lease | no |  |  |  |
| S1-06 | P6 finite settling and informativeness | **ready** | BASE+METRICS | S0-06 | lease | no |  |  |  |
| S1-07 | S1 report and D1 input | **pending** | INTEGRATOR+METRICS | S1-01, S1-02, S1-03, S1-04, S1-05, S1-06 | none | yes |  |  |  |

## S2

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2-01 | Residual scales and radius calibration | **pending** | BASE+MEMORY | S0-10, DATA-01 | lease | yes |  |  |  |
| S2-02 | Aggregate step screening | **pending** | MEMORY+METRICS | S2-01 | lease | yes |  |  |  |
| S2-03 | LoRA baselines B1 (and B0) | **ready** | BASELINES | S0-09, S0-04 | short | yes |  |  |  |
| S2-04 | Replay baseline B3 | **pending** | BASELINES | S2-03, S0-08 | short | no |  |  |  |
| S2-05a | GRACE reference environment and smoke (PA-6) | **ready** | BASELINES | DATA-00 | none | no |  |  |  |
| S2-05b | GRACE reference parity cases | **pending** | BASELINES | S2-05a, S0-09 | none | no |  |  |  |
| S2-05 | GRACE baseline B4 adapter with parity (PC-10) | **pending** | BASELINES | S2-05b, S0-04 | short | yes |  |  |  |
| S2-06 | Throughput profile | **pending** | INTEGRATOR | S2-01, S2-02, S2-03, S2-04, S2-05 | lease | yes |  |  |  |
| S2-07 | Full cost projection and D1 memo | **pending** | INTEGRATOR+METRICS | S2-06, S1-07, ENV-02 | none | yes |  |  |  |
| CAP-08 | Read variants R-h0, R-g, R-e (optional) | **pending** | BASE+MEMORY | S0-10, S0-06 | short | yes |  |  |  |
| CAP-09 | Optional difficulty weight | **pending** | MEMORY | CAP-07 | none | no |  |  |  |

## S3

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3-01 | Full control suite and development run matrix | **pending** | INTEGRATOR | S0-11, DATA-03, CAP-07, S2-05, DATA-06 | short | yes |  |  |  |
| S3-02 | Constructed fixture runs | **pending** | MEMORY+DATA | S3-01 | short | no |  |  |  |
| S3-03 | Learned grammar runs and tracing | **pending** | DATA+METRICS | S3-01, DATA-07 | lease | no |  |  |  |
| S3-04 | Short editing checks | **pending** | BASELINES+MEMORY | S3-01 | lease | no |  |  |  |
| S3-05 | CR distribution and re-profile | **pending** | METRICS+INTEGRATOR | S3-02, S3-03, S3-04 | lease | yes |  |  |  |
| S3-06 | D2 memo | **pending** | INTEGRATOR | S3-05, S1-07 | none | yes |  |  |  |

## S4

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ANA-01 | Frozen paired analysis code on synthetic tables (D.11) | **done** | METRICS | ENV-03 | none | yes | codex | bc04bc5 | 19 analysis controls passed; task branch awaiting Claude review/merge. CPU-only. |
| S4-01 | Frozen manifest | **pending** | INTEGRATOR | S3-06, DATA-02, DATA-08, S2-07, ANA-01 | none | yes |  |  |  |
| S4-02 | Scope selection | **pending** | INTEGRATOR | S4-01 | none | yes |  |  |  |
| S4-03 | Confirmatory run schedule | **pending** | run owner | S4-02 | none | no |  |  |  |
| S4-04 | Confirmatory run execution | **pending** | run owner | S4-03 | lease | no |  |  |  |
| S4-05 | Resource views | **pending** | METRICS | S4-04 | none | no |  |  |  |
| S4-06 | Frozen paired analysis and D3 audit | **pending** | METRICS+INTEGRATOR | S4-05 | none | yes |  |  |  |

## S5

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S5-01 | Eligibility and arm definition | **pending** | BASE+INTEGRATOR | S4-01, S1-07, REG-03 | none | no |  |  |  |
| S5-02 | Substrate execution | **pending** | run owner | S5-01 | lease | no |  |  |  |
| S5-03 | Optional substrate repeats and read variants | **pending** | run owner | S5-02, CAP-08 | lease | no |  |  |  |
| S5-04 | S5 report | **pending** | METRICS | S5-02 | none | no |  |  |  |

## S6

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S6-01 | Deficit statement and authorization | **pending** | BASE | S3-06 | none | yes |  |  |  |
| S6-02 | Regularizer implementation | **pending** | BASE | S6-01 | short | no |  |  |  |
| S6-03 | Differentiable error features (create_graph path) with FD test | **pending** | BASE | S6-02 | short | yes |  |  |  |
| S6-04 | Matched continuation pair EPC-CONT / EPC-REG | **pending** | BASE | S6-03 | lease | no |  |  |  |
| S6-05 | P1-P6 on both arms | **pending** | METRICS | S6-04 | lease | no |  |  |  |

## S7

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S7-01 | Cloned-state reversals | **pending** | METRICS | S4-04 | lease | no |  |  |  |
| S7-02 | Damage matrix | **pending** | METRICS | S7-01 | lease | no |  |  |  |
| S7-03 | Order variation from permutations | **pending** | METRICS | S4-04 | none | no |  |  |  |
| S7-04 | Optional HVP diagnostics | **pending** | METRICS | S7-03, S0-07b | lease | no |  |  |  |

## S8

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S8-01 | Core completion and reproduction audit | **pending** | INTEGRATOR+METRICS | S4-06 | lease | yes |  |  |  |
| S8-02 | Fixed exploratory ablations | **pending** | run owner | S8-01 | lease | no |  |  |  |
| S8-03 | Integrated report | **pending** | INTEGRATOR | S8-01, S5-04, S7-03 | none | yes |  |  |  |
| S8-04 | Handoff package and T4 | **pending** | INTEGRATOR | S8-03 | none | yes |  |  |  |

