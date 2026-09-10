# pc_cap — continual-learning predictive-coding caps on GPT-2 (JAX)

A one-month, preregistered study of *caps*: small radius-gated activation memories written at three
depths of a frozen GPT-2 small, with routers that decide which depth an edit goes to. The scientific
contract is `docs/pc_cap_month_plan_readable.pdf`; the execution plans are `docs/updated_plan2.md` … `docs/updated_plan5.md` (each a delta over the previous); every decision that changed course is in `docs/decisions.md` (DEC-nnn) and every
specification defect in `docs/spec_defects.md` (SD-nn). The current work log is `docs/ongoing.md`;
the task board is `docs/tasks/STATUS.md`.

**What is measured.** Editing streams (zsRE, CounterFact; later a synthetic grammar) under the cap arms
C0/C1/C2/CR/CO and baselines B0 (frozen), B1 (LoRA), B3 (LoRA + replay), B4 (GRACE): immediate and
retained edit success, locality, LM drift, memory and accelerator cost; substrate properties P1–P6 of
the BP base and of an error-optimising predictive-coding (ePC) base regenerated here by distillation.

**Note on `docs/epc_energy.md`:** it documents the predictive-coding *energy functional*
(½Σ‖e‖² + task loss) and the error-optimisation solver — nothing to do with power consumption.

## Layout

```
src/pccap/        bases/ (functional GPT-2, BP and ePC wrappers)   pc/ (FabricPC nodes, ePC solver, KD energy)
                  cap/ (banks, transactions, learning)   routers/  transport/   baselines/ (B0/B1/B3, GRACE adapter)
                  harness/ (CLI runner, ledger, lease, snapshots, stages, arm registry, freeze, schedule)
                  data/ (datasets, tokenizer, decoding, sealed confirmation loader)   distill/ (ePC regeneration)
                  analysis/ (S1 properties, projections, memos, paired bootstrap)   metrics/   fixtures/
tests/            pytest; markers gpu (short CUDA), slow, lease (harness only)
manifests/        dev/ (development manifests), confirm/ (sealed), frozen.draft.json, tasks.json, datasets.json
results/          stage outputs (JSON/CSV/markdown), ledger, REG logs      docs/  plans, decisions, records, memos
scripts/          data preparation, diagnostics, reference recorders     logs/  interim reports
```

Large resources (datasets, weights, checkpoints, third-party clones, HF cache, auxiliary
environments) live outside the repository under `/home/derp/cap/assets/` (DEC-004).

## Quick start (this host)

```bash
cd /home/derp/cap/pc_cap
make test-fast        # CPU tests (~1 min)
make test-gpu         # short GPU tests (no lease)
make status           # regenerate docs/tasks/STATUS.md from manifests/tasks.json
/home/derp/cap/venv/bin/python -m pccap.cli report --stage S1     # render a stage report
/home/derp/cap/venv/bin/python -m pccap.cli run --stage S3 --arm C2 --manifest manifests/dev/s3_smoke.json --dry-run
```

The environment is the pre-existing JAX venv at `/home/derp/cap/venv` (Python 3.12, JAX 0.11 with the
CUDA 13 plugin, FabricPC 0.5.2, optax); `requirements.lock` is its exact `pip freeze` and
`docs/environment.md` describes it and the determinism flags applied by `import pccap`.
See `CONTRIBUTING.md` for the working protocol.

## Where things are

| Question | Look at |
| --- | --- |
| What was decided and why | `docs/decisions.md`, `docs/spec_defects.md` |
| What is done, what is running | `docs/tasks/STATUS.md`, `docs/tasks/<ID>.md`, `docs/ongoing.md` |
| Development results | `results/S0/report.md`, `results/S1/report.md`, `results/S2/report.md`, `results/S3/report.md`, `docs/D1_decision.md`, `docs/D2_decision.md` |
| ePC regeneration | `docs/tasks/REG-0{0,1,2,3}.md`, `results/REG/`, `docs/epc_energy.md` |
| Narrative so far | `logs/interim_report1.md` |
| The freeze | `manifests/frozen.draft.json`, `docs/lead_queue.md` T-CP-E |
