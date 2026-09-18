"""RSS attribution must handle PID reuse, missing argv and incomplete telemetry."""

import json

import pytest
from scripts import r1_58i_host_peaks as host


def sample(t, pid=7, ticks=10, rss=1024):
    return dict(unix_time=t, rss_kib=rss, hwm_kib=2048, timestamp=f"2026-09-17T00:00:{t:02d}+00:00")


def group(samples):
    return dict(
        identity=dict(pid=7, start_ticks=10, command="python -m scripts.r1_73d_locality_recipes"),
        boot_id="boot",
        samples=samples,
    )


def test_unique_temporal_match_keeps_sampled_peak_distinct_from_hwm():
    index = dict(
        processes={"boot:7:10": group([sample(t, rss=1000 + t) for t in [1, 11, 21, 31, 41]])}
    )
    r = host.match_monitor(dict(start=0, end=42), index)
    assert r["method"] == "monitor_temporal_match"
    assert r["measured_peak_host_mib"] == 1041 / 1024
    assert r["observed_hwm_mib"] == 2 and not r["attribution_reviewed"]
    index["processes"]["boot:7:99"] = group([sample(22)])
    assert host.match_monitor(dict(start=0, end=42), index)["method"] == "unavailable"


def test_gap_and_short_coverage_refuse():
    for times in ([1], [1, 61, 91], [1, 11]):
        r = host.match_monitor(
            dict(start=0, end=100), dict(processes={"p": group([sample(t) for t in times])})
        )
        assert r["method"] == "unavailable"


def test_bounded_log_snapshot_and_pid_reuse(tmp_path):
    p = tmp_path / "memory.jsonl"
    header = dict(
        type="header", boot_id="boot", process_columns=["pid", "start_ticks", "rss_kib", "hwm_kib"]
    )
    lines = [header]
    for t, ticks in [(1, 10), (11, 10), (21, 99)]:
        lines.append(
            dict(
                type="sample",
                timestamp=sample(t)["timestamp"],
                identities=[
                    dict(
                        pid=7,
                        start_ticks=ticks,
                        command="python -m scripts.r1_64c_comparator_recipes",
                    )
                ],
                processes=[[7, ticks, 1024, 2048]],
            )
        )
    raw = "".join(json.dumps(r) + "\n" for r in lines)
    p.write_text(raw + '{"partial":')
    index = host.monitor_index([p])
    assert len(index["processes"]) == 2
    assert index["segments"][0]["prefix_bytes"] == len(raw.encode())
    assert index["issues"][0]["reason"] == "incomplete live tail omitted"
    assert p.read_text() == raw + '{"partial":'


def test_direct_time_requires_exact_successful_command(tmp_path):
    recipe = dict(path=str(tmp_path / "recipe.json"), sha256="a" * 64)
    result = dict(manifest_sha256="a" * 64)
    p = tmp_path / "time.txt"
    text = f'Command being timed: "python -m scripts.r1_68c_dev_cell --manifest {recipe["path"]} --manifest-sha256 {recipe["sha256"]} --execute"\nMaximum resident set size (kbytes): 4096\nExit status: 0\n'
    p.write_text(text)
    assert host.direct_time(p, recipe, result)["measured_peak_host_mib"] == 4
    for bad in (
        text.replace("Exit status: 0", "Exit status: 1"),
        text.replace("a" * 64, "b" * 64),
        text.replace(" --execute", ""),
    ):
        p.write_text(bad)
        with pytest.raises(ValueError):
            host.direct_time(p, recipe, result)


def test_missing_phase_clock_and_unknown_driver_refuse(tmp_path):
    p = tmp_path / "result.json"
    p.write_text("{}")
    with pytest.raises(ValueError, match="timing window missing"):
        host.attempt_window(p, {})
    assert not host.driver_command("python -m scripts.r1_64f_full_endpoints")
    assert not host.driver_command("python -m scripts.r1_73d_locality_recipes_fake")
    assert host.driver_command("/path/python -m scripts.r1_73d_locality_recipes")
