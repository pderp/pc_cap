# Interim report 2 — REG-02, integration readiness, and the next independent work

Evidence snapshot: **2026-09-10 12:33:19 UTC / 08:33:19 America/New_York**. Reviewed working tree at commit **f92c510ec853f1a4668233a9a5ad2df75f651e35**; REG-02 logs were advancing during inspection. Author: Codex.

**Recommendation: let REG-02 continue under its existing protocol, use the remaining GPU window to repair and test the experiment's integration on CPU, and keep confirmation closed until those checks pass.** There is substantial independent work available. The largest immediate risks are in the paths connecting the components: confirmation access, run identity, order construction, cost accounting, and the post-regeneration handoff. Passing component tests has not yet established that a scheduled confirmatory job can run correctly from the CLI through final analysis.

This report creates no new experimental decision. The [PDF](../docs/pc_cap_month_plan_readable.pdf) remains the scientific contract, with explicit lead decisions in [decisions.md](../docs/decisions.md). Suggested repairs preserve the endpoints, contrasts, thresholds, and allocation rules. Any implementation changes to existing files still require the applicable permission and ownership coordination. This review changed no code, manifests, environments, reference repositories, running jobs, or shared boards.

## 1. What has changed since interim report 1

The project now has a useful tested core and considerably more integration code. The raw task manifest contains **87 tasks: 48 done, 1 in progress, 10 partial, and 28 pending**. Some pending rows render as “ready” after dependency evaluation. DATA-02a's completion is outside that board inventory. Counts are bookkeeping, not a percentage of the scientific programme completed. The filesystem inventory contained **107 source modules / 12,409 source lines and 51 test files**. Sources: [tasks.json](../manifests/tasks.json), [status renderer](../src/pccap/harness/status.py), [DATA-02a completion](../docs/tasks/DATA-02a-completed.md).

| Area | Current evidence | What it establishes |
| --- | --- | --- |
| Base and cap controls | GPT-2 stored-oracle agreement, cap-off identity, transactional memory, complete-answer decoding, cloning, metric and analysis controls | A substantial component-level foundation; retain these tests while repairing integration |
| REG-00/01 | Byte-exact prepared training shard, independent formula checks, micro-batch/resume controls, real-model float32 diagnosis and fix, 100-step pilot | A justified new JAX regeneration attempt; not continuity with the missing original checkpoint |
| REG-02 | Running through the prescribed homotopy; current rows finite, no logged holds or step gaps | Proceed under the existing stop rules; final preflight and substrate evidence remain pending |
| B0/B1/B3 | Codex implementations integrated into the orchestrator's arm registry and evaluator; development rate screen completed | Practical baseline runs are available; poor efficacy/locality is a development result requiring careful interpretation |
| DATA-02/02a | Six sealed realizations, metadata sidecars, verified loader, actual public API connected | The loader component is complete; the surrounding CLI still has separate blockers described below |
| S3 | Constructed controls, short editing rows, learned CR distribution, D2 memo | Descriptive mechanism evidence; learned grammar and the complete development matrix remain incomplete |
| S4/S5/S7/S8 | Draft freeze, schedule, runners, collectors, substrate arm definitions, order-analysis and reproduction drafts | Useful preparatory code; several “partial” labels are appropriate and should remain until end-to-end checks pass |

Evidence: [interim report 1](interim_report1.md), [REG-00](../docs/tasks/REG-00.md), [REG-01](../docs/tasks/REG-01.md), [baseline completion and integration](../docs/tasks/S2-04-completed.md), [S3 report](../results/S3/report.md), [S5-01](../docs/tasks/S5-01.md), [S7-03](../docs/tasks/S7-03.md), [S8-04](../docs/tasks/S8-04.md).

Two coordination changes matter immediately:

- **GRACE's dependency permission is resolved.** The latest addendum records lead approval, installation of Setuptools 78.1.0, and successful imports of pkg_resources and wandb. The older ongoing/task records still describe this as blocked. The final twenty-case parity manifest and five-case smoke log remain absent. Resume source controls and reference generation; do not ask for the same pin permission again. Sources: [approval addendum](../docs/tasks/S2-05a-environment-edit-request.md), [installation log](../results/grace_lane_d/setuptools_pin_install.txt), [reference task commands](../docs/tasks/S2-05a.md).
- **DATA-02a is complete.** The approved wrapper and PDF-reference correction are applied. Its most recent verification is 90 targeted pytest tests, five actual public-API smoke cases, and lint, all passing. Older “pending integration” text is superseded by the [completion addendum](../docs/tasks/DATA-02a-completed.md). These checks exercised the loader, not the complete S4 CLI.

## 2. REG-02: healthy logged progress, substantial work still ahead

At the snapshot, the metrics CSV had **4,464 completed optimizer steps of 9,766**, representing **22,855,680 training tokens**, at **T=8**. There were no duplicate or missing step indices, no rows with hold=True, and no nonfinite values in the checked loss, energy, gradient-norm, and step-time columns. Observed median step times were:

