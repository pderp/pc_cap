"""P2: final-tree CPU audit; live inputs are read-only, regeneration is isolated."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
BASE = ROOT / ".worktrees/reproduce_final_20260913"
COPY = BASE / "pc_cap"
RES = ASSETS / "tmp/reproduce_final_20260913"
OUT = ROOT / "logs/reproduce_final_20260913"
PYTHON = ASSETS / "envs/venv-check-plan6-df/bin/python"
EXP = "frozen-confirmatory-v2-84126123"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def main():
    started = time.monotonic()
    for p in (COPY, RES, OUT):
        p.mkdir(parents=True, exist_ok=False)
    (BASE / "assets").symlink_to(RES, target_is_directory=True)
    spec = importlib.util.spec_from_file_location("prior_audit", ROOT / "scripts/reproduce_preaudit_round4.py")
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    copied = {}
    for rel in filter(None, tracked):
        if (rel.startswith("logs/") or rel == "manifests/frozen.json"
                or (rel.startswith("manifests/confirm/") and not rel.endswith("/SHA256SUMS"))
                or rel.startswith(("results/S4/", "results/S5/", "results/S7/", "results/S8/"))
                or rel.startswith("results/S3/dev/grammar/C2/BP/h/0/0/")):
            continue
        src, dst = ROOT / rel, COPY / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied[rel] = sha(dst)
    for rel in ("data/raw", "data/prepared/lm", "models/gpt2", "models/grammar", "reference/gpt2", "third_party/GRACE"):
        src, dst = ASSETS / rel, RES / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", "-aL", "--reflink=auto", str(src), str(dst)], check=True)
    (RES / "tmp").mkdir()
    env = os.environ.copy()
    env.update(P=str(PYTHON), PYTHONPATH=str(COPY / "src") + ":" + str(COPY), PCCAP_ASSETS=str(RES),
               PCCAP_HDPC_PATH=str(ROOT.parent / "llm-by-neural-predictive-coding"), HF_HOME=str(RES / "hf_cache"),
               XDG_CACHE_HOME=str(RES / "cache"), TMPDIR=str(RES / "tmp"), PYTHONDONTWRITEBYTECODE="1",
               CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu", OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2",
               MKL_NUM_THREADS="2", RAYON_NUM_THREADS="2", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
               GIT_OPTIONAL_LOCKS="0", GIT_CEILING_DIRECTORIES=str(BASE),
               PYTEST_ADDOPTS="-p no:cacheprovider --basetemp=" + str(RES / "pytest"))
    setup = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
             "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
             "copy": str(COPY), "resources": str(RES), "python": str(PYTHON), "copied_sources": copied,
             "environment": {k: env[k] for k in ("PYTHONPATH", "PCCAP_ASSETS", "PCCAP_HDPC_PATH", "JAX_PLATFORMS", "CUDA_VISIBLE_DEVICES", "GIT_CEILING_DIRECTORIES")},
             "excluded": "Sealed payloads, production frozen manifest, S4/S5/S7/S8 outputs, and the C2 grammar p0 destination (fresh run).",
             "deferred_commands": [{"command": c, "reason": reason} for c, reason in prior.DEFERRED[:-1]],
             "limits": "No final freeze or sealed sampling. Analysis commands below use the sanctioned loader on live read-only inputs and new --out paths. GPU commands are classified, not executed. Source copy has no git metadata."}
    save(OUT / "setup.json", setup)
    rows = []

    def run(name, command, cwd=COPY, run_env=None, expected=0):
        print("START", name, flush=True)
        t0 = time.monotonic()
        with (OUT / f"{name}.txt").open("x") as log:
            try:
                p = subprocess.run(["bash", "--noprofile", "--norc", "-c", command], cwd=cwd, env=run_env or env,
                                   stdout=log, stderr=subprocess.STDOUT, timeout=900, check=False)
                code = p.returncode
            except subprocess.TimeoutExpired:
                code = 124
        row = {"name": name, "command": command, "cwd": str(cwd), "exit_code": code, "expected_exit": expected,
               "wall_seconds": time.monotonic() - t0, "log": f"{name}.txt"}
        rows.append(row)
        save(OUT / f"{name}.json", row)
        print("DONE", name, code, round(row["wall_seconds"], 2), flush=True)

    commands = list(prior.CPU[:24])
    commands[8] = (commands[8][0], "$P -m pccap.distill.data --parquet ../assets/data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet")
    commands[22] = (commands[22][0], "$P -m pccap.harness.freeze --draft --run-allowance-seconds 2400 --stage-allowance S4=97200 --stage-allowance S5=64800")
    for name, cmd in commands:
        run(name, cmd)
    # Only read-only live interfaces are used here; each analysis destination is new.
    live = env | {"PYTHONPATH": str(ROOT / "src") + ":" + str(ROOT), "PCCAP_ASSETS": str(ASSETS)}
    gen = OUT / "generated"
    gen.mkdir()
    run("25_resource_analysis", f"$P -m pccap.analysis.s4_05 --experiment-id {EXP} --out {shlex.quote(str(gen / 'resource_views.json'))}", ROOT, live)
    run("26_paired_analysis", f"$P -m pccap.analysis.s4_06 --dataset zsre --experiment-id {EXP} --out {shlex.quote(str(gen / 'paired_zsre.json'))}", ROOT, live)
    run("27_order_analysis", f"$P -m pccap.analysis.s7_03 --dataset zsre --arm C2 --experiment-id {EXP} --out {shlex.quote(str(gen / 'order_zsre_C2.json'))}", ROOT, live)
    run("28_progress_s4", "$P scripts/s4_progress.py --json", ROOT, live)
    run("29_progress_s5", "$P scripts/s4_progress.py --stage S5 --json", ROOT, live)
    for stage in ("S4", "S5"):
        run("30_queue_" + stage, "$P -m pccap.cli queue --dry-run --stage " + stage)
    confirm_cmd = "$P -m pccap.cli run --stage S4 --mode confirm --dataset zsre --arm C2 --realization 0 --perm 0 --manifest " + shlex.quote(str(ROOT / "manifests/confirm/zsre_r0.json")) + " --dry-run"
    run("31_final_tree_confirm_dryrun", confirm_cmd, ROOT, live, expected=2)
    # Extra positive control: materialize only the historical frozen source, never bypass the current-tree refusal.
    historical = BASE / "frozen_source"
    historical.mkdir()
    ref = "6b4b76918966487a4f0593bbe8f71d4decb89152"
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", ref, "src"], cwd=ROOT, text=True).splitlines()
    for rel in paths:
        dst = historical / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("xb") as f:
            f.write(subprocess.check_output(["git", "show", ref + ":" + rel], cwd=ROOT))
    (historical / "manifests").mkdir()
    shutil.copy2(ROOT / "manifests/frozen.json", historical / "manifests/frozen.json")
    old_env = live | {"PYTHONPATH": str(historical / "src") + ":" + str(historical)}
    run("32_frozen_tree_confirm_dryrun", confirm_cmd, historical, old_env)
    # s7_summary has no --out argument: copy its input records and render into the isolated root.
    for src in (ROOT / "results/S7" / EXP).rglob("reversals.json"):
        dst = COPY / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    run("33_s7_summary", "$P scripts/s7_summary.py")
    # Save only compact generated outputs, not the copied input tree or checkpoint payloads.
    selected = ["results/S7/summary.json", "results/S7/summary.md", "results/S3/dev/grammar/C2/BP/h/0/0/metrics.json",
                "results/S3/grammar_dev_matrix.json", "manifests/frozen.draft.json", "results/GRAM/competence.json",
                "results/S4/jobs.json", "results/S4/queue_summary_dryrun.json", "results/S5/queue_summary_dryrun.json"]
    for rel in selected:
        src = COPY / rel
        if src.is_file():
            dst = gen / "isolated" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    save(OUT / "summary.json", {"source_head": setup["source_head"], "commands": rows, "gpu_seconds": 0,
                                "wall_seconds": time.monotonic() - started,
                                "live_copied_inputs_changed": [p for p, h in copied.items() if sha(ROOT / p) != h],
                                "generated_sha256": {str(p.relative_to(OUT)): sha(p) for p in gen.rglob("*") if p.is_file()}})
    print("P2 AUDIT FINISHED", len(rows), "invocations", flush=True)


if __name__ == "__main__":
    main()
