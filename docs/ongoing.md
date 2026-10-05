# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-15 15:40 EDT (round 13 committed; round 14 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-15-1540.md`. Rules §1 are
unchanged and restated in `CONTRIBUTING.md`: JAX only, sibling/FabricPC read-only, resources under
`assets/`, **no commits by agents** (the lead commits; the orchestrator commits only when the lead asks),
task records in `docs/tasks/<ID>.md`, claim rows with the status tool or a claim JSON, lease for any GPU
use > 60 s, placeholder modules are the lane's to replace, other existing files need an edit request.
Board: `docs/tasks/STATUS.md`.

**Round 3 is evaluated (08:10 EDT).** V3 confirmed the five repairs; Lane X's P4 reproduction holds and its S7
findings are repaired; B4-S ran the sensitivity control, which did not reproduce the divergence class, so B4 stays
unregistered (DEC-020) while Codex localizes the first cross-framework gradient difference. Codex's round-4 lanes are
in §3 (B4-D in progress; S3-01, V4, P open). The lead has accepted the defaults for D-A/C/D/G/H (DEC-021…024); the
freeze command is posted in `docs/lead_queue.md` and waits only on the B4 deadline (2026-09-12 12:00 EDT). The orchestrator's next GPU use (B4 profile, one confirm-mode smoke job against the real base, the
GPU test subset) comes after Lane B4-S lands and is announced in `docs/lead_queue.md`; short `-m gpu` tests by
either agent need no lease.

**Post-freeze rule for every agent (from the moment `manifests/frozen.json` exists).** The freeze binds the hash of the
whole installed `src/pccap` tree; every confirm-mode job compares the tree at start and refuses on any difference (exit 2,
the queue stops). Therefore: no edits under `src/pccap/` after the freeze — not even in your own lane's files
(`src/pccap/baselines/grace_*.py` included). Put B4-D diagnostics and fixes in new files under `scripts/`, `logs/`,
`results/` or `docs/`, or as a proposed patch under `docs/tasks/`; a fix that must land in `src/pccap` is applied only with
a versioned manifest and `--allow-code-drift` recorded by the orchestrator (plan 4 §2). Tests under `tests/` and everything
outside `src/pccap` are unaffected.

**(17:56 EDT) The hold on `src/pccap/` is lifted: the v3 grammar rerun is finished and no confirm-mode job remains. New
modules go under `src/pccap/revision_v1/` as planned; anything drafted under `revision_v1_staging/` can move in.**

## 1. State (2026-09-14, 17:20 EDT)

