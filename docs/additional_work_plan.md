# Additional experiments before October 9

Prepared September 20, 2026, for Charlie Derr and Claude. Includes Charlie's suggestion to restrict the cap to upper transformer layers. **Status: proposed supplemental work; no experimental runs launched by this document.** The experimental completion deadline is October 9, not the October 15 presentation. October 10–14 remains available for analysis of locked results, slides and rehearsal.

**Recommendation:** use any genuine spare capacity first to test a smaller, upper-layer cap interface, then to test bounded corrections that might reduce the concentrated harm already measured. These are manageable extensions of our working JAX system. If substantially more time remains, reproduce generated readers on a small new text corpus. Treat joint base–cap distillation as a conditional alternative, and postpone writable PC feedback, a large new transformer and learned structural-search guides.

The aim is one or two complete, interpretable supplemental results. Completing the registered experiment, including its comparators and reporting, takes priority over every item below. All numerical ceilings, supplemental selection rules and schedules proposed here are planning choices, not changes to the registered protocol.

## 1. What the supplied documents contribute

The six supplied files were inventoried with SHA-256 hashes in [source_inventory.json](../logs/additional_work_planning_20260920/source_inventory.json). PDF text and the notebook's checksum-verified embedded Python sources are retained in the same planning-log directory. The embedded code was decoded for inspection, not executed. The evidence below is reported by the supplied authors unless explicitly identified as a local pc_cap result; we have not independently reproduced their experiments.

| Source | Relevant idea or result | Consequence for this plan |
|---|---|---|
| [General report](gen-trans/generalized_transformers_cd_pc.pdf), especially §§3–7, 9–10 | Separate choosing evidence, transporting it, constructing features, settling and re-encoding. Preserve behavior on declared future uses. Explicit memory accounts for most of the H2 improvement. | Test narrow interfaces and identify which component causes an improvement. A useful cap need not replace the transformer. |
| [14-slide deck](<gen-trans/Generalized Transformers and CD Caps a PC Perspective.pdf>) and [presenter notes](gen-trans/gt_presenter_notes.pdf) | Distinguish temporary inference, parameter learning and structural change; distinguish stored information from access to it. | Keep reading, writing, routing, PC learning and structural search as separate experimental questions. |
| [H3 architecture/results](gen-trans/H3_architecture_and_results-1.pdf) | Generated count readers, including one parent–child composition, improve a small cap; nonlinear gates and PC training are not uniformly superior to simpler controls. | A small generated-reader replication is a credible stretch experiment. Include fixed-reader, random-addition, BP and separately trained no-settling controls. |
| [H3 distillation report](gen-trans/H3_distillation_results.md), September 19 | Jointly fitting a compressed student and a read-only cap improves combined prediction; writable PC variants perform worse in this experiment. | If the necessary implementation becomes available, investigate read-only joint fitting with a full-width control. Do not spend the deadline repairing the writable branch. |
| [Supplied Colab notebook](gen-trans/CDPC_enwik8_Colab_7h.ipynb) | An executable **PyTorch H2** experiment with 13 readers and pruning, budgeting and restart machinery. It has no saved execution outputs. | It is a specification/reference, not a JAX drop-in or evidence that our H3 experiment takes seven hours. |

Important quantitative distinctions:

- H2's reported frozen-base loss is 2.896241 bits per byte (bpb), versus 2.428546 for a global reader mixture and 2.335741 for compression-first CD–PC. Much of the gain precedes PC and structural search. Against the update-matched fixed-five PC control, the CD improvement is 0.010217 bpb, not the full base-to-cap difference. H2 CD–BP slightly outperforms CD–PC.
- H3's main five-seed generated-reader PC result is 2.316095 bpb versus 2.328272 for fixed readers with a nonlinear PC cap. The following segment also improves. However, these seeds share a base, corpus and reader construction; they are not five independently trained language models or five fresh corpora. The nonlinear-versus-linear comparison changes direction between segments.
- The later H3 distillation result is more informative than the earlier report's statement that joint base–cap training was still future work. Read-only joint PC gives 2.289393 bpb on the first test segment, versus 2.297331 for staged student fitting then cap fitting; joint BP gives 2.289320. This supports testing joint preparation, not a PC learning advantage.
- Compressing the final feed-forward width from 256 to 96 reduces the tiny base from 120,576 to 99,936 distinct parameters: **17.12% of the whole base**, not 62.5%. Reader tables, vocabulary, cap and retained teacher storage still count. The reported 711-second continuation stage excludes important prior work; it is not an end-to-end runtime prediction.
- The forgetting experiment reports that approximately 10% replay reduces old-domain deterioration while retaining most new-domain improvement. It also demonstrates that freezing memory does not prevent the learned gate from losing useful access to it. This is directly relevant to our reader/null-decision problem.

The H3 report references a separate implementation/evidence archive and `H3_enwik8_Colab_6p5h.ipynb`. Neither is in the supplied six-file directory, and a filename search under the local `assets/` and `errata/` directories found no H3/enwik8 bundle. They might be available elsewhere, but their availability is an entry condition, not an assumed shortcut. The supplied notebook implements H2, not generated H3 readers or H3 distillation.

## 2. Why these additions fit the present project

The [block-1 partial report](R1_stage4_report_block1_partial.md) supplies the most relevant local evidence. All 45 cells pass integrity/admission checks, but every learned-v5 cell exceeds the 0.001-nat ordinary-text mean-KL benchmark. Dataset means are approximately 0.00238 for zsRE, 0.00577 for CounterFact and 0.00712 for MQuAKE. Their largest positive target-loss increases are about 9.26, 15.38 and 13.14 nats. Only 69, 119 and 182 of 245,237 scored positions, respectively, carry half the KL.

