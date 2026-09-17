"""Promote the reviewed v5 overlay and debit later declared development exposure."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.r1_d9_receipts import read_resource, ref, sha
from scripts.r1_d10a_review import ASSETS, ROOT, Snapshot, collect, write_new
from scripts.r1_d10a_review_core import DATASETS, Entities, Matcher, digest, event_blocks
from scripts.r1_d10d_options import layouts
from scripts.r1_d10e_adjudication import waive

from pccap.data.tokenize import GPT2Tokenizer


def promote(candidate, adoption, events, aliases):
    if not adoption.get("decision", "").startswith("ADOPTED"):
        raise ValueError("explicit orchestrator adoption required")
    if candidate.get("context_adjudication_admitted") is not False:
        raise ValueError("unpromoted v5 proposal required")
    result = copy.deepcopy(candidate)
    result["dispositions"] = result.pop("proposed_dispositions")
    entities = Entities(aliases)
    names = [d["canonical_subject"] for d in result["dispositions"]]
    matcher = Matcher(names + list(aliases) + list(aliases.values()), entities)
    by_entity = defaultdict(list)
    for i, event in enumerate(events):
        matched = matcher.matches(event.get("text", ""))
        if event.get("subject"):
            matched.add(entities.identity(event["subject"])[0])
        for entity in matched:
            by_entity[entity].append(i)
    losses = []
    for d in result["dispositions"]:
        blocked = [
            i
            for i in by_entity.get(d["entity_id"], [])
            if event_blocks(d["dataset"], events[i], d["entity_id"], entities)
            and not waive(events[i])
        ]
        if not blocked:
            continue
        before = d["preteacher_eligible"]
        d["preteacher_eligible"] = False
        d["decision"] = "exclude"
        d["exposure_clear"] = False
        if any(events[i].get("text") for i in blocked):
            d["context_clear"] = False
        if any(
            events[i].get("subject")
            and entities.identity(events[i]["subject"])[0] == d["entity_id"]
            for i in blocked
        ):
            d["alias_clear"] = False
        d["reasons"] = sorted(
            (set(d["reasons"]) - {"pending_final_teacher_token_and_role_review"})
            | {"later_development_exposure"}
        )
        if before:
            losses.append(
                dict(
                    dataset=d["dataset"],
                    item_id=d["item_id"],
                    entity_id=d["entity_id"],
                    event_indices=blocked,
                )
            )
    layout = layouts("D")
    counts = {}
    for ds in DATASETS:
        rows = [d for d in result["dispositions"] if d["dataset"] == ds]
        available = [d for d in rows if d["preteacher_eligible"]]
        counts[ds] = {
            **candidate["counts"][ds],
            "preteacher_items": len(available),
            "preteacher_subjects": len({d["entity_id"] for d in available}),
            "demand_subjects": layout[ds]["demand_subjects"],
            "reasons": dict(Counter(x for d in rows for x in d["reasons"])),
        }
        counts[ds]["preteacher_headroom"] = (
            counts[ds]["preteacher_subjects"] - counts[ds]["demand_subjects"]
        )
    result.update(
        mode="unsealed_partial_clearance_evidence",
        schema_version=5,
        status="adopted_context_rule_with_later_exposure_preteacher_only",
        context_adjudication_admitted=True,
        counts=counts,
        dataset_layouts=layout,
        teacher_token_review_complete=False,
        role_compatibility_complete=False,
    )
    return result, losses


def run(commit, output, report):
    if (
        output.exists()
        or not output.resolve().is_relative_to(ASSETS)
        or not report.resolve().is_relative_to(ROOT / "logs")
    ):
        raise ValueError("new assets output and repository report required")
    adoption_path = ROOT / "docs/tasks/R1-D10e-orchestrator-review.json"
    adoption = json.loads(adoption_path.read_text())
    for b in adoption["bindings"].values():
        if sha(ROOT / b["path"]) != b["sha256"]:
            raise ValueError("adoption input changed")
    candidate_ref = adoption["bindings"]["candidate_v5"]
    candidate = read_resource(candidate_ref)
    previous_report = json.loads((ROOT / "logs/r1_round22/r1-d10a-review-v4.json").read_text())
    prior = read_resource(previous_report["inputs"])
    snap = Snapshot(commit)
    register = snap.read(candidate["register"]["path"])
    tok = GPT2Tokenizer(snapshot=Path(candidate["base"]["path"]))
    if tok.file_sha256() != candidate["tokenizer_sha256"]:
        raise ValueError("tokenizer identity changed")
    current = collect(snap, register, tok)
    if current["verified_alias_pairs"] != prior["verified_alias_pairs"]:
        raise ValueError("alias policy changed; explicit new review required")
    old = {digest(e) for e in prior["events"]}
    events = [e for e in current["events"] if digest(e) not in old]
    # Enumerate every development recipe, including shared-payload re-profiles:
    # collect() deduplicates payloads but this roster preserves all constructors.
    recipes = []
    payload_bindings = {
        (x.get("path"))
        for x in current["inventory"]
        if x["kind"] == "committed_development_payload"
    }
    for name in sorted(snap.files):
        if name.startswith("docs/tasks/") and name.endswith(".recipe.json"):
            doc = snap.read(name)
            if doc.get("mode") == "stage4_development_cell":
                if doc["payload"]["path"] not in payload_bindings:
                    raise ValueError("unreviewed declared payload")
                recipes.append(
                    dict(recipe=ref(ROOT / name), cell=doc["cell"], payload=doc["payload"])
                )
    supplement = dict(
        from_commit=candidate["exposure_as_of_commit"],
        to_commit=snap.commit,
        events=events,
        event_count=len(events),
        inventory=current["inventory"],
        recipes=recipes,
        policy="all declared payloads reserved whether executed or pending; no outcome-based release",
        source_bindings=[{"path": p, "sha256": h} for p, h in sorted(snap.bindings.items())],
    )
    snapshots = ROOT / "logs/r1_round24/producer_snapshot"
    snapshots.mkdir(exist_ok=True)
    replacements, bound = [], {}
    # Provenance code is preserved byte-for-byte before this round changes its
    # consumers. A historical producer is never silently rebound to new code.
    for b in candidate["evidence_bindings"]:
        path = Path(b["path"])
        if sha(path) != b["sha256"]:
            raise ValueError("predecessor input changed before promotion: " + str(path))
        if path.is_relative_to(ROOT / "scripts"):
            archived = snapshots / (b["sha256"][:12] + "-" + path.name + ".txt")
            if not archived.exists():
                with archived.open("xb") as f:
                    f.write(path.read_bytes())
            if sha(archived) != b["sha256"]:
                raise ValueError("historical producer snapshot changed")
            new = ref(archived)
            replacements.append(dict(original=b, preserved=new))
            bound[new["path"]] = new["sha256"]
        else:
            bound[b["path"]] = b["sha256"]
    operative, losses = promote(candidate, adoption, events, prior["verified_alias_pairs"])
    supplement["preteacher_losses"] = losses
    snap.verify()
    output.mkdir(parents=True)
    supplement_ref = write_new(output / "later-exposure.json", supplement)
    for b in [
        ref(adoption_path),
        candidate_ref,
        supplement_ref,
        ref(__file__),
        *supplement["source_bindings"],
    ]:
        bound[b["path"]] = b["sha256"]
    operative.update(
        exposure_as_of_commit=snap.commit,
        orchestrator_review_receipt=ref(adoption_path),
        evidence_bindings=[{"path": p, "sha256": h} for p, h in sorted(bound.items())],
        historical_producer_snapshots=replacements,
        later_exposure=supplement_ref,
    )
    operative_ref = write_new(output / "evidence-v5-operative.json", operative)
    eligibility = dict(
        mode="preteacher_inventory_not_teacher_certification",
        evidence=operative_ref,
        dataset_layouts=layouts("D"),
        rows={
            ds: [
                d["item_id"]
                for d in operative["dispositions"]
                if d["dataset"] == ds and d["preteacher_eligible"]
            ]
            for ds in DATASETS
        },
    )
    eligibility_ref = write_new(output / "teacher-inputs.json", eligibility)
    result = dict(
        task="R1-D10g",
        evidence=operative_ref,
        supplement=supplement_ref,
        teacher_inputs=eligibility_ref,
        adoption=ref(adoption_path),
        parent_candidate=candidate_ref,
        parent_v4=previous_report["evidence"],
        counts=operative["counts"],
        later_events=len(events),
        lost_items=len(losses),
        declared_development_recipes=len(recipes),
        exposure_as_of_commit=snap.commit,
        future_exposure_requires_supplement=True,
        gpu_seconds=0,
        model_calls=0,
        draws=0,
        seals=0,
    )
    write_new(report, result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    r = run(args.commit, args.output, args.report)
    print(
        json.dumps(
            {
                k: r[k]
                for k in ("counts", "later_events", "lost_items", "declared_development_recipes")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
