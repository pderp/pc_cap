"""Occupancy classification uses commands, independent of PID namespaces."""

from pathlib import Path

from aw.pc_v0 import blocking_cuda_processes


def test_project_and_python_block_but_desktop_and_vanished_do_not(monkeypatch):
    commands = {
        "10": b"/usr/bin/python3\0train.py\0",
        "11": b"/home/derp/cap/assets/native-compute\0",
        "12": b"/usr/bin/gnome-shell\0",
    }

    def cmdline(path):
        if path.parent.name not in commands:
            raise FileNotFoundError(path)
        return commands[path.parent.name]

    monkeypatch.setattr(Path, "read_bytes", cmdline)
    apps = [{"pid": pid, "used_memory": "10 MiB"} for pid in ("10", "11", "12", "13")]
    blocking = blocking_cuda_processes(apps)
    assert [b["pid"] for b in blocking] == ["10", "11"]
    assert "cmdline" in blocking[0]


def test_empty():
    assert blocking_cuda_processes([]) == []
