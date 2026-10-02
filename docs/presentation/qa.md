# Reviewer and audience questions

2026-10-01, Capex; rehearsal answers for charlie. Completed supplemental results
are distinguished from pending PC-reader seeds, Option R and upper-layer results.
Evidence references name claim-ledger rows or canonical reports. The three-seed
answer must be refreshed after the expected October 3 evaluations. Friday review
notes have not yet arrived; no feedback from that meeting is assumed here.

## 1. What connects this experiment to active inference?

The programme is a small adaptive system on a frozen transformer prior that could update beliefs and choose actions for preferred outcomes and useful information.
The implemented testbed measures correction, retention and unintended prediction changes, while the preference model and autonomous policy loop remain proposed.

Evidence: `AI-programme`, `AI-loop`, `AI-testbed`.

## 2. Does the current system select actions by expected free energy?

That capability is **not established**: investigators supply the edits and evaluation probes.
A direct test would specify beliefs, observation and action models, preferences and candidate policies, then compare information-seeking audits with fixed or random audits at equal budget.

Evidence: `AI-loop`, `AI-next`.

## 3. Where does predictive coding enter the experiment?

SE-E introduces temporary internal error variables and optimizes a quadratic error penalty plus the taught-target loss before using the site errors as acquisition credit.
SE-A supplies the comparison through adjoint credit, with the base, reader where applicable, data and bounded update policy held fixed within each paired study.

Evidence: `PC-mechanism`, `PC-v0`, `PC-fixed-v5`.

## 4. Is this biologically local or backpropagation-free predictive coding?

Neither claim is established: this error-optimization implementation uses JAX differentiation to infer errors.
The current treatment uses eight settling steps and nine forward/reverse evaluations including the terminal diagnostic, and the fixed-v5 reader remains BP-trained.

Evidence: `PC-mechanism`, `PC-fixed-v5`.

## 5. What was SD-24, and did it invalidate the main experiment?

The old SE-E write-site prior penalized the inferred error plus the existing write, while the corrected energy penalizes the inferred error before adding that write.
The September 13 repair motivates the supplemental corrected-SE-E replication; the completed R1 feedforward matrix did not use this PC credit path.

Evidence: `PC-SD24`, `R1-controls`.

## 6. How do you know the repaired solver computes the intended signal?

Actual-solver regression checks verify that, from zero error and with a nonzero write, one inference step produces the negative adjoint scaled by the error learning rate at each write site.
That validates a local mathematical identity, while completed depth controls show better own-prompt retention with more settling but no general paraphrase or harm advantage.

Evidence: `PC-mechanism`, `PC-SD24`.

## 7. Why leave the reader trained by backpropagation?

Holding the selected v5 reader fixed makes the second PC experiment a comparison of acquisition credit on the same reader and base.
A separate PC-trained-reader experiment now has BP evaluations for three seeds and ePC evaluations for seeds 0–1: 10/12 evaluations and two paired seeds; this is not yet a three-seed paired result.

Evidence: `PC-fixed-v5`, `R1-controls`; [PC-reader report](../additional_work/PC-reader_report.md).

## 8. Are the two PC studies fresh confirmation of the original hypothesis?

They reuse exposed populations: historical S5 streams for the v0 defect-correction replication and realization-zero R1 prefixes for the fixed-v5 transfer check.
Their results must therefore be labelled supplemental replication and post hoc transfer evidence, with the historically defective SE-E scores kept separate.

Evidence: `PC-v0`, `PC-fixed-v5`, `PC-SD24`.

## 9. What would count as PC working here?

We need the paired change in correction and retention alongside locality, ordinary-text harm and measured computational cost.
A null or adverse result is informative, and neither a successful execution nor the one-step solver identity demonstrates a useful PC advantage.

Evidence: `PC-v0`, `PC-fixed-v5`, `PC-mechanism`.

## 10. Why three realizations, and do five orders give fifteen independent replicates?

Three realizations are the registered scope, with five dependent orders within each realization that reuse the selected subjects.
We report every realization and order dispersion, but three clusters provide limited uncertainty information and do not establish a 95-percent familywise guarantee.

Evidence: `R1-design`, `R1-triplet-summary`.