| Relaxation horizon | Observed median seconds/step |
| --- | ---: |
| T=1 | 0.710 |
| T=2 | 0.942 |
| T=4 | 1.382 |
| T=8 | 2.264 |

These agree closely with the pilot's timings. The final three horizons have not yet been exercised by this full run. Using the original remaining stage counts and the pilot's measured timings gives **10.88 compute hours remaining**, approximately:

| Remaining stage | Estimated hours |
| --- | ---: |
| T=8 remainder | 0.70 |
| T=16 | 1.55 |
| T=32 | 2.95 |
| T=64 | 5.68 |

Thus roughly 46% of optimizer steps does **not** mean roughly half the compute is finished. The CSV contains about 1.38 hours of measured step time so far; late relaxation horizons dominate. This estimate excludes extra holds, contention, checkpoints, evaluations, and process startup. It is not a promised finish time. Sources: [live metrics](../results/REG/epc-50m/metrics.csv), [pilot timing projection](../results/REG/pilot.json), [schedule](../src/pccap/distill/schedule.py), [recipe](../src/pccap/distill/recipe.py).

The latest complete milestone at step 4,297 / 22,000,640 tokens reported:

- Prompt KD divergence, temperature 2 with the recipe's scaling: **6.65e-6**.
- Additional tail divergence at temperature 1: **1.40e-5**.
- Small probe perplexity: teacher **93.3409**, student **93.2989**, a relative change of approximately **−0.045%**.

These support continued fidelity monitoring. They do not establish P1 on the independently specified H set, useful factual capability, P2–P6 properties, or superiority of error credit. The training tracking residual is an **energy ratio**; the P6 convergence residual is a **gradient-norm ratio**. They must not be interpreted interchangeably. Sources: [milestones](../results/REG/epc-50m/milestones.csv), [training loop](../src/pccap/distill/train.py), [declared energy and solver](../docs/epc_energy.md).

The summary JSON still said paused_chunk at step 4,000 while the CSV had advanced beyond it. That is a last-completed-chunk snapshot, not evidence that training stopped. The saved peak memory was about **7,816 MiB**, not a measurement of currently free GPU memory. The review environment could not query NVIDIA's driver through nvidia-smi; live conclusions here come from advancing logs and the lease record, not direct GPU telemetry.

**Preserve the numerical training implementation through completion.** In particular, changes to the shared PC graph, error solver, weight phase, or distillation code could affect later resumed chunks. Keep unrelated S4/analysis fixes outside those paths. The REG lease's exclusive=False flag does not remove its exclusive file lock; it controls additional process monitoring.

## 3. Findings to resolve before dependent execution

The identifiers below are review findings, not new SD entries or task-board mutations.

### R2-01 — Post-REG automation has already taken a stale completion marker

**Priority: repair before REG-02 finishes; CPU-only preparation.**

[chain_after_reg02.sh](../results/REG/chain_after_reg02.sh) waits for any occurrence of “REG-02 loop exited” in the accumulated training log. That log contains an earlier exit at **10:58:14 UTC**. The follow-on log subsequently records **11:28:17 UTC: status=paused_chunk; not completed; stopping chain**. A newly launched copy can also immediately match that old marker. The repository therefore does not establish that the advertised REG-03 → P1 → P2/P3/P5/P6 sequence is still armed for the current run. The [S5 preparation chain](../results/REG/chain_s5_prep.sh) waits for the downstream completion marker and can remain waiting indefinitely.

There is a second failure mode: these chains do not stop the whole sequence when an individual command fails. A command followed by “&& echo DONE” does not prevent the next line executing. The terminal CHAIN_AFTER_REG02_DONE/S5_PREP_DONE markers can be printed after failures.

Recommended sub-tasks:

1. Identify a current run/attempt by protocol hash and checkpoint provenance; wait for its terminal status, not a historical substring.
2. Distinguish normal chunk pauses, explicit stop, abort, and successful completion.
3. Require each prerequisite to succeed before launching the next job; write the final success marker only after all prerequisites pass.
4. Make relaunch/resume idempotent and preserve old failure logs.
5. Test stale markers, paused chunks, aborts, failed preflight, and successful completion using synthetic statuses and a fake command executor.
6. Have the orchestrator verify/re-arm the repaired chain; do not restart or alter the training process merely to repair its handoff.

This is supported by the actual [after_reg02.log](../results/REG/after_reg02.log) and the source scripts. Process visibility in this review was insufficient to certify every background shell's current state.

### R2-02 — The public CLI bypasses the loader's pre-access gate and rejects the scheduled manifest format

**Priority: confirmation blocker. Confirmed with an in-memory CPU reproducer.**

[runner.load_manifest](../src/pccap/harness/runner.py) reads and parses the supplied file before main checks whether the freeze exists. In confirm mode it validates that file as manifest_frozen. However, [the scheduler](../src/pccap/harness/schedule.py) passes a **per-realization DATA-02 manifest**, whose layout intentionally differs from the freeze document.

