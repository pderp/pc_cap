# Updated plan 6 — 2026-09-11, day 3 (06:20 EDT), pause for counter-reviews

Delta over [updated_plan5.md](updated_plan5.md) (which stands where not restated; plan 4's gate table and
interpretation notes still apply). Written while Codex is paused, before the counter-review series the lead
announced. No threshold, endpoint, arm, contrast or budget changes; the PDF remains the contract.
`docs/derp_review3.md` contained only its title line at the tree time of this document (51 bytes,
04:15 EDT); nothing from it is folded in yet — §6 says how it will be.

## 1. Where the programme stands

**Calendar.** D0 was 2026-09-09; today is D2 by the plan's calendar. The plan placed the freeze around
D8–D10 and the confirmatory runs at D11–D16. The freeze draft has been complete (no pending inputs,
schema-valid) since the evening of D1. The critical path is therefore no longer engineering; it is the
lead's decisions (§5) and, after them, GPU wall-clock for S4.

**Board** (`docs/tasks/STATUS.md`, 08:31 UTC): 61 done, 8 partial, 5 ready, 14 pending of 88.

**GPU used** (ledgers, κ = 1 provisional): S0–S5 together ≈ 1.5 local h; REG-01/02 12.3 h charged to
S6's allocation (DEC-014). Projection for the selected confirmatory scope (zsRE 1000 / CounterFact 300 /
grammar 10,000): 20.5 of the 27.0 local hours available after the 25% headroom.

**Ready for confirmation** (all reviewed at least once, tests green on the CPU and GPU subsets):

| component | state | evidence |
| --- | --- | --- |
| BP editing core: C0/C1/C2/CR(learned), B0/B1/B3 | ready | S2-06 re-profile with ledger deltas, S3-04 short checks, `results/S2/throughput.json` |
| Confirm-mode path (CLI → scheduler → stage → collectors → paired analysis) | repaired and reviewed twice | R2-01…08 and V-01…06 repaired; Lane V2 ran 150/150 synthetic S4 jobs and the nine CLI controls on the repaired tree |
| Regenerated ePC substrate; SB/SE-A/SE-E arms | eligible (P1 mean KL 2.9e-5) | REG-02/03, S1-01, S5-01 |
| Replacement grammar (generator, base, streams, tracing, paraphrases, calibration) | provisional until PA-2 (tonight 23:59 ET) | GRAM-01/02, DATA-06/07, S3-03 dev matrix, SD-20 |
| S1 report card | all rows present (BP, ePC, grammar P4) | `results/S1/report.md`; S1-07 awaits the lead's review |
| S7 harness and fixed pair inventory | CPU part done | S7-01 record; `manifests/dev/s7_pairs.json` |
| S4-05/06, S7-03, S8-04 analysis code | ready on synthetic data | task records (partial: need real runs) |

**Not ready.** B4 (GRACE) fails PC-10 on learned values (§2.1); S3-01 (the full control suite table)
waits on PC-10's outcome; coverage tooling waits on the lead; S6 is closed for the month under DEC-014
unless hours are reassigned.

## 2. Things that need updating (found in this pause)

### 2.1 B4 / PC-10: a cross-framework parity that fp32 cannot deliver — needs a spec-defect entry (SD-21) and a lead decision

Codex's adapter (`pccap.baselines.grace_jax`, `docs/baselines/grace_adapter.md`) reproduces GRACE's
cold initialization exactly, matches keys, radii and labels at all 40 snapshots, and matches the 40
greedy outputs and teacher-forced NLLs. The learned values differ (max |Δ| up to 0.35 after 100 Adam
steps at lr 1.0) while the loss trajectories agree to ≈ 1e-5 relative at steps 1, 10 and 100. The first
gradient already differs by 1e-4 relative L2 before any update — the same class as SD-14's
PyTorch-CPU-vs-XLA fp32 GEMM differences (≤ 1e-3 on logits). Adam at lr 1.0 amplifies a 1e-4 gradient
difference into O(0.1) value differences in a flat valley; the outputs agree because the valley is flat.

The test's own message says: "Do not widen tolerances or register B4 on output agreement alone", and
Codex has correctly refused to. The plan text did not anticipate that value-level parity is not a
property of the algorithm but of the GEMM kernels. Proposed handling, to be decided by the lead after the
counter-reviews:

