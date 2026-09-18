# Scientific programme review before revision-v1 execution

**For Charlie Derr and Claude, September 18, 2026.** Experimental stop: **October 9**. Presentation: October 15. This is an independent review of our joint scientific choices, including choices I previously helped formulate. It proposes changes for discussion; it does not change the approved experiment.

**My judgment:** the project has developed a useful, testable research question and several worthwhile results. I support completing the frozen-base editing study, retaining the reduced MQuAKE arm, and reporting the κ pilot's null result. I would **not** endorse strong statistical confidence claims from the current three-realization bootstrap. I also want us to distinguish a comparison of complete editing systems from an experiment isolating learning, predictive coding, or coupled active inference. The current design primarily does the former.

The two decisions I would revisit before outcomes are **the interpretation of DEC-057/058 uncertainty** and **DEC-051's execution order**. Most other concerns can be addressed through accurate interpretation and additive analysis, without more training or a larger matrix. We should avoid another expansion of the programme before October 9.

## 1. What programme we are actually conducting

The original monthly plan, [plan 9](updated_plan9.md), its [coding guide](<more_input/pc_cap_coding_agent_guide (1).pdf>), and the later Stage-4 amendments describe related but distinct questions. Later approved decisions take precedence over superseded scope and budget statements.

| Part of the programme | Current evidence | What it can establish |
|---|---|---|
| Historical v0 routing/substrate study | Completed, with negative or uninformative primary contrasts and disclosed defects | Results for those specified routing and substrate implementations. Revision-v1 development does not reverse them. |
| Diagnosis of the v0 failure | Oracle, live/stable observation and stable-key diagnostics on development streams | Evidence that observation instability and record selection were important bottlenecks in the tested setting. This is a stronger basis for redesign than simply adding capacity. |
| Stronger frozen-base cap | A selected BP-trained reader, rejection rules, stable observations and support-taught per-position residuals | Whether this deployed editing package improves acquisition/generalization while controlling unintended intervention on fresh reserved streams. |
| Base/cap co-training, matched BP/ePC training, cap settling | Earlier synthetic BP/ePC pilots exist; these branches are not the selected natural-data confirmatory matrix | Their pilot evidence remains informative, but the planned broad base×cap and feedforward×settled causal comparisons have not been delivered by the current matrix. |
| Tail and stress studies | Audited development vectors, four full-validation profiles, a six-cell stress panel | Concentrated probability harm and the response to the tested schedules; these are bounded empirical results. |
| Loss-level κ pilot | Complete, three seeds per arm, null under its declared retention/tail rule | A preliminary trade-off for this specified loss modification. It does not validate or refute the full coupled-free-energy programme. |
| Fresh revision-v1 comparison | D.4 specifies 285 core cells, plus 45 optional historical-v2 cells; no completed current confirmatory matrix | The central evidence still to obtain. Three independently drawn fact realizations are crossed with five orders; these are not fifteen independent fact samples. |

The selected system is more specifically a **learned applicability/read mechanism plus support-taught residual editing on a frozen transformer**. Its current per-answer-position deltas replace the controller's write when present; describing the natural-data result as a demonstration of a generally learned conditional correction network would obscure that implementation choice. See [the adapter configurations](../src/pccap/revision_v1/stage4_adapters.py) and [the read path](../src/pccap/revision_v1/learner.py).

This narrower programme is scientifically worthwhile. It should be the October result, with the larger active-inference architecture presented as the research agenda. The submitted abstract's coupled blankets, expected-free-energy policy choice, epistemic audit selection, frontier-scale transfer and one-κ geometric conjecture are not established by these experiments. The [current talk outline](presentation/talk_outline_v1.md) already makes much of this distinction correctly.

One historical distinction is essential: the v0 SE-E result used the SD-24 defective energy and is evidence about that implementation, not a clean test of the corrected predictive-coding rule. The corrected synthetic BP/ePC pilot exists, but does not supply a broad natural-data superiority or equivalence result. Retain both histories without treating a code defect as a refutation of predictive coding.

