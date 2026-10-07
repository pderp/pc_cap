# 25-minute speaking script — draft for charlie

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
| 1 | 00:00–01:05 | 65 s | 114 |
| 2 | 01:05–03:05 | 120 s | 254 |
| 3 | 03:05–05:35 | 150 s | 318 |
| 4 | 05:35–07:20 | 105 s | 199 |
| 5 | 07:20–09:10 | 110 s | 212 |
| 6 | 09:10–11:40 | 150 s | 298 |
| 7 | 11:40–13:25 | 105 s | 242 |
| 8 | 13:25–15:30 | 125 s | 286 |
| 9 | 15:30–18:05 | 155 s | 318 |
| 10 | 18:05–20:35 | 150 s | 374 |
| 11 | 20:35–22:30 | 115 s | 214 |
| 12 | 22:30–25:00 | 150 s | 337 |

Total allocation: **25:00**.

This version retains separate design/results and distribution/consequence
slides. If the chair requests 15 minutes, use the companion script: merge 4–5
and 6–7 as speaking units, shorten kappa and move diagnostics/accounting to backup.
Do not obtain the shorter version by removing one of the three central themes.

## Slide 1 — Three questions for Active Inference in the Extremes

**00:00–01:05; 65 seconds.**

Say:

Our starting question is how a small adaptive system on a frozen language model
could learn useful corrections while remaining attentive to their unintended
consequences. This connects three themes of today's session: active inference,
predictive coding, and heavy-tailed distributions. I will distinguish the agent
we hope to build from the mechanisms and measurements we have actually tested.

Active inference asks how beliefs, preferred outcomes and expected information
should guide what an agent does next. Predictive coding gives us a concrete
learning-mechanism question: can iterative error inference supply useful credit
for a correction? The study of extremes gives us a measurement question: if most
predictions remain nearly unchanged, can a few nevertheless become much worse?

Evidence: `AI-loop`, `AI-next`, `AI-programme`, `AI-testbed`, `HT-readout`, `PC-mechanism`, `PC-v0`, `R1-retention-counterfact`, `R1-retention-zsre`, `R1-specificity`; [source draft](slide01-three-questions.md).

## Slide 2 — From active inference to a testable adaptive system

**01:05–03:05; 120 seconds.**

Say:

The starting point is active inference. An agent has a model of how observations
arise, updates its beliefs when observations disagree with predictions, and chooses
what to do next. Those choices can concern both outcomes it prefers and information
that would reduce uncertainty. That is the programme behind our July abstract.
In this experiment, we have built a testbed for some of its components.

The diagram has three parts. On the right is a pretrained transformer. In the
main learned-reader condition its weights stay fixed: it provides the existing
predictions and representations. In the middle is a much smaller adaptive cap.
It stores corrections, decides whether a memory applies to the current query,
and supplies bounded changes to the transformer's internal representations.
On the left are the supplied edits and the questions and ordinary text used to
evaluate their consequences. A correction should help when it is relevant;
the null decision lets the system leave the base prediction alone.

Here is the distinction I want the picture to preserve. We supply the edit
stream and the evaluations. The system does not yet choose an experiment or an
audit by comparing the expected information and preferred outcomes of alternative
actions. The dashed return loop is that proposed extension. The two software
interfaces make the abstract's architecture concrete enough to study; they do
not by themselves establish the conditional independence properties of a Markov
blanket or a coupled free-energy formulation. Nelson’s manuscript offers a candidate objective; a matching probability model and constraints remain to be specified.

Evidence: `AI-coupled-FE`, `AI-loop`, `AI-next`, `AI-programme`, `AI-testbed`, `HT-readout`, `PC-fixed-v5`, `PC-v0`; [source draft](slide02-active-inference-testbed.md).

## Slide 3 — What predictive coding changes in this experiment

**03:05–05:35; 150 seconds.**

Say:

Teaching a fact requires more than noticing that an answer is wrong. We need a
direction in which to change the stored correction. The comparison here keeps
the original cap and frozen transformer the same, but changes how that direction
is obtained. SE-A uses the derivative of the answer loss, computed by the usual
adjoint or backpropagation calculation. SE-E instead introduces temporary error
variables inside the network and lets them settle before using their values at
the write sites as the acquisition direction.

The settling objective is a quadratic penalty on these inference errors plus
the task loss for the taught answer:

\[
 E(e;w)=\tfrac12\sum_j\|e_j\|^2+\ell_y(f(x;w,e)).
\]

