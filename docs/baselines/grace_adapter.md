# GRACE JAX adapter candidate (B4 / S2-05)

**B4 eligibility: blocked on the unmet DEC-020 sensitivity prerequisite. Do not
register B4 for confirmation.** Canonical imports are available from
`pccap.baselines.grace_adapter`; the implementation and vmapped batch helper are in
`grace_jax.py` and `grace_batch.py`. Batch integration and its verified test corrections
were committed in `9bfd9a7`.

DEC-020 conditionally approves the label **“reference baseline, parity at the output
level”**. That label has not been earned: the same-framework sensitivity experiment
preserved outputs and losses but did not reproduce the required value-divergence scale.
The existing `results/S2/grace_jax/pc10.json` preserves the earlier elementwise parity
failure; it is not a completed form-(b) assessment.

## Source and binding

The read-only GRACE source is `../assets/third_party/GRACE`, revision
`f674183f17a995d109e10ee6140d4c3e6d016115`, primarily
`grace/editors/grace.py:57–204`. The reference manifest is
`manifests/dev/grace_parity_cases.json`, SHA-256
`05e640c00671449f8d739fc5dbd00431494b7f9e9568001f40776640fac6338a`.
The GPT-2 snapshot revision is `607a30d783dfa663caf39e06633721c8d4cfcd7e`.
Reference preparation and its intentional task bindings are documented in
`docs/baselines/grace_reference.md`.

The hook is `transformer.h[8].mlp.c_fc`. Its key is the **layer-normalized MLP input**
(768 dimensions), and the stored replacement is the **linear projection output before
GELU** (3,072 dimensions). Calling the key a block residual would be inaccurate.
`replace_prompt` replaces positions strictly before the prompt's last position; it
excludes the key-position token, exactly as the original source slice does.

## Interface and algorithm

```python
from pccap.baselines.grace_adapter import GraceLearner

learner = GraceLearner(base, block=8, radius=1.0, value_steps=100,
                       value_lr=1.0, seed=0,
                       ceiling_bytes=None, eviction="none")
outcome = learner.update_item(item)
logits = learner.predict(item.prompt_ids)
state = learner.export_state()
learner.import_state(state)
```

The frozen GPT-2 functions are reused through `pccap.bases.gpt2_jax`; no sibling
repository code is imported at runtime or modified. A within-edit cached prefix
reaches the hook once; only the chosen value receives gradients through the suffix.
The objective is mean answer cross-entropy including the shared newline delimiter.
Adam restarts each edit, uses lr 1, beta1 .9, beta2 .999, epsilon 1e-8, and runs
100 steps for parity. No base parameters are optimized.

Lookup uses Euclidean distance and first-minimum tie selection. The source's initial
radius, coverage expansion, conflicting-label admission and radius split are retained.
Its label comparison uses the fp32 mean of the full label sequence, including masked
`-100` positions. Its zero-distance conflicting-label behavior can leave the oldest
key with a negative radius and defer a tied query; the candidate preserves this
behavior rather than silently repairing the source algorithm.

Cold initialization reproduces the pinned PyTorch CPU MT19937 float sampler using
NumPy's integer MT output, the low 24 bits, and multiplication by 2^-24. It does not
use NumPy's floating-point uniform sampler. All unused cold draws made by the original
100 optimization forwards are consumed. Source oracle evaluation preserves RNG state;
candidate evaluation likewise does not advance RNG or mutate the codebook.

## Integration boundary: original prompt position

During greedy continuation, callers **must preserve the original prompt position**:

```python
logits = learner.predict(growing_prefix,
                         key_position=len(original_prompt) - 1,
                         last_only=True)
```

The reference oracle and candidate parity evaluator fix that boundary throughout
decoding and teacher-forced NLL. Claude's `GraceArm` declares
`decode_key_positions=True`, and the shared decoder and `harness.runs.Evaluator` now
pass original prompt positions through to the learner. The separate S7 scoring
findings and repairs belong to Claude's lane; see [the S7 review](../../logs/review_p4_s7.md).

