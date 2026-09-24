# Lead queue

> **Signing procedure (the lead's acts):** `docs/tasks/R1-D9-operator-sheet-v8.md`, section "Ordered operator workflow" —
> nine steps, one command each (`python -m scripts.r1_58g_operator <step> --inputs docs/tasks/R1-D9-inputs-v9.json`),
> dry run first, then `--form <signed form> --execute`. Steps 6 (endpoints) and 9 (launch) are the orchestrator's; the
> orchestrator prepares the freeze assembly inputs between steps 7 and 8. This banner is updated when the sheet version changes.

Asynchronous questions for the lead (updated_plan2.md §1, four touchpoints T1–T4). The
orchestrator continues with everything that does not depend on an answer. Answers are recorded
in `docs/decisions.md`.

## T1 (opened 2026-09-09, D0) — accept the plan; locate assets

**Question.** Accept updated_plan2.md and its pre-authorizations PA-1…PA-9, as modified by the
execution directives DEC-001…DEC-005 (JAX only; FabricPC for PC; sibling and FabricPC read-only;
resources under `assets/`). State the locations, if any exist, of:

1. the production ePC checkpoint (SHA-256 `4f0c23aaba9d8daabfc1f455ee673776a940171e2456b3291a5bb00015284eb5`,
   sibling `artifacts/models/gpt2-predictive-coding.pt`) and its resume state;
2. the R8/R9 six-layer grammar model, tokenizer and generator;
3. causal-fibres v0.3 (joint block diagonalizer, supplied-support sandbox);
4. comcrit (HVP / quadratic control code);
5. RelaLeap harnesses;
6. documents [2] and [5] of `docs/footnotes.md` (no links given).

**Default if no answer by CP-A + 2 working days** (deadline written by S0-01): PA-1 fires as
REG-00→REG-01 (JAX re-implementation of the recipe; SD-15) and PA-2 fires as GRAM-01/02;
items 3–6 are marked `unavailable` and the optional work that needs them is `unsupported`.

*(S0-01 appends the measured absent list below.)*

## T2 — reserved (D1, only if the smallest complete core comparison does not fit)

## T3 — reserved (D3, only if a required core pair must be dropped)

## T4 — reserved (CP-F, report review before any external release)

### T1 measured absent list (S0-01, 2026-09-09)

Absent on this host, in `~/repos`, and in the sibling: the ePC checkpoint `4f0c23aa…` and its
resume state; the R8/R9 six-layer grammar (model, tokenizer, generator); causal-fibres v0.3;
comcrit; RelaLeap. Documents [2] and [5] have no link. Drive links [1], [3], [4] resolve (not
downloaded). Details: `manifests/assets.json` (`assets`, `inventory`).

**Clock:** CP-A = 2026-09-09. PA-1 (REG-00 → REG-01 pilot) and PA-2 (GRAM-01/02) fire after
**2026-09-11 23:59 (America/New_York)** unless T1 names a location. GRAM-01 (the generator) and
REG-00 (the JAX distillation driver) are pure engineering and may start before the clock; only
the GPU regeneration/training waits.

## Lease schedule (orchestrator, 2026-09-10)

REG-02 (ePC regeneration, ≈ 12 GPU-h) holds `results/.gpu_lease` in chunks of ≤ 500 steps or 90 min, releasing it between chunks; any other lease user simply queues (fcntl). Short `-m gpu` tests need no lease. Stop file: `results/REG/reg02.stop` pauses the loop after the current chunk.

## Agent questions

(append dated lines here)

- 2026-09-11 (orchestrator → codex): **Lane V2 is unblocked** — the V-01…V-06 repairs are committed (`0f1f9d5`; `logs/review_repairs_r2_response.md`; `tests/harness/test_confirm_cli.py` has 9 controls). The orchestrator takes P4 (S1-04) and S7-prep per your handoff note.

- 2026-09-10 (orchestrator, relaying Lane D) — **answered: approved and applied** (see the edit-request file). Original: codex needs your yes/no on pinning `setuptools==78.1.0` inside the new auxiliary env `assets/envs/grace` (touches only that env; unblocks the GRACE reference smoke and parity cases): `docs/tasks/S2-05a-environment-edit-request.md`.

## T-CP-E (opened 2026-09-10; re-dated 2026-09-10 afternoon by DEC-019) — freeze decision

**Re-dated:** Codex's interim report 2 found integration defects on the confirmatory path (now repaired, `logs/review_interim_report2.md`); the freeze request stands only after the gate in `docs/updated_plan4.md` §2 is green (re-profile with reconcilable costs, GPU tests, Lane V review). Grammar/B4 may then be accepted as unavailable explicitly (`--accept-unavailable`).

`manifests/frozen.draft.json` is schema-valid (`python -m pccap.harness.freeze --draft`); the readiness checklist is docs/D2_decision.md §5. Pending inputs at writing: grammar dataset id (GRAM-02, PA-2 clock 2026-09-11 23:59 ET), B4 (Lane D), ePC checkpoint (REG-02 running, S5 only). Decision requested: freeze the BP core when the B1 learning-rate screen and the CR re-profile are in (today), recording grammar/B4 as `unavailable` in the manifest if still missing — or wait for PA-2. Act: `python -m pccap.harness.freeze --final --i-am-the-lead` and commit `manifests/frozen.json` (this unlocks confirmation access; no agent will do it).

## S7 pair inventory note (2026-09-11; no decision needed)

`manifests/dev/s7_pairs.json` is fixed. The CounterFact *shared* stratum has 9 pairs, not 34: the two 300-item development pools have unique subjects, and the only CounterFact records that share a reserved development subject with a different relation and target are these 9; reaching 34 would mean drawing from the sealed confirmation pools, which is refused. zsRE shared/private/near-neighbour pairs come from the MEND train split (subjects in no pool), over-sampled 3× because the E.2 teacher filter needs one short GPU pass before the first S7 run; the selection rule is written in the manifest. If you would rather have the CounterFact shared stratum filled from the sealed pools (contaminating S7's independence), say so explicitly; the default is to report it short.

## T-ENV/S6 (opened 2026-09-10, updated_plan5.md §4)

1. Coverage tooling (`pytest-cov`) in the frozen venv: yes/no (derp_review2 N7).
2. S6 (conditional re-distillation): closed for the month under DEC-014's charge of REG to S6's allocation (≈ 14 of 20 A100-h consumed by REG-01/02 and the follow-up chains), unless you reassign hours.

## PA-2 note (2026-09-10)

The replacement grammar (GRAM-01/02, DATA-06/07) is built and trained on the CPU in seconds (no GPU hours spent). It is recorded as *provisional* in `manifests/assets.json` until the PA-2 clock (2026-09-11 23:59 ET) passes without T1 locating R8/R9; if you prefer, say so and it is promoted now.

## S4-02 allowances (opened 2026-09-10 20:20 EDT) — needed before the freeze

The freeze draft has **no pending inputs** now (`python -m pccap.harness.freeze --draft`). Two fields are yours at S4-02 and must be set before `frozen.json` is written: `resource_rules.run_allowance_seconds` (per confirmatory run) and `resource_rules.stage_allowance_seconds.S4/S5`. The refreshed projection prices the selected scope (zsRE 1000 / CounterFact 300 / grammar 10000) at 20.5 of the 27.0 local hours after headroom; per-run figures from `results/S2/throughput.json` (learning + query s/edit × items, plus rescoring) are in `results/S2/projection.json` `table[..].parts`. A `None` is allowed but then recorded as *not enforced* in every run.


## Consolidated decisions (2026-09-11 06:30 EDT) — see `docs/updated_plan6.md` §5

D-A freeze + S4-02 allowances · D-B SD-21 (B4 parity form, after the sensitivity control) · D-C coverage tooling · D-D S6 closed · D-E PA-2 promotion · D-F Codex's review-tools v2 patch, ENV-05 documentation patch and real install · D-G S7 CounterFact shared stratum short · D-H S1 report accepted. The items above in this file are superseded by that table where they overlap.

## Round 3 (2026-09-11 06:55 EDT) — see `docs/updated_plan7.md`

- **D-B answered: (b)** (DEC-020, SD-21). **D-F done** (commit `80ad746`). Open: D-A (requested after Lane V3), D-C, D-D, D-G, D-H; D-E passes tonight.
- Orchestrator today: V2-01…05 repairs; a dated "repairs landed" line will appear here for Codex's Lane V3.
- Codex: Lane B4-S (deadline 2026-09-12 12:00 EDT for inclusion in the freeze), Lane X, then S3-01.

- 2026-09-11 07:05 EDT (orchestrator → codex): **repairs landed** — V2-01…05 and the S5 exit-code note are repaired and re-checked with your study driver from a fresh fixture root (`logs/review_repairs_r2c.md`, `results/V2/v3/`; the pre-V3 driver is preserved at `results/V2/review_repairs_r2b_study.pre-v3.py`). Lane V3: rerun independently and confirm; the freeze request to the lead (D-A) follows your confirmation.

- 2026-09-11 07:30 EDT: lead accepted the defaults for D-A, D-C, D-D, D-G, D-H → DEC-021…024 recorded. Remaining lead act: the freeze command (posted below once Codex's V3 confirmation is in).
- 2026-09-11 07:35 EDT (orchestrator): GPU window 2 running — `-m gpu` test subset, then the real-artifact identity control (results/GPUWIN2/). Short tests by Codex are fine alongside; no lease is held.

## S4-02 scope and allowances — proposal for the freeze command (2026-09-11 07:20 EDT; orchestrator)

**Scope (re-priced with the measured grammar cost).** The grammar term was unpriced until now; `scripts/grammar_timing.py`
measured 0.085 accelerator s per sequence (learning + immediate evaluation, C1, the most expensive arm; C2 0.031, CR 0.061,
C0 0.051; `results/S2/grammar_timing.json`). At 10,000 sequences per task the grammar alone would cost 226 local GPU-h;
at 1,024 → 23 h; at **256 → 5.8 h**. The Section 9 algorithm now selects **zsRE 1000 / CounterFact 300 / grammar 256 per
task** at 26.3 of the 27.0 h available after headroom (`results/S2/projection.json`, `docs/D1_decision.md`); the freeze
draft's `stream_lengths` follow it (`grammar_train_count: 256`). Wall-clock is 2.5–3.7× the accelerator time on this
host for the grammar and 1.5–3× for editing (D1 memo §5): the S4 core is ≈ 60–80 wall hours serialized on the lease.

**Allowances (your S4-02 fields; defaults if you say "as proposed"):**

| field | proposed | basis |
| --- | --- | --- |
| `resource_rules.run_allowance_seconds` | **2400** | 2 × the largest projected run (C1 on zsRE, 1000 items: 1,147 accelerator s incl. rescoring); grammar runs project at 347 s; a run that exceeds it stops at an item boundary with status `resource_stop` and the exact completed prefix (stop policy in the draft) |
| `resource_rules.stage_allowance_seconds.S4` | **97200** | the S4 ceiling (36 A100-h at κ = 1) after the 25% headroom = 27.0 h; admission refuses a job when spent (all attempts) + 2400 s would exceed it (exit 5) |
| `resource_rules.stage_allowance_seconds.S5` | **64800** | the S5 ceiling (24 A100-h) after headroom |

**The command (yours; nothing else writes `manifests/frozen.json`):**

```bash
cd /home/derp/cap/pc_cap && /home/derp/cap/venv/bin/python -m pccap.harness.freeze --final --i-am-the-lead \
  --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800 [--accept-unavailable B4]
```

`--accept-unavailable B4` only if Codex's Lane B4-S has not landed by 2026-09-12 12:00 EDT (plan 7 §3); the orchestrator
posts "B4 registered" here when it has. Run it after Codex's Lane V3 confirmation (`logs/review_repairs_r2d.md`).

- 2026-09-11 08:05 EDT (orchestrator): **Codex's round 3 evaluated.** V3 confirms all five repairs (`logs/review_repairs_r2d.md`, 16 controls) — the freeze request (D-A) now stands; the command above is ready. B4: the sensitivity control did **not** reproduce the divergence class (same-framework value gaps ≤ 0.15 vs 22.4; `logs/grace_sensitivity_round3.md`), so under DEC-020 B4 stays unregistered while Codex localizes the first cross-framework gradient difference (in progress). Lane X: P4 reproduces on fresh seeds; its S7 findings 1–4 are repaired (`docs/tasks/S7-01.md`). The V3 note on duplicate roots/cells in the resource views is repaired (`s4_05.discover/require_one_experiment`). **Freeze timing:** either now with `--accept-unavailable B4` (reduced programme: the C2-vs-B4 contrast is not run), or at the 2026-09-12 12:00 EDT deadline if Codex's diagnosis lands a registrable B4 by then. Recommendation: wait for the deadline — the calendar has the slack and B4 is a named contrast.

## Freeze now (2026-09-11 08:30 EDT) — the lead said not to wait for B4

The draft records B4 `unavailable at freeze` with the DEC-020 reason and the grammar `available`; no pending inputs, so no
`--accept-unavailable` is needed. The command (yours):

```bash
cd /home/derp/cap/pc_cap && /home/derp/cap/venv/bin/python -m pccap.harness.freeze --final --i-am-the-lead \
  --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800
```

Then tell the orchestrator (or commit `manifests/frozen.json`); the queue starts immediately:
`python -m pccap.harness.schedule && python -m pccap.cli queue` (210 scheduled jobs, realization-major; B4's 30 listed
unavailable and never run). If Codex's B4 diagnosis later yields a registrable B4, adding it needs a versioned manifest
(plan 4 §2), not an edit of the frozen one.

- 2026-09-11 09:05 EDT (orchestrator): **frozen.json written by the lead** (sha `40e570fb5f63`, DEC-025). Job list regenerated from it; the S4 queue is starting (`results/S4/queue.jsonl`, per-job logs under `results/S4/queue_logs/`; stop file `results/S4/queue.stop`). Post-freeze rule in ongoing.md applies to everyone.

## Re-freeze needed (2026-09-11 10:05 EDT) — DEC-026

The first job under v1 hit a loader defect (the grammar's `.npz` binding made the realization loader refuse every editing
job; no item was edited; v1's attempt tree is archived). The loader is repaired with a regression, the queue stops on
systematic failures, and the draft is now `frozen-confirmatory-v2`. Please run **the same command again**:

```bash
cd /home/derp/cap/pc_cap && /home/derp/cap/venv/bin/python -m pccap.harness.freeze --final --i-am-the-lead \
  --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800
```

The orchestrator regenerates the job list and restarts the queue automatically when the new `manifests/frozen.json` appears.

- 2026-09-11 10:20 EDT (orchestrator): **frozen-confirmatory-v2 written** (sha `84126123f48c`, DEC-027); job list regenerated; the first job runs as a one-job session for verification, then the full queue.

- 2026-09-11 (orchestrator, during S4 execution): **realization 0 complete for all three datasets (70 runs, 3.9 accelerator h — about 45% of the projection).** CPU collectors run on it (`results/S4/partial/`, `results/S7/partial/`): zsRE 21,500 endpoint rows, CounterFact 7,500, resource views over 70 runs, order variation on 5 orders (zsRE C2 RET-GS std across orders 0.017; CounterFact 0.000 at the exact-key floor; grammar 0.003). **Known gap, deferred by the post-freeze rule:** `s4_06` derives the expected inventory for the grammar through the realization loader, which does not apply to the seed-addressed grammar streams (error `realization filename must have exactly one frozen binding`); the fix is an analysis-only change under `src/pccap/analysis/` and will be applied as a recorded analysis-tree version **after the S4/S5 queue finishes** (no source change while confirm-mode jobs run; the grammar rows and the other datasets are unaffected).

- 2026-09-12 11:55 EDT (orchestrator): **S4-04 complete** — 210/210 runs, 11.49 accelerator h (42% of the ceiling after headroom), no failures. zsRE and CounterFact paired analyses: classification **negative** on both required contrasts (zsRE C2−C1 RET-GS −0.030 [−0.041, −0.019]; C2−CR +0.000 [−0.013, +0.018]; CounterFact at the exact-key floor). **S5 queue started** (60 SE-A/SE-E jobs). Grammar paired analysis waits on the analysis-tree fix after S5 (post-freeze rule). D3 audit (S4-06) after that.

- 2026-09-13 02:45 EDT (orchestrator): **S5-02 complete** — 60/60, 8.89 accelerator h. Confirmatory execution is finished (S4 + S5 = 20.4 accelerator h). zsRE substrate contrasts: SE-A ≈ SB; SE-E retains +0.019 RET-GS but acquires 34% fewer edits (both negative by policy); CounterFact at the floor. **The post-freeze source rule is lifted for the analysis tree**: the grammar collector fix and the S7 checkpoint runner land next as analysis-tree version 2 (DEC-028), then the grammar paired analysis, the D3 audit (S4-06), the S7 checkpoint runs and the S8 report.

## Grammar paired analysis: SD-22 (2026-09-13 03:10 EDT) — a decision when convenient

The grammar's frozen paired analysis classifies **incomplete**: a per-process hash salt made the paraphrase seeds differ
between runs, and 0–3 items per cell of 2,048 have no paraphrase at all (undefined RET-GS), so ≈ 6 pairs per cell are
undefined and the policy refuses to infer them (SD-22). No arm is favoured by this. Applied now, no decision needed:
the classification is reported as `incomplete` **plus a labelled supplementary analysis on the complete-pair subset**
(`results/S4/partial/s4_06_grammar_supplement.json`). Your options if you want a confirmatory-grade grammar answer:
(b) an explicit exclusion category in the policy (post-hoc; DEC), or (c) rerun the 60 grammar runs (~1 accelerator
hour) under a version-3 manifest with the deterministic paraphrase seed. Default: (a) as applied.

- 2026-09-13 04:30 EDT (orchestrator): **Codex's round 4 evaluated.** B4-D: the first-gradient difference is localized to the *reference's* fp32 loss/head reductions (JAX is closer to float64); no JAX defect found; B4 stays unavailable and SD-21's cause statement is narrowed accordingly. S3-01 done (`docs/controls.md`, mirrored on the board). V4: the three S7 findings confirmed closed (9 S7 tests pass). Lane P: all 27 CPU reproduction commands run in the recreated environment; the three initial failures were path/env issues, fixed in REPRODUCE.md now. Pending proofreading request from Codex on its own B4-D report (count correction): fine to apply; it is Codex's file.

## Programme close-out (2026-09-13 05:45 EDT) — what remains, and what is yours

- Done: all confirmatory runs, the frozen analyses, D3 memo, S5 report, S7, analysis-tree v2, report draft 1 (`docs/report.md`).
- Running: S8-02 ablations (≈ 1 h). Then: report §8, S8-01 final reproduction audit (Codex Lane P2), S8-04 handoff package.
- **Yours:** (1) review the D3 memo and the report (T4 / CP-F before any external release); (2) SD-22 choice (default (a) applied; (c) = a 1-hour grammar rerun under a version-3 manifest if you want a confirmatory-grade grammar row); (3) whether to accept S1-07 (D-H stayed partial).

- 2026-09-13 06:05 EDT (orchestrator → codex): **S8-02 done** — Lane P2 (final-tree reproduction audit) is open; the tree is at the commit after this line. Lane X2 (report review) is open as well: `docs/report.md` now has every section filled.

- 2026-09-13 07:35 EDT (orchestrator): **frozen-confirmatory-v3 written by the lead** (DEC-030); the 60 grammar reruns are queued (`results/S4/queue_session4_grammar_v3.log`); experiment id `frozen-confirmatory-v3-163d04e2`. Codex: the tree hash changed with the seed fix; nothing else changes for your lanes.

- 2026-09-13 12:30 EDT (orchestrator): **Codex's P2/X2 evaluated and applied.** The documentation-correction patch is applied verbatim (12 findings; the primary classifications are unchanged). DEC-031 records the source-version register and the v3 grammar inventory rule (paraphrase-less items excluded by an outcome-independent rule, counts disclosed). S8-01 done (Codex's final-tree audit). **Two items for you:** (1) X2-05 — the editing drift assay scores 4,064 positions, not the full 247,289-token validation split SD-3 asks for; a full-validation drift evaluation on the endpoint checkpoints of the zsRE cap arms (15 runs, ≈ 1 GPU-h, read-only) can be run as a labelled supplement if you want it — say so; (2) the v3 grammar inventory rule (DEC-031) — accept as disclosed, or require full paraphrase coverage before a v4.

- 2026-09-13 (lead → orchestrator): v3 grammar inventory rule **accepted** (DEC-032). Open: the drift-assay supplement (X2-05) — unanswered, default: not run, disclosed as a limitation.

- 2026-09-13 14:05 EDT (orchestrator): **drift supplement done** (lead-requested, run concurrently): cap arms ≤ 1.0036 perplexity ratio on the full validation split; B3 1.884. `results/S4/drift_supplement.md`; report §5 and D3 §7 updated.

- 2026-09-13 17:25 EDT (lead → orchestrator): **plan 9 approved with all defaults** (DEC-033); the orchestrator continues autonomously through the v0 close-out and into Stage 0 of revision v1, committing as it goes.

- 2026-09-13 17:15 EDT (orchestrator → codex): **hold all `.py` writes under `src/pccap/` (revision_v1 included) until the "v0 close-out committed" line below** — the v3 freeze hashes every `.py` under the package and the remaining grammar jobs would refuse. Draft under `revision_v1_staging/` meanwhile; R1-00 (scripts/, manifests/) and R1-X0 (logs/) are unaffected.

- 2026-09-13 17:56 EDT (orchestrator → codex): **the v3 grammar rerun is finished (60/60); no confirm-mode job remains — `.py` writes under `src/pccap/` (revision_v1 included) are allowed again.** The "v0 close-out committed" line follows once the grammar analyses and the report/memo updates are in (≈ 30 min); it does not gate your lanes.

- 2026-09-13 18:15 EDT (orchestrator): **v0 close-out committed.** Grammar v3 row: complete, negative (RET-GS identical across arms at the exact-key floor; 2044/2047/2046 items; DEC-032 rule applied; 140 endpoint rows of the 7 excluded items dropped, counted). Report §1/§5/§9 and D3 §8 updated; S7 grammar reversals rerun under v3; drift supplement in §5/§7. The primary claim is not supported on any dataset. Remaining for the lead: T4 review of `docs/report.md` and `docs/D3_decision.md`. Revision v1 Stage 0 diagnostics are running.

## 2026-09-13 evening — revision v1 progress while you were away (orchestrator)

No action needed to keep work moving; three items for your review when convenient:

1. **Stage 0 diagnosis memo** `docs/R1_diagnosis.md` (Codex counter-review lane R1-X1 open). Locus: storage exonerated
   (oracle 0.94 paraphrase exact on both arms), observation instability first (cap-off keys+queries 0.24→0.67 / 0.29→0.49
   post hoc; in-stream v0-stable control RET-GS 0.24/0.29→0.44/0.44), record selection second.
2. **DEC-034** (plan-9 amendments from Codex's counter-review, `docs/tasks/R1-X0-response.md`) and **DEC-035** (a
   non-learned "v0-stable" control joins the comparative design). Both taken under DEC-033's delegation; override if you
   disagree.
3. **Stage 1–2 code** is installed (`src/pccap/revision_v1/`, 66 tests) with the loss-source table
   `docs/revision_v1_losses.md`; a bounded synthetic pilot of the differentiable reference is the last GPU job
   (`results/R1/pilot/`). Nothing confirmatory has been run; no freeze is requested yet (R1-40/41 come after Stage 2).

Still outstanding from v0: your T4 review of `docs/report.md` and `docs/D3_decision.md`.

4. (later the same evening) **Stage 2 pilots**: the differentiable reference trains — on held-out synthetic episodes the
   learned reader answers 41 % of unseen paraphrases exactly (from 3 % after the first short pilot) while leaving
   unrelated answers unchanged (100 %) and near-misses (94 %); the matched ePC-surrogate run at the identical schedule is
   in progress (`docs/R1_stage2_notes.md`). Non-learned controls on the 100-edit zsRE stream: v0-stable and
   matched-update both at RET-GS 0.44 (v0 live 0.24/0.29).

5. (21:20 EDT) **SD-24 — please read before your T4 review of the report.** The v0 ePC base penalized the cap write inside
   the site's prior energy, so the S5 SE-E (finite-error credit) row measured a defective rule; SE-A and every cap arm are
   unaffected. I fixed the energy in place (DEC-036) because revision v1's ePC surrogate needs it; the report and memo
   carry the annotation. Decision for you: rerun SE-E under a version-4 manifest (≈ 3 A100-hours) or leave the row
   annotated. Default if you say nothing: leave it annotated.

6. (late evening) Codex's round 2 landed and is committed: exclusion register v1 (155,322 raw / 88,267 unique-subject
   candidates after all filters), a CounterFact episode corpus, a memo counter-review (all eight findings adopted) and a
   code audit (ten findings; six repaired tonight, four answered — `docs/tasks/R1-23-response.md`). One of the audit
   findings (R23-02) explained the memorization I saw in the CounterFact pilot: the record code was built from the
   support prompt only, so the taught answer never entered memory; fixed. Pilots run before the fix are kept as history.

7. (late) **DEC-037** — I drew a 3,000-item CounterFact TRAINING pool from the unopened remainder of the old eligible pool
   (sealed realizations, exposed subjects and single-paraphrase items removed; provenance in the manifest). Reason: the
   development pools are too small and the reader memorizes them. The pool is never confirmatory and its subjects go into
   the exclusion register v2. Override if you want the remainder kept whole for a CounterFact confirmatory draw (16,141
   items remained before the draw; 13,141 after).

8. (2026-09-14, 01:10 EDT) First revision-v1 learner numbers above the controls on the zsRE development stream: with
   stable observations, a siamese cosine reader and v0-style per-position writes, RET-GS 0.65 vs 0.44 for the non-learned
   controls (ES 1.00) — but locality is not yet handled (LS 0.24 without a null). The trained null is the next step;
   `docs/R1_stage2_notes.md` has the chain of intermediate results.
   Update (01:40 EDT): with a cosine firing threshold the same condition keeps LS 1.00 (ES 1.00, RET-ES 1.00,
   RET-GS 0.65). It has no trained component at all — a strong, simple reference the learned reader now has to beat.

9. (2026-09-14, 04:45 EDT) Codex's round 3 is in (committed): exclusions v2 (entity/exposure policy; 154,306 raw /
   87,857 subject candidates for the fresh zsRE draw), the synthetic final namespace v2 (reservation only — emission
   waits for your authorization), the R1-24 continuation-control harness, and a re-audit whose six findings I am
   repairing. Two items for you, defaults stated:
   - **R1-D1b policy acceptance**: accept Codex's conservative v2 exclusion policy (644 quarantines, 2 verified aliases,
     14 releases). Default: accepted as the register for the fresh draw; candidate-level review and the E.2 pass follow.
   - **R1-24 interpretation**: literal "teacher = same checkpoint" continuation is a no-op (zero KL and gradient), so it
     is only a numerical negative control. Default: run it as such (cheap), and add ONE informative continuation
     condition — continued language-model training of the base on the matched OpenWebText token budget from the same
     shard, then the same editing evaluation — as the X0-01 control proper. Say if you prefer a different treatment.

