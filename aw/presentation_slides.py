"""Render presentation sources and export draft speaker files; no claim regeneration."""

from __future__ import annotations

import base64
import html
import json
from pathlib import Path

from aw.pc_v0_report import ROOT, sha
from aw.presentation_claims import read_rows

SOURCE = ROOT / "docs/presentation/deck_v3"


def diagram(spec, *, allow_tail=False):
    def text(x, y, value, size=23, weight="normal"):
        return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}">{html.escape(value)}</text>'

    body = [
        '<rect width="1500" height="850" fill="#faf9f5"/>',
        text(45, 64, spec["title"], 40, "bold"),
        text(45, 108, spec["status"], 24),
        text(45, 151, "DRAFT — lead review", 22, "bold"),
    ]
    if spec["number"] == "03":
        # Two alternative credit rules branch from the same teaching problem;
        # a serial chain would incorrectly imply that SE-E follows SE-A.
        for panel, x, y, w, h in (
            (spec["panels"][0], 45, 240, 380, 285),
            (spec["panels"][1], 475, 185, 495, 190),
            (spec["panels"][2], 475, 415, 495, 220),
            (
                dict(
                    title="Common readout",
                    lines=[
                        "Bounded acquisition update",
                        "Efficacy + harm + cost",
                        "Compare SE-E minus SE-A",
                    ],
                ),
                1050,
                255,
                410,
                260,
            ),
        ):
            body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#e0ecef"/>')
            body.append(text(x + 15, y + 40, panel["title"], 25, "bold"))
            body.extend(
                text(x + 15, y + 90 + 35 * j, line, 21) for j, line in enumerate(panel["lines"])
            )
        for route in (
            "M425 350 H450 V280 H470",
            "M425 350 H450 V525 H470",
            "M970 280 H1008 V380 H1045",
            "M970 525 H1008 V380 H1045",
        ):
            body.append(f'<path d="{route}" stroke="#526675" stroke-width="2" fill="none"/>')
        for x, y in ((470, 280), (470, 525), (1045, 380)):
            body.append(
                f'<path d="M{x} {y} L{x - 12} {y - 7} L{x - 12} {y + 7} Z" fill="#526675"/>'
            )
    elif spec["panels"]:
        for i, p in enumerate(spec["panels"]):
            x = 45 + 485 * i
            body.append(
                f'<rect x="{x}" y="205" width="445" height="275" rx="14" fill="{["#e0ecef", "#e5eddd", "#f3e5d6"][i]}"/>'
            )
            body.append(text(x + 18, 254, p["title"], 26, "bold"))
            body.extend(text(x + 18, 316 + 51 * j, line, 23) for j, line in enumerate(p["lines"]))
        if spec.get("connections", True):
            body.extend(
                [
                    '<path d="M496 342 H520 M981 342 H1005" stroke="#314753" stroke-width="3"/>',
                    '<path d="M1240 490 V543 H267 V490" stroke="#526675" stroke-width="3" stroke-dasharray="9 6" fill="none"/>',
                ]
            )
    else:
        figure = ROOT.parent / spec["figure"]
        if allow_tail or not spec.get("requires_tail_gate", True):
            encoded = base64.b64encode(figure.read_bytes()).decode()
            body.append(
                f'<image x="30" y="181" width="1440" height="455" href="data:image/png;base64,{encoded}"/>'
            )
        else:
            body.append('<rect x="45" y="195" width="1410" height="365" rx="12" fill="#e0ecef"/>')
            for y, t in (
                (
                    270,
                    "HT-13 figure slot — source requires validation before this export",
                ),
                (
                    331,
                    "Check the expected-shortfall implementation and descriptive empirical labels.",
                ),
                (392, "Use a verified snapshot; refresh again after the reconciled 270-cell halt."),
                (
                    453,
                    "Source: figures/tails/survival_by_dataset.png in assets/presentation-materials",
                ),
            ):
                body.append(text(70, y, t, 25))
    body.extend(
        [
            text(45, 690, spec["footer"], 24),
            text(45, 741, spec["notes"], 22),
            text(45, 798, "Claims: " + ", ".join(spec["claims"]), 21),
        ]
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="850" viewBox="0 0 1500 850"><g font-family="DejaVu Sans, sans-serif" fill="#18252e">'
        + "".join(body)
        + "</g></svg>\n"
    )