The synthetic check supplied no real files, returned a realization-shaped JSON object from a mocked read, and simulated an absent freeze. The CLI read the payload once, then returned exit code 2 with “missing frozen field: code_commit”, env_lock_sha, and other freeze-field errors. It never reached the protected stage loader. Passing the freeze itself as --manifest is also not the scheduled interface: the stage subsequently asks the data loader to load that freeze filename as a realization.

Required checkpoint: execute the real CLI validation path with a separate frozen configuration and realization reference. A missing, invalid, or unapproved freeze must cause **zero payload opens**. A valid synthetic freeze and matching realization must pass without needing a GPU. The stage should reuse the verified manifest and hash rather than independently reopen unbound paths.

The [DATA-02a helper](../src/pccap/data/confirmation_integrity.py) passed its component checks. The gap is in its integration into the existing entry point. A source-text firewall alone cannot establish the access boundary.

### R2-03 — Dataset omission produces 75 output-directory collisions

**Priority: confirmation blocker. Confirmed using the draft schedule and actual path function.**

The current preview has **150 scheduled jobs but only 75 unique paths** under runner.run_dir_for. Every scheduled path is shared by a zsRE and CounterFact job. For example, both C0 / realization 0 / permutation 0 map to:

    results/S4/C0/BP/h/0/0

The paths omit the dataset and freeze/run identity. [run_stream](../src/pccap/harness/runs.py) deletes existing item/decision logs at startup and writes metrics/checkpoints into that same location; learner checkpoint paths derive from it. Once the CLI issue is fixed, later jobs can erase or mix earlier results. The same identity problem applies to S5.

Required sub-tasks: include dataset and a stable experiment/freeze identifier in the result and resource paths; validate CLI realization/order against the manifest; reject incompatible existing outputs; define explicit resume behavior; test schedule-to-path uniqueness across both datasets, all arms, and all 3×5 cells. Keep readers/collectors consistent with the revised identity.

### R2-04 — Truncating after shuffling changes the examples across “orders”

**Priority: scientific-design blocker. Confirmed by code inspection and a four-item example.**

[S4](../src/pccap/harness/stage_s4.py) and [S5](../src/pccap/harness/stage_s5.py) take the first n entries of each full committed order. DATA-02 has 3,000 zsRE or 1,000 CounterFact items per realization; the draft selects 1,000 / 300. Consequently, different order prefixes generally contain different example subsets. Meanwhile, [expected_from_loader](../src/pccap/analysis/s4_06.py) declares the first n entries of the unshuffled items array to be the common inventory.

Synthetic example:

| Quantity | Value |
| --- | --- |
| Realization inventory | a, b, c, d |
| Selected n | 2 |
| Order 100 | d, c, b, a → execution uses d, c |
| Order 101 | a, b, c, d → execution uses a, b |
| Analysis inventory | a, b |

With the explicit inventory, paired analysis rejects unexpected items; without it, the union-of-observed inventory produces missing cells. Independently of the software error, this mixes example selection with order effects. PDF Appendix B and D.11 specify orders within a realization that share items.

Before freeze, define a deterministic selected subset per realization and derive every order as a permutation of that same subset. Filtering the existing full orders to a predeclared subset is one implementation option that need not rewrite the sealed payloads. Define how C0's 300-item comparison is paired to the other arms' corresponding 300-item checkpoint. Put the selection rule in the freeze and use the same helper for execution, expected inventories, and S7.

Checkpoint: three synthetic realizations × five orders, multiple affordable scopes, identical item sets within each realization, permutation differences preserved, and no unexpected/missing required-arm inventory.

### R2-05 — GPU exclusion, runtime limits, and restart behavior are not enforced by the scheduled S4/S5 path

**Priority: operational blocker before actual runs; fixes can be developed on CPU.**

Neither the shared CLI nor the S4/S5 stage runners acquire gpu_lease. The schedule emits ordinary CLI commands, so it does not supply an outer lease either. This contradicts the “one job (lease)” reproduction description and permits accidental contention with REG-02 or its follow-on jobs.

Both stages call run_stream without resource_stop_seconds, leaving its default None. Even when that option is supplied elsewhere, the current loop checks the limit before starting an item; it commits the update without a post-update limit check. The stronger documented mid-item rollback/resource-stop guarantee is not demonstrated by that path. Saved learner snapshots exist, but the public stage runner does not implement a matching resume entry path and rerun protection.

Required checkpoints:

- A run waits for the lease before constructing a GPU-backed model or calling determinism_report's backend discovery.
- Explicit frozen run/stage allowances are enforced and all consumed cost is retained.
- An interrupted/uncommitted item restores the complete learner state.
- A compatible resume continues from the exact item boundary; an incompatible or accidental rerun refuses existing outputs.
- A synthetic learner, fake ledger, and fake lease test these cases without using REG-02's GPU.