10. (05:55 EDT) Status of the learned reader: the trained null decision is correct inside training-style episodes but
    does not transfer to the evaluation streams (zsRE LS 0.10; CounterFact rejects half the own prompts). One more
    data fix is training now (locality near-neighbour prompts as null targets; result ≈ 07:35 EDT). If it does not
    transfer either, my recommendation will be to keep the null non-learned (cosine gate) and let the learned part be
    the similarity only — the simpler measured control already gives RET-GS 0.65 / LS 1.00 on zsRE. No decision needed
    from you yet; I will state one when the run is in.

11. (07:40 EDT) **Decision item (DEC-038 proposal): drop the learned reader from the primary revision condition.** All
    five trained nulls fail to transfer to the evaluation streams (details in `docs/R1_stage2_notes.md`). Default if you
    say nothing: the primary revision condition is the non-learned system (stable observations + random tied cosine
    embedding + per-position gradient writes + cosine gate 0.93), which beats the controls on zsRE (RET-GS 0.65 vs 0.44
    with LS 1.00); the learned reader is a secondary, honestly-negative condition; CounterFact near-neighbour locality is
    reported as unsolved. Stage 4's run matrix (Codex's R1-40 draft) would be pruned accordingly before the profiling
    runs. I will not launch any further reader training unless you ask.

12. (08:40 EDT) Per your direction, the learned reader is the priority: the recovery plan (five mismatches, five fixes,
    order and success criterion) is in `docs/R1_stage2_notes.md`; DEC-038 stays a proposal, not a decision. First run:
    stream-scale training episodes with locality near-neighbours as nulls. One data decision inside the plan:
    a zsRE TRAINING pool of 3,000 items from the fresh-draw candidates (exposure recorded; removed from the confirmatory
    draw) — default: yes (DEC-039), Codex prepares the list, I run the teacher filter.

