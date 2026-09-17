# HT-4e — claim ledger v5 and corrected-result refresh

Status: current ledger snapshot and tested refresh producer complete; **post-chain-P result update pending**.
Agent: Codex, round25, 2026-09-17.

Outputs: `scripts/ht4e_claim_ledger.py`, `docs/talk_claim_ledger_v5.md`,
`logs/r1_round25/talk_evidence_v5.json`, `ht4e-profile-inventory-v5.json`.
Inputs: preserved v4 rows with unchanged exact hashes, corrected post-R1-77d MQuAKE recipes,
concurrency admission/policy, execution plan, certified population, DEC-060 and analysis implementation.

Every row is hash-bound. v5 carries stable tail/pilot/stress and historical development evidence forward,
preserves the required κ framing and null gates, and supersedes outdated population/scope/operator rows.
It includes the empty zsRE teacher baseline, 2,161-subject MQuAKE population, actual-300-only scale
limitation, unchanged 63-interval family, and separate process-hour versus elapsed-hour accounting.

At this snapshot **0 / 8 corrected MQuAKE recipes have completed results**. Each row is explicitly
pending; historical Chain M locality 0/50 is never substituted. The owner can run the new recipes now.
After the runs complete, create a fresh snapshot:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.ht4e_claim_ledger --version v5-after-chain-p
```

The producer refuses altered recipes/payloads, mismatched result/checkpoint/receipt identities,
partial retention populations and ambiguous multiple completed attempts. It retains failed attempts
and labels pending cases. Tests exercise both the currently pending and future completed-result paths.
All data remains under assets; this is not a new GPU job or outcome-based profile selection.

Verify: `logs/r1_round25/{ht4e-build,review-tests}.txt`; exact hashes in the ledger JSON.
Done-when: current snapshot met; final corrected MQuAKE numerical rows await owner execution.
Cost: CPU only, no GPU/model calls/commits. Deviation: a truthful pending snapshot is delivered before
chain-P comparator completion so talk preparation can proceed. Unresolved: eight completed owner results;
new snapshot after them. Questions for lead: none.