- **Discriminating control first (CPU, ≈ 2 h, Codex):** a *same-framework* sensitivity run — the JAX
  adapter against itself with a perturbed but mathematically equal computation (e.g. a different
  matmul association or a 1e-7 perturbation of the initial value). If it reproduces the same divergence
  class (values O(0.1) apart, losses and outputs equal), the value gap is a conditioning property of
  GRACE's optimization, not an adapter defect. If it does not, the adapter has a real difference and
  the diagnosis continues.
- **Then SD-21 with two options:** (a) B4 `unavailable` this month (reduced programme, as plan 4 §2's
  rule already allows); (b) PC-10 satisfied in the form *outputs + NLL + keys/radii/labels exact within
  tolerance, values compared by loss trajectory, plus the sensitivity control*, with B4 labelled
  "reference baseline, parity at the output level" in the frozen manifest and in every table.
  Recommendation: (b) if the control passes — B4 is a measured reference like B1/B3 (plan 4 §4), not a
  validity gate — otherwise (a). Neither changes an endpoint, arm list or budget; both are recorded.

### 2.2 Lane V2's open observations become repairs (orchestrator, CPU, small; after the reviews)

- **V2-01** No start-of-run comparison of the loaded base's parameter digest and the tokenizer file hash
  against the frozen manifest (`bp_param_digest`, tokenizer hash). The base is checked for immutability
  during the run, which is a different property. Repair: compare at stage entry in confirm mode; refuse
  with exit code 2 on mismatch; synthetic negative controls in `test_confirm_cli.py`.
- **V2-02** Collectors accept runs whose config has no experiment id even when filtering by a specific
  id (`experiment_id in (x, None)`). Repair: a missing id never matches a specific filter; test.
- **V2-03** The S7-03 CLI does not expose its loader's experiment filter. Repair: `--experiment-id`.
- Codex's study fixture had a schema-invalid checkpoint override (`[1, 2]`) — a review-fixture error,
  not a regression. Its fix is Codex's own new file (§2.4).

### 2.3 ENV-05 (environment recreation) — resolution verified, installation not run

`scripts/setup_venv.{sh,py}` resolve all 150 lock pins to their exact versions in a scratch env under
`assets/envs/`; the real installation, `pip check` and the CPU determinism report have not run because
an editable install may write packaging metadata into the shared checkout. Lead: approve the real run
into a fresh scratch destination (it writes only `src/pccap.egg-info`, which already exists and is
ignored) and the proposed "Recreating the environment" section for `docs/environment.md`
(`docs/tasks/ENV-05-environment.patch`).

### 2.4 Two edit requests from Codex await approval (their own new files)

`docs/tasks/CODEX-20260911-review-tools-v2.patch`: removes the invalid checkpoint override from
`scripts/review_repairs_r2b_study.py`, tidies imports and binds per-case closures in
`scripts/grace_numerical_trace.py` while keeping `import pccap` before JAX. Reviewed here: no model,
tolerance or reference change. Recommendation: approve; Codex then reruns V2 from a fresh fixture root
and writes `logs/review_repairs_r2b.md`.

### 2.5 Board and records

S2-05 mirrored as in progress (Codex; blocked on value parity), ENV-05 added as partial (Codex);
S1-04 done and S7-01 partial (orchestrator). S1-07 stays partial until the lead reviews the S1 report.
The S7 pair inventory's CounterFact shared stratum is short (9 of 34 pairs; the only shared-subject
records outside the sealed pools) and is reported short by default (`docs/lead_queue.md`).

### 2.6 P4 reading carried into D1/D2

