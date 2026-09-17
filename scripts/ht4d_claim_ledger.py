"""New v4 talk ledger bound to the completed Round22 CPU counter-review."""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

from scripts.r1_d9_receipts import ref, sha
from scripts.r1_d10a_review import ROOT, write_new


def profile_inventory():
    recipes = {
        "I": sorted((ROOT / "docs/tasks").glob("R1-64c-*.recipe.json")),
        "K": sorted((ROOT / "docs/tasks/R1-64d").glob("*.recipe.json")),
    }
    expected = {}
    for chain, paths in recipes.items():
        for p in paths:
            doc = json.loads(p.read_text())
            if chain == "K" and doc["cell"]["condition"] in ("R1_nonlearned", "R1_learned_ff_v2"):
                continue
            expected[sha(p)] = {
                "chain": chain,
                "condition": doc["cell"]["condition"],
                "dataset": doc["cell"]["dataset"],
                "recipe": ref(p),
                "status": "not_filed",
            }
    for p in sorted(
        (ROOT / "results/R1/stage4_dev_cells").glob("*development-source*/attempt-*/result.json")
    ):
        doc = json.loads(p.read_text())
        h = doc.get("manifest_sha256")
        if (
            h not in expected
            or doc.get("status") != "complete"
            or doc.get("completed_checkpoint") != 300
        ):
            continue
        if expected[h]["status"] == "complete":
            raise ValueError(
                "multiple completed attempts for a profile; review selection explicitly"
            )
        drift = doc["phase_timer_summary"]["drift"]
        if drift["count"] != 1:
            raise ValueError("profile drift cadence differs from once-per-cell expectation")
        expected[h].update(
            status="complete",
            result=ref(p),
            attempt_wall_seconds=doc["attempt_wall_seconds"],
            drift_operation_seconds=drift["operation_seconds"],
            drift_calls=drift["count"],
        )
    return list(expected.values())


