"""DEC-045 teacher/eligibility pass over Codex's prepared MQuAKE-CF items (R1-D4): the zsRE rule (DEC-039) — the base's
greedy answer to the edit prompt must not already match the new answer or an alias; one paraphrase suffices. Writes every
eligible item in the training-pool schema (no draw, no roles, no seal): the pool is the input of the later development /
training / confirmatory reservations.
    python scripts/r1_d5_mquake_teacher.py [--no-lease] → manifests/revision_v1/mquake_pool_v1.json"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ITEMS = Path("/home/derp/cap/assets/data/prepared/revision_v1/r1_d4_v1/items.jsonl")
MANIFEST = ROOT / "manifests" / "revision_v1" / "mquake_items_v1.json"
OUT = ROOT / "manifests" / "revision_v1" / "mquake_pool_v1.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; pools are versioned")
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.data.decode import greedy_decode_batch
    from pccap.data.streams import normalize_answer
    from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger

    man = json.loads(MANIFEST.read_text())
    expected = man["artifacts"]["items"]["sha256"]
    if hashlib.sha256(ITEMS.read_bytes()).hexdigest() != expected:
        raise SystemExit("items.jsonl does not match manifests/revision_v1/mquake_items_v1.json")
    rows = [json.loads(line) for line in ITEMS.read_text().splitlines() if line.strip()]
    tok = GPT2Tokenizer()
    counts = {"candidates": len(rows), "excluded_tokenize": 0, "no_paraphrase": 0, "no_locality": 0, "teacher_correct": 0, "eligible": 0}
    prepared = []
    for c in rows:
        if not c.get("paraphrases"):
            counts["no_paraphrase"] += 1
            continue
        loc = c.get("locality") or []
        if not loc:
            counts["no_locality"] += 1
            continue
        pair = tokenize_pair(tok, c["prompt"], c["answer"])
        if pair.excluded:
            counts["excluded_tokenize"] += 1
            continue
        if list(pair.prompt_ids) != list(c["prompt_ids"]) or list(pair.answer_ids) != list(c["answer_ids"]):
            raise SystemExit(f"tokenization differs from the prepared record for {c['item_id']}")
        aliases = sorted({normalize_answer(a) for a in (c.get("aliases") or [c["answer"]])} | {normalize_answer(c["answer"])})
        prepared.append((c, pair, aliases, loc))
    t0 = time.time()
    items = []
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:d5_mquake_teacher", stage="R1", projected_seconds=1800.0)):
        base = BPBase(ledger=Ledger())
        prompts = [np.asarray(p[1].prompt_ids, np.int32) for p in prepared]
        decs = greedy_decode_batch(base, prompts, tok, batch_size=64, phase="query")
        for (c, pair, aliases, loc), d in zip(prepared, decs):
            if normalize_answer(d.text) in set(aliases):
                counts["teacher_correct"] += 1
                continue
            items.append({"item_id": c["item_id"], "dataset": "mquake", "prompt": c["prompt"], "answer": c["answer"], "aliases": aliases,
                          "paraphrases": list(c["paraphrases"]), "locality_prompts": [x["prompt"] for x in loc], "locality_answers": [x["answer"] for x in loc],
                          "subject": c["subject"], "fact_id": c["fact_id"], "relation_id": c["relation_id"], "target_true": c["target_true"]["str"] if isinstance(c["target_true"], dict) else c["target_true"],
                          "prompt_ids": pair.prompt_ids.tolist(), "answer_ids": pair.answer_ids.tolist(), "answer_tokens": len(pair.answer_ids),
                          "teacher_generation": d.text, "teacher_stopped_by": d.stopped_by, "digest": c["digest"], "source_case_id": c["source_case_id"],
                          "near_miss_candidates": c.get("near_miss_candidates"), "composition_questions_available": c.get("composition_question_count_available_dependencies", 0)})
        counts["eligible"] = len(items)
    doc = {"name": "mquake_pool_v1", "dataset": "mquake", "date": "2026-09-14", "decision": "DEC-045", "rule": "zsRE teacher rule (DEC-039): greedy base answer to the edit prompt is not the new answer or an alias; >= 1 paraphrase; >= 1 locality prompt",
           "sources_sha256": {str(ITEMS): expected, str(MANIFEST): hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}, "counts": counts, "teacher_seconds": time.time() - t0,
           "status": "teacher-eligible pool; no roles assigned, no draw, no seal", "items": items,
           "subjects_normalized": sorted({normalize_answer(it["subject"]) for it in items})}
    OUT.write_text(json.dumps(doc, ensure_ascii=False) + "\n")
    print(json.dumps({"counts": counts, "teacher_seconds": round(doc["teacher_seconds"], 1), "out": str(OUT)}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
