# Plan 2: executable month plan and sibling-repository reuse assessment

Prepared 2026-09-09. This is a work breakdown and source audit, not a report of completed experiments. All task IDs below are pending unless explicitly described as an observation from this audit.

## 1. Authority, scope, and audit evidence

The source of truth is [the readable month-plan PDF](pc_cap_month_plan_readable.pdf), revised 7 September 2026, 37 pages. References such as F.3, S2, and D.11 below refer to that PDF. Its SHA-256 at this audit is `9a2b64680452394a57da6d07536f00b215320bdd2e7deef65e9f3bec3d359080`. This document operationalizes the entire S0–S8 programme; it does not replace the PDF's thresholds or authorize an expanded research programme. Resolve a genuine PDF contradiction during development and record both readings. Freeze the resolution before confirmation.

Local inputs reviewed:

- `pc_cap` at `8e71d1fb485805e6eba53482d70e6575f41c0766`: the PDF, [summary](pc_cap_month_plan_summary.md), [reference inventory](footnotes.md), [week-one plan](week1/week1plan1.md), [review](week1/review_plan1.md), and [counter-review](week1/counter_review_week1plan1.md). The repository contains documentation, with no `pccap` implementation yet.
- Sibling `../../llm-by-neural-predictive-coding` at `298fc719a0bb3e50a2b818990dd61ccca438ee62`: source/package inventory, implementation of the relevant wrapper, energy, inference, diagnostics and checkpoint interfaces, test inventory, reproduction recipes, documentation, report source, archived result schemas, and vendor provenance. Links into that repository below are relative to this file.
- No applicable `AGENTS.md` was found in either project. Existing documents are preserved; this plan is the new proposed execution baseline.

Audit limits: source inspection establishes reusable mechanisms, not numerical correctness on this machine. Archived reports, CSVs, JSONs and plots are historical evidence with their own protocols; they do not pass any new stage. Vendored Rust internals were inventoried and their integration/provenance reviewed, not exhaustively correctness-audited. No training, checkpoint reproduction, dependency installation, external asset retrieval, or full test suite was performed for this documentation task.

Observed environment: the active `python` is 3.14.7, and `torch`, `transformers`, `numpy`, and `pytest` are absent from that interpreter. The sibling has no `.venv`, `artifacts`, or `runs` directory. `nvidia-smi` cannot communicate with the NVIDIA driver in this execution environment; this does not establish the physical machine's GPU model or the availability of another execution host. The old week plan's RTX 5070 assumptions therefore remain unverified here.

The intended outcome remains one reproducible integrated report, including valid negative or inconclusive findings. Cap v0 is a **PC-motivated gated activation memory** with a frozen transformer, one memory level, and three depths. A second cap level, general domain adaptation, symbolic integration, and framework optimization are outside this month.

## 2. Reuse decision

**Use the sibling as a pinned source dependency behind a small compatibility adapter, not as the project to rename or as an existing implementation of cap v0.** It can shortcut much of base loading, error-coordinate reconstruction, inference instrumentation, artifact preparation, and checkpoint plumbing. The central cap, transactional memory, editing protocol, fixtures, controls, and confirmatory harness still require implementation.

Start with a configurable local dependency path and record its exact commit and any dirty diff. Keep all new orchestration and adaptations in `pc_cap`. Do not make scientific results depend on an unrecorded moving sibling checkout. Before release, choose a reproducible dependency/distribution arrangement with documented provenance. There is no top-level license file in the sibling checkout; do not infer redistribution rights from its availability. This is a provenance task before publishing, not a reason to stop local inspection or design.

### 2.1 Component-level disposition

| Asset and evidence | What it can shortcut | Required adaptation / boundary | Gate and owner |
| --- | --- | --- | --- |
| [wrap.py](../../llm-by-neural-predictive-coding/src/hdpc/wrap.py), `PCGPT2`, `forward_states`, `vanilla_logits`, `final_logits` | GPT-2 loading, masks, residual reconstruction, post-block error sites, no-cache forward reference | Add live sequential bank callbacks; returned states alone cannot implement downstream recomputation. Preserve post-block, pre-`ln_f` sites and last-position-only writes. Expose hidden adjoints with frozen weights. Test actual pinned Transformers behavior. | S0-04/05; BASE |
| [energy.py](../../llm-by-neural-predictive-coding/src/hdpc/energy.py), `prediction_energy`, `LossSpec`, `energy` | Quadratic error penalty plus CE, KD, and unclamped `none` objectives | Existing CE is a token mean, and training multiplies by microbatch size. D.6 token credit uses only the current target; sequence diagnostics use a declared sum. Implement explicit masking/reduction, padding rules, and gamma rather than inheriting scale by accident. | S0-06; BASE |
| [relax.py](../../llm-by-neural-predictive-coding/src/hdpc/relax.py), `relax_errors` | Zero-error initialization, simultaneous error-gradient descent, eval mode, energy traces, no accumulated weight gradients | Fix cap retrieval choices within each inference call; reset every call; instrument actual forward/reverse costs. `grad_norms` describes pre-update iterations: compute terminal gradients explicitly for r8/r64. Existing steps detach and `create_graph=False`; unsuitable unchanged for S6 differentiation through error features. | S0-06, S1-06, S6-03; BASE |
| [models guide](../../llm-by-neural-predictive-coding/docs/models.md), reproduction recipes | Concrete production-model identity and recovery path; avoid gratuitous new 50M-token distillation | Claimed inference weight SHA-256 is `4f0c23aaba9d8daabfc1f455ee673776a940171e2456b3291a5bb00015284eb5`. Weights are absent. Three bundled `.pt` files are small flowmap endpoint tensors, not GPT-2 checkpoints. Locate and verify the actual production artifact; link it to its teacher, configuration, and run. | S0-01; BASE/INTEGRATOR |
| [reproduction package](../../llm-by-neural-predictive-coding/src/hdpc/reproduction/), [model_source.py](../../llm-by-neural-predictive-coding/src/hdpc/model_source.py) | Immutable teacher revision, hash checks, data recipes, dry runs, offline preparation | Teacher snapshot is `607a30d783dfa663caf39e06633721c8d4cfcd7e`. Bundled pilot/frontier tokens are smoke inputs, not new disjoint editing/LM test sets. Large shards must be prepared or located; record document-level overlap. | S0-01/02, DATA-01/04 |
| [checkpoint.py](../../llm-by-neural-predictive-coding/src/hdpc/checkpoint.py) and resume tests | Atomic file replacement, source/protocol checking, Python/Torch/CUDA RNG serialization | New schema must cover cap slots, counters, indices, complete-item boundary, replay/optimizer state, and any NumPy/custom generators. Existing relaxed resume fields and CUDA-RNG mismatch fallback are too permissive for frozen paired runs. Cost ledger must survive learner rollback. | S0-03/08; INTEGRATOR |
| [metrics.py](../../llm-by-neural-predictive-coding/src/hdpc/metrics.py), `g4_distinctness.py` | Float64 cosine accumulation, gradient collection patterns, energy/cost traces | Historical cosine concerns **parameter-update gradients**, not necessarily hidden-site adjoints versus error vectors. Zero-denominator returns of 0 and skipped missing groups do not satisfy structured undefined/missing reporting. Collect the actual signals required by D.2–D.6. | S1-02/03/06; METRICS/BASE |
| [frontier_statistics.py](../../llm-by-neural-predictive-coding/src/hdpc/reproduction/frontier_statistics.py) and archived frontier results | Instrumented error collection, layer histograms, concentration diagnostics | Scalar feature-cell concentration is not D.3's mass per `(layer, token)` after summing width. Recompute PR, active fraction and coverage at specified granularity and sample size. Historical anchor/fresh windows are not 1,000 independent new sequences. | S1-03; METRICS |
| [fidelity.py](../../llm-by-neural-predictive-coding/src/hdpc/reproduction/fidelity.py) | Batched teacher/student scoring and checkpoint loading | Archived KL uses temperature 2 and multiplies by 4; D.1 needs ordinary next-token KL, tails, edit agreement, and 2M held-out tokens. Historical terminal evaluation uses 409,600 positions per dataset and revisits positions for domain shards. Recompute, do not relabel. | S1-01; METRICS |
| [train_distill.py](../../llm-by-neural-predictive-coding/src/hdpc/train_distill.py), `homotopy.py` | Conditional continuation driver, token/KD schedule accounting, optimizer and checkpoints | S6 only: add a validated differentiable regularizer and a matched plain continuation; preserve tokens, optimizer and KD mass on both sides. Full production training is not a default prerequisite or a free asset recovery operation. | S6; BASE |
| [spectral.py](../../llm-by-neural-predictive-coding/src/hdpc/spectral.py), `caprate.py` | HVP/Lanczos patterns and settling diagnostics; may reduce need for external comcrit infrastructure | Existing HVP is of **error-coordinate energy**, not task loss over frozen-topology cap values. Rewrite the objective/coordinates for D.9. Add scalar, Gram-sign, loop-sign and full-block controls. Optional only. | S7-04; METRICS |
| [caprate results](../../llm-by-neural-predictive-coding/results/diagnostics/caprate/RESULTS.md), [flowmap results](../../llm-by-neural-predictive-coding/results/diagnostics/flowmap/RESULTS.md) | Focused hypotheses for solver calibration instead of blind search | Caprate “cap depth” means trailing relaxed base layers, not memory banks. Faster CE solves use particular loss scales. Flowmap results use one GPT-2 block on CPU. Neither establishes end-to-end 12-layer cap speedup or permits a silent solver change. | S1-06; optional development diagnostic |
| [continual.py](../../llm-by-neural-predictive-coding/src/hdpc/continual.py), `train_continual.py` | Result-matrix and experiment-driver patterns | Existing task is weight training on code/legal/bio, with perplexity-based signs and relative metrics. D.7 uses accuracy and best-to-final forgetting. Write new metric functions and frozen-base cap orchestration; do not import these outputs as editing evidence. | S0-07; METRICS |
| [evidence_gate.py](../../llm-by-neural-predictive-coding/src/hdpc/evidence_gate.py), [crown.py](../../llm-by-neural-predictive-coding/src/hdpc/crown.py) | Background experiments only | Evidence gate weights local base updates; crown is a zero-initialized residual MLP. Neither has F.1–F.3 slots, radii, routing or transactions. Do not substitute either for v0 or its optional loss-EMA heuristic. | Defer |
| [tests](../../llm-by-neural-predictive-coding/tests/), especially wrapper, energy, resume and microbatch tests | Existing smoke cases and numerical regression patterns | Tiny fixture is four layers, vocabulary 257, width 64; it is not the six-layer vocabulary-64 learned grammar. Existing tests do not satisfy PC-1–PC-10. Numerical goldens depend on thread settings. | S0; all owners |
| [cluster requirements](../../llm-by-neural-predictive-coding/cluster/requirements.txt), [testing guide](../../llm-by-neural-predictive-coding/docs/testing.md) | Candidate production dependency pins and setup recipe | Python 3.11 environment must be established. Requirements pin direct versions, not all transitives; resolve and lock the actual tested environment. Run focused Python tests first, without building Rust. | S0-02; INTEGRATOR |
| [MORK adapter](../../llm-by-neural-predictive-coding/src/hdpc/mork/), [vendor inventory](../../llm-by-neural-predictive-coding/vendor/README.md) | Future symbolic deployment reference; NumPy forward comparison ideas | No Torch-autograd bridge for cap learning; incremental decode semantics differ from E.2. Native engine and trie work add build/provenance cost, including missing MORK top-level license. Keep off critical path. | Deferred next-month work |
| `reports/`, `results/`, figure generator | Reporting structure, archived observations and failure examples | Use as inherited references. New report must disclose differing protocols, incomplete runs and checkpoint limitations. No transplanted performance claims. | S8; METRICS |

