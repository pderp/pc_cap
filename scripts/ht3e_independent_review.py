"""Independent CPU reproduction of the 36 pilot cells and six stress filings.

Reads original measurement files. Does not call the prior aggregator, its tail
helper or the stress relative/recovery helpers. No model or result-file writes.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scripts.r1_d9_receipts import ref, sha
from scripts.r1_d10a_review import ROOT, write_new

ARMS = ("ordinary", "kappa02", "kappa05", "clip2")
DATASETS = ("zsre", "counterfact", "mquake")
CADENCE = (20, 60, 70, 80, 100)


def tail(values):
    x = np.asarray(values, dtype=np.float64).ravel()
    if not x.size or not np.isfinite(x).all():
        raise ValueError("finite nonempty tail population required")
    x = np.sort(np.maximum(x, 0))[::-1]
    mass = len(x) / 20
    weights = np.clip(mass - np.arange(len(x)), 0, 1)
    return float(x @ weights / mass), float(x[0])


def recovery_from_bands(bands):
    if set(bands) != set(CADENCE):
        raise ValueError("complete fixed cadence required")
    candidates = [i for i in range(1, 5) if all(bands[t] for t in CADENCE[i:])]
    if not candidates:
        return {
            "recovered": False,
            "right_censored": True,
            "censor_after_updates": 40,
            "origin": "treatment end (edit60), not time of first detected harm",
        }
    i = candidates[0]
    return {
        "recovered": True,
        "right_censored": False,
        "lag_interval_updates": [0 if i == 1 else CADENCE[i - 1] - 60, CADENCE[i] - 60],
    }


class Reader:
    def __init__(self):
        self.bindings = {}

    def read(self, path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        if not path.is_relative_to(ROOT) or "confirm" in path.parts:
            raise PermissionError("unsealed repository measurements only")
        value = sha(path)
        if expected and expected != value:
            raise ValueError("bound source changed: " + str(path))
        self.bindings[str(path)] = value
        return json.loads(path.read_text())

    def verify(self):
        if any(sha(p) != h for p, h in self.bindings.items()):
            raise ValueError("source changed during review")


def pilot_review(reader):
    previous = reader.read("logs/r1_round18/ht3d-pilot-final-aliases.json")
    manifest = reader.read("manifests/revision_v1/kappa_pilot_v3.json")
    for name, expected in previous["input_bindings"].items():
        reader.read(name, expected)
    aliases = {a["requested_path"]: a for a in previous["legacy_name_aliases"]}
    rows, populations = [], defaultdict(list)
    if {(r["arm"], r["seed"], r["dataset"]) for r in previous["rows"]} != {
        (arm, seed, ds) for arm in ARMS for seed in range(3) for ds in DATASETS
    } or len(previous["rows"]) != 36:
        raise ValueError("exact 36-cell inventory required")
    for old in previous["rows"]:
        docs = {}
        for kind, name in old["sources"].items():
            if name in aliases and not (ROOT / name).exists():
                alias = aliases[name]
                docs[kind] = reader.read(alias["observed_path"], alias["observed_sha256"])
                reference = reader.read(
                    alias["population_reference"]["path"], alias["population_reference"]["sha256"]
                )
                actual = docs[kind]
                if (
                    actual["theta"] != alias["theta"]
                    or sha(alias["theta"]["path"]) != alias["theta"]["sha256"]
                    or any(
                        actual[k] != reference[k] for k in ("edited_item_ids", "outside_item_ids")
                    )
                ):
                    raise ValueError("legacy alias checkpoint/population differs")
            else:
                docs[kind] = reader.read(name)
        ret, unseen, positions, summary = [
            docs[k] for k in ("retention", "unseen", "tail", "tail_summary")
        ]
        if (
            ret["args"]["n"] != 100
            or ret["args"]["stream_seed"] != 21
            or ret["args"]["dataset"] != old["dataset"]
            or Path(ret["theta"]).name != "theta_avg150-300.npz"
            or len({ret["theta"], unseen["theta"]["path"], summary["theta"]}) != 1
        ):
            raise ValueError("retention/checkpoint population differs")
        if any(
            unseen["summary"][k] != 100 for k in ("expected_n", "scored_n", "firing_observed_n")
        ):
            raise ValueError("incomplete outside population")
        off, on = [np.asarray(positions[k], np.float64) for k in ("nll_cap_off", "nll_cap_on")]
        if off.shape != (32, 127) or on.shape != off.shape:
            raise ValueError("fixed tail population differs")
        es95, maximum = tail(on - off)
        row = {
            "arm": old["arm"],
            "seed": old["seed"],
            "dataset": old["dataset"],
            "ret_gs": ret["stream_metrics"]["ret_gs_end"],
            "ls_complete_answer": ret["stream_metrics"]["ls_complete_answer_end"],
            "unseen_rate": unseen["summary"]["false_fires"] / 100,
            "es95": es95,
            "maximum": maximum,
        }
        if any(
            not np.isclose(row[k], old[k], rtol=0, atol=1e-12)
            for k in ("ret_gs", "ls_complete_answer", "unseen_rate", "es95", "maximum")
        ):
            raise ValueError("independent pilot reproduction differs")
        rows.append(row)
        populations[old["dataset"]].append(
            {
                "outside": unseen["outside_item_ids"],
                "edits": unseen["edited_item_ids"],
                "off": positions["nll_cap_off"],
                "retention_selection": ret.get("dev_receipt"),
            }
        )
    for values in populations.values():
        if any(v != values[0] for v in values[1:]):
            raise ValueError("paired pilot populations differ")
    stats = {}
    for arm in ARMS:
        stats[arm] = {}
        for metric in ("ret_gs", "es95", "maximum"):
            macros = [
                float(np.mean([r[metric] for r in rows if r["arm"] == arm and r["seed"] == s]))
                for s in range(3)
            ]
            stats[arm][metric] = {"seed_macros": macros, "mean": float(np.mean(macros))}
    ordinary = stats["ordinary"]
    comparisons = {}
    for arm in ARMS[1:]:
        floor = ordinary["ret_gs"]["mean"] - 0.02
        tails = {}
        for metric in ("es95", "maximum"):
            x, y = (
                np.array(stats[arm][metric]["seed_macros"]),
                np.array(ordinary[metric]["seed_macros"]),
            )
            delta, spread = float(x.mean() - y.mean()), float(max(np.ptp(x), np.ptp(y)))
            tails[metric] = {
                "difference": delta,
                "seed_spread": spread,
                "separated": abs(delta) > spread,
            }
            if (
                tails[metric]["separated"]
                != previous["comparisons"][arm]["tails"][metric]["separated"]
            ):
                raise ValueError("tail gate differs")
        unseen = {
            ds: {
                a: float(
                    np.mean(
                        [r["unseen_rate"] for r in rows if r["arm"] == a and r["dataset"] == ds]
                    )
                )
                for a in ("ordinary", arm)
            }
            for ds in DATASETS
        }
        comparisons[arm] = {
            "retention_floor": floor,
            "retention_pass": stats[arm]["ret_gs"]["mean"] >= floor,
            "tails": tails,
            "unseen_by_dataset": unseen,
            "unseen_nonincrease": all(v[arm] <= v["ordinary"] for v in unseen.values()),
            "verdict": "descriptive control"
            if arm == "clip2"
            else (
                "declared secondary condition"
                if stats[arm]["ret_gs"]["mean"] >= floor
                and all(v[arm] <= v["ordinary"] for v in unseen.values())
                and any(t["separated"] for t in tails.values())
                else "null result"
            ),
        }
        if any(
            comparisons[arm][k] != previous["comparisons"][arm][k]
            for k in ("retention_pass", "verdict")
        ):
            raise ValueError("independent pilot verdict differs")
    return {
        "rows": rows,
        "stats": stats,
        "comparisons": comparisons,
        "reproduced_rows": 36,
        "max_absolute_tolerance": 1e-12,
        "framing": previous["framing"],
        "clip_interpretation": manifest["comparator_interpretation"],
        "limitations": [
            "Original measured stream scalars were independently aggregated; no model generations were rerun.",
            "Tail populations have identical ordered cap-off arrays but no historical embedded token-ID receipt.",
            "Three seeds and dependent token positions; finite-sample descriptive gates, not a significance test or power-law claim.",
        ],
    }


def stress_review(reader):
    result = {}
    root = ROOT / "results/R1/stage4_dev_cells/ht_panel"
    for ds in DATASETS:
        schedules = {}
        for schedule in ("shuffled", "clustered"):
            dirs = list(root.glob(f"R1_learned_ff-{ds}-ht-dev-s303-{schedule}-*/attempt-0000"))
            if len(dirs) != 1:
                raise ValueError("unique stress cell required")
            cps = {n: reader.read(dirs[0] / f"checkpoint-{n}.json") for n in CADENCE}
            final = reader.read(dirs[0] / "result.json")
            baseline = {r["key"]: r for r in cps[20]["ht_probes"]["tokens"]}
            points = {}
            for n, cp in cps.items():
                tokens, facts = cp["ht_probes"]["tokens"], cp["ht_probes"]["facts"]
                if len(facts) != 20 or [r["item_id"] for r in facts] != [
                    r["item_id"] for r in cps[20]["ht_probes"]["facts"]
                ]:
                    raise ValueError("stress fixed fact population differs")
                if len(tokens) != len(baseline) or {r["key"] for r in tokens} != set(baseline):
                    raise ValueError("stress fixed positions changed")
                deltas = []
                per_fact = defaultdict(list)
                for r in tokens:
                    before = baseline[r["key"]]
                    if any(
                        r[k] != before[k]
                        for k in (
                            "item_id",
                            "prompt_index",
                            "target_index",
                            "target_token",
                            "original_nll",
                        )
                    ):
                        raise ValueError("stress source identity changed")
                    delta = r["cap_nll"] - before["cap_nll"]
                    deltas.append(delta)
                    per_fact[r["item_id"]].append(delta)
                positive = np.maximum(deltas, 0)
                exact = sum(r["es"] for r in facts)
                points[n] = {
                    "mean_positive": float(np.mean(positive)),
                    "max_positive": float(np.max(positive)),
                    "exact": exact,
                    "within_band": np.mean(positive) <= 0.01 and exact >= 20,
                    "deltas": deltas,
                    "harmed_facts": {
                        iid: {"mean_signed": float(np.mean(v)), "max_positive": max(0, max(v))}
                        for iid, v in per_fact.items()
                        if max(v) > 0
                    },
                }
                if not np.isclose(
                    points[n]["mean_positive"],
                    cp["ht_relative"]["mean_positive_delta_nats"],
                    atol=1e-12,
                    rtol=0,
                ):
                    raise ValueError("stress positive mean differs")
            recovered = recovery_from_bands({n: bool(p["within_band"]) for n, p in points.items()})
            if recovered["right_censored"] != final["ht_recovery"]["right_censored"]:
                raise ValueError("stress recovery classification differs")
            harmful = [n for n in CADENCE if points[n]["max_positive"] > 0]
            schedules[schedule] = {
                "points": points,
                "recovery": recovered,
                "first_detected_harm": min(harmful) if harmful else None,
                "observed_updates_after_first_detection": 100 - min(harmful) if harmful else None,
                "wall_seconds": final["attempt_wall_seconds"],
                "ordered_ids": {n: [r["item_id"] for r in cps[n]["history"]] for n in CADENCE},
            }
        left, right = [schedules[s] for s in ("shuffled", "clustered")]
        errors = {
            n: float(
                np.max(
                    np.abs(np.asarray(left["points"][n]["deltas"]) - right["points"][n]["deltas"])
                )
            )
            for n in CADENCE
        }
        result[ds] = {
            "schedules": schedules,
            "max_token_difference_between_schedules": errors,
            "same_fact_sets_at_each_checkpoint": {
                n: set(left["ordered_ids"][n]) == set(right["ordered_ids"][n]) for n in CADENCE
            },
            "different_treatment_order": left["ordered_ids"][60] != right["ordered_ids"][60],
        }
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--output", type=Path, default=ROOT / "logs/r1_round22/ht3e-independent-review-v2.json"
    )
    args = ap.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "logs"):
        ap.error("repository report required")
    reader = Reader()
    pilot = pilot_review(reader)
    stress = stress_review(reader)
    reader.verify()
    result = {
        "task": "HT-3e",
        "pilot": pilot,
        "stress": stress,
        "gpu_seconds": 0,
        "evidence_bindings": [{"path": p, "sha256": h} for p, h in sorted(reader.bindings.items())]
        + [ref(__file__)],
    }
    # JSON cannot encode numpy booleans; these are measurements, not object blobs.
    result = json.loads(json.dumps(result, default=lambda x: x.item()))
    write_new(args.output, result)
    print(
        json.dumps(
            {
                "reproduced_pilot_rows": 36,
                "stress_datasets": list(stress),
                "bound_sources": len(reader.bindings),
                "gpu_seconds": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
