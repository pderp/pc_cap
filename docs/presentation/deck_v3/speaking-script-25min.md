# 25-minute speaking script — draft for charlie

Updated 2026-10-01 by Capex from the twelve slide drafts. **Author review and
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
| 2 | 01:05–03:05 | 120 s | 238 |
| 3 | 03:05–05:50 | 165 s | 318 |
| 4 | 05:50–07:40 | 110 s | 199 |
| 5 | 07:40–09:35 | 115 s | 212 |
| 6 | 09:35–12:05 | 150 s | 289 |
| 7 | 12:05–13:25 | 80 s | 130 |
| 8 | 13:25–15:05 | 100 s | 187 |
| 9 | 15:05–17:55 | 170 s | 318 |
| 10 | 17:55–20:45 | 170 s | 346 |
| 11 | 20:45–22:45 | 120 s | 243 |
| 12 | 22:45–25:00 | 135 s | 324 |

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
blanket or a coupled free-energy formulation.

Evidence: `AI-loop`, `AI-next`, `AI-programme`, `AI-testbed`, `HT-readout`, `PC-fixed-v5`, `PC-v0`; [source draft](slide02-active-inference-testbed.md).

## Slide 3 — What predictive coding changes in this experiment

**03:05–05:50; 165 seconds.**

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

**05:50–07:40; 110 seconds.**

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

**07:40–09:35; 115 seconds.**

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

## Slide 6 — Why look past the mean?

**09:35–12:05; 150 seconds.**

Say:

At each position we ask how much the negative log probability of the actual
next token increases. Positive delta NLL means the system gives that token less
probability after enabling the cap. The unit is nats: an increase of one nat
corresponds to a factor of e reduction in probability for that token. This is
a prediction-loss measure, not a direct measure of human harm or the preference-
risk term of expected free energy.

The horizontal axis sets a loss-increase threshold x. The vertical axis gives
the fraction of evaluated cell-position observations whose increase exceeds x.
Moving right asks about increasingly severe consequences; moving down asks
about increasingly rare ones. The log axes let us see several scales together.
The zero-change mass is part of the denominator even though zero cannot be
placed on the logarithmic x-axis.

We also report expected shortfall: for ES99, the average positive loss increase
within the worst one percent of all positions, with zeros retained and a fractional
boundary when needed. A percentile is the threshold at the edge of that tail;
expected shortfall averages what lies inside it. These are different quantities.
The maximum identifies the worst observed event, and concentration tells us how
few positions account for much of the positive harm.

Heavy-tailed distributions are central to why this question matters at this
satellite. But a finite set of rare severe changes is not itself proof of a
power law or an asymptotic heavy-tail class. Nor does it tell us whether rare
inputs caused them, whether they cluster in time, or how the system will behave
under an unseen extreme regime. Our measured claim is concentrated unintended
prediction loss. That gives the active-inference programme a concrete quantity
to explain and potentially regulate.

Evidence: `AI-next`, `HT-readout`, `HT13-empirical`; [source draft](slide06-beyond-the-mean.md).

## Slide 7 — Similar averages can conceal different consequences

**12:05–13:25; 80 seconds.**

Say:

On zsRE, the learned reader's mean signed loss increase is about 0.00249 nats.
The live-C2 comparator's is about 0.00320. Those small means accompany different
patterns: roughly 0.159 percent versus 0.0187 percent of observations exceed
0.01 nat, while their observed maxima are about 11.05 versus 50.60 nats. The
learned cap changes more positions at that threshold; live C2 has a rarer but
more severe observed extreme. Their means are not equal, and this plot is not
a test that the means are equivalent.

None of this makes probability drift an integrity failure. All forty-five
learned-reader cells exceed the secondary mean-KL benchmark of 0.001, while the
registered data-integrity checks and experimental admission are separate. KL
measures a change in the whole next-token distribution; target-token loss and
exact generated-answer agreement measure different properties.

Evidence: `HT-readout`, `HT13-corrected`, `R1-design`, `R1-fidelity`; [source draft](slide07-local-consequences.md).

## Slide 8 — Two interventions against extreme prediction loss

**13:25–15:05; 100 seconds.**

Say:

The kappa pilot changed the reader's training loss. Both kappa settings reduced a development tail statistic but lost too much retention and failed the declared success rule. Clipping also reduced that tail descriptively. These remain preliminary trade-offs, without evidence of a special coupling advantage.

Evaluation then used ten already-exposed memories: five orders on each dataset, at three hundred edits. All ten met the declared rule: smaller maximum loss and worst-one-percent average, with retention inside tolerance. zsRE endpoints were unchanged. CounterFact paraphrase retention changed by {{awb.counterfact.gs_change}}, a loss of roughly 0.7 to 1.2 percentage points. The largest observed token losses fell from as much as fifteen nats to one.

The guarantee has a precise scope. At the same prefix, mixing in a base share of exp minus one ensures the target probability never falls below that share of the base probability. Its extra negative log likelihood is therefore at most one nat per token. That does not bound a whole generated answer by one nat, preserve every greedy answer, or establish a heavy-tail family. It also does not implement coupled free energy or autonomous action selection.

Evidence: `AI-testbed`, `AW-B`, `kappa-design`; [source draft](slide08-kappa-tradeoff.md).

## Slide 9 — Predictive coding: retention, harm and the controls

**15:05–17:55; 170 seconds.**

Say:

This brings predictive coding directly into the experiment. We keep the frozen base, cap and teaching stream fixed and change acquisition credit: ordinary adjoint or iteratively inferred errors. The energy defect was corrected before these runs. The original comparison has three realizations and five dependent orders; the depth controls use only the common order100. These exposed historical streams are supplemental evidence, not new confirmation.

One step is a mechanism check: starting from zero inferred error, the first step gives a scaled negative adjoint. Normalizing the update direction removes that scale in exact arithmetic. The measured behavioral endpoints agree exactly across all six one-step pairs, although tiny floating-point differences remain in some harm vectors.

On zsRE, own-prompt retention for error credit rises from {{depth.1.RET-ES}} to {{depth.8.RET-ES}} to {{depth.32.RET-ES}} at one, eight and thirty-two steps. Paraphrase retention does not improve at thirty-two steps; it falls to {{depth.32.RET-GS}}. Learning costs and the worst-one-percent positive-loss average rise with depth. The maximum loss itself is not monotonic. More retained taught answers are therefore not an overall superiority result.

The direction control paid for real credit, then replaced its orientation with random directions of the same norm. Its first zsRE run stopped by the resource rule after {{control.random.n}} of a thousand items, with immediate success {{control.random.es}}. Ten planned cells were never started. This is a poor result for that random-credit implementation on one stream, not a completed replication or a proof that all random search must fail.

The additional-update adjoint arm was offered the eight-step PC operation budget but spent only part of it: it usually reached its own stopping thresholds earlier. All twelve cells completed, without recovering the own-prompt gain. Because actual compute was not equal and stopping behavior differed, this remains a weak test of direction versus extra effective computation. The cause of the PC gain is not fully separated.

Evidence: `HT-readout`, `PC-SD24`, `PC-budget`, `PC-depth`, `PC-one-step`, `PC-random`, `PC-v0`; [source draft](slide09-pc-v0-results.md).

## Slide 10 — Does PC credit transfer to the fixed v5 reader?

**17:55–20:45; 170 seconds.**

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

The stream-engine times sum to {{v1.SE-A.seconds}} seconds for SE-A and
{{v1.SE-E.seconds}} for SE-E; the separate harm readout is
{{v1.harm.seconds}} seconds. Startup and lease wait are reported separately by
the driver. We need the behavior, harm and cost together before deciding whether
this credit rule is useful here. Whatever the outcome, autonomous policy choice
and coupled free energy remain proposed parts of the larger active-inference
programme.

Evidence: `AI-next`, `AI-programme`, `HT-readout`, `PC-fixed-v5`, `PC-mechanism`; [source draft](slide10-fixed-v5-credit.md).

## Slide 11 — Return to active inference: what should the agent do next?

**20:45–22:45; 120 seconds.**

Say:

Let me return to the question we started with. A cap that can store and apply a
correction is a useful component, but active inference asks a further question:
what should the agent do next? The experiments supply evidence about the
correction mechanism and its consequences. The next step would connect those
consequences to a model of preferred outcomes, uncertainty and possible actions.

Consider an audit as an action. After learning a correction, a future controller
might decide whether to test a nearby paraphrase, probe an unrelated context,
ask for another observation, or leave its memory unchanged. To make that an
expected-free-energy comparison, we would have to specify beliefs over hidden
states, an observation model, candidate policies and preferences. We would also
need to evaluate what information an audit is expected to provide. A trigger
based only on a large observed loss is useful engineering, but it does not
by itself supply all of those ingredients.

A useful next scientific comparison would give a policy-driven audit mechanism
and a fixed or random audit rule the same budget, then measure useful corrections,
information gained, unintended loss and computational cost under changing
conditions. We would predefine those quantities rather than declare an audit
informative because it found a striking example. That is a proposed next study,
not an additional promise before October 9. The contribution today is the
testbed, the measured behavior, and a sharper experimental route from
predictive-coding credit and extremes to active inference.

Evidence: `AI-next`, `AI-programme`, `HT13-empirical`, `PC-fixed-v5`, `PC-v0`, `kappa-kappa02`, `kappa-kappa05`; [source draft](slide11-return-to-active-inference.md).

## Slide 12 — What we learned, what remains, what it took

**22:45–25:00; 135 seconds.**

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
be stated just as directly as an improvement.

For heavy-tailed distributions and extremes, the measured result is concentrated
unintended prediction loss: a small fraction of evaluated positions can account
for substantial harm even when averages look small. We need the frequency,
severity and concentration beside retention. This is empirical evidence about
our finite test population, not a proof of a heavy-tail family or future
robustness. The mixture intervention now supplies a measured way to cap per-token loss increase at a fixed prefix, with a small CounterFact paraphrase cost and all ten evaluation memories meeting the declared rule.

The approved stop leaves S1_literal CounterFact and the optional extension
unrun. MQuAKE's omitted comparators and unavailable thousand-edit endpoint have
their earlier, separate design reasons. Experimental work finishes October 9
at 17:00 Eastern; the remaining days are for analysis of fixed results, slides
and rehearsal before October 15. These limits help make the claims readable:
what we tested, what it showed, and what remains a question.

Evidence: `AI-next`, `AI-programme`, `AI-testbed`, `AW-B`, `HT-readout`, `HT13-corrected`, `PC-SD24`, `PC-fixed-v5`, `PC-v0`, `resources`, `talk-scope`, `unavailable`; [source draft](slide12-takeaways-and-scope.md).

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