def export(output):
    out = Path(output).resolve()
    if not out.is_relative_to(ROOT.parent / "assets/presentation-materials"):
        raise ValueError("presentation exports belong under assets/presentation-materials")
    specs = json.loads((SOURCE / "diagram-specs.json").read_bytes())
    from aw.presentation_pc import resolve, substitute

    pc = resolve()
    specs = substitute(specs, pc["slots"])
    ids = {row[0] for row in read_rows((ROOT / "docs/talk_claim_ledger_v7.md").read_text())}
    if any(c not in ids for spec in specs["slides"] for c in spec["claims"]):
        raise ValueError("diagram claim not in ledger")
    from aw.refresh_after_halt import tail_gate

    try:
        tail_gate()
        allow_tail = True
    except ValueError:
        allow_tail = False
    out.mkdir(parents=True, exist_ok=False)
    exports = []
    for spec in specs["slides"]:
        target = out / f"slide{spec['number']}.svg"
        target.write_text(diagram(spec, allow_tail=allow_tail))
        exports.append(dict(path=str(target), sha256=sha(target)))
    for p in sorted(SOURCE.glob("*.md")):
        q = out / p.name
        q.write_text(substitute(p.read_text(), pc["slots"]))
        exports.append(dict(path=str(q), sha256=sha(q)))
    backup_sources = []
    for suffix in ("pdf", "png"):
        original = (
            ROOT.parent
            / f"assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.{suffix}"
        )
        target = out / f"ht17-survival-backup.{suffix}"
        target.write_bytes(original.read_bytes())
        backup_sources.append(original)
        exports.append(dict(path=str(target), sha256=sha(target)))
    sources = [
        *backup_sources,
        *SOURCE.glob("*.json"),
        *SOURCE.glob("*.md"),
        ROOT / "logs/additional_work/HT-17/snapshot-20261004-complete/report.json",
        ROOT / "docs/additional_work/HT-17_report.md",
        ROOT.parent
        / "assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.png",
        Path(__file__),
        ROOT / "aw/presentation_prepare.py",
        ROOT / "aw/presentation_pc.py",
        ROOT / "docs/talk_claim_ledger_v7.md",
        *[ROOT.parent / spec["figure"] for spec in specs["slides"] if "figure" in spec],
        *[
            ROOT.parent / spec["figure_manifest"]
            for spec in specs["slides"]
            if "figure_manifest" in spec
        ],
    ]
    # Bind the canonical follow-up reports behind literal speaker/Q&A numbers.
    # They are partial snapshots, not new slots implying completed replications.
    for name in ("PC-reader", "R", "AW-L"):
        document = ROOT / f"docs/additional_work/{name}_report.md"
        sources.append(document)
        import re
        references = re.findall(r"logs/additional_work/[^`\s]+/report\.json", document.read_text())
        if not references:
            raise ValueError(f"canonical numerical report not named: {document}")
        for reference in set(references):
            report_path = ROOT / reference
            sources.append(report_path)
            verify = json.loads(report_path.read_bytes())
            from aw.presentation_pc import verify_sources
            verify_sources(verify, pc["sources_sha256"])
    sources.extend([ROOT / "docs/R1_stage4_report.md", ROOT / "docs/presentation/qa.md"])
    mapping = ROOT / "docs/presentation/abstract_to_testbed.md"
    if mapping.exists():
        sources.append(mapping)
    report = dict(
        draft=True,
        lead_review_required=True,
        pc_experimental_results_inserted=bool(pc["slots"]),
        pc_result_sources=pc,
        existing_measured_results_included=True,
        ht13_image_included=allow_tail,
        ht14="available; author review still needed"
        if mapping.exists()
        else "pending owner document",
        sources_sha256={str(p): sha(p) for p in sources},
        exports=exports,
    )
    report["sources_sha256"].update(pc["sources_sha256"])
    resolved = out / "resolved-diagram-specs.json"
    resolved.write_text(json.dumps(specs, indent=2) + "\n")
    exports.append(dict(path=str(resolved), sha256=sha(resolved)))
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