def build():
    old = json.loads((ROOT / "logs/r1_round18/talk_evidence_v3.json").read_text())
    review_path = ROOT / "logs/r1_round22/ht3e-independent-review-v2.json"
    review = json.loads(review_path.read_text())
    pilot, stress = review["pilot"], review["stress"]
    profiles = profile_inventory()
    profile_ref = write_new(
        ROOT / "logs/r1_round22/ht4d-profile-inventory.json", {"profiles": profiles}
    )
    rows = []
    stable = {"A1", "A2", "A3", "O2", "TAIL-zsre", "TAIL-counterfact", "LS-DEC053", "A4", "N1"}
    for row in old["rows"]:
        if row["id"] not in stable:
            continue
        for binding in row["evidence"]:
            if sha(ROOT / binding["path"]) != binding["sha256"]:
                raise ValueError("historical claim needs fresh review: " + row["id"])
        rows.append(copy.deepcopy(row))

    def claim(identity, label, statement, limits, paths):
        evidence = []
        for p in paths:
            b = ref(ROOT / p if not Path(p).is_absolute() else p)
            b["path"] = str(Path(b["path"]).relative_to(ROOT))
            evidence.append(b)
        rows.append(
            {
                "id": identity,
                "label": label,
                "statement": statement,
                "limits": limits,
                "evidence": evidence,
            }
        )

    for arm, label in (("kappa02", "κ=.2"), ("kappa05", "κ=.5"), ("clip2", "clipped surprisal 2")):
        stats, comp = pilot["stats"][arm], pilot["comparisons"][arm]
        claim(
            "K-" + arm,
            "null" if arm != "clip2" else "implemented",
            f"{label}: three-seed/dataset macro RET-GS {stats['ret_gs']['mean']:.6f}; ordinary {pilot['stats']['ordinary']['ret_gs']['mean']:.6f}; declared floor {comp['retention_floor']:.6f}, pass={comp['retention_pass']}. Mean ES95 positive harm {stats['es95']['mean']:.9f} nats; tail separation=False; unseen nonincrease={comp['unseen_nonincrease']}.",
            "All 36 raw-file rows independently reproduced. Coupled arms fail the retention floor and seed-spread tail gate. Clip2 meets the floor but has one CounterFact false fire versus ordinary zero; descriptive control, not robust superiority. Clip2 ceiling-matches κ=.5 only. Developmental, not confirmatory; no tail-selected checkpoint.",
            [
                review_path,
                "manifests/revision_v1/kappa_pilot_v3.json",
                "docs/heavy_tail_counter_review.md",
            ],
        )
    for ds in ("zsre", "counterfact", "mquake"):
        data = stress[ds]
        last = data["schedules"]["shuffled"]["points"]["100"]
        first = data["schedules"]["shuffled"]["first_detected_harm"]
        claim(
            "STRESS-" + ds,
            "implemented",
            f"{ds}: the two tested schedules have identical token deltas at all five checkpoints (max difference 0); 20/20 old primary exact answers remain. Edit100 mean positive target-token ΔNLL {last['mean_positive']:.9f}, max {last['max_positive']:.9f}; first detected harm {first}; harmed facts {json.dumps(last['harmed_facts'], sort_keys=True)}.",
            "One seed and two schedules per dataset. Empirical equality is not a universal order-invariance theorem. Harm persisted through edit100; no claim of permanent harm. CounterFact was unharmed at60/70 and first harmed at80, leaving20 observed later updates; the registered40-update censor starts at treatment end60.",
            [
                review_path,
                "manifests/revision_v1/ht_development_panel_v1.json",
                "scripts/ht5_probe_assays.py",
            ],
        )
    for chain in ("I", "K"):
        for ds in ("zsre", "counterfact"):
            group = [p for p in profiles if p["chain"] == chain and p["dataset"] == ds]
            done = [p for p in group if p["status"] == "complete"]
            values = [p["attempt_wall_seconds"] for p in done]
            description = (
                f"attempt times {min(values):.3f}–{max(values):.3f} s"
                if values
                else "no completed measurement"
            )
            claim(
                f"COST-{chain}-{ds}",
                "implemented" if done else "proposed",
                f"Chain {chain}, {ds}: {len(done)}/{len(group)} expected profiles filed; 300 edits, {description}. Every filed result records exactly one drift assay per cell.",
                "Attempt wall time excludes process/model initialization. I includes reader and v0/S1 profiles; K inventories the six v0/S1 re-profiles only. Bind exact recipes/results when comparing speeds. Missing profiles are unavailable, not zero-cost; these are not1000-edit timings or whole-matrix admission.",
                [
                    profile_ref["path"],
                    *[p["result"]["path"] for p in done],
                    *[p["recipe"]["path"] for p in group],
                ],
            )
    matrix_path = ROOT / "manifests/revision_v1/run_matrix_v5_1.json"
    matrix = json.loads(matrix_path.read_text())
    counts = Counter(c["condition"] for c in matrix["cells"])
    readers = sum(n for c, n in counts.items() if c in ("R1_learned_ff", "R1_nonlearned"))
    nonreaders = len(matrix["cells"]) - readers
    claim(
        "COST-matrix",
        "proposed",
        f"Matrix v5.1: {len(matrix['cells'])} core cells = {nonreaders} v0/S1-style + {readers} reader-based; optional historical-v2 extension adds45 reader cells. Each condition contributes45 core cells.",
        "Earlier notes'225/135 split does not match this core matrix. Also do not multiply the once-per-cell drift assay by three checkpoints. Reprice from measured components, reserve failures and preparation, and obtain explicit cost admission; no whole-matrix completion guarantee. October9 experiment stop, October10–14 analysis/slides/rehearsal, October15 presentation.",
        [matrix_path, profile_ref["path"], "docs/tasks/R1-72-decision-addendum.md"],
    )
    calibration_path = ROOT / "manifests/revision_v1/calibration_v3.json"
    claim(
        "MQ-calibration",
        "implemented",
        "Calibration v3 preserves historical zsRE/CounterFact entries and records MQuAKE radius0 on all three banks, the declared exact-key fallback.",
        "Development calibration, not confirmation admission. No positive-radius setting met the declared coverage/preservation requirement; source geometry and exact-key firing must accompany the MQuAKE comparator results. Continued-base transfer qualifications remain.",
        [calibration_path, "results/R1/calibration_mquake_v3/calibration_candidate.json"],
    )
    claim(
        "MQ-capacity",
        "proposed",
        "D10a's conservative preteacher review leaves2129 MQuAKE subjects versus4050 demand. Ignoring all near-miss reservations as a diagnostic leaves3450; neither is final clearance.",
        "Resolve verified-near-miss policy wording and review incidental/homonym context matches. Do not silently waive context exclusions or sample to fill capacity. Final-base teacher/role review and a draw-time exposure supplement remain. Name-based global IDs are operational equivalence, not external entity-linking certification.",
        [
            "logs/r1_round22/r1-d10a-review-v4.json",
            "logs/r1_round22/r1-d10a-capacity-diagnostics-v2.json",
            "manifests/revision_v1/exclusions_frozen_v6.json",
        ],
    )
    claim(
        "O7",
        "proposed",
        "D9 receipt producers, exhaustive partial evidence, resumable teacher script, endpoint constructor/catalog and unsigned operator inputs exist; current dry runs refuse admission.",
        "No real draw, seal, freeze or confirmatory result was produced here. MQuAKE capacity and semantic review remain open; synthetic/development constructor checks do not establish endpoint coverage or model efficacy.",
        [
            "docs/tasks/R1-D9-inputs-v2.json",
            "logs/r1_round22/r1-d9-clearance-dry.json",
            "logs/r1_round22/r1-d10c-development-rehearsal.json",
        ],
    )
    decisions = "manifests/revision_v1/decisions_snapshot_v6.md"
    claim(
        "U12-14",
        "proposed",
        "DEC-057:63 nominal simultaneous metric intervals, three realization clusters, five paired orders each. DEC-058 preserves the four-way classifier and margins. DEC-059 keeps secondary benchmarks separate from primary inference.",
        "Three clusters make coverage nominal; complete paired populations required, no imputation. Bounded equality under DEC-053 is primary for locality/near-miss, with termination/truncation alongside. Fixed outside populations and actual occupancy are necessary for occupancy claims; earlier10/12/9% used different populations.",
        [
            decisions,
            "docs/R1_stage4_protocol_draft_v5_1.md",
            "scripts/r1_49g_analyze.py",
            "docs/tasks/R1-76b-mquake-historical-v3.population.spec.json",
        ],
    )
    # Every row points to immutable source hashes; metadata/claims carry the full framing.
    framing = pilot["framing"]
    current = (
        (ROOT / "docs/heavy_tail_counter_review.md")
        .read_text()
        .split("**What it is not.**", 1)[1]
        .split("\n\n", 1)[0]
    )
    if framing != "**What it is not.**" + current:
        raise ValueError("required framing differs")
    for row in rows:
        for b in row["evidence"]:
            if sha(ROOT / b["path"]) != b["sha256"]:
                raise ValueError("claim source changed during ledger build")
    report = {
        "task": "HT-4d",
        "rows": rows,
        "framing": framing,
        "profiles": profile_ref,
        "matrix_condition_counts": dict(counts),
        "gpu_seconds": 0,
        "producer": ref(__file__),
        "snapshot_policy": "Completed, exact-hash profiles only; later owner results require a new snapshot.",
    }
    write_new(ROOT / "logs/r1_round22/talk_evidence_v4.json", report)
    lines = [
        "# Talk claim–evidence ledger v4 — Round22",
        "",
        "Charlie Derr, Binghamton, October15. Experiments stop October9; October10–14 is for analysis, slides and rehearsal.",
        "",
        "Revision-v1 measurements remain developmental. Missing work is proposed/unavailable; measured failed pilot gates are labelled null. Every statement below is bound to source files.",
        "",
        framing,
        "",
        "| ID | Status | Statement | Limits | Evidence (SHA-256) |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        refs = "; ".join(f"[{b['path']}](../{b['path']}) `{b['sha256']}`" for b in row["evidence"])
        fields = [row["id"], row["label"], row["statement"], row["limits"], refs]
        lines.append(
            "| " + " | ".join(f.replace("|", "\\|").replace("\n", " ") for f in fields) + " |"
        )
    with (ROOT / "docs/talk_claim_ledger_v4.md").open("x") as handle:
        handle.write("\n".join(lines) + "\n")
    print(
        json.dumps(
            {
                "claims": len(rows),
                "profile_status": dict(Counter(p["chain"] + ":" + p["status"] for p in profiles)),
                "core_reader_cells": readers,
                "core_v0_s1_cells": nonreaders,
            }
        )
    )


if __name__ == "__main__":
    build()