Sources: [runner](../src/pccap/harness/runner.py), [S4 runner](../src/pccap/harness/stage_s4.py), [S5 runner](../src/pccap/harness/stage_s5.py), [stream loop](../src/pccap/harness/runs.py), [lease implementation](../src/pccap/harness/lease.py).

### R2-06 — Resource views currently use incomplete per-item time and substitute running acquisition for retained performance

**Priority: blocker for efficiency claims; directly measurable from existing development logs.**

The resource-view collector sums items.jsonl cost.accel_seconds. Those records come from ItemOutcome.cost **before immediate evaluation**. For cap updates, that aggregate also omits timing recorded separately by adjoint/probe calls in the shared ledger.

Two existing runs illustrate the discrepancy:

| Run | Sum of item cost seconds | Ledger learning seconds | Ledger query seconds | Ledger total seconds |
| --- | ---: | ---: | ---: | ---: |
| C2 / zsRE, original throughput run | 5.359 | 9.416 | 13.475 | 22.891 |
| B1 / CounterFact | 6.107 | 6.107 | 16.996 | 23.104 |

Thus the same per-item field does not even have identical completeness across these two arm implementations. This affects the reported within-20% update-time ratios. It also makes “100 items within 30 seconds” tables easy to misread: those budgets exclude substantial query cost.

The current time-matched table reports **running mean immediate ES**, not retained performance of the learner at that budget. Retention is stored at checkpoints, but its assigned accelerator timestamp is again the incomplete item-cost sum. The exposure table intersects checkpoints across *all* discovered arms, so a shorter optional arm can suppress a valid longer checkpoint for the C2–C1/C2–CR pair.

Recommended repair: record learning/query/total ledger deltas at item and checkpoint boundaries, including evaluation setup and rescoring; reconcile them with the final ledger; build pair-specific exposure views and retained-performance-versus-budget views from actual saved states. Keep immediate ES as a separately named acquisition curve. Test a synthetic run with large query overhead, expensive C2 probes, and an optional arm stopping early.

Sources: [stream cost capture](../src/pccap/harness/runs.py), [cap cost assembly](../src/pccap/cap/learn.py), [resource views](../src/pccap/analysis/s4_05.py), [C2 cost](../results/S2/throughput/C2/zsre/cost.json), [B1 cost](../results/S2/throughput_baselines/B1/counterfact/cost.json). Existing numerical efficiency ratios should be treated as provisional until reconciled.

### R2-07 — The selected scope is a conditional projection, not a priced complete core

**Priority: before final scope approval.**

The saved projection selects **1,000 zsRE / 300 CounterFact / 10,000 grammar**, with **90,504.85 seconds = 25.14 local hours** against **27 hours after headroom** at κ=1. It explicitly sets grammar_included=False and assumes B4's cost from C1. Only **6,695.15 seconds = 1.86 hours** remain within that headroom-adjusted allowance.

Additional issues in [budget.project](../src/pccap/analysis/budget.py):

1. The grammar term is 4 arms × 15 runs × gr × grammar_learn_s. PDF E.1 and DATA-06 define gr as training sequences **per task**, across **eight tasks**. If grammar_learn_s is per sequence, the eight-task multiplier is absent. The unit must be explicit.
2. Under the current expression, the remaining allowance permits about 11.2 ms per grammar sequence at gr=10,000. Including eight tasks reduces that to about **1.4 ms per sequence before evaluation and joint-reference costs**. Neither number is a measurement.
3. Profile query time already includes rescoring, locality, and drift. The projection reuses that blended per-edit number as a marginal rescore cost. The source comment assumes one endpoint pass, while actual 100-item logs contain both ckpt100 and end passes. Separate fixed setup, immediate query, and per-checkpoint costs before extrapolating.
4. The profile defaults to 100 locality prompts and 1,024 drift positions; S4 uses 200 and 4,096, while the plan/SD-3 specify the whole 247,289-token validation drift set. A development subset is useful, but the confirmatory coverage and price must be explicit and compliant.
5. Challenge evaluation, grammar's per-task evaluation sets, and joint-training reference need explicit terms or a documented exclusion; a null grammar term cannot price them.
6. κ remains provisional. Re-running the existing formula in memory yields selected editing scopes of 1,000/1,000 at κ=0.5, 1,000/300 at κ=1, and 300/300 at κ=2; all still omit grammar.

Re-price the complete declared workload after B4/grammar measurements, correct the unit accounting, and use the existing scope/drop rules. Do not choose scope from favourable experimental outcomes.

Sources: [projection](../results/S2/projection.json), [profile defaults](../src/pccap/harness/stage_s2_throughput.py), [S4 evaluation setup](../src/pccap/harness/stage_s4.py), [SD-3](../docs/spec_defects.md), [DATA-06 and S2-07 specifications](../docs/updated_plan2.md).

