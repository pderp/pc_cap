# After Binghamton: selective continual learning with predictive-coding caps

Capex, for charlie derr and collaborators · 19 October 2026

**Recommendation:** start with two connected experiments: explain and improve the cap's selection of corrections, and build a small predictive-coding reader whose learning really can be implemented through local operations. Evaluate both under continual change. Use those results to decide whether distributed learning, neural-symbolic composition, or a more elaborate dynamical model is the next useful investment.

This is a proposal for the next research programme, not a launch record. The conference experiments remain a completed historical study. Budgets, dates and advancement criteria below are proposed defaults, not previously approved commitments.

## 1. Relationship to the presentation

I read the entire supplied [slidedeck.txt](../../slidedeck.txt), including the material through and beyond the first fourteen slides. Its SHA-256 is `da52868c1e3dc03ac494aa355d0f56999f1a84c31372d60abee293826378e7d3`.

**Slide-number assumption:** this plain-text export has no slide numbers or page boundaries. I interpret the requested slides 11–12 as the sections headed **“Final Thoughts, Conclusions and/or Takeaways”** and **“Possible future research directions.”** I asked for confirmation while drafting. The older local PDF versions have different ordering; their slide numbers do not override the supplied text. The plan is anchored to the section titles and the following explicit ideas in the supplied presentation:

| Presentation idea | Concrete next investigation | Where in this plan |
|---|---|---|
| Improve selective retrieval and application of corrections | Separate missed retrieval, wrong retrieval, and ineffective writes; compare selection at matched useful coverage | Experiment A |
| More tests of continual learning | Interleaved domains, changed facts, bounded memory, and actual online reader updates | Experiment B |
| Distributed PC training | Verify local dependencies, then test message passing and stale states before making hardware claims | Experiments C and F |
| Understand BP/PC internals, dynamics and representations; possibly use singular learning theory | Paired representations, gradient/settling diagnostics, interventions, then a limited local-learning-coefficient pilot | Experiment D |
| NESS / neural-symbolic sandwich experiments | A small explicit composition task, grounded in the available H3 work and controlled against symbolic-only and BP alternatives | Experiment E |
| Other PC architectures, standard PC, cortical columns | A shallow activation-PC reader first; a matched modular architecture only after its components work | Experiments C and F |
| Information-theoretic explanations of extreme-case behaviour | Record predictive entropy, both KL directions and per-prefix losses; distinguish these from loss-distribution shape | Shared measurement protocol |

Active inference and coupled entropy remain connected longer-term questions. They receive a specific next experiment in §9, rather than being used as names for mechanisms we have not implemented.

## 2. What the completed work actually motivates

Use the **October 10 cap-value supplement**, which incorporates the completed October 9 MQuAKE evaluations, as the starting empirical record. It is newer than several planning and support documents. In particular, an older statement that no MQuAKE BP/PC reader comparison exists is now out of date.

At 300 edits, the measured paraphrase results are:

| Dataset | Frozen GPT-2 mean target NLL | BP-CAP mean target NLL | PC-CAP mean target NLL | BP / PC paraphrase exact match |
|---|---:|---:|---:|---:|
| zsRE | 6.10 | 0.13 | 0.20 | 98.0% / 96.6% |
| CounterFact | 7.37 | 1.31 | 2.43 | 81.5% / 66.9% |
| MQuAKE | 6.05 | 1.59 | 2.09 | 67.4% / 59.6% |

NLL is nats per target token under teacher forcing; exact match uses free generation. These are different outcomes. The cap values summarize three paired training seeds on the same exposed realization/order. They are not three independent subject populations. Source: [cap-value report, §§1 and 10](../results/extremes_analysis/ext-20261009/reports/cap_value_report.md).

Five findings should shape the next experiments:

