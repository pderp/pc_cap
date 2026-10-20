# Feedback on Capstan's post-conference proposal

**Reviewer:** Omega agent (derp)
**Date:** 20 October 2026
**Subject:** Review of `post_conference_capstan_proposal.md`, in response to Charlie Derr's request for feedback

---

## 1. Overall Assessment

Capstan's proposal is a sharp, well-argued narrowing of Capex's plan. Its strongest contribution is identifying three analyses that cost almost nothing and could change the interpretation of everything we have done: the risk–coverage curve comparison, the in-context retrieval arm, and the recognition that the existing "PC" was a global error-state solver, not local PC. The proposal is correct that Phase 0 should come before any training, and correct that the shared artefact should be a cached-feature small-reader harness rather than another through-GPT-2 run.

**Recommendation: adopt Capstan's Phase 0 and Phase 1 as the primary sequence, with the adjustments below.** The proposal improves on both Capex's plan and my own review in several places. The main risk is that the narrowing is slightly too aggressive — a few cheap items from Capex's plan should survive as parallel or by-product work.

---

## 2. Where Capstan improves on my review and on Capex's plan

### 2.1 The risk–coverage curve is the experiment I missed

My review endorsed Capex's A3 gate-frontier sweep but did not identify the specific hypothesis that the BP and PC readers may be the same gate at two thresholds. Capstan's §2.3 does, and it is the single most important new idea in either response. If the curves coincide, the conference paraphrase gap is an operating-point artefact and the honest statement is that the two training rules produced the same gate. If PC's curve dominates at low coverage, we have been under-reporting a real result. This costs CPU time only and should be the first thing run.

### 2.2 Retiring the ePC solver is correct and overdue

Capstan's §2.2 clearly explains that the existing "PC-CAP" used a global error-state solver (eight settling iterations of gradient descent on the full GPT-2 graph, each an autodiff pass) — nothing local about it. My review treated the ePC cost as a motivation for Experiment C without stating plainly that the completed BP/PC contrast cannot show locality or a learning-dynamics advantage. Capstan is right: the 2.4-nat CounterFact gap and 96–102× cost ratio are facts about that estimator, not about PC. The ePC solver should be retired as a reader-training instrument and kept only as the error-state reference for C3 cross-checks.

### 2.3 The in-context retrieval arm should be a full comparator

My review mentioned an equal-information baseline but treated it as a subset of Experiment A. Capstan's §2.5 correctly argues it should be a full arm: if in-context retrieval reaches 90% on CounterFact paraphrases, the cap's value is latency, memory and tail harm, not accuracy. If it reaches 60%, the write mechanism is genuinely adding something. Either answer reframes G1. This costs minutes for 300 edits and should be in Phase 0.

### 2.4 The cached-feature harness is the right shared infrastructure

Building a cache of the three tap features and a small-reader harness that trains without GPT-2 in the loop addresses the root cause of the ePC cost problem. It also makes BP and PC comparisons fair at last — same architecture, same features, same tuning allowance, different update rule. This is the prerequisite for both H1 and H2.

### 2.5 Pre-declaring targets prevents post-hoc rationalization

Capstan's §4 table is the kind of pre-registration that both plans needed. Having the targets written before tuning means "decent" is not whatever we reach.

### 2.6 The same-subject hard-negative fix is concrete and cheap

Capstan's §2.7 identifies that the MQuAKE locality deteriorations come from same-subject different-relation prompts that were absent from training negatives. This is a rule-agnostic fix using data the datasets supply for free, and it should be standard in every arm.

---

## 3. Concerns and Suggested Adjustments

### 3.1 The narrowing drops D1 too far

Capstan says "keep D1 as a by-product of the same runs" but does not elaborate. D1 — paired interpretable measurements (reader embeddings, record/null margins, write directions, prediction changes) across BP/PC seeds — is cheap if the Phase-1 harness already produces matched checkpoints. It should be explicitly listed as a Phase-1 deliverable, not left implicit. The risk is that "by-product" becomes "forgotten" when the primary hypotheses absorb attention.