Those measurements motivate a question the October satellite can understand: **can we preserve useful new knowledge while restricting how much the correction disturbs unrelated predictions?** They do not prove a power law, and they do not establish that a particular layer caused the harm. There is only one realization in that report; later results must be incorporated before making a final account of the primary study.

The GT connection is concrete. Restricting the cap's read/write ports tests an affordable behavioral interface. Bounding the output correction tests the report's explicit preservation construction. Generated readers test whether useful new evidence, selected by measured contribution, transfers beyond repeatedly used Shakespeare. Joint distillation tests whether preparing an upper part of a base together with its cap helps. These are four separate questions, not four ingredients that must all be added to one model.

Keep the [September 18 scientific review](scientific_program_review_2026-09-18.md) and [heavy-tail presentation proposal](heavy_tail_suggested_slight_pivot.md) as interpretive constraints: editing success, generalization, preservation, extreme losses and resource use must be shown together. A system that merely stops applying edits is not a successful adaptation method.

## 3. Scope, resource rules and entry conditions

1. **Finish and protect R1.** The frozen matrix contains 330 cells, including its planned comparators and historical extension. Claude owns dispatch and the current DEC-072 drain/resume. No supplemental GPU work competes with that queue. No additions or changes under `scripts/` or `src/pccap/` while its live content lock remains active. Documentation, source inspection and modest analysis of completed summaries can proceed now; an idle interval between primary cells is not release of the lock.
2. **Use the actual release date.** The primary budget is 750 shared process-hours. DEC-072 changes concurrency allowances, not that cap or October 9. The old approximately 431-process-hour forecast and early throughput are not guaranteed spare time. At release, reconcile completed cells, retries, unresolved endpoints, remaining primary obligations and available GPU time.
3. **Keep supplemental work separate.** Give each experiment its own manifest, namespaces and report, e.g. `AW-L`, `AW-B`, `AW-G`, `AW-D`. Do not add these arms to the registered matrix, relabel them as confirmation, or replace an unfavorable primary result with a better supplemental one. Charlie and Claude should choose the supplemental scope and resource allowance before implementation/launch; no elaborate second signing system is proposed.
4. **Use JAX in the existing venv.** `import pccap` precedes JAX imports. CPU is appropriate for small mathematical checks and reader construction; actual accelerator runs must verify CUDA availability and stop rather than silently run a GPU-sized job on CPU. FabricPC and `llm-by-neural-predictive-coding` remain read-only. Backpropagation implemented in JAX is a valid control and does not mean using PyTorch.
5. **Keep artifacts in their assigned locations.** Implementation, tests, manifests, reports, logs and small numerical result vectors go in `pc_cap`. Corpora, model weights, checkpoints, reader tables and large feature caches go under `/home/derp/cap/assets/pc_cap/additional_work/`. A decoded reference source remains code and belongs in the repo. Do not install a second framework or modify the frozen environment to execute the Colab notebook.
6. **Start with one supplemental GPU worker.** Take the existing lease and use the established monitors/retention. Record process elapsed hours and GPU reservation hours separately; a second worker does not halve the scientific budget. Set bounded batches/cache sizes from a measured pilot. Review both host RAM and VRAM before increasing them. JAX documents substantial default GPU preallocation, so use the project's existing configuration and verify the observed footprint rather than starting an unconstrained second process. [JAX GPU-memory documentation](https://docs.jax.dev/en/latest/201/gpu-memory.html)
7. **No unauthorized population reuse.** Use registered development resources for exploration. Any new supplemental holdout must be constructed without reusing training/selection/primary-confirmation identities, with actual availability and overlap checked before claiming freshness. If a fresh population is unavailable, say “post hoc development analysis” and complete a smaller honest study. Already published confirmation results cannot become an unseen tuning set.

The block-1 report is a stable planning snapshot. Operational progress can change while this document is written; re-check `docs/ongoing.md` and the lead's queue at every transition to implementation or GPU execution.

## 4. AW-L — Does an upper-layer cap interface suffice?

**Priority 1, incorporating Charlie's suggestion.** The defensible hypothesis is that later representations may offer a better usefulness/cost tradeoff for this cap. “Lower layers are mostly noise” is stronger and is not established. An activation can be useful to the base yet unnecessary or poorly exploited by the cap. Our experiment changes the cap's access; all lower transformer blocks still run.

There is also reason to retain a middle-layer comparison. ROME's causal tracing found important factual-retrieval computations in middle-layer MLPs, followed by later transport toward the prediction. That is evidence against treating layer usefulness as universally increasing with depth; it does not determine the best ports for our different, frozen-base cap. [ROME project and paper](https://rome.baulab.info/)

### 4.1 What we already have

The actual JAX mapping in [gpt2_jax.py](../src/pccap/bases/gpt2_jax.py) is:

| Bank identifier | Zero-based block index | Human-readable location |
|---|---:|---|
| 1 | 3 | After block 4 |
| 2 | 7 | After block 8 |
| 3 | 11 | After block 12, before the final layer normalization/output head |

The R1 reader combines the last-position and prompt-span observations from all three banks. The registered adapter uses the default `single_site=False`, allowing writes at all three. These are three taps, not observations from every layer. The observation module's introductory “entering” wording should not determine experimental placement: the BP/JAX implementation returns the post-block, pre-write residuals. Verify that convention with a fixture before a new port experiment.

[RevisionCap](../src/pccap/revision_v1/learner.py) already has a `single_site=True` prediction path that zeros banks 1/2 and resumes at bank 3. **It is not a fully trained final-layer-only treatment:** [the delta-acquisition routine](../src/pccap/revision_v1/adapt.py) still optimizes all bank deltas. Merely flipping the flag would test deleting learned writes at deployment. It would not fairly compare architectures trained for different write sites.

### 4.2 Separate three questions

