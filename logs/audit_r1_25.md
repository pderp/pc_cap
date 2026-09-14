# R1-X2: R1-25 repairs and Stage 2 redesign audit

2026-09-14. Read-only audit of HEAD `e9c22c42a918ad38d44897bfa17a187fdd155e72` and the installed revision modules. **The answer-sensitive support path, nonfinite-code rollback and semantic-configuration refusal are repaired. The full scientific gates remain open.** New CPU controls reproduce delta-selection, restoration/accounting and transaction defects. Current results establish useful development diagnostics; they do not yet establish the planned episodic reference or alternating base-learning comparison.

No GPU, training pilot, core edit, final-data emission, sealed-payload inspection or commit was performed for this audit. The orchestrator's active `cf_pool3k_pair_own_400` results are outside the audited completed-result set.

## Evidence and reproducibility

- `scripts/r1_25_reaudit.py` → `logs/r1_round3/r1_25_controls.json`: installed-code controls and before/after hashes of every revision module; the hashes match.
- `scripts/r1_25_edge_cases.py` → `logs/r1_round3/r1_25_edge_cases.json`: nondefault retrieval geometry, direct adaptation capacity failure, controlled loss-comparator experiment and development answer-length inventory.
- Reused `scripts/r1_23_boundaries.py` with a new output: `logs/r1_round3/r1_23_legacy_boundaries.json`. Two accepted support updates, six poisoned query labels, identical predictions, unchanged unrelated records and base/reusable weights; independent queries were explicitly reset.
- Reused `scripts/r1_23_audit.py`; `logs/r1_round3/legacy_audit.txt` records its expected incompatibility with the repair. It tries to read the rejected replacement that is now correctly removed and exits with `KeyError`. This obsolete probe assumption is not a failed rollback repair. The new audit covers that case without modifying the old script.
- Twenty-five existing tests pass across `test_learner_cpu`, `test_contracts_memory`, `test_reader_controller`, `test_train_reference` and `test_epc_surrogate` (30.62 s). Twenty-six new namespace/control tests pass separately (0.82 s). These are selected CPU checks, not a full GPU/system certification.

Run diagnostics with `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python`, always supplying a **new** output path. The original controls are preserved.

Specification: `docs/more_input/pc_cap_coding_agent_guide (1).pdf`, especially pp. 5–6; `docs/updated_plan9.md` R1-21/R1-22; DEC-033/034. Responses: `docs/tasks/R1-23-response.md`, `docs/tasks/R1-X1-response.md`. Implementations audited: `adapt.py`, `memory.py`, `learner.py`, `reader.py`, `controller.py`, `train.py`, `epc_train.py`, plus shared evaluator and pilot call sites.

## Disposition of the previous ten findings

| Prior finding | Current disposition | Evidence / remaining checkpoint |
| --- | --- | --- |
| R23-01 loss normalization | Declared approximation; contract gap remains | New prose declares a prefix **sum**, while the loss table still specifies means. Guide p. 5 and plan R1-21 require each component normalized by its own count. Finite differences prove the implemented sum, not compliance with the requested mean. Correct the table and either implement normalization or obtain an explicit plan amendment. |
| R23-02 support answer absent; no fast unroll | Answer path repaired; differentiable adaptation still absent | Holding prompts fixed and swapping supplied answers preserves keys and changes codes. Five `own_prompt` queries are added from supplied supports. `LossConfig(fast_steps=1)` now refuses. This is good admission behavior; the reference unroll remains a required separate implementation or amendment. |
| R23-03 cap-only ePC called alternating | Renaming repaired; base-learning work remains | The new name “ePC-credit surrogate for cap weights” is accurate. Freezing the base during **editing evaluation** does not remove the plan's **training** base phase. Guide pp. 5–6 and plan R1-21/R1-22 explicitly require declared base masks and a matched alternating BP/ePC pair. |
| R23-04 failed revision retires old record | Nonfinite-code repair verified; broader transaction gap | The nonfinite code fixture restores the exact old state and removes the replacement. No-improvement intentionally retains the answer-derived replacement, as the response declares. The new delta capacity exception still leaves a supersession in place outside `ItemGuard` (X25-03). |
| R23-05 independent prefix-related queries share selection | Open | Fresh `[5,6,7]` gets prompt length 3; after an independent `[5,6]` query it inherits length 2. Explicit resets work. An assertion about sampled development prompts does not establish correctness for all paraphrases, locality inputs, generation prefixes or future data. |
| R23-06 semantic snapshot configuration | Repair verified | Changing single-site, null threshold, binary mass or hard top-1 each causes import refusal. Config integrity does not catch omitted weight-byte accounting (X25-02). |
| R23-07 memory ceiling excludes weights | Partially repaired | Initial accounting includes reusable weights. Restore loses them, constructors accept an already exceeded ceiling, and fixed metadata/index assumptions do not describe the actual representation (X25-02). |
| R23-08 cost reconciliation | Open and relevant to R1-24 | First empty-memory prediction calls the base once but returns zero full forwards. Direct outer-gradient calls remain outside the ledger; learning tokens include nontraining work. A synchronized pass ledger is needed before matched-compute claims. |
| R23-09 unsupported ePC code penalty | Repair verified by refusal | Nonzero `w_code_norm` raises `NotImplementedError`. Both compared estimators must use the supported zero setting until implemented. |
| R23-10 candidate geometry differs from trained score | Typical cosine path improved; not fully repaired | Store defaults to cosine, consistent in ordinary nonzero default cases. `ReaderConfig(cosine=False)` does not change store geometry, and the two cosine epsilon definitions disagree near zero (X25-05). |

