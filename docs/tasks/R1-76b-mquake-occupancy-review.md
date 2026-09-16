# R1-76b — DEC-056 bounded MQuAKE occupancy population

Status: CPU review and versioned population complete; production runner cadence patch awaits permission.
Agent: Codex, 2026-09-16. GPU/model calls: zero. No final-register subject allocated; no owner result written.

| Filter | Rows remaining |
| --- | ---: |
| Historical train v2 plus legacy development | 1,200 |
| Remove selected-reader training identities and exact query overlaps | 700 |
| Conservative alias/context/role review | 657 |
| Cached teacher identity/answer-alias check, exact token reconstruction, vocabulary/context limits | 657 |
| Remaining cross-row subject/query collisions | 657 |
| Assigned edits / fixed outside | 300 / 100 |
| Unassigned reviewed reserve | 257 |

The 43 further exclusions are subject mentions in the selected reader's training query contexts.
The audit verifies the bound training prefixes (zsRE1,000 / CounterFact1,000 / MQuAKE500), exact
own/paraphrase/locality query strings, inherited verified aliases, NFKC/case/whitespace and
punctuation-token equivalence. It rejects final-register subjects across all three datasets.
It does not claim exhaustive external entity resolution or unknown-alias clearance.

Every emitted row is labelled **“new to the selected reader's training; historically exposed elsewhere”**.
Edits are the first300 surviving rows in historical source order; outside prompts are the next100.
The outside set excludes every edit including future fillers. The 1,000-record point is explicitly absent.
Historical locality/near-miss fields are omitted from the execution population because they are not
needed by this assay and can reference subjects outside the reviewed inventory.

Teacher eligibility is reproduced from the cached historical teacher generation, exact support fields,
answer aliases and current tokenizer. All657 pass. The historical teacher pool **does not record a
base-weight hash**: this is a cached development eligibility audit, not a newly certified final-base
teacher pass. The owner should preserve that limitation in the result report. Tokenization and context
limits are checked against the current pinned tokenizer/config without constructing the base.

Artifacts:

- `scripts/r1_76b_mquake_review.py`: reproducible CPU review and exclusive new-file writer.
- `logs/r1_round19/r1-76b-clearance.json`: filter counts,43 exclusion IDs/reasons, source hashes and limitations.
- `docs/tasks/R1-76b-mquake-historical-v1.population.spec.json`: identity-bound pending-runner spec.
- Resource: `/home/derp/cap/assets/runs/pc_cap/R1/r1_76_common/round19/mquake_historical_v1.json`.
- `docs/tasks/R1-76b-runner-cadence.patch`: narrow existing-runner change for explicitly labelled
  DEC-056 MQuAKE100/300, while retaining the original full cadence for other production populations.

The existing production validator deliberately rejects a truncated schedule. The proposed patch
accepts only MQuAKE, decision DEC-056, exactly `[100,300]`, missing `[1000]`, outside100 and every
required exposure label. Existing uniqueness/prompt/hash checks remain in place. Do not run a real
base with `test_fixture=True` to bypass this guard.

After the patch is approved/applied, create a **new spec version** binding the new runner hash.
The delivered v1 spec intentionally binds the inspected current runner and is not edited in place.
An owner can use this exact CPU-only rebinding step (exclusive output; fails unless the new production
validator accepts the population):

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python - <<'PY'
import json
from pathlib import Path
from scripts import r1_76_unseen_common as runner
old = Path('docs/tasks/R1-76b-mquake-historical-v1.population.spec.json')
spec = json.loads(old.read_text())
population = Path(spec['population']['path'])
assert runner.sha(population) == spec['population']['sha256']
runner.validate_population(json.loads(population.read_text()))
spec['runner_bindings']['scripts/r1_76_unseen_common.py'] = runner.sha('scripts/r1_76_unseen_common.py')
spec['status'] = 'prepared_not_executed_DEC056_runner_admitted'
spec['runner_status'] = 'DEC056 production cadence patch bound'
spec['supersedes'] = {'path': str(old.resolve()), 'sha256': runner.sha(old)}
with Path('docs/tasks/R1-76b-mquake-historical-v2.population.spec.json').open('x') as stream:
    json.dump(spec, stream, indent=2, sort_keys=True)
    stream.write('\n')
PY
```

The owner then inspects the new spec with `python -m scripts.r1_76_unseen_common --spec ...` and
uses the admitted MQuAKE primary-v5 constructor/recipe, explicit recipe hash, new result directory,
positive projected time and GPU lease for execution after the stress panel. Model execution remains
with the orchestrator. Occupancy shortfalls remain unavailable; no population changes after outcomes.

Verification: CPU tests reproduce657 survivors, protect exposure labels and absent1000, verify rejection
of unauthorized partial schedules, and preserve the existing full-size zsRE population. No board,
protocol, existing runner, result or reservation file was changed. Remaining request: approve the
prepared cadence patch; do not infer production readiness from the existence of the population file.
