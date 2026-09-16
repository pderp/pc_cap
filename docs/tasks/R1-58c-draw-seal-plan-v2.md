# R1-58c — dry draw, seal and freeze checklist v2

Status: checklist and refusing dry-run previews prepared; Markdown-binding correction awaits permission.
Agent: Codex, 2026-09-16. Inputs: register v6, matrix v5, protocol draft v5, freeze candidate v5,
DEC-042/048/051–056, R1-77b sealed backend. No draw, role allocation of confirmation subjects,
seal, frozen manifest, model execution or launch occurred. GPU cost: zero.

## Commands and current outcome

Run from `/home/derp/cap/pc_cap`, using the existing venv. These commands have **no mutation mode**;
they print intended paths, demand, verified receipts and every missing prerequisite. Exit 2 means
refused; exit 0 means metadata is ready for owner review, never authorization to execute.

The script currently needs the small correction in `R1-58c-markdown-binding-v2.patch` (permission
pending). It must hash the Markdown protocol without parsing it as JSON, and allow its `docs/` path.
The corrected code was tested in memory; corrected previews are in `logs/r1_round19/`.
Do not use the superseded first patch. After applying the approved correction:

```bash
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m scripts.r1_58c_draw_seal_preflight --stage clearance --inputs docs/tasks/R1-58c-dry-inputs-v2.json
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m scripts.r1_58c_draw_seal_preflight --stage draw --inputs docs/tasks/R1-58c-dry-inputs-v2.json
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m scripts.r1_58c_draw_seal_preflight --stage seal --inputs docs/tasks/R1-58c-dry-inputs-v2.json
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m scripts.r1_58c_draw_seal_preflight --stage freeze --inputs docs/tasks/R1-58c-dry-inputs-v2.json
```

All four currently refuse because the named owner receipts are absent. Preserve the supplied v2
input file; create a new version to bind completed receipts. Each receipt uses exact `path`/`sha256`,
`status: closed`, `lead_approved: true` and the same v6 register binding. Never fill placeholders
with assumed approval. The code contains the required stage-specific fields and validates capacity,
roles, gate closure and finite positive cost ceilings.

## 1. Clearance before RNG or role assignment

1. Recheck register-v6 source hashes and cumulative exposure through draw time. Record the exact
   selected primary weights/training prefixes, installed code, tokenizer/base identities, recent
   development uses and exclusions. Keep all historical primary exposure excluded.
2. Bind CounterFact's **reason-specific DEC-042 exception**. Its strict-source eligible count is
   zero; DEC-048 does not waive CounterFact reasons. Retain zsRE cross-dataset priority.
3. Apply DEC-048 option C literally: an MQuAKE **true-fact query presentation** is not by itself a
   counterfactual-edit exposure. Actual training/edit use, unknown roles, conflicts, aliases,
   cross-dataset priority and all nonwaived reasons remain exclusions. No suffix-based waiver.
4. Review entity aliases, punctuation/name variants and contextual ambiguity jointly across datasets.
   Quarantine unresolved identity cases. Recheck answer aliases separately; an answer alias is not
   automatically an alias of the edited subject.
5. Reconstruct prompt/answer tokens with the final tokenizer; enforce the 32-token answer limit,
   context/vocabulary eligibility and required paraphrases. Bind the final-base teacher receipt.
   Historical teacher text without a base-weight identity is not a new final-base certificate.
6. Verify compatible near-support/neighbour roles, revision cases and composition dependency closure.
   Subject/item/fact exclusions apply across **all** allocated roles and realizations, not just edits.
7. Certify usable joint capacities and role feasibility. Nominal v6 counts are zsRE 52,411,
   CounterFact 12,246 and MQuAKE 4,218 subjects. MQuAKE has only 168 nominal spare subjects;
   losing 169 fails demand. Nominal capacity is not clearance. Abort on any dataset below 4,050,
   unresolved role feasibility, changed input hash or post-review exposure.
8. Write the reviewed `joint_clearance` receipt only after those checks. It binds policy
   `DEC-048-option-C;DEC-042-CounterFact;zsRE-priority`, all six clearance booleans in the script,
   per-dataset usable counts and review evidence. Expected path:
   `docs/tasks/R1-final-joint-clearance.receipt.json`.

The DEC-056 development population uses already historically exposed subjects. Its report confirms
zero final-register subject use; it does not increase or certify final headroom.

## 2. Draw: three datasets, three realizations each

Before drawing, bind `protocol_admission`, `rng_admission`, `draw_authorization` and clearance.
The protocol decision covers U12–U14 and all comparisons/conditions, including whether the 45-cell
historical-v2 extension is actually admitted. The RNG receipt specifies algorithm/version, seed,
source ordering, stratification/quota rounding, tie handling and deterministic replay. No unspecified
random seed is silently selected by this checklist.

For **each dataset and each of three fresh realizations**, reserve disjoint subject inventories:
1,000 edits; 100 outside facts/prompts; 100 near-miss supports; 100 near-miss neighbours; 50 revision
facts. That is 1,350 per realization, 4,050 per dataset, 12,150 overall. The five orders 100–104 permute
one realization's fixed 1,000 edits; they are not five independent draws. Every condition shares the
same realization and order. Outside100 is disjoint from the full stream, including future fillers.

