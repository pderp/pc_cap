"""Build versioned deck v2 against prepared v6 content, with cost pending explicit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from scripts import ht4g_ledger_content as ledger
from scripts import ht10_slide_deck as rendering
from scripts import ht11_deck_review as review

ROOT = rendering.ROOT
CANONICAL = ROOT / "docs/presentation/deck_v2"
EXPORT = rendering.ASSETS / "deck_v2"


def prepare(content_path=ledger.CONTENT):
    content, binding = ledger.read(content_path)
    ledger.verify_sources(content)
    saved = json.loads((ROOT / "docs/presentation/deck_v1/slides.json").read_text())
    expected = copy.deepcopy(saved)
    for edit in review.REPLACEMENTS:
        if edit["field"].startswith("points/"):
            index = int(edit["field"].split("/")[1])
            if expected[edit["slide"] - 1]["points"][index] != edit["old"]:
                raise ValueError("v1 wording differs from reviewed patch")
            expected[edit["slide"] - 1]["points"][index] = edit["new"]
    for original, current in zip(expected, rendering.CONTENT, strict=True):
        if any(original[k] != v for k, v in current.items()):
            raise ValueError("deck CONTENT changed beyond HT11 patch")
    manifest, manifest_ref = ledger.read(rendering.MANIFEST)
    raw = rendering.OUTLINE.read_text()
    change = next(r for r in review.REPLACEMENTS if r["field"] == "speaker_notes")
    if raw.count(change["new"]) != 1:
        raise ValueError("corrected full-validation window qualification missing")
    old = raw.replace(change["new"], change["old"])
    if hashlib.sha256(old.encode()).hexdigest() != manifest["canonical_outline"]["sha256"]:
        raise ValueError("outline changed beyond the reviewed HT11 correction")
    evidence = [
        binding,
        ledger.ref(rendering.OUTLINE),
        manifest_ref,
        ledger.ref(rendering.__file__),
        ledger.ref(review.__file__),
        ledger.ref(__file__),
        ledger.ref("scripts/ht10b_render_pdf.py"),
        ledger.ref("docs/tasks/HT-11-deck-edit-request.patch"),
    ]
    for b in [*manifest["sources"], *manifest["exports"]]:
        if "path" not in b:
            b = b.get("export", b.get("destination"))
        if ledger.ref(b["path"]) != b:
            raise ValueError("HT9 evidence changed: " + str(b))
        evidence.append(b)
    section = raw.split("## Slide-by-slide outline", 1)[1].split("## Figures,", 1)[0]
    notes = re.findall(r"^### (\d+)\. (.*?) — ([^\n]+)\n(.*?)(?=^### |\Z)", section, re.M | re.S)
    if [int(r[0]) for r in notes] != list(range(1, 13)):
        raise ValueError("twelve ordered outline slides required")
    rows = {r["id"]: (i, r) for i, r in enumerate(content["rows"])}
    slides = []
    for source, (number, title, duration, text) in zip(rendering.CONTENT, notes, strict=True):
        number = int(number)
        slide = copy.deepcopy(source)
        identities = [i.removeprefix("PROPOSED-") for i in review.FAMILIES[number]]
        links = []
        for identity in identities:
            i, row = rows[identity]
            if row["status"] == "superseded" or not row["current_claim"]:
                raise ValueError("slide refers to superseded row")
            links.append(
                dict(
                    id=identity,
                    pointer=f"/rows/{i}",
                    statement_sha256=hashlib.sha256(row["statement"].encode()).hexdigest(),
                    evidence=row["evidence"],
                )
            )
        slide.update(
            number=number,
            outline_title=title,
            suggested_duration=duration,
            ledger=binding,
            ledger_rows=links,
            speaker_notes=text.strip()
            + "\n\n**Ledger v6 content:** "
            + ", ".join(identities)
            + ". Source: "
            + binding["path"]
            + " (SHA256 "
            + binding["sha256"]
            + "). Signed cost remains pending; this binds prepared content, not a published signed-cost ledger or launch approval.",
        )
        if slide.get("figure"):
            b = ledger.ref(rendering.FIGURES / slide["figure"])
            if b not in evidence:
                raise ValueError("figure missing from verified evidence")
            slide["figure_binding"] = b
        slides.append(slide)
    for n in (7, 8):
        if slides[n - 1]["foot"] != rendering.DEC054:
            raise ValueError("full visible DEC054 sentence required")
    return (
        slides,
        evidence,
        dict(
            prior=manifest["canonical_outline"],
            current=ledger.ref(rendering.OUTLINE),
            allowed_edit=change,
            ledger=binding,
            signature_status="pending_signed_cost_receipt",
        ),
    )


def build(canonical=CANONICAL, export=EXPORT):
    canonical, export = Path(canonical).resolve(), Path(export).resolve()
    if not canonical.is_relative_to(ROOT / "docs/presentation") or not export.is_relative_to(
        rendering.ASSETS
    ):
        raise ValueError("canonical docs in repo; exports in presentation assets")
    if canonical.exists() or export.exists():
        raise FileExistsError("new versioned deck directories required")
    values, evidence, lineage = prepare()
    canonical.mkdir(parents=True, exist_ok=False)
    export.mkdir(parents=True, exist_ok=False)
    documents = {
        "slides.json": json.dumps(values, indent=2, ensure_ascii=False) + "\n",
        "slides.md": rendering.markdown(values).replace("<!-- HT-10 ·", "<!-- HT-10b v2 ·", 1),
        "index.html": rendering.html_deck(values),
        "speaker-notes.md": "# Deck v2 — full notes and v6 evidence bindings\n\n"
        + "\n\n".join(
            f"## {s['number']}. {s['outline_title']}\n\n{s['speaker_notes']}" for s in values
        ),
    }
    for name, text in documents.items():
        ledger.write_new(canonical / name, text)
        shutil.copyfile(canonical / name, export / name)
    subprocess.run(
        [
            str(ROOT.parent / "assets/envs/status-paper-20260911/bin/python"),
            "-m",
            "scripts.ht10b_render_pdf",
            "--slides",
            str(canonical / "slides.json"),
            "--output",
            str(export / "current-research-deck.pdf"),
        ],
        cwd=ROOT,
        check=True,
    )
    for b in evidence:
        if ledger.ref(b["path"]) != b:
            raise ValueError("source changed during rendering")
    report = dict(
        task="HT-10b",
        version=2,
        slides=12,
        ledger=lineage["ledger"],
        signature_status=lineage["signature_status"],
        outline_lineage=lineage,
        evidence=evidence,
        canonical=[ledger.ref(p) for p in sorted(canonical.iterdir())],
        exports=[ledger.ref(p) for p in sorted(export.iterdir())],
        producer=ledger.ref(__file__),
        inherited_renderer=ledger.ref(rendering.__file__),
        new_experiments=0,
        gpu_seconds=0,
        pending=[
            "signed cost and later factual status refresh",
            "actual October9 completion/results",
        ],
        existing_files_changed=False,
    )
    ledger.write_new(canonical / "build-manifest.json", report)
    return dict(
        slides=12,
        ledger=report["ledger"],
        pdf=ledger.ref(export / "current-research-deck.pdf"),
        manifest=ledger.ref(canonical / "build-manifest.json"),
        pending=report["pending"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=CANONICAL)
    parser.add_argument("--export", type=Path, default=EXPORT)
    args = parser.parse_args()
    print(json.dumps(build(args.canonical, args.export), indent=2))
