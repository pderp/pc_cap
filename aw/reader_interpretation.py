"""Descriptive paired-seed prose from completed reader results; CPU only."""

from __future__ import annotations

from aw.reader_results import table


def narrative(report):
    cells = {
        (c["rule"], c["seed"], c["dataset"]): c
        for c in report["cells"]
        if c["status"] == "complete"
    }
    seeds = [
        seed
        for seed in range(3)
        if all(
            (rule, seed, dataset) in cells
            for rule in ("bp", "epc")
            for dataset in ("zsre", "counterfact")
        )
    ]
    rows = []
    for seed in seeds:
        for dataset in ("zsre", "counterfact"):
            bp, epc = [cells[rule, seed, dataset] for rule in ("bp", "epc")]
            rows.append(
                [
                    dataset,
                    seed,
                    bp["metrics"]["RET-ES"]["value"],
                    epc["metrics"]["RET-ES"]["value"],
                    100 * (epc["metrics"]["RET-GS"]["value"] - bp["metrics"]["RET-GS"]["value"]),
                    bp["gate"]["selected"],
                    epc["gate"]["selected"],
                ]
            )
    positions = sorted({c["gate"]["logical_positions"] for c in cells.values()})
    text = (
        f"Fully paired training seeds: {', '.join(map(str, seeds)) or 'none'} "
        f"({len(seeds)}/3 planned). The table uses **ePC minus BP** in percentage points "
        f"for paraphrase retention; ordinary-text positions per available cell: {positions}. "
        "Own-prompt retention is shown for each arm, not assumed identical.\n\n"
    )
    text += table(
        [
            "Dataset",
            "Seed",
            "BP RET-ES",
            "ePC RET-ES",
            "RET-GS difference (percentage points)",
            "BP fired",
            "ePC fired",
        ],
        rows,
    )
    if rows and all(row[4] < 0 for row in rows):
        text += (
            "ePC paraphrase retention is lower in every fully paired row available here. "
            f"The deficits range from {min(-row[4] for row in rows):.2f} to "
            f"{max(-row[4] for row in rows):.2f} percentage points; the magnitude matters. "
        )
    for dataset in ("zsre", "counterfact"):
        retention = [row[4] for row in rows if row[0] == dataset]
        if retention:
            text += (
                f"On {dataset}, ePC paraphrase retention is lower in "
                f"{sum(x < 0 for x in retention)}/{len(retention)} paired seeds; "
                f"ePC−BP differences range from {min(retention):+.2f} to "
                f"{max(retention):+.2f} percentage points. "
            )
        differences = [row[6] - row[5] for row in rows if row[0] == dataset]
        if differences and min(differences) < 0 < max(differences):
            text += f"On {dataset}, the ePC-minus-BP firing direction reverses across seeds. "
        for metric in ("mean_delta_nll", "es99_positive"):
            differences = [
                cells["epc", seed, dataset]["harm"]["capoff"][metric]
                - cells["bp", seed, dataset]["harm"]["capoff"][metric]
                for seed in seeds
            ]
            if differences:
                text += (
                    f"{dataset} {metric}, ePC−BP by seed ({', '.join(map(str, seeds))}): "
                    + ", ".join(f"{x:+.7g}" for x in differences) + " nats. "
                )
    if len(seeds) < 3:
        text += "The three-seed comparison remains partial. "
    text += (
        "Read seed-specific magnitudes and directions together: a quieter reader is not "
        "itself improved editing. Descriptive spreads are not confidence intervals. "
        "Comparisons intersect seed identities, never a mean of three BP seeds minus "
        "fewer ePC seeds. Training seeds reuse one subject realization. No training losses "
        "are compared as though settled ePC CE and feedforward BP CE were the same objective.\n\n"
    )
    return text
