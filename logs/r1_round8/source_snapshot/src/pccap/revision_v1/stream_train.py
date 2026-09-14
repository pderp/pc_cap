"""Stream-scale training episodes for the learned reader (R1-50; recovery plan M1/M2 in docs/R1_stage2_notes.md).

A FeatureBank holds, for every pool item, the write-free observations the trainer needs (key/code features, answer-prefix
features for the own prompt and each paraphrase, locality-prompt features with cap-off logits). Building it is the only
GPU cost; afterwards an episode with a memory of 64–128 records and its queries is assembled by indexing. Episode
populations mirror deployment: memory = random pool items; queries = own prompts and paraphrases of IN-memory records
(answer targets), locality near-neighbour prompts of in-memory records (null targets, the streams' LS population) and
prompts of OUT-of-memory facts (null targets). Labels live only in the EpisodeFeatures targets the outer loop uses.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.revision_v1.contracts import RevisionCost
from pccap.revision_v1.observations import answer_mask, observation_from_pass, prompt_mask
from pccap.revision_v1.reader import ReaderConfig, obs_arrays
from pccap.revision_v1.train import EpisodeFeatures, PrefixFeat, QueryFeat, SupportFeat


@dataclass
class ItemFeatures:
    item_id: str
    fact_id: str
    key_last: np.ndarray
    key_span: np.ndarray
    code_last: np.ndarray
    code_span: np.ndarray
    prompt_ids: np.ndarray
    answer_ids: np.ndarray
    own: list[PrefixFeat]  # own prompt answer prefixes
    paraphrases: list[tuple[np.ndarray, np.ndarray, list[PrefixFeat]]]  # (last, span, answer prefixes) per paraphrase
    locality: list[tuple[np.ndarray, np.ndarray, PrefixFeat]]  # (last, span, prefix with cap-off logits) per locality prompt
    subject: str = ""


BUILDER_VERSION = 2  # bump when build_bank's observation recipe changes


@dataclass
class FeatureBank:
    items: list[ItemFeatures]
    dataset: str
    cost: RevisionCost = field(default_factory=lambda: RevisionCost(phase="learning"))
    identity: dict = field(default_factory=dict)  # R50-06: pool content hash, ordered item/token hash, base checksum, encoder version/taps, builder version, limits, logits dtype

    def by_id(self) -> dict[str, ItemFeatures]:
        return {it.item_id: it for it in self.items}

    def content_hash(self) -> str:
        h = hashlib.sha256()
        for it in self.items:
            h.update(it.item_id.encode())
            h.update(np.asarray(it.prompt_ids, np.int32).tobytes())
            h.update(np.asarray(it.answer_ids, np.int32).tobytes())
        return h.hexdigest()


def bank_identity(rows: list[dict], base_hash: str, encoder_version: int, taps, max_paraphrases: int, max_locality: int, logits_dtype) -> dict:
    pool = hashlib.sha256(json.dumps([(r["item_id"], r["prompt_ids"], r["answer_ids"]) for r in rows], sort_keys=True).encode()).hexdigest()
    return {"pool_content_sha256": pool, "n_items": len(rows), "base_checksum": base_hash, "encoder_version": int(encoder_version), "taps": list(taps),
            "builder_version": BUILDER_VERSION, "max_paraphrases": max_paraphrases, "max_locality": max_locality, "logits_dtype": np.dtype(logits_dtype).name}


def verify_bank(bank: "FeatureBank", expected: dict) -> None:
    """Refuse a cached bank whose recorded identity differs from the requested one (R50-06)."""
    got = bank.identity
    for k, v in expected.items():
        if got.get(k) != v:
            raise ValueError(f"cached bank identity mismatch on {k!r}: cached {got.get(k)!r} != requested {v!r}")


def build_bank(base, enc, rows: list[dict], rc: ReaderConfig, tok: GPT2Tokenizer | None = None, max_paraphrases: int = 2,
               max_locality: int = 2, logits_dtype=np.float16, progress=None) -> FeatureBank:
    """One write-free pass per prefix; cap-off logits (last row) kept only for locality prompts (preservation KL)."""
    tok = tok or GPT2Tokenizer()
    cost = RevisionCost(phase="learning")

    def observe(ids, mask=None, want_logits=False):
        fr = base.forward(ids, (), retain_sites=True, phase="learning", last_only=True)
        cost.add(fr.cost)
        cost.extra_pass_forwards += 1
        obs = observation_from_pass(fr, ids, mask, enc.base_hash, enc.encoder_version, rc.taps)
        last, span = obs_arrays(obs, rc)
        return np.asarray(last), np.asarray(span), (np.asarray(fr.logits).astype(logits_dtype) if want_logits else None)

    def answer_prefixes(prompt: np.ndarray, answer: np.ndarray) -> list[PrefixFeat]:
        out, cur = [], prompt
        for y in answer:
            last, span, _ = observe(cur, prompt_mask(len(prompt), len(cur)))
            T = g.bucket_len(len(cur))
            out.append(PrefixFeat(ids=g.pad_ids(cur, T), n=len(cur), target=int(y), last=last, span=span, capoff_logits=None))
            cur = np.concatenate([cur, np.int32([int(y)])])
        return out

    items = []
    for i, row in enumerate(rows):
        prompt = np.asarray(row["prompt_ids"], np.int32)
        answer = np.asarray(row["answer_ids"], np.int32)
        k_last, k_span, _ = observe(prompt)
        full = np.concatenate([prompt, answer])
        c_last, c_span, _ = observe(full, answer_mask(len(prompt), len(full)))
        own = answer_prefixes(prompt, answer)
        paras = []
        for p_text in row.get("paraphrases", [])[:max_paraphrases]:
            pair = tokenize_pair(tok, p_text, row["answer"])
            p_ids = np.asarray(pair.prompt_ids, np.int32)
            p_last, p_span, _ = observe(p_ids)
            paras.append((p_last, p_span, answer_prefixes(p_ids, np.asarray(pair.answer_ids, np.int32))))
        locs = []
        for l_text in row.get("locality_prompts", [])[:max_locality]:
            l_ids = np.asarray(tok.encode(l_text), np.int32)
            l_last, l_span, cl = observe(l_ids, None, want_logits=True)
            T = g.bucket_len(len(l_ids))
            locs.append((l_last, l_span, PrefixFeat(ids=g.pad_ids(l_ids, T), n=len(l_ids), target=-1, last=l_last, span=l_span, capoff_logits=cl)))
        items.append(ItemFeatures(item_id=row["item_id"], fact_id=row.get("fact_id", row["item_id"]), key_last=k_last, key_span=k_span, code_last=c_last, code_span=c_span,
                                  prompt_ids=prompt, answer_ids=answer, own=own, paraphrases=paras, locality=locs, subject=row.get("subject", "")))
        if progress and (i + 1) % progress == 0:
            print(f"bank {i + 1}/{len(rows)}", flush=True)
    ident = bank_identity(rows, enc.base_hash, enc.encoder_version, rc.taps, max_paraphrases, max_locality, logits_dtype)
    return FeatureBank(items=items, dataset=rows[0].get("dataset", "") if rows else "", cost=cost, identity=ident)


def stream_episode(bank: FeatureBank, rng: np.random.Generator, n_memory: int = 64, n_query_records: int = 8, n_out: int = 8,
                   pool_indices: list[int] | None = None, episode_id: str = "") -> EpisodeFeatures:
    """Memory of ``n_memory`` items; queries from ``n_query_records`` of them (own prompt, one paraphrase, one locality
    null each) and from ``n_out`` out-of-memory items (prompt as null)."""
    idx = np.asarray(pool_indices if pool_indices is not None else np.arange(len(bank.items)))
    perm = rng.permutation(idx)
    mem, out = perm[:n_memory], perm[n_memory : n_memory + n_out]
    supports, queries = [], []
    for i in mem:
        it = bank.items[int(i)]
        supports.append(SupportFeat(record_id=it.item_id, fact_id=it.fact_id, last=it.key_last, span=it.key_span, code_last=it.code_last, code_span=it.code_span, prompt_ids=it.prompt_ids))
    q_records = rng.choice(len(mem), size=min(n_query_records, len(mem)), replace=False)
    for j in q_records:
        it = bank.items[int(mem[j])]
        queries.append(QueryFeat(query_id=f"own:{it.item_id}", role="own_prompt", last=it.key_last, span=it.key_span, prefixes=it.own, target_record=int(j), query_ids=it.prompt_ids))
        if it.paraphrases:
            p_last, p_span, prefs = it.paraphrases[int(rng.integers(len(it.paraphrases)))]
            queries.append(QueryFeat(query_id=f"para:{it.item_id}", role="new_paraphrase", last=p_last, span=p_span, prefixes=prefs, target_record=int(j), query_ids=prefs[0].ids[: prefs[0].n]))
        if it.locality:
            l_last, l_span, lpf = it.locality[int(rng.integers(len(it.locality)))]
            queries.append(QueryFeat(query_id=f"loc:{it.item_id}", role="unrelated", last=l_last, span=l_span, prefixes=[lpf], target_record=-1, query_ids=lpf.ids[: lpf.n]))
    for i in out:
        it = bank.items[int(i)]
        # an out-of-memory fact's prompt: nothing in memory applies (L2 null target only; no stored cap-off logits)
        lpf = PrefixFeat(ids=it.own[0].ids, n=it.own[0].n, target=-1, last=it.key_last, span=it.key_span, capoff_logits=None)
        queries.append(QueryFeat(query_id=f"out:{it.item_id}", role="unrelated_no_kl", last=it.key_last, span=it.key_span, prefixes=[lpf], target_record=-1, query_ids=it.prompt_ids))
    return EpisodeFeatures(episode_id=episode_id or f"stream-{rng.integers(1 << 31)}", supports=supports, queries=queries)


def merge_banks(banks: list[FeatureBank]) -> FeatureBank:
    """Concatenate banks from several pools (mixed-domain training); item ids stay unique per pool naming."""
    items = [it for b in banks for it in b.items]
    cost = RevisionCost(phase="learning")
    for b in banks:
        cost.add(b.cost)
    return FeatureBank(items=items, dataset="+".join(sorted({b.dataset for b in banks})), cost=cost)


def stream_episode_mixed(banks_idx: list[list[int]], bank: FeatureBank, rng: np.random.Generator, n_memory: int = 64, n_query_records: int = 8, n_out: int = 8,
                         episode_id: str = "") -> EpisodeFeatures:
    """Memory drawn from every pool in proportion to its size (so each domain's own prompts, paraphrases, locality nulls and
    out-of-memory nulls appear in every episode); queries as in ``stream_episode``."""
    sizes = np.asarray([len(ix) for ix in banks_idx], float)
    share = sizes / sizes.sum()
    total = n_memory + n_out
    counts = [max(2, int(np.floor(total * sh))) for sh in share]  # R50-04: at least two items per domain
    while sum(counts) < total:
        counts[int(np.argmax(share))] += 1
    while sum(counts) > total:
        counts[int(np.argmax(counts))] -= 1
    picked = []
    for ix, k in zip(banks_idx, counts):
        picked.extend(rng.permutation(np.asarray(ix))[:k].tolist())
    picked = rng.permutation(np.asarray(picked)).tolist()
    ep = stream_episode(bank, rng, n_memory=n_memory, n_query_records=n_query_records, n_out=n_out, pool_indices=picked, episode_id=episode_id)
    # R50-04: guarantee every domain contributes at least one query record (own prompt + paraphrase + locality null)
    mem_ids = {s_.record_id for s_ in ep.supports}
    queried = {q.query_id.split(":", 1)[1] for q in ep.queries if q.role in ("own_prompt",)}
    for ix in banks_idx:
        dom_items = [bank.items[i] for i in ix if bank.items[i].item_id in mem_ids]
        if dom_items and not any(it.item_id in queried for it in dom_items):
            it = dom_items[int(rng.integers(len(dom_items)))]
            j = [s_.record_id for s_ in ep.supports].index(it.item_id)
            ep.queries.append(QueryFeat(query_id=f"own:{it.item_id}", role="own_prompt", last=it.key_last, span=it.key_span, prefixes=it.own, target_record=j, query_ids=it.prompt_ids))
            if it.paraphrases:
                p_last, p_span, prefs = it.paraphrases[0]
                ep.queries.append(QueryFeat(query_id=f"para:{it.item_id}", role="new_paraphrase", last=p_last, span=p_span, prefixes=prefs, target_record=j, query_ids=prefs[0].ids[: prefs[0].n]))
            if it.locality:
                l_last, l_span, lpf = it.locality[0]
                ep.queries.append(QueryFeat(query_id=f"loc:{it.item_id}", role="unrelated", last=l_last, span=l_span, prefixes=[lpf], target_record=-1, query_ids=lpf.ids[: lpf.n]))
    return ep


@dataclass
class TextNull:
    """An ordinary-text prefix used as a null-target query (R1-54): features plus cap-off logits for the preservation KL."""

    text_id: str
    ids: np.ndarray
    last: np.ndarray
    span: np.ndarray
    prefix: PrefixFeat


def build_text_bank(base, enc, tokens: np.ndarray, rc: ReaderConfig, n_windows: int = 512, window: int = 128, prefix_lengths=(16, 48, 96),
                    seed: int = 0, logits_dtype=np.float16) -> list[TextNull]:
    """Ordinary-text null population from a pinned token array (training range only): random windows, several prefix lengths,
    one write-free pass each with the cap-off logits kept (float16, declared approximation)."""
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, len(tokens) - window, size=n_windows)
    out = []
    for s0 in starts:
        win = np.asarray(tokens[int(s0) : int(s0) + window], np.int32)
        for L in prefix_lengths:
            ids = win[:L]
            fr = base.forward(ids, (), retain_sites=True, phase="learning", last_only=True)
            obs = observation_from_pass(fr, ids, None, enc.base_hash, enc.encoder_version, rc.taps)
            last, span = obs_arrays(obs, rc)
            T = g.bucket_len(len(ids))
            pf = PrefixFeat(ids=g.pad_ids(ids, T), n=len(ids), target=-1, last=np.asarray(last), span=np.asarray(span), capoff_logits=np.asarray(fr.logits).astype(logits_dtype))
            out.append(TextNull(text_id=f"text:{int(s0)}:{L}", ids=ids, last=np.asarray(last), span=np.asarray(span), prefix=pf))
    return out


def add_text_nulls(ep: EpisodeFeatures, text_bank: list[TextNull], rng: np.random.Generator, n_text: int = 8) -> EpisodeFeatures:
    """Append ``n_text`` ordinary-text null queries (role 'unrelated': L2 null target + L3 preservation KL) to an episode."""
    if not text_bank or n_text <= 0:
        return ep
    for i in rng.choice(len(text_bank), size=min(n_text, len(text_bank)), replace=False):
        t = text_bank[int(i)]
        ep.queries.append(QueryFeat(query_id=t.text_id, role="unrelated", last=t.last, span=t.span, prefixes=[t.prefix], target_record=-1, query_ids=t.ids))
    return ep
