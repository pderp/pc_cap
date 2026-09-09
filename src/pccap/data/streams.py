"""Editing pools (DATA-01; PDF E.2, D.1; SD-2, SD-9).

Readers for zsRE (MEND eval file) and CounterFact with the DATA-00 field mapping, canonical
answer + newline through the tested tokenization helper (answers > 32 tokens excluded and
counted), deduplication of facts and subjects, the E.2 selection filter (keep only items whose
BP-teacher complete greedy answer is **outside** the aliases), and the split into:

* the development pool (≥ 300 edits with paraphrases per dataset, including the S0 sample;
  ≥ 1,000 unrelated / near-neighbour prompts per dataset) → ``manifests/dev/<ds>_dev.json``;
* the sealed confirmation source pool (the remaining eligible items, not yet split into
  realizations) → ``assets/data/prepared/editing/<ds>_eligible.jsonl`` (hash in
  ``manifests/dev/pools.json``).

Teacher generations run under the GPU lease with the batched cap-off decoder and every access is
logged in ``results/DATA/selection_access.log``.

    python -m pccap.data.streams --build      # generate + select + split (GPU lease)
    python -m pccap.data.splits --audit       # counts and the dev/confirm subject disjointness
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from pccap import ASSETS_ROOT
from pccap.data.splits import (
    DEV,
    ROOT,
    counterfact_item,
    item_digest,
    load_counterfact,
    load_zsre,
    zsre_item,
)
from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.metrics.editing import normalize_answer

PREPARED = Path(ASSETS_ROOT) / "data" / "prepared" / "editing"
POOLS = DEV / "pools.json"
ACCESS_LOG = ROOT / "results" / "DATA" / "selection_access.log"
DEV_SEED = 13
DEV_EDITS = 300
DEV_UNRELATED = 1000


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidates(dataset: str) -> list[dict]:
    if dataset == "zsre":
        return [zsre_item(i, r) for i, r in enumerate(load_zsre("eval"))]
    if dataset == "counterfact":
        return [counterfact_item(r) for r in load_counterfact()]
    raise ValueError(dataset)


def tokenize_and_filter(items: list[dict], tok: GPT2Tokenizer) -> tuple[list[dict], dict]:
    """Attach token ids; drop empty/over-long answers; deduplicate facts (prompt+answer) and subjects."""
    counts = {"candidates": len(items), "excluded_length": 0, "excluded_empty": 0, "dup_fact": 0, "dup_subject": 0}
    seen_fact, seen_subject = set(), set()
    out = []
    for it in items:
        te = tokenize_pair(tok, it["prompt"], it["answer"])
        if te.excluded:
            counts["excluded_length" if te.reason.startswith("answer_tokens") else "excluded_empty"] += 1
            continue
        fk = (normalize_answer(it["prompt"]), normalize_answer(it["answer"]))
        if fk in seen_fact:
            counts["dup_fact"] += 1
            continue
        sk = normalize_answer(it["subject"])
        if sk in seen_subject:
            counts["dup_subject"] += 1
            continue
        seen_fact.add(fk)
        seen_subject.add(sk)
        it = dict(it)
        it["prompt_ids"] = te.prompt_ids.tolist()
        it["answer_ids"] = te.answer_ids.tolist()
        it["answer_tokens"] = len(te.answer_ids)
        it["digest"] = item_digest(it)
        out.append(it)
    return out, counts


def teacher_select(items: list[dict], base, tok: GPT2Tokenizer, dataset: str, batch_size: int = 64) -> tuple[list[dict], dict]:
    """E.2: keep only items whose teacher greedy answer is outside the aliases. Logs the access."""
    from pccap.data.decode import greedy_decode_batch

    ACCESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    prompts = [np.asarray(it["prompt_ids"], np.int32) for it in items]
    decs = greedy_decode_batch(base, prompts, tok, batch_size=batch_size, phase="query")
    kept, correct = [], 0
    for it, d in zip(items, decs):
        gen = normalize_answer(d.text)
        it["teacher_generation"] = d.text
        it["teacher_stopped_by"] = d.stopped_by
        if gen in set(it["aliases"]):
            correct += 1
            continue
        kept.append(it)
    with open(ACCESS_LOG, "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "task": "DATA-01", "dataset": dataset,
                            "purpose": "E.2 selection: teacher complete greedy generation on every candidate prompt",
                            "prompts": len(items), "teacher_correct": correct, "eligible": len(kept),
                            "decoder": "greedy_decode_batch (cap-off, no cache, max 32, stop at newline/EOS)",
                            "seconds": time.time() - t0}) + "\n")
    return kept, {"teacher_correct": correct, "eligible": len(kept)}


def split_dev(eligible: list[dict], dataset: str, seed: int = DEV_SEED) -> tuple[list[dict], list[dict], list[str]]:
    """Development pool = S0-sample items (must be inside) + random eligible items to reach DEV_EDITS
    with paraphrases; confirmation pool = the rest; unrelated prompts from the dev items' own
    locality prompts plus, if short, locality prompts of confirmation items (prompts only, no answers
    of theirs are used for anything)."""
    s0 = json.loads((DEV / "s0_sample.json").read_text())
    s0_ids = {it["item_id"] for it in s0["items"] if it["dataset"] == dataset}
    rng = np.random.default_rng(seed)
    with_para = [it for it in eligible if it["paraphrases"]]
    dev = [it for it in with_para if it["item_id"] in s0_ids]
    rest = [it for it in with_para if it["item_id"] not in s0_ids]
    order = rng.permutation(len(rest))
    need = max(0, DEV_EDITS - len(dev))
    dev += [rest[i] for i in order[:need]]
    dev_ids = {it["item_id"] for it in dev}
    dev_subjects = {normalize_answer(it["subject"]) for it in dev}
    confirm = [it for it in eligible if it["item_id"] not in dev_ids and normalize_answer(it["subject"]) not in dev_subjects]
    # unrelated / near-neighbour prompts
    unrelated: list[str] = []
    seen = set()
    for it in dev:
        for p in it["locality_prompts"]:
            if p not in seen:
                seen.add(p)
                unrelated.append(p)
    if len(unrelated) < DEV_UNRELATED:
        for i in rng.permutation(len(confirm)):
            for p in confirm[i]["locality_prompts"]:
                if p not in seen:
                    seen.add(p)
                    unrelated.append(p)
            if len(unrelated) >= DEV_UNRELATED:
                break
    return dev, confirm, unrelated


def build(datasets=("zsre", "counterfact"), batch_size: int = 64) -> dict:
    from pccap.bases.bp import BPBase
    from pccap.harness.lease import gpu_lease

    tok = GPT2Tokenizer()
    summary = {}
    PREPARED.mkdir(parents=True, exist_ok=True)
    DEV.mkdir(parents=True, exist_ok=True)
    with gpu_lease("DATA-01", stage="DATA", projected_seconds=3600) as lease:
        base = BPBase()
        for ds in datasets:
            items, counts = tokenize_and_filter(candidates(ds), tok)
            eligible, sel = teacher_select(items, base, tok, ds, batch_size)
            dev, confirm, unrelated = split_dev(eligible, ds)
            dev_manifest = {"name": f"{ds}_dev", "mode": "dev", "stage": "DATA", "seed": DEV_SEED, "dataset": ds,
                            "items": dev, "unrelated_prompts": unrelated, "counts": {**counts, **sel, "dev": len(dev),
                                                                                       "unrelated": len(unrelated), "confirm_pool": len(confirm)},
                            "selection": "E.2 teacher-incorrect only; aliases per SD-9; answers <= 32 tokens incl. newline"}
            (DEV / f"{ds}_dev.json").write_text(json.dumps(dev_manifest, indent=1) + "\n")
            pool_path = PREPARED / f"{ds}_eligible.jsonl"
            with open(pool_path, "w") as f:
                for it in confirm:
                    f.write(json.dumps(it) + "\n")
            summary[ds] = {**dev_manifest["counts"], "dev_manifest": str(DEV / f"{ds}_dev.json"),
                           "dev_sha256": _sha(DEV / f"{ds}_dev.json"), "confirm_pool_path": str(pool_path),
                           "confirm_pool_sha256": _sha(pool_path)}
            print(ds, summary[ds], flush=True)
        summary["lease"] = lease.report
        summary["base_checksum"] = base.checksum()
        summary["ledger"] = base.ledger.totals()
    POOLS.write_text(json.dumps(summary, indent=1, default=str) + "\n")
    return summary


def audit() -> dict:
    out = {}
    for ds in ("zsre", "counterfact"):
        m = json.loads((DEV / f"{ds}_dev.json").read_text())
        pool_path = PREPARED / f"{ds}_eligible.jsonl"
        confirm_subjects = set()
        n_conf = 0
        with open(pool_path) as f:
            for line in f:
                n_conf += 1
                confirm_subjects.add(normalize_answer(json.loads(line)["subject"]))
        dev_subjects = {normalize_answer(it["subject"]) for it in m["items"]}
        overlap = dev_subjects & confirm_subjects
        out[ds] = {**m["counts"], "confirm_pool_lines": n_conf, "dev_confirm_subject_overlap": len(overlap)}
        assert not overlap, f"{ds}: dev/confirm subject overlap {len(overlap)}"
        assert len(m["items"]) >= DEV_EDITS and len(m["unrelated_prompts"]) >= DEV_UNRELATED, ds
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--batch-size", type=int, default=64)
    args = ap.parse_args(argv)
    if args.build:
        build(batch_size=args.batch_size)
    if args.audit:
        print(json.dumps(audit(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
