"""Prepare v6 claim content now; attach only verified signed costs at publication.

Read-only evidence use. No signatures, operator transitions or experiments.
Historical statements and old hashes remain explicit; superseded rows cannot
be used as current scope/cost evidence by the deck builder.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts import r1_58g_operator as operator
from scripts import r1_d9_receipts as d9
from scripts.ht4e_claim_ledger import profile_inventory

ROOT = operator.ROOT
PARENT = ROOT / "logs/r1_round25/talk_evidence_v5.json"
ADDITIONS = ROOT / "logs/r1_round39/ht11-final-v2/proposed-ledger-additions.json"
CONTENT = ROOT / "logs/r1_round40/talk_evidence_v6_content.json"
CHANGED = {
    "docs/R1_stage2_notes.md": "Retained null/rejection-training chronology is development history; subsequent sections do not isolate causal effects of each repair.",
    "docs/decisions.md": "DEC-057/058 family and classifier retained; DEC-064 supersedes the cap veto, DEC-066 supersedes old MQuAKE execution counts.",
    "scripts/r1_49g_inference.py": "Current FAMILY retains 63 intervals, three realization clusters, five paired orders, seed0 and 10000 draws; the DEC-058 primary inequalities remain explicit.",
    "scripts/r1_77_queue.py": "Current queue retains two-worker accounting with a single1.15 multiplier and delegates retry/host-failure policy to the scheduler; old probes remain limited development throughput evidence.",
}
SUPERSEDED = {"DEC060-scale": "D4-scope", "COST-matrix": "cost-v3"}


def ref(path):
    p = Path(path)
    return d9.ref(p if p.is_absolute() else ROOT / p)


def read(path):
    binding = ref(path)
    return d9.read_metadata(binding), binding


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        if isinstance(value, str):
            stream.write(value)
        else:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    return ref(path)


def verify_sources(content):
    for path, sha in content["sources_sha256"].items():
        if ref(path)["sha256"] != sha:
            raise ValueError("ledger source changed: " + path)
    if content["pending"] != ["signed_cost_receipt"] or content["signed_cost_receipt"] is not None:
        raise ValueError("content must have precisely one pending signed-cost field")
    ids = [r["id"] for r in content["rows"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate ledger row")
    rows = {r["id"]: r for r in content["rows"]}
    for name, successor in SUPERSEDED.items():
        if rows[name]["status"] != "superseded" or rows[name]["superseded_by"] != successor:
            raise ValueError("stale scope/cost row not superseded")
    if len(rows["HT6-full-validation"]["numeric_rows"]) != 8:
        raise ValueError("all eight full-validation cell/reference rows required")
    return content


def prepare():
    parent, parent_ref = read(PARENT)
    additions, addition_ref = read(ADDITIONS)
    evidence = {
        parent_ref["path"]: parent_ref["sha256"],
        addition_ref["path"]: addition_ref["sha256"],
    }
    rebounds = {}
    historical = []
    rows = []
    for original in parent["rows"]:
        row = copy.deepcopy(original)
        row["status"] = row.get("label", "historical_development")
        row["inherited_from"] = parent_ref
        row["historical_evidence"] = copy.deepcopy(row["evidence"])
        rebound = []
        for old in row["evidence"]:
            current = ref(old["path"])
            evidence[current["path"]] = current["sha256"]
            if current["sha256"] != old["sha256"]:
                relative = str(Path(current["path"]).relative_to(ROOT))
                entry = dict(path=relative, old=old, current=current, claims=[])
                if relative in CHANGED:
                    entry["review"] = CHANGED[relative]
                    target = rebounds.setdefault(relative, entry)
                    target["claims"].append(row["id"])
                elif row["id"] in SUPERSEDED:
                    entry["review"] = (
                        "Changed historical plan; attached only to superseded historical claim. Current costs use plan v3."
                    )
                    entry["claims"] = [row["id"]]
                    historical.append(entry)
                else:
                    raise ValueError("unreviewed historical source drift: " + relative)
            rebound.append(current)
        row["evidence"] = rebound
        if row["id"] in SUPERSEDED:
            row.update(
                status="superseded", superseded_by=SUPERSEDED[row["id"]], current_claim=False
            )
        else:
            row["current_claim"] = True
        rows.append(row)
    if set(rebounds) != set(CHANGED):
        raise ValueError("expected four reviewed historical rebindings")
    profiles = profile_inventory()
    if len(profiles) != 8 or any(p["status"] != "complete" for p in profiles):
        raise ValueError("all corrected Chain-Q profiles required")
    for p in profiles:
        row = next(r for r in rows if r["id"] == "MQ-locality-" + p["condition"])
        row["historical_statement"] = row["statement"]
        row.update(
            status="development_measured_corrected_population",
            statement=f"MQuAKE {p['condition']}: RET-ES {p['retention']['es']}; RET-GS {p['retention']['gs']}; bounded locality {p['locality']['preserved_n']}/{p['locality']['expected_n']}; driver attempt {p['attempt_wall_seconds']:.3f} s.",
            limits="300 attempted development edits on the corrected exposed population. Attempt timing excludes outer startup and does not establish all final endpoints/costs. Chain-M locality0/50 was invalid payload evidence. Missing endpoints remain unavailable.",
            evidence=[p[k] for k in ("recipe", "payload", "result", "checkpoint", "receipt")],
        )
    for proposed in additions:
        row = copy.deepcopy(proposed)
        row["proposed_origin_id"] = row["id"]
        row["id"] = row["id"].removeprefix("PROPOSED-")
        row["status"] = (
            "planning_scenario"
            if row["id"] == "cost-v3"
            else "policy"
            if row["id"] in ("DEC064", "D4-scope")
            else "development_or_programme_evidence"
        )
        row["current_claim"] = True
        row["limits"] = (
            "No new experiment, confirmatory result, signature or launch authority. Cost scenario is not measured progress; all development/population qualifications in the statement apply."
        )
        row["evidence"] = [ref(b["path"]) for b in row["evidence"]]
        # The proposal's source hashes must still match: never silently rebind
        # new numeric claims just because a file happens to exist.
        for old, current in zip(proposed["evidence"], row["evidence"], strict=True):
            if old["sha256"] != current["sha256"]:
                raise ValueError("HT11 addition evidence changed")
        if row["id"] == "DEC064":
            row["evidence"].append(ref("docs/R1_stage4_protocol_v5_2_D_3.md"))
        rows.append(row)
    facts, facts_ref = read("logs/r1_round35/ht6-final/report.json")
    numbers = next(r for r in rows if r["id"] == "HT6-full-validation")["numeric_rows"]
    for n in numbers:
        c = facts["cells"][n["cell"]]
        r = n["reference"]
        expected = dict(
            cell=n["cell"],
            reference=r,
            **c["cap_fidelity_benchmark"]["references"][r],
            maximum_positive_nll=c["full"]["references"][r]["loss"]["maximum_positive"],
            source_pointer=f"/cells/{n['cell']}/full/references/{r}",
            n=c["full"]["scored"],
            kl_half_mass_positions=c["concentration"]["full"]["references"][r]["kl_positions"][
                "minimum_count_for_half_mass"
            ],
        )
        if n != expected or c["checkpoint"] != 300 or n["n"] != 245237:
            raise ValueError("HT6 numeric row differs from source")
    for row in rows:
        for b in row["evidence"]:
            if ref(b["path"]) != b:
                raise ValueError("claim evidence changed while preparing")
            evidence[b["path"]] = b["sha256"]
    for path in (
        "docs/tasks/R1-73d-post77d/inspection-receipts.json",
        "scripts/ht4e_claim_ledger.py",
        "docs/tasks/R1-D9-inputs-v9.json",
        "scripts/ht4f_claim_ledger.py",
        __file__,
    ):
        b = ref(path)
        evidence[b["path"]] = b["sha256"]
    content = dict(
        task="HT-4g",
        schema_version=1,
        version="v6-content",
        created_utc=datetime.now(UTC).isoformat(),
        parent=parent_ref,
        additions=addition_ref,
        producer=ref(__file__),
        rows=rows,
        historical_binding_updates=list(rebounds.values()),
        superseded_binding_changes=historical,
        sources_sha256=evidence,
        profiles=profiles,
        framing=parent["framing"],
        signed_cost_receipt=None,
        pending=["signed_cost_receipt"],
        publication_status="content_ready_cost_signature_pending",
        experiment_deadline="2026-10-09",
        presentation="2026-10-15",
        gpu_seconds=0,
        confirmatory_results=False,
        launch_authorized=False,
    )
    return verify_sources(content)


def markdown(content, *, cost=None):
    def escape(value):
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Talk claim ledger v6 — "
        + ("published evidence snapshot" if cost else "content ready; signed cost pending"),
        "",
        "Experiments stop October 9; presentation October 15. Development measurements, programme statements, adopted policies and planning scenarios are distinguished. No confirmatory outcome or launch authority is created by this ledger.",
        "",
        "Signed cost: "
        + (json.dumps(cost) if cost else "**pending — the single unfilled publication field**")
        + ".",
        "",
        "| Claim | Status | Statement | Limits |",
        "|---|---|---|---|",
    ]
    for row in content["rows"]:
        lines.append(
            "| "
            + " | ".join(escape(row[k]) for k in ("id", "status", "statement", "limits"))
            + " |"
        )
    lines += [
        "",
        "## Full-validation numerical rows",
        "",
        "Four development cells at 300 edits, two references each, 245,237 positions / 1,931 windows. Original and own-cap-off references stay distinct. Zero total KL has an undefined half-mass count.",
        "",
        "| Cell | Reference | Mean KL | Mean signed NLL change | Max positive NLL | Half-KL positions | KL / NLL labels |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in next(r for r in content["rows"] if r["id"] == "HT6-full-validation")["numeric_rows"]:
        lines.append(
            f"| {r['cell']} | {r['reference']} | {r['mean_kl_nats']:.12g} | {r['mean_signed_nll_increase_nats']:.12g} | {r['maximum_positive_nll']:.12g} | {r['kl_half_mass_positions'] if r['kl_half_mass_positions'] is not None else 'undefined (zero total)'} | {r['mean_kl_label']} / {r['mean_nll_label']} |"
        )
    lines += [
        "",
        "## Historical source rebindings",
        "",
        "These are reviewed new source snapshots; historical files/claims are retained through the parent ledger. Superseded scope/cost rows are not current evidence. Old and new hashes are explicit.",
        "",
    ]
    for row in [*content["historical_binding_updates"], *content["superseded_binding_changes"]]:
        lines += [
            f"- `{row['path']}`: `{row['old']['sha256']}` → `{row['current']['sha256']}`. {row['review']}"
        ]
    lines += [
        "",
        "The accompanying JSON binds every row to evidence. The final publisher fills the one signed-cost field and binds this exact content document; it does not change empirical statements, supersession, historical hashes or numeric rows. Other signing/launch gates remain separate.",
        "",
        content["framing"],
        "",
    ]
    return "\n".join(lines)


def build():
    content = prepare()
    binding = write_new(CONTENT, content)
    doc = write_new(ROOT / "docs/talk_claim_ledger_v6_content.md", markdown(content))
    return dict(
        content=binding,
        document=doc,
        rows=len(content["rows"]),
        pending=content["pending"],
        historical_rebindings=len(content["historical_binding_updates"]),
    )


def publish(content_path, cost_path):
    content, binding = read(content_path)
    verify_sources(content)
    cost, cost_ref = read(cost_path)
    if type(cost.get("receipt_revision")) is not int or cost["receipt_revision"] != 4:
        raise ValueError("typed v4 cost receipt required")
    spec, _ = read("docs/tasks/R1-D9-inputs-v9.json")
    d9.check_receipt("chain_i_cell_ceilings", cost, spec)
    journal = ROOT / "logs/R1/operator_v8/receipts.jsonl"
    journal_ref = ref(journal)
    rows = operator.journal_read(journal)
    matches = [
        r
        for r in rows
        if r.get("status") == "complete"
        and r.get("step") == "cost-admit"
        and r.get("receipt") == cost_ref
    ]
    if len(matches) != 1 or matches[0]["request_sha256"] != cost.get("operator_request_sha256"):
        raise ValueError("exact completed operator cost request required")
    verify_sources(content)
    if ref(content_path) != binding or ref(cost_path) != cost_ref or ref(journal) != journal_ref:
        raise ValueError("publication evidence changed during verification")
    final = copy.deepcopy(content)
    final.update(
        task="HT-4f",
        version="v6",
        content=binding,
        signed_cost_receipt=cost_ref,
        pending=[],
        publication_status="published_signed_cost_bound",
        published_utc=datetime.now(UTC).isoformat(),
        cost_journal_snapshot=journal_ref,
        publisher=ref(__file__),
    )
    # Preserve every prepared claim and historical hash exactly.
    assert (
        final["rows"] == content["rows"]
        and final["historical_binding_updates"] == content["historical_binding_updates"]
    )
    out = ROOT / "logs/r1_round40/talk_evidence_v6.json"
    doc = ROOT / "docs/talk_claim_ledger_v6.md"
    if out.exists() or doc.exists():
        raise FileExistsError("new publication files required")
    return dict(
        ledger=write_new(out, final),
        document=write_new(doc, markdown(content, cost=cost_ref)),
        pending=[],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "publish"))
    parser.add_argument("--content", type=Path, default=CONTENT)
    parser.add_argument("--cost-receipt", type=Path)
    args = parser.parse_args()
    if args.action == "publish" and args.cost_receipt is None:
        parser.error("--cost-receipt is required for publication")
    print(
        json.dumps(
            build() if args.action == "build" else publish(args.content, args.cost_receipt),
            indent=2,
        )
    )
