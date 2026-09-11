# ENV-05 — environment recreation

Status: implementation and dependency-resolution validation complete; real installation
and runtime validation unexecuted. Owner: Codex. CPU/network only; no GPU use.

## Deliverables

- `scripts/setup_venv.sh`: executable wrapper accepting `PCCAP_SETUP_PYTHON`.
- `scripts/setup_venv.py`: Python 3.12 helper; exclusive new environment/evidence paths;
  unchanged lock; exactly one private editable entry removed from a scratch copy;
  local checkout install in real mode; revision and dirty-path provenance; pip check
  and CPU determinism report after real installation.
- `docs/tasks/ENV-05-environment.patch`: proposed “Recreating the environment” section.
  Prepared for review, **not applied** to the existing environment document.

## Validation and evidence

The first invocation created `../assets/envs/venv-check` but its pip dry run failed on
sandbox DNS. `results/ENV05/venv-check/setup.json` correctly remains `status=failed`.
A network-approved retry used that scratch Python and the original scratch filtered
lock with `pip install --dry-run --no-input --no-compile --report ... -r ...`.
`results/ENV05/network_check/resolve_lock.txt` records the successful resolution;
`pip_report.json` contains package versions, origins and distribution hashes.
`verification.json` independently compares all **150** resolved package names/versions
with the retained lock pins and records refusal controls for the active and existing
scratch environments. The private editable line is the only removed entry.

Three in-memory lock-filter controls, Ruff, and shell syntax validation passed.
Neither dry run installed `pccap` or the resolved dependencies. The bare scratch venv
is therefore not a usable recreation yet; full dependency installation, local editable
installation, `pip check`, and CPU determinism output remain unexecuted. GPU validation
is outside this lane. Python, resources and caches were placed under `assets/`; the
active venv, lock, sibling repositories and source reference artifacts were untouched.

The invocation recorded checkout `25c988b850371576975df6cd7d80267ca3476a23`
and `source_was_dirty=true`; this is not a clean-revision reproducibility claim.

## Reproduction and next checkpoint

See the proposed section for a fresh-destination command. The default scratch target
already exists and is intentionally not reusable. Every attempt gets a new result path.
Do not remove or overwrite a previous attempt to get a passing status.

The lead may apply the proposed documentation patch and mirror this completion record
into the task board. No existing file was edited and no commit was made for this lane.
A real editable install may rewrite repository packaging metadata, so it needs review
under the user's new-files-only rule before execution in this shared checkout.
