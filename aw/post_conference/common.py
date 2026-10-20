"""Paths, saved-record loaders and bookkeeping shared by the Phase 0 analyses (post-conference programme).

Phase 0 uses only the frozen ext-20261009 record (scores, raw selection chunks, payloads, memory snapshots) plus
forward-only GPU replays. Nothing here writes into the frozen record.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from aw.extremes.common import ASSETS, MPL_SITE, ROOT, Status as _Status, atomic_csv, atomic_json, atomic_parquet, atomic_write_bytes, git_head, now, read_json, sha, sha_bytes  # noqa: F401
from aw.extremes.common import DATA as EXT_DATA, OUT as EXT_OUT  # noqa: F401

STUDY = "phase0"
OUT = ROOT / "results" / "post_conference" / STUDY  # tables, report, manifest (text)
LOGS = ROOT / "logs" / "post_conference" / STUDY
DATA = ASSETS / "post_conference" / STUDY  # parquet + figures
CACHE = ASSETS / "runs" / "post_conference" / STUDY  # replay / in-context raw chunks
TABLES = OUT / "tables"
FIGURES = DATA / "figures"

DATASETS = ("zsre", "counterfact", "mquake")
RULES = {"bp": "BP-CAP", "epc": "PC-CAP"}
SEEDS = (0, 1, 2)
READERS = [f"{r}_reader_s{s}" for r in RULES for s in SEEDS]
HORIZON = 300
NULL_THRESHOLD = 0.5  # the registered gate (semantic_config.null_threshold)
NOISE = 1e-3  # nats: |D| <= NOISE counts as unchanged (supplement convention)
SEVERE = 2.0  # nats/token: a deterioration above this is "severe" (supplement convention)
ITEM_FAMILIES = ("edit", "paraphrase", "locality_item")
COLLATERAL = ("locality_item", "near_miss_neighbour", "unseen", "locality")


def ensure_dirs():
    for p in (OUT, LOGS, DATA, CACHE, TABLES, FIGURES):
        p.mkdir(parents=True, exist_ok=True)


def label(model: str) -> str:
    if model == "frozen":
        return "Frozen GPT-2"
    rule, seed = model.replace("_reader_s", " ").split()
    return f"{RULES[rule]} seed {seed}"


def rule_of(model: str) -> str | None:
    return None if model == "frozen" else model.split("_")[0]


class Status(_Status):
    def __init__(self):
        super().__init__(OUT)
        self.manifest.setdefault("study", STUDY)


def log_line(name: str, text: str):
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / f"{name}.log").open("a") as f:
        f.write(f"{now()} {text}\n")


def mpl():
    """matplotlib lives in the status-paper environment, not in the JAX venv."""
    if str(MPL_SITE) not in sys.path:
        sys.path.append(str(MPL_SITE))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


# ----------------------------------------------------------------------------------------------- saved record
def scores(horizon: int | None = HORIZON) -> pd.DataFrame:
    """ext-20261009 scores.parquet; readers at `horizon`, the frozen model at 0 (no memory)."""
    s = pd.read_parquet(EXT_DATA / "data" / "scores.parquet")
    if horizon is not None:
        s = s[(s.horizon == horizon) | (s.model == "frozen")]
    return s


def frozen_losses(s: pd.DataFrame) -> pd.DataFrame:
    f = s[s.model == "frozen"][["dataset", "probe_id", "target", "nll_token", "exact", "status"]].rename(columns={"nll_token": "L_frozen", "exact": "X_frozen", "status": "status_frozen"})
    return f.drop_duplicates(["dataset", "probe_id", "target"])


def selection_table(models=READERS, datasets=DATASETS, horizon: int = HORIZON) -> pd.DataFrame:
    """Per probe reader selection from the raw score chunks: record ids, weights, hard null, null mass, best score."""
    rows = []
    for model in models:
        for ds in datasets:
            d = EXT_DATA / "checkpoints" / "scores" / model / ds / f"h{horizon}"
            manifest = read_json(d / "chunks.json")
            if manifest.get("status") != "complete":
                raise ValueError(f"incomplete scores for {model} {ds}")
            for path in sorted(glob.glob(str(d / "chunk-*.jsonl"))):
                with open(path) as f:
                    for line in f:
                        r = json.loads(line)
                        sel = r.get("selection") or {}
                        rids = list(sel.get("record_ids", []))
                        w = list(sel.get("weights", []))
                        top = rids[int(np.argmax(w))] if rids and w else None
                        iid = str(r.get("item_id"))
                        rows.append(dict(model=model, dataset=ds, probe_id=r["probe_id"], family=r["family"], item_id=r.get("item_id"),
                                         hard_null=sel.get("hard_null"), null_mass=sel.get("null_mass"), best_score=sel.get("best_score"),
                                         n_candidates=len(rids), top_record=top,
                                         own_in_candidates=any((":" + iid + ":") in rid for rid in rids),
                                         own_is_top=(top is not None and (":" + iid + ":") in top),
                                         record_ids=json.dumps(rids), weights=json.dumps(w)))
    t = pd.DataFrame(rows)
    # Gate decomposition (registered config: null_threshold 0.5, min_score None, rare_overlap_min 1):
    t["veto"] = np.where(~t.hard_null.astype(bool), "fired", np.where(t.n_candidates == 0, "no_candidates", np.where(t.null_mass >= NULL_THRESHOLD, "null_threshold", "rare_token_veto")))
    return t


def own_record_id(store, dataset: str, item_id: str) -> str | None:
    key = ":" + str(item_id) + ":"
    for r in store.records:
        if key in r.record_id:
            return r.record_id
    return None
