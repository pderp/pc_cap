"""S7-01/02 summary over the committed checkpoints: damage matrices per stratum in both orders, D_ij, per-item accuracy
changes, update counts, allocations and evictions (PDF D.9).   python scripts/s7_summary.py → results/S7/summary.{json,md}"""

from __future__ import annotations

import glob
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = "frozen-confirmatory-v2-84126123"


def main() -> int:
    files = sorted(glob.glob(str(ROOT / "results" / "S7" / EXP / "*" / "*" / "r*" / "p*" / "*" / "reversals.json")))
    rows, out = [], {"experiment_id": EXP, "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "checkpoints": []}
    md = ["# S7-01/02 — cloned-state reversals and damage matrices (PDF D.9)", "", f"Rendered {out['written']} from {len(files)} checkpoint runs (`results/S7/{EXP}/`).", "",
          "D_ij = mean JS (nats) over Q = both edits' prefixes (prompt + paraphrases) and unrelated controls; I_ij = mean over Q_i of L_i(U_j U_i s) − L_i(U_i s) (complete-answer NLL, nats; positive = harm); I_ji symmetric. 100 fixed pairs per checkpoint (CounterFact 75: shared stratum 9, DEC-023).", ""]
    for f in files:
        d = json.load(open(f))
        ck = d["checkpoint"]
        acc = {"i_lost_ij": 0, "j_lost_ji": 0, "n": 0}
        for p in d["pairs"]:
            a = p["accuracy"]
            acc["n"] += 1
            acc["i_lost_ij"] += int(a["ij"]["i"][1] < 1.0)  # i not exact after i then j
            acc["j_lost_ji"] += int(a["ji"]["j"][1] < 1.0)
        rec = {"dataset": d["dataset"], "arm": d["arm"], "checkpoint": ck, "n_pairs": d["n_pairs"], "pairs_per_stratum": d["pairs_per_stratum"],
               "damage_matrix": d["damage_matrix"], "accel_seconds": d["ledger_totals"]["total"]["accel_seconds"], "wall_seconds": d["wall_seconds"],
               "first_edit_not_exact_after_second": {"i_after_ij": acc["i_lost_ij"] / max(1, acc["n"]), "j_after_ji": acc["j_lost_ji"] / max(1, acc["n"])},
               "same_endpoint_fraction": d["damage_matrix"]["all"]["same_endpoint_fraction"]}
        out["checkpoints"].append(rec)
        md += [f"## {d['dataset']} / {d['arm']} / {ck['tag']} ({ck['label']}; {ck['items']} items; state `{ck['state_hash'][:12]}…`)", "",
               "| stratum | n | I_ij (learn i, then j) | I_ji | both orders | harmful fraction | D_ij mean | D_ij max | rounds/update | allocations | evictions |",
               "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for stn, v in d["damage_matrix"].items():
            if v.get("n", 0) == 0:
                md.append(f"| {stn} | 0 | — | — | — | — | — | — | — | — | — |")
                continue
            md.append(f"| {stn} | {v['n']} | {v['I_ij_mean']:+.3f} | {v['I_ji_mean']:+.3f} | {v['I_both_orders_mean']:+.3f} | {v['I_positive_fraction']:.2f} | {v['D_ij_mean']:.4f} | {v['D_ij_max']:.4f} | {v['updates_mean_rounds']:.2f} | {v['allocations_total']} | {v['evictions_total']} |")
        md += ["", f"First edit no longer exact after the second: {rec['first_edit_not_exact_after_second']['i_after_ij']:.2f} (i after i→j), {rec['first_edit_not_exact_after_second']['j_after_ji']:.2f} (j after j→i); identical endpoint states in {rec['same_endpoint_fraction']:.0%} of pairs; {rec['accel_seconds']:.0f} accelerator s.", ""]
        rows.append(rec)
    # cross-checkpoint reading
    md += ["## Reading", ""]
    for rec in rows:
        dm = rec["damage_matrix"]
        order = sorted((s for s in ("shared", "private", "near_neighbour") if dm[s].get("n")), key=lambda s: -dm[s]["I_both_orders_mean"])
        md.append(f"- {rec['dataset']} {rec['checkpoint']['tag']}: damage ranks {' > '.join(f'{s} ({dm[s]['I_both_orders_mean']:+.2f})' for s in order)}; D_ij by stratum " + ", ".join(f"{s} {dm[s]['D_ij_mean']:.3f}" for s in order) + ".")
    md += ["", "Strata are operational proxies on the natural-language datasets and generator-defined on the grammar (`manifests/dev/s7_pairs.json`, `strata_qualification`). No analytic inverse of the allocation/eviction map is assumed; the same-endpoint fraction reports how often the two orders reached an identical complete state."]
    (ROOT / "results" / "S7" / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    (ROOT / "results" / "S7" / "summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[-len(rows) - 2:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