1. **The cap provides substantial adaptation.** Keeping a no-cap reference central is useful, but the cap receives new facts that the frozen reference does not. Include an equal-information retrieval or in-context baseline when claiming an advantage of the cap architecture itself. A zero frozen edit score caused by eligibility screening is not a general statement about GPT-2's factual accuracy.
2. **Many remaining extreme paraphrase losses involve abstention.** On CounterFact, abstentions account for approximately 90–100% of each reader's own worst 5% of paraphrases. That makes selection a strong first hypothesis. It does not establish that simply lowering the null threshold will help without increasing false corrections. Source: cap-value report §9.2.
3. **The specific ePC reader training was expensive and did not win.** Completed training took roughly 96–102 times BP's process time. This motivates diagnosing the estimator and testing a smaller, more local design; it does not establish that every PC algorithm is inferior. The current [ePC solver](../src/pccap/pc/epc_inference.py) differentiates the reconstructed graph to optimize error states. Frozen weights do not mean that backward computation through the base is absent.
4. **Composition is a separate missing capability.** Both cap types scored zero on complete three-question MQuAKE cases. Better single-fact retrieval alone may not fix this. New composition experiments need an explicit mechanism and component tests, rather than another large unchanged MQuAKE run.
5. **Extremes are real, but their statistical interpretation depends on the observable.** Absolute answer NLL, additional ordinary-text harm, and KL between token predictions are different distributions. The presentation's lack of established Pareto-type answer-loss tails does not contradict the finite-range harm/KL differences in [measurements.md](../../assets/support-information/measurements.md). Report the variable and population every time.

The available [H3 distillation report](gen-trans/H3_distillation_results.md) is another useful constraint. Joint fitting of a small student and cap helped in its Tiny Shakespeare sandbox; the writable-PC extension did not. Its “tail segment” is a later segment of text, not an extreme-value tail. It describes a Torch implementation and a partly trainable student, so it is reference evidence, not an executable JAX component or a direct replication of our frozen-GPT-2 experiment.

## 3. A small shared experimental foundation

Keep frozen GPT-2 small as the factual-editing substrate initially. Preserve the existing checkpoints and reports; put new work in a separate namespace. All execution is **local and JAX-based**. FabricPC and `llm-by-neural-predictive-coding` remain read-only references. Any borrowed Torch implementation must be ported and checked before execution here; there is no Colab lane.

### 3.1 Reuse the evidence and loaders already available

| Existing component | Reuse |
|---|---|
| [extremes data dictionary](../results/extremes_analysis/ext-20261009/reports/data_dictionary.md) and [cap-value analysis](../aw/extremes/cap_value.py) | Matched frozen/BP/PC probe losses, generation outcomes, firing, selected-own-record fields, write norms, and fixed difficult subsets |
| [model reconstruction](../aw/extremes/models.py), [probe construction](../aw/extremes/probes.py), [scorer](../aw/extremes/score.py) | Load the right reader and memory; score the same serialized inputs; extend these through new wrappers |
| [paired reader trainer](../aw/pc_reader_train.py) and [evaluation driver](../aw/trained_reader_eval.py) | Initialization/data pairing, checkpoint averaging, acquisition and endpoint assays |
| [entropy measurements](../aw/entropy_tail_measurements.py) and [tail analysis](../aw/tail_class.py) | Definitions, saved-vector analysis, explicit fit failures and threshold sensitivity |
| [interface experiments](../aw/interface.py) and [AW-L results](additional_work/AW-L_report.md) | Controlled read/write masks; evidence against assuming upper-only writes are safer |
| [memory monitor](../scripts/process_memory_monitor.py) and existing GPU lease | Resource monitoring and single-owner GPU execution |

These are reuse candidates, not a promise that a legacy command can be launched unchanged: old runners contain conference deadlines and bound source checks. Create a new experiment entry point with explicit new limits. Do not disable historical checks globally or replace their old receipts.

### 3.2 Population and comparison rules

- Use exposed streams for diagnosis and development, labelled as such. Reserve a later evaluation population before selecting a winner. Recheck current exposure and subject/family overlaps; old statements about remaining reserves are not a current inventory. Never count new permutations as new independent subjects.
- Keep zsRE as the easier retrieval/continual-learning check, CounterFact as the first difficult paraphrase/selectivity test, and MQuAKE for targeted single-hop/composition diagnosis. Do not expand MQuAKE merely to fill a balanced-looking table.
- For a final comparison, aim for three independently constructed populations with paired seeds, if feasible. If the real-data reserve cannot support that, use independent synthetic worlds for mechanism tests and report a smaller real-data external-validity check honestly. Do not silently manufacture independent evidence by duplicating exposed rows.
- Start each paired run from the same base, facts, order, resources and initial memory. Hold writer/payloads fixed for selection-only experiments where the architecture permits it. If a new reader changes code construction or acquisition, reacquire in both arms and call the contrast a whole-pipeline comparison.
- Separate **equal updates/data** from **equal measured compute**. In the compute comparison, give the cheaper arm additional learning updates within the common allowance, not meaningless repeated calculations. Include tuning and failed runs in the cost account.

