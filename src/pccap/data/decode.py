"""Reference greedy decoder and complete-answer scoring (S0-09; PDF E.2, D.8, PC-7, PC-8).

* greedy, at most 32 new tokens, stop at newline (198) or EOS (50256);
* **full prefix recompute, no KV cache**: every step calls ``predict(ids)`` on the whole prefix;
  a cap applies its writes only at the current prediction position inside ``predict``;
* read-only: ``predict`` must not mutate learner state; when ``state_hash`` is given the hash is
  asserted unchanged after decoding (PC-8);
* the decoder has **no answer argument** (the hidden answer is unreachable from the decode path);
* scoring: the text before the terminator, normalized (NFKC, casefold, whitespace collapse, trim)
  is matched exactly against the aliases; truncation (no terminator within 32 tokens) is a
  failure unless the complete accepted answer was already emitted under the same stopping rule;
* teacher-forced NLL of the gold answer is reported alongside (diagnostic, never a substitute).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

import numpy as np

from pccap.contracts import Metric, metric
from pccap.data.tokenize import EOS_ID, MAX_ANSWER_TOKENS, NEWLINE_ID, GPT2Tokenizer
from pccap.metrics.editing import exact_match_aliases, normalize_answer

PredictFn = Callable[[np.ndarray], np.ndarray]  # ids [T] -> logits [T, V] (or [V] for the last position)


@dataclass
class DecodeResult:
    new_ids: np.ndarray
    text: str  # decoded new tokens, terminator excluded
    stopped_by: str  # "newline" | "eos" | "max"
    truncated: bool
    steps: int
    logprobs: list[float] = field(default_factory=list)


def _last_logits(out) -> np.ndarray:
    a = np.asarray(out)
    return a[-1] if a.ndim == 2 else a


def greedy_decode(predict: PredictFn, prompt_ids: np.ndarray, tok: GPT2Tokenizer, max_new: int = MAX_ANSWER_TOKENS,
                  state_hash: Callable[[], str] | None = None) -> DecodeResult:
    before = state_hash() if state_hash else None
    ids = np.asarray(prompt_ids, np.int32).reshape(-1)
    new: list[int] = []
    lps: list[float] = []
    stopped = "max"
    for _ in range(max_new):
        logits = _last_logits(predict(ids)).astype(np.float64)
        nxt = int(np.argmax(logits))  # ties -> smallest id (np.argmax semantics)
        m = logits.max()
        lps.append(float(logits[nxt] - (m + np.log(np.exp(logits - m).sum()))))
        new.append(nxt)
        ids = np.concatenate([ids, np.int32([nxt])])
        if nxt == NEWLINE_ID:
            stopped = "newline"
            break
        if nxt == EOS_ID:
            stopped = "eos"
            break
    if state_hash and state_hash() != before:
        raise RuntimeError("decode mutated learner state (PC-8 violation)")
    body = [t for t in new if t not in (NEWLINE_ID, EOS_ID)] if stopped != "max" else new
    text = tok.decode(body)
    return DecodeResult(np.asarray(new, np.int32), text, stopped, stopped == "max", len(new), lps)


def score_generation(result: DecodeResult, aliases: Iterable[str]) -> Metric:
    """ES/GS-style exact match of the complete generated answer (PC-7)."""
    return exact_match_aliases(result.text, list(aliases), truncated=result.truncated)


def teacher_forced_nll(predict_full: PredictFn, prompt_ids: np.ndarray, answer_ids: np.ndarray) -> Metric:
    """Sum of −log p(y_t | x, y_<t) over the answer tokens (incl. the terminator) from one forward."""
    ids = np.concatenate([np.asarray(prompt_ids, np.int32), np.asarray(answer_ids, np.int32)])
    logits = np.asarray(predict_full(ids), np.float64)
    n_p = len(prompt_ids)
    total = 0.0
    for t, y in enumerate(np.asarray(answer_ids)):
        row = logits[n_p + t - 1]
        m = row.max()
        total += float(m + np.log(np.exp(row - m).sum()) - row[int(y)])
    return metric(total, units="nats", numerator=total, denominator=len(answer_ids), n=len(answer_ids))


def canonical(text: str) -> str:
    return normalize_answer(text)
