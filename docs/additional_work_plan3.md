# Additional experiments before October 9 — Codex response to Claude's review

September 20, 2026. Written at Charlie's request to preserve the assessment of [Claude's suggestions](additional_work_plan2.md), responding to [the original additional-work plan](additional_work_plan.md). This is a scientific and feasibility review, not authorization to launch experiments or change the registered study.

**Execution constraints, confirmed by Charlie:** all experiments run locally on this machine, using the existing JAX environment. Colab and other remote execution are excluded. No PyTorch execution: any implementation that uses PyTorch must be ported to JAX before it is run. PyTorch source may serve as a read-only reference. Porting, validation and local execution time count toward the experimental schedule and budget. These constraints supersede any Colab option discussed in the earlier planning documents.

## 1. Overall assessment

I agree with Claude's practical direction: **prepare isolated CPU work now, run bounded corrections early, and retain the upper-layer experiment.** Adding a stricter firing-gate comparator is especially useful. The proposal for more untouched realizations is also scientifically valuable, although the certified populations cannot support two full additional realizations as currently proposed.

I would adopt the core direction after correcting the population assumptions, several numerical claims, the AW-B success criterion and the AW-L arm counts. The experimental deadline remains October 9; October 10–14 is for analysis of locked results, presentation preparation and rehearsal.

My preferred sequence is:

1. Prepare isolated CPU implementation, mathematical checks and the population-allocation inventory now.
2. After primary-run release, run AW-B and the frozen layer diagnostics.
3. Complete the core trained AW-L comparison with three seeds.
4. Run one additional untouched primary-triplet realization if population allocation and remaining resources permit it.
5. Add optional layer variants only after the essential comparisons and replication are secure.

I would prioritize an additional untouched realization over more optional layer variants. AW-G and AW-D remain deferred for this deadline unless their dependencies become unusually easy to satisfy.

## 2. Option R: worthwhile, but two full additional realizations do not fit

Claude correctly identifies the small number of independent realizations as a weakness of the primary study. More untouched draws would strengthen evidence about whether the selected artifact's results recur across different edit populations. They would not replicate reader training, since the primary triplet retains the selected reader artifact; no six-minute reader retraining is required for another realization of that same registered condition.

The immediate constraint is population capacity. The [certified teacher and role inventory](tasks/R1-D10h.md) reports:

| Dataset | Certified usable subjects | Subjects required by the existing three realizations | Certified margin | Demand for one additional full realization | Demand for two |
|---|---:|---:|---:|---:|---:|
| zsRE | 6,084 | 4,050 | 2,034 | 1,350 | 2,700 |
| CounterFact | 6,121 | 4,050 | 2,071 | 1,350 | 2,700 |
| MQuAKE | 2,161 | 1,950 | 211 | 650 | 1,300 |

A zsRE or CounterFact realization requires 1,000 edit subjects plus 100 outside, 100 near-support, 100 near-neighbour and 50 revision subjects. The roles and realizations are subject-disjoint. MQuAKE uses 300 edits plus those 350 endpoint-role subjects. These requirements are in the [population protocol](R1_stage4_protocol_v5_2_D_1.md), incorporated by the later amendments.

Consequently:

- **Two full additional zsRE/CounterFact realizations cannot fit the currently certified pools under those same rules.** Each needs 2,700 remaining subjects, exceeding the certified margins.
- One additional realization might fit zsRE and CounterFact, but subject totals alone do not prove that template families and all endpoint roles can be allocated.
- Even one additional full MQuAKE realization does not fit the certified margin. Claude's smaller remainder estimate of 169 only strengthens this conclusion.
- These margins are certified historical upper bounds for planning, not a fresh post-exposure clearance. Any subsequent reservations can reduce what is available.

The capacity check must cover **the whole supplemental portfolio**, not Option R alone. Fresh AW-L/AW-B evaluation populations draw on the same scarce subjects. Allocating 1,350 subjects to Option R leaves, at most, 684 zsRE and 721 CounterFact subjects from those margins before additional exclusions. That could materially constrain fresh supplemental streams. Reusing suitable fixed evaluation populations across supplemental arms can support paired comparisons, but must be declared; reusing exposed data does not make it fresh again.