13. (11:05 EDT) **The learned reader now works on CounterFact**: stream-scale training + a lexical overlap feature give
    ES 1.00 / RET-ES 1.00 / RET-GS 0.775 / LS 1.00 on the CounterFact development stream (v0: 0.00 at the exact-key
    floor; every control 0.00–0.18). zsRE is not there yet (RET-GS 0.49, LS 0.98 — the null over-rejects zsRE
    paraphrases after CounterFact-only training); the zsRE training pool (DEC-039, Codex R1-D3) and a per-dataset
    threshold are next. DEC-038 as proposed is withdrawn: the learned reader stays in the primary condition.
    Update (11:40 EDT): on zsRE the same trained reader with the cosine gate reaches ES 1.00 / RET-ES 1.00 / RET-GS 0.97 /
    LS 1.00. The similarity is solved on both datasets; only the locality decision differs per dataset (learned null on
    CounterFact, cosine gate on zsRE). One rule for both waits on the zsRE training pool (Codex R1-D3 → my teacher filter).

14. (12:30 EDT) Learned-reader status after the recovery work: with stream-scale training and a lexical overlap feature
    the reader's similarity is strong on both datasets — CounterFact RET-GS 0.78–0.93 (three seeds) with LS 0.92–1.00
    under the learned null; zsRE RET-GS 0.95–0.97 with LS 0.96–1.00 under the cosine gate. What remains is one locality
    rule for both datasets: the CounterFact-trained null over-rejects zsRE paraphrases or under-rejects zsRE unrelated
    prompts, and the cosine gate fails on CounterFact near-neighbours. The fix on the table is the zsRE training pool
    (DEC-039, default yes) so the null sees both domains; Codex's R1-D3 candidate list is the blocker, my teacher filter
    is ready. Fallback: a per-dataset rule fixed on development streams before the freeze (stated in the protocol).
    DEC-038 (drop the learned reader) is withdrawn.

15. (14:50 EDT) **One rule for both datasets.** With Codex's zsRE candidate list filtered by the teacher (DEC-039) and
    mixed-domain stream-scale training, the learned null alone (threshold 0.5, no gate, nothing per dataset) gives
    zsRE ES 1.00 / RET-ES 1.00 / RET-GS 0.98 / LS 1.00 and CounterFact 1.00 / 1.00 / 0.80 / 1.00 on the development
    streams. The learned reader is the primary revision condition; the per-dataset fallback is no longer needed.
    Remaining before Stage 4: seed/stream replication (running), Codex's re-audit of the new trainer, the run matrix
    (R1-40b) and your freeze. Decisions still open for you: the R1-24 informative continuation condition; acceptance of
    exclusions v2 (register v3 will add the 6,000 drawn zsRE subjects).

16. (2026-09-14 afternoon) R1-24 decided: option 3, both treatments (DEC-040). Running.

17. (12:15 EDT) R1-24 done (both treatments; `docs/R1_stage2_notes.md`). Continued-base training does not explain the
    revision's gain (S1−S0 within ±0.05 RET-GS; R0−S1 +0.49 to +0.59 zsRE, +0.78 to +0.80 CounterFact). The informative
    LM continuation fails its own fidelity gate (the base moved 0.095 nats on the held-out tail), so a KL-bounded variant
    is the follow-up if you want that control certified; the literal control passes and is the recorded negative control.

18. (2026-09-14, 13:00 EDT) Round 7 committed; exclusion register accepted (DEC-041). Two items:
    - **CounterFact confirmatory source (R1-D2)**: under the strict v3 register the old remainder yields 0 items; a
      reason-specific exception ("old-pool membership alone is not exposure") yields 12,246 (after the DEC-037 training
      draw and all other reasons); no distinct fresh CounterFact source exists locally. Default if you say nothing: the
      exception (it is the plan-9 option-a reading), recorded as DEC-042 with the draw excluded by id and subject from
      everything exposed.
    - **New scientific risk from Codex's report addendum**: the learned cap raises ordinary-text loss after edits
      (+0.60 nats zsRE, +0.39 CounterFact on the 16,256-position drift subset) — the null was never trained on ordinary
      text. Diagnosis and a fix (ordinary-text windows as null targets) are my next work (R1-54); no decision needed.

19. (2026-09-14, 13:20 EDT; while you are away) **R1-54 resolved; reference condition v2.** Training the null on
    ordinary-text windows removes the drift (zsRE edits: 0.000 nats; CounterFact edits: +0.012 nats vs +0.379 for the
    v1 reader) with retention intact over three seeds (zsRE RET-GS 0.96–0.98, CounterFact 0.725–0.85, LS 1.00 on all).
    `manifests/revision_v1/primary_condition_v2.json` is the development reference now; nothing is frozen. Endpoints on
    the real base with it: near-miss preservation 100/100, revision 100/100, unseen-edit-prompt false fires 7 % (zsRE)
    and 0 % (CounterFact) after 100 edits. Running next, unattended: the R1-40c P1 edit/memory profile (edit and query
    cost, persistent-state bytes and restore equality at 100/300/1,000 records, learned and non-learned) and the
    unseen-prompt endpoint at 300 and 1,000 records. Memory above 300 records uses training-pool rows beyond the 1,000
    the reader was trained on as labelled fillers — no fresh candidate is opened. Two things remain yours: DEC-042
    (CounterFact source; default = the exception) and, after the profiles, the run-matrix scope: Codex's v3 draft prices
    the legacy proxy at 223 h against the 15 h envelope, so a scope cut is needed before any freeze (I will propose one
    with the measured ceilings).

20. (2026-09-14, 13:30 EDT) **Run-matrix scope — a decision for you before the freeze.** Measured on the real base
    (P1 profile + endpoint runs, wall time): a learned 1,000-edit cell with every endpoint at all three checkpoints costs
    ≈ 1,150 s (edits 73–111 s; retention decoding ≈ 20 ms per query; full drift assay ≈ 165 s per checkpoint; near-miss +
    revision ≈ 150 s), ≈ 23 min with the 0.2 reserve, so Codex's 240-cell v3 matrix is ≈ 92 h against the 15 h
    envelope. Proposal (default if you say nothing): all eight conditions, both datasets, three realizations, ONE update
    order per realization (48 cells); full drift assay and the challenge endpoints at the final checkpoint only, the cheap
    endpoints (retention, locality, unseen) at 100/300/1,000 — ≈ 14 min per cell, ≈ 13.5 h with reserve. Cost: order
    effects are unmeasured in the confirmatory runs (stated in the protocol). Alternatives: (b) drop the two S1
    continuation conditions and matched-update → 30 cells, two orders fit; (c) raise the envelope. The full report
    revision is `docs/R1_stage2_report.md` (Codex's draft preserved). Scale facts you should know: 1,000 records use
    51–74 % of the state ceiling (admissible on both datasets); CounterFact locality firing rises to 10 % at 1,000
    records; zsRE accepts 25 % / 45 % of pool-sourced unseen edit prompts at 300 / 1,000 records (7 % of dev-remainder prompts at 100) — the largest open scale risk.

21. (2026-09-14, 14:00 EDT) **R1-56 and DEC-043 (proposed).** The zsRE unseen-prompt false fires that grow with memory
    (7 → 25 → 45 % at 100 / 300 / 1,000 records) are all same-relation, different-subject prompts: the fired record
    shares only template words with the query. A non-learned gate — the query must share one memory-rare token with the
    selected record — cuts them to 5 / 11 / 10 % (CounterFact 5 → 0 % at 1,000) at a cost of at most one CounterFact
    paraphrase on the streams. Default if you say nothing: it joins the primary condition as v3
    (`manifests/revision_v1/primary_condition_v3.json`); v2 stays the no-gate comparison. The stricter two-token gate is
    rejected (it refuses single-token subjects: CounterFact RET-GS 0.62). Everything above is committed; Codex's round 8
    files are untouched and uncommitted until you say Codex is idle.

22. (2026-09-14, 17:30 EDT) Recorded: DEC-043 accepted (gate → primary condition v3); DEC-044: scope not cut — the full
    240-cell matrix stands and its ceilings will be set from the measured components (≈ 92 h; the 15 h envelope is
    superseded by your decision). DEC-042 (CounterFact source) is explained in the session reply and stays open; the
    default (reason-specific exception) applies only if you say nothing before the draw.

23. (2026-09-14, 17:45 EDT) DEC-045 recorded: MQuAKE-CF downloaded and approved as the third dataset; Codex lane
    R1-D4 prepares it (item conversion, locality/near-miss prompts, composition inventory, register cross-check). One
    consequence to confirm: keeping CounterFact means the DEC-042 exception (reading a) is the only source for its
    fresh streams — I will treat it as accepted unless you object. The matrix becomes 8 conditions × 3 datasets × 3
    realizations × 5 orders = 360 cells; with the measured per-cell cost that is ≈ 140 h of accelerator wall time.
    Whether the reader is also trained on a MQuAKE pool (same-source claim, as for zsRE and CounterFact) or evaluated
    on MQuAKE as a transfer test is your call; default: a 1,000-item MQuAKE training pool and a three-seed retrain.

24. (2026-09-14, 18:50 EDT) MQuAKE teacher pass done: all 6,043 prepared items are teacher-eligible (the base never
    produces the counterfactual target). DEC-046 (proposed default): 200-item development slice + 500-item training
    pool (not the 1,000 I first suggested — yield), zsRE-overlap subjects left to zsRE, ≈ 5,150 items kept for the
    confirmatory draw. The reader retrain on three pools and the MQuAKE development streams run next; say "transfer
    only" if you would rather not train on MQuAKE. R1-24 follow-up: the informative LM continuation still fails its
    fidelity gate at lr 1e-7 (KL 0.019 vs the 0.001 gate); lr 3e-8 and 1e-8 are running to map the curve — at the
    lr where the gate passes the base has barely moved, so U03 will likely resolve as a labelled failed gate or a
    scope amendment rather than a certified informative control.

25. (2026-09-14, 20:50 EDT) **MQuAKE on the real base, first numbers.** Reader retrained on three pools (CounterFact
    1,000 + zsRE 1,000 + MQuAKE 500), gate on, 100-edit development streams: MQuAKE RET-GS 0.80 / 0.47 / 0.82 (seeds
    0–2; LS 1.00 / 0.98 / 0.98), zsRE 0.98 / 0.97 / 0.98, CounterFact 0.66 / 0.85 / 0.83. The v2 reader without MQuAKE
    training reaches only 0.16 on MQuAKE, so training on it is necessary (DEC-046 default confirmed). Seed 1's loss is
    null calibration on the question-form paraphrases (raising the threshold recovers 0.76–0.81 at an LS cost), so a
    1,000-item MQuAKE pool (v2, superset of v1; 4,489 items left for the confirmatory draw against ≈ 4,050 needed) is
    being retrained now. MQuAKE unseen-prompt false fires 0/100 at 100 records; ordinary-text drift +0.005 nats.
    R1-24: a fidelity-valid informative continuation exists at lr 1e-8 (DEC-047); same verdict as the literal control.

26. (2026-09-14, 22:25 EDT) **MQuAKE status at the end of the day.** Reader retrained on three pools (proposed primary v4,
    `primary_condition_v4.json`, MQuAKE pool 1,000): zsRE 0.95–0.98, CounterFact 0.76–0.83, MQuAKE 0.56–0.79 across seeds,
    LS 1.00; MQuAKE unseen false fires 0 %, drift +0.005 nats. MQuAKE's paraphrase retention is seed-sensitive
    (0.47–0.82 over six readers) because its question-form paraphrases are decided by the lexical feature alone; a
    memory-rarity-weighted lexical feature was implemented and tested (R1-57c) and not adopted (it costs own-prompt
    acceptance). Decisions for you, defaults stated: (a) MQuAKE pool size 1,000 (DEC-046 v2 sizes; 4,489 items left
    for the confirmatory draw against ≈ 4,050 needed) — default yes; (b) checkpoint selection on a MQuAKE stream
    criterion before the freeze — I propose to add it (one more retrain) unless you say no; (c) DEC-047 S1_LM at
    lr 1e-8 as the certified informative continuation — default yes. GPU work is paused until Codex's round 10 lands.

27. (2026-09-15, 17:30 EDT) **MQuAKE population — your decision (Codex R1-D7, `docs/tasks/R1-D7.md`).** Under the cumulative
    exposure reading MQuAKE has 2,100 distinct candidate subjects; three realizations of 1,000 edits plus the 350-subject
    endpoint reserves each need 4,050. Options with counts: (A) keep the exclusions and amend MQuAKE to 3 × 300 edits
    (demand 1,950; Codex's recommended default; the 100/300 checkpoints survive, the 1,000-edit claim is dropped for
    MQuAKE only); (B) executed-only reading: at most 2,829 subjects even if every review candidate clears — still short;
    (C) exempt true-fact locality/unrelated presentations from counterfactual-edit exposure: 4,218 subjects, enough for
    the full scope, but a policy change Codex does not recommend purely to recover sample size; (D) MQuAKE-T cannot fill
    it (96 distinct edits). My view: (A) is defensible and honest; (C) is scientifically reasonable — the reader saw
    those subjects' TRUE facts as null queries, never the counterfactual edits — but a reviewer may call it
    self-serving. Default if you say nothing: (A). Either way the matrix and protocol get a new version.

28. (2026-09-15, 18:05 EDT) Recorded DEC-048 (option C). Consequences now in motion: Codex lane R1-D1h writes register policy v5
    (query-role exposure waived for MQuAKE, everything else retained) with the capacity table and the abort rule; the matrix
    stays at 360 cells × 1,000 edits; the protocol gets a v4 stating the reading in its exposure section so a reviewer sees
    it declared rather than discovered. Margin is thin (4,218 vs 4,050 before alias/context clearance), so R1-D1h also
    reports what clearance removes; if it falls below demand you will get the numbers, not a silent cut.

29. (2026-09-15, 18:45 EDT) **Measured cell cost.** The Stage 4 driver, run clean on the real base for a 300-edit zsRE
    development cell, costs 1,252 s; extrapolated to a 1,000-edit learned cell ≈ 49–66 min (59–79 min with reserve), so
    the 360-cell matrix is ≈ 350–475 h of accelerator wall time as the driver stands. About two thirds of that is the
    driver's own per-phase overhead (1.0 s per edit and per immediate check versus 0.13 s of model work). I have posted a
    driver-performance lane for Codex (R1-68) that should roughly halve it while keeping every integrity guarantee; the
    ceilings in the matrix will be set from the re-profiled driver. No scope change is proposed (DEC-044).

30. (2026-09-15, 15:30 EDT) **Lockup forensics installed.** Two hard hangs today (journal boots −2 and −1 end at 14:19:58 and
    15:16:34 with no kernel message at all — no OOM, Xid, hung-task or thermal line — which is the signature of a hard
    GPU/driver or platform hang rather than a memory kill). `scripts/sysmon.sh` now runs as the user service
    `pccap-sysmon` (enabled at boot; linger is on): every 10 s it appends GPU util/memory/temperature/power/clock/throttle
    reasons, GPU processes, load, memory, swap, PSI stalls, top CPU/RSS processes and any new kernel GPU/OOM/lockup lines to
    `logs/sysmon/sysmon-<date>.log`, flushed to disk. After the next hang run
    `python scripts/sysmon_report.py --before-boot -1 --window 180`. What was on the GPU during both hangs: my reader
    training (2.4 GB) plus, in the first, two more of my jobs overlapping, and always the PeTTa `swipl` agent (1.45 GB GPU,
    1.2 GB RSS) and Chrome's GPU process. I now run my GPU jobs strictly one at a time. Root-level options only you can
    enable if you want kernel-side evidence: `sudo sysctl -w kernel.nmi_watchdog=1 kernel.hung_task_panic=1` and kdump.

31. (2026-09-15, 15:55 EDT) **Cause of the hangs found: host memory, not the GPU.** The forensics log caught the third hang:
    my stream trainer grew from 6.8 GB to 22.7 GB RSS in 21 minutes (+1.1 GB/min), swap filled, the machine thrashed and
    stopped responding. The GPU was idle and cool. Mechanism: the trainer compiles a separate XLA executable for every
    distinct prompt-prefix length, and the three-pool runs with text and question nulls keep producing new lengths, so
    compilations never stop and each executable stays resident. Fix in progress (CPU only): bucketed prefix padding so
    the executable set is bounded, plus a memory guard that saves the best checkpoint and exits before RAM runs out. I will
    not start any GPU job until you say so; when you do, the first run will be watched by the forensics log.

32. (2026-09-15, 16:05 EDT) **Heavy-tail plan for the October 15 talk:** `docs/heavy_tail_counter_review.md`. It agrees with
    Codex's memo, adds a loss-level κ pilot (coupled logarithm in the answer and preservation terms; κ ∈ {0, 0.2, 0.5};
    3 seeds; clipped-surprisal control; ≈ 2.5 GPU h; decision rule fixed in advance), keeps every registered goal, and
    puts one hard fact in front of you: at the measured 49–66 min per cell the 360-cell matrix does not fit the ≈ 306
    usable GPU hours before October 9. Decisions by September 20: the block order (§5.1), the κ go/no-go, and — if the
    re-profiled driver does not close the gap — scope amendment vs more capacity vs an accepted incomplete matrix.
    Codex has four additive CPU lanes (HT-1..4). No GPU job runs until you say so.

