# R1-D4b — self-contained MQuAKE slices

Status: done (prospective slices delivered; historical capacity not repaired). Agent: Codex. GPU seconds: 0.

Inputs: training pool v1 (500 items), original development manifest (first 100 of 200), teacher-eligible pool, prepared MQuAKE records, register v4 and its rebound supplement v1. Existing files remain unchanged.

Outputs: `scripts/r1_d4b_self_contained.py`, `tests/revision_v1/test_self_contained_slices.py`, `manifests/revision_v1/train_pool_mquake_v3.json`, `manifests/dev/mquake_dev_v3.json`, `manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json`, and `logs/r1_round11/d4b_capacity_run.json`.

Every original support field, including target, tokens, aliases, paraphrases and identity, remains unchanged. Only locality prompts/answers and near-miss candidates change. Each item gets two other items from its own slice, preferring its relation and breaking ties by item ID. Scarce relations use a labelled other-relation fallback: 18 neighbour references in training and 18 in development. The references use the source's original `target_true`; no new teacher-agreement claim is made. Near-miss prompt tokens are retained; target tokenization can use the shared tokenizer when an endpoint is constructed. The development unrelated list is the deduplicated union of its own locality prompts (52). Training has 92 distinct locality prompts. No cross-slice queries are introduced.

| Exposure reading | zsRE items / subjects | CounterFact items / subjects | MQuAKE items / subjects |
| --- | ---: | ---: | ---: |
| Prospective 500+100 only; historical MQuAKE work hypothetically absent | 52,498 / 52,498 | 12,246 / 12,246 | 5,180 / 4,818 |
| Cumulative history retained, effective supplement v2 | 52,411 / 52,411 | 12,246 / 12,246 | 2,171 / 2,100 |

The new slices reserve exactly 600 primary subjects; locality and unrelated query subjects are subsets. The 4,818-subject figure is a counterfactual, not an available fresh population. Prior training used pool v2 (1,000 items), and prior development used original query lists. A smaller retraining run cannot erase that history. Supplement v2 retains all prior exclusions and releases zero subjects. CounterFact still requires the reason-specific source exception; other gates remain open.

Verification: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= /home/derp/cap/venv/bin/python -m pytest tests/revision_v1/test_self_contained_slices.py -q -p no:cacheprovider`. Four tests pass; full installed suite: 479 passed, 8 skipped (54.59 s). Capacity generation command: `python -m scripts.r1_d4b_self_contained --write` from the repo with the same CPU environment; it refuses to overwrite outputs. The initial direct-script invocation failed to resolve the `scripts` namespace; the module invocation succeeded. `d4b_capacity.json` is the empty output from that failed invocation, not evidence.

Done-when: exact memberships, preserved certified support labels, slice-contained query references, explicit source bindings, capacity table and no-release supplement are all delivered. No model or teacher execution.

Deviation: the requested capacity repair cannot undo executed research exposure. Both prospective and cumulative readings are explicit. The older supplement's current-inventory validator correctly becomes obsolete once v3 slices appear; v2 binds the expanded inventory and its historical predecessors.

Unresolved / questions for lead: use R1-X9's qualified audit and decide a genuinely adequate fresh-population strategy before drawing. The owner may retrain/evaluate v3 as development, with a new reader identity and costs; that alone does not expand admitted capacity. Task-board mirrors require owner action or specific permission.
