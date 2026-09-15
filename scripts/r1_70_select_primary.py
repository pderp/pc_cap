"""DEC-049/DEC-050: select the primary reader among candidate (training run, checkpoint) pairs on COMMON development
populations. Reads the stream-eval summaries (`results/R1/stream_eval_<tag>*.json`; tags built as
<run>_step<N>_rare1_null0.5 with dataset suffix @counterfact / @mquake) and the zsRE unseen summaries
(`results/R1/endpoints/<run>_step<N>_rare1_n100_unseen_zsre/summary.json`), applies the rule — mean RET-GS over the three
datasets, subject to zsRE unseen false fires ≤ 10 % at 100 records and LS ≥ 0.98 on every dataset — and writes
`manifests/revision_v1/primary_selection_v1.json` with every candidate's numbers, the admissible set, the winner and the
population identities. No model execution.
    python scripts/r1_70_select_primary.py --runs r1_50_stream_tri4_text_s0,... --steps 50,100,150,200,250,300"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("zsre", "counterfact", "mquake")


def load_eval(tag: str, ds: str):
    p = ROOT / "results" / "R1" / (f"stream_eval_{tag}.json" if ds == "zsre" else f"stream_eval_{tag}@{ds}.json")
    if not p.exists():
        return None, None
    d = json.loads(p.read_text())
    sm = d.get("stream_metrics") or d.get("stream") or {}
    return sm, hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="comma-separated training run tags")
    ap.add_argument("--steps", default="50,100,150,200,250,300")
    ap.add_argument("--unseen-max", type=float, default=0.10)
    ap.add_argument("--ls-min", type=float, default=0.98)
    ap.add_argument("--output", default="manifests/revision_v1/primary_selection_v1.json")
    a = ap.parse_args()
    out = ROOT / a.output
    if out.exists():
        raise SystemExit(f"{out} exists; selections are versioned")
    cands = []
    for run in a.runs.split(","):
        for step in [x if x == "avg" else int(x) for x in a.steps.split(",")]:
            tag = f"{run}_step{step}_rare1_null0.5"
            row = {"run": run, "step": step, "tag": tag, "metrics": {}, "sources": {}}
            complete = True
            for ds in DATASETS:
                sm, h = load_eval(tag, ds)
                if sm is None:
                    complete = False
                    continue
                row["metrics"][ds] = {k: sm.get(k) for k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")}
                row["sources"][ds] = h
            up = ROOT / "results" / "R1" / "endpoints" / f"{run}_step{step}_rare1_n100_unseen_zsre" / "summary.json"
            if up.exists():
                u = json.loads(up.read_text())["summary"]
                row["metrics"]["unseen_zsre_100"] = u["false_fire_rate_full_inventory"]
                row["sources"]["unseen"] = hashlib.sha256(up.read_bytes()).hexdigest()
            else:
                complete = False
            row["complete"] = complete
            if complete:
                gs = [row["metrics"][ds]["ret_gs_end"] for ds in DATASETS]
                ls = [row["metrics"][ds]["ls_complete_answer_end"] for ds in DATASETS]
                row["mean_ret_gs"] = sum(gs) / 3
                row["admissible"] = row["metrics"]["unseen_zsre_100"] <= a.unseen_max and min(ls) >= a.ls_min
            cands.append(row)
    adm = [c for c in cands if c.get("admissible")]
    winner = max(adm, key=lambda c: (c["mean_ret_gs"], -c["metrics"]["unseen_zsre_100"])) if adm else None
    doc = {"name": "primary_selection_v1", "rule": "DEC-050: max mean RET-GS over zsRE/CounterFact/MQuAKE development streams (stream seed 21; MQuAKE dev v3b) subject to zsRE unseen false fires <= 10 % at 100 records (dev prompts) and LS >= 0.98 on every dataset; candidates = (run, checkpoint) pairs (DEC-049)",
           "populations": {"zsre": "manifests/dev/zsre_dev.json stream 21", "counterfact": "manifests/dev/counterfact_dev.json stream 21", "mquake": "manifests/dev/mquake_dev_v3b.json stream 21", "unseen": "zsRE dev remainder, 100 prompts after 100 edits"},
           "candidates": cands, "n_complete": sum(c["complete"] for c in cands), "n_admissible": len(adm), "winner": {k: winner[k] for k in ("run", "step", "tag", "mean_ret_gs", "metrics")} if winner else None,
           "status": "development selection; not frozen"}
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"complete": doc["n_complete"], "admissible": doc["n_admissible"], "winner": doc["winner"] and {"run": winner["run"], "step": winner["step"], "mean_ret_gs": round(winner["mean_ret_gs"], 4), "unseen": winner["metrics"]["unseen_zsre_100"]}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
