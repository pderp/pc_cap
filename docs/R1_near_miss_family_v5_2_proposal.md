# Stage 4 v5.2 near-miss family proposal (R1-D10f)

Proposed near-miss family NM-template-v1. In each realization reserve 100 support subjects and
100 different neighbour subjects, disjoint from all other roles, realizations and datasets under the
bound name/verified-alias entity policy. A support/neighbor pair is structurally compatible when its
two source rows have the same nonempty near_key: exact source relation_id for CounterFact/MQuAKE,
or exactly equal subject-masked question template for zsRE. zsRE normalizes subject and prompt using
pccap.metrics.editing.normalize_answer and requires exactly one complete-word subject occurrence;
replace that occurrence with {subject}. Bind the implementation hash. This is different-subject,
same-relation/template specificity, not the historical same-subject/other-relation assay, nor proof
that two facts are semantic nearest neighbours. No lexical distance or causal closeness is inferred.

Pair only within already reserved roles, in lexical support-item order with the first unused
lexical neighbour of equal near_key, as in R1-D10c. Do not change the admitted role RNG, retry a
draw, select on outcomes or borrow another role to improve pair availability. The structural
capacity certificate is not a guarantee about independently drawn support/neighbour subsets.
An allocation that deliberately coordinates families would need separate RNG/role admission.

Use an isolated restored episode per available pair: apply the support's bound edit and measure
the neighbour query against its pre-edit baseline under DEC-053 bounded text equality, retaining
termination and truncation diagnostics. Old/own-answer acquisition is recorded, never used as an
admission filter. No answer is invented. Missing compatible pairs remain named unavailable slots
in the planned 100-case inventory per realization. Report evaluated/preserved/missing counts and
the observed-case rate; a full 100-case rate is unavailable if any required slot is missing. Do not
replace the planned denominator by the observed count or count missing cases as failures/successes.

This paragraph is proposed semantic admission text, not an admission receipt. Final teacher review,
current exposure clearance and frozen source/role/endpoint bindings are separate requirements.

Evidence: [feasibility report](../logs/r1_round23/r1-d10f-feasibility.json).
