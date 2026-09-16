"""R1-X12: independently audit saved selection evidence; no model execution."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/r1_round16"
SOURCES = {
    "zsre": "zsre_dev.json",
    "counterfact": "counterfact_dev.json",
    "mquake": "mquake_dev_v3b.json",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def interval(k, n):
    p, z = k / n, 1.959963984540054
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {
        "k": k,
        "n": n,
        "rate": p,
        "wilson95": [center - half, center + half],
        "clopper_pearson95": [
            float(beta.ppf(0.025, k, n - k + 1)) if k else 0.0,
            float(beta.ppf(0.975, k + 1, n - k)) if k < n else 1.0,
        ],
        "scope": "descriptive fixed-candidate binomial reference; not post-selection adjusted or a population guarantee",
    }


def audit():
    bindings = {}

    def read(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        if "confirm" in path.parts:
            raise PermissionError("sealed input refused")
        observed = sha(path)
        if expected is not None and observed != expected:
            raise ValueError(f"source hash mismatch: {path}")
        bindings[str(path)] = observed
        return json.loads(path.read_text())

    selection = read("manifests/revision_v1/primary_selection_v2.json")
    primary = read("manifests/revision_v1/primary_condition_v5.json")
    assert sha(ROOT / primary["selection"]["manifest"]) == primary["selection"]["sha256"]
    manifests = {ds: read(ROOT / "manifests/dev" / name) for ds, name in SOURCES.items()}
    s0 = {r["item_id"] for r in read("manifests/dev/s0_sample.json")["items"]}
    expected_ids = {}
    for ds, doc in manifests.items():
        pool = (
            doc["items"] if ds == "mquake" else [r for r in doc["items"] if r["item_id"] not in s0]
        )
        indices = sorted(np.random.default_rng(21).permutation(len(pool))[:100])
        expected_ids[ds] = [pool[i]["item_id"] for i in indices]
    signatures, all_rows, reference_unseen = {}, [], None
    for row in selection["candidates"]:
        observed_metrics = {}
        weight_identities = []
        for ds in SOURCES:
            suffix = "" if ds == "zsre" else "@" + ds
            summary_path = ROOT / "results/R1" / f"stream_eval_{row['tag']}{suffix}.json"
            ev = read(summary_path, row["sources"][ds])
            run = ROOT / "results/R1/streams_revision" / (row["tag"] + suffix)
            item_path = run / "items.jsonl"
            bindings[str(item_path)] = sha(item_path)
            items = [json.loads(line) for line in item_path.read_text().splitlines()]
            ids = [r["item_id"] for r in items]
            assert ids == expected_ids[ds], (row["tag"], ds, "population mismatch")
            weight_identities.append((ev["theta"], ev["theta_hash"]))
            assert ev["args"]["n"] == 100 and ev["args"]["stream_seed"] == 21
            assert ev["args"]["rare_overlap"] == 1 and ev["args"]["null_threshold"] == 0.5
            assert ev["args"]["delta_steps"] == 5 and ev["args"]["fast_steps"] == 0
            if ds == "mquake":
                assert ev["dev_receipt"]["manifest_sha256"] == sha(
                    ROOT / "manifests/dev" / SOURCES[ds]
                )
                assert ev["dev_receipt"]["selected_item_ids"] == ids
            checkpoints = read(run / "checkpoints.json")
            cp = checkpoints[-1]
            assert [r["item_id"] for r in cp["rows"]] == ids
            ret = sum(r["ret_gs"] for r in cp["rows"]) / 100
            metrics = read(run / "metrics.json")
            assert metrics["base_hash_before"] == metrics["base_hash_after"]
            assert metrics["status"] == "complete" and metrics["items_completed"] == 100
            assert math.isclose(ret, row["metrics"][ds]["ret_gs_end"], abs_tol=1e-12)
            for key, value in row["metrics"][ds].items():
                assert value == ev["stream_metrics"][key] == metrics["metrics"][key]["value"]
            assert cp["locality"]["n"] == 50
            assert (
                cp["locality"]["ls_complete_answer"] == row["metrics"][ds]["ls_complete_answer_end"]
            )
            observed_metrics[ds] = row["metrics"][ds]
            signatures[ds] = {
                "n": len(ids),
                "ordered_ids_sha256": digest(ids),
                "source": str(ROOT / "manifests/dev" / SOURCES[ds]),
                "source_sha256": sha(ROOT / "manifests/dev" / SOURCES[ds]),
                "locality_prompt_count": 50,
                "locality_prompts_sha256": digest(manifests[ds]["unrelated_prompts"][:50]),
                "locality_proof": "same loader/config and current bound source; raw locality identities not saved in these legacy stream reports",
            }
        unseen_root = (
            ROOT / "results/R1/endpoints" / f"{row['run']}_step{row['step']}_rare1_n100_unseen_zsre"
        )
        u = read(unseen_root / "summary.json", row["sources"]["unseen"])
        report = read(unseen_root / "report.json")
        assert len(set(weight_identities)) == 1
        assert weight_identities[0] == (u["theta"]["path"], u["theta"]["params_hash"])
        pop = {
            "edited": u["edited_item_ids"],
            "outside": u["outside_item_ids"],
            "pool": u["pool"],
            "queries": [
                [r["item_id"], r["source_row_sha256"], r["reference"]["prompt_sha256"]]
                for r in report["rows"]
            ],
        }
        if reference_unseen is None:
            reference_unseen = pop
        assert pop == reference_unseen
        assert u["edited_item_ids"] == expected_ids["zsre"]
        assert len(report["rows"]) == 100 and all(r["status"] == "ok" for r in report["rows"])
        k = sum(r["false_fire"] for r in report["rows"])
        assert (
            k / 100
            == u["summary"]["false_fire_rate_full_inventory"]
            == row["metrics"]["unseen_zsre_100"]
        )
        assert u["summary"]["scored_n"] == 100 and u["summary"]["source_shortfall"] == 0
        mean = sum(observed_metrics[ds]["ret_gs_end"] for ds in SOURCES) / 3
        admissible = (
            k <= 10
            and min(observed_metrics[ds]["ls_complete_answer_end"] for ds in SOURCES) >= 0.98
        )
        assert row["complete"] and math.isclose(mean, row["mean_ret_gs"], abs_tol=1e-12)
        assert admissible == row["admissible"]
        all_rows.append(
            {
                "run": row["run"],
                "step": row["step"],
                "tag": row["tag"],
                "mean_ret_gs": mean,
                "unseen_k": k,
                "unseen_n": 100,
                "unseen_rate": k / 100,
                "admissible": admissible,
                "min_ls": min(observed_metrics[ds]["ls_complete_answer_end"] for ds in SOURCES),
                "family": "question-null" if "_sel6_" in row["run"] else "ordinary-null",
            }
        )
    assert len(all_rows) == selection["n_complete"] == 42
    assert sum(r["admissible"] for r in all_rows) == selection["n_admissible"] == 15
    winner = max(
        (r for r in all_rows if r["admissible"]),
        key=lambda r: (r["mean_ret_gs"], -r["unseen_rate"]),
    )
    assert winner["tag"] == selection["winner"]["tag"]
    weights = primary["weights"]
    assert sha(weights["path"]) == weights["sha256"]
    bindings[weights["path"]] = sha(weights["path"])
    source_arrays = []
    for path in weights["sources"]:
        bindings[path] = sha(path)
        with np.load(path, allow_pickle=False) as z:
            source_arrays.append({k: np.asarray(z[k]) for k in z.files})
    assert [Path(p).name for p in weights["sources"]] == [
        f"theta_step{s}.npz" for s in (150, 200, 250, 300)
    ]
    with np.load(weights["path"], allow_pickle=False) as z:
        assert all(set(a) == set(z.files) for a in source_arrays)
        counts = {"reader": 0, "controller": 0}
        for key in z.files:
            average = np.mean(
                np.stack([np.asarray(a[key], np.float64) for a in source_arrays]), axis=0
            ).astype(source_arrays[0][key].dtype)
            np.testing.assert_array_equal(average, z[key])
            counts["reader" if "reader" in key else "controller"] += int(z[key].size)
    occupancy = []
    for n in (100, 300, 1000):
        u = read(ROOT / f"results/R1/endpoints/v5_rare1_n{n}_unseen_zsre/summary.json")
        r = read(ROOT / f"results/R1/endpoints/v5_rare1_n{n}_unseen_zsre/report.json")
        outside = u["outside_item_ids"]
        assert len(outside) == 100 and len(u["edited_item_ids"]) == n
        dev_ids = {i["item_id"] for i in manifests["zsre"]["items"]}
        actual_dev = sum(i in dev_ids for i in u["edited_item_ids"])
        occupancy.append(
            {
                "records": n,
                **interval(u["summary"]["false_fires"], 100),
                "outside_source": u["outside_source"],
                "outside_ids_sha256": digest(outside),
                "outside_ids": outside,
                "actual_dev_items": actual_dev,
                "actual_pool_fillers": n - actual_dev,
                "reported_memory_content": u["memory_content"],
                "state_identity": r["rows"][0]["state_before"],
            }
        )
    overlaps = []
    for i, a in enumerate(occupancy):
        for b in occupancy[i + 1 :]:
            overlaps.append(
                {
                    "records": [a["records"], b["records"]],
                    "shared_probe_ids": len(set(a["outside_ids"]) & set(b["outside_ids"])),
                }
            )
    for r in occupancy:
        r.pop("outside_ids")
    return {
        "task": "R1-X12",
        "status": "saved selection rule reproduced; qualifications and provenance repairs required before freeze",
        "manifest_name": selection["name"],
        "n_candidates": 42,
        "n_admissible": 15,
        "winner": winner,
        "candidates": all_rows,
        "populations": signatures,
        "unseen_common_population": {
            "edited_sha256": digest(reference_unseen["edited"]),
            "outside_sha256": digest(reference_unseen["outside"]),
            "full_query_signature_sha256": digest(reference_unseen["queries"]),
            "n": 100,
        },
        "winner_interval": interval(10, 100),
        "occupancy": occupancy,
        "occupancy_probe_overlaps": overlaps,
        "weight_average": {
            "verified_bitwise": True,
            "uniform_weights": [0.25] * 4,
            "steps": [150, 200, 250, 300],
            "parameter_counts": counts,
            "weights": weights,
        },
        "bindings_sha256": bindings,
        "gpu_seconds": 0,
        "model_executions": 0,
    }


def figure(report):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5.6), layout="constrained")
    colors = {"ordinary-null": "#4379b5", "question-null": "#d0802f"}
    for family, color in colors.items():
        for averaged in (False, True):
            rows = [
                r
                for r in report["candidates"]
                if r["family"] == family and (r["step"] == "avg") == averaged
            ]
            ax.scatter(
                [100 * r["unseen_rate"] for r in rows],
                [r["mean_ret_gs"] for r in rows],
                marker="D" if averaged else "o",
                s=65 if averaged else 35,
                c=color,
                alpha=0.85,
                label=f"{family}: " + ("average 150–300" if averaged else "single checkpoint"),
            )
    w = report["winner"]
    ax.scatter(
        [100 * w["unseen_rate"]],
        [w["mean_ret_gs"]],
        marker="*",
        s=250,
        c="#202020",
        label="selected v5",
        zorder=5,
    )
    ax.axvline(10, color="#666666", ls="--", lw=1)
    ax.annotate(
        "v5: 0.803 retention, 10/100 fires",
        (10, w["mean_ret_gs"]),
        xytext=(18, 0.70),
        arrowprops={"arrowstyle": "->", "color": "#444444"},
        fontsize=9,
    )
    ax.set(
        xlabel="Unseen zsRE prompts accepted by the gate (%)",
        ylabel="Mean RET-GS across three datasets",
        title="Development retention–rejection trade-off: 42 candidates",
        xlim=(-2, 62),
        ylim=(0.40, 0.91),
    )
    ax.text(
        0.02,
        0.02,
        "Same 100 edited facts per dataset and 100 unseen zsRE prompts.\nLS ≥ 0.98 also required; these points are not independent replications.",
        transform=ax.transAxes,
        fontsize=8,
    )
    ax.legend(loc="lower right", fontsize=8)
    for suffix in ("pdf", "svg", "png"):
        path = OUT / f"selection_retention_rejection.{suffix}"
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    report = audit()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "selection_audit.json"
    with path.open("x") as f:
        json.dump(report, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    figure(report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "n_candidates",
                    "n_admissible",
                    "winner",
                    "winner_interval",
                    "occupancy_probe_overlaps",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