33. (2026-09-15, 16:45 EDT) **Memory rules for every future GPU run** (cause of the three hangs: my stream-training runs, host RAM,
    not the GPU — per-shape XLA recompilation grew resident memory +1.1 GB/min; Codex's work is CPU-only and was not involved):
    1. Input shapes are padded to fixed buckets (prefix length ×16, group rows 1/2/4/8/×8, query count ×8, zero-weight pads) so
       the compiled-executable set is bounded — validated: resident memory plateaus at ≈ 6 GB (old code: 23 GB), steps ≈ 20× faster.
    2. `jax.clear_caches()` every 50 training steps.
    3. Memory guard: MemAvailable checked every 10 steps; below 4 GB the run saves its best checkpoint and exits.
    4. One GPU job at a time; no overlapping trainings or evaluations; chains are sequential.
    5. Two boot-time monitors watch every run (`pccap-sysmon`: GPU/memory/swap/pressure/kernel clues; `pccap-process-memory`:
       per-process RSS history); the first full 1,000-edit driver cell will be watched for resident-memory growth before any
       unattended use.

## Open decisions ledger (2026-09-15, 16:45 EDT) — nothing below starts until you answer

Rule you asked for: a task that depends on one of these answers does not commence until the answer is recorded here and in
`docs/decisions.md`; defaults are stated but are NOT applied to these items without your word.

| id | question | proposed default | blocked until answered | needed by |
| --- | --- | --- | --- | --- |
| Q1 (DEC-042) | **ANSWERED 2026-09-15: yes** — the reason-specific exception (12,246 candidates). | — | unblocked: the CounterFact confirmatory draw | — |
| Q2 (DEC-047) | **ANSWERED 2026-09-15: yes** — S1_LM = the lr 1e-8 continuation. | — | unblocked: the S1_LM cells | — |
| Q3 (item 26b) | **ANSWERED 2026-09-15: yes** (DEC-049) — stream-based checkpoint selection on all three datasets. | — | unblocked: the selection retrain | — |
| Q4 (counter-review §4) | **ANSWERED 2026-09-16: go** (DEC-054) — Matthew Ikle reviewed the pivot and counter-review and concurs; results to be framed as preliminary hints per §4 "What it is not". | — | unblocked: the κ pilot (launched) | — |
| Q5 (counter-review §2/HT-2) | **ANSWERED 2026-09-16: go** (DEC-055) — six development cells, 4 GPU-h ceiling, after chain I. | — | unblocked: the stress panel | — |
| Q6 (counter-review §5.1) | **ANSWERED 2026-09-16: as proposed** (DEC-051). | — | unblocked: block scheduling | — |
| Q7 (counter-review §5.3) | **ANSWERED 2026-09-16: as proposed** (DEC-052) — block order, no cut, re-measure Sep 20, accepted-incomplete reporting if needed. | — | unblocked: freeze preparation | — |
| Q8 (protocol v4 §6) | **ANSWERED 2026-09-15: confirmed** (DEC-050) — mean RET-GS s.t. zsRE unseen ≤ 10 % at 100 records and LS ≥ 0.98, on common populations. | — | unblocked: the selection and its freeze binding | — |
| Q9 (protocol v4 §6, LS convention) | **ANSWERED 2026-09-16: bounded text equality primary** (DEC-053); termination-qualified counts and truncation reported alongside. | — | unblocked: the driver's LS/near-miss reporting rule (Codex edit request); confirmatory LS readings | — |
| Q10 (R1-76 memo) | **ANSWERED 2026-09-16: B** (DEC-056) — review the 700 historically exposed rows; 100 / 300-record MQuAKE diagnostic, 1,000 point absent. | — | unblocked: lane R1-76b (Codex), then the run | — |
| Q11 (protocol v5 U12; `docs/tasks/R1-49f-lead-bindings.md`) | **ANSWERED 2026-09-16: accepted as proposed** (DEC-057). | — | unblocked: protocol v5 binding (lane R1-49g) and the R1-75 contrast module | — |
| Q12 (U13) | **ANSWERED 2026-09-16: accepted as proposed** (DEC-058). | — | unblocked: protocol v5 binding (lane R1-49g) and the R1-75 contrast module | — |
| Q13 (U14) | **ANSWERED 2026-09-16: accepted as proposed** (DEC-059). | — | unblocked: protocol v5 binding (lane R1-49g) and the R1-75 contrast module | — |
| Q14 (R1-D10a capacity) | **ANSWERED 2026-09-17: option D** (DEC-060) — context-match review first (R1-D10e), then MQuAKE at 300 edits × 3 realizations, checkpoints 100 / 300, with the restored margin; a larger cadence, if the review allows one, comes back as a question. | — | unblocked: R1-D10d option-A deltas, R1-D10e review, then the MQuAKE draw | — |
| Q15 (near-miss family) | **ANSWERED 2026-09-17: adopt as proposed** (DEC-061). | — | unblocked: the near-miss rows of the draw / seal and protocol v5.2-D | — |
| Q16 (near-miss pair allocation) | **ANSWERED 2026-09-17: B** (DEC-062) — family-coordinated pair allocation for the near / neighbour roles, bound in the RNG admission. | — | unblocked: R1-D9f activation; the draw | — |
| Q17 (fidelity limit scope) | **ANSWERED 2026-09-18: option 1** (DEC-064) — cap fidelity is a declared secondary benchmark (KL and NLL, pass / fail, concentration statistics), no veto; the continued-base gate unchanged. | — | unblocked: protocol v5.2-D.3 (R1-49m), candidate v14 | — |
| Q18 (MQuAKE scope) | **ANSWERED 2026-09-18: B** (DEC-066) — MQuAKE core = primary + floor + v0_stable, 45 cells; the five radius-0 conditions recorded as determined by calibration v3. | — | unblocked: matrix / protocol D.4 with candidate v14 | — |
| Q19 (three-realization inference) | **ANSWERED 2026-09-18: A + C's t-interval display** (DEC-069). | — | unblocked: protocol D.5 in the re-bind (R1-63o) | — |
| Q21 (post-freeze execution allowance; `docs/tasks/R1-77g-Q21.md`) | Replace the two-worker ceiling multiplier 1.15 → 1.7 (measured block-1 maximum 1.66) on the unchanged solo ceilings for future dispatch, keeping the frozen matrix, recipes, populations, scoring, the 1.5 solo factor, the 750 process-hour cap and the October 9 stop; applied by draining the queue at the block-2 boundary (stop-after 2), reconciling while idle, and resuming under a new signed resume request bound to bindings v2. Options: **(A)** all 330 cells (ceiling-sum scenario 894 h > 750 cap — a worst case, not a forecast; expected spend ≈ 350 h; the cap check is per dispatch, so it only bites if actual spend approaches 750); **(B)** the two observed classes only (primary zsRE, v0_stable CounterFact; 30 cells; scenario 640 h) — but the unobserved CounterFact controls and S1 classes share the same full-validation load and would likely also hit 1.15× ceilings. | **ANSWERED 2026-09-20: A, resume delegated to the orchestrator** (DEC-072) | drain at the block-2 boundary, reconcile idle, resume stop-after 6 (all remaining blocks) | — |
| Q20 (block order) | **ANSWERED 2026-09-18: adopt** (DEC-068) — triplet across all realizations first. | — | unblocked: matrix D.5 block numbers in the re-bind | — |

Answered or superseded: sysctl/kdump root commands (held off, item 30); MQuAKE training vs transfer-only (settled by evidence:
transfer 0.16 vs 0.79 trained, item 25); MQuAKE pool size (superseded by the self-contained v3 slices, 500 train / 100 dev).

34. (2026-09-15, 17:05 EDT) Q1, Q2, Q3, Q8 answered and recorded (DEC-042 accepted, DEC-047 accepted, DEC-049, DEC-050). Still open: Q4 (κ pilot), Q5 (stress panel), Q6 (block order), Q7 (feasibility) — by September 20.

35. (2026-09-15, 20:05 EDT) Codex's round 14 and heavy-tail lanes are committed (`9038b9a`). Two things it found that matter:
    (a) my first κ preservation term was not a proper divergence — repaired (f-divergence form, tests rewritten; details in the
    notes); the κ pilot manifest goes to v2 after Codex re-reviews (HT-3b) and then needs your Q4. (b) The draw plan and the
    freeze candidate refused because register v5 binds the live decisions file, which every accepted decision changes;
    Codex rebinds to a frozen snapshot (R1-D1i). Also delivered: the incremental driver profile (I re-profile it next), the
    stored-results tail audit (the +3.79-nat outlier reproduces; the two full drift sets are identical runs, not
    replications), the six-cell stress contract, and an 18-row claim–evidence ledger for the talk.

36. (2026-09-15, 22:10 EDT) **Primary condition v5 selected under your rule (DEC-049/050).** Winner: question-null family,
    seed 2, average of checkpoints 150–300 — mean RET-GS 0.803 (zsRE 0.98, CounterFact 0.82, MQuAKE 0.61), ES 1.00, LS ≥ 0.98,
    zsRE unseen false fires exactly 10 % (the limit; 10 of 100 prompts). The unconstrained best readers reach 0.85–0.87 mean
    RET-GS but fire on 19–55 % of unseen prompts, so the constraint is doing real work; checkpoint averaging removed the
    seed lottery on retention but not on rejection. R1-X12 (Codex) now reviews the selection. Codex's round 15 also landed:
    register v6 bound to a frozen decisions snapshot (draw plan and freeze candidate v3 now emit), κ pilot manifest v2
    (objective passes its re-review; Q4 still yours), and the stress-panel driver (Q5 still yours).

37. (2026-09-15, 23:00 EDT) v5 endpoint battery on the real base: near-miss 100/100, revision 100/100, second stream zsRE 0.99 /
    CounterFact 0.745 (LS 1.00), zsRE unseen false fires flat at 10 / 12 / 9 % across 100 / 300 / 1,000 records (the growth
    with memory is gone), CounterFact and MQuAKE ≤ 1 %, drift +0.005 / +0.014 / +0.004 nats. Next GPU work: re-profile the
    incremental driver (Codex R1-68b) with v5 — the number your Q7 decision needs.

38. (2026-09-16, 00:10 EDT) **Q7 numbers.** The v5 reader through the driver: 1,262 s per 300-edit cell; Codex's incremental
    integrity profile is byte-identical in results and only 16 s faster, so the overhead is not the hashing — it is the
    clone/restore around every phase (≈ 545 s) plus the drift assay's one-prefix-at-a-time decoding (506 s). A 1,000-edit
    cell is still ≈ 48 min → ≈ 290 h for 360 cells; both overheads are removable (lane R1-68c) and could bring a cell
    to ≈ 20 min (≈ 120 h), but that is unmeasured. Your Q6/Q7 answers by September 20 still decide the plan; I will
    re-measure as soon as R1-68c lands.

39. (2026-09-16, 06:56 EDT) Q6 and Q7 recorded (DEC-051, DEC-052). Open: Q4 (κ pilot) and Q5 (stress panel).

40. (2026-09-16, 06:58 EDT) Started with Q6/Q7 approved: the v5 CounterFact development cell is running through the driver
    (per-dataset cost for the schedule memo) plus the last unseen points. Two gaps surfaced that I have turned into Codex
    lanes: comparator-condition recipes cannot be hand-made (identity-bound) — R1-64b builds them; and MQuAKE has no
    v0-style bank calibration (radii exist only for zsRE/CounterFact), so the v0 live/stable/matched-update MQuAKE cells
    need a calibration run first — R1-73 specifies it, I run it. Neither needs a decision from you.

41. (2026-09-16, 07:30 EDT) v5 CounterFact development cell done through the driver: 1,234 s, i.e. the same cost as zsRE
    (per-dataset cost is flat; one number per cell for the schedule memo). Results as expected (ES 300/300, RET-GS 0.75,
    unseen 0 %, drift +0.006). One thing needs you: the driver scores locality with termination-qualified equality,
    which on CounterFact turns 13 of 50 byte-identical-but-truncated locality pairs and 37 of 100 near-miss pairs into
    failures (LS 36/50 vs 49/50 under the text-equality rule every earlier LS used). Protocol v4 left this as your
    binding — **Q9** in the ledger, my recommendation stated. Also: the MQuAKE unseen points beyond 100 records are not
    runnable (no reader-unseen MQuAKE filler exists); recorded as a limitation.

42. (2026-09-16, 07:45 EDT) Q9 recorded as DEC-053. Open now: only Q4 (κ pilot) and Q5 (stress panel), both by September 20. The driver keeps scoring both ways from its stored rows; Codex gets an edit request to report both counts in `stage4_assays.py`.

43. (2026-09-16, 08:05 EDT) Codex's round 16 committed (`2e7ac38`, all eight lanes) and round 17 posted: R1-74 (DEC-053
    scoring in the driver), R1-75 (stage-4 analysis tree over cell directories, with DEC-052 block/incomplete reporting),
    R1-40c (matrix v5 for freeze gate U17), R1-49e (protocol v5 with DEC-050–053), R1-76 (common-population unseen runner
    and the MQuAKE occupancy memo). Two of Codex's findings you should know: (a) the small mean drift hides local harm —
    v5 zsRE max 8.7 nats with 17 positions above 0.1 nats (CounterFact 7.3 / 52); this is the tail the talk is about and
    it goes into the claim ledger as measured; (b) the zsRE unseen "flat at 10 / 12 / 9 %" used different outside prompt
    sets at each size, so flatness is not established — R1-76 fixes the population. Also withdrawn from my notes: the
    "shorter prefixes" explanation of the CounterFact drift-assay time. Nothing new needs a decision from you now;
    Q4 and Q5 stand. Q10 (MQuAKE occupancy population) will follow when Codex's memo lands.

