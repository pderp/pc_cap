# REG-02 regeneration report — the ePC substrate is back (2026-09-10)

Written 2026-09-10 evening (EDT) by the orchestrating session, after the run completed at 19:24 EDT and
the automatic preflight and P1 fidelity measurement finished. Everything here is on disk under
`results/REG/`, `results/S1/`, `docs/tasks/REG-0{0,1,2,3}.md`, `docs/tasks/S1-01.md`, and the checkpoint
under `/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/`. Nothing is committed; the
lead commits.

## 1. Why this run existed

The month plan needs an error-optimising predictive-coding (ePC) conversion of GPT-2 small as the second
substrate for the matched-fidelity comparisons of Thread 1 (S1 property rows, S5 SB / SE-A / SE-E). The
sibling repository's production checkpoint (`4f0c23aa…`) was absent from every reachable location (T1,
DEC-010), and the sibling's training recipe is PyTorch, which the execution directive excludes (DEC-001).
Pre-authorization PA-1 allowed regeneration "with the sibling's reproduction recipe" under a 10 GPU-hour
bound, which the sibling's own 35.7 A100-hours made hopeless. On 2026-09-10 the lead raised the bound to
120 local GPU-hours (DEC-014) after I showed that micro-batching makes the recipe exact on the 12 GiB
RTX 5070 and projected 15–17 hours. The run therefore produces a *new* checkpoint (PA-1 says so
explicitly): every inherited ePC claim is re-measured, and no continuity with the missing original is
asserted anywhere.

## 2. What was reproduced, and how exactly

The driver (`pccap.distill`) re-implements the sibling's `hdpc-distill` line by line on the FabricPC graph
already used by the ePC wrapper of S0-06, with two additions that are themselves FabricPC objects: a
knowledge-distillation energy functional on the logits node (`pccap.pc.kd_energy.KDEnergy`, the forward KL
at temperature 2 times 4, averaged over positions) and the local weight-phase energy
(`pccap.pc.weight_phase.local_weight_energy`, each block's Gaussian energy with a detached input and a
detached target, so that block *l*'s parameter gradient is −J_lᵀ e_l and the task term reaches only the
final norm and the tied embedding). The protocol is the sibling's: seed 1729, batches of 10 × 512
contiguous OpenWebText tokens (`start = (index · 5120) mod (N − 5120)`), plain SGD on the errors with
step 0.1 for T iterations, the homotopy T ∈ {1, 2, 4, 8, 16, 32, 64} with stage ends at
`completed + ⌈remaining_steps / remaining_stages⌉`, AdamW at 1e-6 without weight decay, one optimizer
step per batch, 9,766 steps, the hold monitor (median baseline over 64 steps, EMA 0.99, hold above
baseline + 0.5·(1 − baseline) or 1.02, subdivision of a rung after 100 held steps), the prompt-KL abort at
0.05 and the relaxation-divergence abort. Micro-batches of 5 (two per batch) reproduce the whole-batch
protocol exactly because both energies are per-sample sums and the local gradients decompose per sample;
Adam's normalization is the only place where reduction order shows, at the level of a few float32 ulps.

The data are byte-exact: the parquet shard `plain_text/train-00000-of-00080` at the pinned revision was
tokenized with the pinned GPT-2 tokenizer, one EOS per document, cut at 52,500,000 tokens, and its SHA-256
(`ae5b795a…`) equals the sibling's pinned value. Training reads the first 50,001,920 tokens; the tail is
untouched and served as the held-out fidelity window.

Verification before spending GPU hours (REG-00, REG-01): a tiny-model test suite checks the FabricPC
path against an independent plain-JAX implementation of the sibling's formulas (relaxation energies and
errors, the local energy and its gradient, an explicit vector–Jacobian product for one block),
micro-batch exactness, Adam against torch's update rule, checkpoint/resume equivalence, the stage
boundaries, the batch indexing and the probe tiling. One real defect was found only on the real model:
the FabricPC form `stop(z_mu + e) − z_mu` loses a 1e-8 error entirely because GPT-2's residual stream is
O(10–1,000) (the ulp of 10 is 1e-6), which made the block gradients 50–700× too small and misaligned
(cosine 0.05). Writing the energy in the sibling's order, `(z_mu − stop(z_mu)) − e`, and keeping node
errors equal to the free variable fixed it; after the fix the local gradient equals the reference in all
twelve blocks (cosine 1.0000, norm ratio 1.0000). A 100-step pilot then reproduced the sibling's logged
trajectory statistically (median per-step ratios 0.93–1.02 for the KD loss, the local energy and the
gradient norm; tracking residual 0.999 with an interquartile range of 0.995–1.004), and the timing probe
projected 12.2 hours at a peak of 6.8 GiB. DEC-015 authorized the full run.

