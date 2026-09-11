"""pccap command-line interface (skeleton at ENV-03; completed by S0-03).

    pccap run --stage S --arm A --base B --read R --realization i --perm j --manifest M [--mode dev|confirm]
    pccap report --stage S
    pccap status
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pccap")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="execute one manifest-driven run")
    run.add_argument("--stage", required=True)
    run.add_argument("--arm", default=None)
    run.add_argument("--base", default="BP")
    run.add_argument("--read", default="h")
    run.add_argument("--realization", type=int, default=0)
    run.add_argument("--perm", type=int, default=0)
    run.add_argument("--manifest", required=True)
    run.add_argument("--mode", choices=["dev", "confirm"], default="dev")
    run.add_argument("--task", default=None)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--dataset", default=None, help="dataset identity (confirm: must match the realization file name)")
    run.add_argument("--force", action="store_true", help="archive an existing run directory and rerun")
    run.add_argument("--no-lease", action="store_true", help="do not take the GPU lease (CPU/fake runners only)")
    run.add_argument("--projected-seconds", type=float, default=3600.0)
    run.add_argument("--allow-code-drift", action="store_true", help="confirm mode: run although src/pccap differs from the frozen tree (approved fix only)")
    rep = sub.add_parser("report", help="render a stage report")
    rep.add_argument("--stage", default=None)
    rep.add_argument("--final", action="store_true")
    sub.add_parser("status", help="regenerate docs/tasks/STATUS.md")
    q = sub.add_parser("queue", help="S4-04: run the frozen confirmatory job list in order (resumable; stops on refusals)")
    q.add_argument("--jobs", default=None)
    q.add_argument("--stage", default="S4")
    q.add_argument("--max-jobs", type=int, default=None)
    q.add_argument("--dry-run", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "status":
        from pccap.harness import status

        return status.main([])
    if args.cmd == "queue":
        from pccap.harness import execute

        qargs = ["--stage", args.stage] + (["--jobs", args.jobs] if args.jobs else []) + (["--max-jobs", str(args.max_jobs)] if args.max_jobs is not None else []) + (["--dry-run"] if args.dry_run else [])
        return execute.main(qargs)
    if args.cmd == "run":
        from pccap.harness import runner

        return runner.main(args)
    if args.cmd == "report":
        from pccap.analysis import report

        return report.main(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
