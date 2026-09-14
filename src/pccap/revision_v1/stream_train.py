"""Stream-scale training episodes for the learned reader (R1-50; recovery plan M1/M2 in docs/R1_stage2_notes.md).

A FeatureBank holds, for every pool item, the write-free observations the trainer needs (key/code features, answer-prefix
features for the own prompt and each paraphrase, locality-prompt features with cap-off logits). Building it is the only
GPU cost; afterwards an episode with a memory of 64–128 records and its queries is assembled by indexing. Episode
populations mirror deployment: memory = random pool items; queries = own prompts and paraphrases of IN-memory records
(answer targets), locality near-neighbour prompts of in-memory records (null targets, the streams' LS population) and
prompts of OUT-of-memory facts (null targets). Labels live only in the EpisodeFeatures targets the outer loop uses.
"""

from __future__ import annotations

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


@dataclass
class FeatureBank:
    items: list[ItemFeatures]
    dataset: str
    cost: RevisionCost = field(default_factory=lambda: RevisionCost(phase="learning"))

    def by_id(self) -> dict[str, ItemFeatures]:
        return {it.item_id: it for it in self.items}


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
    return FeatureBank(items=items, dataset=rows[0].get("dataset", "") if rows else "", cost=cost)


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
        supports.append(SupportFeat(record_id=it.item_id, fact_id=it.fact_id, last=it.key_last, span=it.key_span, code_last=it.code_last, code_span=it.code_span))
    q_records = rng.choice(len(mem), size=min(n_query_records, len(mem)), replace=False)
    for j in q_records:
        it = bank.items[int(mem[j])]
        queries.append(QueryFeat(query_id=f"own:{it.item_id}", role="own_prompt", last=it.key_last, span=it.key_span, prefixes=it.own, target_record=int(j)))
        if it.paraphrases:
            p_last, p_span, prefs = it.paraphrases[int(rng.integers(len(it.paraphrases)))]
            queries.append(QueryFeat(query_id=f"para:{it.item_id}", role="new_paraphrase", last=p_last, span=p_span, prefixes=prefs, target_record=int(j)))
        if it.locality:
            l_last, l_span, lpf = it.locality[int(rng.integers(len(it.locality)))]
            queries.append(QueryFeat(query_id=f"loc:{it.item_id}", role="unrelated", last=l_last, span=l_span, prefixes=[lpf], target_record=-1))
    for i in out:
        it = bank.items[int(i)]
        # an out-of-memory fact's prompt: nothing in memory applies (L2 null target only; no stored cap-off logits)
        lpf = PrefixFeat(ids=it.own[0].ids, n=it.own[0].n, target=-1, last=it.key_last, span=it.key_span, capoff_logits=None)
        queries.append(QueryFeat(query_id=f"out:{it.item_id}", role="unrelated_no_kl", last=it.key_last, span=it.key_span, prefixes=[lpf], target_record=-1))
    return EpisodeFeatures(episode_id=episode_id or f"stream-{rng.integers(1 << 31)}", supports=supports, queries=queries)
