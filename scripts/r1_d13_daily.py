"""Daily queue/watch/monitor report, or one-command idle-boundary D11 -> D12.

Creates a new report directory only. Never posts, executes cells, edits admissions,
reads model payloads, queries the GPU, or changes monitoring services.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts import process_memory_monitor as memory
from scripts import r1_d11_block_report as d11
from scripts import r1_d12_reprice as d12

ROOT = d11.ROOT
MAX_TAIL = 2 * 1024 * 1024


def tail(path, limit=MAX_TAIL):
    """Bounded complete lines with byte offsets; an active partial tail is omitted."""
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        start = max(0, size - limit)
        f.seek(start)
        raw = f.read(limit)
    if start:
        end = raw.find(b"\n")
        if end < 0:
            return [], True
        start, raw = start + end + 1, raw[end + 1:]
    partial = bool(raw and not raw.endswith(b"\n"))
    lines = raw.splitlines(keepends=True)
    if partial:
        lines.pop()
    out = []
    for line in lines:
        out.append((start, line))
        start += len(line)
    return out, partial


def source(path, offset, raw):
    return dict(path=str(path), offset=offset, bytes=len(raw),
                line_sha256=hashlib.sha256(raw).hexdigest())


def age(timestamp, now, maximum):
    delta = (now - timestamp).total_seconds()
    return delta, "fresh" if 0 <= delta <= maximum else "future_timestamp" if delta < 0 else "stale"


def finite(value, *, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError("invalid numeric monitor field")
    return value


def memory_health(directory, now, maximum, boot_id=None):
    candidates, issues = [], []
    # Latest two segments are enough for a rollover; never scan all 48 hours.
    paths = sorted(Path(directory).glob("memory-*.jsonl"), key=lambda p:p.stat().st_mtime_ns)[-2:]
    for path in paths:
        try:
            with path.open("rb") as f:
                header = json.loads(f.readline(memory.MAX_RECORD + 1))
            if (header.get("type") != "header" or header.get("schema") != 1
                    or header.get("process_columns") != memory.COLUMNS or not header.get("boot_id")):
                raise ValueError("unrecognized memory monitor header")
            rows, partial = tail(path)
            if partial:
                issues.append(str(path) + ": partial tail omitted")
            for offset, raw in reversed(rows):
                try:
                    sample = json.loads(raw)
                    if sample.get("type") != "sample":
                        continue
                    stamp = datetime.fromisoformat(sample["timestamp"])
                    if stamp.tzinfo is None:
                        raise ValueError("memory timestamp lacks timezone")
                    mem = sample["host"]["meminfo_kib"]
                    available = finite(mem["MemAvailable"]) / 1024
                    total = finite(mem["MemTotal"], minimum=1) / 1024
                    if available > total:
                        raise ValueError("available memory exceeds total")
                    elapsed, freshness = age(stamp, now, maximum)
                    if boot_id is not None and header["boot_id"] != boot_id:
                        freshness = "different_boot"
                    top, rss_unavailable = [], 0
                    for row in sample["processes"]:
                        item = dict(zip(memory.COLUMNS, row, strict=True))
                        # Kernel threads and vanished/inaccessible address spaces
                        # legitimately lack VmRSS. Missing is not zero memory.
                        if item["rss_kib"] is None:
                            rss_unavailable += 1
                            continue
                        finite(item["rss_kib"])
                        top.append({k:item[k] for k in ("pid", "start_ticks", "rss_kib", "swap_kib")})
                    candidates.append((stamp, dict(status=freshness, timestamp=stamp.isoformat(),
                        age_seconds=elapsed, boot_id=header["boot_id"], mem_available_mib=available,
                        mem_total_mib=total, below_launch_floor=available < 6144,
                        swap_used_mib=(finite(mem.get("SwapTotal", 0)) - finite(mem.get("SwapFree", 0))) / 1024,
                        monitor_alerts=sample.get("alerts", []), coverage=sample.get("coverage", {}),
                        psi=sample["host"].get("psi"),
                        rss_unavailable_processes=rss_unavailable,
                        top_rss=sorted(top, key=lambda p:p["rss_kib"], reverse=True)[:5],
                        source=source(path, offset, raw))))
                    break
                except (ValueError, TypeError, KeyError) as error:
                    issues.append(f"{path}:{offset}: {error}")
                    break  # Do not silently hide a malformed newest complete sample.
        except (OSError, ValueError, TypeError, KeyError) as error:
            issues.append(f"{path}: {error}")
    result = max(candidates, key=lambda x:x[0])[1] if candidates else dict(status="unavailable")
    result["read_issues"] = issues
    result["process_labels"] = "PID/start_ticks only; no guessed command identity or argv"
    return result


def gpu_health(directory, now, maximum, timezone="America/New_York"):
    candidates, issues = [], []
    paths = sorted(Path(directory).glob("sysmon-*.log"))[-2:]
    for path in paths:
        try:
            rows, partial = tail(path, 1024 * 1024)
            if partial:
                issues.append(str(path) + ": partial tail omitted")
            if not rows:
                continue
            offset, raw = rows[-1]
            line = raw.decode("utf-8")
            stamp = datetime.fromisoformat(line[:19]).replace(tzinfo=ZoneInfo(timezone))
            elapsed, freshness = age(stamp, now, maximum)
            match = re.search(r"gpu\[[^]]*\]=(.*?) gpu_procs=(\S*)", line)
            if match is None:
                raise ValueError("GPU sample absent")
            parts = match[1].split()
            values = [finite(float(p)) for p in parts[:6]] if len(parts) == 8 else []
            if len(values) != 6 or values[0] > 100 or values[1] > values[2]:
                raise ValueError("GPU unavailable or malformed")
            candidates.append((stamp, dict(status=freshness, timestamp=stamp.isoformat(),
                age_seconds=elapsed, utilization_percent=values[0], memory_used_mib=values[1],
                memory_total_mib=values[2], temperature_c=values[3], power_w=values[4],
                clock_mhz=values[5], throttle_mask=parts[6], pstate=parts[7],
                gpu_processes=match[2], kernel_clues=line.partition(" kmsg=")[2].strip(),
                source=source(path, offset, raw),
                boot_identity="not recorded by sysmon; timestamp freshness only")))
        except (OSError, ValueError, TypeError, KeyError) as error:
            issues.append(f"{path}: {error}")
    result = max(candidates, key=lambda x:x[0])[1] if candidates else dict(status="unavailable")
    result["read_issues"] = issues
    result["interpretation"] = "Saved observations, not a crash diagnosis or launch clearance; throttle mask is preserved, not classified."
    return result


def health(memory_dir, sysmon_dir, *, now=None, max_age_seconds=120, boot_id=None):
    now = now or datetime.now(UTC)
    if now.tzinfo is None or max_age_seconds <= 0:
        raise ValueError("timezone-aware time and positive freshness window required")
    if boot_id is None:
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    return dict(observed_utc=now.isoformat(), freshness_limit_seconds=max_age_seconds,
                memory=memory_health(memory_dir, now, max_age_seconds, boot_id),
                gpu=gpu_health(sysmon_dir, now, max_age_seconds),
                source_policy="Bounded complete-line tails from two segments; missing/stale/partial data explicitly reported; no live GPU query.")


def prior_report(previous_run):
    if previous_run is None:
        return None, None
    binding = d11.ref(previous_run)
    prior = d12.read_ref(binding)
    if prior.get("report_sha256") != d12.digest({k:v for k,v in prior.items() if k != "report_sha256"}):
        raise ValueError("previous daily report digest differs")
    if prior.get("task") != "R1-D13" or prior.get("mode") != "daily":
        raise ValueError("previous-run must be a daily D13 report")
    d12.read_ref(prior["d11_report"])
    return prior["d11_report"]["path"], binding


def build(matrix, *, receipt_root, journal, previous_run=None, workers=2,
          memory_dir=ROOT / "logs/process_memory", sysmon_dir=ROOT / "logs/sysmon",
          now=None, boot_id=None, max_age_seconds=120):
    previous, binding = prior_report(previous_run)
    snapshot = d11.build(matrix, receipt_root=receipt_root, journal=journal,
                        previous=previous, workers=workers)
    # D11's saved JSON stays byte-identical. This wrapper explicitly distinguishes
    # generation cursors from the last report actually posted by the owner.
    result = dict(task="R1-D13", version=1, mode="daily", previous_run=binding,
                  d11=snapshot, health=health(memory_dir, sysmon_dir, now=now,
                                             boot_id=boot_id, max_age_seconds=max_age_seconds),
                  watch_delta_basis="since previous generated daily report, not asserted delivered",
                  posted=False, launch_authorized=False)
    return result


def text(report):
    snapshot = report.get("d11")
    body = (d11.text(snapshot).replace("Watch since previous posted snapshot:",
            "Watch since previous generated daily report:") if snapshot else "Queue not inspected (health-only report).\n")
    lines = [body, "Monitor observations:"]
    for name in ("memory", "gpu"):
        value = report["health"][name]
        fields = ("mem_available_mib", "below_launch_floor", "swap_used_mib", "monitor_alerts") if name == "memory" else (
            "utilization_percent", "memory_used_mib", "temperature_c", "throttle_mask", "kernel_clues")
        lines.append(f"- {name}: {value['status']}; age={value.get('age_seconds', 'unknown')} s; " +
                     "; ".join(f"{k}={value.get(k, 'unavailable')}" for k in fields))
        lines.extend("  read issue: " + i for i in value["read_issues"])
    lines += ["Saved samples are not a launch clearance. Verify live memory/lease before execution.",
              "Not posted. Relay new creep alerts promptly; daily generation does not acknowledge delivery."]
    return "\n".join(lines) + "\n"


def emit(report, output):
    output = d11.local(output)
    if not output.is_relative_to(ROOT / "logs"):
        raise ValueError("new output directory under repository logs required")
    if report.get("d11"):
        # Reuse D12's coherent-snapshot recheck without making a cost proposal.
        d12.verify_snapshot(dict(d11=report["d11"], inputs={}))
    output.mkdir(parents=True, exist_ok=False)
    report = dict(report)
    if report.get("d11"):
        with (output / "d11-report.json").open("x") as f:
            json.dump(report["d11"], f, indent=2, allow_nan=False)
        report["d11_report"] = d11.ref(output / "d11-report.json")
    report["report_sha256"] = d12.digest(report)
    with (output / "daily.json").open("x") as f:
        json.dump(report, f, indent=2, allow_nan=False)
    with (output / "lead-queue.txt").open("x") as f:
        f.write(text(report))
    return d11.ref(output / "daily.json")


def boundary(matrix, *, output_dir, memory_dir=ROOT / "logs/process_memory",
             sysmon_dir=ROOT / "logs/sysmon", **kwargs):
    report = d12.build(matrix, **kwargs)  # D11 -> globally idle check -> D12 proposal.
    monitors = health(memory_dir, sysmon_dir)
    binding = d12.emit(report, output_dir)  # rechecks queue immediately before writing.
    output = Path(output_dir)
    with (output / "monitor-health.json").open("x") as f:
        json.dump(monitors, f, indent=2, allow_nan=False)
    with (output / "operations-text.txt").open("x") as f:
        f.write(d12.text(report) + "\n" + text(dict(health=monitors)))
    return dict(plan=binding, health=d11.ref(output / "monitor-health.json"),
                text=str(output / "operations-text.txt"), posted=False, launch_authorized=False)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("daily", "boundary", "health"))
    for name in ("matrix", "receipt-root", "journal", "output-dir", "previous-run",
                 "cost-receipt", "previous-plan", "previous-posted-report"):
        p.add_argument("--" + name, type=Path, required=name == "output-dir")
    p.add_argument("--memory-dir", type=Path, default=ROOT / "logs/process_memory")
    p.add_argument("--sysmon-dir", type=Path, default=ROOT / "logs/sysmon")
    p.add_argument("--boundary-block", type=int)
    p.add_argument("--workers", type=int, choices=(1, 2), default=2)
    p.add_argument("--synthetic", action="store_true")
    a = p.parse_args(argv)
    if a.mode != "health" and any(getattr(a, k) is None for k in ("matrix", "receipt_root", "journal")):
        p.error("daily/boundary require --matrix, --receipt-root and --journal")
    if a.mode == "boundary" and (a.cost_receipt is None or a.boundary_block is None):
        p.error("boundary requires --cost-receipt and --boundary-block")
    if a.mode == "boundary" and a.previous_run:
        p.error("boundary uses --previous-posted-report, not the daily generation cursor")
    if a.mode != "boundary" and any((a.cost_receipt, a.boundary_block, a.previous_plan,
                                     a.previous_posted_report, a.synthetic)):
        p.error("cost/repricing options require boundary mode")
    try:
        monitors = dict(memory_dir=a.memory_dir, sysmon_dir=a.sysmon_dir)
        if a.mode == "boundary":
            result = boundary(a.matrix, output_dir=a.output_dir, receipt_root=a.receipt_root,
                journal=a.journal, cost_receipt=a.cost_receipt, boundary_block=a.boundary_block,
                previous_plan=a.previous_plan, previous_report=a.previous_posted_report,
                workers=a.workers, synthetic=a.synthetic, **monitors)
        else:
            report = (build(a.matrix, receipt_root=a.receipt_root, journal=a.journal,
                            previous_run=a.previous_run, workers=a.workers, **monitors)
                      if a.mode == "daily" else dict(task="R1-D13", version=1, mode="health",
                            health=health(**monitors), posted=False, launch_authorized=False))
            result = emit(report, a.output_dir)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(json.dumps(dict(task="R1-D13", blocked=str(error), posted=False)))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
