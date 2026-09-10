"""Challenge sets (DATA-08; PDF E.2 challenge paragraph; plan §6.6).

Built from the sealed confirmation source pools (never from development items), disjoint from
development by subject, and written to ``manifests/dev/challenges.json`` (the sets are evaluated
separately from the primary benchmark; they are fixed here and consumed read-only later):

1. **Near-neighbour pairs** (≥ 100): CounterFact items paired with a neighbourhood prompt whose
   true answer (the item's ``target_true``) differs from the edited target, plus zsRE items that
   share a subject with a different relation (different ``src`` template) and a different answer.
2. **Compositions** (≥ 100 where the reference supports unambiguous evaluation): zsRE pairs
   ``(s, r1) → o1`` and ``(o1, r2) → o2`` where ``o1`` is the subject of another item in the pool;
   if fewer than 100 exist the remainder is reported as ``unsupported``.
3. **Temporal corrections** (≥ 100): CounterFact items presented twice as versions 1 and 2 of
   the same fact id — ``target_true`` first, then ``target_new`` — with a ``RevisionEvent``
   payload for the correction track (SD-4).

    python -m pccap.data.challenges --build --audit
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from pccap import ASSETS_ROOT
from pccap.metrics.editing import normalize_answer

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "manifests" / "dev"
POOLS = Path(ASSETS_ROOT) / "data" / "prepared" / "editing"
OUT = DEV / "challenges.json"
MIN = 100


def _pool(ds: str) -> list[dict]:
    with open(POOLS / f"{ds}_eligible.jsonl") as f:
        return [json.loads(line) for line in f]


def _dev_subjects() -> set[str]:
    subs = set()
    for ds in ("zsre", "counterfact"):
        subs |= {normalize_answer(it["subject"]) for it in json.loads((DEV / f"{ds}_dev.json").read_text())["items"]}
    subs |= {normalize_answer(s) for s in json.loads((DEV / "reserved_subjects.json").read_text())["subjects"]}
    return subs


def near_neighbours(cf: list[dict], zs: list[dict], rng: np.random.Generator) -> list[dict]:
    out = []
    for it in cf:
        if normalize_answer(it.get("target_true", "")) == normalize_answer(it["answer"]):
            continue
        nbrs = it.get("locality_prompts", [])
        if not nbrs:
            continue
        out.append({"dataset": "counterfact", "edit_item_id": it["item_id"], "edit_prompt": it["prompt"], "edit_answer": it["answer"],
                    "neighbour_prompt": nbrs[int(rng.integers(0, len(nbrs)))], "neighbour_answer": it["target_true"],
                    "type": "same_relation_other_subject"})
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for it in zs:
        by_subject[normalize_answer(it["subject"])].append(it)
    for _subj, items in by_subject.items():
        for a in items:
            for b in items:
                if a is b:
                    continue
                if normalize_answer(a["answer"]) != normalize_answer(b["answer"]) and a["prompt"] != b["prompt"]:
                    out.append({"dataset": "zsre", "edit_item_id": a["item_id"], "edit_prompt": a["prompt"], "edit_answer": a["answer"],
                                "neighbour_prompt": b["prompt"], "neighbour_answer": b["answer"], "type": "same_subject_other_relation"})
    return out


def compositions(zs: list[dict]) -> list[dict]:
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for it in zs:
        by_subject[normalize_answer(it["subject"])].append(it)
    out = []
    for a in zs:
        o1 = normalize_answer(a["answer"])
        for b in by_subject.get(o1, []):
            if normalize_answer(b["answer"]) == normalize_answer(a["subject"]):
                continue  # trivial cycle
            out.append({"dataset": "zsre", "first_item_id": a["item_id"], "first_prompt": a["prompt"], "o1": a["answer"],
                        "second_item_id": b["item_id"], "second_prompt": b["prompt"], "o2": b["answer"],
                        "composed_reference": "unambiguous: o2 is the pool's stored answer for (o1, r2)"})
    return out


def temporal_corrections(cf: list[dict], rng: np.random.Generator, n: int = MIN) -> list[dict]:
    cands = [it for it in cf if normalize_answer(it.get("target_true", "")) not in ("", normalize_answer(it["answer"]))]
    idx = rng.permutation(len(cands))[:n]
    out = []
    for i in idx:
        it = cands[i]
        digest = hashlib.sha256(f"fact|{it['fact_id']}".encode()).hexdigest()[:32]
        out.append({"dataset": "counterfact", "fact_id": it["fact_id"], "fact_digest": digest, "prompt": it["prompt"],
                    "versions": [{"version": 1, "answer": it["target_true"], "aliases": [normalize_answer(it["target_true"])]},
                                 {"version": 2, "answer": it["answer"], "aliases": [normalize_answer(it["answer"])]}],
                    "paraphrases": it.get("paraphrases", []), "subject": it["subject"],
                    "evaluation": "only the currently valid (latest) answer counts; reappearance of the obsolete answer reported separately"})
    return out


def build(seed: int = 23) -> dict:
    rng = np.random.default_rng(seed)
    dev_subs = _dev_subjects()
    cf = [it for it in _pool("counterfact") if normalize_answer(it["subject"]) not in dev_subs]
    zs = [it for it in _pool("zsre") if normalize_answer(it["subject"]) not in dev_subs]
    nn = near_neighbours(cf, zs, rng)
    rng.shuffle(nn)
    comp = compositions(zs)
    temp = temporal_corrections(cf, rng)
    doc = {
        "name": "challenges", "mode": "dev", "stage": "DATA", "seed": seed,
        "source": "sealed confirmation source pools, development subjects excluded",
        "near_neighbour": {"n": len(nn), "required": MIN, "status": "ok" if len(nn) >= MIN else "unsupported", "items": nn[: max(MIN, min(len(nn), 400))]},
        "composition": {"n": len(comp), "required": MIN, "status": "ok" if len(comp) >= MIN else "unsupported",
                        "unsupported_remainder": max(0, MIN - len(comp)), "items": comp},
        "temporal_correction": {"n": len(temp), "required": MIN, "status": "ok" if len(temp) >= MIN else "unsupported", "items": temp},
    }
    for k in ("near_neighbour", "composition", "temporal_correction"):
        doc[k]["sha256_items"] = hashlib.sha256(json.dumps(doc[k]["items"], sort_keys=True).encode()).hexdigest()
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    return doc


def audit() -> dict:
    doc = json.loads(OUT.read_text())
    dev_subs = _dev_subjects()
    used = set()
    for it in doc["near_neighbour"]["items"]:
        used.add(normalize_answer(it["edit_prompt"]))
    for it in doc["temporal_correction"]["items"]:
        assert normalize_answer(it["subject"]) not in dev_subs
    for k in ("near_neighbour", "composition", "temporal_correction"):
        assert hashlib.sha256(json.dumps(doc[k]["items"], sort_keys=True).encode()).hexdigest() == doc[k]["sha256_items"]
    return {k: {"n": doc[k]["n"], "status": doc[k]["status"], "unsupported_remainder": doc[k].get("unsupported_remainder", 0)}
            for k in ("near_neighbour", "composition", "temporal_correction")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args(argv)
    if args.build:
        build()
    if args.audit:
        print(json.dumps(audit(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