Missing from both local projects: causal-fibres v0.3/support sandbox and joint block diagonalizer, the identified six-layer R8/R9 grammar assets, comcrit, RelaLeap, factual-edit datasets, validated GRACE/LoRA adapters, and a complete `pccap` harness. Search specified asset locations when provided. The essential grammar needs recovery or a documented replacement decision; optional causal-fibres/comcrit assets do not block the BP programme.

Engineering savings are qualitative until integration tests and throughput measurements exist. The strongest shortcut is recovering production weights and adapting the existing PyTorch wrapper. The riskiest shortcut is treating old metrics or a similarly named “cap” as protocol-equivalent.

## 3. Execution ownership and architecture

Role names are assignable work packages, not assumed people or agents already working. One agent may fill multiple roles; with four available workers use one integrator plus three workstream owners, rotating later work as predecessors finish.

| Role | Owned paths in proposed `pc_cap` implementation | Responsibility |
| --- | --- | --- |
| INTEGRATOR | `pyproject.toml`, lockfile, `src/pccap/contracts.py`, `harness/`, `cli.py`, `manifests/` schemas | Interfaces, stage gates, ledger, runs, integration and freeze |
| BASE | `src/pccap/bases/`, `transport/`, base tests | BP/ePC adapters, hooks, credit, solver and conditional continuation |
| MEMORY | `src/pccap/cap/`, `routers/`, transaction/control tests | Memory, routing, conflicts, complete-edit update |
| DATA | `src/pccap/data/`, `fixtures/`, data manifests/generators | Editing data, grammar, modular fixture, disjointness |
| METRICS | `src/pccap/metrics/`, `analysis/`, numerical tests, report generation | Metrics, report card, uncertainty, order diagnostics |
| BASELINES | `src/pccap/baselines/`, parity tests | B0/B1/B3/B4 and optional validated comparators |

Freeze interface version 0 before parallel implementation. BASE/MEMORY must agree on a small analytic mock before either codes against production models. The integrator owns shared schemas; other owners propose changes through a versioned patch.

Proposed contracts:

- `Base.forward(prefix, interventions, retrieval_mode)` returns logits, precisely named pre-write hidden sites, and a per-call cost record. Support no cap, live read-only cap retrieval, and a frozen retrieval trace for differentiation. Hooks include block number, position, dtype and normalization boundary.
- `Base.adjoint(loss_spec, trace, sites)` returns hidden-site adjoints, zero/undefined status, and actual reverse count; one reverse may expose all sites. `EPCBase.infer_errors(...)` returns error tensors, E0…Ek, explicitly measured terminal residual, reset/solver metadata and cost. Unsupported capabilities fail explicitly.
- `Transport` turns a chosen signal into a unit descent direction at a declared site; projects onto allowed fixture subspaces **before** normalization. It never manufactures a direction for a zero vector or flips sign per example.
- `Bank` supplies deterministic read, transaction planning and allocated/occupied byte accounting. `Router` supplies scheduled banks, scores/abstentions, and item-keyed randomness. `Cap` supplies read-only predict, complete-edit update, serialize/restore/clone and memory reporting (F.7).
- Learner snapshot includes all future-behavior-affecting state: arrays, radii, IDs, metadata, correction index, training-use counters, RNG, replay/optimizer if applicable, and caches if any. Immutable base weights can be shared read-only between clones; hash persistent buffers too.
- An append-only **execution ledger is outside rollback state**. Record rejected probes/searches and aborted partial items even when all learner mutations are restored. Evaluation may append telemetry but cannot change subsequent learning decisions.
- Every metric stores value/status, units, numerator, denominator, sample count, strata and exclusions. Distinguish `undefined`, `unreachable`, `unsupported`, `unavailable`, resource stop, unexpected nonfinite failure and ordinary candidate rejection.

Proposed result layout: `results/<stage>/<arm>/<base>/<realization>/<permutation>/`, containing config, source/environment/data/checkpoint hashes, decisions JSONL, metrics, cost ledger, and resumable learner checkpoint. Add read/credit variant to run identity or a configuration-hash subdirectory so optional variants cannot overwrite each other.

## 4. Granular work breakdown and dependencies

Each ID denotes a reviewable unit. Its listed artifact and acceptance condition are required together. Owners attach a commit, evidence path, measured cost and status on completion. Setup/debug smoke outputs are not admissible experimental evidence until the relevant gates pass.

### S0 — harness, assets and invariants (8 A100-equivalent hours)

