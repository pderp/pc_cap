

# Current research status
PC_CAP  •  INTERIM RESEARCH PAPER  •  11 SEPTEMBER 2026
Continual learning throughpredictive-coding caps
Current evidence, confirmatory readiness, and the remaining research programme
pc_cap research project · Evidence synthesis prepared by CodexSource-of-truth plan: Goertzel &amp; Fable, revised 7 September 2026 [1].Evidence cutoff: 11 September 2026, 12:39:45 EDT (16:39:45 UTC).
Abstract
This project studies whether a small, bounded correction memory can teach a frozen language model new answers while preserving unrelated behavior. The central hypothesis is that measuring where an intervention helps, then routing learning to that location, improves retention relative to simpler delivery rules at comparable cost. A second thread separates the effects of an error-based predictive-coding substrate from those of its credit signal. The JAX apparatus, controlled fixtures, regenerated substrate, and frozen comparison schedule are implemented. Regeneration processed 50.002 million tokens in 12.18 local GPU-hours; the full fidelity audit measured mean KL divergence of 2.923 × 10−5 over 1,999,872 positions. Constructed examples validate useful routing, but short natural-language development runs do not demonstrate a routing advantage. At cutoff, five of 210 S4 jobs were complete, all C0 orders within one zsRE realization; the required C2 contrasts remain unmeasured. GRACE is excluded after its registration gate failed. A newly identified drift-evaluation sample mismatch requires lead review before plan-conformant drift claims. The project has reached confirmation early in its calendar, but a final scientific verdict and reliable resource forecast remain pending.
For a reader new to the project
Think of the base model as a reference book whose pages cannot be rewritten. The cap adds a limited set of notes that activate for relevant questions. The experiment asks both whether the notes last and where inside the model they should be applied. Remembering the exact question is easier than answering a rephrased question; the latter is the main test.
**Present conclusion** The apparatus supports a controlled experiment. It has not yet established that measured routing, predictive-coding conversion, or error-based credit improves continual learning. Development findings and partial confirmation are reported separately throughout.
Keywords: continual learning; activation memory; model editing; predictive coding; frozen transformers; paired experiments. This is an internal interim paper, not a peer-reviewed claim of efficacy.


# 1. Research question and experimental apparatus
1. Research question and experimental apparatus
Learning one correction can damage another when both use the same internal mechanism. The original plan asks whether targeted delivery can reduce that interference while preserving useful sharing. It explicitly separates the location of a helpful write, the representation carrying it, and the rule that computes the write direction [1].
Figure 1. Cap v0 on the frozen GPT-2 base. Banks attach after blocks 4, 8, and 12 (zero-based sites 3, 7, 11; the last before final layer normalization). Arrows show reads and additive writes; the drawing does not imply that every bank fires on every query [1,2].
![Figure 1. Cap v0 on the frozen GPT-2 base. Banks attach after blocks 4, 8, and 12 (zero-based sites 3, 7, 11; the last before final layer normalization). Arrows show reads and additive writes; the drawing does not imply that every bank fires on every query [1,2].](fig01_apparatus.png)
Table 1. Experimental arms
| Arm | Delivery or learning rule | Role |
| --- | --- | --- |
| C0 | Last bank only; the entire cap byte budget is at that bank. | Simple late-correction comparator. |
| C1 | All three banks share the total write-step budget. | Main distributed-delivery comparator. |
| C2 | Probe each bank; select the greatest positive loss improvement; abstain if none helps. | Measured routing hypothesis. |
| CR | Choose a bank randomly using probabilities fixed from development C2 deliveries. | Controls for where C2 tends to write. |
| CO | Supplied correct site in constructed fixtures only. | Diagnostic oracle; no natural-language claim. |
| B0 / B1 / B3 | Frozen base / rank-8 low-rank adaptation (LoRA) / the same adapter plus replay. | Baseline context; B3 enters confirmation. |
A slot stores an address, a correction, a radius and bounded metadata. Retrieval is gated by similarity; a miss leaves the base behavior intact. The base weights remain frozen during cap learning. Cap v0 is a PC-motivated activation memory: it does not itself run an autonomous predictive-coding inference process. JAX supplies CUDA execution; FabricPC and the sibling predictive-coding repository serve as read-only resources [1,2,14].


