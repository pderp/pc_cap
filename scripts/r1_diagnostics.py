"""Revision v1, Stage 0 diagnostics D0/D1/D2 (coding-agent guide §0) on the v0 cap.

For each arm (C1, C2): a fresh 100-edit zsRE development stream under the frozen v2 budget/calibration, then on the endpoint
state:
  D0 current read path — per site: which slot fires for the item's own prompt, its paraphrases and 200 unrelated prompts
      (recall = the item's own slot fires; irrelevant firing = anything fires on an unrelated prompt), answer outcomes with
      live retrieval (teacher-forced first-token loss; exact full answer by greedy decoding);
  D1 oracle selection — force the item's own slots (per answer-prefix index when the item wrote one) inside a diagnostic
      evaluator; report the same outcomes; an upper bound with unavailable deployment information, never an efficacy score;
  D2 stable observations — keys from a cap-off pass vs the sequential edited-key read on the same prefixes: key distance per
      site and how often the retrieval outcome differs; the extra pass is charged.
    python scripts/r1_diagnostics.py [--arms C1,C2] [--n 100] → results/R1/diagnostics_<arm>.json, results/R1/diagnostics.md"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1"


def _nll_first(logits: np.ndarray, target: int) -> float:
    L = logits.astype(np.float64)
    m = L.max()
    return float(m + np.log(np.exp(L - m).sum()) - L[target])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="C1,C2")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--unrelated", type=int, default=200)
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.contracts import Budget, SiteId
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.arms import router_for
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream
    from pccap.harness.stage_s2 import load_dev_items

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    radii = {int(k): float(v) for k, v in frozen["radii"]["bank"]["zsre"].items()}
    b_m = {int(k): float(v) for k, v in frozen["b_m"].items()}
    budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
    items, unrelated = load_dev_items("zsre", args.n, seed=21)
    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# Revision v1 — Stage 0 diagnostics D0 / D1 / D2 (v0 cap, zsRE development, 100 edits)", ""]
    with gpu_lease("R1:diagnostics", stage="R1", projected_seconds=2 * 3600.0):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        unrel_ids = [np.asarray(tok.encode(u), np.int32) for u in unrelated[: args.unrelated]]
        for arm in args.arms.split(","):
            t0 = time.time()
            cap = Cap(base, CapConfig(arm=arm, read=frozen["radii"]["read"], radii=radii, bank_scales=b_m, seed=0, d=base.d), ledger)
            rd = OUT / "streams" / arm
            ev = Evaluator(base, tok, unrelated[:50], None)
            m = run_stream(cap, items, router_for(arm, cr_distribution=None), budget, ev, rd, ledger, checkpoints=(), seed=1, arm=arm)
            # ownership: slot -> (item digest, prefix index) per bank, from the decision records (accepted writes)
            owners: dict[int, dict[int, tuple[str, int]]] = {mm: {} for mm in cap.cfg.banks()}
            own_slots: dict[str, dict[int, dict[int, int]]] = {}  # digest -> bank -> prefix_index -> slot
            for line in (rd / "decisions.jsonl").read_text().splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                for mm, pb in (r.get("per_bank") or {}).items():
                    if pb.get("code") == "accepted" and pb.get("slot", -1) is not None and int(pb.get("slot", -1)) >= 0:
                        mm = int(mm)
                        owners[mm][int(pb["slot"])] = (r["item_digest"], int(r["prefix_index"]))
                        own_slots.setdefault(r["item_digest"], {}).setdefault(mm, {})[int(r["prefix_index"])] = int(pb["slot"])
            state_hash = cap.state_hash()
            banks = cap.cfg.banks()
            d0 = {mm: {"prompt_own": 0, "prompt_none": 0, "prompt_other": 0, "para_own": 0, "para_none": 0, "para_other": 0, "para_n": 0, "unrel_fire": 0} for mm in banks}
            d1 = {"prompt": {"live_first_nll": [], "oracle_first_nll": [], "live_exact": 0, "oracle_exact": 0, "n": 0},
                  "paraphrase": {"live_first_nll": [], "oracle_first_nll": [], "live_exact": 0, "oracle_exact": 0, "n": 0}}
            d2 = {mm: {"key_l2": [], "key_cos": [], "retrieval_differs": 0, "n": 0} for mm in banks}
            extra_pass_cost = 0.0

            def outcomes(ids: np.ndarray, it, frozen_ret_fn, cap=cap):
                """first-token NLL and exact-answer flag under a retrieval policy (live: None; oracle: slots per prefix)."""
                cur = np.asarray(ids, np.int32)
                exact = True
                first = None
                for t, y in enumerate(np.asarray(it.answer_ids, np.int32)):
                    ep = cap.edited_forward(cur, phase="query", frozen_retrieval=frozen_ret_fn(t))
                    lg = np.asarray(ep.logits)
                    if t == 0:
                        first = _nll_first(lg, int(y))
                    nxt = int(np.argmax(lg))
                    if nxt != int(y):
                        exact = False
                        break
                    cur = np.concatenate([cur, np.int32([nxt])])
                return first, exact

            for it in items:
                dg = it.digest.hex() if isinstance(it.digest, (bytes, bytearray)) else str(it.digest)
                mine = own_slots.get(dg, {})

                def oracle(t, mine=mine, banks=banks):
                    fr = {}
                    for mm in banks:
                        slots = mine.get(mm, {})
                        fr[mm] = slots.get(t, slots.get(0, -1)) if slots else -1
                    return fr

                for kind, prefixes in (("prompt", [np.asarray(it.prompt_ids, np.int32)]), ("paraphrase", [np.asarray(tok.encode(p_), np.int32) for p_ in it.paraphrases])):
                    for ids in prefixes:
                        ep = cap.edited_forward(ids, phase="query")
                        for mm in banks:
                            s = ep.fired[mm]
                            cat = "none" if s < 0 else ("own" if owners[mm].get(s, ("", -1))[0] == dg else "other")
                            d0[mm][f"{'prompt' if kind == 'prompt' else 'para'}_{cat}"] += 1
                            if kind == "paraphrase":
                                d0[mm]["para_n"] += 1
                        # D2: stable keys from a cap-off pass on the same prefix
                        fr = base.forward(ids, (), retain_sites=True, phase="query", last_only=True)
                        extra_pass_cost += fr.cost.accel_seconds if hasattr(fr.cost, "accel_seconds") else 0.0
                        p = len(ids) - 1
                        for mm in banks:
                            q_stable = cap.key(np.asarray(fr.sites[SiteId(mm, cap.blocks[mm], p)], np.float32))
                            q_live = ep.keys[mm]
                            d2[mm]["key_l2"].append(float(np.linalg.norm(q_stable - q_live)))
                            d2[mm]["key_cos"].append(float(np.dot(q_stable, q_live) / (np.linalg.norm(q_stable) * np.linalg.norm(q_live) + 1e-12)))
                            d2[mm]["retrieval_differs"] += int(cap.banks[mm].bank.retrieve(q_stable).slot != ep.fired[mm])
                            d2[mm]["n"] += 1
                        live_first, live_exact = outcomes(ids, it, lambda t: None)
                        orc_first, orc_exact = outcomes(ids, it, oracle)
                        d1[kind]["live_first_nll"].append(live_first)
                        d1[kind]["oracle_first_nll"].append(orc_first)
                        d1[kind]["live_exact"] += int(live_exact)
                        d1[kind]["oracle_exact"] += int(orc_exact)
                        d1[kind]["n"] += 1
            for ids in unrel_ids:
                ep = cap.edited_forward(ids, phase="query")
                for mm in banks:
                    d0[mm]["unrel_fire"] += int(ep.fired[mm] >= 0)
            assert cap.state_hash() == state_hash, "diagnostics mutated the cap (PC-8)"
            summary = {"arm": arm, "n_items": len(items), "stream_metrics": {k: v["value"] for k, v in m["metrics"].items() if k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")},
                       "occupancy": {str(mm): cap.banks[mm].bank.occupancy() for mm in banks}, "state_hash": state_hash,
                       "D0": {str(mm): {**v, "para_recall": v["para_own"] / max(1, v["para_n"]), "prompt_recall": v["prompt_own"] / len(items), "unrelated_firing_rate": v["unrel_fire"] / len(unrel_ids)} for mm, v in d0.items()},
                       "D1": {k: {"n": v["n"], "live_exact_rate": v["live_exact"] / max(1, v["n"]), "oracle_exact_rate": v["oracle_exact"] / max(1, v["n"]),
                                  "live_first_nll_mean": float(np.mean(v["live_first_nll"])), "oracle_first_nll_mean": float(np.mean(v["oracle_first_nll"]))} for k, v in d1.items()},
                       "D2": {str(mm): {"n": v["n"], "key_l2_mean": float(np.mean(v["key_l2"])), "key_l2_max": float(np.max(v["key_l2"])), "key_cos_min": float(np.min(v["key_cos"])),
                                        "retrieval_differs_rate": v["retrieval_differs"] / max(1, v["n"])} for mm, v in d2.items()},
                       "extra_capoff_pass_accel_seconds": extra_pass_cost, "wall_seconds": time.time() - t0,
                       "labels": {"D1": "upper-bound diagnostic with unavailable deployment information (edit identity), never an efficacy score",
                                  "D2": "stable keys = cap-off pass; live keys = the sequential edited read the arm actually uses"}}
            (OUT / f"diagnostics_{arm}.json").write_text(json.dumps(summary, indent=1, default=float))
            md += [f"## {arm} (stream: ES {summary['stream_metrics']['es_immediate']:.3f}, RET-ES {summary['stream_metrics']['ret_es_end']:.3f}, RET-GS {summary['stream_metrics']['ret_gs_end']:.3f}, LS {summary['stream_metrics']['ls_complete_answer_end']:.3f}; occupancy {summary['occupancy']})", "",
                   "| site | prompt fires own / none / other | paraphrase recall (own) / none / other | unrelated firing rate | D2 key L2 mean (max) | D2 retrieval differs |", "| --- | --- | --- | ---: | ---: | ---: |"]
            for mm in banks:
                a, b = summary["D0"][str(mm)], summary["D2"][str(mm)]
                md.append(f"| {mm} | {a['prompt_own']} / {a['prompt_none']} / {a['prompt_other']} | {a['para_recall']:.2f} / {a['para_none'] / max(1, a['para_n']):.2f} / {a['para_other'] / max(1, a['para_n']):.2f} | {a['unrelated_firing_rate']:.3f} | {b['key_l2_mean']:.4f} ({b['key_l2_max']:.3f}) | {b['retrieval_differs_rate']:.3f} |")
            md += ["", "| D1 | n | exact answer, live retrieval | exact answer, oracle slots | first-token NLL live → oracle |", "| --- | ---: | ---: | ---: | --- |"]
            for k, v in summary["D1"].items():
                md.append(f"| {k} | {v['n']} | {v['live_exact_rate']:.3f} | {v['oracle_exact_rate']:.3f} | {v['live_first_nll_mean']:.3f} → {v['oracle_first_nll_mean']:.3f} |")
            md.append("")
            print(json.dumps({"arm": arm, "D0_para_recall": {mm: round(summary["D0"][str(mm)]["para_recall"], 3) for mm in banks}, "D1": {k: (round(v["live_exact_rate"], 3), round(v["oracle_exact_rate"], 3)) for k, v in summary["D1"].items()}, "D2_differs": {mm: round(summary["D2"][str(mm)]["retrieval_differs_rate"], 3) for mm in banks}}), flush=True)
    (OUT / "diagnostics.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
