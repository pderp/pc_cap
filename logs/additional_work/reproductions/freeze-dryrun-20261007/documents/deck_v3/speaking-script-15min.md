# 15-minute speaking script — draft for charlie

Updated 2026-10-04 by Capex from the twelve slide drafts. **Author review and
rehearsal required; this is a duration option, not a confirmed conference slot.**
Clock includes slide changes and pointing pauses, excludes audience Q&A. Read
only the paragraphs under “Say”; source/cut notes and tables are not spoken.

Completed result values remain literal source slots here. The presentation
export resolves them from `pc-result-sources.json`; an absent source
renders PENDING, never zero. If still pending at rehearsal, say “this comparison
is pending; I cannot yet report a direction or effect” instead of the numerical
paragraph. Do not read placeholder braces aloud or imply completion prematurely.

Word counts approximate slot values as three spoken words and omit the displayed
equation. Rehearse again after filling actual numbers, particularly realization
lists; timing is a target, not a measured delivery duration.

| Slide | Running clock | Allocation | Approximate spoken words |
| --- | --- | --- | --- |
| 1 | 00:00–00:50 | 50 s | 92 |
| 2 | 00:50–02:15 | 85 s | 163 |
| 3 | 02:15–04:05 | 110 s | 195 |
| 4 | 04:05–04:40 | 35 s | 71 |
| 5 | 04:40–05:55 | 75 s | 110 |
| 6 | 05:55–07:05 | 70 s | 122 |
| 7 | 07:05–08:10 | 65 s | 102 |
| 8 | 08:10–09:00 | 50 s | 81 |
| 9 | 09:00–10:50 | 110 s | 158 |
| 10 | 10:50–12:25 | 95 s | 115 |
| 11 | 12:25–13:50 | 85 s | 107 |
| 12 | 13:50–15:00 | 70 s | 131 |

Total allocation: **15:00**.

Short-version cuts follow the outline: slides 4–5 form one 1:50 unit
(35 seconds of design, then 75 of results); slides 6–7 form one 2:15 unit.
Keep both slide numbers for the existing figure files and advance at the stated
clock. The kappa and mixture section is 50 seconds; detailed settling diagnostics, operation
tables, comparator breakdowns and process accounting move to backup. Retain the
active-inference opening and return, corrected-PC comparison and empirical tails.

## Slide 1 — Three questions for Active Inference in the Extremes

**00:00–00:50; 50 seconds.**

Say:

Our question is how a small adaptive system on a frozen language model could learn useful corrections while remaining attentive to their unintended consequences. That connects the three themes of this session: active inference, predictive coding, and heavy-tailed distributions.

Active inference asks what to do next. Predictive coding gives us a question about how to learn a correction. The study of extremes asks whether a few predictions can become much worse even when the average change is small. I will distinguish the proposed agent from the components and measurements we have tested.

Evidence: `AI-loop`, `AI-next`, `AI-programme`, `AI-testbed`, `HT-readout`, `PC-mechanism`, `PC-v0`, `R1-retention-counterfact`, `R1-retention-zsre`, `R1-specificity`; [source draft](slide01-three-questions.md).

## Slide 2 — From active inference to a testable adaptive system

**00:50–02:15; 85 seconds.**

Say:

On the right of this diagram is a pretrained transformer. In the main condition its weights stay fixed, supplying predictions and representations. In the middle is the adaptive cap: it stores corrections, decides when a memory applies, and supplies bounded changes to internal representations. A null decision lets it leave the original prediction alone.

On the left are the edits and evaluation questions supplied by us. That is the boundary of the present experiment. The system does not yet choose its own audit by comparing expected information and preferred outcomes. The dashed return loop represents that proposed extension.

This architecture gives us a testbed for two questions: which learning signal makes a useful correction, and what else does the correction change? The software interfaces do not themselves establish a Markov blanket or coupled free energy.

