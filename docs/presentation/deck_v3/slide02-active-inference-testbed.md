# Slide 2 — From active inference to a testable adaptive system

**Draft speaker text for charlie's review; not final wording.**

**On screen:** “Programme: predict, update beliefs, choose actions for outcomes and information.”
Below it: “Implemented testbed: a small adaptive cap on a frozen transformer.”
Solid boxes: implemented components. Dashed loop: proposed policy/audit mechanism.
Visible claim footer: `AI-programme`, `AI-loop`, `AI-testbed`. Diagram specification:
`diagram-specs.json`, slide `02`.

## Speaker text

“The starting point is active inference. An agent has a model of how observations
arise, updates its beliefs when observations disagree with predictions, and chooses
what to do next. Those choices can concern both outcomes it prefers and information
that would reduce uncertainty. That is the programme behind our July abstract.
In this experiment, we have built a testbed for some of its components.”
[`AI-loop`, `AI-programme`]

“The diagram has three parts. On the right is a pretrained transformer. In the
main learned-reader condition its weights stay fixed: it provides the existing
predictions and representations. In the middle is a much smaller adaptive cap.
It stores corrections, decides whether a memory applies to the current query,
and supplies bounded changes to the transformer's internal representations.
On the left are the supplied edits and the questions and ordinary text used to
evaluate their consequences. A correction should help when it is relevant;
the null decision lets the system leave the base prediction alone.” [`AI-testbed`]

“Here is the distinction I want the picture to preserve. We supply the edit
stream and the evaluations. The system does not yet choose an experiment or an
audit by comparing the expected information and preferred outcomes of alternative
actions. The dashed return loop is that proposed extension. The two software
interfaces make the abstract's architecture concrete enough to study; they do
not by themselves establish the conditional independence properties of a Markov
blanket or a coupled free-energy formulation. Nelson’s manuscript offers a candidate objective; a matching probability model and constraints remain to be specified.” [`AI-loop`, `AI-programme`, `AI-coupled-FE`]

“This gives us two tractable experimental questions. First, when teaching a
correction, can iterative predictive-coding inference provide useful learning
credit? Second, when a correction succeeds, where else does it change the model's
predictions? Predictive coding addresses the learning mechanism. Distributional
harm measurements address consequences that a mean can conceal. Both help us
ask what a future active-inference controller would have to notice and regulate.”
[`PC-v0`, `PC-fixed-v5`, `HT-readout`, `AI-next`]

## Diagram and source notes

Use the neutral label “adaptive cap,” not “completed active-inference agent.”
Label the left arrows “supplied observations / tested predictions,” and the right
arrows “features / bounded residual writes.” Place “preferences + policy model +
information-seeking audits: proposed” on the dashed loop. The frozen-base label
describes the main condition, not the S1 continued-base controls. [`AI-testbed`]

Sources: [shared brief](../presentation_brief_2026-09-26.md),
[claim ledger](../../talk_claim_ledger_v7.md),
[implemented main-condition report](../../R1_stage4_report_triplet.md).
**HT-14 cross-reference:** The [abstract-to-testbed map](../abstract_to_testbed.md) is now available. It agrees on the implemented interfaces and the proposed policy loop. The frozen-base description here refers to the main condition; S1 includes base continuation as a control. No additional experimental commitment is made by this slide.
