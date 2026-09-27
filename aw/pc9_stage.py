"""Prepare PC-9 copies/patch without editing the source-bound live runners.

Copies are review/test inputs, not executable entrypoints. Apply the patch only
after Capstan confirms an idle boundary AND all reports consuming the old
source identities have been generated. Never apply during a PC-7 profile/run.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/tasks/PC-9-candidate"


def replace(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError(f"expected {count} occurrences: {old!r}")
    return text.replace(old, new)


def v0(text):
    text = replace(text, "from pccap.bases import", "from aw.pc_sweep import add_options, projected_sweep, settings\nfrom pccap.bases import")
    text = replace(text, "seed, frozen=None):", "seed, frozen=None, *, credit_iters=8):")
    text = replace(text, '    cal = f["calibration"]["EPC"]', '    solver = settings(arm, credit_iters)\n    cal = f["calibration"]["EPC"]')
    text = replace(text, "credit=ARMS[arm], credit_iters=8,", 'credit=ARMS[arm], credit_iters=solver["credit_iters"],')
    text = replace(text, 'files = [Path(__file__), ARCHIVE,', 'files = [Path(__file__), ROOT / "aw/pc_sweep.py", ARCHIVE,')
    text = replace(text, '    out = _new_output(args.output)\n    started', '    solver = settings(args.arm, args.credit_iters, args.error_lr)\n    out = _new_output(args.output)\n    started')
    text = replace(text, '"arm": args.arm}', '"arm": args.arm, **solver}')
    text = replace(text, 'ledger=ledger, error_lr=0.1)', 'ledger=ledger, error_lr=solver["error_lr"])')
    text = replace(text, 'args.arm, cap_seed, f)', 'args.arm, cap_seed, f, credit_iters=args.credit_iters)')
    text = replace(text, '"error_lr": 0.1, "credit_iters": 8,', '**solver,')
    text = replace(text, '"wall_seconds": args.wall_seconds, "sources": source_identities()',
                   '"wall_seconds": args.wall_seconds, "credit": {a: settings(a, args.credit_iters, args.error_lr) for a in ARMS}, "sources": source_identities()')
    text = replace(text, '            for k, v in c.items():',
                   '            cmd += ["--credit-iters", str(args.credit_iters), "--error-lr", str(args.error_lr)]\n            for k, v in c.items():')
    text = replace(text, '    p.add_argument("--orders"', '    add_options(p)\n    p.add_argument("--profile", help="plan-only completed development profile for cost projection")\n    p.add_argument("--orders"')
    text = replace(text, '    if a.command == "plan":', '    if a.command != "plan" and (a.profile or a.sweep_error_lrs):\n        p.error("--profile and --sweep-error-lrs are plan-only; no sweep is launched")\n    if a.command == "plan":')
    text = replace(text, '"model_execution": False}',
                   '"model_execution": False,\n                  "credit": {arm: settings(arm, a.credit_iters, a.error_lr) for arm in ARMS},\n                  "sweep_cost": projected_sweep(a.profile, design(a.orders), a.sweep_error_lrs or [a.error_lr])}')
    return text


def v1(text):
    text = replace(text, "from aw.pc_v0 import", "from aw.pc_sweep import add_options, projected_sweep, settings\nfrom aw.pc_v0 import")
    text = replace(text, 'files = [Path(__file__), ROOT / "requirements.lock"]', 'files = [Path(__file__), ROOT / "aw/pc_sweep.py", ROOT / "requirements.lock"]')
    text = replace(text, 'def plan(development=False):\n    recipes', 'def plan(development=False, *, credit_iters=8, error_lr=0.1):\n    settings("SE-E", credit_iters, error_lr)\n    recipes')
    text = replace(text, 'credit=dict(arms=ARMS, iters=8, error_lr=0.1, energy="SD-24 corrected"),',
                   'credit=dict(arms=ARMS, iters=credit_iters, error_lr=error_lr, energy="SD-24 corrected",\n                    arm_settings={a: settings(a, credit_iters, error_lr) for a in ARMS}),')
    text = replace(text, 'def construct(spec, arm):', 'def construct(spec, arm, *, credit_iters=8, error_lr=0.1):')
    text = replace(text, '    recipe = checked(spec["construction_recipe"])', '    solver = settings(arm, credit_iters, error_lr)\n    recipe = checked(spec["construction_recipe"])')
    text = replace(text, '        error_lr=0.1,', '        error_lr=solver["error_lr"],')
    text = replace(text, '        credit_iters=8,', '        credit_iters=solver["credit_iters"],')
    text = replace(text, '        iters=cap.credit_iters,', '        iters=cap.credit_iters,\n        error_lr=cap.base.error_lr,')
    text = replace(text, '    finish = dict(\n        status=',
                   '    solver = dict(credit_iters=cap.credit_iters, error_lr=cap.base.error_lr,\n                  error_solver_active=cap.acquisition_credit == "error")\n    finish = dict(\n        **solver,\n        requested_solver=config.get("solver"),\n        status=')
    text = replace(text, '    configuration = dict(\n        config,', '    configuration = dict(\n        config,\n        **solver,')
    text = replace(text, 'def validate_profile(path):', 'def validate_profile(path, *, credit_iters=8, error_lr=0.1):')
    text = replace(text, 'if p != plan(True):', 'if p != plan(True, credit_iters=credit_iters, error_lr=error_lr):')
    text = replace(text, '    p = plan(development)', '    p = plan(development, credit_iters=args.credit_iters, error_lr=args.error_lr)', 2)
    text = replace(text, 'validate_profile(args.profile)', 'validate_profile(args.profile, credit_iters=args.credit_iters, error_lr=args.error_lr)', 2)
    text = replace(text, '    context = {}', '    solver = settings(c["arm"], args.credit_iters, args.error_lr)\n    context = {}')
    text = replace(text, 'construct(spec, c["arm"])', 'construct(spec, c["arm"], credit_iters=args.credit_iters, error_lr=args.error_lr)')
    text = replace(text, '                cell=c,\n                population', '                cell=c,\n                solver=solver,\n                population')
    text = replace(text, '                    status="failed",\n                    error=', '                    status="failed",\n                    **solver,\n                    error=')
    text = replace(text, '            if not development:\n                cmd', '            cmd += ["--credit-iters", str(args.credit_iters), "--error-lr", str(args.error_lr)]\n            if not development:\n                cmd')
    text = replace(text, '    ap.add_argument("--execute"', '    add_options(ap)\n    ap.add_argument("--execute"')
    text = replace(text, '    if args.command == "plan":', '    if args.command != "plan" and args.sweep_error_lrs:\n        ap.error("--sweep-error-lrs is plan-only; no sweep is launched")\n    if args.command == "plan":')
    text = replace(text, '        result = plan(args.population == "development")',
                   '        result = plan(args.population == "development", credit_iters=args.credit_iters, error_lr=args.error_lr)\n        result["sweep_cost"] = projected_sweep(args.profile, result["cells"], args.sweep_error_lrs or [args.error_lr])')
    return text


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    records, patch = {}, []
    for name, transform in (("pc_v0.py", v0), ("pc_v1_run.py", v1)):
        relative = "aw/" + name
        original = (ROOT / relative).read_text()
        candidate = transform(original)
        compile(candidate, relative, "exec")
        with (DEST / name).open("x") as f:
            f.write(candidate)
        records[relative] = dict(before_sha256=hashlib.sha256(original.encode()).hexdigest(),
                                candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest())
        patch.extend(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                        fromfile="a/"+relative, tofile="b/"+relative))
    with (DEST / "solver-options.patch").open("x") as f:
        f.writelines(patch)
    with (DEST / "sources.json").open("x") as f:
        json.dump(records, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
