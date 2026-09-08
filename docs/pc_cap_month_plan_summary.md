# A Plain-Language Summary of the One-Month Cap Research Plan

Source: [A One-Month Programme for Continual-Learning Predictive-Coding Caps on GPT-2-Scale Transformers](pc_cap_month_plan_readable.pdf), Ben Goertzel and Claude Fable, revised readable edition, 7 September 2026.

This summary covers the research proposal and its implementation appendix. It explains the design and the main numerical commitments; the PDF remains the reference for exact equations, edge cases, and implementation settings. **The source is a plan, not a report of new experimental results.**

## 1. What Is the Project Trying to Do?

Teach a language model new information, one item at a time, without repeatedly retraining it on everything it has learned before.

The proposed approach keeps the original model's weights fixed and attaches a small, editable memory called a **cap**. The cap reads the model's internal signals and adds corrections while the model is producing an answer.

The central question is:

> If we test several places for a correction and choose the one that helps most, can we learn new information with less damage to earlier knowledge, while preserving useful connections between tasks?

For example, an edit should fix one answer, work when the question is rephrased, and leave unrelated answers intact. If two tasks use the same underlying rule, learning one should still be able to help the other.

The project must also check whether any improvement is worth its memory and computing cost. A method that learns very little can appear to forget very little, so preservation alone is never sufficient evidence of success.

## 2. The Basic Pieces

| Term | Plain-language meaning |
| --- | --- |
| Base | The original transformer, whose weights stay fixed during cap learning. |
| Residual stream | The internal vector passed through the model's layers and modified by each layer. |
| Cap | An added memory that reads these vectors and adds corrections to them. |
| Bank | One part of the cap, attached at a particular layer depth. |
| Slot | A stored entry containing a matching key, a correction vector, a matching radius, and a small amount of bookkeeping. |
| Key and query | The stored matching pattern and the pattern computed for the current input. |
| Credit | A signal suggesting which direction to change a correction to reduce prediction error. |
| Router | The rule choosing which bank receives an update. |
| Arm | One experimental configuration. |
| Stream | The sequence of facts or tasks presented for learning. |

There are three banks: roughly one-third, two-thirds, and all the way through the transformer. A bank reads the current prediction position before making its own write. Earlier writes can therefore affect what later banks see.

At prediction time, each bank finds the nearest stored key within that slot's allowed radius. It adds the matching slot's correction, or does nothing if no slot matches.

Turning the cap off must recover the original model's computation. **Keeping the base weights fixed does not guarantee unchanged answers while the cap is on.** The corrections deliberately change the computation, so unintended changes must be measured.

## 3. Where Predictive Coding Fits

Ordinary backpropagation computes a gradient: a direction in which a small change would reduce the loss, or prediction penalty. The document calls the gradient at an internal model state an **adjoint**. Gradients can be computed through a frozen model without updating its weights.

Predictive coding explicitly represents mismatches as error variables. In error-based predictive coding, or **ePC**, an iterative calculation adjusts these errors and reconstructs internal states from them. The document calls this process **settling**.

The project compares an ordinary model, **BP**, with an existing ePC conversion of it. It does not assume ePC is better. Earlier internal reports claimed close agreement with the original model and strong alignment between ePC errors and gradients, but those claims must first be reproduced.

Two distinctions matter:

- The cited digital ePC implementation uses backward automatic differentiation during settling. Settling has a real computing cost.
- This month's cap, **v0**, is a gated correction memory inspired by predictive coding. It has no separate cap-level inference process or energy function of its own. It is not yet the full predictive-coding cap envisioned for later work.

The default error-credit procedure uses eight iterations. Eight iterations do not automatically mean convergence; the experiment checks the remaining error and compares against a 64-iteration reference.

## 4. Three Separate Questions, Three Controlled Comparisons

Changing several things at once would make a winning result difficult to explain. The plan separates routing, model conversion, and the choice of learning or retrieval signal.

### A. Does Choosing the Write Location Help?

First build and test the cap on the ordinary BP model.

| Arm | Where it schedules writes | What it tests |
| --- | --- | --- |
| C0 | Only the last bank | Whether access to earlier layers helps. |
| C1 | All three banks | The reference for updating everywhere. |
| C2 | The one bank with the best helpful trial correction, or none | Whether measured selection helps. |
| CR | One randomly selected bank | Whether the benefit is simply updating fewer banks. |
| CO | Banks supplied by the constructed test's known rules | What correctly informed routing can achieve in that test. |

