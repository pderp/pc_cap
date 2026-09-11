# Updated plan 6 review — D-F execution

Author: Codex. Reviewed and executed 2026-09-11 from starting commit
`af98eab218ef55308be333615c9a228a0b0eb5ef`, with a clean working tree before this task.
The user's clarification authorizes **only section 5, decision D-F**, including its
several tasks and the resulting commit. This is not approval of D-D, D-E, or a range
of decisions. The earlier new-files-only restriction is lifted for these approved
edits; the other decisions remain outside this execution.

**D-F is complete.** Both approved patches were applied, the expanded independent
V2 study finished, and a fresh environment was actually installed and checked.
The V2 review still identifies production defects, so this completion does not make
the confirmation path ready or change the existing GRACE parity failure.

## Files re-ingested and evidence boundary

Read the current `updated_plan6.md`, `ongoing.md`, preceding plans 4/5 as relevant,
working protocol, task board and ENV-05/B4/V2 records, approved patch proposals,
the repaired confirmation runner/stages/collectors, and the original and expanded
study drivers. Also inspected the new P4/S7 modules, tests and task records, S1
integration changes, and the S7 inventory's counts and shortfalls. PDF D.4, D.9
and PC-10 remain the scientific reference. `derp_review3.md` is still **51 bytes,
containing only its title** at this snapshot; there is no substantive review there
to accept or rebut.

P4 now explicitly uses settled errors from the declared solver on BP grammar weights,
with residual PCA labelled as a companion. S7 now has a dedicated independent-data
inventory and reversal harness; its CounterFact shared stratum contains nine pairs.
Those are relevant additions since the previous handoff. D-F does not include the
separate Lane X resampling/subject-exclusion audit or GPU teacher filtering, so this
review does not certify those scientific or independence claims anew.

The recorded starting snapshot, lock hash and active package inventory are in
`results/PLAN6/DF/before.json`. No production final freeze or sealed confirmation
payload was opened or written. All checks in this task ran on CPU.

## D-F deliverables

| Task | Completed result | Evidence |
| --- | --- | --- |
| Apply final review-tools patch | Corrected the study's schema-invalid checkpoint override; cleaned imports and bound per-case diagnostic closures; preserved pccap-before-JAX initialization | `scripts/review_repairs_r2b_study.py`, `scripts/grace_numerical_trace.py`; approved patch remains archived in `docs/tasks/CODEX-20260911-review-tools-v2.patch` |
| Finish V2 | Fresh fixture; 150/150 synthetic editing jobs; all remaining probes exercised; report written | `logs/review_repairs_r2b.md`, `results/V2/plan6_df/` |
| Apply environment documentation patch | Added the recreation section and refreshed it with actual installation evidence | `docs/environment.md` |
| Perform real ENV-05 install | New environment, all retained lock pins installed, local editable package installed, pip consistency and CPU determinism checks passed | `results/ENV05/plan6_df_install/` |
| Update completion records | ENV-05 marked done and board regenerated; other task rows verified unchanged | `docs/tasks/ENV-05.md`, `results/PLAN6/DF/status_update.json` |

The original failed V2 and DNS/resolution-only installation records remain preserved.
The final patch request record now states that the approved edit was applied. No
baseline optimizer, tolerance, model or production harness was modified.

## V2: passing repairs and remaining work

The expanded study completed in **2.787 seconds** with synthetic models and outcomes.
It exercised the actual editing CLI, confirmation loader, stage, stream, checkpoint
writer and analysis collectors. The source-tree digest matched the fixture freeze
before and after the run; exact provenance is recorded alongside the output.

The repaired path correctly refuses invalid schedules, base/read arguments, unknown
arms and unapproved code drift. Lease acquisition precedes backend discovery. S5
uses the frozen EPC identity/calibration and passes the frozen run allowance through;
missing authority or mismatched EPC bytes stop before model construction. Explicit
force preserves the previous result directory and checkpoint bytes even when the
new learned state differs. Normal finite per-run/stage allowances reject an
over-budget next job. Both required synthetic paired contrasts collect completely.

**A completed study is not an all-clear.** These findings remain for the orchestrator:

| Finding | Measured evidence | Required follow-up |
| --- | --- | --- |
| V2-01: BP/tokenizer startup identity | Deliberately inconsistent frozen BP and tokenizer hashes were accepted with exit 0 | Compare actual loaded identities with the freeze before editing/evaluation; retain mismatch controls |
| V2-02: unknown experiment IDs | A specific filter returned two runs / 16 rows instead of one run / eight rows after an unknown-ID record was added | Require exact identity under an explicit filter; reject or report unknown provenance |
| V2-03: experiment selection/grouping | Two identified experiments collapsed into one S7 order cell and one resource-comparison cell; S7 CLI lacks its loader's filter | Expose the CLI filter and reject mixed-experiment analysis or carry identity through every grouping |
| V2-04: stage limit without run limit | A 0.01-second stage allowance with `run_allowance_seconds=None` was labelled enforced but consumed 7.2000034 synthetic seconds | Refuse the inconsistent configuration or enforce a remaining-stage-derived run allowance |
| V2-05: archived spending omitted | Two force attempts consumed 14.4000069 synthetic seconds; stage accounting counted only 7.2000035 | Include prior attempts in resource spending while excluding their superseded results from scientific analysis |