| Question | Intervention | What it can establish |
|---|---|---|
| Which features does the selected reader currently rely on? | Frozen-reader tap removal/re-encoding on development examples | Dependence of this trained artifact; an abrupt change can itself cause failure. |
| Which read interface can be learned effectively? | Train the same reader recipe using all taps versus an upper subset | A practical interface comparison, conditional on training and parameter counts. |
| Where must corrections be applied? | Constrain acquisition **and** deployment to the declared write sites | A properly adapted write-location comparison, separate from retrieval. |

If “only upper layers” instead means running predictive-coding activity inference only in upper transformer blocks, that is a further experiment. The current main condition is feed-forward; changing ePC's free-state set would introduce a different learner. Do not quietly bundle that into AW-L.

### 4.3 Smallest useful trained experiment

Use two read interfaces and two write interfaces, yielding a 2×2 design:

| Arm | Reader taps | Acquisition/deployment writes | Main comparison |
|---|---|---|---|
| L-AA | 1, 2, 3 | 1, 2, 3 | Freshly trained all-site control |
| L-UA | 2, 3 | 1, 2, 3 | Does excluding the earliest read tap help or suffice? |
| L-AU | 1, 2, 3 | 3 only | Does final-block-only writing suffice with the same reader? |
| L-UU | 2, 3 | 3 only | Does the smaller overall interface work? |

Proposed scope: **three paired reader-training seeds, two datasets (zsRE and CounterFact), one deterministic edit order per stream, 300 sequential edits per dataset/seed**. This is six trained readers, twelve dataset/reader streams, and 24 arm×dataset×seed evaluations after the write factor. Reader training is held identical between the two write variants; stored corrections are acquired afresh under each write constraint. If the chosen training code itself depends on write location, either hold that dependency fixed and state the resulting estimand or train the complete four-arm factorial; do not pretend reused weights are independently trained treatments.

The selected v5 artifact can be reported as an additional descriptive reference; it is not the freshly trained L-AA control. The new reader recipe should fix training exposure, minibatches, optimizer, seeds, lexical features, null rule, training pools and checkpoint policy before fitting. No repeat of the 42-candidate model-selection search.

Use the same normalized aggregate write allowance and five-step acquisition budget for both write sets. Mask inactive sites **before gradient normalization, updates and projection**, and keep them zero throughout. Do not multiply the final-bank budget by three simply because two sites were removed. Log the achieved support loss, accepted/failed edits, per-bank norms, aggregate norm, step counts and memory cost; equal nominal bounds do not imply equal effects on predictions.

Start with the practical two-tap comparison. If time remains, add final-only reads `{3}` and middle-only reads `{2}` using the same fitting recipe. These are optional controls, not another twelve-layer search. Dropping a tap also removes trainable projection parameters; report that explicitly. Without an additional capacity-controlled design, conclude that a smaller interface performed better/worse, not that the discarded layer contained noise.

### 4.4 Tasks and checkpoints

| Task | Specific work | Completion checkpoint |
|---|---|---|
| L0: identity audit | Inspect the frozen constructor and saved reader metadata; record tap indices, pre/post-normalization convention, write sites, acquisition rule and active `single_site` value. Verify all-site reconstruction against a saved development checkpoint. | Exact baseline identity and prediction agreement; no sealed data needed. |
| L1: cheap screen | On cached development observations, report per-tap norm/variance and retrieval/null discrimination for all, upper, final and middle features. Fit identical small probes if needed, splitting by subject/template family. Include the existing lexical-only feature as a diagnostic control. | Paired retrieval/false-fire tables; no claim that probe quality equals editing quality or that raw norm measures semantic information. |
| L2: frozen diagnostics | Mask selected reader branches, re-encode **both** support keys and queries, rebuild memory identities, and evaluate the selected artifact. Separately delete early writes without re-adaptation. Keep these two diagnostics labeled as interventions on a previously trained system. | No mixed old/new key geometry, no query-label use, no mutation of original checkpoints. |
| L3: trained implementation | Add explicit read/write sets in an isolated supplemental implementation. Make acquisition, fallback controller writes, stored deltas, deployment and memory accounting obey the same mask. Clear query/JIT caches on identity changes. | Tests establish inactive writes remain exactly zero and all-site behavior reproduces the baseline. |
| L4: resource pilot | Use synthetic cases, then a short development stream. Profile one training segment, a 100-edit acquisition and full-vocabulary scoring. Account for compilation, cache construction and evaluation. | Projected complete paired matrix fits the lane ceiling and deadline; otherwise choose the read-only factor or stop at diagnostics. |
| L5: fixed fitting | Run the paired seeds; use the same fixed training count and checkpoint policy. Rebuild record keys/codes under each reader. Save final artifact hashes before supplemental evaluation. | All planned trained conditions exist, or missing runs/reasons are explicit. |
| L6: evaluate | Evaluate at 100 and 300 edits; do full ordinary-text fidelity at the final checkpoint. Run the same locality, paraphrase, near-miss and revision definitions for every arm. Log per-example outcomes and truncations. | Complete paired endpoint and resource tables with both factors identifiable. |
| L7: summarize | Plot RET-GS versus KL and positive-loss severity; compare latency and memory; show the interaction between read and write restrictions. | A short report states whether an upper interface suffices, and whether evidence distinguishes access from write effects. |

**What counts as useful:** a smaller interface retains comparable useful editing while reducing time/memory or harm; alternatively, it reveals that the middle/earlier tap is needed. Both outcomes answer Charlie's question. As a proposed practical selection rule, identify variants within 0.02 absolute RET-GS and RET-ES of the paired all-site control on each dataset, without a decrease in locality or near-miss preservation, then compare cost and fidelity. Fix that rule before selection, report all arms, and call it a descriptive tolerance rather than a powered noninferiority test.

The frozen diagnostic is deliverable on its own if time is short, but the report must say why it cannot establish that a trained upper-only cap would fail. Likewise, final-only writing may reduce the corrected-pass work substantially while saving little on the mandatory full-base observation pass. Measure total query cost rather than claiming that the lower blocks have been eliminated.

