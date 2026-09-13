# Task status board

Regenerated 2026-09-13 22:21 UTC from `manifests/tasks.json` by `python -m pccap.harness.status`.
Do not edit by hand.

| status | count |
| --- | ---: |
| done | 84 |
| in_progress | 1 |
| partial | 5 |
| ready | 5 |
| pending | 17 |

GPU seconds charged to tasks so far: 118743

## ENV

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENV-01 | Python environment (JAX venv) verified and completed | **done** | INTEGRATOR | — | short | no | orchestrator | pending |  |
| ENV-02 | Shared-workload benchmark and kappa | **done** | INTEGRATOR | ENV-01, DATA-00 | lease | no | orchestrator |  |  |
| ENV-03 | Package scaffold, contracts v0, Makefile, docs skeleton | **done** | INTEGRATOR | ENV-01 | none | yes | orchestrator | pending |  |
| ENV-04 | Sibling reference recorder (read-only sibling, DEC-003) | **done** | INTEGRATOR | ENV-03 | none | no | orchestrator | pending |  |
| ENV-05 | Environment recreation script | **done** | ENV | ENV-01 | none | no | codex |  | D-F approved: real scratch install 150/150 pins; pip check and CPU determinism pass; active package inventory/lock unchanged; CUDA packages installed, GPU execution untested. |

## DATA

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DATA-00 | Fetch and hash public assets into assets/ | **done** | DATA | ENV-01 | none | no | orchestrator |  |  |
| REF-01 | Reference oracle fixtures from HF PyTorch (CPU env under assets/) | **done** | DATA | DATA-00 | none | no | codex |  | fixtures verified by orchestrator; parity tests pass |
| DATA-01 | Editing pools | **done** | DATA | S0-09 | lease | yes | orchestrator |  |  |
| DATA-02 | Realizations, orders, sealed confirmation manifests | **done** | DATA | DATA-01, DATA-08 | none | yes | orchestrator |  |  |
| DATA-03 | MODULAR-CONTROL fixture | **done** | DATA+MEMORY | ENV-03, CAP-05 | none | yes | orchestrator |  |  |
| DATA-04 | LM, probe and property sets with inventory | **done** | DATA+METRICS | DATA-00 | none | no | orchestrator |  |  |
| DATA-06 | Grammar task streams | **done** | DATA | GRAM-02 | none | no | orchestrator |  |  |
| DATA-08 | Challenge sets | **done** | DATA+BASELINES | DATA-01 | short | no | orchestrator |  |  |

## S0

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S0-01 | Asset inventory and lead queue (T1) | **done** | INTEGRATOR+BASE | ENV-04, DATA-00 | none | no | orchestrator |  |  |
| S0-03 | Schemas, outcome codes, CLI skeleton, ledger, records | **done** | INTEGRATOR | ENV-03 | none | yes | orchestrator |  |  |
| S0-04 | BP base wrapper (GPT-2 small in JAX) | **done** | BASE | ENV-01, ENV-03, DATA-00 | short | yes | orchestrator |  |  |
| S0-05 | Hidden-site adjoints and forced interventions | **done** | BASE | S0-04 | short | yes | orchestrator |  |  |
| S0-06 | ePC base wrapper on FabricPC and declared energy (BP weights first) | **done** | BASE | S0-04, ENV-04 | short | yes | orchestrator |  |  |
| S0-07 | Metric library with known-answer tests | **done** | METRICS | ENV-03 | none | yes | codex | a39be6b | Implementation verified (33 tests); awaiting Claude control review and merge. Do not overwrite owned paths. |
| S0-07b | HVP small-matrix controls (optional) | **done** | METRICS | S0-07 | none | no | codex | 65ffe84 | 6 small-matrix controls plus all 33 metric controls pass. Based on task/S0-07. Awaiting Claude integration; no real HVP runs. |
| S0-08 | Snapshot, clone, strict resume, resource-stop rollback | **done** | INTEGRATOR | S0-03, CAP-02 | none | yes | orchestrator |  |  |
| S0-09 | Development reservation, tokenization helper, reference decoder | **done** | DATA | DATA-00, S0-03 | short | yes | orchestrator |  |  |
| CAP-01 | Key features and deterministic retrieval | **done** | MEMORY | ENV-03 | none | no | orchestrator |  |  |
| CAP-02 | Slot metadata, use-count semantics, byte layout | **done** | MEMORY | CAP-01 | none | no | orchestrator |  |  |
| CAP-03 | Byte ceiling and capacity | **done** | MEMORY | CAP-02 | none | no | orchestrator |  |  |
| CAP-04 | Transactions, conflicts, eviction, revisions | **done** | MEMORY | CAP-03, S0-08 | none | yes | orchestrator |  |  |
| CAP-05 | Routers | **done** | MEMORY+BASE | CAP-04, S0-05 | short | yes | orchestrator |  |  |
| CAP-06 | Transactional candidate search and budget | **done** | MEMORY | CAP-05 | short | yes | orchestrator |  |  |
| CAP-07 | Complete-edit learning loop | **done** | MEMORY+DATA | CAP-06, S0-09 | short | yes | orchestrator |  |  |
| S0-10 | Minimal cap integration smoke and the four pre-run invariants | **done** | MEMORY | CAP-07, S0-08, S0-04 | short | yes | orchestrator |  |  |
| S0-11 | S0 stage report and CP-C | **done** | INTEGRATOR | S0-10, S0-06, S0-07, S0-09 | none | yes | orchestrator |  |  |
| DATA-02a | Sealed confirmation loader and seal test | **done** | DATA | DATA-02 | none | yes | codex |  | public loader connected; 90 tests + 5 API smokes (codex); mirrored by the orchestrator |

