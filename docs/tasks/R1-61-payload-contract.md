# R1-61 — admitted cell input and output contract

The example JSON is a recipe template, not a seal or executable research condition. Real execution requires the recipe's externally supplied SHA-256 to match, the frozen code identity to match, and every explicit admission gate to be true.

## Payload resource

Store the payload JSON under assets and bind its exact bytes in the recipe. It contains:

- `items`: all 1,000 prepared edit rows, in the admitted order. Preserve original payload fields so each canonical row hash matches its R1-58 reservation. Each row has item_id, fact_id, subject, dataset, prompt, answer, aliases, paraphrases and prepared prompt/answer token IDs.
- `pool_rows`: unique metadata for all edit and outside items, including item_id, fact_id, subject, prompt and dataset. Edit metadata must match the edit rows.
- `endpoints.locality`: ordered expected_ids and available rows containing item_id and prompt. The common original base supplies LS references.
- `endpoints.unseen`: ordered expected_ids and available rows containing the original outside item_id and prompt. The expected IDs must be in the bound pool, disjoint from the entire edit stream, and equal the R1-58 outside reservation. Full attempted history, including failed edits, is supplied to unseen admission.
- `endpoints.near_miss`: independently constructed rows with item_id, dataset, edit_item_id, edit_prompt, edit_answer and neighbour_prompt, plus expected_ids. This bundle's semantics and relationship to reserved support/neighbour facts need independent admission.
- `endpoints.revision`: rows with item_id, dataset, fact_id, prompt, exactly two increasing versions (version, answer, aliases) and paraphrases, plus expected_ids.
- `endpoints.composition`: expected composition IDs and the original R1-D4 case rows. Each dependency item must belong to this realization. A zero-case inventory is permitted and remains not applicable, not perfect performance.
- `endpoints.drift`: integer token windows and expected_positions, fixed independently of outputs. Incomplete windows/positions never yield a full-inventory drift estimate.

Expected endpoint IDs can exceed available source rows. Missing cases remain planned. Available rows must follow the independently specified order without duplicates. Do not construct this inventory by looking at which model outcomes succeeded.

The recipe separately binds the full endpoint bundle and ordered edit IDs in its admission receipt. Scientific challenge construction and final eligibility are upstream responsibilities; content sealing alone does not supply them.

## Construction and identity

Construction binds the base snapshot config/weights, optional original-base snapshot for S1, tokenizer hash, reader checkpoint where applicable, stop-token source, seed, calibration and budget. The owner compares the constructed adapter's identity against the predeclared identity. No implicit latest or best checkpoint lookup occurs.

For S1, base is the continued base and original_base is the common original reference. The unseen reference is the continued cap-off base; locality references the original base. For learned/random RevisionCap conditions, the checkpoint arrays must match the registered parameter structure and have finite float32 values.

## Immutable outputs and resume

The identity-named output directory is derived from all cell axes and the externally bound manifest. It contains cell.json and one new attempt directory per invocation. An attempt contains immutable phase records, checkpoint reports, chained checkpoint receipts and a result or failure file.

Snapshots are written to the corresponding assets directory. A checkpoint receipt is created only after its report and snapshot are complete. On resume, verify the entire contiguous receipt chain, restore the latest completed snapshot, keep prior files intact, and replay later interrupted work. All attempts remain part of resource accounting.

The Python API permits shorter explicitly synthetic checkpoints for TinyBase tests. The owner CLI executes only an admitted real recipe with 100/300/1,000 checkpoints and a 32-token greedy limit. Default CLI inspection reads metadata only.
