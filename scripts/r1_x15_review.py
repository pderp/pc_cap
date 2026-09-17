"""Independent count, teacher-baseline and inventory review; no admission or draw."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("zsre", "counterfact", "mquake")


def reference(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def bound(binding):
    if reference(binding["path"]) != binding:
        raise ValueError("review source changed: " + binding["path"])
    return json.loads(Path(binding["path"]).read_text())


def reproduce(register, evidence, layout):
    """Independent implementation; no call to D9's review or capacity functions."""
    dispositions = {(r["dataset"], r["item_id"]): r for r in evidence["dispositions"]}
    expected = {(ds, r["item_id"]) for ds in DATASETS for r in register["candidates"][ds]}
    if len(dispositions) != len(evidence["dispositions"]) or set(dispositions) != expected:
        raise ValueError("candidate/disposition coverage differs")
    result, used = {}, set()
    for ds in DATASETS:
        first, eligible_items, exclusions = {}, 0, Counter()
        for meta in register["candidates"][ds]:
            d = dispositions[ds, meta["item_id"]]
            if any(d[k] != meta[k] for k in ("canonical_subject", "payload_sha256")):
                raise ValueError("register/disposition identity differs")
            if d["decision"] != "eligible":
                exclusions.update(d["reasons"])
                continue
            if d["reasons"] or not all(d[k] is True for k in (
                "alias_clear", "context_clear", "exposure_clear", "teacher_pass", "tokens_pass")):
                raise ValueError("eligible disposition has unresolved flags")
            if d["entity_id"] in used:
                raise ValueError("cross-dataset entity overlap")
            eligible_items += 1
            first.setdefault(d["entity_id"], d)
        used.update(first)
        demands = layout[ds]["demand_by_role"]
        roles = {r: sum(r in d["roles"] for d in first.values()) for r in demands}
        hall = []
        for size in range(1, len(demands) + 1):
            for subset in itertools.combinations(demands, size):
                capacity = sum(bool(set(subset).intersection(d["roles"])) for d in first.values())
                demand = sum(demands[r] for r in subset)
                hall.append(dict(roles=subset, capacity=capacity, demand=demand, margin=capacity-demand))
        result[ds] = dict(nominal_items=len(register["candidates"][ds]),
                         eligible_items=eligible_items, subjects=len(first),
                         demand=layout[ds]["demand_subjects"],
                         margin=len(first)-layout[ds]["demand_subjects"],
                         duplicate_entity_items=eligible_items-len(first),
                         role_subjects=roles, hall=hall,
                         all_hall_checks_pass=all(r["margin"] >= 0 for r in hall),
                         exclusion_reason_counts=dict(exclusions))
    return result


