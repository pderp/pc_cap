"""Attach the actual v10 signed cost to a versioned v6 historical supplement.

No operator action/signature is executed. Historical claims and their original
hashes remain unchanged. DEC-069's later inference qualification is explicit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts import ht4f_v6_source_archive as archive  # noqa: E402
from scripts import r1_58g_operator as operator  # noqa: E402
from scripts import r1_63n_assembly_inputs as gates  # noqa: E402

HERE = Path(__file__).resolve().parent
REPLACE = sys.argv[1:] == ["--replace"]


def ref(path):
    return archive.ref(path)


def write(path, value):
    with path.open("w" if REPLACE else "x") as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    if sys.argv[1:] and not REPLACE:
        raise ValueError("only --replace is supported")
    parent_path = ROOT / "logs/r1_round40/talk_evidence_v6.json"
    parent_ref = ref(parent_path)
    parent = json.loads(parent_path.read_bytes())
    old_archive = json.loads((ROOT / "logs/r1_round41/ledger-v6-source-archive/manifest.json").read_bytes())
    resolved = []
    for item in old_archive["sources"]:
        old = item["original"]
        target = item["resolved"]
        if ref(target["path"])["sha256"] != target["sha256"]:
            raw, commit = archive.history(Path(old["path"]), old["sha256"])
            destination = HERE / ("v6-historical-" + Path(old["path"]).name)
            with destination.open("wb" if REPLACE else "xb") as stream:
                stream.write(raw)
            target = ref(destination)
            item = dict(item, historical_git_commit=commit)
        if target["sha256"] != old["sha256"]:
            raise ValueError("historical source identity differs")
        resolved.append(dict(original=old, resolved=target))
    session = ROOT / "logs/R1/operator_v10"
    raw = (session / "receipts.jsonl").read_bytes()
    if not raw.endswith(b"\n"):
        raise ValueError("torn operator journal")
    history = [json.loads(line) for line in raw.splitlines()]
    matches = [r for r in history if r.get("status") == "complete" and r.get("step") == "cost-admit"]
    if len(matches) != 1:
        raise ValueError("one completed cost admission required")
    completed = matches[0]
    snap = gates.Snapshot()
    previous = ref(ROOT / "docs/tasks/R1-58g-operator_v10/01-inputs.json")
    spec = snap.read(previous)
    cost = snap.read(completed["receipt"])
    form_ref = ref(ROOT / "docs/tasks/operator-v10/02-reviewed.json")
    form = snap.read(form_ref)
    candidate = ref(ROOT / "manifests/revision_v1/freeze_candidate_v15.json")
    request = gates.request_for("cost-admit", previous, spec, cost, candidate, session, snap)
    digest = operator.validate_signature(form, request)
    if (digest != completed["request_sha256"] or digest != cost["operator_request_sha256"]
            or form["fields"] != request["fields"] or cost["lead_signature"] != form["lead_signature"]):
        raise ValueError("v10 exact signed request differs")
    operator.preflight.check_receipt("chain_i_cell_ceilings", cost, spec)
    expected = operator.cost_source(spec) | dict(operator.common(spec), **form["fields"], status="closed",
        lead_approved=True, lead_signature=form["lead_signature"], operator_request_sha256=digest,
        failures_included=True, cost_admission_source=operator.cost_binding(spec))
    if cost != expected:
        raise ValueError("signed cost contents differ")
    prefix = b"".join(raw.splitlines(keepends=True)[:history.index(completed) + 1])
    with (HERE / "ledger-v10-cost-journal-prefix.jsonl").open("wb" if REPLACE else "xb") as stream:
        stream.write(prefix)
    snap.verify()
    for item in resolved:
        if ref(item["resolved"]["path"]) != item["resolved"]:
            raise ValueError("historical source changed")
    if ref(parent_path) != parent_ref or not (session / "receipts.jsonl").read_bytes().startswith(prefix):
        raise ValueError("publication inputs changed")
    overlay = [
        dict(id="D5-interpretation", status="adopted_policy", statement="DEC-069 qualifies the registered computation as preliminary decision summaries: no demonstrated 95% familywise control or established population effect. Three realization estimates and order dispersion precede labels; secondary df=2 t sensitivity assumes independent normal realization errors and never changes classification.", supersedes_current_reading_of="U12-14"),
        dict(id="D5-order", status="adopted_policy", statement="DEC-068 puts the primary/random/stable triplet across all three realizations first. The scope remains 285 core +45 optional cells, 75 prospective omissions and 63 primary slots; MQuAKE-1000 remains unavailable.", supplements="D4-scope"),
        dict(id="v10-cost-signed", status="verified_signed_cost", statement="Session v10 step 2 contains the exact signed typed revision-4 cost admission with the unchanged 750 process-hour cap. It binds estimates/reviewed transfers, not experimental outcomes. Later ceiling amendments are separate authorities; this supplement does not activate them.", supplements="cost-v3"),
        dict(id="block1-results-location", status="separate_partial_research_report", statement="The 45 realization-0 block-1 observations are reported separately in R1_stage4_report_block1_partial.md. They do not turn the historical development rows into confirmation results; no classifier is available from one realization.")]
    result = dict(task="HT-4f", version="v6_session_v10_supplement", publication_status="published_verified_v10_cost",
                  parent=parent_ref, historical_rows=parent["rows"], historical_claims_unchanged=True,
                  historical_source_resolution=resolved, signed_cost_receipt=completed["receipt"],
                  exact_request=request, exact_request_sha256=digest, signed_form=form_ref,
                  journal_prefix=ref(HERE / "ledger-v10-cost-journal-prefix.jsonl"),
                  cost_source=operator.cost_binding(spec), verification_sources=snap.bindings,
                  current_policy_overlay=overlay, matrix=ref(ROOT / "manifests/revision_v1/run_matrix_final.json"),
                  producer=ref(__file__), experiment_deadline="2026-10-09", presentation_date="2026-10-15",
                  launch_authorized=False, new_signatures=False, gpu_seconds=0,
                  interpretation="Versioned historical claim ledger plus current session cost and D.5 qualifications; not a silent replacement of v6 or a deck-builder compatibility claim.")
    write(HERE / "talk-evidence-v6-session-v10.json", result)
    lines = ["# Talk claim ledger v6 — session v10 supplement", "",
        "Published September 20, 2026. The [original v6](talk_claim_ledger_v6.md) remains the historical publication on session v8. This versioned supplement verifies session v10 step 2, preserves all 40 original claim rows and restores their exact historical source bytes. It supersedes the task-board instruction that v6 still awaits initial publication.", "",
        "Experiments stop **October 9**; the presentation is October 15. These historical development results are distinct from the [first partial confirmation report](R1_stage4_report_block1_partial.md).", "",
        "Signed v10 cost receipt: `" + completed["receipt"]["path"] + "`, SHA256 `" + completed["receipt"]["sha256"] + "`. Exact signed request: `" + digest + "`. The existing operator validator and receipt contract pass; no new signature or launch action was performed.", "",
        "## Current qualifications", ""]
    lines += ["- **" + r["id"] + ":** " + r["statement"] for r in overlay]
    lines += ["", "## Unchanged historical claims", "", "The following statuses describe the original evidence snapshot. Later adopted qualifications above govern any current talk wording. In particular, the original U12 row is not evidence of demonstrated familywise error control; cost scenarios are forecasts, and none of these rows establishes the full active-inference programme.", "",
              "| Claim | Historical status | Statement | Limits |", "|---|---|---|---|"]
    for row in parent["rows"]:
        lines.append("| " + " | ".join(str(row[k]).replace("|", "\\|").replace("\n", " ") for k in ("id", "status", "statement", "limits")) + " |")
    lines += ["", "## Evidence and reproduction", "", "[Machine-readable supplement](../logs/R1/reports/block1/talk-evidence-v6-session-v10.json) contains all original numeric rows, 141 historical source resolutions, the exact signed request, cost receipt and journal prefix. The historical inference implementation is archived at its original bytes; the current locked D.5 implementation is unchanged. The old v6 publisher is intentionally not rerun: it targets existing filenames and hard-codes session v8.", ""]
    write(ROOT / "docs/talk_claim_ledger_v6_session_v10.md", "\n".join(lines))
    print(json.dumps(dict(status=result["publication_status"], historical_rows=len(parent["rows"]), verified_historical_sources=len(resolved), request_sha256=digest)))


if __name__ == "__main__":
    main()