| ID | Owner; dependencies | Specific subtasks and artifact | Acceptance/checkpoint |
| --- | --- | --- | --- |
| S0-01 | INTEGRATOR + BASE; none | Inventory files and hashes; inspect teacher/model config and tokenizer; locate actual production state dict and full resume state separately; record asset owner/location, source revision and provenance; list absent fixtures. Write `manifests/assets.json`. | Every asset has verified/unavailable status. Matching numerical claims remain pending. No assumption that flowmap `.pt` is weights. CP-A |
| S0-02 | INTEGRATOR; none | Establish Python 3.11 environment; test direct dependency pins against actual hardware; lock transitives; record Torch/CUDA/driver, CPU, RAM, thread count and deterministic settings; run tiny sibling wrapper/energy/resume tests; distinguish asset-dependent skips. Measure a shared local/A100 workload when accessible. | Tested environment and benchmark record, or explicit host/access blocker. A provisional conversion is not measured compliance. CP-A |
| S0-03 | INTEGRATOR; none | Create package/CLI skeleton, typed contracts, outcome schema, manifests and stage report template; separate development/confirmation mode; fail missing required fields; add unique run IDs and append-only attempt ledger. | Analytic mock passes interface contract; no production test data needed. CP-B |
| S0-04 | BASE; S0-02/03 | Adapt BP wrapper; freeze parameters and persistent buffers; disable dropout and KV cache; assert GPT-2 bank sites 4/8/12 (zero-based 3/7/11), last before final normalization; modify only final prefix position; test padding and prompt lengths. | Same-wrapper cap-off behavior on 256 probes; bank order, read-before-write and downstream effect verified. CP-B/C |
| S0-05 | BASE; S0-04 | Expose differentiable hidden leaves while parameters are frozen; collect all bank gradients in one reverse when possible; freeze discrete retrieval for differentiation; implement forced additive intervention separately from stored-memory retrieval; test finite differences on analytic/tiny cases. | Correct descent sign and gradient site; earlier write moves downstream state; no base update. CP-C |
| S0-06 | BASE; S0-02/03 and available ePC assets | Adapt error reconstruction and masked target loss; declare energy, gamma, solver, step size, dtypes, precision matrices, reset and stopping; choose nominal eight steps; implement terminal gradient measurements and call counters; distinguish cap values from transient errors. Document `docs/epc_energy.md`. | Analytic sign, no-clamp consistency, no weight-gradient accumulation and fresh-state tests pass. Late assets require this ePC preflight before any ePC evidence. BP proceeds without them. |
| S0-07 | METRICS; S0-03 | Implement effective rank, PR, overlap, KL/JS, accuracy matrix, complete-answer scoring and structured ratios; numerical fixtures for zero and degenerate inputs; scalar quadratic reversal with displacement eta² and commuting Hessians. | All S0 known-answer tests pass, including unequal singular spectrum having effective rank below algebraic rank. CP-B/C |
| S0-08 | INTEGRATOR; S0-03, MEMORY schema | Implement atomic serialization, clone, strict resume, RNG capture and complete-item snapshot; keep cost ledger external; simulate kill/resume and resource stop after an accepted early answer prefix. | Incomplete item restores all learner state; its compute remains charged. Identical sequences produce identical discrete decisions. CP-C |
| S0-09 | DATA; S0-03 | Reserve/hash small S0 development sample before decoder/smoke use; permanently exclude its subjects/facts from confirmation; implement boundary tokenization, normalization and no-cache greedy reference decoder with mock base first. | Correct target and newline round trip; two-token failure control; hidden answers inaccessible to prediction. CP-B/C |
| S0-10 | MEMORY; S0-03 and CAP-01…07 | Deliver minimum bounded cap, full rollback, memory and clone tests; combine with wrapper, decoder and ledger for one complete development smoke edit. | Four pre-run invariants—cap-off identity, memory accounting, rollback, complete-state cloning—pass before any admissible experiment. A smoke edit may legitimately fail acquisition. CP-C |
| S0-11 | INTEGRATOR; applicable S0 evidence | Publish S0 report and control/dependency table; identify ePC-only missing capabilities; list what is ready for S1/S2 and what is still setup. | No blanket “S0 passed” if required harness invariants are missing. Preparation and repair can continue independently. |

### CAP — F.1–F.4 implementation tasks, integrated during S0/S2

| ID | Owner; dependencies | Implementation details | Evidence / due |
| --- | --- | --- | --- |
| CAP-01 | MEMORY; S0-03 | Implement parameter-free LN0 with epsilon `1e-5`, divide by sqrt(d); allocate immutable FP32 keys and values; key radius uses Euclidean distance, inclusive boundary, smallest immutable ID on ties; zero radius requires exact equality. | Hand-built boundary/tie/zero-vector tests; S0 |
| CAP-02 | MEMORY; CAP-01 | Use packed bounded metadata: radius, successful-item count, creation/last-use, last target token, owner digest/version, optional prior-loss EMA. Count each complete training item at most once per slot across its rounds/prefixes. Choose a bounded item-use marker and document repeat-delivery semantics. No prediction-time count changes. | Multi-prefix/multi-round use count and inference immutability tests; S0 |
| CAP-03 | MEMORY; CAP-02 | Set Bcap=`6144*(8*d+128)`; at d=768 this is 38,535,168 bytes. C0 gets all bytes; C1/C2/CR split equally. Account for indices, alignment, correction bookkeeping, persistent caches and allocator-resident arrays; compute capacity after fixed overhead. Report occupied/allocated and peak training memory separately. | Nominal upper bounds: 6,144 narrow slots for C0; 2,048 per three-bank arm; 1,374 wide-key slots per bank assuming 128 metadata bytes and no other overhead. Actual limits can be lower. PC-6; S0 |
| CAP-04 | MEMORY; CAP-02/03 | Snapshot before conflict/allocation. Distinct conflicting key: old/new radii bounded by `0.49*distance`, preserve old key/value. Identical incompatible key rejects unless explicit newer correction-track version. Retire old fact/version slots only within replacement transaction; bounded active-digest index. Evict lowest successful-use count, then oldest last-use, then lowest ID. | Test rollback of eviction/radii/IDs/RNG; identical ambiguity; newer version; failed replacement; exact revision replay. Full PC-4 before S3, not a stub. |
| CAP-05 | MEMORY + BASE; S0-05, CAP-04 | Routers Last C0, Full C1, Measured C2, Random CR, Supplied CO. C2 forces epsilon*b_m*d_m with epsilon=.01, recomputes downstream **live** discrete retrieval, scores `(L-Lprobe)/epsilon`; require improvement `>max(1e-8,1e-6*L)`, select best positive score, tie by depth, otherwise abstain. CR keyed by seed/item/prefix/round. | Signed helpful/harmful probe; independent forced probe and actual write records; no retained probe mutations. Uniform CR allowed for S2 profiling only. |
| CAP-06 | MEMORY; CAP-04/05 | For b scheduled banks reserve A/b each, no redistribution. Process by depth and recompute loss/features/gates/credit after accepted earlier writes. Test increments `a*b_m*d_m` for a in `{A/b,A/(2b),A/(4b),A/(8b)}` from the same original snapshot, plus no-op. New values start zero. Choose minimum loss, tie smaller increment; commit only above improvement threshold. | Analytic nonmonotone search, accepted state exactly equals evaluated candidate, sum of normalized accepted increments ≤ A. Rejected searches charged. PC-5/6 |
| CAP-07 | MEMORY + DATA; CAP-06, S0-09 | Visit every gold answer prefix including terminating newline; at most five rounds/prefix; stop prefix at CE≤.1. Log threshold attainment separately from end-item free-generated ES/GS. Update metadata consistently; optional EMA uses pre-update loss at rate .2, never fitted residual. | PC-3 repeat 20 threshold-fitted complete edits without extra slots; no single-slot-per-answer assumption. Resource-stop item rollback via S0-08. |
| CAP-08 | BASE + MEMORY; core validated, optional | R-h0 uses cap-disabled hidden pass. R-g adds gradient of CE against cap-off argmax pseudo-label; R-e adds ePC error against the same pseudo-label. Concatenate individually normalized features /sqrt(2); dk=2d. Same key procedure in learning/inference; no true-answer conditioning of keys. | PC-8 hidden-answer substitution leaves key/prediction unchanged; query state resets; charge extra forward/reverse/settle each query; wide-key PC-6. Freeze before use. |
| CAP-09 | MEMORY; optional S8 choice | Difficulty arm `w=max(.1,1/(1+prior_EMA/Lref))`, Lref>0 fixed on development, new slot w=1; weight is inside every tested increment. | PC-5 weighted candidate identity and byte accounting; label heuristic, not Bayesian precision. Primary w=1. |

### DATA — fixtures and datasets, prepared in parallel

