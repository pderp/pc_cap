"""Private DEC-075 random-vs-adjoint control driver; plan is CPU-only.

Reuses the native PC-v0 cell/stream engine with private function globals. It
does not modify the live settling-depth runner or any frozen source module.
GPU dispatch remains Capstan's responsibility after review and a profile.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

from aw import pc_v0
from aw.pc_historical import bind
from aw.pc_random_credit import TREATMENT, RandomCreditCap
from pccap.harness.records import append_jsonl

ARMS = ("SE-A", "SE-R")
OUTPUT = pc_v0.OUTPUT / "random-control"
MODULE = "aw.pc_random_run"


def settings(arm, credit_iters=8, error_lr=0.1):
    if arm not in ARMS or credit_iters != 8 or error_lr != 0.1:
        raise ValueError("random control admits only SE-A/SE-R with reference k=8/lr=0.1")
    record = pc_v0.settings("SE-E" if arm == "SE-R" else "SE-A", 8, 0.1)
    return dict(
        record,
        control_treatment=dict(
            TREATMENT,
            arm=arm,
            credit="random" if arm == "SE-R" else "adjoint",
            role="random_direction" if arm == "SE-R" else "adjoint_control",
        ),
    )


def sources():
    result = pc_v0.source_identities()
    for name in ("aw/pc_random_run.py", "aw/pc_random_credit.py", "aw/pc_historical.py"):
        result[name] = pc_v0.sha(pc_v0.ROOT / name)
    return result


def design(profile=False, items=10):
    return [
        dict(
            dataset=d,
            realization=r,
            order=100,
            arm=a,
            items=items if profile else 1000 if d == "zsre" else 300,
        )
        for d in ("zsre", "counterfact")
        for r in ([0] if profile else range(3))
        for a in ARMS
    ]


def plan(profile=False, items=10):
    return dict(
        population="development" if profile else "exposed S5",
        cells=design(profile, items),
        control_treatment=TREATMENT,
        credit={a: settings(a) for a in ARMS},
        sources=sources(),
        model_execution=False,
        claim="exploratory DEC-075 direction control; no new confirmation",
        compute_note="Reference error cost is paid before randomizing; norm is removed by the ordinary unit transport.",
    )


def build_cap(base, dataset, arm, seed, frozen=None, *, credit_iters=8):
    settings(arm, credit_iters, base.error_lr)
    ordinary = pc_v0.build_cap(base, dataset, "SE-E" if arm == "SE-R" else "SE-A", seed, frozen)
    if arm == "SE-A":
        return ordinary
    return RandomCreditCap(base, ordinary.cfg, base.ledger)


def stream(cap, items, router, budget, evaluator, out, ledger, **kwargs):
    if isinstance(cap, RandomCreditCap):
        cap.router_seed = kwargs.get("seed", 0)
        cap.on_decision = lambda record: append_jsonl(Path(out) / "decisions.jsonl", record)
        if kwargs.get("correction_track") or kwargs.get("permitted") is not None:
            raise ValueError("random control covers only the archived ordinary editing stream")
    return pc_v0.run_stream(cap, items, router, budget, evaluator, out, ledger, **kwargs)


def new_output(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OUTPUT) or path == OUTPUT:
        raise ValueError(f"new control output must be below {OUTPUT}")
    return pc_v0._new_output(path)


def cell(args):
    settings(args.arm)
    expected = sources()
    execute = bind(
        pc_v0.run_cell,
        settings=settings,
        build_cap=build_cap,
        run_stream=stream,
        source_identities=sources,
        _new_output=new_output,
    )
    result = execute(args)
    if sources() != expected:
        raise RuntimeError("control source changed during execution")
    return result


def group(args):
    if not args.execute:
        raise ValueError("GPU dispatch requires --execute")
    out = new_output(args.output)
    p = plan(args.command == "profile", args.items)
    pc_v0.dump(out / "plan.json", p)
    start, finished = time.monotonic(), []
    try:
        for c in p["cells"]:
            if sources() != p["sources"]:
                raise RuntimeError("control source changed before dispatch")
            remaining = min(
                args.wall_seconds - (time.monotonic() - start), pc_v0.CUTOFF - time.time(), 7200
            )
            if remaining <= 0:
                raise TimeoutError("control wall ceiling or October 9 cutoff")
            dest = out / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
            command = [
                sys.executable,
                "-m",
                MODULE,
                "cell",
                "--execute",
                "--output",
                str(dest),
                "--population",
                "development" if args.command == "profile" else "replication",
                "--wall-seconds",
                str(remaining),
            ]
            for k, value in c.items():
                command += ["--" + k, str(value)]
            with (out / (dest.name + ".log")).open("x") as log:
                process = subprocess.run(
                    command, stdout=log, stderr=subprocess.STDOUT, timeout=remaining + 30
                )
            path = dest / "finish.json"
            finish = json.loads(path.read_bytes()) if path.exists() else None
            finished.append(dict(cell=c, exit_code=process.returncode, finish=finish))
            if process.returncode or not finish or finish["status"] != "complete":
                raise RuntimeError("random control cell incomplete; inspect durable receipts")
    finally:
        pc_v0.dump(
            out / "summary.json",
            dict(
                planned=len(p["cells"]),
                finished=finished,
                elapsed_process_seconds=time.monotonic() - start,
                complete=len(finished) == len(p["cells"])
                and all(x["finish"] and x["finish"]["status"] == "complete" for x in finished),
            ),
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "profile", "run", "cell"))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--dataset", choices=("zsre", "counterfact"), default="zsre")
    parser.add_argument("--realization", type=int, choices=range(3), default=0)
    parser.add_argument("--order", type=int, choices=(100,), default=100)
    parser.add_argument("--arm", choices=ARMS, default="SE-R")
    parser.add_argument(
        "--population", choices=("development", "replication"), default="replication"
    )
    parser.add_argument("--items", type=int, default=10)
    parser.add_argument("--wall-seconds", type=float, default=28800)
    a = parser.parse_args()
    a.credit_iters, a.error_lr, a.diagnostic = 8, 0.1, False
    if not math.isfinite(a.wall_seconds) or a.wall_seconds <= 0 or a.items < 1:
        parser.error("positive finite allowance and item count required")
    if a.command == "plan":
        print(json.dumps(plan(), indent=2))
    else:
        if not a.execute or not a.output:
            parser.error("--execute and a new --output are required")
        if a.command == "cell":
            expected = 1000 if a.dataset == "zsre" else 300
            if a.population == "replication" and a.items != expected:
                parser.error("replication requires the complete archived stream")
            cell(a)
        else:
            group(a)


if __name__ == "__main__":
    main()
