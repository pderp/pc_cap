"""Aggregate the development kappa pilot exactly as manifest v3; never run a model.

Outputs are exclusive-create files under logs/r1_round18. Missing, invalid and
charged-failure rows remain in the 36-row inventory. Source results are read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("ordinary", "kappa02", "kappa05", "clip2")
SEEDS = (0, 1, 2)
DATASETS = ("zsre", "counterfact", "mquake")
METRICS = ("ret_gs", "ls_complete_answer", "unseen_rate", "es95", "maximum")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def positive_tail(on, off):
    """Fractional empirical upper 5% mean, including zero harm in denominator."""
    if not on or len(on) != len(off):
        raise ValueError("empty or unequal populations")
    if any(not math.isfinite(x) for x in (*on, *off)):
        raise ValueError("nonfinite tail population")
    harm = sorted((max(a - b, 0.0) for a, b in zip(on, off, strict=True)), reverse=True)
    mass = len(harm) * 0.05
    whole = math.floor(mass)
    total = math.fsum(harm[:whole])
    if whole < len(harm):
        total += (mass - whole) * harm[whole]
    return {"es95": total / mass, "maximum": harm[0]}


def separation(candidate, ordinary):
    if len(candidate) != 3 or len(ordinary) != 3:
        raise ValueError("exactly three seed macros required")
    delta = math.fsum(candidate) / 3 - math.fsum(ordinary) / 3
    spread = max(max(candidate) - min(candidate), max(ordinary) - min(ordinary))
    return {
        "signed_difference": delta,
        "seed_spread_threshold": spread,
        "separated": abs(delta) > spread,
        "separated_decrease": delta < 0 and abs(delta) > spread,
    }


class Inputs:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.bindings = {}

    def read(self, relative):
        path = (self.root / relative).resolve()
        if "confirm" in path.parts or not path.is_relative_to(self.root):
            raise PermissionError("only unsealed repository inputs")
        data = path.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        if sha(path) != h:
            raise ValueError("input changed while reading")
        self.bindings[str(path.relative_to(self.root))] = h
        return json.loads(data)

    def unchanged(self):
        return [p for p, h in self.bindings.items() if sha(self.root / p) != h]


def framing(root):
    text = (Path(root) / "docs/heavy_tail_counter_review.md").read_text()
    start = text.index("**What it is not.**")
    return text[start:].split("\n\n", 1)[0]


def valid_rate(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("rate is not numeric")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("invalid rate")
    return value


def extract_row(inputs, arm, seed, dataset):
    run = f"r1_50_stream_sel6_text_s{seed}" if arm == "ordinary" else f"ht3_{arm}_s{seed}"
    row = dict(arm=arm, seed=seed, dataset=dataset, run=run, issues=[], **dict.fromkeys(METRICS))
    paths = {
        "retention": f"results/R1/stream_eval_{run}_stepavg_rare1_null0.5"
        + ("" if dataset == "zsre" else f"@{dataset}")
        + ".json",
        "unseen": f"results/R1/endpoints/{run}_stepavg_rare1_n100_unseen_{dataset}/summary.json",
        "tail": f"results/R1/drift_assay_ht3_{run}_{dataset}.positions.json",
        "tail_summary": f"results/R1/drift_assay_ht3_{run}_{dataset}.json",
    }
    row["sources"] = paths
    docs = {}
    for kind, path in paths.items():
        try:
            docs[kind] = inputs.read(path)
        except (OSError, ValueError) as exc:
            row["issues"].append(f"{kind}: {type(exc).__name__}: {exc}")
    for kind in ("retention", "unseen", "tail"):
        if kind not in docs:
            continue
        try:
            obj = docs[kind]
            if kind == "retention":
                args = obj["args"]
                expected = dict(
                    dataset=dataset,
                    n=100,
                    stream_seed=21,
                    delta_steps=5,
                    delta_lr=0.1,
                    null_threshold=0.5,
                    rare_overlap=1,
                )
                if any(args.get(k) != v for k, v in expected.items()):
                    raise ValueError("retention evaluation configuration mismatch")
                if Path(obj["theta"]).name != "theta_avg150-300.npz":
                    raise ValueError("predeclared averaged checkpoint required")
                row["ret_gs"] = valid_rate(obj["stream_metrics"]["ret_gs_end"])
                row["ls_complete_answer"] = valid_rate(
                    obj["stream_metrics"]["ls_complete_answer_end"]
                )
                row["retention_population"] = digest(
                    {
                        "dataset": dataset,
                        "seed": args["stream_seed"],
                        "dev_manifest": args.get("dev_manifest"),
                        "selected": (obj.get("dev_receipt") or {}).get("selected_item_ids"),
                    }
                )
            elif kind == "unseen":
                s = obj["summary"]
                if obj["dataset"] != dataset or obj["n_edits"] != 100:
                    raise ValueError("unseen dataset/occupancy mismatch")
                if any(s.get(k) != 100 for k in ("expected_n", "scored_n", "firing_observed_n")):
                    raise ValueError("incomplete unseen inventory")
                ff = s["false_fires"]
                if type(ff) is not int or not 0 <= ff <= 100:
                    raise ValueError("invalid false-fire count")
                ids = obj["outside_item_ids"]
                if len(ids) != 100 or len(set(ids)) != 100:
                    raise ValueError("unseen IDs missing or duplicated")
                row.update(
                    unseen_rate=ff / 100,
                    false_fires=ff,
                    unseen_population=digest([obj["edited_item_ids"], ids]),
                )
            else:
                if (
                    obj["windows"] != 32
                    or obj["positions_per_window"] != 127
                    or obj["rule"] != "0.5:none"
                ):
                    raise ValueError("tail definition mismatch")
                on, off = obj["nll_cap_on"], obj["nll_cap_off"]
                if any(len(a) != 32 or any(len(w) != 127 for w in a) for a in (on, off)):
                    raise ValueError("tail matrix must be 32 by 127")
                row.update(positive_tail([x for w in on for x in w], [x for w in off for x in w]))
                # The legacy producer has no embedded IDs. Its fixed row/column
                # ordering plus identical cap-off values certifies comparison;
                # the source/token snapshot and this limitation are reported.
                row["tail_population"] = digest(
                    {"rule": obj["rule"], "off": off, "policy": obj["policy"]}
                )
                summary = docs.get("tail_summary")
                if (
                    not summary
                    or summary["dataset"] != dataset
                    or summary["windows"] != 32
                    or summary["window"] != 128
                ):
                    raise ValueError("tail summary missing or mismatched")
                theta = summary["theta"]
                if Path(theta).name != "theta_avg150-300.npz":
                    raise ValueError("tail checkpoint is not predeclared average")
        except (ValueError, KeyError, TypeError) as exc:
            row["issues"].append(f"{kind}: {exc}")
            for metric in {
                "retention": ("ret_gs", "ls_complete_answer"),
                "unseen": ("unseen_rate",),
                "tail": ("es95", "maximum"),
            }[kind]:
                row[metric] = None
    if all(k in docs for k in ("retention", "unseen", "tail_summary")):
        t = [
            docs["retention"].get("theta"),
            docs["unseen"].get("theta", {}).get("path"),
            docs["tail_summary"].get("theta"),
        ]
        if len(set(t)) != 1:
            row["issues"].append("checkpoint paths disagree across endpoints")
    row["status"] = "complete" if not row["issues"] else "unavailable"
    return row


def summarize(rows):
    result = {}
    for arm in ARMS:
        arm_rows = [r for r in rows if r["arm"] == arm]
        stats = {}
        for metric in METRICS:
            seeds = []
            for seed in SEEDS:
                values = [r[metric] for r in arm_rows if r["seed"] == seed]
                seeds.append(
                    math.fsum(values) / 3
                    if len(values) == 3 and all(v is not None for v in values)
                    else None
                )
            stats[metric] = {
                "seed_macros": seeds,
                "mean": math.fsum(seeds) / 3 if all(v is not None for v in seeds) else None,
            }
        stats["unseen_by_dataset"] = {
            ds: (
                math.fsum(v) / 3
                if len(v := [r["unseen_rate"] for r in arm_rows if r["dataset"] == ds]) == 3
                and all(x is not None for x in v)
                else None
            )
            for ds in DATASETS
        }
        result[arm] = stats
    return result


def comparisons(stats, rows, failures, source_errors):
    out = {}
    for arm in ("kappa02", "kappa05", "clip2"):
        a, o = stats[arm], stats["ordinary"]
        relevant = [r for r in rows if r["arm"] in (arm, "ordinary")]
        issues = [
            f"{r['run']}/{r['dataset']}: {r['status']}"
            for r in relevant
            if r["status"] != "complete"
        ]
        for ds in DATASETS:
            for field in ("tail_population", "unseen_population", "retention_population"):
                keys = {r.get(field) for r in relevant if r["dataset"] == ds}
                if len(keys) != 1 or None in keys:
                    issues.append(f"{ds}: {field} incomplete or unequal")
        issues.extend(source_errors)
        issues.extend(
            f"charged failure: {f['run']}" for f in failures if f["arm"] in (arm, "ordinary")
        )
        tests = {}
        for metric in ("es95", "maximum"):
            x, y = a[metric]["seed_macros"], o[metric]["seed_macros"]
            tests[metric] = separation(x, y) if all(v is not None for v in x + y) else None
        floor = None if o["ret_gs"]["mean"] is None else o["ret_gs"]["mean"] - 0.02
        ret_pass = (
            None if floor is None or a["ret_gs"]["mean"] is None else a["ret_gs"]["mean"] >= floor
        )
        unseen = {}
        for ds in DATASETS:
            x, y = a["unseen_by_dataset"][ds], o["unseen_by_dataset"][ds]
            unseen[ds] = {
                "candidate": x,
                "ordinary": y,
                "nonincrease": None if x is None or y is None else x <= y,
            }
        tail_pass = any(t and t["separated"] for t in tests.values())
        passed = (
            ret_pass is True
            and all(t["nonincrease"] is True for t in unseen.values())
            and tail_pass
        )
        verdict = (
            "unavailable"
            if issues
            else ("declared secondary condition" if passed else "null result")
        )
        if arm == "clip2":
            verdict = "descriptive control" if not issues else "unavailable"
        out[arm] = dict(
            verdict=verdict,
            unavailable_reasons=issues,
            retention_floor=floor,
            retention_pass=ret_pass,
            unseen_by_dataset=unseen,
            tails=tests,
            tail_separation=tail_pass if all(t is not None for t in tests.values()) else None,
            robustness_improvement_eligible=not issues
            and ret_pass is True
            and all(t["nonincrease"] is True for t in unseen.values())
            and any(t and t["separated_decrease"] for t in tests.values()),
        )
    return out


def aggregate(root=ROOT):
    root = Path(root).resolve()
    inputs = Inputs(root)
    manifest = inputs.read("manifests/revision_v1/kappa_pilot_v3.json")
    if manifest["schema_version"] != 3 or tuple(manifest["aggregation"]["datasets"]) != DATASETS:
        raise ValueError("pilot v3 required")
    if (
        tuple(a["id"] for a in manifest["arms"]) != ARMS
        or tuple(manifest["aggregation"]["seeds"]) != SEEDS
    ):
        raise ValueError("unrecognized arm/seed plan")
    source_errors = []
    sources = manifest["training"]["sources_sha256"]
    for p, h in sources.items():
        if sha(root / p) != h:
            source_errors.append("manifest source hash mismatch: " + p)
    rows = [extract_row(inputs, arm, seed, ds) for arm in ARMS for seed in SEEDS for ds in DATASETS]
    failures = []
    for arm in ARMS:
        for seed in SEEDS:
            run = f"r1_50_stream_sel6_text_s{seed}" if arm == "ordinary" else f"ht3_{arm}_s{seed}"
            p = f"results/R1/pilot/{run}/failure_receipt.json"
            if (root / p).exists():
                receipt = inputs.read(p)
                failures.append(
                    dict(
                        arm=arm,
                        seed=seed,
                        run=run,
                        charged=True,
                        charged_wall_seconds=receipt.get("charged_wall_s"),
                        receipt=receipt,
                        path=p,
                    )
                )
                for row in rows:
                    if row["run"] == run:
                        row["status"] = "charged_failure"
    source_errors += ["changed during aggregation: " + p for p in inputs.unchanged()]
    stats = summarize(rows)
    paragraph = framing(root)
    return dict(
        schema_version=1,
        task="HT-3d",
        created_at=datetime.now(timezone.utc).isoformat(),
        scope=manifest["aggregation"]["inferential_scope"],
        rows=rows,
        arms=stats,
        comparisons=comparisons(stats, rows, failures, source_errors),
        failures=failures,
        source_errors=source_errors,
        input_bindings=inputs.bindings,
        producer_sources=sources,
        framing=paragraph,
        framing_source_sha256=sha(root / "docs/heavy_tail_counter_review.md"),
        complete_rows=sum(r["status"] == "complete" for r in rows),
        expected_rows=36,
        population_identity_note="Legacy tail files contain no explicit token IDs: fixed 32x127 positions from the manifest-bound producer and identical ordered cap-off NLLs are compared. This is reconstructed population identity, not a historical embedded token-hash receipt.",
        clip_comparison={
            m: (
                stats["kappa05"][m]["mean"] - stats["clip2"][m]["mean"]
                if stats["kappa05"][m]["mean"] is not None and stats["clip2"][m]["mean"] is not None
                else None
            )
            for m in METRICS
        },
        clip_interpretation=manifest["comparator_interpretation"],
        verdict_scope="Each coupled arm requires all its own and ordinary seed/dataset rows; missing clipped-control rows leave the descriptive control comparison pending. Whole-pilot completion is reported separately.",
    )


def markdown(report):
    def f(x):
        return "unavailable" if x is None else f"{x:.9g}"

    lines = [
        "# HT-3d κ pilot aggregation",
        "",
        report["scope"] + ".",
        f"Complete rows: {report['complete_rows']}/36. Snapshot: {report['created_at']}.",
        "",
        report["framing"],
        "",
        report["verdict_scope"],
        "",
        "| Arm | Seed | Dataset | RET-GS | LS (legacy complete-answer) | Unseen FF/100 | ES95 harm | Max harm | Status |",
        "|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in report["rows"]:
        lines.append(
            f"| {r['arm']} | {r['seed']} | {r['dataset']} | {f(r['ret_gs'])} | {f(r['ls_complete_answer'])} | {r.get('false_fires', '—')} | {f(r['es95'])} | {f(r['maximum'])} | {r['status']} |"
        )
    lines += [
        "",
        "Equal dataset weights within seed, then equal weights across all three seeds; no missing-value averaging.",
        "",
        "| Arm | RET-GS macro | ES95 seed macros | ES95 macro | Maximum seed macros | Maximum macro |",
        "|---|---:|---|---:|---|---:|",
    ]
    for arm, s in report["arms"].items():
        lines.append(
            f"| {arm} | {f(s['ret_gs']['mean'])} | {', '.join(map(f, s['es95']['seed_macros']))} | {f(s['es95']['mean'])} | {', '.join(map(f, s['maximum']['seed_macros']))} | {f(s['maximum']['mean'])} |"
        )
    for arm, c in report["comparisons"].items():
        lines += [
            "",
            f"## {arm}: {c['verdict']}",
            "",
            f"Retention floor: {f(c['retention_floor'])}; passes: {c['retention_pass']}.",
            "Unseen non-increase by dataset: "
            + json.dumps(c["unseen_by_dataset"], sort_keys=True)
            + ".",
            "Tail contrasts (signed candidate − ordinary): "
            + json.dumps(c["tails"], sort_keys=True)
            + ".",
            f"Eligible for a robustness-improvement description: {c['robustness_improvement_eligible']}. An increase can separate but is not an improvement.",
        ]
        lines += [f"- {x}" for x in c["unavailable_reasons"]]
    lines += [
        "",
        "## Clipped control",
        "",
        report["clip_interpretation"],
        "κ0.5 minus clip2, descriptive: " + json.dumps(report["clip_comparison"], sort_keys=True),
        "",
        "## Missingness, failures and provenance",
        "",
        report["population_identity_note"],
        "Legacy LS is printed as recorded; it is not silently converted to the DEC-053 driver convention.",
        f"Charged failures: {len(report['failures'])}; receipts and costs are retained in JSON.",
        "Input paths and SHA-256 values are in the companion JSON. Raw owner files were never modified.",
        "",
    ]
    lines += [
        f"- {r['run']}/{r['dataset']}: {'; '.join(r['issues'])}"
        for r in report["rows"]
        if r["issues"]
    ]
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-prefix", type=Path, required=True)
    args = p.parse_args(argv)
    base = args.output_prefix.resolve()
    if not base.is_relative_to(ROOT / "logs/r1_round18"):
        p.error("outputs must be under logs/r1_round18")
    paths = [Path(str(base) + suffix) for suffix in (".json", ".md")]
    if any(x.exists() for x in paths):
        p.error("new output prefix required; existing reports are immutable")
    report = aggregate()
    texts = [json.dumps(report, indent=2, allow_nan=False) + "\n", markdown(report)]
    base.parent.mkdir(parents=True, exist_ok=True)
    for path, text in zip(paths, texts, strict=True):
        with path.open("x") as f:
            f.write(text)
    print(
        json.dumps(
            {
                "complete_rows": report["complete_rows"],
                "verdicts": {k: v["verdict"] for k, v in report["comparisons"].items()},
                "outputs": [str(p) for p in paths],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
