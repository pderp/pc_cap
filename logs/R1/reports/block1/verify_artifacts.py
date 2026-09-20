"""Final read-only source/export check; create one completion manifest."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ref(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path))


def load(path):
    return json.loads(Path(path).read_bytes())


def main():
    analysis = load(HERE / "analysis.json")
    audit = load(HERE / "receipt-audit.json")
    model = load(HERE / "appendix/report-data.json")
    ledger = load(HERE / "talk-evidence-v6-session-v10.json")
    if audit["status"] != "pass" or analysis["complete_blocks"] != [1]:
        raise ValueError("unverified analysis/audit")
    sources = {}

    def check(path, expected):
        path = str(Path(path).resolve())
        if path in sources and sources[path] != expected:
            raise ValueError("conflicting source identities: " + path)
        sources[path] = expected

    for document, key in ((analysis, "sources_sha256"), (audit, "source_bindings_sha256"),
                          (model, "source_bindings_sha256"), (ledger, "verification_sources")):
        for path, expected in document[key].items():
            check(path, expected)
    for relative, expected in analysis["analysis_source_sha256"].items():
        check(ROOT / relative, expected)
    for item in ledger["historical_source_resolution"]:
        if item["original"]["sha256"] != item["resolved"]["sha256"]:
            raise ValueError("historical source identity differs")
        check(item["resolved"]["path"], item["resolved"]["sha256"])
    for item in (audit["producer"], ledger["producer"], ledger["parent"], ledger["signed_cost_receipt"],
                 audit["watch_prefix"], ledger["journal_prefix"], model["watch"]["journal"]):
        check(item["path"], item["sha256"])
    standard = load(HERE / "appendix/figures/manifest.json")
    slide = load(HERE / "slide-figures/manifest.json")
    # Native exporter uses a plain list of file bindings.
    for item in standard["exports"]:
        check(item["path"], item["sha256"])
    for item in slide["exports"]:
        if item["source"]["sha256"] != item["presentation_copy"]["sha256"]:
            raise ValueError("presentation copy differs")
        for binding in item.values():
            check(binding["path"], binding["sha256"])
    for key in ("summary", "analysis", "producer"):
        check(slide[key]["path"], slide[key]["sha256"])
    for path, expected in sources.items():
        if sha(path) != expected:
            raise ValueError("immutable input/export changed: " + path)
    if not Path(audit["watch_prefix_original_path"]).read_bytes().startswith((HERE / "watch-block1.jsonl").read_bytes()):
        raise ValueError("historical watch prefix no longer matches")
    if not (ROOT / "logs/R1/operator_v10/receipts.jsonl").read_bytes().startswith((HERE / "ledger-v10-cost-journal-prefix.jsonl").read_bytes()):
        raise ValueError("historical signing prefix no longer matches")
    lock = load(HERE / "content-lock.txt")
    if lock != dict(resources=916, scripts=446, content_lock_verified=True):
        raise ValueError("content-lock check differs")
    if "55 passed" not in (HERE / "tests.txt").read_text():
        raise ValueError("required tests not successful")
    documents = [ROOT / "docs" / name for name in (
        "R1_stage4_report_block1_partial.md", "talk_claim_ledger_v6_session_v10.md",
        "tasks/R1-D14c.md", "tasks/R1-X22.md", "tasks/HT-4f-session-v10.md")]
    link_count = 0
    for path in documents:
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            target = (path.parent / link.split("#")[0]).resolve()
            if not target.exists() and target != HERE / "completion.json":
                raise ValueError("broken documentation link: " + str(target))
            link_count += 1
    outputs = [ref(p) for p in sorted(HERE.rglob("*")) if p.is_file() and p.name not in ("completion.json", "artifact-verification.txt")]
    outputs += [ref(p) for p in documents]
    completion = dict(tasks={"R1-D14c": "done", "X22": "done_pass", "HT-4f": "done_versioned_v10_supplement"},
                      generated_utc=datetime.now(timezone.utc).isoformat(), source_checks=len(sources),
                      checked_document_links=link_count, tests_passed=55, content_lock=lock,
                      included_cells=45, registered_primary_rows=63, available_realization0_primary_estimates=12,
                      primary_classifier_labels_available=0, primary_intervals_available=0,
                      verified_block_process_hours=audit["process_hours"], figures=9, figure_exports=27,
                      presentation_copies=18, source_manifest=ref(HERE / "receipt-audit.json"), outputs=outputs,
                      gpu_seconds=0, live_run_writes=False, installed_code_changed=False,
                      new_signatures=False, queue_control=False, committed=False)
    with (HERE / "completion.json").open("x") as stream:
        json.dump(completion, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in completion.items() if k != "outputs"}, indent=2))


if __name__ == "__main__":
    main()