# 2. Frozen methods and decision criteria
2. Frozen methods and decision criteria
The development phase chose settings before the confirmatory data were opened. The v2 manifest binds the code tree, environment lock, tokenizer, base checkpoints, data identities, random seeds, scope, budgets and analysis rules. It was frozen at 16:17:30 UTC on 11 September. The present paper reads saved run summaries and source code; it does not open sealed item manifests or tune on confirmation [2].
Table 2. Outcome measures
| Measure | Meaning and interpretation |
| --- | --- |
| ES / GS | Immediate complete-answer accuracy on the edited question / its paraphrases. Free generation must match an accepted complete answer. |
| RET-ES / RET-GS | Accuracy after subsequent edits, on original questions / paraphrases. RET-GS is the primary endpoint; exact-edit retention is a companion. |
| LS | Agreement with the cap-disabled base on unrelated complete answers. Agreement measures preservation, not factual correctness. |
| LM drift | Perplexity ratio and mean loss change on held-out text. Ratio 1 means no measured drift on the evaluated sample; see the sample-size defect in Section 8. |
Each dataset uses three sampled stream realizations and five fixed orders per realization. The 15 orders are paired across arms, but they are not 15 independent datasets. Analysis resamples the three realization means, keeping all five orders together, using 10,000 bootstrap draws and two-sided 97.5% percentile intervals. This is a small-cluster uncertainty assessment [2,15].
**What would count as support?** For both C2−C1 and C2−CR: the RET-GS point gain must be at least 2 percentage points and its interval lower bound above zero. The ES lower bound must exceed −2 points, and the LS lower bound −1 point. Incomplete pairs are not imputed. Other outcomes are classified as qualified, inconclusive or negative under the frozen policy [2,15].
Table 3. Frozen job schedule
| Scheduled work | Scope | Jobs |
| --- | --- | --- |
| S4: C1, C2, CR, B3 | zsRE 1,000 edits; CounterFact 300; 15 runs per arm/dataset. | 120 |
| S4: C0 | Initial 300 edits per natural-language stream/order. | 30 |
| S4: grammar | C0/C1/C2/CR; eight tasks × 256 sequences/task; 15 runs. | 60 |
| S5: SE-A and SE-E | Two natural-language datasets × 15 runs × two new arms. | 60 |
The cap ceiling is 38,535,168 bytes (36.75 MiB), with 6,272 bytes per slot. Shared settings are A = 0.3, probe ε = 0.01, five rounds per target prefix, and edit-loss threshold 0.1 nats. Radii target ≤1% unrelated false firings. Matching total bytes does not match each bank’s capacity: interpret C0 versus distributed arms with that allocation difference and with C0’s shorter scope. Compute comparisons require measured update costs within 20%, or an explicit cost frontier [1,2].


# 3. Regenerated substrate: faithful, but not settled
3. Regenerated substrate: faithful, but not settled
The unavailable inherited checkpoint was replaced by a new, documented run. REG-02 finished 9,766 steps on 50,001,920 tokens, using a settling schedule T = 1, 2, 4, 8, 16, 32, 64. It consumed 12.18 local GPU-hours; the terminal summary reports 7,447 MiB peak memory. This is a regenerated substrate, not a recovered copy of the earlier research artifact [3].
Table 4. Full P1 fidelity audit
| Full P1 fidelity audit | Result | Interpretation |
| --- | --- | --- |
| Prediction positions | 1,999,872 | Held-out WikiText-103 train sample H. |
| Mean / 99th-percentile KL | 2.923e−5 / 2.445e−4 nats | Mean is below the 1e−3 eligibility ceiling. |
| Maximum finite KL / nonfinite positions | 0.1161 / 0 | A small average does not bound every token. |
| Teacher–student argmax agreement | 99.649% | Agreement, not answer accuracy. |
| Teacher / student mean NLL | 3.570225 / 3.569724 nats | Very similar predictive distributions. |
Figure 2. Actual regenerated ePC checkpoint, 64 development prompts (32 per natural-language dataset). Residual bars are prompt means, with no confidence intervals. The dashed line is only one part of the per-prompt convergence test. Cosines compare errors with the negative adjoint; high alignment is not evidence of editing superiority [4].
![Figure 2. Actual regenerated ePC checkpoint, 64 development prompts (32 per natural-language dataset). Residual bars are prompt means, with no confidence intervals. The dashed line is only one part of the per-prompt convergence test. Cosines compare errors with the negative adjoint; high alignment is not evidence of editing superiority [4].](fig02_epc_credit.png)
Eight-step credit is labeled finite-iteration error credit. Mean residual ratios are 0.404 at eight steps and 0.098 at 64; the maximum at 64 is 1.350. The declared settled criterion requires ≤0.001 for every prompt plus negligible final energy change. Mean energy falls by 2.423 nats, but settling is not established. Longer inference also reduces early-bank alignment with the adjoint in this diagnostic [4].
The full P1 record is preserved in Git commit 25c988b. Its live filename later held a 199,680-position follow-up, with a similar mean KL of 2.875e−5. This paper preserves and cites both separately. The regenerated parameters moved only 4.460e−4 in relative norm, so fidelity eligibility should not be read as evidence of a better learning substrate [3,4].


# 4. Constructed and learned synthetic evidence
4. Constructed and learned synthetic evidence
Two synthetic settings answer different questions. A constructed modular fixture has a known useful delivery site, making it suitable for checking the apparatus. A learned grammar has shared and private latent causes, so its internal organization must be measured rather than assumed. Both are development evidence [5,6].
Figure 3. A: useful-sharing fixture, 180 items per arm (60 private, 60 shared, 60 mixed); precision is measured over deliveries. B: grammar development, one realization and two orders, each eight tasks × 16 items. Bars are order means; dots show the two observed values, not confidence intervals. The panels use different metrics and populations [5,6].
![Figure 3. A: useful-sharing fixture, 180 items per arm (60 private, 60 shared, 60 mixed); precision is measured over deliveries. B: grammar development, one realization and two orders, each eight tasks × 16 items. Bars are order means; dots show the two observed values, not confidence intervals. The panels use different metrics and populations [5,6].](fig03_synthetic.png)
Constructed fixture: delivery can matter when the site is known
C2 and the oracle recover 180/180 items; C1 recovers 178/180, CR 170/180, and C0 46/180. C2 delivery precision is 87.9% and recall 89.4%, compared with C1 precision 48.1% and recall 100%. Recovery can therefore be perfect even when the measured delivery pattern is not identical to the oracle’s. The separate PC-1 controls recover 20/20 planted targets and 120/120 full-fixture cases, while a wrong router recovers only 1/30 in its negative control [5,11].
Learned grammar: exact edits succeed; generalization is restricted
Grammar RET-ES is 100% for C0 and C2, 70.3% for C1, and 91.4% for CR in both development orders. C2 RET-GS is 25.78% and 25.39%. No positive retrieval radius met the false-firing criterion, so the grammar uses exact keys. The report identifies these paraphrase scores as the base’s task-accuracy floor, not retrieval generalization. Locality is 100% on the tested prompts; the grammar drift ratio is a synthetic-domain diagnostic, not a WikiText language-model result [6].
The replacement grammar is available in the v2 freeze but remains provisional under PA-2 until 11 September at 23:59 Eastern. It must retain replacement provenance if the inherited artifacts do not arrive. Synthetic results establish controlled feasibility; they do not by themselves establish that the same latent mechanisms or routing benefits exist in natural language [2,6].