Expected artifacts: an owner draw receipt and an **unsealed** fact reservation under
`assets/runs/pc_cap/R1/stage4_sealed_payloads/`. The receipt lists source hashes, RNG state, exact
ordered subject/item/fact IDs for every role, counts before/after filters and all rejected cases.
No replacement based on model outcomes; abort and seek a versioned decision if feasibility fails.

**Implementation handoff:** the old `r1_58_draw_streams.py` CLI binds register v3 and two datasets;
the historical three-dataset helper is also not a certified v6 final writer. Do not run either as
though it implements this sequence. The owner must bind and test the final three-dataset v6 draw
adapter before actual drawing. The delivered command is deliberately a dry preflight, not that adapter.

## 3. Construct endpoints, then seal content

1. Preserve the unsealed draw receipt. Construct endpoint cases only from the admitted roles, with
   composition dependencies entirely inside that realization. Preserve all independent expected IDs
   even when an endpoint is unavailable. No denominator inferred from successful observations.
2. Bind checkpoint cadence `[100,300,1000]`, decoder max_new=32, locality/unseen probes at checkpoints,
   and final near-miss/revision/composition/drift inventory. Drift windows/position IDs and the
   `row_hash` source convention must match the analysis inventory exactly.
3. Freeze LS and near-miss preservation as **bounded-text equality (DEC-053)**. Termination,
   truncation and terminated-match counts remain diagnostics.
4. Produce per-item canonical content hashes, admitted endpoint-bundle hashes and ordered-item hashes.
   The installed sealed loader uses canonical compact `content_digest` for row/endpoint content and
   the existing analysis `digest` convention for ordered item IDs; do not interchange them.
5. Write `content_sealed_fact_reservations`, a complete payload-file hash inventory, and the independent
   analysis-population map keyed by coordinate ID. Verify round-trip byte hashes, all role counts,
   no duplicate facts/subjects, outside disjointness, and composition closure.
6. Expected seal receipt: `docs/tasks/R1-final-seal.receipt.json`, with opaque bindings named
   `reservations`, `payload_inventory`, `analysis_population`. Payloads/resources stay in assets.
   The dry checker inspects receipt metadata; it never opens these payloads.

## 4. September20 cost admission and candidate v5 → final freeze

These are named inputs, **not estimated or approved values**:

| Placeholder | Owner evidence required |
| --- | --- |
| `chain_i_cell_ceilings` | Every admitted condition/dataset's current-code profile; wall, peak host/device memory, failures and construction included; missing MQ calibration/profile cells explicit |
| `september20_admission` | Approved per-cell ceilings and total envelope, full-scope schedule through Oct9, failures/retries allowance, DEC-052 whole-block stop rule |
| `protocol_admission` | Accepted Q11–Q13 text, fidelity/continuation receipts, primary and separately approved secondary conditions |
| `closed_gate_receipts` | Independently reviewed U01–U18 closures, including execution implementation and actual final payload seal |
| `freeze_authorization` | Lead approval of the complete identities and admitted schedule |

Do not use a scenario estimate as a launch ceiling. Audit whether a partial checkpoint restart,
construction failure or interrupted process is already included; never double-count nested envelopes,
and never convert an unknown abandoned attempt into zero. The experiment stop is the end of
**October9 America/New_York**, not presentation day. Analysis/rehearsal occupy Oct10–14.

Freeze candidate v5 is evidence/provenance, not the final frozen marker. It still has 17 open gates
and predates this backend and the later DEC-055/056 work. Preserve it as historical input. Reconcile
its bindings explicitly, including the newly approved code/patches, instead of copying stale hashes
or changing its authorization booleans.

The proposed R1-77b final interface is documented in `R1-77b-sealed-backend.md`. Order the final writes
so there is **no circular hash**:

1. Final protocol JSON, clearance/seal/population artifacts and all gate-closure receipts.
2. Per-cell recipe contracts including payload, base/reader/calibration/config/budget, ceilings,
   backend SHA and independent population binding; compute their canonical digests **excluding only
   the future `freeze` field**.
3. Lead writes `manifests/revision_v1/frozen_stage4.json`, binding all contracts, code and closed gates.
4. Write final recipe envelopes with the frozen-file binding; hash the complete recipe files.
5. Write the complete final analysis matrix (`scope: confirmatory`) with exact recipe hashes,
   canonical result directories, populations and admitted ceilings. Write the queue binding file
   referring to that matrix hash and each exact recipe/backend hash. Use stop-after to run a prefix;
   never remove cells from the frozen inventory to make a partial matrix appear complete.
6. Run metadata inspection and queue status first. Owner execution additionally verifies the actual
   sealed payloads using the installed sealed loader. GPU lease and real-base smoke/admission remain
   owner responsibilities. The dry plan and CPU fixtures do not authorize launch.

## Checkpoints and concurrency

Before clearance: independent CPU workers can review aliases, teacher/token eligibility, role
feasibility, protocol text and profile accounting against immutable input hashes. Their outputs must
merge into one joint exclusion/capacity receipt before any role assignment. One lead owns the RNG
and final allocation; independent workers can then construct endpoint packages for distinct
realizations, using disjoint output paths and the same fixed reservations. Seal validation, protocol
admission and cost analysis can run concurrently once their inputs are stable. Final freeze is a
single owner operation. Queue execution follows the ordered whole-block policy and the GPU lease.

Done-when: the four corrected dry commands report the actual missing gates, emit no payloads,
and the lead can identify every required receipt and remaining implementation step. The one existing-
file correction is pending permission; the owner-only scientific gates remain open by design.
