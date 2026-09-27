"""Fresh CPU evidence for tests that verify the current runner's source hashes."""

from uuid import uuid4

import pytest


@pytest.fixture(scope="session")
def pc_v0_smoke():
    from aw.pc_v0_smoke import ROOT, generate

    # run_stream keeps reports under the repo and checkpoint bytes under assets.
    # The existing .pytest_cache ignore rule covers these disposable test reports.
    return generate(ROOT / "results/additional_work/PC-v0/.pytest_cache" / uuid4().hex)
