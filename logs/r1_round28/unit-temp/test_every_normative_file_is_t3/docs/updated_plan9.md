# Updated plan 9 — the revision-v1 programme (after the v0 close-out)

Written 2026-09-13 ≈ 17:15 EDT by the orchestrator from the three documents in `docs/more_input/` (the results overview,
the joint redesign proposal and the coding-agent guide, all dated 13 September and pinned to commit `170fad3`), reconciled
with the repository as it stands now (commits through `SD-23`; v3 grammar rerun at 49/60). Plans 2–8 governed v0 and are
closed by tonight's close-out; this plan governs what follows. Nothing here reopens a v0 number: the v0 report, frozen
manifests, sealed data and results are preserved unchanged (guide §"Starting evidence and scope").

## 0. Reconciliation of the three documents with the repository

| document statement | repository state now | consequence for this plan |
| --- | --- | --- |
| Reviewed snapshot `170fad3` | 40 commits later: v3 grammar rerun (DEC-029/030/032), drift supplement (X2-05), X2 corrections applied, DEC-031 source register | the v0 baseline for revision v1 is the close-out commit of tonight, not `170fad3`; its results are the same numbers plus the grammar v3 row and the drift supplement |
| "C1 is single-bank" is a documentation error (overview p.3) | confirmed: `ARM_BANKS` gives C1 banks (1, 2, 3) with a fixed schedule; only C0 is single-bank | corrected in `docs/report.md` and `results/S5/report.md` (SD-23) |
| Reference quantities to reconstruct (guide p.2): zsRE C1/SE-A/SE-E ES 0.998467 / 0.998533 / 0.662333, RET-ES 0.523667 / 0.522067 / 0.366133, RET-GS 0.139467 / 0.137467 / 0.156333, learning s/run 272.793 / 267.558 / 816.588 | these are the saved run means under `frozen-confirmatory-v2-84126123` | R1-00 reproduces them from the records as its first gate |
| "The old sealed examples have been inspected; treat them as historical, not a fresh confirmatory test" (guide p.8) | true: the v0 analyses opened every sealed realization | a fresh held-out draw is required for the revision's confirmatory streams (§3, DATA-R1); the remainder of the eligible pools is 1,420 zsRE and 17,091 CounterFact items, so zsRE cannot supply 3 × 1,000 fresh items — decision D-R2 |
| Drift assay: "evaluate the declared split or freeze and disclose a subsample" (guide p.8) | the full-split supplement exists (`results/S4/drift_supplement.md`, 13 min per checkpoint) | the revision freezes a disclosed subsample of the validation split (e.g. 16,384 positions) for per-run assays and scores the full split at endpoints only |
| Grammar keys separate paraphrases from unrelated inputs poorly (overview p.4; S8-02 (c)) | measured | Stage 0's D2 diagnostic (stable observations) and Stage 1's learned reader are the direct response |
| GRACE did not qualify (overview p.4) | DEC-020/SD-21; localization in `logs/grace_gradient_localization.md` | B4 stays out; a learned-cap comparison to SERAC/RECIPE-style baselines is *not* in scope unless the lead adds it (D-R6) |

## 1. Objective and the questions (from the proposal and guide)

Build a cap with a learned reader (applicability with an explicit null), a context-dependent correction network writing
at the three taps jointly, bounded episodic memory with support-only fast updates; train base and cap on short
continual-learning episodes; make the ePC comparison executable as named surrogate conditions; add a cap-local
predictive-coding energy last. Four questions, each a controlled comparison holding everything else fixed:

1. current cap vs stronger cap (base and fast rule fixed) — do retrieval and conditional corrections help?
2. current base vs episodically trained base (cap and training budget fixed) — does the base support learning better?
3. alternating BP surrogate vs alternating ePC surrogate (same schedule, data, mask) — does the base-update rule add value?
4. feedforward cap vs settled cap (same base, cap family, memory, episodes) — does cap-local inference earn its cost?