# 5. Natural-language development: a mixed result
5. Natural-language development: a mixed result
zsRE supplies question-answer edits; CounterFact supplies factual replacements and paraphrases. The revised throughput matrix evaluates 100 edits per arm and dataset in one development order. These runs selected and priced the experiment; they are not independent confirmation. Figure 4 uses the revised JSON records, including CR’s development-learned bank distribution [7].
Figure 4. zsRE complete-answer development metrics. Values are percentages; no uncertainty intervals are claimed for this single-order screen. CR is the learned-distribution random router (cr_dev_c2_zsre), despite a stale “uniform” label in one prose table. Locality uses the reported development probe set [7].
![Figure 4. zsRE complete-answer development metrics. Values are percentages; no uncertainty intervals are claimed for this single-order screen. CR is the learned-distribution random router (cr_dev_c2_zsre), despite a stale “uniform” label in one prose table. Locality uses the reported development probe set [7].](fig04_natural_language.png)
C2 reaches 99% immediate edit success but retains 30% paraphrase success, compared with 31% for C1, 38% for learned CR and 43% for C0. The corresponding retained exact-edit rates are 94%, 90%, 77% and 99%. Thus the current natural-language screen does not support the central routing advantage. C2 routes about 97% of zsRE deliveries and all CounterFact deliveries to the last bank; the learned CR comparator is deliberately matched to this late-bank preference [7].
Table 5. CounterFact development
| CounterFact development | ES | RET-ES | RET-GS | LS / drift ratio |
| --- | --- | --- | --- | --- |
| C0 / C1 / C2 / CR | 100% | 100% | 0% | 100% / 1.00 |
| B1: LoRA | 8% | 11% | 5.5% | 0% / 3.17 |
| B3: LoRA + replay | 7% | 10% | 6.5% | 0% / 3.94 |
CounterFact’s calibrated exact-key gate fits original answers but transfers to none of the tested paraphrases. Its zero cap RET-GS is therefore a consequential limitation of this registered retrieval setup. Perfect locality and a drift ratio of 1 on small probes do not establish that the method learns broadly useful corrections. They must be interpreted together with this lack of generalization [7].
B1 and B3 use rank 8, ten Adam steps and the shared learning rate 1e−4, selected by mean development RET-GS across both datasets. Their weak acquisition and locality restrict the breadth of the baseline comparison. They do not show that cap v0 outperforms all well-tuned editing methods. B4/GRACE would broaden that comparison, but its gate remains failed [2,7,10].


# 6. Mechanistic evidence and interpretation limits
6. Mechanistic evidence and interpretation limits
The grammar P4 study asks whether errors associated with different causes occupy different directions in the model’s internal space. It measures the declared eight-step ePC solver on a grammar model trained with backpropagation, not an ePC-trained grammar and not GPT-2 natural-language domains [8].
Figure 5. P4 uses 8,192 vectors per cause kind, six block outputs, width 128 and rank-16 bases. A: mean subspace overlap (diagonal is 1 by definition); independent random rank-16 subspaces would have expected overlap 16/128 = 0.125, a reference value rather than a significance test. B: held-out projection capture for matching and nonmatching mechanism changes, averaged over layers [8].
![Figure 5. P4 uses 8,192 vectors per cause kind, six block outputs, width 128 and rank-16 bases. A: mean subspace overlap (diagonal is 1 by definition); independent random rank-16 subspaces would have expected overlap 16/128 = 0.125, a reference value rather than a significance test. B: held-out projection capture for matching and nonmatching mechanism changes, averaged over layers [8].](fig05_mechanism.png)
Between-kind overlaps are 0.268–0.351. The bases are stable under resampling (minimum overlap 0.933), and rank 16 captures 98.6% of measured error variance. Held-out private-only and shared-only changes are largely captured by the matching basis (0.963 and 0.994), with lower cross-capture (0.208 and 0.211). This supports a reproducible distinction between these constructed cause kinds [8].
However, private-versus-private contexts overlap by 0.927. “Private” therefore does not mean a separate orthogonal subspace for each context. Natural-language domain PCA remains unsupported. The appropriate claim is structured grammar error geometry, not a general discovery that unrelated knowledge naturally occupies independent compartments [8].
Helpful repair is not necessarily the location of the mechanism
Grammar routing illustrates this distinction: shared-1 deliveries favor bank 1 (89.3%), but shared-2 deliveries reach bank 2 only 2.1%, even though causal tracing identifies bank 2 as its earliest restoring site. A loss-minimizing local write can exploit a downstream shortcut. Router preference, causal tracing, error geometry and retained accuracy are complementary measurements, not interchangeable proof [6,8].
Production S7 reversals will directly test whether the order of two updates changes retention or damages earlier answers. The repaired harness starts reversals from the same full state, averages damage over every evaluation prefix, preserves original prompt boundaries, and uses disjoint grammar seeds. Its pair inventory is ready; checkpoint outcomes and semantic contradiction review are still due [12].


