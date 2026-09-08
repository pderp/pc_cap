# Counter-review of Week 1 Plan (v1)

Date: 8 September 2026. This is a document review and proposed revision, not a report of completed experiments or an authorization to execute the research programme.

**Recommendation: retain the experimental design, but revise the execution gates and feasibility commitments before treating week1plan1 as an executable schedule.** The plan preserves the important controlled comparisons. Its main weaknesses are inconsistent completion criteria, missing implementation details that affect those comparisons, and a Monday workload whose feasibility has not been established.

Documents read in full for this response:

| Document | Role in this review |
| --- | --- |
| [week1plan1.md](week1plan1.md) | Primary response target; references below use its section numbers and task IDs. |
| [review_plan1.md](review_plan1.md) | Contains only the heading `Critical Review of week1plan1.md`. There are no substantive review claims to accept or rebut. This counter-review does not invent any. |
| [pc_cap_month_plan_readable.pdf](pc_cap_month_plan_readable.pdf) | Full 37-page programme and implementation contract; PDF section references below refer to this document. |
| [pc_cap_month_plan_summary.md](pc_cap_month_plan_summary.md) | Explanatory cross-check, especially the separation of routing, substrate, and credit claims. |
| [footnotes.md](footnotes.md) | Bibliographic inventory. Reading this file does not establish that the linked papers, private reports, or their implementations have been audited. |

The PDF supplies the experimental contract. The summary is explanatory. Week-specific choices should be identified as choices, and departures should be recorded explicitly. Hardware measurements and asset availability reported by week1plan1 are inherited statements, not measurements reproduced by this review.

## 1. What the plan gets right

**Accept the BP-first path and conditional ePC work** in §§1–3 and RV-1/RV-9. PDF §4, Appendix B, and S5 explicitly allow useful BP work when ePC is unavailable or ineligible. Missing ePC is not failed fidelity. Failed teacher fidelity blocks a matched-fidelity superiority claim, while an otherwise valid same-ePC SE-A/SE-E comparison can remain informative. Requiring ePC to unlock every task would contradict the programme.

**Retain the common memory ceiling, aggregate write budget, C0 depth control, and CR sparse control** in W1-2.5 and W1-3.5/3.6. They address different confounds. C2 beating C1 alone cannot establish that measured selection adds value beyond sparse writing. Likewise, a useful forced probe is not proof that the actual stored update will work; the transactional candidate evaluation must remain.

**Retain complete-answer generation, the reference decoder, frozen-base checks, and read-only evaluation** in W1-2.1/2.6/2.7 and §9. These are central to the measurement, not expendable implementation polish. Keep the distinction between teacher-forced loss and generated-answer success.

**Retain bounded development and negative-result semantics.** The fixed candidate sets, disjoint confirmation data, conditional S6, and refusal to treat poor C2 routing as a failed correctness test are faithful to PDF Appendices A, C, and F.5. None of the corrections below requires relaxing a scientific threshold or changing the primary endpoint.

## 2. Explicit corrections to week1plan1

### CR-1 — Reconcile S0 exit with the permission to start S1

**Responds to:** §0.1, §2 dependency paragraph, CP-3, and RV-4.

Section 0 says every S0 known-answer test and the four pre-run invariants pass before experimental work. CP-3 then allows S1 to start when PC-4/PC-5/PC-9 are not green, and RV-4 permits P5 work while cap fixes continue. PC-4 and PC-9 overlap the rollback and cloning invariants themselves. A blanket exception based on whether S1 uses the update path does not resolve that conflict.

PDF S0 requires cap-off identity, memory accounting, rollback, and complete-state cloning before any experimental run; Operating rule 5 also says to stop only affected work. Apply both rules explicitly: setup, fixture construction, data preparation, and repair may continue during a failed gate, but do not label experimental S1/S2 measurements admissible until the four invariants pass. After that gate, identify which additional failing control blocks which measurement. P5's actual gated-cap component depends on more than the uncapped base wrapper.

