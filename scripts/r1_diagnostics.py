"""Revision v1, Stage 0 diagnostics D0/D1/D2 (coding-agent guide §0) on the v0 cap — revised per R1-X0 finding X0-14.

For each arm (C1, C2): a fresh 100-edit zsRE development stream under the frozen v2 budget/calibration, then on the endpoint
state (PC-8: the cap is never mutated; the state hash is asserted):
  D0 current read path — per site and per query (own prompt, each paraphrase, 200 unrelated prompts): which slot fires and
      whose it is (owner digest read from the CURRENT bank metadata); every per-query/per-site trace is persisted.
  D1 oracle selection — force the item's own slot per answer prefix, taken from the decision records and VERIFIED against the
      current bank (active, owner digest = the item's, last_target = the presented answer token); a missing or failed entry is
      counted unavailable (retrieval forced to none at that bank/position) — never replaced by another prefix's slot.
      Outcomes: teacher-forced NLL over the complete answer, first-token NLL (kept, qualified), exact answer (greedy ⇔ every
      teacher-forced argmax matches). An upper bound with unavailable deployment information, never an efficacy score.
  D2 stable observations — keys from a cap-off pass vs the sequential edited read on the same prefixes (key distance, retrieval
      differs), PLUS the controlled outcome assay: the complete answer read with retrieval decided from cap-off keys at every
      answer position (stable read), same outcome measures as D1. Every extra base pass is charged and reconciled.
Ledger: totals snapshotted before the stream, after the stream and after diagnostics; diagnostic call costs are also summed by
purpose (live, oracle, stable-read, cap-off key passes) and reconciled against the ledger delta.
    python scripts/r1_diagnostics.py [--arms C1,C2] [--n 100] → results/R1/diagnostics_<arm>.json, traces_<arm>.jsonl, diagnostics.md"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1"


def _nll(logits: np.ndarray, target: int) -> float:
    L = logits.astype(np.float64)
    m = L.max()
    return float(m + np.log(np.exp(L - m).sum()) - L[target])


def _cost(ep) -> float:
    c = getattr(ep, "cost", None)
    return float(getattr(c, "accel_seconds", 0.0) or 0.0)


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
    md = ["# Revision v1 — Stage 0 diagnostics D0 / D1 / D2 (v0 cap, zsRE development, 100 edits; X0-14 revision)", ""]
    with gpu_lease("R1:diagnostics", stage="R1", projected_seconds=3 * 3600.0):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        unrel_ids = [np.asarray(tok.encode(u), np.int32) for u in unrelated[: args.unrelated]]
        def run_arm(arm: str) -> None:
            nonlocal md
            t0 = time.time()
            cap = Cap(base, CapConfig(arm=arm, read=frozen["radii"]["read"], radii=radii, bank_scales=b_m, seed=0, d=base.d), ledger)
            rd = OUT / "streams" / arm
            ev = Evaluator(base, tok, unrelated[:50], None)
            ledger_before = ledger.totals()
            m = run_stream(cap, items, router_for(arm, cr_distribution=None), budget, ev, rd, ledger, checkpoints=(), seed=1, arm=arm)
            ledger_after_stream = ledger.totals()
            banks = cap.cfg.banks()
            # historical claims: digest -> bank -> prefix_index -> slot (last accepted write wins)
            claims: dict[str, dict[int, dict[int, int]]] = {}
            for line in (rd / "decisions.jsonl").read_text().splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                for mm, pb in (r.get("per_bank") or {}).items():
                    if pb.get("code") == "accepted" and pb.get("slot") is not None and int(pb["slot"]) >= 0:
                        claims.setdefault(r["item_digest"], {}).setdefault(int(mm), {})[int(r["prefix_index"])] = int(pb["slot"])
            state_hash = cap.state_hash()

            def owner_of(mm: int, s: int) -> str | None:
                """current owner digest (hex) of an active slot, from the bank metadata; None if inactive/none."""
                if s < 0:
                    return None
                meta = cap.banks[mm].bank.meta
                if int(meta["active"][s]) != 1:
                    return None
                return bytes(meta["owner_digest"][s]).ljust(16, b"\0").hex()

            def verified_oracle(it, dg: str) -> tuple[dict[int, dict[int, int]], dict[str, int]]:
                """bank -> prefix -> slot, only where the current bank confirms ownership, activity and presented token."""
                ok: dict[int, dict[int, int]] = {mm: {} for mm in banks}
                st = {"claimed": 0, "verified": 0, "reused_or_inactive": 0, "target_mismatch": 0, "missing_prefix": 0}
                ans = np.asarray(it.answer_ids, np.int32)
                for mm in banks:
                    meta = cap.banks[mm].bank.meta
                    cl = claims.get(dg, {}).get(mm, {})
                    for t in range(len(ans)):
                        s = cl.get(t)
                        if s is None:
                            st["missing_prefix"] += 1
                            continue
                        st["claimed"] += 1
                        if owner_of(mm, s) != dg:
                            st["reused_or_inactive"] += 1
                            continue
                        if int(meta["last_target"][s]) != int(ans[t]):
                            st["target_mismatch"] += 1
                            continue
                        ok[mm][t] = s
                        st["verified"] += 1
                return ok, st

            costs = {"live": 0.0, "oracle": 0.0, "stable_read": 0.0, "stable_rebuilt_read": 0.0, "stable_keys": 0.0, "rebuild_keys": 0.0, "d0_probe": 0.0, "unrelated": 0.0}
            from pccap.cap.bank import KEY_TOL

            # shadow keys: every active slot's key re-derived from a cap-off pass on its write prefix (prompt + answer[:t]),
            # so that the "stable keys and queries" condition compares like with like; the cap itself is never touched.
            by_digest = {(it.digest.hex() if isinstance(it.digest, (bytes, bytearray)) else str(it.digest)): it for it in items}
            shadow_keys = {mm: cap.banks[mm].bank.keys.copy() for mm in banks}
            rebuild = {mm: {"rebuilt": 0, "kept_stored": 0, "l2": []} for mm in banks}
            prefix_cache: dict[tuple[str, int], dict[int, np.ndarray]] = {}
            for mm in banks:
                bank = cap.banks[mm].bank
                for s_ in np.flatnonzero(bank.meta["active"] == 1):
                    s_ = int(s_)
                    own = owner_of(mm, s_)
                    hit = None
                    for t, sl in claims.get(own or "", {}).get(mm, {}).items():
                        if sl == s_:
                            hit = t
                    if own is None or own not in by_digest or hit is None:
                        rebuild[mm]["kept_stored"] += 1
                        continue
                    key_ = (own, hit)
                    if key_ not in prefix_cache:
                        it_ = by_digest[own]
                        ids_ = np.concatenate([np.asarray(it_.prompt_ids, np.int32), np.asarray(it_.answer_ids, np.int32)[:hit]])
                        fr_ = base.forward(ids_, (), retain_sites=True, phase="query", last_only=True)
                        costs["rebuild_keys"] += _cost(fr_)
                        p_ = len(ids_) - 1
                        prefix_cache[key_] = {b_: cap.key(np.asarray(fr_.sites[SiteId(b_, cap.blocks[b_], p_)], np.float32)) for b_ in banks}
                    shadow_keys[mm][s_] = prefix_cache[key_][mm]
                    rebuild[mm]["rebuilt"] += 1
                    rebuild[mm]["l2"].append(float(np.linalg.norm(shadow_keys[mm][s_] - bank.keys[s_])))

            def shadow_retrieve(mm: int, q: np.ndarray) -> int:
                bank = cap.banks[mm].bank
                diff = shadow_keys[mm] - np.asarray(q, np.float32)[None, :]
                dist = np.sqrt(np.sum(diff * diff, axis=1, dtype=np.float32)).astype(np.float32)
                eligible = bank.active & (dist <= bank.meta["radius"] + KEY_TOL)
                if int(eligible.sum()) == 0:
                    return -1
                idx = np.flatnonzero(eligible)
                order = np.lexsort((idx, dist[idx]))
                return int(idx[order[0]])

            def stable_slots(ids: np.ndarray) -> tuple[dict[int, int], dict[int, np.ndarray], dict[int, int]]:
                fr = base.forward(ids, (), retain_sites=True, phase="query", last_only=True)
                costs["stable_keys"] += _cost(fr)
                p = len(ids) - 1
                slots, keys, rslots = {}, {}, {}
                for mm in banks:
                    q = cap.key(np.asarray(fr.sites[SiteId(mm, cap.blocks[mm], p)], np.float32))
                    keys[mm] = q
                    slots[mm] = int(cap.banks[mm].bank.retrieve(q).slot)
                    rslots[mm] = shadow_retrieve(mm, q)
                return slots, keys, rslots

            def outcomes(ids: np.ndarray, it, policy: str, oracle: dict[int, dict[int, int]] | None = None) -> dict:
                """teacher-forced pass over the complete answer under a retrieval policy: live | oracle | stable | stable_rebuilt."""
                cur = np.asarray(ids, np.int32)
                ans = np.asarray(it.answer_ids, np.int32)
                nlls, matches, fired_seq, unavailable = [], [], [], 0
                for t, y in enumerate(ans):
                    if policy == "live":
                        fr_ret = None
                    elif policy == "oracle":
                        fr_ret = {}
                        for mm in banks:
                            s = oracle[mm].get(t)
                            if s is None:
                                unavailable += 1
                                s = -1
                            fr_ret[mm] = s
                    elif policy == "stable":
                        fr_ret, _, _ = stable_slots(cur)
                    else:  # stable_rebuilt: cap-off query against cap-off (rebuilt) keys
                        _, _, fr_ret = stable_slots(cur)
                    ep = cap.edited_forward(cur, phase="query", frozen_retrieval=fr_ret)
                    costs[{"live": "live", "oracle": "oracle", "stable": "stable_read", "stable_rebuilt": "stable_rebuilt_read"}[policy]] += _cost(ep)
                    lg = np.asarray(ep.logits)
                    nlls.append(_nll(lg, int(y)))
                    matches.append(int(np.argmax(lg)) == int(y))
                    fired_seq.append({str(mm): int(ep.fired[mm]) for mm in banks})
                    cur = np.concatenate([cur, np.int32([int(y)])])
                return {"tf_nll_sum": float(np.sum(nlls)), "tf_nll_mean": float(np.mean(nlls)), "first_nll": float(nlls[0]),
                        "exact": bool(all(matches)), "n_tokens": len(ans), "fired": fired_seq, "unavailable_positions": unavailable}

            d0 = {mm: {"prompt_own": 0, "prompt_none": 0, "prompt_other": 0, "para_own": 0, "para_none": 0, "para_other": 0, "para_n": 0, "unrel_fire": 0} for mm in banks}
            d1 = {k: {p: [] for p in ("live", "oracle", "stable", "stable_rebuilt")} for k in ("prompt", "paraphrase")}
            d2 = {mm: {"key_l2": [], "key_cos": [], "retrieval_differs": 0, "retrieval_differs_rebuilt": 0, "n": 0} for mm in banks}
            oracle_stats = {"claimed": 0, "verified": 0, "reused_or_inactive": 0, "target_mismatch": 0, "missing_prefix": 0}
            traces = (OUT / f"traces_{arm}.jsonl").open("w")
            for idx, it in enumerate(items):
                dg = it.digest.hex() if isinstance(it.digest, (bytes, bytearray)) else str(it.digest)
                oracle, st = verified_oracle(it, dg)
                for k in oracle_stats:
                    oracle_stats[k] += st[k]
                for kind, prefixes in (("prompt", [(None, np.asarray(it.prompt_ids, np.int32))]), ("paraphrase", [(p_, np.asarray(tok.encode(p_), np.int32)) for p_ in it.paraphrases])):
                    for text, ids in prefixes:
                        ep = cap.edited_forward(ids, phase="query")
                        costs["d0_probe"] += _cost(ep)
                        fired = {}
                        for mm in banks:
                            s = int(ep.fired[mm])
                            own = owner_of(mm, s)
                            cat = "none" if s < 0 else ("own" if own == dg else "other")
                            fired[str(mm)] = {"slot": s, "owner": own, "category": cat, "last_target": (int(cap.banks[mm].bank.meta["last_target"][s]) if s >= 0 else None)}
                            d0[mm][f"{'prompt' if kind == 'prompt' else 'para'}_{cat}"] += 1
                            if kind == "paraphrase":
                                d0[mm]["para_n"] += 1
                        sslots, skeys, rslots = stable_slots(ids)
                        for mm in banks:
                            q_stable, q_live = skeys[mm], ep.keys[mm]
                            d2[mm]["key_l2"].append(float(np.linalg.norm(q_stable - q_live)))
                            d2[mm]["key_cos"].append(float(np.dot(q_stable, q_live) / (np.linalg.norm(q_stable) * np.linalg.norm(q_live) + 1e-12)))
                            d2[mm]["retrieval_differs"] += int(sslots[mm] != ep.fired[mm])
                            d2[mm]["retrieval_differs_rebuilt"] += int(rslots[mm] != ep.fired[mm])
                            d2[mm]["n"] += 1
                        res = {p: outcomes(ids, it, p, oracle) for p in ("live", "oracle", "stable", "stable_rebuilt")}
                        for p in res:
                            d1[kind][p].append(res[p])
                        traces.write(json.dumps({"item_index": idx, "item_id": getattr(it, "item_id", None), "digest": dg, "kind": kind, "text": text,
                                                 "prefix_len": int(len(ids)), "answer_ids": [int(x) for x in np.asarray(it.answer_ids)],
                                                 "fired_first_position": fired, "stable_slots_first_position": {str(k): v for k, v in sslots.items()}, "stable_rebuilt_slots_first_position": {str(k): v for k, v in rslots.items()},
                                                 "oracle_slots": {str(mm): {str(t): s for t, s in v.items()} for mm, v in oracle.items()},
                                                 "oracle_verification": st, "outcomes": res}, default=float) + "\n")
            for ids in unrel_ids:
                ep = cap.edited_forward(ids, phase="query")
                costs["unrelated"] += _cost(ep)
                for mm in banks:
                    d0[mm]["unrel_fire"] += int(ep.fired[mm] >= 0)
            traces.close()
            assert cap.state_hash() == state_hash, "diagnostics mutated the cap (PC-8)"
            ledger_after_diag = ledger.totals()

            def delta(a, b):
                return {ph: {k: (b[ph][k] - a[ph][k]) for k in ("accel_seconds", "wall_seconds", "full_forwards", "partial_forwards", "tokens") if k in b[ph]} for ph in ("query", "learning", "total")}

            def agg(rows: list[dict]) -> dict:
                return {"n": len(rows), "exact_rate": float(np.mean([r["exact"] for r in rows])), "tf_nll_sum_mean": float(np.mean([r["tf_nll_sum"] for r in rows])),
                        "tf_nll_token_mean": float(np.mean([r["tf_nll_mean"] for r in rows])), "first_nll_mean": float(np.mean([r["first_nll"] for r in rows])),
                        "unavailable_positions_total": int(sum(r["unavailable_positions"] for r in rows))}

            summary = {"arm": arm, "n_items": len(items), "stream_metrics": {k: v["value"] for k, v in m["metrics"].items() if k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")},
                       "occupancy": {str(mm): cap.banks[mm].bank.occupancy() for mm in banks}, "state_hash": state_hash,
                       "D0": {str(mm): {**v, "para_recall": v["para_own"] / max(1, v["para_n"]), "prompt_recall": v["prompt_own"] / len(items), "unrelated_firing_rate": v["unrel_fire"] / len(unrel_ids)} for mm, v in d0.items()},
                       "D1": {k: {p: agg(v[p]) for p in v} for k, v in d1.items()},
                       "D1_oracle_verification": oracle_stats,
                       "D2": {str(mm): {"n": v["n"], "key_l2_mean": float(np.mean(v["key_l2"])), "key_l2_max": float(np.max(v["key_l2"])), "key_cos_min": float(np.min(v["key_cos"])),
                                        "retrieval_differs_rate": v["retrieval_differs"] / max(1, v["n"]), "retrieval_differs_rebuilt_rate": v["retrieval_differs_rebuilt"] / max(1, v["n"])} for mm, v in d2.items()},
                       "D2_key_rebuild": {str(mm): {"rebuilt": v["rebuilt"], "kept_stored": v["kept_stored"], "l2_mean": float(np.mean(v["l2"])) if v["l2"] else None, "l2_max": float(np.max(v["l2"])) if v["l2"] else None,
                                                    "radius": float(radii[mm])} for mm, v in rebuild.items()},
                       "ledger": {"before_stream": ledger_before, "after_stream": ledger_after_stream, "after_diagnostics": ledger_after_diag,
                                  "stream_delta": delta(ledger_before, ledger_after_stream), "diagnostics_delta": delta(ledger_after_stream, ledger_after_diag),
                                  "diagnostics_by_purpose_accel_seconds": costs, "diagnostics_by_purpose_sum": float(sum(costs.values()))},
                       "wall_seconds": time.time() - t0,
                       "labels": {"D1": "upper-bound diagnostic with unavailable deployment information (edit identity), never an efficacy score; oracle slots verified against the current bank; unavailable entries force none",
                                  "D1_first_nll": "first answer token only; tf_nll_* are teacher-forced over the complete answer",
                                  "D2": "stable = cap-off query keys against the STORED (edited-read) bank keys; stable_rebuilt = cap-off query keys against bank keys re-derived from cap-off passes on each slot's write prefix (shadow keys; cap untouched); values applied as usual; extra passes charged (stable_keys, rebuild_keys)",
                                  "prereview_pass": "results/R1/prereview/ holds the earlier pass (oracle prefix-0 fallback, historical ownership, first-token only)"}}
            (OUT / f"diagnostics_{arm}.json").write_text(json.dumps(summary, indent=1, default=float))
            md += [f"## {arm} (stream: ES {summary['stream_metrics']['es_immediate']:.3f}, RET-ES {summary['stream_metrics']['ret_es_end']:.3f}, RET-GS {summary['stream_metrics']['ret_gs_end']:.3f}, LS {summary['stream_metrics']['ls_complete_answer_end']:.3f}; occupancy {summary['occupancy']})", "",
                   "| site | prompt fires own / none / other | paraphrase recall (own) / none / other | unrelated firing rate | D2 query key L2 mean (max) | D2 retrieval differs (stored keys / rebuilt keys) | key rebuild L2 mean (max) vs radius |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
            for mm in banks:
                a, b, c = summary["D0"][str(mm)], summary["D2"][str(mm)], summary["D2_key_rebuild"][str(mm)]
                md.append(f"| {mm} | {a['prompt_own']} / {a['prompt_none']} / {a['prompt_other']} | {a['para_recall']:.2f} / {a['para_none'] / max(1, a['para_n']):.2f} / {a['para_other'] / max(1, a['para_n']):.2f} | {a['unrelated_firing_rate']:.3f} | {b['key_l2_mean']:.4f} ({b['key_l2_max']:.3f}) | {b['retrieval_differs_rate']:.3f} / {b['retrieval_differs_rebuilt_rate']:.3f} | {(c['l2_mean'] or 0):.4f} ({(c['l2_max'] or 0):.3f}) vs {c['radius']:.3f} |")
            md += ["", "| D1/D2 outcomes | n | policy | exact answer | TF NLL / answer | TF NLL / token | first-token NLL | unavailable oracle positions |", "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |"]
            for k, v in summary["D1"].items():
                for p, a in v.items():
                    md.append(f"| {k} | {a['n']} | {p} | {a['exact_rate']:.3f} | {a['tf_nll_sum_mean']:.3f} | {a['tf_nll_token_mean']:.3f} | {a['first_nll_mean']:.3f} | {a['unavailable_positions_total']} |")
            ov = oracle_stats
            md += ["", f"Oracle verification (bank × prefix entries): claimed {ov['claimed']}, verified {ov['verified']}, reused/inactive {ov['reused_or_inactive']}, target mismatch {ov['target_mismatch']}, missing prefix {ov['missing_prefix']}.",
                   f"Ledger: stream Δ accel {summary['ledger']['stream_delta']['total'].get('accel_seconds', 0):.1f} s; diagnostics Δ accel {summary['ledger']['diagnostics_delta']['total'].get('accel_seconds', 0):.1f} s vs by-purpose sum {summary['ledger']['diagnostics_by_purpose_sum']:.1f} s ({', '.join(f'{k} {v:.1f}' for k, v in costs.items())}).", ""]
            print(json.dumps({"arm": arm, "D0_para_recall": {mm: round(summary["D0"][str(mm)]["para_recall"], 3) for mm in banks},
                              "D1_exact": {k: {p: round(a["exact_rate"], 3) for p, a in v.items()} for k, v in summary["D1"].items()},
                              "oracle_verification": oracle_stats, "wall_s": round(summary["wall_seconds"])}), flush=True)

        for arm in args.arms.split(","):
            run_arm(arm)
    (OUT / "diagnostics.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
