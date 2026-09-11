# Updated plan 8 — 2026-09-11, day 3 (08:50 EDT), freeze now; B4 out of this month's programme

Delta over [updated_plan7.md](updated_plan7.md). Inputs: the lead's decisions (defaults for D-A/C/D/G/H → DEC-021…024;
"we're not going to wait" for B4), Codex's round 3 (`docs/tasks/CODEX-round3-20260911.md`: V3 confirmed, Lane X findings
repaired, B4 sensitivity control negative) and the orchestrator's round-3/4 work. No threshold, endpoint, arm, contrast
or budget changes; the reduced-programme rule of plan 4 §2 is exercised for B4.

## 1. What changed

1. **B4 is unavailable at the freeze** (DEC-020's condition failed: same-framework value gaps ≤ 0.15 vs 22.4 across
   frameworks; the adapter matches outputs, NLL, keys, radii and labels at 40/40). The frozen manifest records the reason;
   the C2-vs-B4 contrast is not run this month. Codex continues the gradient localization (Lane B4-D); a later registrable
   B4 needs a versioned manifest and its own runs, never an edit of the frozen one.
2. **The freeze is one command away** (`docs/lead_queue.md`, "Freeze now"), with the S4-02 allowances on the command line
   (2400 s per run; 97,200 s S4; 64,800 s S5). The scope is zsRE 1000 / CounterFact 300 / grammar 256 per task at 26.3 of
   27.0 accelerator hours (grammar priced from a GPU measurement, 0.085 s per sequence). S5 (SE-A/SE-E, SB reused from
   S4's C1) is priced at 12.8 of 18.0 hours.
3. **Execution machinery is ready:** `pccap queue` runs the fixed job list (210 S4 jobs, then 60 S5 jobs; 30 B4 jobs
   listed unavailable; 30 SB jobs listed reused) one subprocess at a time under the lease, resumable, stopping on refusals.
4. **S7 is D.9-conformant** after Lane X: damage averaged over every prefix of Q_i with operands recorded, original-prompt
   boundaries for boundary-keyed learners, the grammar pair block disjoint from every development diagnostic, strata
   qualified. The E.2 selection is regenerated; the CounterFact shared stratum stays at 9 (DEC-023).
5. **The confirmatory path has been reviewed three times** (R2, V, V2/V3) and every finding is repaired with a control;
   the frozen-identity check is verified on the real artifacts.

## 2. Sequence from here

```
lead: freeze --final (allowances on the command line) ──► orchestrator: schedule → pccap queue (S4: 210 jobs, realization-major)
   ├─ S4-05/06 incremental as pairs complete (D3 audit at the end of S4)
   ├─ pccap queue --stage S5 (60 jobs) once the S4 C1 runs of a realization exist (SB reuse) — interleaving by realization is allowed by the lease
   ├─ S7-01/02 on committed 300-edit checkpoints and the grammar task-4/8 checkpoints (E.2 selection ready) · S7-03
   └─ S8-01/02/03 · T4 review
Codex (ongoing.md §3): B4-D localization · S3-01 accurate control table · V4 re-check of the S7 repairs · reproduction pre-audit
```

Wall-clock: ≈ 60–80 h for S4 and ≈ 30–40 h for S5 serialized on the lease (wall/accelerator 1.5–3.7× on this host); the
queue survives restarts and stop files. The GPU is otherwise idle: short `-m gpu` tests from either agent may run alongside.

## 3. Board

62 done; partial: S1-07 (awaiting review), S4-01/03/04/05/06, S5-02, S7-01/03, S8-04; S2-05 in progress (Codex, B4-D);
S6 closed (DEC-022).