**Required revision:** replace the CP-3/RV-4 exception with a dependency table naming the passing invariant evidence, affected measurement, and unresolved control. Keep development smoke tests clearly distinguished from experiments used as evidence.

### CR-2 — Complete the control inventory without moving every control into S0

**Responds to:** W1-3.3/3.7, D-13/D-21, CP-3, and §0.

There is a valid defense of the existing schedule: PDF S3 explicitly starts by running F.5 controls. The PDF does not require the entire E.1 fixture and every baseline adaptation to be finished at S0 exit. Deferring PC-1 until before S3 is therefore defensible. Calling a partial PC-4 implementation complete, or leaving PC-3 and PC-8 unscheduled, is not.

| Control | Existing treatment | Required disposition |
| --- | --- | --- |
| PC-1 planted acquisition | Explicitly deferred | Retain a dated gate before S3; distinguish the 20-target control from the full E.1 fixture and its shared/private/mixed cases. |
| PC-2 identity | Scheduled | Retain. |
| PC-3 repeat idempotence | No explicit task | Add 20 successfully fitted complete edits, repeated without intervening updates, with no additional allocation. Finish before S3. |
| PC-4 conflicts and revisions | Revision retirement only stubbed | Mark coverage partial until newer-version replacement, failed-replacement rollback, and exact revision replay are tested. The full challenge dataset may come later. |
| PC-5 signed search | Scheduled | Retain analytic sign, nonmonotone search, and exact rollback checks. |
| PC-6 budgets | Scheduled | Include actual storage overhead and training-use semantics from CR-3. |
| PC-7 complete answers | Scheduled | Retain. |
| PC-8 isolation/read-only evaluation | A scope rule, no assigned test | Test complete learner-state preservation for current R-h evaluation before using it. Add the pseudo-label feature tests before enabling R-g/R-e. Explicitly mark those optional variants unimplemented meanwhile. |
| PC-9 cloning/randomness | Scheduled | Retain complete-state and item-keyed randomness checks. |
| PC-10 parity | Assigned to WD5 | Start reference smoke/parity work earlier; require evidence before comparative baseline claims. |

**Required revision:** add owner, due checkpoint, implemented cases, and evidence path for every row. Report S0 completion separately from readiness for the complete S3 control suite.

### CR-3 — Fix use-count semantics and qualify slot counts

**Responds to:** W1-2.5, W1-3.2/3.6, and §9.13; PDF Appendix B and F.2.

The budget arithmetic is correct: at `d = 768`, the ceiling is 38,535,168 bytes and each three-bank allocation is 12,845,056 bytes. The advertised 2,048 narrow-key or 1,374 wide-key slots per bank assume the stated slot layout and no additional bank storage that consumes the ceiling. C0's 6,144 slots likewise consume its full nominal allowance. They are not guaranteed capacities once indices, alignment, caches, and correction bookkeeping are included.

More consequentially, F.2 requires counting each training item at most once per slot, even if several rounds touch it. The week plan says to update metadata on commit but does not carry over that restriction. Incrementing on each successful round would change eviction priorities and potentially confound comparisons between routers.

**Required revision:** derive capacity after budgeting all persistent storage. Add a test in which one complete item touches a slot in several rounds or prefixes and increments its successful-item count only once. Define the item identity and bounded bookkeeping used to enforce that rule; document repeated-delivery behavior. Prediction must never increment it.

### CR-4 — Exact-key fallback does not redefine RET-GS

**Responds to:** U9 and RV-5.

RV-5 says exact-key retrieval makes endpoint RET-GS mostly measure exact-prompt retention. That is incorrect: RET-GS is still evaluated on held-out paraphrases. Exact-prompt retention is RET-ES. Changing retrieval cannot change which prompts define the endpoint.