The canonical `last_logits_batch(seqs, phase, key_positions=...)` now vmaps the
unchanged lookup and suffix. It groups inputs by the scalar path's padding width,
restores input row order, and charges every sequence and token to the requested
ledger phase. It does not mutate codebook metadata, RNG or learner-persistent caches.
An empty batch returns shape `(0, vocab)`; invalid boundaries are rejected before
model work. Each continuation retains its own original prompt boundary:

```python
last_rows = learner.last_logits_batch(
    [growing_prefix], phase="query",
    key_positions=[len(original_prompt) - 1],
)
```

The [applied integration record](../tasks/B4-S-batch-applied.md) reports 11 passing
GRACE/boundary controls. The canonical adapter also passed a CPU comparison on the
fixed final source codebook: 20 cases and 61 teacher-forced answer prefixes, with
unchanged base and learner state. Maximum summed-answer NLL difference was
1.902733e-7 and teacher-forced argmax agreed throughout. This verifies the batch query
path; it does not establish training parity, free-generation parity, or DEC-020
eligibility.

## State, costs, and SD-8 adaptation

Snapshots include keys, values, radii, full labels, use counts, allocation ages, item/
allocation/eviction counters, the complete MT state and position, seed, configuration,
base digest and memory limit. Import validates inventory, dimensions, dtypes, finite
values, base/config identity and accounting before replacing live state. Adam has no
state between edits because the source resets it each edit. Loss histories are returned
in the outcome and are not persistent learner memory.

`memory_bytes()` counts the complete serialized learner state, including RNG and labels.
It does not estimate Python interpreter overhead. Every optimization operation is
charged through `base.ledger` in the learning phase: one cached-prefix partial forward
plus 100 suffix partial forwards/reverses per edit. Predictions charge full forwards
in the requested phase. Counts describe actual candidate work; the cached prefix makes
its arithmetic cost different from 100 complete source-model forwards. CPU ledger
`accel_seconds` follows the repository's synchronized-wall-time convention and is not
GPU usage. No GPU work was done for this lane.

Optional `eviction="use_count_then_age"` enforces the byte ceiling after an edit by
removing the lowest-use entry, breaking ties by oldest allocation. To keep predictions
read-only, **use counts mean active learning lookups**, not evaluation queries. This
choice is an explicit SD-8 adaptation; it is disabled for parity. An impossible ceiling
or update exception restores the prior learner state; incurred ledger cost remains.
The bounded variant was checked with synthetic controls, not a GRACE source parity
claim or a long editing benchmark.

## Historical elementwise PC-10 evidence

The existing legacy gate validates reference artifact hashes before running all 20
isolated edits and the 20-edit sequential run, then compares every codebook and
all isolated/final-sequence evaluations. Tolerances were fixed before seeing real-case
results and were not widened:

| Quantity | Absolute tolerance | Relative tolerance |
| --- | ---: | ---: |
| Keys and radii | 2e-4 | 2e-5 |
| Values | 2e-3 | 2e-4 |
| Complete-answer summed NLL | 1e-3 | 1e-4 |
| Greedy token IDs and labels | exact | exact |

| Check | Isolated | Sequential |
| --- | ---: | ---: |
| Keys, radii, labels | 20/20 each | 20/20 snapshots each |
| Learned values | **0/20** | **0/20 snapshots** |
| Greedy output and NLL | 20/20 | 20/20 final evaluations |

The largest isolated value discrepancy is **22.4391**, far beyond tolerance.
The maximum NLL difference across all 40 evaluations is **4.2486e-5**.
The base checksum was unchanged. The CPU parity measurement took 57.7293 seconds;
its ledger counts 4,040 partial learning forwards and 4,000 reverses for 40 updates.
Five synthetic adapter controls passed in that run, including identity/read-only queries,
source conflict/radius behavior, restored future updates, snapshot rejection, and
bounded eviction. The unchanged elementwise PC-10 test still fails on this candidate.
Its retained failure is separate from the outstanding form-(b) implementation and
acceptance checks.

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
  OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 ../venv/bin/python -B -m pytest \
  -p no:cacheprovider --basetemp=../assets/tmp/b4_adapter_controls \
  tests/baselines/test_grace_jax.py tests/baselines/test_grace_batch.py \
  tests/harness/test_b4_wiring.py

