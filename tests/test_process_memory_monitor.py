"""CPU-only tests for durable memory evidence and per-process attribution."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "process_memory_monitor.py"
SPEC = importlib.util.spec_from_file_location("process_memory_monitor", MODULE)
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)


class ProcessMemoryTests(unittest.TestCase):
    def setUp(self):
        # Fixtures are disposable resources; source, logs, and reports stay in pc_cap.
        root = Path("/home/derp/cap/assets")
        self.temp = tempfile.TemporaryDirectory(prefix="process-memory-test-", dir=root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proc, self.cgroups = self.root / "proc", self.root / "cgroups"
        self.proc.mkdir()
        self.cgroups.mkdir()
        (self.proc / "meminfo").write_text(
            "MemTotal: 8192000 kB\nMemAvailable: 1048576 kB\nSwapTotal: 1000 kB\nSwapFree: 100 kB\n"
        )
        (self.proc / "vmstat").write_text("oom_kill 2\npgmajfault 10\npswpout 15\n")
        (self.proc / "pressure").mkdir()
        for name in ("memory", "io", "cpu"):
            (self.proc / "pressure" / name).write_text(
                "some avg10=2.00 avg60=0.00 avg300=0.00 total=42\n"
                "full avg10=1.50 avg60=0.00 avg300=0.00 total=10\n"
            )
        self.logs = self.root / "logs"
        self.header = {"boot_id": "old-boot", "session": "test"}
        self.process(123, 10, 1024)

    def process(self, pid, ticks, rss, name="python (worker)"):
        directory = self.proc / str(pid)
        directory.mkdir(exist_ok=True)
        fields = ["S", "1"] + ["0"] * 17 + [str(ticks)]
        fields[9] = "8"
        (directory / "stat").write_text(f"{pid} ({name}) " + " ".join(fields))
        (directory / "status").write_text(
            f"Name:\t{name}\nUid:\t1001 1001 1001 1001\nVmRSS:\t{rss} kB\n"
            f"VmHWM:\t{rss + 10} kB\nVmSwap:\t100 kB\nRssAnon:\t{rss} kB\n"
            "RssFile:\t0 kB\nRssShmem:\t0 kB\nVmSize:\t99999 kB\nThreads:\t4\n"
        )
        (directory / "cmdline").write_bytes(
            b"python\0scripts/r1_50_stream_train.py\0--tag\0tri6\0--token\0secret-value\0"
        )
        (directory / "cgroup").write_text("0::/test.scope\n")

    def sample(self, seconds):
        value = monitor.collect(self.proc, self.cgroups)
        value["monotonic_ns"] = int(seconds * 1e9)
        value["timestamp"] = f"2026-09-15T00:{int(seconds // 60):02d}:{int(seconds % 60):02d}+00:00"
        return value

    def writer(self, segment=10**7, budget=10**8):
        return monitor.Recorder(self.logs, self.header, segment, budget, 0)

    def test_parse_stat_handles_spaces_parentheses_and_start_identity(self):
        stat = (self.proc / "123/stat").read_text()
        self.assertEqual(monitor.parse_stat(stat), (10, 1, 8, "python (worker)"))

    def test_collect_process_units_pressure_and_no_secret_arguments(self):
        sample = self.sample(60)
        self.assertEqual(
            sample["processes"][0], [123, 10, 1024, 1034, 100, 1024, 0, 0, 99999, 4, 8]
        )
        self.assertEqual(sample["identities"][0]["uid"], 1001)
        self.assertIn("r1_50_stream_train.py --tag tri6", sample["identities"][0]["command"])
        self.assertNotIn("secret-value", json.dumps(sample))
        self.assertEqual(len(sample["alerts"]), 3)
        self.assertEqual(sample["coverage"]["sampled"], 1)
        self.assertIsNone(sample["identities"][0]["executable"])

    def test_inline_python_is_not_logged_and_module_is_identified(self):
        self.assertEqual(
            monitor.command_label("python\0-c\0password='secret'\0", "?"), "python <inline Python>"
        )
        self.assertEqual(
            monitor.command_label("python\0-m\0pccap.train\0--seed=4\0", "?"),
            "python -m pccap.train --seed=4",
        )

    def test_missing_memory_field_is_null_not_zero(self):
        path = self.proc / "123/status"
        path.write_text("Name: python\nUid: 1001\nThreads: 1\n")
        self.assertIsNone(self.sample(0)["processes"][0][2])

    def test_disappearing_unreadable_and_reused_pids_are_counted(self):
        original = monitor.read_text

        def denied(path, limit=65536):
            if path == self.proc / "123/status":
                raise PermissionError("denied")
            return original(path, limit)

        with patch.object(monitor, "read_text", side_effect=denied):
            sample = self.sample(0)
            self.assertEqual(sample["coverage"]["unreadable"], 1)
            self.assertFalse(sample["processes"])
        with patch.object(monitor, "parse_stat", side_effect=[(10, 1, 8, "x"), (11, 1, 0, "x")]):
            self.assertEqual(self.sample(0)["coverage"]["raced"], 1)
        (self.proc / "999").mkdir()
        self.assertEqual(self.sample(0)["coverage"]["raced"], 1)

    def test_cgroup_limits_events_and_path_escape(self):
        group = self.cgroups / "test.scope"
        group.mkdir()
        (group / "memory.current").write_text("1048576\n")
        (group / "memory.max").write_text("max\n")
        (group / "memory.events").write_text("high 3\noom_kill 1\n")
        result = self.sample(0)["cgroups"][0]
        self.assertEqual(result["memory.current"], 1048576)
        self.assertEqual(result["memory.max"], "max")
        self.assertEqual(result["memory.events"]["oom_kill"], 1)
        self.assertIsNone(monitor.cgroup_memory(self.cgroups, "/../../outside"))

    def test_exclusive_singleton_and_no_previous_segment_modification(self):
        writer = self.writer()
        try:
            with self.assertRaises(BlockingIOError):
                self.writer()
            writer.write_sample(self.sample(60))
            path = next(self.logs.glob("memory-*.jsonl"))
            old = path.read_bytes()
        finally:
            writer.close()
        later = self.writer()
        try:
            later.write_sample(self.sample(120))
        finally:
            later.close()
        self.assertEqual(path.read_bytes(), old)
        self.assertEqual(len(list(self.logs.glob("memory-*.jsonl"))), 2)

    def test_fsync_per_sample_and_rotation_repeats_all_identities(self):
        writer = self.writer(segment=1)
        try:
            with patch.object(monitor.os, "fsync", wraps=monitor.os.fsync) as fsync:
                writer.write_sample(self.sample(60))
                writer.write_sample(self.sample(120))
                self.assertEqual(fsync.call_count, 6)  # header, directory, sample each segment
        finally:
            writer.close()
        for path in self.logs.glob("memory-*.jsonl"):
            records = list(monitor.iter_records(path, {}))
            self.assertEqual(len(records[1]["identities"]), 1)

    def test_storage_budget_and_free_space_fail_closed(self):
        writer = self.writer(budget=1)
        try:
            with self.assertRaises(monitor.StorageLimitError):
                writer.write_sample(self.sample(0))
            self.assertFalse(list(self.logs.glob("memory-*.jsonl")))
        finally:
            writer.close()
        writer = self.writer()
        try:
            with patch.object(
                monitor.shutil, "disk_usage", return_value=type("Disk", (), {"free": 0})()
            ):
                with self.assertRaises(monitor.StorageLimitError):
                    writer.write_sample(self.sample(0))
        finally:
            writer.close()

    def test_growth_pid_reuse_and_identity_deltas_report(self):
        with patch.object(monitor.time, "monotonic_ns", return_value=0):
            writer = self.writer()
            try:
                writer.write_sample(self.sample(60))
                self.process(123, 10, 3072)
                writer.write_sample(self.sample(120))
                self.process(123, 11, 512)
                writer.write_sample(self.sample(180))
            finally:
                writer.close()
        records = list(monitor.iter_records(next(self.logs.glob("memory-*.jsonl")), {}))
        self.assertEqual(records[2]["identities"], [])
        report = monitor.build_report(self.logs, "previous", 300, 10, "new-boot")
        self.assertIn("123/10 | 3.0 | 1.0→3.0 | +2.0", report)
        self.assertIn("123/11 | 0.5 | 0.5→0.5 | n/a", report)
        self.assertIn("r1_50_stream_train.py --tag tri6", report)

    def test_torn_final_record_and_header_and_malformed_middle(self):
        with patch.object(monitor.time, "monotonic_ns", return_value=0):
            writer = self.writer()
            try:
                writer.write_sample(self.sample(60))
            finally:
                writer.close()
        source = next(self.logs.glob("memory-*.jsonl"))
        damaged = self.root / "damaged"
        damaged.mkdir()
        (damaged / "memory-1.jsonl").write_bytes(
            source.read_bytes() + b"{bad-json}\n" + b'{"type":"sample","monotonic_ns":'
        )
        (damaged / "memory-2.jsonl").write_bytes(b'{"type":"header"')
        report = monitor.build_report(damaged, "latest", 300, 10, "old-boot")
        self.assertIn("1 samples", report)
        self.assertIn('"incomplete_lines": 1', report)
        self.assertIn('"incomplete_headers": 1', report)
        self.assertIn('"malformed_lines": 1', report)

    def test_window_boot_choice_and_out_of_window_identity(self):
        with patch.object(monitor.time, "monotonic_ns", return_value=0):
            writer = self.writer()
            try:
                writer.write_sample(self.sample(60))
                writer.write_sample(self.sample(120))
            finally:
                writer.close()
        report = monitor.build_report(self.logs, "latest", 30, 10, "old-boot")
        self.assertIn("1 samples", report)
        self.assertIn("r1_50_stream_train.py", report)
        with self.assertRaisesRegex(ValueError, "no previous recorded boot"):
            monitor.build_report(self.logs, "previous", 30, 10, "old-boot")


if __name__ == "__main__":
    unittest.main()
