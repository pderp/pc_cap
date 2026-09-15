"""DEC-046 (proposed default): MQuAKE development slice and training pool from the teacher-eligible pool (R1-D5), leaving the
rest untouched for the confirmatory draw (R1-58). Fixed seed; subjects disjoint between the two slices; the 159 subjects
shared with the zsRE fresh candidates are left out of both (they stay on the zsRE side, R1-D1g default).
    python scripts/r1_d6_mquake_split.py [--dev 200] [--train 500] [--seed 46]
    → manifests/dev/mquake_dev.json, manifests/revision_v1/train_pool_mquake_v1.json"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "manifests" / "revision_v1" / "mquake_pool_v1.json"
OVERLAP = Path("/home/derp/cap/assets/data/prepared/revision_v1/r1_d4_v1/zsre_overlap_subjects.jsonl")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", type=int, default=200)
    ap.add_argument("--train", type=int, default=500)
    ap.add_argument("--seed", type=int, default=46)
    ap.add_argument("--suffix", default="v1", help="output version suffix (v1 = DEC-046 sizes)")
    args = ap.parse_args()
    DEV_OUT = ROOT / "manifests" / "dev" / ("mquake_dev.json" if args.suffix == "v1" else f"mquake_dev_{args.suffix}.json")
    TRAIN_OUT = ROOT / "manifests" / "revision_v1" / f"train_pool_mquake_{args.suffix}.json"
    for p in (DEV_OUT, TRAIN_OUT):
        if p.exists():
            raise SystemExit(f"{p} exists; pools are versioned")
    from pccap.data.streams import normalize_answer

    pool = json.loads(POOL.read_text())
    overlap = set()
    for line in OVERLAP.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            overlap.add(normalize_answer(r if isinstance(r, str) else (r.get("subject_key") or r.get("subject") or r.get("normalized_subject") or "")))
    items = [it for it in pool["items"] if normalize_answer(it["subject"]) not in overlap]
    n_overlap_removed = len(pool["items"]) - len(items)
    rng = np.random.default_rng(args.seed)
    order = rng.permutation(len(items))
    used_subjects, dev, train = set(), [], []
    for i in order:
        it = items[int(i)]
        key = normalize_answer(it["subject"])
        if key in used_subjects:
            continue
        if len(dev) < args.dev:
            dev.append(it)
            used_subjects.add(key)
        elif len(train) < args.train:
            train.append(it)
            used_subjects.add(key)
        else:
            break
    chosen = {it["item_id"] for it in dev} | {it["item_id"] for it in train}
    rest = [it for it in items if it["item_id"] not in chosen and normalize_answer(it["subject"]) not in used_subjects]
    unrelated = [lp for it in rest for lp in it["locality_prompts"][:1]]
    rng2 = np.random.default_rng(args.seed + 1)
    unrelated = [unrelated[int(i)] for i in rng2.permutation(len(unrelated))[:1000]]
    dev_doc = {"name": "mquake_dev", "mode": "dev", "stage": "R1", "seed": str(args.seed), "dataset": "mquake", "decision": "DEC-046 (proposed default)",
               "source": {"path": str(POOL), "sha256": hashlib.sha256(POOL.read_bytes()).hexdigest()},
               "counts": {"pool": len(pool["items"]), "zsre_overlap_removed": n_overlap_removed, "dev": len(dev), "train": len(train), "remaining_for_confirmatory": len(rest)},
               "selection": "fixed-seed permutation; one item per subject; dev and training subjects disjoint; the zsRE-overlap subjects excluded from both",
               "unrelated_prompts": unrelated, "unrelated_source": "first locality prompt of remaining (unselected) pool items; same-relation prompts, harder than zsRE's NQ questions",
               "items": dev}
    train_doc = {"name": f"train_pool_mquake_{args.suffix}", "dataset": "mquake", "date": "2026-09-14", "decision": "DEC-046 (proposed default)", "seed": args.seed,
                 "sources_sha256": dev_doc["source"], "counts": dev_doc["counts"], "exposure": "training pool: its subjects go into register v4 as exposed; never confirmatory",
                 "items": train, "drawn_subjects_normalized": sorted({normalize_answer(it["subject"]) for it in train})}
    DEV_OUT.write_text(json.dumps(dev_doc, ensure_ascii=False) + "\n")
    TRAIN_OUT.write_text(json.dumps(train_doc, ensure_ascii=False) + "\n")
    print(json.dumps(dev_doc["counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