V2-01…03 confirm and sharpen plan 6 §2.2. V2-04/05 extend that repair list and should
be included in the pre-confirmation resource gate. The 150 executed jobs cover
zsRE/CounterFact editing; the current draft's **210 scheduled paths** were checked
for identity uniqueness, not executed as 210 end-to-end jobs. Grammar confirmation
execution remains a separate check.

The study's exit code 0 records successful completion of the diagnostic, including
expected failing properties. S5 missing-calibration/checkpoint errors currently
produce exit 1 (`correctness_failure`), rather than the proposed exit-2 preflight
classification; they do stop before model construction. The full review contains
the exact boundaries and commands. Production repairs were not part of D-F.

## ENV-05: actual recreation and CUDA status

The new environment is:

`/home/derp/cap/assets/envs/venv-check-plan6-df`

The existing setup script completed its non-dry path without implementation changes:
create venv → install filtered lock → install local editable pccap → `pip check` →
CPU determinism report. All **150 pinned dependencies** match the installed versions
exactly. Local `pccap==0.0.1` is editable from `/home/derp/cap/pc_cap`; bootstrap
`pip==26.0.1` is the other distribution beyond the retained lock entries. The original
private editable requirement was replaced by the authorized local checkout install.

`pip check` reports no broken requirements. The report confirms JAX **0.11.1**, CPU
device `cpu:0`, highest matmul precision, x64 disabled and partitionable Threefry
disabled. The setup took approximately **158.58 seconds**, measured from its start
record to completion. The original `requirements.lock` hash is unchanged, and the
active environment's package inventory matches the pre-task snapshot. Ignored local
editable packaging metadata was allowed by this approval.

**CUDA support is installed.** The lock includes JAX's CUDA 13 plugin/runtime packages.
The setup checks deliberately run with `CUDA_VISIBLE_DEVICES=''` and
`JAX_PLATFORMS=cpu`, as specified by D-F. These variables are scoped to the verification
processes and are not a permanent environment setting. GPU execution in this new
environment has not been tested; CPU verification cannot certify its GPU execution.
The project continues to use JAX/CUDA for GPU work.

The install record captures the starting commit and `source_was_dirty=true`, because
the approved patch changes were present. This is a version-verified editable
recreation, not a claim of bit-identical wheels or an immutable source snapshot.
Use fresh environment and evidence destinations when rerunning; the completed
destination is deliberately protected against reuse. The exact command, logs and
remaining verification boundaries are in `docs/tasks/ENV-05.md`.

## Corrections to plan 6's interpretation

1. **Section 2.1 understates GRACE's value mismatch.** Case 0 reaches 0.3534, but the
   maximum over the 20 isolated cases is **22.4391**, as recorded in
   `results/S2/grace_jax/pc10.json` and the case-1 trace. The plan's approximate
   1e-5 *relative* loss-agreement description also confuses absolute and relative
   differences: case 1 at step 10 differs by about 1.35e-5 absolute, or 1.48e-3
   relative; case 0 at step 100 differs by about 3.04e-3 relative.
2. **The cause is narrowed, not proved.** Exact initialization and fixed-gradient
   Adam replay support a numerical-sensitivity explanation, but they do not prove
   that cross-framework fp32 value parity is impossible or that the adapter has no
   implementation difference. A within-JAX sensitivity experiment can supply useful
   evidence without logically excluding a coexisting adapter defect. Preserve the
   current gate and uncertainty until the separate D-B decision; no sensitivity
   experiment, tolerance change or B4 registration was performed under D-F.
3. **Section 1's readiness language is premature.** The expanded study confirms
   material startup-provenance, experiment-isolation and budget defects despite the
   passing baseline tests. Schema-valid inputs and successful synthetic jobs are
   necessary evidence, but do not close these negative controls. The sequence should
   keep those repairs and their independent re-check ahead of confirmation.

The PDF's PC-10 requires reference validation on shared single-/multi-token cases
and explicit documentation of adaptations. The present lane implements a stricter
concrete codebook comparison; this review reports its failure without silently
substituting a different acceptance rule.

## Validation and commit scope

Patched diagnostic scripts and the environment helper pass Ruff. The targeted CPU
suite passes **14/14** tests (nine confirmation controls and five GRACE controls)
in **7.27 seconds**. The expanded study, real install, exact installed-version check,
local editable provenance check, active-inventory comparison and lock comparison
also completed. Logs: `results/PLAN6/DF/`, `results/V2/plan6_df/`, and
`results/ENV05/plan6_df_install/`.

ENV-05 is the only changed task-manifest row; the status tool regenerated its board.
This change set records D-F execution and findings. It does not record approval for
the freeze/allowances, B4 parity relaxation, coverage-tool installation, S6 closure
or new work, grammar promotion, S7 shortfall acceptance, or S1 scientific acceptance.
All resulting D-F files are to be committed as requested; nothing is pushed.