The saved [stage ledger summary](../results/ledger/stages.json) is also stale: 0.918 hours. Recomputing its own current inputs without writing produced **1.279 hours**, still **zero S6/REG task seconds**, despite live REG-02 step time already exceeding an hour. REG-00/01 task records also report costs not present there. The sum is not a trustworthy full-project consumption total yet. Reconcile task charges, per-run charges, repeated attempts, and REG chunk deltas without double-counting; preserve DEC-014's explicit budget amendment.

### R2-08 — Freeze fidelity and failure gates need tests beyond “schema-valid”

**Priority: before freeze / asset promotion.**

Several safeguards exist as metadata but are not fully enforced:

- The freeze writer writes the final file before acting on schema errors and does not reject unresolved required inputs merely because pending is nonempty. Many required fields have presence-only schema checks. Some unavailable fields can be legitimate, but they need an explicit claim/scope decision.
- The defect-table parser assumes four columns; SD-13 onward has five. For SD-15, the generated resolution is actually the “Both readings” text, and status contains the resolution plus the real status. The freeze is not faithfully copying the resolution fields.
- The draft's decisions list stops at DEC-016 although DEC-017/018 determine the selected LoRA rate and CR policy.
- The generic schema CLI infers **manifest_dev** for frozen.draft.json. The reproduction command without an explicit --kind therefore checks the weaker schema.
- S4 records a field named frozen_sha256 from the CLI's supplied-manifest hash, which is the realization hash in the intended job interface. Record and verify the freeze and realization hashes separately.
- S5 confirmation still reads arm definitions, calibration, and checkpoint selection from mutable development/assets files. The frozen substrate fields are not the source of those choices. S4 also needs actual code/base/tokenizer/hash and availability checks, not only an unchanged-before/after base checksum.

Required checkpoint: a synthetic freeze must bind the actual configuration consumed by execution and analysis. Mutating a bound source, using a draft, providing an unavailable arm, changing a dataset/order identity, or leaving a required field unresolved must fail before data/model execution. Test both defect-table layouts. Publish a valid final freeze atomically only through the lead's authorized act.

Sources: [freeze builder](../src/pccap/harness/freeze.py), [schema inference](../src/pccap/harness/schema.py), [draft](../manifests/frozen.draft.json), [S4](../src/pccap/harness/stage_s4.py), [S5](../src/pccap/harness/stage_s5.py).

REG-03 has a related, separate issue: [preflight.py](../src/pccap/distill/preflight.py) computes finiteness, shape, identity, and energy-descent flags, but returns 0 and can mark a final checkpoint regenerated without requiring those flags to pass. Define an explicit validity result and refuse promotion on failure. Its identity threshold should be reconciled with SD-10's recorded criterion rather than silently relying on a generic 1e-3 absolute tolerance. Also, [P1](../src/pccap/analysis/s1_p1.py) filters nonfinite KL values before calculating the eligibility mean; the nonfinite count must itself prevent an eligible result.

### R2-09 — Grammar is an independent engineering lane, with shared-interface work still required

**Priority: begin CPU design/code now; train only when authorized and the GPU is available.**

The generator, model, and tracing modules are still placeholders. PA-2's existing deadline remains **2026-09-11 23:59 America/New_York**, absent a different lead decision. REG-02's separate authorization does not move that deadline. Generator/model code can proceed now.

Use the full PDF E.1 / detailed GRAM-01 specification, not only the shorthand “agreement/dependency grammar” in ongoing4:

- Eight observable contexts, two shared switches, one private switch per context.
- A switch intervention changes only its declared mechanism; no ambiguous unlabelled task changes.
- Vocabulary 64, length 64, one designated evaluated position and one learning item per sequence.
- Independent development/training/evaluation manifests; 2,000 evaluation sequences per task.
- Five balanced task orders, held-out combinations, and a joint-training reference with the same total examples.
- Tracing pairs and patch sites fixed before results; weak, multiple-site, no-site, and overshoot cases retained under D.10's rules.

A new Base implementation alone will not connect cleanly to today's cap: CapConfig defaults to d=768, and cap/credit code uses GPT-2's fixed block map 3/7/11. The proposed grammar is d=128 with blocks 1/3/5. make_learner does not pass model-specific dimensions/sites. The scheduler's grammar branch also emits BP jobs using a single grammar.json path, while S4 hardcodes BPBase, GPT2Tokenizer, editing-style records, and editing stream-length lookup.

Prepare model-specific dimension/site and stream interfaces together with the generator, and coordinate the small shared changes with the orchestrator. A CPU model control should exercise the actual cap at d=128 and sites 1/3/5, including forward_from, adjoint, write shape, and byte accounting. Training the model first would not resolve these interface gaps.

Sources: [GRAM-01/02 and DATA-06/07](../docs/updated_plan2.md), [cap configuration](../src/pccap/cap/cap.py), [credit site lookup](../src/pccap/cap/learn.py), [arm registry](../src/pccap/harness/arms.py), [scheduler](../src/pccap/harness/schedule.py).

