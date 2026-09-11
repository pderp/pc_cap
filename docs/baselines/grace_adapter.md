# GRACE JAX adapter candidate (B4 / S2-05)

**PC-10 status: parity failure. Do not register B4 for confirmation.** The implementation
is in `pccap.baselines.grace_jax`; `grace_adapter.py` remains the existing placeholder.
The complete comparison is `results/S2/grace_jax/pc10.json`. Agreement on answers is
insufficient because the required learned-value arrays do not match.

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
from pccap.baselines.grace_jax import GraceLearner

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

The reference oracle fixes that boundary throughout decoding and teacher-forced NLL.
The candidate parity evaluator does the same. The generic harness decoder currently
does not pass this boundary; relying on the default last position after generated
tokens have been appended changes GRACE behavior. Therefore merely re-exporting this
class from the placeholder or registering it in `harness.arms` is insufficient.
A future integration must provide the boundary without changing query state. The
optional `last_logits_batch(seqs, phase, key_positions=...)` is a sequential fallback,
not a vmapped implementation, and needs those same original positions.

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

## PC-10 evidence

The gate validates reference artifact hashes before running all 20 isolated edits and
the 20-edit sequential run, then compares every isolated and sequential codebook and
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
Five synthetic adapter controls passed, including identity/read-only queries,
source conflict/radius behavior, restored future updates, snapshot rejection, and
bounded eviction. The full PC-10 test intentionally fails on this candidate.

```bash
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
  OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 ../venv/bin/python -B -m pytest \
  -p no:cacheprovider tests/baselines/test_grace_jax.py

# Expected to fail until a reviewed numerical repair passes the unchanged gate:
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
  OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 ../venv/bin/python -B -m pytest \
  -p no:cacheprovider tests/controls/test_pc10_parity.py
```

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
arithmetic have **not** been isolated; cross-framework rounding sensitivity is an
explanation supported by these measurements, not proof that all later differences
are harmless. Matching saturated outputs cannot satisfy state parity.

Next work should compare the frozen suffix's intermediate activations and value
adjoints against the source, checking normalization, GELU, softmax/cross-entropy and
fusion boundaries without adjusting hyperparameters, seeds, fixtures or tolerances.
Only an independently justified numerical repair followed by the unchanged complete
gate can unblock B4. Any change to existing candidate or harness files requires the
lead's permission under the current new-files-only rule.
