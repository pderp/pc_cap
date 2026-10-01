"""Publish the completed PC-13 tables and claims without advancing the pending deck."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import json
from pathlib import Path

from aw.pc_depth_report import DOCUMENT, OUTPUT
from aw.pc_historical import ROOT, Sources, sha

MARKER = "<!-- PC-13 settling-depth controls -->"
LEDGER = ROOT / "docs/talk_claim_ledger_v7.md"
REVIEW = ROOT / "docs/presentation/review-results.md"
EXPORT = ROOT.parent / "assets/presentation-materials/review-data/results.md"


def publish():
    path = OUTPUT / "report.json"
    r = json.loads(path.read_bytes())
    if r["status"] != "complete":
        raise ValueError("completed depth report required")
    sources = Sources()
    sources.check(r["sources_sha256"])
    receipt = json.loads((OUTPUT / "publication.json").read_bytes())
    if receipt["document"] != str(DOCUMENT) or receipt["sha256"] != sha(DOCUMENT):
        raise ValueError("report document differs from its publication")
    rows = {(v["depth"], v["arm"]): v for v in r["summary"] if v["dataset"] == "zsre"}

    def endpoint(k, arm, metric):
        return rows[k, arm]["metrics"][metric]

    retention = ", ".join(
        f"k={k}: {endpoint(k, 'SE-E', 'RET-ES') - endpoint(k, 'SE-A', 'RET-ES'):+.6f}"
        for k in (1, 8, 32)
    )
    tails = "/".join(f"{rows[k, 'SE-E']['es99_positive']:.6f}" for k in (1, 8, 32))
    max_difference = max(v["maximum_absolute_vector_difference"] for v in r["one_step_check"])
    claims = {
        "PC-depth": (
            "Predictive coding / extremes | measured descriptive control | "
            f"zsRE SE-E−SE-A own-prompt retention {retention}; "
            f"k=32 paraphrase difference {endpoint(32, 'SE-E', 'RET-GS') - endpoint(32, 'SE-A', 'RET-GS'):+.6f}; "
            f"SE-E ES99+ {tails} nats at depths 1/8/32 | "
            "Exposed S5; two datasets × three realizations × order100 only; 4064 harm positions/cell | "
            "Paired adjoint at each depth; eight-step order100 subset only | "
            "More settling increases taught-answer retention and learning cost; tail mean rises, maximum is nonmonotonic | "
            "No paraphrase benefit, selected best depth, general PC superiority or separation of direction from compute; random stopped early and offered-budget control underspent | "
            "docs/additional_work/PC-controls_report.md; logs/additional_work/PC-v0/controls-report-20260929/report.json"
        ),
        "PC-one-step": (
            "Predictive coding | measured mechanism check | "
            f"All six one-step pairs have exactly equal primary and bounded-secondary endpoints; largest absolute harm-vector difference {max_difference:.9g} | "
            "Same six dataset/realization pairs, order100; η=0.1 | "
            "Zero-error first step e₁=−η·adjoint; normalized direction removes scale in exact arithmetic | "
            "One-step endpoint equality agrees with the corrected mechanism; floating-point tolerance matters | "
            "Not bitwise-equal final memories, probabilities or zsRE harm; not an efficacy advantage | "
            "docs/additional_work/PC-controls_report.md; aw/tests/test_pc9.py"
        ),
    }
    originals = {p: p.read_bytes() for p in (LEDGER, REVIEW, EXPORT)}
    ledger = originals[LEDGER].decode()
    ledger = ledger.replace("2026-09-26 preparation snapshot.", "2026-09-29 evidence snapshot.", 1)
    lines = [
        line
        for line in ledger.splitlines()
        if not any(line.startswith(f"| {key} |") for key in claims)
    ]
    ledger = "\n".join(lines).rstrip() + "\n"
    ledger += "\n".join(f"| {key} | {value} |" for key, value in claims.items()) + "\n"
    previous = originals[REVIEW].decode().split(MARKER)[0].rstrip()
    previous = previous.replace(
        "These results do not include the later DEC-075 controls.",
        "The opening sections retain the completed default treatment; the PC-13 section below adds the later settling-depth controls.",
        1,
    )
    document = DOCUMENT.read_text()
    nested = "\n".join(
        "#" + line if line.startswith("#") else line for line in document.splitlines()
    )
    review = (
        previous
        + "\n\n"
        + MARKER
        + "\n\n"
        + "2026-09-29 addition, generated from the completed PC-13 report. "
        + "The earlier five-order tables remain separate from this common-order depth comparison.\n\n"
        + nested
        + "\n\n"
        + "Figure: `assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png` "
        + "(PDF/SVG and source manifest beside it). These are shareable scientific assets outside the repository.\n"
    )
    sources.verify_unchanged()
    if any(p.read_bytes() != value for p, value in originals.items()):
        raise ValueError("presentation documents changed concurrently; retry after coordination")
    LEDGER.write_text(ledger)
    REVIEW.write_text(review)
    EXPORT.write_text(review)
    outputs = {str(p): sha(p) for p in (LEDGER, REVIEW, EXPORT)}
    log = ROOT / "logs/additional_work/round53/pc13-materials.json"
    log.write_text(
        json.dumps(
            dict(
                inputs={
                    str(path): sha(path),
                    str(DOCUMENT): sha(DOCUMENT),
                    str(Path(__file__).resolve()): sha(__file__),
                },
                outputs=outputs,
                deck_status="Depth and credit controls published; PRES-6 export is recorded separately",
            ),
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(dict(status="PC-13 materials published", outputs=list(outputs))))


if __name__ == "__main__":
    publish()
