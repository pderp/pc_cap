"""PC-10: explicit treatment identity; separate reports for solver contingencies.

Staged for aw/pc_treatments.py. Metadata only; never selects or executes a sweep.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aw.pc_sweep import settings

DEFAULT = dict(credit_iters=8, error_lr=0.1)


def normalized(iters, rate):
    if isinstance(iters, bool) or not isinstance(iters, int) or isinstance(rate, bool):
        raise ValueError("integer treatment iterations required")
    s = settings("SE-E", iters, rate)
    return {k: s[k] for k in DEFAULT}


def label(t):
    t = normalized(t["credit_iters"], t["error_lr"])
    return f"SE-E k={t['credit_iters']}, lr={t['error_lr']!r}; SE-A unchanged"


def key(t):
    t = normalized(t["credit_iters"], t["error_lr"])
    return f"k{t['credit_iters']}-lr{t['error_lr']!r}"


def planned(plan):
    credit = plan.get("credit")
    if credit is None:
        return dict(DEFAULT)
    arms = credit.get("arm_settings", credit)
    if set(arms) != {"SE-A", "SE-E"}:
        raise ValueError("plan must specify both treatment arms")
    e = arms["SE-E"]
    t = normalized(e["requested_credit_iters"], e["requested_error_lr"])
    for arm in arms:
        if arms[arm] != settings(arm, **t):
            raise ValueError("planned effective/requested settings disagree")
    return t


def recorded(cfg, finish=None, plan=None):
    """Legacy missing finish metadata is allowed only for the original 8/.1 run."""
    arm = cfg.get("arm", cfg.get("cell", {}).get("arm"))
    s = cfg.get("solver", cfg)
    effective = normalized(s["credit_iters"], s["error_lr"])
    has_requested = "requested_credit_iters" in s or "requested_error_lr" in s
    if has_requested:
        t = normalized(s["requested_credit_iters"], s["requested_error_lr"])
        expected = settings(arm, **t)
        if any(s.get(k) != v for k, v in expected.items()):
            raise ValueError("cell effective/requested treatment differs")
    else:
        if effective != DEFAULT:
            raise ValueError("nondefault treatment needs explicit requested settings")
        t, expected = dict(DEFAULT), settings(arm)
    if plan is not None and t != planned(plan):
        raise ValueError("cell treatment differs from plan")
    if finish is not None:
        actual = {k: finish.get(k) for k in DEFAULT}
        if all(v is None for v in actual.values()) and not has_requested:
            pass  # historical default finish format, validated from config
        elif actual != effective:
            raise ValueError("config/finish treatment differs")
        if has_requested:
            saved = finish.get("requested_solver", finish)
            if any(saved.get(k) != v for k, v in expected.items()):
                raise ValueError("finish lacks matching requested treatment")
            if finish.get("error_solver_active") != expected["error_solver_active"]:
                raise ValueError("finish active credit flag differs")
    return dict(treatment=t, solver=expected)


def homogeneous(rows):
    variants = {key(r.get("treatment", DEFAULT)): r.get("treatment", DEFAULT) for r in rows}
    if len(variants) > 1:
        raise ValueError("mixed treatments cannot be pooled into one arm; build a sweep report")
    return next(iter(variants.values()), dict(DEFAULT))


def build_sweep(groups, output, document, build, read, *, orders, smoke, diagnostics):
    """One normal child report per treatment; no cross-treatment efficacy mean."""
    if diagnostics:
        raise ValueError("attach diagnostics to individual treatments, not to a pooled sweep")
    output, document = Path(output), Path(document)
    output.mkdir(parents=True, exist_ok=False)
    groupings, bindings = {}, {}
    for group in groups:
        t = planned(read(Path(group) / "plan.json", bindings))
        entry = groupings.setdefault(key(t), dict(treatment=t, groups=[]))
        entry["groups"].append(group)
    reports, lines = [], []
    for ident, entry in sorted(groupings.items()):
        child = output / ident
        r = build(entry["groups"], child, output / (ident + ".md"), orders=orders, smoke=smoke)
        reports.append(
            dict(treatment=entry["treatment"], report=str((child / "report.json").resolve()))
        )
        for a in r["aggregates"]:
            vals = [
                label(entry["treatment"]),
                a["dataset"],
                a["metric"],
                a["realizations"],
                a["mean"],
            ]
            lines.append(
                "| " + " | ".join("unavailable" if x is None else str(x) for x in vals) + " |"
            )
        bindings.update(r["sources_sha256"])
        bindings[str((child / "report.json").resolve())] = file_sha(child / "report.json")
    result = dict(
        schema="pc-treatment-sweep-v1",
        smoke=smoke,
        treatments=reports,
        sources_sha256=bindings,
        pooling="none; paired effects within each declared treatment only",
    )
    (output / "report.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        "# PC contingency sweep — separate treatments\n\n"
        + (
            "CPU SMOKE ONLY; synthetic outcomes.\n\n"
            if smoke
            else "Exposed S5; exploratory solver contingency, not fresh confirmation.\n\n"
        )
        + "No pooled arm or selected best-treatment claim; each child retains missing slots and secondary scores.\n\n"
        + "| Treatment | Dataset | Metric | Realization differences | Mean SE-E − SE-A |\n"
        + "| --- | --- | --- | --- | --- |\n"
        + "\n".join(lines)
        + "\n"
    )
    return result


def file_sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def harm_sweep(paths, output, document):
    """Read completed readouts; display each treatment/coordinate without pooling."""
    refs, entries, lines, seen = {}, [], [], set()
    population = None
    for path in map(Path, paths):
        report = json.loads(path.read_text())
        cost_path = path.parent / "cost.json"
        cost = json.loads(cost_path.read_text())
        if cost["status"] != "complete":
            raise ValueError("complete harm readout required")
        for p, h in report["sources_sha256"].items():
            if file_sha(p) != h:
                raise ValueError("harm input identity differs")
            refs[p] = h
        identity = (report["smoke"], report["selection"])
        if population is not None and identity != population:
            raise ValueError("different populations/position inventories cannot share a sweep")
        population = identity
        t = homogeneous(report["cells"])
        if t != report.get("treatment", DEFAULT):
            raise ValueError("harm group/cell treatment differs")
        if any(c["readout"].get("treatment", DEFAULT) != t for c in report["cells"]):
            raise ValueError("nested readout treatment differs")
        cells = {(c["dataset"], c["realization"], c["order"], c["arm"]) for c in report["cells"]}
        if len(cells) != len(report["cells"]):
            raise ValueError("duplicate harm cell")
        covered = set()
        for p in report["pairs"]:
            coord = (p["dataset"], p["realization"], p["order"])
            if (key(t), *coord) in seen or p.get("treatment", DEFAULT) != t:
                raise ValueError("duplicate pair or mixed treatment in harm sweep")
            seen.add((key(t), *coord))
            for arm in ("SE-A", "SE-E"):
                if (*coord, arm) not in cells:
                    raise ValueError("missing matched harm arm")
                covered.add((*coord, arm))
            delta = p["positionwise"]["original"]["loss"]["mean_signed"]
            es = p["difference_of_arm_es99"]["original"]
            lines.append(f"| {label(t)} | {coord[0]} | {coord[1]} | {coord[2]} | {delta} | {es} |")
        if covered != cells or not cells:
            raise ValueError("incomplete harm pairing")
        refs[str(path.resolve())], refs[str(cost_path.resolve())] = (
            file_sha(path),
            file_sha(cost_path),
        )
        entries.append(
            dict(
                treatment=t,
                report=str(path.resolve()),
                readout_process_seconds=cost["elapsed_process_seconds"],
            )
        )
    if not entries:
        raise ValueError("at least one complete readout required")
    result = dict(
        schema="pc-harm-sweep-v1",
        smoke=population[0],
        selection=population[1],
        treatments=entries,
        sources_sha256=refs,
        pooling="none",
    )
    with Path(output).open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    with Path(document).open("x") as f:
        f.write(
            "# Harm sweep — separate treatments\n\n"
            + (
                "CPU SMOKE ONLY.\n\n"
                if result["smoke"]
                else "Exposed supplemental populations; no treatment selection or pooled estimate.\n\n"
            )
            + "Positive differences favor SE-A for harm; difference of arm ES99 is not ES99 of positionwise differences.\n\n"
            + "| Treatment | Dataset | Realization | Order | Mean paired ΔNLL | Difference of arm ES99 |\n"
            + "| --- | --- | --- | --- | --- | --- |\n"
            + "\n".join(lines)
            + "\n"
        )
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("harm-sweep",))
    p.add_argument("--report", action="append", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--document", required=True)
    a = p.parse_args()
    harm_sweep(a.report, a.output, a.document)


if __name__ == "__main__":
    main()
