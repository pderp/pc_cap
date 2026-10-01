# PRES-8 — rehearsal and audience questions

Status: complete for October 1 evidence; later result/review refresh pending by design. Agent: Capex. Inputs: Round57 deck, canonical supplemental reports, HT-17, reviewer entropy feedback and S4-LIM scope caveat.

Outputs: refreshed `docs/presentation/qa.md` (27 questions), `numbers_to_say.md`, `rehearsal.md`, slide12, both timed source scripts and `aw/rehearsal_pack.py`. Canonical export: sibling `assets/presentation-materials/deck_v3/rehearsal/` (39 hashed files plus rehearsal manifest). Earlier `round58-delivered/` is an intermediate preview. The pack includes twelve SVG slides, resolved 15/25-minute scripts, timing JSON, source-referenced numerical prompts, Q&A and three backup figures. No private equation-126 author question is in the public pack.

Verification: scripts allocate exactly 900/1500 seconds; estimated peak rates 121.7/142.4 words per minute. No unresolved result slots. Slide12 rendered and visually inspected with readable caveat/footer. Deck manifest includes 1,889 input bindings, including canonical PC-reader/Option R/AW-L report sources behind literal narrative values. X25 checks the export. The PC-reader answer explicitly awaits seeds1–2; Option R uses only four completed cells and retains deferrals. October2 review notes have not yet arrived.

Reproducer: `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ../venv/bin/python -m aw.rehearsal_pack --output ../assets/presentation-materials/deck_v3/NEW_REHEARSAL`. Update scientific narrative/literal values and canonical report pointers when new results arrive before exporting.

Done-when: met for current snapshot. Cost: CPU only, no models/GPU. Unresolved: charlie's rehearsal/talk-duration choice and Friday feedback; future results remain pending. No new scientific approval requested.