## 11. What has the completed main study actually shown?

Mean final paraphrase retention is about 96 percent on zsRE and 68 percent on CounterFact after a thousand edits, with about 72 percent on MQuAKE after three hundred.
These are learned-reader results, accompanied by specificity and fidelity failures, rather than evidence of PC credit or autonomous active inference.

Evidence: `R1-retention-zsre`, `R1-retention-counterfact`, `R1-retention-mquake`, `R1-specificity`, `R1-fidelity`.

## 12. What do the comparator packages isolate?

The controls compare the learned package with random and stable readers, matched-update and live-cap packages, and continued-base controls.
They do not decompose every architectural ingredient, and S1 continuation before a stable cap is not fine-tuning on the factual edit stream or an exact compute match to v5.

Evidence: `R1-controls`.

## 13. Why stop the main queue at 270 cells?

DEC-074b approved stopping after the specified 270-cell prefix to release time for corrected-PC work before the experimental deadline.
S1_literal CounterFact and the original optional extension remain unavailable; the later Option R supplement is separate, with its stable-v0 class deferred under DEC-080.

Evidence: `resources`, `unavailable`, `talk-scope`; decision context: [lead queue, items 116 and 122](../lead_queue.md).

## 14. How can the data be sound if every learned cell fails fidelity?

Data integrity asks whether the intended inputs, conditions and records were preserved, whereas fidelity asks how much the cap changed predictions relative to its reference.
All 45 learned-reader cells exceed the secondary mean-KL benchmark of one thousandth, which is a scientific finding about preservation rather than an integrity or admission failure.

Evidence: `R1-fidelity`, `R1-design`.

## 15. Why is perfect locality insufficient?

Locality checks exact bounded answer text on fifty unrelated prompts, while near misses probe closer alternatives and KL measures changes in the whole next-token distribution.
The learned zsRE condition preserves all fifty locality answers but preserves only 86, 92 and 87 of a hundred near misses across the realizations, illustrating the distinct failure modes.

Evidence: `R1-specificity`, `HT-readout`, `R1-design`.

## 16. What do the tail figures measure, and what does a nat mean?

The empirical survival curve reports how often the target-token log-loss increase exceeds a threshold, with one nat corresponding to a factor-of-e reduction in that token's assigned probability.
Zeros remain in the denominator, and original-base versus own-cap-off references are kept distinct, especially when S1 has continued the base.

Evidence: `HT-readout`, `HT13-corrected`.

## 17. Have you demonstrated a power law or robustness to extreme regimes?

Neither is established: the observations demonstrate finite-sample concentration and rare severe prediction-loss changes, without identifying an asymptotic tail family.
Repeated text positions and dependent orders do not provide independent tail draws, nor do these curves establish input rarity, temporal clustering or robustness to unseen extremes.

Evidence: `HT13-empirical`, `HT13-corrected`.

## 18. Is ES99 the same as the 99th percentile or the ES99 of paired differences?

ES99 averages positive loss in the worst one percent of all evaluated positions, including zeros and a fractional boundary, whereas the percentile is a threshold.
The difference between the two arms' ES99 values and ES99 of their positionwise differences are separate quantities, both retained in the paired harm readout.

Evidence: `HT-readout`, `PC-v0`, `PC-fixed-v5`.

## 19. Did the kappa pilot validate coupled free energy or the one-kappa conjecture?

For a single surprisal ℓ, the pilot used Lκ(ℓ) = (1 − exp(−κℓ))/κ, a bounded loss deformation whose derivative is exp(−κℓ); it did not implement Nelson’s normalized escort expectation or calibrated entropy.
Both kappa arms showed descriptive tail reductions but failed the declared retention and tail-separation rule, so the result remains a preliminary trade-off without a declared gain.

Evidence: `kappa-design`, `kappa-kappa02`, `kappa-kappa05`, `AI-programme`.

## 20. What remains before the talk and beyond it?

PC-reader seeds 1–2, Option R learned/random cells and the upper-layer comparison remain to be reported with harm and measured cost; experiments end October 9 at 17:00 Eastern before the October 15 presentation.
Beyond this testbed, a budget-matched test of policy-driven audits is proposed, while autonomous epistemic action and a coupled active-inference agent remain unestablished.