## 5. AW-B — Bound individual corrections while retaining useful edits

**Priority 2; preferred fallback when little implementation time remains.** General-report §5.2 gives a bounded output tilt; §9.4 gives a retained-predictor mixture. Both can be evaluated around our existing frozen base and learned cap. This is closer to the observed extreme-loss problem than starting a new κ objective.

Let `p0` be the unchanged base distribution and `p1` the unmodified v5 distribution on the **same prefix**, computed over the full vocabulary. In natural-log units define

```text
r(y)   = log p1(y) - log p0(y)
s_b(y) = clip(r(y), -b, b)
p_b(y) = p0(y) exp(s_b(y)) / sum_v p0(v) exp(s_b(v))
```

For finite logits and exact normalization, `exp(-b) ≤ Z ≤ exp(b)`. Therefore the target loss increase relative to `p0` is at most `2b` nats for every token at every fixed prefix. This is an exact consequence of the bounded score, not an empirical tail fit. The construction also bounds `KL(p0 || p_b)` by `2b`; that bound is generally too loose to establish our 0.001 mean-KL benchmark at a useful correction strength.

A simple comparison is `p_mix = rho*p0 + (1-rho)*p1`. Its one-target loss increase is at most `-log(rho)` nats. For a fair bound comparison set `rho = exp(-2b)`. Include ordinary global score shrinkage `softmax(log p0 + alpha*r)` to determine whether the benefit comes mainly from weakening every edit.

These bounds are relative to the specified base and common prefix. They do not guarantee exact-answer preservation, the same generated continuation, a fixed total loss bound independent of answer length, or a smaller tail without loss of editing efficacy. Turning the cap off is an indispensable control and a poor scientific success criterion by itself.

### 5.1 Fixed small comparison

- Use `b ∈ {0.5, 1, 2, 4}` nats; the four matching mixture weights; `alpha ∈ {0.25, 0.5, 0.75}`; unmodified v5 and cap-off. That is **13 configurations**, specified before scoring. Zero-bound and unrestricted-bound behavior are numerical fixtures rather than extra candidates.
- Reuse one qualified v5 development memory per dataset for calibration. Prefer zsRE and CounterFact initially. Add MQuAKE only if both core datasets and the primary study are complete; it is not needed to answer whether bounding can protect the useful cap.
- Select at most one bound and one simple comparator on the calibration split using the same declared efficacy-preservation tolerance as AW-L. Then evaluate those two plus v5 and cap-off on three paired supplemental streams per dataset: **24 final arm×dataset×stream evaluations**. Acquisition can be shared across wrappers because they are query-time interventions on the same immutable memory.
- If only known development streams are available, keep this as an exploratory operating-curve report. Do not take the best point on the ordinary-text validation source and describe that source as independent confirmation. A new text holdout and new edit streams, if available, get frozen before final scoring.

### 5.2 Tasks and checkpoints

| Task | Specific work | Completion checkpoint |
|---|---|---|
| B0: reconstruct | Restore a development checkpoint and verify v5/cap-off predictions and reference identities. Determine whether reusable logits exist; the saved KL/NLL vectors alone cannot reconstruct modified distributions. | Baseline parity before changing predictions. |
| B1: mathematical oracle | Implement full-vocabulary log-space clipping, normalization, mixture and shrinkage. Test normalization, zero/identity limits, extreme finite logits and the per-target bounds using CPU float64 fixtures. | Bounds hold within a declared numerical tolerance; no top-k renormalization. |
| B2: real wrapper | Wrap every prediction call, including each generated answer token. Keep memory updates and gates unchanged; report gate firing separately from the correction actually applied. | Unrestricted wrapper equals v5; hard-null behavior equals base; scalar/batch outputs agree. |
| B3: calibration | Run the 13-config development grid with shared streamed base/cap logits for fixed-prefix assays. Generate full answers separately for each wrapper because prefixes may diverge. | Paired retention–fidelity curves and a frozen, at-most-two-setting selection. |
| B4: final evaluation | Run the four final arms, all paired streams, and full endpoint definitions. Charge reconstruction, full vocabulary, generation and any retries. | Both useful editing and harm measured; no favorable-only subset. |
| B5: report | Show mean KL, signed ΔNLL, positive-tail severity, exceedance frequency and efficacy/cost. Compare empirical maxima with the theoretical ceilings. | A reduction in harm is interpreted alongside any lost editing/generalization. |

Reuse the full-validation normalization/metric conventions in [r1_68f_full_validation.py](../scripts/r1_68f_full_validation.py), but do not route supplemental results through a producer that authenticates a registered recipe as if they were R1 confirmation. Add a separately identified evaluator after the source lock is released.

## 6. AW-G — Generated readers on a fresh small corpus

**Priority 3; only with a working JAX reference and at least a week of usable time.** This is the most direct additional experiment from H3. The question is whether a small, explicitly generated memory reader provides useful predictive evidence beyond a fixed bank and an equally sized unselected addition, outside the repeatedly studied Shakespeare corpus.

### 6.1 Keep the first version small

Use a two-block, width-64, context-64, 256-byte model, trained once in JAX and frozen before cap fitting. Use tied input/output embeddings and count unique parameters. If a verified original teacher is supplied, first reproduce its deterministic outputs; using it on a different corpus is a transfer experiment, not equivalent to training a new base there. Otherwise train the tiny base locally under a fixed budget and label the result a new implementation, not an exact reproduction of unavailable H3 checkpoints.

