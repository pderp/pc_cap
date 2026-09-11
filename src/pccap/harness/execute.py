"""S4-04: the confirmatory job queue (plan §6.10 S4-04; PDF S4, §4.5 rule 4).

Runs the fixed job list of ``pccap.harness.schedule`` in order, one ``pccap run --mode confirm`` subprocess per job
(each takes the GPU lease itself), resumable and fail-fast:

* a job whose run directory already holds a ``complete`` or ``resource_stop`` result is skipped (never rerun);
* exit 0 → next job; exit 1 (``correctness_failure``, a result) → recorded, the queue continues; exit 2 (refused:
  precondition, identity, code drift) or 5 (stage allowance) → the queue **stops** — a refusal is never retried blindly;
* a stop file (``results/S4/queue.stop``) pauses the queue at the next job boundary; ``--max-jobs`` bounds a session.

Every attempt is appended to ``results/S4/queue.jsonl`` (job identity, command, start/end, exit code, run directory).
``python -m pccap.harness.execute [--jobs results/S4/jobs.json] [--max-jobs N] [--dry-run] [--stage S4]``.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "results"
STOP_CODES = {2: "refused", 5: "stage allowance exceeded"}


def run_dir_of(job: dict, frozen: dict, frozen_sha: str) -> Path:
    """The run directory the runner will use for ``job`` (same identity rule: frozen name + hash prefix, R2-03)."""
    from types import SimpleNamespace

    from pccap.harness.runner import experiment_id, run_dir_for

    args = SimpleNamespace(stage=job["stage"], arm=job["arm"], base=job["base"], read=job["read"], realization=job["realization"],
                           perm=job["perm"], dataset=job["dataset"], mode="confirm", manifest=job["manifest"])
    return run_dir_for(args, experiment_id(args, frozen, frozen_sha), job["dataset"])


def stale_attempt(rd: Path) -> str | None:
    """A previous attempt that produced no results (``refused``, ``running`` from an interrupted session, or a
    ``correctness_failure`` before any item): its status, so the queue reruns it with ``--force`` (the directory and its
    error record are archived by the runner, never deleted)."""
    cfg = rd / "config.json"
    if not cfg.exists() or (rd / "metrics.json").exists():
        return None
    try:
        return json.loads(cfg.read_text()).get("status")
    except Exception:
        return "unreadable"


def done_status(rd: Path) -> str | None:
    cfg = rd / "config.json"
    if not cfg.exists():
        return None
    try:
        st = json.loads(cfg.read_text()).get("status")
    except Exception:
        return None
    return st if st in ("complete", "resource_stop") and (rd / "metrics.json").exists() else None


def command_for(job: dict, force: bool = False) -> list[str]:
    """The exact CLI invocation for one job (the schedule's ``cmd`` string with the interpreter prefix)."""
    parts = shlex.split(job["cmd"])
    assert parts[:2] == ["pccap", "run"], job["cmd"]
    return [sys.executable, "-m", "pccap.cli"] + parts[1:] + (["--force"] if force else [])


def subprocess_invoke(job: dict, log_dir: Path, force: bool = False) -> int:
    log_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{job['dataset']}_{job['arm']}_r{job['realization']}_p{job['perm']}"
    with open(log_dir / f"{tag}.log", "a") as log:
        log.write(f"\n=== {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {' '.join(command_for(job, force))}\n")
        log.flush()
        env = dict(os.environ)
        env.setdefault("PYTHONUNBUFFERED", "1")
        return subprocess.call(command_for(job, force), cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT, env=env)


def run_queue(jobs: list[dict], frozen: dict, frozen_sha: str, invoke=None, *, max_jobs: int | None = None, stop_file: Path | None = None,
              queue_log: Path | None = None, log_dir: Path | None = None, dry_run: bool = False, stage: str = "S4",
              max_consecutive_failures: int = 3) -> dict:
    """Execute the scheduled jobs of ``stage`` in order. ``invoke(job, force=False) -> exit code`` defaults to the subprocess
    runner; tests inject an in-process fake. ``max_consecutive_failures`` correctness failures in a row that completed no
    item stop the queue (a systematic failure, not a run result). Returns the queue summary."""
    invoke = invoke or (lambda j, force=False: subprocess_invoke(j, log_dir or (RESULTS / stage / "queue_logs"), force))
    consecutive_empty_failures = 0
    summary = {"stage": stage, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "scheduled": 0, "skipped_done": 0, "ran": 0,
               "ok": 0, "correctness_failure": 0, "stopped": None, "unavailable": 0, "attempts": []}
    n = 0
    for job in jobs:
        if job["stage"] != stage:
            continue
        if job["status"] != "scheduled":
            summary["unavailable"] += 1
            continue
        summary["scheduled"] += 1
        rd = run_dir_of(job, frozen, frozen_sha)
        if done_status(rd):
            summary["skipped_done"] += 1
            continue
        if stop_file is not None and stop_file.exists():
            summary["stopped"] = f"stop file {stop_file} present"
            break
        if max_jobs is not None and n >= max_jobs:
            summary["stopped"] = f"max_jobs {max_jobs} reached"
            break
        stale = stale_attempt(rd)
        rec = {"job": {k: job[k] for k in ("dataset", "arm", "realization", "perm", "n_items")}, "cmd": " ".join(command_for(job, bool(stale))), "run_dir": str(rd),
               "start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "archived_previous_attempt": stale}
        if dry_run:
            rec["exit"] = None
            summary["attempts"].append(rec)
            n += 1
            continue
        t0 = time.time()
        code = int(invoke(job, bool(stale)) if stale else invoke(job))
        items = rd / "items.jsonl"
        n_items = sum(1 for line in items.read_text().splitlines() if line.strip()) if items.exists() else 0
        rec.update(exit=code, end=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), wall_seconds=time.time() - t0, status=done_status(rd), items_completed=n_items)
        summary["attempts"].append(rec)
        if queue_log is not None:
            queue_log.parent.mkdir(parents=True, exist_ok=True)
            with open(queue_log, "a") as f:
                f.write(json.dumps(rec) + "\n")
        n += 1
        summary["ran"] += 1
        if code == 0:
            summary["ok"] += 1
            consecutive_empty_failures = 0
        elif code == 1:
            summary["correctness_failure"] += 1  # a result (error.json in the run directory); the queue continues …
            consecutive_empty_failures = consecutive_empty_failures + 1 if n_items == 0 else 0
            if consecutive_empty_failures >= max_consecutive_failures:  # … unless failures are systematic (no item ever completed)
                summary["stopped"] = f"{consecutive_empty_failures} consecutive correctness failures with no item completed (systematic): last {rec['job']}"
                break
        else:
            summary["stopped"] = f"exit {code} ({STOP_CODES.get(code, 'unexpected')}) on {rec['job']}: fix the cause before resuming"
            break
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=str(RESULTS / "S4" / "jobs.json"))
    ap.add_argument("--stage", default="S4")
    ap.add_argument("--max-jobs", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    frozen = ROOT / "manifests" / "frozen.json"
    if not frozen.exists():
        print("REFUSED: the confirmatory queue needs manifests/frozen.json (the lead's CP-E act)", file=sys.stderr)
        return 2
    import hashlib

    frozen_sha = hashlib.sha256(frozen.read_bytes()).hexdigest()
    frozen_obj = json.loads(frozen.read_text())
    jobs_doc = json.loads(Path(args.jobs).read_text())
    if jobs_doc.get("draft") or jobs_doc.get("manifest_sha256") != frozen_sha:
        print(f"REFUSED: {args.jobs} was not generated from the current manifests/frozen.json (regenerate with python -m pccap.harness.schedule)", file=sys.stderr)
        return 2
    out_dir = RESULTS / args.stage
    summary = run_queue(jobs_doc["jobs"], frozen_obj, frozen_sha, max_jobs=args.max_jobs, stop_file=out_dir / "queue.stop", queue_log=out_dir / "queue.jsonl",
                        log_dir=out_dir / "queue_logs", dry_run=args.dry_run, stage=args.stage)
    (out_dir / ("queue_summary_dryrun.json" if args.dry_run else "queue_summary.json")).write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != "attempts"}, indent=1))
    return 0 if summary["stopped"] is None or summary["stopped"].startswith(("max_jobs", "stop file")) else 3


if __name__ == "__main__":
    raise SystemExit(main())
