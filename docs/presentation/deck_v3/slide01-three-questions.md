# Slide 1 — Three questions for Active Inference in the Extremes

**Draft speaker text for charlie's review; conceptual opening.**

**On screen:** retain the submitted title, *Coupled Active Inference on a Frozen
Transformer Prior: A Risk-Aware Residual Agent for Non-Equilibrium Regimes*.
Subtitle: “Predictive-coding credit, continual correction, and what averages hide.”
Three questions: what should the agent do next; how should it learn a correction;
where do unintended consequences fall? Claim footer: `AI-programme`, `AI-loop`,
`PC-v0`, `HT-readout`. Renderable source: `diagram-specs.json`, slide `01`.

## Speaker text

“Our starting question is how a small adaptive system on a frozen language model
could learn useful corrections while remaining attentive to their unintended
consequences. This connects three themes of today's session: active inference,
predictive coding, and heavy-tailed distributions. I will distinguish the agent
we hope to build from the mechanisms and measurements we have actually tested.”
[`AI-programme`, `AI-testbed`]

“Active inference asks how beliefs, preferred outcomes and expected information
should guide what an agent does next. Predictive coding gives us a concrete
learning-mechanism question: can iterative error inference supply useful credit
for a correction? The study of extremes gives us a measurement question: if most
predictions remain nearly unchanged, can a few nevertheless become much worse?”
[`AI-loop`, `PC-v0`, `HT-readout`]

“We use factual correction as a controlled testbed. Teach a correction, ask it
again in different words, and check what else changed. Our completed reader
experiments show useful retention together with preservation and specificity
problems. The corrected PC comparison is a separate study whose result belongs
beside its harm and cost, even if the outcome is null or adverse.”
[`R1-retention-zsre`, `R1-retention-counterfact`, `R1-specificity`, `PC-v0`]

“I will first map the active-inference proposal to this testbed, explain the PC
intervention, and then show the empirical distribution of unintended prediction
loss. Finally, I will return to what a controller would still need to choose
informative actions or audits for itself.” [`AI-programme`, `PC-mechanism`, `AI-next`]

## Diagram and source notes

Three equal visual panels, one per central theme; no positive-result badges.
Label the active-inference loop **programme**, the PC comparison **experiment
pending**, and the loss distributions **measured testbed evidence**. This opening
does not announce a complete coupled agent or an established heavy-tail family.
[`AI-programme`, `PC-v0`, `HT13-corrected`]

Sources: [shared brief](../presentation_brief_2026-09-26.md),
[claim ledger](../../talk_claim_ledger_v7.md), July abstract, and
[triplet report](../../R1_stage4_report_triplet.md). The captured full satellite
title is *Thriving in the Extremes: Active Inference in Non-equilibrium Systems*;
keep it alongside charlie's heading. Individual talk length remains unspecified.

Before presentation, replace “experiment pending” with the actual PC disposition;
do not change it into a positive claim merely because the run completed.
