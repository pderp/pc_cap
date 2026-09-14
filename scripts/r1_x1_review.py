"""Read-only R1-X1 recount of saved diagnostics and endpoint metadata, without a model."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pccap.harness.snapshot import load as load_snapshot


def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def run():
    result = {"task": "R1-X1", "gpu_seconds": 0, "model_forward_calls": 0, "sources_sha256": {}, "arms": {}}
    sources = result["sources_sha256"]
    for arm in ("C1", "C2"):
        p = ROOT / f"results/R1/diagnostics_{arm}.json"
        sources[str(p)] = sha(p)
        summary = json.loads(p.read_text())
        p = ROOT / f"results/R1/traces_{arm}.jsonl"
        sources[str(p)] = sha(p)
        traces = [json.loads(s) for s in p.read_text().splitlines() if s]
        p = ROOT / f"results/R1/streams/{arm}/decisions.jsonl"
        sources[str(p)] = sha(p)
        decisions = [json.loads(s) for s in p.read_text().splitlines() if s]
        p = ROOT.parent / f"assets/runs/R1/streams/{arm}/learner_end.ckpt"
        sources[str(p)] = sha(p)
        state = load_snapshot(p)
        assert state.content_hash() == summary["state_hash"]
        meta = {str(b): state.arrays[f"bank{b}/meta"] for b in (1, 2, 3)}
        banks = list(meta)

        def owner(b, slot):
            if slot < 0 or not meta[b]["active"][slot]:
                return None
            return bytes(meta[b]["owner_digest"][slot]).ljust(16, b"\0").hex()

        claims, chronological_last = {}, {}
        for i, d in enumerate(decisions):
            for b, entry in (d.get("per_bank") or {}).items():
                slot = entry.get("slot")
                if entry.get("code") == "accepted" and slot is not None and int(slot) >= 0:
                    dg, t, s = d["item_digest"], int(d["prefix_index"]), int(slot)
                    claims.setdefault(dg, {}).setdefault(b, {})[t] = s
                    chronological_last[b, s] = (dg, t, i)
        verification = Counter()
        prefix_mismatches, oracle_map_mismatches, d0_mismatches = [], [], []
        for row in traces:
            dg = row["digest"]
            expected = {b: {} for b in banks}
            st = Counter({k: 0 for k in ("claimed", "verified", "reused_or_inactive", "target_mismatch", "missing_prefix")})
            for b in banks:
                for t, y in enumerate(row["answer_ids"]):
                    s = claims.get(dg, {}).get(b, {}).get(t)
                    if s is None:
                        st["missing_prefix"] += 1
                        continue
                    st["claimed"] += 1
                    if owner(b, s) != dg:
                        st["reused_or_inactive"] += 1
                        continue
                    if int(meta[b]["last_target"][s]) != int(y):
                        st["target_mismatch"] += 1
                        continue
                    expected[b][str(t)] = s
                    st["verified"] += 1
                    if chronological_last[b, s][:2] != (dg, t) and row["kind"] == "prompt":
                        prefix_mismatches.append({"item_id": row["item_id"], "bank": b, "prefix": t, "slot": s,
                            "last_accepted": chronological_last[b, s]})
            if expected != row["oracle_slots"] or dict(st) != row["oracle_verification"]:
                oracle_map_mismatches.append(row["item_id"] + ":" + row["kind"])
            if row["kind"] == "prompt":
                verification.update(st)
            for b, entry in row["fired_first_position"].items():
                o = owner(b, entry["slot"])
                category = "none" if o is None else "own" if o == dg else "other"
                if category != entry["category"] or o != entry["owner"]:
                    d0_mismatches.append({"item": row["item_id"], "bank": b, "kind": row["kind"]})
        assert not oracle_map_mismatches and not d0_mismatches
        assert dict(verification) == summary["D1_oracle_verification"]
        rebuild, rebuild_issues = {}, []
        unique_prefixes = set()
        for b in banks:
            rebuilt = kept = ambiguous = 0
            for s in np.flatnonzero(meta[b]["active"]):
                s = int(s)
                dg = owner(b, s)
                hits = [t for t, sl in claims.get(dg, {}).get(b, {}).items() if sl == s]
                if not hits:
                    kept += 1
                    continue
                rebuilt += 1
                ambiguous += len(hits) > 1
                t = hits[-1]
                unique_prefixes.add((dg, t))
                if chronological_last[b, s][:2] != (dg, t):
                    rebuild_issues.append({"bank": b, "slot": s, "chosen_prefix": t, "last_accepted": chronological_last[b, s]})
            rebuild[b] = {"rebuilt": rebuilt, "kept_stored": kept, "multiple_candidate_prefixes": ambiguous,
                          "capacity": len(meta[b]), "active": int(np.sum(meta[b]["active"]))}
            assert rebuilt == summary["D2_key_rebuild"][b]["rebuilt"]
            assert kept == summary["D2_key_rebuild"][b]["kept_stored"]
        aggregate, d0_counts, associations = {}, {}, {}
        for kind in ("prompt", "paraphrase"):
            rows = [r for r in traces if r["kind"] == kind]
            aggregate[kind] = {}
            for policy in ("live", "oracle", "stable", "stable_rebuilt"):
                vals = [r["outcomes"][policy] for r in rows]
                stat = {"n": len(vals), "exact_rate": float(np.mean([v["exact"] for v in vals])),
                    "tf_nll_sum_mean": float(np.mean([v["tf_nll_sum"] for v in vals])),
                    "tf_nll_token_mean": float(np.mean([v["tf_nll_mean"] for v in vals])),
                    "first_nll_mean": float(np.mean([v["first_nll"] for v in vals])),
                    "unavailable_positions_total": sum(v["unavailable_positions"] for v in vals)}
                for k, v in stat.items():
                    assert np.isclose(v, summary["D1"][kind][policy][k], rtol=0, atol=1e-12), (arm, kind, policy, k)
                stat["exact_count"] = sum(v["exact"] for v in vals)
                stat["total_target_tokens"] = sum(v["n_tokens"] for v in vals)
                stat["pooled_token_nll"] = sum(v["tf_nll_sum"] for v in vals) / stat["total_target_tokens"]
                aggregate[kind][policy] = stat
            d0_counts[kind] = {}
            for b in banks:
                co = Counter(r["fired_first_position"][b]["category"] for r in rows)
                d0_counts[kind][b] = dict(co)
                pre = "prompt" if kind == "prompt" else "para"
                for cat in ("own", "none", "other"):
                    assert co[cat] == summary["D0"][b][pre + "_" + cat]
            if kind == "paraphrase":
                for row in rows:
                    s = row["stable_rebuilt_slots_first_position"]["3"]
                    o = owner("3", s)
                    cat = "none" if o is None else "own" if o == row["digest"] else "other"
                    item = associations.setdefault(cat, {"n": 0, "exact": 0})
                    item["n"] += 1
                    item["exact"] += int(row["outcomes"]["stable_rebuilt"]["exact"])
        ledger = summary["ledger"]
        purpose_sum = sum(ledger["diagnostics_by_purpose_accel_seconds"].values())
        delta = ledger["after_diagnostics"]["total"]["accel_seconds"] - ledger["after_stream"]["total"]["accel_seconds"]
        assert abs(purpose_sum - delta) < 1e-8
        result["arms"][arm] = {"rows": len(traces), "state_hash_verified": state.content_hash(),
            "all_saved_D1_and_D0_edited_query_aggregates_match": True, "D1_recount": aggregate, "D0_recount": d0_counts,
            "oracle_verification": dict(verification), "verified_oracle_last_accepted_prefix_mismatches": prefix_mismatches,
            "shadow_rebuild": rebuild, "shadow_rebuild_last_accepted_prefix_mismatches": rebuild_issues,
            "unique_rebuilt_prefix_passes": len(unique_prefixes), "stable_rebuilt_site3_paraphrase_association": associations,
            "purpose_sum_seconds": purpose_sum, "ledger_delta_seconds": delta, "cost_residual_seconds": purpose_sum-delta,
            "unrelated_rows_saved": sum(r["kind"] == "unrelated" for r in traces),
            "limitations": ["Recounts validate saved outcomes, not logits: no model recomputation here.",
                "No per-query unrelated traces or stable/shadow unrelated locality measurements were persisted.",
                "Oracle prefix identity additionally checked against chronological last accepted writes, beyond installed owner/token checks.",
                "No current prefix-identity failures does not make owner+token alone a general prefix-identity guarantee."]}
    for name in ("scripts/r1_diagnostics.py", "docs/R1_diagnosis.md", "results/R1/diagnostics.md", "results/R1/v0_stable.md", "results/R1/matched_update.md", "docs/decisions.md"):
        p = ROOT / name
        if p.exists():
            sources[str(p)] = sha(p)
    assert all(sha(Path(p)) == h for p, h in sources.items())
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    p = a.output.resolve()
    if p.exists() or not p.is_relative_to(ROOT):
        raise ValueError("output must be a new file inside pc_cap")
    result = run()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps({arm: {k: v for k, v in row.items() if k not in ("D1_recount", "D0_recount", "limitations")}
                      for arm, row in result["arms"].items()}, indent=2))


if __name__ == "__main__":
    main()
