"""Owner driver: paired ordinary-text harm readout for the fixed-v5 credit run (PC-6 adapter + PC-5 readout).

Capstan, 2026-09-27. Integrates Capex's pieces without changing them: the run's checkpoint bindings
(``checkpoint-300.json["snapshot"]``), ``aw.pc_v1_run.construct`` for the original BP base with the EPC interface and
the selected reader, ``aw.pc_v1_readout.PCPositionBatchReader.from_checkpoint`` for strict restoration, and
``aw.pc_harm_readout.read_arm`` / ``pair`` for the scoring on the full 245,237-position inventory (``selection("v5")``).
Costs count against the shared eight-hour readout ceiling. GPU only, under the exclusive lease, with the project-only
occupancy guard.

    JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src:. ../venv/bin/python -m aw.pc_v1_harm --execute \
        --run results/additional_work/PC-v1/replication-4-20260927 \
        --output results/additional_work/PC-v1/harm/pc-v1-4-20260927 --batch-size 16 --wall-seconds 14400
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from aw.pc_harm_readout import CUTOFF, dump, pair, read_arm, selection, sha, table_block, wall_limit
from aw.pc_v0 import blocking_cuda_processes
from aw.pc_v1_readout import PCPositionBatchReader
from aw.pc_v1_run import construct, plan

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/additional_work/PC-v1/harm"
CHECKPOINT = 300


def load_cells(run: Path) -> list[dict]:
    cells = json.loads((run / "plan.json").read_bytes())["cells"]
    rows = []
    for c in cells:
        name = f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        d = run / name
        finish = json.loads((d / "finish.json").read_bytes())
        if finish.get("status") != "complete":
            raise ValueError(f"readout requires a completed group; {name} is {finish.get('status')}")
        cp = json.loads((d / f"checkpoint-{CHECKPOINT}.json").read_bytes())
        binding = cp["snapshot"]
        if binding["credit"] != {"SE-A": "adjoint", "SE-E": "error"}[c["arm"]] or binding["iters"] != 8:
            raise ValueError(f"{name}: checkpoint credit/iters differ from the planned arm")
        rows.append(dict(c, name=name, directory=str(d), binding=binding, checkpoint_sha256=sha(d / f"checkpoint-{CHECKPOINT}.json")))
    return rows


def run(run_dir: str, output: str, *, wall_seconds: int, batch_size: int) -> dict:
    out = Path(output).resolve()
    if not out.is_relative_to(OUTPUT) or out == OUTPUT:
        raise ValueError(f"new output must be below {OUTPUT}")
    if not 0 < wall_seconds <= 28800 or not 1 <= batch_size <= 32:
        raise ValueError("readout allowance must fit the shared 8-hour ceiling; batch size 1..32")
    run_path = Path(run_dir).resolve()
    rows = load_cells(run_path)
    spec = plan()
    import jax

    from pccap.harness.lease import gpu_lease

    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cost = dict(status="failed", cost_scope="fixed-v5 harm readout only", shared_ceiling_seconds=28800, run=str(run_path))
    report = dict(
        smoke=False,  # required by table_block
        run=str(run_path), checkpoint=CHECKPOINT, population=spec["population"], selection=None, cells=[], pairs=[],
        sources_sha256={}, note="Fixed-v5 credit arms restored from their checkpoint-300 snapshots; own cap-off reference "
        "(original base = cap-off base for this intervention); descriptive paired positions.",
    )
    try:
        allowance = min(wall_seconds, CUTOFF - time.time())
        if allowance <= 0:
            raise ValueError("experimental cutoff reached")
        with gpu_lease("PC-6", stage="additional_work", projected_seconds=allowance, exclusive=True) as lease, wall_limit(allowance):
            others = lease.other_cuda_processes()
            cost["other_cuda_processes"] = others
            if any("error" in row for row in others) or blocking_cuda_processes(others) or not any(d.platform == "gpu" for d in jax.devices()):
                raise RuntimeError("owner needs a released CUDA device")
            windows, meta = selection("v5")
            report["selection"] = meta
            paired = {}
            for ds in sorted({r["dataset"] for r in rows}):
                adapter, _ = construct(spec["recipes"][ds], "SE-A")  # base / config / selected reader; the arm is irrelevant here
                cap = adapter.learner
                for row in [r for r in rows if r["dataset"] == ds]:
                    reader = PCPositionBatchReader.from_checkpoint(cap.base, cap.cfg, cap.params, row["binding"], batch_size=batch_size)
                    result = read_arm(reader, windows, meta, out / row["name"])
                    report["cells"].append({k: row[k] for k in ("dataset", "realization", "order", "arm", "directory", "binding", "checkpoint_sha256")} | dict(readout=result))
                    paired.setdefault((ds, row["realization"], row["order"]), {})[row["arm"]] = result
            for (ds, r, o), arms in paired.items():
                if set(arms) != {"SE-A", "SE-E"}:
                    raise ValueError("both completed arms required")
                report["pairs"].append(dict(dataset=ds, realization=r, order=o, **pair(arms["SE-A"], arms["SE-E"], out / f"{ds}-r{r}-o{o}-paired.npz")))
            for row in rows:
                if sha(Path(row["directory"]) / f"checkpoint-{CHECKPOINT}.json") != row["checkpoint_sha256"]:
                    raise ValueError("input changed during readout")
            if selection("v5")[1] != meta:
                raise ValueError("position source changed during readout")
            for path in (Path(__file__), ROOT / "aw/pc_harm_readout.py", ROOT / "aw/pc_v1_readout.py", ROOT / "aw/pc_v1_run.py",
                         ROOT / "aw/scoring.py", ROOT / "scripts/r1_68f_full_validation.py"):
                report["sources_sha256"][str(path)] = sha(path)
            dump(out / "report.json", report)
            (out / "table.md").write_text(table_block(report))
            cost["status"] = "complete"
    finally:
        cost.update(elapsed_process_seconds=time.monotonic() - started, completed_arms=len(report["cells"]))
        dump(out / "cost.json", cost)
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--run", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--wall-seconds", type=int, default=14400)
    p.add_argument("--batch-size", type=int, default=16)
    a = p.parse_args()
    if not a.execute:
        rows = load_cells(Path(a.run).resolve())
        print(json.dumps(dict(cells=[r["name"] for r in rows], execute=False, positions=None)))
        return
    r = run(a.run, a.output, wall_seconds=a.wall_seconds, batch_size=a.batch_size)
    print(json.dumps(dict(cells=len(r["cells"]), pairs=len(r["pairs"]), output=a.output)))


if __name__ == "__main__":
    main()
