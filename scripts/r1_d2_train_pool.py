"""DEC-037: a CounterFact TRAINING pool for revision v1 Stage 2 from the unopened remainder of the old eligible pool.

Source: the E.2-filtered eligible file (`assets/data/prepared/editing/counterfact_eligible.jsonl`, 20,091 items: teacher-
incorrect, aliases per SD-9, subjects deduplicated, token ids attached). Removed: every item in the three sealed
realizations (r0–r2 orders), every item whose normalized subject appears in the R1-D1 exclusion register for a reason
other than membership of the old eligible pool itself (i.e. anything exposed by development, S7, challenges or emitted
episodes), and items with fewer than two paraphrases. A fixed-seed sample of N items is written with full provenance;
the drawn subjects are an exposure to be added to the register's next version.
    python scripts/r1_d2_train_pool.py [--n 3000] [--seed 137] → manifests/revision_v1/train_pool_counterfact_v1.json"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ELIGIBLE = Path("/home/derp/cap/assets/data/prepared/editing/counterfact_eligible.jsonl")
REGISTER = ROOT / "manifests" / "revision_v1" / "exclusions.json"
OUT = ROOT / "manifests" / "revision_v1" / "train_pool_counterfact_v1.json"


def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", s).casefold().split())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=137)
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; the pool is versioned — write a new version instead")
    items = [json.loads(l) for l in ELIGIBLE.open()]
    sealed = set()
    seal_files = {}
    for r in range(3):
        p = ROOT / "manifests" / "confirm" / f"counterfact_r{r}.json"
        d = json.loads(p.read_text())
        for order in d["orders"].values():
            sealed.update(order)
        seal_files[str(p)] = sha(p)
    reg = json.loads(REGISTER.read_text())
    exposed = {e["normalized_subject"] for e in reg["exclusions"] if any(not r.startswith("old_eligible:") for r in e["reasons"])}
    counts = {"eligible": len(items), "sealed_realization_items": 0, "exposed_subject": 0, "fewer_than_two_paraphrases": 0}
    keep = []
    for it in items:
        if it["item_id"] in sealed:
            counts["sealed_realization_items"] += 1
            continue
        if norm(it["subject"]) in exposed:
            counts["exposed_subject"] += 1
            continue
        if len(it.get("paraphrases", [])) < 2:
            counts["fewer_than_two_paraphrases"] += 1
            continue
        keep.append(it)
    counts["remainder_after_filters"] = len(keep)
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(keep))[: args.n]
    drawn = [keep[i] for i in sorted(idx)]
    counts["drawn"] = len(drawn)
    doc = {"name": "train_pool_counterfact_v1", "mode": "train_pool", "dataset": "counterfact", "decision": "DEC-037", "seed": args.seed,
           "purpose": "revision v1 Stage 2 training episodes (never confirmatory); drawn subjects are an exposure for the exclusion register v2",
           "sources_sha256": {str(ELIGIBLE): sha(ELIGIBLE), str(REGISTER): sha(REGISTER), **seal_files}, "counts": counts,
           "filters": ["not in sealed realizations r0-r2 (all five orders)", "normalized subject not excluded for any reason other than old_eligible:*", ">= 2 paraphrases"],
           "items": drawn, "drawn_subjects_normalized": sorted({norm(it["subject"]) for it in drawn})}
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"counts": counts, "out": str(OUT), "sha256": sha(OUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
