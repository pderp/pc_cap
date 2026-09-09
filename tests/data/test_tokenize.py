"""S0-09: tokenization helper round-trip and the 32-token exclusion."""

import numpy as np
import pytest

from pccap.data.tokenize import MAX_ANSWER_TOKENS, NEWLINE_ID, GPT2Tokenizer, count_exclusions, tokenize_pair


@pytest.fixture(scope="module")
def tok():
    return GPT2Tokenizer()


def test_round_trip_and_newline(tok):
    t = tokenize_pair(tok, "The capital of France is", "Paris")
    assert t.sep == " " and t.answer_text == " Paris\n" and not t.excluded
    assert t.answer_ids[-1] == NEWLINE_ID and tok.decode(t.answer_ids) == " Paris\n"
    assert tok.decode(np.concatenate([t.prompt_ids, t.answer_ids])) == "The capital of France is Paris\n"
    t2 = tokenize_pair(tok, "Q: who? A: ", "Paris")
    assert t2.sep == "" and t2.answer_text == "Paris\n"


def test_exclusion_counted(tok):
    long_answer = " ".join(["antidisestablishmentarianism"] * 8)
    t = tokenize_pair(tok, "Say it:", long_answer)
    assert t.excluded and t.reason.startswith("answer_tokens>") and len(t.answer_ids) > MAX_ANSWER_TOKENS
    c = count_exclusions(tok, [("p", "Paris"), ("p", long_answer), ("p", "  ")])
    assert c == {"n": 3, "excluded_length": 1, "excluded_empty": 1, "kept": 1}


def test_answer_tokenized_separately(tok):
    # the answer's tokens do not depend on the prompt text (boundary is fixed by the helper)
    a = tokenize_pair(tok, "Alpha beta gamma", "Illinois Institute of Technology").answer_ids
    b = tokenize_pair(tok, "Completely different prompt", "Illinois Institute of Technology").answer_ids
    assert np.array_equal(a, b)
