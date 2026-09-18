# Round 32 handoff

Codex, September 18, 2026; starting HEAD `9131140`. New files only this round; no commits, GPU/model execution, threshold edits or changes to installed execution sources.

## Decision-ready finding

[R1-49l](R1-49l.md) is complete. Original registration supports **continued/changed-base fidelity with the cap disabled**. The guide says this explicitly; DEC-033 adopts that guide; DEC-047 uses the bounds to certify S1; the Q12 proposal accepted by DEC-058 still says “For continued-base fidelity.” Draft v5/v5.1 wording became ambiguous; D.2 explicitly extended the bounds to both-reference cap-on final endpoints, and my round-31 code connected that result to primary admission. No explicit lead adoption of that added veto was found.

This qualifies my previous explanation: the cap result exceeds the current D.2 check, but describing that applicability as unambiguously registered from the outset was too strong. The measurement is unchanged. It is a scope issue for the lead, not permission to silently relax a limit after inspecting a result.

The report quotes exact sources across all **14 protocol documents**, both governing PDFs, plan 9 and decisions. The numerical and code consequences are tested: complete metrics/intervals remain calculated; failed cell fidelity makes `scientific_admission=False`, and DEC-058 returns **unavailable before its performance inequalities**. A failed primary cell affects all seven comparisons sharing it; a failed control affects one. MQuAKE's 1,000-edit comparisons remain unavailable independently under DEC-060. Its one development result is not a prediction of every future confirmatory outcome.

The orchestrator can now post **Q17**, using the two options prepared in R1-49l: newly declared secondary cap-fidelity benchmarks with an explicit label/admission meaning, or cap NLL≤.01 admission with descriptive KL. Keep the continued-base gate, full measurements, references and observed values unchanged. If the lead wants to retain the current joint KL/NLL veto, explicitly adopt its expanded scope and label consequence. After the decision, version the protocol/consumer/package bindings; do not overwrite the historical evidence or change the classifier opportunistically.

## Work status

| Lane | Status | Dependency |
|---|---|---|
| R1-49l | Complete provenance and behavior audit | Lead resolves Q17; orchestrator posts it |
| HT-6 | Generator tested; one-cell preview, figures and talk framing saved | All four chain-S measurements before final report |
| R1-58l | Existing one-cell inventory; final receipt still pending | Remaining donors, transfer evidence, explicit v4 validator, ceilings/projection |
| R1-63m | Pending | Cost v4, idle-boundary backend patch and resolved fidelity scope |
| X19 | Pending | Exact candidate v14 package |
| HT-4f | Pending | Signed receipt v4 |

[HT-6](HT-6.md) includes a completion command that refuses partial evidence by default. [Preview report](../../logs/r1_round32/ht6-partial-preview-v2/report.md) keeps all three missing cells visible. Full and sample statistics differ legitimately because the sample is the first 128 windows; their overlapping NLL measurements agree. Sample KL comes from a full-vector prefix slice and is labelled accordingly. The figure is a strict empirical survival curve with correct tie/step handling, not a power-law fit.

## Validation and artifacts

- **13 focused CPU tests passed**: 5 classifier/provenance-behavior cases and 8 report/curve cases. Logs: `logs/r1_round32/final-tests.txt`, `lint.txt`.
- Exact quote inventory and source hashes: `logs/r1_round32/provenance/fidelity-source-quotes.json`.
- Synthetic full-family classifier evidence: `logs/r1_round32/provenance/fidelity-classifier-rehearsal.json`.
- Historical round-31 admission diff: `logs/r1_round32/provenance/round31-admission-change.diff`.
- New scripts: `r1_49l_fidelity_audit.py`, `ht6_full_validation_report.py`, `ht6_plot.py`; corresponding new test files. The plotting helper uses the already installed assets plotting environment; no dependency installation.
- No existing protocol, analysis, driver, backend, decision, task board or active owner artifact was edited. Existing untracked assembler fixtures at the start, and those created concurrently by the owner, are not part of this work.
- Source-protection verification and final snapshot are in `logs/r1_round32/final-integrity-check.json`.

The pending lanes require measured evidence or an explicit scope decision. They are not awaiting signatures alone.
