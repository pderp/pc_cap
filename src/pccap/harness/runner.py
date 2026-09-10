"""`pccap run` entry (S0-03 skeleton; stage runners register themselves later).

Responsibilities fixed here:
* load the manifest, hash it, validate it against the schema for ``--mode`` (a frozen manifest
  missing any S4-01 field is refused with the missing fields listed; exit code 2);
* build the run directory ``results/<stage>/<arm>/<base>/<read>/<realization>/<perm>/`` and
  write ``config.json`` (with determinism settings and the code commit);
* dispatch to a registered stage runner ``RUNNERS[stage]``; any exception is written to
  ``error.json`` and the status becomes ``correctness_failure`` (Op. rule 8).

``--dry-run`` stops after validation and prints the resolved configuration.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Callable

from pccap.harness import schema
from pccap.harness.records import RunStatus, write_error_json

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "results"

RUNNERS: dict[str, Callable[[dict, Path], dict]] = {}


def register(stage: str):
    def deco(fn):
        RUNNERS[stage] = fn
        return fn

    return deco


def code_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def load_manifest(path: Path, mode: str) -> tuple[dict, str, list[str]]:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = json.loads(raw)
    kind = "manifest_frozen" if mode == "confirm" else "manifest_dev"
    errs = schema.errors(kind, obj)
    if mode == "confirm":
        missing = schema.missing_frozen_fields(obj)
        errs = [f"missing frozen field: {m}" for m in missing] + [
            e for e in errs if not any(f"'{m}' is a required property" in e for m in missing)
        ]
    return obj, sha, errs


def run_dir_for(args) -> Path:
    return RESULTS / args.stage / (args.arm or "none") / args.base / args.read / str(args.realization) / str(args.perm)


def main(args) -> int:
    import pccap

    mpath = Path(args.manifest)
    if not mpath.exists():
        print(f"manifest not found: {mpath}", file=sys.stderr)
        return 2
    manifest, msha, errs = load_manifest(mpath, args.mode)
    if errs:
        print(f"REFUSED: manifest {mpath} is not a valid {args.mode} manifest:", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        return 2
    if args.mode == "confirm":
        frozen = ROOT / "manifests" / "frozen.json"
        if not frozen.exists():
            print("REFUSED: confirm mode requires manifests/frozen.json (plan §4.5 rule 4)", file=sys.stderr)
            return 2
    cfg = {
        "stage": args.stage,
        "arm": args.arm or "none",
        "base": args.base,
        "read": args.read,
        "realization": args.realization,
        "perm": args.perm,
        "manifest": str(mpath),
        "manifest_sha256": msha,
        "mode": args.mode,
        "task": getattr(args, "task", None),
        "code_commit": code_commit(),
        "determinism": pccap.determinism_report(),
        "base_hash_before": "",
        "status": RunStatus.running.value,
    }
    if args.dry_run:
        print(json.dumps(cfg, indent=1))
        return 0
    import pccap.harness.stage_s0  # noqa: F401  (registers "S0")
    import pccap.harness.stage_s3  # noqa: F401  (registers "S3")
    import pccap.harness.stage_s4  # noqa: F401  (registers "S4")
    import pccap.harness.stage_s5  # noqa: F401  (registers "S5")

    runner = RUNNERS.get(args.stage)
    if runner is None:
        print(f"no runner registered for stage {args.stage}", file=sys.stderr)
        return 3
    rd = run_dir_for(args)
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "config.json").write_text(json.dumps(cfg, indent=1))
    try:
        result = runner({"config": cfg, "manifest": manifest, "run_dir": rd}, rd)
        cfg.update(result or {})
        cfg.setdefault("status", RunStatus.complete.value)
    except Exception as exc:  # Op. rule 8: no silent fallback
        write_error_json(rd, exc, None, traceback.format_exc())
        cfg["status"] = RunStatus.correctness_failure.value
        (rd / "config.json").write_text(json.dumps(cfg, indent=1))
        print(f"correctness_failure: {exc}", file=sys.stderr)
        return 1
    (rd / "config.json").write_text(json.dumps(cfg, indent=1))
    print(f"{cfg['status']}: {rd}")
    return 0 if cfg["status"] in (RunStatus.complete.value, RunStatus.resource_stop.value) else 1
