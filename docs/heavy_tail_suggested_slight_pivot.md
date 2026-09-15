# Suggested slight pivot: rare-event harm and recovery on a frozen transformer

Prepared for **Charlie Derr and Matthew Iklé**, September 15, 2026. **Experiments must finish by October 9, 2026.** October 10–14 is reserved for analysis of locked results, figures, slides and rehearsal; the presentation is October 15. This is a proposal for discussion with Charlie and Claude, not an amendment to the registered experiments or authorization to launch additional runs.

**Recommendation.** Keep the current frozen-base cap experiments as the main scientific contribution. Add a small, explicit evaluation of **how damage is distributed, what happens when difficult requests cluster, and whether the system recovers while retaining useful corrections**. This connects the work directly to the satellite without requiring a new architecture. A genuine κ-coupled objective should be a separately gated, optional pilot; distinguish the working system from that longer-term theoretical programme.

The minimum useful change is threefold: preserve granular results already computed by the driver; report rare harm alongside average performance; and run a tightly bounded, matched stress test only if the main experiments fit the October 9 deadline. This can produce a strong presentation even if a new κ treatment is not ready.

**The presentation brief and what the audience will expect**

I read both files in [presentation_details](../../errata/presentation_details/): the three-page [July abstract](../../errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf), including its two-interface diagram and references, and the [supplied schedule](../../errata/presentation_details/sattellite-schedule). The [Photrek page](https://www.photrek.io/thriving-extremes-css2026) confirms the session and lists your joint talk within Session 3, 2:45–4:15 p.m.; it does not specify your individual speaking duration. The [conference programme](https://ccs26.cssociety.org/program.html) places the October 15 satellite in Lecture Hall 7. These scheduling sources were checked September 15; your October 9 experimental cutoff governs this proposal.

Your abstract promises a frozen transformer with a much smaller adaptive residual system, auditable interference, robustness under extreme and changing conditions, a κ-coupled free energy, and action selection balancing preferred outcomes against information gain. Its most ambitious conjecture is that one κ controls tail behaviour, boundary porosity and forgetting geometry together.

The satellite's themes give the talk a useful progression: predictive coding foundations; non-equilibrium and socioeconomic dynamics; coupled inference; and a final project-planning discussion. Our contribution can be the experimentally concrete link: **what an adaptive correction boundary must get right before claims about resilience under heavy-tailed conditions become credible**. Bring measured failures, controls and operational definitions to that discussion.

**Where the abstract and the implementation currently meet**

Repository evidence was reviewed through owner commit **3f1f242**. [Plan 9](updated_plan9.md), [protocol v4](R1_stage4_protocol_draft_v4.md), the [Stage 2 report](R1_stage2_report.md), [current notes](R1_stage2_notes.md) and [R1-X11 review](../logs/review_r1_65_66.md) are the main local sources. The notes and versioned result identities qualify earlier reports.

| Abstract idea | Current evidence | Wording and next step |
| --- | --- | --- |
| Frozen generative prior plus small adaptive residual system | The JAX GPT-2-small base is fixed; reusable reader/controller weights are fixed during evaluation; support updates alter bounded episodic state and additive writes | Present a small-scale mechanistic testbed. The current substrate is GPT-2 small, not a frontier-scale model. Report actual parameter counts and bytes rather than inheriting “orders of magnitude” from the abstract. |
| Auditable, reversible corrections | Explicit null decisions, state hashes, bounded writes, isolated endpoint restores and record supersession | Make these central results. Transactional rollback establishes engineering reversibility; it is not evidence of thermodynamic reversibility or automatic recovery after every behavioural failure. |
| Learning a residual R = F* − F0 | Learned writes improve prescribed answer targets while preservation losses penalize unwanted changes | F* is not observed as a complete desired hidden-state function. Explain the support-target approximation; do not portray the abstract's complete residual variational model as implemented. |
| Active inference / expected-free-energy policies | Current learning uses answer NLL, retrieval/null cross-entropy and preservation KL; deployment uses learned selection and hard gates | This is not yet a demonstrated expected-free-energy planner. Separate the predictive-coding lineage, present implementation and proposed active-inference extension. |
| κ-coupled free energy and heavy-tailed residuals | No such objective is established by the inspected revision-v1 loss/selection implementation; no empirical tail-family result is established | Add explicit tail measurements now. A new objective requires a separately specified likelihood, inference distribution, normalization and controlled experiment. |
| Two Markov blankets | There are useful software interfaces from environment to cap and from cap to frozen base | Use the diagram as a proposed architectural interpretation. Conditional independence or a coupled replacement has not been established merely by having two APIs. |
| Interference as geometric invariant | v0 includes direct order-reversal and damage measurements; revision-v1 has shared retrieval, gates and episodic memory | Reuse those measurements as operational interference evidence. A holonomy invariant needs a defined connection, loops and invariance tests. |
| Epistemic value of entering failure regimes | The project has already learned from failures, and its audit machinery can inspect conflicting cases | Investigator-driven audits are not yet an agent choosing costly actions for expected information gain. An active audit policy is a later, separately tested mechanism. |

These distinctions strengthen the abstract's experimental status. A non-Gaussian predictive-coding formulation is possible in principle; [Pinchetti et al.](https://papers.nips.cc/paper_files/paper/2022/hash/08f9de0232c0b485110237f6e6cf88f1-Abstract-Conference.html) explicitly generalize PC beyond Gaussian distributions. That literature does not imply that our existing categorical losses implement coupled free energy. Likewise, formal active inference includes beliefs, preferences and policy inference beyond a retrieval threshold; [Da Costa et al.](https://arxiv.org/abs/2001.07203) is an appropriate reference for specifying those missing pieces.

Treat the session's broad claims about non-equilibrium destroying Markov blankets as its motivating theoretical position, not as something our experiments already prove. Temporal change, long-range dependence, tail shape, conditional independence and forgetting are distinct properties. In particular, κ = 0 need not imply zero interference in a shared adaptive memory. A gate threshold is not automatically κ, and uncertainty precision is not automatically the cost assigned to an error.

**An immediate result that makes the pivot worthwhile**

There is already a striking illustration in the completed historical-v4 zsRE development profile after 300 edits. I recomputed the following directly from its saved [checkpoint report](../results/R1/stage4_dev_cells/R1_learned_ff-zsre-development_profile-source-8a5edf8cea14e816ace0/attempt-0000/checkpoint-300.json), with no model execution.

Let Δ be cap NLL minus original-base NLL on the same next token and prefix; positive Δ is harm. Let H = max(Δ, 0).

| Quantity | Recomputed value |
| --- | ---: |
| Scored next-token positions / windows | 16,256 / 128 |
| Mean signed Δ | +0.000233148 nats |
| Mean H | 0.000234574 nats |
| Largest Δ | +3.789635 nats |
| Location of that position | w125:p26 |
| Original-base / cap NLL there | 11.473859 / 15.263495 |
| Second-largest Δ | 0.0000245866 nats |
| Positions with Δ > 0.01 nats | 1 / 16,256 |
| Largest position's share of summed positive H | 99.3813% |

At that position, the cap assigns the observed token about **44.24 times less probability** than the original base. That is a next-token likelihood comparison, not a statement that an answer or a deployed application became 44 times more dangerous. Tiny differences elsewhere need a matched numerical-control tolerance before being counted as meaningful events.

This supports the narrow statement **“a nearly unchanged average can coexist with one large local deterioration.”** It does not establish a heavy-tailed population, a power law, a practical catastrophe, or the cause of this deterioration. Have Claude verify the saved example using the exact checkpoint, numerical reference and selection trace before making it a headline result. Keep it as exploratory historical-v4 evidence and repeat the analysis on the final reader; do not promote or reject readers using this already-inspected example.

The checkpoint SHA-256 is `1b015feeb2ad8e1c8d487cfcf2de47a5c79b1410673288f24abd8638cb51802f`. The relevant rows are at `endpoints.drift.rows`; calculate each row's `cap - original`. Their existing granularity makes this an inexpensive starting point.

The retention/rejection tradeoff is another useful result. The [paired recent development evidence](../logs/r1_round13/training_review_evidence.json) gives:

| Reader | zsRE / CounterFact / MQuAKE RET-GS | Equal-dataset mean | zsRE outside fires, 100 actual records | Minimum reported LS |
| --- | --- | ---: | ---: | ---: |
| Fixed-locality tri4, seed 0 | .98 / .86 / .79 | .8767 | 30/100 | .98 |
| Fixed-locality tri4, seed 2 | .98 / .86 / .79 | .8767 | 52/100 | .98 |
| Full question-null tri5, seed 0 | .91 / .81 / .55 | .7567 | 5/100 | .98 |

RET-GS assesses all 100 attempted-edit items at the endpoint in each dataset; LS uses 50 queries. This is a concrete boundary tradeoff: stronger rejection can sacrifice useful generalization. It is not a κ experiment. Same training seed does not make training trajectories paired. Historical v4 and these newer MQuAKE streams share only 47/100 items, so final candidate comparison still needs common populations. Tri6 and the final primary selection were not complete in the reviewed records.

**Recommended experiment changes, ordered by value and deadline risk**

| Priority | Addition | Why it fits this talk | Scope limit |
| --- | --- | --- | --- |
| 1 — do first | Distributional audit of existing per-position/per-item results | Makes extremes and average-versus-tail tradeoffs measurable using current experiments | CPU analysis first; no retraining or new data source |
| 2 — modest extension | Matched shuffled versus clustered development streams | Tests temporal concentration and recovery with the same support facts | A small, separately labelled stress panel; no expansion of every core matrix axis |
| 3 — if affordable | Paired interference probes from identical snapshots | Connects the “value of failing” and modularity ideas to measured forgetting | Reuse the existing S7 design; a fixed small development inventory |
| 4 — conditional | One mathematically specified κ pilot | Directly tests part of the coupled-objective claim | Only after an objective review, CPU gates and a measured budget; never a prerequisite for a defensible talk |
| Later project | Expected-free-energy audit policy and coupled-blanket theory | Connects to the final satellite planning session | Do not make October delivery depend on a new full agent architecture |

**Priority 1: a distributional audit with little extra model work**

The [current driver assay](../src/pccap/revision_v1/stage4_assays.py) already saves per-position original, cap-off and cap NLL for drift. Older aggregate-only drift summaries cannot be decomposed after the fact: mark those quantities unavailable unless a separately budgeted replay supplies them. Preserve useful granular outputs in the upcoming runs before optimizing their storage.

For each fixed population, report mean signed harm, mean positive harm, median, 95th and 99th percentiles, empirical worst-5% mean harm, maximum, exceedance counts at predeclared thresholds, and the fraction of total positive harm contributed by the worst 1% of observations. This profile illustrates why percentiles alone can also miss an extremely sparse event. Always print the numerator, denominator, atom at zero and number of distinct windows/facts.

A precise empirical expected-shortfall definition is:

```text
H_i = max(0, NLL_cap(i) - NLL_reference(i))
ES_95 = min_eta [eta + (1 / (0.05 * n)) * sum_i max(H_i - eta, 0)]
```

This handles ties and a nonintegral 5% tail mass. Report “empirical worst-tail mean” rather than implying that a finite-sample statistic certifies an unobserved catastrophic-risk bound. Numerical nonfinite values are explicit failures, not rows to discard. This operational tail-risk statistic is not the expected-free-energy preference-divergence term simply because both are called risk. Keep legitimate new-answer learning loss separate from preservation harm; a counterfactual target is meant to disagree with the original base.

Define “extreme” along separate, interpretable axes:

| Axis | Proposed measurement | Important distinction |
| --- | --- | --- |
| Difficult input | Original-base NLL, prompt/answer length, development-defined rare relation or subject-frequency strata | Teacher-selected counterfactual edit pools condition on base error; they do not estimate natural deployment frequency |
| Rare harmful consequence | Positive preservation-NLL change, unintended answer change, severe forgetting | Rare input and severe outcome are different labels |
| Temporal concentration | Length and clustering of difficult-request blocks, harm runs and recovery lag | A burst is not itself proof of a heavy-tailed marginal distribution |
| Memory pressure | Attempted edits, active occupancy and bytes at 100/300/1,000 | Fixed query identities are needed to attribute differences to scale |
| Boundary failure | Hard-gate acceptance on an outside query; target rejection on an applicable query | Gate acceptance, nonzero writes and changed answers must remain separate |

Freeze bins and primary tail summaries on development data before applying them to fresh data. If the main protocol is already frozen by implementation time, record a separate exploratory analysis addendum rather than silently replacing its endpoints or primary contrasts. Preserve the current reader-selection criterion: mean development RET-GS subject to zsRE outside firing ≤10% at 100 records and LS ≥.98. Tail diagnostics do not authorize a new hidden selection rule.

Inference needs the right units. Positions within one text window are dependent; windows reused across conditions must be paired. Five orders from one edit realization are not five independent datasets. For confirmatory comparisons, retain the existing realization-level grouping; supplementary window/block resampling describes uncertainty conditional on those sampled streams. Three realizations give limited population-level tail inference. Report single-realization diagnostics descriptively.

A reader firing on 5/100 outside queries is an observed 5% rate, not a statistically established population upper bound below 10%. Its apparent success under the existing point-estimate selection rule should not become a stronger reliability claim on a slide.

Do not fit a straight line to a log-log plot and call the errors power-law distributed. If enough independent tail observations exist, compare plausible distributions with suitable estimation, goodness-of-fit and alternative-model checks; otherwise report concentration and exceedances without a tail-family claim. This follows the methodological caution of [Clauset, Shalizi and Newman](https://arxiv.org/abs/0706.1062). One large token loss is particularly insufficient. Binary exact-match outcomes and clipped measurements cannot identify an asymptotic heavy-tail exponent.

**Priority 2: a small non-stationary stress panel**

Use existing permitted development facts and queries. Compare two schedules with **identical marginal items and counts**:

1. A shuffled reference schedule.
2. A schedule that clusters a predetermined difficult/confusable relation family, then returns to a mixture containing the earlier families.

Choose families from metadata or original-base development difficulty, before seeing the tested reader's outcomes. Keep target answers, paraphrases, query probes, number of updates, decoding, memory ceiling and seeds paired. Reorder edit presentations; do not quietly inject corrupt labels. Where memory is not full, a correct cap may simply retain earlier facts; this is an informative result rather than a reason to invent pressure after inspecting the outcome.

Measure immediately before the block, at its end and after a fixed number of subsequent updates: old-fact retention, new-fact acquisition, outside rejection, tail preservation harm and recovery lag. Recovery means return to a preregistered performance band on a fixed old-fact probe set, not just recovery on the newest examples. If the band is not reached by the end, report censored recovery time rather than dropping the run.

A practical exploratory first panel is **2 completed, identity-bound reader candidates × 2 schedules × 3 datasets × 100 edits = 12 development cells**, with one predeclared seed. Use the original base as the paired preservation reference. Start with a two-cell timing/validity pilot; propose a **4 GPU-hour ceiling for the entire panel**, including its assays. This is a requested cap, not a runtime estimate or an authorization. If the pilot cannot fit the panel inside that ceiling and the core schedule, omit the extension or seek an explicit scope decision.

Do not add these schedules to all 360 cells automatically. The first panel tests clustered sequence effects; it does not simulate a socioeconomic system or establish long-range dependence. A majority-vote simulator is a good collaboration topic for Session 4, but building and validating one now would turn the slight pivot into another project.

**Priority 3: make interference observable without overclaiming geometry**

The historical [v0 report](report.md), section 7, already describes paired update reversals. It found positive zsRE near-neighbour damage and also conditions with zero measured answer damage despite different endpoint states. This supports the abstract's point that the probe population matters, while showing why “no observed forgetting” does not prove that updates commute.

For a bounded revision-v1 follow-up, start each pair from the same complete snapshot and execute A→B and B→A. Predeclare mutually consistent support pairs in operational shared-relation, unrelated and near-neighbour strata. Probe both taught facts, paraphrases and a fixed unaffected set. Record signed cross-damage in each direction, endpoint answer divergence, state difference and the selection changes that accompany them. Keep deliberately conflicting revisions separate: latest-valid-answer semantics legitimately depend on order.

A simple behavioural quantity is `D(A→B) = NLL_on_A(after A then B) - NLL_on_A(after A)`. Positive values mean damage to A after learning B. Use new-answer targets for edited facts. Report both directions and per-stratum denominators; never substitute a count of directions for a count of pairs.

Keep a fixed random panel in addition to an uncertainty/conflict-enriched panel, or the audit itself will change the apparent prevalence of interference. Describe the latter as targeted discovery. Freeze discovery versus evaluation roles. These measurements can motivate where modular boundaries should be studied; they do not yet demonstrate a transferable curvature or holonomy invariant. Do not reopen v0's frozen conclusions.

**Priority 4: the smallest defensible route to an actual κ result**

Make the decision to attempt this **by September 20**, based on a written objective that Charlie and Matthew can defend and Claude can implement. If it is not ready, keep κ as a clearly stated hypothesis and use the empirical boundary/risk results above. A last-minute renamed loss would weaken the presentation.

The [Nelson et al. CFE paper, v3](https://arxiv.org/html/2506.09091v3) couples distributional assumptions with the objective and a modified sampling/expectation rule. A Student-t likelihood by itself is not that entire construction. Pin the exact paper version and parameter convention; [Nelson's coupled-entropy account](https://arxiv.org/abs/2506.17229v3) is a useful companion reference. Do not transfer claims about finite generalized moments into a claim that every ordinary raw moment is finite.

The pilot must specify the observed continuous residual or latent variable, its units and scale, the generative density and prior, the inference distribution, the coupled divergence/expectation, normalization and the κ→0 limit. F* cannot be supplied by held-out answers at inference. The existing answer and retrieval losses are categorical: they are not Gaussian residual losses merely because earlier predictive-coding literature used Gaussians.

First establish the κ=0 reference and a small positive κ on a CPU fixture with known generating assumptions. Separate changing scale from changing shape. If a finite-κ pilot goes to the real base, hold the base, writes, gate, data, training budget and evaluation population fixed. Include an ordinary robust-loss comparator so an improvement is not automatically attributed to the distinctive coupled construction.

This distinction matters operationally. A Student-t robust location loss, for example, has a residual-dependent precision proportional to `(nu + 1) / (nu * scale^2 + residual^2)`. It reduces the influence of a very large residual. That can help with corrupted observations yet suppress learning from a legitimate regime change. “Ignore outliers” and “learn the changed world” are competing behaviours; test and label them separately. This formula is an illustrative robust-loss control, not the proposed CFE objective.

Keep κ and the gate threshold as separate axes unless a derivation links them. The abstract's one-κ conjecture needs evidence that κ changes both interference and tail risk under controlled conditions, and eventually tests against independently varied boundary parameters. An interior optimum in an arbitrary threshold sweep would not prove that conjecture.

Suggested stop gate: at most **4 additional GPU hours** after CPU validation and only if core experiments retain their reserve. Register the roster and stop condition in advance. A verified null or adverse result is useful; repeated tuning until a Goldilocks-shaped curve appears is not. Do not attempt both a new CFE learner and a new expected-free-energy planner before October 9.

**An active-inference direction for the discussion, rather than a rushed requirement**

The smallest later policy problem would offer three actions: apply a correction, retain the prior's answer, or request a costly audit/support observation. Specify a belief over applicability or environmental regime, observable audit outcomes, preferences over wrong changes/missed corrections/cost, and how an audit updates that belief. Compare a policy with information gain against a risk-only policy and random audits at matched audit budgets.

Any benefit should be measured on future decisions, not on the queried labels alone. This would operationalize the abstract's “value of failing” claim. Entropy-triggered auditing without a model of expected information gain should be described as an uncertainty heuristic. This is a concrete project-planning proposal to bring to the satellite, not a mechanism already demonstrated by our current routing code.

**How this fits the work with Claude**

The current [ongoing task list](ongoing.md) puts the incremental driver, v5 draw plan and freeze candidate on the critical path. R1-67 loader/trace wiring has now been committed by Claude; the next opportunity is to preserve useful tail-observation fields before the final execution identity is frozen.

| Parallel work stream | Suggested responsibility | Deliverable and dependency |
| --- | --- | --- |
| Core driver, common-population selection and scheduled GPU runs | Claude | Complete R1-68b, truthful timers, restore/resume and model identity; retain existing experiment priorities |
| Existing-result tail audit | Codex / CPU | New audit script and report with input hashes, per-window/per-item summaries and missing-data inventory; can start without the GPU |
| Stress design and analysis contract | Codex drafts; Charlie approves; Claude executes | New schedule/measurement manifest, fixed populations and independent probes; depends on candidate receipts and measured capacity |
| κ definition and abstract claim review | Charlie and Matthew, with a targeted technical review if useful | Exact objective or an explicit deferral by September 20; no inference that a consultation has already occurred |
| Execution budget and evidence cutoff | Charlie with both agents' measured reports | A feasible calendar by September 20; no new experimental work after October 9 |
| Figures and talk narrative | Charlie with CPU/report support | Source-bound figures, claim/evidence ledger and rehearsed explanation during October 10–14 |

Possible new files, if this direction is adopted: `scripts/ht_audit_existing.py`, `scripts/ht_build_dev_schedules.py`, `docs/tasks/HT-evaluation-contract.md`, `manifests/revision_v1/ht_development_panel_v1.json` and `logs/heavy_tail/`. These are proposed outputs, not files created by this memo.

Any required edits to driver, assay, loss or task-board files need the standing permission/ownership process. Whole-tree code hashes must be rebound before a new admitted run. Do not change source during an active job that verifies it. Keep sibling repositories read-only, use JAX and the designated venv, put data/checkpoints in assets, and run GPU jobs serially while the recent machine hangs are investigated.

Two population details deserve explicit attention before final scheduling. MQuAKE's v5 capacity is **4,218 subjects against 4,050 demand**, leaving 168 before alias/context/role clearance; losing 169 aborts. A new stress panel must use already permitted development data rather than silently consume that remainder. Also, the round-14 R1-58b shorthand writes 1,000+100+100+50 per realization, whereas protocol v4 separately reserves 100 near supports and 100 near neighbours, yielding 1,350 and total 4,050. Reconcile that shorthand before the dry-run report; do not accidentally replace the accepted demand by 3,750.

**A schedule that ends experiments on October 9**

There are **24 calendar days from September 15 to October 9**, not 30 experimental days until the talk. The following dates are proposed work gates; October 9 is Charlie's hard constraint.

| Date | Required state |
| --- | --- |
| September 15–17 | Audit stored tail observations; agree claim boundaries; inventory missing per-item outputs; complete a driver timing/restore check |
| September 18–20 | Bind common-population primary selection and analysis; resolve clearance/demand; decide whether stress/κ additions fit; record the feasible GPU schedule |
| September 21–October 3 | Execute admitted core work in balanced blocks; run only approved, budgeted extensions; inspect operational failures without tuning to fresh test outcomes |
| October 4–7 | Complete the planned experimental inventory, replications and predefined diagnostic checks; stop introducing new hypotheses or treatments |
| October 8–9 | Reserved reruns of failed/incomplete work and validation; **all model-dependent experiments and diagnostic replays finish by October 9** |
| October 10–12 | Work from locked data: analysis, final figures, limitations and slides; an issue requiring a new model rerun becomes an exclusion/limitation rather than reopening experiments |
| October 13–14 | Coauthor review and rehearsal; figures/data identities remain fixed |
| October 15 | Present completed evidence and a bounded research agenda |

There is a real feasibility issue. The current learned-cell extrapolation of 49–66 minutes gives roughly **294–396 GPU hours for 360 homogeneous cells**, or **353–475 hours with 20% reserve**. Other conditions are not yet equally profiled; full-validation assays, initialization, remaining training and failures add costs. The 45-cell extension is additional. These are planning scenarios, not measured costs for the full matrix.

For illustration, September 21 through the start of October 8 gives 408 wall-clock hours. At an assumed 75% usable GPU availability, that is **306 hours**. With 20% reserve, the 360-cell average would have to be **at most 42.5 minutes even before other required work is charged**. Reserving the proposed 8 hours for both optional extensions lowers that ceiling further, to about 41.4 minutes. Thus the present 49–66-minute proxy does not establish that the October 9 programme fits. Do not budget an unmeasured R1-68b speedup as if it exists.

By September 20, compare measured per-condition costs with actual available hours. If the schedule does not fit, Charlie needs an explicit choice among validated acceleration, additional execution capacity, or a documented scope amendment. The standing full-scope decision must not be silently overridden by this memo. Prioritize omitting optional new work before changing the accepted core. If a hard stop still leaves incomplete experiments, report them as incomplete; neither extend experimentation into October 10–14 nor present a partial matrix as complete.

Execute comparable condition/dataset blocks together so an interruption does not leave only the favourable conditions evaluated. Schedule the slowest unprofiled comparator early enough to expose an unrealistic estimate. Maintain a running spend/remaining-work table, including failed work and recovery from the recent hard machine hangs. Machine hangs are operational failures and censoring, not evidence that the model itself collapsed under a heavy-tailed environment.

**What to show on October 15**

Keep most of the talk on experiments. A useful allocation, adjusted to the actual speaking slot, is roughly 20% motivation/architecture, 55% completed results and 25% interpretation, limits and the next collaboration.

| Figure or table | Message | Evidence needed by October 9 |
| --- | --- | --- |
| Two-panel boundary diagram | Proposed active-inference/CFE architecture beside the implemented frozen-base reader, memory and writes | Explicit implemented/proposed labels; correct GPT-2-small substrate |
| Retention versus unintended intervention | Useful correction and selective rejection can trade off | Common-population points with denominators and exact candidate identities |
| Mean versus local harm | Aggregate preservation can hide sparse large changes | Per-position/window loss deltas, zero mass and numerical controls; the saved v4 example is an exploratory illustration |
| Recovery curve | Whether a cluster of difficult updates leaves persistent damage | Matched schedules and fixed old-fact probes; omit if the bounded panel is not completed |
| Interference heatmap | Where updates help, harm or reveal no measurable effect | Fixed pair panel, both directions, consistent supports and operational family labels |
| Small κ panel, only if valid | What a specified coupled treatment actually changes | Matched controls and complete results; otherwise a clearly marked proposed experiment |

A defensible opening is: “We are testing a small adaptive memory on a frozen transformer as a controlled substrate for the coupled active-inference programme. Today I will show what it preserves, where it intervenes incorrectly, and why average performance is not enough to evaluate that boundary.”

A defensible result statement is: “In one development profile, almost all of the positive likelihood damage was concentrated in a single token position, despite a tiny average drift. This motivates a distributional audit; it does not establish a power law.”

The discussion question for the satellite is then precise: **can a correctly specified coupled objective improve the correction-versus-tail-harm tradeoff under correlated regime changes, beyond ordinary robust losses and better rejection training?** That keeps the spirit of the July abstract while making the October evidence concrete.

**Provenance and limits of this memo**

The abstract SHA-256 is `bb9bb99c196c0392f790223096bef92627d5ea7cad09e349e84f2b5004db6f01`; the supplied schedule SHA-256 is `39b90570144a38a34bdae07cb17c6cc403d0b41f4e7da82dc8d1c6ec03bfa3e3`. Online scheduling and theoretical references are linked at the relevant claims. The abstract was read in full and its first-page diagram inspected. Reference-list inclusion in the abstract is not treated as validation of every theory claim; this memo does not review all fourteen cited works.

The only new numerical analysis here is a CPU recount of the already-saved development drift rows, explicitly identified above. Existing protocol, result and source files were not edited; no training, GPU inference, draw, seal, experiment, message to collaborators or commit was performed for this memo. All additional experiments, treatments and deadlines except Charlie's October 9 hard stop remain suggestions.
