# Lead queue

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
