"""X2: independently aggregate existing research records; no model or sealed-data reads."""

from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/review_report_draft1"
EXP = "frozen-confirmatory-v2-84126123"
METRICS = ["es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end", "lm_drift_perplexity_ratio"]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree_digest(root):
    h = hashlib.sha256()
    for p in sorted(root.rglob("*.py")):
        h.update(p.relative_to(root).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    sources = {}

    def read(rel):
        p = ROOT / rel
        sources[str(rel)] = digest(p)
        return json.loads(p.read_text())

    fz = read("manifests/frozen.json")
    fsha = sources["manifests/frozen.json"]
    groups, records, evictions = defaultdict(list), [], defaultdict(list)
    for stage in ("S4", "S5"):
        for mp in sorted((ROOT / "results" / stage / EXP).rglob("metrics.json")):
            m = read(mp.relative_to(ROOT))
            c = read(mp.with_name("config.json").relative_to(ROOT))
            cost = read(mp.with_name("cost.json").relative_to(ROOT))
            row = {"path": str(mp.relative_to(ROOT)), "stage": stage, "dataset": m["config"]["dataset"], "arm": m["arm"],
                   "realization": m["config"]["realization"], "order": m["config"]["perm"], "status": m["status"],
                   "items": m["items_completed"], "planned": m["items_planned"],
                   "accel_seconds": cost["total"]["accel_seconds"], "wall_seconds": m["wall_seconds"],
                   "ledger_agrees": abs(cost["total"]["accel_seconds"] - m["ledger_totals"]["total"]["accel_seconds"]) < 1e-6,
                   "experiment_agrees": c["experiment_id"] == EXP and c["frozen_manifest_sha256"] == fsha,
                   "source_agrees": c["src_tree_sha256"] == fz["code_commit"]["src_tree_sha256"],
                   "base_unchanged": m["base_hash_before"] == m["base_hash_after"],
                   "frozen_identity": m["config"].get("frozen_identity"),
                   "drift_positions": m["metrics"]["lm_drift_perplexity_ratio"]["n"],
                   "metrics": {k: m["metrics"][k]["value"] for k in METRICS},
                   "occupied_bytes": m["metrics"].get("memory_occupied_bytes", {}).get("value")}
            records.append(row)
            key = f"{stage}/{row['dataset']}/{row['arm']}"
            groups[key].append(row)
            if stage == "S4" and row["dataset"] == "zsre" and row["arm"] in ("C0", "C1", "C2", "CR"):
                dp = mp.with_name("decisions.jsonl")
                n_evicted = n_allocated = n_events = 0
                with dp.open() as f:
                    for line in f:
                        if not line.strip():
                            continue
                        d = json.loads(line)
                        for v in d.get("per_bank", {}).values():
                            if v.get("code") != "accepted":
                                continue
                            n_events += 1
                            n_allocated += bool(v.get("allocated"))
                            n_evicted += v.get("evicted") is not None and v.get("evicted", -1) != -1
                sources[str(dp.relative_to(ROOT))] = digest(dp)
                evictions[key].append({"realization": row["realization"], "order": row["order"],
                                       "accepted_bank_events": n_events, "allocations": n_allocated, "evictions": n_evicted})
    cell_means = {}
    for key, rows in groups.items():
        cell_means[key] = {"runs": len(rows), "items": sorted({r["items"] for r in rows}),
                           "metrics": {k: statistics.mean(r["metrics"][k] for r in rows) for k in METRICS},
                           "metric_ranges": {k: [min(r["metrics"][k] for r in rows), max(r["metrics"][k] for r in rows)] for k in METRICS},
                           "accel_seconds_mean": statistics.mean(r["accel_seconds"] for r in rows),
                           "drift_positions": sorted({r["drift_positions"] for r in rows}),
                           "occupied_bytes_mean": statistics.mean(r["occupied_bytes"] for r in rows if r["occupied_bytes"] is not None)}
    paired = {}
    for label in ("zsre_complete", "counterfact_complete", "grammar_complete", "grammar_supplement"):
        d = read(f"results/S4/partial/s4_06_{label}.json")
        rep = d["report"]
        paired[label] = {"classification": rep["classification"], "inference": rep["inference"], "margins": rep["margins"],
                         "exclusions": {k: {kk: vv for kk, vv in v.items() if kk != "excluded_items"} for k, v in d.get("exclusions", {}).items()},
                         "contrasts": {}}
        for name in ("C2-C1", "C2-CR"):
            c = rep["contrasts"][name]
            paired[label]["contrasts"][name] = {"status": c["status"], "checks": c.get("checks"),
                                              "paired_table": c.get("paired_table"), "missing": c.get("missing"),
                                              "measures": {k: {kk: vv for kk, vv in v.items() if kk != "paired_differences"} for k, v in (c.get("measures") or {}).items()}}
    substrates = {ds: read(f"results/S5/paired_{ds}.json") for ds in ("zsre", "counterfact")}
    resource = read("results/S4/resource_views.json")
    ratios = defaultdict(list)
    for cell, arms in resource["comparable_compute"].items():
        for arm, v in arms.items():
            ratios[cell.split("/")[0] + "/" + arm].append(v["ratio_to_C2_update"])
    ratio_summary = {k: {"mean": statistics.mean(v), "min": min(v), "max": max(v), "within_20pct_cells": sum(0.8 <= x <= 1.2 for x in v), "cells": len(v)} for k, v in ratios.items()}
    s7 = read("results/S7/summary.json")
    s7_recomputed = []
    for p in sorted((ROOT / "results/S7" / EXP).rglob("reversals.json")):
        d = read(p.relative_to(ROOT))
        matrices = {}
        for st in ("shared", "private", "near_neighbour", "all"):
            pairs = [r for r in d["pairs"] if st == "all" or r["stratum"] == st]
            harm = [r[k] for r in pairs for k in ("I_ij", "I_ji")]
            matrices[st] = {"pairs": len(pairs), "ordered_directions": len(harm), "mean_damage": statistics.mean(harm),
                            "positive_direction_count": sum(v > 0 for v in harm), "positive_direction_fraction": statistics.mean(v > 0 for v in harm),
                            "positive_either_order_pairs": sum(r["I_ij"] > 0 or r["I_ji"] > 0 for r in pairs),
                            "D_mean": statistics.mean(r["D_ij"]["value"] for r in pairs),
                            "same_endpoint_count": sum(r["same_endpoint"] for r in pairs)}
        s7_recomputed.append({"path": str(p.relative_to(ROOT)), "dataset": d["dataset"], "checkpoint": d["checkpoint"], "matrices": matrices})
    variations = {}
    for ds in ("zsre", "counterfact", "grammar"):
        vals = []
        for arm in ("C0", "C1", "C2", "CR"):
            rel = f"results/S7/order_variation_{ds}_{arm}.json" if ds == "grammar" else f"results/S7/partial/order_variation_{ds}_{arm}_complete.json"
            d = read(rel)
            vals.extend(v["acc_ret_gs_std_across_orders"] for v in d["realizations"].values())
        variations[ds] = {"max_std_across_orders": max(vals), "cells": len(vals)}
    properties, property_differences = {}, {}
    for prop in (2, 3, 5, 6):
        b = read(f"results/S1/P{prop}_bp.json")
        e = read(f"results/S1/P{prop}_epc.json")
        properties[f"P{prop}_epc"] = {k: v.get("value") for k, v in e["metrics"].items()}
        differences = []
        for k in sorted(set(b["metrics"]) & set(e["metrics"])):
            x, y = b["metrics"][k].get("value"), e["metrics"][k].get("value")
            if isinstance(x, (int, float)) and isinstance(y, (int, float)) and round(x, 3) != round(y, 3):
                differences.append({"metric": k, "BP": x, "EPC": y})
        property_differences[f"P{prop}"] = differences
    p1 = read("results/S1/P1_epc.json")
    full_bytes = subprocess.check_output(["git", "show", "25c988b:results/S1/P1_epc.json"], cwd=ROOT)
    p1full = json.loads(full_bytes)
    p4 = read("results/S1/P4_gram.json")
    ablations = read("results/S8/ablations.json")
    ablation_groups = defaultdict(list)
    for row in ablations["rows"]:
        ablation_groups[f"{row['ablation']}/{row.get('factor', row.get('keys'))}/{row['arm']}"].append(row)
    ablation_means = {k: {"n": len(v), "items": sorted({r["items"] for r in v}),
                          "means": {m: statistics.mean(r[m] for r in v) for m in ("es", "ret_es", "ret_gs", "ls", "accel_s")}} for k, v in ablation_groups.items()}
    live_costs = defaultdict(float)
    for p in sorted((ROOT / "results").glob("S*/**/cost.json")):
        d = read(p.relative_to(ROOT))
        live_costs[p.relative_to(ROOT / "results").parts[0]] += d["total"]["accel_seconds"]
    tp = ROOT / "results/ledger/tasks.jsonl"
    sources[str(tp.relative_to(ROOT))] = digest(tp)
    task_costs = defaultdict(float)
    mapping = {"ENV": "S0", "DATA": "S0", "CAP": "S0", "REF": "S0", "GRAM": "S3", "REG": "S6", "ANA": "S4"}
    for line in tp.read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            prefix = d["task"].split("-")[0]
            task_costs[mapping.get(prefix, prefix)] += d.get("gpu_seconds", 0)
    old_budget = read("results/ledger/stages.json")
    versions = read("manifests/analysis_versions.json")
    budget_raw = {s: {"run_cost_seconds": live_costs[s], "task_cost_seconds": task_costs[s], "raw_sum_hours": (live_costs[s] + task_costs[s]) / 3600} for s in [f"S{i}" for i in range(9)]}
    # This is an audit of the collector inputs, not a newly certified all-cost ledger.
    for rel in ("docs/report.md", "docs/D3_decision.md", "docs/REPRODUCE.md", "docs/pc_cap_month_plan_readable.pdf", "docs/spec_defects.md", "docs/decisions.md"):
        sources[rel] = digest(ROOT / rel)
    evidence = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "run_records": records, "cell_means": cell_means, "zsre_accepted_event_counts": dict(evictions), "paired": paired,
                "substrate_paired": substrates, "compute_ratios": ratio_summary, "S7_published": s7, "S7_recomputed": s7_recomputed,
                "order_variation": variations, "property_metrics": properties, "property_differences_at_3dp": property_differences,
                "P1_current": {"H": p1["H"], "kl": p1["metrics"]["kl_mean"]["value"]},
                "P1_full_at_25c988b": {"sha256": hashlib.sha256(full_bytes).hexdigest(), "H": p1full["H"], "kl": p1full["metrics"]["kl_mean"]["value"]},
                "P4_metrics": {k: v.get("value") for k, v in p4["metrics"].items()},
                "ablation_means": ablation_means, "S8_row_accel_hours": sum(r["accel_s"] for r in ablations["rows"]) / 3600,
                "budget_collector_inputs": budget_raw, "published_budget_cache": {"total": old_budget["total_local_hours"], "ceiling": old_budget["total_ceiling_a100_h"]},
                "code": {"frozen": fz["code_commit"]["src_tree_sha256"], "current": tree_digest(ROOT / "src/pccap"), "analysis": tree_digest(ROOT / "src/pccap/analysis"),
                         "recorded_versions": versions, "changed_since_frozen_snapshot": subprocess.check_output(["git", "diff", "--name-only", "6b4b769", "HEAD", "--", "src/pccap"], cwd=ROOT, text=True).splitlines()},
                "source_sha256": sources, "gpu_seconds": 0,
                "limits": "Existing recorded outcomes only. No model replay, sealed-file reads or policy amendment. Cost aggregation can omit embedded ledgers or overlap task estimates; not an independently certified total."}
    with (OUT / "evidence.json").open("x") as f:
        json.dump(evidence, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"runs": len(records), "statuses": dict(Counter(r['status'] for r in records)), "sources": len(sources),
                      "S4_hours": sum(r['accel_seconds'] for r in records if r['stage'] == 'S4') / 3600,
                      "S5_hours": sum(r['accel_seconds'] for r in records if r['stage'] == 'S5') / 3600,
                      "code_changes": evidence['code']['changed_since_frozen_snapshot']}))


if __name__ == "__main__":
    main()