# Historical elementwise gate; expected to fail on the current candidate:
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
  OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 ../venv/bin/python -B -m pytest \
  -p no:cacheprovider tests/controls/test_pc10_parity.py
```

## DEC-020 sensitivity and conditional form-(b) gate

The [policy](../tasks/B4-S-sensitivity-policy.json) was written before execution.
The [full result](../../results/S2/grace_jax/sensitivity.json) records all 20 isolated
cases at steps 1, 10 and 100; the [interpretation](../../logs/grace_sensitivity_round3.md)
retains the negative result. Original seeds, initial-value RNG and Adam settings were
held fixed.

| Same-framework control | Maximum step-100 value gap | Loss-trajectory checks | Final greedy / NLL checks |
| --- | ---: | ---: | ---: |
| Initial value + float32(1e-7) | 0.073916 | 60/60 | 20/20 each |
| Algebraically equal hook addition reassociation | 0.152517 | 60/60 | 20/20 each |

The declared reproduction threshold was 2.243913, one tenth of the previously observed
cross-framework maximum 22.439135. The algebraic control did not reach it. Both
controls exceed 0.001, so the recorded verdict is `inconclusive_or_equality_failure`:
the cause is insufficient divergence magnitude, with no output/loss equality failure.
The experiment took 98.33 seconds on CPU and left the base unchanged.

At each selected step, mean training loss was multiplied by answer-token count
(including newline) and checked using the unchanged summed-answer NLL tolerance:
absolute 0.001, relative 0.0001. No loss tolerance was fitted or widened. A completed
form-(b) assessment must retain keys/radii/labels and greedy/NLL checks, compare loss
trajectories at steps 1/10/100 for both isolated and sequential updates, report
elementwise value gaps as descriptive quantities, and record a qualifying sensitivity
verdict. Those conditions are not yet met; neither B4 availability nor S3-01 completion
follows from the implemented batch interface.

## Failure diagnosis and next checkpoint

`scripts/grace_numerical_trace.py` observes the original optimizer in the approved
CPU-only auxiliary reference environment and compares JAX trajectories for case 0
and case 1 (the largest isolated discrepancy). Diagnostic arrays are new resources
under `assets/reference/grace_diagnostics/first_steps_20260911`; the immutable oracle
fixtures were neither regenerated nor changed. Observed source final values match
the corresponding original fixtures **exactly**, and both initial random values match
JAX exactly.

The first gradient already differs: relative L2 errors are approximately 2.20e-4 and
1.28e-4; maximum absolute errors are 6.42e-6 and 3.58e-6. There were no sign differences
in the separately compiled first-gradient probe. The actual compiled optimization
loop yields first-step value discrepancies .00490 and .04774, increasing to .35343
and 22.43913 after 100 steps. Replaying the fixed source gradients through JAX's
first-step Adam expression reproduces source values within 2.99e-7.

This localizes the initial divergence to the gradient/compiled-model arithmetic,
rather than random initialization or an obvious first-step Adam coefficient error.
The separately compiled gradient probe and the fused optimization loop also have
slightly different fp32 losses. The exact responsible primitive and later optimizer
arithmetic have **not** been isolated. The subsequent same-framework control
demonstrates some sensitivity but does not explain the 22.4 cross-framework gap or
exclude an adapter defect. Matching saturated outputs does not satisfy DEC-020's
additional prerequisite.

Next work should compare the frozen suffix's intermediate activations and value
adjoints against the source, checking normalization, GELU, softmax/cross-entropy and
fusion boundaries without adjusting hyperparameters, seeds, fixtures or tolerances.
Preserve the existing references and predeclared tolerances. A future conditioning
control needs its verdict rule stated before execution; do not search perturbations
until the desired label becomes available. The next acceptance checkpoint requires
the complete isolated/sequential comparison and a justified sensitivity verdict under
DEC-020. Batch implementation is complete; the numerical diagnosis remains open.