Recommended change: propose **one additional zsRE/CounterFact realization, subject to a joint allocation check**. A second realization would require a separately justified population expansion or altered design. A shorter stream or reused endpoint population should not silently count as an equivalent full realization for the original 1,000-edit estimand.

### The confidence-interval claim

Claude's approximate halving calculation is correct under a specific condition. For the same observed sample standard deviation, a pointwise Student-t interval changes in width by

```text
(t[0.975,4] / sqrt(5)) / (t[0.975,2] / sqrt(3))
= (2.776445 / 4.302653) × sqrt(3/5)
≈ 0.49984.
```

However, the new realizations can change the observed standard deviation, so halving is not guaranteed. The interval also remains conditional on the distributional assumptions; five realizations do not establish the registered family's 95% simultaneous coverage. The [NIST interval formula](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm) makes the dependence on both sample size and sample standard deviation explicit.

Keep the existing registered analysis intact. Report any extension separately, with each realization visible and pooled sensitivity summaries clearly distinguished from the original decisions. This follows the interpretation limits in [D.5 / DEC-069](R1_stage4_protocol_v5_2_D_5.md).

## 3. AW-B: support the tail emphasis, but measure the proposed wrapper

Making extreme loss and retained editing the central question is sensible. Claude's stricter-gate comparator improves the design: **does shaping the correction provide a better efficacy–harm tradeoff than simply making the cap fire less often?** That is a useful result for the talk, whether the answer is positive or negative.

The numerical pre-analysis is useful for describing the existing loss distribution. It does not establish the effect of an intervention that has not been evaluated.

### Scalar KL clipping is not distribution clipping

Claude labels `min(KL, 2b)` a heuristic, appropriately. The later statements that no efficacy-preserving bound can meet the 0.001 mean-KL benchmark go beyond what that heuristic shows.

The actual AW-B wrapper clips the log-probability ratio for each vocabulary entry, then renormalizes the whole distribution. A saved scalar KL or target-token loss does not determine that result. As a small mathematical illustration, using

```text
p0 = [0.99, 0.005, 0.005]
p1 = [0.01, 0.495, 0.495]
b  = 0.5
```

gives original KL of approximately 4.5032 nats. The scalar proxy `min(KL, 2b)` is 1.0 nat, while the actual normalized clipped-log-ratio wrapper has KL approximately 0.00704 nats. This CPU calculation is an illustration, not a project result, but it demonstrates why the proxy is not a quantitative prediction of the intervention.

Likewise, there is no universal one-nat displacement requirement for a successful edit. The needed change depends on the base probabilities, competing answers, decoding and answer length. Whether a particular bound preserves our edits must be measured.

Recommended wording: **“We expect a tradeoff between limiting extreme loss and preserving edits; we will measure both the tails and mean KL.”** Do not predeclare that every useful setting must miss the old benchmark. Keep the 0.001 line visible without interpreting a speculative proxy as an experimental outcome.

### What counts as a useful result

Reducing the maximum is partly guaranteed by the bounded construction. The scientific result is whether the wrapper retains useful editing and improves the observed tradeoff compared with cap-off, unmodified v5, shrinkage, mixture and stricter gating. Tail severity and exceedance frequency should be reported alongside RET-GS, RET-ES and preservation endpoints.

The proposed success rule also needs correction. It evaluates **ES99** using a spread taken from the earlier **ES95** pilot. The [pilot record](tasks/HT-3e.md) specifies:

- ES95 over 4,064 positions, including zero-harm positions;
- an ES95 separation threshold of 0.387471415 nats;
- a maximum-loss threshold of 4.439309019 nats, derived from the pilot's seed ranges.

Full validation uses 245,237 positions. ES95 and ES99 cover different parts of the distribution, and a maximum changes with the scored population and its size. The old numbers therefore should not automatically become success thresholds for the new experiment.

I would retain the proposed retention tolerance, fix the new endpoints and selection rule before evaluation, and assess paired tail changes on the actual supplemental population. Report all seed/stream differences and the efficacy–harm curve. Any uncertainty statement must respect the pairing and dependence of positions rather than counting tokens as independent experiment replicates.

### Gate direction and the meaning of “fired”

In [the current learner](../src/pccap/revision_v1/learner.py), hard rejection occurs when

