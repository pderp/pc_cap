"""REP-1: regenerate saved-result reports/figures in fresh directories, CPU only.

No GPU dispatch, model execution, publication or modification of canonical
directories. Native reporting adapters are in aw.refresh_report_steps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Ordered dependencies: immutable completed studies first, then available reader
# vectors/tails, extension/interface reports, figures/deck, and integrity checks.
DEPENDENCIES = {
    "ht15": (),
    "stage4": ("ht15",),
    "pc-default": (),
    "pc-matched": (),
    "pc-controls": ("pc-default", "pc-matched"),
    "pc-settings": ("pc-default",),
    "aw-b": (),
    "kappa": (),
    "ht13": (),
    "ht17": (),
    "pc-reader": ("ht17",),
    "option-r": (),
    "aw-l": (),
    "figures": ("pc-default", "pc-controls", "aw-b", "kappa", "ht13", "ht17"),
    "deck": ("stage4", "figures", "pc-reader", "option-r", "aw-l"),
    "audit": ("deck", "pc-settings"),
}
CPU_ENV = dict(
    JAX_PLATFORMS="cpu",
    CUDA_VISIBLE_DEVICES="",
    PYTHONDONTWRITEBYTECODE="1",
    OPENBLAS_NUM_THREADS="1",
    OMP_NUM_THREADS="1",
    MKL_NUM_THREADS="1",
    MPLBACKEND="Agg",
)


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def ordered_steps(requested):
    wanted = set()

    def visit(name):
        if name not in DEPENDENCIES:
            raise ValueError(f"unknown CPU report step: {name}")
        if name in wanted:
            return
        for dependency in DEPENDENCIES[name]:
            visit(dependency)
        wanted.add(name)

    for name in requested or DEPENDENCIES:
        visit(name)
    return [name for name in DEPENDENCIES if name in wanted]


def difference(old, new):
    return dict(
        added=sorted(new.keys() - old.keys()),
        removed=sorted(old.keys() - new.keys()),
        changed=sorted(k for k in old.keys() & new.keys() if old[k] != new[k]),
    )


def input_inventory(root=ROOT):
    """Terminal metadata, code and authored sources; excludes live metrics/logs.

    Each generator additionally binds the raw arrays/checkpoints it actually
    reads. This inventory is a change detector, not a replacement for those hashes.
    """
    paths = set((root / "aw").glob("*.py"))
    paths.update((root / "docs/presentation/deck_v3").glob("*"))
    paths.update((root / "docs/additional_work").glob("*_report.md"))
    paths.update(
        root / n
        for n in (
            "docs/talk_claim_ledger_v7.md",
            "docs/presentation/qa.md",
            "requirements.lock",
            "manifests/additional_work/run_matrix_R_v1.json",
            "manifests/revision_v1/kappa_pilot_v3.json",
            "logs/R1/reports/triplet/summary.json",
            "logs/R1/reports/comparators-270/report.json",
            "logs/R1/reports/comparators-270/accounting.json",
            "logs/R1/operations/HALT_REPORT/d11-report.json",
        )
    )
    terminal = {
        "report.json",
        "cost.json",
        "finish.json",
        "summary.json",
        "plan.json",
        "process.json",
        "session-finish.json",
        "session-start.json",
        "resume.json",
    }
    for family in ("PC-v0", "PC-v1", "AW-B", "PC-reader", "AW-L"):
        paths.update(
            p
            for p in (root / "results/additional_work" / family).rglob("*.json")
            if p.name in terminal
        )
    paths.update((root / "logs/additional_work/R/queue").rglob("*.json"))
    return {str(p.resolve()): sha(p) for p in sorted(paths) if p.is_file()}


def execute(
    output, assets, steps, *, previous=None, root=ROOT, inventory=input_inventory, launch=None
):
    """Injectable launcher/inventory allow real filesystem failure tests without JAX."""
    output, assets = Path(output).resolve(), Path(assets).resolve()
    if output.exists() or assets.exists():
        raise FileExistsError("both report and figure destinations must be new")
    if output == assets or output.is_relative_to(assets) or assets.is_relative_to(output):
        raise ValueError("report and figure destinations must be disjoint")
    selected = ordered_steps(steps)
    before = inventory(root)
    old = json.loads(Path(previous).read_text())["input_hashes"] if previous else {}
    output.mkdir(parents=True, exist_ok=False)
    assets.mkdir(parents=True, exist_ok=False)
    (output / "documents").mkdir()
    (output / "commands").mkdir()
    state = dict(
        schema="supplemental-refresh-v1",
        status="running",
        created_utc=datetime.now(timezone.utc).isoformat(),
        output=str(output),
        assets=str(assets),
        input_hashes=before,
        previous=str(previous) if previous else None,
        changes_since_previous=difference(old, before),
        cpu_environment=CPU_ENV,
        steps=[],
        gpu_seconds=0,
        model_calls=0,
        publication="staged only; narrative review and explicit promotion remain required",
    )
    start = time.monotonic()
    save(output / "refresh.json", state)
    env = dict(os.environ, **CPU_ENV, MPLCONFIGDIR=str(assets / "matplotlib-cache"))
    for step in selected:
        command = [
            sys.executable,
            "-m",
            "aw.refresh_report_steps",
            "--step",
            step,
            "--output",
            str(output),
            "--assets",
            str(assets),
        ]
        log = output / "commands" / f"{step}.log"
        item = dict(step=step, command=command, log=str(log), status="running")
        state["steps"].append(item)
        save(output / "refresh.json", state)
        began = time.monotonic()
        print(f"{step}: starting CPU report", flush=True)
        try:
            with log.open("w") as handle:
                if launch:
                    code = launch(command, root, env, handle)
                else:
                    code = subprocess.run(
                        command,
                        cwd=root,
                        env=env,
                        stdout=handle,
                        stderr=subprocess.STDOUT,
                        check=False,
                    ).returncode
            item.update(
                returncode=code,
                wall_seconds=time.monotonic() - began,
                status="complete" if code == 0 else "failed",
            )
            if code:
                raise RuntimeError(f"CPU step {step} failed ({code}); see {log}")
        except Exception as exc:
            item.update(status="failed", error=str(exc), wall_seconds=time.monotonic() - began)
            state.update(status="failed", wall_seconds=time.monotonic() - start)
            save(output / "refresh.json", state)
            raise
        save(output / "refresh.json", state)
        print(f"{step}: complete ({item['wall_seconds']:.2f}s)", flush=True)
    try:
        if launch is None:
            from aw.reproduction_catalog import build

            build(output, state)
        # Artifacts carry detailed source manifests; exclude the self-referential
        # receipt and disposable MPL cache from the final output hashes.
        state["outputs_sha256"] = {
            str(p): sha(p)
            for directory in (output, assets)
            for p in sorted(directory.rglob("*"))
            if p.is_file() and p != output / "refresh.json" and "matplotlib-cache" not in p.parts
        }
        drift = difference(before, inventory(root))
        state.update(
            status="complete_with_input_changes" if any(drift.values()) else "complete",
            changes_during_refresh=drift,
            wall_seconds=time.monotonic() - start,
        )
    except Exception as exc:
        state.update(
            status="failed",
            phase="catalog/output verification",
            error=str(exc),
            wall_seconds=time.monotonic() - start,
        )
        save(output / "refresh.json", state)
        raise
    save(output / "refresh.json", state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--previous", type=Path, help="previous refresh.json, for input-change comparison"
    )
    parser.add_argument(
        "--steps", nargs="+", choices=tuple(DEPENDENCIES), help="dependency closure; default all"
    )
    parser.add_argument(
        "--plan", action="store_true", help="print CPU steps and destinations without writing"
    )
    args = parser.parse_args()
    output = args.output.resolve()
    base = ROOT / "logs/additional_work/reproductions"
    if not output.is_relative_to(base) or output == base:
        parser.error("fresh output must be below logs/additional_work/reproductions/")
    assets = ROOT.parent / "assets/presentation-materials/reproductions" / output.relative_to(base)
    if args.plan:
        print(
            json.dumps(
                dict(
                    output=str(output),
                    assets=str(assets),
                    steps=ordered_steps(args.steps),
                    cpu_environment=CPU_ENV,
                ),
                indent=2,
            )
        )
        return
    record = execute(output, assets, args.steps, previous=args.previous)
    print(json.dumps({k: record[k] for k in ("status", "wall_seconds", "output", "assets")}))


if __name__ == "__main__":
    main()
