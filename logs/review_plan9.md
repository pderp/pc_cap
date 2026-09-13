# R1-X0 — counter-review of revision-v1 plan 9

Reviewed 2026-09-13 by Codex. Contract: `docs/updated_plan9.md`, accepted by DEC-033. Specifications read in full: `docs/more_input/pc_cap_results_overview (1).pdf` (4 pages), `pc_cap_joint_redesign_proposal (1).pdf` (3 pages), and `pc_cap_coding_agent_guide (1).pdf` (10 pages). Starting checkout: `b0da8bd`; the v3 grammar queue and another agent's source restoration were active. This is a review and a set of proposed clarifications, not a change to accepted decisions or frozen results.

The plan preserves the main scientific sequence and most numerical constraints. It is a reasonable basis for implementation. It does not yet specify enough controls to attribute a gain to the episodic objective, enforce all label/retrieval boundaries, or justify the complete GPU budget. These gaps should be resolved before the corresponding training or confirmation gates. CPU baseline reconstruction and development-only episode work can proceed now.

## 1. Findings that change what needs to be built

### X0-01 — missing ordinary teacher-matching continuation control (high)

The guide, p.8, requires ordinary teacher-matching continuation to receive the same added training data/tokens when attributing a gain to the new distillation objective. Plan 9 includes the BP-trained counterpart and the 2×2 table, but neither replaces this objective control. A checkpoint receiving more training can improve for reasons other than the new episode losses.

Add a named teacher-only continuation condition starting from the same checkpoint, with matched added examples/tokens and a reported compute comparison. Retrain its cap under the same development allowance. Record whether this condition shares an already scheduled comparison cell. Until it runs, describe gains as effects of the combined training procedure, not evidence that the editability objective caused the gain.

### X0-02 — the common fast-update comparison needs an executable adapter (high)

The proposal p.3 and guide p.8 hold the fast learning rule fixed when comparing caps. Plan 9 repeats this requirement, but v0 uses bounded direction/candidate search over stored activation writes (`cap/learn.py`), while Stage 1 proposes gradient updates of a learned fact code. These differ in update variables and optimization procedure. Moreover, v0 has no reusable learned reader/controller to “retrain” in the same sense as the stronger cap.

Specify a common support-only optimizer interface, update budget and stopping rule for the controlled architecture comparison. If a v0-shaped cap must gain a differentiable value-code adapter, label it as a new matched-update control and retain the unchanged v0 result separately. Report the learned-cap system comparison even if this isolation is impractical, but do not infer that retrieval architecture alone caused that combined change.

### X0-03 — train retrieval beyond the chosen top-k set (high)

Guide p.5 requires full-episode retrieval supervision to train keys that did not enter the selected candidate set. Stage 2 names `L_retrieval` and fixed retrieval inside the differentiable segment, but does not specify this additional route. Loss through selected keys alone can leave missed positive memories without corrective supervision.

Add a full-active-episode key/null discrimination loss outside the fixed-top-k adaptation segment. Normalize and log it independently. Test an episode where the relevant record lies outside top four and verify that the intended reader/key parameters receive a nonzero update. Preserve the fixed-selection gradient interpretation of the fast unroll.

### X0-04 — make loss labels and base-step stop-gradients explicit (high)

The guide pp.5–6 separates revised new labels, retained revised old labels, and teacher preservation targets. It also requires memory, retrieval identities **and generated writes** to remain fixed within each alternating base-update call, with observations/retrieval/writes refreshed between calls. The plan's abbreviated surrogate description does not spell out all of these boundaries.

Write a loss-source table before R1-21/R1-22: input population, target source, normalization denominator, trainable leaves and stopped leaves. Assert that teacher imitation cannot score an explicitly revised answer as the old answer. Match initial checkpoints, masks, examples, proportions, schedules and normalizations in the BP/ePC pair. Report ordinary-gradient updates to heads/tied embeddings and reader weights. Keep the differentiable reference's mathematical controls separate from surrogate controls.

### X0-05 — selected fact consistency across answer positions is underspecified (medium)

Guide p.4 specifies one retrieved fact across the positions of an answer, while the correction depends on the current prefix. Plan 9 describes joint three-site writes but omits answer-level record selection. Re-running retrieval freely at every generated token can switch facts mid-answer and confound the intended decoder test.