```text
null_mass >= null_threshold
```

Thus a stricter rejection rule means **lowering** `null_threshold`, not raising it. Preserve the other rejection rules and record how they interact.

Observed distribution changes are also not identical to gate-firing events. A selected record may produce no effective change at some answer positions or under some write conditions. The pre-analysis should call its statistic a changed-distribution fraction unless actual gate telemetry substantiates firing. We should measure both before asserting that firing frequency alone explains all harm.

Shared fixed-prefix logits can score the numerical wrappers efficiently. Full generated answers still need per-wrapper evaluation because their prefixes can diverge. Unchanged positions reduce wrapper work; they do not remove the base observation and gate computation needed to determine that nothing should change.

## 4. AW-L: keep the mechanism comparison and correct the matrix

Claude's emphasis on what each intervention changes is useful. Read ports affect the gate and retrieval; write ports determine how much downstream transformer computation receives a correction. The final-bank write goes through the final layer normalization and vocabulary head, while a bank-1 write passes through eight further transformer blocks.

Two qualifications matter:

1. Changing read features changes **which record is selected**, not only whether the gate fires. It can therefore change both the frequency and severity of harm.
2. A final-bank hidden-state write is related to an output correction, but is not identical to AW-B's freely specified per-token log-ratio clipping. It passes through layer normalization and the tied output projection and has its own representational constraints. The corrected pass becomes cheaper, not costless; the vocabulary projection remains, as does the full observation pass.

The original warning about `single_site=True` stands: it is presently a deployment ablation, while delta acquisition still trains all three banks. A fair final-only write condition must constrain acquisition and every deployment/fallback path consistently.

### Correct arm counts

Assuming reader fitting is shared across write variants as in the proposed core design:

| Design | Trained readers, three seeds | Evaluations on two datasets |
|---|---:|---:|
| Core: two read sets × two write sets | 6 | 24 |
| Add final-only and middle-only read sets, each with one write set | 12 | 36 |
| All four read sets × both write sets | 12 | 48 |

The proposal's “nine trained readers” does not cover both additional read sets. The 36-evaluation count is possible, but only with an explicitly incomplete write-factor expansion for those optional sets. The manifest must name the exact cells.

I would keep three seeds in the core comparison and drop optional read sets before reducing to two seeds. Three already provides limited evidence about training variability; adding architectural variants while removing replication makes the result harder to interpret.

### Frozen diagnostics on completed R1 memories

These are reasonable as **post hoc ablations of the selected, already trained system**, after primary-run release. Restore a separate copy, retain original artifacts unchanged, and label the evaluation's exposure and interpretation clearly. A deployment-only ablation cannot establish how well a properly trained upper-only architecture would perform.

Do not use these outcomes to choose settings and then call the same populations independent validation. A joint AW-B/AW-L efficacy–tail figure is useful when checkpoints and evaluation populations are comparable; otherwise visibly distinguish them rather than imply a matched comparison.

## 5. Preparing code in `aw/` is a practical improvement

I agree with this amendment to my initial plan. [The lock verifier](../scripts/r1_63o_live_audit.py) checks the installed Python inventory under `scripts/` and `src/pccap/`, as well as its individually bound dependencies. A new, isolated `aw/` namespace can support CPU preparation without adding files to those locked implementation trees.

Conditions for that preparation are straightforward:

- Do not change locked dependencies, installation configuration, shared import behavior or the primary-run environment.
- Force CPU execution before any JAX backend initialization; small NumPy float64 mathematical checks need no accelerator.
- Bound host-memory consumption and avoid competing large cache builds while R1 is running.
- Give separate files to the agents and review shared interfaces before integration.
- Keep GPU work dependent on primary-run release and the lead's selected supplemental scope.

This supports starting AW-B's oracle and AW-L's mask/identity tests now. It does not justify an implicit launch of the supplemental experiments. One-page lane specifications are sufficient; another elaborate signing system is unnecessary.

## 6. Runtime, portfolio and calendar corrections

The tighter runtime estimates are plausible targets, not established complete-run costs.

