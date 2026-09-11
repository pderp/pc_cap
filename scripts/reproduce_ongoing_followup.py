"""Lane P delta audit: fresh CPU shells and isolated, additive outputs only."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / ".worktrees/ongoing_followup_20260911"
OUT = ROOT / "logs/ongoing_followup_20260911"
TMP = ROOT.parent / "assets/tmp/ongoing_followup_20260911"
PYTHON = ROOT.parent / "assets/envs/venv-check-plan6-df/bin/python"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for path in (COPY, OUT, TMP):
        path.mkdir(parents=True, exist_ok=False)
    copied = {}
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    exact = {"docs/spec_defects.md", "docs/decisions.md", "docs/REPRODUCE.md", "requirements.lock",
             "docs/pc_cap_month_plan_readable.pdf", "scripts/s4_progress.py", "pyproject.toml",
             "results/ENV/kappa.json", "results/S2/grace_jax/pc10.json", "results/S5/projection.json",
             "tests/harness/test_confirm_cli.py"}
    for rel in tracked:
        if not rel:
            continue
        wanted = (rel in exact or rel.startswith("src/")
                  or (rel.startswith("manifests/") and not rel.startswith("manifests/confirm/")
                      and rel not in {"manifests/frozen.json", "manifests/frozen.draft.json"})
                  or rel == "manifests/confirm/SHA256SUMS"
                  or (rel.startswith("results/S2/") and rel.count("/") == 2 and rel.endswith(".json")))
        if not wanted:
            continue
        src, dst = ROOT / rel, COPY / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("xb") as f:
            f.write(src.read_bytes())
        copied[rel] = digest(dst)
    env = os.environ.copy()
    env.update(P=str(PYTHON), PYTHONPATH=str(COPY / "src") + ":" + str(COPY),
               PCCAP_HDPC_PATH=str(ROOT.parent / "llm-by-neural-predictive-coding"),
               PYTHONDONTWRITEBYTECODE="1", CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu",
               OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", MKL_NUM_THREADS="2",
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HOME=str(TMP / "hf"),
               TMPDIR=str(TMP), XDG_CACHE_HOME=str(TMP / "cache"), GIT_OPTIONAL_LOCKS="0")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    frozen_bytes = (ROOT / "manifests/frozen.json").read_bytes()
    frozen = json.loads(frozen_bytes)
    exp_id = frozen["name"] + "-" + hashlib.sha256(frozen_bytes).hexdigest()[:8]
    records = []

    def run(name, command, cwd=COPY, expected=0):
        start = time.monotonic()
        print("START", name, flush=True)
        with (OUT / (name + ".txt")).open("x") as log:
            p = subprocess.run(["bash", "--noprofile", "--norc", "-c", command], cwd=cwd, env=env,
                               stdout=log, stderr=subprocess.STDOUT, timeout=180, check=False)
        rec = {"name": name, "command": command, "cwd": str(cwd), "exit_code": p.returncode,
               "expected_exit": expected, "wall_seconds": time.monotonic()-start}
        records.append(rec)
        print("DONE", name, p.returncode, flush=True)
        return p.returncode

    run("01_cpu_environment", '$P -c "import pccap; print(pccap.__file__); print(pccap.determinism_report())"')
    run("02_draft_allowances", "$P -m pccap.harness.freeze --draft --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800")
    run("03_draft_schedule", "$P -m pccap.harness.schedule")
    run("04_resource_empty", f"$P -m pccap.analysis.s4_05 --experiment-id {exp_id}")
    run("05_pairs_empty", f"$P -m pccap.analysis.s4_06 --dataset zsre --experiment-id {exp_id}")
    run("06_orders_empty", f"$P -m pccap.analysis.s7_03 --dataset zsre --arm C2 --experiment-id {exp_id}")
    run("07_progress_empty", "$P scripts/s4_progress.py --json")
    # This copies the existing lead-authored freeze; it neither creates a new CP-E act
    # nor imports any sealed realization. Queue calls below are dry-run only.
    with (COPY / "manifests/frozen.json").open("xb") as f:
        f.write(frozen_bytes)
    run("08_frozen_schedule", "$P -m pccap.harness.schedule --out results/S4/jobs_frozen.json")
    run("09_s4_dry_queue", "$P -m pccap.cli queue --jobs results/S4/jobs_frozen.json --dry-run")
    run("10_s5_dry_queue", "$P -m pccap.cli queue --jobs results/S4/jobs_frozen.json --stage S5 --dry-run")
    tests = ["test_s4_02_allowances_on_the_freeze_command", "test_queue_executor_resumes_continues_on_failure_and_stops_on_refusal",
             "test_s5_jobs_follow_the_s4_jobs_and_reuse_sb", "test_loader_accepts_resource_bindings_of_other_datasets",
             "test_queue_stops_on_systematic_failures_and_archives_stale_attempts"]
    selector = " ".join("tests/harness/test_confirm_cli.py::" + x for x in tests)
    run("11_changed_path_regressions", "$P -m pytest -q " + selector + " -p no:cacheprovider --basetemp=" + shlex.quote(str(TMP / "pytest")))
    # Progress has an explicit read-only interface; use the live script in a fresh shell.
    run("12_live_progress", "$P scripts/s4_progress.py --json", cwd=ROOT)
    generated = {}
    for path in COPY.rglob("*"):
        if path.is_file() and path.relative_to(COPY).as_posix() not in copied:
            rel = path.relative_to(COPY)
            dst = OUT / "generated" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open("xb") as f:
                f.write(path.read_bytes())
            generated[str(rel)] = digest(dst)
    changed_copies = [rel for rel, old in copied.items() if digest(COPY / rel) != old]
    assert not changed_copies, changed_copies
    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "source_head": head,
        "prior_audit_head": "0d6e8d0a9f513ba7813b86074093b2bf26db9626", "copied_sources": copied,
        "commands": records, "generated": generated, "existing_copied_inputs_changed": changed_copies,
        "live_sources_changed_since_copy": [rel for rel, old in copied.items() if digest(ROOT / rel) != old],
        "gpu_seconds": 0, "sealed_payloads_copied_or_read": False,
        "scope": "Changed CPU commands and affected regressions only. Empty analysis outputs do not establish complete paired research. Final freeze and actual queues were not executed.",
    }
    with (OUT / "summary.json").open("x") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print("DONE: follow-up audit", flush=True)


if __name__ == "__main__":
    main()
