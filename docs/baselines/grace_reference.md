# GRACE reference implementation and B4 eviction design

Status: source review, CPU environment preparation, runner, and non-editor controls complete; source-editor execution is waiting for the Setuptools compatibility permission described in `docs/tasks/S2-05a-environment-edit-request.md`. No successful-edit result or completed parity fixture is claimed yet. This document records the implemented reference algorithm and the proposed adapter design; completion evidence will be a new task addendum.

## Source and environment

Read-only source: `/home/derp/cap/assets/third_party/GRACE`, commit `f674183f17a995d109e10ee6140d4c3e6d016115`, matching DATA-00's `manifests/datasets.json`. No license file is present in the pinned clone; the inventory records license as unknown. No source file is copied or modified. The standalone CPU runner imports the original `grace.editors.grace.GRACE` class directly. The notebook uses a different barebones class and a T5 example; it is not a GPT-2-small default.

The published `environment.yml` pins Python 3.9.7, torch 2.0.0, Transformers 4.20.1, NumPy 1.24.3, and wandb 0.13.2, among full-experiment dependencies. This task created `assets/envs/grace` using Python 3.10.20 and CPU-only torch 2.0.0+cpu, with the same Transformers, NumPy, and wandb versions. Python 3.10 provides compatible binary wheels while the project itself continues to run under its existing Python 3.12 JAX environment. Only packages needed to import the reference editor and produce/test fixtures were installed; Hydra, datasets, and experiment-tracking execution are not used. Resolver output is in `results/grace_lane_d/environment_install.txt`.

The original REF-01 environment was inspected read-only. It has newer torch/Transformers/NumPy versions and lacks wandb; its import failure is recorded in `reference_env_preflight.txt`. The new GRACE environment has a separate packaging incompatibility: wandb 0.13.2 imports `pkg_resources`, omitted by its newly resolved Setuptools 84.0.0. A pin to 78.1.0 is proposed but not applied. W&B initialization is never called; tracking is disabled. Both pre-existing environments and all reference repositories remain unchanged by this lane.

## Defaults and GPT-2-small binding

| Setting | Pinned clone | Planned reference binding |
| --- | --- | --- |
| Architecture | GPT-2 XL, 48 blocks | Pinned GPT-2 small, 12 blocks |
| Editable module | `transformer.h[35].mlp.c_fc` | `transformer.h[8].mlp.c_fc` |
| Initial radius | 1.0 | 1.0 |
| Distance | Raw Euclidean distance | Unchanged |
| Value initialization | `cold`, uniform random [0, 1) | Unchanged |
| Value optimizer | Adam, lr 1.0 | Unchanged |
| Iterations per edit | 100 | Unchanged |
| Replacement | `replace_prompt` | Unchanged |
| Radius expansion | `coverage` | Unchanged |
| Byte ceiling | None | None for the reference fixtures |

Sources: `grace/config/model/gpt2xl.yaml:5`, `grace/config/editor/grace.yaml:2`, and `grace/editors/grace.py:57` in the read-only clone. **The clone supplies no GPT-2-small default.** The binding maps the XL location by relative depth: `(35 + 1)/48 = (8 + 1)/12`. This is an explicit port choice for reference construction, not a source-authored small-model default, development optimization, or frozen scientific choice. Layer/radius selection for B4 remains the orchestrator's development task.

Transformers 4.20 predates its native safetensors loader. The runner creates its `GPT2LMHeadModel` from the local config and maps every pinned safetensors parameter directly into the legacy model. Every named parameter is checked for exact equality and fp32 dtype. The only missing checkpoint tensors in the successful preflight are twelve deterministic legacy `attn.masked_bias` buffers. No model download or new model weight file is needed. Evidence: `results/grace_lane_d/legacy_model_load_check.json`.

## Algorithm as actually implemented

