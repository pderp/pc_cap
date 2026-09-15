"""Summarise the OS-level forensics log (scripts/sysmon.sh) around a hang.
    python scripts/sysmon_report.py                 # last 2 minutes of the current log
    python scripts/sysmon_report.py --before-boot -1 --window 180   # the 3 minutes before the previous boot ended
Prints the boot table, the log lines in the window (GPU util/mem/temp/power/throttle, memory, load, PSI, top processes,
kernel clues) and a one-line verdict on what was consuming the GPU and memory at the end."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path

DIR = Path("/home/derp/cap/pc_cap/logs/sysmon")


def boots():
    out = subprocess.run(["journalctl", "--list-boots", "--no-pager"], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        m = re.match(r"\s*(-?\d+)\s+(\w+)\s+(\w{3} \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \w+\s+(\w{3} \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if m:
            rows.append((int(m.group(1)), m.group(2), m.group(3)[4:], m.group(4)[4:]))
    return rows


def lines_between(t0: dt.datetime, t1: dt.datetime):
    out = []
    for f in sorted(DIR.glob("sysmon-*.log")):
        for line in f.read_text().splitlines():
            try:
                ts = dt.datetime.strptime(line[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
            if t0 <= ts <= t1:
                out.append(line)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-boot", type=int, default=None, help="boot index as in journalctl --list-boots (e.g. -1): window ends when that boot's journal ends")
    ap.add_argument("--window", type=int, default=120, help="seconds")
    a = ap.parse_args()
    b = boots()
    print("boots (index, id, first, last):")
    for r in b[-6:]:
        print("  ", r)
    if a.before_boot is not None:
        match = [r for r in b if r[0] == a.before_boot]
        if not match:
            raise SystemExit("no such boot")
        end = dt.datetime.strptime(match[0][3], "%Y-%m-%d %H:%M:%S")
    else:
        end = dt.datetime.now()
    start = end - dt.timedelta(seconds=a.window)
    rows = lines_between(start, end)
    print(f"\n{len(rows)} sysmon lines between {start} and {end}:")
    for line in rows[-40:]:
        print("  " + line[:400])
    if rows:
        last = rows[-1]
        g = re.search(r"gpu\[[^\]]*\]=(.*?) gpu_procs=", last)
        print("\nverdict: last sample", last[:19], "| gpu(util%,memMB,totMB,C,W,MHz,throttle,pstate)=", g.group(1) if g else "?",
              "| gpu procs:", re.search(r"gpu_procs=(\S*)", last).group(1) if re.search(r"gpu_procs=(\S*)", last) else "?",
              "| top cpu:", re.search(r"top_cpu=(\S*)", last).group(1) if re.search(r"top_cpu=(\S*)", last) else "?",
              "| kernel clues:", (re.search(r"kmsg=(.*)$", last).group(1) or "none"))
    else:
        print("\nno sysmon samples in the window (the logger was not running then — it was installed on 2026-09-15 15:22 EDT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