If no bank fires anywhere during a paraphrase's generated trajectory, its prediction follows the uncapped model. Thus the cap contributes no improvement on that trajectory, but absolute GS need not be zero: the base may already answer a paraphrase correctly even when the original edit prompt was selected as incorrect. Exact normalized keys may also coincide, and an exact-key fallback at one bank does not imply that all other banks fail to fire.

**Replacement interpretation:** “Exact-key fallback may severely limit cap-induced paraphrase gains. Report paraphrase firing, base GS, immediate GS, and RET-GS separately from RET-ES. A low RET-GS remains a generalization limitation; it is not evidence about exact-prompt retention.”

### CR-5 — Separate the per-prefix stopping criterion from acquisition

**Responds to:** U10, W1-5.1, and RV-6; PDF F.3, D.8, and E.2.

U10 identifies immediate acquisition with `CE ≤ 0.1` within five rounds. That threshold is the per-prefix training stop. Immediate ES is complete-answer success under free generation. A model can generate the desired answer while its target probability is below `exp(-0.1)`; conversely, later prefix updates can disturb earlier fitted predictions.

**Required revision:** record threshold attainment and free-generation ES separately. Use the specified immediate acquisition outcome and locality constraint for step screening. Diagnose candidates that fail to function, but do not classify every threshold miss as zero generated-answer efficacy. Preserve both outcome fields even when their names in the implementation need clarification.

### CR-6 — Separate learner rollback from consumed-cost accounting

**Responds to:** W1-2.4, W1-3.3/3.4/3.7, and §6; PDF Appendix B and F.2/F.3.

The plan requires snapshots of counters and exact rollback, while charging every rejected search. A single undifferentiated counter snapshot risks deleting the cost of rejected work. The same issue arises when read-only prediction emits telemetry or a run stops halfway through a multi-token item.

**Required revision:** define rollback state separately from an append-only execution ledger. Restore keys, values, metadata, allocation state, learning counters, and RNG as specified; retain costs and rejected-decision records. Resource-limited termination must restore the whole incomplete item's learner state, including earlier accepted prefixes, while charging all its execution time. Test that case before using resource-matched endpoints. Evaluation telemetry must not alter future learner behavior.

### CR-7 — Profile with an explicit provisional CR schedule

**Responds to:** W1-3.5, W1-5.3, and §9.3; PDF S3 and §7.

CR needs a fixed bank distribution to run on Monday, but PDF S3 says the confirmatory probabilities are estimated from that stage only. The week plan does not specify what the earlier profiling run uses.

**Required revision:** declare a profiling-only distribution, such as uniform, in the S2 manifest. Estimate final probabilities from the prescribed development C2 runs in S3, then freeze them for S4. Recheck throughput if the resulting bank mix materially changes the projection. Log proposed routes, abstentions, accepted writes, and actual write counts separately; the fixed nominal budget does not guarantee equal realized writing.

### CR-8 — Make the data sequence executable and audit the sampling commitments

**Responds to:** §0.5, W1-2.6/2.7, CP-3, W1-4.1/4.2, and §9.1.

The decoder tests and Thursday smoke edit need development items before Friday creates the development manifest. Reserve and hash a small S0 development manifest first, then include it in the permanent development partition and exclude its subjects/facts from confirmation.

Creating the confirmation pool necessarily reads source records; teacher-based eligibility selection also inspects prompts and target aliases. That preparation is different from using confirmatory outcomes to tune a configuration. Specify a deterministic preparation process, record its access, seal its output, and prevent tuning code from opening it. Hashing alone does not establish disjointness or enforce that boundary.

The named 2M-token P1 set, 1M-token WikiText drift sample, and disjoint probe partitions also need a tokenized inventory. Do not assume the named split can supply the requested sample under the intended uniqueness and sampling rules. Record whether sampling is with or without replacement, counts of distinct documents/tokens, and any shortfall. If the prescribed source cannot supply the intended sample, log a source-specification issue before choosing a substitute. Distinct P1 and drift sets and D.5 subsets of the calibration pool are compatible choices, not established contradictions in the PDF.

