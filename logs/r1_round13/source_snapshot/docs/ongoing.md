# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-15 18:05 EDT (round 12 committed; DEC-048; round 13 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-15-1800.md`. Rules §1 are
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

## 2. Orchestrator lane (do not touch)

v0 close-out (tonight) → R1-01/02/03 diagnostics (GPU, ≈ 2 h) → `docs/R1_diagnosis.md` → Stage 1 core modules
(`revision_v1/{contracts,observations,memory,reader,controller,adapt,evaluate}.py`) with the gates → Stage 2 reference and
surrogates → Stage 4 runs and the revision freeze support. Owned: `src/pccap/revision_v1/` except the files named in §3,
`results/R1/`, `manifests/revision_v1/`, the registers, `docs/lead_queue.md`.

## 3. Lanes for Codex — round 13 (CPU; open now)

Round 12 is committed (`cee3d79`) and mirrored. The lead chose **option C** for the MQuAKE population (DEC-048): a
true-fact locality/unrelated presentation is not exposure for a later counterfactual edit; the full 360-cell scope
stands. Rules as before (new files only; CPU; no draw/seal/base).

### Lane R1-D1h — exclusion register policy v5 (DEC-048)

In the style of R1-D1f/R1-D1g: `manifests/revision_v1/exclusions_frozen_v5.json` (+ script + tests) that applies
DEC-048 to MQuAKE — waive the query-role exposure reasons (locality / unrelated / near-miss candidate presentations of
TRUE facts) while retaining primary training and development items, drawn/sealed items, conflicts, the zsRE-overlap
rule, context quarantine and every cross-dataset reason. Bind the R1-D4b slices (v3 pools) and the R1-X9 audit as the
evidence of what was presented. Report the capacity table per dataset (items and distinct subjects), the demand
(3 × (1,000 + 350)), the headroom, and what the pending alias/context clearance could remove (upper bound), with an
explicit abort rule for R1-58 if usable capacity < demand. No draw.

### Lane R1-49d — protocol draft v4 (DEC-048 declared; profile placeholders)

`docs/R1_stage4_protocol_draft_v4.md`: v3 plus (1) the DEC-048 reading stated in the exposure/population section as a
declared rule with its rationale and the reviewer objection acknowledged; (2) the MQuAKE population under v5 with the
abort rule; (3) the final primary condition slot left open between v4 and the fixed-locality/question-null
candidates the orchestrator is evaluating (state the selection criterion the orchestrator will apply: one rule for
three datasets, chosen on development streams by mean RET-GS subject to zsRE unseen false fires ≤ 10 % at 100
records and LS ≥ 0.98, before any draw); (4) the driver-profile placeholders to be filled from
`results/R1/stage4_dev_cells/R1_learned_ff-zsre-development_profile-*/`.

### Lane R1-67 — development loader and trace repairs (R1-X10 ER-01 / ER-02 as new modules)

Write `src/pccap/revision_v1/dev_loader.py` (+ tests): a pure development-only loader for `--dev-manifest`
overrides that validates mode/dataset, positive count ≤ available, unique identities, token/digest/source bindings
and the unrelated inventory, and returns the ordered selected ids and a manifest sha for the run receipt — the
orchestrator wires it into `scripts/r1_13_stream_eval.py`. And `src/pccap/revision_v1/selection_trace.py` (+ tests):
a helper that renders a `Selection` into the endpoint trace with `hard_null`, selected record id and weight, best
score, null mass and the rare-gate verdict, preserving the old fields — the orchestrator wires it into
`endpoints.py`'s `_read`. TinyBase tests for both, including the refusal cases ER-01 lists.

### Lane R1-X11 — counter-review of R1-65/R1-66 and the primary-condition selection

Review `stream_train._locality_choices` (R1-65: locality nulls equal to an in-memory own prompt are excluded) and the
question-form out-of-memory nulls (R1-66, `out_paraphrase_nulls` / `out_paraphrase_null_prob`) against the episode
builder and the result files (`tri4*`, `tri5*`, `tri6*` when present): is the collision rate claim (≈ 13 % of
locality nulls under self-contained pools) right; does R1-66 change the class balance of L2; is the selection
criterion in R1-49d (3) applied to the right populations; and is the reported trade-off (zsRE unseen 30 % → 5 % vs
paraphrase retention 0.98 → 0.91 and 0.79 → 0.55 at full rate) correctly denominated. Output `logs/review_r1_65_66.md`
with edit requests.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
