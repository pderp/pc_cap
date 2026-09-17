# HT-3e — independent pilot and stress-panel counter-review

- Status: complete, with reporting qualifications below.
- Agent: Codex, Round22.
- Inputs: all36 original pilot endpoint measurements and their bound legacy aliases; six stress cells with checkpoints
  20/60/70/80/100; pilotv3 and the existing final-alias aggregate.183 repository source files verified.
- Outputs: `scripts/ht3e_independent_review.py`, `logs/r1_round22/ht3e-independent-review-v2.json`, this review.
- Verify: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m
  scripts.ht3e_independent_review --output <new-repository-log.json>`; final CPU checks in `logs/r1_round22/final-checks.txt`.
- Verify output: all36 rows match within absolute1e-12; same pilot verdicts; all six stress relative-loss/censor
  classifications reproduced independently, without calling the original aggregation or stress-analysis helpers.
- Done-when check: raw-file reproduction, bound averaged checkpoint and aliases, common populations, floor/spread
  arithmetic, clipped comparison, two-sentence slide text, stress schedule/fact/censor review delivered.
- Cost: GPU0/model calls0; CPU file analysis only.
- Deviations: original retention scalars are independently aggregated from measurement outputs; generations are
  not rerun. Legacy tail files lack embedded token IDs; ordered cap-off arrays are identical, as previously qualified.
- Unresolved: revise the owner's presentation wording about permanence/universal invariance. No confirmatory claim
  is established; no owner notes/results were edited during the active chain.
- Questions for lead: none for completing this counter-review.

## Required result framing — DEC-054

**What it is not.** It is not the coupled free energy of Nelson et al. (no coupled expectation, no changed
inference distribution), not a coupled Markov blanket, and not a test of the one-κ conjecture that porosity and
interference are the same parameter. It is the first controlled measurement of what a loss-level coupling does on
this substrate, which is the honest thing to bring to a session chaired by the people who defined κ.

## Pilot arithmetic

The predeclared150–300 averaged checkpoint, all three seeds and all three datasets are retained. Per-seed dataset
macros are averaged over seeds. Positive-harm ES95 uses the worst5% of all4,064 positions, includes zero-harm
positions in the denominator and fractionally weights the boundary observation; positions are not independent trials.

| Arm | RET-GS mean | Change from ordinary | Mean ES95 positive harm (nats) | Mean maximum (nats) | RET floor pass |
|---|---:|---:|---:|---:|---|
| Ordinary | 0.796111 | — | 0.222921753 | 5.263680318 | reference |
| κ=.2 | 0.754444 | −0.041667 | 0.083635392 | 2.700845462 | no |
| κ=.5 | 0.747778 | −0.048333 | 0.063475976 | 2.603639761 | no |
| Clipped surprisal2 | 0.778889 | −0.017222 | 0.103265537 | 3.620790576 | yes |

The floor is0.796111−0.02=**0.776111**. The ES95 separation threshold is0.387471415 and the maximum threshold
4.439309019, each the larger of the two arms' three-seed ranges. Neither coupled arm nor the clipped control exceeds
either threshold in absolute mean difference. Both coupled arms therefore remain **null results under the declared
pilot gate**, despite smaller descriptive tail means. These are screening criteria, not significance tests.

Mean zsRE false-fire rates are ordinary11.6667%, κ=.2 5%, κ=.5 4%, clip2 4.6667%. Ordinary/coupled CF and MQ rates
are0; clip2 has one CF false fire across300 queries (0.3333%). Clip2 passes retention but fails the per-dataset
nonincrease criterion and has no separated tail improvement. Its ceiling matches κ=.5 only; it is not a matched
control for κ=.2, nor evidence of a coupled-free-energy effect. The ordinary seed2 CF/MQ historical aliases match
checkpoint SHA and exact ordered edit/outside IDs; they do not create new replications.

Two-sentence slide result: **“In a three-seed development pilot, loss-level κ=.2 and κ=.5 reduced descriptive tail
means, but neither met the predeclared retention and seed-spread gates, yielding a null pilot result. A clipped-loss
control met the retention floor but also lacked a qualifying robustness improvement, so these preliminary results
do not establish an advantage specific to coupling.”** Carry the required paragraph above with the result.

## Stress-panel review

All20 fixed old facts retain primary exact answers at all five probes. The two schedules have different treatment
orders but the same fact sets at each checkpoint; their saved per-token loss changes are identical (maximum absolute
difference0) on all three datasets. This supports equality of **these measured schedules**, not a theorem that order
cannot matter for this architecture, for ties, different states, other schedules or other training seeds.

| Dataset | First detected harm | Affected old facts | Signed mean change within affected fact | Largest token increase | Positive token-mean trajectory at60/70/80/100 |
|---|---:|---|---|---:|---|
| zsRE | none | none | 0 | 0 | 0 /0 /0 /0 |
| CounterFact | 80 | cf-45; cf-20223 | +2.465432; +4.008543 | 12.531881 | 0 /0 /0.323792 /0.323792 |
| MQuAKE | 60 | mquake:9405b94b70d56357158651df | +2.048760 | 6.555213 | 0.111751 at all four probes |

The positive-token mean uses all measured target positions; it is not an equal-weight average of the20 fact means.
Paraphrase retention is a separate measurement: primary20/20 must not be described as every paraphrase remaining exact.

The implemented recovery rule is correctly right-censored at40 updates **from treatment end (edit60)** for CF/MQ.
That does not show40 updates of harm after its onset in CF: no harm appears at60/70, it first appears at80, and the
last probe at100 supplies20 observed later updates. MQ supplies40 updates after its first detection at60. Positive
loss changes persist through the final observed probe, but finite follow-up cannot establish permanence. The lack
of an explicit stored-record repair operation does not rule out recovery through future changes in selection.

Suggested replacement for the owner's “permanent” and universal-invariance wording: **“The two tested schedules
produced identical observed trajectories. Sparse probability degradation persisted through edit100 while primary
exact answers stayed20/20; recovery was unobserved within the study window.”** Any particular competing-edit or
rare-token-gate explanation remains a mechanism hypothesis until selection evidence and a controlled ablation isolate it.
