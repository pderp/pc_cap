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
ASSETS_RUNS = Path(__import__("pccap").ASSETS_ROOT) / "runs"

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


def _src_tree_sha() -> str:
    """Hash of the installed package tree (the code that actually runs), matching freeze.py's record."""
    import pccap as _pkg
    from pccap.harness.freeze import tree_sha

    return tree_sha(Path(_pkg.__file__).resolve().parent)


def _stage_spent_seconds(stage: str, exp_id: str) -> float:
    """Accelerator seconds already recorded by completed runs of this experiment and stage (metrics.json ledger totals),
    excluding archived (``.superseded-``) attempts."""
    total = 0.0
    for mp in (RESULTS / stage / exp_id).rglob("metrics.json"):
        if ".superseded-" in str(mp):
            continue
        try:
            total += float(json.loads(mp.read_text()).get("ledger_totals", {}).get("total", {}).get("accel_seconds", 0.0))
        except Exception:
            continue
    return total


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


def experiment_id(args, frozen: dict | None, frozen_sha: str | None) -> str:
    """Run identity: ``dev`` in development, else the frozen manifest's name plus its hash prefix (R2-03)."""
    if args.mode != "confirm" or frozen is None:
        return "dev"
    return f"{frozen.get('name', 'frozen')}-{(frozen_sha or '')[:8]}"


def dataset_of(args, manifest: dict | None) -> str:
    """Dataset identity without opening a sealed payload: ``--dataset``, else the dev manifest's field,
    else the realization file name ``<dataset>_r<k>.json``."""
    if getattr(args, "dataset", None):
        return args.dataset
    if manifest is not None and manifest.get("dataset"):
        return str(manifest["dataset"])
    stem = Path(args.manifest).stem
    return stem.split("_r")[0] if "_r" in stem else stem


def run_dir_for(args, exp_id: str = "dev", dataset: str = "-") -> Path:
    return RESULTS / args.stage / exp_id / dataset / (args.arm or "none") / args.base / args.read / str(args.realization) / str(args.perm)