## 2. The most consequential concern: uncertainty with three realizations

DEC-057 resamples the three realization means, retaining the five orders inside each realization, to construct 63 Bonferroni-labelled component intervals. Clustering at the realization level is the right direction: treating orders or token positions as independent trials would be worse. The problem is that **three clusters do not support the confidence interpretation being attached to the percentile intervals**.

I checked the [installed implementation](../scripts/r1_49g_inference.py), rather than relying on a general small-sample warning. With three observed realization means, the nonparametric bootstrap has only **27 ordered resampling sequences**, or ten multiplicity patterns. The probability of drawing the smallest realization three times is 1/27, about 3.70%; the same holds for the largest. Both the 97.5% interval's lower-tail probability, 1.25%, and the adjusted interval's lower-tail probability, about 0.03968%, lie inside those extreme atoms.

The installed seed-0 simulation draws each repeated-index extreme 373, 391 and 333 times out of 10,000. Consequently, **both the pointwise 97.5% interval and the adjusted 99.9206% interval reduce to the observed minimum and maximum realization means**. For example, means −.02, .03 and .12 produce [−.02, .12] under both labels. More bootstrap draws will not solve this.

There is a simple quantitative counterexample to calibrated coverage. Suppose the three independent realization estimates have continuous, symmetric errors around the true effect. Their observed range excludes the truth when all three errors are positive or all three are negative. Its coverage is therefore:

**1 − 2 × (1/2)³ = 75%.**

This is a mathematical counterexample under a stated sampling model, **not an estimate of our experiment's actual error rate**. A separately labelled 200,000-trial synthetic Gaussian illustration reproduced 75.12% coverage. With true retention effect zero, realization SD .10, and ES/LS differences fixed at zero, the installed classifier's equivalent positive inequalities were met in 9.80% of those synthetic trials. That is not a prediction about the cap; it demonstrates that a nominal confidence label and Bonferroni division cannot repair an inadequately calibrated underlying interval. [Reproducible diagnostic and evidence](../logs/scientific_review_20260918/evidence.json).

**My recommendation for Charlie and Claude:** agree on the inferential claim now, before confirmatory outcomes. The least disruptive honest choice is to retain the registered computations and classification rules for traceability, explicitly treat them as preliminary decision summaries, show every realization estimate and order dispersion, and decline claims of demonstrated 95% familywise error control or a strongly established population-level effect. The existing phrase “nominal approximate bootstrap” is directionally correct, but does not communicate how severe this specific limitation is.

If calibrated confirmatory inference is essential to the October claim, request a pre-outcome redesign of the inferential procedure and its assumptions. A Student-t sensitivity analysis with two degrees of freedom would require strong distributional assumptions and very wide adjusted intervals; it is not an automatic fix. An ordinary two-sided exact paired sign-flip calculation with only three exchangeable signs cannot attain a p-value below 2/8 = .25. More order permutations cannot supply missing independent fact realizations. Additional fresh realizations would require a population and budget amendment; simply resampling existing facts does not create them.

I do **not** recommend silently replacing the registered classifier, shrinking its 63-member family to the 42 potentially available components, or selecting a more favorable interval after observing results. The design can still yield strong descriptive and mechanistic evidence even if broad significance claims remain preliminary.

This is also a retrospective interpretation caution: the [historical bootstrap helper](../src/pccap/analysis/bootstrap.py) uses the same realization-mean percentile construction. Historical measurements remain unchanged, but confidence language attached to that construction deserves the same qualification. This is a limitation in our shared design, not a newly introduced Claude implementation error.

Two further wording points matter under DEC-058: “positive” requires a point gain of at least five percentage points and a lower bound above zero; it does not establish a lower confidence bound of five points. “Negative” can mean failure to meet the five-point target even when a smaller beneficial difference is observed. Publish the effects before the category names.

## 3. Do the controls answer the causal questions we care about?