| ID | Owner; dependencies | Subtasks and artifact | Acceptance / stage |
| --- | --- | --- | --- |
| DATA-01 | DATA; S0-09, teacher | Pin zsRE editing and CounterFact release/preprocessing; preserve IDs, prompt forms, canonical targets, aliases, paraphrases, neighbours; filter with BP teacher complete generation only; deduplicate facts/subjects; exclude canonical answer+newline >32 tokens; log every exclusion. | At least 300 development edits plus ≥1,000 unrelated/near-neighbour prompts; source selection and split access auditable. S2 |
| DATA-02 | DATA; DATA-01 | Create independent realizations 0/1/2, with subject-disjoint sets where feasible and overlap report; editing order seeds 100–104; separate cap/router/replay seeds. Seal confirmation records and expose only metadata to tuning code. | All arms consume identical items/order within a contrast. Preparation may read source labels for deterministic filtering; no confirmatory outcomes tune choices. S4 |
| DATA-03 | DATA + MEMORY; contracts | Construct masked three-group residual fixture with explicit private/shared paths and partitioned outputs. Supply fixed bank write subspaces to **every** arm, oracle permitted routes only to CO. Generate ≥100 private, ≥100 shared, ≥100 mixed cases, held-out combinations, no-sharing/useful-sharing/wrong-router variants. | Separate 20-target PC-1 and full E.1 ≥95% attainable oracle success, unrelated probability difference ≤1e-6. C2 agreement remains scientific. Before S3 |
| DATA-04 | DATA + METRICS; teacher/tokenizer | Token inventory for 2M-token P1 H; 1M-token WikiText-103 validation drift sample; P2 4,096 positions; P3 1,000 sequences; POS ≥20k train/5k test tagged tokens; E.4 eight domains×256 sequences×128 tokens in separate development/regularizer/final document partitions. Record unique documents/tokens and replacement rules. | Detect insufficient source volume before choosing substitute/repetition. Hashes and new seeds alone do not prove disjointness. S1/S4 |
| DATA-05 | DATA + BASE; asset inventory | Recover six-layer grammar model/tokenizer/generator and verify vocabulary 64, length 64. If unavailable, document replacement specification, base-training cost, competence criterion and scope decision; use tiny untrained networks only for controls meanwhile. | Recovered/replacement provenance explicit; a trained competent fixture exists before learned-grammar evidence. No invented checkpoint continuity. |
| DATA-06 | DATA; DATA-05 | Eight observable contexts, two shared switches and one private switch/context; shared setting consistent across immutable stream. One evaluated token/sequence is one item; supply one causal label. Generate disjoint dev/train/eval, 2,000 eval sequences/task, held-out combinations. Commit five balanced eight-task orders, each task early and late at least once across orders. | Generator property tests: isolated private change, cross-context shared effect, observable context, valid balanced schedule. Training counts selected at S4. Joint-training reference sees same total examples. |
| DATA-07 | DATA + METRICS; DATA-06 | Manifest clean/corrupt pairs changing one latent; freeze patch sites before observing results. Compute restoration score with clean-corrupt probability gap≥.1; retain every site with recovery≥.5, continuous overshoot, weak/no-site/multiple-site cases. | Tracing is separate from oracle truth; no redesign to force a unique depth. S3/S7 |
| DATA-08 | DATA + BASELINES; DATA-01 | Build ≥100 held-out cases each for near-neighbour incompatible answers, unambiguous relation composition, and explicit corrections with stable fact IDs/versions available to all methods. Track currently valid answer and obsolete-answer reappearance. | Separate challenge reports; revisions excluded from immutable order claims; unsupported composition explicitly reported. Prepared before S4 freeze. |

E.2 common decoder: full-prefix recomputation without KV cache; greedy, at most 32 new tokens, stop at newline/EOS; normalize Unicode, case-fold, collapse whitespace, trim ends. Aliases are scoring alternatives unless a shared training augmentation is explicitly frozen. Truncation fails unless a complete accepted answer was already emitted under the common rule. Do not strip arbitrary answer content. All evaluation is read-only. Fixed-prefix probability metrics must not compare different freely generated histories.

### S1 — substrate report card (12 hours; parallel with S2 after S0)

Run every applicable row for BP adjoints, ePC adjoints, and finite ePC error fields; identify which properties describe a base rather than three independent bases. Use a coverage matrix with `complete/pending/unsupported/unavailable`, manifest, prerequisite, count, cost, and evidence path. BP P4 does not disappear when ePC is missing. A synthetic-only model gets latent-label probes and unsupported natural-language metrics, not fabricated POS/LM results.

| ID | Owner; dependency | Subtasks and exact measurements | Output and gate |
| --- | --- | --- | --- |
| S1-01 P1 | METRICS + BASE; S0 gate, DATA-04, actual weights | Ordinary teacher→student KL on 2M held-out tokens at matched teacher-forced positions; feedforward and target-unclamped eight-step checks; mean/p95/p99/max finite KL; base task accuracy and argmax/edit-prompt agreement; initial-correct fraction on teacher-selected stream. | Both means≤1e-3 nats for matched-fidelity claims. Zero-initialized no-loss ePC may simply duplicate feedforward: label consistency check. Common initially-incorrect subset is secondary, never reselect stream. |
| S1-02 P2 | METRICS; S0-07, DATA-04 | Centre features; p_i=s_i²/sum(s²), effective rank=exp(-sum p log p); save spectra, seeds, ratios and zero-matrix status. Fit fixed matched POS/latent probes. | Rank ratio<.9 or probe drop>.02 triggers diagnostic alert, not base exclusion. |
| S1-03 P3 | METRICS + BASE; S0-05/06 | Collect sequence-summed-loss adjoints or declared errors; m_(layer,token)=squared vector norm; PR=(sum m)²/sum(m²), nPR=PR/N; raw/scale-normalized distributions over 1,000 sequences, last-block share, active fraction above .01×max mass, zero fields and dataset layer coverage. | Last-block share>.4 is alert only. Save mechanism-stratified coverage and distinguish scalar-cell historical results. |
| S1-04 P4 | METRICS; DATA-04 or grammar | Per domain/mechanism and layer, centre 8,192 vectors; use top-r orthonormal basis with r=16 only if supported; overlap=||UaᵀUb||F²/r; save captured variance, eigen gaps and resampling stability. | Insufficient rank explicit; optional common lower rank separately labelled. Domain PCA descriptive; shared/private claims require intervention/transfer evidence from fixtures. |
| S1-05 P5 | BASE + METRICS; cap gates, fixed DATA-01 subset | Use Q=200 edit and U=200 unrelated/near-neighbour development prompts; seek 50% current-token loss reduction through bounded F.3-style search at each site; save reached improvement, normalized norm, unreachable outcomes. Apply same write unconditionally to U; separately test actual gated behavior, answer change and firing. Track key movement and slot changes after upstream writes. | Compare collateral at matched achieved improvement where possible; ratio 0/0 undefined and positive/0 right-unbounded. Include ePC procedures when available; gated component requires validated cap. |
| S1-06 P6 | BASE + METRICS; S0-06 | E0…E64 and r_k=||grad E_k||/max(1,||grad E0||); explicit r8/r64; first step achieving 95% of E0−E64 only if positive; nominal eight, optional 16. Error/loss Spearman with constant vectors undefined. Measure real runtime/reverse counts and query costs. | 64 is reference, not guaranteed convergence; use converged language only if r64≤1e-3 and terminal changes small. Any solver change logged on development and frozen. |
| S1-07 | INTEGRATOR + METRICS; above | Publish P1–P6 rows, eligibility versus descriptive alerts, missing coverage and exact credit conventions; reconcile historical KL/cosine/concentration claims with newly measured quantities. | D1: partial rows remain partial. Fidelity failure does not invalidate a same-ePC credit contrast but prevents matched-fidelity BP superiority claim. |

### S2 — calibration, baseline parity and feasibility (12 hours)

