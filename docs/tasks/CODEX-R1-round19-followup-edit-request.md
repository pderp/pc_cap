# Round19 post-approval verification — two additional edits requested

Status: prepared and tested; **not applied**. Agent: Codex, 2026-09-16.
The three previously approved patches have been applied exactly. Their focused suite passes34 tests
and lint passes. Full MQuAKE spec inspection and the older queue regression tests then exposed these
additional issues. The standing new-files-only rule requires fresh permission for changes beyond
the three approved patches.

## 1. MQuAKE metadata-resource admission

Target: `scripts/r1_76_unseen_common.py`.
Exact patch: `R1-76b-metadata-resource-allowlist.patch`.
Current/proposed source hashes: `R1-76b-metadata-resource-edit-bindings.json`.

The v2 population spec now binds the approved cadence runner. Production validation accepts the
300-edit/outside100 population, but `load_spec` subsequently rejects its provenance resources
because the original loader allowed only repository metadata. The CPU review correctly recorded
resources outside the repo, as the project requires.

The proposed change allows **only** these three exact resolved paths for DEC-056 MQuAKE populations:

- `assets/data/prepared/revision_v1/r1_d4_v1/items.jsonl`;
- the current default GPT-2 snapshot's `tokenizer.json`;
- that snapshot's `config.json` (its existing symlink resolves to an HF-cache blob).

Each file must still match its already-bound SHA256. No model weights, generic assets directory,
sealed payload or arbitrary external path is allowed. Other population modes retain the existing
repository-only source rule. No GPU/model construction is needed for inspection.

Seven CPU tests run the proposed loader in memory, with a virtual spec binding the proposed source
hash. They inspect the real unchanged population/resources, reject hash drift separately for all
three files, and reject unrelated assets and sealed paths before reading them. Evidence:
`logs/r1_round19/r1-76b-metadata-resource-proposed-tests.txt` (7 passed,0.51s).
The observed current failure is in `logs/r1_round19/r1-76b-v2-spec-inspection.txt`.

After approval, create a **new v3 spec** binding the new runner hash; preserve v1 and v2. Inspect the
new spec without `--execute`, keeping the population itself unchanged. This is preparation only;
actual occupancy execution remains the orchestrator's task.

## 2. Legacy queue refusal-message assertion

Target: `tests/revision_v1/test_r1_77_queue.py`.
Exact patch: `R1-77b-legacy-firewall-test-message.patch`.
Current/proposed source hashes: `R1-77b-legacy-test-edit-bindings.json`.

The approved dispatch patch retains the refusal of `confirmation_draft` matrices but changes its
error text to `explicit development or confirmatory matrix scope required`. The older test still
matches `Final execution unavailable`. Correct only that expected message (formatter wraps it).
The test continues requiring a PermissionError and checks all405 draft slots remain incomplete.
No production code or launch behavior changes in this second patch.

Current old suite:10 passed,1 assertion failure,5.19s
(`logs/r1_round19/approved-queue-legacy-tests.txt`).
With the proposed assertion:11 passed,5.08s
(`logs/r1_round19/legacy-queue-proposed-message-tests.txt`).

Both patches pass `git apply --check`. Lint passes using each proposed file's actual destination
path (`logs/r1_round19/followup-proposals-lint-verified.txt`); a raw preview-path lint run classified
imports differently and is retained as diagnostic history. No existing test was edited to hide a failure.

Requested authorization: apply these two precise additional patches, write a new hash-bound MQuAKE
spec, and repeat the affected CPU validation. No draw, seal, freeze, GPU launch, staging or commit.