## REG

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REG-00 | JAX distillation driver for ePC regeneration (PA-1 enabler) | **done** | BASE | DATA-00 | short | no | orchestrator |  |  |
| REG-01 | Cost pilot (100 steps) | **done** | BASE | ENV-04, S0-01, REG-00, S0-06 | lease | no | orchestrator |  |  |
| REG-02 | Full regeneration (<= 10 GPU-h) | **done** | BASE | REG-01 | lease | no | orchestrator |  |  |
| REG-03 | Load and preflight | **done** | BASE | REG-02, S0-06 | short | yes | orchestrator |  |  |

## GRAM

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GRAM-01 | Grammar generator per E.1 | **done** | DATA | ENV-03 | none | yes | orchestrator |  | Lane G′ taken by the orchestrator while REG-02 holds the GPU (codex on Lanes D/V) |
| GRAM-02 | Train the six-layer replacement grammar base | **done** | DATA+BASE | GRAM-01 | lease | no | orchestrator |  | CPU-trained provisional replacement; promote after PA-2 |
| DATA-07 | Causal tracing pairs on the grammar | **done** | DATA+METRICS | GRAM-02 | short | no | orchestrator |  |  |

## S1

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1-01 | P1 fidelity | **done** | METRICS+BASE | REG-03, DATA-04, S0-11 | lease | yes | orchestrator |  |  |
| S1-02 | P2 geometry | **done** | METRICS | S0-07, DATA-04, S0-04 | short | no | orchestrator |  |  |
| S1-03 | P3 localization and coverage | **done** | METRICS+BASE | S0-05, S0-06, DATA-04 | short | no | orchestrator |  |  |
| S1-04 | P4 separability | **done** | METRICS | DATA-04, GRAM-02 | short | no | orchestrator |  | P4 measured in the D.4 error space on the replacement grammar (settled errors of the declared solver on BP weights); natural-language domain unsupported (DATA-04) |
| S1-05 | P5 write locality | **done** | BASE+METRICS | S0-10, S2-01, DATA-01 | lease | no | orchestrator |  |  |
| S1-06 | P6 finite settling and informativeness | **done** | BASE+METRICS | S0-06 | lease | no | orchestrator |  |  |
| S1-07 | S1 report and D1 input | **partial** | INTEGRATOR+METRICS | S1-01, S1-02, S1-03, S1-04, S1-05, S1-06 | none | yes | orchestrator |  | BP and regenerated-ePC rows done; P4 grammar row done (S1-04); report re-rendered; D1 input stands |