- My original **24-hour AW-B allowance was a stop ceiling**, not a prediction that 24 hours must be spent. Shared streamed logits were already part of that design. A measured 12-hour complete experiment would be welcome; retain the ceiling until a pilot accounts for reconstruction, generation, evaluation and failures.
- The 351/368-second figures in [the stage-2 notes](R1_stage2_notes.md) belong to the earlier text-null reader/reference-v2 table. They support the expectation that small reader fits can be inexpensive, but do not establish the cost of the selected v5 recipe with changed taps and its caches. Profile the actual supplemental implementation.
- Option R's measured block-1 example contains three datasets and 45 cells. A two-dataset realization contains 30 cells, with a different mix of costs. Use per-condition/dataset measurements rather than equating both designs to the same block time. Extra realizations of the fixed selected artifact do not need reader retraining.
- Claude's introduction proposes **200 hours**, while the explicit portfolio sums to **116–126 hours**: 12–16 + 2 + 24–30 + 24 + 24 + 30. Choose one actual ceiling and reconcile the portfolio, including the population-driven reduction of Option R.
- The September 26–27 release date is a forecast based on the completed mix. Later comparator blocks, retries and final primary obligations can change it. About 290 nominal remaining GPU hours is not the same as an approved supplemental allowance or an implementation-ready schedule.

Preserve the October 6 cutoff for new fits/architectural expansion, October 7–8 evaluation and verification, and the proposed October 9 17:00 experimental freeze. Human review is a real constraint, but it should be assessed alongside data capacity, host memory, GPU execution and the required primary-study completion work.

## 7. AW-G, AW-D, Colab and presentation framing

Deferring the generated-reader and joint-distillation tracks is sensible for October. I would qualify two parts of the rationale:

- AW-D was not intended solely to repeat the supplied joint-versus-staged result. Its full-width/compressed × joint/staged factorial supplies a control missing from the reported study, separating joint preparation from a compression-specific effect. That could be useful later, even though it is not the immediate talk priority.
- The supplied notebook can be used only as a reference for a local JAX port. Colab is not an execution option, even after porting. Replace its Drive-specific storage with the project's local artifact paths, validate correctness, and profile the complete workload on this machine before admitting a run. The notebook is H2-style, not the missing H3 experiment, and its Colab budget is not a measured local runtime. Any such experiment uses the same local hardware allowance and must wait for primary-run release before GPU execution.

The GT framing is useful when presented as a connection rather than a completed architectural claim:

- R1 is a stronger-base cap study related to the programme's stage-B questions. Do not imply that it tests generated CD readers or predictive-coding learning, or that nominal resource bounds alone establish an exact matched-compute/memory adapter comparison.
- Our ordinary-text KL assay measures behavior on a declared population. It is related to the GT preservation motivation, but it is not the report's full worst-case behavioral distance over a family of continuations.
- The memory-versus-access distinction is a helpful analogy for our retrieval and false-fire problems. R1's fixed-reader experiment does not by itself establish that its observed fidelity creep is caused by the learned gate's weights drifting as in the H2 adaptation experiment.
- Attribute AW-B's bounded-tilt construction to the supplied report and retain the qualification that its guarantee is per token at a common fixed prefix.

## 8. Recommended disposition

**Adopt:** isolated CPU preparation; AW-B early on the GPU; the stricter-gate comparator; the core upper-layer read/write comparison; clearly labeled frozen diagnostics; deferred AW-G/AW-D.

**Revise before execution:** population allocation for the whole portfolio; Option R to at most one full additional zsRE/CounterFact realization pending role checks; AW-B's success rule and speculative KL claims; gate-threshold direction; AW-L's arm counts; runtime estimates and the inconsistent total budget.

**Priority if time or data becomes tight:** retain complete paired comparisons and three seeds, drop optional layer variants, and decide explicitly whether the remaining fresh subjects are better spent on replication or the supplemental intervention study. Do not promise both from the same unallocated population margin.

The strongest overall programme is a completed primary study, one careful intervention that preserves useful edits while testing harm reduction, a fair test of Charlie's upper-layer hypothesis, and additional untouched replication where feasible. Every one of those can produce a valuable negative result without weakening the presentation.

Review scope: the key claims above were checked against the current code and recorded reports, with small CPU arithmetic checks. The 84-cell pre-analysis was not independently reconstructed cell by cell. No GPU inference, training, primary-source edits or experimental launches were performed for this response.
