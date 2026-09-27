"""The GPU-occupancy guard blocks on project compute processes only; desktop CUDA contexts are reported, not blocking."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from aw.pc_v0 import blocking_cuda_processes  # noqa: E402


def test_own_python_process_blocks_and_init_does_not():
    apps = [{"pid": str(os.getpid()), "used_memory": "10 MiB"}, {"pid": "1", "used_memory": "5 MiB"},
            {"pid": "999999999", "used_memory": "1 MiB"}]
    blocking = blocking_cuda_processes(apps)
    assert [b["pid"] for b in blocking] == [str(os.getpid())]  # this interpreter counts; pid 1 and a dead pid do not
    assert "cmdline" in blocking[0]


def test_empty():
    assert blocking_cuda_processes([]) == []
