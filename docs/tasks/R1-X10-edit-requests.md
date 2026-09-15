# R1-X10 — proposed existing-file edits

Status: review requests prepared, **not applied**. The user's new-files-only rule remains in force.
No permission for these edits has been inferred from earlier repair approvals. Owner task files, results and
reference identities may change while GPU work proceeds; recheck their hashes before any approved application.

The scientific findings and evidence are in [the review](../../logs/review_r1_mquake.md).
The [notes patch](R1-X10-notes.patch) is a concrete textual correction for the inspected notes.
Other repairs below specify implementation and acceptance criteria; they are not presented as tested patches.

| Request | Existing file(s) requiring permission | Exact requested change | Acceptance checkpoint |
| --- | --- | --- | --- |
| ER-01 | scripts/r1_13_stream_eval.py | Replace ad-hoc override loading with a pure development-only loader; validate mode/dataset, positive count and available size, unique identities, token/digest/source bindings and unrelated inventory; record manifest SHA and ordered selected/query IDs before GPU work | Synthetic wrong mode/dataset, n≤0, n>available, duplicate identities and tampered tokens/hash refuse before model, lease or outputs; valid v3 preserves selected order and metrics schema |
| ER-02 | src/pccap/revision_v1/endpoints.py | Extend cached-selection trace with actual hard_null and selected weights/record identity; identify rare-gate veto where available; preserve old trace fields | Low null mass plus gate veto reports no fire; accepting gate reports fire; no extra model query, selection recomputation or answer conditioning; restore identity tests pass |
| ER-03 | scripts/r1_60_composition_run.py | Snapshot/verify pool, composition, calibration, tokenizer and weights before execution; bind ordered planned IDs and selection limits; distinguish selected/scored/unavailable and preserve structural exclusions in an explicit source-stage inventory | Mutated/missing input refuses before execution; zero/negative max-cases policy explicit; missing dependency/alias overlap remains visible; hashes reflect consumed bytes |
| ER-04 | scripts/r1_d5_mquake_teacher.py | Add versioned producer/base/tokenizer/decoder/max-token identities, generation cardinality check, explicit bounded/complete eligibility policy, reason counts and complete ledger receipt | Wrong output count and input-hash mismatch refuse; truncated teacher fixture follows declared policy; no old-answer correctness claim without corresponding test |
| ER-05 | scripts/r1_d6_mquake_split.py | Correct “rest untouched” documentation and future receipt labeling to primary-only remainder; record locality/unrelated subject exposure and reference cumulative register; do not overwrite historical pools | A toy neighbour outside primary train/dev enters exposure union; item and subject counts separate; independent overlap reasons retained |
| ER-06 | docs/R1_stage2_notes.md | Apply prepared notes qualification patch after checking current contents | Patch applies cleanly; arithmetic and referenced identities match R1-X10 evidence; active owner additions retained |
| ER-07 | docs/decisions.md and/or a new dated decision receipt | Qualify DEC-046's remaining-capacity statement and record the lead's chosen D7 policy/scope; correct T inventory 1,825→1,868 local cases / 96 edits / 86 subjects in current planning references | No retrospective subject release; exact policy and independent-role demand stated; current register preserved until versioned successor |
| ER-08 | No overwrite of existing primary manifest recommended | Create a new primary version for selected self-contained tri3 weights; structure result references by reader/split/metric, identify older drift/unseen assays; update matrix/profile/freeze through new versions | Every cited result matches selected weight/config and population; no inherited assay becomes a current-reference certificate |

ER-01/02 affect shared execution paths; coordinate with the owner after active jobs and rebind all affected
code identities. ER-03/04 should write new run/receipt versions. ER-06 is textual, but still needs the user's
permission because it edits an existing file. The matrix written in this round is a draft; it will need a new
version if the selected reference or endpoint execution code changes.

The task was to review and supply requests. No repair above is applied and no pending permission is being treated
as approval. Population/final-reference decisions remain separate from permission to edit code.
