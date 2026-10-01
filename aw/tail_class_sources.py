"""Read-only HT-17 adapters; completed outputs only, no model imports/execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from aw.tail_cells import FIELDS, load_cells
from aw.tail_figures import CELL_RE

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ("R1_learned_ff", "v0_stable", "R1_nonlearned")


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path, bindings):
    path = Path(path).resolve()
    raw = path.read_bytes()
    bindings[str(path)] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def load_delta(cell, bindings):
    vector = cell["vector"]
    path = Path(vector["path"])
    if sha(path) != vector["sha256"]:
        raise ValueError(f"vector hash changed: {path}")
    bindings[str(path)] = vector["sha256"]
    if cell.get("format") == "pilot_json":
        d = read(path, bindings)
        on, off = np.asarray(d["nll_cap_on"]), np.asarray(d["nll_cap_off"])
        values = on - off
    else:
        with np.load(path, allow_pickle=False) as archive:
            v = archive["values"]
        if v.shape != (cell["windows"], 127, 5) or not np.isfinite(v).all():
            raise ValueError("invalid five-field vector shape/values")
        values = v[:, :, 0] - v[:, :, 1]
    if values.shape != (cell["windows"], 127) or not np.isfinite(values).all():
        raise ValueError("invalid signed harm matrix")
    return values


def efficacy(checkpoint):
    ret = checkpoint["retention"]
    if len(ret["rows"]) != ret["planned"]:
        raise ValueError("incomplete retention endpoint")
    return {"RET-ES": float(np.mean([r["es"] for r in ret["rows"]])),
            "RET-GS": float(np.mean([r["gs"] for r in ret["rows"]]))}


def stage4(bindings, secondary):
    rows, source = load_cells(ROOT / "logs/R1/final_queue")
    bindings.update(source["sources_sha256"])
    pop = source["population"]["coverage"]
    cells = []
    for r in sorted(rows, key=lambda c: (c["condition"], c["dataset"], c["realization"],
                                        c["order"])):
        if r["dataset"] not in ("zsre", "counterfact"):
            continue
        if not secondary and r["condition"] not in PRIMARY:
            continue
        if CELL_RE.search(r["attempt"]) is None:
            raise ValueError("unexpected Stage-4 attempt identity")
        cp = read(Path(r["attempt"]) / f"checkpoint-{r['checkpoint']}.json", bindings)
        c = {k: r[k] for k in ("condition", "dataset", "realization", "order", "vector",
                               "checkpoint", "attempt", "finish_receipt")}
        c.update(phase="stage4", seed=None, population=pop["windows_int64le_sha256"],
                 windows=pop["complete_windows"], efficacy=efficacy(cp), gate=None,
                 role="primary" if r["condition"] in PRIMARY else "secondary")
        cells.append(c)
    return cells, source


def check_selection(s, population):
    if (s["windows_sha256"] != population or s["windows"] != 1931
            or s["positions"] != 245237 or s["window_tokens"] != 128):
        raise ValueError("supplemental ordinary-text population mismatch")


def aw_b(bindings, population):
    root = ROOT / "results/additional_work/AW-B/evaluation-20260929"
    doc, cost = read(root / "report.json", bindings), read(root / "cost.json", bindings)
    if doc["status"] != "complete" or cost["status"] != "complete":
        raise ValueError("AW-B evaluation is not complete")
    if doc["command"] != "evaluate" or len(doc["cells"]) != 10:
        raise ValueError("wrong AW-B evaluation inventory")
    check_selection(doc["selection"], population)
    cells = []
    for name, row in sorted(doc["cells"].items()):
        if row != read(root / name / "report.json", bindings):
            raise ValueError("AW-B aggregate/per-memory mismatch")
        dataset, order = name.split("-o")
        for condition, harm in sorted(row["harm"].items()):
            check_selection(harm["selection"], population)
            gate = harm["telemetry"]
            if gate["logical_positions"] != 245237 or gate["selected"] + gate["hard_null"] != 245237:
                raise ValueError("AW-B gate coverage mismatch")
            cells.append(dict(
                phase="AW-B", condition=condition, dataset=dataset, realization=0,
                order=int(order), seed=None, population=population, windows=1931,
                checkpoint=300, vector=harm["vectors"], gate=gate,
                efficacy={k: v["value"] for k, v in row["efficacy"][condition]["metrics"].items()},
                role="primary", memory=name, reference="own_capoff",
            ))
    return cells


def readers(bindings, population):
    cells, pending = [], []
    for rule in ("bp", "epc"):
        for seed in range(3):
            for dataset in ("zsre", "counterfact"):
                root = ROOT / f"results/additional_work/PC-reader/eval-{rule}-s{seed}-{dataset}"
                if not (root / "report.json").exists() or not (root / "cost.json").exists():
                    pending.append(dict(rule=rule, seed=seed, dataset=dataset, status="pending"))
                    continue
                doc = read(root / "report.json", bindings)
                cost = read(root / "cost.json", bindings)
                if doc["status"] != "complete" or cost["status"] != "complete":
                    pending.append(dict(rule=rule, seed=seed, dataset=dataset, status="unfinished"))
                    continue
                harm = read(root / "harm/summary.json", bindings)
                hc = read(root / "harm/cost.json", bindings)
                finish = read(root / "stream/finish.json", bindings)
                cp = read(root / "stream/checkpoint-300.json", bindings)
                if (doc["development"] or doc["rule"] != rule or doc["seed"] != seed
                        or doc["dataset"] != dataset or hc["status"] != "complete"
                        or finish["status"] != "complete" or doc["harm"] != harm
                        or finish["state_sha256"] != harm["state_sha256"]
                        or harm["fields"] != FIELDS):
                    raise ValueError("reader completion/coordinate/harm binding mismatch")
                check_selection(harm["selection"], population)
                if doc["gate_telemetry"]["logical_positions"] != 245237:
                    raise ValueError("reader gate coverage mismatch")
                cells.append(dict(
                    phase="PC-reader", condition=rule, dataset=dataset, realization=0,
                    order=100, seed=seed, population=population, windows=1931, checkpoint=300,
                    vector=harm["vectors"], gate=doc["gate_telemetry"], role="primary",
                    efficacy={k: v["value"] for k, v in cp["metrics"].items()},
                    reference="own_capoff",
                ))
    return cells, pending


def pilot(bindings):
    """Legacy input ordering: exact ordered cap-off matrix, not explicit token IDs."""
    cells, off_identity = [], None
    for arm in ("ordinary", "kappa02", "kappa05", "clip2"):
        for seed in range(3):
            run = f"r1_50_stream_sel6_text_s{seed}" if arm == "ordinary" else f"ht3_{arm}_s{seed}"
            for dataset in ("zsre", "counterfact", "mquake"):
                path = ROOT / f"results/R1/drift_assay_ht3_{run}_{dataset}.positions.json"
                d = read(path, bindings)
                off = np.asarray(d["nll_cap_off"], dtype="<f8")
                h = hashlib.sha256(off.tobytes()).hexdigest()
                if off.shape != (32, 127) or (off_identity is not None and off_identity != h):
                    raise ValueError("legacy pilot ordered cap-off matrix mismatch")
                off_identity = h
                retpath = ROOT / (f"results/R1/stream_eval_{run}_stepavg_rare1_null0.5"
                                  + ("" if dataset == "zsre" else f"@{dataset}") + ".json")
                ret = read(retpath, bindings)["stream_metrics"]
                cells.append(dict(
                    phase="kappa-pilot", condition=arm, dataset=dataset, realization=None,
                    order=21, seed=seed, population="legacy-32-capoff-" + h, windows=32,
                    checkpoint=100, format="pilot_json", vector=dict(path=str(path), sha256=sha(path)),
                    gate=None, efficacy={"RET-GS": ret["ret_gs_end"]}, role="secondary",
                    reference="own_capoff; legacy file equates original and cap-off",
                ))
    return cells


def inventory(secondary=False):
    bindings = {}
    cells, source = stage4(bindings, secondary)
    population = source["population"]["coverage"]["windows_int64le_sha256"]
    cells += aw_b(bindings, population)
    r, pending = readers(bindings, population)
    cells += r
    cells += pilot(bindings)
    for c in cells:
        c["id"] = "/".join(str(c[k]) for k in (
            "phase", "dataset", "condition", "realization", "order", "seed"))
    if len({c["id"] for c in cells}) != len(cells):
        raise ValueError("duplicate cell identity")
    return cells, dict(sources_sha256=bindings, stage4_admission=source,
                      pending_reader_cells=pending, legacy_population_limit=(
                          "Explicit token IDs absent; producer ordering and exact ordered "
                          "cap-off equality support legacy pairing only. Not joined to full inventory."))
