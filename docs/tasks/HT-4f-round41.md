# HT-4f — published v6 ledger and historical sources

Status: **done**. Agent: Codex. September 18, 2026. CPU only; new files only, no signatures or commits.

Inputs: 40-row v6 content from round 40, genuine v8 step 2 signed typed-v4 cost receipt, and exact completed cost request in the operator journal.

Outputs: [published claim ledger](../talk_claim_ledger_v6.md), [machine-readable evidence](../../logs/r1_round40/talk_evidence_v6.json), and [publication verification](../../logs/r1_round41/ht4f-publication.txt). The publisher verified content sources, cost schema/admission, exact journal request identity and stable inputs before publication. All 40 claims and historical rebindings are unchanged; the sole pending cost field is filled. This publication is not launch clearance.

## Concurrent DEC-067 update

After publication, the orchestrator appended DEC-067 to decisions.md and continued the signing journal. The prepared ledger/deck intentionally reject current source bytes that differ from their bound hashes. Two existing round 40 tests consequently fail; the other 93 cases in the combined run pass. [Combined output](../../logs/r1_round41/tests-final.txt) preserves that result. No test or source hash was weakened.

Added [a historical-source resolver](../../scripts/ht4f_v6_source_archive.py) and [manifest](../../logs/r1_round41/ledger-v6-source-archive/manifest.json). They preserve:

- Exact earlier decisions bytes recovered from Git with their originally bound SHA. Every prior nonempty line remains an unchanged prefix of the current document; new delegation text is recorded separately.
- Exact original publication-journal prefix, matched by its saved SHA despite later appended events.
- All **141 ledger sources**, with one historical relocation. Original ledger hashes, claims, signed receipt and files remain untouched.

[Archival verification](../../logs/r1_round41/ht4f-historical-sources.txt) passes. This establishes reproducible **historical** evidence; it does not make the old deck current. A new deck/content version should explicitly update its obsolete “cost signature pending” label. Existing current-source tests continue to reject changed live decisions as designed.

Verify command already executed, outputs exclusive: python -m scripts.ht4g_ledger_content publish --content logs/r1_round40/talk_evidence_v6_content.json --cost-receipt docs/tasks/R1-58g-operator_v8/02-cost-admit.receipt.json.

Done-when: genuine receipt verified and ledger published without claim changes. Cost: **0 GPU seconds**. Unresolved: next deck revision should bind the published ledger and a reviewed current decision snapshot; previously signed/published bytes were not rewritten.