| ID | Owner; dependencies | Specific subtasks | Acceptance / evidence |
| --- | --- | --- | --- |
| S2-01 | BASE + MEMORY; S0 gate, DATA-01 | Compute cap-off development median raw residual norms b_m, floor 1e-8; build per-layer/read 20-quantile distance grid; select largest radius with unrelated false-fire≤1%, tie paraphrase coverage. Store every candidate. | Shared within base/read contrast across C0/C1/C2/CR; no positive radius→exact-key pilot and explicit limitation. RET-GS still scores paraphrases. |
| S2-02 | MEMORY + METRICS; S2-01 | Screen only A={.03,.1,.3}, nominal .1, epsilon=.01, R=5, CE stop=.1. Select one shared A by immediate free-generated acquisition under common locality criterion. | Preserve threshold attainment and ES separately. If no candidate functions, ≤3 diagnoses with cheapest discriminating test; no unbounded new sweep. |
| S2-03 | BASELINES; environment/contracts, calibrated experiments after S2-01 | Start dependency/reference smoke tests early. Implement B0, B1/B3 LoRA rank8 on Q/V only in every layer; GPT-2 fused QKV requires slice-aware adaptation with K untouched. Adam, initial LR1e-4, screen {3e-5,1e-4,3e-4}; 10 optimizer steps/complete edit, one epoch/synthetic task. Shared full-answer decoder. | Assert intended trainable tensors and frozen original weights; count optimizer state and all tokens. B0 has zero training updates but evaluation costs. |
| S2-04 | BASELINES; S2-03 | B3 reservoir, ≤5% seen edits and Bcap replay bytes, whichever binds; one replay item/new item/step where available; define rounding, RNG, item storage and revision policy; clone replay and optimizer. | Reservoir/restore tests and reported total state, not a claim that total B3 memory equals cap memory. |
| S2-05 | BASELINES; environment and development manifest | Pin authors' GRACE commit; smoke reference; adapt shared single/multi-token inputs, reference optimization initially 100 value steps, dev layer/radius selection and byte-bound eviction; document every intentional change. | PC-10 parity evidence before B4 comparative claims. No functioning reference→comparison unavailable/incomplete, not “validated by poor score.” B2 EWC/B5 WISE optional with separate parity manifests. |
| S2-06 | INTEGRATOR; cap/baseline parity and calibration | Profile 100–300 complete edits for all cap routing rules, baselines and available ePC credit; include query evaluation, answer-length strata, full memory search, checkpoints/rescoring and reference production costs. Record warmup/compile separately. Provisional CR uniform; later reprofile if S3 bank mix affects cost. | Operation ledger and actual elapsed/accelerator time, peak memory; measured conversion or clear provisional status. |
| S2-07 | INTEGRATOR + METRICS; S2-06 | Build manifest-derived cost sum over grammar, both editing datasets, all arms, 3×5 pairing, checkpoint/endpoint LM/challenge evaluation. Project each allowed stream length and uncertainty. | D1 feasibility memo with complete/partial S0–S2 status and remaining owners/dates; never certify a projection as a measured run. |

### S3 — BP mechanism screening (16 hours, week 2)

| ID | Owner; dependencies | Subtasks | Acceptance / next gate |
| --- | --- | --- | --- |
| S3-01 | INTEGRATOR; S2, fixtures | Run full applicable PC-1–PC-10 suite, attach evidence table; pseudo-label controls required before enabling optional keys. Freeze development run matrix: one realization, two orders. | CP-D: implemented mechanisms pass controls before their S3 runs; optional unavailable mechanisms explicitly excluded. |
| S3-02 | MEMORY + DATA; S3-01, DATA-03 | Run C0/C1/C2/CR/CO on constructed fixture; measure oracle success, private/shared/mixed transfer and harm, wrong-router control, precision/recall versus supplied routes and majority-bank reference. | CO known attainable target is correctness gate. C2 bands .6/.8 are descriptive science, not gates. |
| S3-03 | DATA + METRICS; S3-01, DATA-06/07 | Run C0/C1/C2/CR on learned grammar; joint-training competence reference; full task matrix, held-out combinations and tracing; log continuous/no-site/multisite outcomes. | No demand for a unique mechanistic location. |
| S3-04 | BASELINES + MEMORY; parity | Short BP editing checks under common decoder; route, probe/search, collision, drift, eviction, abstention and allocation records. Separate proposed routes, accepted writes and acquired complete answers. | Demonstrated bugs repaired; valid scientific failures retained. |
| S3-05 | METRICS + INTEGRATOR; S3-02…04 | Estimate final fixed CR bank distribution from development C2 routes only; specify which counts enter estimator and deterministic handling if C2 never routes. Uniform no-route fallback is a proposed development resolution requiring logged declaration. Update throughput if needed. | CR distribution frozen before S4. Actual realized write counts reported even with equal nominal budgets. |
| S3-06 | INTEGRATOR; S1/S3 | D2 memo: correctness versus science, ≤3 diagnoses per failure and cheapest test, core feasibility, optional S6 deficit recommendation, freeze readiness. | A valid negative C2 result proceeds. Missing grammar/reference evidence cannot silently become a completed core comparison. |

### S4 — protocol freeze and confirmatory BP experiments (36 hours)

| ID | Owner; dependencies | Subtasks | Acceptance / evidence |
| --- | --- | --- | --- |
| S4-01 | INTEGRATOR; S1/S3 evidence, DATA-02/08 | Commit `manifests/frozen.json` and analysis revision: all hashes, full arm list, bank sites/radii/b_m/A, loss/solver conventions, byte budgets, dataset IDs, seeds/orders, stream sizes, primary endpoint order, intervals/margins, resource and stopping rules, selected checkpoints and challenge policies. Seal any remaining numerical decisions. | CP-E: schema rejects missing fields; tuning code cannot open confirmation payload; schedule set independently of advantages. Freeze includes negative-case interpretation. |
| S4-02 | INTEGRATOR; measured S2 projection | Choose largest affordable common zsRE prefix from {300,1000,3000}, CounterFact from {300,1000}, grammar count/task from {256,1024,10000}; 25% headroom. Proposed conservative interpretation: projected workload≤.75×ceiling, recorded before freeze. | Grammar plus both edit streams fit as a complete core schedule, or explicit feasibility/scope decision. Do not silently reduce 3 realizations×5 orders. |
| S4-03 | run owners; CP-E | Grammar: C0/C1/C2/CR. Editing: C1/C2/CR plus B3/B4; C0 required initial editing scope, long extension lower priority. Specify C0 initial prefix explicitly (proposed 300) in manifest; only compare its completed common scope. Include B0/B1 curves where already available on identical streams. | Every arm paired by realization/order; CO remains constructed-only. No full factorial grid. |
| S4-04 | run owners; S4-03 | Execute fixed schedule; hash base before/after; save at 100/300/1000/3000 where applicable plus endpoint; record immediate ES/GS, retention, locality, LM drift, strata, memory and costs; checkpoint whole learner. | On resource stop roll back incomplete item and charge it. Keep exact common completed-prefix checkpoints for resource comparison, not just arbitrary endpoints. |
| S4-05 | METRICS; completed pairs | Report exposure-matched and time-matched views, retention versus time/items and longest common completed prefix. Update times within 20% or supporting resource-matched results required for comparable-compute claim. | Incomplete arms shown without imputation. Optional jobs cannot consume reserved core budget. |
| S4-06 | METRICS + INTEGRATOR; S4-05 | Apply D.11 paired analysis from frozen code; publish per-realization/permutation differences and all constraints, including negative/inconclusive classifications. D3 coverage/cost audit. | No post-result endpoint/seed/schedule changes. Bugfix creates version and reruns every affected paired arm or marks comparison incomplete. |

### S5 — controlled representation and credit (24 hours, week 3)

| ID | Owner; dependencies | Subtasks | Acceptance / evidence |
| --- | --- | --- | --- |
| S5-01 | BASE + INTEGRATOR; S4 freeze, ePC preflight/S1 | Determine matched architecture/tokenizer/task eligibility; use fixed C1/R-h: SB=BP adjoints, SE-A=ePC adjoints, SE-E=same ePC finite error credit. Match data, memory, write policy and evaluation. | SB↔SE-A isolates representation; SE-A↔SE-E isolates credit. No routing change hidden in substrate contrast. |
| S5-02 | BASE + run owners; S5-01 | Execute paired streams and capture report-card/cost rows; eight iterations nominal for SE-E. Reuse an S4 SB/C1 run only if all frozen configuration, data/order, checkpoint and measurement semantics match; link provenance and charge shared production once. | Same-ePC credit can be studied if fidelity fails, with narrower claim. Synthetic-only pairs remain synthetic; BP factual editing separate. |
| S5-03 | BASE + MEMORY; optional frozen budget | Optional C2 substrate repeats; R-h0 drift control; R-e vs R-h and same-dimensional ePC R-g. Include BP R-g if claiming added-feature benefit across bases. | Equal byte ceilings, separately calibrated radii, label-free pseudo-target keys, and every extra query cost. No R-e claim without R-g control. |
| S5-04 | METRICS; above | Report all paired outcomes, eligibility limitations and cost frontiers; do not treat repeated cap runs as independent base-training replicates. | S5 stage report / D3 input. |