Nelson’s coupled-entropy framework offers a candidate objective. Its probability model, constraints and policy loop still need to be specified; the present interfaces do not establish a coupled blanket.

Evidence: `AI-coupled-FE`, `AI-loop`, `AI-next`, `AI-programme`, `AI-testbed`, `HT-readout`, `PC-fixed-v5`, `PC-v0`; [source draft](slide02-active-inference-testbed.md).

## Slide 3 — What predictive coding changes in this experiment

**02:15–04:05; 110 seconds.**

Say:

To teach a correction, we need a direction for changing its stored residual write. SE-A obtains that direction from the answer-loss derivative, the ordinary adjoint calculation. SE-E introduces temporary error variables and lets them settle, then uses their values at the write sites as acquisition credit. The same base and bounded update policy surround the two alternatives.

The settling energy is a quadratic penalty on the inference errors plus the taught-answer loss. We hold the existing write fixed, initialize errors at zero, and take eight steps at learning rate one tenth. The teaching target is supplied for acquisition, not during evaluation.

An earlier implementation penalized the error plus the write, where the intended penalty was on the error alone. SD-24 corrected that defect. The older SE-E result remains a separate historical reference; the completed R1 feedforward experiment did not use this PC path.

The actual solver passes the one-step check against the negative adjoint even with nonzero writes. That check does not prove that longer settling helps. This implementation uses JAX differentiation and nine forward/reverse evaluations for eight steps, so the experiment concerns predictive-coding acquisition credit; wholly backpropagation-free computation and biological locality are not established.

Evidence: `PC-SD24`, `PC-fixed-v5`, `PC-mechanism`, `PC-v0`; [source draft](slide03-predictive-coding-credit.md).

## Slide 4 — Correct a fact, then test its boundaries

**04:05–04:40; 35 seconds.**

Say:

Here is the correction testbed in one pass: teach a fact, ask it again, ask its paraphrase after further edits, and check unrelated predictions. Immediate success, retained paraphrase success and locality measure different properties.

The base and previously BP-trained reader are fixed; memory changes during the stream. We compare declared packages, with three realizations and five dependent orders per realization. The orders reuse subjects, so they are not extra independent populations.

Evidence: `AI-testbed`, `HT-readout`, `PC-SD24`, `PC-v0`, `R1-controls`, `R1-design`, `R1-specificity`; [source draft](slide04-testbed-controls.md).

## Slide 5 — Useful retention, with limits on specificity

**04:40–05:55; 75 seconds.**

Say:

The learned reader's final paraphrase retention averages about 96 percent on zsRE and 68 percent on CounterFact after a thousand edits. The points show the individual realizations. MQuAKE reaches about 72 percent at its separate three-hundred-edit endpoint.

Three of four available triplet contrasts receive a preliminary positive label. CounterFact versus the stable cap remains inconclusive because locality drops to 48 of 50 prompts in realization two.

On zsRE, all fifty locality answers are preserved, yet only 86, 92 and 87 of a hundred near misses are preserved across realizations. Useful retention therefore coexists with specificity failures. These limited three-cluster summaries describe the tested populations; they do not establish population-wide superiority.

Evidence: `HT-readout`, `R1-design`, `R1-retention-counterfact`, `R1-retention-mquake`, `R1-retention-zsre`, `R1-specificity`, `R1-triplet-summary`, `unavailable`; [source draft](slide05-retention-and-controls.md).

## Slide 6 — How often, and how severe?

**05:55–07:05; 70 seconds.**

Say:

The plot separates two questions. How often does a token's loss increase exceed 0.01 nat, and how large is that increase when it does? The denominator includes unchanged and improved predictions. This is not the gate firing rate.

On zsRE, learned v5 has a harmful-change frequency of 0.1594 percent and conditional severity 1.630 nats. Stable v0 has 0.1041 percent and 1.716 nats. On CounterFact, the random reader is both more frequent and more severe than learned v5. Stable v0 has zero observed harm there but also zero paraphrase retention.

