"""Resolve completed AW-B and depth/control evidence for slides and claims."""

from __future__ import annotations

import json
from pathlib import Path

from aw.pc_historical import ROOT, Sources, sha
from aw.presentation_pc import present, verify_sources


def values(name, report, slots, bindings):
    if report["status"] != "complete":
        raise ValueError("completed report required for follow-up claims")
    verify_sources(report, bindings)
    if name == "depth_controls":
        rows = {(v["depth"], v["arm"]): v for v in report["summary"] if v["dataset"] == "zsre"}
        for depth in (1, 8, 32):
            for metric in ("RET-ES", "RET-GS"):
                slots[f"depth.{depth}.{metric}"] = present(rows[depth, "SE-E"]["metrics"][metric])
        random = report["credit_controls"]["random"][1]
        slots["control.random.es"] = present(random["es"])
        slots["control.random.n"] = str(random["n"])
        return "measured depth controls; random closed partial; adjoint budget offered, underspent"
    cells = report["evaluation"]["cells"]
    if len(cells) != 10 or not report["success"]["all_coordinates_by_config"]["mixture:0.367879"]:
        raise ValueError("AW-B result differs: revise the interpretation")
    for ds in ("zsre", "counterfact"):
        selected = [c for k, c in cells.items() if k.startswith(ds + "-")]
        if len(selected) != 5:
            raise ValueError("five AW-B orders required")
        for arm in ("v5", "mixture:0.367879"):
            label = "mixture" if arm.startswith("mixture") else arm
            for key, section, field in (
                ("maximum", "loss", "maximum_positive"),
                ("es99", "loss", "es99_positive"),
                ("kl", "kl", "mean_signed"),
            ):
                data = [c["harm"][arm]["summary"]["original"][section][field] for c in selected]
                slots[f"awb.{ds}.{label}.{key}"] = f"{min(data):.4g}–{max(data):.4g}"
        changes = [
            c["efficacy_changes"]["RET-GS"]
            for c in report["success"]["per_coordinate"]
            if c["config"].startswith("mixture") and c["cell"].startswith(ds + "-")
        ]
        slots[f"awb.{ds}.gs_change"] = f"{min(changes):.4g} to {max(changes):.4g}"
    slots["awb.hours"] = present(
        sum(report[k]["elapsed_process_seconds"] for k in ("calibration_cost", "evaluation_cost"))
        / 3600
    )
    return "measured: all ten exposed evaluation memories pass the declared rule"


def publish():
    from aw.presentation_pc import resolve

    resolved = resolve()
    slots = resolved["slots"]
    ledger = ROOT / "docs/talk_claim_ledger_v7.md"
    review = ROOT / "docs/presentation/review-results.md"
    originals = {p: p.read_bytes() for p in (ledger, review)}
    claims = {
        "AW-B": "Heavy-tail questions / active inference testbed | measured intervention | "
        f"Mixture rho=exp(-1) passes the declared rule in ten memories; zsRE maximum {slots['awb.zsre.v5.maximum']} → {slots['awb.zsre.mixture.maximum']} nats; CounterFact {slots['awb.counterfact.v5.maximum']} → {slots['awb.counterfact.mixture.maximum']}; CF RET-GS change {slots['awb.counterfact.gs_change']} | "
        "Exposed realization0, five dependent orders/dataset, saved 300-edit memories; 245237 fixed-prefix positions | v5 and cap-off, development-selected wrapper; no eligible shrink/gate comparator | Smaller maximum and ES99 with retention inside two points in every cell | Per-token same-prefix bound only; no unchanged-greedy, total-loss or heavy-tail-family guarantee; CounterFact KL still above .001; DEC-078 intervention, not a recommended configuration | docs/additional_work/AW-B_report.md",
        "PC-random": "Predictive coding | measured partial control, closed DEC-079 | "
        f"Random immediate ES {slots['control.random.es']} after {slots['control.random.n']} items; stopped by resource rule | One zsRE realization/order; ten planned cells unstarted | Adjoint paired stream and first993 common prefix | Informative direction matters in this tested implementation | No complete random replication, general random-search impossibility, or PC-over-adjoint claim | docs/additional_work/PC-controls_report.md",
        "PC-budget": "Predictive coding | measured offered-budget control | Twelve cells completed; adjoint underspent the PC allowance and did not recover the eight-step retention gain | Three realizations/dataset; order100 | Additional acquisition updates with threshold stopping | Reports achieved efficacy and actual operations | Not realized compute matching; direction-versus-compute attribution remains unresolved; no separate ES99 readout | docs/additional_work/PC-matched-control_report.md",
    }
    lines = [
        line
        for line in originals[ledger].decode().splitlines()
        if not any(line.startswith(f"| {key} |") for key in claims)
    ]
    text = (
        "\n".join(lines)
        .replace("2026-09-29 evidence snapshot", "2026-10-01 evidence snapshot")
        .rstrip()
        + "\n"
    )
    text += "\n".join(f"| {key} | {value} |" for key, value in claims.items()) + "\n"
    awb = ROOT / "docs/additional_work/AW-B_report.md"
    nested = "\n".join(
        "#" + line if line.startswith("#") else line for line in awb.read_text().splitlines()
    )
    review_text = originals[review].decode().split("<!-- AW-B4 final -->")[0].rstrip()
    review_text += (
        "\n\n<!-- AW-B4 final -->\n\n"
        + nested
        + "\n\nSurvival figure: `assets/presentation-materials/figures/aw_b/evaluation-survival.png` (PDF/SVG beside it). DEC-078: an intervention beside the κ pilot, not a recommended cap configuration.\n"
    )
    check = Sources()
    check.check(resolved["sources_sha256"])
    if any(p.read_bytes() != b for p, b in originals.items()):
        raise ValueError("presentation files changed concurrently")
    ledger.write_text(text)
    review.write_text(review_text)
    exported = ROOT.parent / "assets/presentation-materials/review-data/results.md"
    exported.write_text(review_text)
    out = ROOT / "logs/additional_work/round55"
    out.mkdir(parents=True, exist_ok=True)
    (out / "presentation-evidence.json").write_text(
        json.dumps(
            dict(
                resolved,
                producer={str(Path(__file__).resolve()): sha(__file__)},
                outputs={str(p): sha(p) for p in (ledger, review, exported)},
            ),
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    publish()
