"""One tested tokenization helper for prompt/answer boundaries (S0-09; PDF E.2).

Convention (recorded here and in every manifest that uses it):

* the GPT-2 tokenizer from the pinned snapshot (``tokenizer.json``), no special tokens added;
* the prompt is tokenized alone;
* the canonical answer text is ``sep + answer.strip() + "\\n"`` where ``sep`` is one space unless
  the prompt already ends with whitespace (GPT-2 BPE marks word starts with a leading space),
  tokenized **separately** from the prompt; the terminating newline is token 198 and is part of
  the target sequence ``y_1..y_M``;
* the helper asserts ``decode(answer_ids) == sep + answer + "\\n"`` and excludes (and counts)
  answers whose token count with the delimiter exceeds ``MAX_ANSWER_TOKENS = 32``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from pccap.bases.gpt2_jax import DEFAULT_SNAPSHOT

MAX_ANSWER_TOKENS = 32
NEWLINE_ID = 198
EOS_ID = 50256


class GPT2Tokenizer:
    def __init__(self, snapshot: Path = DEFAULT_SNAPSHOT):
        from tokenizers import Tokenizer

        self.path = Path(snapshot) / "tokenizer.json"
        self.tok = Tokenizer.from_file(str(self.path))
        assert self.tok.encode("\n").ids == [NEWLINE_ID]
        assert self.tok.token_to_id("<|endoftext|>") == EOS_ID

    def file_sha256(self) -> str:
        """Identity of the tokenizer file (compared with the frozen ``tokenizer_rev`` at confirm-mode stage entry, V2-01)."""
        import hashlib

        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def encode(self, text: str) -> np.ndarray:
        return np.asarray(self.tok.encode(text, add_special_tokens=False).ids, dtype=np.int32)

    def decode(self, ids) -> str:
        return self.tok.decode([int(i) for i in np.asarray(ids).reshape(-1)], skip_special_tokens=False)


@dataclass(frozen=True)
class TokenizedEdit:
    prompt_ids: np.ndarray
    answer_ids: np.ndarray  # includes the terminating newline
    answer_text: str  # sep + answer + "\n" exactly as decoded
    sep: str
    excluded: bool
    reason: str = ""


def tokenize_pair(tok: GPT2Tokenizer, prompt: str, answer: str, max_answer_tokens: int = MAX_ANSWER_TOKENS) -> TokenizedEdit:
    sep = "" if (prompt and prompt[-1].isspace()) else " "
    ans = answer.strip()
    text = sep + ans + "\n"
    prompt_ids = tok.encode(prompt)
    answer_ids = tok.encode(text)
    back = tok.decode(answer_ids)
    if back != text:
        raise ValueError(f"answer does not round-trip: {text!r} -> {back!r}")
    if not ans:
        return TokenizedEdit(prompt_ids, answer_ids, text, sep, True, "empty_answer")
    if len(answer_ids) > max_answer_tokens:
        return TokenizedEdit(prompt_ids, answer_ids, text, sep, True, f"answer_tokens>{max_answer_tokens}")
    return TokenizedEdit(prompt_ids, answer_ids, text, sep, False)


def count_exclusions(tok: GPT2Tokenizer, pairs: list[tuple[str, str]]) -> dict:
    out = {"n": len(pairs), "excluded_length": 0, "excluded_empty": 0, "kept": 0}
    for p, a in pairs:
        t = tokenize_pair(tok, p, a)
        if t.excluded:
            out["excluded_length" if t.reason.startswith("answer_tokens") else "excluded_empty"] += 1
        else:
            out["kept"] += 1
    return out