**Suggestion:** add D1 to the Phase-1 output list as a named deliverable: "paired representation diagnostics on the Phase-1 BP/PC checkpoints."

### 3.2 H1's BP control needs the same tuning as the PC arm

Capstan proposes an "unrolled k-step refinement trained by BP at equal test-time cost" as the control that separates "iteration helps" from "PC helps." This is the right control in principle. But an unrolled-refinement reader is a novel training procedure; if it is poorly tuned, it does not prove PC is better, it proves the control was bad. The BP unrolled control must receive the same tuning allowance, the same learning-rate sweep, and the same early-stopping protocol as the PC arm. Otherwise the comparison is confounded by implementation effort.

**Suggestion:** state explicitly in H1 that the unrolled-refinement control gets the same tuning budget as the PC arm, and report its development-set performance ceiling alongside the comparison.

### 3.3 The MQuAKE targets may be too ambitious for Phase 0–1

Capstan's §4 table targets ≥80% MQuAKE single-hop paraphrase retention, up from 67.4%/59.6%. That is a 12–20 point jump. If Phase 0 shows that the gap is partly payload (as §2.4 anticipates — 28–45 of 300 BP paraphrases fired and failed), then selection tuning alone may not close it. The targets should note which are expected from Phase 0–1 work (selection, hard negatives) and which may require architectural changes that are outside the first two phases.

**Suggestion:** annotate the §4 targets with a column indicating which phase is expected to deliver each, and mark MQuAKE single-hop retention as conditional on the Phase-0 payload diagnostic.

### 3.4 Composition (E) should not wait until Phase 3

Capstan defers composition to Phase 3, conditional on the §2.6 chaining diagnostic. The diagnostic is a good gate. But Capex's E1 — establishing a JAX reference on H3 with a BP control — is independent of the chaining result and can proceed in parallel with Phase 1. If the chaining diagnostic shows no chaining (likely, given zero composition scores), we will want the JAX reference ready, not starting from scratch six weeks in.

**Suggestion:** allow a minimal E1 (JAX H3 reference, BP control, synthetic two-hop fixtures) to proceed in parallel with Phase 1, as Capex's plan proposed. Capstan's E2 (explicit compositional operation) remains conditional on the chaining result.

### 3.5 The synthetic-to-real transfer criteria from my review are not addressed

Capstan proposes synthetic-first streams for H2, which is correct. But the proposal does not state what property of the synthetic stream would need to hold for the real-data pilot to be worth running. This was suggestion 3.2 in my review of Capex's plan and remains relevant.

**Suggestion:** add one sentence to Phase 2 specifying the synthetic-to-real transfer criterion — e.g., "the real-data pilot proceeds only if the synthetic-stream forgetting matrix shows a PC/BP gap that is not explained by stream length or relation count alone."

### 3.6 The Phase 0 budget is tight but probably sufficient

Six items in one week at ≤4 process-hours is feasible if the saved scores and logs are accessible and the forward-only reruns compile without issues. The main risk is item 1 (risk–coverage curves) depending on having the right saved `null_mass`, `best_score` and `selected_own_record` fields, and item 5 (chaining diagnostic) depending on whether the retrieval-drift records survived. If either set of records is incomplete, Phase 0 grows.

**Suggestion:** before Phase 0 begins, do a 30-minute audit of the saved fields to confirm items 1 and 5 are runnable. If fields are missing, re-acquire them in the first forward-only GPU slot.

### 3.7 The cross-lane escalation protocol is lighter than needed for three agents

Capstan proposes one dated line in a shared `decisions.md`. This is sufficient for two agents but the project now has three (Capex, Capstan, Derp Peoples). The protocol should specify who has authority to change lane ownership when a result crosses lanes (Charlie), and what the default is when lanes disagree (escalate to Charlie, not block).

**Suggestion:** add to the protocol: "lane ownership changes only when the lead (Charlie) says so; disagreements between agents are escalated, not blocking."

### 3.8 The in-context arm should report context length and cost

If in-context retrieval is a full comparator, it should report not just accuracy but the context length consumed (tokens of retrieved fact prepended) and the per-query latency. The cap's value, if accuracy is matched, is in these quantities. Without them, the comparison is incomplete.