## S2

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2-01 | Residual scales and radius calibration | **done** | BASE+MEMORY | S0-10, DATA-01 | lease | yes | orchestrator |  |  |
| S2-02 | Aggregate step screening | **done** | MEMORY+METRICS | S2-01 | lease | yes | orchestrator |  |  |
| S2-03 | LoRA baselines B1 (and B0) | **done** | BASELINES | S0-09, S0-04 | short | yes | codex |  |  |
| S2-04 | Replay baseline B3 | **done** | BASELINES | S2-03, S0-08 | short | no | codex |  |  |
| S2-05a | GRACE reference environment and smoke (PA-6) | **done** | BASELINES | DATA-00 | none | no | codex |  | GRACE CPU reference env + oracle; 6 controls; 5/5 smoke (mirrored by the orchestrator) |
| S2-05b | GRACE reference parity cases | **done** | BASELINES | S2-05a, S0-09 | none | no | codex |  | 20 parity cases isolated+sequential, 63 hashed artifacts (mirrored) |
| S2-05 | GRACE baseline B4 adapter with parity (PC-10) | **in_progress** | BASELINES | S2-05b, S0-04 | short | yes | codex |  | DEC-020: PC-10 in form (b) — Codex: sensitivity control + test rewrite + adapter surface (Lane B4-S, deadline 2026-09-12 12:00 EDT); orchestrator: registration + profile. Element-wise value gaps 0.09–22.4 with 40/40 output/NLL agreement (SD-21) |
| HARN-BATCH | Batched cap-on evaluation with sequential-decoder parity (E.2 optimization) | **done** | INTEGRATOR | HARN-C2 | short | no | orchestrator |  |  |
| S2-06 | Throughput profile | **done** | INTEGRATOR | S2-01, S2-02, S2-03, S2-04, S2-05 | lease | yes | orchestrator |  |  |
| S2-07 | Full cost projection and D1 memo | **done** | INTEGRATOR+METRICS | S2-06, S1-07, ENV-02 | none | yes | orchestrator |  |  |
| CAP-08 | Read variants R-h0, R-g, R-e (optional) | **ready** | BASE+MEMORY | S0-10, S0-06 | short | yes |  |  |  |
| CAP-09 | Optional difficulty weight | **ready** | MEMORY | CAP-07 | none | no |  |  |  |

## S3

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HARN-C2 | C2 probe binding and general stream runner (pccap run --stage S3, all cap arms) | **done** | INTEGRATOR | S0-10, S2-02 | short | no | orchestrator |  |  |
| S3-01 | Full control suite and development run matrix | **done** | INTEGRATOR | S0-11, DATA-03, CAP-07, S2-05, DATA-06 | short | yes | codex |  | control register PC-1…PC-10 with evidence and status (PC-10 recorded failed/unqualified; B4 unavailable); 63 CPU controls pass |
| S3-02 | Constructed fixture runs | **done** | MEMORY+DATA | S3-01 | short | no | orchestrator |  |  |
| S3-03 | Learned grammar runs and tracing | **done** | DATA+METRICS | S3-01, DATA-07 | lease | no | orchestrator |  |  |
| S3-04 | Short editing checks | **done** | BASELINES+MEMORY | S3-01 | lease | no | orchestrator |  | cap arms done; baselines + second order pending |
| S3-05 | CR distribution and re-profile | **done** | METRICS+INTEGRATOR | S3-02, S3-03, S3-04 | lease | yes | orchestrator |  |  |
| S3-06 | D2 memo | **done** | INTEGRATOR | S3-05, S1-07 | none | yes | orchestrator |  |  |

## S4

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ANA-01 | Frozen paired analysis code on synthetic tables (D.11) | **done** | METRICS | ENV-03 | none | yes | codex | bc04bc5 | 19 analysis controls passed; task branch awaiting Claude review/merge. CPU-only. |
| S4-01 | Frozen manifest | **done** | INTEGRATOR | S3-06, DATA-02, DATA-08, S2-07, ANA-01 | none | yes | orchestrator |  |  | v1 written by the lead (DEC-025), superseded before any result (DEC-026); v2 pending the same command |
| S4-02 | Scope selection | **done** | INTEGRATOR | S4-01 | none | yes | lead |  |  | v1 written by the lead (DEC-025), superseded before any result (DEC-026); v2 pending the same command |
| S4-03 | Confirmatory run schedule | **done** | run owner | S4-02 | none | no | orchestrator |  |  | frozen.json written by the lead (DEC-025) |
| S4-04 | Confirmatory run execution | **done** | run owner | S4-03 | lease | no | orchestrator |  | v2: 210/210 (11.49 h); v3 grammar rerun (DEC-029/030): 60/60, 1 code-drift refusal (analysis edit during the queue) rerun; results committed per arm |
| S4-05 | Resource views | **done** | METRICS | S4-04 | none | no | orchestrator |  | resource views over all 210 runs (results/S4/resource_views.json); no arm within the comparable-compute band of C2 |
| S4-06 | Frozen paired analysis and D3 audit | **done** | METRICS+INTEGRATOR | S4-05 | none | yes | orchestrator |  | D3 memo + addenda §7 (drift supplement) and §8 (v3 grammar row: complete, negative); primary claim not supported on any dataset; awaits the lead's T4 review |

