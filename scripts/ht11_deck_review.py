"""Read-only, claim-level deck-v1 review and proposed wording/ledger additions."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from scripts import ht10_slide_deck as deck
from scripts import r1_63l_full_validation_contract as full

ROOT = deck.ROOT
LEDGER = ROOT / "logs/r1_round25/talk_evidence_v5.json"
DECK = ROOT / "docs/presentation/deck_v1/slides.json"
# Human-reviewed claim families: a ledger row is not silently repurposed to
# support a newer scope or a different measurement population.
FAMILIES = {
    1: ["A1", "A2", "A3", "N1", "PROPOSED-programme"],
    2: ["A1", "A2", "A3"],
    3: ["O2", "PROPOSED-selection-uncertainty"],
    4: ["TAIL-zsre", "TAIL-counterfact"],
    5: ["PROPOSED-HT6-full-validation", "PROPOSED-DEC064"],
    6: ["A2", "O2", "TAIL-zsre", "PROPOSED-HT6-full-validation"],
    7: ["A4", "K-kappa02", "K-kappa05", "K-clip2"],
    8: ["K-kappa02", "K-kappa05", "K-clip2"],
    9: ["STRESS-zsre", "STRESS-counterfact", "STRESS-mquake"],
    10: ["U12-14", "ZSRE-empty-baseline", "PROPOSED-D4-scope"],
    11: ["CONCURRENCY", "PROPOSED-cost-v3"],
    12: ["A3", "A4", "K-kappa02", "K-kappa05", "K-clip2", "TAIL-zsre", "PROPOSED-programme"],
}
DIRECT = {
    1: [
        "docs/heavy_tail_counter_review.md",
        "../errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf",
        "../errata/presentation_details/sattellite-schedule",
    ],
    2: [
        "logs/r1_round16/selection_audit.json",
        "logs/review_r1_selection.md",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/revision_v1/reader.py",
        "src/pccap/revision_v1/adapt.py",
        "src/pccap/revision_v1/memory.py",
    ],
    3: ["logs/r1_round16/selection_audit.json", "logs/review_r1_selection.md"],
    4: ["logs/heavy_tail/audit-v5-round16-supplement/audit.json"],
    5: ["logs/r1_round35/ht6-final/report.json", "docs/R1_stage4_protocol_v5_2_D_4.md"],
    6: [
        "docs/R1_stage2_notes.md",
        "logs/review_r1_selection.md",
        "logs/heavy_tail/audit-v5-round16-supplement/audit.json",
        "logs/r1_round35/ht6-final/report.json",
    ],
    7: [
        "manifests/revision_v1/kappa_pilot_v3.json",
        "logs/heavy_tail/HT-3b-objective-review.json",
        "logs/r1_round22/ht3e-independent-review-v2.json",
    ],
    8: [
        "logs/r1_round22/ht3e-independent-review-v2.json",
        "logs/r1_round18/ht3d-pilot-final-aliases.json",
    ],
    9: [
        "logs/r1_round22/ht3e-independent-review-v2.json",
        "manifests/revision_v1/ht_development_panel_v1.json",
    ],
    10: [
        "manifests/revision_v1/run_matrix_v5_2_D_4.json",
        "docs/R1_stage4_protocol_v5_2_D_4.md",
        "docs/R1_U03_interpretation_memo.md",
        "logs/r1_round25/r1-x15-independent.json",
    ],
    11: [
        "docs/R1_execution_plan_v3.md",
        "docs/tasks/R1-cost-admission-receipt-v4.json",
        "docs/heavy_tail_suggested_slight_pivot.md",
    ],
    12: ["docs/heavy_tail_counter_review.md", "logs/r1_round22/ht3e-independent-review-v2.json"],
}
ASSESSMENT = {
    1: "Programme and meeting metadata, with implemented claims separated from the broader submitted abstract. No CFE implementation claim.",
    2: "Parameter arithmetic 1,640,964 + 1,707,264 = 3,348,228; 2.7002% of the stated 124M. Record state is additional. Interfaces remain analogies.",
    3: "42/15, selected-seed retention and Wilson interval agree with the audit. The interval is fixed-candidate descriptive and not selection-adjusted. Add zsRE to the unseen-query point.",
    4: "Values reproduce the 16,256-position historical assay. exp(8)=2980.96 justifies approximately 3,000. Positive harm and signed mean differ; no power-law inference.",
    5: "The four HT6 cells and both references support the numbers and DEC-064 interpretation. Ledger v5 predates this population, so a new ledger row is needed; clarify the 1,931/128-window distinction in notes.",
    6: "Chronology is supported as retrospective methodological learning; causal attribution to individual repairs is explicitly excluded. Chain-M invalid locality is not used.",
    7: "Bounded answer surprisal, zero limit, controls, seed count and checkpoint averaging agree with the registered pilot and repaired objective review. Neither all gradients nor the entire objective is bounded.",
    8: "Both kappa arms fail the predeclared rule; Clip2 meets the retention floor but is below ordinary mean retention and fails the full rule. Replace keeps retention with meets the floor.",
    9: "20/20 and edit-100 probability harm agree with the one-seed/two-schedule audit. Qualify the old-answer point by tested datasets and observed checkpoints. No permanent harm or order-invariance claim.",
    10: "Current D4 supports 285+45 and 75 omissions; v5 DEC060-scale has been superseded. Existing U12-14 and zsRE baseline qualifications apply. Prospective, no confirmatory outcome.",
    11: "Plan v3 supports scenario arithmetic, not measured progress or a signed cost admission. Older COST-matrix amounts are superseded. Keep process and elapsed hours distinct and the October9 stop.",
    12: "A proposed discriminating comparison, not an experimental conclusion about coupled free energy. Current null and descriptive improvements neither confirm nor refute the broader programme.",
}
PROPOSED_STATEMENTS = {
    "PROPOSED-programme": "Charlie Derr and Matthew Iklé; October 15, 2026 Binghamton satellite. The submitted active-inference abstract describes a broader programme; current frozen-GPT-2/memory experiments do not implement its complete coupled-free-energy agent.",
    "PROPOSED-selection-uncertainty": "Selected v5 zsRE unseen gate acceptance is 10/100 at 100 memory records, with descriptive fixed-candidate Wilson 95% interval 5.52–17.44%; no selection adjustment or certified rate below 10%.",
    "PROPOSED-HT6-full-validation": "Four development cells at 300 edits cover 1,931 complete 128-token windows / 245,237 scored positions each. Learned MQuAKE/zsRE mean KL is .005544/.002270; stable-v0 MQuAKE/zsRE is 0/.000789. zsRE stable-v0 maximum positive NLL change is 16.159 nats despite passing mean benchmarks. Bound numeric rows retain both references and concentration.",
    "PROPOSED-DEC064": "Mean cap KL <= .001 and signed mean NLL increase <= .01 nats are secondary benchmarks for original and own-cap-off references; equality passes. Numerical failure does not veto primary admission; incomplete/corrupt evidence remains unavailable. Continued-base certification is separate.",
    "PROPOSED-D4-scope": "D4 declares 120 zsRE + 120 CounterFact + 45 MQuAKE core cells, plus 45 optional learned-v2 cells. Five MQuAKE conditions / 75 cells are prospectively omitted. MQuAKE is limited to 100/300 checkpoints, leaving 21 of the fixed 63 checkpoint-1000 primary intervals unavailable. S1 is not certified as exact-v5 compute matched.",
    "PROPOSED-cost-v3": "Execution plan v3 scenarios: 431.31 expected process-hours, 646.96 at all cell ceilings, 750 shared process-hour cap; approximately 227.30 elapsed hours at assumed 1.65x throughput. Projections, not measured completion or proof of signed cost admission. Experiments stop October 9; October 10–14 is for analysis and preparation.",
}

REPLACEMENTS = [
    dict(
        id="HT11-W1",
        slide=3,
        field="points/3",
        old="Unseen gate acceptance: 10/100",
        new="zsRE unseen gate acceptance: 10/100",
        reason="The count is zsRE-specific, not a three-dataset macro.",
        priority="clarity",
    ),
    dict(
        id="HT11-W2",
        slide=5,
        field="speaker_notes",
        old="The fixed first 128 windows are not an iid sample.",
        new="Full validation covers 1,931 complete 128-token windows (245,237 next-token positions), with context reset per window. The earlier 128-window prefix is a dependent subset, not an iid sample.",
        reason="Distinguish the full validation population on this slide from the historical sampled-prefix assay.",
        priority="scope_precision",
    ),
    dict(
        id="HT11-W3",
        slide=8,
        field="points/4",
        old="Clip2 keeps retention; fails separation and adds a CounterFact false fire",
        new="Clip2 meets the retention floor; fails separation and adds a CounterFact false fire",
        reason="Clip2 mean .7789 is lower than ordinary .7961, although it meets the .7761 floor.",
        priority="evidence_precision",
    ),
    dict(
        id="HT11-W4",
        slide=9,
        field="points/0",
        old="All 20 old exact answers remain correct",
        new="Each tested dataset retains 20/20 old exact answers at observed checkpoints",
        reason="State the measured population and time scope instead of an unrestricted retention claim.",
        priority="clarity",
    ),
]


def reference(path):
    return full.ref((ROOT / path).resolve())


def fields(slide):
    result = [("title", slide["title"]), ("label", slide["label"])]
    result += [(f"points/{i}", value) for i, value in enumerate(slide["points"])]
    result += [("foot", slide["foot"])]
    if slide.get("submitted_title"):
        result += [("submitted_title", slide["submitted_title"])]
    # Notes are broken at paragraph/table boundaries, not silently treated as
    # a single blanket assertion. Retain their exact deck text in the record.
    result += [
        (f"speaker_notes/paragraph/{i}", value)
        for i, value in enumerate(slide["speaker_notes"].split("\n\n"))
    ]
    return result


def review():
    slides = json.loads(DECK.read_text())
    ledger = json.loads(LEDGER.read_text())
    rows = {r["id"]: r for r in ledger["rows"]}
    manifest = json.loads((ROOT / "docs/presentation/deck_v1/build-manifest.json").read_text())
    checked = []
    for binding in [
        manifest["outline"],
        manifest["ht9_manifest"],
        *manifest["evidence"],
        *manifest["canonical"],
        *manifest["exports"],
    ]:
        if reference(binding["path"]) != binding:
            raise ValueError("deck build binding changed: " + binding["path"])
        checked.append(binding)
    if [s["number"] for s in slides] != list(range(1, 13)):
        raise ValueError("expected all twelve slides")
    claims, proposed = [], []
    for number in range(1, 13):
        slide = slides[number - 1]
        direct = [reference(p) for p in DIRECT[number]]
        links = []
        for identity in FAMILIES[number]:
            if identity.startswith("PROPOSED-"):
                links.append(
                    dict(id=identity, status="proposed_addition_not_an_existing_ledger_row")
                )
                if identity not in {p["id"] for p in proposed}:
                    proposed.append(
                        dict(
                            id=identity,
                            status="proposed_only",
                            statement=PROPOSED_STATEMENTS[identity],
                            evidence=direct,
                            limits="Development, policy or planning evidence only; no new experiment or confirmatory admission. Add through the versioned ledger producer after the signing session.",
                        )
                    )
                continue
            row = rows[identity]
            lineage = []
            for binding in row["evidence"]:
                current = reference(binding["path"])
                lineage.append(
                    dict(
                        recorded=binding,
                        current=current,
                        unchanged=current["sha256"] == binding["sha256"],
                    )
                )
            links.append(
                dict(
                    id=identity,
                    status="existing_v5",
                    ledger=full.ref(LEDGER),
                    pointer=f"/rows/{ledger['rows'].index(row)}",
                    statement=row["statement"],
                    limits=row["limits"],
                    evidence_lineage=lineage,
                )
            )
        for field, text in fields(slide):
            replacements = [
                r["id"] for r in REPLACEMENTS if r["slide"] == number and r["old"] in text
            ]
            claims.append(
                dict(
                    id=f"S{number:02d}:{field}",
                    slide=number,
                    field=field,
                    text=text,
                    status="wording_refinement_requested"
                    if replacements
                    else (
                        "supported_directly_ledger_addition_needed"
                        if any(i.startswith("PROPOSED-") for i in FAMILIES[number])
                        else "supported_with_displayed_qualifications"
                    ),
                    assessment=ASSESSMENT[number],
                    ledger_links=links,
                    direct_evidence=direct,
                    edit_requests=replacements,
                    prospective=number in (10, 11),
                )
            )
    for edit in REPLACEMENTS:
        slide = slides[edit["slide"] - 1]
        content = (
            slide["speaker_notes"]
            if edit["field"] == "speaker_notes"
            else slide["points"][int(edit["field"].split("/")[1])]
        )
        if content.count(edit["old"]) != 1:
            raise ValueError("proposed old wording is not unique")
    checks = dict(
        kappa_slide_7=slides[6]["foot"] == deck.DEC054,
        kappa_slide_8=slides[7]["foot"] == deck.DEC054,
        slide_10_prospective="NO CONFIRMATORY RESULTS" in slides[9]["label"],
        slide_11_prospective="NOT MEASURED PROGRESS" in slides[10]["label"],
        nll_probability_ratio=math.exp(8),
        all_slide_fields_reviewed=True,
    )
    if not all(
        checks[k]
        for k in ("kappa_slide_7", "kappa_slide_8", "slide_10_prospective", "slide_11_prospective")
    ):
        raise ValueError("required slide framing missing")
    facts = json.loads((ROOT / "logs/r1_round35/ht6-final/report.json").read_text())
    full_values = []
    for identity, cell in facts["cells"].items():
        if cell["checkpoint"] != 300 or cell["concentration"]["full"]["positions"] != 245237:
            raise ValueError("HT6 population changed")
        for ref, value in cell["cap_fidelity_benchmark"]["references"].items():
            full_values.append(
                dict(
                    cell=identity,
                    reference=ref,
                    **value,
                    maximum_positive_nll=cell["full"]["references"][ref]["loss"][
                        "maximum_positive"
                    ],
                    source_pointer=f"/cells/{identity}/full/references/{ref}",
                    n=245237,
                    kl_half_mass_positions=cell["concentration"]["full"]["references"][ref][
                        "kl_positions"
                    ]["minimum_count_for_half_mass"],
                )
            )
    next(p for p in proposed if p["id"] == "PROPOSED-HT6-full-validation")["numeric_rows"] = (
        full_values
    )
    all_refs = {b["path"]: b["sha256"] for c in claims for b in c["direct_evidence"]}
    all_refs.update({b["path"]: b["sha256"] for b in checked})
    all_refs[str(DECK)] = full.sha(DECK)
    all_refs[str(LEDGER)] = full.sha(LEDGER)
    for p, sha in all_refs.items():
        if full.sha(p) != sha:
            raise ValueError("source changed during review: " + p)
    return dict(
        task="HT-11",
        created_utc=datetime.now(UTC).isoformat(),
        producer=full.ref(__file__),
        slides=12,
        reviewed_fields=len(claims),
        claims=claims,
        checks=checks,
        edits=REPLACEMENTS,
        proposed_ledger_additions=proposed,
        ht6_values=full_values,
        sources_sha256=all_refs,
        deck_build_bindings_checked=len(checked),
        decision="Keep the qualified development narrative. Apply four wording refinements and add explicit current evidence rows after the session; do not certify v5 as a complete ledger for deck v1.",
        superseded_ledger_rows=["DEC060-scale", "COST-matrix"],
        signing_status="No signing or launch decision is made by this review. Slides10/11 remain prospective; refresh their dated status only from actual completed receipts.",
        changed_existing_files=False,
        models_run=0,
        gpu_seconds=0,
    )


def write(output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "logs"):
        raise ValueError("review output must be under repo logs")
    result = review()
    output.mkdir(parents=True, exist_ok=False)
    with (output / "review.json").open("x") as f:
        json.dump(result, f, indent=2)
    with (output / "proposed-ledger-additions.json").open("x") as f:
        json.dump(result["proposed_ledger_additions"], f, indent=2)
    lines = [
        "# HT-11 — deck-v1 claim review",
        "",
        result["decision"],
        "",
        f"Reviewed all 12 slides and {result['reviewed_fields']} title/label/point/footnote/notes-paragraph fields. Verified {result['deck_build_bindings_checked']} deck-build bindings. No existing presentation or ledger file changed.",
        "",
        "## Requested wording refinements",
        "",
    ]
    for edit in result["edits"]:
        lines += [
            f"### {edit['id']} — slide {edit['slide']} ({edit['field']})",
            "",
            f"Current: {edit['old']}",
            "",
            f"Replacement: **{edit['new']}**",
            "",
            edit["reason"],
            "",
        ]
    lines += [
        "## Evidence lineage gaps",
        "",
        "v5 predates HT6 complete-validation results, DEC-064, D.4 scope and execution-plan-v3 amounts. Existing `DEC060-scale` and `COST-matrix` rows are superseded; they cannot substantiate the current numbers. The numerical sources themselves support the deck. The proposed additions JSON supplies direct source bindings, without pretending these rows have already been adopted. Selection uncertainty and programme/meeting metadata also receive explicit proposed rows. The later final v6 generator inherits v5 and adds SCOPE/COST; HT6 and DEC-064 still need explicit ledger entries.",
        "",
        "Historical row evidence is checked separately: each review row records old versus current SHA values. A changed implementation file does not rewrite the original ledger; stable audit reports plus current direct sources remain distinguishable. No missing or stale binding is silently labelled unchanged.",
        "",
        "## Slide-by-slide assessment",
        "",
        "| Slide | Assessment | Ledger IDs |",
        "|---|---|---|",
    ]
    for n in range(1, 13):
        lines += [f"| {n} | {ASSESSMENT[n]} | {', '.join(FAMILIES[n])} |"]
    lines += [
        "",
        "## Required framing",
        "",
        "Both κ slides contain the complete DEC-054 sentence visibly, not only in notes. Slide10 explicitly says planned/no confirmatory results; slide11 says planning scenarios/not measured progress. No κ gain, power law, universal preservation, permanent stress harm, or 1,000-record MQuAKE conclusion is justified or asserted with the present qualifications.",
        "",
        "## Claim-by-claim trace",
        "",
        "Each point and notes paragraph is retained verbatim in `review.json`, with ledger row index, evidence bindings, source lineage, qualification assessment and any edit-request ID. The table below provides a readable index; notes evidence tables are kept intact as a single paragraph.",
        "",
        "| Claim / deck field | Assessment | Ledger | Evidence |",
        "|---|---|---|",
    ]
    for c in result["claims"]:
        paths = "; ".join(
            Path(b["path"]).relative_to(ROOT).as_posix()
            if Path(b["path"]).is_relative_to(ROOT)
            else b["path"]
            for b in c["direct_evidence"]
        )
        lines += [
            f"| {c['id']} | {c['status']} {' '.join(c['edit_requests'])} | {', '.join(l['id'] for l in c['ledger_links'])} | {paths} |"
        ]
    lines += [
        "",
        "## Applying later",
        "",
        "Edit requests only during the signing session. After the session, apply W1/W3/W4 to the deck source CONTENT and W2 to the source outline notes, then generate a new versioned deck/export set so the build hashes remain coherent. Do not hand-edit only the PDF or generated slides JSON. Publish current ledger rows through a versioned ledger update and bind the new deck to that ledger. Retain this v1 snapshot for provenance. Update optional-extension/cost-signature wording only from exact operator receipts.",
        "",
    ]
    with (output / "review.md").open("x") as f:
        f.write("\n".join(lines))
    return dict(
        slides=12,
        fields=result["reviewed_fields"],
        edits=len(REPLACEMENTS),
        checks=result["checks"],
        status_counts=dict(Counter(c["status"] for c in result["claims"])),
        review=full.ref(output / "review.md"),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(write(parser.parse_args().output), indent=2))