Here, x is the teaching prefix, y the taught target, w the current residual
write, and e the temporary inference error. During settling, w is held fixed
and is part of the computation seen downstream. We start e at zero and take
eight gradient steps with learning rate 0.1. The resulting site errors supply
the direction for the bounded acquisition update. The taught target is clamped
for acquisition, not supplied as an answer at evaluation.

An earlier implementation put the write into the quadratic penalty at the
write sites. In effect it penalized e plus w, where the intended prior penalty
was on e alone. That changes the inferred learning signal. SD-24 corrected this
on September 13. The older SE-E result is retained as a historical defective-
energy result, and the new experiment asks the corrected question. None of the
ongoing R1 feedforward conditions uses this PC credit rule.

The computational price belongs beside the result. Our eight-step implementation
performs nine forward and nine reverse evaluations, including the terminal
gradient diagnostic. The solver itself uses JAX differentiation. This is an
experiment on predictive-coding-derived acquisition credit, not a demonstration
that all computation is backpropagation-free or biologically local. We will show
retention, ordinary-text harm and measured cost together. A null or adverse
comparison would still answer the question.

Evidence: `PC-SD24`, `PC-fixed-v5`, `PC-mechanism`, `PC-v0`; [source draft](slide03-predictive-coding-credit.md).

## Slide 4 — Correct a fact, then test its boundaries

**05:35–07:20; 105 seconds.**

Say:

The unit of work is a supplied factual correction. We ask whether the system
can give the taught answer immediately, whether it retains the answer after many
more edits, and whether that correction transfers to a differently worded
question. Immediate editing success is ES. End-of-stream retention on the
original prompt is RET-ES; retention on paraphrases is RET-GS. These are different
questions: memorizing a prompt is easier than using a correction appropriately
when the wording changes.

The main R1 condition has three distinct kinds of state. The GPT-2 base stays
fixed. A reader, trained earlier with backpropagation and then fixed, decides
whether a stored correction applies. The edit stream changes the cap's memory
records and bounded residual writes. This completed study evaluates a feedforward
reader; it does not contain the forthcoming predictive-coding credit treatment.

For each condition and dataset, we have three realizations with five orders
within each. The five orders reuse subjects; they are not five more independent
populations. zsRE and CounterFact reach a thousand edits. MQuAKE ends at three
hundred and is descriptive there. The PC-v0 replication uses its specified
regenerated ePC base and exposed historical streams, so we also keep it distinct
from this GPT-2 reader study.

Evidence: `AI-testbed`, `HT-readout`, `PC-SD24`, `PC-v0`, `R1-controls`, `R1-design`, `R1-specificity`; [source draft](slide04-testbed-controls.md).

## Slide 5 — Useful retention, with limits on specificity

**07:20–09:10; 110 seconds.**

Say:

The learned reader retains taught corrections across paraphrases on the tested
streams. At the final checkpoint, mean paraphrase retention is about 96 percent
on zsRE and 68 percent on CounterFact. The three realization means are shown
individually: 0.955, 0.965 and 0.961 for zsRE, and 0.6915, 0.666 and 0.6765 for
CounterFact. Each of those values averages five orders within its realization.

Against the random reader and stable v0 cap, three of the four available triplet
contrasts receive the registered preliminary positive label. CounterFact versus
stable v0 remains inconclusive: retention improves, but locality falls to 48 of
50 prompts in realization two. That is why I want the effect and the preservation
measure beside the label rather than presenting retention alone as success.

There is a further specificity warning. The learned zsRE condition preserves
all fifty locality answers but passes only 86, 92 and 87 of the hundred near-miss
probes across the three realizations. An apparently clean locality score can
coexist with inappropriate transfer on closer alternatives. We therefore need
the probability-level harm measurements as well.

Three realization clusters provide limited uncertainty information. The displayed
range and the registered labels are preliminary summaries, not an established
95-percent familywise guarantee. The result is useful behavior on these tested
populations, accompanied by specific observed failure modes.

Evidence: `HT-readout`, `R1-design`, `R1-retention-counterfact`, `R1-retention-mquake`, `R1-retention-zsre`, `R1-specificity`, `R1-triplet-summary`, `unavailable`; [source draft](slide05-retention-and-controls.md).

## Slide 6 — How often, and how severe?

**09:10–11:40; 150 seconds.**

Say:

An average can conceal a small number of large unintended changes. We measure delta NLL: the increase in negative log probability of the actual next token when the cap is enabled at the same prefix. One nat means that token becomes a factor of e less probable. This is a prediction-loss measure, not human harm or the preference term of expected free energy.