## 3. How the run went

It started at 07:03 EDT and completed at 19:24 EDT: 12.18 GPU-hours of step time, 12.22
hours of wall time inside the training processes, in 25 chunks of at most 500 steps or 90 minutes each.
Every chunk was a separate process that resumed from the last checkpoint (18 process restarts,
contiguous step indices, no repeated or missing step), which is the forced-interruption test the second
review asked for, exercised in production. The lease was released between chunks; four pause windows
were used for other GPU work (baseline throughput, the CR re-profile, the learning-rate screen and the
GPU test subset), costing only one compile per restart (8–24 s). No hold ever fired, no rung was
subdivided, no value was non-finite, and the six stage boundaries (1396, 2791, 4186, 5581, 6976, 8371)
are identical to the sibling's realized run.

The per-stage statistics against the sibling's logged run (same data, same protocol, different float
round-off from step 0 on, so per-step values are not expected to match exactly):

| T | steps | KD-loss mean ours / sibling | tracking-residual median ours / sibling | gradient-norm median ours / sibling | median s/step |
| --- | ---: | --- | --- | --- | ---: |
| 1 | 1396 | 7.03e-05 / 6.64e-05 | 0.991 / 0.991 | 1.24e-02 / 1.26e-02 | 0.71 |
| 2 | 1395 | 1.34e-04 / 1.28e-04 | 0.986 / 0.987 | 1.94e-02 / 1.90e-02 | 0.94 |
| 4 | 1395 | 9.51e-05 / 1.19e-04 | 0.975 / 0.978 | 2.01e-02 / 2.17e-02 | 1.38 |
| 8 | 1395 | 1.86e-04 / 2.06e-04 | 0.972 / 0.973 | 2.78e-02 / 2.73e-02 | 2.26 |
| 16 | 1395 | 1.12e-04 / 1.61e-04 | 0.966 / 0.968 | 2.86e-02 / 2.81e-02 | 3.99 |
| 32 | 1395 | 1.27e-04 / 9.46e-05 | 0.969 / 0.969 | 4.03e-02 / 2.99e-02 | 7.48 |
| 64 | 1395 | 2.26e-04 / 1.15e-04 | 0.971 / 0.966 | 5.18e-02 / 3.48e-02 | 14.47 |

Over steps 2–9,765 the KD-loss means are 1.358e-04 (ours) and 1.272e-04 (sibling) with a median
per-step ratio of 1.029. The 50 milestones tracked the sibling's throughout: prompt KL
between 2e-6 and 3.2e-5 (abort at 0.05; the sibling's own run peaked at 3.1e-5), the 32k-token tail KL
between 4e-6 and 7e-5 with the student–teacher NLL difference never above 5e-4 nats, and the small
96-token perplexity probe wandering by ±1 % (noise). The terminal milestone reads prompt KL
6.84e-06 against the sibling's 5.81e-06, and held-out perplexity 92.861 against the sibling's
92.859 (teacher 93.341).

## 4. Preflight (REG-03) — valid, and promoted

The automatic chain waited for the terminal state (not for a log line: an earlier version of the chain had
fired on a stale marker, which the second review caught) and ran the preflight within a minute of
completion. Every validity check passed: all parameters finite and float32, shapes equal to the teacher's,
the ePC wrapper's cap-off identity exact (maximum logit difference between the graph derive and the plain
functional forward 0.0), energy non-increasing over the nominal eight iterations on eight prompts,
prompt KL below the abort threshold. The relative parameter shift from the teacher is 4.46e-04. On
49,664 unseen tail positions the KL(teacher ‖ student) is 1.41e-05 at temperature 1, or
4.60e-05 in the sibling's scaling (its inherited figure on its own unseen set was 1.24e-4); the student's
NLL is 3.22635 against the teacher's 3.22637. The checkpoint (sha256 `ea4c561d3963ffd8…`) is recorded
in `manifests/assets.json` as `regenerated`, with its provenance (protocol hash, data hash, step count,
the float32 fix) and the explicit statement that it has no continuity with the original.

## 5. P1 fidelity (S1-01) — eligible