Proposed fresh corpus: a fixed four-million-byte prefix of enwik8, with chronological 90/5/5 roles and contexts contained within their roles. enwik8 is a 100-million-byte Wikipedia-derived compression dataset; its original source publishes checksums. Download it to `assets`, verify and record the full file and subset identities. Our small subset and selected targets would **not** be a standard enwik8 leaderboard result. [Original dataset description](https://mattmahoney.net/dc/textdata.html)

Proposed fixed data use: first 700,000 training bytes for the frozen count dictionary; 65,536 eligible cap-fitting targets later in the training region; a separate 4,096-target structural-outcome set; development and checkpoint-selection sets from disjoint validation regions; 32,768 final targets from each of two disjoint test regions. Reserve at least the context length at each boundary. Base fitting may use training text, never validation/test; record repeated exposures rather than equating draws with unique data. Freeze exact offsets, seeds and selection policy in G0. Training-only word vocabulary and an unknown-word code are required.

This is one new corpus and one shared base. Three cap seeds measure optimization variation conditional on that base, not independent corpus replications. Use the two test segments as separately reported continuations, not independent studies.

### 6.2 Minimal reader and inference specification

Begin from H3's finite byte-context grammar: lag atoms, partial/current-word prefix, previous word, capped length and byte class. Store bounded count tables with explicit support thresholds, backoff and a normalized probability floor. Cap generated additions at **two**, with at most **100 evaluated candidate proposals**, a 16-million-bit model-cost proxy ceiling and a separately measured total storage ceiling. The proxy is not a substitute for actual bytes.

Admit a candidate only by a fixed development gain rule against the same no-growth refit. Retain rejected candidates and costs. The H3 reported threshold of 0.0002 bpb is a starting recipe choice, not evidence that that threshold is optimal for enwik8. Do not force an accepted reader. Distinguish adding a root reader from selecting an actual parent–child composition.

Use the H3 nonlinear 96/64 gate and its declared energy/inference if the reconstruction passes tests: 32 free steps, step size 0.15, recent 16 already observed targets, and centered nudges ±0.05 during PC training. The H2 notebook instead uses a linear gate and an unnudged-control/nudged contrast; copying it without changing these details does not implement H3.

If a faithful H3 version cannot pass its CPU checks within **two focused implementation days after source access**, stop that port. A validated H2 fixed-reader versus no-settling experiment is an acceptable smaller alternative, but it must be named H2-style and cannot claim generated-reader discovery. Prefer completing AW-L/AW-B to spending the remaining week on a port.

### 6.3 Comparison matrix

| Arm | Readers | Gate/training | Purpose |
|---|---|---|---|
| G-F | Fixed bank | Nonlinear PC, settling | No-growth baseline |
| G-S | Fixed + selected additions | Same nonlinear PC | Generated-evidence effect |
| G-R | Fixed + randomly selected admissible additions | Same nonlinear PC | Extra-memory/capacity control |
| G-B | Same selected graph as G-S | BP through identical finite free inference | Learning-rule control |
| G-N | Same selected graph as G-S | Separately trained feed-forward/no-settling gate | Inference contribution after fair retraining |

Three cap seeds yield **15 fits**, plus inexpensive bare-base and global-mixture references. Fit the global mixture on training data. G-R must match the number of additions, grammar eligibility and declared storage bucket as closely as possible; report an unmatched footprint rather than claiming perfect matching. If no candidate is accepted, report no structural gain and do not manufacture G-R additions to simulate success.

Also score G-S with settling disabled and with permuted recent-history evidence as cheap, explicitly invalid-input diagnostics. These do not replace G-N. A generated-linear gate and a parent-only ablation are optional only after the five-arm matrix is complete.

### 6.4 Tasks and checkpoints

| Task | Specific work | Completion checkpoint |
|---|---|---|
| G0: provenance/recipe | Identify available H3 source and artifact formats; state exact reconstruction deviations. Freeze text roles, reader grammar, costs, fit count, seeds and test segments. | No dependence on an unavailable notebook/archive; independently executable recipe. |
| G1: byte base/readers | Implement or port small pure functions to JAX/NumPy. Verify raw-prefix readers, normalized distributions, frozen dictionary, unknown words and storage accounting. | Same prefix gives the same output; changing a future byte cannot change that prediction. |
| G2: inference/numerics | Verify energy/state gradients, free/nudged separation, update orientation and direct parameter derivatives. Compare finite-step BP with its own finite-difference oracle, and equilibrium PC only with a sufficiently converged equilibrium oracle. | Numerical tests pass; no claim that 32 steps equal equilibrium. |
| G3: cost pilot | Train/freeze the base, construct a bounded cache and profile one cap fit plus evaluation. Verify checkpoint interruption/resume. | Whole five-arm matrix fits remaining budget and dates, including base training/search. |
| G4: fixed search | Evaluate candidates and matched no-growth controls; record signed outcome gains, rejected proposals and accepted structure. Freeze the graph before final arm fitting. | Reconstructible search trace with zero, one or two admitted readers. |
| G5: paired fits | Fit five arms with identical target sampling/checkpoint opportunities where applicable. Charge additional PC steps and rejected search work separately. | All 15 fits complete, or predetermined scope reduction declared before test access. |
| G6: final evaluation | Recompute predictions on both test segments; report bpb, byte-level loss changes/tails, storage, peak memory and total latency. | Raw-prefix checks agree with cached evaluation; results do not depend on target leakage. |
| G7: interpretation | Show generated-vs-fixed, generated-vs-random, PC-vs-BP and trained-inference contrasts separately. | No attribution of the entire base-to-cap gain to CD or PC. |

Full reader distributions over 256 bytes are tractable here. They are not a drop-in replacement for GPT-2's 50,257-token reader/output interface. Any later integration into R1 must preserve tokenizer semantics, causal timing and full normalization; it is beyond this deadline-sized experiment.

## 7. AW-D — Read-only joint preparation of a smaller upper base and cap

**Conditional stretch/alternative, not part of the default commitment.** Attempt only if a validated H3 JAX sandbox already exists early enough. It depends on G0–G3 infrastructure, not on obtaining a favorable G-S result. Freeze the available reader graph; do not combine ongoing reader births with distillation.

The H3 result suggests modifying only the final feed-forward block and associated normalizations while retaining the lower trunk. This is an especially natural version of Charlie's upper-layer idea: the lower representation is reused, and the smaller upper part and cap learn to cooperate. Here **read-only means the cap does not alter base activities during prediction**. It does not mean the student parameters remain frozen during joint training.

Use a width×training design, addressing the missing full-width joint control in the supplied report:

| Final feed-forward width | Staged fitting | Joint fitting |
|---|---|---|
| 256, full width | Fit upper base then cap | Fit upper base and cap together |
| 96, compressed | Fit upper student then cap | Fit upper student and cap together |

Run the four cells with **BP in JAX first**, three paired seeds, identical lower trunk/readers, identical teacher supervision, and equal update counts **per trainable parameter group**. Report total work as well, since sequential and joint fitting need not consume equal compute. Add a fifth, compressed-joint PC arm only if the numerical audit passes and time permits. That is 12 essential fits, at most 15; not all eleven variants of the supplied report.

Tasks:

1. **D0:** verify teacher/student identity, finite probabilities and an exact zero-change full-width baseline. Freeze the same source graph and lower trunk for every comparison.
2. **D1:** construct the narrower upper block and shared teacher-KL warm start using training data only. Account for the warm start and retained teacher.
3. **D2:** match parameter-group update counts, minibatch targets, selection opportunities and teacher access. Fix the task/KD weighting before fitting; do not use test results to set it.
4. **D3:** run the factorial, saving both the standalone base/student and combined-system predictions. This distinguishes a better language model from a better prepared base–cap partnership.
5. **D4:** score bpb and paired loss changes on both test regions; measure total parameters, actual stored bytes including readers/teacher, peak memory and raw-prefix throughput. Cached continuation time alone cannot establish a deployment speedup.
6. **D5:** only if adding PC, report stationarity residuals and finite-step/implicit-gradient comparisons on representative prefixes. A correct local derivative does not establish that the free state converged.

Cache the unchanged lower trunk where valid, but recompute features, base-backed copy readers and predictions that depend on the changing upper student. Include their direct parameter derivatives in the learning rule. Reusing a teacher-era cache after updating the student would change the objective and could create a false joint-training result. If any learned memory keys depend on the updated representation, their rebuild/migration also belongs in the experiment and its cost.

A positive interaction would support joint preparation under compression. A joint advantage at both widths with no compression interaction would instead support joint preparation generally. A smaller student that harms combined prediction is a useful negative result. None of these outcomes demonstrates whole-transformer PC, knowledge-edit retention, or frontier-scale compression.

The supplied writable-PC audit is a reason to defer that branch: its 32-step estimator agrees poorly with its equilibrium gradient in the investigated example, and training/inference feedback proposals differ. The equilibrium-propagation theory concerns the appropriate stationary/nudged construction; it does not make arbitrary short inference gradients interchangeable. [Scellier and Bengio](https://arxiv.org/abs/1602.05179)

## 8. Common evaluation and statistical discipline

### 8.1 R1-based additions: AW-L and AW-B

Use identical examples across paired arms and retain the existing definitions of immediate edit success, retained original-answer success (RET-ES), retained paraphrase generalization (RET-GS), bounded-text locality, near-miss preservation and revision behavior. Include scored/planned counts, truncation and unavailable fields. At the final checkpoint report:

- Mean reference-to-cap KL and mean signed target ΔNLL, using the same prefix/reference; original-base and own-cap-off identities remain explicit.
- Positive-part ΔNLL, ES95 and ES99 including zero mass, maximum with location/ties, and strict exceedance proportions at 0.01, 0.1 and 1 nat.
- Frequency of positive harm and conditional severity among harmed positions; the number of positions/windows carrying half the KL or positive loss.
- Efficacy versus fidelity/cost operating curves, not a single number labeling an arm “safe.” Show the existing 0.001-KL and 0.01-mean-ΔNLL benchmark lines without silently changing their interpretation.
- Total acquisition/query time, compilation/cache construction, memory/VRAM, serialized artifacts and failures. Full ordinary-text coverage and fixed-prefix sample coverage are separate populations.

The primary text assay has 1,931 reset-context windows and 245,237 scored positions. Use it for comparability, but it is already known from development and reporting. Only a separately reserved text source can support a fresh-text generalization claim. Its short windows do not establish safety during arbitrarily long generation.

Three reader seeds or three edit streams do not make hundreds of thousands of tokens independent experimental replicates. Show all paired seed/stream differences and within-dataset consistency. If using uncertainty intervals over text, resample paired contiguous windows/blocks and identify that conditional estimand; do not present them as uncertainty over new corpora or new base pretraining. Do not add these contrasts to the registered primary family or borrow its decision labels.

### 8.2 Byte experiments: AW-G and AW-D

Use bpb for the tiny byte models and nats/token for R1. Dividing nats by `ln(2)` yields bits per **token**, not automatically bits per byte for GPT-2. Never pool the two scales in an effect-size chart.

Save paired per-position losses and source/segment identifiers. Report both test regions, all seeds, rejected structures and zero gains. A survival curve can show concentrated rare losses without a power-law claim. Smoothing floors impose finite loss ceilings in H3; a clipped output imposes a bound in AW-B. Neither should be advertised as an observed natural tail cutoff.

Before reporting any PC advantage, identify whether the difference is the learning rule, prediction-time settling, available evidence, structure, parameter count or exposure. Match what can be matched and explicitly charge what cannot. The theoretical convex-energy discussion also needs care: convexity alone does not ensure a unique minimizer; strict/strong convexity or another uniqueness argument is required.

### 8.3 Memory and reproducibility

Do not store dense paired logits for the whole GPT-2 validation population. One float32 array of `245237 × 50257` is approximately **45.9 GiB**; a base/cap pair is approximately 91.8 GiB, before activations and workspaces. Stream full-vocabulary batches, compute exact normalizers/statistics, and retain compact per-position metrics. Top-k logits alone are insufficient for exact KL or the proposed bounds.

For byte inference, the past-evidence term needs each reader's probability of the byte that actually occurred, not a dense vocabulary vector for every historical position. Bound full next-byte distribution caches separately. Record data, code, model, graph, read/write-set and reference hashes; use deterministic seeds and a tested resume point. Preserve failed attempts in resource accounting. Do not start a large cache build simply because the GPU is idle.

## 9. What to reuse and what still requires new work

| Existing resource | Reuse | Limit/new work |
|---|---|---|
| `src/pccap/bases/gpt2_jax.py`, BP wrapper | Exact frozen-base forward, site tensors, partial corrected passes, batched logits | Do not move the registered sites. Alternate interfaces belong to the supplemental implementation after lock release. |
| `revision_v1/reader.py`, `observations.py`, `stream_train.py` | Configurable taps, stable observations, cached stream training, null/lexical features | Refit/re-encode for a new feature interface; verify writer dependencies and cache identities. |
| `revision_v1/adapt.py`, `controller.py`, `learner.py` | Delta acquisition, aggregate bounds, serialized memory and query path | Existing `single_site` is a deployment ablation; training-time masks and all fallback paths need explicit work. |
| `scripts/r1_68f_full_validation.py`, completed R1 analysis | Full-vocabulary metrics, streamed scoring, tail definitions, output checks | Existing authentication is for existing recipes; create supplemental output provenance. Saved aggregate metrics do not recover logits. |
| Existing HT plots and report formatters | Figures and denominator/tail conventions | New experiment labels; no rewriting primary figures/results. |
| FabricPC and `pc/epc_inference.py` | JAX graph/inference patterns and numerical-test lessons | The current ePC error-variable solver is not H3's free/centered-nudge cap energy. Reusing it without deriving the correct objective would change the experiment. |
| Supplied H2 notebook source | Byte model/readers, causal caching, update accounting, restart/test design | PyTorch source only; must be reimplemented in JAX. No H3 birth/distillation implementation or measured local runtime. |
| H3 reports | Equations, controls, data-role design and numerical failure warnings | Missing executable H3 archive/checkpoints are a real development dependency. |

After lock release, suggested new namespaces are `src/pccap/additional_work/`, matching scripts/tests, `manifests/additional_work/`, `results/additional_work/`, and `logs/additional_work/`. Choose exact files with Claude before editing. Avoid opportunistic refactoring of production R1 while implementing a supplemental hypothesis.

## 10. Time and compute plan

The following are **stop ceilings and engineering estimates**, not profiled predictions. A lane is admitted only if its measured pilot projects the complete comparison within its ceiling and the remaining calendar. All ceilings include shared preprocessing attributable to the lane, compilation, fitting, evaluation and normal retries. Charge shared work once with an explicit owner.

| Lane | Estimated implementation/review effort | Proposed maximum GPU reservation | Scope reduction if the pilot does not fit |
|---|---|---:|---|
| AW-0 preparation | 0.5–1 person-day | 0 h | Source/specification/resource audit only |
| AW-L upper interface | 1–2 person-days plus execution | 48 h | Read-interface factor only, then frozen diagnostics if training still does not fit |
| AW-B bounded output | 0.5–1.5 person-days plus execution | 24 h | Known-checkpoint exploratory curves, capped at 8 h; no fresh-outcome claim |
| AW-G generated readers | 2–4 person-days if code/equations are adequate | 32 h | Validated H2-style smaller study, or defer; do not omit critical controls to retain an H3 headline |
| AW-D joint upper fitting | 1–2 additional person-days **after validated sandbox exists** | 24 h incremental | Four BP factorial cells only, or defer |

Default complete portfolio: **AW-L + AW-B = at most 72 GPU reservation hours**, plus a 12-hour verification/retry reserve, hence at most **84 hours**. Keep a proposed global supplemental ceiling of **120 GPU reservation hours**, including reserves, if Charlie allocates that much. The 120 hours are not automatically authorized by unused R1 process-hours.

An expanded portfolio can be AW-L + AW-B + AW-G = 104 hours plus a 16-hour reserve, totaling 120. An alternative is AW-L + AW-G + AW-D = 104 plus 16, also 120. **Do not promise all four full lanes:** that would be 128 hours before reserve. AW-D can replace another lane only when its software dependencies and calendar are satisfied. CPU preparation, human review time and elapsed days still matter even if GPU hours fit.

### 10.1 Release-date decision table

| When primary work and source lock are released | Recommended supplemental commitment |
|---|---|
| By September 27, with working prep and at least nine usable days | AW-L and AW-B; consider one expanded portfolio only after measured pilots. |
| September 28–October 1 | Prefer AW-L + AW-B if the 84-hour envelope and implementation fit; otherwise choose the complete upper-interface study first. |
| October 2–4 | One ready lane only. Prefer AW-L if its implementation is already validated; otherwise AW-B's bounded exploratory study. No new H3 port. |
| October 5–6 | At most a pretested ≤8-hour measurement on known checkpoints, or analysis-only work. No new architecture/training campaign. |
| October 7 or later | Consolidate and verify completed results. Do not create a new dependency for the presentation. |

The dates are conservative project-management defaults, not inferred completion forecasts. Release requires completion of required primary work, not merely the last primary GPU call. A missing registered endpoint/report has priority over supplemental feature development.

### 10.2 Calendar checkpoints

- **September 20–23:** prepare recipes, inventory available inputs, identify exact source-lock restrictions, draft result tables and obtain any missing H3 materials if the lead already has them. No heavy host work or GPU activity competes with R1.
- **September 24–27, conditional on release:** pass AW-L/AW-B correctness and resource pilots; choose the portfolio. Drop AW-D from October scope if a validated H3 implementation is not available by September 27. Do not wait for missing code indefinitely.
- **September 28–October 4:** execute complete paired comparisons in priority order, with daily cost/completion checks. A lane may be narrowed only before its final outcomes are inspected; partial attempts and exclusions remain visible.
- **October 5–6:** complete remaining admitted fits. **No new architecture or hyperparameter family after October 6.** Preserve time for final assays, not just training.
- **October 7–8:** finish held-out evaluation, rerun only specific failed/invalid measurements, recompute summaries and produce draft figures. Target all new successful experimental measurements by October 8 evening.
- **October 9:** contingency verification and final experimental freeze; proposed internal cutoff **17:00 America/New_York**. Any incomplete comparison is reported as incomplete rather than extending into presentation preparation.
- **October 10–14:** analysis of frozen outputs, checking claims, slide construction and rehearsal. No additional experimental fitting or outcome collection.

Before dispatching a job, require `conservative projected completion + remaining validation/report time < cutoff`. Record the projection and decision. If primary repairs consume the buffer, cancel supplemental work rather than alter the primary scientific commitments.

## 11. Parallel work without contention

These are suggested ownership lanes for Charlie and Claude to assign, not agents launched by this planning task.

| Lane/owner role | Work that can proceed independently | Dependencies and contention boundary |
|---|---|---|
| Primary-run owner, Claude | Finish R1, reconcile costs, resolve primary endpoints and release the lock | Owns dispatch and production source until explicit handoff. |
| Upper-interface implementer | AW-L recipe, cache identity audit, then new supplemental read/write code | No production source edits while locked; one owner for adaptation-mask implementation. |
| Preservation implementer | AW-B mathematics, CPU oracle, separate wrapper and report schema | Shares only documented logits/model-state contracts with AW-L. Can develop independently after release. |
| Optional sandbox implementer | AW-G source inventory, byte readers and CPU causality/numerical checks | Separate namespace; no competition for GPU or large host caches. AW-D depends on this implementation. |
| Independent reviewer/analyst | Verify split/identity checks, paired denominators, normalization, resource totals and figures | Reviews another person's numerical implementation before GPU use. Reads immutable results. |

With two active coding agents, use one on AW-L and one on AW-B, then exchange reviews. GPU executions remain serialized unless a later measured concurrency review justifies otherwise. Do not have both edit a common adapter, status registry, `ongoing.md` or report at once. Use per-lane records; one designated integrator updates shared coordination documents.

The main dependencies are:

```text
R1 completion + lock release + supplemental budget
    ├─ AW-L correctness → resource pilot → paired layer study → report
    └─ AW-B oracle → resource pilot → calibration freeze → evaluation → report

AW-G source/causality/numerics → resource pilot
    ├─ generated-reader comparison → report
    └─ if ready early: AW-D joint/staged factorial → report

All completed lanes → independent recount → October 9 experimental freeze
```

## 12. Deliverables and completion criteria

For each executed lane, deliver a compact manifest with hypothesis, data roles, controls, seeds, configuration grid, checkpoint/selection rules, resource ceiling and source hashes; an executable JAX/CPU implementation with focused correctness tests; paired raw results and resource accounting; and a short report showing all planned arms, failures and limitations.

For the presentation, the useful figures would be:

1. **Upper interfaces:** retained paraphrase accuracy versus ordinary-text harm, with read/write sets and query cost visible. A small diagram distinguishes the unchanged lower trunk from cap read/write ports.
2. **Bounded correction:** efficacy–fidelity curves and empirical loss-survival curves, showing both theoretical bounds and lost efficacy, if any.
3. **Generated readers, if completed:** paired bpb changes for selected versus fixed/random evidence and PC versus BP, with actual memory cost beside predictive gain.
4. **Joint preparation, if completed:** the width×training interaction, reporting combined and standalone student scores plus total storage/latency.

Keep a one-page claim table with columns “measured result,” “population,” “control,” “what it supports,” and “what it does not support.” Negative results belong in that table. Do not combine a better scalar metric from one lane with a different lane's efficacy as if one system achieved both.

AW-L is complete when a paired comparison or explicitly limited frozen diagnostic answers which interfaces were tested and at what cost. AW-B is complete when reducing rare harm has been assessed alongside useful editing. AW-G is complete when structural search and the essential controls have final test scores, including a possible no-birth result. AW-D is complete when the factorial distinguishes joint fitting from compression. The entire supplemental effort is complete when every attempted lane has a reproducible result or an explicit stopped/incomplete disposition and the October 9 freeze is met.

## 13. Work to defer beyond the presentation

- Writable feedback into the transformer, full-base PC training, new Fisher/precision energies and unconstrained settling-depth searches. Their numerical and design uncertainties exceed this window.
- Learned history/STLM-style proposal guides. H3 has too little independent search-history evidence to justify that complexity here; candidate labels are not independent search trajectories.
- Multi-cap summed energies, module exchange across machines, a standalone generalized transformer, and symbolic-platform integration. These are valid program directions but need their own experiments.
- A seven-hour Colab run treated as a validated schedule or a porting shortcut; the supplied notebook does not substantiate either claim for our environment.
- A large new corpus/model sweep, another full MQuAKE expansion, or a new κ-training campaign. None is required for the narrow upper-interface/preservation questions.

If a validated byte sandbox finishes unusually early, a small frozen-reader domain-transfer/replay comparison is preferable to the speculative items above: report old-domain loss increase and new-domain improvement together, with PC, BP, replay and continued-old-domain controls. It is a replacement use of a remaining lane budget, not an uncosted extra promise. Fix replay exposure accounting and the held-out domains before running it.

The recommended immediate decision is therefore **prepare AW-L and AW-B, with AW-G held as a conditional option**. This folds the GT documents into our actual scientific problem, gives Charlie's upper-layer hypothesis a fair test, and preserves a realistic path to additional results before October 9.