The horizontal axis asks how often the increase exceeds 0.01 nat. Its denominator includes every scored position, including improvements and unchanged predictions. The vertical axis asks how large the increase is, on average, among positions exceeding that threshold. Neither axis is the gate firing rate: an activated correction need not cause harmful change.

On zsRE, learned v5 has harmful changes at 0.1594 percent of positions with conditional severity 1.630 nats. Stable v0 has 0.1041 percent and 1.716 nats. On CounterFact, learned v5 has 0.2984 percent and 1.913 nats; the random reader has 2.0450 percent and 3.486 nats. Stable v0 has no observed harmful changes there, but also zero paraphrase retention. Its conditional severity is undefined, not zero.

These are fifteen cells per condition and dataset: three subject realizations and five dependent orders, at a thousand edits. Every cell reuses the same 245,237 ordinary-text positions. The intervals resample matching window identities jointly, conditional on the observed cells. They do not account for subject or seed uncertainty, and independence between windows is unverified.

Expected shortfall asks another question: ES99 averages positive loss within the worst one percent of all positions, with zeros and a fractional boundary retained. The maximum is the single largest observed event. Learned v5 on zsRE has a lower maximum than stable v0, 11.05 versus 27.68 nats, but a higher average cell ES99, 0.260 versus 0.179. No single summary orders every kind of risk.

Evidence: `HT-readout`, `HT17-tails`; [source draft](slide06-beyond-the-mean.md).

## Slide 7 — What does the observed tail shape add?

**11:40–13:25; 105 seconds.**

Say:

For learned v5, shape estimates at 0.01 nat are close to zero: 0.0435 to 0.0588 on zsRE and 0.0294 to 0.0978 on CounterFact. The fixed illustrative realization-zero, order-one-hundred intervals are minus 0.097 to 0.177 and minus 0.009 to 0.187. Both include zero. Held-out-window log-likelihood gains over the exponential are tiny, at most about 0.0028 nats per excess. An exponential is an economical approximation on this measured range; this is not an equivalence test.

Stable v0 on zsRE shows a more pronounced tail: fitted shapes range from 0.433 to 1.029, with an illustrative interval of 0.390 to 0.779. Held-out predictive gains are 0.149 to 0.594 nats per excess in every cell. But at a one-nat threshold, thirteen of fifteen cells have too few events for a fit. The evidence does not establish the farthest tail or infinite variance.

The random CounterFact reader illustrates a failure mode: all fitted shapes are negative, yet ten of fifteen held-out comparisons fail because an estimated endpoint excludes an observed held-out event. Every mixture fit has an endpoint pathology and is labelled invalid. Sparse random-zsRE, stable-CounterFact and individual kappa-pilot cells have no eligible headline shape. These cases remain in the report.

We have not measured system state growth, identified a complexity class or assigned a temperature. The scientific advance is a tested distinction in the observed shape of prediction-loss changes, with failed predictions visible. Those consequences can inform a future active-inference audit policy; they do not establish one.

Evidence: `AI-next`, `HT17-tails`; [source draft](slide07-local-consequences.md).

## Slide 8 — Two interventions against extreme prediction loss

**13:25–15:30; 125 seconds.**

Say:

The kappa pilot replaced one answer surprisal ℓ with the bounded loss (1 − exp(−κℓ))/κ, saturating at 1/κ. The tested settings, 0.2 and 0.5, failed the declared retention and tail-separation rule; ordinary clipping also reduced the tail. This uses the coupled-logarithm family, but differs from Nelson’s calibrated entropy in its probability transformation, independent-equals or escort averaging, outer root and informational-scale calibration. We did not test that entropy or a coupled free-energy objective. This result neither confirms nor refutes those untested proposals.

Evaluation then used ten already-exposed memories: five orders on each dataset, at three hundred edits. All ten met the declared rule: smaller maximum loss and worst-one-percent average, with retention inside tolerance. zsRE endpoints were unchanged. CounterFact paraphrase retention changed by {{awb.counterfact.gs_change}}, a loss of roughly 0.7 to 1.2 percentage points. The largest observed token losses fell from as much as fifteen nats to one.

The guarantee has a precise scope. At the same prefix, mixing in a base share of exp minus one ensures the target probability never falls below that share of the base probability. Its extra negative log likelihood is therefore at most one nat per token. That does not bound a whole generated answer by one nat, preserve every greedy answer, or establish a heavy-tail family. It also does not implement coupled free energy or autonomous action selection.

