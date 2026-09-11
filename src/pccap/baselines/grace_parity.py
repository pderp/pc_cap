"""PC-10 source parity measurement; CPU-capable, no tolerances fitted to outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import unicodedata
from pathlib import Path

import numpy as np

from pccap.baselines.grace_jax import GraceLearner
from pccap.bases.bp import BPBase
from pccap.contracts import EditItem
from pccap.data.tokenize import GPT2Tokenizer

ROOT = Path(__file__).resolve().parents[3]
# Set before the first real-case comparison. Failure is retained, never widened.
TOLERANCE = {"keys": {"atol": 2e-4, "rtol": 2e-5},
             "values": {"atol": 2e-3, "rtol": 2e-4},
             "radii": {"atol": 2e-4, "rtol": 2e-5},
             "answer_nll": {"atol": 1e-3, "rtol": 1e-4}}


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def to_item(raw):
    return EditItem(raw["item_id"], bytes.fromhex(raw["digest"]), raw["prompt"], raw["answer"],
                    list(raw["aliases"]), list(raw["paraphrases"]), list(raw["locality_prompts"]),
                    np.asarray(raw["prompt_ids"], np.int32), np.asarray(raw["answer_ids"], np.int32))


def evaluate(learner, item, tokenizer):
    before = learner.state_hash()
    ids, emitted = item.prompt_ids.tolist(), []
    for _ in range(32):
        nxt = int(learner.predict(ids, key_position=len(item.prompt_ids)-1, last_only=True).argmax())
        ids.append(nxt)
        emitted.append(nxt)
        if nxt in (198, 50256):
            break
    stopped = bool(emitted and emitted[-1] in (198, 50256))
    text = tokenizer.decode(emitted[:-1] if stopped else emitted)
    logits = learner.predict(np.concatenate([item.prompt_ids, item.answer_ids]), key_position=len(item.prompt_ids)-1)
    rows = logits[len(item.prompt_ids)-1:len(item.prompt_ids)+len(item.answer_ids)-1].astype(np.float64)
    maxima = rows.max(-1)
    nll = float(np.sum(maxima + np.log(np.exp(rows-maxima[:, None]).sum(-1))
                       - rows[np.arange(len(item.answer_ids)), item.answer_ids]))
    assert learner.state_hash() == before, "evaluation mutated GRACE state"
    return {"new_ids": emitted, "text": text, "stopped": stopped,
            "target_match": normalize(text) == normalize(item.answer), "answer_nll": nll}


def compare_book(learner, path):
    result = {}
    with np.load(path, allow_pickle=False) as book:
        for name in ("keys", "values", "radii"):
            actual = getattr(learner, name)
            target = book[name].reshape(actual.shape) if book[name].size == actual.size else book[name]
            same_shape = actual.shape == target.shape
            result[name] = {"actual_shape": list(actual.shape), "reference_shape": list(target.shape),
                            "max_abs": float(np.max(np.abs(actual-target))) if same_shape and actual.size else None,
                            "pass": bool(same_shape and np.allclose(actual, target, **TOLERANCE[name]))}
        result["labels"] = {"pass": len(learner.labels) == len([k for k in book.files if k.startswith("key_label_")])
                           and all(np.array_equal(a, book[f"key_label_{i}"].reshape(-1)) for i, a in enumerate(learner.labels))}
    return result


def compare_eval(actual, reference):
    return {"greedy_ids_equal": actual["new_ids"] == reference["greedy"]["new_ids"],
            "canonical_text_equal": normalize(actual["text"]) == normalize(reference["greedy"]["text"]),
            "nll_abs_difference": abs(actual["answer_nll"]-reference["teacher_forced_answer_nll"]),
            "nll_pass": bool(np.isclose(actual["answer_nll"], reference["teacher_forced_answer_nll"], **TOLERANCE["answer_nll"]))}


def run(manifest=ROOT / "manifests/dev/grace_parity_cases.json"):
    import jax
    m = json.loads(Path(manifest).read_text())
    # Validate every declared source input/artifact before comparing against it.
    for group in ("inputs", "files"):
        for rec in m[group].values():
            path = Path(rec["path"])
            if path.stat().st_size != rec["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != rec["sha256"]:
                raise ValueError("reference input/artifact changed: " + str(path))
    raw = json.loads((ROOT / "manifests/dev/zsre_dev.json").read_text())
    by_id = {r["item_id"]: r for r in raw["items"]}
    items = [to_item(by_id[c["item_id"]]) for c in m["cases"]]
    base, tokenizer = BPBase(), GPT2Tokenizer()
    base_hash = base.checksum()
    started = time.monotonic()
    isolated, sequential = [], []
    for index, (case, item) in enumerate(zip(m["cases"], items)):
        learner = GraceLearner(base, seed=case["isolated_seed"])
        outcome = learner.update_item(item)
        actual = evaluate(learner, item, tokenizer)
        reference = json.loads(Path(m["files"][case["isolated_output"]]["path"]).read_text())
        rec = {"index": index, "item_id": item.item_id, "actual": actual,
               "evaluation": compare_eval(actual, reference["evaluation"]),
               "codebook": compare_book(learner, m["files"][case["isolated_codebook"]]["path"]),
               "losses": outcome.prefix_outcomes[0]["source_losses"]}
        isolated.append(rec)
        print(json.dumps({"phase": "isolated", "completed": index+1,
                          "book_pass": all(x["pass"] for x in rec["codebook"].values()),
                          "evaluation": rec["evaluation"]}), flush=True)
    learner = GraceLearner(base, seed=0)
    for index, (case, item) in enumerate(zip(m["cases"], items)):
        learner.update_item(item)
        rec = {"index": index, "item_id": item.item_id,
               "codebook": compare_book(learner, m["files"][case["sequence_codebook"]]["path"])}
        sequential.append(rec)
        print(json.dumps({"phase": "sequence", "completed": index+1,
                          "book_pass": all(x["pass"] for x in rec["codebook"].values())}), flush=True)
    expected_final = json.loads(Path(m["files"]["sequence_final.json"]["path"]).read_text())
    final = [{"item_id": it.item_id, **compare_eval(evaluate(learner, it, tokenizer), ref)}
             for it, ref in zip(items, expected_final["evaluations"])]
    pass_book = all(x["pass"] for rec in isolated+sequential for x in rec["codebook"].values())
    evals = [r["evaluation"] for r in isolated]+final
    pass_eval = all(r["greedy_ids_equal"] and r["nll_pass"] for r in evals)
    unchanged = base.checksum() == base_hash
    return {"status": "pass" if pass_book and pass_eval and unchanged else "parity_failure",
            "backend": jax.default_backend(), "tolerances": TOLERANCE,
            "reference_manifest_sha256": hashlib.sha256(Path(manifest).read_bytes()).hexdigest(),
            "isolated": isolated, "sequence": sequential, "final_evaluations": final,
            "codebook_parity": pass_book, "evaluation_parity": pass_eval,
            "base_unchanged": unchanged, "wall_seconds": time.monotonic()-started,
            "ledger": base.ledger.totals(),
            "interpretation": "A failure blocks B4 registration; source fixtures and tolerances were not changed."}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.exists():
        raise FileExistsError(args.out)
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as out:
        json.dump(result, out, indent=2, allow_nan=False)
        out.write("\n")
    print(result["status"])
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