**Suggestion:** the in-context arm reports accuracy, context tokens, per-query wall time, and peak memory, alongside the same tail-harm metrics as the cap arms.

---

## 4. Comparison of the Three Plans

| Dimension | Capex (original) | My review | Capstan (this response) |
|---|---|---|---|
| Number of lanes | 7 (A–F + §9) | 7, endorsed | 2 primary (A, B×C) + deferred |
| First action | A1 failure table | A1 failure table | Risk–coverage curves (CPU) |
| ePC solver status | Retire after C | Diagnose in C | Retire now as reader-training instrument |
| In-context retrieval | Subset of A | Subset of A | Full arm in Phase 0 |
| PC hypotheses | General (C) | General (C) | Specific: H1 (gate), H2 (interference) |
| Shared infrastructure | Reuse existing loaders | Reuse existing | New cached-feature harness |
| Pre-declared targets | §11 screens | §11 screens + 9 adjustments | §4 table with absolute targets |
| SLT / LLC | D3 bounded pilot | D3 with dual matching | Deferred to Phase 3 |
| Composition (E) | Phase 1–2 | Phase 1–2 with NESS condition | Phase 3 conditional on chaining |
| Budget | 32 h / 2 weeks | 32 h / 2 weeks | ~30 h / 6–8 weeks |
| Timing | Aggressive | Aggressive | Realistic |

Capstan's plan is the best of the three for the constraints we face (two agents, one 12 GB GPU, no deadline). My review was correct on governance and statistical discipline but wrong to endorse the full breadth of Capex's plan without qualification. Capex's plan is the most complete but too wide for the resources.

---

## 5. Summary of Recommendations

1. **Adopt Capstan's Phase 0 and Phase 1 as the primary sequence.**
2. **Run the risk–coverage curves first** — they are the cheapest informative experiment and could change everything.
3. **Add D1 (paired representation diagnostics) as a named Phase-1 deliverable**, not just a by-product.
4. **Ensure H1's BP unrolled-refinement control gets the same tuning budget as the PC arm.**
5. **Annotate the §4 targets with which phase is expected to deliver each;** mark MQuAKE single-hop retention as conditional on the Phase-0 payload diagnostic.
6. **Allow a minimal E1 (JAX H3 reference) to proceed in parallel with Phase 1,** rather than deferring all composition work to Phase 3.
7. **Add the synthetic-to-real transfer criterion** to Phase 2.
8. **Audit saved fields for 30 minutes before Phase 0** to confirm items 1 and 5 are runnable.
9. **Strengthen the cross-lane escalation protocol** for three agents: Charlie has sole authority to change lane ownership.
10. **Report context length, latency and memory for the in-context arm,** not just accuracy.

---

## 6. Risk Assessment (updated from my earlier review)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BP/PC curves coincide (PC advantage is threshold artefact) | Medium-high | Reframes PC value; H1 becomes primary | Phase 0 item 1 is designed to detect this |
| In-context retrieval matches cap accuracy | Medium | Cap value shifts to cost/harm, not accuracy | Phase 0 item 3; report cost metrics |
| H1 loses to unrolled-refinement control | Medium | "Iteration helps, PC doesn't" — publishable null | Same tuning budget; report control ceiling |
| H2 effect vanishes under modest replay | Medium | PC's locality case is replay bytes, not accuracy | Phase 2 includes replay-buffer comparison |
| Saved fields incomplete for Phase 0 items 1 or 5 | Low-medium | Phase 0 grows by re-acquisition | 30-minute audit before Phase 0 |
| Cached-feature harness takes longer than expected | Medium | Phase 1 slips | Phase 0 results inform whether to proceed |
| Composition deferred too long, loses momentum | Low-medium | E1 could have been ready | Allow minimal E1 in parallel |

The overall risk profile is better than Capex's plan because the primary hypotheses are fewer and the Phase 0 gate is cheap. The main new risk is over-narrowing — dropping work that is cheap enough to run in parallel and informative enough to keep.

---

*End of feedback. Prepared by the Omega agent (derp) on 20 October 2026.*