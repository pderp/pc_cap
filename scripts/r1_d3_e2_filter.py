"""DEC-039: the zsRE TRAINING pool — E.2 teacher filter over Codex's candidate list (R1-D3), tokenized into the pool format
used by the CounterFact training pool (prompt_ids/answer_ids, paraphrases = [rephrase], locality prompts/answers).
    python scripts/r1_d3_e2_filter.py --candidates manifests/revision_v1/train_pool_zsre_candidates_v1.json [--n 3000] [--no-lease]
    → manifests/revision_v1/train_pool_zsre_v1.json"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manifests" / "revision_v1" / "train_pool_zsre_v1.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default="manifests/revision_v1/train_pool_zsre_candidates_v1.json")
    ap.add_argument("--n", type=int, default=3000)
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

    cand_path = ROOT / args.candidates
    doc = json.loads(cand_path.read_text())
    cands = doc.get("items") or doc.get("candidates") or doc["records"]
    tok = GPT2Tokenizer()
    items, counts = [], {"candidates": len(cands), "excluded_tokenize": 0, "no_rephrase": 0, "teacher_correct": 0, "eligible": 0}
    prepared = []
    for c in cands:
        prompt, answer = c.get("prompt") or c.get("src"), c.get("answer") or c.get("alt") or c.get("answers", [None])[0]
        reph = c.get("rephrase") or (c.get("paraphrases") or [None])[0]
        if not reph:
            counts["no_rephrase"] += 1
            continue
        pair = tokenize_pair(tok, prompt, answer)
        if pair.excluded:
            counts["excluded_tokenize"] += 1
            continue
        aliases = [normalize_answer(a) for a in (c.get("aliases") or c.get("answers") or [answer])]
        prepared.append((c, prompt, answer, reph, pair, aliases))
    with (contextlib.nullcontext() if args.no_lease else gpu_lease("R1:d3_e2", stage="R1", projected_seconds=1800.0)):
        base = BPBase(ledger=Ledger())
        t0 = time.time()
        prompts = [np.asarray(p[4].prompt_ids, np.int32) for p in prepared]
        decs = greedy_decode_batch(base, prompts, tok, batch_size=64, phase="query")
        for (c, prompt, answer, reph, pair, aliases), d in zip(prepared, decs):
            if normalize_answer(d.text) in set(aliases):
                counts["teacher_correct"] += 1
                continue
            loc_p = c.get("locality_prompts") or ([c["locality_prompt"]] if c.get("locality_prompt") else [])
            loc_a = c.get("locality_answers") or ([c["locality_answer"]] if c.get("locality_answer") else [])
            items.append({"item_id": c.get("item_id") or f"zsre-train-{c.get('source_record_index', len(items))}", "dataset": "zsre", "prompt": prompt, "answer": answer,
                          "aliases": aliases, "paraphrases": [reph], "locality_prompts": loc_p, "locality_answers": loc_a, "subject": c.get("subject", ""),
                          "fact_id": c.get("fact_id") or c.get("item_id") or f"zsre-train-{len(items)}", "prompt_ids": pair.prompt_ids.tolist(), "answer_ids": pair.answer_ids.tolist(),
                          "answer_tokens": len(pair.answer_ids), "teacher_generation": d.text, "teacher_stopped_by": d.stopped_by, "source_record_index": c.get("source_record_index")})
            if len(items) >= args.n:
                break
        counts["eligible"] = len(items)
    OUT.write_text(json.dumps({"name": "train_pool_zsre_v1", "mode": "train_pool", "dataset": "zsre", "decision": "DEC-039", "purpose": "revision v1 Stage 2 training (never confirmatory); subjects are an exposure for the exclusion register v3",
                               "sources_sha256": {str(cand_path): hashlib.sha256(cand_path.read_bytes()).hexdigest()}, "counts": counts, "selection": "E.2 teacher-incorrect only (greedy, cap-off); one rephrase per item",
                               "teacher_seconds": time.time() - t0, "items": items, "drawn_subjects_normalized": sorted({normalize_answer(it["subject"]) for it in items if it["subject"]})}, indent=1) + "\n")
    print(json.dumps({"counts": counts, "out": str(OUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
