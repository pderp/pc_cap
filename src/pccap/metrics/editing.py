"""Complete-answer scoring, never teacher-forced token scoring (PDF E.2/D.8)."""

import unicodedata
from collections.abc import Iterable

from pccap.contracts import Metric, metric


def normalize_answer(text: str) -> str:
    """NFKC -> casefold -> whitespace collapse -> trim; preserve answer content."""
    if not isinstance(text, str):
        raise TypeError("answer must be text")
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def exact_match_aliases(generated: str, aliases: Iterable[str], *, truncated=False) -> Metric:
    """Score text preceding a newline terminator against complete aliases.

    EOS must already be removed by the decoder. Reaching the token limit is
    successful only if the whole accepted alias was emitted, per E.2. The
    function consumes text only: no target loss can override generated failure.
    """
    if not isinstance(generated, str):
        raise TypeError("generated answer must be text")
    if isinstance(aliases, str):
        raise TypeError("aliases must be a collection of answers, not a string")
    normalized = sorted({normalize_answer(a) for a in aliases})
    if not normalized or any(not a for a in normalized):
        raise ValueError("at least one nonempty answer alias is required")
    answer = normalize_answer(generated.split("\n", 1)[0])
    success = answer in normalized
    return metric(
        int(success),
        units="accuracy_fraction",
        numerator=int(success),
        denominator=1,
        n=1,
        strata={
            "truncated": bool(truncated),
            "terminated_newline": "\n" in generated,
            "complete_answer_match": success,
        },
    )
