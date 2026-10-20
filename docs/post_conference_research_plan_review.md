# Review of "After Binghamton: Selective Continual Learning with Predictive-Coding Caps"

**Reviewer:** Omega agent (derp)  
**Date:** 20 October 2026  
**Subject:** Review and analysis of `post_conference_research_plan.md`, prepared for Charlie Derr and collaborators  
**Files consulted:** `post_conference_research_plan.md`, `pc_cap_month_plan_summary.md`, `slidedeck.txt`, `ongoing.md`, `mandatory_ammendment.md`, `AgentHandoffForResearchInTheExtremes.md`, `round58-capex-claim.json`, `round58-capex-handoff.md`, cap-value report (`results/extremes_analysis/ext-20261009/reports/cap_value_report.md`), additional-work reports (`PC-reader_report.md`, `HT-17_report.md`, `coupled_objective_note.md`)

---

## 1. Overall Assessment

This is a well-structured, scientifically honest post-conference research programme. Its central virtue is that it resists the temptation to declare victory from the conference results and instead proposes a disciplined sequence of experiments designed to isolate *which component* of the cap architecture is actually responsible for observed gains—or losses. The plan is candid about what the completed work does and does not establish, and it proposes concrete checkpoints that would halt unproductive branches rather than escalating commitment.

**Recommendation: proceed with the plan as written, with the following observations and suggested adjustments.**

---

## 2. Strengths

### 2.1 Honest grounding in completed evidence
The plan correctly identifies five findings from the October 10 cap-value supplement that should shape next steps. In particular:

- The cap *does* provide substantial adaptation, but an equal-information retrieval baseline is needed to credit the architecture rather than the information.
- Abstention accounts for ~90–100% of each reader's worst 5% of paraphrases on CounterFact, making selection the first hypothesis.
- The ePC reader training was expensive (~96–102× BP process time) and did not win—this is a strong motivator for the cheaper, more local PC design in Experiment C.
- Composition (three-question MQuAKE) scored zero for both cap types; this is a missing capability that better single-fact retrieval alone will not fix.
- Extremes are real but their statistical interpretation depends on the observable; the plan correctly insists on reporting the variable and population every time.

### 2.2 Clean separation of experiments
Experiments A–F are well-isolated:
- **A** tests selection (the gate) before changing the architecture.
- **B** tests continual learning (online adaptation, bounded memory, stale facts) rather than just append-and-query retention.
- **C** tests a genuinely local PC reader without re-running the expensive ePC training.
- **D** explains internal BP/PC differences with paired diagnostics and a bounded singular-learning-theory pilot.
- **E** tests composition (neural-symbolic) with explicit component controls.
- **F** tests distributed learning as a systems question, not a speedup claim.

Each experiment has a checkpoint that could redirect effort rather than expand it. This is the right structure.

### 2.3 Statistical discipline
The plan distinguishes development and confirmation populations, requires paired seeds and independent stream realizations, forbids counting permutations as new subjects, and insists on reporting uncertainty. The advancement screen (≥2 pp retention or ≥20% ES99+ reduction) is a practical effect-size threshold, not a p-value substitute.

### 2.4 Resource realism
The 32-hour first-tranche ceiling is modest and explicitly a planning cap. The plan correctly notes that historical 300-edit evaluation envelopes were ~30 minutes and that new logging, online adaptation, and new architectures require fresh profiles. The instruction to report both serial reservation and per-process costs is sound.

---

## 3. Concerns and Suggested Adjustments

### 3.1 Experiment A: oracle diagnostic scope
The oracle selection (A2) uses item identity to force the correct record. This is a valid diagnostic, but the plan should also report *how often* the oracle would have selected a record at all, since frequent null-oracle cases would mean that even perfect selection cannot rescue most errors. Consider adding a "oracle selection rate" row to the failure table in A1.

### 3.2 Experiment B: synthetic-to-real transfer risk
B1 proposes a reproducible synthetic relation stream first, then a 300-edit exposed real-data stream. The synthetic stream can isolate mechanisms, but its distributional assumptions (relation families, wording patterns, revision frequency) may not match the real data well enough to transfer. The plan should state explicitly what property of the synthetic stream would need to hold for the real-data pilot to be worth running, and what a mismatch would mean for the interpretation.

### 3.3 Experiment C: activation-PC vs error-state PC
The plan proposes activation-state PC as the first prototype (C2) and adds error-state PC only if the profile budget permits. Given that the *completed* work used error-state ePC and it was expensive, the activation-state choice is reasonable. However, the plan should note that the two formulations can diverge in practice even when theory suggests equivalence, and the verification protocol in C3 should check both energy values and gradient directions against the error-state reference, not just against finite differences on the activation-state model alone.

### 3.4 Experiment D: LLC pilot scope
The LLC pilot (D3) is well-bounded. One concern: the plan says "compare checkpoints matched for task loss as well as matched for training step." If the small reader from C trains much faster under BP than under PC, matching by training step may not be meaningful, and matching by task loss may select different regimes. Consider reporting both and flagging the divergence.