### 3.3 Instrument the quantities we lacked

For each training prefix and evaluation probe, record dataset, item/family, role, step/checkpoint, reference identity, target-token count, target NLL, predictive entropy H(base)/H(cap), forward/reverse token KL, selected record/null probability, gate outcome and write norms. For PC diagnostics add energy, residual norm, settling count and update norm.

Compute scalar entropy/KL during the forward passes already needed; full vocabulary logits need not be permanently saved. Log per-prefix values before averaging. Keep settled-state CE separate from ordinary feedforward CE, and distinguish training's soft routing from deployment's hard gate. Store only a declared small diagnostic sample of large activations; monitor overhead and host memory.

At every checkpoint report:

- Own-prompt success and retained paraphrase success; free-generation exact match and teacher-forced NLL separately.
- Loss on the **fixed frozen-model hardest 5%**, and each model's **own worst 5%**; fractional expected-shortfall weighting for newly defined analyses, while retaining the historical report's exact definitions when reproducing it.
- Ordinary-text signed harm, harmful frequency, conditional severity, ES99+, maximum, and KL tails. Keep zeros and benefits in the population. Use full validation for finalists; a fixed smaller development subset is adequate for screening.
- Selection coverage, precision among accepted corrections, and success conditional on acceptance. Compare harm at matched useful coverage, not merely matched firing count.
- Memory bytes, actual update/query time, settling operations and total run cost. Include symbolic tables and replay buffers in memory comparisons.

Use subject/item grouping for fact probes and text/document blocks for token assays. Show each population and seed; an item bootstrap conditional on one fitted reader does not quantify uncertainty over new training runs. Tail-family fitting is secondary and reports threshold sensitivity and unsupported fits. Do not choose an entropy coupling from a fitted loss-tail shape.

## 4. Experiment A — find the selection failure before changing the architecture

**Question:** how much of the remaining error is caused by deciding whether and which memory to use, rather than by the correction itself?

**A1. Build a failure table from saved results.** For every original/paraphrase/near-miss/locality probe, distinguish: correct record accepted and successful; correct record accepted but unsuccessful; wrong record accepted; null with a relevant stored record; appropriate null. Preserve “unknown” when a saved field is insufficient. Summarize separately by dataset, relation/template family, target frequency, prompt overlap and baseline difficulty.

**A2. Separate retrieval from payload quality.** On a fixed development subset, replay normal selection and diagnostic forced selection of the correct record. Use the existing payload and writer unchanged. The forced condition is an **oracle diagnostic**, not a deployable method: it may use item identity to identify the record, but may not feed the target answer into prediction. If forcing the right record does not rescue an error, inspect acquisition, answer alignment and generation before blaming the gate.

**A3. Draw the operating trade-off.** Sweep the existing gate on development data; show retained-paraphrase performance against near-miss errors and ordinary-text tail harm. Add the existing one-nat probability mixture as a named control. Calibrate on development data, then freeze the setting before independent evaluation. The old conference populations can illustrate the trade-off but cannot become fresh confirmation after tuning.

**A4. Test one low-cost change.** Choose between a calibrated record-versus-null score, a small applicability head trained on hard negatives, or a revised retrieval feature only after A1–A3. Use the same negative examples, memory and tuning allowance for BP and any PC version. Avoid a simultaneous rewrite of reader, writer, loss and memory policy.

**Deliverables:** a failure atlas with actual examples; normal-versus-oracle rescue rates; one accuracy–harm frontier; at most one candidate to carry forward. An equal-information context-retrieval baseline should be included for a small matched subset, accounting for prompt/context cost.