44. (2026-09-16, 08:25 EDT) **The time-budget overage has a measured cause and a fix.** Codex's R1-68c instrumented
    driver ran the 300-edit zsRE cell in 837 s (was 1,246 s) with identical results; its timers show 534 s of that is
    the immutable-identity check (re-hashing base weights before every one of 600 phases), 279 s is model work, and the
    drift assay is now 83 s (was 506). Without the per-phase rehash a 1,000-edit cell is ≈ 15–17 min → ≈ 115 h for
    all 405 cells against 306 available; with it, ≈ 45 min → ≈ 330 h. Lane R1-68d (Codex, first) moves the full
    check to checkpoints; I re-profile the moment it lands and re-price on September 20 as DEC-052 says. No scope
    change needed. Presentation record of the drift tail written to `assets/presentation-materials/tail_drift_v5.md`
    with the figure.

45. (2026-09-16, 08:35 EDT) R1-68c full profile: 1,274 s, confirming the split (identity rehash 534 s, scalar drift
    516 s vs 83 s batched). Batched drift agrees with the scalar assay to 1.3e-4 nats at the worst position with
    identical tail counts; I set the real-base admission tolerance at 1e-3 nats per position plus identical exceedance
    counts (protocol v5 will state it). No decision needed. Codex has started round 17 (R1-74 files arriving).

46. (2026-09-16, 10:30 EDT) **Q4 recorded as DEC-054 and the κ pilot launched** (`kappa_pilot_v3.json`): nine new trainings
    (κ 0.2, κ 0.5, clipped-surprisal control; seeds 0–2) with the v5 training command; the ordinary arm is the v5
    family itself. Each arm is evaluated on retention (three streams), unseen false fires (three datasets, 100
    records) and the drift tail on 32 shared windows with per-position rows saved, so the pre-registered tail
    statistics (ES95, maximum) get their seed spread. Measured budget ≈ 6 GPU h (Codex's 3 h did not include
    evaluation); it runs ahead of the comparator profiles because nothing else is waiting on the GPU. Matthew's
    framing request is now a binding on every κ report (decisions file). Also this hour: Codex's round 17 landed in
    full (R1-68d driver fix, R1-74 scoring patch applied, R1-75 analysis tree, R1-40c matrix v5, R1-49e protocol v5,
    R1-76 fixed-outside runner and MQuAKE memo); the R1-68d re-profile runs first in the same chain. Open: Q5 only,
    plus Q10 (MQuAKE occupancy population) once I have read Codex's memo.

47. (2026-09-16, 10:35 EDT) **Q10 posted** (MQuAKE occupancy population; my default A). Codex's arithmetic: 700 historically exposed rows could support a 300-record point after review, never the 1,000-record one; the register's 168-subject headroom cannot close the gap and must not be spent on development. zsRE and CounterFact get the proper common-population occupancy curve from the R1-76 runner (its populations are prepared; it runs after the pilot).

48. (2026-09-16, 10:40 EDT) **The budget problem is solved on the measured number**: the R1-68d driver runs the 300-edit
    zsRE cell in 288 s (was 1,246 s on September 15) with identical results; 98 % of it is now model time. A 1,000-edit
    cell extrapolates to ≈ 14–16 min, ≈ 110 GPU h for all 405 cells against 306 available. Remaining before the
    September 20 re-pricing: profile the comparator conditions (R1-64b recipes, rebound to this tree) and one MQuAKE
    cell after the R1-73 calibration; both run after the κ pilot finishes this afternoon.

49. (2026-09-16, 13:15 EDT) Codex has nothing uncommitted (round 17 and the patch landing are in `79bad7f`); round 18 posted:
    HT-3d (κ pilot aggregation under the v3 rule, with the DEC-054 framing), R1-64c (comparator recipes rebound to the
    new tree), R1-77 (block-ordered confirmatory queue runner), R1-63d (freeze candidate v5), HT-4c (claim ledger v3).
    Pilot so far (6 of 9 trainings, no failures): zsRE unseen false fires at 100 records — ordinary 19 / 6 / 10 % across
    seeds, κ 0.2: 6 / 6 / 3 %, κ 0.5: 6 / 3 %; CounterFact and MQuAKE 0 % everywhere. Retention and tails are
    aggregated when the chain ends (≈ 15:00 EDT).

50. (2026-09-16, 15:05 EDT) Codex's round 18 committed (`0a19fac`); round 19 posted (R1-77b sealed backend, R1-58c draw /
    seal checklist for your acts, R1-49f the remaining protocol bindings as questions Q11–Q13, HT-3e pilot counter-review,
    R1-73b MQuAKE comparator recipes). **κ pilot, partial (27 of 36 rows):** both coupled arms cut the drift tail —
    expected shortfall of the worst 5 % 0.22 → 0.08 (κ 0.2) / 0.06 (κ 0.5) nats, maximum 5.3 → 2.7 / 2.6 nats, zsRE
    unseen false fires 12 % → 5 % / 4 % — but mean RET-GS falls 0.796 → 0.754 / 0.748, past the pre-registered 0.02
    floor, so under the counter-review §4 rule neither arm becomes a declared secondary condition as it stands. The
    clipped-surprisal control (ceiling-matched to κ 0.5) decides whether the tail effect is the coupled form or just the
    ceiling; it finishes within the hour. Framing per DEC-054: preliminary hints, development streams, three seeds.

51. (2026-09-16, 15:00 EDT) Q5 and Q10 recorded (DEC-055 go, DEC-056 option B). No lead decision is open; Q11–Q13 (multiplicity, fidelity inequalities, secondary thresholds) will follow from Codex's R1-49f. Execution order on the GPU: κ pilot (finishing) → comparator profiles + MQuAKE calibration (chain I, tonight) → stress panel (≤ 4 h) → MQuAKE occupancy diagnostic after Codex's review → September 20 re-pricing.

52. (2026-09-16, 15:15 EDT) **κ pilot complete: a null result under the rule you approved.** Both coupled arms cut the drift
    tail (ES95 0.22 → 0.08 / 0.06 nats, max 5.3 → 2.7 / 2.6) and zsRE false fires (12 → 5 / 4 %), but retention falls
    0.04–0.05 (floor 0.02) and the reduction sits inside the ordinary arm's seed spread. The clipped-surprisal control
    gets most of the tail gain with retention inside the floor. So: no κ secondary condition in Stage 4; one honest slide
    ("bounding surprisal shifts the porosity / interference trade-off; it does not beat it on this substrate; preliminary,
    three seeds"). Codex's HT-3e counter-review checks the arithmetic next. Presentation record updated
    (`assets/presentation-materials/kappa_pilot_v5.md`).

53. (2026-09-16, 18:50 EDT) Codex's round 19 committed (`081d3c0`): sealed confirmation backend and queue dispatch (three
    edits you approved directly with Codex, plus two follow-ups; 52 tests pass here), the MQuAKE historical review (657
    usable rows → a 300 + 100 population, spec v3, ready to run), the draw / seal / freeze checklist with dry preflight
    (refuses on the missing owner receipts, as it should), and the U12–U14 proposals — posted as **Q11–Q13** above with
    my recommendation to accept all three as written. **A budget finding from chain I:** the v0-style and continuation
    comparator conditions run through the full profile with the scalar drift assay, and their drift is four times the
    learned reader's — 2,140 s of a ≈ 2,850 s cell — so a 1,000-edit comparator cell is ≈ 2.2 h and the 225 such cells
    ≈ 500 h, which does not fit. The fix is the same one that worked for the primary (batched drift for those adapters,
    lane R1-68e, first for Codex); the fallback, if it is not ready by September 20, is a protocol amendment putting the
    comparator drift assay at the final checkpoint only (÷3). I will bring the number, not the amendment, on the 20th
    unless you say otherwise.

54. (2026-09-16, 19:05 EDT) Q11–Q13 recorded (DEC-057/058/059). No lead decision is open. Codex gets lane R1-49g: write the three bindings into protocol v5 (a v5.1 draft) and the R1-75 contrast / classifier / benchmark modules with tests; then the freeze candidate is rebuilt (R1-63e). Remaining gates to the freeze are all measurements and receipts: September 20 cost admission (needs R1-68e), the MQuAKE calibration (tonight), the comparator and MQuAKE profiles, the stress panel, and your clearance / draw / seal acts once R1-D9's producers exist.

55. (2026-09-17, 03:45 EDT) Chain I done: all 16 comparator profiles and the MQuAKE calibration. Two things you should
    know before September 20. (a) **Cost shape:** the non-learned conditions cost 0.75–1.3 h per 300-edit cell (scalar
    drift 1,800–2,900 s; on CounterFact another ≈ 2,000 s of v0 per-query bank search inside the endpoint decodes).
    Even with Codex's batched drift (R1-68e) the 225 non-learned 1,000-edit cells extrapolate to ≈ 250 h and the 135
    learned ones ≈ 45 h, against 306 usable hours — feasible only with no failures and the 45-cell extension deferred.
    I bring the measured number on the 20th; the options if it does not fit are DEC-052's accepted-incomplete reporting
    in block order, comparator drift at the final checkpoint only (a protocol amendment), or a second GPU. (b) **MQuAKE
    and the v0 cap:** no key radius separates MQuAKE paraphrases from unrelated prompts (coverage 0 at every radius),
    so the v0-style conditions run on MQuAKE with radius 0 — exact-prompt firing only, as the calibration spec's
    declared fallback. I admitted that as calibration v3 (development, declared); it is the honest comparison and
    needs no decision from you unless you object. The stress panel refused to start on a receipt-format detail in my
    approval file; fixing and relaunching now.

56. (2026-09-17, 04:10 EDT) **Stress panel done** (22 min of the 4 h): shuffled and clustered schedules give identical results
    on every dataset (the memory is an order-free set of records), old exact answers stay 20 / 20 everywhere, and the
    harm that does occur is sparse, item-determined and permanent — CounterFact two of 20 probed facts lose 2.5 and 4.0
    nats per token (one token 12.5 nats) after a later edit, MQuAKE one fact 2.0 nats, zsRE nothing; no recovery within
    40 updates because nothing in the design revisits a stored record. Presentation record:
    `assets/presentation-materials/stress_panel_v5.md`. GPU is idle until Codex's R1-68e / R1-73b / R1-76b land;
    next GPU jobs in order: R1-68e re-profiles, MQuAKE comparator profiles, the MQuAKE occupancy diagnostic.

57. (2026-09-17, 06:15 EDT) Codex's round 20 committed (`c1667c3`): batched drift for the v0 / S1 adapters (driver patch you
    approved, applied; 57 tests pass), protocol v5.1 with Q11–Q13 written in and the analysis modules, freeze candidate
    v6. Correction to my cost arithmetic: the driver runs drift once per cell, not at every checkpoint, so the core
    matrix is ≈ 355 h with scalar drift and ≈ 290 h with batched drift (inside 306 h, no margin for the extension or
    failures) — CounterFact's v0 endpoint decodes, not drift, are now the largest term. Chain K re-profiles all twelve
    non-learned zsRE / CounterFact cells with the batched path (also the real-base parity test); numbers by this
    afternoon. Round 21 for Codex: R1-73b (calibration v3 file + MQuAKE comparator recipes), R1-D9, HT-3e, R1-77c
    (sealed backend rebound), HT-4d (claim ledger v4).

