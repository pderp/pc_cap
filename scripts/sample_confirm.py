"""DATA-02: sealed confirmation realizations and orders (plan §6.6 DATA-02; PDF App. B "Randomization";
§4.5 rule 4). Not tuning code: this script is the only writer of the confirmation manifests.

From the sealed source pools (`assets/data/prepared/editing/<ds>_eligible.jsonl`, hashes in
`manifests/dev/pools.json`; dev items already excluded, subjects unique) draw three subject-disjoint
realizations per dataset (seeds 0, 1, 2; up to 3,000 zsRE / 1,000 CounterFact edits each) and five
orders per realization (seeds 100–104). Each realization manifest carries the items verbatim, the
orders (item-id permutations), and the named seeds for cap initialisation, router and replay
(`seed_cap_init = 1000·r + 10·o`, `seed_router = … + 1`, `seed_replay = … + 2`). Output:
`manifests/confirm/<ds>_r<k>.json`, `manifests/confirm/SHA256SUMS`, and `manifests/confirm/DATA-02.meta.json`
(counts, answer-length strata, subject counts; no prompts or answers — readable by tuning code).
The loader (`pccap.data.confirm`, DATA-02a) refuses to read these before `manifests/frozen.json` exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POOLS = ROOT / "manifests" / "dev" / "pools.json"
SIZES = {"zsre": 3000, "counterfact": 1000}
REALIZATION_SEEDS = (0, 1, 2)
ORDER_SEEDS = (100, 101, 102, 103, 104)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "manifests" / "confirm"))
    ap.add_argument("--datasets", nargs="*", default=["zsre", "counterfact"])
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    pools = json.loads(POOLS.read_text())
    meta = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "datasets": {}, "rule": "plan §4.5 rule 4: sealed until manifests/frozen.json",
            "realization_seeds": list(REALIZATION_SEEDS), "order_seeds": list(ORDER_SEEDS), "sizes_requested": SIZES}
    sums = []
    for ds in args.datasets:
        pool_path = Path(pools[ds]["confirm_pool_path"])
        got = sha256_file(pool_path)
        if got != pools[ds]["confirm_pool_sha256"]:
            raise RuntimeError(f"{ds} pool hash {got} != manifest {pools[ds]['confirm_pool_sha256']}")
        items = [json.loads(line) for line in pool_path.read_text().splitlines() if line.strip()]
        subjects = [it["subject"] for it in items]
        if len(set(subjects)) != len(subjects):
            raise RuntimeError("subjects are not unique in the pool")
        n_req = SIZES[ds]
        avail = len(items)
        per = min(n_req, avail // len(REALIZATION_SEEDS))
        # one global permutation (seed = dataset-level 0) partitions the pool into disjoint blocks; each
        # realization seed then draws its block order — disjointness is by construction
        rng0 = np.random.default_rng(int(hashlib.sha256(f"{ds}-partition".encode()).hexdigest()[:8], 16))
        perm = rng0.permutation(avail)
        ds_meta = {"pool_size": avail, "pool_sha256": got, "requested_per_realization": n_req, "per_realization": per,
                   "short": per < n_req, "realizations": {}}
        for k, rseed in enumerate(REALIZATION_SEEDS):
            block = perm[k * per:(k + 1) * per]
            rng = np.random.default_rng(rseed)
            chosen = [items[i] for i in rng.permutation(block)]
            ids = [it["item_id"] for it in chosen]
            orders = {}
            for oseed in ORDER_SEEDS:
                orng = np.random.default_rng(oseed)
                orders[str(oseed)] = [ids[i] for i in orng.permutation(len(ids))]
            named = {str(oseed): {"seed_cap_init": 1000 * rseed + 10 * (oseed - 100), "seed_router": 1000 * rseed + 10 * (oseed - 100) + 1,
                                  "seed_replay": 1000 * rseed + 10 * (oseed - 100) + 2} for oseed in ORDER_SEEDS}
            man = {"name": f"{ds}_r{rseed}", "mode": "confirm", "dataset": ds, "realization": rseed, "seed": rseed,
                   "order_seeds": list(ORDER_SEEDS), "orders": orders, "named_seeds": named, "n_items": len(chosen),
                   "source_pool_sha256": got, "items": chosen}
            p = out / f"{ds}_r{rseed}.json"
            p.write_text(json.dumps(man, indent=0, ensure_ascii=False) + "\n")
            h = sha256_file(p)
            sums.append(f"{h}  {p.name}")
            strata = Counter(int(it["answer_tokens"]) for it in chosen)
            ds_meta["realizations"][str(rseed)] = {"file": p.name, "sha256": h, "n_items": len(chosen), "subjects": len({it["subject"] for it in chosen}),
                                                   "answer_length_strata": {str(k2): v for k2, v in sorted(strata.items())},
                                                   "orders": {s2: hashlib.sha256(json.dumps(o).encode()).hexdigest()[:16] for s2, o in orders.items()}}
        sets = [set(items[i]["subject"] for i in perm[k * per:(k + 1) * per]) for k in range(len(REALIZATION_SEEDS))]
        ds_meta["subject_disjoint"] = all(not (a & b) for i, a in enumerate(sets) for b in sets[i + 1:])
        meta["datasets"][ds] = ds_meta
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    (out / "DATA-02.meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({ds: {k: v for k, v in m.items() if k != "realizations"} for ds, m in meta["datasets"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