**Checkpoint A:** advance a selection change if it improves the development trade-off on both zsRE and CounterFact without relying on less useful intervention. If most failures survive oracle selection, redirect the next implementation effort toward payload/generation instead. A failed hypothesis is a useful result.

## 5. Experiment B — test continual learning rather than just accumulating records

The earlier append-and-query streams measure retention and interference as memory grows. They do not fully test an online learner that must change its own parameters, handle stale facts, and operate under a bounded memory budget.

### B1. Construct two stream tests

**B1a — fixed-reader memory interference.** Keep reader parameters fixed. Use an A→B→A schedule of relation/domain blocks, an interleaved control, and a revision event that changes a subset of A facts. Repeat with a fixed memory cap and a declared eviction rule. Returning to A uses held-out probes; it does not silently reteach A before measuring retention.

**B1b — online reader adaptation.** Use the same stream, but update the reader after small blocks of arriving labelled examples. Compare no replay with a fixed-size replay buffer. Only already arrived support examples enter training/replay. Held-out paraphrases, future labels and assessment outcomes never become update targets. Test before learning from each arriving example, then test again afterward.

Use a reproducible synthetic relation stream first, then a 300-edit exposed real-data development stream. Synthetic worlds can isolate true label change, changed wording, and new relation families; keep these interventions distinct. Test 128- and 256-record limits in the pilot, counting metadata, symbolic tables and replay bytes, rather than assuming append-only storage remains affordable indefinitely.

### B2. Minimal controls and outcomes

Begin with fixed-reader/no-adaptation, BP-online/no-replay and BP-online/fixed-replay. Add the matched local-PC reader from C when ready. Keep arrival order, memory cap, eviction and replay allowance paired. An unlimited-memory run is a labelled upper-resource reference, not the matched comparator.

Measure performance on each earlier block after each later block, adaptation speed, old/new-answer preference after revisions, stale-answer recurrence, transfer to new paraphrases, and the shared tail/compute endpoints. Report a forgetting matrix: for an unchanged task, earlier performance minus current performance; for a deliberately revised fact, success means retaining the latest answer, not preserving the obsolete one.

**Checkpoint B:** identify whether deterioration comes from eviction, changed parameter geometry, stale payloads, or selection. Promote only a mechanism whose benefit survives the equal-memory/replay comparison. A frozen transformer cannot forget through changed base weights, but the adaptive system can still lose useful behaviour.

## 6. Experiment C — a small, genuinely local PC reader

**Question:** can PC offer useful learning dynamics or locality in the part of the system where our evidence identifies a bottleneck, without repeatedly differentiating through the entire frozen transformer?

### C1. Reproduce and locate the current cost

Use saved BP/ePC checkpoints first. Profile a few development updates only if a missing diagnostic requires them. Split time into base feature extraction, error settling, preservation evaluation, reader/controller updates and compilation. Record state/gradient magnitudes and compare directions for the same declared objective. A low settled CE is not a low feedforward CE.