### R2-10 — Scientific interpretation should be corrected before it hardens into the next plan

**Priority: CPU analysis/documentation; preserve the registered comparisons.**

The [D2 memo](../docs/D2_decision.md) says C0's higher zsRE RET-GS supports earlier-bank generalization. **C0 is the last-depth-only control**, in both PDF §7 and ARM_BANKS. Its 0.43 versus C2's 0.30 cannot support that explanation. In this 100-item pilot there are no reported evictions, so attributing the difference to capacity pressure is also premature. Inspect paired disagreements, rare early C2 routes, retrieval changes, and accepted candidates before assigning a mechanism.

The development comparison to use is the learned-distribution CR: **RET-GS 0.38**, versus C2 **0.30**, C1 **0.31**, and C0 **0.43** on zsRE. Several S3 tables still use uniform CR's **0.18**. These are distinct runs and policies; keep both, explicitly named, without mixing their metrics or costs. Sources: [CR reprofile](../results/S3/cr_reprofile.json), [current throughput](../results/S2/throughput.json), [older short-editing table](../results/S3/short_editing.md), [DEC-018](../docs/decisions.md).

Other interpretation limits:

- C2's 97.4% last-bank routing and the learned CR distribution make the zsRE C2–CR comparison a useful test of adaptive selection against a strong matched-frequency control. The current point estimates do not favour C2. Keep the planned contrast and accept a valid negative outcome.
- CounterFact's zero-radius retrieval and observed zero GS create a severe primary-endpoint floor in this setting. “Zero by construction” is too absolute for all future prompts: equality-tolerance matches and base-generated answers remain possible. The evidence is zero observed development GS under this gate. Report it as a limitation; do not switch the primary endpoint to RET-ES.
- GPT-2's near-empty zsRE baseline means high immediate ES is mostly acquisition, not proof of competent factual editing. Confirmatory claims must retain that qualification.
- B1/B3's low acquisition and poor locality/drift are measured development outcomes. Their component tests support the implementation but do not rule out every full-protocol defect. Keep DEC-017's completed screen; audit answer-length/terminator strata and complete generation without launching an unrestricted baseline search.
- P1's development “initially correct” implementation checks only the first answer token, despite its docstring's complete-answer wording. That is insufficient for the common-initially-incorrect subset and competence discussion; prepare the full greedy-answer check for the post-REG evaluation.
- The constructed fixture's high recovery and C2 precision do not establish unique causal localization. Its shared-path shortcuts and missing multi-cause coverage are useful limitations. Finish held-out transfer and learned-grammar tracing before making the full causal claim.
- Three stream realizations remain three independent clusters. Five orders and thousands of examples do not turn this into fifteen independent base-training replications.

Sources: [S3 fixture report](../results/S3/report.md), [S1 P1 implementation](../src/pccap/analysis/s1_p1.py), [baseline screen decision](../docs/decisions.md), [PDF D.10/D.11 and E.2](../docs/pc_cap_month_plan_readable.pdf).

## 4. Work that can proceed while REG-02 occupies the GPU

These are proposed work packages, not claims or permissions already added to the shared board. “CPU now” means use explicit CPU/hidden-CUDA settings and avoid changing REG's numerical dependency paths. Existing-file edits remain subject to the user's protocol.

