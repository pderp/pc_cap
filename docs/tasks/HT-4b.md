# HT-4b — claim/evidence ledger v2

Status: complete; new file only. The original ledger is unchanged.

Output: [talk_claim_ledger_v2.md](../talk_claim_ledger_v2.md), with32 full SHA256 evidence bindings in logs/r1_round16/talk_evidence_v2.json. All18 original row IDs are preserved, with two explicit added rows for occupancy flatness and runtime. Every row is labelled implemented, proposed, hypothesis or null; unavailable pilot/panel outcomes remain empty rather than becoming null results.

The update binds primary v5, selection v2, the independently reconstructed selection audit/curve, v5 full/incremental tail audit, newly completed CounterFact full assay, near-miss/revision and unseen endpoints, driver profiles, schedule arithmetic, DEC-051/052 and the new comparator/calibration lanes. It corrects the proposed occupancy-flatness interpretation: zsRE outside populations have zero pairwise ID overlap. It separates low mean drift from large local errors, and complete-answer correctness/termination from cap-induced answer changes.

HT-3/HT-3b Q4 remains the producing lane for trained κ evidence and numerical safeguards. HT-2/HT-5 Q5 remains the producing lane for stress/recovery. Both lead decisions are due September20; experiments stop October9. Approved round15 script cleanup is recorded through its verification receipt; historical task-record wording is not reused as current status.

Validation: every referenced evidence file existed and matched its recorded hash at write time. The figure uses shared source/position/reference vectors and was visually inspected. No scientific gate, protocol, source implementation, board, GPU task or commit was changed.