# 7. GRACE baseline: exclusion and numerical diagnosis
7. GRACE baseline: exclusion and numerical diagnosis
GRACE is a retrieved-correction editing baseline being ported to JAX. The port matches all 40 tested greedy-output/NLL comparisons and all keys, radii and labels across 20 isolated and 20 sequential cases. All 40 learned-value comparisons fail, with a maximum absolute gap of 22.439. The conditional registration rule also required a preregistered same-framework sensitivity control to reproduce the divergence class. Its largest reassociation gap was only 0.153, below the fixed 2.244 threshold [9,10].
Figure 6. Two fixed CPU diagnostic cases. The reference forward graph is unchanged; only the head and loss cotangents are recomputed in float64 during backward replay. The comparison gradient is the unchanged JAX gradient. This experiment localizes a numerical contribution; it is not a repeated optimizer trajectory or a replacement registration control [9].
![Figure 6. Two fixed CPU diagnostic cases. The reference forward graph is unchanged; only the head and loss cotangents are recomputed in float64 during backward replay. The comparison gradient is the unchanged JAX gradient. This experiment localizes a numerical contribution; it is not a repeated optimizer trajectory or a replacement registration control [9].](fig06_grace_numerics.png)
Round-four diagnostics compare 27 common-input components per case. The initial full-gradient relative gaps are 2.197e−4 and 1.279e−4. Replaying both head and loss reductions in float64 lowers them to 1.438e−5 and 1.001e−5, reductions of about 15.3× and 12.8×. Replacing either reduction alone can worsen the second case because errors partly cancel. A single local discrepancy should not be assigned the whole later value divergence [9].
The tested JAX reductions are closer to the float64 reference at the localized boundaries. No formula, mask or position-index defect was found in those checks, and no candidate learner repair was justified. The remaining gap is nonzero; the two-case experiment does not explain all 100 optimizer steps or establish that large learned-value differences are harmless [9].
**Current programme decision** B4 is unavailable in the frozen month programme (DEC-020; updated plan 8). Its 30 comparison jobs are not scheduled. This is a missing baseline, not a failed scientific comparison of C2 against a valid B4. Later inclusion requires a justified gate, a versioned manifest and its own runs [2,10].
A bounded later study could repeat fixed reduction probes across the already saved parity cases and ask whether early gradient discrepancies predict trajectory differences. It should not search perturbations until a threshold is crossed, relax the current gate after seeing outcomes, or consume the core comparison budget merely to make the port registrable.


# 8. Confirmatory snapshot and a protocol gap
8. Confirmatory snapshot and a protocol gap
At 12:39:45 EDT, 5/210 S4 jobs were complete (2.38%), with 205 remaining. All five were zsRE/C0, realization 0, orders 0–4, at 300 edits per run. Their saved configuration and metrics agree with the frozen v2 identity, and their before/after base hashes match. There were no v2 failed cells or resource stops in the captured queue. No C2−C1 or C2−CR confirmation is yet available [13].
Table 6. Partial C0 confirmation
| Order | Edits | ES % | RET-ES % | RET-GS % | LS % |
| --- | --- | --- | --- | --- | --- |
| 0 | 300 | 100.00 | 99.33 | 34.00 | 99.0 |
| 1 | 300 | 99.67 | 98.33 | 36.33 | 95.5 |
| 2 | 300 | 100.00 | 98.33 | 39.33 | 96.5 |
| 3 | 300 | 100.00 | 99.33 | 32.67 | 99.0 |
| 4 | 300 | 100.00 | 99.67 | 37.67 | 96.5 |
Descriptive C0 results, not a routing comparison. Each row has 300 editing items and 200 locality probes; orders share one realization and can select different 300-item prefixes of its 1,000-item scope. C0’s 300-edit endpoint cannot be compared directly with another arm’s 1,000-edit endpoint. Do not pool the rows as five independent samples [2,13].
Failure encountered and repaired before v2
The original v1 freeze produced 50 no-item failures: a loader incorrectly applied a realization-filename rule to the grammar’s .npz resource binding. No edited-item results were produced. The attempts were archived, the loader received a regression, and the queue now stops after three consecutive no-item failures. A newly frozen v2 binds the repaired source. The incident shows why passing component controls did not guarantee a usable end-to-end queue [2].
**New finding: LM-drift coverage does not meet the plan** The PDF requests one million WikiText-103 validation tokens. SD-3 explicitly substitutes the whole available split: 247,289 unique tokens (DATA-04). S4 instead requests 4,096; its evaluator scores 32 windows × 127 next-token positions = 4,064 positions. Every row above reports that count, and S5 also selects 4,096. This is about 1.64% of the approved split’s token count; window boundaries also affect the exact scored-position denominator [1,2,13,15,17].
All five rows report drift ratio 1.00 on that small sample. The result may be correct for those positions, but it does not complete the whole-split assay authorized by SD-3. This review found no authorization for that further reduction. The lead should assess a versioned repair or an explicitly approved, checkpoint-based completion of the missing evaluation, with all cost charged. Changing the frozen source silently is not an acceptable remedy. The review itself has not altered or stopped the active queue.
Locality here is also the 200-prompt development unrelated pool, not evidence of complete near-neighbour challenge coverage. The registered challenge sets and their separate reporting remain necessary. The drift discrepancy does not by itself prove ES or RET-GS wrong; it limits protocol completion and the scope of collateral-damage claims.