1. **Freeze and wrap.** `GRACE.__init__` freezes the base parameters and replaces the selected module with `GRACEAdapter` (`grace.py:20–46`). GPT-2 Conv1D weights have `[input, output]` storage. For the selected MLP expansion, each key is width 768 and each learned replacement value is width 3072. These are MLP projection inputs/outputs, not the cap's residual-write sites.
2. **Query and key position.** For the autoregressive task, `edit` sets `key_id = count(labels == -100) - 1` (`grace.py:57–64`). With this task's unpadded batch size one, that is the last prompt token. The query is the selected module's input vector at that position, after the block's preceding layer normalization. The code does not normalize it to a unit vector (`grace.py:150–155`).
3. **Empty codebook.** At inference before any edit, return the original layer output. The first edit stores the detached query, a trainable cold-initialized value, radius 1.0, and the full label tensor (`grace.py:128–159`).
4. **Admission on iteration zero.** Find the nearest stored key by `torch.cdist(..., p=2)` and the first minimum in insertion order. If its distance is strictly greater than `initial_radius + nearest_radius`, append a new key/value/radius/label entry. Otherwise inspect label compatibility (`grace.py:160–174`).
5. **Label matching.** The actual test is equality of `edit_label.float().mean()` and `key_label.float().mean()` (`grace.py:134–135`). It is not answer-string, token-vector, or fact-identity equality. Ignored prompt labels (-100), label length, and the answer tokens all affect that mean. Reference snapshots retain complete label tensors so a future adapter can reproduce this behavior and test any intentional correction separately.
6. **Expansion or split.** For matching label means and a query outside the current nearest radius, the default `coverage` policy sets that radius to the distance. For conflicting means, append a new entry and set the old radius to `distance/2 - 1e-5` and the new one to `distance/2`. At zero distance the old radius can therefore be negative; it must not be silently clipped in a parity implementation (`grace.py:137–139`, `172–183`). The optional moving-average path moves keys, but it is not the default.
7. **Retrieval and deferral.** Find the nearest key again; substitute its learned value only when the distance is at most its radius. Otherwise preserve the original layer output. The executed path always uses Euclidean distance; alternative distance names in comments do not provide implemented alternatives (`grace.py:189–204`).
8. **Replacement span.** Default `replace_prompt` writes `layer_out[:, :token_to_edit]`. The upper endpoint is excluded: the key-position token itself is not replaced. For a last-prompt key at position `p`, the replaced positions are `0 ... p-1`. `replace_last` and `replace_all` are different supported modes and are not silently substituted (`grace.py:199–204`).
9. **Optimization.** The first edit forward instantiates the values before a new `torch.optim.Adam` is created over the model's parameters. Frozen base weights have no gradients. The loop runs all 100 iterations, backpropagating the model's masked next-token cross-entropy, then marks the adapter non-training. Despite the config string `val_train: sgd`, the optimizer is Adam; the `reg: early_stop` config does not cause an early stop in this method. Adam state is recreated for every edit and does not persist between complete edits (`grace.py:66–91`).
10. **Persisted and transient state.** Keys, learned values, radii and full labels determine subsequent edits and predictions. Keys/radii/labels are plain attributes rather than all being registered state-dict buffers, so saving only `model.state_dict()` would omit necessary state. The runner exports them explicitly. Query key position, chosen-key index, iteration, and cold-initialization RNG also require deliberate treatment when reproducing a run.

## Reference protocol and additive runner

`scripts/grace_reference_oracle.py` implements a standalone reference driver, not the JAX B4 adapter. `manifests/dev/grace_parity_selection.json` records the prepared cases and input-manifest hashes. It selects the first ten eligible single-token and first ten eligible multi-token answers in development-manifest order, excluding every S0 item ID. Stratum lengths exclude the mandatory newline terminator. The planned five smoke cases are the first five single-token cases, chosen before observing any edit result.

The driver uses the shared stored prompt/answer token arrays and verifies each against the legacy GPT-2 tokenizer. Answer IDs include the common trailing newline; this differs from upstream `tokenize_gpt`'s EOS suffix. The standalone tokenizer preflight matched all 20 cases. Training masks only the prompt labels and calls the original editor without changing its update algorithm. The model is fp32/eval, with dropout zero, CPU-only, deterministic algorithms, and two intra-op threads.

Each isolation run starts with a fresh base and empty codebook and seed equal to its case index (0–19). The sequence run starts fresh at seed 0, processes the same twenty cases in order, stores a codebook after every edit, then evaluates all twenty at the final codebook. Greedy decoding recomputes the full prefix with no cache, at most 32 generated tokens, stopping at newline or EOS. The GRACE query position stays at the end of the original prompt during each continuation. Scoring compares normalized complete generated text to the canonical target; teacher-forced NLL is recorded separately.

The source allocates an unused random cold value on inference forwards and updates transient chosen-key bookkeeping. The driver saves/restores the CPU RNG and transient query fields around evaluation and asserts that codebook contents remain unchanged. This declared wrapper policy prevents evaluation frequency from changing future random initializations, and must be matched by the parity driver. It leaves each evaluated numerical output unchanged. There are no source monkey patches.

Planned outputs, all created exclusively:

- `results/S2/grace_reference_smoke.txt`: exact command/environment/config, the five predetermined item IDs, per-item losses and greedy/NLL results, and success count. The driver stops if no case matches its target.
- `assets/reference/grace/environment.json`: versions and full package inventory, config, pins, loading and evaluation conventions.
- `assets/reference/grace/isolated/00..19.json` and matching `.codebook.npz`: per-isolation results, complete keys/values/radii/labels.
- `assets/reference/grace/sequence/00..19.codebook.npz` and `sequence_final.json`: per-edit codebooks plus all final evaluations and update-loss histories.
- `manifests/dev/grace_parity_cases.json`: twenty case IDs, strata, file hashes and byte sizes, source/input/environment hashes, exact invocation and CPU cost. This manifest is written only after successful generation.

The `--check` path uses NumPy only and rehashes every input and output, checks deterministic selection, codebook dimensions/fp32/finite arrays, label/radius counts, and output references. The NPZ archives require no pickle. Existing output directories, manifests, and smoke logs are refused; retries must not overwrite a partial run without permission.

## Eviction adaptation for the future JAX B4

The reference has no byte ceiling, eviction counters or bounded label store. The fixtures keep eviction **disabled**, as required for the PC-10 comparison. Enabling the byte-bounded adaptation changes future retrieval and edit behavior and must be reported as a separate mode.

There is an unresolved wording conflict: latest `ongoing3.md` requests **least recently used** eviction, while committed SD-8 in `docs/spec_defects.md` and `ongoing.md` specify **lowest use count, then oldest**. Pure LRU and that frequency-first rule are different. This reference task implements neither and changes no decision file. The design below gives both precise alternatives for the adapter owner to resolve before implementation/freeze.

1. Measure all allocated mutable bytes: keys, values, radii, stored labels or a parity-validated exact label representation, occupied/free indices, stable insertion IDs, use/recency fields, and counters. Use the same numerical ceiling `B_cap = 6144 * (8 * 768 + 128) = 38,535,168` bytes. Do not borrow the cap's slot count: GRACE's value width is 3072, so its per-entry cost is much larger.
2. Account for optimizer state. Active Adam moments add two fp32 arrays matching the whole values parameter, not just its currently selected row. They are recreated during every edit and discarded afterward. Reserve or otherwise explicitly bound/report these active mutable bytes as well as retained codebook bytes; report peak activation/workspace memory separately. The exact capacity follows measured arrays/metadata rather than an asserted slot count.
3. Under the latest lane's LRU interpretation, evict the entry with the oldest **completed-learning-use** timestamp; ties use insertion order and then stable entry ID. Query evaluation cannot update recency. A slot is counted at most once per complete edit, matching the project's evaluation-read-only rule.
4. Under SD-8's existing interpretation, evict the lowest completed-edit use count, then oldest completed-learning-use timestamp, then stable ID. Maintain a bounded per-item use set and snapshot it; again queries never update it. This preserves the named frequency-first rule rather than relabeling it LRU.
5. Prepare admission/split and eviction together. Preserve the nearest entry needed for a split while reserving the new entry's space; if the required pair cannot fit, emit an explicit capacity failure instead of silently altering the split radius. On error/resource stop restore the pre-edit codebook, counters, topology and RNG while retaining incurred cost.
6. Keep stable insertion ordering for equal-distance retrieval ties when recycling storage. Removing rows and reusing a physical slot must not accidentally change the source's first-minimum tie rule.
7. Log evicted identity, allocated bytes before/after, use/recency values and reason. With eviction disabled, no extra counter or capacity branch may change source outputs/codebooks on the 20 reference cases. With eviction enabled, capacity/retrieval differences are intentional and reported, not failures concealed by a relaxed parity tolerance.

Additional deliberate differences to disclose in B4 are the small-model layer mapping, common tokenization/decoder, inference RNG preservation, and any proposed correction of mean-label matching or prompt-span replacement. Those last two source behaviors are preserved in the reference; improving them silently would invalidate the reference comparison.

## Current verification boundary

`tests/reference/test_grace_reference.py` contains four writer/selection controls and two direct source-adapter controls (expansion/split/deferral and exact prompt-span/RNG behavior). **Four writer/selection controls passed in 0.08 seconds; the two source controls have not run yet** because the source import requires the dependency pin. Ruff passed for both new Python files before creation. The legacy GPT-2 parameter-load and twenty-case tokenization preflight passed independently of the blocked editor import. No GPU was used, and no GRACE editing result, JAX parity pass or scientific checkpoint is asserted.