I agree with adding **v0_stable** (DEC-035). The diagnosis showed that stable observations alone help, so a stronger reader must be compared with that simpler explanation. The matched-update condition also usefully asks whether improving the write rule is sufficient. Those decisions make the experiment more informative.

However, some central comparisons change several things at once:

| Comparison | Defensible interpretation | Stronger claim it does not isolate |
|---|---|---|
| v5 versus random reader | Benefit of these deployed packages | Learning alone: random disables lexical and pairwise-null features, uses a different threshold/cosine floor, and lacks the v5 rare-overlap gate. |
| v5 versus v0_stable/matched_update | End-to-end difference beyond these specified stable-observation controls | A single reader-weight effect, equal total training compute, or equal persistent memory. |
| v5 versus historical v2 extension | Difference between historical and current packages | Gate-only effect: training lineage and gating both differ. |
| Original versus continued base with StableCap | Effect of the particular retained continuation treatments under that cap | The full base×cap interaction, or the best possible base-training alternative to v5. |
| κ versus ordinary/clip2 | Loss-package trade-offs at the declared settings | A uniquely coupled mechanism: answer and preservation terms change together, while clip2 retains ordinary KL. |

The current protocol correctly acknowledges several of these limitations. They must remain central to the conclusion, rather than disappearing when a forest plot says “positive.” The [U03 memo](R1_U03_interpretation_memo.md) is a sound resolution of the continuation question: retain the historical controls, disclose that their token accounting was reconciled to reader v1, and make no exact-v5 compute-match claim. Appending 61,647 tokens to the continuation would not establish compute matching, because the two accounting systems count different work.

**A further fairness issue is the operating point.** MQuAKE's v0-style radius grid is constrained by an empirical 1% outside-fire calibration, whereas selected v5 passed a 10% zsRE unseen-fire development constraint and has different gates. These percentages come from different populations and are not directly comparable risk estimates. Nevertheless, the comparison does not establish superiority at matched unintended-intervention risk. Radius-zero controls are especially informative about the failure of this calibrated geometry, rather than about all nonlearned editing methods.

For October, I would keep these specified controls and make **package effectiveness at declared operating points** the claim. If one modest additional exploratory experiment is affordable, the most useful causal addition is a **same-v5-weights gate-on/gate-off comparison**, with identical items, orders, updates, memory and probes. This isolates the gate's incremental effect, not learning as a whole. A stronger learning-specific comparison would require the same feature architecture and a properly calibrated random/untrained control on a common risk population. Do not relabel the old-v2 extension as either experiment, and do not tune thresholds on the fresh confirmatory results.

A full matched-compute base×cap factorial or a new learned-memory baseline would be valuable later. Neither should become a new prerequisite that prevents the present experiment from completing.

## 4. Fidelity and rare harm: support DEC-064, with a narrower success claim

I support measuring and reporting the cap's fidelity failures rather than excluding those cells from comparative analysis. DEC-064 avoids conditioning the primary result on successful preservation and retains unchanged numerical benchmarks. It also preserves the distinct continued-base certification rule. This is a defensible separation of **measurement integrity**, **editing efficacy** and **preservation performance**.

It does change what an overall success means: a positive retention/locality classification can coexist with failure of the ordinary-text KL benchmark. We cannot summarize such a result as “better editing without damaging the base's behavior,” even though the base weights are frozen. The proposed slide/report should always show efficacy, mean-fidelity flags and tails together. The chronology of the fidelity interpretation decision belongs in the methods history; holding out new streams makes the next assessment prospective, but does not erase the developmental evidence that motivated the discussion.

I independently recomputed these saved full-validation summaries from the four NPZ vectors, each containing 245,237 scored positions. These are **development profiles**, paired by the same within-dataset payload, not fresh confirmation:

| Dataset / package | Mean KL | Mean signed ΔNLL | ES99 positive ΔNLL | Maximum positive ΔNLL | Positions with ΔNLL > 1 | Mean benchmarks |
|---|---:|---:|---:|---:|---:|---|
| zsRE / v5 | .002270 | .002310 | .237363 | 9.944689 | 189 | KL fails; NLL passes |
| zsRE / v0_stable | .000789 | .000855 | .096100 | 16.159299 | 47 | Both pass |
| MQuAKE / v5 | .005544 | .005601 | .572338 | 8.187550 | 485 | KL fails; NLL passes |
| MQuAKE / v0_stable | 0 | 0 | 0 | 0 | 0 | Both pass on these positions |

All loss quantities are nats; KL is reference-to-cap. Original and own-cap-off references coincide for these original-base profiles. The [independent recount](../logs/scientific_review_20260918/evidence.json) agrees with the saved summaries within 1e−12. The same input bindings are recorded in the [scenario evidence](../logs/scientific_review_20260918/order-scenario.json).

This is already a scientifically useful result: v5 zsRE has a smaller worst single loss change than v0_stable, but larger mean KL, ES99 and frequency above one nat. **There is no single scalar sense in which it is uniformly safer.** The all-zero MQuAKE control also cannot be called robust adaptation without its editing/generalization outcomes; doing little can preserve ordinary text.

One additional analysis would strengthen the extremes story without another run: **separate frequency from severity**. Positive loss changes occupy only 313, 190 and 820 positions in the three nonzero rows above, each fewer than 1% of the population. Consequently their empirical ES99 equals 100 times mean positive harm, and “the worst 1% carries all harm” largely reflects sparsity. These statistics remain valid, but they are not independent demonstrations of heavy-tail shape. Show the fraction above the already declared .01/.1/1-nat thresholds, conditional severity, maxima, and window concentration. Use “rare concentrated harm,” not an identified power-law tail or a practical catastrophe rate.

The full-validation addition (DEC-063) is worthwhile: the fixed 128-window prefix missed larger maxima and can over- or underestimate whole-source means. Its 1,931 short, reset-context windows still characterize this fixed ordinary-text source, not arbitrary deployment contexts or long autoregressive rollouts. More positions improve coverage of that source; they do not increase the number of independent edited-memory realizations.

## 5. Population and endpoint choices: reasonable, but specific

**Selection and generalization.** I support DEC-049/050's common-population selection and a fresh confirmatory population. Forty-two candidate definitions and fifteen admissible candidates are honest development work. The winning seed/checkpoint's .8033 mean RET-GS and 10/100 unseen fires should not be treated as unbiased estimates of a generic training procedure. Confirmation evaluates that selected artifact. Three test realizations do not replicate reader training, and the earlier .10/.12/.09 outside rates used different probe sets; they do not establish occupancy invariance.

**zsRE is largely knowledge acquisition under the current decoder.** The reviewed teacher inventory has **6,036 empty one-step-newline outputs among 6,084 eligible zsRE items (99.21%)**. CounterFact and MQuAKE have no empty outputs in the corresponding reviewed inventories. This does not invalidate learning the supplied target or generalizing to its paraphrase, but it changes the story from “correcting confidently expressed false facts” to mostly adding answers where this base/decoder produced none. Keep baseline emptiness, old-answer correctness where observed, answer length and truncation beside the results. Preserve all planned denominators; do not retrospectively discard empty-baseline items. [Teacher characterization](../logs/r1_round25/r1-x15-independent.json).

**CounterFact and MQuAKE exposure decisions.** DEC-042's exception for old-pool membership alone is defensible: mere inclusion in a source pool is not the same as use in training or evaluation. DEC-048's query-role exemption and DEC-060's ordinary-text context adjudication are more substantive. They define “fresh” relative to counterfactual-edit exposure and specified task roles, not a guarantee that the system never encountered the entity or true fact. I support the explicit, outcome-independent rule and preservation of other exclusions. Disclose the capacity-driven chronology and avoid the phrase “wholly unseen subjects.”

**Bounded equality (DEC-053).** Comparing the same generated bounded text is a sensible primary preservation measure. An unchanged truncated response should not automatically count as new cap-induced damage. Continue reporting terminated equality, truncation and raw texts. Bounded equality is neither a correctness score nor proof that token distributions are unchanged.