Specify when fact identity is selected, how the null decision persists or changes, and when state resets between queries. Keep all activations causal. Test a multi-token answer whose later prefix would otherwise prefer a different memory. For multiple-candidate mixtures, explicitly reconcile the mixture policy with the guide's single-fact wording rather than silently choosing one interpretation.

### X0-06 — stable-key rebuilding, revision snapshots and prediction costs need fuller gates (medium)

Guide pp.3–4 includes memory codes, active records, index/encoder versions and RNG in snapshots; active support keys are rebuilt after outer updates to the base/encoder. Source tokens and rebuilding cost count as persistent state and computation. The plan names versions/serialization but leaves the rebuild/reset transaction implicit.

Add tests for encoder-version refusal, complete deterministic resume, revision supersession, and rebuilding all active keys from support only after each outer update. Give predictions a read-only interface. Charge the unedited observation pass and the subsequent corrected pass. Include cached or single-site alternatives in the cost investigation, as requested on guide p.4; they are absent from the current work list.

### X0-07 — cap-level settling must be trained for answer quality (medium)

Plan 9 preserves the proposed latent energy, the target-free loop, zero-step control and compute-matched recurrence. Guide p.7 additionally requires the energy's learned parameters to be coupled to the episodic answer/preservation objective and calls out latent collapse, unused memories and trivial decoders. Merely reducing the reconstruction energy would not meet that requirement.

Before Stage 3, declare gradients through the solve, state reset policy, and any named approximation. Include ablations that remove the relevant memory and measure answer changes, not only energy. Charge failed and terminal-evaluation steps and keep full-base calls outside the latent loop. This is a refinement of the accepted optional stage, not grounds to start it early.

## 2. Data and fresh confirmation

### X0-08 — current zsRE development items cannot satisfy two-paraphrase episodes (high)

The guide p.5 and R1-20 require at least two unseen paraphrases. A new CPU inventory found **300/300 zsRE development items have exactly one distinct supplied paraphrase; 0 have two**. CounterFact has **300/300 with two**. Evidence: `logs/r1_codex_20260913/data_inventory.json`, generated by `scripts/r1_x0_data_inventory.py`; prompts equal to the support prompt and duplicate paraphrases do not count.

Start with the synthetic task and eligible CounterFact development episodes. The zsRE adapter should refuse the unmet cardinality, with its exclusion count recorded. To complete zsRE episode training, approve a documented second-paraphrase source/generation and semantic validation protocol, or explicitly revise the episode requirement. Repeating the one paraphrase is not a second test. Do not fetch fresh confirmation examples to fill development gaps.

### X0-09 — D-R2 must exclude the exposed S7 inventory, not only executed pairs (high)

The chosen MEND train source contains **163,196 subject fields and 91,612 distinct normalized subject strings**. It has already supplied S7 examples. The zsRE S7 manifest exposes 300 candidate pairs with **496 distinct subjects**; the selected 100 pairs use **166 subjects**. Excluding selected pairs alone leaves **330 exposed candidate subjects** available for a nominally fresh test. CounterFact's S7 inventory contains 75 pairs and 141 distinct subjects, all selected.

The subject-only audit conservatively excludes the union of both complete old eligible pools and v0 development/S0 subjects. This leaves 88,999 distinct MEND train subject candidates before S7, and **88,503 after all 496 exposed S7 subjects are removed**; 155,833 raw records refer to those remaining subjects. These are **not** E.2-filtered counts and are **not** a reserved test set. No sealed realization payload was opened by this audit. The full pool exclusion is deliberately stricter than excluding just the old sealed realizations; the final policy remains the lead's decision.

Create a versioned exclusion inventory before new data selection. Include all S7 candidate subjects, v0 development/S0 and sealed subjects, challenge sets, and every subject subsequently used by revision development. Apply the exclusion across datasets. Use normalized subject identity, then document alias/entity resolution and unresolved mentions in paraphrase/locality text. Source-subject disjointness alone does not establish that all entities visible in those prompts are disjoint. Record both raw-record and deduplicated-subject counts before/after each filter, including E.2 failures. Seal only after those gates pass.

