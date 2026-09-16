"""Wait read-only for the owner's chain-H terminal receipt, then emit a new report.

This monitor performs no model work and never starts, stops or modifies an owner
process. One immutable report pair is emitted after completion, charged failure
or the explicit timeout; partial/missing rows retain their unavailable status.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts import ht3d_bound_aliases as report
from scripts import ht3d_pilot_aggregate as core

ROOT = core.ROOT


def observe(spec):
    for relative in spec["failure_receipts"]:
        path = ROOT / relative
        if path.is_file():
            return {"trigger": "owner_charged_failure", "path": relative, "sha256": core.sha(path)}
    directory = ROOT / spec["full_profile_directory"]
    for path in sorted(directory.glob("attempt-*/result.json")):
        obj = json.loads(path.read_text())
        if (
            obj.get("manifest_sha256") != spec["full_recipe"]["sha256"]
            or obj.get("cell") != spec["cell"]
        ):
            raise ValueError("owner terminal result identity mismatch")
        if obj.get("status") == "complete":
            return {
                "trigger": "owner_chain_terminal_profile_complete",
                "path": str(path.relative_to(ROOT)),
                "sha256": core.sha(path),
            }
    for path in sorted(directory.glob("attempt-*/failure.json")):
        return {
            "trigger": "owner_terminal_profile_failure",
            "path": str(path.relative_to(ROOT)),
            "sha256": core.sha(path),
        }
    return None


def refresh(spec, prefix, trigger):
    for name, h in spec["reporter_sources_sha256"].items():
        if core.sha(ROOT / name) != h:
            raise ValueError("reporter source changed while waiting: " + name)
    if core.sha(ROOT / spec["full_recipe"]["path"]) != spec["full_recipe"]["sha256"]:
        raise ValueError("watched recipe changed")
    paths = [Path(str(prefix) + s) for s in (".json", ".md")]
    if any(p.exists() for p in paths):
        raise FileExistsError("refresh outputs already exist")
    obj = report.aggregate()
    obj["automatic_refresh"] = {**trigger, "watch_spec": spec}
    texts = [json.dumps(obj, indent=2, allow_nan=False) + "\n", report.markdown(obj)]
    for path, text in zip(paths, texts, strict=True):
        with path.open("x") as f:
            f.write(text)
    return {
        "outputs": [str(p) for p in paths],
        "complete_rows": obj["complete_rows"],
        "framing": obj["framing"],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--output-prefix", type=Path, required=True)
    p.add_argument("--poll-seconds", type=float, default=60)
    p.add_argument("--timeout-seconds", type=float, default=21600)
    a = p.parse_args(argv)
    prefix = a.output_prefix.resolve()
    if (
        not prefix.is_relative_to(ROOT / "logs/r1_round18")
        or not 1 <= a.poll_seconds <= 60
        or a.timeout_seconds <= 0
    ):
        p.error("new round18 outputs, poll 1–60 seconds and positive timeout required")
    paths = [Path(str(prefix) + s) for s in (".json", ".md", ".watch-status.json")]
    if any(x.exists() for x in paths):
        p.error("output prefix already exists")
    spec = json.loads(a.spec.read_text())
    begun = time.monotonic()
    try:
        while True:
            trigger = observe(spec)
            if trigger is not None:
                break
            if time.monotonic() - begun >= a.timeout_seconds:
                trigger = {
                    "trigger": "timeout_partial_snapshot",
                    "timeout_seconds": a.timeout_seconds,
                }
                break
            time.sleep(min(a.poll_seconds, a.timeout_seconds - (time.monotonic() - begun)))
        result = refresh(spec, prefix, trigger)
        status = {"status": "report_written", "trigger": trigger, **result}
    except Exception as exc:
        status = {"status": "refresh_failed", "error": repr(exc)}
    status.update(
        finished_at=datetime.now(timezone.utc).isoformat(),
        watch_wall_seconds=time.monotonic() - begun,
        gpu_seconds=0,
        model_calls=0,
        owner_files_modified=0,
    )
    with paths[2].open("x") as f:
        json.dump(status, f, indent=2)
        f.write("\n")
    print(json.dumps({"status": status["status"], "status_file": str(paths[2])}), flush=True)
    return 0 if status["status"] == "report_written" else 1


if __name__ == "__main__":
    raise SystemExit(main())
