"""Retention must release the memory monitor's storage budget."""
import json

from scripts.process_memory_monitor import Recorder


def test_deleted_closed_segments_release_budget(tmp_path):
    header = {"boot_id": "test-boot", "session": "test-session"}
    sample = {"type": "sample", "identities": [], "processes": [], "padding": "x" * 2048}
    writer = Recorder(tmp_path, header, segment_bytes=1, max_bytes=100000, min_free_bytes=0)
    try:
        writer.write_sample(sample)
        first = sorted(tmp_path.glob("memory-*.jsonl"))[0]
        writer.write_sample(sample)
        writer.max_bytes = writer.total + 128
        first.unlink()  # Simulate the authorized retention job on a disposable fixture.
        writer.write_sample(sample)
        assert len(list(tmp_path.glob("memory-*.jsonl"))) == 2
        assert writer.total == sum(path.stat().st_size for path in tmp_path.glob("memory-*.jsonl"))
        assert writer.total <= writer.max_bytes
    finally:
        writer.close()


def test_previous_segments_remain_independently_readable(tmp_path):
    writer = Recorder(tmp_path, {"boot_id": "boot", "session": "session"}, 1, 100000, 0)
    try:
        writer.write_sample({"type": "sample", "identities": [], "processes": []})
        first = next(tmp_path.glob("memory-*.jsonl"))
        before = first.read_bytes()
        writer.write_sample({"type": "sample", "identities": [], "processes": []})
        assert first.read_bytes() == before
        assert json.loads(before.splitlines()[0])["type"] == "header"
    finally:
        writer.close()