| Priority / owner | Work package and specific sub-tasks | Checkpoint | Dependency / permission |
| --- | --- | --- | --- |
| P0 — orchestrator, independently reviewed | Repair post-REG waiting and failure propagation; test stale exit markers, pauses, aborts, failed preflight; enforce preflight promotion flags | A fake run advances exactly once only after valid terminal success | CPU now; existing chain/preflight edits; do not touch running training math |
| P0 — orchestrator; Codex can prepare new test files | Exercise the real confirmation CLI with synthetic freeze/data; enforce pre-access gate; separate freeze/realization schemas and hashes | Zero payload reads on denied access; a valid synthetic CLI job reaches its registered fake runner | CPU now; fixes in existing runner/stage code |
| P0 — orchestrator | Give jobs unique dataset/freeze identities; add refusal/resume policy; check all schedule keys and resource paths | 150 currently scheduled jobs produce 150 unique paths; incompatible reruns preserve outputs | CPU now; existing runner/collector interfaces |
| P0 — DATA + analysis owners | Define selected realization subset and filtered permutations; align C0 prefix, expected inventory, and S7 | Same subject/item set in all five orders; complete synthetic 3×5 paired table | CPU now; no real sealed-item access; changes agreed before freeze |
| P0 — harness + metrics owners | Capture ledger deltas, reconcile totals, record checkpoint cost; enforce resource bounds/rollback; repair retention-vs-budget views | Known synthetic costs reconcile exactly; early-stopped optional arm does not remove required-pair evidence | CPU now; existing shared loop/analysis edits |
| P1 — Codex, Lane D | Recheck input/selection hashes; run all six reference controls in the already-fixed GRACE env; run five-case smoke; require ≥1 full greedy target match; produce twenty isolated/sequential cases and verify artifact hashes | Honest smoke verdict and completed parity manifest, or a specific failure report | CPU now, roughly the lane's remaining 2 h; no repeat dependency permission; new output paths only |
| P1 — Codex, Lane G | Specify switches/contexts/target positions; build generator/checker; deterministic split and order manifests; design d=128/site interface; implement model CPU controls | Reproducible grammar sample plus intervention/balance controls and actual cap/model interface test | Code now; new files/proposed patches; existing placeholder/shared-cap edits need permission |
| P1 — metrics owner | Audit all pilot costs and grammar units; reconcile saved ledger; derive κ scenarios and complete budget components | A scope table with explicit measured/assumed/missing costs and no zero-priced required workload | CPU now using existing logs; profiling missing arms later needs GPU |
| P1 — analysis owner | Audit learned-CR vs uniform-CR reports, C0 explanation, answer-length strata, route/retention disagreements | One source-identified development comparison table; remaining hypotheses labelled as hypotheses | CPU now; new report first; existing report/renderer corrections coordinated |
| P2 — Codex, ENV-05 | Design a fresh-environment setup script; audit lock's editable source entry; use a new assets environment and dry-run resolution; document assets/HF_HOME and tested commands | A reproducible environment procedure tied to the intended code revision | CPU/network, not GPU; never install into project venv; existing environment-doc edit needs permission |
| P2 — orchestrator | Mirror DATA-02a completion and GRACE approval; reconcile task statuses and dependency exceptions; refresh reports from correct variants | Current board and rendered summaries agree with completion/approval records | CPU now; shared board/report edits by owner |
| P2 — S7 owner | Specify reversal pair inventory, complete-state restore, reference-Q hashes, cost and missingness schema; CPU analytic controls | GPU evaluation can start later with a predetermined interface and pair set | CPU preparation now; actual reversal/JS results need learner checkpoints and GPU |

Suggested division for the next remaining REG window:

1. **Orchestrator:** R2-01 and R2-08 promotion checks first, then the small synthetic CLI → stream → result collection → paired-analysis path covering R2-02 through R2-06. Keep REG training running as its separate leased process.
2. **Codex:** finish the newly unblocked GRACE reference lane, then prepare grammar generator/model/interface work and, if time permits, ENV-05. Use the runner's existing --threads 2 setting for the CPU oracle; avoid saturating the host with simultaneous large CPU model jobs.
3. **Joint checkpoint:** review the synthetic end-to-end evidence, source/ownership changes, and the complete cost table before asking the lead to freeze.
4. **Next GPU opportunities:** REG-03 and P1 first, then the required ePC report-card/calibration/error-credit controls. Schedule grammar training only after PA-2 or explicit earlier authorization, and only in a coordinated free-device window.

Code review, metadata calculations, new tests, and most grammar design do not require a REG pause. Real GPT-2 GPU checks, B4 JAX parity/profiling, grammar training, ePC calibration, and substrate execution do.

## 5. Recommended changes in direction

**Make a complete synthetic execution the next acceptance gate.** The most valuable immediate investment is a small study that uses the real scheduler and CLI, two synthetic datasets, all required arm identities, three realizations and five orders, intentional failure/resume cases, exact budgets, and the real collectors. It should use a fake/small CPU learner and never open sealed study items. Today's analysis wiring tests build a single-dataset result tree directly from development results; they do not exercise the CLI, its access gate, schedule paths, or full-pool truncation. Component-green and pipeline-ready must remain separate recorded states.

**Treat the regenerated model as a candidate substrate, with separate claim gates.** Finish the fixed REG protocol and validity preflight. Then evaluate fidelity, output competence, geometry, localization, write locality, and finite-iteration credit on that checkpoint. Low KD divergence alone does not justify S5 superiority. Preserve the PDF distinction between SE-A versus SE-E within one substrate and a matched-fidelity comparison against BP.

**Keep the grammar central to the causal question.** The factual-development evidence currently gives weak discrimination between adaptive and mostly-last routing, and CounterFact has a generalization floor. A properly controlled learned grammar offers the planned mechanism test. Invest in the generator's interventions and joint reference, rather than choosing latent rules that manufacture a preferred bank. Keep constructed-oracle and learned-tracing evidence separate.

**Do not freeze an incomplete core merely because the GPU is busy.** REG-03 is not a prerequisite for the BP-only routing comparisons, but the integration blockers are. B4's CPU reference lane is now available, and PA-2 only delays training, not grammar code. If the lead elects a reduced BP-only scope with B4/grammar unavailable, label it as an explicit reduced programme with missing planned evidence. Any later added component needs a prospective versioned protocol; it should not silently change an already-open confirmatory analysis.

**Keep S6 and optional breadth deferred.** D2's recommendation to defer S6 remains sensible. R-h0/R-g/R-e keys, difficulty weighting, HVP diagnostics, extra capacities, and extra post-result seeds should not outrank correctness, required references, grammar competence, and complete accounting. Existing CPU log analyses can refine the deficit statement without tuning the registered core to obtain a favourable result.

