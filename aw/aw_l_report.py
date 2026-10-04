"""AW-L6: CPU report for upper/all reads × last/all writes, three paired seeds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aw import aw_l_interpretation as interpretation
from aw import reader_results as rr

READ = {"all": [1, 2, 3], "upper": [2, 3]}
WRITE = {"all": [1, 2, 3], "last": [3]}


def factorial(cells):
    """Marginal upper−all read, last−all write, and difference of differences."""
    if set(cells) != {("all", "all"), ("all", "last"), ("upper", "all"), ("upper", "last")}:
        raise ValueError("four distinct factorial coordinates required")
    if any(c["status"] != "complete" for c in cells.values()):
        return None
    a, b, c, d = (
        cells[k] for k in (("all", "all"), ("all", "last"), ("upper", "all"), ("upper", "last"))
    )
    for row in (b, c, d):
        rr.paired(row, a)  # population checks; no outcome-dependent filtering
    for left, right in ((a, b), (c, d)):
        if left["training"]["reader_sha256"] != right["training"]["reader_sha256"]:
            raise ValueError("write arms must share the same trained reader")
    v = [rr.values(x) for x in (a, b, c, d)]
    keys = (*rr.METRICS, *rr.HARM, "fired")
    return {
        k: dict(
            read=((v[2][k] - v[0][k]) + (v[3][k] - v[1][k])) / 2,
            write=((v[1][k] - v[0][k]) + (v[3][k] - v[2][k])) / 2,
            interaction=(v[3][k] - v[2][k]) - (v[1][k] - v[0][k]),
        )
        for k in keys
    }


def build(root, shared, *, positions=245237):
    root, shared, sources = Path(root), Path(shared), {}
    cells, trainings, profiles = [], [], []
    # Discover by recorded coordinates; duplicate completed production candidates are ambiguous.
    candidates = {}
    for path in sorted(root.glob("*/report.json")):
        d = rr.read(path, sources)
        if "dataset" not in d or "read_taps" not in d:
            continue
        if d.get("development"):
            n = d.get("stream", {}).get("items_planned", 10)
            pos = d.get("harm", {}).get("selection", {}).get("positions", 1016)
            profiles.append(
                rr.admitted(path.parent, sources, development=True, checkpoint=n, positions=pos)
            )
            continue
        key = (d["seed"], d["dataset"], tuple(d["read_taps"]), tuple(d["write_sites"]))
        if key in candidates:
            raise ValueError(
                f"ambiguous production cell {key}; supply a root with one declared result per coordinate"
            )
        candidates[key] = path.parent
    for seed in range(3):
        for read in READ:
            trdir = root / f"train-{read}-s{seed}"
            if read == "all" and not trdir.exists():
                trdir = shared / f"train-bp-s{seed}"
            tr = rr.training(trdir, sources)
            if tr["status"] == "complete" and (
                tr["read_taps"] != READ[read]
                or tr["rule"] != "bp"
                or tr["seed"] != seed
                or tr["profile_only"]
            ):
                raise ValueError("unexpected factorial reader")
            trainings.append(
                dict(
                    tr,
                    planned_read=read,
                    planned_seed=seed,
                    reused_from_pc_reader=trdir.parent == shared,
                )
            )
            for write in WRITE:
                for ds in rr.DATASETS:
                    key = seed, ds, tuple(READ[read]), tuple(WRITE[write])
                    path = candidates.get(key, root / f"eval-{read}-{write}-s{seed}-{ds}")
                    reused = False
                    if key not in candidates and read == write == "all" and not path.exists():
                        path = shared / f"eval-bp-s{seed}-{ds}"
                        reused = True
                    row = rr.admitted(path, sources, positions=positions)
                    if row["status"] == "complete" and (
                        row["rule"] != "bp"
                        or (
                            row["seed"],
                            row["dataset"],
                            tuple(row["read_taps"]),
                            tuple(row["write_sites"]),
                        )
                        != key
                    ):
                        row = dict(
                            path=str(path), status="invalid", reason="factorial coordinate mismatch"
                        )
                    if (
                        row["status"] == "complete"
                        and tr["status"] == "complete"
                        and row["training"]["reader_sha256"] != tr["reader_sha256"]
                    ):
                        raise ValueError("evaluation and planned training reader differ")
                    cells.append(
                        dict(
                            row,
                            planned_read=read,
                            planned_write=write,
                            planned_seed=seed,
                            planned_dataset=ds,
                            reused_from_pc_reader=reused,
                        )
                    )
    effects, tolerance = [], []
    for seed in range(3):
        for ds in rr.DATASETS:
            block = {
                (c["planned_read"], c["planned_write"]): c
                for c in cells
                if c["planned_seed"] == seed and c["planned_dataset"] == ds
            }
            effects.append(dict(seed=seed, dataset=ds, effects=factorial(block)))
            base = block["all", "all"]
            for (read, write), c in block.items():
                diff = rr.paired(c, base)
                tolerance.append(
                    dict(
                        seed=seed,
                        dataset=ds,
                        read=read,
                        write=write,
                        ret_es_difference=diff.get("RET-ES") if diff else None,
                        ret_gs_difference=diff.get("RET-GS") if diff else None,
                        within_descriptive_002=(
                            diff["RET-ES"] >= -0.02 - 1e-12 and diff["RET-GS"] >= -0.02 - 1e-12
                        )
                        if diff
                        else None,
                        baseline=read == write == "all",
                    )
                )
    spread = [
        dict(
            dataset=ds,
            effect=e,
            metric=k,
            **rr.spread(
                x["effects"][k][e]
                for x in effects
                if x["dataset"] == ds and x["effects"] is not None
            ),
        )
        for ds in rr.DATASETS
        for e in ("read", "write", "interaction")
        for k in (*rr.METRICS, *rr.HARM, "fired")
    ]
    # One receipt per actually executed process. Shared PC controls are provenance, not a second charge.
    costs = {}
    for x in (*trainings, *cells, *profiles):
        c = x.get("cost", {})
        if c.get("seconds") is not None:
            costs[c["path"]] = c
    for path in root.glob("*/cost.json"):
        c = rr.cost(path.parent, sources)
        if c["seconds"] is not None:
            costs[c["path"]] = c
    sources[str(Path(__file__).resolve())] = rr.sha(Path(__file__))
    sources[str(Path(rr.__file__).resolve())] = rr.sha(Path(rr.__file__))
    sources[str(Path(interpretation.__file__).resolve())] = rr.sha(Path(interpretation.__file__))
    historical_gate = interpretation.cost_gate(rr.ROOT, sources) if root.resolve() == (rr.ROOT / 'results/additional_work/AW-L') else None
    return dict(
        task="AW-L6",
        status="complete" if all(c["status"] == "complete" for c in cells) else "partial",
        planned_trainings=6,
        planned_evaluations=24,
        completed_evaluations=sum(c["status"] == "complete" for c in cells),
        reused_evaluations=sum(
            c["status"] == "complete" and c["reused_from_pc_reader"] for c in cells
        ),
        trainings=trainings,
        cells=cells,
        effects=effects,
        effect_spread=spread,
        write_comparisons=interpretation.comparisons(cells),
        historical_cost_gate=historical_gate,
        tolerance=tolerance,
        development_profiles=profiles,
        cost_inventory=list(costs.values()),
        attributed_process_seconds=sum(c["seconds"] for c in costs.values()),
        incremental_aw_l_process_seconds=sum(
            c["seconds"] for c in costs.values() if Path(c["path"]).is_relative_to(root.resolve())
        ),
        sources_sha256=sources,
        gpu_seconds=0,
        model_calls=0,
    )


def markdown(r, output):
    text = f"""# Upper-layer read/write factorial — {r["status"]} report