## New findings

### X25-01 — High: a zero-weight candidate delta suppresses another record's controller

`learner.py:140` collects every candidate with a non-None delta, including candidates with weight zero. With hard top-1 weights `[1,0]`, a selected record **without** a delta and an unselected record **with** a delta produce a non-None all-zero mixed delta. Because deltas replace controller writes, the selected record's otherwise valid controller write disappears.

Reproduction: adding an unselected opposite-key record changes logits by **0.0897357464 maximum absolute difference**, even though its selection weight is zero. This affects mixed code/delta memories, including records whose delta adaptation failed to improve. It is not proof that every all-delta 100-edit pilot suffered this failure.

Owner repair/checkpoint: derive delta availability from positive-weight selected records; specify mixed code/delta semantics for soft mixtures. Test insertion, removal and supersession of irrelevant zero-weight records and require identical predictions for the unchanged selected record. Test variable-length delta padding separately.

### X25-02 — High: restored memory has the same hash but a different ceiling charge

`memory.py:188` reconstructs `RecordStore` without `weights_bytes`; export omits it too. `learner.import_state` replaces its correctly initialized store with that reconstructed store. The tiny fixture reports **7,828 B before restore and 212 B after restore**, with the **same state hash**. The missing 7,616 B are precisely its reusable parameters. At the current 3,348,226-parameter default, the analogous omitted float32 weight allocation is **13,392,904 B**.

The constructor also accepts a one-byte ceiling with 7,616 B of weights already present. `from_state` appends records directly without validating the resulting total. A record with a 10,000-character ID passes a 256-byte ceiling while reporting 184 B, yet its serialized arrays plus records JSON already require at least **10,141 B**. The actual Python strings, list/dictionary index and object overhead are additional. The response's “128 B metadata and 0 B index are what the implementation uses” is therefore not literally correct.

Owner repair/checkpoint: serialize or deterministically rederive reusable-weight charges, validate them against the loaded parameter tree, and enforce the ceiling at construction/import. Choose and document a persistent-representation accounting convention. Either store bounded fixed-width metadata or charge actual encoded metadata; measure working-memory overhead separately. Hash the accounting-relevant state. Require identical `memory_bytes()` before/after snapshot and rollback, including deltas, inactive revisions and long IDs.

### X25-03 — High: failed delta allocation leaves a replacement active in the direct API

`adapt_record` inserts/supersedes before running the adaptation. `memory.set_delta` can then raise `CapacityError` after the answer's multi-position delta is constructed. In the real tiny-base reproduction, the error is raised, state changes, the old record becomes inactive and the replacement remains present.

The shared stream runner normally wraps edits in `ItemGuard`; that is a separate protection, and its restore path encounters X25-02. Direct callers, including episode adaptation paths, cannot assume that guard. This finding is an API transaction failure, not a claim that every stream retains the bad item.

Owner repair/checkpoint: reserve the complete record budget before mutation or implement exception-safe rollback around the entire adaptation. Force failures at observation, insertion, each code/delta update, and final allocation; assert the old active record, hash, byte charge and lookup results are restored while failed compute remains charged.

### X25-04 — Medium: the delta acceptance baseline and combined configuration need explicit semantics

`adapt.py:127` enters delta adaptation only when `fast.steps == 0`. A configuration with one code step and five delta steps is accepted but runs only the code path; no delta is stored. Refuse the combination or implement/document sequential phases.

`_delta_steps` starts from zero deltas (cap-off loss), but accepts the final delta against `loss0` from the **code/controller path**. A controlled loss oracle has controller initial loss 100, delta initial loss 1 and delta final loss 2; the worsened delta is accepted because 2 < 100. This isolates the comparison rule; it is not an observed GPT-2 trajectory. Choosing the better representation can be intentional, but the current “loss fell” trace conflates two baselines and can also reject a useful cap-off improvement if the controller starts better.

Owner checkpoint: log controller baseline, zero-delta baseline and final delta separately. Decide whether the rule selects the best representation or enforces improvement along the delta trajectory. Test both directions and the equality/nonfinite cases. Current per-prefix steps project into the aggregate bound, but do not require monotonic loss decrease after every step.

### X25-05 — Medium: candidate retrieval and learned score still disagree in supported configurations

