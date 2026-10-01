"""Shared reporting caveat and prose-only refresh of historical publications."""
from pathlib import Path

SCALE = 'The base is GPT-2 small (124M parameters); transfer of these findings to production-scale models has not been established.'
SCOPE = 'DEC-074b left S1_literal CounterFact and the original optional extension unavailable. The later supplemental Option R study is separate; its stable-v0 class is deferred under DEC-080.'
PARAGRAPH = SCALE + ' ' + SCOPE


def refresh(document, marker):
    """Keep the saved numerical tables and figure decoration byte-for-byte intact."""
    document = Path(document)
    before = document.read_text()
    if PARAGRAPH in before:
        return
    if before.count(marker) != 1:
        raise ValueError('ambiguous limitations insertion point')
    after = before.replace(marker, marker + '\n\n' + PARAGRAPH, 1)
    if after.replace('\n\n' + PARAGRAPH, '', 1) != before:
        raise ValueError('refresh would change existing text')
    if document.read_text() != before:
        raise ValueError('publication changed concurrently')
    document.write_text(after)
