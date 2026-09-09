"""LM, probe and property sets with inventory (DATA-04; PDF S1, D.2, D.3, D.8, E.4; SD-1, SD-3).

Documents = WikiText-103 articles delimited by level-1 headings (`` = Title = `` lines, single
``=``); every set is built **by document** and the sets are disjoint by document id.

* ``H``: 2×10⁶ GPT-2 tokens sampled by document from *train* (seed 11) → P1 fidelity.
* ``drift``: the entire *validation* split, tokenized once (247,289 tokens; SD-3 shortfall from
  the PDF's 10⁶ logged, PA-5) → LM drift.
* ``P2``: 4,096 held-out positions = 256 sequences of 128 tokens from H's complement in train
  (seed 12), 16 positions per sequence (positions 8, 16, …, 128) → geometry (D.2).
* ``P3``: 1,000 teacher-forced sequences of 128 tokens from the complement (seed 13), disjoint
  from P2's documents → localization (D.3).
* ``POS``: UD English EWT train (≥ 20,000 tokens) and dev (≥ 5,000) mapped to GPT-2 tokens by
  first-subtoken labelling (each word's UPOS tag is assigned to its first GPT-2 sub-token; the
  remaining sub-tokens are unlabelled and excluded), sentences joined with spaces → probes.
* ``E.4`` natural-language domains: **unsupported** for GPT-2 small this month (no eight-domain
  corpus); the grammar's labelled mechanisms substitute for P4 (PDF E.4 permits this).

Large arrays go to ``assets/data/prepared/lm/`` (``.npy``); ``manifests/dev/lm_sets.json`` holds
document ids, seeds, counts and SHA-256 hashes.  ``python -m pccap.data.lm_sets --build`` /
``--audit``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from pccap import ASSETS_ROOT
from pccap.data.tokenize import GPT2Tokenizer

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(ASSETS_ROOT) / "data" / "raw"
LM = Path(ASSETS_ROOT) / "data" / "prepared" / "lm"
MANIFEST = ROOT / "manifests" / "dev" / "lm_sets.json"
H_TOKENS = 2_000_000
P2_SEQS, P2_LEN, P2_STRIDE = 256, 128, 8
P3_SEQS, P3_LEN = 1000, 128
SEEDS = {"H": 11, "P2": 12, "P3": 13}
UPOS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _is_article_heading(line: str) -> bool:
    s = line.strip()
    return s.startswith("= ") and s.endswith(" =") and not s.startswith("= =")


def documents(split: str) -> list[list[str]]:
    """Group WikiText lines into articles (level-1 heading starts a document)."""
    import pyarrow.parquet as pq

    docs: list[list[str]] = []
    cur: list[str] = []
    for part in sorted((RAW / "wikitext103").glob(f"{split}-*.parquet")):
        for t in pq.read_table(part).column("text").to_pylist():
            if _is_article_heading(t):
                if cur:
                    docs.append(cur)
                cur = [t]
            else:
                cur.append(t)
    if cur:
        docs.append(cur)
    return docs


def tokenize_docs(docs: list[list[str]], tok: GPT2Tokenizer) -> list[np.ndarray]:
    texts = ["".join(d) for d in docs]
    out = []
    B = 512
    for i in range(0, len(texts), B):
        enc = tok.tok.encode_batch(texts[i : i + B], add_special_tokens=False)
        out += [np.asarray(e.ids, np.int32) for e in enc]
    return out


def sample_by_document(doc_tokens: list[np.ndarray], target: int, rng: np.random.Generator, exclude: set[int]) -> tuple[np.ndarray, list[int]]:
    ids = []
    total = 0
    for i in rng.permutation(len(doc_tokens)):
        if int(i) in exclude or len(doc_tokens[i]) == 0:
            continue
        ids.append(int(i))
        total += len(doc_tokens[i])
        if total >= target:
            break
    arr = np.concatenate([doc_tokens[i] for i in ids])[:target]
    return arr, ids


def windows_from_docs(doc_tokens: list[np.ndarray], n_seqs: int, length: int, rng: np.random.Generator, exclude: set[int]) -> tuple[np.ndarray, list[int]]:
    seqs, used = [], []
    for i in rng.permutation(len(doc_tokens)):
        if int(i) in exclude or len(doc_tokens[i]) < length:
            continue
        start = int(rng.integers(0, len(doc_tokens[i]) - length + 1))
        seqs.append(doc_tokens[i][start : start + length])
        used.append(int(i))
        if len(seqs) >= n_seqs:
            break
    return np.stack(seqs), used


def pos_from_conllu(path: Path, tok: GPT2Tokenizer, min_tokens: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Returns (token ids [N], labels [N] (-1 = unlabelled), sentence ids [N], counts)."""
    import conllu

    ids_all, lab_all, sent_all = [], [], []
    n_words = n_labelled = 0
    with open(path, encoding="utf-8") as f:
        for si, sent in enumerate(conllu.parse_incr(f)):
            words = [t for t in sent if isinstance(t["id"], int)]
            text = ""
            spans = []
            for w in words:
                form = w["form"]
                piece = form if (not text or w.get("misc") and text.endswith(" ") is False and False) else form
                sep = "" if not text else " "
                spans.append((len(text) + len(sep), w["upos"]))
                text += sep + piece
            enc = tok.tok.encode(text, add_special_tokens=False)
            offsets = enc.offsets
            starts = {s: u for s, u in spans}
            labels = np.full(len(enc.ids), -1, np.int32)
            for k, (a, _b) in enumerate(offsets):
                # GPT-2 leading-space tokens have offset starting at the space; the word starts one later
                for cand in (a, a + 1):
                    if cand in starts and starts[cand] in UPOS:
                        labels[k] = UPOS.index(starts[cand])
                        del starts[cand]
                        break
            ids_all.append(np.asarray(enc.ids, np.int32))
            lab_all.append(labels)
            sent_all.append(np.full(len(enc.ids), si, np.int32))
            n_words += len(words)
            n_labelled += int((labels >= 0).sum())
            if sum(len(x) for x in ids_all) >= min_tokens and si > 0:
                pass
    ids = np.concatenate(ids_all)
    labs = np.concatenate(lab_all)
    sents = np.concatenate(sent_all)
    return ids, labs, sents, {"words": n_words, "labelled_first_subtokens": n_labelled, "gpt2_tokens": int(len(ids)), "sentences": int(sents.max() + 1)}


