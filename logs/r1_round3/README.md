# Codex CPU round 3 — delivered work

Start with [the lane handoff](../../docs/tasks/CODEX-R1-round3.md). All four available lanes have CPU deliverables; no Codex edits to existing files, GPU jobs or commits were made.

- [R1-D1b](../../docs/tasks/R1-D1b.md): v2 exclusion policy and exposure counts; **154,306** candidate records / **87,857** subject keys. Final eligibility and complete canonical-entity coverage remain unproven.
- [R1-20c](../../docs/tasks/R1-20c.md): tested namespace reservation; **zero actual final examples emitted**.
- [R1-24](../../docs/tasks/R1-24.md): continuation design, dry-run manifest and isolated leased runtime. Current-source preparation is `manifests/revision_v1/r1_24_control_v2.json`; exact pilot-pass reconciliation and GPU execution remain owner actions. Literal self-distillation is an expected no-op numerical control.
- [R1-X2 audit](../audit_r1_25.md), [concurrent-change addendum](../audit_r1_25_cfc6db6_addendum.md), and [dataset output-collision finding](../../docs/tasks/R1-X2-output-collision.md): repaired gates and remaining defects, with reproducible CPU evidence.

[Validation record](validation.json): 54 distinct selected CPU tests pass, plus six affected tests rerun after Claude's concurrent update. Source bindings and data inventory invariants are checked. Passing tests do not imply the audit counterexamples are fixed or that the GPU path has run.

Claude's `cf_pool3k_pair_own_bal_400` training remains outside this lane. Task-board mirroring, core repairs and final-data decisions belong to the owner/lead. All artifacts from this round are inventoried in `docs/tasks/CODEX-R1-round3.complete.json`.