### S6 — optional matched re-distillation (20 hours including both arms)

| ID | Owner; dependencies | Subtasks | Acceptance / evidence |
| --- | --- | --- | --- |
| S6-01 | BASE + INTEGRATOR; S1/S3 development | Write reproducible deficit and one intervention family; reserve both training and evaluation costs; record run-manifest authorization and independent final holdout before starting. | No deficit, missing weights or unaffordable pair→skip; unused budget reassigned only by logged amendment. |
| S6-02 | BASE + METRICS; S6-01 | Localization family: positive normalized PR penalty, coverage KL(q_ref||q); derive q_ref from useful dev adjoint interventions, floor entries .01 and renormalize, add 1e-8 before shares. Average PR/N only where mass>1e-12; all-zero batch term zero plus explicit event. | Penalize diffusion without rewarding vanishing credit; compare acquisition and unregularized mass. |
| S6-03 | BASE; S6-01, or S6-02 | Alternative private family: fix dev shared basis Q; penalize unrelated labelled private residual overlap only, preserve projected starting error via squared difference. Normalize active objectives by nonzero fixed dev reference magnitudes. Implement actual higher-order/unrolled gradient flow; current `relax_errors` detachment must be replaced in this training path. | Finite-difference/small-model test that regularizer changes parameter gradient; insufficient residual rank unsupported; no domain-wide orthogonalization. |
| S6-04 | BASE; chosen family and gradient test | EPC-CONT and EPC-REG from identical production state, same token order/exposures, optimizer schedule and KD mass sum(wKD*n). Initial active weights .01; only one dev comparison at .0025 allowed. Freeze selected objective/weights. | Do not combine both families without separate matched ablation; sum cost includes both arms and tests. |
| S6-05 | METRICS; S6-04 | Evaluate both P1–P6, fidelity cost and held-out shared/private transfer; save both checkpoints and parity manifest. Cap tests exploratory unless independently registered before confirmation. | A failed regularizer remains a result; no replacement of main ePC checkpoint in already frozen contrasts. |

### S7 — order effects and optional mathematics (10 hours)

| ID | Owner; dependencies | Subtasks | Acceptance / evidence |
| --- | --- | --- | --- |
| S7-01 | METRICS; S4/S5 checkpoints, frozen probe manifest | At selected immutable checkpoints choose 100 independent pairs, stratified shared/private/near-neighbour; exclude revisions and contradictions; clone identical complete learner state; run i→j and j→i with item-keyed randomness. | Same starting state and per-item protocol; all costs recorded; no assumed inverse of discrete updates. |
| S7-02 | METRICS; S7-01 | On fixed Q of edits, paraphrases and unrelated controls compute mean JS, item disagreement/loss changes, routes/write counts/allocations/evictions; damage Iij=mean[L_i(Uj(Ui(s)))−L_i(Ui(s))], positive harmful. Include both orders and strata. | Helpful transfer retained, not folded into harm. Fixed prefixes common to both states. |
| S7-03 | METRICS; S4 permutation outputs | ACC variation across orders, pairwise JS and prediction disagreement at identical prefixes; item-level loss/survival; descriptive PR-E checkpoint table linking P4/P5 to cap outcomes. | Similar accuracy does not imply same forgotten items; two/three bases cannot establish a general substrate law. |
| S7-04 | METRICS; optional capability/budget | Freeze keys/radii/gates/active slots/topology; choose finite cap-value or LoRA parameter block, task-loss Hessians. Use 16 Rademacher probes, four HVPs per commutator application; compute Cij=HiHj−HjHi, Gram mean[(Ca v)ᵀ(Cb v)]. Normalize only for nonzero Hessian norms. | Exact small-matrix Gram PSD/sign, loop I−eta²C, and full sum over cross-bank blocks pass first. Error-energy `spectral.hvp_at` is not drop-in. Report local surrogate, not finite-update mechanism. |

### S8 — replication, selected ablations and report (16 hours)

| ID | Owner; dependencies | Subtasks | Acceptance / evidence |
| --- | --- | --- | --- |
| S8-01 | INTEGRATOR + METRICS; D3 | Complete missing preregistered core pairs first; reproduce selected completed runs from clean state; audit exclusions, ledger totals, fixed-base hashes, failed controls and post-freeze changes. | No added seeds motivated by near-significance; mark irreparable comparisons incomplete. |
| S8-02 | MEMORY + BASE; dev-chosen list frozen before test | Exploratory priority: R-h0 vs R-h, half/double Bcap, optional difficulty weight, R-e/R-g if implemented. Use 3 realizations×2 permutations. | Label exploratory, preserve controls and byte/cost matching within each contrast. Drop before sacrificing core completion. |
| S8-03 | METRICS; all reports | Generate integrated report: P1–P6, routing, representation/credit, acquisition/retention/locality, transfer/order, resource frontiers, uncertainty and complete failure/deviation tables. Distinguish correctness, resource, unmet-assumption and scientific-negative outcomes. | Every claimed effect maps to its controlled contrast; no unsupported claims of causal origin, independent substrate replication or cap-level PC inference. |
| S8-04 | INTEGRATOR; S8-03 | Package source/environment, manifest/generator hashes, baseline modifications/parity, checkpoint paths/provenance, licenses, commands and artifact index. Reproduce a small end-to-end run and rebuild report tables from saved records. | One integrated report and runnable handoff, including unavailable/unscheduled work; two working days remain reserved for overruns. |

## 5. Control and checkpoint register

Control evidence goes to `results/S0/controls/` initially and is referenced, not falsely duplicated, by later stage reports. Keep an applicability column for optional mechanisms.

| Control | Owner | Required cases | Due / what it blocks |
| --- | --- | --- | --- |
| S0 numerical controls | METRICS | Uniform rank-r and unequal spectra; uniform/nonexistent mass; overlap 0/1; unchanged JS=0; scalar quadratic eta² order displacement | Before admissible measurements |
| PC-1 | DATA/MEMORY | ≥19/20 planted targets within round budget, supplied invariant support, unrelated unchanged; full E.1 fixture also ≥95% | Before S3 mechanism evidence |
| PC-2 | BASE | Oracle-false support identity and whole-cap-disabled 256 probes against same-base reference | S0 pre-run invariant |
| PC-3 | MEMORY | 20 threshold-fitted complete edits repeated without intervening updates allocate no extra slots | Before S3 |
| PC-4 | MEMORY | Distinct conflicts; nonnegative radii; preserved old key/value; failed full replacement rollback; identical ambiguity; newer revision; same-version replay | Basic rollback before experiments; full suite before S3 |
| PC-5 | MEMORY/BASE | Helpful/harmful signed probes; nonmonotone bounded search; exact accepted candidate; rollback; weighted update identity when enabled | Before affected cap measurements |
| PC-6 | MEMORY/BASELINES | Equal cap byte ceilings, real overhead and wide-key capacity; aggregate increment; deterministic full-bank eviction; item-use count once per complete item | S0 budget invariant; repeat for new variants |
| PC-7 | DATA/METRICS | Correct first/wrong second token fails; teacher forcing cannot override free-generation failure; newline/EOS/truncation | Before editing measurements |
| PC-8 | DATA/BASE/MEMORY | Read-only complete learner state; query cannot see hidden answer; pseudo-label-derived R-g/R-e keys invariant under hidden-answer substitution | R-h read-only before experiments; auxiliary-key test before enabling variants |
| PC-9 | INTEGRATOR | Complete-state clones; identical sequence replay; reversal start equality; item-keyed CR; scalar order effect; resource-stop rollback with retained cost | S0 cloning invariant; full order harness before S7 |
| PC-10 | BASELINES | Shared single/multi-token reference adaptation parity and documented deviations | Before baseline comparison, full applicable suite before S3 |