### 3.5 Experiment E: NESS specification gap
The plan acknowledges that the NESS system mentioned in correspondence is not fully specified by the available reports. This is honest, but it creates a risk: if E1 establishes a JAX reference on H3 but the NESS specification never arrives, E2's "explicit compositional operation" may diverge from what its authors intended. The plan should set a deadline or condition for obtaining the NESS specification before committing to E2's design.

### 3.6 §9: Active inference route
The decision problem in §9 is well-constructed (three actions, costly verification, finite simulated world). However, the plan should clarify whether the "coupled objective" branch can proceed independently of A–D or whether it requires a trained reader from C or B first. The text says "this branch may proceed independently once the mathematical definition is available," which is good, but the experimental instantiation (fitting observation likelihoods on development data) still needs a working reader.

### 3.7 Division of work
The suggested ownership table (§10) is for coordination, not assignment. This is clearly stated. However, the boundary between Capex (failure analysis, metrics, representation/SLT) and Capstan (local-PC implementation, profiling, dispatch) may be ambiguous if C2's implementation reveals a selection failure that belongs to A. Consider adding a shared escalation protocol for when an experiment's results cross lanes.

---

## 4. Relationship to the One-Month Plan

The `pc_cap_month_plan_summary.md` describes a prior one-month programme (Goertzel and Fable, 7 September 2026) with a 154 A100-hour budget, three test beds (constructed control, learned synthetic grammar, factual editing), and a focus on routing, ePC conversion, and retrieval keys.

The post-conference plan is a natural successor:
- It reuses the same base model (frozen GPT-2 small), the same datasets (zsRE, CounterFact, MQuAKE), and the same evaluation philosophy (full-answer generation, paired seeds, separated development/confirmation).
- It *shifts* the focus from "does routing help?" (the one-month plan's primary question) to "where does the remaining error come from, and can local PC or composition add a capability that a simpler alternative does not?" This is a reasonable evolution after the conference results showed strong paraphrase exact match but weak composition and expensive ePC.
- The one-month plan's 154-hour budget is much larger than the post-conference plan's 32-hour first tranche. This is appropriate: the first tranche is a diagnostic and prototype phase, not a full confirmation run.

**One gap:** the post-conference plan does not explicitly state which results from the one-month plan (if any) it treats as confirmed versus provisional. If the one-month plan's routing comparisons (C2 vs C1, C2 vs CR) were run to completion, those results should be cited as prior evidence in Experiment A's failure table. If they were not completed, the post-conference plan should say so.

---

## 5. Relationship to the Mandatory Amendment and Agent Handoff

The `mandatory_ammendment.md` and `AgentHandoffForResearchInTheExtremes.md` documents impose constraints on how agents collaborate and how research artifacts are managed. The post-conference plan appears consistent with these:
- It proposes new paths under `aw/post_conference/` rather than modifying existing files.
- It preserves historical checkpoints and reports.
- It requires explicit code/data/model identity recording.
- It does not assume Colab or remote execution.

No conflicts were identified between the plan and these governance documents.

---

## 6. Summary of Recommendations

1. **Proceed with the plan as written.** The experiment sequence (A→B→C→D, with E and F conditional) is well-designed.
2. **Add an oracle selection rate** to Experiment A's failure table.
3. **State synthetic-to-real transfer criteria** for Experiment B.
4. **Cross-check activation-state PC against the error-state reference**, not only against finite differences.
5. **Report both step-matched and loss-matched LLC comparisons** in Experiment D, flagging divergence.
6. **Set a condition for obtaining the NESS specification** before committing to Experiment E2's design.
7. **Clarify the coupled-objective branch's dependency** on a working reader.
8. **Add a cross-lane escalation protocol** for when an experiment's results cross the Capex/Capstan boundary.
9. **Cite or explicitly set aside the one-month plan's routing results** in Experiment A's prior-evidence table.

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation in plan |
|---|---|---|---|
| Selection is not the bottleneck (A fails) | Medium | Redirects to payload/generation | Checkpoint A explicitly handles this |
| Local PC is not cheaper than BP (C fails) | Medium-high | Removes PC from the story; use BP | Checkpoint C preserves the result |
| Composition cannot beat symbolic-only (E fails) | Medium | Simpler solution wins; no PC needed | Checkpoint E accepts this |
| LLC is unstable (D3 fails) | Medium | No SLT contribution; publish instability | Checkpoint D stops the branch |
| Distributed locality has no systems advantage (F fails) | High | No hardware investment justified | Checkpoint F stops expansion |
| 32-hour budget is insufficient | Medium | Delay; request more | Reserve of 6 h; stop-or-reduce rule |

The plan's checkpoint structure means that no single failure invalidates the programme. The most likely outcome is that some branches succeed and others produce informative negatives, which is the correct scientific posture.

---

*End of review. Prepared by the Omega agent on 20 October 2026.*