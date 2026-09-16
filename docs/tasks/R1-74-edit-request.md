# R1-74 — DEC-053 scoring edit request

Status: tested patch delivered, NOT applied. Agent: Codex. Applying this existing-file change requires the user's permission under the new-files-only rule. CONTRIBUTING.md also requires an edit request and wait for files owned by another lane.

Target: src/pccap/revision_v1/stage4_assays.py. Exact patch: [R1-74-stage4_assays.patch](R1-74-stage4_assays.patch); complete tested preview: [R1-74-stage4_assays.preview.py](R1-74-stage4_assays.preview.py). Before/after SHA256 are in logs/r1_round17/R1-74-patch-identity.json.

The patch makes locality and near-miss preserved use exact decoded-text equality within the existing32-token bound, with no normalization or termination condition (DEC-053). Each row also carries preserved_terminated, truncated_pair, reference_truncated and query_truncated. Unavailable rows have null verdicts. Both sections gain checkpoint summaries with planned/scored/unavailable denominators, both counts/fractions and per-side truncation counts. Missing cases never become zero-rate or100% preservation. ES/edit-exact/revision scoring and generation are unchanged.

The separate scripts/r1_74_rescore.py reads historical checkpoint traces, recomputes both conventions and writes new reports only. Its audited six-checkpoint output is logs/r1_round17/R1-74-rescore.json. CounterFact reproduces49/50 bounded versus36/50 termination-qualified locality at100/300, and100/100 versus63/100 near-miss at300. The13/37 identical truncated pairs explain the difference. Both zsRE cells reproduce50/50 locality under both conventions.

**Correction to the lane's expected zsRE near-miss result:** both listed zsRE cells contain zero near-miss rows against100planned IDs (and zero revision rows against50planned IDs). Their near-miss fraction is unavailable, not100/100. The rescorer preserves that missingness. No experiment was rerun to fill the gap.

Verification:14tests passed in1.58s, including actual TinyBase identical truncated locality, the real challenge pipeline with terminating/truncated controlled generations, both-side truth table, missing/malformed/duplicate refusal and input immutability. Ruff passes for helper, preview and tests; git apply --check succeeds. The installed file is unchanged.

Landing sequence after permission AND completion of the owner's active profile: verify the before hash; apply this one-file patch; run the scoring tests against the landed source as well as the preview; reconcile any independent source changes; then rebuild new versions of the R1-68c and R1-64b recipes once against the final installed tree. Every src change invalidates existing recipe code_sha256. Do not change sources during an active cell or overwrite historical recipes. New analysis modules in this round stay under scripts so they do not force another source-tree rebind.

No numerical or policy choice remains for this patch: DEC-053 already binds the scoring rule. User approval is still required for the existing-file write; active-profile coordination is an additional execution constraint. No commit, lease, GPU execution, draw, seal or freeze occurred.