- **2026-10-05 06:00** — Capex's colleague long-talk deck committed (30 pages, HTML, notes). Round 64 lanes not yet done → carried as round 65 (FIN-1, FIN-2 on Oct 6, LINT-1, DOC-3 + support-information link).
- **2026-10-04 06:30** — Capex round 63 committed (final PC-reader, Option R, AW-L reports; HT-17 complete; deck refresh; X25/X26/reproduction pass). DEC-083: portfolio closed. Round 64: FIN-1 consolidated report, FIN-2 freeze dry run (Oct 6), LINT-1, DOC-3. Capstan: deck file assembly (DECK-1), report slice review.
- **2026-10-04 01:30** — AW-L5 complete (24 cells; item 162: last-site-only writes keep efficacy but raise harm 3–4×; upper-tap readers lose CounterFact paraphrases). **AW-L6: go.** All planned GPU experiments done; GPU idle. Remaining: CPU reports (PC-16b, R-3, AW-L6), PRES refresh, X25 + reproduction, freeze Oct 9.
- **2026-10-03 15:55** — Option R complete (20 complete / 1 incomplete / 9 deferred; item 161). **R-3: go.** AW-L5 chain launched 15:50 (profiles → dev evals → cost gate → 3 trainings → 18 evaluations; ≈ Oct 4 06:00). AW-L6 after.
- **2026-10-03 08:45** — ePC reader seed 2 done (item 160: paraphrase deficit on CounterFact in all three seeds, on zsRE in two of three; zsRE firings 0–6 vs 13–21; CounterFact mixed). **PC-16b: go.** Option R resumed 08:36 (16 cells, two workers) → AW-L5 after.
- **2026-10-03 06:30** — Capex round 62 committed (POST-1 proposal `docs/post_conference/coupled_collaboration_proposal.md`; PRES-9 outcome note, reviewer folder closed). Round 63: PC-16b (three-seed refresh, go when seed-2 evaluations land ≈ 08:45). Seed 2 at step 282/300.
- **2026-10-02 14:00** — DEC-082: review held; proceed as planned; post-conference collaboration foundation; κ readout closed. Round 62: POST-1 (collaboration proposal), PRES-9 (outcome recorded, folder closed). GPU unchanged.
- **2026-10-02 11:00** — Round 61 committed (DOC-2; PC-16a seed-1 refresh). Reviewer entry point: `assets/presentation-materials/review-data/CURRENT.md` → `UPDATE-2026-10-02.md` first. Next lanes (POST-1, PRES-9) after the review.
- **2026-10-02 09:55** — Round 61: DOC-2 (add `UPDATE-2026-10-02.md` to the reviewer entry point before this afternoon's meeting), then PC-16a seed-1 refresh. POST-1/PRES-9 after the review.
- **2026-10-02 09:50** — Capex round 60 committed (REP-1 guide + refresh-all runner). ePC seed 1 evaluated (item 155: the seed-0 'quiet reader' was largely a seed effect; consistent small RET-GS deficit). **PC-16a trigger: go** (both seed-1 evaluations complete). Seed 2 training since 08:13 (≈ Oct 3 09:30 with evaluations) → Option R → AW-L5. POST-1/PRES-9 after the review.
- **2026-10-02 07:30** — Capex round 59 committed (X26 clean; DOC-1 + `review-data/CURRENT.md`). ePC seed 1 trained (24.1 h); evaluations running (≈ 08:15), then seed 2 (≈ Oct 3 09:30), Option R, AW-L5. Round 60: PC-16a (conditional refresh), REP-1 (reproduction document + refresh-all); POST-1/PRES-9 after today's review.
- **2026-10-01 15:20** — Capex round 58 committed (X25 PASS 25 groups + freeze checklist `docs/freeze_checklist_20261009.md`; S4-LIM caveats in the three Stage-4 reports; PRES-8 Q&A, numbers-to-say, rehearsal pack; KP-1 no-go for an exact κ-pilot continuation; CAL-1 checks pass + `coupled_objective_note.md`). Round 59: X26, DOC-1; POST-1 after the Oct 2 review. Optional κ readout: default no (see item 153).
- **2026-10-01 15:05** — Capex round 57 committed (PRES-7 deck with B–D and HT-17; PC-16/R-3/AW-L6 report generators, partial reports). Round 58 lanes: X25 audit + freeze checklist, S4-LIM model-scale caveat, PRES-8 rehearsal/Q&A, KP-1 κ-pilot restoration check, CAL-1 optional. Corrections noted: AW-B severity falls to about one-third (not half); ePC reader training is ≈ 100× BP measured (37× was a projection).
- **2026-10-01 14:40** — HT-17 complete and committed (finite-range tail differences, not classes; AW-B halves conditional severity; GPD adds nothing over exponential for the learned reader; stable v0 zsRE shape 0.43–1.03 beats exponential on held-out windows). Slice check passes. Round 57 lanes: PRES-7, PC-16, R-3, AW-L6.
- **2026-10-01 14:05** — Lane HT-17 opened for Capex (round 56; `docs/tasks/HT-17.md`): saved-vector tail analysis per Capex's specification, CPU only, fits by Oct 5. GPU queue unchanged.
- **2026-10-01 13:40** — DEC-081a: B–D wording revised to Capex's conservative language after its review of the entropy feedback (fitted shapes, not classes; mixture = proven ceiling; κ pilot = bounded loss deformation); HT-17 narrowed to Capex's saved-vector tail analysis spec, opens on the lead's word. Capex review files committed.
- **2026-10-01 12:10** — DEC-081: reviewer feedback (Nelson 2026) items B–D drafted (`docs/friday-10.02-review/talk-text-B-C-D.md`, abstract-to-testbed map, tails_v1 §class prototype); A = lane HT-17 (class fits, CPU) pending the lead's go and Capex's availability; E deferred post-conference. Capex processing the same inputs (not to be interrupted).
- **2026-10-01 10:35** — DEC-080: Option R resumes with the v0 class deferred (16 runnable cells, 9 deferred) as soon as the ePC seeds 1–2 chain releases the GPU (≈ Oct 3 10:30; watcher armed); AW-L5 after it. Capex round 55 committed (R-2, AW-B report, matched-control report, PRES-6). Friday review primer at `docs/friday-10.02-review/README.md`.
- **2026-10-01 07:20** — PC-trained reader: BP arm complete (item 145); ePC seed 0 complete (item 146: own-prompt retention equal to BP, RET-GS 0.03/0.24 lower on zsRE/CounterFact, zero ordinary-text firings on zsRE); ePC seeds 1–2 chained (≈ Oct 3 10:30), then AW-L5 2×2. Option R waits for R-2. Capex idle since Sep 29.
- **2026-09-29 06:50** — DEC-077: no external review; all remaining work proceeds on defaults. GPU queue after the controls: fixed-v5 credit settings → Option R (go decision `docs/additional_work/R_decision.md`) → PC-trained reader → upper-layer 2×2 → scaling. Round 54 lanes below for the runners still missing.

- **2026-09-29 06:35** — Capex round 52 committed (AW-B3, PC-12, X24-final PASS, PC-8 reports, PC-11 tests, R-1 consumer). GPU: settling-depth control done (items 132–133); AW-B calibration done, mixture ρ = e⁻¹ selected (item 134); AW-B evaluation running since 05:24; PC-12 random and matched controls queued behind it. Round 53 lanes below.

- **2026-09-28 17:50** — DEC-076: AW-B pre-registration approved; calibration follows the settling-depth controls on the GPU. Lane AW-B3 (calibration driver) opened first; PC-12 second.

- **2026-09-28 18:00** — DEC-075: three PC-v0 controls approved (settling depth 1/32, random-direction credit, compute-matched adjoint); no base control. Capstan applies the staged PC-9/PC-10 patch tonight (old versions kept) and runs the settling-depth control; lanes PC-12 (the two new credit arms) and PC-8 below.

- **2026-09-28 17:20** — Capex round 51 committed (PC-10 staged, X24 pass on 44 cells, REV-3 Tuesday form). The PC chain finished Sunday 16:13 (both efficacy runs and both harm readouts; lead queue 126–129). Round 52 lanes below: PC-8 is unblocked.

- **2026-09-27 11:05** — Capex round 50 committed (PC-9 contingency patch staged on copies, REV-2 Q&A + results scaffold, PRES-5 timed scripts). PC-v0 replication 39 / 60 (CounterFact cells running), ETA ≈ 13:30. Round 51 lanes below.

- **2026-09-27 08:35** — Capex round 49 committed (Stage-4 report assembled; X23 PASS on cells 136–270). Reviewer primer in `assets/presentation-materials/review-data/README.md`. PC-v0 replication 26 / 60. Round 50 lanes below.

- **2026-09-27 08:10** — Capex round 48 committed (PC-7 fixed-v5 driver, PRES-4 result slides, HT-15b, PC-8 checklist). PC-v0 replication 25 / 60. Capstan's GPU chain: replication → PC-5 harm readout → PC-7 profile (4 development cells) → PC-7 run (4 exposed cells) → PC-6 harm readout. Round 49 lanes below; PC-8 stays pending the run.

- **2026-09-27 07:00** — Capex round 47 committed (PRES-3, PC-6, HT-15); HT-15 paragraph and wording corrections merged into `tails_v1.md`; HT-14 written (`docs/presentation/abstract_to_testbed.md`); post-halt refresh run (R1-D14f). PC-v0 replication 19 / 60 cells done, ETA ≈ 14:15. Round 48 lanes below; PC-7 remains first.

- **2026-09-27 00:00** — queue halted at 270 (DEC-074b), reconciled, boundary report posted; PC-v0 diagnostic + profile running (occupancy guard in `aw/pc_v0.py` narrowed to project processes — Capex please review). Capex round 47 in progress (PRES-3 slides on disk, PC-6 readout adapter `aw/pc_v1_readout.py`).

- **2026-09-26 19:10** — Capex round 46 committed (PC-5 harm driver, R1-D14f refresh, PRES-2 drafts for slides 2/3/6/11); Capstan fixed HT-13 per Capex's review (ES99 → expected shortfall in `aw/scoring.py` and `aw/tail_figures.py`, receipt-filtered collection, title and reference caveats; `tails_v1.md` v1.1). Halt trigger at the 270th start tonight; round 47 lanes below.

- **2026-09-26 11:00** — Capex round 45 committed (PC-3 report generator, PC-4 dev-checkpoint parity, R1-D14e comparator report at 225, PRES-1 brief / deck v3 outline / figure pipeline / claim ledger v7); 65 `aw` tests pass; HT-13 tail figures in assets. Queue at 252 / 330, halt trigger at the 270th start tonight. Round 46 lanes below.

- **2026-09-24 15:55** — DEC-074/074b: the queue runs through block 4 and block-5 positions 1–45 (S1_LM both datasets, S1_literal zsRE), halt trigger armed at the 270th start (≈ Saturday evening); then the PC refocus; Codex round 43 delivered (AW-R0, AW-L0/L1/L3, AW-L prereg) and superseded in priority by the PC lanes below.

- **2026-09-21 17:25** — block 3 complete (135 / 330, the whole triplet); block 4 running with two workers under bindings v2; Codex lane R1-D14d (triplet confirmatory analysis) opened ahead of the additional-work lanes.

- **2026-09-20 17:30** — block 2 complete (90 / 330, 0 failures); Q21 cutover done (drain, idle reconciliation, signed resume); queue running under bindings v2 (factor 1.7, stop-after 6) since 17:16; block-3 watcher armed. Additional work: DEC-073, `aw/` namespace, Codex lanes AW-R0 / AW-L0-L1 / AW-L3 / AW-L-prereg open.

- **v0 closed** (close-out identity `cb04d5e`); the lead's T4 review of the report/memo is still outstanding.
- **Revision v1, Stage 2 is done on the development side.** The learned reader (tied cosine + pairwise null + lexical
  overlap, stable observations, per-position deltas) with ordinary-text null training is reference condition v2; with the
  R1-56 rare-token overlap gate it is the proposed v3 (DEC-043). Development streams, three seeds: zsRE RET-GS 0.96–0.98,
  CounterFact 0.715–0.85, ES / RET-ES / LS 1.00; drift 0.000 / +0.012 nats; near-miss 100/100, revision 100/100; unseen
  edit-prompt false fires zsRE 10–11 % at 1,000 records (45 % without the gate), CounterFact 0 %. Report:
  `docs/R1_stage2_report.md`; running log `docs/R1_stage2_notes.md`; identities `manifests/revision_v1/primary_condition_v{1,2,3}.json`.
- **Costs measured on the real base** (R1-55, `results/R1/p1_profile/`): 1,000 records use 51–74 % of the state
  ceiling with exact restore; edit 0.07–0.13 s; query 10–15 ms; a full 1,000-edit cell with every endpoint at three
  checkpoints ≈ 1,150 s. Codex's 240-cell matrix v3 ≈ 92 h against the 15 h envelope; the lead keeps the full scope (DEC-044);
  ceilings will be set from the measured components.
- **Round 13 committed by Codex** (`c238f02`): register policy v5 (4,218 MQuAKE subjects), protocol v4, dev-loader and
  selection-trace modules (orchestrator wires them), R1-65/66 review (collision rate 2.1–2.3 %), R1-68 integrity components
  (partial). Clean driver profile: 1,252 s per 300-edit cell; 1,000-edit cell ≈ 49–66 min.
- **Primary condition v5** (DEC-049/050; `primary_condition_v5.json`): question-null family seed 2, averaged checkpoints 150–300;
  mean RET-GS 0.803 (zsRE 0.98 / CounterFact 0.82 / MQuAKE 0.61), ES 1.00, LS ≥ 0.98, zsRE unseen 10 / 12 / 9 % at
  100 / 300 / 1,000, near-miss 100/100, revision 100/100, full-assay drift +0.0022 nats. Driver: 1,262 s per 300-edit
  cell (overhead = per-phase clone/restore ≈ 545 s + one-at-a-time drift 506 s); the incremental profile changes nothing.
- **DEC-048 (option C)**: true-fact query presentations are not counterfactual-edit exposure; MQuAKE capacity 4,218 vs
  4,050 demand; full scope stands. **Round 12 committed by Codex** (`cee3d79`): population memo, protocol v3, matrix v4,
  MQuAKE counter-review (notes corrected). Reader status: fixed-locality readers (R1-65) keep retention (MQuAKE 0.79,
  zsRE 0.98, CounterFact 0.86) but zsRE unseen false fires stay 30–52 % at 100 records; question-form nulls (R1-66)
  bring them to 5 % at a retention cost; a 35 % rate and the clean driver profile are running.
- **Round 11 committed** (`8f82316`): self-contained MQuAKE slices (train 500 / dev 100, v3), development payload builder and
  execution mode for the cell driver (materialized base copy, checkpoint-identity helper), exposure trace audit (no
  certified releases; MQuAKE ≤ 2,829 subjects even if every review candidate cleared), freeze candidate v1 (dry).
- **Round 10 committed** (`3e8a980`): register v4 + MQuAKE exposure supplement, composition endpoint module, Stage 4 cell
  driver with all comparator adapters, three-dataset analysis. MQuAKE capacity deficit found (2,100 distinct candidate
  subjects vs 4,050 needed under conservative reservations) → R1-D4b.
- **MQuAKE reader**: proposed primary v4 (three pools; `primary_condition_v4.json`): zsRE 0.95–0.98, CounterFact 0.76–0.83,
  MQuAKE 0.56–0.79 (seed-sensitive); DEC-046/047 proposed defaults.
- **Round 9 committed by Codex** (`678c703`): analysis adapter (R1-57), draw recipe dry-run (R1-58), protocol v2 (R1-59, 360 cells),
  counter-review (R1-X8; cache repair applied), MQuAKE preparation (R1-D4: 6,043 items, composition inventory).
- **Round 8 committed** (`c401f55`): Stage 4 protocol draft (R1-49, gates U01–U18), frozen register binding
  (R1-D1f, `exclusions_frozen_v3.json`), ordinary-text null spec (R1-50b), R1-24 review (R1-X7; qualifications applied
  to the notes).
- **DEC-045**: MQuAKE-CF is the third dataset (`assets/data/raw/mquake/`); CounterFact stays (which needs the DEC-042
  exception). DEC-043 accepted, DEC-044 keeps the full matrix (now 360 cells). Then the freeze (R1-41). No draw, seal or launch before those.
- Rules unchanged (§ top); Codex: new files only, CPU only, no sealed payloads, no real-base execution; edit requests
  as patches under `docs/tasks/`. Tests under `tests/revision_v1/` (CPU) must pass.

- **Round 16 committed** (`2e7ac38`, 2026-09-16): R1-X12 selection review (42 candidates, 15 admissible, unique winner;
  zsRE unseen 10/100, Wilson 95 % 5.5–17.4 %; occupancy flatness unproved because the outside sets differ), R1-68c
  instrumented driver with batched drift (owner re-profile running), R1-72 schedule scenarios (331–452 GPU h vs 306
  available), HT-1b v5 tail audit (v5 zsRE mean +0.0022 nats but max 8.7 nats and 17 positions > 0.1; CounterFact
  +0.006## 3. Lanes for Codex — round 41 (CPU; open now; posted 2026-09-18 15:05 EDT) — report coverage; verification lanes wait

Round 40 is committed and mirrored. New files only while the lead signs; `scripts/r1_d14_report.py` and its template are
Codex's own and not bound by the operator's digests, so they may be edited. Priority order: **R1-63o (urgent; supersedes R1-D10i) → R1-D14b → X20 (after
step 8) → HT-4f (after step 2).**

### Lane R1-63o — re-bind the ENTIRE live package to the current tree, then freeze the tree (URGENT; supersedes R1-D10i)

**Sequencing (17:30 EDT): both answered — DEC-069 (Q19: A + the t-interval secondary display) and DEC-068 (Q20: triplet-first). Proceed now.** Fold both into the same
versioned pass: protocol **D.5** (Q19: the three-cluster inference statement per review §2 — registered computation kept,
relabelled as preliminary decision summaries, every realization estimate and order dispersion shown, effects before
labels, no 95 % familywise claim; plus the assumption-labelled t-interval if the lead takes it; and §1's explicit
deferral of the unperformed factorial / PC branches) and matrix **D.5** block numbers under the amended order (Q20:
triplet across all realizations first, then matched / live, then S1, then the extension). One package, one rebind,
then the tree freeze.

The signing session (DEC-067: delegated to the orchestrator; session v9 on inputs v10) completed steps 1–5 — clearance,
RNG admission with the lead's seed, draw (100 / 100 near-miss pairs matched in every dataset × realization) — and
stopped at endpoints: `r1_d10c_endpoints construct` refuses ("review input changed: scripts/r1_d10c_endpoints.py")
because the role plan binds that script at its round-26 bytes. A recursive scan of every resource the remaining
steps read (`logs/r1_round41/stale-bindings-inventory.txt`, 1,701 resources, 93 with stale bindings) shows the drift
is package-wide: producer scripts edited after their outputs were bound — `r1_d10c_endpoints.py` (role plan, joint
evidence, historical evidence), `r1_49g_inference.py` / `r1_49g_analyze.py` (matrix D.4 and earlier), `r1_63j_production_bundle.py`
(all 27 runtime templates in `R1-63m-runtime-v2/`), `r1_58h_cost_contract.py` (cost receipts), `r1_d9_receipts.py`
(D10 evidence chain), `r1_68c_dev_cell.py` / `r1_77b_sealed_backend.py` (older candidates). Do, in one versioned pass
on the current tree: role plan v2 and joint evidence v7 (provenance refresh only; state that no row changed), matrix
D.4.1 regenerated by its producer, runtime templates v3, cost receipt v5 (same content, current producer binding),
candidate v15, inputs v11 (clearance evidence → v7, role plan → v2, matrix → D.4.1, construction inputs → v10),
forms v10 and sheet v9; verify with the orchestrator's scanner method that NO resource on the live path (inputs v11 →
everything reachable) binds a file whose bytes differ from the tree. Then **declare the tree frozen**: from that commit
until launch, no edit to any script bound anywhere in the package (list them); any further change requires a new
package version and the orchestrator's go-ahead. The orchestrator then runs a fresh session (steps 1–8) on inputs v11
with the same seed, and X20 verifies.

### Lane R1-D10i — clearance evidence re-bound to the current endpoint constructor (URGENT; blocks the lead's step 3)

The lead's `clearance --execute` refuses with `exhaustive_clearance_review: clearance evidence binding changed`: the
operative joint evidence (`assets/runs/pc_cap/R1/r1_d9e/round26_final/joint_evidence_DEC061.json`) lists
`scripts/r1_d10c_endpoints.py` at its round-26 bytes (sha a2c968b4…) among its `evidence_bindings`, and round 31
changed that file (now 9afe6221…; full-validation contract) — the dry run does not check the bindings, the execute
path (`r1_d9_receipts.clearance_value`) does. The clearance rows themselves are untouched. Emit evidence v6 = v5 with
that binding refreshed (and any other stale producer binding — run the check over all 865), a statement that the
D10c edits since round 26 do not affect clearance, inputs v10 binding evidence v6, candidate v15, and say explicitly
whether the signed step-1 / step-2 receipts stay valid under inputs v10 (see the orchestrator's finding on what the
receipts bind, lead queue item 94) or must be re-signed. New files only; the lead's session is paused at step 3.

### Lane R1-D14b — apply X21's four coverage gaps to the report formatter (first)

G1: the remaining v5.1 §5.2 / D.2 tail fields (exp(mean ΔNLL) with overflow handling, signed maximum with position
and tie convention, zero-mass atoms; KL counterparts; sample fields bound from the analysis JSON, never invented);
G2: the joint cap-fidelity benchmark flag beside the per-reference labels, with unavailable ≠ false; G3: the
secondary historical-v2 package comparison table (eight secondary-role contrasts, 24 metric rows, `secondary_descriptive`,
the 63-interval family untouched); G4: the DEC-052 execution-accounting section bound to a verified D11 / D13 report
(process spend, unknown-cost records, retries, host failures, block reconciliation) or an explicit "unavailable"
section. Acceptance fixtures as X21 lists; the 63 primary rows and classifiers identical before / after; the skeleton
refilled from the synthetic output with no unbound placeholder.

## Round 43 — additional work (DEC-073), Codex lanes (2026-09-20)

Ground rules for every lane: CPU only (`JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=`), no file under `scripts/` or
`src/pccap/` is added or edited (content lock; the resume consumer re-verifies it), no large cache builds while the
queue runs, Codex-owned files only (listed per lane; `aw/bounded.py`, `aw/wrapper.py`, `aw/scoring.py` and
`docs/additional_work/{AW-B,R}.md` are the orchestrator's), task record `docs/tasks/AW-<lane>.md` + completion JSON as
usual. Plans: `docs/additional_work_plan_final.md` (binding), `additional_work_plan{,2,3}.md` (history).

## Round 52 — reports from real data (2026-09-28, 17:20)

The GPU chain is complete: `results/additional_work/PC-v0/replication-60-20260927/` (60 cells),
`results/additional_work/PC-v0/harm/pc-v0-60-20260927/` (legacy S5 subset, 4,064 positions per arm),
`results/additional_work/PC-v1/replication-4-20260927/` (4 cells), `results/additional_work/PC-v1/harm/pc-v1-4-20260927/`
(full inventory, 245,237 positions per arm; see its `cost-repair.json`: the table was generated after a driver
KeyError and its population caption is the fixed v0 text). Capstan's preliminary reads are lead-queue items 126–129.

**Note for Capex (2026-09-28 18:10):** the round-52 list you acknowledged predates two additions: **AW-B3 below is now
first** (the calibration is the next GPU job after tonight's controls), then PC-12, then PC-8 / X24-final / R-1. The
applied PC-9/PC-10 files in `aw/` are the running versions until the settling-depth chain ends (≈ 03:00); build PC-12
against those applied versions (committed at 1074ccc), not the originals under `PC-9-candidate/old/`, and land the
edits in new files or after the chain's finish is posted in the lead queue.

## Round 65 — the round-64 lanes, carried forward (2026-10-05, 06:00)

Round 64's lanes were pre-empted by the lead's direct request for the colleague long-talk deck (PRES-colleague-long,
delivered and committed 5 Oct). They stand unchanged and are now the round: **FIN-1** (consolidated supplemental-
programme report via a generator), **FIN-2** (freeze dry run on 6 Oct producing `docs/freeze_handoff_20261009_draft.md`),
**LINT-1** (five ruff findings; `aw/cost_gate.py`), **DOC-3** (reviewer entry point: results complete, plus a link to the
colleague deck PDF and to `assets/support-information/`). Specifications are in the round-64 section below. Priority:
FIN-1 → FIN-2 → LINT-1 → DOC-3. Add to DOC-3: link `assets/support-information/Capstan-README.md` and
`README-random-sample.md` (public GitHub URLs) as the "worked examples" entry. Colleague-deck follow-ups (timing cut,
example swaps) wait for the lead's rehearsal notes.

## Round 64 — closing the record: consolidated report, freeze dry run, small fixes (2026-10-04, 06:30; DEC-083)

Priority: FIN-1 → FIN-2 (on Oct 6) → LINT-1 → DOC-3. All CPU. No experiments.

### Lane FIN-1 — consolidated report of the supplemental programme

`docs/additional_work_report.md`, assembled by a generator (`aw/additional_work_assembly.py`, in the manner of
`aw.stage4_assembly`: lettered sources with hashes, no new scoring): one entry point for everything after the halt —
PC-v0 and its three controls, fixed-v5 credit and settings, the harm readouts, AW-B, PC-trained reader (three seeds),
Option R (realizations 0–3, v0 deferred), the upper-layer 2×2, HT-13/15/17, the κ pilot — each with its question,
design, population and exposure label, headline table copied from the canonical report, limitations, measured cost, and
the decision that authorised it. A closing section states what the supplemental programme supports and does not
(the DEC-081a language), the GPT-2-small caveat, and the total GPU process-hours spent after the halt from receipts
(no double charging of shared controls or nested costs). Tests on a synthetic tree. Done-when: regenerable from the named
sources; X25 covers it.

### Lane FIN-2 — freeze dry run (run on Oct 6, after FIN-1)

Execute every item of `docs/freeze_checklist_20261009.md` except the lead's signature: closed inventory check, receipt
closure check (including the cost-gate note from AW-L5 and the Option R segment totals), the final CPU refresh in
dependency order into dated directories, X25 and X26 reruns, the one-command reproduction, the deck archive
(`assets/presentation-materials/deck_v3/freeze-20261009/`). Produce `docs/freeze_handoff_20261009_draft.md`: the dated
artifact list (every canonical directory and its hash), generator versions, open items and disclosed exceptions, and
the exact lines the lead signs. Done-when: the lead can complete the freeze on Oct 9 by reading one document.

### Lane LINT-1 — small fixes

`ruff check aw/` reports five findings; fix them (no behaviour change; tests pass). Add `aw/cost_gate.py`: reads the
exact projected-process-hours field from a `reader_portfolio_cost` output (extensionless file), rejects missing or
invalid input, compares with a stated gate; document it in `REPRODUCE_additional_work.md` beside the AW-L5 note. Tests.

### Lane DOC-3 — reviewer entry point: final results

`assets/presentation-materials/review-data/CURRENT.md`: add a dated "Results complete (Oct 4)" block linking the three
final reports, the HT-17 complete snapshot and FIN-1's consolidated report (public GitHub URLs); keep the Oct 2
documents as historical. Regenerate the folder manifest.

## Round 63 — the three-seed reader refresh (2026-10-03, 06:30; conditional)

### Lane PC-16b — PC-reader, HT-17 and deck refresh for ePC seed 2 (**go since 2026-10-03 08:36: both evaluations complete**)

Seed-2 training is at step 282/300 (ends ≈ 07:45); its two evaluations follow (≈ 08:45). When
`results/additional_work/PC-reader/eval-epc-s2-counterfact/report.json` exists with a complete status (the owner also
posts the trigger in a lead-queue item): run `aw.pc_reader_report` with `--refresh-tail` into fresh dated directories,
rewrite `docs/additional_work/PC-reader_report.md` as the **complete** 12/12 report (three paired seeds), apply
`aw/reader_interpretation.py`'s rules for the three-seed reading (within-recipe consistency of the paraphrase deficit;
firing and harm by seed with signs; nearly-equal own-prompt retention; measured ≈ 100× cost; no superiority or safer-
learning claim; training seeds are not subject realizations), then refresh the deck's reader statements (slides 10–12
as applicable), `numbers_to_say.md`, Q&A, ledger rows and the rehearsal pack through PRES; replace every "partial /
10 of 12" statement. Rerun X26. Done-when: report, tail snapshot, deck, numbers and pack agree on twelve evaluations.

Then: R-3 after Option R (≈ this evening), AW-L6 after AW-L5 (≈ Oct 5), PRES refresh after each, X25 and the
one-command reproduction at the end (Oct 7–8).

## Round 62 — after the review: collaboration foundation; closing the review folder (2026-10-02, 14:00; DEC-082)

### Lane POST-1 — foundation for the post-conference collaboration on coupled entropy / coupled free energy

Write `docs/post_conference/coupled_collaboration_proposal.md` (new folder) for the authors' group, building on
`docs/additional_work/coupled_objective_note.md` and the Oct 2 review (DEC-082): (1) what this testbed offers a coupled
objective (frozen GPT-2 small base, the residual cap with read/write interfaces, the null gate, the delta acquisition
with adjoint or ePC credit, the 245,237-position harm readout, the receipted/hashed pipeline, local JAX) and what it
lacks (no probability model over latent correction states, no policy loop); (2) the open questions for the
collaborators, verbatim from `docs/friday-10.02-review/UPDATE-2026-10-02.md` §6, each with the decision it unblocks;
(3) a first joint experiment as a pre-registration skeleton: a specified coupled objective (to be chosen with the
authors) vs the ordinary objective, matched initialisation, data, schedule and cost, three seeds, the existing 300-edit
exposed evaluation and the full harm readout, with the "minimum evidence before training" tests from the note as entry
conditions; (4) cost and calendar (CPU validation, GPU hours from the measured reader-training and readout profiles),
and the data-reservation situation (what fresh subjects remain after Option R). Nothing is implemented or scheduled;
no PyTorch, no remote. Done-when: a document the lead can send to Kenric's group after 15 Oct.

### Lane PRES-9 — close the review folder; record the outcome

Add a dated "Outcome" section to `docs/friday-10.02-review/UPDATE-2026-10-02.md`? No: that file is Capstan's; instead
write `docs/friday-10.02-review/OUTCOME-2026-10-02.md` recording DEC-082 (proceed as planned; collaboration foundation;
κ readout closed), link it from `assets/presentation-materials/review-data/CURRENT.md` (public GitHub URL, second entry),
mark `qa.md`'s reviewer-meeting placeholders as resolved with "no changes requested", and refresh the reviewer folder
manifest. Done-when: CURRENT.md shows the outcome and the folder manifest is consistent.

Then the owner-triggered refreshes as before: PC-16a for seed 2 (≈ Oct 3 09:30), R-3 after Option R (≈ Oct 3 evening),
AW-L6 after AW-L5 (≈ Oct 5), PRES deck refresh after each, X25 and the one-command reproduction at the end.

## Round 61 — reviewer entry point for this afternoon; the seed-1 refresh (2026-10-02, 09:50)

Two lanes, in this order; both CPU; the meeting is this afternoon, so DOC-2 first.

### Lane DOC-2 — add the 2 October update to the reviewer entry point

`docs/friday-10.02-review/UPDATE-2026-10-02.md` (Capstan, committed 8b9d3c6) is the summary of everything since
Nelson's feedback, written for Kenric Nelson and Matt Iklé. Add it as the first link in
`assets/presentation-materials/review-data/CURRENT.md` (label it "2 October update: read first"), reference it from
`review-data/results.md` and `final-experiments.md` where they summarise the PC-reader, HT-17 and Option R state, and
regenerate the folder through `aw.reviewer_folder` so the hashes and manifest match. Do not edit the update itself (it is
Capstan's file); if a number in it conflicts with a canonical report, note the conflict in the handoff. Done-when:
CURRENT.md lists the update first and the folder manifest is consistent.

### Lane PC-16a (continued) — refresh for ePC seed 1 (go since 08:13)

Both seed-1 evaluations are complete (`eval-epc-s1-{zsre,counterfact}/report.json`, status complete). Run
`aw.pc_reader_report` with `--refresh-tail` into fresh dated directories, rewrite
`docs/additional_work/PC-reader_report.md` (10 of 12 cells; two paired seeds; the two-seed reading in lead-queue item
155: seed 0's quiet reader was largely a seed effect; the consistent finding is identical own-prompt retention with a
small paraphrase deficit, zsRE −0.026/−0.020, CounterFact −0.242/−0.022; firing seed-dependent under both rules;
measured cost ≈ 100×), then refresh the deck's reader statements, `numbers_to_say.md` and the rehearsal pack through
PRES, keeping the three-seed answer marked partial. Seed 2 lands ≈ 3 Oct 09:30; the owner posts the trigger.

## Round 60 — seed-1 refresh; reproduction document for the supplemental work (2026-10-02, 07:30)

Held for the Oct 2 review outcome: POST-1 (coupled-objective study design) and PRES-9 (fold the reviewers' notes). Both
open as soon as the owner relays the meeting.

### Lane PC-16a — PC-reader and HT-17 refresh for ePC seed 1 (**condition met 2026-10-02 08:13: go**; then seed 2)

ePC seed-1 training finished 07:15 (86,798 s; 300 steps); its zsRE evaluation is running and the CounterFact one
follows (≈ 08:15). When `results/additional_work/PC-reader/eval-epc-s1-counterfact/report.json` exists with a complete
status: run `aw.pc_reader_report` with its `--refresh-tail` step into fresh dated directories (per the PC-16 task),
rewrite `docs/additional_work/PC-reader_report.md` (now 10 of 12 cells; two paired seeds), and refresh the deck's
reader statements and `numbers_to_say.md` through PRES, keeping the three-seed answer marked partial. Repeat when seed
2 lands (≈ Oct 3 09:30; the owner posts the trigger). Done-when: report, HT-17 snapshot, deck and numbers agree on the
available seeds, with denominators.

### Lane REP-1 — reproduction document and one-command refresh for the supplemental work

`docs/REPRODUCE.md` covers v0 only. Write `docs/REPRODUCE_additional_work.md`: for every supplemental result and every
figure the deck cites (PC-v0 and its controls, PC-v1 and the credit-setting variants, the harm readouts, AW-B calibration
and evaluation, PC-reader, Option R, AW-L, HT-13/15/17, κ pilot), the exact command, its inputs with hashes, the output
directory, CPU or GPU, and the measured cost; the generator dependency order from `docs/freeze_checklist_20261009.md`.
Add `aw/refresh_reports.py` (CPU): runs the report generators in that order into fresh dated directories, records which
inputs changed since the previous run, and refuses to overwrite canonical directories; tests on a synthetic tree. GPU
steps are documented, never executed by it. Done-when: a reader with the two repositories can regenerate every CPU
artifact the deck cites from the document alone.

## Round 59 — consistency audit of the spoken numbers; reviewer-folder refresh (2026-10-01, 15:20)

Two small CPU lanes now; refresh duties follow as results land (owner triggers: PC-16 + HT-17 refresh after ePC seed 1
≈ Oct 2 09:00 and seed 2 ≈ Oct 3 10:30; R-3 after Option R ≈ Oct 3 evening; AW-L6 after AW-L5 ≈ Oct 5; then PRES deck
refresh and the X25 rerun). A post-conference proposal lane (POST-1: the coupled-objective study design, building on
`coupled_objective_note.md`) opens after the Oct 2 review so it can carry the reviewers' answers.

### Lane X26 — spoken-number consistency audit

`aw/script_numbers_check.py` (CPU): extract every numeral and percentage from the resolved 15- and 25-minute scripts,
`qa.md` and the slide drafts; match each to `docs/presentation/numbers_to_say.md` and from there to a canonical report
or ledger row (tolerance for rounding stated); list unmatched numbers, literal placeholders and any number whose source is
an intermediate directory. Output `logs/additional_work/X26/` (table, JSON) and a short `docs/tasks/X26.md` with the
discrepancies. Rerun after each deck refresh. Done-when: every spoken number traces or is listed as a discrepancy.

### Lane DOC-1 — reviewer-folder refresh

Bring `assets/presentation-materials/review-data/results.md` and `final-experiments.md` (Capex's) up to the round-58
state: HT-17's finite-range reading and the AW-B one-third severity cut, the PC-reader partial (BP ×3, ePC s0, ≈ 100×
measured cost), Option R's resume with the v0 class deferred (DEC-080), DEC-081/081a, the S4-LIM caveats, the freeze
checklist pointer; keep the Oct 1 Capstan primer and feedback documents referenced as the reviewers' entry points.
Done-when: a reviewer reading the folder on Oct 2 sees the same state as the repository.

## Round 58 — freeze readiness, rehearsal, limitations, optional checks (2026-10-01, 15:05)

Priority order: X25 → S4-LIM → PRES-8 → KP-1 → CAL-1. All CPU; no GPU; the GPU queue is Capstan's. Round-57
generators are rerun by the owner as results land (ePC seeds ≈ Oct 2 08:40 / Oct 3 10:10; Option R ≈ Oct 3 evening;
AW-L5 ≈ Oct 5); Capex refreshes the deck through PRES after each.

### Lane X25 — supplemental-results receipt and hash audit; freeze checklist

In the style of X22–X24, an independent read-only audit of every post-halt result that a report or slide cites: PC-v0
(60 cells + controls k1/k32, random, matched), PC-v1 (4 + the credit-setting variants) and their harm readouts, AW-B
calibration and evaluation, PC-reader (profiles, trainings, evaluations as they complete), Option R session segments,
HT-17 snapshots. For each: the cited file exists, its hash matches the report's `sources_sha256` / `sources.json`, the
cost/finish receipts are complete, no number in a report or ledger row lacks a named source, and no result is cited from
an intermediate directory where a canonical one exists. Output `logs/additional_work/X25/` (table, JSON, PASS/FAIL per
report) and a one-page **freeze checklist** for Oct 9 17:00 (`docs/freeze_checklist_20261009.md`): what the lead signs,
which directories are final, which generators were last run on which inputs, open items. Rerun once more after the last
GPU result lands (owner tells you). Done-when: every cited result PASS or an explicit discrepancy list.

### Lane S4-LIM — Stage-4 report limitations: the model-scale caveat

`docs/R1_stage4_report.md` (assembled; `logs/R1/reports/stage4-assembled/`) has no statement that the base is GPT-2 small
(124M) and that findings may not transfer to production-scale models (the lead's 29 Sep review asked for this in every
external report). Add it to the report's limitations section through its generator (not by hand-editing an assembled
file), with the same sentence in the triplet and comparator reports' limitations and in the deck's scope slide (12)
if absent; also note there the DEC-074b halt (S1_literal CounterFact and the extension unavailable) and the DEC-080
Option R v0-class deferral as reporting limitations. No numbers change. Done-when: regenerated reports carry the caveat;
diff shows only the added text.

### Lane PRES-8 — rehearsal pack and Q&A refresh

`docs/presentation/qa.md`: add the questions the entropy feedback raises and the answers the deck now supports (what
class the data support and why we say "fitted finite-range shapes"; the κ pilot versus the calibrated coupled entropy,
with the (1 − e^{−κℓ})/κ form; the one-nat bound as a proven ceiling; W(N) and why no entropy-growth claim; the
equation-126 question kept private); the PC-reader three-seed answer as a placeholder to fill on Oct 3; the Option R
answer (learned vs random on realization 3, v0 deferred). Rehearsal pack under `assets/presentation-materials/deck_v3/
rehearsal/`: the 15- and 25-minute scripts with per-slide timings from `aw/presentation_timing.py`, a backup-slide index
(HT-17 survival, κ trade-off, controls figure), and a one-page "numbers to say" sheet with sources. Fold the lead's
notes from the 2 Oct review when they arrive (owner relays). Done-when: Q&A and rehearsal pack exist and match the
round-57 deck.

### Lane KP-1 — κ-pilot reader restoration check (CPU; enables the optional Oct 5 readout)

Determine, without model execution, whether the nine κ-pilot readers (ordinary / κ 0.2 / κ 0.5 × seeds 0–2) and the
memories used by `results/R1/drift_assay_ht3_*` can be restored exactly for a 245,237-position readout under
`aw/pc_harm_readout.py` (or the AW-B scoring path): artifact paths and hashes, memory snapshots, calibration, gate
settings, the development streams and edit counts used; a dry-run plan with the exact owner command, projected cost
(from the 25-min-per-cell readout profile) and what would be comparable to the Stage-4 assay (different population:
label it). If restoration is not exact, say so and stop. Done-when: `docs/tasks/KP-1.md` with a go/no-go and the
command; nothing launched.

### Lane CAL-1 — calibration demonstration and the post-conference objective note (optional, half a day)

Known-distribution checks of Nelson 2026's one-sided α = d = 1 formulas in `aw/entropy_feedback_checks.py` or a sibling:
normalised density, slope condition x f′/f = −1 at x = σ, escort moment E_escort[X] = σ, κ → 0 limit, the entropy
1 + ln_{κ/(1+κ)} σ, for κ ∈ {0, 0.25, 1, 2} (ordinary mean finite/divergent vs escort moment); plus a two-page note
`docs/additional_work/coupled_objective_note.md`: what a JAX implementation of a coupled free-energy objective for the
residual agent would need to specify (modelled variable, reference distribution, constraints, normalisation, escort
gradients, tests), as the starting point for the post-conference discussion with the reviewer's group. No training, no
GPU. Stop if it becomes a library port.

## Round 57 — fold the new results in; report generators for the last three runs (2026-10-01, 14:40)

Priority order: PRES-7 → PC-16 → R-3 → AW-L6. All CPU. Generators are scaffolded on the cells that exist and rerun by
the owner when the remaining cells land (ePC seeds ≈ Oct 2 08:45 and ≈ Oct 3 10:30; Option R 16 cells ≈ Oct 3 evening;
AW-L5 ≈ Oct 5). No GPU use; the GPU queue is Capstan's.

### Lane PRES-7 — deck integration of B–D and HT-17

Fold `docs/friday-10.02-review/talk-text-B-C-D.md` (slides 2/6/7/8/11; ledger rows `kappa-design`, `AW-B`, new
`HT17-tails` and `AI-coupled-FE`) into `docs/presentation/deck_v3/` and `docs/talk_claim_ledger_v7.md`, replacing the
"[prototype, pending HT-17]" placeholders and the appendix with HT-17's reported numbers (frequency, conditional
severity, shapes with intervals where eligible, the held-out comparison, the AW-B severity cut, the invalid-fit
labelling). Slide 6/7 on-screen: HT-17's frequency-vs-severity figure beside (or instead of) the HT-13
rarity-vs-severity; survival figure as backup. Update both speaking scripts, `docs/presentation/final-experiments.md`
(DEC-080/081/081a, HT-17, Option R deferral), `review-results.md` and the resolved deck export. Language: fitted
finite-range shapes; no class, no W(N), no infinite variance, no temperature; the κ pilot as a bounded deformation of
one surprisal; the mixture as a proven ceiling. Done-when: deck, ledger, scripts and export agree with the HT-17 report.

### Lane PC-16 — PC-trained reader report generator (three seeds per rule)

`aw/pc_reader_report.py` (CPU): reads `results/additional_work/PC-reader/train-*/report.json` and
`eval-*-s*-{zsre,counterfact}/{report.json, stream/checkpoint-300.json, harm/}`; tables per reader × dataset (ES,
RET-ES, RET-GS, LS, near-miss, revision, unseen false fires, gate telemetry: fired positions, hard nulls; harm: mean KL,
mean ΔNLL, ES99+, max, exceedances; training cost, parameter count, evaluation cost); paired BP−ePC differences by seed
and the seed spread; the selected v5 artifact's values on the same streams as a labelled historical reference (items
145–146); failed/missing cells visible with denominators. Then a step that runs HT-17's refresh (new output directory,
per its report) and cites the reader rows. Report `docs/additional_work/PC-reader_report.md` from the completed BP ×3 +
ePC s0 now, marked partial; the owner reruns when seeds 1–2 land. Framing: a quieter reader (fewer paraphrase
retrievals, fewer ordinary-text firings) if it holds across seeds; training seeds are not subject realizations; no
superiority claim; cost 37× stated. Tests on a tiny synthetic result tree.