HT-17 separates the mixture’s effect into frequency and severity. Frequency above 0.01 nat is almost unchanged, while conditional severity falls from 1.619 to 0.542 nats on zsRE and 1.925 to 0.581 on CounterFact. All ten generalized-Pareto mixture fits hit an endpoint pathology and are invalid; none yields a tail-class estimate. The one-nat ceiling follows from the mixture algebra, independently of those fits.

Evidence: `AI-testbed`, `AW-B`, `HT17-tails`, `kappa-design`; [source draft](slide08-kappa-tradeoff.md).

## Slide 9 — Predictive coding: retention, harm and the controls

**15:30–18:05; 155 seconds.**

Say:

This brings predictive coding directly into the experiment. We keep the frozen base, cap and teaching stream fixed and change acquisition credit: ordinary adjoint or iteratively inferred errors. The energy defect was corrected before these runs. The original comparison has three realizations and five dependent orders; the depth controls use only the common order100. These exposed historical streams are supplemental evidence, not new confirmation.

One step is a mechanism check: starting from zero inferred error, the first step gives a scaled negative adjoint. Normalizing the update direction removes that scale in exact arithmetic. The measured behavioral endpoints agree exactly across all six one-step pairs, although tiny floating-point differences remain in some harm vectors.

On zsRE, own-prompt retention for error credit rises from {{depth.1.RET-ES}} to {{depth.8.RET-ES}} to {{depth.32.RET-ES}} at one, eight and thirty-two steps. Paraphrase retention does not improve at thirty-two steps; it falls to {{depth.32.RET-GS}}. Learning costs and the worst-one-percent positive-loss average rise with depth. The maximum loss itself is not monotonic. More retained taught answers are therefore not an overall superiority result.

The direction control paid for real credit, then replaced its orientation with random directions of the same norm. Its first zsRE run stopped by the resource rule after {{control.random.n}} of a thousand items, with immediate success {{control.random.es}}. Ten planned cells were never started. This is a poor result for that random-credit implementation on one stream, not a completed replication or a proof that all random search must fail.

The additional-update adjoint arm was offered the eight-step PC operation budget but spent only part of it: it usually reached its own stopping thresholds earlier. All twelve cells completed, without recovering the own-prompt gain. Because actual compute was not equal and stopping behavior differed, this remains a weak test of direction versus extra effective computation. The cause of the PC gain is not fully separated.

Evidence: `HT-readout`, `PC-SD24`, `PC-budget`, `PC-depth`, `PC-one-step`, `PC-random`, `PC-v0`; [source draft](slide09-pc-v0-results.md).

## Slide 10 — Does PC credit transfer to the fixed v5 reader?

**18:05–20:35; 150 seconds.**

Say:

The second experiment asks whether the credit rule transfers to the learned
reader that retained edits in our main study. Both arms use the same original
BP-trained GPT-2, selected reader weights, calibration, gates, memory capacity
and stream order. Both begin with fresh memory. Only the delta-acquisition
credit changes: the registered adjoint path versus corrected eight-step error
inference. The reader itself remains trained by backpropagation.

This is deliberately small and exposed: realization zero of zsRE and
CounterFact, order one hundred, with three hundred edits each. It is a post hoc
transfer check, not fresh confirmation or three independent replications. We
use the installed R1 editing, retention, bounded-text locality, near-miss and
semantic revision functions. We evaluate at one hundred and three hundred
edits; ordinary-text harm is a separate readout on the full fixed inventory.

At the final checkpoint, SE-E minus SE-A is {{v1.zsre.es}} for immediate editing
success and {{v1.zsre.ret_gs}} for paraphrase retention on zsRE. The CounterFact
differences are {{v1.counterfact.es}} and {{v1.counterfact.ret_gs}}. Locality
differences are {{v1.zsre.ls}} and {{v1.counterfact.ls}}; near-miss differences are
{{v1.zsre.near_miss}} and {{v1.counterfact.near_miss}}; semantic revision
differences are {{v1.zsre.revision}} and {{v1.counterfact.revision}}. Higher is
better for these behavior measures. If an assay is unavailable, that is shown
as unavailable rather than a successful zero difference.

For unintended effects, the difference of the two arms' ES99 positive-harm
values is {{v1.zsre.harm_es99_difference}} nats on zsRE and
{{v1.counterfact.harm_es99_difference}} on CounterFact. Lower favors SE-E. Both
arms are evaluated on the same two hundred forty-five thousand, two hundred
thirty-seven ordinary-text positions. That gives matched predictions, not that
many independent experimental units.