The main comparisons are **C2 versus C1** and **C2 versus CR**. CR's bank probabilities are fixed using C2's routing frequencies on development data. Its actual write rate and C2's abstentions are also reported.

If C2 beats C1 but does not beat CR, there is no demonstrated advantage from its measured selection over random sparse routing. CO is only a control in the constructed test, where permitted routes are known.

All these arms get the same total memory ceiling and nominal total write-size budget. C0 receives the entire memory allowance at its last bank; C1 divides its write budget among three banks.

### B. Does Converting the Base to ePC Help?

Use the same all-bank routing rule, plain hidden-state keys, and memory/update protocol:

| Arm | Base | Learning signal |
| --- | --- | --- |
| SB | Ordinary BP model | Gradient |
| SE-A | Converted ePC model | Gradient |
| SE-E | The same ePC model | Error after the declared inference procedure |

**SB versus SE-A** tests the conversion under a common credit rule. **SE-A versus SE-E** tests the credit procedure on the same converted model.

The BP work continues if ePC is unavailable, too expensive, or unsuitable. If the matched models only support a synthetic language, their comparison stays synthetic; factual editing uses a separate capable BP model. A same-ePC credit comparison can still be informative if teacher fidelity fails, but cannot establish an advantage over BP at matched fidelity.

### C. Do Different Retrieval Keys Help?

The default key comes from the current, cap-modified hidden state. Optional comparisons use:

- **R-h0:** hidden states from a separate pass with the cap off, to test whether upstream edits disturb later retrieval.
- **R-g:** cap-off hidden states plus gradient features.
- **R-e:** cap-off hidden states plus ePC error features.

R-g and R-e have equal key dimensions and memory ceilings. Wider keys mean fewer available slots. Their extra calculations are charged at prediction time as well as learning time.

Neither can use the correct answer to build a prediction-time key. Both use the uncapped model's own predicted token as a temporary target, and the same key procedure during training and inference.

## 5. How One Edit Is Learned

An edit supplies a prompt and a complete desired answer. Training visits the answer token by token, including its ending delimiter, using the correct preceding tokens as context.

For each token, the cap can take up to five rounds:

1. Compute the current prediction and its loss.
2. Compute a proposed correction direction for the relevant banks.
3. For C2, temporarily try a small correction at each bank. Choose the largest meaningful loss reduction; abstain if none helps.
4. Try four bounded correction sizes at each scheduled bank, evaluating actual retrieval and predictions. Retain the best only if it meaningfully improves the loss.
5. Commit the associated memory changes, or restore the complete previous state if the candidate fails.

The default total normalized write budget is 0.1 per round, the routing probe size is 0.01, and token training stops early at a loss of 0.1 nats. Development may select among the specified step-budget candidates before testing begins.

A useful temporary probe does not guarantee a useful stored edit: creating slots or changing which slot fires can alter the result. The final stored candidate must be tested too. Improvement on the current training token also does not guarantee safety on other inputs.

Memory handling follows explicit rules:

- Stored keys remain fixed, although the input features used to query them can move after upstream learning.
- For different keys with conflicting target tokens, shrink the matching regions and try a separate entry while preserving the old key and value.
- Identical keys requiring incompatible targets cannot be separated by shrinking their radii. Reject and log the ambiguity unless this is an explicitly identified newer revision in the correction test.
- When a bank fills, evict the least-used slot, with deterministic tie-breaking.
- A rejected candidate rolls back everything, including eviction, radii, metadata, and random state.
- Prediction and evaluation do not update memory or usage statistics.

The appendix requires known-answer tests for these rules, cap-off identity, cloning, budgets, full-answer scoring, query-label isolation, and adapted baselines. A router choosing poorly is a scientific result once correctness controls pass.

## 6. The Three Test Beds

| Test | What it contains | What it can establish |
| --- | --- | --- |
| Constructed modular control | Deliberately separated private mechanisms and explicitly shared mechanisms, with restricted write paths | Whether correct routing can help in an identifiable case and whether the measurement machinery works. |
| Learned synthetic grammar | A six-layer transformer, eight observable task contexts, two shared switches, and one private switch per context | Whether routing preserves private rules and useful sharing in a learned model. |
| Factual answer editing | Separate zsRE and CounterFact streams with full answers, paraphrases, and nearby unrelated questions | Whether the approach works on language-model editing. |

The constructed oracle must recover at least 95% of planted attainable targets while preserving unrelated outputs within the specified numerical tolerance. That does not imply an unrestricted transformer has equally cleanly separated mechanisms.

On the learned grammar, corruption-and-restoration experiments probe which layers help recover an answer. Several layers may qualify, or none may qualify. These measurements do not uniquely locate a mechanism's origin.

