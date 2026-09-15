# HT-3 — objective review and actual-trainer CPU probes

Status: tests and blocked pilot manifest delivered; objective review required before training.
Agent: Codex. No optimizer steps, real base, GPU work, or existing trainer edits.

The principal finding is mathematical, independent of JAX. The proposed preservation term
Dκ(p,q) = Σ p_i (p_i^κ − q_i^κ)/κ is not a divergence in general. At κ=.5,
p=(.9,.1) and q=(.99,.01), it equals **−0.0401018971**. At q=p its logit gradient is
(−.0569209979,+.0569209979), although its value is zero. Minimization can therefore move a
previously matching model away from its reference. This undermines its stated preservation role.

Differentiating with q=softmax(z) gives
∂D/∂z_j = −p_j q_j^κ + q_j Σ_i p_i q_i^κ.
At q=p this is generally nonzero unless the reference is uniform or κ=0. The numerical counterexample and
gradient are recorded in logs/heavy_tail/kappa_definition_review.json and reproduced by the actual fast-trainer
group loss with a controlled-logit base stub.

The bounded answer loss does pass the requested saturation checks at κ=.2/.5: ≤1/κ, with finite logit gradients
at target logit −10,000. This does not mean that dL/dp remains finite: it is −p^(κ−1), which diverges as p→0 for
0<κ<1. “Finite precision” needs a specified parameterization and interpretation. The clipped c=2 comparator
passes boundedness/gradient checks and keeps preservation KL unchanged. At exactly κ=0 the fast objective is
bitwise identical to its default branch; TinyBase reference/fast gradients agree within their established tolerance.

Additional implementation findings:

- train.py's reference episode_grads ignores κ and clipping, while train_fast.py applies them. The TinyBase test
  observes this discrepancy rather than assuming the two trainers are interchangeable.
- The positive-κ expression (1−exp(−κs))/κ cancels to zero for κ=1e−10 in float32, despite ordinary loss >4.
  Use an explicit zero branch and expm1 for a stable positive branch after authorization.
- LossConfig admits NaN κ and infinite clipping thresholds; finite-value validation is missing.
- Retrieval/null CE retains its formula, but shared reader parameters still change under other terms, so κ does
  not guarantee an unchanged rejection boundary.

The cited version is [Nelson and Umarov, arXiv:0912.0748v1](https://arxiv.org/abs/0912.0748v1),
published in Physica A 389 (2010), 2157–2163. Its logarithm uses (x^Q−1)/Q; Eq. (3) uses
surprisal log_Q(1/p)=−log_−Q(p). Thus this pilot's bounded −log_κ(p) maps to Q=−κ for that
surprisal convention. Do not identify the pilot with the full coupled-entropy construction or its positive-Q
surprisal without the mapping. The abstract's “Nelson 2023/2024” citation does not identify a unique version.

Manifest: manifests/revision_v1/kappa_pilot_v1.json pins the current proposal, reference version, 12-training
budget, thresholds, proposed exact aggregation rule, and blockers. The one clipped c=2 control matches κ=.5's
ceiling; it does not match κ=.2's ceiling5. Adding a c=5 arm changes the stated 9+3 training design. That ambiguity
and the preservation objective need a scientific decision before pilot execution. Plausible options are keeping
ordinary preservation KL for an explicitly answer-only robust-loss pilot, or deriving a proper reference-minimized
preservation objective. Neither change is applied here.

Verification: tests/revision_v1/test_ht_kappa_actual.py exercises installed trainer code (not just copied formulas).
The first installed run had 6 passing cases and 2 fixture failures: history_size=1 violates the generator's minimum2,
and a 0.0008 near-zero tolerance was below the actual O(κs²/2) difference (~0.0035).
The exact two-line correction is tested in memory: all eight cases pass, including TinyBase gradients.
Applying it awaits Charlie's existing-file permission; see HT-3-test-fixture-correction-request.md.
Known production defects are explicit diagnostic assertions, not claims that those behaviors are acceptable;
future approved repairs must update these assertions to the desired invariants.

Verify command after fixture approval:
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q -p no:cacheprovider tests/revision_v1/test_ht_kappa_actual.py

Inputs: counter-review §4, actual train.py/train_fast.py, TinyBase, pinned paper version.
Outputs: test file, blocked pilot manifest, mathematical evidence JSON, this record, fixture correction request.
Done-when: boundedness, exact-zero default, near-zero behavior, gradients and clipped comparator investigated;
pilot definition and decision rule made reviewable. Unresolved: fixture permission, scientific objective choice,
trainer parity/stability/config repairs, comparator scope, selected-primary binding and explicit go/no-go.
Cost: GPU seconds0; initial CPU run9s plus corrected in-memory verification. No κ experimental result exists yet.
