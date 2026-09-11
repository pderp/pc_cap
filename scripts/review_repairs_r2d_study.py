#!/usr/bin/env python3
"""Independent V3 outcome-isolation control over fresh synthetic fixtures."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True

import pccap  # noqa: E402,F401
from pccap.analysis import s4_05, s4_06, s7_03  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/V2/codex_v3"


def put(path, value, lines=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        if lines:
            f.write("".join(json.dumps(row) + "\n" for row in value))
        else:
            json.dump(value, f, indent=2)


def refusal(fn):
    try:
        fn()
    except ValueError as exc:
        return str(exc)
    return None


def main():
    study = json.loads((OUT / "study.json").read_text())
    original = Path(study["fixture_root"]) / "two_experiment_copies"
    fixture = Path(study["fixture_root"]) / "conflicting_outcomes"
    assert not fixture.exists()
    sources = []
    for mp in sorted(original.rglob("metrics.json")):
        m = json.loads(mp.read_text())
        if ".superseded-" not in str(mp) and m["config"].get("experiment_id"):
            sources.append((mp.parent, m))
    assert len(sources) == 2
    ids = [m["config"]["experiment_id"] for _, m in sources]
    watched = [Path(m.__file__) for m in (s4_05, s4_06, s7_03)]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    for (src, metrics), expected in zip(sources, (1.0, 0.0)):
        dest = fixture / metrics["config"]["experiment_id"]
        items = [json.loads(s) for s in (src / "items.jsonl").read_text().splitlines() if s]
        # Both acquire every item; the second experiment loses every item afterwards.
        assert all(it["es"] == 1.0 for it in items)
        checkpoints = json.loads((src / "checkpoints.json").read_text())
        for ck in checkpoints:
            for field in ("ret_es", "ret_gs", "survival_conditional_on_immediate"):
                ck[field] = expected
            for row in ck["rows"]:
                row["ret_es"] = row["ret_gs"] = expected
        for field in ("ret_es_end", "ret_gs_end", "survival_conditional_end"):
            metrics["metrics"][field]["value"] = expected
        put(dest / "metrics.json", metrics)
        put(dest / "checkpoints.json", checkpoints)
        put(dest / "items.jsonl", items, lines=True)

    result = {"fixture_root": str(fixture), "experiment_ids": ids, "filtered": {}, "unfiltered_refusals": {}, "source_before": before}
    item_sets = []
    for eid, expected in zip(ids, (1.0, 0.0)):
        discovered = s4_05.discover([fixture], eid)
        view = s4_05.views(discovered)
        rows, notes = s4_06.collect_rows(fixture, "zsre", eid)
        runs = s7_03.load_runs(fixture, "zsre", "C2", eid)
        assert len(discovered) == 1 and len(rows) == 8 and len(runs) == 1
        assert view["experiment_id"] == eid and all(r["ret_gs"] == r["ret_es"] == expected for r in rows)
        assert view["per_run"][0]["retention_vs_items"]["end"]["ret_es"] == expected
        assert all(r["experiment_id"] == eid for r in runs.values())
        assert all(x["ret_es"] == x["ret_gs"] == expected for run in runs.values() for x in run["end"].values())
        item_sets.append(set(r["item_id"] for r in rows))
        cli_out = OUT / ("s7_order_" + str(int(expected)) + ".json")
        assert not cli_out.exists()
        cli = subprocess.run([sys.executable, "-B", "-m", "pccap.analysis.s7_03", "--root", str(fixture), "--dataset", "zsre", "--arm", "C2", "--experiment-id", eid, "--out", str(cli_out)], capture_output=True, text=True)
        assert cli.returncode == 0, cli.stderr
        report = json.loads(cli_out.read_text())
        assert report["experiment_id"] == eid and report["n_runs"] == 1
        realization = report["realizations"]["0"]
        assert list(realization["acc_ret_es_per_order"].values()) == [expected]
        assert list(realization["lost_items_per_order"].values()) == [int((1-expected)*8)]
        result["filtered"][eid] = {"runs": len(discovered), "paired_rows": len(rows), "order_cells": len(runs), "retained_es": expected, "retained_gs": expected, "lost_items": int((1-expected)*8), "cli_exit": cli.returncode, "cli_stdout": cli.stdout, "notes": notes}
    assert item_sets[0] == item_sets[1], "conflict must be at identical exposure"
    for name, fn in {
        "paired": lambda: s4_06.collect_rows(fixture, "zsre"),
        "order": lambda: s7_03.load_runs(fixture, "zsre", "C2"),
        "resource": lambda: s4_05.views(s4_05.discover([fixture])),
    }.items():
        result["unfiltered_refusals"][name] = refusal(fn)
        assert result["unfiltered_refusals"][name]
    assert s4_05.discover([fixture], "nonexistent") == []
    assert s4_06.collect_rows(fixture, "zsre", "nonexistent")[0] == []
    assert s7_03.load_runs(fixture, "zsre", "C2", "nonexistent") == {}

    # Additional boundary, beyond the five V2 findings: an overlapping root list.
    duplicate_runs = s4_05.discover([fixture, fixture], ids[0])
    duplicate_error = refusal(lambda: s4_05.views(duplicate_runs))
    duplicate_view = None if duplicate_error else s4_05.views(duplicate_runs)
    result["additional_same_experiment_duplicate_root"] = {
        "runs": len(duplicate_runs), "refusal": duplicate_error,
        "per_run_rows": None if duplicate_view is None else len(duplicate_view["per_run"]),
        "cell_tables": None if duplicate_view is None else len(duplicate_view["comparable_compute"]),
        "interpretation": "Report this separately; the required cross-experiment control must pass regardless.",
    }
    result["source_after"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    assert result["source_before"] == result["source_after"]
    result["required_controls_pass"] = True
    put(OUT / "conflicting_outcomes.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
