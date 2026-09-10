"""S4-05/S4-06 wiring on a synthetic confirmatory tree built from the development C2/C1/CR runs
(3 realizations × 5 orders with deterministic jitter): the collectors produce the paired table the
ANA-01 analysis expects and the resource views render (CPU only; synthetic, labelled)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from pccap.analysis.paired import analyze_paired
from pccap.analysis.s4_05 import discover, views
from pccap.analysis.s4_06 import collect_rows

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "results" / "S2" / "throughput"


def _build_tree(tmp_path_factory):
    if not (DEV / "C2" / "zsre" / "metrics.json").exists():
        pytest.skip("development runs absent")
    base = tmp_path_factory.mktemp("s4")
    rng = np.random.default_rng(0)
    for arm in ("C1", "C2", "CR"):
        src = DEV / arm / "zsre"
        items = [json.loads(line) for line in (src / "items.jsonl").read_text().splitlines() if line.strip()]
        ck = json.loads((src / "checkpoints.json").read_text())
        m = json.loads((src / "metrics.json").read_text())
        for r in range(3):
            for o in range(5):
                d = base / arm / "BP" / "h" / str(r) / str(o)
                d.mkdir(parents=True)
                shift = 0.05 if arm == "C2" else 0.0
                rows = []
                for it in items:
                    it2 = dict(it)
                    it2["es"] = float(it["es"])
                    rows.append(it2)
                end = dict(ck[-1])
                end["rows"] = [{"item_id": x["item_id"], "ret_es": x["ret_es"], "ret_gs": (None if x["ret_gs"] is None else float(np.clip(x["ret_gs"] + shift + 0.02 * rng.standard_normal(), 0, 1)))} for x in end["rows"]]
                (d / "items.jsonl").write_text("\n".join(json.dumps(x) for x in rows) + "\n")
                (d / "checkpoints.json").write_text(json.dumps([end], default=float))
                m2 = dict(m)
                m2["arm"] = arm
                m2["config"] = {"dataset": "zsre", "realization": r, "perm": o}
                (d / "metrics.json").write_text(json.dumps(m2, default=float))
    return base


@pytest.fixture(scope="module")
def synthetic_tree(tmp_path_factory):
    return _build_tree(tmp_path_factory)


@pytest.fixture()
def synthetic_tree_fresh(tmp_path_factory):
    return _build_tree(tmp_path_factory)


def test_collect_rows_and_paired(synthetic_tree):
    rows, notes = collect_rows(synthetic_tree, "zsre")
    assert len(rows) == 3 * 5 * 3 * 100 and not notes
    assert {r["arm"] for r in rows} == {"C1", "C2", "CR"}
    rep = analyze_paired(rows, seed=0, stream_id="zsre", draws=200)
    assert rep["classification"] in ("positive", "qualified", "inconclusive", "negative", "incomplete")
    assert rep["classification"] != "incomplete"


def test_resource_views(synthetic_tree):
    runs = discover([synthetic_tree])
    assert len(runs) == 45
    v = views(runs)
    key = "zsre/0/0"
    assert "C2-C1" in v["longest_common_prefix"][key] and v["longest_common_prefix"][key]["C2-C1"] == 100
    assert v["comparable_compute"][key]["C2"]["within_20pct"]
    shutil.rmtree(synthetic_tree, ignore_errors=True)


def test_order_variation(synthetic_tree_fresh):
    from pccap.analysis.s7_03 import analyze, load_runs

    runs = load_runs(synthetic_tree_fresh, "zsre", "C2")
    assert len(runs) == 15
    rep = analyze(runs)
    assert set(rep["realizations"]) == {"0", "1", "2"}
    r0 = rep["realizations"]["0"]
    assert len(r0["pairwise"]) == 10 and r0["acc_ret_gs_std_across_orders"] is not None
    assert rep["js_at_identical_prefixes"]["status"] == "unavailable"
