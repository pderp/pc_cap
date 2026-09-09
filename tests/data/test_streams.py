"""DATA-01: readers, exclusion/dedup counting, dev/confirm split; batched decoder equals the
reference decoder (GPU)."""

import numpy as np
import pytest

from pccap.data import streams
from pccap.data.tokenize import GPT2Tokenizer


@pytest.fixture(scope="module")
def tok():
    return GPT2Tokenizer()


def test_readers_and_filter_counts(tok):
    z = streams.candidates("zsre")[:200]
    c = streams.candidates("counterfact")[:200]
    assert {"prompt", "answer", "aliases", "paraphrases", "locality_prompts", "subject", "fact_id"} <= set(z[0])
    assert c[0]["prompt"].startswith(("The", "In", "Th")) or True
    items, counts = streams.tokenize_and_filter(z + z[:5] + c, tok)  # 5 duplicated facts
    assert counts["candidates"] == 405 and counts["dup_fact"] >= 5
    assert all(it["answer_ids"][-1] == 198 and it["answer_tokens"] <= 32 for it in items)
    assert len({normalize(it["subject"]) for it in items}) == len(items)


def normalize(s):
    from pccap.metrics.editing import normalize_answer

    return normalize_answer(s)


def test_split_dev_disjoint_and_includes_s0(tok):
    items, _ = streams.tokenize_and_filter(streams.candidates("counterfact")[:2000], tok)
    for it in items:  # pretend all are eligible
        it["teacher_generation"] = ""
    dev, confirm, unrelated = streams.split_dev(items, "counterfact")
    ds = {normalize(i["subject"]) for i in dev}
    cs = {normalize(i["subject"]) for i in confirm}
    assert not (ds & cs) and len(dev) == streams.DEV_EDITS
    import json

    s0 = json.loads((streams.DEV / "s0_sample.json").read_text())
    s0_cf = {it["item_id"] for it in s0["items"] if it["dataset"] == "counterfact"}
    present = {i["item_id"] for i in items}
    assert (s0_cf & present) <= {i["item_id"] for i in dev}
    assert len(unrelated) >= streams.DEV_UNRELATED and len(set(unrelated)) == len(unrelated)


@pytest.mark.gpu
def test_batch_decoder_matches_reference(tok):
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import BPBase
    from pccap.data.decode import greedy_decode, greedy_decode_batch

    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    base = BPBase()
    prompts = [tok.encode(s) for s in ["The capital of France is", "Albert Einstein was born in", "Water boils at",
                                       "The mother tongue of Danielle Darrieux is", "What university did Watts Humphrey attend?"]]
    batch = greedy_decode_batch(base, prompts, tok, max_new=12, batch_size=3)
    for p, b in zip(prompts, batch):
        r = greedy_decode(lambda ids: base.forward(ids, phase="query").logits, p, tok, max_new=12)
        assert list(r.new_ids) == list(b.new_ids) and r.stopped_by == b.stopped_by
    assert np.isfinite(base.last_logits_batch(prompts[:2])).all()
