"""Post-freeze CPU measurements of saved losses, KL and cached teacher entropy.

No model execution or checkpoint selection. Loss-mass entropy, binned-loss
entropy, and predictive entropy are intentionally separate quantities.
"""
from __future__ import annotations

import argparse
import csv
import gc
import gzip
import hashlib
import json
import math
import pickle
import resource
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

from aw.tail_class import analyze, window_plan
from aw.tail_figures import expected_shortfall

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
HT15 = ROOT / "logs/additional_work/round48/HT-15b-270/cell_tails.json"
HT17 = ROOT / "logs/additional_work/HT-17/snapshot-20261004-complete/report.json"
AWL = ROOT / "logs/additional_work/AW-L/report-round63-final/report.json"
BINS = np.array([0, .01, .1, .5, 1, 2, 3, 5, 8, 12, 20, 40, 80, np.inf])
PRIMARY = {"R1_learned_ff", "v0_stable", "R1_nonlearned"}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path, sources):
    raw = Path(path).read_bytes()
    sources[str(Path(path).resolve())] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def verify(path, expected, sources):
    actual = sha(path)
    if actual != expected:
        raise ValueError(f"Source changed: {path}")
    sources[str(Path(path).resolve())] = actual


def entropy(probabilities):
    p = np.asarray(probabilities, float)
    if not np.isfinite(p).all() or np.any(p < 0) or not np.isclose(p.sum(), 1):
        raise ValueError("A normalized probability vector is required")
    p = p[p > 0]
    return float(-np.dot(p, np.log(p)))


