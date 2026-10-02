# Slide 12 — What we learned, what remains, what it took

**Draft speaker text for charlie's review; completed credit and bounded-intervention evidence; reader replication continues.**

**On screen:** three themes with measured/proposed labels. Claims: `AI-next`,
`PC-depth`, `PC-budget`, `AW-B`, `HT13-corrected`, `talk-scope`.

## Speaker text

“There are three takeaways. For active inference, we now have a concrete
correction testbed with measurable boundaries and failure modes. The next
mechanistic question is how an agent would choose informative actions or audits
using beliefs, preferences and an action model. That loop remains proposed.”
[`AI-testbed`, `AI-next`]

“For predictive coding: the completed SE-E minus SE-A paraphrase-retention
differences are {{v0.zsre.ret_gs}} and {{v0.counterfact.ret_gs}} for the exposed
S5 zsRE and CounterFact streams. The fixed-v5 differences are
{{v1.zsre.ret_gs}} and {{v1.counterfact.ret_gs}} on the single exposed R1
realization. The corresponding differences in positive-harm ES99 are
{{v0.zsre.harm_es99_difference}} / {{v0.counterfact.harm_es99_difference}}
and {{v1.zsre.harm_es99_difference}} / {{v1.counterfact.harm_es99_difference}}
nats. The depth controls show an own-prompt retention gain with increased harm and cost; the underspent adjoint control leaves attribution unresolved. Read them
alongside the process and operation costs on the preceding slides. The historical defective-energy run
and CPU readiness checks do not fill this slot. A null or adverse result should
be stated just as directly as an improvement. Separately, reader training now
has two paired seeds and ten of twelve evaluations: paraphrase retention is lower
under ePC in each completed pair, ordinary-text firing is seed-dependent, and
training costs about one hundred times BP. The three-seed answer remains
partial.” [`PC-v0`, `PC-fixed-v5`, `PC-SD24`, `PC-reader-partial`]

“For heavy-tailed distributions and extremes, the measured result is concentrated
unintended prediction loss: a small fraction of evaluated positions can account
for substantial harm even when averages look small. We need the frequency,
severity and concentration beside retention. This is empirical evidence about
our finite test population, not a proof of a heavy-tail family or future
robustness. The mixture intervention now supplies a measured way to cap per-token loss increase at a fixed prefix, with a small CounterFact paraphrase cost and all ten evaluation memories meeting the declared rule.” [`HT13-corrected`, `HT-readout`, `AW-B`]

“The cost and scope also belong with these conclusions. The reconciled 270-cell
snapshot accounts for about 392.42 process-hours. Two workers overlap, so this
is not 392.42 elapsed GPU hours. Separate PC acquisition/readout costs must
be included alongside it before the talk.
The report retains unavailable comparisons rather than assigning them zero
effect.” [`resources`, `unavailable`]

“The base is GPT-2 small (124M parameters); transfer of these findings to production-scale models has not been established. DEC-074b left S1_literal CounterFact and the original optional extension unavailable. The later supplemental Option R study is separate; its stable-v0 class is deferred under DEC-080. MQuAKE's omitted comparators and unavailable thousand-edit endpoint have
their earlier, separate design reasons. Experimental work finishes October 9
at 17:00 Eastern; the remaining days are for analysis of fixed results, slides
and rehearsal before October 15. These limits help make the claims readable:
what we tested, what it showed, and what remains a question.” [`unavailable`, `talk-scope`, `model-scale`]

“I would welcome discussion about which uncertainty signal should drive the next
audit, and which controlled environment would best test the proposed coupled
agent under correlated change. The aim is to turn the architectural programme
into further experiments with measurable consequences.” [`AI-next`, `AI-programme`]

## Diagram and source notes

Use the same three themes as the opening. Put proposed / measured / pending
labels on the individual statements, not just in a footnote. Sources:
[claim ledger](../../talk_claim_ledger_v7.md),
[comparator report](../../R1_stage4_report_comparators.md),
[PC report](../../additional_work/PC-v0_report.md), and
[shared brief](../presentation_brief_2026-09-26.md). Before finalization update the
resource and PC cost snapshots, verify PC source populations and costs,
and confirm the allotted speaking time. No experiment is promised by this close.