### Lane R-3 — Option R extension report generator

`aw/r_report.py` (CPU): from the session receipts (`logs/additional_work/R/queue/20260929T174143/`, resume segments) and
cell outputs, an extension report `docs/additional_work/R_report.md`: realization 3, learned reader vs random reader
on zsRE and CounterFact, five orders each (the `v0_stable` class explicitly deferred per DEC-080, the ceiling-killed cell
incomplete by ceiling, both visible); behaviour at 100/300/1,000 beside realizations 0–2; the registered learned-vs-random
contrast recomputed on realizations 0–3 as a labelled sensitivity with the t(3) display (no re-issued classifier labels,
no re-run of the registered family); fidelity-watch entries; costs (segments, ceilings, deferrals). Scaffold on the four
complete cells now; the owner reruns when the 16 land. Tests on a synthetic session.

### Lane AW-L6 — upper-layer interface 2×2 report generator (lowest priority)

`aw/aw_l_report.py` (CPU) for the AW-L5 outputs (six readers, read {1,2,3}/{2,3} × write {1,2,3}/{3}, 24 evaluations):
per seed/dataset/arm tables, paired read, write and interaction differences, the 0.02 descriptive tolerance shown and
not inferential, fidelity beside efficacy, cost with the dense-zero charging rule; report `docs/additional_work/AW-L_report.md`.
Scaffold against the AW-L5 development outputs; final when the run completes (≈ Oct 5).

