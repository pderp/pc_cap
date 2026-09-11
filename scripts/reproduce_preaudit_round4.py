#!/usr/bin/env python3
"""Lane P: CPU command audit in an isolated source copy and resource tree.

The ENV-05 environment is reused without installation. Shells force CPU execution.
No confirmation payload, production output, active checkpoint, or GPU lease is used.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
COPY = ROOT / ".worktrees/reproduce_round4"
RESOURCES = ASSETS / "tmp/reproduce_round4"
OUT = ROOT / "logs/reproduce_round4"
PYTHON = ASSETS / "envs/venv-check-plan6-df/bin/python"

CPU = [
    ("01_environment", '$P -c "import pccap; print(pccap.__file__); print(pccap.determinism_report())"'),
    ("02_assets", "$P scripts/fetch_assets.py --verify"),
    ("03_schema", "$P -m pccap.harness.schema validate manifests/frozen.draft.json --kind manifest_frozen"),
    ("04_test_fast", 'make PY="$P" test-fast'),
    ("05_report_s0", "$P -m pccap.cli report --stage S0"),
    ("06_report_s1", "$P -m pccap.cli report --stage S1"),
    ("07_splits_audit", "$P -m pccap.data.splits --audit"),
    ("08_cr_distribution", "$P -m pccap.analysis.s3_05"),
    ("09_distill_data", "$P -m pccap.distill.data --parquet assets/data/raw/openwebtext/hf/plain_text/train-00000-of-00080.parquet"),
    ("10_pilot_compare", "$P scripts/reg_pilot_compare.py --run pilot-100"),
    ("11_merge_throughput", "$P scripts/merge_throughput.py results/S2/throughput_baselines.json"),
    ("12_d1", "$P -m pccap.analysis.d1"),
    ("13_short_editing", "$P -m pccap.analysis.s3_04"),
    ("14_d2", "$P -m pccap.analysis.s3_06"),
    ("15_grammar_generator", "JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_generator"),
    ("16_grammar_training", "JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_model --steps 3000 --no-lease"),
    ("17_grammar_competence", "JAX_PLATFORMS=cpu $P scripts/grammar_competence.py"),
    ("18_grammar_streams", "JAX_PLATFORMS=cpu $P -m pccap.data.grammar_streams"),
    ("19_grammar_tracing", "JAX_PLATFORMS=cpu $P -m pccap.fixtures.tracing"),
    ("20_grammar_calibration", "JAX_PLATFORMS=cpu $P -m pccap.fixtures.grammar_eval"),
    ("21_grammar_run", "JAX_PLATFORMS=cpu $P -m pccap.cli run --stage S3 --arm C2 --dataset grammar --manifest manifests/dev/s3_grammar_dev.json --no-lease"),
    ("22_grammar_analysis", "JAX_PLATFORMS=cpu $P -m pccap.analysis.s3_03"),
    ("23_draft", "$P -m pccap.harness.freeze --draft"),
    ("24_schedule", "$P -m pccap.harness.schedule"),
    ("25_resource_analysis", "$P -m pccap.analysis.s4_05"),
    ("26_paired_analysis", "$P -m pccap.analysis.s4_06 --dataset zsre"),
    ("27_order_analysis", "$P -m pccap.analysis.s7_03 --dataset zsre --arm C2"),
]

DEFERRED = [
    ("make test-gpu", "GPU subset; not executed in this CPU lane"),
    ("$P -m pytest -q tests/controls -m gpu", "GPU controls; selector excludes CPU PC-1/4/5/6/7 and PC-10"),
    ("$P -m pccap.analysis.s1_p2", "BP substrate GPU lease"),
    ("$P -m pccap.analysis.s1_p3", "BP substrate GPU lease"),
    ("$P -m pccap.analysis.s1_p5", "BP substrate GPU lease"),
    ("$P -m pccap.analysis.s1_p6", "BP substrate GPU lease"),
    ("$P -m pccap.analysis.s1_p1 --epc-weights /home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz", "ePC substrate GPU lease"),
    ("$P -m pccap.analysis.s1_p3 --epc-weights <same npz>", "Illustrative placeholder; GPU ePC rows"),
    ("$P -m pccap.data.streams --build", "Teacher generations under GPU lease; regenerates reserved pools"),
    ("$P -m pccap.cap.calibrate", "BP calibration GPU lease"),
    ("$P -m pccap.cap.calibrate --epc-weights <npz> --label EPC", "Illustrative placeholder; ePC calibration GPU lease"),
    ("$P -m pccap.harness.stage_s2 --n 30", "GPU A screening"),
    ("$P scripts/reg_timing_probe.py --micro 5 --timed 2", "GPU timing lease"),
    ("results/REG/run_reg02_v2.sh 500 5400", "REG-02 GPU run; owned by orchestrator"),
    ("$P -m pccap.distill.preflight --update-assets", "GPU preflight and production manifest update"),
    ("$P -m pccap.harness.stage_s2_throughput --n 100 --arms C0 C1 C2 CR --out results/S2/throughput.json", "GPU throughput lease"),
    ("$P -m pccap.harness.stage_s2_throughput --arms B0 B1 B3 --out results/S2/throughput_baselines.json --tag baselines", "GPU throughput lease"),
    ("$P -m pccap.cli run --stage S3 --arm C2 --manifest manifests/dev/s3_smoke.json", "Real-base development GPU lease"),
    ("$P scripts/sample_confirm.py", "Sealed realization creation is outside this development pre-audit"),
    ("$P -m pccap.harness.freeze --final --i-am-the-lead [--accept-unavailable <pending…>]", "Lead-only act; illustrative optional syntax"),
    ("$P -m pccap.cli run --stage S4 --mode confirm --dataset zsre --arm C2 --realization 0 --perm 0 --manifest manifests/confirm/zsre_r0.json", "Production confirmation execution; GPU and lead freeze required"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    for p in (COPY, RESOURCES, OUT):
        p.mkdir(parents=True, exist_ok=False)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    copied, excluded = {}, []
    for rel in files:
        if not rel:
            continue
        if ((rel.startswith("manifests/confirm/") and not rel.endswith("/SHA256SUMS"))
                or rel == "manifests/frozen.json"
                or rel.startswith(("results/S4/", "results/S5/", "results/S7/"))):
            excluded.append(rel)
            continue
        src, dst = ROOT / rel, COPY / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied[rel] = sha(dst)
    # Reflink-capable copies, never hard links or shared writable symlinks.
    for rel in ("data/raw", "data/prepared/lm", "models/gpt2", "models/grammar", "reference/gpt2", "third_party/GRACE"):
        src, dst = ASSETS / rel, RESOURCES / rel
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-aL", "--reflink=auto", str(src), str(dst)], check=True)
    (RESOURCES / "tmp").mkdir()
    env = os.environ.copy()
    env.update(P=str(PYTHON), PYTHONPATH=str(COPY / "src") + ":" + str(COPY),
               PCCAP_ASSETS=str(RESOURCES), HF_HOME=str(RESOURCES / "hf_cache"),
               XDG_CACHE_HOME=str(RESOURCES / "cache"), TMPDIR=str(RESOURCES / "tmp"),
               PYTHONDONTWRITEBYTECODE="1", CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu",
               OPENBLAS_NUM_THREADS="2", OMP_NUM_THREADS="2", HF_HUB_OFFLINE="1",
               TRANSFORMERS_OFFLINE="1", GIT_OPTIONAL_LOCKS="0",
               PYTEST_ADDOPTS="-p no:cacheprovider --basetemp=" + str(RESOURCES / "pytest"))
    manifest = {"time_utc": datetime.now(timezone.utc).isoformat(), "source_head_at_copy": head,
                "copied_files_sha256": copied, "excluded_without_reading_payloads": excluded,
                "snapshot": str(COPY), "resource_copy": str(RESOURCES), "python": str(PYTHON),
                "environment": {k: env[k] for k in ("PYTHONPATH", "PCCAP_ASSETS", "CUDA_VISIBLE_DEVICES", "JAX_PLATFORMS", "PYTEST_ADDOPTS", "OMP_NUM_THREADS")},
                "deferred_commands": [{"command": c, "reason": r} for c, r in DEFERRED],
                "caveats": ["Source is a file copy; git metadata queries can discover the parent checkout.",
                            "Resource hashes and read-only hard-coded snapshot references can still name original assets.",
                            "Confirmation realization payloads and production S4/S5/S7 results are deliberately absent.",
                            "Preserved historical development results are inputs, not newly reproduced experiments."]}
    with (OUT / "setup.json").open("x") as f:
        json.dump(manifest, f, indent=2)
    summaries = []
    for name, command in CPU:
        print("START", name, flush=True)
        t = time.monotonic()
        with (OUT / (name + ".txt")).open("x") as log:
            process = subprocess.run(["bash", "--noprofile", "--norc", "-c", command], cwd=COPY, env=env,
                                     stdout=log, stderr=subprocess.STDOUT, check=False)
        result = {"name": name, "command": command, "exit_code": process.returncode,
                  "wall_seconds": time.monotonic()-t, "log": str((OUT / (name + ".txt")).relative_to(ROOT))}
        with (OUT / (name + ".json")).open("x") as f:
            json.dump(result, f, indent=2)
        summaries.append(result)
        print("DONE", name, process.returncode, round(result["wall_seconds"], 2), flush=True)
    # Preserve generated snapshot evidence in the repo; the ignored snapshot remains
    # a navigable audit resource, and this inventory makes its outputs reviewable.
    changed = {}
    for path in COPY.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            rel = path.relative_to(COPY).as_posix()
            current = sha(path)
            if copied.get(rel) != current:
                changed[rel] = current
    summary = {"commands": summaries, "gpu_seconds": 0, "wall_seconds": time.monotonic()-started,
               "changed_snapshot_files": changed,
               "production_source_changes_during_run": [rel for rel, digest in copied.items()
                                                       if (ROOT / rel).exists() and sha(ROOT / rel) != digest]}
    with (OUT / "summary.json").open("x") as f:
        json.dump(summary, f, indent=2)
    print("CPU pre-audit complete", flush=True)


if __name__ == "__main__":
    main()