| Checkpoint | Target relative window | Evidence to require | If incomplete |
| --- | --- | --- | --- |
| CP-A asset/environment | Week 1 early | Asset inventory, dependency smoke results, small development partition, hardware/conversion status, baseline feasibility started | Independent CPU design/fixtures continue; dependent runs pending |
| CP-B interface/measurement | Week 1 middle | Contracts, hook and decoder tests, numerical controls, learner/ledger separation | Fix owner-specific defects; no artificial global halt for independent preparation |
| CP-C S0 gate | Week 1 middle/late | All four pre-run invariants, required known-answer controls, ledgered smoke edit and S0 report | Admissible S1/S2 evidence waits; setup/debug can continue |
| CP-D / D1 | Week 1 end or next available working checkpoint | Honest S0–S2 stage status, coverage/parity/calibration/profile, full cost projection; full F.5 readiness before S3 | Publish partial decision on time, date remaining work; don't claim stages passed |
| D2 mechanism decision | Week 2 middle | Oracle controls, grammar/edit screening, CR probabilities, negative-result diagnosis, conditional S6 decision | Repair proven bugs; valid negatives proceed; missing core assets trigger scope decision |
| CP-E freeze | Week 2 end | Complete machine-readable manifest, analysis tests, sealed data, affordable matrix, all required gates | No confirmation until ready; reserve paired core, drop optional work |
| D3 scope audit | Week 3 end | Completed pairs, budget, checkpoint integrity, uncertainty/coverage and limits | Drop error-key/regularization/HVP extensions first; preserve endpoint/paired design |
| CP-F report/reproduction | Week 4, before buffer expires | Integrated report, artifact index, reproducible commands, all deviations and cost totals | Explicit partial/feasibility result and prioritized remaining work |

Calendar is dependency-based, with five working days/week and no assumed weekend labor. The earlier Tuesday 8 September start is historical; on 9 September this audit found documentation, not evidence that scheduled implementation was complete. Rebase actual dates at CP-A instead of retroactively marking Tuesday work done. If a gate slips, publish new dates and its effect on freeze/confirmation; do not use conflicting automatic Tuesday/Wednesday D1 fallbacks. Engineering time and accelerator hours are separate estimates.

## 6. Concurrent-agent schedule and handoffs

The PDF expressly allows independent jobs once inputs are ready. Concurrent **coding** does not authorize concurrent state mutation or unbudgeted accelerator work. Suggested four-worker waves:

| Wave | Worker 1 | Worker 2 | Worker 3 | Worker 4 | Join condition |
| --- | --- | --- | --- | --- | --- |
| A: initial setup | INTEGRATOR: S0-01/02/03, schemas | BASE: wrapper/energy audit and mock-compatible adapter | MEMORY: packed bank/transaction design against mock | DATA/METRICS: development reservation, decoder and numerical controls | Shared contract review CP-B |
| B: first integration | INTEGRATOR: cloning/ledger/CLI, review | BASE: BP/ePC hooks and analytic credit | MEMORY: CAP-04…07 and PC controls | DATA: modular/grammar recovery; then baseline reference smoke | CP-C, no experiment before four invariants |
| C: S1/S2 | METRICS: report card | BASE: credit/solver diagnostics | MEMORY: radius/A calibration then fixtures screening prep | BASELINES/DATA: B1/B3/B4 parity, data/challenges | D1 and PC-1…10 readiness |
| D: S3/freeze | INTEGRATOR: run matrix, projection, freeze | MEMORY: constructed/small editing runs | DATA/METRICS: grammar and tracing | BASE/BASELINES: parity gaps or conditional S6 preparation | D2/CP-E |
| E: confirmation | INTEGRATOR: scheduler/coverage/ledger | BP run owner: S4 immutable jobs | BASE: S5, optional separately budgeted S6 | METRICS: analysis of completed jobs and S7 checkpoint probes | D3; all pairs protected |
| F: close | INTEGRATOR: reproducibility/artifacts | METRICS: paired report/uncertainty | MEMORY: fixed exploratory ablations | BASE/DATA: failure audit and independent reproduction | CP-F |

DATA, METRICS and BASELINES are substantial roles: rotating a worker does not make their remaining work disappear. With fewer workers, run these packages sequentially; with more, split them by the owned paths above. No date estimate assumes unlimited agents.

Rules for safe independent work:

1. One owner per file area and one integrator for shared contracts/manifests. Use separate branches/worktrees where practical. In a shared checkout, reserve paths explicitly; never reset another agent's work. Exchange small reviewable patches.
2. Each task handoff names ID, input commit/schema, modified paths, output/evidence paths, executed checks, unresolved defects and measured cost. An independent reviewer checks the relevant PDF contract before integration.
3. Merge wrapper+mock contract first, then memory+transport, then decoder+whole-item rollback, then real-data parity, then profile. These are dependency joins, not opportunities for independent speculation about the same interface.
4. Separate processes own separate learner instances and output directories. Never have agents update one cap concurrently. Parallelize distinct arm/realization/order jobs only from immutable manifests and clean initial snapshots.
5. An accelerator lease queue records job, device, stage, projected ceiling and stop boundary. On one GPU, serialize timed jobs to avoid contention corrupting throughput; CPU coding/analysis can proceed. Multiple GPUs may run independent jobs with device-specific timing/provenance.
6. S1 and S2 may run concurrently after S0, subject to gates and resource reservations. S6 can run alongside S4/S5 only after its own decision and reservation. S7 can consume a committed checkpoint while later stream checkpoints are being trained, using independent probes and separate state.
7. Confirmation workers cannot tune configurations from observed endpoints. Review frozen analysis before exposing results. A data-preparation worker may filter using the frozen BP selection rule, with an access log; it does not optimize arms on the sealed pool.
8. A failed control pauses the affected mechanism and its dependent claims. File invariant, ≤3 explanations and cheapest discriminating test; other preparation continues. Never silently move an algorithm to a different solver or metric to clear a run queue.

## 7. Budget, scope selection and measurement contract

| Stage | A100-equivalent ceiling | Priority |
| --- | ---: | --- |
| S0 | 8 | Required foundation |
| S1 | 12 | Required applicable report-card rows |
| S2 | 12 | Required calibration/parity/profile |
| S3 | 16 | Required development mechanism screen |
| S4 | 36 | Required BP confirmation |
| S5 | 24 | Matched-base comparison when assets/capabilities permit |
| S6 | 20 | Conditional, both arms and evaluation |
| S7 | 10 | Direct behavioral order effects; HVP optional |
| S8 | 16 | Core completion, selected ablations, integrated report |
| Total | **154** | No silent expansion |

For a measured shared workload define kappa=local throughput/A100 throughput; local-hour ceiling=stage A100-hours/kappa. Until the A100 reference and same workload exist, report local cost with provisional sensitivity bands, not certified A100-equivalent compliance. Preserve uncertainty across sequence length, batch shape, credit procedure and evaluation mix.

For each candidate scope, sum measured complete-item learning cost, immediate generation, retained checkpoint rescoring, endpoint/challenge evaluation, LM drift, retrieval and serialization, across all required datasets/arms/realizations/orders. Include grammar base/fixture training if a replacement is needed; its feasibility cannot be hidden in preparation. Count shared teacher-reference production once, record reuse, and retain per-arm query costs actually incurred. Charge compile/warmup separately from steady-state timing, and include total consumed costs in the allocation decision.

Proposed headroom convention is reserving 25% of the ceiling, rather than multiplying estimates by 1.25; document this interpretation before scope selection. Define exposure/time ceilings and checkpoints needed for longest-common-prefix rescoring before runs. Resource-limited partial items consume budget despite rollback. Full/partial forward calls, reverse/VJP, settling iterations, prefix microsteps, probes, rejected searches, memory search, wall/accelerator time and peak memory are explicit counters. B0 is not free to evaluate.

Drop optional key, S6 and HVP work before core pairs. C0's long editing extension has lower priority, but initial C0 scope is required. If even the smallest complete core is unaffordable, issue the PDF's feasibility result and a scope decision to the human lead; do not silently halve realizations/orders, omit CR/B4, or change the endpoint. Reassign unused S6 allocation only through a logged budget amendment.

## 8. Frozen analysis details

D.7 task matrix: with task-order index i and T tasks, ACC=mean(a_T,i); BWT=mean over i<T of (a_T,i−a_i,i); FWT=mean over i>1 of (a_(i−1),i−b_i); forgetting=mean over i<T of (max over u=i…T a_u,i−a_T,i). Save raw matrix and acquisition. Late acquisition is gain over pre-task performance, matched by task across orders; late/early ratios are secondary and undefined for zero denominator. The sibling's relative-perplexity functions are not these metrics.

D.8 editing: report immediate complete ES and paraphrase GS; endpoint/checkpoint RET-ES and RET-GS both unconditional and conditional survival among immediately acquired items. No acquired items makes conditional survival undefined. LS compares complete answers with same-base cap-off generation, plus first-token agreement, fixed-prefix KL and reference correctness where available. LM drift reports perplexity ratio **and** mean loss difference in nats. Retention on explicit corrections uses latest valid answers only. Keep edit length, frequency, novelty and near-neighbour strata.

