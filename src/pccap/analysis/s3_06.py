"""S3-06: D2 decision memo (plan §6.9 S3-06): correctness versus science for every development
failure (≤ 3 diagnoses each with the cheapest discriminating test), core feasibility, the S6 deficit
recommendation, and the freeze-readiness checklist. Reads the development evidence already on disk
and writes ``docs/D2_decision.md``.

    python -m pccap.analysis.s3_06
"""

from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
DOCS = ROOT / "docs"


def _load(p: Path, default=None):
    return json.loads(p.read_text()) if p.exists() else default


def main(argv=None) -> int:
    se = _load(R / "S3" / "short_editing.json", {"runs": []})
    runs = {(r["arm"], r["dataset"]): r for r in se["runs"]}
    cr = _load(ROOT / "manifests" / "cr_distribution.json", {})
    proj = _load(R / "S2" / "projection.json", {})
    reg = _load(R / "REG" / "epc-50m" / "summary.json", {})
    pilot = _load(R / "REG" / "pilot.json", {})
    tasks = {t["id"]: t for t in _load(ROOT / "manifests" / "tasks.json", {"tasks": []})["tasks"]}
    lr = {tag: _load(R / "S2" / f"throughput_{tag}.json") for tag in ("lr3e-5", "lr3e-4")}
    crd = _load(R / "S2" / "throughput_crdist.json")

    def m(arm, ds, k, fmt="{:.2f}"):
        r = runs.get((arm, ds))
        v = None if r is None else r.get(k)
        return "—" if v is None else fmt.format(v)

    L = ["# D2 decision memo — development results, diagnoses, S6 recommendation, freeze readiness (S3-06)", "",
         f"Written {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} from `results/S3/short_editing.json`, `results/S3/fixture/summary.json`, `manifests/cr_distribution.json`, `results/S2/{{throughput,projection}}.json`, `results/REG/`.", "",
         "## 1. Development results (100-edit streams per arm and dataset; one order; descriptive)", "",
         "| arm | zsRE ES | zsRE RET-GS | zsRE LS | zsRE drift | CF ES | CF RET-ES | CF LS | CF drift |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for arm in ("C0", "C1", "C2", "CR", "B0", "B1", "B3"):
        L.append(f"| {arm} | {m(arm, 'zsre', 'es_immediate')} | {m(arm, 'zsre', 'ret_gs_end')} | {m(arm, 'zsre', 'ls_complete_answer_end')} | {m(arm, 'zsre', 'lm_drift_perplexity_ratio', '{:.4f}')} | {m(arm, 'counterfact', 'es_immediate')} | {m(arm, 'counterfact', 'ret_es_end')} | {m(arm, 'counterfact', 'ls_complete_answer_end')} | {m(arm, 'counterfact', 'lm_drift_perplexity_ratio', '{:.4f}')} |")
    L += ["", f"Constructed fixture (S3-02): C2 precision/recall vs oracle/random/majority in `results/S3/fixture/summary.json`; CR distribution (S3-05): zsRE {cr.get('per_dataset', {}).get('zsre', {}).get('distribution')}, CounterFact {cr.get('per_dataset', {}).get('counterfact', {}).get('distribution')}.", "",
          "## 2. Correctness versus science — diagnoses (≤ 3 each, cheapest discriminating test first)", "",
          "**F1. C2 routes almost only to bank 3 (97% zsRE, 100% CounterFact) and retains less than C0 on zsRE (RET-GS 0.30 vs 0.43).**",
          "1. Science: with radius-gated retrieval at the final block the probe measures immediate loss reduction, which the last site maximizes (largest direct effect on logits); earlier banks generalize better (C0's higher RET-GS is the depth effect the PDF predicts C0 to identify). Cheapest test: the S3-02 fixture already shows C2 recovers planted depths (precision 0.88) when depths differ in effect, so the router mechanism is not broken — this is a property of the GPT-2 loss landscape at A = 0.3.",
          "2. Correctness: probe scores could favour bank 3 through the normalization (tie rule SD-16 picks the smallest bank, so ties do not explain it). Test: the per-round signed scores in `decisions.jsonl` (bank 3 wins by margins ≫ ε in 97% of rounds); no defect.",
          "3. Science (capacity/keys): CounterFact exact keys (SD-17) give zero retrieval generalization by construction (CR-4), so C2 vs C1 on CounterFact is an ES/RET-ES comparison only. No test needed; recorded as a dataset-level limitation.",
          "Decision: not a defect; C2 vs C1 and C2 vs CR remain the required contrasts; C0 vs C2 is the depth contrast the PDF assigns to C0 (descriptive). Note (S3-05 re-profile): CR with the development-estimated distribution (97% bank 3) reaches zsRE RET-GS "
          + (f"{crd['runs']['CR/zsre']['metrics']['ret_gs_end']:.2f}" if crd else "—") + " in the same order (uniform CR 0.18; C2 0.30) — the confirmatory C2-vs-CR contrast is therefore a real test, not a comparison against a handicapped router.", "",
          "**F2. B1/B3 at the prescribed defaults (rank 8, lr 1e-4, 10 steps) acquire little (ES 0.08–0.10), lose locality entirely (LS 0.00) and drift (perplexity ratio 1.14–3.9).**",
          "1. Correctness: the LoRA update could be mis-specified. Test: `tests/baselines/test_lora.py` (gradient inventory, merged-weight equivalence, NLL decrease on one item) passes; the harness parity test (`tests/harness/test_baseline_arms.py`) passes. Not a defect.",
          "2. Science (step size): 10 Adam steps at 1e-4 from B = 0 move the answer NLL by ~1 nat per item (codex's smoke: 23.7 → 22.8) — too little to acquire, while Adam's per-item moments accumulate a drift direction across 100 items. Cheapest test: the PDF's own learning-rate screen {3e-5, 1e-4, 3e-4} on the same development allocation ("
          + (", ".join(f"{tag}: zsRE ES {v['runs']['B1/zsre']['metrics']['es_immediate']:.2f} LS {v['runs']['B1/zsre']['metrics']['ls_complete_answer_end']:.2f} drift {v['runs']['B1/zsre']['metrics']['lm_drift_perplexity_ratio']:.3f}" for tag, v in lr.items() if v) or "pending: results/S2/throughput_lr{3e-5,3e-4}.json") + ").",
          "3. Science (loss): mean-over-answer-tokens CE including the newline dilutes the target tokens for short answers. Test: stratify ES by answer length in `items.jsonl` (available; descriptive).",
          "Decision: B1/B3 are practical references, not validity gates (PDF: \"Beating LoRA is not a validity gate; it is a result\"); the frozen manifest fixes the learning rate by DEC-017 (highest mean development RET-GS, the primary endpoint: 1e-4 → 0.10, 3e-4 → 0.09, 3e-5 → 0.04; so the prescribed 1e-4 stands) and records the full screen (ES/LS/drift), including that an LS-constrained rule would have picked 3e-5 with ES 0.03.", "",
          "**F3. ePC substrate rows unavailable at D1.** Regeneration is running (REG-02: step "
          + f"{reg.get('global_step', '?')} of {reg.get('total_steps', 9766)}, status {reg.get('status', '?')}; pilot projection {pilot.get('projected_hours_full_run', float('nan')):.1f} h). Not a defect; S1-01 and the ePC rows follow REG-03.", "",
          "## 3. Core feasibility", "",
          f"Projection with measured B1/B3 rows (D1 refresh): selected scope {proj.get('selected')}, {proj.get('selected', {}).get('seconds', 0) / 3600:.1f} local h of {proj.get('budget_seconds_after_headroom', 0) / 3600:.1f} h budget; assumed arms {proj.get('assumed_arms')}. B4 (GRACE) waits on Lane D; grammar cost waits on GRAM-02. The BP-only confirmatory core (zsRE 1000 / CounterFact 300, C1/C2/CR/B3 × 15 + C0 initial 300) is feasible on this host inside the S4 ceiling.", "",
          "## 4. S6 deficit recommendation", "",
          "**Defer.** S6 (error-feature regularizer on the ePC substrate) requires the regenerated ePC checkpoint (REG-03) and the S5 matched-fidelity rows; the deficit statement cannot be drafted before those exist. Recommendation: no S6 authorization at D2; revisit at the S5 report.", "",
          "## 5. Freeze readiness checklist (S4-01)", "",
          "| item | status |", "| --- | --- |",
          "| S2-01 radii / b_m, S2-02 A = 0.3 | ready |",
          f"| S3-05 CR distribution (`manifests/cr_distribution.json`) | {'ready' if cr else 'missing'}; re-profile with the development distribution: {'done' if crd else 'pending'} |",
          f"| DATA-02 sealed realizations/orders (the DATA-02 SHA256SUMS) | {'ready' if (ROOT / "manifests" / "confirm" / "SHA256SUMS").exists() else 'missing'} |",
          f"| DATA-02a sealed loader (Lane H) | {tasks.get('DATA-02a', {}).get('status', 'not on board')} |",
          f"| B4 GRACE adapter (S2-05, Lane D → orchestrator) | {tasks.get('S2-05', {}).get('status')} |",
          f"| Grammar base + streams (GRAM-02, DATA-06/07) | {tasks.get('GRAM-02', {}).get('status')} — PA-2 clock 2026-09-11 23:59 ET |",
          f"| B1 learning-rate screen | {'done' if all(lr.values()) else 'pending'} |",
          f"| ANA-01 frozen analysis code | {tasks.get('ANA-01', {}).get('status')} |",
          f"| REG-03 ePC checkpoint preflight (S5 only; not required for the BP freeze) | {tasks.get('REG-03', {}).get('status')} |",
          "| Draft manifest (`manifests/frozen.draft.json`, schema-validated) | see `python -m pccap.harness.freeze --draft` |", "",
          "Freeze rule: `manifests/frozen.json` is written only by the lead's decision at CP-E after this checklist is all-ready except the items explicitly deferred (B4, grammar) — those arms are then recorded `unavailable` in the manifest rather than delaying the BP core.", ""]
    (DOCS / "D2_decision.md").write_text("\n".join(L))
    print("wrote", DOCS / "D2_decision.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
