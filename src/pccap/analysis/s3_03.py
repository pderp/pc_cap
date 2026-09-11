"""S3-03: grammar development matrix summary and routing-versus-tracing agreement (plan §6.9 S3-03; PDF D.10).

Reads the development grammar runs under ``results/S3/dev/grammar/<arm>/<base>/<read>/<r>/<perm>/`` and the
tracing results ``results/GRAM/tracing.json`` (DATA-07). For every run: ES/GS/RET-ES/RET-GS/LS/drift,
accepted-route counts per bank, order invariance across the two orders (per-item outcome equality, route
count equality). For C2: the accepted route distribution per mechanism kind (items joined to decisions by the
digest) against the tracing localization per kind (the earliest site whose restoration reaches R ≥ 0.5 on
≥ 50 % of pairs; "all sites" when every bank restores). Agreement is descriptive (D.10: tracing is a diagnostic,
not R*). Writes ``results/S3/grammar_dev_matrix.json`` and ``.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "S3"


def _digest16(item_id: str) -> str:
    return hashlib.sha256(item_id.encode()).digest()[:16].hex()


def summarize(root: Path) -> dict:
    runs = {}
    for mp in sorted(root.rglob("metrics.json")):
        if ".superseded-" in str(mp):
            continue
        d = mp.parent
        m = json.loads(mp.read_text())
        arm, perm = m["arm"], int(m["config"]["perm"])
        items = [json.loads(line) for line in (d / "items.jsonl").read_text().splitlines() if line.strip()]
        decs = [json.loads(line) for line in (d / "decisions.jsonl").read_text().splitlines() if line.strip()] if (d / "decisions.jsonl").exists() else []
        routes = Counter(int(b) for r in decs for b, inc in r["accepted_increment"].items() if inc > 0)
        mt = {k: v["value"] for k, v in m["metrics"].items()}
        runs[(arm, perm)] = {"metrics": {k: mt[k] for k in ("es_immediate", "gs_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end", "lm_drift_perplexity_ratio")},
                             "routes": {str(k): v for k, v in sorted(routes.items())}, "items": {it["item_id"]: it["es"] for it in items}, "decisions": decs,
                             "task_order": m["config"].get("task_order"), "n_items": len(items)}
    return runs


def order_invariance(runs: dict) -> dict:
    out = {}
    arms = sorted({a for a, _ in runs})
    for arm in arms:
        perms = sorted(p for a, p in runs if a == arm)
        if len(perms) < 2:
            continue
        a, b = runs[(arm, perms[0])], runs[(arm, perms[1])]
        common = set(a["items"]) & set(b["items"])
        same = sum(a["items"][i] == b["items"][i] for i in common)
        out[arm] = {"orders": perms, "items_common": len(common), "per_item_immediate_es_equal": same / len(common) if common else None,
                    "route_counts_equal": a["routes"] == b["routes"]}
    return out


def routing_vs_tracing(runs: dict, tracing: dict, arm: str = "C2") -> dict:
    from pccap.data import grammar_streams as gs

    # kind per item: regenerate the stream's items (seed-addressed) to read their strata
    kinds = {}
    for (a, perm), r in runs.items():
        if a != arm:
            continue
        for it in gs.stream(0, perm, r["n_items"] // 8):
            kinds[_digest16(it.item_id)] = it.strata["kind"]
    per_kind: dict[str, Counter] = defaultdict(Counter)
    for (a, _perm), r in runs.items():
        if a != arm:
            continue
        for dec in r["decisions"]:
            kd = kinds.get(dec["item_digest"])
            if kd is None:
                continue
            for b, inc in dec["accepted_increment"].items():
                if inc > 0:
                    per_kind[kd][int(b)] += 1
    trace_loc = {}
    for kd, v in tracing.get("by_kind", {}).items():
        frac = v["frac_site_ge_0.5"]
        sites = {k: f for k, f in frac.items()}
        strong = [k for k, f in sites.items() if f >= 0.5]
        banks = sorted({int(k.split("@")[0].replace("bank", "")) for k in strong})
        trace_loc[kd] = {"restoring_sites": sites, "earliest_restoring_bank": banks[0] if banks else None, "all_banks_restore": banks == [1, 2, 3]}
    agreement = {}
    for kd, c in per_kind.items():
        tot = sum(c.values())
        dist = {str(b): c[b] / tot for b in (1, 2, 3)} if tot else {}
        tl = trace_loc.get(kd, {})
        eb = tl.get("earliest_restoring_bank")
        agreement[kd] = {"c2_accepted_route_distribution": dist, "n_deliveries": tot, "tracing_earliest_restoring_bank": eb,
                         "tracing_all_banks_restore": tl.get("all_banks_restore"),
                         "share_at_earliest_restoring_bank": dist.get(str(eb)) if eb else None}
    return {"per_kind": agreement, "tracing_localization": trace_loc, "note": "descriptive (D.10): tracing on the learned model is a diagnostic; where every bank restores (input-token mechanisms) no depth is preferred by tracing"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "results" / "S3" / "dev" / "grammar"))
    ap.add_argument("--tracing", default=str(ROOT / "results" / "GRAM" / "tracing.json"))
    args = ap.parse_args(argv)
    runs = summarize(Path(args.root))
    tracing = json.loads(Path(args.tracing).read_text()) if Path(args.tracing).exists() else {}
    rep = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": {f"{a}/perm{p}": {k: v for k, v in r.items() if k not in ("items", "decisions")} for (a, p), r in runs.items()},
           "order_invariance": order_invariance(runs), "routing_vs_tracing": routing_vs_tracing(runs, tracing),
           "floor": "GS/RET-GS equal the frozen base's task accuracy (0.24–0.31): exact keys (SD-20) give no retrieval generalization on the grammar"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "grammar_dev_matrix.json").write_text(json.dumps(rep, indent=1, default=float))
    L = ["# S3-03 grammar development matrix (replacement grammar; one realization, two orders; 8 tasks × 16 items)", "",
         "| arm | order | ES | GS | RET-ES | RET-GS | LS | drift | accepted routes (1/2/3) |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for (a, p), r in sorted(runs.items()):
        m = r["metrics"]
        L.append(f"| {a} | {p} | {m['es_immediate']:.2f} | {m['gs_immediate']:.2f} | {m['ret_es_end']:.2f} | {m['ret_gs_end']:.2f} | {m['ls_complete_answer_end']:.2f} | {m['lm_drift_perplexity_ratio']:.3f} | {'/'.join(str(r['routes'].get(b, 0)) for b in ('1', '2', '3'))} |")
    L += ["", "Order invariance across the two committed orders:", ""]
    for arm, v in rep["order_invariance"].items():
        L.append(f"- {arm}: per-item immediate-ES equal on {v['per_item_immediate_es_equal']:.2f} of items; route counts equal: {v['route_counts_equal']}")
    L += ["", "C2 routing versus tracing (D.10, descriptive):", ""]
    for kd, v in rep["routing_vs_tracing"]["per_kind"].items():
        L.append(f"- {kd}: C2 accepted routes {v['c2_accepted_route_distribution']} over {v['n_deliveries']} deliveries; tracing's earliest restoring bank {v['tracing_earliest_restoring_bank']} (all banks restore: {v['tracing_all_banks_restore']}); share at that bank {v['share_at_earliest_restoring_bank']}")
    L += ["", rep["floor"], ""]
    (OUT / "grammar_dev_matrix.md").write_text("\n".join(L))
    print("\n".join(L[-8:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
