"""ENV-05: recreate dependencies in a new auxiliary environment from the unchanged lock."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def filtered_lock(text):
    kept, skipped = [], []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("-e ") and re.fullmatch(r"-e git\+ssh://[^ \t]+#egg=pccap", stripped):
            skipped.append(stripped)
        elif stripped and not stripped.startswith("#") and not re.fullmatch(r"[A-Za-z0-9_.-]+==[^ \t;]+", stripped):
            raise ValueError("unsupported lock entry; review without rewriting the lock")
        else:
            kept.append(line)
    if len(skipped) != 1:
        raise ValueError("expected exactly one private editable pccap entry")
    return "".join(kept), skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--venv", type=Path, default=ROOT.parent / "assets/envs/venv-check")
    ap.add_argument("--dry-run", action="store_true", help="resolve locked dependencies without installing them")
    ap.add_argument("--out", type=Path, help="new evidence directory inside pc_cap; default results/ENV05/<UTC>")
    args = ap.parse_args(argv)
    if sys.version_info[:2] != (3, 12):
        ap.error("run with Python 3.12 (set PCCAP_SETUP_PYTHON for the shell wrapper)")
    target = args.venv.expanduser().resolve()
    assets = (ROOT.parent / "assets").resolve()
    if not target.is_relative_to(assets / "envs"):
        ap.error("the new environment must be inside the sibling assets/envs directory")
    if target.exists() or args.venv.is_symlink():
        ap.error("refusing to replace an existing environment")
    if target == (ROOT.parent / "venv").resolve():
        ap.error("the active project environment cannot be a setup target")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = (args.out or ROOT / "results/ENV05" / timestamp).resolve()
    if not evidence.is_relative_to(ROOT) or evidence.exists():
        ap.error("evidence directory must be a new path inside pc_cap")
    original = (ROOT / "requirements.lock").read_bytes()
    filtered, skipped = filtered_lock(original.decode())
    revision = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True)
    evidence.mkdir(parents=True)
    resources = assets / "tmp" / ("env05-" + timestamp)
    resources.mkdir(parents=True, exist_ok=False)
    lockfile = resources / "requirements.filtered.lock"
    with lockfile.open("x") as out:
        out.write(filtered)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1",
           "PIP_CACHE_DIR": str(resources / "pip-cache"), "TMPDIR": str(resources),
           "HF_HOME": str(assets / "hf_cache"), "PCCAP_ASSETS": str(assets),
           "CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "GIT_OPTIONAL_LOCKS": "0"}
    commands = []
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "python": sys.executable,
              "python_version": sys.version, "target": str(target), "source_checkout": str(ROOT),
              "source_revision": revision, "source_was_dirty": bool(dirty), "source_status": dirty.splitlines(),
              "requirements_lock_sha256": hashlib.sha256(original).hexdigest(),
              "filtered_requirements_sha256": hashlib.sha256(filtered.encode()).hexdigest(),
              "skipped_entry": skipped[0], "dry_run": args.dry_run,
              "package_install": "pip install --no-deps --no-build-isolation -e <local checkout>",
              "resources": str(resources), "gpu_use": False}

    def invoke(name, command):
        commands.append({"name": name, "argv": command})
        with (evidence / (name + ".txt")).open("x") as log:
            proc = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        commands[-1]["exit_code"] = proc.returncode
        print(name, "exit", proc.returncode, "log", evidence / (name + ".txt"), flush=True)
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, command)

    rc = 0
    try:
        invoke("create_venv", [sys.executable, "-B", "-m", "venv", str(target)])
        python = str(target / "bin/python")
        command = [python, "-B", "-m", "pip", "install", "--no-input", "--no-compile"]
        if args.dry_run:
            command += ["--dry-run"]
        command += ["-r", str(lockfile)]
        invoke("resolve_lock" if args.dry_run else "install_lock", command)
        if args.dry_run:
            result["status"] = "dependency_resolution_passed"
            result["local_package_installed"] = False
            result["determinism_report"] = "pending real installation; resolution is not a tested environment"
        else:
            invoke("install_checkout", [python, "-B", "-m", "pip", "install", "--no-input", "--no-compile",
                                        "--no-deps", "--no-build-isolation", "-e", str(ROOT)])
            invoke("pip_check", [python, "-B", "-m", "pip", "check"])
            invoke("determinism", [python, "-B", "-c",
                                  "import json,pccap; print(json.dumps(pccap.determinism_report(), indent=2))"])
            print((evidence / "determinism.txt").read_text())
            result["status"] = "environment_created_cpu_probe_passed"
            result["local_package_installed"] = True
    except (OSError, subprocess.CalledProcessError) as exc:
        rc = 1
        result["status"] = "failed"
        result["error"] = str(exc)
    finally:
        result["commands"] = commands
        result["lock_unchanged"] = (ROOT / "requirements.lock").read_bytes() == original
        with (evidence / "setup.json").open("x") as out:
            json.dump(result, out, indent=2)
            out.write("\n")
    print("setup record:", evidence / "setup.json")
    if not result["lock_unchanged"]:
        raise RuntimeError("lock changed concurrently; inspect source provenance")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