**Near misses (DEC-061/062).** Drawing disjoint support/neighbour subjects from the same declared family is better than calling arbitrary unrelated pairs near misses. Multiple pairs per family are reasonable and solve the capacity problem without fabricating families. Their dependence remains real: report family counts and concentration as well as 100 planned pair slots. This tests transfer within the specified relation/template boundary, not every possible semantic near miss. Keep family allocations and missingness independent of outcomes.

**Revision and composition.** Their isolated clone/restore design makes controlled interference tests possible, but distinguishes them from behavior in the complete retained 1,000-edit memory. Composition teaches just the relevant dependencies into an isolated clone and asks the source questions; it does not directly establish long-stream retained-memory composition. Moreover, X21-G6 found that the installed main analyzer drops the raw composition section. That should be repaired in an additive consumer before the final scientific report, or reported as an unfulfilled endpoint. Completing a job is not equivalent to completing its promised scientific analysis. The same applies to resource ratios still unavailable under X21-G7. [Concrete existing requests](tasks/R1-X21-edit-requests.md).

## 6. MQuAKE still earns its reduced place

I agree with DEC-060's 300-edit limit and DEC-066's prospective reduction to primary, random reader and v0_stable. It adds a different prompt/relation regime, a weaker selected-reader development result, an explicit failure of the admitted v0 geometry, and useful harm/composition questions. It is not necessary to run five nearly degenerate control configurations to learn that the particular calibration failed.

In the current cost model its **45 core cells cost about 30.84 expected process-hours**, approximately **7.9% of the 389.27-hour core scenario**. That is a reasonable return for the additional domain. These are estimates reconstructed from the typed cost components, not measured confirmation time. By comparison, CounterFact accounts for about 225.19 core process-hours and zsRE 133.24.

However, MQuAKE currently contributes **no available checkpoint-1,000 primary contrast**. All 21 registered component intervals remain unavailable; actual 300-edit results are descriptive. Keep that distinction rather than presenting a uniformly replicated three-dataset primary result. Radius-zero observations demonstrate limitations of a particular calibrated implementation, not impossibility for every positive radius or nonlearned reader. Omitted S1 arms are not measured zeros: different continued bases can differ from the original even with a disabled cap. D.4 states this more carefully than the abbreviated DEC-066 row, and its qualified wording should govern the report.

I would not expand MQuAKE again before October 9 or spend its remaining fresh-pool headroom on new development. Its remaining 211-subject clearance headroom is a constraint, not a general research reserve.

## 7. The κ and stress results are useful because the conclusions stay bounded

**κ:** the independently audited three-seed/dataset RET-GS means are .796111 ordinary, .754444 at κ=.2, .747778 at κ=.5 and .778889 for clip2. Both κ arms fail the declared .776111 retention floor and the seed-spread tail-separation criterion. The clipped control passes retention but has a CounterFact false fire where ordinary has none. I agree with DEC-054's decision rule and the resulting **no κ addition to the confirmatory matrix**. We should not pursue another κ or checkpoint merely to make the October story positive. [Independent pilot review](tasks/HT-3e.md).

The lower descriptive harm could partly reflect weaker useful intervention, rather than a better preservation–learning frontier. The next research question is matched-retention or matched-risk performance, with answer-loss and preservation-divergence changes separated. Also retain the implemented objective's distinction: bounded answer surprisal does not bound the full preservation objective or its gradients. The historical counter-review's claim that κ leaves the boundary decision unchanged is too strong: shared trained parameters can alter rejection even when the rejection loss formula stays ordinary. The later objective review and talk qualifications correctly narrow these statements.

**Stress:** all twenty old exact answers survived, while target-token probability harm appeared in CounterFact and MQuAKE. That is informative and complementary to exact-match retention. The two schedules had identical measured token changes at the recorded checkpoints. This does not establish resilience to general nonstationarity or a failed recovery mechanism.