Plus the 2 × 2 (base × cap) table with each cap retrained under equal budgets, the original BP base with the stronger cap,
and a BP-trained counterpart of the strongest revised system with comparable data and compute.

## 2. Stages, deliverables, gates (guide §0–§4), owners and costs

Task IDs are `R1-<stage><seq>`; every task gets a `docs/tasks/R1-….md` record and a board row; each stage ends with a
Codex counter-review before the next starts (the v0 practice that caught the defects). Owners: **O** = orchestrator (core
modules, GPU runs, integration, freeze support), **C** = Codex (data/episode generation and audits, controls, counter-reviews,
diagnostics scripts), **L** = lead (decisions, freezes, T4).

### Stage 0 — baseline audit and failure diagnosis (days 1–3; GPU ≈ 2 h)

| task | deliverable | exit | owner |
| --- | --- | --- | --- |
| R1-00 | `manifests/revision_v1/baseline.json`: commit, dirty diff, versions, hashes, seeds; the reference table reproduced from the saved records to six decimals | table equals the guide's numbers | C |
| R1-01 D0 | current read path traced on 100 development edits (zsRE, C1 and C2): retrieval recall, irrelevant firings, acquisition, paraphrase answers, which record and answer-prefix entry fires at each site | `results/R1/D0.json` + memo | O |
| R1-02 D1 | oracle selection: force the correct stored entry (diagnostic evaluator only, edit identity as input); teacher-forced target-token loss separately from free generation | upper-bound diagnostic labelled as such | O |
| R1-03 D2 | stable observations: every key from a cap-disabled pass vs the sequential edited-key read, identical examples, extra pass charged | separates key drift from the rest | O |
| R1-04 | diagnosis memo: missing retrieval / inappropriate retrieval / ineffective corrections / capacity eviction, with the S8-02 no-pressure gap and the grammar key-distance finding folded in | `docs/R1_diagnosis.md`; counter-review by C | O, C |

### Stage 1 — the stronger feedforward cap (days 3–10; GPU ≈ 4 h development)

New package `src/pccap/revision_v1/` behind adapters to `pccap.contracts` (v0 contracts untouched): `contracts.py`,
`observations.py` (one unedited base pass; taps at blocks 3/7/11; causal prompt masks; encoder versioning), `memory.py`
(bounded records, retrieval, revisions, serialization, index rebuild, accounting), `reader.py` (query = MLP over the tap's
last-position activation and a masked question-span summary, width 256; up to four candidates, deterministic ties;
applicability score with an explicit null; threshold calibrated on near-misses and unrelated examples), `controller.py`
(query + weighted value code → three 768-d writes jointly, every write × non-null mass, exact zero on the hard null; aggregate
bound Σ‖w_m‖/b_m ≤ A with A = 0.3 for the controlled comparison), `adapt.py` (support-only fast updates of the fact code:
1/3/5 steps, lr screen 1e-3/1e-2, accepted-step check, rollback on non-finite, norm bound), `evaluate.py` (paired streams,
phase costs, traces). Capacity: ≤ 5 M trainable cap parameters; persistent-state ceiling 64 MiB counted in full; optimizer
and replay reported separately; a matched-total-memory comparison or cost frontier against v0's 36.75 MiB.

Gates (all must pass before any training run): no hidden target access (change held-out labels → predictions and state
hashes unchanged; strict support/query API separation); frozen evaluation components (base and reusable weights hashed
before/after a stream); memory round-trip and key-version checks; causality and exact cap-off writes on the null branch;
resource reconciliation with warm-up separated; the planted-fact behavioural sanity check. Tests under `tests/revision_v1/`.
Profile 10 edits before any stream. Development streams: 100–300 edits, three seeds, two orders.

### Stage 2 — episodic co-training (days 8–18; GPU ≈ 8 h development)

