# HT-3b — repaired objective review and pilot proposal

Status: scientific review and pilot v2 delivered; standalone diagnostic-script cleanup awaits permission. Agent: Codex.

Inputs: installed `train.py` and `train_fast.py`, rewritten actual-objective tests, HT-3 review, and the previously identified Nelson–Umarov version. Outputs: `scripts/ht3b_objective_review.py`, `logs/heavy_tail/HT-3b-objective-review.json`, `manifests/revision_v1/kappa_pilot_v2.json`, and `docs/tasks/HT-3b-review-script-cleanup-request-v2.md`.

The repaired preservation term is a proper divergence for normalized positive distributions:

`Dκ(p||q) = Σ p · expm1(κ(log p − log q)) / κ = Σ q f(p/q)`, with `f(t)=(t^(1+κ)−t)/κ`.

For κ>0, `f(1)=0` and `f''(t)=(1+κ)t^(κ−1)>0`. Jensen's inequality gives non-negativity; q=p is a minimum, including stationarity with respect to q's logits. The ordinary branch is KL. Reference distributions are fixed episode inputs; the helper itself does not detach arbitrary differentiable first arguments.

Independent checks covered 128 random positive distribution pairs at κ=.2/.5. All values were finite/nonnegative; maximum logit-gradient norm at equality was 2.3911e−7. At κ=1e−10 the preservation value was 2.204957485 versus ordinary KL 2.204957724. Answer surprisal also has the correct small-κ limit. Eleven invalid configurations were refused. Existing actual-objective and TinyBase tests passed: reference/fast gradients agree at κ=.5, explicit zero agrees with the ordinary branch, and the original negative-divergence counterexample is repaired.

**Remaining numerical launch gate:** the preservation term is unbounded as q approaches zero where p>0. Float32 `expm1` can overflow when κ·log(p/q) exceeds roughly 88.7; a two-class example with q logits [0,−1000] reproduces positive infinity. Bounded answer loss does not bound the full objective or its gradients. Require finite loss/gradient/parameter checks that abort with a charged failure record before launching the pilot. Do not silently clip the divergence, since that changes the objective.

The manifest keeps the **9+3 = 12-training design**: ordinary, κ=.2, κ=.5, and ordinary with clipped answer surprisal c=2, each at seeds 0/1/2. The c=2 arm ceiling-matches κ=.5 only; κ=.2 has ceiling 5 and is a secondary unmatched dose. Adding c=5 would require a separately approved 15-training design and budget amendment. Matching answer ceilings also does not isolate preservation-term effects, since coupled arms use the repaired divergence while the clipped arm retains KL.

The exact aggregation proposal awaits Q4 acceptance:

- Retention: equal-weight mean RET-GS over three datasets × three seeds at the declared final pilot checkpoint; coupled mean must be at least ordinary mean minus .02.
- Unseen firing: mean over the three seeds separately for each dataset must not exceed the corresponding ordinary mean; publish individual seeds too.
- Tail populations: identical bound ordinary-text positions, positive per-token NLL harm relative to the original base. Any missing/nonfinite cell makes the gate unavailable; never drop it.
- Tail summaries: ES95 with fractional boundary weights and maximum positive harm. Compute each seed's equal-dataset macro, then compare three-seed arm means. Separation requires absolute mean difference greater than the larger within-arm seed range. Print direction: increased harm is not improved robustness. This is an exploratory rule, not a significance test.
- Compare κ=.5 versus c=2 descriptively on the same metrics; make no ceiling-matched claim for κ=.2. Keep the aggregate three-GPU-hour ceiling, including failures, and October 9 experimental deadline.

Mapping: [Nelson–Umarov, arXiv:0912.0748v1](https://arxiv.org/abs/0912.0748v1), DOI 10.1016/j.physa.2010.01.044, uses `ln_Q(x)=(x^Q−1)/Q` and `ln_Q(1/p)=−ln_−Q(p)`. This pilot's bounded `−ln_κ(p)` maps to **Q=−κ** for surprisal. This does not identify the entire mixed objective with that paper's coupled-entropy construction. The abstract's “Nelson 2023/2024” still needs a uniquely identified citation.

κ does not repair the rejection boundary. Its CE formula is unchanged, but shared parameters can change its predictions. The null/rejection assays remain essential.

Verify command: the actual tests are recorded verbatim in pilot v2; they passed 10/10 in 13.59 s. Independent probes were run by importing `pccap` before the review module and calling `checks()`. Combined targeted suite: 28 passed in 30.57 s. The numerical review passes; it is not an optimizer-convergence or real-base validation.

The standalone diagnostic needs an import-order safeguard and explicit lambda variable binding for lint. The tested exact patch is in cleanup-request-v2; the first request draft is superseded. No existing-file edit has been applied. Pilot v2 binds installed trainer/test sources; its diagnostic producer hash is explicitly historical so this mechanical cleanup does not invalidate the scientific proposal.

Done-when: repaired objective reviewed and v2 proposal emitted. Cost: GPU seconds 0, training runs 0; CPU wall time not separately metered. Deviations: pilot launch remains gated on finite-value safeguards, selected-primary bindings and lead Q4; no trainer changes. Questions for lead: accept/adjust the explicit arm and aggregation proposal before outcomes, and authorize the separately requested script cleanup. Board unchanged.