There is a design limitation worth emphasizing: the schedules differ within the middle forty updates, but probes occur at edits 20, 60, 70, 80 and 100. The first probe after treatment is at its end, when both schedules contain the same fact set. We did not sample transient differences at 30/40/50 during the burst. The cap also has no demonstrated autonomous revisiting/repair policy. Persistent harm is an observation over this finite horizon, not proof of irreversible damage or failed active recovery. If a later bounded exploratory replay is desired, within-burst probes are more informative than merely adding another endpoint plot. It is optional; do not expand the current matrix or reinterpret the existing panel's censoring rule.

## 8. Protect scientific completion, not just cell completion

The cost repairs and explicit estimates are much better than the original approximate 15-hour envelope. Current expected totals are **389.27 core + 42.03 optional = 431.31 process-hours**, with **646.96** at the summed cell ceilings, below the shared **750** cap. The estimated 227.30 elapsed hours with the extension assumes the inherited 1.65× throughput. Memory at the full 1,000-record/S1 workload, interruptions, failed attempts and future concurrency remain important uncertainties. The October 9 stop remains firm. [Execution plan](R1_execution_plan_v3.md).

**I recommend discussing one change to DEC-051 before outcomes: finish the primary/random/v0_stable triplet across all three realizations first.** Keep all 285 core cells and all their populations, settings and measurements; change only scheduling priority through an explicit amendment. This produces the central complete paired panel sooner if a host problem or deadline interrupts the programme.

| Priority milestone | Cells | Expected process-hours | Elapsed scenario at inherited throughput |
|---|---:|---:|---:|
| Proposed: primary/random/stable across all three realizations and datasets | 135 | 147.83 | 77.91 h |
| Current: completion of blocks 1–4, including all six early conditions | 225 | 283.14 | 149.22 h |

These are different milestones, not claims of a faster implementation. Under the current ordering the full three-dataset central triplet panel is complete by the end of block 4; some individual comparisons become complete earlier. Reordering brings forward the central panel while leaving the final work unchanged. It **does not** repair the three-cluster inference problem. [Recomputed proposal](../logs/scientific_review_20260918/order-scenario.json).

After the triplet, finish matched-update/live controls and then the S1 controls. The historical-v2 extension should remain optional until the core is secure. If the existing ordering is retained, explicitly accept the chance of a broader collection of partial comparisons instead of an earlier complete central panel. Any stopping decision must be based on predetermined time/resource rules, not on whether interim scientific results look favorable.

My suggested programme to the deadline is:

1. **Before launch:** settle the scope/claim language and the statistical interpretation; decide whether to amend scheduling; keep selected weights, populations and thresholds fixed. Complete operational preparation without adding new scientific axes.
2. **At the first complete block:** reconcile actual process time, host/device memory and endpoint completeness against the estimates. Archive the small cost/memory extracts needed for the paper before the raw monitoring logs expire under their 48-hour retention policy. Numeric fidelity failures are reported outcomes, not grounds for silently dropping a cell.
3. **In parallel on CPU:** finish the composition consumer, measured resource/ceiling reporting, and the remaining X21 narrative fixes. Prepare per-realization plots, baseline-characterization tables and the frequency/severity views from saved observations. No retuning on confirmatory results.
4. **By October 3:** aim to have the core complete and a full first scientific report, so defects and incomplete endpoints can be identified while experimental time remains. This is a proposed internal target, not a guaranteed completion forecast.
5. **October 4–7:** finish authorized missing work and consider the optional extension only with demonstrated buffer. A new matched gate diagnostic, if chosen, needs a separate small exploratory scope and budget; it is not a replacement for any required core cell.
6. **October 8–9:** reserve for permitted failure recovery and completeness checks; preserve incomplete results honestly. **October 10–14:** analysis, figures, limitations and rehearsal on locked experimental data.

## 9. Decisions I would carry back to Claude

