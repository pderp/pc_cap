# R1-D10i — independent review of the concurrent refresh

Status: **review complete; construction and signing owned by the orchestrator**. Agent: Codex. September 18, 2026. New files only; CPU only.

The urgent lane appeared while D14b was being tested. Codex inspected the source change, then detected the orchestrator already writing evidence v6, inputs v10 and signing forms. The unexecuted parallel metadata builder was withdrawn before creating a competing artifact. Codex changed no existing input, candidate, form, receipt, operator or journal.

Inputs: original evidence v5, orchestrator's refreshed evidence v6 / inputs v10, Git's round 26 D10c source, current D10c and genuine v8 steps 1/2 receipts.

Outputs: [read-only reviewer](../../scripts/r1_d10i_refresh_review.py), [verification JSON](../../logs/r1_round41/d10i-independent-review.json), [successful run](../../logs/r1_round41/d10i-independent-review-v2.txt).

## Findings

1. All **865** refreshed bindings match. The original inventory contains two copies of **one** stale producer path, scripts/r1_d10c_endpoints.py: a2c968b4… → 9afe6221…. Other source identities remain intact.
2. All **69,146 dispositions** are unchanged. AST comparison finds changes only in construct/main: DEC-063 checking/propagation during postdraw endpoint construction. Role-plan and clearance-related functions are identical. Historical judgments have not been recomputed or relabelled as new outcomes.
3. Installed exhaustive clearance succeeds: usable subjects **zsRE 6,084; CounterFact 6,121; MQuAKE 2,161**. The unsigned v10 preview's sole remaining blocker at review time is its own owner authorization, not a data failure.
4. Genuine v8 protocol and cost receipts pass the installed validator under v10. Common register/matrix/protocol/layout/full-validation/family bindings and cost basis are unchanged. **A provenance-only refresh requires no new substantive protocol/cost approval.** A fresh clearance request still needs its new evidence identity and current exposure attestation.
5. The original operator chooses the previous completed journal inputs; merely passing --inputs v10 does not move an active v8 session. Failed clearance also left an authorization receipt that makes unchanged retry refuse overwrite. The outer preview can omit failures retained in dry_run.blocked; a safe check must propagate nested errors. These were documented for reconciliation, not bypassed.

The orchestrator subsequently documented fresh operator_v9 and completed clearance (lead-queue item 95). Its new session, delegated forms and candidate handling are its work. This timestamped independent review does not certify that later session or replace X20.

Verify command under the standard CPU venv: python -m scripts.r1_d10i_refresh_review --output logs/NEW_REVIEW.json.

The reviewer creates one new report and invokes no operator. Its first run stopped on a reviewer comparison bug: some bindings include an extra records field. The corrected version compares path/SHA identity while preserving metadata; the source had not changed.

Done-when: refreshed sources, unchanged judgments, source-change scope and signature applicability checked. Cost: **0 GPU seconds**; no models, signatures, draws or seals. Unresolved: **X20 waits for actual step 8**; the owner subsequently advanced through RNG admission and the actual draw. Codex sent no duplicate permission or seed request.
