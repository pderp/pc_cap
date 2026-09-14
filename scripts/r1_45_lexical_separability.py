"""R1-45: all-item GPT-2 lexical separability; CPU text/tokenizer only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections import Counter
from pathlib import Path

from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
FEATURES = (
    "subject_recall",
    "subject_recall_stop200",
    "prompt_overlap",
    "prompt_overlap_stop200",
    "longest_common_span_tokens",
    "longest_common_span_fraction",
    "relation_template_overlap",
    "relation_template_overlap_stop200",
)
POOLS = {
    "counterfact_dev": "manifests/dev/counterfact_dev.json",
    "zsre_dev": "manifests/dev/zsre_dev.json",
    "counterfact_train": "manifests/revision_v1/train_pool_counterfact_v1.json",
}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def sequence_index(ids):
    index = {}
    for i, token in enumerate(ids):
        index.setdefault(token, []).append(i)
    return index


def common_span(index, query):
    longest = 0
    previous = {}
    for token in query:
        current = {}
        for pos in index.get(token, ()):
            length = previous.get(pos - 1, 0) + 1
            current[pos] = length
            longest = max(longest, length)
        previous = current
    return longest


def recall(reference, query):
    return len(reference & query) / len(reference) if reference else 0.0


def symmetric_overlap(a, b):
    if not a or not b:
        return 0.0
    hit = len(a & b)
    return 0.5 * (hit / len(a) + hit / len(b))


def features(support, query):
    q, qs = query["set"], query["stopped"]
    length = common_span(support["index"], query["ids"])
    return (
        recall(support["subject"], q),
        recall(support["subject_stopped"], qs),
        symmetric_overlap(support["set"], q),
        symmetric_overlap(support["stopped"], qs),
        float(length),
        length / len(support["ids"]) if support["ids"] else 0.0,
        recall(support["relation"], q),
        recall(support["relation_stopped"], qs),
    )


def roc(positive, negative):
    """Exact tie-aware empirical ROC. Inputs are weighted score histograms."""
    p, n = sum(positive.values()), sum(negative.values())
    if not p or not n:
        return {"auc": None, "positive_weight": p, "negative_weight": n, "points": []}
    below, winning = 0.0, 0.0
    for score in sorted(set(positive) | set(negative)):
        winning += positive.get(score, 0.0) * (below + 0.5 * negative.get(score, 0.0))
        below += negative.get(score, 0.0)
    tp, fp = 0.0, 0.0
    points = [{"threshold": None, "tpr": 0.0, "fpr": 0.0, "meaning": "accept no scores"}]
    for score in sorted(set(positive) | set(negative), reverse=True):
        tp += positive.get(score, 0.0)
        fp += negative.get(score, 0.0)
        points.append({"threshold": float(score), "tpr": tp / p, "fpr": fp / n})
    best = max(points, key=lambda r: r["tpr"] - r["fpr"])
    at_low = max((r for r in points if r["fpr"] <= 0.01 + 1e-12), key=lambda r: r["tpr"])
    return {
        "auc": winning / (p * n),
        "positive_weight": p,
        "negative_weight": n,
        "best_youden_development_only": best,
        "max_tpr_at_fpr_le_0.01": at_low,
        "points": points,
    }


def support_features(item, encoded, stop):
    enc = encoded[item["prompt"]]
    ids = tuple(enc.ids)
    matches = list(
        re.finditer(
            r"(?<!\w)" + re.escape(item["subject"]) + r"(?!\w)", item["prompt"], re.IGNORECASE
        )
    )
    positions = {
        i
        for match in matches
        for i, (a, b) in enumerate(enc.offsets)
        if a < match.end() and b > match.start()
    }
    subject = {ids[i] for i in positions}
    method = "literal_subject_span_in_support_prompt"
    if not positions:
        subject = set(encoded[" " + item["subject"]].ids)
        method = "fallback_space_prefixed_subject_tokens_no_literal_span"
    relation = {t for i, t in enumerate(ids) if i not in positions}
    return {
        "ids": ids,
        "set": set(ids),
        "stopped": set(ids) - stop,
        "subject": subject,
        "subject_stopped": subject - stop,
        "relation": relation,
        "relation_stopped": relation - stop,
        "index": sequence_index(ids),
        "subject_method": method,
        "subject_span_found": bool(positions),
    }


def analyze(output):
    started = time.monotonic()
    sources = {}

    def load(rel):
        p = ROOT / rel
        sources[str(p)] = sha(p)
        return json.loads(p.read_text())

    pools = {name: load(path)["items"] for name, path in POOLS.items()}
    ref = load("manifests/reference.json")["inputs"]["tokenizer.json"]
    tokenizer_path = Path(ref["path"])
    if sha(tokenizer_path) != ref["sha256"]:
        raise ValueError("tokenizer hash mismatch")
    sources[str(tokenizer_path)] = ref["sha256"]
    source_script = Path(__file__).resolve()
    sources[str(source_script)] = sha(source_script)
    installed = load("manifests/revision_v1/stop_tokens_v1.json")
    documents = [
        text
        for rows in pools.values()
        for row in rows
        for text in [row["prompt"], *row["paraphrases"], *row["locality_prompts"]]
    ]
    extra = [" " + row["subject"] for rows in pools.values() for row in rows]
    texts = sorted(set(documents + extra))
    tok = Tokenizer.from_file(str(tokenizer_path))
    encoded = dict(zip(texts, tok.encode_batch(texts, add_special_tokens=False)))
    counts = Counter(t for text in documents for t in encoded[text].ids)
    document_counts = Counter(t for text in documents for t in set(encoded[text].ids))
    stop_list = sorted(counts, key=lambda t: (-counts[t], t))[:200]
    stop = set(stop_list)
    q_cache = {
        text: {"ids": tuple(enc.ids), "set": set(enc.ids), "stopped": set(enc.ids) - stop}
        for text, enc in encoded.items()
    }
    reports = {}
    for name, items in pools.items():
        supports = [support_features(row, encoded, stop) for row in items]
        h = {
            role: [Counter() for _ in FEATURES]
            for role in ("paraphrase", "locality", "other_prompt")
        }
        weighted = {role: [Counter() for _ in FEATURES] for role in h}
        totals = Counter()
        records = []
        for i, (item, support) in enumerate(zip(items, supports)):
            record = {
                "item_id": item["item_id"],
                "source_row_sha256": digest(item),
                "subject_span_found": support["subject_span_found"],
                "subject_method": support["subject_method"],
                "subject_token_count": len(support["subject"]),
                "subject_token_count_after_stop": len(support["subject_stopped"]),
                "relation_token_count": len(support["relation"]),
                "relation_token_count_after_stop": len(support["relation_stopped"]),
            }
            for role in h:
                local = [Counter() for _ in FEATURES]
                details = []
                if role == "paraphrase":
                    queries = [(None, s) for s in item["paraphrases"]]
                elif role == "locality":
                    queries = [(None, s) for s in item["locality_prompts"]]
                else:
                    queries = ((r["item_id"], r["prompt"]) for j, r in enumerate(items) if j != i)
                nq = 0
                for _other_id, text in queries:
                    values = features(support, q_cache[text])
                    for hist, value in zip(local, values):
                        hist[value] += 1
                    nq += 1
                    if role != "other_prompt":
                        details.append(
                            {
                                "query_sha256": hashlib.sha256(text.encode()).hexdigest(),
                                "values": list(values),
                            }
                        )
                totals[role] += nq
                for global_hist, whist, local_hist in zip(h[role], weighted[role], local):
                    global_hist.update(local_hist)
                    for value, count in local_hist.items():
                        whist[value] += count / nq
                if role == "other_prompt":
                    record["other_prompt_count"] = nq
                    record["other_prompt_feature_means"] = [
                        sum(k * v for k, v in counter.items()) / nq if nq else None
                        for counter in local
                    ]
                else:
                    record[role] = details
            records.append(record)
            if (i + 1) % 300 == 0:
                print(
                    json.dumps(
                        {
                            "pool": name,
                            "items_done": i + 1,
                            "items_total": len(items),
                            "elapsed_seconds": time.monotonic() - started,
                        }
                    ),
                    flush=True,
                )
        comparisons = {}
        for negative in ("locality", "other_prompt"):
            comparisons["paraphrase_vs_" + negative] = {
                feature: {
                    "query_weighted": roc(h["paraphrase"][k], h[negative][k]),
                    "item_balanced": roc(weighted["paraphrase"][k], weighted[negative][k]),
                }
                for k, feature in enumerate(FEATURES)
            }
        reports[name] = {
            "dataset": items[0]["dataset"],
            "n_items": len(items),
            "query_counts": dict(totals),
            "coverage": {
                "subject_span_missing": sum(not s["subject_span_found"] for s in supports),
                "subject_tokens_empty_after_stop": sum(not s["subject_stopped"] for s in supports),
                "relation_tokens_empty": sum(not s["relation"] for s in supports),
                "relation_tokens_empty_after_stop": sum(
                    not s["relation_stopped"] for s in supports
                ),
            },
            "comparisons": comparisons,
            "records": records,
        }
    result = {
        "task": "R1-45",
        "schema_version": 1,
        "sources_sha256": sources,
        "feature_order": list(FEATURES),
        "tokenization": {
            "source": "pinned GPT-2 tokenizer.json; add_special_tokens=False",
            "text_policy": "original text/case/punctuation, no lowercasing; consistent with deployed lexical token IDs",
            "documents_counted": len(documents),
            "unique_texts_encoded": len(texts),
            "answer_texts_counted": False,
        },
        "stoplist": {
            "rule": "200 highest occurrence-count GPT-2 token IDs over all source prompt/paraphrase/locality documents in all three pools; repeated document occurrences count; ties by token ID",
            "tokens": stop_list,
            "counts": [
                {
                    "token": t,
                    "occurrences": counts[t],
                    "document_occurrences": document_counts[t],
                    "decoded": tok.decode([t], skip_special_tokens=False),
                }
                for t in stop_list
            ],
            "installed_stoplist_intersection": len(stop & set(installed["tokens"])),
            "installed_stoplist_size": len(installed["tokens"]),
            "difference": "installed v1 uses document frequency and only first two localities; this audit obeys all-items/all-localities occurrence frequency; neither is a fresh generalization test",
        },
        "feature_definitions": {
            "subject_recall": "fraction of distinct token IDs from the support prompt's literal subject span found in the query; fallback space-prefixed subject tokens when span absent",
            "subject_recall_stop200": "same after removing the empirical top-200 tokens; empty reference gets zero and its coverage count is explicit",
            "prompt_overlap": "mean of two directional distinct-token overlaps, matching reader.lex_feature without a stop list",
            "prompt_overlap_stop200": "same after removing the empirical top-200 tokens",
            "longest_common_span_tokens": "exact longest contiguous common GPT-2 token substring length",
            "longest_common_span_fraction": "same length divided by the support prompt's token length",
            "relation_template_overlap": "fraction of distinct support prompt token IDs outside its literal subject span found in the query; lexical proxy, not inferred relation semantics",
            "relation_template_overlap_stop200": "same after top-200 removal; empty reference gets zero; fallback relation template is the whole support prompt if no literal subject span",
        },
        "negative_populations": {
            "locality": "every source locality prompt against its item's own prompt; zsRE locals are generally NQ unrelated questions, not asserted relation near-neighbours",
            "other_prompt": "ALL ordered distinct-item prompt pairs within each pool, excluding only self; no negative subsampling",
            "other_prompt_identity_caveat": "different item ID is not proof of different canonical fact/subject; source hash and IDs allow later review",
        },
        "roc_policy": {
            "positive": "paraphrase; higher score predicts positive",
            "ties": "exact empirical score ties receive half credit in AUC; threshold uses score >= threshold",
            "weighting": "query-weighted and separately item-balanced (each item contributes one unit to each populated class)",
            "uncertainty": "descriptive development ROC only; pair observations share source items and are not independent; no naive pair-count confidence intervals",
        },
        "pools": reports,
        "gpu_seconds": 0,
        "model_loaded": False,
        "teacher_executed": False,
        "wall_seconds": time.monotonic() - started,
        "recommendation_status": "see task record for a two-feature recommendation based on this fixed analysis",
    }
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("source changed during analysis: " + path)
    payload = (
        json.dumps(result, indent=1, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    )
    with output.open("x") as f:
        f.write(payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "wall_seconds": result["wall_seconds"],
                "counts": {k: v["query_counts"] for k, v in reports.items()},
            }
        ),
        flush=True,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository report required")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    analyze(args.output)


if __name__ == "__main__":
    main()
