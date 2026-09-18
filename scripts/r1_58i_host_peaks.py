"""Extract direct and temporally matched host RSS, preserving attribution limits.

Read bounded prefixes of live monitor files; never alter or restart monitoring.
Saved excerpts survive the monitor's 48-hour retention. No model/GPU use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from datetime import datetime
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.r1_58h_cost_receipt import completed_profiles
from scripts.r1_d10a_review import ROOT, write_new

DRIVER_MODULES = (
    "r1_68c_dev_cell",
    "r1_68b_dev_cell",
    "r1_64_dev_cell",
    "r1_64c_comparator_recipes",
    "r1_73b_comparator_recipes",
    "r1_73d_locality_recipes",
)


def driver_command(command):
    return any(
        token == f"scripts.{module}"
        or token == f"scripts/{module}.py"
        or token.endswith(f"/{module}.py")
        for token in command.split()
        for module in DRIVER_MODULES
    )


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def monitor_index(paths):
    processes, segments, issues = {}, [], []
    for path in sorted(map(Path, paths)):
        try:
            with path.open("rb") as f:
                limit = path.stat().st_size
                header_raw = f.readline()
                header = json.loads(header_raw)
                if header.get("type") != "header":
                    raise ValueError("monitor header missing")
                columns = header["process_columns"]
                identities = {}
                digest = hashlib.sha256(header_raw)
                consumed, lines = len(header_raw), 1
                while consumed < limit:
                    offset = consumed
                    raw = f.readline(limit - consumed)
                    if not raw.endswith(b"\n"):
                        issues.append(
                            dict(
                                path=str(path), reason="incomplete live tail omitted", offset=offset
                            )
                        )
                        break
                    consumed += len(raw)
                    lines += 1
                    digest.update(raw)
                    value = json.loads(raw)
                    if value.get("type") != "sample":
                        continue
                    for identity in value["identities"]:
                        identities[(identity["pid"], identity["start_ticks"])] = identity
                    time = timestamp(value["timestamp"])
                    for row in value["processes"]:
                        identity = identities.get((row[0], row[1]), {})
                        command = identity.get("command", "")
                        if not driver_command(command):
                            continue
                        data = dict(zip(columns, row, strict=True))
                        key = f"{header['boot_id']}:{row[0]}:{row[1]}"
                        group = processes.setdefault(
                            key, dict(identity=identity, boot_id=header["boot_id"], samples=[])
                        )
                        group["samples"].append(
                            dict(
                                timestamp=value["timestamp"],
                                unix_time=time,
                                rss_kib=data["rss_kib"],
                                hwm_kib=data["hwm_kib"],
                                source_path=str(path.resolve()),
                                byte_offset=offset,
                                line=lines,
                                sample_sha256=hashlib.sha256(raw).hexdigest(),
                            )
                        )
                segments.append(
                    dict(
                        path=str(path.resolve()),
                        prefix_bytes=consumed,
                        prefix_sha256=digest.hexdigest(),
                        header=header,
                        live_file_size_at_open=limit,
                        complete_lines=lines,
                    )
                )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as error:
            issues.append(dict(path=str(path), reason=str(error)))
    for p in processes.values():
        p["samples"].sort(key=lambda s: s["unix_time"])
    return dict(
        processes=processes,
        segments=segments,
        issues=issues,
        note="Filtered excerpts retain PID/start_ticks/boot and raw sample hashes. Raw files expire; prefix hashes identify the read snapshot, not later appended bytes.",
    )


def direct_time(path, recipe, result):
    """GNU time -v records the exact command plus kernel maximum RSS on success."""
    raw = Path(path).read_text()
    fields = {}
    for line in raw.splitlines():
        if ": " in line:
            k, v = line.strip().split(": ", 1)
            fields[k] = v
    if fields.get("Exit status") != "0":
        raise ValueError("direct time report not complete/successful")
    tokens = shlex.split(fields["Command being timed"].strip('"'))

    def arg(flag):
        for i, v in enumerate(tokens):
            if v == flag and i + 1 < len(tokens):
                return tokens[i + 1]
            if v.startswith(flag + "="):
                return v.split("=", 1)[1]
        return None

    if (
        arg("--manifest") is None
        or Path(arg("--manifest")).resolve() != Path(recipe["path"]).resolve()
        or arg("--manifest-sha256") != recipe["sha256"]
        or "--execute" not in tokens
        or result["manifest_sha256"] != recipe["sha256"]
    ):
        raise ValueError("time command/recipe/result identity mismatch")
    rss = int(fields["Maximum resident set size (kbytes)"])
    if rss <= 0:
        raise ValueError("positive maximum RSS required")
    return dict(
        method="direct_gnu_time",
        measured_peak_host_mib=rss / 1024,
        metric="GNU time maximum resident set size; KiB /1024",
        fields=fields,
        attribution="exact recipe path/hash in timed successful command",
        source=d9.ref(path),
    )


def attempt_window(result_path, result):
    """The driver has durations, not UTC/PID. File mtimes are explicit auxiliary evidence."""
    path = Path(result_path)
    end = path.stat().st_mtime
    duration = result.get("attempt_wall_seconds")
    files = sorted((path.parent / "phases").glob("*.json"))
    times = [(p.stat().st_mtime, p) for p in files]
    if not times:
        raise ValueError("phase timing window missing")
    first, last = min(times), max(times)
    basis = "result file mtime minus recorded attempt duration; cross-checked phase file mtimes, no embedded UTC or PID"
    if not isinstance(duration, (float, int)) or duration <= 0:
        phase = json.loads(first[1].read_text())
        elapsed = phase.get("phase_wall_seconds", phase.get("wall_seconds"))
        if not isinstance(elapsed, (float, int)) or elapsed <= 0:
            raise ValueError("attempt and first-phase duration missing")
        duration = end - (first[0] - elapsed)
        basis = "first completed phase file mtime minus its wall duration through result file mtime; historical driver lacks attempt duration/UTC/PID"
    start = end - duration
    if duration <= 0:
        raise ValueError("invalid inferred attempt duration")
    if first[0] < start - 2 or last[0] > end + 2:
        raise ValueError(
            "file mtimes incompatible with attempt duration; possible copied artifacts"
        )
    return dict(
        start=start,
        end=end,
        duration_seconds=duration,
        basis=basis,
        result_stat_mtime_ns=path.stat().st_mtime_ns,
        first_phase=dict(binding=d9.ref(first[1]), mtime=first[0]),
        last_phase=dict(binding=d9.ref(last[1]), mtime=last[0]),
    )


def match_monitor(window, index):
    start, end = window["start"], window["end"]
    candidates = []
    for key, p in index["processes"].items():
        within = [s for s in p["samples"] if start <= s["unix_time"] <= end]
        if within:
            candidates.append((key, p, within))
    if len(candidates) != 1:
        return dict(
            method="unavailable",
            measured_peak_host_mib=None,
            reason="no unique driver process in inferred attempt window",
            candidate_processes=[p[0] for p in candidates],
        )
    key, process, samples = candidates[0]
    cover = (samples[-1]["unix_time"] - samples[0]["unix_time"]) / max(end - start, 1)
    gaps = [b["unix_time"] - a["unix_time"] for a, b in zip(samples, samples[1:])]
    if len(samples) < 2 or cover < 0.8 or max(gaps, default=0) > 30:
        return dict(
            method="unavailable",
            measured_peak_host_mib=None,
            reason="monitor coverage insufficient",
            sample_count=len(samples),
            coverage_fraction=cover,
            candidate_processes=[key],
        )
    rss = [s for s in samples if isinstance(s["rss_kib"], (float, int)) and s["rss_kib"] > 0]
    if not rss:
        return dict(
            method="unavailable", measured_peak_host_mib=None, reason="no positive RSS samples"
        )
    peak = max(rss, key=lambda s: s["rss_kib"])
    hwm = max((s["hwm_kib"] or 0 for s in samples), default=0)
    return dict(
        method="monitor_temporal_match",
        measured_peak_host_mib=peak["rss_kib"] / 1024,
        observed_hwm_mib=hwm / 1024,
        process_key=key,
        identity=process["identity"],
        boot_id=process["boot_id"],
        peak_sample=peak,
        sample_count=len(samples),
        coverage_fraction=cover,
        maximum_sample_gap_seconds=max(gaps, default=0),
        attribution="unique driver in inferred file-mtime window; recipe argv/PID absent, requires owner review",
        metric="maximum sampled RSS, a lower bound on true process peak; HWM reported separately",
        window=window,
        attribution_reviewed=False,
    )


def build(output, evidence_dir, *, log_dir=ROOT / "logs/process_memory"):
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=False)
    index = monitor_index(Path(log_dir).glob("*.jsonl"))
    index_ref = write_new(evidence_dir / "monitor-driver-excerpts.json", index)
    profiles = completed_profiles()
    ceilings = d9.read_metadata(d9.ref(ROOT / "manifests/revision_v1/cell_ceilings_v1.json"))[
        "cells"
    ]
    rows = {}
    for key in sorted(ceilings):
        condition, dataset = key.split(":")
        options = profiles.get((condition, dataset), [])
        attempts = []
        for _, rp, _, result_path, result, *_ in options:
            b = d9.ref(rp)
            time_path = ROOT / f"results/R1/stage4_dev_cell_r1_64f_{dataset}-{condition}.time"
            measured = None
            if "R1-64f" in str(rp) and time_path.exists():
                try:
                    measured = direct_time(time_path, b, result)
                    saved = evidence_dir / f"{key.replace(':', '-')}.time.txt"
                    with saved.open("xb") as f:
                        f.write(time_path.read_bytes())
                    if d9.sha(saved) != measured["source"]["sha256"]:
                        raise ValueError("direct time changed during snapshot")
                    measured["snapshot"] = d9.ref(saved)
                except ValueError as error:
                    measured = dict(
                        method="unavailable", measured_peak_host_mib=None, reason=str(error)
                    )
            if measured is None:
                try:
                    measured = match_monitor(attempt_window(result_path, result), index)
                except ValueError as error:
                    measured = dict(
                        method="unavailable", measured_peak_host_mib=None, reason=str(error)
                    )
            measured.update(recipe=b, result=d9.ref(result_path), monitor_excerpts=index_ref)
            attempts.append(measured)
        # Direct first, otherwise highest observed sampled RSS across eligible attempts;
        # this is a conservative memory maximum, not scientific outcome selection.
        available = [a for a in attempts if a["measured_peak_host_mib"] is not None]
        direct = [a for a in available if a["method"] == "direct_gnu_time"]
        selected = max(direct or available, key=lambda a: a["measured_peak_host_mib"], default=None)
        rows[key] = dict(
            selected or dict(method="unavailable", measured_peak_host_mib=None),
            condition=condition,
            dataset=dataset,
            attempts=attempts,
        )
    for row in rows.values():
        if row["measured_peak_host_mib"] is None:
            same = [
                (k, v)
                for k, v in rows.items()
                if v["condition"] == row["condition"] and v["measured_peak_host_mib"]
            ]
            if same:
                donor_key, donor = max(same, key=lambda kv: kv[1]["measured_peak_host_mib"])
                row.update(
                    method="extrapolated_proposal",
                    proposed_peak_host_mib=donor["measured_peak_host_mib"],
                    donor=donor_key,
                    transfer_rule="maximum observed same-condition host RSS across available datasets, before 1.5 ceiling padding",
                    transfer_reviewed=False,
                )
    result = dict(
        schema_version=1,
        task="R1-58i",
        producer=d9.ref(__file__),
        rows=rows,
        monitor_excerpts=index_ref,
        driver_entry_points={m: d9.ref(ROOT / f"scripts/{m}.py") for m in DRIVER_MODULES},
        counts={
            m: sum(r["method"] == m for r in rows.values())
            for m in (
                "direct_gnu_time",
                "monitor_temporal_match",
                "extrapolated_proposal",
                "unavailable",
            )
        },
        note="Temporal matches need attribution review; proposed transfers are not measurements. Sampling can miss peaks. No host-memory floor used as peak.",
    )
    return write_new(Path(output), result)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--log-dir", type=Path, default=ROOT / "logs/process_memory")
    a = p.parse_args()
    print(json.dumps(build(a.output, a.evidence_dir, log_dir=a.log_dir), indent=2))


if __name__ == "__main__":
    main()