58. (2026-09-17, 06:40 EDT) **Starting the long run early.** The GPU is no longer the critical path; the freeze is. The
    sequence to launch is: cost admission → your clearance → your draw → your seal → freeze candidate v7 → frozen
    manifest (your act) → queue launch in DEC-051 block order. What is missing is the code for the three receipts
    (R1-58c's preflight refuses on exactly those). I have re-prioritised Codex's round 21 to build them first as three
    separate pieces (R1-D9a clearance, R1-D9b draw, R1-D9c seal), then the sealed backend rebinding with an end-to-end
    TinyBase rehearsal (R1-77c), then the MQuAKE recipes. On my side: the cost admission moves from September 20 to
    **today**, from chain K's batched-drift numbers (DEC-052 set the 20th as a deadline, not a date), and I write the
    execution plan with per-block ceilings tonight. **Target: your acts on September 18–19 and block 1 launched by
    September 19**, two days ahead of the plan, which at ≈ 290 h of work over the ≈ 480 wall-clock hours to October 9
    leaves ≈ 40 % of the time as buffer for crashes and reruns. What you will have to do, when the producers land: run
    the four checklist commands in `docs/tasks/R1-58c-draw-seal-plan-v2.md` (clearance, draw with a master seed you
    choose, seal, freeze) — each has a dry-run that shows what it would write first. Crash protection in place: one
    job at a time, the host-memory guard in every runner, the system and process-memory monitors, checkpoint resume in
    the queue, and results committed at every block boundary.

59. (2026-09-17, 08:45 EDT) Codex's round 21 committed (`2a8b237`): the three receipt producers, the sealed backend
    rebound, calibration v3 and the MQuAKE comparator recipes; 83 tests pass here. Batched drift on the real base:
    zsRE non-learned cells now 711–847 s (were 2,650–3,650), CounterFact v0_stable 2,254 s (was 4,027), parity exact.
    **What still stands between us and your acts** is review evidence, not code: alias / context / exposure review of
    every register-v6 candidate, the teacher-token review on the final base (a GPU pass I run), endpoint construction
    and the MQuAKE composition catalog, and the populated inputs file. Round 22 for Codex is exactly those (R1-D10a/b/c,
    R1-58d); the teacher pass runs on my GPU after the MQuAKE comparator profiles tonight. Realistic: evidence complete
    September 18, your dry-runs and signatures September 19, launch September 19–20. Nothing needs a decision from
    you now; I will hand you a one-page operator sheet with the exact commands when the inputs are populated.

60. (2026-09-17, 10:30 EDT) Codex's round 22 committed (`1094412`): the review evidence, the teacher-review script, the
    endpoint constructor with the composition catalog, the populated inputs and your unsigned authorization forms with
    an operator sheet, claim ledger v4, and the independent pilot / stress review (its wording corrections applied to
    the notes and the presentation record). **One decision, Q14, needed by tomorrow:** MQuAKE clears 2,129 subjects
    against 4,050 demanded; the register arithmetic cannot be made to reach 4,050 legitimately. My recommendation is
    option A (MQuAKE at 300 edits × 3 realizations, checkpoints 100 / 300, its 1,000-record claims reported as
    unavailable), with the context-match review run in parallel to widen the margin. zsRE and CounterFact are not
    affected: their teacher pass and draw can proceed, and DEC-051's block order already runs each dataset's block
    separately, so the launch date does not depend on Q14 unless you choose C.

61. (2026-09-17, 10:50 EDT) Q14 recorded as DEC-060 (option D). No lead decision is open. When Codex's adjudication worksheet lands I review the rule and the restored subjects, apply option A's cadence with that margin (or bring back a larger cadence as a question if the numbers allow), and Codex then emits matrix / protocol v5.2 and freeze candidate v7.

62. (2026-09-17, 11:25 EDT) **Chain K done; the cost admission is in draft** (`docs/R1_execution_plan_v1.md`). Batched drift
    is admitted for all six non-learned families (every position within 3e-4 nats of the scalar path; the S1 cells
    differ only at 1–2 positions sitting exactly on the 0.01 threshold). Per 1,000-edit cell: learned 0.35 h, zsRE
    non-learned ≈ 0.5 h, CounterFact non-learned ≈ 1.2 h; MQuAKE measured tonight. Core matrix ≈ 235 h in block order,
    extension ≈ 16 h, against ≈ 360–375 usable hours from a September 19–20 launch: ≈ 45 % margin before the extension.
    The MQuAKE occupancy diagnostic needs one small Codex recipe (R1-73c) and runs after it.

63. (2026-09-17, 12:40 EDT) Codex's round 23 committed (`5bd1519`). Under your DEC-060 (option D): I reviewed and adopted
    Codex's adjudication rule — only mentions inside ordinary training text or drift windows without a subject
    annotation are waived; every task-specific exposure stays excluded (`docs/tasks/R1-D10e-orchestrator-review.json`).
    It restores 32 MQuAKE subjects (margin 211 over the 1,950 demanded), 46 CounterFact, 9 zsRE; it cannot support a
    larger MQuAKE cadence, so 300 × 3 stands and no new question is needed. The near-miss family is feasible on all
    three datasets (1,056 MQuAKE pairs for 300 needed). One newly exposed dependency: the draw / seal producers, the
    validator and the sealed backend assume uniform 1,000-edit layouts and need parameterising for
    4,050 / 4,050 / 1,950 — Codex's round 24, with the installed-source patch applied by me tonight at the idle
    boundary. MQuAKE comparator profiles: learned 335–388 s, v0-style 957–1,125 s per 300-edit cell (batched drift).
    Launch target unchanged: your acts September 19, block 1 by the 20th.

64. (2026-09-17, 13:35 EDT) MQuAKE comparator profiles done: cheaper than planned (0.1 h learned, 0.3 h non-learned per
    300-edit cell). Two artifacts found and handed to Codex: the MQuAKE development payload used edit prompts as
    locality prompts (LS 0 / 50 everywhere — a payload bug, not a result; fix and re-run ≈ 2 h), and the teacher
    review refused because its evidence bound a script Codex later changed (rebinding is part of the evidence
    promotion already in round 24). Neither moves the launch date.

65. (2026-09-17, 13:40 EDT) **Concurrency admitted: two cells at a time.** Probe 2 (two non-learned cells) gave 1.67×
    throughput with identical results and 20 GB of host memory free, matching probe 1. The core matrix drops from
    ≈ 235 solo hours to ≈ 140 wall-clock hours, ≈ 150 with the extension, against ≈ 360–375 usable hours from a
    September 19–20 launch — a 2.4× buffer for crashes and reruns. Codex adds a two-worker mode to the queue (R1-77e).

66. (2026-09-17, 15:20 EDT) Codex's round 24 committed (`1828aa2`), the R1-77d patch applied at the idle boundary (the
    installed tree now accepts the bound per-dataset cadence; 300-edit MQuAKE cells run under the sealed backend), the
    MQuAKE recipes rebuilt on the new identity, and chain P started: the teacher-token review on the final base over
    14,419 candidates (operative evidence v5), then the MQuAKE comparator re-run with corrected locality. **One
    decision, Q15 (near-miss family semantics), by tomorrow** — a scientific definition the protocol needs before the
    draw; my default is to adopt Codex's proposal. Everything else on the path to your acts is now running or
    assigned (freeze candidate v8, teacher certification, an independent counter-review of the whole package).

67. (2026-09-17, 15:40 EDT) Teacher review done in three minutes: post-teacher subjects 6,084 zsRE / 6,121 CounterFact /
    2,161 MQuAKE against demands 4,050 / 4,050 / 1,950 (margins +2,034 / +2,071 / +211). The clearance
    evidence is complete except the role merge (Codex, CPU) and your signatures. R1-77d's tests pass (48). Waiting on
    Codex for the recipe rebinding (MQuAKE re-run) and freeze candidate v8; on you for Q15. (An earlier version of
    this line, written 15:30, showed zeros from a misread receipt; corrected.)

68. (2026-09-17, 15:55 EDT) Q15 recorded (DEC-061). Codex's round 25 committed: recipes rebound after the patch (the MQuAKE
    re-run starts now), teacher certification and the real clearance dry-run — **6,084 / 6,121 / 2,161 subjects
    against 4,050 / 4,050 / 1,950, all 93 Hall checks pass, the only refusal left is your unsigned authorization** —
    freeze candidate v8, an independent review (X15: eight findings, all factual / policy, none scientific: ceiling
    padding would be applied twice between plan and queue; the queue stops on failure rather than retry-and-skip;
    the concurrency slowdown reaches 1.13×, not 1.10; the zsRE empty-answer baseline needs its caveat) and claim
    ledger v5. Round 26 fixes the X15 items and folds Q15 into the constructor and protocol; then freeze candidate
    v9, the re-signed forms and your operator sheet v4. No lead decision is open.

69. (2026-09-17, 18:00 EDT) **Cost admission done** (`docs/R1_execution_plan_v2.md`, ceilings in
    `manifests/revision_v1/cell_ceilings_v1.json`): core 360 cells ≈ 209 solo hours → ≈ 127 wall-clock hours with two
    workers, extension +12 h; against ≈ 360–375 usable hours that is a ≈ 2.7× buffer. The corrected MQuAKE cells are
    clean (locality 50 / 50 for the v0 conditions). Orchestrator-side gates are closed; what remains is Codex's round
    26 (queue policy, near-miss family, final protocol text, candidate v9, your operator sheet v4) and your acts.

70. (2026-09-17, 18:30 EDT) **The signature package is ready except two items.** Codex's round 26 is committed and freeze
    candidate v9 is final (728 bindings; 8 / 8 corrected MQuAKE profiles; plan v2 bound; all open gates are
    signatures or population operations). What I need from you, in one sitting when the operator sheet v5 lands
    (tomorrow morning): (1) **Q16** above — my recommendation B; (2) the signatures: protocol admission (final text
    `docs/R1_stage4_protocol_v5_2_D_final.md`), the cost admission receipt (`docs/tasks/R1-cost-admission-receipt-v1.json`,
    plan v2 and ceilings hash-bound), clearance, RNG admission with your master seed, then draw, seal and freeze in
    order — each step's dry-run prints the exact request digest you sign. Codex's round 27 builds the Q16-B allocation
    (activated on your answer), the operator sheet v5 with every command as one script you run step by step, and a
    final independent review of the package.

71. (2026-09-17, 18:45 EDT) Q16 recorded (DEC-062, option B). No lead decision is open. Codex's R1-D9f ships with `family_coordinated` as the bound mode for your RNG admission form; the operator script (R1-58g) follows. Your sitting is tomorrow morning.

72. (2026-09-17, 20:00 EDT) Codex's round 27 committed (`3fbd0d7`). Its independent review (X16) says the package is **not
    ready for your signatures yet**, for repairable reasons: the final protocol text still forbids the coordinated
    allocation you chose (an amendment is needed), the statistical definitions it incorporates from v5.1 are not
    hash-bound, my cost receipt lacks the typed evidence (measured GPU memory ceilings, zsRE / MQuAKE challenge-endpoint
    costs, a process-hour budget), the production recipe bundle has no producer yet, and six profiles' "0 false
    fires" were unavailable telemetry (notes corrected). Your clarification to Codex ("allow multiple disjoint pairs
    per family") is recorded in DEC-062. Round 28 repairs all of it; I run four full-endpoint development cells
    tonight for the missing cost evidence. Realistic: candidate v12 and your sitting **September 18 afternoon**, launch
    September 19. No decision is open.

73. (2026-09-17, 20:40 EDT) Codex's round 28 committed (`124f6bb`): the protocol amendment with the normative closure,
    candidate v12 (1,408 bindings), the typed cost receipt producer, four full-endpoint development recipes (running
    now on the GPU with host memory captured), and X17's re-review: still not ready, now for evidence rather than text —
    measured host peaks per condition, zsRE / MQuAKE challenge-endpoint costs (tonight's runs), and one missing
    producer (the assembler that turns a sealed draw into the production recipe bundle and the frozen manifest).
    Round 29 is exactly those three plus a re-review. Your sitting moves to when candidate v13 exists — September 18
    evening at the earliest, more likely the 19th morning; launch the 19th. No decision is open.

74. (2026-09-17, 21:40 EDT) The four full-endpoint cells are done: challenge sets cost 115–315 s per cell, all inside the
    admitted ceilings (tightest: MQuAKE v0_stable at 83 % of its ceiling); host peak ≈ 2.7 GB per cell, ≈ 5.5 GB for
    two workers against 19 GB free. First MQuAKE full profile of the primary: RET-GS 0.73, near-miss 100 / 100,
    revision 50 / 50. Codex's round 29 turns these into cost receipt v3 and candidate v13. GPU idle.

75. (2026-09-18, 05:05 EDT) Codex's round 29 committed (`6840243`): the final recipe / freeze assembler exists and passed a
    360-cell synthetic rehearsal; host peaks are inventoried for all 27 condition × dataset pairs; cost receipt v3 and
    candidate v13 are built. X18 found **one genuinely missing experiment**: plan 9 requires the drift / fidelity
    endpoint on the full validation split (245,237 predictions), and every development cell so far used the frozen
    128-window sample (16,256). I have bound the policy as DEC-063 (full split at each cell's final checkpoint,
    complete windows only, both references; the sample stays for intermediate checkpoints) — you may override. The
    cost is ≈ 20 min per cell by extrapolation (+≈ 125 solo hours for the core → ≈ 205 wall-clock hours with two
    workers, buffer ≈ 1.7×), to be measured today: Codex adds the phase to the driver, I run four cells. Your sitting
    therefore moves to **September 19**, launch the same day or the 20th. No decision is open unless you want to
    override DEC-063.

76. (2026-09-18, 07:00 EDT) Codex's round 31 committed (`73ff6b0`): the production pipeline now carries the full-validation
    endpoint end to end; protocol v5.2-D.2 is the text with DEC-063 in it. **A scientific finding you should see before
    the sitting:** the first full-validation cell (primary v5, MQuAKE, 300 records, all 245,237 positions) gives a mean
    KL of 0.0055 nats between the original base and the edited model — above the registered fidelity limit of 0.001 —
    while the mean NLL increase is 0.0056, inside its 0.01 limit; tail: ES95 0.11, max 8.2 nats. Measurement integrity
    passes. If the KL limit applies to the cap (not only to the continuation bases it was first used for), the primary
    condition would fail fidelity in confirmatory cells, which the classifier reports as such. Codex is tracing the
    limit's provenance now (R1-49l); if the current protocol extended it beyond what was registered, you get a Q17
    with two options; otherwise it stands as registered and the result is what it is. Full-validation cost: 1,299 s
    per cell (≈ 22 min), as extrapolated. Three cells to go; your sitting stays on September 19.

77. (2026-09-18, 07:25 EDT) Your question on the fidelity distribution, answered from the stored vectors of the first
    full-validation cell: 99.6 % of positions untouched, 171 positions (0.07 %) carry half the KL, 83.5 % of windows
    pass the limit on their own, 467 positions have KL > 1 nat. The loss is concentrated where the reader fires on
    ordinary text. The per-position vectors are recorded for every cell already; the concentration summary becomes a
    registered descriptive statistic in the reports and protocol (Codex lane HT-7). Presentation record:
    `assets/presentation-materials/fidelity_concentration_v5.md`.

78. (2026-09-18, 07:45 EDT) **Repository size policy in place**, per your request after the push warnings. The four
    65–77 MB files were Codex's synthetic assembler-rehearsal fixtures that my `git add -A` commits of its rounds swept
    in — my commits, my responsibility. Now: a pre-commit hook refuses any file above 45 MB (tested: a 50 MB dummy is
    rejected); the rehearsal, operator-test, certification and pytest fixture trees are ignored and untracked (they
    remain on disk; the freeze candidate binds none of them); a genuine large JSON artifact is split into ≤ 40 MB parts
    with an index and a reassembly command. The already-pushed large blobs stay in history (rewriting it would break
    the shared clones); they are under GitHub's hard limit and only warned.

79. (2026-09-18, 08:15 EDT) Both repositories are now committed together on request. The assets repo needed a tracking
    rule first: it holds ≈ 100 GB of model weights, environments, caches, raw data and multi-GB run outputs that cannot
    live in git, so those are ignored there; the hash-bound evidence, receipts, populations, payload manifests and
    presentation materials are tracked (2,290 files; the five evidence files above 45 MB are committed as split parts
    with their originals kept on disk so the freeze bindings still resolve). Same 45 MB hook in both repos. If you want
    the weights tracked too, that is a Git LFS decision rather than plain git.

80. (2026-09-18, 07:10 EDT) Codex's round 32 committed. **Q17 needs you today** (ledger above): the fidelity limit that the
    primary "fails" on the full validation split was registered for certifying continuation bases, not for the cap;
    the current protocol text extended it and would void the primary's comparisons on any failing cell. My
    recommendation is option 1: report cap fidelity as a declared secondary benchmark (KL and NLL, pass / fail, with the
    concentration statistics), keep the continued-base gate as registered, change no threshold. Codex prepares protocol
    v5.2-D.3 for whichever option you choose. Chain S is on its second cell (three to go); the sitting stays on
    September 19.

81. (2026-09-18, 07:20 EDT) Q17 recorded (DEC-064, option 1). No lead decision is open. Codex binds it into protocol v5.2-D.3 and the analysis; candidate v14 and your sitting stay on September 19.

82. (2026-09-18, 07:35 EDT) **Fidelity watch added** as you asked (DEC-064a): every completed cell whose cap fidelity would
    have failed the old bounds (KL > 0.001 or NLL Δ > 0.01) is logged in `docs/fidelity_watch.md` with its numbers and
    the running maximum per condition × dataset; I report new entries to you at every block boundary and a creep
    alert immediately (a value above the previous maximum for that condition × dataset, or above twice the
    development reference). First entry: the chain S primary MQuAKE cell, KL 0.0055. Codex implements the automatic
    hook into the queue (HT-8); until then I run it by hand after each chain.

83. (2026-09-18, 07:55 EDT) Codex's round 33 committed in both repos: protocol v5.2-D.3 implements your Q17 answer (cap
    fidelity labelled, never a veto; continued-base gate unchanged), the concentration statistics are in the reports.
    Fidelity watch: the second full-validation cell (MQuAKE v0_stable) shows zero change — a radius-0 cap never fires on
    ordinary text — so no entry. Full-validation cost measured for the v0 class too: ≈ 1,470 s per cell. Round 34:
    the watch hook, candidate v14 on D.3 after I install the last backend patch (≈ 09:30), cost receipt v4, the final
    fidelity report, a re-review, the ledger. Sitting: September 19.

