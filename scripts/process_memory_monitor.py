#!/usr/bin/env python3
"""Low-overhead Linux process memory recorder and post-reboot report (stdlib only).

Every segment is exclusively created, independently readable, and fsynced per sample.
No GPU queries, environment capture, process termination, or log deletion.
See docs/process_memory_monitor.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shutil
import signal
import sys
import time
import uuid
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[1] / "logs" / "process_memory"
COLUMNS = [
    "pid",
    "start_ticks",
    "rss_kib",
    "hwm_kib",
    "swap_kib",
    "anon_kib",
    "file_kib",
    "shmem_kib",
    "virtual_kib",
    "threads",
    "major_faults",
]
STATUS_FIELDS = [
    "VmRSS",
    "VmHWM",
    "VmSwap",
    "RssAnon",
    "RssFile",
    "RssShmem",
    "VmSize",
    "Threads",
]
MEM_FIELDS = {
    "MemTotal",
    "MemFree",
    "MemAvailable",
    "Buffers",
    "Cached",
    "SwapTotal",
    "SwapFree",
    "SwapCached",
    "Shmem",
    "Slab",
    "SReclaimable",
    "SUnreclaim",
    "KernelStack",
    "PageTables",
    "Dirty",
    "Writeback",
    "Unevictable",
    "Mlocked",
}
VM_FIELDS = {"oom_kill", "pgmajfault", "pswpin", "pswpout", "pgscan_kswapd", "pgscan_direct"}
MAX_RECORD = 32 * 1024 * 1024
GIB = 1024**3


class StorageLimitError(OSError):
    """Stop rather than overwrite evidence or fill the disk."""


def read_text(path: Path, limit: int = 65536) -> str:
    with path.open("rb") as stream:
        return stream.read(limit).decode("utf-8", errors="replace")


def optional_text(path: Path, limit: int = 65536) -> str | None:
    try:
        return read_text(path, limit)
    except OSError:
        return None


def numbers(text: str, colon: bool = False) -> dict[str, int]:
    result = {}
    for line in text.splitlines():
        fields = line.replace(":", " ", 1).split() if colon else line.split()
        if len(fields) >= 2:
            try:
                result[fields[0]] = int(fields[1])
            except ValueError:
                continue
    return result


def parse_stat(text: str) -> tuple[int, int, int, str]:
    """Return start ticks, parent PID, major faults and comm; comm may contain ')'."""
    left, right = text.index("("), text.rindex(")")
    fields = text[right + 2 :].split()
    return int(fields[19]), int(fields[1]), int(fields[9]), text[left + 1 : right]


def command_label(raw: str | None, fallback: str) -> str:
    """Identify interpreter jobs without recording arbitrary arguments or inline code."""
    if not raw:
        return fallback
    args = raw.rstrip("\0").split("\0")
    # Some programs rewrite argv[0] to contain their entire process title.
    argument_zero = args[0].split(maxsplit=1)[0] if args[0].strip() else fallback
    label = [argument_zero[:256]]
    executable = Path(argument_zero).name.lower()
    if executable.startswith(("python", "pypy")):
        if "-c" in args:
            label.append("<inline Python>")
        elif "-m" in args:
            index = args.index("-m") + 1
            if index < len(args) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", args[index]):
                label.extend(["-m", args[index][:256]])
        else:
            for arg in args[1:]:
                if arg.endswith((".py", ".pyw")):
                    label.append(arg[:512])
                    break
        for index, arg in enumerate(args[1:], 1):
            flag, equal, value = arg.partition("=")
            if flag in {"--tag", "--run-name", "--run-id", "--seed"}:
                if equal:
                    label.append(flag + "=" + value[:160])
                elif index + 1 < len(args):
                    label.extend([flag, args[index + 1][:160]])
    return " ".join(label)[:1024]


def pressure(path: Path) -> dict | None:
    raw = optional_text(path)
    if raw is None:
        return None
    result = {}
    try:
        for line in raw.splitlines():
            parts = line.split()
            result[parts[0]] = {
                key: int(value) if key == "total" else float(value)
                for key, value in (part.split("=", 1) for part in parts[1:])
            }
    except (ValueError, IndexError):
        return None
    return result


def cgroup_path(raw: str | None) -> str | None:
    if raw is not None:
        for line in raw.splitlines():
            if line.startswith("0::"):
                return line[3:][:2048]
    return None


def cgroup_memory(root: Path, name: str) -> dict | None:
    # A proc cgroup path can contain ".." if the mount and process namespaces differ.
    parts = Path(name).parts
    if not name.startswith("/") or ".." in parts:
        return None
    path = root.joinpath(*parts[1:])
    current = optional_text(path / "memory.current")
    if current is None:
        return None
    result = {"path": name}
    for field in (
        "memory.current",
        "memory.peak",
        "memory.swap.current",
        "memory.high",
        "memory.max",
    ):
        raw = current if field == "memory.current" else optional_text(path / field)
        if raw is not None:
            value = raw.strip()
            if value == "max" or value.isdigit():
                result[field] = value if value == "max" else int(value)
    for field in ("memory.events", "memory.events.local"):
        raw = optional_text(path / field)
        result[field] = numbers(raw) if raw is not None else None
    return result


def collect(proc: Path, cgroup_root: Path, low_available_gib: float = 3.0) -> dict:
    started = time.monotonic_ns()
    mem = numbers(read_text(proc / "meminfo"), colon=True)
    if not {"MemTotal", "MemAvailable"} <= mem.keys():
        raise OSError("proc meminfo lacks MemTotal/MemAvailable; refusing misleading samples")
    vm = optional_text(proc / "vmstat")
    host = {
        "meminfo_kib": {key: value for key, value in mem.items() if key in MEM_FIELDS},
        "vmstat": {key: value for key, value in numbers(vm or "").items() if key in VM_FIELDS},
        "psi": {name: pressure(proc / "pressure" / name) for name in ("memory", "io", "cpu")},
        "loadavg": optional_text(proc / "loadavg", 256),
    }
    identities, rows, groups = [], [], set()
    coverage = {"visible": 0, "sampled": 0, "unreadable": 0, "raced": 0, "malformed": 0}
    for directory in sorted(proc.iterdir(), key=lambda path: path.name):
        if not directory.name.isdigit():
            continue
        coverage["visible"] += 1
        try:
            first = parse_stat(read_text(directory / "stat", 8192))
            status = read_text(directory / "status")
            fields = numbers(status, colon=True)
            raw_command = optional_text(directory / "cmdline", 8192)
            group = cgroup_path(optional_text(directory / "cgroup"))
            try:
                executable = os.readlink(directory / "exe")[:1024]
            except OSError:
                executable = None
            second = parse_stat(read_text(directory / "stat", 8192))
            if first[:2] != second[:2] or first[3] != second[3]:
                coverage["raced"] += 1
                continue
            pid, (ticks, ppid, faults, name) = int(directory.name), second
            rows.append([pid, ticks, *(fields.get(key) for key in STATUS_FIELDS), faults])
            identities.append(
                {
                    "pid": pid,
                    "start_ticks": ticks,
                    "ppid": ppid,
                    "uid": fields.get("Uid"),
                    "name": name,
                    "executable": executable,
                    "command": command_label(raw_command, name),
                    "command_readable": raw_command is not None,
                    "cgroup": group,
                }
            )
            if group:
                groups.add(group)
            coverage["sampled"] += 1
        except FileNotFoundError:
            coverage["raced"] += 1
        except (PermissionError, ProcessLookupError, OSError):
            coverage["unreadable"] += 1
        except (ValueError, IndexError):
            coverage["malformed"] += 1
    alerts = []
    if mem["MemAvailable"] * 1024 < low_available_gib * GIB:
        alerts.append("low_available_memory")
    total, free = mem.get("SwapTotal", 0), mem.get("SwapFree", 0)
    if total and (total - free) / total >= 0.8:
        alerts.append("swap_at_least_80_percent")
    memory_psi = host["psi"]["memory"] or {}
    if memory_psi.get("full", {}).get("avg10", 0) >= 1:
        alerts.append("memory_full_stall_at_least_1_percent")
    cgroups = [
        value
        for group in sorted(groups)
        if (value := cgroup_memory(cgroup_root, group)) is not None
    ]
    return {
        "type": "sample",
        "timestamp": dt.datetime.now(dt.UTC).isoformat(),
        "monotonic_ns": started,
        "host": host,
        "identities": identities,
        "processes": rows,
        "cgroups": cgroups,
        "coverage": coverage,
        "alerts": alerts,
        "collection_ms": (time.monotonic_ns() - started) / 1e6,
    }


def identity_key(value) -> tuple[int, int]:
    return value["pid"], value["start_ticks"]


class Recorder:
    def __init__(
        self, directory: Path, header: dict, segment_bytes: int, max_bytes: int, min_free_bytes: int
    ):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.directory, self.header = directory, header
        self.segment_bytes, self.max_bytes, self.min_free_bytes = (
            segment_bytes,
            max_bytes,
            min_free_bytes,
        )
        self.lock = os.fdopen(
            os.open(directory / ".monitor.lock", os.O_RDWR | os.O_CREAT, 0o600), "rb"
        )
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lock.close()
            raise
        self.total = sum(path.stat().st_size for path in directory.glob("memory-*.jsonl"))
        self.stream, self.known = None, {}
        self.segment_size, self.segment_index = 0, 0

    def check_space(self, count: int):
        if self.total + count > self.max_bytes:
            raise StorageLimitError("log budget reached; archive logs or raise --max-log-gib")
        if shutil.disk_usage(self.directory).free - count < self.min_free_bytes:
            raise StorageLimitError(
                "free disk floor reached; recording stopped to protect disk space"
            )

    def write_raw(self, data: bytes):
        self.check_space(len(data))
        self.stream.write(data)
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.total += len(data)
        self.segment_size += len(data)

    def open_segment(self):
        if self.stream is not None:
            self.stream.close()
        self.known = {}
        self.segment_index += 1
        header = dict(
            self.header,
            type="header",
            schema=1,
            process_columns=COLUMNS,
            segment_monotonic_ns=time.monotonic_ns(),
        )
        data = encode(header)
        self.check_space(len(data))
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        path = (
            self.directory
            / f"memory-{stamp}-{self.header['session']}-{self.segment_index:05d}.jsonl"
        )
        self.stream = os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb")
        self.segment_size = 0
        self.write_raw(data)
        descriptor = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        print(f"recording {path}", flush=True)

    def write_sample(self, sample: dict):
        if self.stream is None or self.segment_size >= self.segment_bytes:
            self.open_segment()
        current = {identity_key(value): value for value in sample["identities"]}
        output = dict(
            sample,
            identities=[value for key, value in current.items() if self.known.get(key) != value],
        )
        self.write_raw(encode(output))
        # Keep only live processes; every new segment starts with complete identities.
        self.known = current

    def close(self):
        try:
            if self.stream is not None:
                self.stream.close()
        finally:
            self.lock.close()


def encode(value: dict) -> bytes:
    data = (
        json.dumps(value, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n"
    ).encode()
    if len(data) > MAX_RECORD:
        raise StorageLimitError("sample exceeds 32 MiB safety limit")
    return data


def iter_records(path: Path, issues: dict):
    with path.open("rb") as stream:
        while raw := stream.readline(MAX_RECORD + 1):
            if len(raw) > MAX_RECORD:
                while raw and not raw.endswith(b"\n"):
                    raw = stream.readline(MAX_RECORD + 1)
                issues["oversize_lines"] = issues.get("oversize_lines", 0) + 1
                continue
            if not raw.endswith(b"\n"):
                issues["incomplete_lines"] = issues.get("incomplete_lines", 0) + 1
                continue
            try:
                record = json.loads(raw)
                if not isinstance(record, dict):
                    raise ValueError("record is not an object")
            except (ValueError, UnicodeError):
                issues["malformed_lines"] = issues.get("malformed_lines", 0) + 1
                continue
            yield record


def catalog(directory: Path, issues: dict) -> list[tuple[Path, dict]]:
    result = []
    for path in sorted(directory.glob("memory-*.jsonl")):
        with path.open("rb") as stream:
            raw = stream.readline(MAX_RECORD + 1)
        if not raw.endswith(b"\n"):
            issues["incomplete_headers"] = issues.get("incomplete_headers", 0) + 1
            continue
        try:
            header = json.loads(raw)
            if header.get("type") != "header" or header.get("schema") != 1:
                raise ValueError("unsupported or absent header")
            if header.get("process_columns") != COLUMNS:
                raise ValueError("unknown process columns")
            if not isinstance(header["segment_monotonic_ns"], int) or not header["boot_id"]:
                raise ValueError("invalid boot/clock")
        except (ValueError, KeyError, AttributeError, UnicodeError) as error:
            raise ValueError(f"unreadable segment header {path}: {error}") from error
        result.append((path, header))
    return result


def build_report(directory: Path, boot: str, window: float, top: int, current_boot: str) -> str:
    issues = {}
    entries = catalog(directory, issues)
    if not entries:
        raise ValueError(f"no memory segments in {directory}")
    boots = list(dict.fromkeys(header["boot_id"] for _, header in entries))
    if boot == "latest":
        selected = boots[-1]
    elif boot == "previous":
        previous = [value for value in boots if value != current_boot]
        if not previous:
            raise ValueError(
                "no previous recorded boot; the monitor cannot reconstruct old process samples"
            )
        selected = previous[-1]
    elif boot == "current":
        selected = current_boot
    else:
        selected = boot
    files = sorted(
        ((path, header) for path, header in entries if header["boot_id"] == selected),
        key=lambda item: item[1]["segment_monotonic_ns"],
    )
    if not files:
        raise ValueError(f"no segments for boot {selected}")
    end = None
    for path, _ in reversed(files):
        # At most one segment per pass is held by the JSON parser, never a whole boot.
        for record in iter_records(path, {}):
            if record.get("type") == "sample":
                value = record.get("monotonic_ns")
                if isinstance(value, int):
                    end = value if end is None else max(end, value)
        if end is not None:
            break
    if end is None:
        raise ValueError("selected boot has no complete samples")
    cutoff = end - int(window * 1e9)
    before = [
        index for index, (_, header) in enumerate(files) if header["segment_monotonic_ns"] < cutoff
    ]
    start_index = before[-1] if before else 0
    stats, timeline = {}, []
    groups, samples, missing, alert_counts = {}, 0, 0, {}
    minimum_available, maximum_swap, maximum_gap = None, 0, 0.0
    first_timestamp, last_timestamp, last_mono, counters_first, counters_last = (
        None,
        None,
        None,
        None,
        None,
    )
    maximum_collection, minimum_coverage, max_memory_psi, max_io_psi = 0.0, 1.0, 0.0, 0.0
    for path, _ in files[start_index:]:
        identities = {}
        for record in iter_records(path, issues):
            if record.get("type") != "sample":
                continue
            try:
                mono = record["monotonic_ns"]
                rows = record["processes"]
                if not isinstance(mono, int) or not isinstance(rows, list):
                    raise ValueError("bad sample")
                for identity in record["identities"]:
                    identities[identity_key(identity)] = identity
                live = {tuple(row[:2]) for row in rows}
                identities = {key: value for key, value in identities.items() if key in live}
                if mono < cutoff or mono > end:
                    continue
                host, stamp = record["host"], record["timestamp"]
                mem, coverage = host["meminfo_kib"], record["coverage"]
                available = mem["MemAvailable"]
                if any(len(row) != len(COLUMNS) for row in rows):
                    raise ValueError("invalid process row")
            except (KeyError, TypeError, ValueError, IndexError):
                issues["invalid_samples"] = issues.get("invalid_samples", 0) + 1
                continue
            samples += 1
            first_timestamp = first_timestamp or stamp
            last_timestamp = stamp
            if last_mono is not None:
                maximum_gap = max(maximum_gap, (mono - last_mono) / 1e9)
            last_mono = mono
            if minimum_available is None or available < minimum_available[0]:
                minimum_available = (available, stamp)
            maximum_swap = max(maximum_swap, mem.get("SwapTotal", 0) - mem.get("SwapFree", 0))
            maximum_collection = max(maximum_collection, record.get("collection_ms", 0))
            minimum_coverage = min(
                minimum_coverage, coverage["sampled"] / max(1, coverage["visible"])
            )
            for alert in record.get("alerts", []):
                alert_counts[alert] = alert_counts.get(alert, 0) + 1
            for name in ("memory", "io"):
                value = ((host["psi"].get(name) or {}).get("full") or {}).get("avg10", 0)
                if name == "memory":
                    max_memory_psi = max(max_memory_psi, value)
                else:
                    max_io_psi = max(max_io_psi, value)
            counters_first = host["vmstat"] if counters_first is None else counters_first
            counters_last = host["vmstat"]
            # Keep a small ending timeline rather than retaining samples.
            timeline.append(
                (
                    stamp,
                    available,
                    mem.get("SwapTotal", 0) - mem.get("SwapFree", 0),
                    coverage["sampled"],
                    coverage["visible"],
                )
            )
            timeline = timeline[-6:]
            for row in rows:
                pid, ticks, rss, _, swap, *_ = row
                key = pid, ticks
                identity = identities.get(key)
                if identity is None:
                    missing += 1
                if rss is None:
                    continue
                if key not in stats:
                    stats[key] = {
                        "first_ns": mono,
                        "last_ns": mono,
                        "first_rss": rss,
                        "last_rss": rss,
                        "peak_rss": rss,
                        "peak_swap": swap,
                        "count": 0,
                        "identity": identity,
                    }
                item = stats[key]
                item.update(last_ns=mono, last_rss=rss, count=item["count"] + 1)
                item["peak_rss"] = max(item["peak_rss"], rss)
                if swap is not None:
                    item["peak_swap"] = max(item["peak_swap"] or 0, swap)
                if identity is not None:
                    item["identity"] = identity
            for group in record.get("cgroups", []):
                name = group["path"]
                item = groups.setdefault(
                    name, {"peak": 0, "first_events": None, "last_events": None}
                )
                item["peak"] = max(item["peak"], group.get("memory.current", 0))
                events = group.get("memory.events")
                if events is not None:
                    if item["first_events"] is None:
                        item["first_events"] = events
                    item["last_events"] = events
    if not samples:
        raise ValueError("no valid samples in selected window")
    lines = [
        f"Process memory report — boot {selected}",
        f"Recorded window: {first_timestamp} to {last_timestamp} ({samples} samples, UTC)",
        f"Requested lookback: {window:g} seconds before this boot's last complete sample.",
        f"Minimum MemAvailable: {minimum_available[0] / 1024:.1f} MiB at {minimum_available[1]}",
        f"Maximum swap used: {maximum_swap / 1024:.1f} MiB",
        f"Maximum PSI full avg10: memory {max_memory_psi:.2f}%, IO {max_io_psi:.2f}%",
        f"Largest observed sample gap: {maximum_gap:.2f} s; collection max {maximum_collection:.2f} ms",
        f"Minimum sampled/visible process coverage: {minimum_coverage:.1%}",
        f"Alerts (sample counts): {json.dumps(alert_counts, sort_keys=True)}",
        f"Log read issues: {json.dumps(issues, sort_keys=True)}; rows missing identity: {missing}",
        "Host counter changes within the observed window: "
        + json.dumps(
            {
                key: counters_last[key] - value
                for key, value in counters_first.items()
                if key in counters_last and counters_last[key] >= value
            },
            sort_keys=True,
        ),
    ]

    def table(title, ranked):
        lines.extend(
            [
                "",
                title,
                "PID/start_ticks | peak RSS MiB | first→last RSS MiB | net MiB/min | peak swap MiB | samples | identity",
            ]
        )
        for key, item in ranked[:top]:
            duration = (item["last_ns"] - item["first_ns"]) / 1e9
            rate = (
                (item["last_rss"] - item["first_rss"]) / 1024 * 60 / duration if duration else None
            )
            identity = item["identity"] or {}
            label = identity.get("command", "?").replace("\n", " ").replace("\r", " ")
            rate_text = f"{rate:+.1f}" if rate is not None else "n/a"
            swap_text = (
                f"{item['peak_swap'] / 1024:.1f}" if item["peak_swap"] is not None else "n/a"
            )
            lines.append(
                f"{key[0]}/{key[1]} | {item['peak_rss'] / 1024:.1f} | "
                f"{item['first_rss'] / 1024:.1f}→{item['last_rss'] / 1024:.1f} | "
                f"{rate_text} | {swap_text} | {item['count']} | {label} "
                f"(ppid={identity.get('ppid')}, uid={identity.get('uid')}, cgroup={identity.get('cgroup')})"
            )

    table(
        "Largest observed resident-memory consumers:",
        sorted(stats.items(), key=lambda pair: pair[1]["peak_rss"], reverse=True),
    )
    table(
        "Largest positive net RSS increases (first to last observation of the same process):",
        sorted(
            (
                (key, item)
                for key, item in stats.items()
                if item["count"] > 1 and item["last_rss"] > item["first_rss"]
            ),
            key=lambda pair: pair[1]["last_rss"] - pair[1]["first_rss"],
            reverse=True,
        ),
    )
    lines.extend(["", "Largest observed cgroup memory.current peaks (MiB; nested groups overlap):"])
    for name, item in sorted(groups.items(), key=lambda pair: pair[1]["peak"], reverse=True)[:top]:
        first, last = item["first_events"], item["last_events"]
        changes = (
            {
                key: last[key] - value
                for key, value in first.items()
                if key in last and last[key] >= value
            }
            if first is not None and last is not None
            else None
        )
        lines.append(f"{item['peak'] / 1024**2:.1f} | {name} | memory.events delta={changes}")
    lines.extend(
        ["", "Last complete samples: UTC | available MiB | swap used MiB | sampled/visible"]
    )
    for stamp, available, swap, sampled, visible in timeline:
        lines.append(f"{stamp} | {available / 1024:.1f} | {swap / 1024:.1f} | {sampled}/{visible}")
    lines.extend(
        [
            "",
            "Interpretation: RSS is approximate and shared pages appear in multiple processes; do not sum it.",
            "VmSwap excludes swapped shared memory. A missing measurement is not zero.",
            "Net growth is descriptive, not a leak diagnosis; processes may start/exit within this window.",
            "Coverage counts only processes visible in the monitor's PID namespace; inaccessible processes are reported.",
            "A hard freeze can prevent final writes. Logs alone cannot prove a cause or prevent exhaustion.",
        ]
    )
    return "\n".join(lines) + "\n"


def record(args) -> int:
    stop = False

    def request_stop(_signum, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    header = {
        "boot_id": read_text(args.proc_root / "sys/kernel/random/boot_id", 256).strip(),
        "session": uuid.uuid4().hex,
        "started_utc": dt.datetime.now(dt.UTC).isoformat(),
        "interval_seconds": args.interval,
        "proc_root": str(args.proc_root),
        "pid_namespace": os.readlink("/proc/self/ns/pid"),
        "monitor_pid": os.getpid(),
        "clock_ticks_per_second": os.sysconf("SC_CLK_TCK"),
        "command_policy": "executable, Python script/module, allowlisted run selectors; no full argv or environment",
        "low_available_gib": args.low_available_gib,
    }
    recorder = Recorder(
        args.log_dir,
        header,
        int(args.segment_mib * 1024**2),
        int(args.max_log_gib * GIB),
        int(args.min_free_gib * GIB),
    )
    count, previous_alerts = 0, None
    try:
        while not stop and (args.samples is None or count < args.samples):
            started = time.monotonic()
            sample = collect(args.proc_root, args.cgroup_root, args.low_available_gib)
            recorder.write_sample(sample)
            if sample["alerts"] != previous_alerts:
                print(
                    json.dumps(
                        {
                            "timestamp": sample["timestamp"],
                            "alerts": sample["alerts"],
                            "coverage": sample["coverage"],
                        }
                    ),
                    flush=True,
                )
                previous_alerts = sample["alerts"]
            count += 1
            deadline = started + args.interval
            while (
                not stop
                and time.monotonic() < deadline
                and (args.samples is None or count < args.samples)
            ):
                time.sleep(min(0.25, max(0, deadline - time.monotonic())))
    finally:
        recorder.close()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser(
        "record", help="record all visible processes; run as a host user service"
    )
    capture.add_argument("--log-dir", type=Path, default=DEFAULT_DIR)
    capture.add_argument("--interval", type=float, default=10.0)
    capture.add_argument(
        "--samples", type=int, help="stop after this many samples (for a smoke check)"
    )
    capture.add_argument("--segment-mib", type=float, default=64.0)
    capture.add_argument("--max-log-gib", type=float, default=16.0)
    capture.add_argument("--min-free-gib", type=float, default=1.0)
    capture.add_argument("--low-available-gib", type=float, default=3.0)
    capture.add_argument("--proc-root", type=Path, default=Path("/proc"), help=argparse.SUPPRESS)
    capture.add_argument(
        "--cgroup-root", type=Path, default=Path("/sys/fs/cgroup"), help=argparse.SUPPRESS
    )
    report = commands.add_parser(
        "report", help="summarize a recorded boot, including the last minutes before reboot"
    )
    report.add_argument("--log-dir", type=Path, default=DEFAULT_DIR)
    report.add_argument(
        "--boot",
        default="latest",
        help="latest (default), current, previous, or exact recorded boot UUID",
    )
    report.add_argument(
        "--window", type=float, default=1800, help="seconds before the selected boot's last sample"
    )
    report.add_argument("--top", type=int, default=15)
    args = parser.parse_args(argv)
    if args.command == "record":
        for name in ("interval", "segment_mib", "max_log_gib"):
            if not 0 < getattr(args, name) < float("inf"):
                parser.error(f"--{name.replace('_', '-')} must be finite and positive")
        if args.samples is not None and args.samples < 1:
            parser.error("--samples must be positive")
        for name in ("min_free_gib", "low_available_gib"):
            if not 0 <= getattr(args, name) < float("inf"):
                parser.error(f"--{name.replace('_', '-')} must be finite and nonnegative")
    elif not 0 < args.window < float("inf") or args.top < 1:
        parser.error("--window and --top must be positive and finite")
    try:
        if args.command == "record":
            return record(args)
        current = read_text(Path("/proc/sys/kernel/random/boot_id"), 256).strip()
        print(build_report(args.log_dir, args.boot, args.window, args.top, current), end="")
        return 0
    except BlockingIOError:
        print("another monitor already holds this log directory's lock", file=sys.stderr)
        return 74
    except (OSError, ValueError) as error:
        print(f"memory monitor: {error}", file=sys.stderr)
        return 73


if __name__ == "__main__":
    raise SystemExit(main())