def build() -> dict:
    t0 = time.time()
    tok = GPT2Tokenizer()
    LM.mkdir(parents=True, exist_ok=True)
    inv: dict = {"seeds": SEEDS, "document_rule": "WikiText-103 level-1 heading ' = Title = ' starts a document", "files": {}}
    # --- WikiText
    train_docs = documents("train")
    val_docs = documents("validation")
    train_tok = tokenize_docs(train_docs, tok)
    val_tok = tokenize_docs(val_docs, tok)
    inv["wikitext103"] = {"train_documents": len(train_docs), "train_tokens": int(sum(len(t) for t in train_tok)),
                          "validation_documents": len(val_docs), "validation_tokens": int(sum(len(t) for t in val_tok))}
    rng = np.random.default_rng(SEEDS["H"])
    H, h_docs = sample_by_document(train_tok, H_TOKENS, rng, set())
    used = set(h_docs)
    rng = np.random.default_rng(SEEDS["P2"])
    P2, p2_docs = windows_from_docs(train_tok, P2_SEQS, P2_LEN, rng, used)
    used |= set(p2_docs)
    rng = np.random.default_rng(SEEDS["P3"])
    P3, p3_docs = windows_from_docs(train_tok, P3_SEQS, P3_LEN, rng, used)
    drift = np.concatenate([t for t in val_tok if len(t)])
    p2_positions = np.arange(P2_STRIDE, P2_LEN + 1, P2_STRIDE) - 1  # 16 positions: 7, 15, ..., 127
    arrays = {"H_tokens": H, "drift_tokens": drift, "P2_sequences": P2, "P2_positions": p2_positions, "P3_sequences": P3}
    # --- POS
    for split, min_t in (("train", 20000), ("dev", 5000)):
        ids, labs, sents, c = pos_from_conllu(RAW / "ud_ewt" / f"en_ewt-ud-{split}.conllu", tok, min_t)
        arrays[f"POS_{split}_ids"], arrays[f"POS_{split}_labels"], arrays[f"POS_{split}_sentences"] = ids, labs, sents
        inv[f"pos_{split}"] = {**c, "labelling": "first sub-token of each word carries its UPOS tag; others -1", "upos": UPOS,
                               "meets_minimum": c["labelled_first_subtokens"] >= min_t}
    for name, arr in arrays.items():
        p = LM / f"{name}.npy"
        np.save(p, arr)
        inv["files"][name] = {"path": str(p), "shape": list(arr.shape), "dtype": str(arr.dtype), "sha256": _sha(p)}
    inv["sets"] = {
        "H": {"tokens": int(len(H)), "documents": len(h_docs), "doc_ids": h_docs, "split": "train", "purpose": "P1 fidelity (SD-1)"},
        "drift": {"tokens": int(len(drift)), "documents": len(val_docs), "split": "validation", "purpose": "LM drift (D.8)",
                  "shortfall_note": f"PDF asks for 10^6 tokens; the whole validation split has {len(drift)} (SD-3, PA-5); no repetition, test split not used"},
        "P2": {"sequences": int(P2.shape[0]), "length": P2_LEN, "positions_per_sequence": int(len(p2_positions)), "positions_total": int(P2.shape[0] * len(p2_positions)),
               "doc_ids": p2_docs, "purpose": "geometry (D.2): 4,096 held-out positions"},
        "P3": {"sequences": int(P3.shape[0]), "length": P3_LEN, "doc_ids": p3_docs, "purpose": "localization (D.3)"},
        "E4_domains": {"status": "unsupported", "reason": "no eight-domain natural-language corpus for GPT-2 small this month; grammar mechanisms substitute for P4 (PDF E.4)"},
    }
    inv["disjointness"] = {"H_P2": len(set(h_docs) & set(p2_docs)), "H_P3": len(set(h_docs) & set(p3_docs)), "P2_P3": len(set(p2_docs) & set(p3_docs)),
                           "train_validation": "disjoint by split"}
    inv["seconds"] = time.time() - t0
    MANIFEST.write_text(json.dumps(inv, indent=1) + "\n")
    return inv


def audit() -> dict:
    inv = json.loads(MANIFEST.read_text())
    for name, f in inv["files"].items():
        assert _sha(Path(f["path"])) == f["sha256"], name
    d = inv["disjointness"]
    assert d["H_P2"] == 0 and d["H_P3"] == 0 and d["P2_P3"] == 0
    assert inv["sets"]["H"]["tokens"] == H_TOKENS and inv["sets"]["P2"]["positions_total"] == 4096 and inv["sets"]["P3"]["sequences"] == 1000
    assert inv["pos_train"]["meets_minimum"] and inv["pos_dev"]["meets_minimum"]
    return {k: (v if k != "files" else {n: f["shape"] for n, f in v.items()}) for k, v in inv.items() if k != "sets"} | {
        "sets": {k: {kk: vv for kk, vv in v.items() if kk != "doc_ids"} for k, v in inv["sets"].items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args(argv)
    if args.build:
        inv = build()
        print(json.dumps({k: v for k, v in inv.items() if k in ("wikitext103", "pos_train", "pos_dev", "disjointness", "seconds")}, indent=1))
    if args.audit:
        print(json.dumps(audit(), indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