A separate experiment trains the reader itself with predictive coding while
keeping acquisition adjoint. All twelve evaluations now pair three seeds.
ePC minus BP paraphrase retention is −2.67, −2.00 and +0.33 percentage points
on zsRE; CounterFact is −24.17, −2.17 and −17.50. Own-prompt retention is
nearly equal, with CounterFact seed one 1.00 for ePC versus 0.99 for BP.
The ePC readers fire less on ordinary zsRE text in every seed; CounterFact
firing and harm reverse direction across seeds. Training costs about one
hundred times BP. This is within-recipe evidence on one exposed subject
realization, not general superiority or safer learning.

Evidence: `AI-next`, `AI-programme`, `HT-readout`, `PC-fixed-v5`, `PC-mechanism`, `PC-reader`; [source draft](slide10-fixed-v5-credit.md).

## Slide 11 — Return to active inference: what should the agent do next?

**20:35–22:30; 115 seconds.**

Say:

Active inference asks what the agent should do next. Our cap acquires corrections, and our assays measure their benefits and unintended consequences. A future controller might probe a paraphrase, audit unrelated text, request an observation or leave memory unchanged. We would need hidden-state beliefs, observation and action models, preferences and expected information to compare those policies.

Nelson’s coupled-entropy framework and the proposed coupled free energy are candidates for that objective. With their authors, we first need to specify the probability model, constraints, escort weighting, gradients and policy loop. A bounded transformation of one training loss supplies none of those specifications by itself. The architectural interfaces also do not prove Markov-blanket conditional independence.

The predictive-coding experiments now measure learning-credit trade-offs in retention, unintended loss and cost. The tail analysis separates frequency from severity and checks which finite-range models predict held-out events. The mixture supplies a proven per-token ceiling with a measured efficacy cost. These are useful components and measurements for designing an audit policy.

We have not demonstrated autonomous epistemic action: investigators still choose the observations and tests. A next experiment could compare policy-guided audits against fixed or random audits under the same budget, measuring useful corrections, information, loss and cost. That is a proposed study after this programme, not another commitment before October 9.

Evidence: `AI-coupled-FE`, `AI-next`, `AI-programme`, `AW-B`, `HT17-tails`, `PC-fixed-v5`, `PC-v0`, `kappa-design`; [source draft](slide11-return-to-active-inference.md).

## Slide 12 — What we learned, what remains, what it took

**22:30–25:00; 150 seconds.**

Say:

There are three takeaways. For active inference, we now have a concrete
correction testbed with measurable boundaries and failure modes. The next
mechanistic question is how an agent would choose informative actions or audits
using beliefs, preferences and an action model. That loop remains proposed.

For predictive coding: the completed SE-E minus SE-A paraphrase-retention
differences are {{v0.zsre.ret_gs}} and {{v0.counterfact.ret_gs}} for the exposed
S5 zsRE and CounterFact streams. The fixed-v5 differences are
{{v1.zsre.ret_gs}} and {{v1.counterfact.ret_gs}} on the single exposed R1
realization. The corresponding differences in positive-harm ES99 are
{{v0.zsre.harm_es99_difference}} / {{v0.counterfact.harm_es99_difference}}
and {{v1.zsre.harm_es99_difference}} / {{v1.counterfact.harm_es99_difference}}
nats. The depth controls show an own-prompt retention gain with increased harm and cost; the underspent adjoint control leaves attribution unresolved. Read them
alongside the process and operation costs on the preceding slides. The historical defective-energy run
and CPU readiness checks do not fill this slot. A null or adverse result should
be stated just as directly as an improvement. Separately, all three reader-training seeds are complete: ePC loses CounterFact paraphrase retention in every seed and zsRE retention in two of three. Ordinary-text harm is lower on zsRE but mixed on CounterFact. Training costs about one hundred times BP.

The additional subject realization repeats the learned-versus-random paraphrase advantage; the four-realization sensitivity is about 44 percentage points on zsRE and 56 on CounterFact. Own-prompt and fidelity costs remain visible. In the separate upper-layer factorial, writing only at the last site changes paraphrase retention by at most 0.67 percentage points but increases mean ordinary-text loss by 2.64–4.37 times. Reading only upper taps loses CounterFact paraphrases in every seed. These are useful negative results for that interface hypothesis.

The cost and scope also belong with these conclusions. The reconciled 270-cell
snapshot accounts for about 392.42 process-hours. Two workers overlap, so this
is not 392.42 elapsed GPU hours. Separate PC acquisition/readout costs must
be included alongside it before the talk.
The report retains unavailable comparisons rather than assigning them zero
effect.

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
