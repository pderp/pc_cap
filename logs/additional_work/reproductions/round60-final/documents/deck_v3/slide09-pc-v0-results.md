# Slide 9 — Predictive coding: retention, harm and the controls

**Draft speaker text for charlie's review. Completed comparisons; partial random control explicitly labeled.**

**On screen:** depth 1/8/32 retention–harm–cost figure, restricted to the common
order100 on three realizations per dataset. The original five-order comparison
is backup. Claims: `PC-v0`, `PC-depth`, `PC-one-step`, `PC-random`, `PC-budget`.

## Speaker text

“This brings predictive coding directly into the experiment. We keep the frozen base, cap and teaching stream fixed and change acquisition credit: ordinary adjoint or iteratively inferred errors. The energy defect was corrected before these runs. The original comparison has three realizations and five dependent orders; the depth controls use only the common order100. These exposed historical streams are supplemental evidence, not new confirmation.” [`PC-v0`, `PC-SD24`]

“One step is a mechanism check: starting from zero inferred error, the first step gives a scaled negative adjoint. Normalizing the update direction removes that scale in exact arithmetic. The measured behavioral endpoints agree exactly across all six one-step pairs, although tiny floating-point differences remain in some harm vectors.” [`PC-one-step`]

“On zsRE, own-prompt retention for error credit rises from {{depth.1.RET-ES}} to {{depth.8.RET-ES}} to {{depth.32.RET-ES}} at one, eight and thirty-two steps. Paraphrase retention does not improve at thirty-two steps; it falls to {{depth.32.RET-GS}}. Learning costs and the worst-one-percent positive-loss average rise with depth. The maximum loss itself is not monotonic. More retained taught answers are therefore not an overall superiority result.” [`PC-depth`]

“The direction control paid for real credit, then replaced its orientation with random directions of the same norm. Its first zsRE run stopped by the resource rule after {{control.random.n}} of a thousand items, with immediate success {{control.random.es}}. Ten planned cells were never started. This is a poor result for that random-credit implementation on one stream, not a completed replication or a proof that all random search must fail.” [`PC-random`]

“The additional-update adjoint arm was offered the eight-step PC operation budget but spent only part of it: it usually reached its own stopping thresholds earlier. All twelve cells completed, without recovering the own-prompt gain. Because actual compute was not equal and stopping behavior differed, this remains a weak test of direction versus extra effective computation. The cause of the PC gain is not fully separated.” [`PC-budget`]

“The earlier five-order eight-step comparison gives paraphrase differences {{v0.zsre.ret_gs}} and {{v0.counterfact.ret_gs}}, and ES99 differences {{v0.zsre.harm_es99_difference}} and {{v0.counterfact.harm_es99_difference}} nats. These use 4,064 ordinary-text positions per arm. CounterFact has saturated own-prompt retention and zero paraphrase retention in this v0 setup, so it is a limited discriminator. No power-law family or autonomous inference policy follows from these results.” [`PC-v0`, `HT-readout`]

## Sources and backup

[Controls report](../../additional_work/PC-controls_report.md),
[offered-budget per-realization report](../../additional_work/PC-matched-control_report.md),
[original paired report](../../additional_work/PC-v0_report.md).
Figure: `assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png`.
Separate PC-12 full-vector harm results are unavailable; do not copy the depth
arms' ES99 values into those controls. Learning time is part of process time.
