"""R1-14 / DEC-035: the v0-stable control on the Stage 0 stream — same 100 zsRE development edits, v2 calibration and
budget, arms C1 and C2, with StableCap (keys from the write-free pass at write and read). Reports the stream metrics next
to the Stage 0 live numbers and the same per-site firing categories on paraphrases.
    python scripts/r1_14_v0_stable.py [--arms C1,C2] [--n 100] → results/R1/v0_stable_<arm>.json, results/R1/v0_stable.md"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="C1,C2")
    ap.add_argument("--n", type=int, default=100)
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import CapConfig
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.arms import router_for
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.v0_stable import StableCap

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    radii = {int(k): float(v) for k, v in frozen["radii"]["bank"]["zsre"].items()}
    b_m = {int(k): float(v) for k, v in frozen["b_m"].items()}
    budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
    items, unrelated = load_dev_items("zsre", args.n, seed=21)
    md = ["# R1-14 — v0-stable control (StableCap) on the Stage 0 stream (100 zsRE development edits, v2 calibration)", "",
          "| arm | variant | ES | RET-ES | RET-GS | LS | occupancy | paraphrase site-3 own / none / other | unrelated firing |", "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: |"]
    with gpu_lease("R1:v0_stable", stage="R1", projected_seconds=3600.0):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        unrel_ids = [np.asarray(tok.encode(u), np.int32) for u in unrelated[:200]]
        for arm in args.arms.split(","):
            t0 = time.time()
            cap = StableCap(base, CapConfig(arm=arm, read=frozen["radii"]["read"], radii=radii, bank_scales=b_m, seed=0, d=base.d), ledger)
            rd = OUT / "streams_stable" / arm
            ev = Evaluator(base, tok, unrelated[:50], None)
            m = run_stream(cap, items, router_for(arm, cr_distribution=None), budget, ev, rd, ledger, checkpoints=(), seed=1, arm=arm)
            banks = cap.cfg.banks()
            # paraphrase firing categories at the first answer position, by current owner digest
            cats = {mm: {"own": 0, "none": 0, "other": 0} for mm in banks}
            for it in items:
                dg = it.digest.hex() if isinstance(it.digest, (bytes, bytearray)) else str(it.digest)
                for p_ in it.paraphrases:
                    ep = cap.edited_forward(np.asarray(tok.encode(p_), np.int32), phase="query")
                    for mm in banks:
                        s = ep.fired[mm]
                        if s < 0:
                            cats[mm]["none"] += 1
                        else:
                            meta = cap.banks[mm].bank.meta
                            own = bytes(meta["owner_digest"][s]).ljust(16, b"\0").hex() if int(meta["active"][s]) == 1 else None
                            cats[mm]["own" if own == dg else "other"] += 1
            unrel = sum(int(any(cap.edited_forward(u, phase="query").fired[mm] >= 0 for mm in banks)) for u in unrel_ids)
            live = json.loads((OUT / f"diagnostics_{arm}.json").read_text())
            sm = {k: v["value"] for k, v in m["metrics"].items() if k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")}
            summary = {"arm": arm, "variant": "v0-stable", "stream_metrics": sm, "occupancy": {str(mm): cap.banks[mm].bank.occupancy() for mm in banks},
                       "paraphrase_first_position_categories": {str(k): v for k, v in cats.items()}, "unrelated_firing": unrel / len(unrel_ids),
                       "live_reference": {"stream_metrics": live["stream_metrics"], "D0": live["D0"]}, "wall_seconds": time.time() - t0, "state_hash": cap.state_hash()}
            (OUT / f"v0_stable_{arm}.json").write_text(json.dumps(summary, indent=1, default=float))
            l3 = live["D0"]["3"]
            md.append(f"| {arm} | live (Stage 0) | {live['stream_metrics']['es_immediate']:.3f} | {live['stream_metrics']['ret_es_end']:.3f} | {live['stream_metrics']['ret_gs_end']:.3f} | {live['stream_metrics']['ls_complete_answer_end']:.3f} | {live['occupancy']} | {l3['para_own']} / {l3['para_none']} / {l3['para_other']} | {l3['unrelated_firing_rate']:.3f} |")
            c3 = cats[3]
            md.append(f"| {arm} | v0-stable | {sm['es_immediate']:.3f} | {sm['ret_es_end']:.3f} | {sm['ret_gs_end']:.3f} | {sm['ls_complete_answer_end']:.3f} | {summary['occupancy']} | {c3['own']} / {c3['none']} / {c3['other']} | {summary['unrelated_firing']:.3f} |")
            print(json.dumps({"arm": arm, "stable": sm, "live": live["stream_metrics"], "wall_s": round(time.time() - t0)}), flush=True)
    (OUT / "v0_stable.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