## Round 56 — saved-vector tail analysis (2026-10-01, 14:05; DEC-081/081a)

### Lane HT-17 — harmful-change frequency and conditional severity from the saved harm vectors (CPU only)

Specification: `docs/tasks/HT-17.md`, which adopts Capex's own seven-point design from
`docs/friday-10.02-review/feedback-MMK-nelson-entropy-capex.md` as written. Populations: Stage-4 learned / stable v0 /
random caps (both datasets, every realization and order), the paired AW-B arms, the BP and ePC reader seeds as they
land, the pilot assay kept separate. Excess fits over u ∈ {0.01, 0.1, 0.5, 1} nats (generalized Pareto vs exponential
restriction; conditional lognormal if both fail), exceedance probability and contributing windows, joint window-identity
resampling, a "not identified" screen, invalid-fit marking (endpoint boundary; κ ≤ −1/2), no entropy column, small
figures. Language: fitted finite-range shapes, not complexity classes. Fits by Oct 5; report 6–8 Oct. No GPU. Capstan
checks a slice and carries the agreed wording to the deck via PRES. Prototype evidence only:
`feedback-MMK-nelson-entropy.md` §3 (revised).

## Round 55 — Option R reconciliation and resume (2026-09-29, 21:10; urgent)

### Lane R-2 — reconcile the torn Option R attempt and resume the session (first, before PC-15)

