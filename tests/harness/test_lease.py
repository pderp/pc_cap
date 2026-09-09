"""S0-03: the GPU lease is exclusive and records its holder."""

import json
import multiprocessing as mp
import time

from pccap.harness.lease import current_holder, gpu_lease


def _hold(path, seconds, q):
    with gpu_lease("T-A", stage="S0", projected_seconds=seconds, path=path) as lease:
        q.put(("acquired", time.time(), lease.report["waited_seconds"]))
        time.sleep(seconds)


def test_lease_serializes_holders(tmp_path):
    path = tmp_path / ".gpu_lease"
    q = mp.Queue()
    p = mp.Process(target=_hold, args=(path, 1.0, q))
    p.start()
    q.get(timeout=10)
    time.sleep(0.1)
    holder = current_holder(path)
    assert holder and holder["task"] == "T-A"
    t0 = time.time()
    with gpu_lease("T-B", path=path) as lease:
        waited = time.time() - t0
        assert waited > 0.5, waited
        assert lease.report["waited_seconds"] > 0.5
        assert json.loads(path.read_text())["task"] == "T-B"
    p.join()
    assert current_holder(path) is None