| Decision or group | My assessment | Action |
|---|---|---|
| DEC-033/034/035: stronger cap, diagnosis and controls | Good scientific direction; the current matrix is narrower than the full plan-9 programme | Explicitly defer the unperformed factorial/PC branches rather than implying they were tested. |
| DEC-037/039/042/045/048/060: training and final data sources | Usable under the disclosed exposure definitions; not pristine entity/domain transfer | Keep exclusions, chronology and the actual baseline behavior visible. |
| DEC-043/049/050: gating and selected reader | Sensible development selection; not isolation of learning or a reliability certification | Freeze the chosen package and distinguish selected-artifact validation from training-seed generalization. |
| DEC-040/047: continuation controls | Useful specified historical controls | Adopt the U03 qualification; do not claim exact-v5 compute matching. |
| DEC-044/052/065: enlarged budget and honest incompleteness | Reasonable only with measured reconciliation and the October 9 hard stop | Protect completion of paired comparisons; defer optional work when necessary. |
| **DEC-051: block order** | Coherent, but delays the complete central replicated panel | **Consider the 135-cell triplet-first order before outcomes.** |
| DEC-053/059/061/062: equality and secondary challenges | Defensible operational definitions | Preserve diagnostics, family structure, denominators and endpoint-specific limits. |
| DEC-054/055: κ and stress | Worthwhile bounded exploratory work; results do not justify broad theoretical claims | Keep the κ null; distinguish sparse harm from recovery and heavy-tail theory. |
| **DEC-057/058: inference and classification** | **Insufficient calibration for strong confidence claims; this is the main scientific concern** | **Resolve the interpretation or redesign now; publish the exact three-cluster limitation.** |
| DEC-063/064: full validation and cap-fidelity labels | I support the current separation of integrity, efficacy and preservation | Present failures beside efficacy; add frequency/severity interpretation without a new hidden selection rule. |
| DEC-066: reduced MQuAKE | Good return at its current size | Keep 300-edit/descriptive scope and do not impute outcomes for omitted arms. |

The strongest October contribution is a carefully delimited result: **a small frozen-base editing system can retain supplied knowledge while its rejection boundary and sparse probability harms remain measurable limitations; changing a loss can reduce observed harm while also reducing useful learning.** Fresh paired streams can tell us whether the selected package's advantages recur. They cannot, on their own, prove the larger coupled-active-inference theory or isolate every architectural cause.

## Evidence and limited operational appendix

This review follows the current D.4/D.3 amendments, plan 9, original and revised design documents, accepted decisions, installed adapter/assay/inference code, selection/teacher characterization, completed pilot and stress audits, full-validation vectors, cost components, report coverage reviews and presentation materials. It is not a new training run, a GPU replication, or a line-by-line proof of the whole repository. Scientific findings and proposals above take priority over administrative mechanics.

New evidence: [scientific diagnostic script](../scripts/r1_scientific_design_review.py), [31-source evidence record](../logs/scientific_review_20260918/evidence.json), and [unchanged-scope order/cost proposal](../logs/scientific_review_20260918/order-scenario.json). The coverage demonstration is synthetic mathematics; the four-vector recount is existing development evidence. Neither supplies confirmatory outcomes.

The targeted CPU regression across scope, inference, fidelity policy, endpoint construction, costs, production assembly, reporting and the fidelity watch finished **135 passed, one skipped** in 595.51 seconds. The skipped check deliberately avoids an assumption about live signing progress after a real session begins. [Test output](../logs/r1_63o/existing-tests.txt). Passing software tests establish tested implementation behavior; they do not establish the statistical validity questioned above. Both new inspection scripts pass Ruff.

The parallel R1-63o dependency inventory remains operational follow-up. It exposed stale active producer bindings and historical references that should not all be replaced with today's hashes. There are also endpoint-CLI/preview issues to address before actual execution. Those are repairable implementation concerns; they are not the reason for the scientific reservations above. No new package was declared frozen, and no existing protocol, decision, experimental source, signature or result was changed in this review. New package issuance should follow the resolution of any scientific amendments rather than precede it.