# 9. Verification, reproducibility and evidence quality
9. Verification, reproducibility and evidence quality
The project has substantial correctness evidence, including independent review and repaired counterexamples. Such controls verify specified behavior on their inputs; they do not establish statistical superiority or guarantee that every reporting contract has been implemented. The newly found drift gap illustrates the remaining distinction [11,12,14,15].
Table 7. Verification coverage
| Evidence group | What is established | Boundary |
| --- | --- | --- |
| Core controls PC-1…PC-9 | Acquisition fixtures, exact cap-off identity, idempotence, rollback, signed probes, budgets, complete-answer scoring, read-only evaluation and cloning. | The table in docs/controls.md distinguishes CPU and GPU evidence and implemented variants. |
| Round-four CPU audit | 63 controls/known-answer tests, including the full PC-1 fixture; eight snapshot/resource/collector tests; nine S7 regressions. | PC-10 is explicitly excluded as a known failure; counts are not line coverage. |
| GPU window 2 | 46 GPU tests, including real-artifact identity checks and negative refusals. | Previously recorded evidence reviewed here; no GPU rerun for this paper. |
| Environment recreation | ENV-05 recreated the scratch environment with 150/150 pinned packages. | An install audit is distinct from full research-result reproduction. |
| Reproduction pre-audit | 27 CPU command invocations; 24 initially returned zero; three issues were examined in isolated follow-ups. | A sibling path, an assets-relative data path and completed-output rerun semantics required clarification. |
What the two agents have contributed
The execution agent has built the apparatus, regenerated and characterized the substrate, calibrated the cap and baselines, repaired reviewed defects, prepared the frozen schedule and started confirmation. Codex’s concurrent work has supplied baseline-parity diagnostics, independent harness and S7 reviews, control coverage, resource/collector checks and reproduction pre-audits. Implementation and independent review have strengthened the apparatus; control pass counts remain distinct from efficacy [2,9,11,12,14].
A version-aware evidence trail is essential
Several narrative summaries lag behind the machine artifacts: ongoing notes still contain an old “GPU idle” statement; the queue summary describes a bounded earlier session; a CR row is mislabeled uniform; P6 retains a stale BP-wrapper description despite its actual ePC checkpoint path; and the full P1 file was later replaced by a smaller follow-up. This paper resolves those cases using frozen identity, saved values and Git history, and captures the actual source bytes in its evidence bundle [2,4,7,13].
The reproducibility follow-up reports 356 passed, five skipped and 52 deselected CPU tests with the sibling resource path explicit. This is a scoped command result, not “all tests pass.” Before final delivery, the owner should rerun the documented commands against the final artifact set and retain both failed attempts and their resolved successors [14].


# 10. Resource outlook: accounting before confidence
10. Resource outlook: accounting before confidence
The original plan assigns 154 A100-equivalent hours across S0–S8. Actual work runs on a local RTX 5070 with 12 GiB memory. The conversion κ = 1 local hour per A100-equivalent hour is provisional, with a declared 0.5–2 sensitivity band and no measured A100 reference. Local measurements should therefore be reported directly alongside the provisional normalization [1,16].
Figure 7. Recorded local accelerator cost versus projections. Dashed markers show frozen allowances after 25% headroom: S4 27 h and S5 18 h. *The second row only subtracts the excluded B4 components (5.47 h) from the selected S4 arithmetic; it is not a refreshed queue or evaluation-cost model. REG-02 is observed consumption and is charged to S6, not added to S4 [2,3,16].
![Figure 7. Recorded local accelerator cost versus projections. Dashed markers show frozen allowances after 25% headroom: S4 27 h and S5 18 h. *The second row only subtracts the excluded B4 components (5.47 h) from the selected S4 arithmetic; it is not a refreshed queue or evaluation-cost model. REG-02 is observed consumption and is charged to S6, not added to S4 [2,3,16].](fig07_resources.png)
The selected S4 projection is 26.31 h, but still contains 5.47 h of assumed B4 work even though B4 is unavailable. Removing those terms gives 20.84 h arithmetically. Grammar costs are now measured despite a stale “unpriced” status string. Neither calculation incorporates a whole-validation drift assay under SD-3. The practical next step is an accounting reconciliation against the frozen scheduled jobs and actual evaluation requirements, without retuning the scope from outcomes [16].
S5 is projected at 12.85 h against an 18 h allowance. It uses SE-A/SB and SE-E/SB factors of 0.991 and 1.357 from a 20-item zsRE smoke test, extrapolated to CounterFact. SB reuses S4 C1 runs and is charged once. These are useful planning estimates, but setup, rescoring, sequence lengths, stream growth and dataset differences can change the ratios [16].
Why accelerator hours are not an elapsed-time promise
The captured progress tool estimates 50.2 wall-hours remaining for S4. Only 10 remaining jobs use observed same-arm timing; 195 rely on projection, including a fixed 2.5 wall/accelerator multiplier. The median observed C0 queue time is 243.2 seconds. This is a heuristic ETA, not a confidence interval or a measured rate for C1, C2, CR, B3 and grammar [13].
Per-run allowances are 2,400 accelerator seconds; stage allowances are 97,200 for S4 and 64,800 for S5. Resource stops preserve the completed prefix and charge failed work. Checks at item boundaries can overshoot by in-flight work. Final evaluation and all archived attempts must remain in the audit. At κ = 2, the existing scope table has no affordable selection; normalization uncertainty is a material budget issue, not a reason to silently increase the budget [2,16].


