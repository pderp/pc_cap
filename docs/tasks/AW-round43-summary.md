# Round 43 — Codex handoff

2026-09-20. All assigned CPU preparation lanes are delivered. **No GPU use, new cache build, primary-source edit, staging or commit.** Claude's bounded-correction/scoring files and AW-B/R preregistrations are untouched.

| Lane | Delivery | Result |
|---|---|---|
| [AW-R0](AW-R0.md) | `aw/r_extension.py`, 30 recipes, separate matrix, content-sealed populations/payloads | Both datasets feasible; 684 zsRE / 721 CounterFact subjects remain. Every endpoint slot filled. |
| [AW-L0](AW-L0.md) | Frozen identity audit; saved 300-edit development checkpoint reconstruction | 64/64 exact logit vectors; matching cost counts; unchanged saved state. |
| [AW-L1](AW-L1.md) | Existing-cache probes and paired results | All combined read sets match the lexical-only control; tap-only null rejection is weak, especially CounterFact. No basis to call lower layers noise. |
| [AW-L3](AW-L3.md) | `aw/interface.py` and tiny-base tests | Explicit read/write sets mask acquisition through deployment; all-site behavior matches original; dropped read projections reduce actual parameter bytes. |
| [AW-L preregistration](../additional_work/AW-L.md) | Reviewable one-page draft | 2×2 arms, three seeds, six readers, 24 evaluations; exposed realization 0; 48-hour ceiling; October 9 stop. |

**Two dispatch issues remain.** The measured Option R means sum to **38.030 process-hours** against its 30-hour portfolio allocation; 1.7-factor per-cell stop ceilings sum to 64.651 hours. Concurrent process time is not identical to elapsed GPU wall-time, so reconcile units and queue policy before accepting a schedule. The existing frozen backend admits only the original matrix: the extension recipes intentionally have their own mode and `launch_authorized: false`; a supplemental consumer must verify their identities and emit receipts under `logs/additional_work/R/`. These are not automatically executable primary recipes. See [interpretation/cost note](AW-R0-interpretation.md).

**Scientific/implementation qualifications.** The late-tap raw norm is larger, but the reader normalizes features; norm is not evidence of usefulness. The probe evaluation memories have only 15 zsRE / 7 CounterFact records, and shared-subject/family queries are dependent. Actual reader retraining, stream-scale editing/fidelity and the L4 runtime gate remain necessary. Six readers imply shared trained weights across the two write arms; the draft makes this explicit. Dense inactive delta slots are zero but still consume charged storage. The locked `observations.py` docstring incorrectly says taps enter blocks; executable taps are post-block. Record a later documentation fix after release, without changing the active tree now.

**Validation.** `logs/additional_work-round43-tests-final.txt`: **35 passed** (24 new lane tests plus 11 existing supplemental tests). Scoped Ruff passes. Final disk reload independently checks all 30 recipes, ten shared payload files, two populations and their endpoint/order identities. `logs/additional_work/round43-final-verification.json` verifies **165 frozen source bindings, zero mismatches**. Producer hashes in all three reports match current files. The final population replay reproduces content bytes; pre-handoff metadata finalization is recorded separately.

**Next owners/actions:** lead reviews AW-L draft and Option R accounting; Claude can continue AW-B/scoring and plan the supplemental consumer/L4 training plumbing. No allocation, model result, primary analysis label or budget was changed to resolve these open issues. Completed task records and JSON receipts can be mirrored to the shared board by the orchestrator.