The maximum editing lengths are 3,000 zsRE edits and 1,000 CounterFact edits per realization. Actual lengths are selected from fixed options using development throughput, with 25% budget headroom.

Evaluation uses greedy generation of the **whole answer**, under a shared normalization and stopping policy, with up to 32 new tokens. Getting only the first token right is failure. The reference implementation recomputes each full prefix without a key/value cache so all arms share the same semantics.

Separate challenge sets test nearby questions needing different answers, combinations of learned relations, and explicit corrections. In the correction track, the latest valid answer replaces the old one. Such intentionally ordered revisions are excluded from claims that learning order should not matter.

Practical baselines include the frozen model, sequential LoRA, LoRA with bounded replay, and GRACE. LoRA learns small parameter changes; replay revisits a limited sample of earlier examples; GRACE is a published correction-memory method. LoRA with EWC and WISE are optional. Adaptations must be checked against their reference implementations before comparative claims are made.

## 7. What Gets Measured?

### Learning and Preservation

| Measure | Question it answers |
| --- | --- |
| Immediate efficacy, ES | Can the model generate the new answer immediately after the edit? |
| Generalization, GS | Can it answer held-out rephrasings? |
| Retained ES and GS | Can it still do so after later edits? |
| Locality, LS | Do unrelated prompts still get the uncapped model's answer? |
| Forward transfer | Did earlier learning improve a task before it was trained? |
| Backward transfer | Did later learning help or hurt an earlier task? |
| Forgetting | How much did a task decline from its best observed performance? |
| Late acquisition | Can the system still learn new items late in the stream? |
| Language-model drift | How much did performance change on ordinary held-out text? |
| Resources | How much persistent memory, learning time, and prediction time did it use? |

Locality measures agreement with the base, which is not necessarily factual correctness. Retention is reported both overall and conditional on having learned the item initially.

### Direct Interference and Learning Order

Clone the same complete learner state. In one copy, learn A then B; in the other, learn B then A. Compare individual predictions, losses, allocations, and evictions on the edits, their paraphrases, and unrelated controls.

This exposes differences hidden by average accuracy. Also measure whether learning B helps or harms A, distinguishing shared-mechanism pairs from independent private pairs.

Optional Hessian analysis examines local mathematical interactions with keys, gates, and memory structure held fixed. It does not describe the full discrete update process. In particular, commuting Hessians do not guarantee order-independent learning; the gradients matter too. These diagnostics cannot replace behavioral evidence.

### The Base Model's Report Card

Before drawing ePC conclusions, measure six properties:

1. **Fidelity:** Does the conversion preserve the teacher's predictions? Matched-fidelity claims require mean token-distribution KL no greater than 0.001 nats in both specified checks, plus reporting of tails and edit-prompt disagreements.
2. **Geometry:** Has useful internal variation or linearly readable information collapsed?
3. **Localization:** Is each example's error concentrated, while useful error signals still reach different layers across the dataset?
4. **Structure:** Are private mechanisms distinguishable, and is useful shared structure preserved?
5. **Write locality:** How much does a correction help its target and disturb other inputs, both when forced and under actual retrieval gates?
6. **Cost and informativeness:** What does error inference cost, how close is it to convergence, and how does error magnitude relate to loss?

Geometry and concentration thresholds are diagnostic alerts, not automatic reasons to exclude an inconvenient model. Shared features can enable transfer. With only a few checkpoints, correlations between report-card scores and cap performance remain descriptive.

## 8. What Would Count as a Positive Routing Result?

The primary editing outcome is **retained accuracy on paraphrases at the end of the stream**, or endpoint RET-GS.

A positive primary finding requires C2 to satisfy the following against **both C1 and CR**:

- RET-GS improves by at least 2 percentage points, with the lower uncertainty bound above zero.
- Immediate ES is no more than 2 percentage points worse.
- Locality LS is no more than 1 percentage point worse.

The acquisition and locality constraints also need supporting uncertainty bounds. Favorable averages with unresolved constraints produce a qualified result. Claims about comparable compute need their own resource evidence.

Reduced private-mechanism damage, beneficial shared transfer, and reduced harmful order effects support the explanation of why routing works. Correct bank selection on the constructed fixture targets precision and recall of 0.8; below 0.6 is poor agreement. These bands describe scientific performance, not code correctness.

Core comparisons use three independently sampled stream realizations and five orders of each, paired across arms. Uncertainty uses paired resampling of realizations, keeping their orders together, with 10,000 bootstrap draws and 97.5% two-sided intervals for the two primary contrasts. Three realizations provide limited evidence about broader populations; the 15 runs are not 15 independent datasets or base models.