# 11. Timeline assessment and the critical path
11. Timeline assessment and the critical path
D0 is 9 September 2026 (DEC-000); this snapshot is day 3 of the month programme. The plan was revised on 7 September and the repository began earlier than D0, so neither date should be mistaken for the execution clock. The original schedule placed foundation work in week 1, mechanism screening and freeze in week 2, confirmation in week 3, and final synthesis in week 4 [1,2].
Figure 8. Approximate windows from the original month plan, alongside the day-3 evidence state. The early start of S4 is real implementation progress. Bar lengths are planned calendar windows, not measured completion or promises about remaining work [1,2,13].
![Figure 8. Approximate windows from the original month plan, alongside the day-3 evidence state. The early start of S4 is real implementation progress. Bar lengths are planned calendar windows, not measured completion or promises about remaining work [1,2,13].](fig08_timeline.png)
**Schedule judgment** Implementation and freeze milestones have arrived earlier than their original windows. Overall completion cannot yet be called secure: only 2.38% of S4 jobs are finished, the required contrasts are absent, S5 and S7 outcomes remain, and the unresolved drift-evaluation gap can change the critical path. A task-board completion count is not a measure of completed scientific evidence.
Updated plan 8 estimates about 60–80 wall-hours for S4 and 30–40 for S5 when serialized on the GPU lease. Together those planning ranges imply roughly 3.75–5 days of uninterrupted device availability before subsequent work, excluding any evaluation repair. The later live S4 heuristic is shorter, but mostly extrapolated. These estimates are compatible with the original month window under favorable operation; they do not establish that the project is ahead by a specific number of days [2,13].
The next bottleneck is accepted, complete paired evidence. S4 must yield matched required-arm coverage; S5 can follow or interleave by realization once reusable C1 runs exist. S7 depends on committed 300-edit or grammar task-4/8 checkpoints, fixed pairs and semantic review. Final S8 audit and reporting depend on those outputs, the cost ledger and resolution of reporting gaps [2].
S6 conditional re-distillation is closed for this month (DEC-022), because regeneration used much of that allocation and a matched continuation pair does not fit. A future proposal may be written from S5 evidence, but S6-02…05 are not scheduled. This is an explicit scope decision, not a task that should silently return to the GPU queue.


# 12. Risks, decisions and available parallel work
12. Risks, decisions and available parallel work
Table 8. Risks and responsibilities
| Issue / priority | Consequence | Next action and boundary |
| --- | --- | --- |
| Drift sample mismatch — immediate | The 4,064-position results do not cover the approved validation split; a correction may materially alter cost and schedule. | Lead: decide a documented, versioned remedy. CPU reviewer: specify expected coverage and checkpoint evidence. Any GPU rescore uses the lease. |
| Missing comparative evidence — high | Five C0 orders cannot establish C2 superiority or ePC benefit. | Run owner: finish frozen pairs before optional experiments; analysis owner: reject missing cells, mismatched scopes and mixed identities. |
| Only three independent realizations — high | Intervals have limited resolution and may underrepresent broader uncertainty. | Retain all orders and show realization-level effects. Report qualified/inconclusive outcomes honestly; expand replication only in a later protocol. |
| Exact-key generalization limit — high | CounterFact cap RET-GS is zero in development; grammar paraphrases remain at the base floor. | Keep RET-GS primary. Diagnose retrieval and feature invariance separately; preregister future retrieval changes rather than switching the endpoint. |
| GPU / budget forecast — high | One device, extrapolated costs, provisional κ and a larger drift assay could exhaust headroom. | CPU: reconcile ledgers and excluded B4 pricing. GPU owner: preserve complete pairs, monitor resource stops and serialize expensive jobs. |
| Baseline breadth — moderate | B4 is unavailable; B1/B3 development acquisition is weak. | Disclose the missing contrast and tuning rule. Continue B4 numerics only as bounded, separate diagnostics. |
| S7 pair semantics — moderate | CounterFact shared pairs number 9 instead of the target 34; structural strata are only proxies. | CPU: semantic contradiction review before outcomes. Retain stratum counts and qualification; production reversals await checkpoints. |
| Provenance drift — moderate | Overwritten summaries and stale labels can lead to unsupported claims. | CPU: preserve immutable evidence copies, full P1 history, source hashes and per-claim denominators; final reproduction checks the release bundle. |
Concurrency does not require shared-source edits. Independent CPU lanes can prepare coverage validators, review the pair inventory, audit resource arithmetic, write evidence tables and reproduce reporting commands in new output locations. Claude retains the active run queue and GPU lease. No agent should change the frozen src/pccap tree without the versioned approval process [2,11–16].


