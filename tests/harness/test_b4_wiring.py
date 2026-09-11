"""B4 wiring (DEC-020): the batched decoder and the evaluator hand learners that key their retrieval at the original
prompt's last position (``decode_key_positions``) that boundary at every step; other learners are untouched."""

import hashlib
from types import SimpleNamespace

import numpy as np

from pccap.contracts import EditItem
from pccap.data.decode import greedy_decode_batch
from pccap.harness.runs import Evaluator


class _BoundaryLearner:
    """Records the key positions it is given; predicts token 5 then newline (198)."""

    decode_key_positions = True

    def __init__(self, vocab=300):
        self.vocab, self.calls = vocab, []

    def last_logits_batch(self, seqs, phase="query", key_positions=None):
        self.calls.append((tuple(len(s) for s in seqs), None if key_positions is None else tuple(key_positions)))
        out = np.zeros((len(seqs), self.vocab), np.float32)
        for i, s in enumerate(seqs):
            out[i, 5 if len(s) <= 3 else 198] = 9.0
        return out

    def state_hash(self):
        return "fixed"


class _PlainLearner(_BoundaryLearner):
    decode_key_positions = False


def _tok():
    return SimpleNamespace(encode=lambda s: [1, 2], decode=lambda ids: "a")


def test_decoder_passes_original_prompt_boundary_only_to_boundary_learners():
    prompts = [np.asarray([1, 2, 3], np.int32), np.asarray([4, 5], np.int32)]
    b = _BoundaryLearner()
    res = greedy_decode_batch(b, prompts, _tok(), max_new=3)
    assert [r.stopped_by for r in res] == ["newline", "newline"]
    # every step carries the ORIGINAL boundaries (len(prompt) - 1) even as the sequences grow
    assert b.calls[0] == ((2, 3), (1, 2)) and b.calls[1][1] == (1, 2) and b.calls[1][0] == (3, 4)
    p = _PlainLearner()
    greedy_decode_batch(p, prompts, _tok(), max_new=3)
    assert all(kp is None for _, kp in p.calls)


def test_evaluator_passes_prompt_boundaries_for_teacher_forced_prefixes():
    b = _BoundaryLearner()
    ev = Evaluator(SimpleNamespace(), _tok(), [], None)
    item = EditItem(item_id="i", digest=hashlib.sha256(b"i").digest()[:16], prompt="p", answer="a", aliases=["a"], paraphrases=[], locality_prompts=[],
                    prompt_ids=np.asarray([1, 2, 3], np.int32), answer_ids=np.asarray([5, 198], np.int32))
    out = ev.items(b, [item])
    assert out[0]["es"] == 1.0
    nll_calls = [c for c in b.calls if c[0] == (3, 4)]  # the two teacher-forced prefixes (prompt, prompt+first answer token)
    assert nll_calls and nll_calls[-1][1] == (2, 2)  # both keyed at the original prompt boundary