### CR-9 — Close the report-card coverage gaps

**Responds to:** W1-4.4–4.8, W1-5.4, D-18/D-25, and RV-1.

W1-5.4 places “P4 on BP” inside the conditional ePC task. BP P4 should not disappear solely because ePC is absent. It needs its own data and capability assessment under D.4/E.4. Conversely, forcing natural-language POS or WikiText metrics onto a synthetic-vocabulary model would violate the PDF; unsupported entries are legitimate.

P5 is assigned for BP but not explicitly for available ePC credit procedures, despite S1's common report-card requirement. W1-5.3 also omits the conditional ePC credit throughput profile required by S2. Finally, ePC energy conventions are deferred to WD4 even though F.6 calls for resolving them in S0. With late-arriving assets, introduce a clearly identified ePC preflight before admitting its measurements.

**Required revision:** add a P1–P6 coverage matrix by base and credit signal, with data manifest, cost estimate, prerequisite, and status (`complete`, `pending`, `unsupported`, or `unavailable`). Separate P4 domain descriptions from the fixture-dependent intervention/transfer evidence. For P1, explicitly report when zero-initialized unclamped inference is merely the feedforward consistency check described in D.1. Missing applicable rows make S1 partial; they are not silently satisfied by an eligibility table.

### CR-10 — A provisional conversion is not a measured budget, and B0 is not free

**Responds to:** W1-1.3, W1-5.2/5.3, §6, U4/U11, and RV-3/RV-8.

The formula `local hours = A100-equivalent ceiling / κ` is consistent when `κ = local throughput / A100 throughput` for the same workload. Published throughput from an unmatched configuration is an assumption, not the measured shared-workload conversion required by Appendix B. Without that reference, D1 can report measured local costs and sensitivity to provisional κ, but cannot certify measured A100-equivalent compliance.

The claim “B0 (frozen) is free” should mean no training updates. Its generation, reference predictions, and LM evaluation still consume time. Shared cached reference results can be reused where semantics match, with their production cost recorded.

The S4 projection must include the learned grammar, not just both editing datasets. Distinguish C0's required initial editing scope from its lower-priority long extension. Include checkpoint rescoring, LM drift, applicable challenge evaluation, and endpoint work; assign S5/S7 costs to their own ceilings. State whether 25% headroom means reserving 25% of the ceiling or multiplying estimated cost by 1.25, since these produce different admissible workloads.

**Required revision:** make the projection a manifest-derived sum over datasets, arms, realizations, orders, and evaluations, with uncertainty and explicit overhead. Use initial latency measurements early, then the prescribed 100–300 complete-edit profile for the decision. Neither “300 edits should fit” nor “3,000 cannot fit” is established by the current back-of-envelope calculation. Accelerator budget and calendar runtime are separate constraints.

### CR-11 — Start baseline feasibility earlier; do not defer validity to Monday

**Responds to:** W1-1.2, W1-5.2, U8, and RV-7.

Monday currently contains implementation and validation of three baselines, cap screening, six-arm throughput profiling, conditional ePC measurements, and three reports. The document supplies no engineering estimate demonstrating that this fits one working day. Moving dependency installation and reference smoke tests earlier is compatible with S2's instruction to calibrate before baseline experiments: installation/parity preparation need not select a competitive configuration.

**Required revision:** pin and smoke-test the baseline reference as soon as the environment exists. Record how the requested query/value-only LoRA adaptation is realized in the selected model implementation and verify the intended trainable projections. Keep optimizer/replay state in baseline cloning and accounting. A fallback implementation without the required reference validation is not an established B4 comparator; identify the comparative claim as unavailable until parity is demonstrated, rather than suggesting that a provisional label repairs missing evidence.

