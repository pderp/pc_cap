# AW-L preregistration draft

**Status:** done as a draft for lead review. **Agent:** Codex. **Date:** 2026-09-20. **Inputs:** DEC-073 allocation A, final additional-work plan, AW-L0/L1/L3 findings. **Output:** `docs/additional_work/AW-L.md`.

The draft fixes the 2×2 read/write arms, three paired seeds, six readers/24 evaluations, two datasets, 300 edits, one order, exposed realization-0 interpretation, endpoint/fidelity populations, descriptive 0.02 tolerance, cost accounting, L4 gate, 48-hour ceiling and October 9 stop. It explicitly holds reader weights fixed between write arms; six readers cannot also imply independently optimized training for each of four interface arms. Shared-seed tensors should be initialized before tap pruning. No claim of inferential noninferiority, independent token replicates or lower layers being noise.

**Verify:** read against `docs/ongoing.md` round 43 and `docs/additional_work_plan_final.md`; all requested fields are explicit. **Done-when:** complete reviewable draft; no launch authorization inferred. **Cost:** documentation only, zero GPU seconds. **Unresolved/questions for lead:** review the seed/order/training-policy details before GPU execution; Claude owns AW-B/R preregistrations. No commit.
