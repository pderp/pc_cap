"""Bind later development declarations with a strict prior-exposure containment proof."""

from __future__ import annotations

import copy
import json
import subprocess

from scripts.r1_73d_locality_recipes import verify_payload_change
from scripts.r1_d9_receipts import read_resource, ref, sha
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10b_teacher_review import verify_bindings


def main():
    log = ROOT / "logs/r1_round24"
    prior_report = json.loads((log / "r1-d10g-promotion.json").read_text())
    prior = read_resource(prior_report["evidence"])
    verify_bindings(prior["evidence_bindings"])
    supplement = read_resource(prior_report["supplement"])
    review = json.loads((ROOT / "logs/r1_round22/r1-d10a-review-v4.json").read_text())
    review_inputs = read_resource(review["inputs"])
    repaired = json.loads((log / "r1-73d-build.json").read_text())
    original, payload = (
        read_resource(repaired["source_payload"]),
        read_resource(repaired["payload"]),
    )
    unrelated = json.loads((ROOT / "manifests/dev/mquake_dev_v3b.json").read_text())[
        "unrelated_prompts"
    ]
    verify_payload_change(original, payload, unrelated)
    # Non-waived primary reservation text already imposed at least the restrictions
    # of these locality queries. Preserve its exact source event index as proof.
    witnesses = {}
    for i, event in enumerate(review_inputs["events"]):
        if event["reason"] == "development_payload_reserved" and event.get("text"):
            witnesses.setdefault(event["text"], i)
    proof = []
    for row in payload["endpoints"]["locality"]["rows"]:
        if row["prompt"] not in witnesses:
            raise ValueError(
                "new locality text not already covered by a non-waived reservation; new context review required"
            )
        proof.append(dict(item_id=row["item_id"], prior_event_index=witnesses[row["prompt"]]))
    known = {(r["payload"]["path"], r["payload"]["sha256"]) for r in supplement["recipes"]}
    if (repaired["source_payload"]["path"], repaired["source_payload"]["sha256"]) not in known:
        raise ValueError("repaired parent absent from promoted exposure inventory")
    known.add((repaired["payload"]["path"], repaired["payload"]["sha256"]))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    recipes = []
    for path in sorted((ROOT / "docs/tasks").rglob("*.recipe.json")):
        value = json.loads(path.read_text())
        if value.get("mode") != "stage4_development_cell":
            continue
        b = value["payload"]
        if (b["path"], b["sha256"]) not in known:
            raise ValueError("unreviewed development payload: " + str(path))
        if sha(b["path"]) != b["sha256"]:
            raise ValueError("declared development payload changed")
        recipes.append(dict(recipe=ref(path), payload=b, cell=value["cell"]))
    old_recipe_paths = {r["recipe"]["path"] for r in supplement["recipes"]}
    added = [r for r in recipes if r["recipe"]["path"] not in old_recipe_paths]
    declarations = dict(
        task="R1-D10g/R1-73d",
        parent=prior_report["evidence"],
        committed_head=head,
        prior_review_inputs=review["inputs"],
        repaired_payload=ref(log / "r1-73d-build.json"),
        recipes=recipes,
        added_recipes=added,
        locality_coverage_witnesses=proof,
        rule="all other payload bytes/roles unchanged; each new locality string already present as non-waived development_payload_reserved text",
        additional_uncovered_exposure=0,
        eligibility_losses=0,
        note="Explicit current declarations include uncommitted R1-73d recipes; future/new payloads still require review. No context exception or outcome-based release.",
    )
    bindings = [
        prior_report["evidence"],
        review["inputs"],
        ref(log / "r1-73d-build.json"),
        ref(__file__),
        repaired["payload"],
        ref(ROOT / "scripts/r1_73d_locality_recipes.py"),
        ref(ROOT / "scripts/r1_locality_contract.py"),
        *[r["recipe"] for r in recipes],
    ]
    verify_bindings(bindings)
    if head != subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip():
        raise ValueError("HEAD changed during declaration audit")
    output = ROOT.parent / "assets/runs/pc_cap/R1/r1_d10g/round24_v2"
    if output.exists():
        raise FileExistsError("new operative evidence version required")
    output.mkdir(parents=True)
    declaration_ref = write_new(output / "later-declarations.json", declarations)
    evidence = copy.deepcopy(prior)
    evidence.update(
        exposure_as_of_commit=head,
        later_declarations=declaration_ref,
        status="adopted_context_rule_with_contained_locality_repair_preteacher_only",
    )
    evidence["evidence_bindings"] += [*bindings, declaration_ref]
    binding = write_new(output / "evidence-v5-operative.json", evidence)
    teacher = write_new(
        output / "teacher-inputs.json",
        dict(
            mode="preteacher_inventory_not_teacher_certification",
            evidence=binding,
            dataset_layouts=evidence["dataset_layouts"],
            rows={
                ds: [
                    d["item_id"]
                    for d in evidence["dispositions"]
                    if d["dataset"] == ds and d["preteacher_eligible"]
                ]
                for ds in evidence["dataset_layouts"]
            },
        ),
    )
    report = dict(
        prior_report,
        evidence=binding,
        teacher_inputs=teacher,
        exposure_as_of_commit=head,
        parent_operative=prior_report["evidence"],
        declarations=declaration_ref,
        declared_development_recipes=len(recipes),
        added_declarations=len(added),
        locality_coverage_witnesses=len(proof),
        additional_uncovered_exposure=0,
    )
    write_new(log / "r1-d10g-promotion-v2.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("declared_development_recipes", "added_declarations", "evidence")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
