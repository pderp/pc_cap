"""Regressions for process titles rewritten into argv[0]."""

import pytest
from scripts.process_memory_monitor import command_label


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("chrome --token secret-value\0", "chrome"),
        ("python\0-c\0secret-value\0", "python <inline Python>"),
        ("python\0run.py\0--tag\0tri6\0", "python run.py --tag tri6"),
    ],
)
def test_rewritten_title_and_python_labels(raw, expected):
    assert command_label(raw, "fallback") == expected
