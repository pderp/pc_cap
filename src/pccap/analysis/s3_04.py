"""S3-04: short editing checks — summary over 100-edit development streams (plan §6.9).

The S2-06 profile runs (``results/S2/throughput/<arm>/<dataset>/``) are 100-edit development
streams per arm and dataset under the common decoder with every decision logged. This module
summarizes, per run: proposed routes (scheduled banks), accepted writes, acquired complete
answers (immediate ES) and threshold attainment — reported separately; abstentions,
no-direction events, allocations vs value-updates of existing slots, evictions, conflicts
(ambiguous-key rejections), probe counts and search candidates; retrieval drift proxy (slots per
bank at the end); locality and LM drift at the end.

    python -m pccap.analysis.s3_04 [--root results/S2/throughput]  → results/S3/short_editing.json / .md
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "S3"


def summarize_run(d: Path) -> dict | None:
    if not (d / "metrics.json").exists() or not (d / "decisions.jsonl").exists():
        return None
    m = json.loads((d / "metrics.json").read_text())
    decs = [json.loads(line) for line in (d / "decisions.jsonl").read_text().splitlines() if line.strip()]
    items = [json.loads(line) for line in (d / "items.jsonl").read_text().splitlines() if line.strip()]
    proposed = Counter()
    accepted = Counter()
    codes = Counter()
    allocated = evicted = conflicts = rejected = 0
    for r in decs:
        for b in r["candidate_banks"]:
            proposed[str(b)] += 1
        for b, inc in r["accepted_increment"].items():
            if inc > 0:
                accepted[b] += 1
        for c in r["codes"]:
            codes[c] += 1
        for _b, pb in r.get("per_bank", {}).items():
            if pb.get("code") == "accepted":
                allocated += int(bool(pb.get("allocated")))
                evicted += int(pb.get("evicted", -1) >= 0)
            if pb.get("code") == "ambiguous_key_conflict":
                conflicts += 1
            if pb.get("code") == "rejected_no_improvement":
                rejected += 1
    cost = json.loads((d / "cost.json").read_text()) if (d / "cost.json").exists() else {}
    final = m["metrics"]
    return {
        "arm": m.get("arm"), "dataset": d.name, "items": len(items), "rounds": len(decs),
        "proposed_routes": dict(proposed), "accepted_writes": dict(accepted), "abstain_rounds": codes.get("abstain", 0),
        "no_direction_events": codes.get("no_direction", 0), "allocations": allocated, "value_updates_on_existing_slots": sum(accepted.values()) - allocated,
        "evictions": evicted, "ambiguous_key_conflicts": conflicts, "rejected_no_improvement": rejected,
        "router_probes": cost.get("learning", {}).get("router_probes"), "search_candidates": cost.get("learning", {}).get("search_candidates"),
        "threshold_acquisition": final["threshold_acquisition"]["value"], "es_immediate": final["es_immediate"]["value"],
        "gs_immediate": final["gs_immediate"]["value"], "ret_es_end": final["ret_es_end"]["value"], "ret_gs_end": final["ret_gs_end"]["value"],
        "ls_complete_answer_end": final["ls_complete_answer_end"]["value"], "ls_kl_end": final["ls_kl_end"]["value"],
        "lm_drift_perplexity_ratio": final["lm_drift_perplexity_ratio"]["value"], "memory_occupied_bytes": final["memory_occupied_bytes"]["value"],
        "rounds_per_item": len(decs) / max(1, len(items)),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "results" / "S2" / "throughput"))
    args = ap.parse_args(argv)
    root = Path(args.root)
    rows = []
    for arm_dir in sorted(root.iterdir()) if root.exists() else []:
        for ds_dir in sorted(arm_dir.iterdir()):
            if ds_dir.name == "warmup":
                continue
            r = summarize_run(ds_dir)
            if r:
                r["arm"] = r["arm"] or arm_dir.name
                rows.append(r)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "short_editing.json").write_text(json.dumps({"source": str(root), "runs": rows, "baselines": "B1/B3/B4 pending (Lane F/D)"}, indent=1, default=float))
    L = ["# S3-04 short editing checks (100 development edits per arm and dataset)", "", f"Source runs: `{root}`. Baselines B1/B3/B4 pending.", "",
         "| arm | dataset | rounds/item | proposed routes (1/2/3) | accepted writes (1/2/3) | abstain | no-dir | allocs | updates | evict | conflicts | rejected | probes | thr | ES | GS | RET-ES | RET-GS | LS | LS-KL | drift ratio |",
         "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        pr = "/".join(str(r["proposed_routes"].get(b, 0)) for b in ("1", "2", "3"))
        ac = "/".join(str(r["accepted_writes"].get(b, 0)) for b in ("1", "2", "3"))
        f = lambda v, fmt="{:.2f}": "—" if v is None else fmt.format(v)  # noqa: E731
        L.append(f"| {r['arm']} | {r['dataset']} | {r['rounds_per_item']:.1f} | {pr} | {ac} | {r['abstain_rounds']} | {r['no_direction_events']} | {r['allocations']} | {r['value_updates_on_existing_slots']} | {r['evictions']} | {r['ambiguous_key_conflicts']} | {r['rejected_no_improvement']} | {r['router_probes']} | {f(r['threshold_acquisition'])} | {f(r['es_immediate'])} | {f(r['gs_immediate'])} | {f(r['ret_es_end'])} | {f(r['ret_gs_end'])} | {f(r['ls_complete_answer_end'])} | {f(r['ls_kl_end'], '{:.4f}')} | {f(r['lm_drift_perplexity_ratio'], '{:.4f}')} |")
    L += ["", "Proposed routes, accepted writes and acquired complete answers are reported separately (PDF S3). CounterFact runs use exact keys (SD-17), so GS/RET-GS from retrieval are 0 by construction there (CR-4)."]
    (OUT / "short_editing.md").write_text("\n".join(L) + "\n")
    print(f"{len(rows)} runs summarized -> {OUT / 'short_editing.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