Primary editing endpoint is endpoint RET-GS for C2−C1 and C2−CR, analyzed separately for the two editing streams unless an additional aggregation was preregistered. For each contrast require point improvement≥.02 and lower interval>0, immediate ES lower paired bound>−.02, and LS lower bound>−.01. Both routing contrasts are required for the positive primary claim. Report all constraints even after a failure. Favorable point estimates without resolved noninferiority are qualified; intervals spanning meaningful benefit and harm are inconclusive.

Compute paired differences for every realization/order, then average orders within each realization. Resample the three realization clusters, keeping their five orders together, for 10,000 bootstrap draws and conservative 97.5% two-sided intervals. Save bootstrap seed, full paired table and min/max over orders. With three realizations this is limited small-sample evidence. Subject resampling, if done, is separate; 15 runs are not 15 independent datasets or base checkpoints. Synthetic retention, shared/private damage and order effects support mechanism interpretation; they do not replace the primary endpoint.

Constructed delivery precision counts supplied-permitted choices; recall counts eligible items receiving at least one permitted delivery, so abstentions reduce recall. Multi-cause items retain required mechanism sets. Proposed deliveries, accepted writes and successful edits are different denominators. Learned restoration evidence is not pooled into oracle precision/recall.

## 9. Reconciliation of earlier plans and reviews

The [counter-review](week1/counter_review_week1plan1.md) provides useful CR-1…CR-12 corrections; this plan incorporates them through the gates, metadata, analysis, ledger, CR profiling, split inventory, report-card coverage, budget projection, early baseline work and relative calendar above. Two source-status cautions matter:

- `review_plan1.md` currently contains a substantive review, despite the counter-review describing a title-only file at its time of writing. Preserve that chronology; do not claim its current content was absent or rebutted then.
- Several current review claims conflict with the PDF and week plan: numeric thresholds, bounded candidates, accelerator budgets and rollback rules already exist. Do not adopt suggested generic `p<.05`, top-k endpoints, or new agent-token caps. Retain its useful request for a readable risk register and feasibility tracking without changing the scientific protocol.

Explicit corrections versus week1plan1:

1. The four pre-run invariants gate admissible experiments; there is no contradictory broad S1 exception. Additional control failures block only the measurements that use them.
2. PC-3/8 and all revision cases of PC-4 have owners and due gates; PC-1 and full PC-10 cannot vanish into an optional weekend.
3. Count successful complete-item uses once per slot, not per prefix/round. Nominal slots are upper bounds before all persistent overhead.
4. Exact-key fallback may reduce cap-induced paraphrase gains; it does not redefine RET-GS as exact-prompt retention and does not force absolute GS to zero.
5. CE≤.1 is a prefix stop/threshold outcome, distinct from complete free-generation ES. Preserve the PDF's threshold failure record without overriding generation scoring.
6. Restore learner state but never erase execution costs. A resource stop rolls back the entire unfinished edit, including accepted earlier prefixes.
7. CR is explicitly provisional/uniform for early profiling, development-estimated at S3, frozen at S4; count abstentions and realized writes.
8. Reserve S0 development examples early; deterministic test-pool preparation is distinct from tuning access; audit actual document/token counts and sample feasibility.
9. P1–P6 coverage is explicit by base/signal, including BP P4, applicable ePC P5 and credit profiling. Resolve ePC energy before ePC experiments.
10. No measured conversion from an assumed GPU; B0 evaluation costs; grammar and rescoring included in the full projection; headroom convention recorded.
11. Reference feasibility/parity begins with environment setup, while competitive calibration remains development-only. Failed B4 parity leaves a missing required comparator.
12. One dependency calendar, no implicit weekends, and an on-time partial D1 memo is not completed S0–S2.

## 10. Risk and decision register

| Risk / unresolved input | Evidence now | Owner / deadline | Action and contained consequence |
| --- | --- | --- | --- |
| Actual production weights/teacher pairing | Recipes and hash exist; weights absent | BASE / CP-A | Locate and verify; continue BP/harness; ePC claims unavailable until preflight. Do not spend 50M tokens recreating by default. |
| Supported environment and accelerator | Active Python lacks deps; driver inaccessible here | INTEGRATOR / CP-A | Identify execution host, install/test pinned environment there, measure cost; CPU controls proceed. |
| Six-layer grammar asset absent | Sibling tiny fixture differs; no learned grammar located | DATA / D1 | Recovery first; if replacement necessary, specify/training-budget/competence decision before S3. This affects required grammar evidence. |
| Baseline compatibility/parity | No GRACE or LoRA implementation locally | BASELINES / D1 | Start reference smoke early; minimal documented adaptation; required comparison incomplete if validation cannot be obtained. |
| Source/license provenance | No sibling root license; MORK absent license noted | INTEGRATOR / before distribution | Record rights/provenance for selected code and assets; avoid adding Rust dependency this month. |
| LM/POS/domain sample availability | New prescribed inventories not present | DATA / D1 | Count tokenized unique sources; log specification issue before substitute/repetition; no concealed shortfall. |
| Eight-step error usefulness | Old loss scales/horizons differ | BASE / S1 | Exact masked objective, measured r8/r64, finite-iteration label; bounded declared development solver decisions only. |
| Fused QKV LoRA accidentally updates K | Adaptation not implemented | BASELINES / PC-10 | Verify slice masks/trainable tensor list and reference behavior. |
| Radius search finds no positive candidate | Unknown until S2 | MEMORY / D1 | Exact-key pilot and firing/GS diagnostics; retain 1% criterion and primary endpoint. |
| C2 helpful probe fails as stored write | Discrete routing/allocation intentionally differ | MEMORY / S3 | Separate probe/candidate outcomes, transactional evaluation, drift/capacity diagnosis; valid failure is scientific. |
| Ambiguous identical key / corrections | Explicit PDF special case | MEMORY / PC-4 | Reject immutable conflict, versioned transactional replacement only on correction track; no impossible dual-target claim. |
| Scope exceeds 36h S4 | No throughput yet | INTEGRATOR / CP-E | Project full matrix with headroom, select fixed candidate scopes, drop optional first, feasibility result if minimum fails. |
| S6 detached regularizer | Existing inference explicitly detaches | BASE / S6-03 | Dedicated differentiable path and gradient-effect test before training either comparison. |
| Agents diverge on protocol/shared files | Several future contributors expected | INTEGRATOR / continuously | Contracts, path ownership, immutable manifests, small reviews, accelerator lease queue. |
| Confirmation bug or incomplete pair | Not yet run | INTEGRATOR / D3 | Retain old artifacts; version fix and rerun affected pairs within budget or mark incomplete. |
| Human scope/access decision needed | Asset locations, host and calendar unresolved | INTEGRATOR / relevant gate | Prepare concrete options, evidence and cost first; ask only for dependent missing access/scope decisions. No messages to external asset owners are implied by this plan. |

## 11. Required stage report and final handoff

Every S0–S8 report follows Appendix G:

1. Stage, code/config/checkpoint hashes, environment/hardware, realization/order coverage, elapsed cost versus ceiling.
2. Development/confirmation status and completed/partial/correctness-failure/resource-limited/scientifically-negative/inconclusive classification.
3. Expected and observed controls with evidence and pass/fail; separate geometry alerts from correctness.
4. Every planned arm and completed prefix, exclusions, ambiguity, weak tracing pairs, undefined/unsupported/unavailable measures.
5. Acquisition, retention, locality, drift, transfer/order, memory and costs with complete paired tables and uncertainty.
6. Mechanism evidence: oracle, random routing, signed probes, shared/private effects, drift, collisions and evictions.
7. Optional mathematics: coordinates/topology, HVP controls and limits relative to actual updates.
8. Every deviation, its timing relative to test access, evidence and whether affected paired arms were rerun.
9. Supported and unidentified claims, plausible negative explanations, and surprises without endpoint changes.
10. Reproduction commands, manifests, licenses/provenance and prioritized remaining work.

A proposed final command interface, to be implemented under S0-03, is:

```bash
pccap run --stage S4 --arm C2 --base BP --read h \
  --realization 0 --perm 0 --manifest manifests/frozen.json
```

This command does not exist yet. Handoff must include tested commands for environment setup, CPU controls, asset verification, stage runs, checkpoint resume and report generation. Final acceptance is reproducible controlled evidence with explicit limitations, including a useful negative or feasibility answer—not a requirement that C2 or ePC wins.