## S5

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S5-01 | Eligibility and arm definition | **done** | BASE+INTEGRATOR | S4-01, S1-07, REG-03 | none | no | orchestrator |  |  |
| S5-02 | Substrate execution | **done** | run owner | S5-01 | lease | no |  |  | 60/60 SE-A/SE-E runs complete (8.89 accelerator h of 18.0); SB reused from S4 C1; zsRE contrasts: SE-A≈SB (RET-GS −0.002), SE-E +0.019 RET-GS but −0.34 ES vs SE-A; CounterFact at the exact-key floor |
| S5-03 | Optional substrate repeats and read variants | **pending** | run owner | S5-02, CAP-08 | lease | no |  |  |  |
| S5-04 | S5 report | **done** | METRICS | S5-02 | none | no | orchestrator |  | S5 report written (matched fidelity: SE-A ≈ SB; SE-E retention/acquisition trade-off; CounterFact floor) |

## S6

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S6-01 | Deficit statement and authorization | **ready** | BASE | S3-06 | none | yes |  |  | optional: preregistered proposal from S5 evidence only (DEC-022); no S6 runs this month |
| S6-02 | Regularizer implementation | **pending** | BASE | S6-01 | short | no |  |  | closed for the month (DEC-022): REG charged to S6's allocation; not scheduled |
| S6-03 | Differentiable error features (create_graph path) with FD test | **pending** | BASE | S6-02 | short | yes |  |  | closed for the month (DEC-022): REG charged to S6's allocation; not scheduled |
| S6-04 | Matched continuation pair EPC-CONT / EPC-REG | **pending** | BASE | S6-03 | lease | no |  |  | closed for the month (DEC-022): REG charged to S6's allocation; not scheduled |
| S6-05 | P1-P6 on both arms | **pending** | METRICS | S6-04 | lease | no |  |  | closed for the month (DEC-022): REG charged to S6's allocation; not scheduled |

## S7

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S7-01 | Cloned-state reversals | **done** | METRICS | S4-04 | lease | no | orchestrator |  | reversals and damage matrices on 4 committed checkpoints (zsRE C2 ckpt300, CounterFact C2 end, grammar C2 ckpt1000 and end); 100/75/100/100 pairs | grammar checkpoints rerun under v3 (zero damage/divergence, as v2) |
| S7-02 | Damage matrix | **done** | METRICS | S7-01 | lease | no | orchestrator |  | reversals and damage matrices on 4 committed checkpoints (zsRE C2 ckpt300, CounterFact C2 end, grammar C2 ckpt1000 and end); 100/75/100/100 pairs | grammar checkpoints rerun under v3 (zero damage/divergence, as v2) |
| S7-03 | Order variation from permutations | **partial** | METRICS | S4-04 | none | no | orchestrator |  | order variation computed for every arm on zsRE, CounterFact (B3 only nonzero) and the grammar; JS-at-identical-prefixes part pending checkpoints |
| S7-04 | Optional HVP diagnostics | **pending** | METRICS | S7-03, S0-07b | lease | no |  |  |  |

## S8

| ID | title | status | role | deps | GPU | review | agent | commit | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S8-01 | Core completion and reproduction audit | **done** | INTEGRATOR+METRICS | S4-06 | lease | yes | orchestrator |  | core-completion table + Codex's final-tree CPU reproduction audit (38 invocations; 360 tests pass in the recreated env; grammar retraining bit-identical parameters; confirm dry-run refuses on drift as designed); one harness defect (S5 dry-run summary directory) queued for the post-queue source version |
| S8-02 | Fixed exploratory ablations | **done** | run owner | S8-01 | lease | no | orchestrator |  | (b) byte ceiling ×0.5/×1/×2 on zsRE 300 dev edits: identical (ceiling never binds; the C1>C2 retention gap exists without ceiling pressure); (c) grammar 5% radius: no positive radius exists, runs equal exact keys; (a) not run (CAP-08) |
| S8-03 | Integrated report | **partial** | INTEGRATOR | S8-01, S5-04, S7-03 | none | yes | orchestrator |  | draft 1 of docs/report.md written; §8 (ablations) and the final reproduction audit pending |
| S8-04 | Handoff package and T4 | **partial** | INTEGRATOR | S8-03 | none | yes | orchestrator |  |  |