P4 on the grammar (error space, D.4): mechanism kinds occupy distinct but overlapping error subspaces
(cross-kind overlap 0.27–0.35 against a 0.125 chance level, within-kind stability ≥ 0.93, held-out
transfer 0.96–0.99 by the own basis versus 0.21 by the other kind's basis); the eight private mechanisms
share one error subspace (private/private overlap 0.93), so error-space separability distinguishes
kinds, not contexts, on this fixture. This does not change D2's routing findings; it sharpens the
interpretation of the S3 grammar matrix: routing by context (C1's 0.70, CR's 0.91) cannot be read off the
error geometry and is tested only by intervention.

## 3. Counter-review protocol (this pause)

1. Every reviewer states the commit and the tree time read (this document: after commit `0f1f9d5`
   plus the orchestrator's uncommitted files listed in §7, tree time 06:20 EDT 2026-09-11).
2. Reviews go to `docs/<reviewer>_review<N>.md`; responses to `docs/<reviewer>_review<N>_response.md`;
   Codex's reports to `logs/`; nothing else is edited by a reviewer.
3. Each finding gets one of: repaired (with the test), recorded as a spec defect (SD-nn), decided by the
   lead (DEC-nnn), or declined with the reason. The next plan version lists them all.
4. Direction is fixed when the lead writes the decisions of §5; only then do the lanes in
   `docs/ongoing.md` §3 start.

## 4. Sequence after the counter-reviews

```
counter-reviews → lead decisions (§5) → orchestrator repairs V2-01..03 (CPU, ≈ 2 h) → Codex: B4 sensitivity control (CPU)
→ PA-2 passes (tonight) → grammar promoted → lead freeze (--final --i-am-the-lead [--accept-unavailable B4])
→ S4-02 allowances → S4-03/04 execution on the lease (≈ 20.5 accelerator h, realization-major; wall-clock larger, D1 memo §5)
→ S4-05/06 as pairs complete · S5-02 when the freeze names the ePC arms · S7-01/02 on committed checkpoints (E.2 filter pass first)
→ S7-03 · S8-01/02/03 · T4 (CP-F) review before any external release
```

Slack use (we are ≈ 8 calendar days ahead of the plan's critical path): the optional CAP-09 difficulty
weight and CAP-08 read variants only if the S8-02 ablation list names them; S5-03 repeats only from
remaining S5 hours; S6 stays closed.

## 5. Decisions requested from the lead (consolidated; supersedes the scattered items in `docs/lead_queue.md`)

| # | decision | default if silent |
| --- | --- | --- |
| D-A | Freeze (`python -m pccap.harness.freeze --final --i-am-the-lead`) and the S4-02 allowances (`run_allowance_seconds`, `stage_allowance_seconds.S4/S5`) | none — the freeze is the lead's act; agents wait |
| D-B | SD-21: B4 parity form (a) unavailable or (b) output-level + sensitivity control, after the control in §2.1 runs | (a) at the freeze if undecided (`--accept-unavailable`) |
| D-C | `pytest-cov` in the frozen venv | test counts remain the coverage evidence |
| D-D | S6 closed for the month under DEC-014 | closed |
| D-E | PA-2: promote the grammar now or at 23:59 ET | promoted automatically when the clock passes without a T1 location |
| D-F | Approve Codex's review-tools v2 patch; the ENV-05 documentation patch; the real ENV-05 install into a fresh scratch env | not applied |
| D-G | S7 CounterFact shared stratum reported short (9 pairs) rather than filled from sealed pools | reported short |
| D-H | S1 report (S1-07) accepted as the S1 input to D1 | stays partial |

## 6. How `derp_review3.md` will be folded in

When it has content: the orchestrator writes `docs/derp_review3_response.md` within the same working
session, classifies each item per §3.3, updates this plan as `updated_plan7.md` only if a finding changes
the sequence or a decision, and otherwise records the outcomes in the response and the task records.

## 7. Files this pause produced (orchestrator; to be committed as "own work" per the lead's instruction)

`docs/updated_plan6.md`, `docs/ongoing.md` (rewritten; previous version archived as
`docs/archive/ongoing-2026-09-11-0620.md`), `docs/tasks/S1-04.md`, `docs/tasks/S7-01.md`,
`src/pccap/analysis/s1_p4.py`, `src/pccap/analysis/s7_01.py`, `src/pccap/analysis/report.py` (P4 block),
`tests/analysis/test_s1_p4.py`, `tests/analysis/test_s7_01.py`, `results/S1/P4_gram.json`,
`results/S1/report.md`, `results/S1/coverage.json`, `results/S1/logs/`, `manifests/dev/s7_pairs.json`,
`manifests/tasks.json`, `docs/tasks/STATUS.md`, `docs/lead_queue.md`. Codex's files (B4, ENV-05, V2,
patches, status JSONs) and `docs/derp_review3.md` are left uncommitted for the lead.