## 9. Fair Memory and Compute Accounting

The common cap-memory reference is `6144 * (8d + 128)` bytes, where `d` is hidden-state width. At width 768, this is about **36.75 MiB**. Actual keys, values, metadata, alignment, caches, and indices count. Replay and optimizer state are also reported for relevant baselines.

Report two distinct comparisons:

- **Same exposure:** Every arm processes the same complete items; actual cost may differ.
- **Same resources:** Every arm gets the same measured accelerator-time ceiling. Compare the longest common completed prefix, and show performance against time and completed items.

A partly completed item is rolled back for endpoint evaluation, but its consumed time still counts. Probes, rejected searches, backward calculations, settling, replay, and additional key computations all count. Learning and prediction costs are reported separately.

For a joint comparable-compute claim, measured update times must be within 20%, or the equal-resource comparison must support the claim.

## 10. The Month's Schedule

The total budget is **154 A100-equivalent hours**, calibrated to the available hardware. These are spending ceilings, not runtime predictions.

| Stage | Main work | Hours |
| --- | --- | ---: |
| S0 | Locate and verify assets; build the shared harness and correctness controls. | 8 |
| S1 | Measure the existing bases and their learning signals. | 12 |
| S2 | Calibrate settings, validate baselines, and profile 100-300 edits. | 12 |
| S3 | Screen routing on development fixtures and short BP streams. | 16 |
| S4 | Freeze the protocol, then run the main BP comparisons. | 36 |
| S5 | Compare BP, ePC with gradients, and ePC with error credit. | 24 |
| S6 | Optionally test one targeted re-distillation intervention. | 20 |
| S7 | Measure direct order effects and selected optional diagnostics. | 10 |
| S8 | Finish replications, selected ablations, audits, and the report. | 16 |

Week 1 establishes correctness and feasibility. Week 2 screens mechanisms and freezes the final protocol. Week 3 runs confirmation. Week 4 verifies and reports results, preserving two working days for overruns.

S6 happens only after identifying a specific reproducible deficit and reserving enough budget for both a plain continuation and a regularized continuation. Both start from the same checkpoint and use the same training data and schedule.

One allowed intervention concentrates individual error fields while maintaining coverage across layers. The other reduces overlap between explicitly unrelated private mechanisms while preserving supplied shared structure. Broadly forcing all domains apart could destroy useful transfer and is not the default. The intervention must actually affect training gradients.

Optional error-key, regularization, and Hessian experiments are dropped before sacrificing complete paired core comparisons. A second cap level, broader domain adaptation, and the eventual multilevel architecture remain future work.

## 11. Rules That Make the Result Trustworthy

Development and confirmation use separate data. Before confirmation, a machine-readable manifest fixes configurations, data identities, seeds, stream lengths, comparisons, thresholds, stopping rules, and analysis code. The final data cannot be used to tune those choices.

All compared arms share evaluation rules and data order. Code, environment, checkpoint, and configuration versions are recorded. Runs save decisions, metrics, costs, and resumable learner states. The proposed `pccap` package provides base wrappers, memory banks, routers, transactional updates, cloning, serialization, fixtures, and the common harness; missing required frozen settings must make a run fail explicitly.

A failed control stops the affected mechanism for diagnosis. A demonstrated bug can be repaired and versioned; affected paired comparisons must then be rerun or marked incomplete. A correct implementation producing disappointing results is not automatically a bug. Neither scientific thresholds nor the primary outcome can be changed to manufacture success.

Failures must distinguish implementation defects, resource limits, unmet assumptions, and valid negative findings. Undefined measurements and unsupported evaluations are reported explicitly. Failed attempts, abstentions, ambiguous items, exclusions, and incomplete comparisons remain visible. Extra seeds are not added just to cross a significance threshold.

## 12. What Must Exist at the End?

The guaranteed deliverable is **one reproducible integrated report** containing the base report card, controlled routing and credit comparisons, retention and locality results, transfer and order effects, memory and timing tradeoffs, uncertainty, and all important failures and deviations.

Supporting materials include source, pinned dependencies, checkpoint and dataset provenance, manifests, reproduction commands, and baseline adaptations, released where licensing permits. Each stage report records its status, controls, completed scope, costs, findings, interpretation limits, and remaining work.

A separate paper follows only if the evidence supports it. The month succeeds by producing a clear, valid answer within its tested scope, including a negative or inconclusive answer. It does not promise that measured routing or ePC will win.
