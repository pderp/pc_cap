# HT-4c — talk claim ledger v3

- Status: snapshot complete; later pilot/control results require a new snapshot.
- Agent: Codex, round18.
- Inputs: HT-3d verified-alias snapshot; measured R1-68d result; installed DEC-053 implementation and saved generation traces; HT-1b tail audit including CounterFact; R1-X12/R1-76 occupancy reviews; dry candidatev5.
- Outputs: docs/talk_claim_ledger_v3.md; logs/r1_round18/talk_evidence_v3.json; scripts/ht4c_claim_ledger.py.
- Verify command: assemble the ledger in memory and verify every evidence_sha256 value; script refuses to overwrite v3.
- Verify output:19 claim rows,31 bound source files, every row has explicit paths and full SHA-256 values; required counter-review paragraph reproduced verbatim.
- Done-when: measured versus proposed/hypothesis/null labels, no missing-as-null claim, exact pilot rule/population qualifications, observed runtime versus schedule scenarios, both locality conventions, rare-harm tails without distributional overclaim, occupancy caveats, October9 cutoff.
- Cost: GPU0; read-only aggregation and rescoring of saved traces.
- Deviations: v3 is an immutable partial-chain snapshot, not a claim the clipped control or confirmation has finished. The source script supports the named current snapshot; existing ledger files were preserved.
- Unresolved: use the automatic after-chain pilot report to prepare a new ledger snapshot when owner work finishes; final-slide hash revalidation and independent confirmation remain necessary.
- Questions for lead: none.

Validation: 60 focused CPU tests passed (6.49 s); ruff passes all new scripts/tests. Logs: logs/r1_round18/lanes-tests-v2.txt. No real-base calls, GPU time, source-tree changes, results/R1 writes, staging or commits.
