# Presentation direction: active inference, predictive coding, and heavy-tailed distributions

2026-09-26 — charlie's direction, recorded by Capex for charlie, Claude and Capex. This is the shared presentation brief for PRES-1 and deck v3. It supersedes earlier outline priorities where they conflict; it does not change experimental treatments, budgets or operational ownership.

## The lead's direction

The presentation must focus on **three central subjects: active inference, predictive coding, and heavy-tailed distributions**. charlie identifies the day's overarching heading as **“Active Inference in the Extremes.”** This is one presentation among several in the Binghamton satellite, so its narrative should connect our experiments to the day's scientific questions.

All three subjects belong in the opening, the main scientific discussion and the conclusion. Predictive coding needs a substantive explanation and its own experimental evidence; active inference needs an explicit account of the research programme and the path from the implemented components to that programme; heavy-tailed distributions need an explanation of why extremes matter and what our distributional measurements establish. Concentrated harm remains an important finding within this three-part story. The lead has not specified equal speaking time or an individual talk duration.

## Local source material found and read

No refresh or re-upload is needed. Both original files are present in `/home/derp/cap/errata/presentation_details/`:

| Source | Contents and use |
| --- | --- |
| [Submitted July abstract](../../../errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf) | Three pages, including the two-interface diagram and bibliography. Title: *Coupled Active Inference on a Frozen Transformer Prior: A Risk-Aware Residual Agent for Non-Equilibrium Regimes*. Authors: charlie derr and Matthew Iklé; the PDF prints the name as “Charlie Derr.” |
| [Saved satellite page](../../../errata/presentation_details/sattellite-schedule) | An extensionless text file; preserve its existing spelling. It contains the session scope, objectives, committees, talk list and schedule. The captured full title is *Thriving in the Extremes: Active Inference in Non-equilibrium Systems*. |