Session `logs/additional_work/R/queue/20260929T174143/`: four cells complete; cell `61eb6d08…` (v0_stable, zsRE,
order 100) was killed at its 8,002 s allowance with checkpoints 100 and 300 certified and phases open; the consumer
refuses to resume on "unknown/torn attempt cost". Needed: (1) an owner reconciliation step in `aw/r_run.py`
(`reconcile --cell-id … --execute`) that closes the torn attempt with its whole-envelope cost (8,002 s, already
charged in `dispatch-00/finish.json`), records the cell as incomplete-by-ceiling with no retry budget, and writes a
receipt; (2) `run --resume` continuing the same session with the remaining 25 cells, skipping incomplete cells;
(3) a diagnosis of why the v0_stable zsRE cell ran several times slower than its R1 donor (checkpoint 100 at 40 min
against a 78-minute full R1 cell) — phase timings, GPU contention with the paired learned-reader cell, watch or
full-validation cost in the consumer — and, if the class will not fit its ceiling, an explicit owner-visible option
to defer the class rather than burn 8,002 s per cell; no silent ceiling increase. Capstan resumes as soon as this
lands.

## Round 54 — the runners the default portfolio still needs (2026-09-29, 06:50; DEC-077)

Order for Capex: PC-13 and AW-B4 (round 53) remain first because the talk needs them; then the three runners below in
this order, each CPU-validated on the tiny base and handed off with owner commands. Capstan dispatches on the GPU as
each lands, behind the queue (controls → v5 credit settings → Option R).

### Lane PC-15 — PC-trained reader runner

`aw/pc_reader_train.py`: train the selected v5 reader recipe (same data pools, steps, optimiser, seeds, checkpoint
policy) with the corrected ePC surrogate (`revision_v1/epc_train.py`, imported not copied) instead of BP, three seeds
per rule (BP re-trained under the same runner as the control, so the comparison is within-runner), then evaluate each
of the six readers on the exposed realization-0 streams (300 edits, order 100, zsRE and CounterFact) with the R1
endpoints, adjoint acquisition in all arms (the credit rule is not varied here), and a harm readout hook. Record
training cost. Pre-registration paragraph in `docs/additional_work/PC-reader.md` (Capex drafts; defaults apply).

### Lane AW-L5 — upper-layer trained 2×2 runner

`aw/aw_l_train.py`: the AW-L pre-registration as written (read sets {1,2,3} / {2,3} × write sets {1,2,3} / {3},
three paired seeds, six trained readers, 24 evaluations on the exposed realization-0 streams at 300 edits), using
`aw/interface.py` (AW-L3) for the masks and the same training recipe as PC-15's BP control; profile step first.

### Lane HT-16 — 3,000-edit scaling: population check and recipe

Can a 3,000-edit zsRE stream be built for realization 0 without touching Option R's subjects or any exposed
identity outside realization 0? If yes, a recipe with checkpoints at 1,000 / 2,000 / 3,000 and the full-validation
assay at each, three orders; if no, a one-paragraph note and the lane closes.

## Round 53 — fold the new results into the record (2026-09-29, 06:35)

Delivered and committed by Capex in round 52: AW-B3, PC-12, X24-final, PC-8, PC-11, R-1. New results since PC-8's
reports: the settling-depth control (`results/additional_work/PC-v0/control-k{1,32}-20260928/` with harm readouts
under `harm/control-k{1,32}-20260928/`; lead queue 132–133) and the AW-B calibration
(`results/additional_work/AW-B/calibration-20260929/`, selection = mixture ρ = e⁻¹, no comparator; item 134); the
AW-B evaluation on the ten sealed realization-0 memories is running (`evaluation-20260929/`), and the random /
matched controls follow it on the GPU automatically.

### Lane PC-13 — settling-depth control report and the credit × depth figure (first)

`docs/additional_work/PC-controls_report.md` (extend with the random / matched groups when they finish): per depth
1 / 8 / 32 the paired efficacy, harm and cost against adjoint, with the exact one-step equality stated as the mechanism
check; one figure for slide 9 with own-prompt retention, paraphrase retention, ES99+ and learning cost against depth
(`assets/presentation-materials/figures/pc_v0/controls/`); claim-ledger rows; the reviewer table in `review-data/results.md`.
Use the treatment-aware generator; do not pool depths.

### Lane AW-B4 — bounded-correction report (second; the evaluation finished 11:16 and met the success rule — fold `results/additional_work/AW-B/evaluation-20260929/` into the report, ledger and slide 8 now)

`docs/additional_work/AW-B_report.md` from the calibration and evaluation outputs: the sixteen-setting development
table (why every clip fails, why the mixture holds), the mechanical selection with its rule, the sealed-stream
evaluation of v5 / cap-off / mixture per order with paired differences, the tail figure (survival curves before and
after the bound, the 1-nat ceiling visible), cost; ledger rows; slide 8 material beside the κ pilot; the reviewer
table. State the guarantee precisely: ≤ 1 nat per token at a fixed prefix, not a bound on total or generated-text loss.

### Lane PRES-6 — deck update for slides 8 and 9 and the closing slide (third; after PC-13 and AW-B4)

Fold the two new results into the speaker drafts and the resolved export; the measured / proposed labels and the
Tuesday decision form updated with what now exists.

### Lane AW-B3 — bounded-correction calibration driver (first; DEC-076; GPU dispatch by Capstan after the controls)

