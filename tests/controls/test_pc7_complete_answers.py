"""PC-7 (PDF F.5, E.2): complete answers — a wrong second token fails ES; teacher-forced success
does not override free-generation failure; terminators and truncation follow the common policy."""

import numpy as np

from pccap.data.decode import DecodeResult, greedy_decode, score_generation, teacher_forced_nll
from pccap.data.tokenize import EOS_ID, NEWLINE_ID, GPT2Tokenizer

V = 50257


def _predict_from_table(table):
    """table: list of [V] score rows indexed by generation step; also used teacher-forced."""

    def predict(ids):
        step = len(ids) - table["prompt_len"]
        if step < len(table["rows"]):
            return table["rows"][step]
        return np.zeros(V, np.float32)

    return predict


def test_wrong_second_token_fails_es():
    tok = GPT2Tokenizer()
    gold = tok.encode(" New York\n")  # [968, 1971, 198]
    prompt = tok.encode("The big apple is")
    rows = []
    for t, y in enumerate(gold):
        r = np.zeros(V, np.float32)
        r[int(y)] = 5.0
        if t == 1:  # second token: gold still gets probability but a different token wins greedy
            r[int(y)] = 3.0
            r[6342] = 4.0  # " Paris"
        rows.append(r)
    table = {"prompt_len": len(prompt), "rows": rows}
    dec = greedy_decode(_predict_from_table(table), prompt, tok)
    assert dec.text == " New Paris" and dec.stopped_by == "newline"
    es = score_generation(dec, ["New York"])
    assert es["value"] == 0.0 and es["status"] == "ok"
    # teacher-forced NLL is finite/small-ish but does NOT override the free-generation failure
    nll = teacher_forced_nll(_predict_from_table(table), prompt, gold)
    assert nll["status"] == "ok" and nll["value"] < 20
    assert es["value"] == 0.0


def test_terminators_and_truncation():
    ok = DecodeResult(np.array([6342, NEWLINE_ID]), " Paris", "newline", False, 2)
    assert score_generation(ok, ["Paris"])["value"] == 1.0
    eos = DecodeResult(np.array([6342, EOS_ID]), " Paris", "eos", False, 2)
    assert score_generation(eos, ["Paris"])["value"] == 1.0
    # truncated without terminator, the full accepted answer already emitted -> not a failure
    trunc_ok = DecodeResult(np.array([6342] * 32), " Paris", "max", True, 32)
    assert score_generation(trunc_ok, ["Paris"])["value"] == 1.0
    # truncated and the text is only a prefix of the answer -> failure
    trunc_bad = DecodeResult(np.array([968] * 32), " New", "max", True, 32)
    assert score_generation(trunc_bad, ["New York"])["value"] == 0.0
    # partial-token prefixes are never accepted
    partial = DecodeResult(np.array([1]), " Pari", "newline", False, 1)
    assert score_generation(partial, ["Paris"])["value"] == 0.0