Capex · {r["completed_evaluations"]}/24 completed evaluation cells, including {r["reused_evaluations"]} explicitly shared PC-reader BP controls; six planned trained readers.
Numerical source and hashes: `{output}/report.json`.

Read all taps {{1,2,3}} or upper taps {{2,3}}; write all sites {{1,2,3}} or last site {{3}}. Three paired training seeds; each reader serves both write arms with separately acquired fresh memory. All training uses the full-write objective. Same exposed realization 0/order 100 at 300 edits. Lower layers are not assumed to be noise. Training seeds are not subject realizations.

Only complete four-arm seed blocks enter the contrasts below. Full-read/full-write controls are the identical PC-reader BP artifacts; they are reused observations, not additional replication. The three full-read trainings also share the PC-reader controls, as allowed in AW-L5.

{interpretation.narrative(r)}

## Training and reuse

"""
    text += rr.table(
        ["Read", "Seed", "Status", "Shared PC reader", "Parameters", "Process s"],
        [
            [
                t["planned_read"],
                t["planned_seed"],
                t["status"],
                t["reused_from_pc_reader"],
                t.get("parameter_count"),
                t["cost"].get("seconds"),
            ]
            for t in r["trainings"]
        ],
    )
    text += rr.tables(
        r["cells"],
        lambda c: (
            f"s{c['planned_seed']} {c['planned_dataset']} read={c['planned_read']} write={c['planned_write']}"
            + (" [shared]" if c["reused_from_pc_reader"] else "")
        ),
    )
    text += "## Paired read, write and interaction effects\n\nLet A=all/all, B=all/last, C=upper/all and D=upper/last. Read effect=((C−A)+(D−B))/2; write effect=((B−A)+(D−C))/2; interaction=(D−C)−(B−A). Behavior increases favor the first-named upper/last intervention; increases in harm mean worse fidelity. Every term comes from one seed/dataset; unavailable arms withhold that block's effects.\n\n"
    text += rr.table(
        ["Dataset", "Seed", "Complete 2×2 block"],
        [[x["dataset"], x["seed"], x["effects"] is not None] for x in r["effects"]],
    )
    text += rr.table(
        ["Dataset", "Seed", "Metric", "Read effect", "Write effect", "Interaction"],
        [
            [x["dataset"], x["seed"], k, v["read"], v["write"], v["interaction"]]
            for x in r["effects"]
            if x["effects"] is not None
            for k, v in x["effects"].items()
        ],
    )
    text += "The JSON includes effect means, ranges and sample SD across completed paired seeds; no confidence or superiority claim is assigned to a three-seed range.\n\n## Descriptive retention tolerance\n\nThe 0.02 tolerance means neither RET-ES nor RET-GS drops by more than two percentage points versus all-read/all-write in the same seed and dataset. This is a descriptive comparison, **not an inferential noninferiority result or a new classifier**. A baseline row meets its own tolerance by definition and is not evidence for upper layers. Fidelity remains beside efficacy, regardless of this column.\n\n"
    text += rr.table(
        ["Dataset", "Seed", "Read", "Write", "Δ RET-ES", "Δ RET-GS", "Within .02", "Baseline"],
        [
            [
                x[k]
                for k in (
                    "dataset",
                    "seed",
                    "read",
                    "write",
                    "ret_es_difference",
                    "ret_gs_difference",
                    "within_descriptive_002",
                    "baseline",
                )
            ]
            for x in r["tolerance"]
        ],
    )
    text += f"## Cost and development availability\n\nUnique attributed process time: {r['attributed_process_seconds'] / 3600:.4f} hours; new work in the AW-L namespace: {r['incremental_aw_l_process_seconds'] / 3600:.4f} hours. Shared PC-reader cost is not charged a second time across portfolios. All dense allocated delta bytes, including zeroed inactive sites, remain charged. Cost components are subsets of parent receipts.\n\n{len(r['development_profiles'])} AW-L development evaluations are available in this snapshot. The AW-L directory currently has no delivered development outputs if this count is zero; the report does not invent them or substitute profile scores into the 300-edit table. The parser is tested on a synthetic development/production tree; development rows and their different denominators are retained separately in JSON when they arrive.\n\n"
    text += interpretation.cost_note(r)
    text += """Reproduce the saved results (new directory each time):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \\
../venv/bin/python -m aw.aw_l_report --output logs/additional_work/AW-L/report-NEW
```

Scientific design: [AW-L.md](AW-L.md); execution commands: [reader-runners-owner-commands.md](../tasks/reader-runners-owner-commands.md). No GPU or model work is performed by this generator. October 9 at 17:00 EDT remains the experimental cutoff.
"""
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=rr.ROOT / "results/additional_work/AW-L")
    p.add_argument("--shared", type=Path, default=rr.ROOT / "results/additional_work/PC-reader")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--document", type=Path, default=rr.ROOT / "docs/additional_work/AW-L_report.md")
    a = p.parse_args()
    r = build(a.root, a.shared)
    rr.write_outputs(r, markdown(r, a.output), a.output, a.document)
    print(json.dumps({k: r[k] for k in ("status", "completed_evaluations", "reused_evaluations")}))


if __name__ == "__main__":
    main()
