# Slide 3 — What predictive coding changes in this experiment

**Draft speaker text for charlie's review; experimental outcome still pending.**

**On screen:** “Same frozen base and cap; change acquisition credit.”
Two branches: SE-A, negative normalized adjoint; SE-E, normalized site error after
eight inference steps. Center: corrected energy and the SD-24 repair in one figure.
Visible labels: **mechanism implemented/tested**; **efficacy, harm, cost: experiment
pending**. Claim footer: `PC-mechanism`, `PC-SD24`, `PC-v0`, `PC-fixed-v5`.
Diagram specification: `diagram-specs.json`, slide `03`.

## Speaker text

“Teaching a fact requires more than noticing that an answer is wrong. We need a
direction in which to change the stored correction. The comparison here keeps
the original cap and frozen transformer the same, but changes how that direction
is obtained. SE-A uses the derivative of the answer loss, computed by the usual
adjoint or backpropagation calculation. SE-E instead introduces temporary error
variables inside the network and lets them settle before using their values at
the write sites as the acquisition direction.” [`PC-mechanism`, `PC-v0`]

“The settling objective is a quadratic penalty on these inference errors plus
the task loss for the taught answer:

\[
 E(e;w)=\tfrac12\sum_j\|e_j\|^2+\ell_y(f(x;w,e)).
\]

“Here, x is the teaching prefix, y the taught target, w the current residual
write, and e the temporary inference error. During settling, w is held fixed
and is part of the computation seen downstream. We start e at zero and take
eight gradient steps with learning rate 0.1. The resulting site errors supply
the direction for the bounded acquisition update. The taught target is clamped
for acquisition, not supplied as an answer at evaluation.” [`PC-mechanism`]

“An earlier implementation put the write into the quadratic penalty at the
write sites. In effect it penalized e plus w, where the intended prior penalty
was on e alone. That changes the inferred learning signal. SD-24 corrected this
on September 13. The older SE-E result is retained as a historical defective-
energy result, and the new experiment asks the corrected question. None of the
ongoing R1 feedforward conditions uses this PC credit rule.” [`PC-SD24`]

“There is a useful check on the repair. Starting from zero error, one small
inference step at a site should agree with minus 0.1 times the adjoint at that
site, even when the stored write is nonzero. The actual-solver CPU tests check
that identity. Eight steps are a different, finite-inference treatment: the
one-step check does not prove equal acquisition outcomes or that longer settling
is better.” [`PC-mechanism`]

“The computational price belongs beside the result. Our eight-step implementation
performs nine forward and nine reverse evaluations, including the terminal
gradient diagnostic. The solver itself uses JAX differentiation. This is an
experiment on predictive-coding-derived acquisition credit, not a demonstration
that all computation is backpropagation-free or biologically local. We will show
retention, ordinary-text harm and measured cost together. A null or adverse
comparison would still answer the question.” [`PC-mechanism`, `PC-v0`]

“The second comparison keeps the selected v5 reader and its original BP base
fixed while changing acquisition credit. That tests transfer of this mechanism;
it does not retrain the reader with predictive coding.” [`PC-fixed-v5`]

## Figure details and sources

One diagram, not an engineering timeline: common prefix/target and fixed base →
two credit branches → common bounded update → efficacy / harm / cost. Put the
corrected equation inside SE-E and a small SD-24 inset “penalize inference error,
not the stored write.” No convergence guarantee or positive-result arrow.

Sources: [PC-v0 specification](../../additional_work/PC-v0.md),
[PC-1 checks](../../tasks/PC-1.md), `src/pccap/pc/epc_inference.py`,
`aw/tests/test_pc_v0.py`, [claim ledger](../../talk_claim_ledger_v7.md),
DEC-036 and SD-24. No CPU smoke values should appear as experimental outcomes.