`aw/aw_b_calibrate.py` + tests. Inputs: the pre-registration `docs/additional_work/AW-B.md` (approved), Capstan's
`aw/bounded.py` (oracle), `aw/wrapper.py` (`BoundedCap`, generation-time wrapper; unrestricted equals the registered
learner to the bit), `aw/scoring.py` (`Accumulator`: every wrapper configuration from one base/cap pass, expected-
shortfall ES99). Per dataset (zsRE, CounterFact): restore one qualified v5 development memory (the saved 300-edit
development snapshot AW-L0 / PC-4 used for zsRE; identify or produce the CounterFact equivalent from its development
payload with the registered acquisition, and record which); then (1) the **fixed-prefix assay**: one streamed pass over
the full validation inventory (`selection("v5")`) through the registered batch reader (PC-6's adapter pattern),
scoring all thirteen numerical configurations at once with `Accumulator`, plus one further pass per gate threshold
(0.4, 0.3, 0.2 via `dataclasses.replace(cfg, null_threshold=t)`), writing per-configuration vectors in the 68f layout
and the summary table (mean KL, signed ΔNLL, ES99+, maximum with location, exceedance 0.01 / 0.1 / 1, half-mass,
changed fraction) plus gate-firing telemetry; (2) the **efficacy assay**: for each of the sixteen settings, wrap the
restored memory in `BoundedCap` (or the threshold replacement) and run the installed endpoint functions on the
development stream's items (ES on re-query, RET-ES, RET-GS, LS bounded-text, near-miss, revision) — no new
acquisition; (3) the **selection**: apply the pre-registered rule mechanically and write `selection.json` naming at most
one bound and one comparator with the numbers that chose them; (4) cost ledger and identities (memory, base, reader,
wrapper source hashes). Output under `results/additional_work/AW-B/calibration-<date>/`; CPU smoke on the tiny base;
the exclusive lease and the project-only occupancy guard as in the PC runners; ceiling 8 GPU-hours for calibration.
The final evaluation on the sealed realization-0 streams is a second command (`evaluate`) that takes `selection.json`
and runs the four arms on the five orders; ceiling 16 GPU-hours.

### Lane PC-12 — random-direction and compute-matched credit arms (now first; DEC-075)

Two new arms for `aw/pc_v0.py` at the 12-cell scope, implemented as private variants in `aw/` (the locked
`src/pccap/cap/learn.py` is not edited): (a) `credit=random`: at each credit call draw an isotropic random direction
per site and scale it to the norm the true (adjoint or eight-step error) credit would have had, everything else
identical; (b) `credit=adjoint-matched`: adjoint credit with the per-record step budget raised until its ledger cost
(forwards + reverses) equals the eight-step error credit's nine forwards + nine reverses, the matching rule recorded
in the treatment record. Treatment recorded in every cell's `config.json` / `finish.json` as PC-9 does; the
treatment-aware report labels them. CPU tests on the tiny base (random arm reproduces its seed; matched arm's ledger
equals SE-E's within one call). Capstan runs both on the GPU when delivered; the settling-depth arms run tonight.

### Lane X24-final — rerun the replication audit with `--require-complete` (first, short)

On the complete 60-cell set and the four fixed-v5 cells (extend the checks to the v5 run's `checkpoint-300.json`
bindings, base/reader hashes and identical item order across arms). Output `logs/r1_x24/final/`.

### Lane PC-8 — the PC reports from real data (second)

`docs/additional_work/PC-v0_report.md` from the 60-cell run and its harm readout, and a companion
`docs/additional_work/PC-v1_report.md` for the fixed-v5 four cells and their full-inventory harm readout (use the
staged treatment-aware generator on copies if the live one cannot label the v5 selection correctly, and say so).
Fill the claim-ledger PC rows with measured values and populations; export figures to
`assets/presentation-materials/figures/pc_v0/` and `figures/pc_v1/`; fill `review-data/results.md` from the same
sources (Capstan checks it against items 126–129). State each result whichever way it falls, with the cost columns.

### Lane R-1 — supplemental execution consumer for Option R (fourth; prepared now, run only if Tuesday says so)

AW-R0 sealed the realization-3 populations, matrix (`manifests/additional_work/run_matrix_R_v1.json`) and 30 recipes,
but the frozen primary backend admits only its original cells. Build `aw/r_run.py`: a runner in the shape of
`aw/pc_v1_run.py` that executes an extension recipe with the same sealed-cell logic (construction, stream, checkpoints
at 100 / 300 / 1,000, full validation, fidelity-watch observation), writes start / finish receipts of the queue's
shape under `logs/additional_work/R/queue/`, honours per-cell ceilings from AW-R0 (1.7 factor), two workers, the
memory floor and the October 9 cutoff, and a `plan` output with the schedule (38 process-hours projected). CPU smoke
on the tiny base; no GPU. The lead decides on Tuesday whether it runs.

### Lane PC-11 — patch applied by Capstan 2026-09-28 17:22 (old files under `PC-9-candidate/old/`); remaining for Capex: update `test_pc9`, `test_pc10` and `test_comparator_report` to the applied state and regenerate the PC reports with the treatment-aware generator

Capstan confirms the idle boundary (the GPU is idle now; Option R may run on it, which does not touch these files).
Apply the exact commands in PC-10.md, keep the old versions under `docs/tasks/PC-9-candidate/old/`, rerun the
tests, and regenerate the two PC reports with the treatment-aware generator to show they reproduce the PC-8 numbers.

## Round 51 — variant-aware reporting, replication audit, Tuesday outline (2026-09-27, 11:05)

Ground rules unchanged. PC-8 starts when Capstan posts the completed run and harm-readout paths (this afternoon).

### Lane PC-10 — variant-aware report and readout integration (first)

Capex's PC-9 note: the PC-v0 report generator and the harm readout assume the eight-step treatment. Make both
variant-aware on copies (`aw/pc_v0_report.py`, `aw/pc_harm_readout.py`, `aw/pc_v1_readout.py` are Capex-owned;
`aw/scoring.py` stays untouched): read the treatment record (credit iterations, error rate) from each cell's
`config.json` / `finish.json`, group and label by treatment, refuse to pool cells with different treatments into one
arm, and render a sweep table when several treatments exist. Tests on the round-50 smoke fixtures plus a synthetic
two-treatment fixture. Apply the PC-9 patch and this integration only after the running chain's reports exist;
until then keep them under `docs/tasks/PC-9-candidate/` and state the exact apply command.

### Lane X24 — audit of the PC-v0 replication cells as they complete (second; read-only)

For every finished cell in `results/additional_work/PC-v0/replication-60-20260927/`: the two arms of a pair used
identical items in identical order (item IDs and order from `items.jsonl`), identical calibration and seeds, the same
base hash before and after (`finish.json`), fresh memories (no cross-cell state), the credit rule recorded as planned
(SE-A adjoint, SE-E eight-step error), scoring on the old S5 definitions with the secondary column present, and the
cost ledger consistent with nine forwards / nine reverses per SE-E credit. Report the population's exposure label.
No efficacy numbers are read or reported by this lane; it certifies the pairs before PC-8 reads them. Output
`logs/r1_x24/report.md`, rerun on the complete set at the end.

### Lane REV-3 — `final-experiments.md` skeleton for Tuesday (third)

`assets/presentation-materials/review-data/final-experiments.md` (canonical copy in `docs/presentation/`): the
decision tree of `review-data/README.md` §5 as a form to be filled on Tuesday — for each candidate experiment its
question, design, population and exposure label, cost from the delivered profiles or estimates, the reviewer
feedback deadline, what it would add to which theme, and a blank "decision / owner / start" line. No preferences;
the lead, the human reviewers, Capex and Capstan fill it together.

## Round 50 — contingencies wired, results scaffold, talk timing (2026-09-27, 08:35)

Ground rules unchanged. PC-8 still waits for the run (≈ 14:00) and the harm readout; Capstan posts the paths.

### Lane PC-9 — contingency variants wired but unrun (first)

So that Tuesday's choice (`review-data/README.md` §5) needs no new code: (a) in `aw/pc_v0.py`, a `--credit-iters`
option (8 default; 16, 32 admitted) and an `--error-lr` option for the SE-E arm, passed through to the cap config and
recorded in every cell's `config.json` and `finish.json`; (b) the same two options in `aw/pc_v1_run.py`; (c) a `plan`
output that prints the projected cost of a sweep from the profile records. CPU tests only; the running replication's
source is not edited until it finishes (make the change on a copy or wait for the finish receipt, then apply; Capstan
confirms the finish in the lead queue). No GPU.

### Lane REV-2 — results scaffold and reviewer Q&A (second)

(a) `assets/presentation-materials/review-data/results.md` as a scaffold with the exact tables the PC-8 report and
the harm readouts will fill (rows for PC-v0 per dataset × realization, the fixed-v5 four cells, the paired harm
summaries), each cell marked pending with its source path; Capstan fills it Monday. (b) `docs/presentation/qa.md`:
the twenty questions a predictive-coding or active-inference audience is most likely to ask, each with a two-sentence
answer bound to a claim-ledger row or an explicit "not established" — including the SD-24 history, why the reader is
BP-trained, what "error-optimization PC" is and is not, why three realizations, why the halt at 270, what the tail
figures do and do not show, and the coupled-free-energy status.

### Lane PRES-5 — timed scripts (third; the lead's direction applies)

From the twelve slide drafts, two timed speaking scripts under `docs/presentation/deck_v3/`: 15 minutes and 25
minutes, with the cut lines the outline already names, each slide's speaking time, and the result slots left as
slots. No new claims; wording remains the lead's to review.

## Round 49 — Stage-4 report assembly and receipt audit (2026-09-27, 08:10)

Ground rules unchanged. PC-8 (PC-v0 report from real data) remains open and starts when the 60-cell run and the harm
readout exist (Capstan posts the paths in the lead queue). Two new lanes that need no results:

### Lane R1-D14g — the Stage-4 confirmatory report, assembled (first)

`docs/R1_stage4_report.md`: the registered D.5 report skeleton filled from what exists — the triplet report (135
cells, DEC-069 display), the comparator report on the 270-cell state (matched_update, v0_live C1/C2, S1_LM both
datasets, S1_literal zsRE), the fidelity benchmark and concentration statistics, the DEC-052 inventory of the twelve
unavailable contrasts with reasons (DEC-066, DEC-074b), the watch summary (alerts and creep, none a veto), the
resource accounting from the halt report (process-hours by class; 750-hour cap; two-worker factor history 1.15 →
1.7), and the execution history (freeze, launch, cutovers, halt) in one page. Every number cites its source file and
hash. No new computation; no new label. This is the registered deliverable of the confirmatory study independent of
the talk.

### Lane X23 — receipt-chain audit of cells 136–270 (second)

As X22 did for block 1: every start / finish / decision receipt against the frozen recipes, the sealed payload hashes,
the checkpoint receipts in `results/R1/stage4_sealed_cells/`, the charged process time (no double counting; bindings
v1 for cells ≤ 90, v2 with ratio 1.7 afterwards), the four cells without decision records (disclosed in
`logs/R1/operations/Q21_cutover/halt-reconciliation.md`), and the fidelity-watch observations; a plain integrity
statement or the exact defect. Read-only. Output `logs/r1_x23/report.md` + `docs/tasks/X23.md`.

## Round 48 — result slides, refreshed snapshots, PC report (2026-09-27, 07:00)

PC-7 (fixed-v5 paired credit experiment driver; lane text in round 47's block) stays **first**: it is the critical
path for the second PC result, and the GPU is free for it from ≈ 15:00 today once the v0 replication and its harm
readout are done. Then:

### Lane PRES-4 — result slides 9 and 10 and the closing PC takeaway (second)

Speaker drafts and renderable specs for outline slides 9 (corrected PC-v0: efficacy, harm, cost) and 10 (does PC
credit transfer to the fixed v5 reader), in the PRES-2/3 format, with every number a placeholder bound to the PC-3
report's table names and the PC-5 harm summary keys, so the slides fill themselves when `aw/pc_v0_report.py` and the
readout run; plus the closing slot of slide 12. Label the population (exposed historical S5 for v0; exposed
realization-0 streams for v5) and the measured/proposed line on each.

### Lane HT-15b — per-cell tails on the reconciled 270-cell state (third)

Rerun `aw/tail_cells.py` on the refreshed snapshot (`logs/R1/reports/comparators-270/`, receipted inventory), replace
`figures/tails/tail_spread.md` and `cell_tails.csv`, update the paragraph in `tails_v1.md` (S1_literal zsRE now 15
cells: give its three-realization range), and note what changed against the 262-cell snapshot.

### Lane PC-8 — PC-v0 report on the completed 60-cell run (fourth; when the run finishes ≈ 14:15)

Run `aw/pc_v0_report.py` on `results/additional_work/PC-v0/replication-60-20260927/` and the PC-5 harm output when
Capstan has produced it; verify identities; write `docs/additional_work/PC-v0_report.md` from the real data (the
smoke-based draft is replaced, not edited); fill the claim-ledger PC rows with measured values and their populations;
export the figure to `assets/presentation-materials/figures/pc_v0/`. State the result whichever way it falls.

## Round 47 — remaining slides, fixed-v5 readout adapter, per-cell tails (2026-09-26, 19:10)

Ground rules unchanged. HT-13 is repaired (ES99 is now the fractional expected shortfall in both helpers; collection
uses the receipted inventory; title and reference caveats added); `aw.refresh_after_halt` may publish once the halt
is reconciled. The fixed-v5 credit run is held until Monday 09:00 (lead queue 120).

### Lane PC-7 — fixed-v5 paired credit experiment driver (now first; critical path for the second PC result)

PC-2 delivered the acquisition seam (`PCRevisionCap`, adjoint mode bit-equal to the registered learner; PC-4 proved it on
the saved development checkpoint), but no driver runs the paired experiment. `aw/pc_v1_run.py` (+ `aw/tests/test_pc_v1_run.py`,
`docs/tasks/PC-7.md`): mirror `aw/pc_v0.py`'s shape (plan / profile / run / cell; `--execute`; the narrowed occupancy
guard from `aw/pc_v0.blocking_cuda_processes`, imported not copied; new output directories; cost ledger; per-cell
`finish.json`). Arms: adjoint (registered path) vs corrected eight-step error credit, everything else identical (selected
v5 recipe and theta, original BP base, calibration, gate, seeds, fresh memory per cell). Populations: the exposed
realization-0 zsRE and CounterFact confirmatory streams, 300 edits, order 100 (the same items the block-1 cells used),
labelled post hoc / exposed. Endpoints through the installed outcome functions exactly as R1 defines them (ES, RET-ES,
RET-GS, LS bounded-text, near-miss, revision at 100 and 300); save the checkpoint snapshots at 100 and 300 in the form
`aw/pc_v1_readout.py` (PC-6) restores, so the harm readout runs on them. Profile: 10 items per arm on the development
payloads before the run. CPU smoke on the tiny base; the GPU steps are Capstan's on Sunday evening.

### Lane PRES-3 — speaker drafts for the remaining slides that do not wait for PC results (first)

Slides 1, 4, 5, 7, 8 and 12 of `deck_v3_outline.md`, in the PRES-2 format (one file per slide under
`docs/presentation/deck_v3/`, claim-ledger links, renderable specs; SVG where a diagram is needed). Slide 5 uses the
triplet and 225-cell comparator reports; slide 7 uses the corrected HT-13 figures and table (v1.1); slide 8 the κ
pilot page (`assets/presentation-materials/kappa_pilot_v5.md`); slide 12 leaves the PC takeaway as a visible slot.
The lead reviews wording; nothing is final.

### Lane PC-6 — fixed-v5 harm-readout adapter (second)

The checkpoint / batch-reader adapter PC-5 needs for the fixed-v5 credit run (Capex's handoff: "not a bypass of the
frozen reader's exact-class guard"): restore a `PCRevisionCap` (adjoint or error mode) from a saved supplemental
checkpoint, expose the same base/cap logit pair per position that `aw/pc_harm_readout.py` consumes, and prove on the
saved development checkpoint (PC-4's fixture) that the adjoint-mode adapter reproduces the registered reader's
logits to the bit. CPU tests; the GPU pass is the orchestrator's on Monday.

### Lane HT-15 — per-cell tail statistics with realization spread (third)

Extend `aw.refresh_after_halt` (or a sibling `aw/tail_cells.py`) with a per-cell table: for every receipted cell,
ES99+ (fractional), maximum with location, exceedance at 0.01 / 1 / 5 nats and half-mass count, then per condition ×
dataset the mean over cells with the three realization means and the min–max range, so the pooled HT-13 numbers have
a spread beside them. Import `aw.tail_figures.expected_shortfall`; do not copy it. Output beside the HT-13 table in
`assets/presentation-materials/figures/tails/`, and a paragraph for `tails_v1.md` §"What the pooled tails show"
that Capstan merges.

## Round 46 — harm readout driver, post-halt refresh, explanatory slides (2026-09-26, 11:00)

Ground rules unchanged. Round 45 is delivered and committed (c.f. §1). The orchestrator runs the halt, reconciliation
and the PC-v0 GPU steps tonight, and takes HT-14 below.

### Lane PC-5 — paired harm readout driver for the PC arms (first)

`aw/pc_harm_readout.py` + `aw/tests/test_pc_harm_readout.py`: for a completed PC-v0 run (and later the fixed-v5 credit
run), take each arm's final memory/checkpoint and the preselected ordinary-text validation positions (the legacy S5
drift subset for v0; the full 245,237-position inventory for v5), compute base and cap logits per position once per
arm, and score with `aw.scoring` **unchanged** (import it; do not copy it): the 68f-layout vectors, mean KL, signed
ΔNLL, ES99, maximum with location, exceedance at 0.01 / 0.1 / 1 nat, half-mass concentration, paired SE-E − SE-A per
position. Output under `results/additional_work/PC-v0/harm/`; a table block that `aw/pc_v0_report.py` can include
(same section format as its efficacy table). CPU tests on the smoke outputs; the GPU pass is the orchestrator's, within
the 8-hour readout ceiling. Cost counted separately from the replication.

### Lane R1-D14f — post-halt refresh, prepared now, run Sunday (second)

A single command (or `aw/refresh_after_halt.py`) that, once the orchestrator has reconciled the halted queue and
posted the block-5 boundary report, regenerates: the comparator report on the final 270-cell state
(`docs/R1_stage4_report_comparators.md`, superseding the 225 snapshot and saying what changed), the HT-13 figures
(`python3 -m aw.tail_figures --out /home/derp/cap/assets/presentation-materials/figures/tails`), the claim-ledger v7
rows that depend on comparators, and the DEC-052 inventory of unavailable contrasts (S1_literal CounterFact, the
extension, MQuAKE comparator slots) with DEC-074b as the reason. Dry-run it on the 252-cell state now; leave the
outputs untouched until the halt is reconciled.

### Lane PRES-2 — explanatory slides that do not wait for results (third; the lead's direction applies)

Draft the full speaker text and diagram specifications for outline slides 2, 3, 6 and 11 (active inference → testbed;
what predictive coding contributes, with the corrected energy, the eight-step credit and SD-24 in one figure; why look
past the mean, using the HT-13 survival figure; returning to active inference), under `docs/presentation/deck_v3/`
(one file per slide, plus diagram specs as SVG or a description Capex's `presentation_prepare.py` can render). Keep
measured / proposed labels visible; every assertion maps to a claim-ledger row. The lead reviews the text; nothing
here is final wording.

### Lane HT-14 — abstract-to-testbed map (orchestrator's lane)

`docs/presentation/abstract_to_testbed.md`: for each idea in the July abstract (frozen prior, residual agent, two
κ-porous interfaces, coupled free energy, expected-free-energy policy choice, pragmatic/epistemic value,
uncertainty-directed audits, coupling–boundary–interference conjecture, learning from failure) and each satellite
objective: implemented (where, in which decision), measured (which result, which population), or proposed (what it
would take). Checked against `decisions.md`. Claude writes it; Capex cites it from slides 2 and 11.

## Round 45 — plug-in analysis and presentation preparation, Codex lanes (2026-09-26)

Ground rules unchanged (CPU only; nothing under `scripts/` or `src/pccap/`; Codex-owned files only; the orchestrator
owns operations, `aw/bounded.py`, `aw/wrapper.py`, `aw/scoring.py`, `docs/additional_work/PC-v0.md`). Everything below
is built and tested now so that tonight's and next week's results drop into finished tables and slides.

### Lane HT-13 — distributional harm figures for the deck (orchestrator's lane)

`aw/tail_figures.py` (Claude): from the saved per-position full-validation vectors of every completed cell, per
condition × dataset: survival curves P(ΔNLL > x) on log axes, exceedance at 0.01 / 0.1 / 1 / 2 / 5 nats, maxima, ES99,
half-mass concentration; a rarity-versus-severity figure (fraction of positions changed vs maximum) placing the
learned cap beside every comparator. Output `assets/presentation-materials/figures/tails/` + `tails_v1.md` with the
data table; read-only on results; reruns after the halt to include the S1 cells. Capex cites the figure paths from
the deck.

### Lane PC-3 — PC-v0 comparison report generator (first)

`aw/pc_v0_report.py` + `aw/tests/test_pc_v0_report.py`: reads one or more `results/additional_work/PC-v0/<run>/`
directories produced by `aw.pc_v0 run` (Codex knows the format), verifies identities (config, source, model, data
hashes; `finish.json` complete/partial), and writes `docs/additional_work/PC-v0_report.md` + `logs/additional_work/PC-v0/report/`:
the paired SE-E − SE-A table per dataset × realization (ES, RET-ES, RET-GS, LS; the secondary bounded-text score in
its own column), the mean difference with the three realization values and the min–max range (no interval treats
tokens as replicates), the historical defective-energy row as reference, the cost table (process time, forwards,
reverses per credit) and the 1/8/32 diagnostic table. Include a figure (efficacy vs cost, both arms; realizations as
points) written to `assets/presentation-materials/figures/pc_v0/`. Test on the runner's CPU smoke output so the
generator is proven before real results exist. Partial runs render with the missing cells marked, never dropped.

### Lane PC-4 — PC-2 parity on a saved development checkpoint (second)

Before Tuesday's GPU run: on CPU, load a saved v5 development checkpoint (as AW-L0 did for its 64-prefix
reconstruction) with the real GPT-2 base, run `PCRevisionCap` in adjoint mode against `RevisionCap` on a handful of
development prefixes and one short acquisition, and show bit-equality of predictions, memory state and cost counters;
then run PC mode once on the same items to confirm it executes end to end on the real base (no claim about quality).
Record timings so the GPU profile has a CPU reference. Files: `aw/tests/test_pc_v1_devcheckpoint.py` (skipped when
the checkpoint is absent), `docs/tasks/PC-4.md`.

### Lane R1-D14e — comparator report generator (third; runs now on block 4, reruns after the halt)

`aw/comparator_report.py`: the registered comparator tables (matched_update, v0_live C1/C2 — complete; S1_LM both
datasets and S1_literal zsRE — after the halt), same endpoints and display rules as the triplet report, the fidelity
benchmark and concentration columns, the DEC-052 inventory listing every unavailable contrast (S1_literal CounterFact,
the extension, MQuAKE comparator slots) with its reason (DEC-074b), and a figure per dataset placing every condition on
retention-versus-harm axes. Output `docs/R1_stage4_report_comparators.md`; read-only on results. Run it on the current
225-cell state now; rerun on Sunday and mark what changed.

### Lane PRES-1 — deck v3 skeleton, figure pipeline and claim ledger v7 (fourth; the lead will add direction)

Under `assets/presentation-materials/deck_v3/`: an outline that reflects DEC-054's framing (small mean drift hides
concentrated local harm), the completed triplet, the comparators, the fidelity/concentration results, the corrected
PC results (slots), the "what it is not" section (DEC-054, Matthew Ikle's review), and the resource story; each slide
lists its figure/table source file and which report fills it. A `figures/pipeline.md` mapping every figure to the
generator command that produces it. A claim ledger v7 (`docs/talk_claim_ledger_v7.md`) with columns measured result /
population / control / supports / does not support, seeded from the triplet report and the block-4 comparators, with
empty rows for PC-v0 and the fixed-v5 credit test. **The lead's direction for this lane goes in the subsection below
and overrides the defaults above.**

#### Lead's direction for PRES-1

**2026-09-26 — direct instruction from charlie, recorded by Capex for both agents.** The presentation must focus
on **active inference, predictive coding, and heavy-tailed distributions**, under the day's heading
**“Active Inference in the Extremes.”** All three are central to the narrative. Connect the actual experiments
to the submitted abstract and the satellite's scientific questions, distinguishing implemented mechanisms,
measured results and proposed active-inference/coupled-free-energy extensions. Concentrated harm remains a key
finding within this three-part framing. Earlier outline priorities do not override this direction.

Read the shared [presentation brief](presentation/presentation_brief_2026-09-26.md) before continuing PRES-1.
The July abstract (including its diagram) and the saved satellite page were found and read in
`/home/derp/cap/errata/presentation_details/`; no refresh is needed. The captured full session title is
*Thriving in the Extremes: Active Inference in Non-equilibrium Systems*. Keep it alongside charlie's heading.
Experimental completion remains October 9 at 17:00 ET, with presentation October 15; individual speaking
duration is not established by the saved material. This direction changes presentation emphasis, not the
registered experiments, queue operations or budgets.

## Round 44 — PC refocus (DEC-074a), Codex lanes (2026-09-24)

Same ground rules as round 43 (CPU only; nothing under `scripts/` or `src/pccap/`; Codex-owned files only; the
orchestrator owns `aw/bounded.py`, `aw/wrapper.py`, `aw/scoring.py`, the S1 caveat execution, drains/resumes, and
`docs/additional_work/PC-v0.md`). Specification of record: `docs/additional_work_pc_refocus.md` §§2–5 with
`_review.md` §3 sequencing and `_response.md`; decisions DEC-074/074a.

### Lane PC-1 — v0 corrected-credit runner and the actual-solver regression (delivered 2026-09-25, e5b7446; GPU steps are the orchestrator's after the halt)

`aw/pc_v0.py`: a small runner that builds the original v0 C1 cap on the regenerated ePC checkpoint
(`EPCBase.from_npz` on `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz`, SHA-256 `ea4c561d…`; never
the default constructor), with `credit="adjoint"` (SE-A) or `credit="error"`, `credit_iters=8`, error lr 0.1 (SE-E,
corrected energy), fresh empty memory per arm, the archived S5 v2 calibration and stream-selection rules, old S5
scoring (ES, RET-ES, RET-GS, LS) plus the bounded-text score as a separate secondary column, cost counters (nine
forwards + nine reverses per eight-step credit), new output directories under `results/additional_work/PC-v0/`.
Tests in `aw/tests/test_pc_v0.py` against the **real solver** on the tiny base: with nonzero writes, the one-step site
error from zero error equals −0.1 × adjoint within tolerance (the check that catches SD-24); zero-error forward
identity; unchanged base weights; independent empty memories; target clamped only for the taught support answer.
Deliver also the 1/8/32-iteration diagnostic (energy, gradient residual, cosine, norm) on a fixed development prefix
sample, and a timing-profile command for the 12-cell scope (two credit rules × zsRE, CounterFact × realizations 0–2 ×
one preselected order; 1,000 / 300 edits). No GPU: the profile runs after release under the orchestrator.

### Lane PC-2 — fixed-v5 acquisition-credit seam (delivered 2026-09-25, e5b7446; real-base parity and profile after the halt)

`aw/pc_v1_acquire.py`: an isolated variant of `revision_v1/adapt.py`'s delta acquisition that replaces the adjoint
direction by the corrected eight-step error credit while keeping the real feedforward loss for acceptance,
initialisation, bounds, stopping and cost accounting (no hard-coded one-reverse cost); adjoint mode must reproduce
the v5 path to the bit on the tiny base (cf. `aw/tests/test_wrapper.py` for the pattern). Populations: the exposed
realization-0 zsRE/CounterFact streams, 300 edits, one order, paired arms. Tests in `aw/tests/test_pc_v1_acquire.py`.

### Lane R1-D14d — triplet confirmatory analysis (delivered 2026-09-25; `docs/R1_stage4_report_triplet.md`)

### Lane R1-D14d — triplet confirmatory analysis on complete data (see round 44)

Blocks 1–3 are complete: `R1_learned_ff`, `R1_nonlearned`, `v0_stable` × zsRE, CounterFact, MQuAKE × realizations
0–2 × five orders (135 cells). Run the registered D.5 analysis exactly as frozen (R1-49g / R1-75 / the D14 skeleton)
on those cells: the primary contrasts with the registered DEC-057/058 computations and classifier labels kept as
preliminary decision summaries, the DEC-069 t-interval (2 d.f.) secondary display beside the min–max bootstrap, every
realization visible, the cap-fidelity benchmark and concentration statistics per cell, the DEC-052 inventory, the
watch summary, and the comparator slots marked unavailable until blocks 4–5 finish. Read-only on the run and on the
sealed cells; no re-scoring. Output `logs/R1/reports/triplet/` + `docs/R1_stage4_report_triplet.md`, figures worth a
slide to `assets/presentation-materials/figures/triplet/`. Supersedes the block-1 partial report's tables where the
triplet is complete; say what changed between r0-only and r0–r2.

### Lane AW-R0 — portfolio allocation check and the Option R extension matrix (first)

Under DEC-073 the certified fresh subjects go to Option R: one additional untouched realization (index 3) of the
primary triplet (`R1_learned_ff`, `R1_nonlearned`, `v0_stable`) on zsRE and CounterFact, five orders each = 30 cells,
1,000 edits, the selected artifact unchanged (no reader retraining). Deliver: (1) the allocation check with the real
population constructor and the frozen exclusions — subject-disjointness from realizations 0–2 and from every training,
selection and development identity, template-family feasibility, all endpoint roles (outside, near-support,
near-neighbour, revision, locality per DEC-070, question-null family per DEC-061/062) — with a plain yes/no per dataset
and the remaining margin after allocation; (2) if yes, the sealed realization-3 populations and payloads under
`assets/runs/pc_cap/R1/additional_work/R/` and an extension matrix `manifests/additional_work/run_matrix_R_v1.json`
built with the existing builders (recipes identity-bound as in R1, new receipt root `logs/additional_work/R/`,
`block_number` 6, ceilings from the per-condition means of the finished R1 cells under the 1.7 factor), plus the
cell recipes under `docs/tasks/AW-R-cell-recipes/`; (3) a one-page note on what the extension can and cannot say
(reported beside DEC-069, never inside it). No launch, no GPU. Files: `docs/tasks/AW-R0*.md`, the manifests above,
`aw/r_extension.py` if code is needed.

### Lane AW-L0 / AW-L1 — identity audit and cheap tap screen (second)

L0: inspect the frozen constructor and the saved v5 reader metadata; record tap indices (banks after blocks 4, 8, 12;
bank 3 pre-`ln_f`), pre/post-normalisation convention, write sites, the acquisition rule and the active `single_site`
value; verify all-site reconstruction of a saved development checkpoint (prediction agreement on 64 development
prefixes). L1: on cached development observations (existing caches only; no new cache build), per-tap norm/variance
and retrieval/null discrimination for read sets {1,2,3}, {2,3}, {3}, {2}, identical small probes split by
subject/template family, the lexical-only feature as a diagnostic control; paired retrieval/false-fire tables with the
explicit caveat that probe quality is not editing quality. Files: `docs/tasks/AW-L0.md`, `docs/tasks/AW-L1.md`,
`aw/tap_screen.py`, `aw/tests/test_tap_screen.py`, results under `results/additional_work/L1/`.

### Lane AW-L3 — explicit read/write sets (third)

`aw/interface.py`: a supplemental learner configuration with explicit `read_taps` and `write_sites` such that
acquisition (`adapt.py`'s delta routine), the fallback controller writes, stored deltas, deployment and memory
accounting all obey one mask — masked before gradient normalisation, updates and projection; inactive sites exactly
zero throughout; the aggregate write allowance and the five-step acquisition budget unchanged for every write set (no
budget multiplication when sites are removed); query/JIT caches cleared on identity change. Subclass or wrap, never
edit, the locked modules. Tests in `aw/tests/test_interface.py` on the tiny base: inactive writes are exactly zero in
acquisition and deployment; `{1,2,3}`/`{1,2,3}` reproduces `RevisionCap` to the bit (logits and cost counters,
cf. `aw/tests/test_wrapper.py`); dropping a read tap removes the corresponding projection parameters and the count is
reported. Files: `aw/interface.py`, `aw/tests/test_interface.py`, `docs/tasks/AW-L3.md`.

### Lane AW-L-prereg — AW-L pre-registration draft (fourth)

`docs/additional_work/AW-L.md`, one page: hypothesis, the 2×2 arms (read {1,2,3},{2,3} × write {1,2,3},{3}), three
paired reader-training seeds, zsRE and CounterFact, 300 edits, one order, the sealed realization-0 confirmatory
streams as the evaluation population (DEC-073, labelled post hoc/exposed), endpoints (ES, RET-ES, RET-GS, LS,
near-miss, revision at 100 and 300; full ordinary-text fidelity at 300 with the tail statistics of the final plan),
the descriptive 0.02 tolerance rule, resource accounting (training, acquisition, corrected-pass cost per fired query,
observation pass), the L4 pilot gate and the 48-hour ceiling. Draft for the lead's review; the orchestrator writes
`AW-B.md` and `R.md`.

### Lane R1-D14c — first partial confirmatory report from block 1 (done, 2026-09-20; `docs/R1_stage4_report_block1_partial.md`)

Run the D.5 analysis (`r1_49g_analyze` / R1-75 / the D14 report) on the 45 completed block-1 cells (the triplet on
realization 0, three datasets): every table and figure the skeleton promises, filled where data exist and marked
unavailable where not (no classifier labels without three realizations; the primary contrasts as realization-0
estimates with order dispersion only; fidelity benchmarks and concentration statistics per cell; the DEC-052
inventory; the watch summary). Output under `logs/R1/reports/block1/` + `docs/R1_stage4_report_block1_partial.md`; a copy
of any figure worth a slide to `assets/presentation-materials/figures/block1/`. Read-only on the run.

### Lane HT-4f — claim ledger v6 (done, 2026-09-20: v6 was already published against the v8 cost; a session-v10 supplement was delivered instead, `docs/talk_claim_ledger_v6_session_v10.md`)

### Lane X22 — block-1 receipt-chain audit (done, 2026-09-20: PASS, all 45 cells; 46.805 h charged, matching the D11 block-1 report)

Every finish / decision / receipt under `logs/R1/final_queue/` for the 45 cells against the frozen recipes, the sealed
payload hashes, the checkpoint receipts in `results/R1/stage4_sealed_cells/`, the charged process time (no double
counting) and the fidelity-watch observations; a plain integrity statement or the exact defect. Read-only.

### Lane R1-77g — post-freeze ceilings amendment (delivered; Q21 answered A, DEC-072; the orchestrator is executing the drain-and-resume at the block-2 boundary — no Codex action)


- **2026-09-26 (assets):** sealed-cell learner snapshots (`*.snapshot`, ≈ 100 MB per cell, 27 GB in total) are no longer tracked in the assets repo: the unpushed commits were rewritten without them (backup ref `backup/master-before-snapshot-prune`), `*.snapshot` is ignored, the files stay on disk, and their SHA-256 values remain in the checkpoint receipts and `.snapshot.json` sidecars. GitHub refuses packs over 2 GiB; the remaining unpushed volume is 67 MB.
## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