**Improve the handoff record format, not just the number of reports.** Give each finding/task a current status, exact evidence path/hash, owner, dependency, next executable checkpoint, and whether an existing-file edit is pending. Preserve old records as history but have one renderer resolve the latest completion/approval state. Reports currently disagree about GRACE's permission, DATA-02a, S3 completion, CR policy, baseline availability, and even the old PA-1 bound. Fix the generating logic as well as the prose.

## 6. Reproduction/documentation issues worth closing on CPU

[REPRODUCE.md](../docs/REPRODUCE.md) is a useful draft, but its “every command ... has been run” header exceeds the evidence: S4 has not run, REG preflight is pending, and the listed S4 command currently fails the CLI contract above. Several resource examples use assets/... relative to pc_cap even though resources live in the sibling assets directory. The frozen-draft validation example needs --kind manifest_frozen. Split commands into verified, pending, and illustrative, with their exact working directory.

ENV-05 should address the private editable source line in [requirements.lock](../requirements.lock):

    -e git+ssh://git@github.com/pderp/pc_cap.git@e381c9e8a82d15de37277ef9315e156c6d160adf#egg=pccap

A fresh-machine script cannot assume that SSH access exists or that this older revision is the code the user intends to reproduce. Resolve source installation/provenance explicitly while preserving dependency pins; do not silently rewrite the lock or replace the active JAX environment. A scratch environment and dry-run dependency check under assets is sufficient for the first reviewable setup artifact.

## 7. Review method and limits

I inspected the current plan/delta, PDF contract passages, decisions, defects, lead queue, task inventory and completion records; S0–S3 reports and development summaries; REG recipe, training/resume code, CSVs, milestone and chain logs; public runners, freeze/schedule/analysis wiring, arm/cap/credit interfaces, schema, ledger and budget code; GRACE preparation/approval records; and environment/reproduction documentation. This is an integration and scientific-readiness review, not a proof of every source line or every historical result.

Read-only CPU probes:

- Actual scheduler plus actual run_dir_for: 150 scheduled jobs / 75 paths.
- Actual runner.main with mocked synthetic file access: one payload read before denial, then wrong-schema rejection.
- Existing budget.project at κ=0.5/1/2; stages_summary in memory without publishing.
- Existing development item-cost sums versus their ledgers.
- Actual freeze defect parser and schema-kind inference.
- Live CSV continuity, finite-value checks, timing and remaining-stage calculations.

No full model, training, reference generation, broad test suite, or confirmatory analysis was run. No actual confirmation payload was opened or hashed; only the existing aggregate/index/metadata contract was used. No corrective edit was made. The 90-test and five-public-API-smoke results quoted above are the prior recorded DATA-02a verification, not a claim that the complete S4 pipeline passed.

Two short reproductions of the newly confirmed blockers are below. They import code with CUDA hidden, create no files, and use no sealed data.

    PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES='' \
      /home/derp/cap/venv/bin/python -B - <<'PY'
    import json
    from collections import Counter
    from pathlib import Path
    from types import SimpleNamespace
    from pccap.harness.runner import run_dir_for
    from pccap.harness.schedule import jobs_from_manifest

    draft = json.loads(Path("manifests/frozen.draft.json").read_text())
    jobs = [j for j in jobs_from_manifest(draft) if j["status"] == "scheduled"]
    paths = Counter(str(run_dir_for(SimpleNamespace(**j))) for j in jobs)
    print(len(jobs), len(paths), sum(n > 1 for n in paths.values()))
    # Snapshot result: 150 75 75
    PY

    PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES='' \
      /home/derp/cap/venv/bin/python -B - <<'PY'
    import contextlib, io, json
    from pathlib import Path
    from types import SimpleNamespace
    from unittest.mock import patch
    from pccap.harness import runner

    args = SimpleNamespace(manifest="/synthetic-only/realization.json", mode="confirm")
    reads = []
    def read_bytes(path):
        reads.append(str(path))
        return json.dumps({"name": "synthetic", "mode": "confirm",
                           "dataset": "synthetic", "items": []}).encode()
    def exists(path):
        return str(path) == args.manifest  # the real freeze is never accessed
    with patch.object(Path, "read_bytes", read_bytes), \
         patch.object(Path, "exists", exists), \
         contextlib.redirect_stderr(io.StringIO()) as errors:
        code = runner.main(args)
    print("exit:", code, "payload reads:", len(reads))
    print(errors.getvalue().splitlines()[:3])
    # Snapshot: exit 2, one read, then missing frozen-field errors.
    PY

The report's numerical snapshots will age while REG continues. The implementation findings are tied to the reviewed commit and should be rechecked after the owning agent applies fixes. The next useful deliverable is the resulting end-to-end evidence and an updated readiness decision, rather than treating this review itself as a completed repair.
