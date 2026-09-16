"""R1-64: create unsealed development payloads; never execute the base or draw fresh data."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scripts.r1_64_materialize_base import materialize_base

from pccap.contracts import Budget
from pccap.revision_v1.adapt import FastConfig
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.checkpoint_identity import checkpoint_tree
from pccap.revision_v1.controller import ControllerConfig
from pccap.revision_v1.development_cell import (
    BANNER,
    MODE,
    PAYLOAD_ROOT,
    code_identity,
    validate_development_payload,
)
from pccap.revision_v1.endpoints_composition import dependency_ids
from pccap.revision_v1.learner import RevisionConfig
from pccap.revision_v1.reader import ReaderConfig, params_hash
from pccap.revision_v1.stage4_cell import ROOT, sha, write_json


def unique_stream(dev, train, n, n_outside):
    if n not in (100, 300, 1000) or n_outside < 1:
        raise ValueError("100/300/1000 edits and positive outside count required")
    # CF/zsRE use rows beyond the historically trained first 1000; MQ v3
    # contains only 500, all explicitly labelled as training-pool fillers.
    extra = train["items"][1000:] if len(train["items"]) > 1000 else train["items"]
    seen_ids = set()
    seen_subjects = set()
    source = []
    for role, rows in (("development", dev["items"]), ("training_pool_filler", extra)):
        for r in rows:
            s = " ".join(r["subject"].casefold().split())
            if r["item_id"] in seen_ids or s in seen_subjects:
                continue
            seen_ids.add(r["item_id"])
            seen_subjects.add(s)
            source.append({**r, "development_origin": role})
    if len(source) < n + n_outside:
        raise ValueError(
            f"self-contained development capacity {len(source)} < {n + n_outside}; no fresh fillers allowed"
        )
    return source[:n], source[n : n + n_outside], source


def endpoint(rows, kind, n):
    key = "composition_id" if kind == "composition" else "item_id"
    if kind == "composition":
        return {"expected_ids": [r[key] for r in rows], "rows": rows}
    selected = [{**r, "item_id": f"dev:{kind}:{i}"} for i, r in enumerate(rows[:n])]
    return {"expected_ids": [f"dev:{kind}:{i}" for i in range(n)], "rows": selected}


def payload_from_documents(
    ds,
    dev,
    train,
    challenges,
    cases,
    drift,
    n,
    n_outside=100,
    n_loc=50,
    n_near=100,
    n_revision=50,
    n_windows=128,
):
    items, outside, pool = unique_stream(dev, train, n, n_outside)
    ids = {r["item_id"] for r in items}
    available = [c for c in cases if set(dependency_ids(c)) <= ids] if ds == "mquake" else []
    near = [r for r in challenges["near_neighbour"]["items"] if r["dataset"] == ds]
    rev = [r for r in challenges["temporal_correction"]["items"] if r["dataset"] == ds]
    loc = [{"prompt": p} for p in dev["unrelated_prompts"]]
    windows = np.asarray(drift).reshape(-1)
    if n_windows < 1 or len(windows) < n_windows * 128:
        raise ValueError("drift window shortfall")
    windows = windows[: n_windows * 128].reshape(n_windows, 128).astype(int).tolist()
    return {
        "mode": MODE,
        "banner": BANNER,
        "items": items,
        "pool_rows": pool,
        "endpoints": {
            "locality": endpoint(loc, "locality", n_loc),
            "unseen": {"expected_ids": [r["item_id"] for r in outside], "rows": outside},
            "near_miss": endpoint(near, "near", n_near),
            "revision": endpoint(rev, "revision", n_revision),
            "composition": endpoint(available, "composition", 0),
            "drift": {"windows": windows, "expected_positions": n_windows * 127},
        },
        "development_summary": {
            "dev_items": sum(r["development_origin"] == "development" for r in items),
            "training_pool_fillers": sum(
                r["development_origin"] == "training_pool_filler" for r in items
            ),
            "source_order": "manifest order; no outcome-based selection",
            "challenge_shortfalls": {
                "near_miss": max(0, n_near - len(near)),
                "revision": max(0, n_revision - len(rev)),
            },
            "locality_note": "MQuAKE v3 probes are in the edited slice; report interference, not independent outside locality",
            "training_pool_note": "Pool fillers/outside prompts are development data; no claim of reader-training independence",
        },
    }


def v4_construction(ds, seed=0):
    """CPU metadata/NumPy hashing only. Does not instantiate BPBase or evaluate a model."""
    import os

    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import _digest
    primary_path = Path(os.environ.get("PCCAP_PRIMARY_MANIFEST", str(ROOT / "manifests/revision_v1/primary_condition_v4.json")))  # v5+: PCCAP_PRIMARY_MANIFEST=manifests/revision_v1/primary_condition_v5.json
    primary = json.loads(primary_path.read_text())
    frozen_path = (
        ROOT
        / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json"
    )
    frozen = json.loads(frozen_path.read_text())
    if ds not in frozen["calibration"]["BP"]["radii"]:
        raise ValueError("worked v4 construction has no dataset calibration; bind one explicitly")
    weight = primary["weights"] if "path" in primary["weights"] else primary["weights"][f"seed{seed}"]  # v5 binds one averaged checkpoint
    stop_path = (ROOT / primary["stop_tokens"]["path"]).resolve()
    if (
        sha(weight["path"]) != weight["sha256"]
        or sha(stop_path) != primary["stop_tokens"]["sha256"]
    ):
        raise ValueError("v4 reader/stop-list hash mismatch")
    for name, h in primary["pools"].items():
        if sha(ROOT / f"manifests/revision_v1/{name}.json") != h:
            raise ValueError("v4 pool changed")
    stop = json.loads(stop_path.read_text())["tokens"]
    base = Path(g.DEFAULT_SNAPSHOT)
    files = {
        name: sha(base / name) for name in ("config.json", "model.safetensors", "tokenizer.json")
    }
    materialized = materialize_base({"path": str(base), "files": files})
    base = Path(materialized["path"])
    cfgbase = g.GPT2Config.from_snapshot(base)
    base_hash = _digest(g.load_params_numpy(base, cfgbase))
    params = checkpoint_tree(weight["path"])
    cal = {"bank_scales": frozen["b_m"], "radii": frozen["calibration"]["BP"]["radii"][ds]}
    budget = Budget(A=0.3)
    config = RevisionConfig(
        reader=ReaderConfig(d=cfgbase.d, lexical=True, pairwise_null=True, stop_tokens=tuple(stop)),
        controller=ControllerConfig(
            d=cfgbase.d,
            A=budget.A,
            bank_scales=tuple(float(cal["bank_scales"][str(k)]) for k in (1, 2, 3)),
        ),
        fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=budget.tau_edit),
        tau_edit=budget.tau_edit,
        seed=seed,
        min_score=None,
        null_threshold=0.5,
        rare_overlap_min=1,
        rare_df_max=2,
    )
    spec = {
        "base": {"path": str(base), "files": files},
        "weights": weight,
        "stop_tokens": {"path": str(stop_path), "sha256": sha(stop_path)},
        "seed": seed,
        "calibration": cal,
        "budget": asdict(budget),
    }
    identity = {
        "condition": "R1_learned_ff",
        "class": "pccap.revision_v1.learner.RevisionCap",
        "config_sha256": digest(asdict(config)),
        "rule": None,
        "budget": asdict(budget),
        "base_sha256": base_hash,
        "locality_base_sha256": base_hash,
        "params_sha256": params_hash(params),
    }
    provenance = {
        "primary": {"path": str(primary_path), "sha256": sha(primary_path)},
        "calibration": {"path": str(frozen_path), "sha256": sha(frozen_path)},
        "identity_method": "NumPy base/checkpoint hashes and registered dataclass configuration; no base execution",
    }
    return spec, identity, files["tokenizer.json"], provenance


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", choices=("zsre", "counterfact", "mquake"), required=True)
    ap.add_argument("--n-edits", type=int)
    ap.add_argument("--n-outside", type=int, default=100)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--recipe", type=Path, help="also build worked v4 recipe (zsRE/CF)")
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", a.tag):
        raise ValueError("safe unique tag required")
    payload_dir = PAYLOAD_ROOT / a.tag
    if payload_dir.exists() or (a.recipe and a.recipe.exists()):
        raise FileExistsError("new outputs required")
    if a.recipe and not a.recipe.resolve().is_relative_to(ROOT):
        raise ValueError("recipe belongs in pc_cap")
    bindings = {}

    def read(p):
        p = Path(p).resolve()
        bindings[str(p)] = sha(p)
        return json.loads(p.read_text())

    ds = a.dataset
    dev = read(ROOT / f"manifests/dev/{ds}_dev{'_v3' if ds == 'mquake' else ''}.json")
    train = read(
        ROOT / f"manifests/revision_v1/train_pool_{ds}_{'v3' if ds == 'mquake' else 'v1'}.json"
    )
    challenges = read(ROOT / "manifests/dev/challenges.json")
    cases = []
    if ds == "mquake":
        m = read(ROOT / "manifests/revision_v1/mquake_items_v1.json")
        ref = m["artifacts"]["composition"]
        if sha(ref["path"]) != ref["sha256"]:
            raise ValueError("composition source changed")
        bindings[ref["path"]] = ref["sha256"]
        cases = [json.loads(s) for s in Path(ref["path"]).read_text().splitlines()]
    drift_path = ROOT.parent / "assets/data/prepared/lm/drift_tokens.npy"
    bindings[str(drift_path)] = sha(drift_path)
    data = payload_from_documents(
        ds,
        dev,
        train,
        challenges,
        cases,
        np.load(drift_path, allow_pickle=False),
        a.n_edits or len(dev["items"]),
        a.n_outside,
    )
    payload_dir.mkdir(parents=True, exist_ok=False)
    binding = write_json(payload_dir / "payload.json", data)
    report = {
        "mode": MODE,
        "banner": BANNER,
        "payload": binding,
        "summary": data["development_summary"],
    }
    if a.recipe:
        spec, identity, tok_sha, provenance = v4_construction(ds)
        m = {
            "schema_version": 1,
            "mode": MODE,
            "banner": BANNER,
            "cell": {
                "condition": "R1_learned_ff",
                "dataset": ds,
                "realization": "development",
                "order": "source",
            },
            "checkpoints": [n for n in (100, 300, 1000) if n <= len(data["items"])],
            "max_new": 32,
            "code_sha256": code_identity(),
            "tokenizer_sha256": tok_sha,
            "adapter_identity": identity,
            "payload": binding,
            "admission": {
                k: False
                for k in (
                    "lead_approved",
                    "protocol_frozen",
                    "condition_admitted",
                    "launch_authorized",
                )
            },
            "construction": spec,
            "reader_provenance": provenance,
            "source_bindings_sha256": bindings,
        }
        validate_development_payload(m, data)
        report["recipe"] = write_json(a.recipe, m)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
