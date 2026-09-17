# R1-D9f — coordinated near-miss allocation

Round 27, Codex, 2026-09-17. Implementation and CPU diagnostic complete. DEC-062
selects `family_coordinated`. The lead has clarified that **100 pair slots may
include multiple disjoint pairs from the same family**; see
`DEC-062-pair-unit-clarification.md`. No actual draw or signature was made.

## Implementation and admission

`scripts/r1_d9f_allocation.py` supplies the allocator and receipt audit. The public
draw hook is in `scripts/r1_d9_draw.py`; `scripts/r1_d9_receipts.py` binds the new
implementation, enforces matching protocol/RNG/configuration choices, and audits
pair receipts before sealing. Legacy calls without the new mode retain exact
independent output, including ordering and RNG records.

The algorithm first computes the independent allocation, retains its exact edit,
outside and revision selections across all realizations, and releases its
provisional near-role selections. It uses only the remaining cleared candidates.
Within each exact DEC-061 family, it permutes source records, constructs disjoint
support–neighbour units, then permutes those units to select up to 100. Exclusive
role candidates are paired before dual-role candidates to preserve eligibility.
The algorithm permits several disjoint pairs from one family. It is not a draw
of 100 uniformly sampled families; larger families can contribute more units.

Each dataset/realization uses its own PCG64 stream derived from the master seed,
register hash and `R1-D9-family-pairs-v1` namespace. Receipts include derivation,
initial/final states, input-pool digest, selected units, role fillers and missing
slots. Global subject/fact/item disjointness and Hall feasibility remain required.
Any failed capacity check aborts the draw; there is no seed search or outcome-based
replacement. The provisional independent near streams are historical backbone
derivation records, not the final near selections.

If compatible units are insufficient, remaining role-eligible subjects fill the
fixed role reservations without replacement. This does not manufacture matched
cases: the existing DEC-061 constructor recomputes lexical within-family pairing
and preserves every missing slot. Pair units select membership, not endpoint slot
order. Consequently support and neighbour may be re-paired within the same family
by the constructor; the units are not a new scoring definition.

## Real-pool diagnostic

One seed, **20260917**, was declared before evaluating either mode. It is not the
lead's final master seed. No model ran and the diagnostic resources cannot serve
as executable reservations. Source evidence is bound in
`logs/r1_round27/r1-d9f-real-pool.json`; selected IDs and streams are under
`assets/runs/pc_cap/R1/r1_d9f/round27/` outside the repository.

| Dataset | Independent, realizations 0 / 1 / 2 | Coordinated, realizations 0 / 1 / 2 | Planned per realization |
|---|---|---|---:|
| zsRE | 21 / 16 / 18 | 100 / 100 / 100 | 100 |
| CounterFact | 63 / 72 / 68 | 100 / 100 / 100 | 100 |
| MQuAKE | 77 / 79 / 79 | 100 / 100 / 100 | 100 |

All non-near selections are identical between modes. All 900 coordinated planned
slots matched in this diagnostic. This is one outcome-independent allocation,
not a probability estimate or assurance about a future seed. The result uses
multiple pairs per family; requiring 100 distinct families would force missing
slots for CounterFact and MQuAKE.

## Current bindings and remaining work

The updated task list requests the selected mode in the **unsigned v4 RNG
template**; that field is now set, and its previous bytes are archived under
`logs/r1_round27/source_snapshot/`. The operative unsigned package is now
**candidate v11 / inputs and forms v6**, preserving v9/v10 as historical evidence.
The candidate binds 772 files. The exact allocation contract is an unsigned
proposal at `R1-D9f-allocation-contract-unsigned.json`, linked to a snapshot of the
accepted DEC-062 row. Signing the operator's protocol step can admit those exact
details and generate its closed receipt; Codex has not done so.

The first diagnostic and X16 JSON snapshots incorrectly describe DEC-062 as
pending. `logs/r1_round27/r1-x16-DEC062-addendum.json` corrects that status; numerical
results are unchanged. The subsequent lead clarification permits multiple
disjoint pairs per family and resolves the pair-count interpretation.
The bound final protocol also still expressly forbids coordinated allocation:
the X16 edit request calls for a versioned amendment before any signature.

Validation covers independent identity, replay, source-order invariance, sparse
shortfalls, repeated-family pairs, exclusive roles, admission and receipt tampering,
outcome independence and heterogeneous layouts. The synthetic public-producer
rehearsal passes through clearance → draw → endpoints → seal with 360 payload
identities and nine complete planned-100 pair inventories. It does not use a real
admission, final population or GPU. See the round-27 handoff for final test results.

Done-when: software, diagnostic and pair-count clarification complete; protocol
amendment, exact signatures and authorized execution remain owner work.
