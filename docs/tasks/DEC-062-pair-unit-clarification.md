# DEC-062 clarification — 100 pair slots; repeated families allowed

Lead clarification, received in this conversation on 2026-09-17:

> Allow multiple disjoint pairs per family

This answers the question whether the 100 planned support–neighbour pairs must
come from distinct template families. **They need not.** The planned denominator
is 100 pair slots per dataset and realization. Several disjoint pairs may share
the same exact DEC-061 family. Subjects remain distinct within a pair, and the
existing global disjointness and no-reuse requirements still apply. If fewer
than 100 compatible disjoint pairs are available, preserve the planned denominator
and report the missing slots explicitly.

This resolves X16-04's pair-count ambiguity and matches the existing
`scripts/r1_d9f_allocation.py` contract (`multiple_pairs_per_family_allowed`). The
diagnostic reported in R1-D9f already used this interpretation; its results do
not require recomputation. No allocator or scoring change is needed.

The clarification settles this specific semantic choice. Exact protocol/RNG
admission, the DEC-062 protocol amendment, normative bindings, complete cost
evidence and the final production recipe package remain separate requirements.
The signed operator form must still cover the complete reviewed request. This
record does not create a signature, supply a seed or authorize a population draw.

The protocol amendment proposed in `X16-edit-requests.md` §2 can now use the
multiple-pairs-per-family wording without its previous semantic condition.
The orchestrator should replace “fewer than 100 families yield pairs” in the
decision/task wording with “fewer than 100 compatible disjoint pairs are available”
when incorporating this clarification. The reviewed decision/protocol files and
hash-bound historical packages have not been rewritten by this follow-up.

Current status: `CODEX-R1-round27-handoff-v2.md`. Machine-readable provenance and
existing-contract bindings: `logs/r1_round27/dec062-pair-unit-clarification.json`.
