"""Full PC-10 gate; run explicitly on CPU after the source fixture is available."""
import pytest

from pccap.baselines.grace_parity import run


@pytest.mark.slow
def test_pc10_twenty_isolated_and_sequential_cases():
    report = run()
    assert report["status"] == "pass", (
        "PC-10 parity failure; inspect individual codebook and evaluation differences. "
        "Do not widen tolerances or register B4 on output agreement alone."
    )