| task | deliverable | owner |
| --- | --- | --- |
| R1-20 episodes | generator: support history of 2–8 facts, one new edit, ≥ 2 unseen paraphrases, a near-miss, an old-fact query, an unrelated example; two-fact composition only where unambiguous; synthetic domain first (an extension of the grammar generator with explicit latent scope), then the development editing pools; partition by fact/entity and paraphrase family; split/entity/family ids and seeds explicit; query labels only in training/evaluation containers | C |
| R1-21 reference | the differentiable BP reference: L = a·L_fidelity + b·L_new + c·L_old + d·L_scope + e·L_retrieval + f·L_write, each normalized by its own count and logged unweighted; gradients through a short fixed fast-code unroll with retrieval fixed inside the segment; finite-difference check on a tiny smooth fixture; cap trained with the base fixed first, then a declared subset of base parameters near the taps | O |
| R1-22 surrogates | the alternating BP surrogate and the alternating ePC surrogate (same schedule, examples, mask, losses); the ePC base phase extends the declared energy with the query cross-entropy or teacher-KL term, optimizes error variables with weights fixed, then local block updates by the existing weight-phase convention (float32 ordering preserved); logs terminal energy, gradient residual, iterations, forward/reverse calls | O |
| R1-23 audits | data-separation and update-path audits (which parameters changed under which optimizer; which labels were visible at each stage; exact vs surrogate objective) | C |

Exit: a reproducible change in held-out editability with fidelity retained (teacher KL ≤ 1e-3 nats/token; ordinary-text loss
increase ≤ 0.01 on the declared held-out set), or a clean negative. The alternating ePC surrogate is compared with the BP
surrogate before anything is compared with the differentiable reference; it is never described as a meta-gradient method.

### Stage 3 — cap-level predictive coding (days 15–22; optional; GPU ≈ 3 h)

`pc_cap.py`: E = ½‖z₁ − f₁(q, r)‖² + ½‖z₂ − f₂(z₁)‖² + ½λ Σ_m ‖g_m(z₂) − o_m‖², states of width 256 initialized at the
feedforward values, refined for 0/1/4/8 steps with observations, candidates and parameters frozen inside the solve; no
target term at prediction time; the same gated decoder. Controls: target-free invariance, finite energy/gradients, terminal
residuals, deterministic replay, null-memory zero writes, sensitivity to the relevant memory, behaviour after a misleading
memory is removed, a quadratic toy with a known optimum first; assert no full-base forward/reverse inside the latent loop.
Comparators: the same cap at 0 steps, a feedforward cap of comparable parameters, a recurrent controller of comparable
compute.

### Stage 4 — comparative evidence (days 20–28; GPU ≈ 15 h confirmatory)

