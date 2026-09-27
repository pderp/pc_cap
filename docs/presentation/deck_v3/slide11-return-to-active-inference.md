# Slide 11 — Return to active inference: what should the agent do next?

**Draft speaker text for charlie's review. Proposed mechanisms visibly separate
from measured components.**

**On screen:** implemented correction → measured consequences → proposed audit /
policy loop. Under the proposed loop: preferences, uncertainty, action model,
information-seeking audits. Claim footer: `AI-programme`, `AI-next`,
`HT13-empirical`, `PC-v0`, `PC-fixed-v5`, `kappa-kappa02`, `kappa-kappa05`.
Diagram specification: `diagram-specs.json`, slide `11`.

## Speaker text

“Let me return to the question we started with. A cap that can store and apply a
correction is a useful component, but active inference asks a further question:
what should the agent do next? The experiments supply evidence about the
correction mechanism and its consequences. The next step would connect those
consequences to a model of preferred outcomes, uncertainty and possible actions.”
[`AI-programme`, `AI-next`]

“Consider an audit as an action. After learning a correction, a future controller
might decide whether to test a nearby paraphrase, probe an unrelated context,
ask for another observation, or leave its memory unchanged. To make that an
expected-free-energy comparison, we would have to specify beliefs over hidden
states, an observation model, candidate policies and preferences. We would also
need to evaluate what information an audit is expected to provide. A trigger
based only on a large observed loss is useful engineering, but it does not
by itself supply all of those ingredients.” [`AI-next`]

“Predictive coding contributes a candidate way of allocating learning credit.
The corrected paired studies will tell us whether that mechanism helps on our
tested streams, and at what cost. Insert their measured finding here when the
experiments finish, including a null or adverse result. Their outcome does not
on its own settle whether an agent can choose better actions.”
[`PC-v0`, `PC-fixed-v5`, `AI-next`]

“The distributional measurements contribute something different: evidence that
average preservation can conceal a small set of substantial unintended changes.
Those observations suggest what an audit or boundary controller might need to
detect. We have not yet shown that the system autonomously seeks those informative
failures. At present, the investigators use them to learn about the system.”
[`HT13-empirical`, `AI-next`]

“Our loss-level kappa pilot also helps define the boundary of the evidence. The
two kappa settings reduced a development tail statistic, but both failed the
declared retention and tail-separation decision rule. These are preliminary
hints about a robustness trade-off, not the coupled free energy, not a coupled
Markov blanket, and not a test of the abstract's one-kappa conjecture. Those
stronger theoretical ideas need a matching implementation and a direct test.”
[`kappa-kappa02`, `kappa-kappa05`, `AI-programme`]

“A useful next scientific comparison would give a policy-driven audit mechanism
and a fixed or random audit rule the same budget, then measure useful corrections,
information gained, unintended loss and computational cost under changing
conditions. We would predefine those quantities rather than declare an audit
informative because it found a striking example. That is a proposed next study,
not an additional promise before October 9. The contribution today is the
testbed, the measured behavior, and a sharper experimental route from
predictive-coding credit and extremes to active inference.” [`AI-next`]

## Diagram and source notes

Use a feedback loop, with the future action/policy segment dashed. Put distinct
labels on pragmatic value (“preferred outcomes”) and epistemic value (“expected
information”), both **proposed**. Do not draw the observed tail statistic as
identical to expected-free-energy risk. Label “two interfaces” as implemented
architecture and “κ-porous blankets / coupling–boundary–interference relation” as
proposed theoretical interpretation. [`AI-programme`, `AI-next`]

Sources: [shared brief](../presentation_brief_2026-09-26.md), July abstract,
DEC-054, [current schedule](../../plan_from_saturday.md),
[claim ledger](../../talk_claim_ledger_v7.md).
**HT-14 cross-reference:** The [abstract-to-testbed map](../abstract_to_testbed.md) is now available. Policy choice, epistemic audits, formal coupled blankets and the one-κ relation remain proposed. This slide describes a future experiment, not a completed active-inference agent.
