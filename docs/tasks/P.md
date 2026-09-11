# Lane P — reproduction pre-audit

Status: done for the assigned CPU pre-audit. Agent: Codex. Date: 2026-09-11.

Inputs: `docs/REPRODUCE.md`; recreated ENV-05 environment; source snapshot at `0d6e8d0a9f513ba7813b86074093b2bf26db9626`; independently copied static assets and historical development reports.

Outputs: `logs/reproduce_preaudit.md`; `logs/reproduce_round4/` exact command logs, per-command records, setup/source hashes, summary, follow-up record and selected generated evidence; additive `scripts/reproduce_preaudit_round4.py`. Source copy lives in ignored `pc_cap/.worktrees/reproduce_round4`; resource copies and checkpoints in `assets/tmp/reproduce_round4`.

Verify command: `../venv/bin/python -B scripts/reproduce_preaudit_round4.py` creates the isolated copies, then launches each documented CPU command in a fresh Bash shell using `assets/envs/venv-check-plan6-df/bin/python`. It forces CPU and sets PYTHONPATH/PCCAP_ASSETS to the copies. Supplemental exact invocations are in `logs/reproduce_round4/followup.json`.

Verify output: all 27 CPU commands attempted, 24 initial zero exits. The three nonzero results were an isolated-checkout sibling path, the documented asset path abbreviation and refusal to overwrite a complete copied grammar run. Follow-ups resolve each: full CPU suite 356 passed / 5 skipped / 52 deselected; pinned 52.5M-token shard rebuilt byte-exact; isolated grammar C2 rerun completes. Twenty-one other invocations are individually classified as GPU, illustrative, sealed creation or lead-only execution. No GPU command ran.

Done-when check: every CPU command has an outcome, stale commands/defaults and rerun semantics are identified, GPU/lead-only work is explicitly deferred, and empty post-confirmation outputs are not mislabeled completed experiments. Report and all evidence links validated.

Cost: GPU seconds 0. Initial sequence including copying 127.89 s. Supplemental full tests 66.40 s, grammar run 35.88 s in its metrics, shard tokenization 22.82 s. Some follow-ups were concurrent; these are not a single summed wall-clock duration.

Deviations: independent output/source/resource copies avoid altering live files or checkpoints. Historical source snapshot lacks its own Git metadata, and some model-identity lookups use hard-coded read-only paths; the generated draft is not a final freeze validation. The source copy excludes sealed realization payloads and real S4/S5/S7 results. Production freeze/queue activity began concurrently and is outside this audit's claims.

Unresolved: the final S8 audit must run on the final tree, address portability/documentation issues and coordinate GPU commands with the run owner. Existing REPRODUCE text was not edited, and no commit or task-board write was made.

Questions for lead: none required to complete the report. Applying the suggested existing-document corrections is a separate permission-gated action.