The plan's 1,420/17,091 remainder counts are source-pool arithmetic, not a complete subject/alias/challenge exclusion audit. D-R2(b) is plausible on source capacity, but final usable capacity remains unmeasured. Do not turn the subject-only audit into a positive confirmation feasibility result.

### X0-10 — grammar seeds do not by themselves give disjoint facts (high)

The original generator changes surface sequences while reusing eight contexts and fixed latent mechanisms. A new seed block alone does not guarantee new entities, fact identities, paraphrase families, or full paraphrase coverage. Plan 9's “≥6,000,000” seed statement therefore needs a concrete partition manifest for the extended generator.

R1-20 should reserve actual latent scopes/entities and surface families before sampling, and expose composition supports only in the evaluation/training annotation container. Verify at least two distinct unseen paraphrases for **every** generated item and reject an incomplete episode as a whole. Disclose shared composition syntax explicitly. The development generator and fixtures inspected during implementation are not fresh confirmation. Give final generation a separate version/reservation, with seed ranges disjoint from every development episode actually emitted.

## 3. Costs, calendar and scheduling

### X0-11 — the 15-hour confirmation estimate has no complete job matrix (high before launch)

The plan estimates the 2×2 table as 24 runs (4 cells × 3 seeds × 2 orders). That is one dataset. Adding a second natural-language dataset doubles that count before grammar/composition, the original BP-plus-strong-cap control, the strongest BP-trained counterpart, teacher-only continuation, surrogate switches, settling controls, full drift endpoints or failures. Some conditions may share cells, but their reuse must be explicit.

The arithmetic 20 development + 15 confirmation = 35 accelerator-hours leaves roughly five hours within “≈40” for any separately charged co-training. Stage 0/1/2/3 estimates sum to 17 hours, leaving three development hours; whether Stage 2's eight hours already include co-training is ambiguous. This is an accounting ambiguity, not evidence that 40 hours is impossible. Existing v0 learning times do not measure the new reader, support-code unroll, outer gradients, replay, index rebuilding, or JAX compilation costs.

Before GPU launch, create a deduplicated run matrix with condition, dataset, seeds, orders, length, trainable mask, training tokens, shared-checkpoint provenance, proposed ceiling and failure reserve. Profile both ten edits and a short outer-training batch. Include warm-up, checkpointing, failed runs, phase counters, one-time base/cap preparation, total persistent bytes and peak memory. Measure full-drift endpoint costs on the revised model. Freeze ceilings before seeing scientific outcomes, as guide p.9 requires.

### X0-12 — elapsed-time promises are not yet evidence-backed (medium)

Forty accelerator-hours fit into 1.67 days only under continuous availability; 4–6 wall-clock days assume roughly 6.7–10 GPU-hours available each day and omit CPU implementation/review waiting. Four calendar weeks are a planning allocation, not an extrapolation demonstrated by the v0 runs. The guide supplies stage order and profile-based ceilings, not this four-week delivery promise.

If day 1 is September 13, the indicative windows are Stage 0 Sep 13–15, Stage 1 Sep 15–22, Stage 2 Sep 20–30, optional Stage 3 Sep 27–Oct 4, and Stage 4 Oct 2–10. Shift them if close-out or a gate slips. The Stage 1/2/3 overlaps are safe for interface work, episode preparation and controls; training must obey the previous gate. The plan says every stage ends with counter-review, while its calendar overlaps stages: publish explicit “implementation may overlap / training awaits gate” dependencies.

Also separate engineered-fixture correctness from trained generalization. A randomly initialized learned reader need not already pass a genuine unseen-paraphrase learning-quality test before its first training step. Require a controlled planted-fact mechanics check before training and a behavioral generalization check after the bounded pilot, before advancement. This preserves the guide's intent without making the training gate circular.

## 4. Immediate implementation reconciliation

### X0-13 — baseline and new source must not invalidate the running v0 queue

The top of `ongoing.md` prohibits source changes under the active frozen tree, while its new R1-20 lane names `src/pccap/revision_v1/episodes.py`. `harness/freeze.py:tree_sha` includes **all** Python descendants, including newly created modules. Adding a file can therefore invalidate a subsequent queued v0 job even though no existing file was edited.

