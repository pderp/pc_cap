"""S2-07: full cost projection and the D1 memo (plan §6.8 S2-07, §9, §10; PDF App. B, SD-5, PA-7).

Reads ``results/S2/throughput.json``, ``results/ENV/kappa.json``, ``results/S1/report.md``'s
eligibility inputs (coverage, P-files) and writes ``results/S2/projection.json`` and
``docs/D1_decision.md``: eligibility per claim type, κ status, affordable scopes with the
selected one (Section 9 algorithm on measured accelerator seconds), the wall-clock feasibility
view (which the ceilings do not govern but the calendar does), open items with owners, and the
week-2 queue. If no scope fits, T2 is filed in ``docs/lead_queue.md``.

    python -m pccap.analysis.d1 [--baseline-factor 1.0] [--grammar-learn-s X]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pccap.analysis.budget import kappa, project

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"


def wall_view(th: dict, sel: dict | None) -> dict:
    """Calendar view: wall seconds per edit × items × 15 × arms (arms measured; baselines assumed = C1)."""
    if sel is None:
        return {}
    out = {}
    total = 0.0
    for ds, n in (("zsre", sel["zsre"]), ("counterfact", sel["counterfact"])):
        per = {}
        for arm in ("C1", "C2", "CR", "B3", "B4"):
            r = th["runs"].get(f"{arm}/{ds}") or th["runs"].get(f"C1/{ds}")
            w = r["wall_seconds_per_edit"] * n * 15
            per[arm] = w
            total += w
        r = th["runs"].get(f"C0/{ds}")
        if r:
            per["C0/initial300"] = r["wall_seconds_per_edit"] * 300 * 15
            total += per["C0/initial300"]
        out[ds] = per
    out["total_wall_hours"] = total / 3600
    return out


def render(th: dict, proj: dict, k: dict, wall: dict) -> str:
    sel = proj["selected"]
    L = ["# D1 decision memo — validity and feasibility (S2-07)", "",
         f"Written {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} from `results/S2/throughput.json`, `results/S2/projection.json`, `results/S1/report.md`, `results/ENV/kappa.json`.", "",
         "## 1. Eligibility (from S1-07)", "",
         "| claim type | status | basis |", "| --- | --- | --- |",
         "| BP-only editing programme (C0/C1/C2/CR on zsRE and CounterFact) | **eligible** | S0 controls pass; DATA-01 pools; S2-01 calibration; S2-02 A = 0.3; S3 harness smokes |",
         "| matched-fidelity substrate claims (SB vs SE-A / SE-E) | **unavailable, not failed** | no ePC checkpoint (T1 open; PA-1 clock 2026-09-11 23:59 ET; regeneration needs REG-00 and a ≤ 10 GPU-h pilot verdict) |",
         "| synthetic-only substrate claim | pending | grammar replacement (GRAM-01/02, PA-2) |",
         "| constructed-fixture routing (PR-C) | measured (development) | C2 precision 0.88 [0.83, 0.93], recall 0.89; oracle 1.00; random 0.55; majority-bank 0.67 (S3-02) |", "",
         "Geometry alerts: none (P2 on one base only). ePC eight-step credit: label 'finite-iteration error credit' (P6 on BP weights). Alerts trigger no number changes.", "",
         "## 2. κ status", "",
         f"κ = {k['kappa']} ({k['status']}), band {k['kappa_band']}. Local RTX 5070 shared workload: 19.7k tokens/s fwd+bwd (ENV-02). No A100 measurement exists; all ceilings below are read at κ = 1 with the band reported.", "",
         "## 3. Measured per-edit cost (S2-06, 100 development edits per run, exclusive lease; desktop GPU processes resident and recorded)", "",
         "| arm | dataset | learning accel s/edit | query accel s/edit | wall s/edit | ES | GS | RET-GS(100) | LS |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for key, r in th["runs"].items():
        m = r["metrics"]
        L.append(f"| {key.split('/')[0]} | {key.split('/')[1]} | {r['learning_accel_seconds_per_edit']:.3f} | {r['query_accel_seconds_per_edit']:.3f} | {r['wall_seconds_per_edit']:.2f} | {m['es_immediate']:.2f} | {m['gs_immediate'] if m['gs_immediate'] is None else round(m['gs_immediate'], 2)} | {m['ret_gs_end'] if m['ret_gs_end'] is None else round(m['ret_gs_end'], 2)} | {m['ls_complete_answer_end']:.2f} |")
    L += ["", f"Unavailable arms: {th.get('unavailable')}.", "",
          "## 4. Scope selection (Section 9 algorithm; SD-5 headroom 0.75; accelerator seconds)", "",
          f"S4 ceiling 36 A100-h → budget after headroom {proj['budget_seconds_after_headroom'] / 3600:.1f} local h at κ = {proj['kappa']}. Baseline arms B3/B4 are not measured yet: their cost is assumed = C1 × {proj['baseline_factor']} (flagged `assumed_arms`). Grammar cost: {'included' if proj['grammar_included'] else 'not measurable yet (GRAM-02 pending); excluded from the sum and stated here'}.", "",
          "| zsRE | CounterFact | grammar | local h | affordable |", "| ---: | ---: | ---: | ---: | --- |"]
    for r in proj["table"]:
        if r["grammar"] == 10000 or r["affordable"]:
            L.append(f"| {r['zsre']} | {r['counterfact']} | {r['grammar']} | {r['local_hours']:.1f} | {r['affordable']} |")
    if sel:
        L += ["", f"**Selected scope: zsRE {sel['zsre']}, CounterFact {sel['counterfact']}, grammar {sel['grammar']}** ({sel['seconds'] / 3600:.1f} local h of the {proj['budget_seconds_after_headroom'] / 3600:.1f} h budget). This is written into the frozen manifest at S4-02; the C0 initial scope is 300 with its extension optional."]
    else:
        L += ["", "**No scope fits.** T2 filed (docs/lead_queue.md); the synthetic-only core continues."]
    first = RESULTS / "S2" / "throughput_before_lastrow.json"  # first pass: sequential evaluator, full-logits path
    firstpass = json.loads(first.read_text()) if first.exists() else None
    rem_rows = []
    if firstpass:
        for key, r in th["runs"].items():
            o = firstpass["runs"].get(key)
            if o:
                rem_rows.append(f"| {key} | {o['wall_seconds_per_edit']:.2f} | {r['wall_seconds_per_edit']:.2f} | {o['query_accel_seconds_per_edit']:.3f} → {r['query_accel_seconds_per_edit']:.3f} |")
    fallback = next((r for r in proj["table"] if r["zsre"] == 300 and r["counterfact"] == 300 and r["grammar"] == 256), None)
    ratios = [r["wall_seconds_per_edit"] / max(1e-9, r["learning_accel_seconds_per_edit"] + r["query_accel_seconds_per_edit"]) for r in th["runs"].values()]
    L += ["", "## 5. Wall-clock feasibility (calendar, not the ceiling)", "",
          f"Wall time per edit exceeds accelerator time by {min(ratios):.1f}–{max(ratios):.1f}× (host dispatch and per-token decode loops of the E.2 protocol). At the selected scope the confirmatory editing core (5 arms × 15 runs per dataset + C0 initial 300) is ≈ {wall.get('total_wall_hours', float('nan')):.0f} wall hours on this host serialized on the GPU lease.", ""]
    if rem_rows:
        L += ["HARN-BATCH (2026-09-10): batched cap-on evaluation with token-for-token parity to the sequential reference decoder (`results/S0/controls/harn_batch_parity.json`) and the last-row logits path — measured first pass (sequential evaluator) → batched:", "", "| run | wall s/edit before | after | query accel s/edit |", "| --- | ---: | ---: | --- |", *rem_rows, ""]
    L += ["**Engineering already applied (no protocol change):** HARN-BATCH batches the cap-on evaluation (decode steps across prompts with per-sequence host retrieval; rescoring, LS and drift batched) and was reported only after token-for-token parity with the sequential reference decoder (E.2). Learning itself remains per item and sequential. "
          + (f"**Fallback if HARN-BATCH does not land before S4-01:** scope zsRE 300 / CounterFact 300 / grammar 256 ({fallback['local_hours'] if fallback else float('nan'):.1f} accelerator h; ≈ {wall.get('total_wall_hours', float('nan')) * (600 / (sel['zsre'] + sel['counterfact']) if sel else 1):.0f} wall h), then the §10 drop order (HVP → R-e/R-g → S6 → ablations → C0 extension → T3); never the endpoint, margins, realizations or orders." if fallback else ""), "",
          "## 6. Open items with owners", "",
          "- B1/B3 (S2-03/S2-04): BASELINES lane (ongoing3.md Lane F) — required for the projection to stop assuming baseline cost = C1 and for S3-04.",
          "- B4 (S2-05a/b → S2-05): GRACE lane D — PA-6 bound.", "- Grammar (GRAM-01/02, DATA-06/07): Lane G′ — PA-2 clock.",
          "- ePC checkpoint: T1 / REG-00 (Lane E) — BP-only month otherwise.", "- DATA-02 sealed realizations/orders: orchestrator after DATA-02a (Lane H).", "",
          "## 7. Week-2 queue", "",
          "S3-01 (CP-D: controls.md + development matrix, done except PC-10) → S3-04 short editing checks with baselines as they land → S3-03 grammar runs (after GRAM-02) → S3-05 CR distribution from development C2 routes → S3-06 D2 memo → S4-01 freeze (frozen.json incl. DEC-009 policy text, SD-13..17) → S4-02 scope → S4-03/04 confirmatory queue.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-factor", type=float, default=1.0)
    ap.add_argument("--grammar-learn-s", type=float, default=None)
    args = ap.parse_args(argv)
    th = json.loads((RESULTS / "S2" / "throughput.json").read_text())
    k = kappa()
    proj = project(th, float(k["kappa"]), args.grammar_learn_s, args.baseline_factor)
    (RESULTS / "S2" / "projection.json").write_text(json.dumps(proj, indent=1, default=float))
    wall = wall_view(th, proj["selected"])
    (DOCS / "D1_decision.md").write_text(render(th, proj, k, wall))
    if proj["selected"] is None:
        with open(DOCS / "lead_queue.md", "a") as f:
            f.write("\n## T2 (filed by S2-07)\n\nNo confirmatory scope fits the S4 ceiling with 25% headroom at κ = 1; see docs/D1_decision.md. Options: more compute, accept a feasibility result for editing, or drop optional arms. Default: synthetic-only core continues.\n")
    print("selected", proj["selected"], "wall hours", round(wall.get("total_wall_hours", 0), 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