Each condition reuses 245,237 positions across fifteen cells. Window intervals condition on those cells and do not cover subject or seed uncertainty. A mean, conditional severity, expected shortfall and maximum answer different questions.

Evidence: `HT-readout`, `HT17-tails`; [source draft](slide06-beyond-the-mean.md).

## Slide 7 — What does the observed tail shape add?

**07:05–08:10; 65 seconds.**

Say:

Fitting the observed excesses adds a qualified distinction. Learned-v5 shape intervals include zero, and held-out predictions gain very little over an exponential. Stable v0 on zsRE has a more pronounced tail and better generalized-Pareto predictions at the primary threshold.

The failures matter: ten of fifteen random-CounterFact fits exclude held-out observations, and all mixture fits hit an invalid endpoint. Sparse cells have no reported shape. At larger thresholds even stable v0 usually has too few events to fit.

These are finite-range findings, not measured complexity classes, state growth, temperature or infinite variance. The shape intervals assume adequate window blocks, whose independence remains unverified.

Evidence: `AI-next`, `HT17-tails`; [source draft](slide07-local-consequences.md).

## Slide 8 — Two interventions against extreme prediction loss

**08:10–09:00; 50 seconds.**

Say:

The kappa pilot bounded one surprisal and failed its retention and tail-separation rule. It did not test Nelson’s calibrated entropy or coupled free energy; neither is confirmed or refuted.

The query-time mixture passed in ten exposed memories, with a small CounterFact retention cost. HT-17 shows nearly unchanged harmful-change frequency but severity dropping roughly to one-third. The one-nat ceiling at a shared prefix is mathematical, independent of the invalid fitted shapes. It does not bound a whole generated answer by one nat.

Evidence: `AI-testbed`, `AW-B`, `HT17-tails`, `kappa-design`; [source draft](slide08-kappa-tradeoff.md).

## Slide 9 — Predictive coding: retention, harm and the controls

**09:00–10:50; 110 seconds.**

Say:

Predictive coding changes acquisition credit on the same frozen base and cap. The corrected eight-step experiment uses three realizations and five dependent orders; depth controls use their common order100 only.

One step matches the adjoint's behavioral endpoints, as its normalized direction should. More settling raises zsRE own-prompt retention from {{depth.1.RET-ES}} to {{depth.8.RET-ES}} to {{depth.32.RET-ES}}, but the thirty-two-step paraphrase score falls to {{depth.32.RET-GS}}. Tail loss and learning cost rise too.

Random-direction credit stopped after {{control.random.n}} items with immediate success {{control.random.es}}. It is a partial one-stream control, not a full replication. The additional-update adjoint control completed twelve cells but underspent the offered PC budget. That leaves direction versus effective computation unresolved.

The original five-order paraphrase differences are {{v0.zsre.ret_gs}} and {{v0.counterfact.ret_gs}}. Its ES99 differences are {{v0.zsre.harm_es99_difference}} and {{v0.counterfact.harm_es99_difference}} nats. Better taught-answer retention alone does not establish better generalization or lower harm.

Evidence: `HT-readout`, `PC-SD24`, `PC-budget`, `PC-depth`, `PC-one-step`, `PC-random`, `PC-v0`; [source draft](slide09-pc-v0-results.md).

## Slide 10 — Does PC credit transfer to the fixed v5 reader?

**10:50–12:25; 95 seconds.**

Say:

The fixed-v5 transfer check changes acquisition credit on the same BP-trained reader. SE-E minus SE-A paraphrase retention is {{v1.zsre.ret_gs}} on zsRE and {{v1.counterfact.ret_gs}} on CounterFact. Harm and cost must accompany those small descriptive differences; this is one exposed subject realization.