The supplied site associated with the saved material is [Photrek's satellite page](https://www.photrek.io/thriving-extremes-css2026). The earlier [pivot memo](../heavy_tail_suggested_slight_pivot.md) also records a September 15 check of the [conference programme](https://ccs26.cssociety.org/program.html). This briefing uses the local captures; it is not a September 26 verification of the live timetable. Keep charlie's heading and the captured longer title together rather than silently replacing either.

The saved page places the satellite on **October 15, 2026, Binghamton, NY and online**, with co-chairs Kenric Nelson and André Vilela. Its four sessions cover foundations/limitations of active inference; nonequilibrium complex systems; active inference in nonequilibrium; and project planning. The joint Derr–Iklé talk is listed in Session 3, **2:45–4:15 p.m.** That is a session window, not the duration of this talk. The saved page includes tentative entries and an inconsistent registration-year reference; it is background material, not a reason to invent a final speaking slot.

Source identities: abstract SHA-256 `bb9bb99c196c0392f790223096bef92627d5ea7cad09e349e84f2b5004db6f01`; saved page SHA-256 `39b90570144a38a34bdae07cb17c6cc403d0b41f4e7da82dc8d1c6ec03bfa3e3`.

## Connect the abstract, the session and the experiments

The abstract proposes a frozen generative prior with a small adaptive residual agent between two interfaces: one toward the external environment and one toward the transformer. The diagram labels both as κ-porous blankets. Its wider programme includes coupled free energy, expected-free-energy policy choice, pragmatic and epistemic value, uncertainty-directed audits, and a conjectured relationship between coupling, modular boundaries and interference. The text treats learning from failure as a potential source of information. These are the programme's motivating ideas; their appearance in the abstract does not make them completed experimental results.

The satellite's captured objectives connect active inference to nonlinear dependence, extreme fluctuations, generalized/coupled free energy and coupled Markov blankets, with socioeconomic models as possible experimental environments. Present these as the session's questions and theoretical proposals. Our experiments do not establish its broad claims about non-equilibrium dissolving blankets or a coupled framework guaranteeing robustness.

The presentation can be organized around this question: **How far can a small adaptive system on a frozen transformer move us toward active inference in the extremes, and what do predictive-coding credit and the distribution of unintended harm reveal about that path?** This is a proposed narrative, not an additional experimental commitment.

| Central subject | Role in the talk | Evidence and limits |
| --- | --- | --- |
| **Active inference** | Explain the intended relationship between prediction, belief updating, action, preferences and information seeking. Use the two-interface architecture to connect the frozen prior to the adaptive system and environment. Return to what a future agent would need to choose informative audits or actions. | Current retrieval/null decisions and bounded writes are working components. They do not establish expected-free-energy policy selection, proved Markov blankets or the full coupled agent. Investigator-selected failure probes are distinct from autonomous epistemic action. |
| **Predictive coding** | Explain how iterative error inference supplies an acquisition direction, then compare corrected SE-E with adjoint SE-A. Show efficacy, preservation harm and computational cost together; explain why the comparison matters for the programme. | Use the original-v0 comparison and fixed-v5 acquisition-credit comparison when their measured results are available. Current R1 reader results are BP-trained feedforward results. The historical SE-E result used defective energy and is labelled historical; a CPU smoke/parity test verifies execution, not scientific efficacy. PC credit in this implementation does not demonstrate BP-free reader training or a complete active-inference agent. |
| **Heavy-tailed distributions and extremes** | Explain why averages can understate rare severe consequences. Show distributions, exceedances, maxima and concentration beside mean drift and retention. Relate the loss-level κ pilot and its controls to the broader coupled-objective proposal. | Existing observations support concentrated local harm. They do not establish a power-law tail, an asymptotic heavy-tail class, infinite variance or robustness to unobserved black swans. Rare inputs, rare harmful consequences, temporal clustering and nonlinear dependence are distinct properties. Report κ trade-offs/null findings and the repaired implemented objective, not the earlier proposal's obsolete formula. |

DEC-054's qualification remains applicable to the κ pilot: preliminary hints at what the architecture could provide, not the coupled free energy, a coupled Markov blanket, or a test of the one-κ conjecture. The [earlier outline](talk_outline_v1.md) contains useful checked evidence and objective corrections, but its emphasis and provisional 18-minute structure do not override this brief.

## Instructions for the resumed lanes

1. **PRES-1:** Build the deck outline around the three subjects above. Begin with the satellite's question and the abstract's programme, explain the implemented testbed, give PC its own main section, present retention together with distributional harm, and return to the active-inference research questions. Keep measured/proposed labels visible without allowing qualifications or process history to dominate the presentation. Each central theme needs a substantive explanation, a connection to evidence and an explicit unanswered question.
2. **PC-3 and PC-4:** Their report/validation work supports the PC section. Preserve empty result slots until experiments finish. Keep the distinction between implementation validation, defect-correction replication and conclusions about credit rules.
3. **R1-D14e:** Make the comparator results useful for explaining the trade-off between correction, generalization and unintended intervention. Show the tail/concentration context alongside aggregate retention. Preserve comparator meanings: S1 continued-base controls are not direct fine-tuning on the factual edit stream.
4. **Claim ledger v7:** Associate each claim with active inference, predictive coding and/or heavy-tailed-distribution questions as well as its measured result, population, control, supports and does-not-support columns. Include the programme's hypotheses with an explicit proposed status; do not fill pending PC rows with smoke-test results.

Experiments still finish **October 9, 2026, at 17:00 America/New_York**. October 10–14 is for analysis of fixed results, slides and rehearsal; October 15 is presentation day. The presentation direction does not authorize new experiments, change the registered comparisons, restart the GPU queue, or extend that deadline.

Related shared context: [PC specification](../additional_work/PC-v0.md), [PC refocus](../additional_work_pc_refocus.md), [review response](../additional_work_pc_refocus_response.md), [current execution plan](../plan_from_saturday.md), [triplet report](../R1_stage4_report_triplet.md), and [ongoing lanes](../ongoing.md). For scheduling, current decisions and execution instructions take precedence over historical proposals.
