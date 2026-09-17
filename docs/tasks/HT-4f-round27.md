# HT-4f — final claim ledger gate

Round 27, Codex, 2026-09-17. **Blocked; no final ledger v6 published.**

The lane explicitly requires signed cost admission first. The current
`R1-cost-admission-receipt-v1.json` has `lead_approved: false`. Moreover, an
in-memory schema probe shows that setting that flag alone still fails the typed
cost validator (`receipt register identity differs from v6`). The probe was never
written as a signed receipt. See `logs/r1_round27/r1-x16-audit.json` and the DEC-062
addendum for source hashes and the current gate status.

The eight corrected MQuAKE profiles are now complete and independently rescored
in X16. Their bounded locality counts, development RET-GS and available/unavailable
unseen metrics are ready for the later ledger. In particular, six v0/S1 profiles
have unavailable firing telemetry; the ledger must not repeat the notes' zeros.
The κ pilot, stress and tail evidence retain their existing exploratory framing;
no confirmatory or universal heavy-tail claim follows from these checks.

Resume after the typed, source-bound cost admission exists and validates, then
publish a new ledger from the actual current receipts. Include the repaired
protocol/DEC-062 identity, current operator package, measured-versus-projected
cost distinction, MQuAKE actual-300-only limitation, empty zsRE baseline caveat,
October 9 experimental stop and incomplete-inventory rules. No earlier ledger
or evidence artifact was overwritten in this round.
