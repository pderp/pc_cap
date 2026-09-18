# R1-63o locality selection amendment — lead approval

2026-09-18. Charlie's exact reply: **“Approve deterministic exclusion and selection”**.

Approved request: amend D.5 and the constructor to deterministically select the first 50 distinct nonoverlapping locality prompts from the same reserved outside items, preserving all 50 planned slots and explicit shortfalls. No treatment outcomes or model calls guide selection.

This supersedes D.1's confirmation-constructor prohibition on substituting rows after a collision. It does not authorize another draw, another seed, additional subjects, an outcome-based filter, changing the near-miss family, reducing denominators, signing, sealing or launch. The complete reserved edit stream, including future edit prompts and paraphrases, defines exact-text exclusions. Reserved outside items are traversed in sorted item-ID order and their prompts in source order; the first 50 distinct eligible strings are used. All 50 independent expected IDs remain declared when fewer than 50 eligible strings exist. The constructor records exclusions, eligible counts, selections and shortfalls for review. The seal validator still rejects overlapping locality rows.

The old draw was examined in a CPU-only deterministic dry run; its initial constructor failed on locality overlap before endpoint publication. No treatment outcomes were generated or consulted. Reuse of those reservations for software validation is not a new D.5 admission; the orchestrator still starts a fresh signing session using the approved seed.