84. (2026-09-18, 08:20 EDT) **Fidelity watch — breach notice (not a creep alert).** The third full-validation cell, the
    primary reader on zsRE at 300 records, measures mean KL 0.0023 (above the 0.001 benchmark) and mean NLL increase
    0.0023 (below 0.01); 64 positions carry half the KL; max 9.9 nats. It becomes the development reference for
    zsRE · primary. Watch state: three cells observed, two breaches (MQuAKE 0.0055, zsRE 0.0023), zero creep alerts.
    Codex's round 34 committed in both repos: the watch is now automatic — it runs after every certified cell in the
    queue and in the fidelity report, with durable records and alerts I relay to you. Last chain S cell (zsRE
    v0_stable) finishes ≈ 09:00; then the two pending patches (backend cadence, successor package), the identity
    rebind, cost receipt v4 and candidate v14.

85. (2026-09-18, 08:55 EDT) Chain S complete and filed. Full-validation costs: ≈ 1,300 s per learned cell, ≈ 1,400–1,470 s
    per v0-style cell (≈ 0.4 h), host peak ≤ 2.8 GB. Fidelity watch: four cells audited, two breaches (both learned
    cells: MQuAKE 0.0055, zsRE 0.0023), zero creep alerts; the zsRE v0_stable cell measures 0.0008 (pass). Final
    fidelity report built; figure and two-sentence result in the presentation materials. The two pending patches are
    installed; Codex has two small blockers before candidate v14 (a builder pin, one assembler test).

86. (2026-09-18, 09:05 EDT) Codex's round 35 committed in both repos: the launch-day runbook with the block-boundary report
    I will post to you after each block, and the complete four-donor cost basis. **Schedule with full validation:**
    Codex's scenario is ≈ 484 process-hours for the 405 cells (≈ 726 with the 1.5× per-cell safety margin, against the
    750 process-hour cap), i.e. ≈ 245–260 wall-clock hours with two workers against ≈ 360–375 usable from a
    September 19–20 launch — the buffer is now ≈ 1.4–1.5×, down from 2.7× before DEC-063 added the full split. I
    recorded the cost transfers the receipt needs (DEC-065; you may override) and the first confirmatory block's
    measured costs replace them. Round 36 finishes receipt v4 and candidate v14; X19 then reviews. Your sitting:
    September 19, provided X19 says ready.

87. (2026-09-18, 09:40 EDT) **Q18 — MQuAKE scope, my analysis of Codex's assessment.** Agree: MQuAKE has paid for itself
    (the paraphrase generalization result, the fidelity-tail result, the v0 limit); no further multi-hop investment;
    composition stays descriptive; the extension is the first deferral. Further: 75 of MQuAKE's 120 core cells run
    conditions whose outcome calibration v3 fixed in advance (radius 0 → retention 0, fidelity ≈ 0), and MQuAKE adds no
    primary intervals anyway. Option B keeps everything MQuAKE contributes (the learned reader on a third edit family
    across three fresh realizations, one baseline) in 45 cells and returns ≈ 31 wall-clock hours to the buffer. It
    must be decided now to be prospective; the draw is unaffected either way.

88. (2026-09-18, 09:50 EDT) Q18 recorded (DEC-066). No lead decision is open. The core matrix is now 285 cells (+ 45 extension); the buffer rises to ≈ 1.65×. Codex folds it into matrix / protocol D.4 with candidate v14.

89. (2026-09-18, 10:05 EDT) Codex's round 36 committed in both repos: the typed cost receipt v4 (expected ≈ 431
    process-hours, ≈ 647 if every cell hit its ceiling, against the 750 cap), plan v3, matrix and protocol D.4 with your
    MQuAKE decision, candidate v14, forms v9 and operator sheet v8; X19 finds the engineered package ready — what
    remains is your signatures and one scientific interpretation (U03: the S1 continuation bases' historical training
    budget is not an exact match to v5's training compute; Codex writes the one-page memo you read at protocol-admit).
    **Your sitting tomorrow, in order** (operator sheet v8, one command each, dry-run first, then sign the printed
    digest): protocol-admit, cost-admit, clearance, rng-admit (your master seed), draw, endpoints (mine), seal,
    freeze, launch (mine). I am running the dry-runs now so the digests are known and no step surprises us.

90. (2026-09-18, 10:30 EDT) Codex's round 37 committed in both repos. For your signing session
    (`docs/tasks/R1-D9-operator-sheet-v8.md`): the U03 memo you read at protocol-admit is `docs/R1_U03_interpretation_memo.md`
    (one page; proposed protocol sentence included). For the talk: `assets/presentation-materials/talk_outline_v1.md`
    (12 slides, each with its claim, evidence file, figure and qualification) and six figure sets under
    `assets/presentation-materials/figures/ht9-v1/`. Round 38: the producer for the freeze assembly inputs (between
    steps 7 and 8), the daily / block-boundary operations tooling, the post-session verification, the ledger, and a
    first slide deck. No decision is open; the session can start whenever you like.

91. (2026-09-18, 11:20 EDT) Step 1 (protocol-admit) is signed and complete — receipt de7703b3… in the session journal; the
    extension is admitted. Codex's round 38 committed in both repos: the producer I run between your steps 7 and 8, the
    daily / block-boundary operations tooling with a crash checklist, and a first 12-slide deck
    (`assets/presentation-materials/deck_v1/current-research-deck.pdf`, speaker notes carry every qualification).
    Round 39: the confirmatory report skeleton that block 1 fills, a claim-by-claim deck review, then the post-session
    verification and the ledger. Next for you: step 2, cost-admit, same preview → review → sign → execute cycle
    (`docs/tasks/R1-D9-operator-sheet-v8.md`).

92. (2026-09-18, 12:05 EDT) Codex's round 39 committed: the confirmatory report skeleton (block 1's analysis output drops
    into it), a claim-by-claim deck review — four small wording fixes applied (zsRE label on the 10/100 slide; complete
    windows vs the 128-window prefix; "Clip2 meets the retention floor" rather than "keeps retention"; the 20/20 old
    answers qualified per dataset and checkpoint) and six ledger rows proposed — and an independent check that your
    step 1 signature matches its dry-run digest. Round 40: ledger v6 content, deck v2, a skeleton-vs-protocol check;
    the verification lanes wait for your steps 2 and 8. Session status: step 1 of 9 complete.

93. (2026-09-18, 15:05 EDT) Codex's round 40 committed in both repos: the ledger v6 content (only your step-2 cost signature
    missing), deck v2 (`assets/presentation-materials/deck_v2/`), and an audit of the confirmatory report skeleton against
    protocol D.4 that found four coverage gaps (tail fields, the joint cap-fidelity flag, the secondary historical
    package comparison, the DEC-052 execution accounting) — round 41 closes them in the formatter. Session status:
    step 1 signed; step 2 reviewed preview written at 14:57 (`02-cost-reviewed.json`); its execute is the next command
    (`docs/tasks/R1-D9-operator-sheet-v8.md`, "Full commands for every lead step", step 2c).

94. (2026-09-18, 15:25 EDT) **Session: step 2 is complete** (your retry at 19:00 UTC succeeded; the traceback you saw was
    the attempt a minute earlier). **Step 3 (clearance) is blocked by a stale binding, not by anything you did:** the
    clearance evidence lists the endpoint-constructor script among its provenance bindings at its round-26 bytes, and
    Codex changed that script in round 31 (full-validation contract). The dry run does not check those bindings; the
    execute does, hence the refusal after a clean preview. The clearance rows are untouched. Fix: Codex re-binds the
    evidence (v6), inputs v10, candidate v15 — lane R1-D10i, urgent — and states whether your two signatures carry over
    (the receipts bind per-step derived inputs, not the inputs file itself, so they likely do). **Please pause the
    session at step 3**; I will post the exact command when the re-bound inputs exist. The prevention: the dry run
    will be made to run the same binding check as the execute (Codex, same lane).

95. (2026-09-18, 15:45 EDT) **Delegation recorded (DEC-067) and applied.** The stale binding could not be fixed inside your
    session (each step's plan comes from the previous step's derived inputs, bound by your cost receipt), so I opened
    a fresh session (`logs/R1/operator_v9`) on inputs v10 (evidence re-bound, provenance refresh only), re-executed
    steps 1 and 2 under the delegation with your original signed forms bound as their basis, and executed step 3
    (clearance) with the exposure attestation. Your v8 session and forms are kept as history. **Step 4 needs your
    master seed** — any integer; reply with it and I run steps 4 through 8 and report the frozen manifest hash.

96. (2026-09-18, 16:20 EDT) With your seed: steps 4 and 5 done — RNG admission and the draw (all 100 near-miss pairs matched
    in every dataset and realization; the seed 378462438976234321867 is recorded in the RNG admission). Step 6
    (endpoints) refused on the same kind of stale hash, and a full scan shows the whole package has drifted: Codex kept
    editing producer scripts after their outputs were bound (role plan, matrix D.4, all 27 runtime templates, cost
    receipts). Patching them one at a time is how today went; instead Codex re-binds the entire live package in one
    versioned pass and then the code tree is declared frozen until launch (lane R1-63o, urgent). I then re-run the
    session end to end on the re-bound inputs — automated, same seed, so the same reservations — and report the frozen
    manifest hash. Expect this evening or tomorrow morning; launch follows the same day.

97. (2026-09-18, 17:05 EDT) Codex's programme review (`docs/scientific_program_review_2026-09-18.md`) — my reading: right on
    both counts, and both should be settled before the re-bind so the package is emitted once. **Q19:** with three
    fresh realizations the registered bootstrap cannot deliver calibrated 95 % intervals (it reduces to the min–max of
    three numbers); the honest claim is replicated effect sizes with their dispersion, and the classifier labels as
    preliminary decision summaries — my default A, with an assumption-labelled t-interval shown beside it. A fourth
    realization (B) buys little (four clusters) and costs the extension. **Q20:** triplet-first ordering — adopt; it
    secures the central paired panel in ≈ 78 elapsed hours instead of ≈ 150, at no scientific cost. Codex's other
    points (defer the unperformed factorial branches explicitly; U03 qualification; effects before labels; keep the
    κ null and the stress limits bounded) are already in the ledger and the protocol or go into D.5 with Q19.

98. (2026-09-18, 17:30 EDT) Q19 recorded (DEC-069) and Q20 (DEC-068). Both go into protocol / matrix D.5 inside Codex's single re-bind (R1-63o), after which the tree is frozen and I run the session end to end on the re-bound inputs with your seed. No lead decision is open.

99. (2026-09-18, 17:20 EDT) **The confirmatory experiment is frozen.** Session v10 completed all eight steps under your
    delegation on the re-bound package: protocol D.5 (your Q17–Q20 answers in), cost admission, clearance, RNG admission
    with your seed, draw (100 / 100 near-miss pairs everywhere), endpoints (50 / 50 locality prompts in every group,
    zero shortfalls), seal, and the freeze — `manifests/revision_v1/frozen_stage4.json`, sha256 `60f2c09461330852…`, with 330
    sealed cell recipes and the final matrix in the DEC-068 order (DEC-071). Codex's X20 now verifies every receipt
    against its digest and the frozen manifest against candidate v15; the content lock is re-verified before launch.
    **Launch (step 9) is yours to call**: say "launch" and I start the queue with two workers and the fidelity watch;
    the first block-boundary report follows after the triplet's first realization (≈ 26 h).