Stage the episode implementation in `scripts/r1_20_episodes.py` until the orchestrator releases the source tree or supplies the proper versioned transition. Tests can load the staged file directly. No v0 source edits or bypass flags are needed for this CPU work. A starting baseline recorded while the queue/close-out is moving must be marked provisional; the final close-out commit needs its own explicit identity. `ongoing.md` says CPU Stage 0 starts now, whereas plan §6/DEC-033 ties the final baseline to close-out; preparatory audit work is safe, but those identities must not be conflated.

### X0-14 — review the new Stage 0 diagnostic script before spending its GPU allowance

The newly committed `scripts/r1_diagnostics.py` is not itself the plan, but it is the immediate implementation of the guide's first gate. Static inspection at `b0da8bd` found:

* Oracle lookup falls back from a missing answer-prefix entry to prefix 0. The guide p.2 requires explicit answer-prefix matching. Missing entries should be counted as unavailable, not replaced by an entry for a different prefix.
* The per-item slot map retains historical slots. Before an oracle uses one, verify current slot ownership, activity and prefix identity; a slot may have been reused. Aggregate “own item” counts alone do not establish correct prefix ownership.
* D1 records first-token NLL, not teacher-forced loss over the complete target sequence. Keep the first-token statistic explicitly qualified and add the sequence-level assay if the broader guide requirement is intended. Free-generation exactness is a separate measurement.
* D0 discards detailed per-query/per-site retrieved-record and answer-prefix traces after accumulating categories. Persist those traces to support the requested failure diagnosis.
* D2 computes stable/live key and retrieval differences but does not execute the complete stable-read corrected-answer condition. That is useful localization, but it cannot establish that stable observations improve answer retention. Either add the controlled outcome assay or narrow the gate's interpretation.
* The diagnostic calls share a ledger with stream work, but the diagnostic summary does not persist its complete final phase totals. Preserve before/after phase deltas and reconcile stream, oracle and stable-observation costs, including the extra base pass.

These are review requests to the orchestrator, who owns that script and GPU lane. Codex did not edit it or run it.

## 5. Requirements preserved and next gates

| Specification requirement | Plan 9 coverage | Remaining verification |
| --- | --- | --- |
| Preserve v0; keep base fixed during editing evaluation | Explicit | Final close-out identity and frozen component hashes |
| Learned null reader, top four, stable observations, coordinated writes | Explicit | X0-03/05/06; no-target and null-output tests |
| A=0.3, ≤5M parameters, 64 MiB total state, matched memory/frontier | Explicit | Count stored tokens, indices, metadata and all reusable weights |
| Support-only fast code; rollback and bounds | Explicit | Data API separation and accepted-step controls |
| Differentiable reference before scientific surrogate claims | Explicit | Finite differences; fixed discrete choices and loss-source table |
| BP/ePC surrogate pair with honest interpretation | Explicit | Exact matched schedules/masks and stop-gradients, X0-04 |
| PC energy optional; zero-step/feedforward/recurrent controls | Explicit | Answer-objective coupling, state reset, solver accounting |
| Acquisition, unconditional retention, near-miss/revision/composition endpoints | Explicit | Denominators, revision semantics and verified two-hop labels |
| Three seeds; orders clustered; preliminary intervals | Explicit | Frozen pairing, missingness and selection rules for revision data |
| Fresh data, disclosed drift assay and new lead freeze | Explicit | Exclusion inventory, profile-based ceiling and complete run matrix |
| Teacher-only continued-training control | Missing | X0-01 |
| Full failed-work accounting and reproducible command/checkpoint identities | Abbreviated | Explicit CLI/resume schemas and failed-run records |

**Safe parallel lanes now:** Codex R1-00 saved-record reconstruction, R1-X0 review, R1-20 synthetic/development preparation and CPU controls. Orchestrator: v0 close-out and the GPU diagnostics. Once interfaces and diagnosis are accepted, episode integration can overlap Stage 1 core implementation. R1-23's actual parameter/label-path audit waits for those Stage 1/2 implementations; a schema-only check would not complete it. Source installation waits for release of the frozen v0 queue. No training or revision confirmation is authorized by this review alone.

Suggested earliest owner actions: resolve the D0/D1 diagnostic scope before running it; settle the second zsRE paraphrase source; pin the exclusion inventory; add teacher-only continuation and the common-fast-rule adapter to the comparative design; publish the profiled, deduplicated budget. These preserve the accepted direction while making its conclusions more interpretable.