A separate study trains the reader itself with predictive coding. All twelve evaluations pair three seeds. ePC has lower CounterFact paraphrase retention in every seed and lower zsRE retention in two of three. Own-prompt retention is nearly equal. Ordinary-text harm is lower on zsRE but mixed across CounterFact seeds. Training costs about one hundred times BP. This is within-recipe evidence on one exposed subject population, without a superiority or safer-learning claim.

Evidence: `AI-next`, `AI-programme`, `HT-readout`, `PC-fixed-v5`, `PC-mechanism`, `PC-reader`; [source draft](slide10-fixed-v5-credit.md).

## Slide 11 — Return to active inference: what should the agent do next?

**12:25–13:50; 85 seconds.**

Say:

What should the agent do next? Our results now connect predictive-coding learning credit, measured frequency and severity, and an analytic bound on unintended prediction loss. Investigators still choose every audit.

For a coupled active-inference objective, we first need to agree the probability model, constraints, escort weighting, gradients, preferences and policy loop with its authors. A bounded training loss and two software interfaces do not supply those ingredients or a Markov-blanket theorem.

A future controlled study could compare informative audit policies with fixed or random audits at equal budgets, measuring corrections, information, loss and cost. That is a next scientific question, not another experimental commitment before October 9.

Evidence: `AI-coupled-FE`, `AI-next`, `AI-programme`, `AW-B`, `HT17-tails`, `PC-fixed-v5`, `PC-v0`, `kappa-design`; [source draft](slide11-return-to-active-inference.md).

## Slide 12 — What we learned, what remains, what it took

**13:50–15:00; 70 seconds.**

Say:

Active inference gives us the proposed belief-and-action loop; autonomous audit selection remains future work. Predictive coding has measured retention, harm and cost trade-offs, with compute attribution still unresolved. Extreme-loss measurements now motivate a tested per-token mixture bound, alongside the unsuccessful kappa pilot.

These are finite test populations, not proof of a heavy-tail family. The main run stopped at 270 cells; omitted comparisons stay unavailable. All three reader-training seeds are complete. Option R repeats the learned/random paraphrase contrast; last-only writes increase harm in the upper-layer study. Planned GPU work finished October 4; the October 9 freeze review and October 15 talk remain ahead.

The base is GPT-2 small, 124 million parameters; transfer to production-scale models is unestablished. S1 literal CounterFact and the original extension remain unavailable; Option R's stable-v0 arm is deferred.

Evidence: `AI-next`, `AI-programme`, `AI-testbed`, `AW-B`, `AW-L`, `HT-readout`, `HT13-corrected`, `PC-SD24`, `PC-fixed-v5`, `PC-reader`, `PC-v0`, `R-extension`, `model-scale`, `resources`, `talk-scope`, `unavailable`; [source draft](slide12-takeaways-and-scope.md).

## Cut and backup instructions — not spoken

- Slides 4–5: omit the control-by-control tour and detailed order/t-sensitivity tables;
  keep what changes, what stays fixed, independent realizations and the specificity limitation.
- Slides 6–7: show frequency and severity together; retain the reference label, repeated-position
  caveat and distinction between empirical concentration and an established heavy-tail family.
- Slide 3: the detailed one-step/nonzero-write diagnostic and full operation ledger are backup;
  retain SD-24's meaning and the JAX differentiation qualification.
- Slide 8: retain the failed κ rule, measured mixture result, and per-token fixed-prefix limitation even when short.
- Slides 9–10: full per-order metrics, 100-edit tables and cost breakdowns are backup; retain
  effect, harm, cost, exposed population and any unfavorable result.
- Slide 12: detailed process accounting is backup (392.42 process-hours for the main 270-cell
  snapshot, excluding separate PC work; overlapping workers prevent equating it to elapsed GPU time).
  Keep the October 9 experimental deadline and October 15 presentation distinct.

All claims use [claim ledger v7](../../talk_claim_ledger_v7.md). The ledger and
the completed result sources, rather than an inference from the story, determine
the final PC interpretation. No new experimental commitment is made by this script.