On the committed held-out set H (2 × 10⁶ WikiText-103 training tokens sampled by document; SD-1) the
per-token KL from the teacher to the student has mean 2.92e-05, 95th percentile 9.31e-05, 99th
percentile 2.44e-04 and finite maximum 0.116, with no non-finite position. The two bases agree on the
next-token argmax at 99.65 % of positions; their next-token accuracies are 0.3599 and
0.3601, their NLLs 3.5702 and 3.5697. The "unclamped after eight iterations" variant
equals the feedforward one by construction (zero-init errors, unclamped head), checked to 7e-04. On
the BP-selected development streams both bases put the correct first answer token last in 0.0 % (zsRE)
and 0.4 % (CounterFact) of items — the streams are teacher-incorrect by construction — and agree on the
argmax at every prompt. The eligibility rule (mean KL ≤ 1e-3, no non-finite positions) is met: the
matched-fidelity substrate claims of Thread 1 and the natural-language S5 comparison are **eligible**.
The complete-answer version of the initially-correct check is queued for the next GPU window.

## 6. The first ePC property rows

P2 (geometry) on the regenerated substrate gives effective ranks [103, 266, 345, 104] at layers 0/4/8/12 against the
BP rows' [103, 266, 345, 104], and part-of-speech probe accuracies [0.88, 0.92, 0.87] at layers 0/6/12 against [0.88, 0.92, 0.87]: the
conversion did not change the representational geometry at this fidelity. P3 (adjoint mass) is likewise
unchanged: participation ratio 265.9 vs 265.9, final-block share 0.011 vs
0.011. P5 (write locality) and P6 (finite-iteration credit) landed minutes later and tell the same story. P5:
the fraction of items where a bank-1/2/3 write reaches half the loss reduction is 0.945 / 1.00 / 1.00
(BP rows 0.95 / 1.00 / 1.00), the mean improvement 5.21 / 5.58 / 6.47 nats (5.21 / 5.56 / 6.47), the
collateral KL on unrelated prompts 1.086 / 0.137 / 0.202 (1.088 / 0.136 / 0.202). P6, the measurement the
"finite-iteration error credit" label was waiting for: on the regenerated weights the settled error at
bank 3 has cosine 0.998 with the negative adjoint after eight iterations and 0.980 after sixty-four,
the terminal gradient-norm ratios are r₈ 0.404 and r₆₄ 0.098, and 95 % of the energy drop is reached by
iteration 17.5 (median) — every figure equal to the BP-weights row to three decimals. That is what a
relative parameter shift of 4.5e-4 predicts: the conversion preserved the substrate's geometry,
localization, write locality and credit structure, so the S5 contrasts (SB vs SE-A, SE-A vs SE-E) will
be about the credit *procedure* and the substrate *conversion* at matched fidelity, exactly as the PDF's
substrate table intends. `results/S1/report.md` now renders both bases and the eligibility line.

## 7. Cost and what it changes

REG-01 and REG-02 together consumed 12.3 GPU-hours plus about an hour of chains, charged to S6's
allocation as DEC-014 prescribes; S6 (a matched re-distillation pair) is therefore closed for the month
unless the lead reassigns hours (`updated_plan5.md` §4). S5 moves from "bonus" to "expected": its arms,
runner, error-credit rule and calibration procedure are ready (S5-01), and the S5 preparation chain
(error-credit GPU test, ePC radius calibration, a 20-item SB / SE-A / SE-E smoke) starts automatically
after the S1 rows. GPU window 1 is queued behind it: the GPU test subset, the re-profile with
reconcilable per-item ledger costs, and the D1 / D2 / freeze-draft refresh that the freeze gate of
`updated_plan4.md` §2 requires.

## 8. Where everything is

`results/REG/epc-50m/` (per-step metrics, relaxation traces, milestones, summary), `results/REG/epc-50m.log`
(chunk log), `results/REG/preflight.json`, `results/REG/pilot.json`, `results/REG/pilot_compare.json`,
`results/REG/timing_probe.json`, `results/REG/after_reg02_v2.log` (the chain), `results/S1/P1_epc.json`,
`results/S1/P{2,3,5,6}_epc.json`, `docs/tasks/REG-00.md` … `REG-03.md`, `docs/tasks/S1-01.md`,
`docs/epc_energy.md` (the energy, the solver, the REG-00 additions and the float32 note),
`manifests/assets.json` (`assets.epc_checkpoint`), `manifests/datasets.json` (`openwebtext`), and
`/home/derp/cap/assets/models/epc/epc-50m/checkpoints/` (final, stage and rolling step checkpoints with
Adam state, resumable).
