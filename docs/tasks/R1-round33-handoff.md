# Round 33 handoff — DEC-064 adopted; concentration reporting ready

Codex, September 18, 2026, 07:47 EDT. Starting HEAD `cd7dd81`. CPU only; no staging/commits, GPU use, real-base execution, production draw/seal/freeze or signatures. Claude's chain S remains active.

| Lane | Result this round | Next dependency/action |
|---|---|---|
| R1-49m | **Done:** D.3 text, explicit DEC-064 policy, analysis hook, eight-document closure, 405-cell planned matrix, tests and applied patch | Carry the new bindings into R1-63m's successor package |
| HT-7 | **Done:** deterministic concentration definitions, both-reference computation, tests and report integration | Statistics are ready for remaining completed profiles |
| HT-6 | **Prepared, final pending:** reviewed 2/4-cell preview with benchmarks, concentration and survival figure | Both zsRE profiles; then final report and presentation export |
| R1-58l | **Partial:** unknown cost-revision fall-through fixed; two audited donors | Four donors, typed v4 supplement, reviewed transfers, ceilings v2, revised schedule and gap inventory |
| R1-63m | Waiting | Cost v4, D.3 package migration and owner's post-chain-S backend installation |
| X19 | Waiting | Exact candidate v14/forms v9/sheet v8 |
| HT-4f | Waiting | Signed cost receipt v4; then claim ledger v6 |

## Scientific policy and evidence

[D.3](../R1_stage4_protocol_v5_2_D_3.md) implements **DEC-064 option 1**. Cap KL and NLL retain .001/.01 benchmarks and explicit pass/fail labels for both references, but numeric failures no longer veto primary comparisons. Continued-base certification is unchanged. Evidence integrity, endpoint completeness, prior admission and MQuAKE missingness still apply. Rejected options are documented, not built. Historical D.2 matrices retain clearly labelled historical replay behavior; they are not current-policy analyses.

The complete synthetic option-D family retains every interval and classification when all cap benchmarks fail. Receipt/vector integration tests verify current-policy admission despite a numeric failure and preserve nonadmission for missing/corrupt evidence, missing primary observations, development scope or upstream nonadmission. The unchanged DEC-058 boundaries remain tested. The D.3 planned matrix has **360 + 45** cells with no admission or launch authority; its generated analysis has zero scientifically admitted cells, 21 unavailable contrasts and no completed blocks.

[HT-7](HT-7.md) adds position/window concentration, explicit fractional top-share definitions and undefined concentration for zero total harm. Near-zero observed-token NLL change is not proof of an unchanged prediction distribution. These statistics establish neither a power law, reader-firing mechanism nor κ benefit. See the [reviewed partial report](../../logs/r1_round33/ht6-partial-preview-v2/report.md) and [figure](../../logs/r1_round33/ht6-partial-preview-v2/tail-survival.png).

For the completed learned-reader MQuAKE cell, both references give mean KL .0055436876 (benchmark fail), mean NLL increase .0056009764 (pass), **171 positions carrying half KL**, top .1% KL share .631015, Gini .998188 and 1,612/1,931 windows ≤.001 mean KL. The completed v0 MQuAKE cell has zero observed loss/KL change across these validation positions. Both overlap checks pass within 1.4211e-14 nats. These are development measurements on the declared population. They do not alone establish a confirmatory comparison or generalize to the pending zsRE/other-condition runs.

The all-zero survival panel is now explicitly labelled. The reviewed v2 preview was visually inspected and renders without the initial preview's logarithmic-axis warning. No partial output was copied into final presentation material. After four completed donors, run the same generator **without** `--allow-partial`, inspect, and copy its final figure and qualified two-sentence result to `assets/presentation-materials/`.

## Validation and protected work

**79 tests passed, 4 deselected**, in `logs/r1_round33/final-tests.txt`:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m pytest \
  tests/revision_v1/test_ht7_concentration.py \
  tests/revision_v1/test_r1_49m_fidelity_policy.py \
  tests/revision_v1/test_ht6_full_validation_report.py \
  tests/revision_v1/test_r1_49h_analysis.py \
  tests/revision_v1/test_r1_49g_analysis.py \
  tests/revision_v1/test_r1_49k_protocol.py \
  tests/revision_v1/test_r1_58l_revision_dispatch.py \
  tests/revision_v1/test_r1_58h_cost_receipt.py \
  tests/revision_v1/test_r1_49l_fidelity_interpretation.py \
  -k 'not tinybase and not cell_status_distinguishes' \
  --basetemp ../assets/runs/pc_cap/R1/rehearsal_fixtures/round33/<new-pytest-directory> -q
```

The four exclusions are an older TinyBase integration and three older control-flow fixtures that write under the previous result-tree convention. New real-vector policy fixtures cover current and legacy admission under the required assets fixture directory. This is focused validation, not a whole-repository test claim. Initial test setup failures (absent pytest parent directory and missing synthetic matrix root policy binding) are retained in the initial log; corrected fixtures pass in subsequent and final runs.

Ruff and `git diff --check` pass. `git apply --reverse --check docs/tasks/R1-49m-analysis.patch` verifies the delivered patch matches the already installed analysis changes and their new helper modules. The D.3 matrix regenerates exactly from its producer; its eight normative files, analysis sources, preview sources and completed observation hashes verify. **All 168 chain-S protected bindings remain unchanged**, including the installed driver and backend. Evidence: `logs/r1_round33/final-integrity-check.json`. New fixtures live under `assets/runs/pc_cap/R1/rehearsal_fixtures/round33/`.

## Successor package requirements

R1-49m did not switch the current assembler's D.2 default closure while its full package lane remains blocked. R1-63m must use `r1_49m_normative_closure.closure`, D.3 protocol/matrix bindings and both new analysis modules; carry the policy through the copied final matrix cells and bind the new analysis hashes in publication evidence. Update/rehearse the D9 input/receipt and candidate chain against those exact identities. Existing candidate v13/request digests remain historical. Do not use a new policy string to reinterpret old signed bytes.

The cost validator now rejects revision 4 explicitly until its own validator exists. It preserves original/explicit revision 2 and invokes revision 3's supplement; ten dispatch tests prevent unknown-version bypass. This closes a preexisting weakness but **does not complete R1-58l**. Its v4 validator, transfers (CounterFact per-position sample ratio, S1 extra original-base forward, 1,000-record occupancy and unmeasured condition costs), near/revision gaps, memory qualifications, failure charging and revised process-hour projection remain required. No missing measurement or transfer approval was invented. The October 9 stop, 750 process-hour cap, 1.5× solo margin and single 1.15× two-worker adjustment remain unchanged.

Work is uncommitted for the lead. Existing-file changes are the two analysis consumers, HT-6 generator/renderer, typed-cost dispatcher and HT-6/R1-58l task records. New files are the D.3 protocol/matrix/producers/policy/closure, concentration helper, three test modules, applied analysis patch, task/claim/handoff records and round-33 evidence. Owner progress/log/result files and earlier untracked fixtures were left untouched.