The historical algorithm is an error-state formulation, not evidence that we already implemented independently learning cortical modules. The current [ePC paper](https://arxiv.org/abs/2505.20137) also distinguishes the state-based and error-based formulations; its benefits elsewhere do not establish efficiency in this testbed.

### C2. Implement a controlled activation-PC prototype

Use cached frozen observations and a small two- or three-layer reader that scores candidate memory records and null. Fix the initial feature interface, candidate inventory, payloads and writer. The first target is applicability/retrieval, not simultaneous learning of all transformer corrections.

Train **the same small architecture** with ordinary BP and activation-state PC, pairing initialization, samples, output loss, parameter count and tuning allowance. Keep the old 3.35M-parameter readers as historical references; they are not the matched architecture control. Add an error-state implementation of the small model only if it fits the profile budget.

A starting state energy can be written as

\[
E(z;\theta,x,t)=\tfrac12\sum_l\|z_l-f_l(z_{l-1};\theta_l)\|^2_{\Pi_l}
                 +\beta\,\mathrm{CE}(t,\mathrm{softmax}(Wz_L)).
\]

Here x is the frozen observation, t is the training-only record/null label, and the precisions, nudging strength and settling schedule are declared parts of the algorithm. Hold parameters fixed while settling states, then use fixed-state local parameter partials. Start with fixed identity precisions; adaptive precision and learned feedback are later interventions. The output parameter W also needs its explicitly specified local update.

This is an experimental design choice, not a claim that arbitrary finite settling reproduces BP. Local-PC constructions and their assumptions are described by [Whittington and Bogacz](https://doi.org/10.1162/NECO_a_00949) and [Millidge and colleagues](https://arxiv.org/abs/2006.04182). Verify the conditions relevant to the implementation instead of assuming equivalence.

### C3. Tests before model-scale claims

1. On a tiny linear/nonlinear network, check energy values and each local state/parameter partial against finite differences or an independent reference.
2. Check descent for the declared step-size range, exact restart, finite states and the no-settling forward path. Check gradient direction and magnitude versus the appropriate reference as settling/nudging change; do not impose an unjustified exact-equality condition on every finite PC update.
3. Verify local dependencies in code: an update may use adjacent states/errors and local Jacobian-vector products. A backward pass through the entire base or unrolled global settling trajectory would defeat the intended locality claim. Local autodiff primitives are permitted and must be disclosed.
4. At ordinary query time, supply no correct record label or answer. Use a feedforward applicability prediction initially. If query-time settling is added, define a separate target-free objective using only the observed prompt and available memory evidence; compare it with zero settling and equal-cost repeated evaluation.
5. Start with k = 0/1/4/8 as a development diagnostic, not an unbounded hyperparameter search. Compare equal updates first, then equal elapsed/operation budget. Test an adaptive stopping rule only after the fixed schedules are understood.

**Checkpoint C:** a local implementation, informative dynamics and a measured cost curve are worthwhile even before accuracy wins. Full GPT-2 evaluations require a competitive retrieval/false-activation trade-off on development data and a feasible profile. Do not rerun three approximately 24-hour ePC trainings merely to establish the same baseline again.

## 7. Experiment D — explain the internal differences

### D1. Begin with paired, interpretable measurements

Use the same labelled diagnostic prompts across BP/PC seeds: easy successful paraphrases, hard successful paraphrases, missed activations, wrong activations and unchanged locality prompts. Retain a randomly sampled background group and its sampling weights; a collection selected only for failures does not estimate population frequencies.

Compare reader embeddings, record/null margins, per-site write directions/norms, and prediction changes. Centered kernel alignment is a useful first representation-similarity tool, but is descriptive rather than a proof of equivalent computation. Pair it with held-out probes for relation/applicability information and with functional tests. Reference: [Kornblith et al.](https://proceedings.mlr.press/v97/kornblith19a.html).

Measure PC settling energy and residuals, response to small perturbations, local contraction/expansion estimates on a small state subset, and similarity between PC and BP update directions. State the coordinate normalization: raw Euclidean distances or differential entropies can change under a simple rescaling of hidden units.

### D2. Use interventions to test explanations

Compare a gate recalibration, forced correct-record selection, and a compatible reader/head substitution with the payload/writer fixed. If swapping representations requires rebuilding keys or aligning coordinates, verify that compatibility first and report the extra intervention. Measure whether a proposed mechanism predicts which held-out cases are rescued. Correlation between an internal statistic and failure is a hypothesis, not the mechanism itself.

For information theory, use H(base), H(cap), both token KL directions and calibrated record/null distributions on exactly matched prefixes. Prediction entropy measures uncertainty; it is not an estimate of epistemic uncertainty by itself. Mutual-information estimates on high-dimensional deterministic activations are estimator-dependent; begin with well-defined finite variables and held-out predictive tests rather than a large collection of opaque MI numbers.

### D3. Make singular learning theory a bounded pilot

The [local learning coefficient (LLC)](https://proceedings.mlr.press/v258/lau25a.html) offers a way to investigate local loss-landscape complexity. It is not interchangeable with parameter count, Hessian rank, Shannon entropy or a loss-tail exponent.

Start with the small reader from C and **one common smooth empirical loss** evaluated on the same fixed data. A soft record/null likelihood is a tractable first object. Do not compare BP feedforward CE with ePC settled CE, or claim the hard-gated deployed system's global learning coefficient from this submodel.

Port the chosen localized sampling estimator to JAX; check it on a model with an analytically tractable coefficient. Run multiple chains and inspect step size, localization strength, inverse temperature, autocorrelation and effective sample size. State which parameter block moves and which stays frozen. Compare checkpoints matched for task loss as well as matched for training step.

**Checkpoint D:** keep LLC only if it is stable enough to replicate and adds explanatory or predictive value beyond loss, margins and simple geometry. Otherwise publish the instability and stop that branch. Even a stable LLC difference would not establish a cause of better generalization or a thermodynamic phase transition.

## 8. Experiments E and F — composition and distribution, after the small controls work

### E. A minimal neural-symbolic / NESS experiment

**First distinguish the available ideas.** The local [generalized-transformer/CD report](gen-trans/generalized_transformers_cd_pc.pdf), [H3 architecture report](gen-trans/H3_architecture_and_results-1.pdf), and [H3 distillation results](gen-trans/H3_distillation_results.md) give concrete reader and inference designs. They do not specify every detail of the newer NESS system mentioned in correspondence. A faithful NESS replication needs an architecture description, executable interface and reference cases from its authors. That need not block a clearly labelled local prototype.

**E1 — establish a JAX reference on the small problem.** Prefer read-only-base H3 with fixed/generated readers and a BP control. Translate data structures, causal prefix scoring, count smoothing, energy and update equations; test against supplied reference outputs. Do not execute the Torch notebook or call a new toy design an exact H3 replication. Locate the companion code/checkpoints mentioned in the report; if absent, document the missing resources and implement a separately named prototype.

**E2 — add one explicit compositional operation.** Use synthetic two-hop facts with a bounded symbolic join: neural retrieval proposes grounded records, an explicit relation-composition operation forms candidate consequences, and a small neural module scores/reconciles them. Hold out entity combinations and graph structures. Include distractors, conflicting revisions and cases where a required link is missing. All deployable arms receive the same taught facts; no gold answer or dependency path is supplied only to the neural-symbolic arm.

**E3 — use component controls.** Compare single-fact retrieval, a symbolic-only executor with the same facts, fixed versus learned routing, and BP versus PC on the same neural combiner. A gold-support/path oracle is a separately labelled ceiling. Show support-retrieval recall, composition success conditional on available support, and end-to-end answer success, so a tokenizer/entity mismatch is not mistaken for a reasoning failure.

**E4 — transfer narrowly to MQuAKE.** First audit which cases actually contain every required dependency in the installed memory. Test matched two-hop cases before longer chains. If successful, test revisions of a dependency and propagation to derived answers. Keep actual question accuracy and complete-case success separate. A successful symbolic executor is evidence for the composite system, not proof that GPT-2 acquired internal multi-hop reasoning.

Do not start with joint transformer distillation or a writable H3 interface: these would change the frozen-base question, and the supplied writable-PC results are adverse. A later jointly trained student is a separately labelled architectural study. “Cortical columns” should likewise become a specified modular design with local state, routing and messages, not an explanatory metaphor.

**Checkpoint E:** advance only if composition beats the single-fact control on held-out synthetic combinations and the neural component improves on the symbolic-only/fixed-routing control, or clearly improves their cost/robustness. A symbolic-only win is an informative simpler solution. Give NESS/CD credit only to mechanisms actually implemented and ablated.

### F. Distributed learning as a measured systems question

The primary question here is **model-parallel local learning**, distinct from federated learning across private datasets or merely sharing fact records between agents.

1. Partition the validated small reader into two or three modules. Define the exchanged state/error tensors, parameter ownership, timing and synchronization points. Start with synchronous message passing and verify agreement with the serial implementation within declared numerical tolerance.
2. On this local machine, use CPU-worker processes or a single-device simulation to test bounded staleness, delayed messages and recovery. Measure iterations, communication bytes, synchronization overhead, memory and task/tail outcomes. A single-GPU simulation demonstrates semantics and costs, not a multi-GPU speedup.
3. Compare with the same BP model and a reasonable BP partitioning/batching baseline. Keep data, total parameter budget and useful work fixed. Distinguish more parallel operations from less elapsed time.
4. If a “column” design is tested, keep total capacity matched to a monolithic control; distinguish random/fixed/learned routing. Change architecture separately from changing the learning rule.
5. Only after access to actual multi-device hardware is established, measure end-to-end speed, communication and convergence on that hardware. Hardware acquisition or remote execution is not part of this plan.

**Checkpoint F:** retain the distributed branch if locality is real and the measured communication–convergence trade-off supports a plausible systems advantage. Stop expansion if extra settling or synchronization consumes the apparent parallel benefit. PC's locality is a hypothesis about implementation opportunities, not a speedup guarantee.

## 9. A concrete route back to active inference and coupled objectives

After A/B provide a credible estimate of intervention risk, construct a small decision problem with actions **leave the base unchanged, apply a proposed correction, or request a costly verification**. Verification must return an explicitly modeled observation and consume a budget; the correct answer is not freely available to the other actions.

Represent latent states such as “record applicable,” “record stale,” and “no applicable record.” Fit or specify observation likelihoods on development data. Define preferences over correct/incorrect answers and audit cost, a short policy horizon, and belief updates. Compare fixed gating, a cost-sensitive decision rule without information gain, random/fixed-rate verification, and the proposed active-inference policy at the same audit budget.

A risk/information-gain expression becomes an active-inference experiment only after its relationship to the chosen generative model and expected-free-energy formulation is specified. Record realized calibration, audit choices, benefit per audit, severe-error rates and adaptation after a change. Use [Da Costa et al.'s discrete-state synthesis](https://arxiv.org/abs/2001.07203) as a reference. Begin with a finite simulated world where beliefs and policy values can be independently checked.

For a coupled objective, continue the [post-conference collaboration proposal](post_conference/coupled_collaboration_proposal.md) and its [mathematical checks](additional_work/coupled_objective_note.md). Specify the random variable, reference distribution, support, normalization, gradients and ordinary limit with the collaborators. Compare one agreed ordinary objective with one coupled counterpart under the same optimizer/architecture first; do not simultaneously replace the learning rule. Neither a fitted heavy-loss tail nor a bounded-surprisal loss automatically supplies that functional. This branch may proceed independently once the mathematical definition is available; it does not hold up A–D.

## 10. Sequence, resources, and division of work

### First tranche: approximately two working weeks

These dates are a suggested sequence starting October 19, not a new external deadline.

| Window | Work | Concrete reviewable output |
|---|---|---|
| Days 1–2 | A1 saved-result failure classification; inventory new/exposed populations; define shared per-prefix log; C1 inspect/probe current estimator | One matched failure table, baseline snapshot, and measured cost breakdown |
| Days 3–5 | A2/A3 oracle and gate frontier; C2/C3 small JAX BP/PC reader; D1 representation diagnostics; B1 synthetic stream generator | Oracle-rescue result, algorithm tests, one small matched learning curve, deterministic streams |
| Days 6–8 | A4 one selection change; B1a/B1b fixed versus online reader and replay; C small paired seeds | Adaptation/forgetting matrices and matched accuracy–harm–cost curves |
| Days 9–10 | D2 interventions; joint interpretation; select one continuation | Short report stating what failed, what improved, and the next single experiment |

**Proposed initial resource ceiling: 32 local accelerator-backed process-hours**, including profiles, evaluation, failures and retries. CPU-only analysis is reported separately and must not cause memory pressure on the GPU owner's process. This is a planning cap, not a measured estimate or booked resource.

| Allocation | Proposed ceiling | Why |
|---|---:|---|
| Baseline reconstruction, missing instrumentation, small profiles | 4 h | Discover actual costs before a queue is expanded |
| A: limited oracle/selection replay and candidate | 6 h | Directly tests the main observed bottleneck |
| B: continual-learning pilots | 8 h | Fixed-memory and online-learning contrasts |
| C/D: small local-PC comparison and targeted dynamics | 8 h | Keeps PC central without another three-day historical rerun |
| Reserve | 6 h | Failed runs, finalist full-text assays, unexpected reconstruction cost |
| **Total** | **32 h** | Stop or reduce scope if profiles do not fit |

Historical 300-edit evaluation envelopes were approximately half an hour, with the full ordinary-text readout a large component. They are context only: new logging, online adaptation and new architectures require fresh profiles. Report both serial reservation/wall time and per-process costs; overlapping processes do not create extra physical GPU hours.

Do not launch the full product of every dataset, order, threshold, memory size, architecture and training rule. Use one development seed for debugging, then paired seeds for the narrowed comparison. Give both learning rules the same tuning allowance. Scientific negatives remain in the report; execution failures retain costs and missing outcomes.

### Following four weeks, conditional on the first results

- **Weeks 3–4:** complete the best-supported A/B/C comparison and an independently held-out evaluation where feasible. E can establish a tiny JAX composition baseline in parallel. D3 has a short feasibility slot, not an open-ended mandate.
- **Weeks 5–6:** choose **one** larger continuation: a replicated continual learner, NESS/composition transfer, actual distributed execution if suitable hardware exists, or the explicit verification-policy experiment. Publish the mechanism and negative controls before scaling the model.
- If A reveals little gate-remediable error, prioritize writer or composition diagnosis. If C's locality/cost claims fail, preserve the result and use BP for the next architecture test. If E is already solved equally well symbolically, do not add PC complexity merely to put it in the story.

### Parallel work that does not collide

Suggested ownership below is for coordination, not an assignment already sent to anyone.

| Lane | Suggested contributor | Can start alongside | Shared boundary |
|---|---|---|---|
| Failure analysis, metrics, representation/SLT feasibility | Capex | Small-reader implementation and stream design | Read existing artifacts; own analysis modules |
| Local-PC implementation, harness integration, profiling and dispatch | Capstan | Saved-result analysis and CPU symbolic prototype | One owner for shared runtime files and GPU queue |
| NESS specification, symbolic microtasks, H3 reference cases and conceptual review | Derp Peoples / interested human collaborators | A–D development | Provide explicit interfaces and fixtures; no shared-file edits without coordination |
| Scientific priorities, interpretation and collaborator discussion | charlie with colleagues | All lanes | Decide which evidence justifies the next tranche |

CPU analyses can run concurrently after checking memory use. GPU training and model replay share a lease and run serially unless a measured safe schedule justifies otherwise. Training diagnostics should reuse a scored population/cache rather than launch competing large model processes.

## 11. Completion criteria and a light working protocol

For the first tranche, “done” means:

1. We can account for most measured remaining failures with explicit categories and a quantified oracle-selection ceiling.
2. We have a controlled test of online adaptation/forgetting under a memory budget, including a simple replay baseline.
3. We have a small BP/local-PC comparison with verified update semantics, target-free evaluation, and actual costs—even if PC loses.
4. We have at least one tested explanation of the BP/PC behavioural difference, or an explicit statement that the proposed diagnostics did not explain it.
5. We choose the next experiment from those results, preserving the option of a simpler solution.

For candidate advancement, a proposed practical screen is either **at least two percentage points more paraphrase retention without higher tail harm**, or **at least 20% lower ES99+ with no more than one percentage point lost retention**, on development comparisons for both zsRE and CounterFact. Check uncertainty, near-miss changes and costs as well; these are proposed effect-size screens, not p-value thresholds, safety guarantees, or retroactive replacements for the conference criteria. A locality/systems mechanism may justify its own next experiment without meeting this behavioural screen, but must say what advantage is being tested.

Keep the administration small: **one experiment config, one reusable runner, one results table/figure bundle, one concise report**. Record code/data/model identities, selection decisions and compute in those artifacts. Avoid a new chain of signatures or a separate document for each routine engineering step. Add tests for the failure modes that could invalidate the conclusion: target leakage, state restoration, wrong loss/gradient signs, unpaired examples, missing null mass and misleading aggregation.

Proposed new paths, **not files that already exist**: `aw/post_conference/` for new experiment code, `tests/post_conference/` for algorithm checks, `results/post_conference/<study>/` and `logs/post_conference/<study>/` for evidence, and `assets/runs/post_conference/<study>/` for caches/weights. This plan is the only new artifact created for the present request.

The desired scientific outcome is not necessarily “PC beats BP.” It is to identify when a cap should intervene, how it can keep learning without destructive interference, and whether local predictive-coding dynamics or explicit composition add a capability, robustness benefit, or systems advantage that a simpler matched alternative does not already provide.