Evidence: `talk-scope`, `PC-v0`, `PC-fixed-v5`, `AI-next`.

## 21. What heavy-tail class do these data support?

We report **fitted finite-range shapes**, not an asymptotic class: learned-v5 shape intervals include zero with little held-out gain over an exponential, while stable-v0 zsRE has stronger fitted tails at the primary threshold.
Ten of fifteen random-CounterFact fits exclude held-out observations and all AW-B mixture GPD fits hit invalid endpoints; sparse or invalid fits stay unavailable rather than becoming evidence for a class.

Evidence: `HT17-tails`; [HT-17 report](../additional_work/HT-17_report.md). Conditional window intervals assume adequate window blocks and exclude subject/seed uncertainty.

## 22. Why is the mixture's one-nat ceiling stronger than a fitted shape?

With q(y|x) = ρp₀(y|x) + (1−ρ)p_cap(y|x), q ≥ ρp₀ gives log(p₀/q) ≤ −log ρ = 1 nat when ρ = exp(−1), for each token at the **same prefix**.
This mathematical inequality does not need a successful tail fit; it does not guarantee unchanged greedy answers or limit an entire generated answer to one nat.

Evidence: `AW-B`; [AW-B report](../additional_work/AW-B_report.md). The ten-memory retention criterion passed, with a small CounterFact retention cost and remaining KL breaches.

## 23. Does the κ pilot confirm or refute calibrated coupled entropy?

Neither: its bounded point loss decreases the influence of high-surprisal examples, whereas the manuscript's proposed entropy combines a different generalized information function with a normalized escort distribution and a stretching-dependent outer power.
Our κ pilot failed its declared retention/tail-separation rule, which is evidence about that pilot's objective and population, not a test of the manuscript's complete entropy or free-energy programme.

Evidence: `kappa-design`, `AI-coupled-FE`; [coupled objective note](../additional_work/coupled_objective_note.md).

## 24. Did you measure W(N), entropy growth or a thermodynamic temperature?

No: W(N) counts accessible states as system size changes, and we did not operationally define or measure that quantity across sizes.
A fit to prediction-loss exceedances at one model scale cannot establish entropy extensivity, a complexity class, temperature or infinite variance.

Evidence: `HT17-tails`, `AI-coupled-FE`, `model-scale`.

## 25. What does the three-seed PC-reader experiment say?

**Two paired seeds, 10/12 evaluations; seed 2 pending.** ePC minus BP paraphrase-retention differences are −2.67/−2.00 percentage points on zsRE and −24.17/−2.17 on CounterFact for seeds 0/1. The first CounterFact deficit is substantial. Own-prompt retention agrees except CounterFact seed 1 (ePC 1.00, BP .99).

Ordinary-text fired positions on CounterFact are ePC/BP 185/256 for seed 0 and 720/660 for seed 1, out of 245,237 positions each. The second ePC seed has slightly greater mean loss and ES99 there, reversing seed 0's direction; a uniformly quieter or safer reader is not supported. zsRE firing remains lower in both available ePC seeds. Completed training-time ratios are 102.1× and 95.8× BP. A third seed can assess consistency within this recipe but cannot alone establish a systematic training-rule effect or generalization to new subject populations.

Evidence: [PC-reader report](../additional_work/PC-reader_report.md), including source receipts; 37× was an earlier profile forecast, not the completed seed-0 ratio.

## 26. What is Option R adding?

It tests learned versus random readers on realization 3, with five orders each on zsRE and CounterFact; currently four cells are complete and sixteen are pending.
The stable-v0 class has one ceiling-stopped incomplete cell and nine deferred cells, and the four-realization sensitivity remains withheld until complete paired coverage exists.

Evidence: [Option R report](../additional_work/R_report.md), DEC-080. No primary classifier is reissued.

## 27. Can we generalize these results to production models?

The base is GPT-2 small (124M parameters); transfer of these findings to production-scale models has not been established.
The populations, memory sizes and perturbation geometry also limit transfer, so a larger-model study would be a new experiment.

Evidence: `model-scale`; [assembled Stage-4 report](../R1_stage4_report.md).