def main(args) -> int:
    import pccap

    mpath = Path(args.manifest)
    frozen_obj, frozen_sha, manifest = None, None, None
    if args.mode == "confirm":
        # §4.5 rule 4 (R2-02): the freeze is checked BEFORE any payload is opened; the realization file is
        # never read here — only the sanctioned loader (pccap.data.confirm) opens it, inside the stage.
        frozen = ROOT / "manifests" / "frozen.json"
        if not frozen.exists():
            print("REFUSED: confirm mode requires manifests/frozen.json (plan §4.5 rule 4)", file=sys.stderr)
            return 2
        frozen_obj, frozen_sha, errs = load_manifest(frozen, "confirm")
        if errs or frozen_obj.get("draft"):
            print("REFUSED: manifests/frozen.json is not a valid final frozen manifest:", file=sys.stderr)
            for e in errs or ["draft flag set"]:
                print("  -", e, file=sys.stderr)
            return 2
        if not mpath.name.endswith(".json") or not (mpath.exists()):
            print(f"REFUSED: realization manifest not found: {mpath}", file=sys.stderr)
            return 2
        ds = dataset_of(args, None)
        bound = (frozen_obj.get("dataset_ids") or {}).get(ds) or {}
        if mpath.name not in bound:
            print(f"REFUSED: {mpath.name} is not bound in frozen dataset_ids[{ds}]", file=sys.stderr)
            return 2
        msha = bound[mpath.name]  # the sealed file's hash as frozen; verified against the bytes by the loader
        if args.arm in (frozen_obj.get("arm_availability") or {}) and "unavailable" in frozen_obj["arm_availability"][args.arm]:
            print(f"REFUSED: arm {args.arm} is recorded unavailable in the frozen manifest", file=sys.stderr)
            return 2
        # V-06: the CLI identity must lie on the frozen schedule and match the frozen configuration
        if args.arm not in frozen_obj.get("arms", []) and args.arm not in (frozen_obj.get("substrate_arms") or {}):
            print(f"REFUSED: arm {args.arm} is not a frozen arm", file=sys.stderr)
            return 2
        if not (0 <= int(args.perm) < len(frozen_obj["order_seeds"])) or int(args.realization) not in frozen_obj["realizations"]:
            print(f"REFUSED: realization {args.realization} / perm {args.perm} outside the frozen schedule", file=sys.stderr)
            return 2
        if args.stage in ("S4",) and ((args.base != ("GRAM" if ds == "grammar" else "BP")) or args.read != frozen_obj["radii"]["read"]):
            print(f"REFUSED: S4 runs the BP base with read {frozen_obj['radii']['read']!r}; got base {args.base!r} read {args.read!r}", file=sys.stderr)
            return 2
        tree = _src_tree_sha()
        frozen_tree = (frozen_obj.get("code_commit") or {}).get("src_tree_sha256")
        if frozen_tree and tree != frozen_tree and not getattr(args, "allow_code_drift", False):
            print(f"REFUSED: src/pccap tree {tree[:12]} differs from the frozen {frozen_tree[:12]}; a post-freeze change needs a manifest version (S4-06); pass --allow-code-drift only for an approved fix", file=sys.stderr)
            return 2
        # V-04: stage allowance (explicitly None = not enforced; recorded as such)
        rules = frozen_obj.get("resource_rules") or {}
        stage_allow = (rules.get("stage_allowance_seconds") or {}).get(args.stage)
        run_allow = rules.get("run_allowance_seconds")
        if stage_allow is not None:
            spent = _stage_spent_seconds(args.stage, experiment_id(args, frozen_obj, frozen_sha))
            if spent + float(run_allow or 0.0) > float(stage_allow):
                print(f"REFUSED: stage {args.stage} allowance {stage_allow} s would be exceeded (spent {spent:.0f} s + run allowance {run_allow})", file=sys.stderr)
                return 5
    else:
        if not mpath.exists():
            print(f"manifest not found: {mpath}", file=sys.stderr)
            return 2
        manifest, msha, errs = load_manifest(mpath, args.mode)
        if errs:
            print(f"REFUSED: manifest {mpath} is not a valid {args.mode} manifest:", file=sys.stderr)
            for e in errs:
                print("  -", e, file=sys.stderr)
            return 2
        ds = dataset_of(args, manifest)
    exp_id = experiment_id(args, frozen_obj, frozen_sha)
    cfg = {
        "stage": args.stage,
        "arm": args.arm or "none",
        "base": args.base,
        "read": args.read,
        "dataset": ds,
        "realization": args.realization,
        "perm": args.perm,
        "manifest": str(mpath),
        "manifest_sha256": msha,
        "frozen_manifest_sha256": frozen_sha,
        "src_tree_sha256": _src_tree_sha() if args.mode == "confirm" else None,
        "run_allowance_seconds": ((frozen_obj.get("resource_rules") or {}).get("run_allowance_seconds") if frozen_obj else None),
        "stage_allowance_enforced": bool(frozen_obj and ((frozen_obj.get("resource_rules") or {}).get("stage_allowance_seconds") or {}).get(args.stage) is not None),
        "experiment_id": exp_id,
        "mode": args.mode,
        "task": getattr(args, "task", None),
        "code_commit": code_commit(),
        "base_hash_before": "",
        "status": RunStatus.running.value,
    }
    rd = run_dir_for(args, exp_id, ds)
    if args.dry_run:
        cfg["run_dir"] = str(rd)
        cfg["determinism"] = "deferred: the backend is initialized only after the lease is held (R2-05)"
        print(json.dumps(cfg, indent=1))
        return 0
    if (rd / "config.json").exists():  # rerun protection (R2-03/R2-05): existing outputs are never overwritten silently
        prev = json.loads((rd / "config.json").read_text())
        if not getattr(args, "force", False):
            print(f"REFUSED: {rd} already holds a run with status {prev.get('status')}; pass --force to archive it and rerun", file=sys.stderr)
            return 4
        import shutil
        import time as _t

        stamp = _t.strftime("%Y%m%dT%H%M%SZ", _t.gmtime())
        shutil.move(str(rd), f"{rd}.superseded-{stamp}")
        ck_old = ASSETS_RUNS / rd.relative_to(RESULTS)  # V-03: the external checkpoint directory is archived with the results
        if ck_old.exists():
            shutil.move(str(ck_old), f"{ck_old}.superseded-{stamp}")
    cfg["determinism"] = "set inside the lease"  # V-01: no backend discovery before the lease is held
    import pccap.harness.stage_s0  # noqa: F401  (registers "S0")
    import pccap.harness.stage_s3  # noqa: F401  (registers "S3")
    import pccap.harness.stage_s4  # noqa: F401  (registers "S4")
    import pccap.harness.stage_s5  # noqa: F401  (registers "S5")

    runner = RUNNERS.get(args.stage)
    if runner is None:
        print(f"no runner registered for stage {args.stage}", file=sys.stderr)
        return 3
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "config.json").write_text(json.dumps(cfg, indent=1))
    from contextlib import nullcontext

    from pccap.harness.lease import gpu_lease

    lease_ctx = nullcontext() if getattr(args, "no_lease", False) else gpu_lease(f"{args.stage}:{args.arm or 'none'}", stage=args.stage,
                                                                                 projected_seconds=float(getattr(args, "projected_seconds", 3600.0)))
    try:
        with lease_ctx:
            cfg["determinism"] = pccap.assert_determinism()  # runtime check (derp_review2 #8), after the lease is held
            (rd / "config.json").write_text(json.dumps(cfg, indent=1))
            result = runner({"config": cfg, "manifest": manifest, "frozen": frozen_obj, "run_dir": rd}, rd)
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