def build():
    spec = json.loads((ROOT / "docs/tasks/R1-D9-inputs-v3-post77d.json").read_text())
    evidence = bound(spec["d9"]["clearance"]["evidence"])
    register = bound(spec["register"])
    counts = reproduce(register, evidence, spec["dataset_layouts"])
    producer = json.loads((ROOT / "logs/r1_round25/r1-d9-clearance-dry-post77d.json").read_text())
    for ds in DATASETS:
        if counts[ds]["subjects"] != producer["counts"][ds]["usable_subjects"] or counts[ds]["role_subjects"] != producer["counts"][ds]["role_eligible"]:
            raise ValueError("independent count differs from clearance producer")
    teacher = {}
    run = ROOT.parent / "assets/runs/pc_cap/R1/r1_d10b/round24_v2"
    finished = json.loads((run / "teacher_evidence.json").read_text())
    chunks = []
    for ds in DATASETS:
        rows = []
        for path in sorted((run / ds).glob("chunk-*.json")):
            binding = reference(path)
            if binding not in finished["evidence_bindings"]:
                raise ValueError("teacher chunk not bound by completion")
            chunks.append(binding)
            rows.extend(bound(binding)["rows"])
        if len({r["item_id"] for r in rows}) != len(rows):
            raise ValueError("duplicate teacher rows")
        teacher[ds] = dict(reviewed=len(rows), teacher_pass=sum(r["teacher_pass"] is True for r in rows),
                           tokens_pass=sum(r["tokens_pass"] is True for r in rows),
                           empty=sum(r["generation"] == "" for r in rows),
                           empty_newline_one_step=sum(r["generation"] == "" and r["stopped_by"] == "newline" and r["steps"] == 1 for r in rows))
    matrix = bound(spec["matrix"])
    cells = matrix["cells"]
    coords = [(r["dataset"], r["condition"], r["realization"], r["order"]) for r in cells]
    if len(coords) != 360 or len(set(coords)) != 360:
        raise ValueError("core inventory differs")
    for row in cells + matrix["extension"]["cells"]:
        if row["checkpoints"] != ([100, 300] if row["dataset"] == "mquake" else [100, 300, 1000]):
            raise ValueError("cadence disagrees with DEC-060")
    declarations = bound(evidence["later_declarations"])
    prior = bound(declarations["prior"])
    known = {(r["payload"]["path"], r["payload"]["sha256"]) for r in prior["recipes"]}
    for row in declarations["recipes"]:
        value = bound(row["recipe"])
        if value["payload"] != row["payload"] or (row["payload"]["path"], row["payload"]["sha256"]) not in known:
            raise ValueError("new declaration payload lacks prior coverage")
        bound(row["payload"])
    paths = ["docs/decisions.md", "docs/R1_stage4_protocol_draft_v5_2_D.md",
             "docs/R1_stage4_protocol_draft_v5_1.md", "docs/R1_near_miss_family_v5_2_proposal.md",
             "docs/R1_execution_plan_v1.md", "docs/R1_stage4_queue_concurrency_v1.md",
             "docs/R1_stage2_notes.md", "docs/tasks/R1-D10e-orchestrator-review.json",
             "logs/r1_round24/r1-d10g-promotion-v2.json", "logs/r1_round23/r1-d10f-feasibility.json",
             "logs/r1_round24/r1-49h-draft-inventory-v2.json", "scripts/r1_49g_inference.py",
             "scripts/r1_49g_secondary.py", "scripts/r1_77_queue.py", "scripts/r1_77e_workers.py",
             "logs/r1_round25/r1-d9-clearance-dry-post77d.json", "docs/tasks/R1-D9-inputs-v3-post77d.json"]
    bindings = [reference(ROOT / p) for p in paths] + [spec["register"], spec["matrix"],
                spec["d9"]["clearance"]["evidence"], evidence["later_declarations"], *chunks, reference(__file__)]
    output = dict(task="R1-X15", method="independent register-order entity representatives and all role-subset capacities; raw teacher chunks",
                  counts=counts, teacher_baseline=teacher,
                  declarations=len(declarations["recipes"]), added_declarations=declarations["added_declarations"],
                  all_payloads_previously_reserved=True,
                  core_cells=len(cells), extension_cells=len(matrix["extension"]["cells"]),
                  multiplicity=matrix["multiplicity"],
                  protocol_states_empty_zsre_baseline="6,036" in (ROOT / "docs/R1_stage4_protocol_draft_v5_2_D.md").read_text(),
                  clearance_blockers=producer["blocked"],
                  ready_for_clearance_signature_subject_to_current_review=True,
                  ready_for_draw_seal_freeze_or_launch=False,
                  evidence=bindings, gpu_seconds=0, draws=0, seals=0)
    for b in bindings:
        if reference(b["path"]) != b:
            raise ValueError("source changed during independent review")
    path = ROOT / "logs/r1_round25/r1-x15-independent.json"
    with path.open("x") as f:
        json.dump(output, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"subjects": {d: counts[d]["subjects"] for d in DATASETS},
                      "teacher_baseline": teacher, "core_cells": len(cells)}, indent=2))


if __name__ == "__main__":
    build()