The supplementary noncosine fixture uses query `(1,1)`, keys `(10,0)` and `(1,.1)`. Training dot scores are 3.5355 and .3889, so training prefers the first; the cosine store returns the second. The initial main audit's different noncosine fixture did **not** demonstrate a rank reversal; the supplementary result supplies the discriminating case.

For default cosine, the reader normalizes by `sqrt(sum(x*x)+1e-8)`, while the store divides by `norm(x)+1e-8`. Query `(1,0)`, keys `(1e-6,0)` and `(1e-4,1e-4)` give training scores .099995 and 5.77350, while the store ranks the first key highest. These tiny norms are constructed, not measured prevalences in the active GPU run.

Owner checkpoint: share one scoring function and normalization convention, wire the metric from config, and test zero/tiny/large norms, exact ties, masks and top-k recall against full-population scores. Update old memory/response prose that still describes dot or L2 ordering.

## What the redesign now trains versus what it deploys

The current reader has tied query/key heads, cosine scores with scale 10 and a pairwise null head. The null sees the query, best key and their elementwise product. Deployment uses hard top-1, a hard-null decision, binary non-null write mass, and per-answer-position deltas replacing the code controller. Teacher support legitimately determines those delta positions and their values; this audit found no query-answer parameter added to prediction.

The outer training objective still learns through soft full-record mixtures and **initial code/controller writes**, without the support delta adaptation used in the successful deployment path. Thus trained retrieval gradients optimize answer production through a mechanism largely bypassed at deployment. `own_prompt` supervision addresses one real omission, but does not by itself align these objectives. The loss table also omits this newly added role and still describes configurable nonzero fast steps that the implementation now rejects.

Recommended bounded next experiment: hold observation geometry and the successful support delta rule fixed; first train only a pairwise applicability/null decision using own prompts, paraphrases and hard same-relation/different-subject negatives. Measure support acquisition, supporting-record recall, accepted wrong-record rate and null error by query role separately. Compare random and trained encoders under the same gate before retraining the whole controller. If training through stopped support deltas is chosen, name that surrogate explicitly; keep the differentiable fixed-unroll reference as a separate gate. No new sweep was launched by this audit.

The completed notes already support this direction: random tied geometry with cosine gate .93 yields zsRE ES/RET-GS/LS **1.00/.65/1.00**, but CounterFact **1.00/.18/.16**. Applying the same gate to trained pairwise-reader weights gives zsRE **1.00/.54/.92** and CounterFact **1.00/.02/.04**. These are selected development results from `docs/R1_stage2_notes.md`, not outcomes measured in this audit. They locate the current failure in scope/selection and domain transfer; they do not settle whether PC base learning helps.

## Storage and compute implications before scaling

An explicit delta costs **9,216 B per answer prefix**, not per fact. All 300 existing zsRE dev rows average 3.7367 answer tokens (max 13): average delta allocation **34,437 B**, maximum **119,808 B**. CounterFact's 300 dev rows each have two answer tokens: **18,432 B per record**. These are development inventories, not final-stream predictions. Weights, keys, codes, prompt tokens, metadata and inactive revisions add to these numbers. A mean-seven-token 1,000-edit stream already needs 64,512,000 B for deltas alone, leaving insufficient space under 64 MiB once current weights are included.

R1-24's selected completed pilot reports 493,752 learning tokens and 10,721 query tokens, yet its 4,443 s training wall time is not represented by the 58.60 s learning ledger total. Wall time alone cannot yield a correct pass count; it demonstrates why the ledger is not adequate for a compute frontier. Log each actual outer forward/reverse/relaxation pass with valid-token counts, independently identify training versus validation, and bill rejected/compiled work explicitly. Reconcile selected pilot budgets before calling continuation compute-matched.

## Handoff order

1. Repair X25-01/02/03 and explicit query boundaries; validate transactions and per-phase cost reconciliation on CPU, then one isolated real-base profile.
2. Update loss/algorithm declarations and decide the acceptance comparator, noncosine admission and metadata convention. Use a new revision/source manifest for subsequent results.
3. Finish the active own-prompt/pairwise-null run; compare it with random-reader + identical delta/gate controls, with role-level counts and the same development streams.
4. Review `exclusions_v2.json` and the new final namespace reservation. Data eligibility and final emission remain owner/lead actions.
5. R1-24 is implemented as a literal self-distillation negative control. Identical deterministic teacher/student checkpoints with fresh Adam and no decay have zero exact gradient. It cannot by itself exclude benefits from informative extra training. Agree a separate informative continuation treatment if that is the desired causal question; do not silently alter this control's teacher.
6. Implement/amend the normalized fixed-unroll reference and matched alternating base phases before the corresponding scientific claims. Stage 3 and confirmatory freeze still depend on these decisions and functioning audited Stage 2 behavior.

All proposed repairs above touch Claude-owned existing files and were left unapplied. The CPU lane is complete as an audit; accepting its findings does not mark the implementation gates passed.