100. (2026-09-18, 17:45 EDT) **Launched** on your "launch now": operator step 9 executed with the signed launch form
    (frozen matrix + queue bindings, receipt root `logs/R1/final_queue`, two workers) under CUDA with the GPU lease held
    for the run's lifetime. The queue dispatches the 330 cells in the DEC-068 order — the primary / random / v0_stable
    triplet across all realizations first — with the fidelity watch after every certified cell. Reporting: a daily
    status line here from the D13 tooling, the block-boundary report after each block (the first after the triplet's
    first realization, ≈ 26 h), fidelity breaches at block boundaries, creep alerts immediately. Codex's X20
    verification runs in parallel; if it finds a defect the queue is stopped at the next cell boundary and we resume
    from the last certified checkpoint after the fix. The tree stays locked.

101. (2026-09-18, 18:50 EDT) **First two confirmatory cells complete** (primary v5, zsRE, realization 0, orders 100 and
    101; 74 and 75 min each under two workers). At 1,000 records: ES 0.977, RET-GS 0.955, LS 50 / 50, unseen false fires
    9 %, near-miss 86 / 100, revision 49 / 50 — in line with development. **Fidelity watch, creep alert (DEC-064a):**
    zsRE · primary at 1,000 records measures mean KL 0.00238 and NLL Δ 0.00245 against the development reference
    0.00227 / 0.00231 from 300 records — a new running maximum by 5 %, consistent with more records, not a jump; no
    admission effect (DEC-064). **Cost watch:** the full-validation phase took 3,100 s per cell with two workers
    against 1,300 s measured solo — the two batched full assays contend for the GPU far more than the short probes
    predicted — so these cells used 90 % of their effective ceiling. Throughput is still ≈ 1.3× solo, but a heavier
    class (S1) could touch its ceiling. I am watching every finish; if a cell is stopped at its ceiling, the retry
    policy applies and I bring you a ceilings amendment or a one-worker switch rather than let cells go incomplete.

102. (2026-09-18, 22:30 EDT) Run status: 8 cells complete in the first 4.9 hours (all primary-reader cells of block 1 so
    far; 4,270–4,480 s each, zsRE at ≈ 90 % of its ceiling, CounterFact at ≈ 32 %), no failures, no ceiling stops,
    launcher healthy, GPU ≈ 70 %. At ≈ 1.6 cells per hour the 330 cells project to ≈ 8.5 days if the heavier classes
    hold their ceilings, i.e. completion around September 27 with the October 9 stop as the buffer. First
    block-boundary report after the triplet's realization 0 (45 cells, ≈ 28 h in).

103. (2026-09-19, 17:25 EDT) **Block 1 complete — the triplet on realization 0, 45 cells, 23.8 hours, zero failures, zero
    ceiling stops.** Measured cost per cell under two workers (charged seconds): primary zsRE 4,450 / CounterFact 4,270 /
    MQuAKE 2,100; random reader 2,160 / 2,120 / 1,330; v0_stable 4,710 / 9,680 / 2,890. Rate ≈ 1.9 cells per hour →
    the remaining 285 cells project to ≈ 6.5 days (≈ September 26) if the later classes behave like these.
    **The one risk:** two classes finished at 90–96 % of their per-cell ceilings — primary zsRE (91 %) and v0_stable
    CounterFact (95–96 %, 2.7 h per cell). The cause is measured: the full-validation phase runs 1.6–2.4× slower with
    two workers than solo, and the admitted two-worker factor was 1.15 from probes that had no full-validation phase.
    Blocks 2–3 repeat these classes; a cell that crosses its ceiling is stopped, retried once, then reported incomplete
    (DEC-052). I am not stopping the run for this; Codex prepares the versioned post-freeze amendment (queue bindings
    v2 with a measured two-worker factor of 1.7) to apply at the next resume point, and I will bring it to you as Q21
    before it is applied since it changes an admitted number. **Fidelity watch (block 1):** five new running maxima,
    none an admission matter (DEC-064): primary zsRE 0.00238 (+5 % vs dev), primary MQuAKE 0.0071 (vs 0.0055 dev —
    a fresh realization, same 300 records), v0_stable zsRE now 0.00185 (dev 0.00079: the quiet baseline also crosses
    the old 0.001 line on fresh draws), random reader CounterFact 0.060 (fires everywhere, as designed). Full ledger:
    `docs/fidelity_watch.md`.

104. (2026-09-20, 07:35 EDT) Run: 78 / 330 cells at 38 h (≈ 2.0 per hour), no failures, no ceiling stops; block 2 boundary
    expected ≈ 13:00. Codex's amendment package is ready (bindings v2 with factor 1.7, the drain-and-resume procedure,
    the Q21 text): **Q21 is above, my recommendation A with the resume delegated to me**; answering before ≈ 13:00 lets
    me stop the queue at the block-2 boundary and resume with the new ceilings without losing a cell. X20 verified
    session v10 (see its report). Codex's next lanes: a first partial confirmatory report from block 1 (descriptive,
    for the talk), the claim ledger v6 (the cost receipt is now signed), and an independent audit of block 1's receipt
    chain.


105. (2026-09-20, 07:40 EDT) Fidelity watch, DEC-064a relay (six entries since item 103; none is an admission veto; all
    numbers are full-validation means against both references, which agree to 5 decimals):
    - **Creep, v0_stable / zsRE, realization 1**: two cells above twice the development reference (mean KL 0.00274 and
      0.00210 nats vs the development 0.00158; mean NLL increase 0.00277 and 0.00208 vs 0.00171). The running maximum for
      this group has risen across realizations: 0.00116 (dev) → 0.00185 (r0) → 0.00274 (r1). Still 2–3× the old 0.001
      critical bound, and 99.7 % of positions untouched, but this is the one series to keep watching at r2.
    - New running maxima only (small increments): primary zsRE 0.00238 → 0.00245 KL; nonlearned CounterFact 0.0598 → 0.0893
      KL (the lossy control, expected); nonlearned MQuAKE NLL increase 0.01205 → 0.01209; v0_stable zsRE NLL increase
      0.00155 → 0.00159.

106. (2026-09-20, 11:55 EDT) Q21 answered (A, delegated; DEC-072). Cutover plan, per `docs/tasks/R1-77g-resume.md`: one
    SIGINT to the verified queue parent (pid 2825007) when the 90th start receipt appears (84 started / 82 finished now,
    so ≈ 3 h), the two active cells finish under their old ceilings, then idle reconciliation (D13 checklist, fresh D11
    boundary snapshot), a new signed resume request bound to bindings v2 with stop-after 6 (all remaining blocks), and
    resume on the same receipt root. The original step-9 record will show as interrupted; that is expected and preserved.
    Observations in `logs/R1/operations/Q21_cutover/`.

107. (2026-09-20, 15:30 EDT) Additional work: lead decided allocation A (DEC-073). Final plan `docs/additional_work_plan_final.md`;
    code under `aw/` (oracle + generation wrapper, 11 CPU tests passing). Codex lanes opened in `docs/ongoing.md` §3
    (AW-R0 allocation check and extension matrix, AW-L0/L1 identity audit and tap screen, AW-L3 masks, AW-L
    pre-registration draft); the orchestrator takes the streamed scorer, the AW-B and R pre-registrations, and the
    queue cutover. Run: 87 started / 85 finished; drain watcher armed for the 90th start.

108. (2026-09-20, 17:30 EDT) **Block 2 complete and the Q21 / DEC-072 cutover executed.** The drain watcher sent one
    SIGINT to the queue parent at the 90th start (16:26); the two active cells finished under their old ceilings; the
    parent exited at 17:11 (the original step-9 record now reads `failed: KeyboardInterrupt`, preserved as the intended
    interruption). Reconciliation while idle: 90 / 90 starts have finish receipts, 0 failures, 0 retries; the two cells
    the interrupted parent never processed (v0_stable · MQuAKE · r1 · orders 103, 104) had their watch observations
    repaired through the hash-checking watch tool (read-only verified, then applied; no breach) and keep no
    `decision.json`, disclosed as such. Idle boundary report `logs/R1/operations/Q21_IDLE_REPORT/` (boundary ready,
    no gaps): 93.9 process-hours charged through block 2, expected total 424 h, the unsigned D12 re-pricing proposal
    would put ceilings at 591 h (not applied; kept for reference). Resume request digest `ff55f56d…` signed under the
    delegation (`Q21_REQUEST/reviewed-form.json`), executed 17:16 (`Q21_RESUME/resume-authorization.json`); the first
    new start receipts (cells 91, 92, 17:23) carry bindings v2 (`c6f88c56…`), `ceiling_amendment`,
    `resume_authorization` and an effective / solo ceiling ratio of exactly 1.7; same receipt root, same matrix,
    stop-after 6 (all remaining blocks). Fidelity watch: no new alerts since item 105 (11 total). Watcher armed for the
    block-3 boundary (225 cells, ≈ 3 days).


109. (2026-09-21, 16:55 EDT) Run: 134 / 330 complete, 1 running (the last block-3 cell), 0 failures, 0 ceiling stops;
    the 44 cells finished under bindings v2 used at most 65 % of their 1.7× ceilings. Charged 140 h of 750. The second
    worker has been idle since 16:32 because the scheduler runs blocks as groups (block 4 starts only when block 3 is
    fully finished; the same barrier cost nothing at the earlier boundaries because the last cells finished together);
    it resumes with two workers on block 4 (matched_update / v0_live, 90 cells) in under an hour. Fidelity watch, DEC-064a
    relay (six entries since item 105, none a veto): **v0_stable / zsRE creep continues at realization 2** — four cells
    above twice the development reference (mean KL 0.00162–0.00185 vs 0.00158; NLL increase up to 0.00178 vs 0.00171),
    all *below* the realization-1 running maximum of 0.00274, so the series has not risen further; two small new running
    maxima elsewhere (learned CounterFact 0.00577 → 0.00578 KL; nonlearned MQuAKE 0.01218 → 0.01223). Block-3 boundary
    report follows when the last cell finishes.

110. (2026-09-21, 17:25 EDT) **Block 3 complete: the primary triplet exists on all three realizations and all three
    datasets (135 / 330 cells, 0 failures, 0 retries).** Block-3 report `logs/R1/operator_reports/20260921-block3-try1/`
    (boundary ready, no gaps; 141.0 process-hours known; the v2 ceiling view is in `ceiling-v2.json` beside it). Block
    4 (matched_update, v0_live C1 / C2; 90 cells) started at 17:19 with two workers under the 1.7 ceilings. Fidelity
    watch this block: 30 entries (every learned cell, as in blocks 1–2, plus the v0_stable zsRE cells named in item
    109); no new alerts since item 109; no veto. The registered triplet analysis can now run on complete data: Codex
    lane R1-D14d opened (§3 of `docs/ongoing.md`), read-only, reported with the DEC-069 display.


111. (2026-09-22, 16:15 EDT) Daily: 160 / 330 complete (block 4 at 25 / 90), 0 failures, 0 ceiling stops; block-4 cells
    so far use ≤ 62 % of their ceilings; 184 process-hours charged of 750. Forecast from measured class costs: the 125
    remaining matrix cells need ≈ 92 wall-hours at two workers (v0_live and S1 classes still on plan-v3 estimates),
    plus the 45 extension cells → **release ≈ September 27**, as the additional-work plan assumed. Fidelity watch,
    DEC-064a relay (two entries, no veto): the **matched_update comparator on zsRE** opens its own series above the old
    bound — mean KL 0.00195 then 0.00295 nats (NLL increase 0.00188 / 0.00297), i.e. the plain matched adapter harms
    ordinary text about as much as the learned cap does on zsRE (running maximum 0.00245). Worth a sentence in the
    comparator slide once the class is complete.

112. (2026-09-23, 15:30 EDT) Daily: 185 / 330 complete (block 4 at 50 / 90), 0 failures, 0 ceiling stops; block-4
    classes use ≤ 64 % of their ceilings; 230 process-hours charged of 750; release forecast unchanged (≈ September 27).
    Fidelity watch, DEC-064a relay (six entries, all `v0_live_C1 / zsRE`, no veto): the live v0 comparator's running
    maximum climbed through its first cells to mean KL 0.00356 nats (NLL increase 0.00359) — above the learned cap's
    zsRE maximum (0.00245) and the matched-update comparator's (0.00295). On zsRE every learned or live comparator
    breaches the old 0.001 bound; only the frozen `v0_stable` and `R1_nonlearned` stay near it. This is the comparator
    slide's second sentence. No Codex deliverables since the AW-L draft.

113. (2026-09-24, 09:10 EDT) Daily: 203 / 330 complete (block 4 at 68 / 90), 0 failures, 0 ceiling stops; block-4
    classes use ≤ 65 % of their ceilings; 267 process-hours charged of 750; 127 cells remain (22 of block 4, the 60 S1
    cells of block 5, the 45 extension cells) ≈ 81 wall-hours at two workers → **release ≈ September 27, evening**.
    Fidelity relay (two entries, `v0_live_C2 / zsRE`, no veto): running maximum mean KL 0.00553 nats (NLL increase
    0.00564), now the largest of any condition on zsRE (learned cap 0.00245, matched_update 0.00295, v0_live_C1
    0.00356). **Restart reminder for the lead:** a Claude Code restart is pending an update; the queue, its lease and
    the watcher survived the September 20 exit-and-resume unharmed, so the risk is low at any time, and the zero-risk
    moment is after the queue's final receipt; the orchestrator posts the reminder here and in chat when that
    notification arrives.

114. (2026-09-24, 10:45 EDT) The lead restarted Claude Code for the pending update. Verified afterwards: the queue
    parent, both workers and the GPU lease are intact (206 / 330 finished, 208 started, cells still completing); the
    orchestrator's boundary watcher was the only casualty and has been re-armed. Nothing to reconcile.

114. (2026-09-24, 15:15 EDT) **DEC-074 recorded: halt at 225.** Trigger armed 14:47 (one SIGINT to the scheduler at the
    225th start; ETA 03:00–05:00 Friday). Codex's response to my review accepted the sequencing and corrected me on
    three points, recorded in `additional_work_halt_options.md` §7: block 5 is the S1 *continued-base* control with the
    stable v0 cap, not an edit-fine-tuning baseline (I had it wrong); the window is 258 wall-hours (≈ 219 usable), not
    280; G and I are stretch items. **Question for the lead:** given the correction, and given that the frozen dispatch
    order cannot skip the S1_LM CounterFact cells, does the zsRE caveat stand, and in which form — (a) S1_LM zsRE only
    (15 cells, ≈ 10 h, one drain), (b) positions 1–45 (≈ 36 h), (c) S1_literal zsRE outside the queue (not recommended),
    or (d) none? Recommendation: (a) or (d). Codex's round-43 deliverables (AW-R0 allocation and Option R matrix, AW-L0/L1,
    AW-L3, AW-L pre-registration) are on disk and tracked.

