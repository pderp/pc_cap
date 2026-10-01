# S4-LIM — model-scale and incomplete-scope caveats

Status: complete. Agent: Capex. Inputs: saved triplet/270-cell reports, DEC-074b/080, Round58 instruction. Outputs: three refreshed Stage-4 reports and slide12, shared `aw/report_limitations.py`, producer refresh paths, updated source registry.

All three reports state GPT-2 small (124M) with no established transfer to production scale, the original DEC-074b omissions, and the separate Option R stable-v0 deferral. Historical triplet/comparator documents use a prose-only producer command preserving their figure decoration and all existing text. The assembly is regenerated from saved tables; no analyzer/classifier rerun occurred.

Verification: `logs/additional_work/S4-LIM/verification.json` and exact diffs: every table is identical; changes are the added caveat and necessary source-hash updates only. Previous documents/assembly are in `before/`. Original producer versions are preserved under `docs/tasks/round58-source-archive/`; `aw.reporting_sources` supports historical tests without changing runtime resolution. The comparator test imports this reporting-only resolver and still requires the exact original hash.

Reproduce: `python -m aw.triplet_report limitations`; `python -m aw.comparator_report limitations --output logs/R1/reports/comparators-270`; `python -m aw.stage4_assembly --output logs/R1/reports/stage4-assembled --document docs/R1_stage4_report.md --refresh`, using the CPU venv. The normal publication paths also include the caveat.

Done-when: met. Cost: CPU only, zero model calls/GPU. Unresolved/questions: none. Existing numerical snapshots, inference and live dependencies unchanged.
