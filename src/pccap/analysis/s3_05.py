"""S3-05: CR bank distribution from development C2 accepted routes (plan §6.9 S3-05; SD-11).

Counts accepted deliveries per bank over the C2 development streams (``results/S2/throughput/C2/<ds>/
decisions.jsonl``; abstentions and rejected rounds are excluded from the normalizer but reported).
Writes ``manifests/cr_distribution.json`` with per-dataset and pooled distributions; the confirmatory
CR uses the per-dataset distribution (label ``cr_dev_c2_<ds>``), uniform if C2 never routed.

    python -m pccap.analysis.s3_05 [--root results/S2/throughput]
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def estimate(decisions: list[dict]) -> dict:
    accepted, abstain, rejected, rounds = Counter(), 0, 0, 0
    for r in decisions:
        rounds += 1
        if "abstain" in r["codes"]:
            abstain += 1
        got = False
        for b, inc in r["accepted_increment"].items():
            if inc > 0:
                accepted[int(b)] += 1
                got = True
        if not got and "abstain" not in r["codes"]:
            rejected += 1
    n = sum(accepted.values())
    if n == 0:
        dist, label = {1: 1 / 3, 2: 1 / 3, 3: 1 / 3}, "cr_uniform_no_c2_routes"
    else:
        dist, label = {m: accepted.get(m, 0) / n for m in (1, 2, 3)}, "cr_dev_c2"
    return {"distribution": {str(k): v for k, v in dist.items()}, "label": label, "accepted_per_bank": {str(k): accepted.get(k, 0) for k in (1, 2, 3)},
            "accepted_total": n, "rounds": rounds, "abstain_rounds": abstain, "rejected_rounds": rejected}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "results" / "S2" / "throughput"))
    ap.add_argument("--out", default=str(ROOT / "manifests" / "cr_distribution.json"))
    args = ap.parse_args(argv)
    root = Path(args.root) / "C2"
    per, pooled = {}, []
    for ds_dir in sorted(p for p in root.iterdir() if p.is_dir() and p.name != "warmup"):
        decs = [json.loads(line) for line in (ds_dir / "decisions.jsonl").read_text().splitlines() if line.strip()]
        per[ds_dir.name] = estimate(decs) | {"source": str(ds_dir.relative_to(ROOT))}
        per[ds_dir.name]["label"] += f"_{ds_dir.name}"
        pooled += decs
    out = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rule": "accepted C2 deliveries per bank over development streams (SD-11); per-dataset distribution used in confirmatory CR; abstentions/rejections excluded from the normalizer",
           "per_dataset": per, "pooled": estimate(pooled) | {"label": "cr_dev_c2_pooled"}, "profile_distribution": {"1": 1 / 3, "2": 1 / 3, "3": 1 / 3, "label": "cr_profile_uniform"}}
    Path(args.out).write_text(json.dumps(out, indent=1))
    for ds, v in per.items():
        print(ds, v["distribution"], "accepted", v["accepted_total"], "of", v["rounds"], "rounds; abstain", v["abstain_rounds"], "rejected", v["rejected_rounds"])
    print("pooled", out["pooled"]["distribution"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
