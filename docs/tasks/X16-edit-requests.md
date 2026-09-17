# X16 — proposed owner repairs before the signing sitting

Round 27, 2026-09-17. These are **unapplied review findings**, per the X16 lane.
Full evidence: `logs/r1_round27/X16-review.md`, numerical audit JSON and DEC-062
addendum. The earlier audit's statement that DEC-062 was pending is superseded:
B is accepted; exact pair-unit semantics remain to be clarified.

## 1. Bind every incorporated normative document (X16-01)

Final v5.2-D expressly incorporates `docs/R1_stage4_protocol_draft_v5_1.md` for
statistical definitions and other requirements. That file is absent from both
the incoming v9 and current v11 `bindings_sha256`. The successor package builder
must bind it, and check the complete normative dependency closure for any further
incorporated requirements. Historical evidence references need not silently become
new normative requirements, but normative dependencies cannot remain mutable.

Publish a new candidate and unsigned input/form version after the protocol repair
below, recompute D9 request digests, and ensure the operator uses that version
explicitly. Do not overwrite old candidates or reuse old signed digests. Test:
changing a bound inherited normative file must fail verification before admission.

## 2. Reconcile DEC-062 with the actual normative protocol (X16-04/10)

The bound final protocol still says no family-coordinated allocation is authorized.
The recorded decision and new RNG mode cannot both be implemented while that
sentence governs. Make a versioned DEC-062 protocol amendment and bind it in the
matrix/input/receipt/recipe chain where those identities are required.

The proposed replacement paragraph, **conditional on confirmation that multiple
disjoint pairs per family are allowed**, is:

> DEC-062 selects family-coordinated near allocation. Preserve the exact independent
> edit, outside and revision allocations across all realizations. From the cleared
> pool remaining after those roles, use separately receipted RNG streams to select
> disjoint support–neighbour pair units by the exact DEC-061 family definition.
> Several pairs may share a family; the planned denominator is 100 pair slots per
> realization. Preserve global disjointness and Hall checks. If compatible units
> are insufficient, reserve remaining eligible near-role subjects without
> replacement and record unmatched endpoint slots explicitly; do not manufacture
> compatibility or retry a seed. Within the resulting reserved roles, retain
> DEC-061 lexical endpoint pairing. No outcomes enter allocation. Bind the exact
> allocation contract and mode in protocol and RNG admission before the draw.

The lead has been asked to clarify “100 families.” If distinct families are
required, this paragraph and the allocator must change first, and the current
100/100 diagnostics cannot be used as evidence for that interpretation. Do not
convert acceptance of B into approval of unstated pair weighting or new semantics.

The current operator protocol form explicitly exposes the pair-unit policy review;
its exact signature creates a closed allocation-contract receipt. None has been
signed by Codex. Its controls complement, rather than replace, the normative-text
repair.

## 3. Produce complete typed cost admission (X16-02/03)

Do not merely set `lead_approved` in `R1-cost-admission-receipt-v1.json`. Its current
shape fails `check_receipt('chain_i_cell_ceilings', ...)` even with that flag true.
The new operator `cost-admit` step binds v1 as source evidence and can emit a typed
successor after exact lead approval. Supply:

- Current register, protocol, matrix, layouts/hash and near-family identity.
- All 27 condition/dataset wall ceilings and measured peak host/device ceilings,
  with measurement JSON references and hashes.
- A reviewed cost basis covering final endpoints, initialization and complete
  validation, plus failed attempts. Identify which numbers are extrapolations.
- An explicit shared **process-hour** ceiling. Neither 127 projected elapsed hours
  nor a sum of padded worst-case ceilings is an automatic admitted budget.
- Current September 20 schedule admission and remaining resource/gate evidence.

If full measurements require changed ceilings, version the ceiling table and raw
cost source together; do not silently change numbers inside a signed request.
The current operator pins v1, so adapting it to a successor source also requires
a new implementation binding and request digest. A 128-window drift sample does
not satisfy full validation. Resolve U08/U16 with actual evidence or an explicit
lead protocol amendment, not an undocumented substitution.

Validation: typed receipt accepted by the preflight and HT-4f validators; stale
protocol, missing/duplicate cell costs, absent memory measurements, unknown costs
and elapsed/process-unit substitutions rejected.

## 4. Complete production publication inputs (X16-06/08)

Prepare final recipes, matrix, protocol and binding inventory for all admitted
360 core cells and, if chosen, 45 extension cells from the actual sealed resources.
The operator's freeze step requires a reviewed publication bundle; it cannot
invent these artifacts or gate receipts. Close each of U01–U18 with its genuine
current evidence, preserving DEC-052 incomplete-inventory reporting. Current
candidate v11 still lists 17 open identifiers.

Validate the complete publication against the real sealed backend, test rollback
and crash recovery, then sign the exact freeze request. Confirm the execution
environment enables JAX CUDA and the externally held lease is live before launch.
No additional GPU work was performed by this lane.

## 5. Correct the Chain Q notes (X16-07/09)

Exact proposed patch: `docs/tasks/X16-notes-correction.patch`. It changes only the
last Chain Q section: six v0/S1 unseen metrics become unavailable, 0 scored/100
planned; costs become 209.4 core solo, 126.91 projected wall and 12.15 extension
solo hours. It also removes the claim that these profiles complete the full cost
measurement basis. Valid bounded locality and development retention are retained.
The expected original source hash is in
`logs/r1_round27/x16-notes-patch-source.json`. Recheck it if Claude edits that file.

The lead-queue readiness wording and binding count should also be updated after
the actual repairs: incoming v9 verified 744 bindings, current v11 verifies 772,
and neither count implies launch authorization. Do not describe only signatures
as remaining when substantive inputs are absent.

## 6. Publish HT-4f only after valid cost admission

The existing final-ledger producer pins older v4 inputs and final text. When
resuming HT-4f, let it bind the actual successor protocol/input/cost identities
instead of validating a new receipt against an obsolete package. Carry all eight
corrected profiles with unavailable firing represented honestly; retain existing
κ/tail/stress qualifications. The unsigned cost state prevents publication now.

These repairs can be divided without sharing edit targets: protocol/package owner,
cost-evidence owner, final-recipe/publication owner, and notes/ledger owner. Agree
the new protocol and cost identities before rebinding downstream artifacts to
avoid churn. No test, receipt or local signature replaces the lead's scientific
choices and exposure attestation.
