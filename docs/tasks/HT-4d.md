# HT-4d — talk claim ledger v4

- Status: complete snapshot; subsequent profiles/admissions require an updated version.
- Agent: Codex, Round22.
- Inputs: prior ledgerv3's unchanged supported claims; independent HT-3e reproduction; completed exact-recipe
  Chain I/K results; calibrationv3; matrix/protocolv5.1; immutable decisions snapshotv6; D10a/D10c/D9 CPU artifacts.
- Outputs: `docs/talk_claim_ledger_v4.md`, `logs/r1_round22/talk_evidence_v4.json`,
  `logs/r1_round22/ht4d-profile-inventory.json`, `scripts/ht4d_claim_ledger.py`.
- Verify: every claim's direct file SHA and the required DEC-054 framing paragraph rechecked; original unchanged
  claims are copied only when every original evidence binding still matches. Final tests: `logs/r1_round22/final-checks.txt`.
- Verify output:24 claims;16/16 Chain I and9/12 expected Chain K v0/S1 re-profiles filed at this snapshot.
- Done-when check: pilot/control result, bounded stress findings, measured heterogeneous costs versus scheduling
  assumptions, MQuAKE radius0, DEC-053/057–059, capacity/admission limitations and October9 stop are represented.
- Cost: GPU0; reads completed result files only, never writes owner results or binds a changing progress log.
- Deviations: final Chain K/M and real admissions are unavailable, not filled. The ledger corrects earlier accounting:
  core360=270 v0/S1-style +90 reader-based cells; optional historical-v2 extension adds45 reader cells. The drift
  profile records one assay per cell, not three. This is not a replacement whole-matrix cost admission.
- Unresolved: cost repricing with the correct condition inventory, missing profiles, population/context resolution,
  actual teacher pass and final confirmation. Stress evidence supports persistence through the window, not permanence.
- Questions for lead: none for producing the snapshot; use the new qualifications in presentation preparation.

All κ results and qualifications, including the exact required framing paragraph, are in the linked ledger and
HT-3e report. Previous ledgers remain historical snapshots; neither development improvements nor the pilot alter
the completed v0 study's negative/inconclusive conclusions.