def kl(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    entropy(p)
    entropy(q)
    if p.shape != q.shape:
        raise ValueError("Probability supports must match")
    mask = p > 0
    if np.any(q[mask] == 0):
        return dict(value=None, status="infinite_support_mismatch")
    return dict(value=max(0., float(np.dot(p[mask], np.log(p[mask] / q[mask])))),
                status="finite")


def histogram(x, bins=BINS):
    x = np.asarray(x, float)
    if not x.size or not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError("Finite nonnegative losses required")
    counts = np.histogram(x, bins=bins)[0]
    if counts.sum() != x.size:
        raise ValueError("Bins do not cover the data")
    return dict(counts=counts.tolist(), entropy_nats=entropy(counts / counts.sum()))


def histogram_comparison(a, b, bins=BINS):
    """Distribution of a loss value, not KL between token predictions."""
    ca = np.asarray(histogram(a, bins)["counts"], float)
    cb = np.asarray(histogram(b, bins)["counts"], float)
    p, q = ca / ca.sum(), cb / cb.sum()
    mid = (p + q) / 2
    result = dict(raw_a_to_b=kl(p, q), raw_b_to_a=kl(q, p),
                  js_nats=(kl(p, mid)["value"] + kl(q, mid)["value"]) / 2,
                  smoothed={})
    for alpha in (.1, .5, 1.):
        pa, pb = (ca + alpha) / (ca.sum() + alpha * len(ca)), (
            cb + alpha) / (cb.sum() + alpha * len(cb))
        result["smoothed"][str(alpha)] = dict(a_to_b=kl(pa, pb)["value"],
                                             b_to_a=kl(pb, pa)["value"])
    return result


def concentration(x):
    x = np.asarray(x, float).ravel()
    if not x.size or np.any(x < 0) or not np.isfinite(x).all():
        raise ValueError("Nonnegative finite loss masses required")
    total = float(x.sum())
    if total == 0:
        return dict(status="undefined_zero_mass", entropy_nats=None,
                    effective_positions=None, kl_to_uniform_nats=None,
                    half_mass_positions=None, top_0_1_percent_mass_share=None)
    h = entropy(x / total)
    ordered = np.sort(x)[::-1]
    return dict(status="defined", entropy_nats=h, effective_positions=math.exp(h),
                kl_to_uniform_nats=math.log(x.size) - h,
                half_mass_positions=int(np.searchsorted(np.cumsum(ordered), total / 2) + 1),
                top_0_1_percent_mass_share=expected_shortfall(x, .999) * .001 * len(x) / total)


def describe(values):
    x = np.asarray(values, float).ravel()
    if not x.size or not np.isfinite(x).all():
        raise ValueError("Finite nonempty sample required")
    positive = np.maximum(x, 0.)
    idx = int(np.argmax(x))
    return dict(n=len(x), mean=float(x.mean()), minimum=float(x.min()), maximum=float(x.max()),
                max_flat_index=idx, quantiles={str(q): float(np.quantile(x, q))
                    for q in (.01, .05, .5, .95, .99, .999, .9999)},
                es99_positive=expected_shortfall(positive, .99),
                es99_9_positive=expected_shortfall(positive, .999),
                exceedances={str(u): dict(count=int((x > u).sum()), fraction=float((x > u).mean()),
                    conditional_mean=float(x[x > u].mean()) if np.any(x > u) else None)
                    for u in (.01, .1, .5, 1., 5., 10., 20.)},
                exact_zero=int((x == 0).sum()), negative=int((x < 0).sum()),
                positive_histogram=histogram(positive), positive_mass=concentration(positive))


def predictive_entropy(logits):
    z = np.array(logits, dtype=np.float64, copy=True).reshape(-1)
    if not np.isfinite(z).all() or z.size != 50257:
        raise ValueError("Expected one finite GPT-2 vocabulary logit row")
    z -= z.max()
    logp = z - np.log(np.exp(z).sum())
    p = np.exp(logp)
    h = float(-np.dot(p, logp))
    return h, math.log(len(p)) - h


class CachedRecord:
    """Inert state container for project dataclasses; avoids importing JAX."""


class CacheReader(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith("pccap."):
            return CachedRecord
        return super().find_class(module, name)


def cached_entropies(sources):
    """Trusted, hash-checked local caches only; deserialize one bank at a time."""
    rows = []
    caches_seen = set()
    for seed in range(3):
        report = read(ROOT / f"results/additional_work/PC-reader/train-bp-s{seed}/report.json", sources)
        for record in report["caches"]:
            path = Path(record["path"])
            if str(path) in caches_seen:
                continue
            caches_seen.add(str(path))
            verify(path, record["sha256"], sources)
            with path.open("rb") as f:
                bank = CacheReader(f).load()
            populations = defaultdict(list)
            if isinstance(bank, dict):
                dataset = "ordinary-text"
                for item in bank["bank"]:
                    populations["training-range-null-cache"].append(
                        (item.text_id, item.prefix.capoff_logits,
                         np.asarray(item.prefix.ids[:item.prefix.n], dtype='<i4').tobytes()))
            else:
                dataset = next(ds for ds in ("counterfact", "zsre", "mquake") if ds in path.name)
                if len(bank.items) != record["identity"]["n_items"]:
                    raise ValueError("Cached item coverage mismatch")
                split = 9 * len(bank.items) // 10
                for i, item in enumerate(bank.items):
                    population = "training-locality-cache" if i < split else "heldout-locality-cache"
                    for j, (_, _, prefix) in enumerate(item.locality):
                        populations[population].append((f"{item.item_id}:locality{j}", prefix.capoff_logits,
                            np.asarray(prefix.ids[:prefix.n], dtype='<i4').tobytes()))
            for population, pairs in populations.items():
                hs, ks, ids = [], [], []
                for label, logits, _ in pairs:
                    h, k = predictive_entropy(logits)
                    hs.append(h)
                    ks.append(k)
                    ids.append(label)
                rows.append(dict(dataset=dataset, seed=seed if dataset == "ordinary-text" else None,
                                 population=population, path=str(path), sha256=record["sha256"],
                                 logits_dtype="float16 cached teacher; float64 calculation",
                                 unique_token_prefixes=len({p[2] for p in pairs}),
                                 entropy=describe(hs), kl_teacher_to_uniform=describe(ks),
                                 lowest_entropy_id=ids[int(np.argmin(hs))],
                                 highest_entropy_id=ids[int(np.argmax(hs))]))
            del populations, bank
            gc.collect()
    return rows


def training(sources):
    runs = [("historical-v5-bp", 2, ROOT / "results/R1/pilot/r1_50_stream_sel6_text_s2")]
    runs += [(rule, seed, ROOT / f"results/additional_work/PC-reader/train-{rule}-s{seed}")
             for rule in ("bp", "epc") for seed in range(3)]
    out = []
    identities = {}
    for rule, seed, path in runs:
        file = path / "metrics.jsonl"
        raw = file.read_bytes()
        sources[str(file)] = hashlib.sha256(raw).hexdigest()
        rows = [json.loads(line) for line in raw.splitlines()]
        if len(rows) != 300:
            raise ValueError("Expected 300 recorded training steps")
        supplemental = rule != "historical-v5-bp"
        if supplemental:
            report = read(path / "report.json", sources)
            if report["status"] != "complete" or report["steps"] != 300:
                raise ValueError("Incomplete training")
            identities[rule, seed] = [r["episode_sha256"] for r in rows]
            if identities[rule, seed] != report["trajectory"]:
                raise ValueError("Training trajectory mismatch")
        else:
            read(path / "summary.json", sources)
        metrics = [r["metrics"] if supplemental else r for r in rows]
        result = dict(rule=rule, seed=seed, path=str(file), n=300, windows={},
                      diagnostic="settled answer CE" if rule == "epc" else "feedforward answer CE",
                      dev=[dict(step=r["step"] + (0 if supplemental else 1),
                                **{k: v for k, v in r.items() if k.startswith("dev_")})
                           for r in rows if any(k.startswith("dev_") for k in r)],
                      series={k: [m[k] for m in metrics] for k in ("answer", "preserve", "retrieval", "grad_norm")})
        for label, start, stop in (("all300", 0, 300), ("first50", 0, 50), ("last50", 250, 300),
                                   ("last150", 150, 300)):
            result["windows"][label] = {}
            for key in ("answer", "preserve", "retrieval", "grad_norm"):
                x = np.array(result["series"][key][start:stop])
                stats = describe(x)
                stats["maximum_step_one_based"] = start + stats["max_flat_index"] + 1
                result["windows"][label][key] = stats
        result["late_to_early_histogram"] = {
            k: histogram_comparison(result["series"][k][-50:], result["series"][k][:50])
            for k in ("answer", "preserve", "retrieval")}
        out.append(result)
    for seed in range(3):
        if identities["bp", seed] != identities["epc", seed]:
            raise ValueError("Paired BP/ePC episodes differ")
    return out


def evaluations(sources):
    stage4, ht17, awl = (read(p, sources) for p in (HT15, HT17, AWL))
    if len(stage4["cells"]) != 270:
        raise ValueError("Expected complete 270-cell inventory")
    specs = [dict(c, phase="stage4", seed=None) for c in stage4["cells"]]
    specs += [c for c in ht17["cells"] if c["phase"] in ("PC-reader", "AW-B")]
    for c in awl["cells"]:
        if c["reused_from_pc_reader"]:
            continue
        if c["status"] != "complete":
            raise ValueError("Incomplete AW-L cell")
        specs.append(dict(phase="AW-L", condition=f"read{c['read_taps']}-write{c['write_sites']}",
                          dataset=c["dataset"], seed=c["seed"], realization=0, order=100,
                          checkpoint=300, vector=c["vector"]))
    existing = {(c["condition"], c["dataset"], c["realization"], c["order"]): c["statistics"]
                for c in ht17["cells"] if c["phase"] == "stage4"}
    weights, folds = window_plan(1931, 200)
    output = []
    for i, spec in enumerate(specs):
        vector = spec["vector"]
        path = Path(vector["path"])
        verify(path, vector["sha256"], sources)
        with np.load(path, allow_pickle=False) as data:
            v = data["values"]
        if v.shape != (1931, 127, 5) or not np.isfinite(v).all() or np.any(v[:, :, :3] < 0):
            raise ValueError(f"Invalid vector {path}")
        if np.min(v[:, :, 3:]) < -1e-8:
            raise ValueError("KL outside roundoff tolerance")
        delta = v[:, :, 0] - v[:, :, 1]
        row = {k: spec[k] for k in ("phase", "condition", "dataset", "seed", "realization", "order", "checkpoint")}
        row.update(vector=vector, positions=delta.size,
                   metrics={"cap_nll": describe(v[:, :, 0]), "capoff_nll": describe(v[:, :, 1]),
                            "delta_nll": describe(delta), "kl_capoff_to_cap": describe(v[:, :, 3]),
                            "kl_original_to_cap": describe(v[:, :, 4])},
                   loss_histogram_cap_to_capoff=histogram_comparison(v[:, :, 0], v[:, :, 1]),
                   severe_harm_kl_overlap=dict(harm_gt5=int((delta > 5).sum()),
                       also_kl_gt1=int(((delta > 5) & (v[:, :, 3] > 1)).sum())))
        if spec["phase"] == "stage4" and spec["condition"] in PRIMARY:
            coordinate = tuple(spec[k] for k in ("condition", "dataset", "realization", "order"))
            if spec["dataset"] == "mquake":
                stats, _ = analyze(delta, weights=weights, folds=folds,
                                   bootstrap_fits=spec["realization"] == 0 and spec["order"] == 100)
                row["tail_fit_origin"] = "new_posthoc_saved_vector_analysis"
            else:
                stats = existing[coordinate]
                if not np.isclose(stats["mean_signed"], delta.mean(), rtol=1e-12, atol=1e-15):
                    raise ValueError("HT-17 reused statistics mismatch")
                row["tail_fit_origin"] = str(HT17)
            row["tail_fits"] = {u: {k: val for k, val in s.items() if k != "survival"}
                                for u, s in stats["thresholds"].items()}
            kl_stats, _ = analyze(np.maximum(v[:, :, 3], 0), weights=weights, folds=folds,
                                 bootstrap_fits=spec["realization"] == 0 and spec["order"] == 100)
            row["kl_tail_fits"] = {u: {k: val for k, val in s.items() if k != "survival"}
                                   for u, s in kl_stats["thresholds"].items()}
        grid = np.geomspace(.01, max(.0101, float(delta.max())), 120)
        flat = np.sort(delta.ravel())
        row["survival"] = dict(x=grid.tolist(), probability=((len(flat) - np.searchsorted(
            flat, grid, side="right")) / len(flat)).tolist())
        output.append(row)
        if (i + 1) % 30 == 0:
            print(f"Measured {i + 1}/{len(specs)} evaluation cells", flush=True)
    return output


def groups(cells):
    grouped = defaultdict(list)
    for c in cells:
        grouped[c["phase"], c["condition"], c["dataset"]].append(c)
    result = []
    for (phase, condition, dataset), rows in sorted(grouped.items()):
        group = dict(phase=phase, condition=condition, dataset=dataset, cells=len(rows), metrics={})
        for metric in rows[0]["metrics"]:
            group["metrics"][metric] = {}
            for key in ("mean", "maximum", "es99_positive", "es99_9_positive"):
                vals = [r["metrics"][metric][key] for r in rows]
                group["metrics"][metric][key] = dict(mean=float(np.mean(vals)), minimum=min(vals), maximum=max(vals))
            for u in (.01, 1., 5., 10.):
                es = [r["metrics"][metric]["exceedances"][str(u)] for r in rows]
                n = sum(e["count"] for e in es)
                group["metrics"][metric][f"exceed_{u}"] = dict(
                    fraction=float(np.mean([e["fraction"] for e in es])),
                    conditional_mean=sum(e["count"] * (e["conditional_mean"] or 0) for e in es) / n if n else None)
            for key in ("entropy_nats", "effective_positions", "kl_to_uniform_nats", "half_mass_positions",
                        "top_0_1_percent_mass_share"):
                vals = [r["metrics"][metric]["positive_mass"][key] for r in rows]
                group["metrics"][metric][key] = None if any(v is None for v in vals) else dict(
                    mean=float(np.mean(vals)), minimum=min(vals), maximum=max(vals))
        result.append(group)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    sources = {}
    cells = evaluations(sources)
    trains = training(sources)
    print("Reading cached teacher logits, one bank at a time", flush=True)
    cached = cached_entropies(sources)
    sources[str(Path(__file__).resolve())] = sha(__file__)
    for name in ("aw/tail_class.py", "aw/tail_figures.py", "src/pccap/revision_v1/epc_train.py",
                 "src/pccap/revision_v1/train_fast.py", "aw/pc_reader_train.py"):
        sources[str(ROOT / name)] = sha(ROOT / name)
    report = dict(schema="entropy-tail-measurements-v1", created_utc=datetime.now(timezone.utc).isoformat(),
                  model_calls=0, gpu_seconds=0, bins=[float(x) if np.isfinite(x) else "inf" for x in BINS],
                  quantile_method="numpy linear", cells=cells, groups=groups(cells),
                  training=trains, cached_teacher_entropy=cached, sources_sha256=sources,
                  versions=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__),
                  wall_seconds=time.monotonic() - started,
                  peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    raw = (json.dumps(report, separators=(",", ":"), allow_nan=False) + "\n").encode()
    (args.output / "measurements.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    summaries = []
    for cell in cells:
        row = {k: cell[k] for k in ("phase", "condition", "dataset", "seed", "realization", "order", "checkpoint")}
        row.update(vector_path=cell["vector"]["path"], vector_sha256=cell["vector"]["sha256"])
        for metric, stats in cell["metrics"].items():
            for key in ("mean", "maximum", "es99_positive", "es99_9_positive"):
                row[f"{metric}_{key}"] = stats[key]
            for key in ("entropy_nats", "effective_positions", "kl_to_uniform_nats"):
                row[f"{metric}_positive_mass_{key}"] = stats["positive_mass"][key]
        summaries.append(row)
    with (args.output / "cells.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    (args.output / "sources.json").write_text(json.dumps(sources, indent=2) + "\n")
    print(json.dumps(dict(cells=len(cells), training_runs=len(trains), cache_populations=len(cached),
                          wall_seconds=report["wall_seconds"], peak_rss_mib=report["peak_rss_mib"])))


if __name__ == "__main__":
    main()