# 13. Remaining checkpoints and scientific direction
13. Remaining checkpoints and scientific direction
Table 9. Remaining completion checks
| Checkpoint | Concrete completion evidence |
| --- | --- |
| Resolve evaluation contract | A lead decision on the drift mismatch; a named sample, recorded evaluated-position count, matching checkpoints, proper cost treatment and a plan-conformant report or explicit disclosed limitation. |
| S4: finish and audit | Complete required C1/C2/CR matrices for each dataset and frozen scope; paired 97.5% intervals, ES/LS constraints, cost views and resource-stop accounting. Keep C0 and B3 comparisons scope-aware. |
| S5: isolate substrate from credit | SB = BP + C1 + adjoint (reused); SE-A = ePC + C1 + adjoint; SE-E = the same ePC + C1 + eight-step error credit. Report SE-A−SB separately from SE-E−SE-A. |
| S7: direct interference | Semantically reviewed fixed pairs, correct selection hash, identical reversal starts and complete-prefix damage; report both orders and all strata, including the nine-pair CounterFact shared stratum. |
| S8: final deliverable | Reproduce the final artifact set, reconcile all costs and deviations, issue positive/qualified/inconclusive/negative classifications, and complete licensing/publication review (T4). |
Where the evidence suggests focusing next
First, complete the registered comparison and resolve evaluation coverage. The natural-language development signal is not a reason to abandon a controlled negative result: it may show that this measured router spends extra probing effort while behaving mostly like a late-bank editor. Compare C2 with learned CR at measured cost, and examine acquisition, forgetting and retrieval failures separately.
Second, keep exact recall and generalization distinct. If exact-key retrieval remains the dominant bottleneck, a future study could test more paraphrase-stable keys or a different retrieval rule under the same locality and memory constraints. Those changes need a new development phase and frozen experiment; current RET-GS must not be replaced after results become visible.
Third, retain the substrate/credit separation. The regenerated model is highly faithful but only slightly different from BP, and its errors are not settled at the chosen iteration count. An absent SE-A gain would limit claims about this conversion, while an SE-E difference would concern finite-iteration credit. Neither result alone settles the general value of predictive coding.
The frozen exploratory list includes cap-disabled keys versus ordinary residual keys, half/double memory, difficulty weighting, and optional error/gradient keys only if their implementation and isolation controls exist. These are three-realization, two-order exploratory studies, dropped before any core pair. Optional Hessian diagnostics and additional re-distillation should not displace direct order-effect tests or the main evidence [1,2,11].
Conclusion
The working apparatus demonstrates controlled acquisition, substrate fidelity and reproducible synthetic error structure. The main continual-learning advantage remains unproven. A rigorous finish requires complete paired outcomes, resolution of drift-evaluation coverage and transparent costs. A well-supported negative result would also be a useful outcome.


# Supplementary property scorecard: P2, P3 and P5
Supplementary property scorecard: P2, P3 and P5
The substrate programme includes three further diagnostics that help explain what the base makes available to a cap. They describe feature diversity, gradient concentration and the reach of writes. They do not replace retained-answer comparisons, and geometric quantities depend on the chosen coordinates [1,18].
Figure 9. Effective rank summarizes how many directions carry substantial feature variation; it is not an accuracy score or a count of stored facts. Values use 4,096 sampled positions on the regenerated ePC base. Site labels follow the recorded P2 convention, including the pre-final-normalization site at block 12. No uncertainty interval is inferred [18].
![Figure 9. Effective rank summarizes how many directions carry substantial feature variation; it is not an accuracy score or a count of stored facts. Values use 4,096 sampled positions on the regenerated ePC base. Site labels follow the recorded P2 convention, including the pre-final-normalization site at block 12. No uncertainty interval is inferred [18].](fig09_feature_rank.png)
Table 10. Additional property diagnostics
| Diagnostic | Observed result | Interpretation |
| --- | --- | --- |
| P2: representation structure | Effective rank 103.3 at the embedding, peak 349.4 at site 9, and 104.4 at site 12. Best part-of-speech probe accuracy 91.81% on 5,040 held-out labels. | Features carry recoverable linguistic information; neither rank nor a probe establishes better continual learning. |
| P3: adjoint localization | 1,000 sequences; raw normalized participation ratio 0.1745; final-block share 0.01098. Layer-normalized participation ratio 0.1158. | The diagnostic uses the BP adjoint on the ePC base. Gradient mass is not all at the last block; coordinates and layer normalization change the statistic. |
| P5: write locality | 200 edit prompts and 200 unrelated probes. Banks 1/2/3 achieve a 50% current-token loss reduction on 94.5% / 100% / 100% of edit prompts. | Median normalized write norms at the target are 0.80 / 0.20 / 0.05. Ease of correcting one token is distinct from retained complete-answer success. |
P5’s mean unconditional collateral KL is 1.086, 0.137 and 0.202 nats for banks 1–3, respectively. This deliberately applied-write assay is different from deployed retrieval gating. A separate A = 0.3 development gate screen records zero firings on 1,000 unrelated probes per dataset; that is finite probe evidence, not a universal locality guarantee [18].
These diagnostics help explain why useful routes and anatomical mechanisms need not coincide: late writes can reduce immediate loss with smaller normalized increments, although most raw gradient mass lies elsewhere. Retrieval-key drift still requires saved-learner checkpoint analysis. The stronger question—whether such local advantages improve acquisition, retention and sharing at matched cost—remains with S4, S5 and S7.


