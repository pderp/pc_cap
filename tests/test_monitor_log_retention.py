"""Real logrotate expiry tests using disposable fixtures, never host logs."""

from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "monitor_log_retention.py"
SPEC = importlib.util.spec_from_file_location("monitor_log_retention", MODULE)
retention = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retention)


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="monitor-retention-", dir="/home/derp/cap/assets"
        )
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.logs = self.root / "logs"
        self.now = time.time_ns()
        for name in retention.FAMILIES:
            (self.logs / name).mkdir(parents=True)

    def log(self, family, name, age):
        path = self.logs / family / name
        with path.open("x") as stream:
            stream.write("synthetic log\n")
        stamp = self.now - int(age * 3.6e12)
        os.utime(path, ns=(stamp, stamp))
        return path

    def plan(self, opened=()):
        return retention.plan_expiry(self.logs, now_ns=self.now, opened=opened)

    def test_48_hour_boundary_for_both_log_families(self):
        old = self.log("sysmon", "sysmon-20260101.log", 49)
        new = self.log("sysmon", "sysmon-20260102.log", 47)
        exact = self.log("process_memory", "memory-exact.jsonl", 48)
        expired = self.log("process_memory", "memory-old.jsonl", 48.01)
        plan = self.plan()
        self.assertEqual({row["path"] for row in plan["eligible"]}, {str(old), str(expired)})
        self.assertEqual({row["path"] for row in plan["kept"]}, {str(new), str(exact)})

    def test_open_old_file_symlink_hardlink_and_unrelated_report_are_protected(self):
        path = self.log("process_memory", "memory-open.jsonl", 100)
        outside = self.root / "report.md"
        outside.write_text("report")
        link = self.logs / "process_memory/memory-link.jsonl"
        link.symlink_to(outside)
        hard = self.log("process_memory", "memory-hard.jsonl", 100)
        os.link(hard, self.root / "other-link")
        note = self.logs / "sysmon/acceptance.md"
        note.write_text("keep")
        info = path.stat()
        plan = self.plan({(info.st_dev, info.st_ino)})
        self.assertFalse(plan["eligible"])
        self.assertEqual(
            {row["reason"] for row in plan["kept"]},
            {"open_file", "not_a_regular_file", "foreign_owner_or_hardlink"},
        )
        self.assertTrue(note.exists())

    def test_descriptor_scan_identifies_an_open_regular_file(self):
        path = self.log("process_memory", "memory-open.jsonl", 100)
        with path.open():
            opened, _ = retention.open_log_inodes()
            info = path.stat()
            self.assertIn((info.st_dev, info.st_ino), opened)

    def test_changed_file_is_rechecked_before_rotation(self):
        path = self.log("sysmon", "sysmon-20260101.log", 50)
        plan = self.plan()
        os.utime(path, ns=(self.now, self.now))
        result = retention.perform(plan, self.root / "changed", apply=True)
        self.assertEqual(result["selected"], 0)
        self.assertTrue(path.exists())

    def test_dry_run_never_deletes(self):
        path = self.log("process_memory", "memory-old.jsonl", 50)
        result = retention.perform(self.plan(), self.root / "dry")
        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(result["selected"], 1)
        self.assertEqual(result["deleted"], [])
        self.assertTrue(path.exists())

    @unittest.skipUnless(shutil.which("logrotate"), "logrotate executable required")
    def test_real_logrotate_deletes_only_expired_closed_logs_and_keeps_no_archives(self):
        old = self.log("sysmon", "sysmon-20260101.log", 50)
        memory = self.log("process_memory", "memory-old.jsonl", 50)
        recent = self.log("process_memory", "memory-new.jsonl", 1)
        result = retention.perform(self.plan(), self.root / "real", apply=True)
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(result["logrotate_returncode"], 0)
        self.assertEqual(set(result["deleted"]), {str(old), str(memory)})
        self.assertFalse(old.exists())
        self.assertFalse(memory.exists())
        self.assertFalse(list(self.logs.rglob("*.1")))
        self.assertTrue(recent.exists())

    def test_config_refuses_glob_and_newline_injection(self):
        for path in ("/tmp/*.log", '/tmp/a"\npostrotate\necho bad'):
            with self.assertRaises(ValueError):
                retention.configuration([{"path": path}])


if __name__ == "__main__":
    unittest.main()