### CR-12 — Distinguish an on-time D1 decision from completed S0–S2

**Responds to:** §§0/4/5/7/8, RV-4/RV-11, and §11's weekend question.

The plan can hold D1 on Monday even if its decision is “valid partial harness; S1/S2 incomplete; confirmation not ready.” Its current “week 1 done when all are true” language conflicts with fallback paths that knowingly defer required work. Preserve the decision deadline where useful, but do not call incomplete stages passed.

The optional weekend also carries work required before Tuesday S3. RV-4 moves D1 to Wednesday after a long slip; RV-11 moves it to Tuesday without resolving how the rules interact. Those are different calendars, not a single dependable fallback.

**Required revision:** publish one dependency-based schedule with a five-day baseline and optional weekend acceleration. Give unfinished required tasks revised dates and identify the effect on S3/S4. The asset questions in §11 are appropriate draft requests; owner identity, access, compute, and availability remain unknown until answered. A missing reply should block only dependent work. Nothing in this document review constitutes sending those requests.

## 3. Proposed replacement checkpoint plan

This is a prioritization proposal, not a new claim that the full implementation fits five days. It preserves thresholds, required contrasts, and the 32-hour week-1 accelerator allocation.

| Checkpoint | Concrete result to require | If incomplete |
| --- | --- | --- |
| CP-1, Tuesday | Asset inventory; tested environment or recorded blocker; initial development partition; source/provenance inventory; baseline dependency smoke test started; local benchmark and conversion status. | Continue independent scaffold and CPU controls. Do not certify a provisional conversion as measured. |
| CP-2, Wednesday | Wrapper and hook checks; known-answer metrics; complete-answer decoder; explicit learner/ledger state boundaries; memory layout; baseline parity issues identified. | Continue independent implementation; affected tests retain failure status. |
| CP-3, Thursday | Four pre-run invariants pass; required S0 tests pass; recorded development smoke edit; complete control-coverage table; resource-stop rollback test. | S0 remains incomplete; experimental measurements wait on their documented gates. |
| CP-4, Friday | Audited partitions and sample inventory; BP report-card coverage/status; shared scale/radius calibration where prerequisites pass; initial latency estimates; modular control progressing on a scheduled working day. | Report missing measurements and revise dates; exact-key fallback receives CR-4's interpretation. |
| D1, Monday | Stage statuses and evidence; completed calibration/parity/profile results or explicit gaps; full remaining-budget projection; base eligibility; owners and dates for remaining controls; S3 readiness decision. | Issue the memo on time if useful, but mark S1/S2 partial and move dependent S3 work. |

Before S3 begins, require the full applicable F.5 control evidence, including PC-1/3/4/8/10 as scoped above. Do not require C2 to beat the oracle, random routing, or LoRA as a correctness gate. Freeze confirmatory CR probabilities after S3, and freeze the final protocol at S4.

## 4. Disposition of the existing files

**week1plan1.md:** retain its scientific comparisons and most implementation procedures. Address CR-1–CR-12 in a logged v2, updating the definition of done, task tables, deliverable checklist, unknowns, revision points, and checkpoint summary together. Correcting one paragraph while retaining contradictory gate text elsewhere would leave the schedule ambiguous.

**review_plan1.md:** no substantive response is possible beyond acknowledging its current title-only state. If a critical review is added later, respond to its actual numbered claims separately; this document should not be represented as having rebutted an unwritten review.

**Month-plan PDF and summary:** retain their distinction between correctness, resource eligibility, and scientific outcomes. The proposed fixes make week1plan1 more faithful to those distinctions. Any genuine source ambiguity, such as an infeasible prescribed data sample or unresolved headroom convention, should receive a documented development resolution rather than an unannounced protocol change.

**footnotes.md:** retain it as the reference inventory. Private-report results remain inherited claims pending reproduction; bibliographic links do not establish asset access, reference-code parity, or experimental validity.