# References, data availability and provenance
References and data availability
References below identify local primary evidence, relative to the pc_cap repository. The accompanying evidence_final.json captures source contents and SHA-256 hashes at the stated cutoff; it includes aggregate completed-run records but no sealed item manifests. Figures are generated from that snapshot, not from hand-entered visual estimates. The original plan PDF is the scientific authority; decisions document subsequent operational resolutions.
[1] Goertzel, B., &amp; Fable, C. (2026). A One-Month Programme for Continual-Learning Predictive-Coding Caps on GPT-2-Scale Transformers. Readable edition, revised 7 September.
docs/pc_cap_month_plan_readable.pdf; extracted text: docs/pdf_text/plan.txt
[2] Frozen protocol, decisions and current plan delta. DEC-000, 020, 022, 025–027; freeze timestamp is read from the manifest.
manifests/frozen.json; docs/decisions.md; docs/updated_plan8.md; docs/ongoing.md
[3] REG-02 regeneration and preflight.
results/REG/epc-50m/summary.json; results/REG/preflight.json
[4] Substrate fidelity and finite-iteration credit diagnostics. Full P1 is the historical blob at commit 25c988b; the current P1 is a smaller follow-up.
git show 25c988b:results/S1/P1_epc.json; results/S1/P1_epc.json; results/S1/P6_epc.json
[5] Constructed fixture study.
results/S3/fixture/summary.json
[6] Replacement grammar development and routing versus tracing.
results/S3/grammar_dev_matrix.json
[7] Revised natural-language development and random-router policy.
results/S2/throughput_v2.json; results/S2/throughput_v2_baselines.json; manifests/cr_distribution.json
[8] Grammar error geometry, P4.
results/S1/P4_gram.json
[9] GRACE round-four localization and backward replay.
results/S2/grace_jax/gradient_localization/{candidate,head_loss_probes,reduction_replay_candidate}.json; logs/grace_gradient_localization.md
[10] GRACE registration gate and preregistered sensitivity.
results/S2/grace_jax/pc10.json; results/S2/grace_jax/sensitivity.json; docs/updated_plan8.md
[11] Control coverage and round-four CPU audit.
docs/controls.md; results/S3/control_audit_round4/run.json
[12] Independent S7 repair and pair-inventory review.
logs/review_p4_s7_r2.md
[13] Completed v2 run records and queue snapshot (12:39:45 EDT).
results/S4/frozen-confirmatory-v2-84126123/zsre/C0/BP/h/0/{0,1,2,3,4}/{config,metrics}.json; results/S4/queue.jsonl; results/S4/jobs.json; scripts/s4_progress.py
[14] Environment and reproduction evidence.
docs/environment.md; docs/REPRODUCE.md; logs/reproduce_preaudit.md; logs/reproduce_round4/{summary,followup}.json
[15] Analysis implementation and evaluation coverage.
src/pccap/analysis/{bootstrap,paired}.py; src/pccap/harness/{stage_s4,stage_s5,stage_s3,runs}.py
[16] Projection and provisional hardware conversion.
results/S2/projection.json; results/S5/projection.json; results/ENV/kappa.json
[17] Approved whole-validation drift corpus (SD-3 / PA-5); 247,289 unique tokens.
docs/spec_defects.md; docs/tasks/DATA-04.md; manifests/dev/lm_sets.json
[18] Additional regenerated-substrate property diagnostics.
results/S1/P2_epc.json; results/S1/P3_epc.json; results/S1/P5_epc.json


# Technical appendix: identity and reading guide
Technical appendix: identity and reading guide
Bound identities at the evidence cutoff
Experiment
frozen-confirmatory-v2-84126123
Evidence cutoff (UTC)
2026-09-11T16:39:45+00:00
Repository HEAD at capture
6a1cf590e74a514577344bed35f500239ee0e4c5
Frozen manifest SHA-256
84126123f48c83e9270d6995335e86562e733efab7926ffa3178daadc5305a1f
Frozen src/pccap tree SHA-256
0f20e120067b40eb09f346ebaa5f83578b325c581125eb0e86faa9d98d14e22f
Plan PDF SHA-256
9a2b64680452394a57da6d07536f00b215320bdd2e7deef65e9f3bec3d359080
Frozen environment lock SHA-256
b8bc3a542813e294ece6c9fe6eb957287414d412738e31638dbc69bbcea524bb
Regenerated checkpoint SHA-256
ea4c561d3963ffd89f866337ef5e789a4ef15b7558b4c717594dbef88cd26f51
The freeze records a dirty working tree and an earlier Git HEAD because the lead commits separately. The frozen source-tree hash is therefore the operative code identity; a later repository commit alone does not imply different scientific code. The active queue continued after this report’s cutoff. None of its later results are silently included [2,13].
Compact glossary
Table 11. Glossary
| Term | Reading guide |
| --- | --- |
| Predictive coding / ePC | A model formulation with explicit errors and iterative inference; here, error-optimizing predictive coding. This month also studies a simpler correction memory motivated by that idea. |
| Adjoint / credit | The gradient of loss with respect to an internal vector / the signal used to choose a correction direction. |
| KL / NLL / nats | Distribution discrepancy / negative log-likelihood / natural-log units. Lower usually indicates closer distributions or less prediction loss. |
| Realization / order | A sampled set of learning items / a permutation of that set. Orders share a realization and are statistically dependent. |
| Frozen protocol / checkpoint | A bound experimental specification / a saved learner state. Freezing a protocol does not mean every part of the implementation is already proven correct. |
Reproduction: use capture_status_evidence_v2.py only for a new dated snapshot. Build this exact paper from the saved evidence_final.json using build_status_paper_v4.py and a new output directory. The renderer records layout checks and exports all nine figures as PNG and vector PDF. Findings are limited to GPT-2-scale editing and synthetic tasks; broader domain adaptation is deferred. The paper contains no new GPU experiment and does not change production code, thresholds, task boards or prior evidence.
