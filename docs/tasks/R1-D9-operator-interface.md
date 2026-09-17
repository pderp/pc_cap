# R1-D9 — owner receipt producers

2026-09-17. The three separate commands are implemented. **No real clearance, draw, seal, freeze or launch has been performed.** The input template has deliberately missing owner receipts and evidence. It is not an authorization file.

Run from `pc_cap` with the existing venv:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d9_clearance --dry-run --inputs docs/tasks/R1-D9-inputs-template-v1.json
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d9_draw --dry-run --inputs docs/tasks/R1-D9-inputs-template-v1.json
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d9_seal --dry-run --inputs docs/tasks/R1-D9-inputs-template-v1.json
```

Default is dry-run even when `--dry-run` is omitted. Exit 2 means unresolved prerequisites. Inspection prints nominal or reviewed counts, refusal reasons, intended paths and the exact request digest. It emits no selected candidate identities and uses no RNG. Clearance inspection can read the explicitly supplied unsealed review resource to check all dispositions. Draw and seal inspection read metadata only. `--execute` is the separate owner mutation command; it requires every named, hash-bound approval. Output directories and receipts must be new. A failed partial write leaves unadmitted artifacts, never overwrites or resumes them.

Use a new, populated version of `R1-D9-inputs-template-v1.json`. Its register is v6, matrix v5.1, protocol draft v5.1; its historical freeze candidate is provenance only. JSON metadata receipts belong in `docs/tasks/`. Data, dispositions, reserved rows, constructed payloads and analysis populations belong under `assets/`. The seal uses the assets paths accepted by the sealed backend; it does not place resources inside the code repository.

## Approval contract

All owner receipts have `status: "closed"`, `lead_approved: true`, and the exact `register` binding. The stage authorization additionally has `operation: "clearance" | "draw" | "seal"` and `request_sha256` matching the current dry-run. That digest binds the producer/core/dependencies, register, matrix, protocol, stage configuration and prerequisite receipts, excluding only that stage's own authorization to avoid a hash cycle. Supply an authorization only after reviewing those exact inputs; run dry-run again immediately before execution. Any source/code/recipe change requires a newly reviewed matching request.

The producer records `lead_approved: true` in its result only after validating that supplied owner authorization. It does not manufacture an approval from a passing count check. None of these result receipts grants launch authorization. R1-58c can consume the three result receipts unchanged, with its existing exact fields and counts.

## R1-D9a: clearance

Required approval: `clearance_authorization`. Configure `d9.clearance.evidence` as an exact path/SHA binding to an **unsealed** review JSON resource with:

- `register`: exact v6 binding; `policy`: `DEC-048-option-C;DEC-042-CounterFact;zsRE-priority`.
- `alias_review_complete`, `context_review_complete`, `teacher_token_review_complete`, `role_compatibility_complete`, `cross_dataset_disjoint`, `cumulative_exposure_current`: all reviewed true.
- Final `base_tensor_sha256`, `tokenizer_sha256`, and `model_limits: {vocabulary, max_context}`.
- `evidence_bindings`: nonempty exact file bindings for the actual alias/context/exposure and final-base teacher/token reviews. Historical teacher reports without the final base identity do not satisfy this requirement.
- `dispositions`: **exactly one row for every v6 candidate item**, including excluded rows. Each row has dataset, item_id, canonical_subject, reviewed global entity_id, prepared payload_sha256, decision (`eligible` or `exclude`), and reasons. An excluded row has nonempty reasons. An eligible row has empty reasons, explicit nonempty compatible `roles`, matching base/tokenizer identities, and true `alias_clear`, `context_clear`, `exposure_clear`, `teacher_pass`, `tokens_pass`.

The source loader verifies the v6 register and every bound prepared row and source hash. It does not recalculate or broaden DEC-042/048 exceptions. Reviews may remove candidates; they cannot add candidates to the register. It preserves all dispositions in the output resource. Within each reviewed entity it takes the first eligible item in register order, documents later representatives as rejected, refuses cross-dataset entity or fact collisions, checks answer/token/context limits and paraphrases, and checks all 31 nonempty role-subset capacities (Hall's condition), not only the total 4,050 per dataset.

Output: `joint_clearance` metadata receipt and `cleared-candidates.json`, containing the complete dispositions, usable source rows and role capacities. **The semantic reviews are still actual work:** filling booleans without the underlying review does not constitute clearance. The present template refuses because that evidence and authorization are absent.

## R1-D9b: draw

Required receipts: clearance authorization, joint clearance, protocol admission, RNG admission and draw authorization. Set the master seed explicitly in `d9.draw.master_seed`. The draw authorization also attests `cumulative_exposure_current: true` at draw time. Original review resources are rehashed before selection.

The RNG admission must bind the exact `RNG_RULE` object exported by `scripts.r1_d9_receipt_core`, the installed NumPy version and `master_seed`. It must state:

- `paired_order_rule: "R1-D9-order-v1; orders100..104; same order for every condition"`.
- `composition_rule: "all bound catalog cases with every dependency in the realization edit set"`.

Set `d9.draw.composition_catalog` to a hash-bound unsealed JSON map from dataset to predetermined composition cases. Empty lists are explicit; malformed dependencies or duplicate IDs refuse. Cases are included solely by dependency membership in a realization's edits, before any outcome exists. The draw retains that planned inventory for sealing.

Separate PCG64 streams derive from the master seed **and frozen register SHA**, dataset, realization, role and stratum using the first 16 bytes of SHA-256 over canonical compact JSON. Each stream records coordinates, derived seed and before/after RNG state. Quotas use largest remainders on the remaining role-eligible strata with lexical ties; source rows are ordered by global entity/item identity. Allocation follows declared dataset, realization and role order. Every step checks remaining role feasibility. A shortfall aborts the whole draw: no silent seed retries, substitutions or outcome-based selection.

All three realizations reserve 1,000 edits +100 outside +100 near supports +100 neighbours +50 revision facts, with no shared entities, canonical subjects, facts or items across roles, realizations or datasets. Five separately recorded orders 100–104 permute the same 1,000 edits; all conditions share an order. These are five paired orders, not five independent draws.

Output: draw receipt and unsealed reservations, full source content/hashes, all RNG states, five paired orders and planned compositions. Draw-time composition closure concerns dependency membership; it does not claim that semantic challenge construction has occurred.

## R1-D9c: seal

Required receipts: joint clearance, protocol and RNG admissions, draw authorization, draw receipt, endpoint construction and seal authorization. `protocol_admission` binds the current matrix and an explicit boolean `extension_admitted`; the matrix's declared core cells are always retained. The endpoint construction receipt has the standard preflight population fields and binds the exact draw receipt, reservations, `bundle`, and `independent_population`.

Set `d9.seal.bundle` to a bound unsealed JSON resource `{payloads: {coordinate_id: {path,sha256}}}` and `independent_population` to a separately reviewed `{cells: {coordinate_id: planned_population}}` resource. The coordinate convention is the existing R1-75 function; planned-population shape is the sealed backend's existing function. Independent expected IDs must be fixed before observations; never derive denominators from successful assay output.

The validator checks every admitted matrix coordinate, all dataset/realization groups, exact reserved row content, complete disjoint roles, paired edit orders, endpoint counts, pool equality to all reserved roles, near-miss support/neighbour IDs and source prompts/answers, revision fact/prompt identity, and composition membership. Near-miss constructed rows require `neighbour_item_id` as well as `edit_item_id`; neither role can be reused. It preserves missing assay rows in their independently planned denominators. Endpoint bundles stay constant across paired orders; full payloads stay identical across conditions sharing an order. Drift definitions and independent population hashes must agree.

Output: `content_sealed_fact_reservations`, deduplicated content-named payload files, a coordinate-indexed payload inventory, the analysis population and the seal receipt. Row/endpoint hashes use canonical compact `content_digest`; ordered IDs use the existing analysis `digest` convention. The installed sealed loader consumes these exact reservation and content hashes. Its admission still requires the subsequent final protocol, freeze, cell contracts, ceilings and queue bindings.

## Validation and remaining work

Small synthetic fixtures check exhaustive review, restricted role feasibility, deterministic/register-bound allocation, all five paired orders, cross-role and cross-realization disjointness, missing authorization refusal, exact seal content/denominators, immutable output behavior and receipt schemas. A reserved-item smoke uses TinyBase on CPU. The R1-77c end-to-end rehearsal is a separate integration gate; these producer tests alone do not close it or certify real clearance.

No real source population was drawn, no real sealed resource was opened or written, and no real base or GPU was used. Operator evidence construction, owner approvals and final admission remain required even though the commands now exist.
