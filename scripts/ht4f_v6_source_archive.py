"""Preserve exact historical sources of the published v6 ledger after DEC-067.

No ledger claim, prior hash, signature, live journal or decision is modified.
The supplement resolves historical source identities; it does not make old
snapshots current or bypass existing current-source refusal checks.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/r1_round41/ledger-v6-source-archive"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(raw)
    return ref(path)


def history(path, expected):
    relative = str(path.relative_to(ROOT))
    commits = subprocess.check_output(
        ["git", "log", "--all", "--format=%H", "--", relative], cwd=ROOT, text=True
    ).splitlines()
    for commit in commits:
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"], cwd=ROOT, capture_output=True
        )
        if result.returncode == 0 and sha(result.stdout) == expected:
            return result.stdout, commit
    raise ValueError("exact historical source unavailable: " + str(path))


def build():
    ledger_path = ROOT / "logs/r1_round40/talk_evidence_v6.json"
    binding = ref(ledger_path)
    ledger = json.loads(ledger_path.read_bytes())
    if ledger["pending"] or ledger["publication_status"] != "published_signed_cost_bound":
        raise ValueError("published signed-cost-bound ledger required")
    if OUT.exists():
        raise FileExistsError("new archival snapshot required")
    resolved, relocations = [], []
    for source, expected in ledger["sources_sha256"].items():
        path = Path(source)
        current = ref(path)
        if current["sha256"] == expected:
            resolved.append(dict(original=dict(path=source, sha256=expected), resolved=current))
            continue
        if path != ROOT / "docs/decisions.md":
            raise ValueError("unreviewed source change: " + source)
        raw, commit = history(path, expected)
        old_lines = [line for line in raw.decode().splitlines() if line]
        new_lines = [line for line in path.read_text().splitlines() if line]
        if new_lines[: len(old_lines)] != old_lines:
            raise ValueError("prior decision content changed; independent review required")
        archived = write(OUT / "decisions-through-DEC066.md", raw)
        row = dict(
            original=dict(path=source, sha256=expected),
            resolved=archived,
            current=current,
            historical_git_commit=commit,
            added_nonempty_lines=new_lines[len(old_lines) :],
            interpretation="Exact historical decision bytes; later delegation is not retroactively part of the signed-cost publication.",
        )
        resolved.append(row)
        relocations.append(row)
    cost = ledger["signed_cost_receipt"]
    if ref(cost["path"]) != cost:
        raise ValueError("signed cost receipt changed")
    journal = ledger["cost_journal_snapshot"]
    current = Path(journal["path"]).read_bytes()
    prefix = b""
    for line in current.splitlines(keepends=True):
        prefix += line
        if sha(prefix) == journal["sha256"]:
            break
    else:
        raise ValueError("original cost publication journal prefix was rewritten")
    journal_archive = write(OUT / "cost-publication-journal.jsonl", prefix)
    for row in resolved:
        if ref(row["resolved"]["path"]) != row["resolved"]:
            raise ValueError("source changed during historical verification")
    if ref(ledger_path) != binding:
        raise ValueError("ledger changed during archival verification")
    result = dict(
        task="HT-4f-historical-source-supplement",
        ledger=binding,
        signed_cost_receipt=cost,
        original_cost_journal=journal,
        resolved_cost_journal=journal_archive,
        sources=resolved,
        source_count=len(resolved),
        relocated_sources=relocations,
        ledger_rows=len(ledger["rows"]),
        ledger_claims_and_hashes_unchanged=True,
        current_source_checks_still_fail_on_changed_live_decisions=True,
        producer=ref(__file__),
    )
    write(OUT / "manifest.json", (json.dumps(result, indent=2) + "\n").encode())
    return dict(
        manifest=ref(OUT / "manifest.json"),
        sources=len(resolved),
        historical_relocations=len(relocations),
        ledger_rows=len(ledger["rows"]),
    )


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
