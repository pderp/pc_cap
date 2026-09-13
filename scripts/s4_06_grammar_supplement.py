"""SD-22 supplement: the grammar paired analysis on the complete-pair subset.

The frozen policy classifies the grammar `incomplete` because 0–3 items per cell have an undefined RET-GS (no paraphrase
found; per-process hash salt, SD-22). This supplement runs the SAME frozen machinery with the expected inventory
restricted, per realization, to the items whose RET-GS is defined in EVERY cell (all arms, all orders) — an exclusion
that is independent of the edit outcome and identical for every arm — and reports the exclusion counts. It is labelled
supplementary; it does not replace the frozen classification.   python scripts/s4_06_grammar_supplement.py"""

from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = "frozen-confirmatory-v2-84126123"


def main() -> int:
    from pccap.analysis.paired import analyze_paired
    from pccap.analysis.s4_06 import collect_rows, expected_from_loader

    rows, notes = collect_rows(ROOT / "results" / "S4" / EXP, "grammar", EXP)
    expected = expected_from_loader("grammar")
    undefined: dict[int, set] = {r: set() for r in expected}
    cells: dict[int, int] = {r: 0 for r in expected}
    seen_cells = set()
    for row in rows:
        if row["ret_gs"] is None:
            undefined[row["realization"]].add(row["item_id"])
        seen_cells.add((row["realization"], row["arm"], row["order"]))
    for r, _arm, _o in seen_cells:
        cells[r] += 1
    restricted = {r: [i for i in ids if i not in undefined[r]] for r, ids in expected.items()}
    kept_rows = [row for row in rows if row["item_id"] in set(restricted[row["realization"]])]
    rep = analyze_paired(kept_rows, expected_items=restricted, stream_id="grammar", draws=10_000)
    out = {"label": "SUPPLEMENTARY (SD-22): complete-pair subset; not the frozen classification", "experiment_id": EXP,
           "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "exclusions": {str(r): {"excluded_items": sorted(undefined[r]), "n_excluded": len(undefined[r]), "n_expected_full": len(expected[r]), "n_kept": len(restricted[r]), "cells": cells[r]} for r in expected},
           "rule": "an item is excluded for a realization if its RET-GS is undefined (no paraphrase) in any cell (arm × order) of that realization; the same subset is used for every arm",
           "report": rep, "collector_notes": notes}
    (ROOT / "results" / "S4" / "partial" / "s4_06_grammar_supplement.json").write_text(json.dumps(out, indent=1, default=float))
    print("exclusions per realization:", {r: v["n_excluded"] for r, v in out["exclusions"].items()})
    print("classification (supplementary):", rep["classification"])
    for name in ("C2-C1", "C2-CR"):
        c = rep["contrasts"][name]
        print(f"{name}: {c['classification']}; checks {c['checks']}")
        for meas, m in (c.get("measures") or {}).items():
            e, iv = m.get("estimate", {}), m.get("interval", {})
            print(f"  {meas:8s} Δ={e.get('value'):+.4f} 97.5% [{iv.get('lower'):+.4f}, {iv.get('upper'):+.4f}] per-realization {[round(x, 4) for x in m.get('realization_means', [])]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
