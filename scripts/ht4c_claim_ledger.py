"""Build the round18 talk claim ledger from immutable measured evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import ht3d_pilot_aggregate as ht
from scripts.r1_63d_freeze_candidate import PROFILE
from scripts.r1_74_rescore import rescore

ROOT = ht.ROOT
TAIL = "logs/heavy_tail/audit-v5-round16-supplement/audit.json"
CF = "results/R1/stage4_dev_cells/R1_learned_ff-counterfact-development-source-bc285b69b70dff8514a4/attempt-0000/checkpoint-300.json"


def assemble(pilot_path):
    bindings = {}

    def bind(path):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(ROOT)
        name = str(path)
        if "confirm" in path.parts:
            raise PermissionError("no sealed inputs")
        h = ht.sha(ROOT / path)
        if name in bindings and bindings[name] != h:
            raise ValueError("changed evidence")
        bindings[name] = h
        return name

    def read(path):
        name = bind(path)
        return json.loads((ROOT / name).read_text())

    pilot = read(pilot_path)
    primary = read("manifests/revision_v1/primary_condition_v5.json")
    selection = read("logs/r1_round16/selection_audit.json")
    tail = read(TAIL)
    cf = rescore(read(CF))
    profile = read(PROFILE)
    freeze = read("manifests/revision_v1/freeze_candidate_v5.json")
    inventory = read("logs/r1_round18/r1-77-final-draft-inventory.json")
    rows = []

    def claim(identity, label, statement, limits, *sources):
        rows.append(
            dict(
                id=identity,
                label=label,
                statement=statement,
                limits=limits,
                evidence=[
                    {
                        "path": bind(p),
                        "sha256": bindings[
                            str(Path(p).relative_to(ROOT) if Path(p).is_absolute() else Path(p))
                        ],
                    }
                    for p in sources
                ],
            )
        )

    claim(
        "A1",
        "implemented",
        "Frozen GPT-2 prior plus 3,348,228 adaptive reader/controller parameters (1,640,964 + 1,707,264), about 2.7% of the stated 124M base.",
        "Per-record state is additional. Current results are a controlled GPT-2-scale JAX/BP-base study, not evidence of frontier-scale or FabricPC transfer.",
        "logs/r1_round16/selection_audit.json",
        "src/pccap/revision_v1/learner.py",
    )
    claim(
        "A2",
        "implemented",
        "Per-answer-position residual writes optimize supplied support targets; null selection and the memory-rare overlap gate control intervention.",
        "Acceptance, nonzero writes and answer changes are different events. No global optimum, autonomous audit planner or calibrated precision interpretation is established.",
        "src/pccap/revision_v1/adapt.py",
        "src/pccap/revision_v1/reader.py",
    )
    claim(
        "A3",
        "proposed",
        "Query/rejection and observation/write interfaces motivate the abstract's two-blanket interpretation.",
        "No conditional-independence factorization, blanket theorem, one-kappa equivalence or geometric-invariant theorem has been proved.",
        "docs/heavy_tail_counter_review.md",
        "src/pccap/revision_v1/memory.py",
    )
    claim(
        "O2",
        "implemented",
        f"{selection['n_candidates']} development candidates, {selection['n_admissible']} admissible; selected v5 seed2 average has RET-GS macro {selection['winner']['mean_ret_gs']:.6f} (zsRE .98 / CounterFact .82 / MQuAKE .61), ES 1, minimum LS .98.",
        "Selection followed DEC-050 point estimates. Its unseen 10/100 is on the boundary; Wilson95% 5.52–17.44% is descriptive, not selection-adjusted certification. This selected-seed score differs from the ordinary three-seed pilot mean.",
        "logs/r1_round16/selection_audit.json",
        "manifests/revision_v1/primary_condition_v5.json",
    )
    claim(
        "A9",
        "hypothesis",
        "Historical zsRE unseen rates of 10/12/9% at 100/300/1000 records do not establish occupancy flatness.",
        "Outside-ID populations have zero pairwise overlap. R1-76 prepares one fixed outside100 population across one stream; its owner experiment remains outstanding.",
        "logs/r1_round16/selection_audit.json",
        "docs/tasks/R1-76.md",
    )
    for ds, identifier in (("zsre", "d22ce680"), ("counterfact", "bc285b69")):
        s = next(
            s
            for s in tail["series"]
            if identifier in s["source"]
            and s["source"].endswith("checkpoint-300.json")
            and s["metric"] == "preservation_nll_minus_original"
        )
        if ht.sha(ROOT / s["source"]) != s["source_sha256"]:
            raise ValueError("tail audit source changed")
        stat = s["statistics"]
        claim(
            "TAIL-" + ds,
            "implemented",
            f"{ds}: 128 windows × 127 = {stat['n']} scored positions; signed mean {stat['mean_signed']:+.9f} nats, ES95 positive harm {stat['ES95_positive']:.9f}, maximum {stat['maximum_positive']:.6f}; {stat['exceedances_nats']['0.1']['count']} positions > .1 nat; worst 1% contains {100 * stat['worst_1pct_share_positive']:.4f}% of positive harm.",
            "Rare concentrated harm is observed. No power-law fit, heavy-tail exponent, iid-position inference or universal preservation claim. The pilot's 32-window population is a different assay.",
            TAIL,
            s["source"],
            "logs/heavy_tail/audit-v5-round16-supplement/mean_vs_tail_v5.pdf",
        )
    ls = cf["locality"]["summary"]
    nm = cf["endpoints"]["near_miss"]["summary"]
    claim(
        "LS-DEC053",
        "implemented",
        f"CounterFact locality: {ls['preserved_n']}/{ls['expected_n']} bounded-equal and {ls['preserved_terminated_n']}/{ls['expected_n']} terminated-and-equal; near miss: {nm['preserved_n']}/{nm['expected_n']} bounded-equal and {nm['preserved_terminated_n']}/{nm['expected_n']} terminated-and-equal. Equal truncated pairs explain the 13 and 37 additional preserved cases.",
        "DEC-053 makes bounded decoded-text equality primary; termination and per-side truncation remain reported. This is rescoring the same saved generations. A truncated unchanged reference is not automatically cap-induced damage.",
        CF,
        "src/pccap/revision_v1/stage4_assays.py",
        "docs/tasks/R1-74-R1-75-approved-landing.md",
    )
    ordinary = pilot["arms"]["ordinary"]
    for arm in ("kappa02", "kappa05"):
        s = pilot["arms"][arm]
        c = pilot["comparisons"][arm]
        delta = s["ret_gs"]["mean"] - ordinary["ret_gs"]["mean"]
        tails = c["tails"]
        claim(
            "K-" + arm,
            "null"
            if c["verdict"] == "null result"
            else ("implemented" if c["verdict"] == "declared secondary condition" else "proposed"),
            f"{arm}: registered decision = {c['verdict']}; RET-GS {s['ret_gs']['mean']:.6f} versus ordinary {ordinary['ret_gs']['mean']:.6f} (difference {delta:+.6f}, floor {c['retention_floor']:.6f}). ES95 difference {tails['es95']['signed_difference']:+.6f} versus spread {tails['es95']['seed_spread_threshold']:.6f}; maximum difference {tails['maximum']['signed_difference']:+.6f} versus spread {tails['maximum']['seed_spread_threshold']:.6f}.",
            "These are all three seeds × three datasets for this coupled arm versus ordinary, using the predeclared average150–300. Retention fails the .02 tolerance and neither tail difference exceeds the seed spread. Preliminary developmental hints; no confirmatory significance or causal coupled-free-energy conclusion.",
            pilot_path,
            "manifests/revision_v1/kappa_pilot_v3.json",
            "docs/heavy_tail_counter_review.md",
        )
    claim(
        "K-unseen",
        "implemented",
        "Three-seed mean unseen false fires at 100 edits: ordinary zsRE 11.6667%, kappa .2 5%, kappa .5 4%; all three arms 0% on CounterFact and MQuAKE.",
        "This endpoint improves descriptively while the retention gate fails. It is not a claim of overall robust superiority or occupancy flatness. Ordinary seed2 CF/MQ files use verified historical v5 names.",
        pilot_path,
        "docs/tasks/HT-3d-ordinary-seed2-unseen-aliases.json",
    )
    claim(
        "K-clip",
        "proposed" if pilot["arms"]["clip2"]["ret_gs"]["mean"] is None else "implemented",
        f"Clipped-control comparison remains separately labeled: pilot snapshot has {pilot['complete_rows']}/36 complete arm/seed/dataset rows; clip2 comparison = {pilot['comparisons']['clip2']['verdict']}.",
        "Clip2 ceiling-matches kappa .5 only, not kappa .2. Finish all three control seeds and rerun the immutable report before comparing objectives. Never select a checkpoint on the observed tail outcome.",
        pilot_path,
        "manifests/revision_v1/kappa_pilot_v3.json",
    )
    claim(
        "A4",
        "implemented",
        "The answer loss is bounded for positive kappa; the repaired preservation term is a convex f-divergence with a KL zero limit.",
        "The whole objective and its gradients are not uniformly bounded; float32 expm1 overflow remains possible. The trainer's finite guard preserves charged failure receipts. This is loss-level coupling, not demonstrated finite precision on arbitrary events.",
        "manifests/revision_v1/kappa_pilot_v3.json",
        "logs/heavy_tail/HT-3b-objective-review.json",
    )
    operations = sum(v["operation_seconds"] for v in profile["phase_timer_summary"].values())
    claim(
        "COST-measured",
        "implemented",
        f"R1-68d incremental zsRE 300-edit cell: {profile['attempt_wall_seconds']:.3f} seconds, including {operations:.3f} seconds in model-operation phase scopes; full boundary-identity checks {profile['boundary_identity_seconds']:.3f} seconds.",
        "One selected-primary/dataset/profile measurement. Cell attempt time excludes pre-attempt model construction. Full-profile and comparator pricing remain owner work; all sixteen R1-64c recipes are inspected without a model.",
        PROFILE,
        "docs/tasks/R1-68d-zsre-v5-incremental.recipe.json",
        "logs/r1_round18/r1-64c-inspection-runlist.json",
    )
    claim(
        "COST-schedule",
        "proposed",
        "The 288-second profile materially improves feasibility. A 14–16-minute 1000-edit scenario would use 94.5–108 hours for 405 cells, before additions and failed-work reserves.",
        "Arithmetic scenario, not admitted heterogeneous cost. The September20 review must price all conditions/datasets, MQuAKE calibration, preparation, retries and optional panels against available time. October9 is the experiment stop; October10–14 is analysis/slides/rehearsal, October15 presentation.",
        PROFILE,
        "manifests/revision_v1/freeze_candidate_v5.json",
        "docs/tasks/R1-72-decision-addendum.md",
    )
    claim(
        "O7",
        "proposed",
        f"Matrix v5 retains 360 core + 45 extension cells in DEC-051 blocks. At this snapshot the final inventory has {len(inventory['incomplete_cells'])} incomplete cells and {len(inventory['complete_blocks'])} completed blocks.",
        "Development cells are not confirmation. Queue pause/resume/cost/memory guards are CPU-tested; R1-68d still rejects sealed execution. Final sealed backend, recipes, populations and admission remain required.",
        "logs/r1_round18/r1-77-final-draft-inventory.json",
        "manifests/revision_v1/run_matrix_v5.json",
        "scripts/r1_77_queue.py",
    )
    claim(
        "MQ-capacity",
        "proposed",
        "MQuAKE register has 4218 nominal subjects against 4050 demand; clearance loss of169 exhausts headroom. Separately, 700 historically exposed metadata-eligible rows cannot supply a 1000-edit + outside100 occupancy assay.",
        "The 168-subject headroom is not a certified free development pool. Q10 must choose unavailability or a separately reviewed 100/300-only diagnostic; even 700+168 remains232 short of1100.",
        "logs/r1_round17/R1-76-historical-mquake-capacity.json",
        "docs/tasks/R1-76-mquake-occupancy.md",
    )
    claim(
        "O6",
        "proposed",
        "A fixed-probe clustered-stress/recovery design and CPU-tested driver exist.",
        "No recovery trajectories are claimed. Q5 and its separate stress budget remain open; Q4 is approved DEC-054 and must no longer be called open.",
        "manifests/revision_v1/ht_development_panel_v1.json",
        "manifests/revision_v1/freeze_candidate_v5.json",
    )
    claim(
        "N1",
        "null",
        "The completed v0 primary study retains its negative/inconclusive contrasts and registered margins.",
        "Revision-v1 development improvements and the new pilot do not retrospectively confirm v0.",
        "docs/report.md",
        "results/S7/summary.json",
    )
    for name, h in bindings.items():
        if ht.sha(ROOT / name) != h:
            raise ValueError("evidence changed: " + name)
    if pilot["framing"] != ht.framing(ROOT):
        raise ValueError("mandatory framing changed")
    return {
        "task": "HT-4c",
        "rows": rows,
        "evidence_sha256": bindings,
        "pilot_snapshot": str(pilot_path),
        "pilot_complete_rows": pilot["complete_rows"],
        "framing": pilot["framing"],
        "primary_weights": primary["weights"],
        "freeze_open_gates": len(freeze["remaining_gates"]),
        "snapshot_policy": "All rows are tied to observed files and hashes; subsequent owner results require a new report/ledger snapshot.",
    }


def markdown(report):
    lines = [
        "# Talk claim–evidence ledger v3 — round18",
        "",
        "Charlie Derr, October15 Binghamton presentation. Experiments stop October9; October10–14 is reserved for analysis, slides and rehearsal.",
        "All Revision-v1 results below are developmental. The completed v0 study remains separate. Labels: implemented = code or measurement exists; proposed = unexecuted design; hypothesis = untested scientific claim; null = measured registered negative/inconclusive outcome. Missing is not null.",
        "",
        "## Required κ framing (DEC-054)",
        "",
        report["framing"],
        "",
        "## Claims and limits",
        "",
        "| ID | Maturity | Supported statement | Limits and next evidence | Bound evidence |",
        "|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        refs = "; ".join(
            f"[{e['path']}](../{e['path']}) SHA-256 {e['sha256']}" for e in row["evidence"]
        )
        lines.append(
            f"| {row['id']} | {row['label']} | {row['statement']} | {row['limits']} | {refs} |"
        )
    lines += [
        "",
        "## Population and timing qualifications",
        "",
        "- The pilot uses 32 ordinary-text windows ×127 positions. The HT-1b full driver audit uses128×127. Do not pool or interchange their numerical tails.",
        "- The pilot retention stream uses MQuAKE v3b; legacy standalone unseen/short-drift assays use the legacy development population. Their within-endpoint populations match across arms; this is not one shared population across different endpoints.",
        "- Pilot ES95 uses fractional empirical boundary mass on positive harm; seed spread is the larger within-arm range of three dataset-macro seed values. It is not a p-value or confidence interval.",
        "- Legacy pilot LS values retain their recorded complete-answer convention. DEC-053 driver rows separately report bounded equality, terminated equality and truncation; they are not silently relabeled.",
        "- Tail position identity for the legacy pilot is reconstructed from the bound deterministic producer and identical ordered cap-off matrices. Those files do not embed historical token-hash receipts.",
        "- The new cost measurement replaces old primary zsRE timing assumptions; it does not establish speedups for StableCap, matched updates, live caps or continued S1 bases.",
        "- Freeze candidate v5 resolves the installed DEC-053 implementation but retains17 final admission gates plus Q5/Q10. Its initial pilot binding predates the verified legacy-name alias supplement; this ledger uses the newer explicitly named pilot snapshot.",
        "",
        "The companion logs/r1_round18/talk_evidence_v3.json records all row bindings. Revalidate hashes before final slides; an immutable snapshot does not claim future files are unchanged.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--pilot",
        type=Path,
        default=Path("logs/r1_round18/ht3d-pilot-partial-v2-verified-aliases.json"),
    )
    a = p.parse_args(argv)
    paths = [ROOT / "docs/talk_claim_ledger_v3.md", ROOT / "logs/r1_round18/talk_evidence_v3.json"]
    if any(x.exists() for x in paths):
        p.error("v3 exists; create a new version instead of editing")
    report = assemble(a.pilot)
    for path, text in zip(
        paths, [markdown(report), json.dumps(report, indent=2) + "\n"], strict=True
    ):
        with path.open("x") as f:
            f.write(text)
    print(
        json.dumps(
            {
                "claims": len(report["rows"]),
                "bound_files": len(report["evidence_sha256"]),
                "pilot_rows": report["pilot_complete_rows"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