Freeze a revision protocol (`manifests/frozen_revision_v1.json`, the lead's act) after development: the four comparisons of
§1, the 2 × 2 table, the BP-trained counterpart, the switches (ePC surrogate, settling steps); endpoints = immediate
full-answer ES, unconditional RET-ES and RET-GS after the whole stream, survival-conditional as a diagnostic, near-miss
locality, older revised facts, explicit revision cases, controlled two-fact composition with the supporting memories
identified; the proposed margins (RET-GS ≥ +0.05 over the stronger-cap BP reference with the paired interval above zero;
ES loss ≤ 0.02; LS loss ≤ 0.01) frozen only after development (D-R3); paired by item and order, clustered by realization
with orders together, intervals labelled preliminary at three clusters; 1,000-edit streams on the fresh held-out draw
(DATA-R1) plus the composition task; the same queue/lease/identity machinery as v0 (`pccap queue`, frozen-identity
checks, versioned manifests). Report: measured findings separated from hypotheses; which parameters changed under which
optimizer; which labels were available where; exact vs surrogate objectives; base frozen during evaluation; abandoned
conditions and failed runs; the v0 report preserved.

## 3. Data (DATA-R1) — decision needed

The v0 sealed realizations are historical. Fresh confirmatory streams need items disjoint by subject from every v0
development, sealed and S7 item. Available without new sources: zsRE 1,420 eligible items outside the sealed
realizations (enough for one 1,000-item realization, not three), CounterFact 17,091 (enough for three of 1,000). Options:
(a) zsRE confirmatory at 3 × 300 fresh items + CounterFact 3 × 1,000, with the v0 sealed streams reported as historical
comparison; (b) add the zsRE MEND train split (163k records; already used only for S7 pairs, whose subjects would be
excluded) as a new source, run through the E.2 teacher filter, to reach 3 × 1,000; (c) both. Recommendation: (b) — it keeps
the 1,000-edit endpoint the guide asks for. Grammar: new seed blocks (≥ 6,000,000) with full paraphrase coverage
verified before sealing (SD-22 lesson), plus the composition task from the extended generator.

## 4. Budget, calendar, roles

- Development envelope 20 accelerator-hours across the first selected configurations, 2-hour per-run ceiling, checkpointed
  stops; ceilings frozen from the measured 10-edit and short-outer-batch profiles before launch (guide p.9). Confirmatory
  ≈ 15 h (2 × 2 × 3 seeds × 2 orders × 1,000 edits with the extra unedited pass ≈ 2× v0's per-edit cost, plus the
  co-training runs, counted once and not amortized away). Total ≈ 40 accelerator-hours ≈ 4–6 days of wall clock on this host.
- Calendar: four weeks, gated as above; Stage 3 is skipped if Stage 1–2 do not produce a working feedforward cap.
- Concurrency: Codex and the orchestrator work in one checkout as in v0 (lanes in `docs/ongoing.md`; new files first; the
  post-freeze source rule applies from the revision freeze). Every stage gate has a Codex counter-review with a written
  response; the lead's decisions are recorded as DEC entries.
- What depends on results (guide p.10 table): oracle helps but learned retrieval does not → keys and null training;
  oracle still poor → fact representation and conditional writes; new acquisition but old failures → collisions, replay,
  stable keys before more storage; equal gains on BP and ePC → a cap/objective result, not a PC result; BP surrogate works
  but ePC does not → residuals, scaling, update signs; settling lowers energy without helping answers → reconsider the
  energy; only joint co-training helps → repeat across seeds and tasks before claiming general editability.

## 5. Decisions requested from the lead before Stage 1 starts

| # | decision | default if silent |
| --- | --- | --- |
| D-R1 | Accept this plan as the revision-v1 contract (with the guide as the specification) | accepted |
| D-R2 | DATA-R1 source for fresh zsRE confirmatory streams: (a) 3 × 300 from the remainder, (b) MEND train through the E.2 filter to 3 × 1,000, (c) both | (b) |
| D-R3 | Proposed confirmatory margins (RET-GS +0.05, ES −0.02, LS −0.01) and fidelity bounds (KL ≤ 1e-3, loss increase ≤ 0.01) to be frozen after development | as proposed |
| D-R4 | Budget: 20 h development + ≈ 15 h confirmatory + co-training (≈ 40 h total) | as proposed |
| D-R5 | Stage 3 (cap-level PC) is conditional on a working Stage 1–2 cap | conditional |
| D-R6 | External learned-memory baselines (SERAC/RECIPE-style) in the 2 × 2 comparison: out of scope this cycle | out of scope |
| D-R7 | Who freezes the revision protocol and when: the lead, after the Stage 2 counter-review | the lead |

## 6. Tonight's close-out remains unchanged

The v3 grammar rerun finishes ≈ 17:55 EDT; the post-queue chain runs; the report, D3 memo and records get the
confirmatory-grade grammar row; Codex's dry-run harness fix and the analysis-tree re-apply are committed; the lead's T4
review closes v0. Stage 0 of this plan can begin the moment the close-out is committed.

changed