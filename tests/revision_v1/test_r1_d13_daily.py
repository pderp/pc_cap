"""Synthetic queue/watch and saved monitor records, without GPU/service access."""

import json
from datetime import UTC, datetime

import pytest
from scripts import r1_d13_daily as daily

from tests.revision_v1 import test_r1_d12_reprice as fixtures

scenario = fixtures.scenario
validated_v4 = fixtures.validated_v4
finish_block = fixtures.finish_block

NOW = datetime(2026, 9, 18, 15, tzinfo=UTC)


def monitors(root, *, stamp="2026-09-18T14:59:50+00:00", available=7000, gpu=True, boot="test-boot"):
    memdir, sysdir = root / "memory", root / "sysmon"
    memdir.mkdir(parents=True)
    sysdir.mkdir()
    header = dict(type="header", schema=1, process_columns=daily.memory.COLUMNS, boot_id=boot)
    sample = dict(type="sample", timestamp=stamp,
                  host=dict(meminfo_kib=dict(MemAvailable=available * 1024, MemTotal=32768 * 1024,
                                            SwapTotal=4096 * 1024, SwapFree=3000 * 1024), psi={}),
                  processes=[[42, 100, 2000, 3000, 10, 1, 2, 3, 4, 1, 0],
                             [10, 19, None, None, None, None, None, None, None, 1, 0]],
                  alerts=[], coverage={})
    path = memdir / "memory-test.jsonl"
    path.write_text(json.dumps(header) + "\n" + json.dumps(sample) + "\n")
    line = "2026-09-18T10:59:50 load=0 0 0 gpu[util%,memMB,totMB,C,W,MHz,throttle,pstate]="
    line += "25 8000 12227 65 100 2000 0x0 P0" if gpu else "no_response"
    line += " gpu_procs=42,8000; top_cpu=x top_rss=x kmsg=\n"
    (sysdir / "sysmon-20260918.log").write_text(line)
    return dict(memory_dir=memdir, sysmon_dir=sysdir, now=NOW, boot_id="test-boot")


def test_health_units_timezone_line_binding_and_partial_tail(tmp_path):
    opts = monitors(tmp_path)
    path = opts["memory_dir"] / "memory-test.jsonl"
    with path.open("a") as f:
        f.write('{"type":"sample"')
    h = daily.health(**opts)
    assert h["memory"]["status"] == h["gpu"]["status"] == "fresh"
    assert h["memory"]["age_seconds"] == h["gpu"]["age_seconds"] == 10
    assert h["memory"]["mem_available_mib"] == 7000
    assert h["memory"]["top_rss"][0]["pid"] == 42
    assert h["memory"]["rss_unavailable_processes"] == 1
    assert h["memory"]["read_issues"]
    b = h["memory"]["source"]
    with path.open("rb") as f:
        f.seek(b["offset"])
        assert daily.hashlib.sha256(f.read(b["bytes"])).hexdigest() == b["line_sha256"]
    assert h["gpu"]["memory_used_mib"] == 8000


@pytest.mark.parametrize("params,status", [
    ({"stamp":"2026-09-18T14:00:00+00:00"}, "stale"),
    ({"stamp":"2026-09-18T15:01:00+00:00"}, "future_timestamp"),
    ({"boot":"old-boot"}, "different_boot"),
])
def test_never_label_stale_or_previous_boot_current(tmp_path, params, status):
    h = daily.health(**monitors(tmp_path, **params))
    assert h["memory"]["status"] == status


def test_low_memory_and_missing_gpu_not_clearance(tmp_path):
    h = daily.health(**monitors(tmp_path, available=6000, gpu=False))
    assert h["memory"]["below_launch_floor"]
    assert h["gpu"]["status"] == "unavailable" and h["gpu"]["read_issues"]
    missing = daily.health(tmp_path / "absent", tmp_path / "absent", now=NOW, boot_id="test")
    assert missing["memory"]["status"] == missing["gpu"]["status"] == "unavailable"


def test_daily_delta_is_since_generation_not_delivery(scenario):
    f = scenario
    opts = monitors(f["root"] / "monitors")
    args = dict(receipt_root=f["receipts"], journal=f["journal"], **opts)
    f["process"](0)
    f["observe"](0)
    first = daily.build(f["mp"], **args)
    b = daily.emit(first, f["root"] / "daily1")
    assert first["d11"]["watch"]["new_queue_observations"] == 1
    f["process"](1)
    f["observe"](1, kl=0.006)
    second = daily.build(f["mp"], previous_run=b["path"], **args)
    assert second["d11"]["watch"]["new_queue_observations"] == 1
    assert len(second["d11"]["watch"]["entries"]) == 1
    assert second["d11"]["watch"]["alerts"]
    assert "since previous generated daily report" in daily.text(second)
    assert not second["posted"] and not second["launch_authorized"]
    daily.emit(second, f["root"] / "daily2")
    unchanged = daily.build(f["mp"], previous_run=f["root"] / "daily2/daily.json", **args)
    assert unchanged["d11"]["watch"]["new_observations"] == 0


def test_live_process_keeps_unknown_cost_unavailable(scenario):
    f = scenario
    f["process"](0, finish=False)
    report = daily.build(f["mp"], receipt_root=f["receipts"], journal=f["journal"],
                         **monitors(f["root"] / "monitors"))
    assert report["d11"]["issues"]
    assert report["d11"]["inventory"]["cost"]["projected_total_hours"] is None


def test_boundary_chains_one_snapshot_and_refuses_later_live_worker(scenario):
    f = scenario
    finish_block(f)
    opts = monitors(f["root"] / "monitors")
    args = dict(receipt_root=f["receipts"], journal=f["journal"], cost_receipt=f["cp"],
                boundary_block=1, synthetic=True,
                memory_dir=opts["memory_dir"], sysmon_dir=opts["sysmon_dir"])
    result = daily.boundary(f["mp"], output_dir=f["root"] / "boundary1", **args)
    plan = daily.d12.read_ref(result["plan"])
    assert plan["d11"]["boundary_ready"] and not plan["lead_approved"]
    assert (f["root"] / "boundary1/operations-text.txt").exists()
    f["process"](2, finish=False)
    with pytest.raises(ValueError, match="idle"):
        daily.boundary(f["mp"], output_dir=f["root"] / "must-not-create", **args)
    assert not (f["root"] / "must-not-create").exists()


def test_changed_watch_cannot_be_published(scenario):
    f = scenario
    opts = monitors(f["root"] / "monitors")
    r = daily.build(f["mp"], receipt_root=f["receipts"], journal=f["journal"], **opts)
    f["observe"](0)
    with pytest.raises(ValueError, match="snapshot"):
        daily.emit(r, f["root"] / "must-not-exist")
    assert not (f["root"] / "must-not-exist").exists()
