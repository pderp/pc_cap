"""CPU adapters for REP-1; output redirections are process-local and recorded.

Legacy producers keep their original files/hashes. Only declared output paths
and dependencies are redirected. A write guard rejects publication outside the
fresh report/figure roots. This guard is an accident check, not a security sandbox.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import shutil
import site
import sys
from pathlib import Path

from aw.refresh_reports import DEPENDENCIES, ROOT, save, sha


class RedirectRoot:
    def __init__(self, mapping):
        self.mapping = {str(k): Path(v) for k, v in mapping.items()}
        self.parent = ROOT.parent

    def __truediv__(self, name):
        return self.mapping.get(str(name), ROOT / name)

    def __fspath__(self):
        return str(ROOT)


def guard_writes(roots):
    roots = tuple(Path(p).resolve() for p in roots)

    def allowed(path):
        if isinstance(path, int):
            return  # inherited stdout/stderr descriptors
        p = Path(os.fsdecode(path)).resolve()
        if not any(p.is_relative_to(root) for root in roots):
            raise PermissionError(f"refresh refuses a write outside its fresh outputs: {p}")

    def audit(event, args):
        if event == "open":
            _, mode, flags = args
            if (mode and any(c in mode for c in "wax+")) or flags & (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            ):
                allowed(args[0])
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
            allowed(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            allowed(args[0])
            allowed(args[1])

    sys.addaudithook(audit)


def cli(module, *arguments):
    old = sys.argv
    try:
        sys.argv = [module.__name__, *map(str, arguments)]
        module.main()
    finally:
        sys.argv = old


def plotting():
    # Preserve the project NumPy first, then use the existing plotting env;
    # no installation or network access and no alternate JAX interpreter.
    import numpy  # noqa: F401

    site.addsitedir(
        str(ROOT.parent / "assets/envs/status-paper-20260911/lib/python3.12/site-packages")
    )


def report_paths(out):
    return {
        "PC-v0": out / "pc-default/v0/report.json",
        "PC-v0 harm": out / "pc-default/v0/harm/report.json",
        "PC-v1": out / "pc-default/v1/report.json",
        "PC-v1 harm": out / "pc-default/v1/harm/report.json",
        "depth/random controls": out / "pc-controls/report.json",
        "matched control": out / "pc-matched/report.json",
        "AW-B": out / "aw-b/report.json",
        "PC-reader": out / "pc-reader/report.json",
        "Option R": out / "option-r/report.json",
        "AW-L": out / "aw-l/report.json",
        "HT-17": out / "ht17/report.json",
    }


def reader_number_line(report):
    cells = {
        (c["rule"], c["seed"], c["dataset"]) for c in report["cells"] if c["status"] == "complete"
    }
    paired = [
        seed
        for seed in range(3)
        if all(
            (rule, seed, dataset) in cells
            for rule in ("bp", "epc")
            for dataset in ("zsre", "counterfact")
        )
    ]
    ratios = [
        r["epc_over_bp"] for r in report["training_cost_ratios"] if r["epc_over_bp"] is not None
    ]
    cost = (
        (f"{min(ratios):.1f}–{max(ratios):.1f}×" if len(ratios) > 1 else f"{ratios[0]:.1f}×")
        if ratios
        else "unavailable"
    )
    scope = (
        "No three-seed finding yet."
        if len(paired) < 3
        else "All three seeds paired; interpretation requires review."
    )
    return f"- **PC-reader:** **{report['completed_evaluations']}/{report['planned_evaluations']}** evaluations available; fully paired seeds: {', '.join(map(str, paired)) or 'none'}. Completed training ePC/BP process-time ratios **{cost}**; 37× was a forecast. {scope} [P]"


def reader_number_sheet(text, report, mapping):
    text, count = re.subn(r"(?m)^- \*\*PC-reader:\*\*.*$", reader_number_line(report), text)
    if count != 1:
        raise ValueError("expected exactly one reader number-sheet row")
    text = text.replace(
        "# Numbers to say — October 1 evidence snapshot",
        "# Numbers to say — regenerated evidence snapshot",
    )
    text = text.replace(
        "`training_cost_ratios[seed=0]`", "`training_cost_ratios` for completed trainings"
    )
    for old, new in mapping.items():
        text = text.replace(f"`{old}`", f"`{new}`")
    return text


def pc_default(out):
    from aw import pc_complete_report as module

    child = out / "pc-default"
    child.mkdir()
    mapping = {
        "logs/additional_work/PC-v0/original-generator-replay-20260928": child / "original-replay",
        "logs/additional_work/PC-v0/original-generator-replay-20260928.md": child
        / "original-replay.md",
        "docs/additional_work/PC-v0_report.md": out / "documents/PC-v0_report.md",
        "docs/additional_work/PC-v1_report.md": out / "documents/PC-v1_report.md",
    }
    module.ROOT = RedirectRoot(mapping)
    module.OUT0, module.OUT1 = child / "v0", child / "v1"
    module.main()
    save(child / "output-redirections.json", {k: str(v) for k, v in mapping.items()})


def pc_settings(out):
    from aw import pc_complete_report as native
    from aw.reporting_sources import Sources

    dest = out / "pc-settings"
    dest.mkdir()
    all_rows, costs, bindings = [], [], {}
    for label in ("k32", "lr0.05", "lr0.2"):
        native.V1 = ROOT / f"results/additional_work/PC-v1/replication-4-{label}-20260929"
        sources = Sources()
        r = native.fixed_report(sources)  # reruns both old/current metric calculations
        plan = native.read(native.V1 / "plan.json", sources)
        # The legacy helper's eight-step label is specific to its default study.
        # Read the treatment from each variant's bound plan, never its directory name.
        r["treatment"] = plan["credit"]
        h, cost = native.validate_harm(
            ROOT / f"results/additional_work/PC-v1/harm/pc-v1-4-{label}-20260929", sources, 1
        )
        sources.verify_unchanged()
        r["sources_sha256"] = dict(sources.bindings)
        r["harm"] = h
        r["harm_cost"] = cost
        save(dest / f"{label}.json", r)
        bindings.update(sources.bindings)
        costs.append(
            dict(
                setting=label,
                acquisition_process_seconds=sum(
                    c["process"]["elapsed_process_seconds"] for c in r["cells"]
                ),
                harm_process_seconds=cost["elapsed_process_seconds"],
            )
        )
        for c in r["cells"]:
            all_rows.append(
                [
                    label,
                    c["dataset"],
                    c["arm"],
                    *[
                        c["checkpoints"]["300"][k]["value"]
                        for k in ("ES", "RET-ES", "RET-GS", "LS", "near_miss", "revision")
                    ],
                ]
            )
    save(
        dest / "report.json",
        dict(
            task="PC-settings",
            status="complete",
            costs=costs,
            sources_sha256=bindings,
            gpu_seconds=0,
        ),
    )
    (out / "documents/PC-settings_report.md").write_text(
        "# Fixed-reader credit-setting variants\n\nTwelve exposed cells; original/current endpoint scoring and full-vector harm reproduce. No independent realization uncertainty or equivalence claim. Process and harm costs remain separate.\n\n"
        + native.generator.table(
            ["Setting", "Dataset", "Arm", "ES", "RET-ES", "RET-GS", "LS", "Near miss", "Revision"],
            all_rows,
        )
        + "\nComplete harm statistics, treatment records and costs are in the three JSON files.\n"
    )


def figures(out, assets):
    plotting()
    from scripts import ht9_presentation_figures as kappa

    from aw import (
        aw_b_tail_figure,
        ht17_slides,
        pc_depth_figure,
        presentation_retention,
        tail_class_plot,
        upper_layer_figure,
    )
    from aw import pc_result_figures as pc

    # The legacy function appends a historical report directory to the study root.
    class FigureRoot(RedirectRoot):
        def __truediv__(self, name):
            if str(name) in ("logs/additional_work/PC-v0", "logs/additional_work/PC-v1"):
                return StudyPath(
                    out / ("pc-default/v0" if str(name).endswith("0") else "pc-default/v1")
                )
            return super().__truediv__(name)

    class StudyPath:
        def __init__(self, target):
            self.target = target

        def __truediv__(self, name):
            if name not in ("report-60-20260927", "report-4-20260927"):
                raise ValueError("unexpected legacy figure suffix")
            return self.target

    pc.ROOT, pc.BASE = FigureRoot({}), assets / "pc"
    pc.main()
    pc_depth_figure.draw(out / "pc-controls/report.json", assets / "pc-controls")
    aw_b_tail_figure.draw(out / "aw-b/report.json", assets / "aw-b")
    presentation_retention.render(assets / "retention")
    cli(tail_class_plot, "--report", out / "ht17/report.json", "--out", assets / "ht17")
    cli(ht17_slides, "--report", out / "ht17/report.json", "--out", assets / "ht17-slide")
    upper_layer_figure.render(out / "aw-l/report.json", assets / "upper-layer")
    kappa.ROOT = RedirectRoot(
        {
            "logs": assets,
            "logs/r1_round22/ht3e-independent-review-v2.json": out / "kappa/report.json",
        }
    )
    kappa.render(assets / "kappa")


def deck(out, assets):
    from aw import presentation_pc as pc
    from aw import presentation_slides as slides
    from aw import presentation_timing as timing
    from aw import rehearsal_pack as pack

    source = out / "documents/deck_v3"
    shutil.copytree(ROOT / "docs/presentation/deck_v3", source)
    paths = report_paths(out)
    register = json.loads((source / "pc-result-sources.json").read_text())
    for key, name in (
        ("v0_report", "PC-v0"),
        ("v0_harm", "PC-v0 harm"),
        ("v1_harm", "PC-v1 harm"),
        ("depth_controls", "depth/random controls"),
        ("aw_b", "AW-B"),
    ):
        register["sources"][key]["path"] = str(paths[name])
    save(source / "pc-result-sources.json", register)
    original_resolve = pc.resolve
    pc.resolve = lambda: original_resolve(source / "pc-result-sources.json")
    timing.SOURCE = slides.SOURCE = source
    specs = json.loads((source / "diagram-specs.json").read_text())
    replacements = {
        "05": (assets / "retention/paraphrase-retention.png", assets / "retention/manifest.json"),
        "06": (
            assets / "ht17-slide/frequency-severity-stage4.png",
            assets / "ht17-slide/manifest.json",
        ),
        "08": (
            assets / "aw-b/evaluation-survival.png",
            assets / "aw-b/evaluation-survival-manifest.json",
        ),
        "09": (
            assets / "pc-controls/depth-retention-harm-cost.png",
            assets / "pc-controls/depth-retention-harm-cost-manifest.json",
        ),
    }
    for slide in specs["slides"]:
        if slide["number"] in replacements:
            figure, manifest = replacements[slide["number"]]
            slide.update(figure=str(figure), figure_manifest=str(manifest))
    save(source / "diagram-specs.json", specs)
    mapping = {
        "logs/additional_work/PRES-8": out / "timing",
        "logs/additional_work/HT-17/snapshot-20261004-complete/report.json": paths["HT-17"],
        "logs/additional_work/PC-reader/report-round63-final/report.json": paths["PC-reader"],
        "logs/additional_work/R/report-round63-final/report.json": paths["Option R"],
        "logs/additional_work/AW-L/report-round63-final/report.json": paths["AW-L"],
        "docs/presentation/numbers_to_say.md": out / "documents/numbers_to_say.md",
        "docs/presentation/rehearsal.md": out / "documents/rehearsal.md",
        "docs/R1_stage4_report.md": out / "documents/R1_stage4_report.md",
        "docs/additional_work/AW-B_report.md": out / "documents/AW-B_report.md",
    }
    for name in ("PC-reader", "R", "AW-L"):
        mapping[f"docs/additional_work/{name}_report.md"] = out / f"documents/{name}_report.md"
    # Only these two parent-relative figure paths are hardcoded by the legacy pack.
    parent_map = {
        "assets/presentation-materials/figures/upper_layer/round63-complete/upper-layer-tradeoffs.png": assets
        / "upper-layer/upper-layer-tradeoffs.png",
        "assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.png": assets
        / "ht17/survival_thresholds.png",
        "assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.pdf": assets
        / "ht17/survival_thresholds.pdf",
        "assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png": assets
        / "pc-controls/depth-retention-harm-cost.png",
    }

    class Parent:
        def __truediv__(self, name):
            return parent_map.get(str(name), ROOT.parent / name)

    redirect = RedirectRoot(mapping)
    redirect.parent = Parent()
    # is_relative_to needs an ordinary base path, which Parent returns for the root.
    slides.ROOT = pack.ROOT = redirect
    mapping["logs/r1_round37/presentation-figures-v2/kappa-tradeoff.png"] = (
        assets / "kappa/kappa-tradeoff.png"
    )
    redirect.mapping.update(mapping)
    pack.build(assets / "deck")
    reader = json.loads(paths["PC-reader"].read_text())
    sheet = out / "documents/numbers_to_say.md"
    text = reader_number_sheet(sheet.read_text(), reader, mapping)
    sheet.write_text(text)
    (assets / "deck/numbers-to-say.md").write_text(text)
    manifest_path = assets / "deck/rehearsal-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sources_sha256"][str(Path(__file__).resolve())] = sha(__file__)
    manifest["exports"][str(assets / "deck/numbers-to-say.md")] = sha(
        assets / "deck/numbers-to-say.md"
    )
    save(manifest_path, manifest)
    pack_record = out / "timing/pack.json"
    recorded = json.loads(pack_record.read_text())
    recorded["manifest_sha256"] = sha(manifest_path)
    save(pack_record, recorded)
    save(
        out / "presentation-review-required.json",
        dict(
            note="Numerical slot sources/figures refreshed; literal author-written seed/coverage/interpretation text is copied, not automatically endorsed. Review before publication. Canonical files are unchanged.",
            reader_completed=json.loads(paths["PC-reader"].read_text())["completed_evaluations"],
            source_deck=str(ROOT / "docs/presentation/deck_v3"),
        ),
    )


def run(step, out, assets):
    if os.environ.get("JAX_PLATFORMS") != "cpu" or os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("explicit CPU-only environment required")
    receipt = json.loads((out / "refresh.json").read_text())
    if (
        receipt.get("status") != "running"
        or Path(receipt["output"]) != out
        or Path(receipt["assets"]) != assets
        or not receipt["steps"]
        or receipt["steps"][-1].get("step") != step
        or receipt["steps"][-1].get("status") != "running"
    ):
        raise ValueError("worker requires its orchestrator's active fresh-output receipt")
    import pccap  # noqa: F401 # before any model-related reporting imports

    guard_writes((out, assets))
    target = out / step
    if step == "pc-default":
        pc_default(out)
    elif step == "pc-settings":
        pc_settings(out)
    elif step == "ht15":
        from aw.tail_cells import build

        build(ROOT / "logs/R1/final_queue", target)
    elif step == "stage4":
        from aw import stage4_assembly as m

        m.SOURCE = dict(m.SOURCE, F=str(out / "ht15/cell_tails.json"))
        m.build(target, out / "documents/R1_stage4_report.md")
    elif step == "pc-matched":
        from aw.pc_control_report import build

        build(
            ROOT / "results/additional_work/PC-v0/matched-control/run-20260929",
            out / "documents/PC-matched-control_report.md",
            target,
        )
    elif step == "pc-controls":
        from aw import pc_credit_control_review as controls
        from aw import pc_depth_report as m

        m.OUT0 = out / "pc-default/v0"
        controls.MATCHED = out / "pc-matched/report.json"
        m.build(target, out / "documents/PC-controls_report.md")
    elif step == "aw-b":
        from aw.aw_b_report import build

        build(final=True, output=target, document=out / "documents/AW-B_report.md")
    elif step == "kappa":
        target.mkdir()
        cli(
            importlib.import_module("scripts.ht3e_independent_review"),
            "--output",
            target / "report.json",
        )
    elif step == "ht13":
        plotting()
        cli(importlib.import_module("aw.tail_figures"), "--out", assets / "ht13")
    elif step == "ht17":
        cli(
            importlib.import_module("aw.tail_class"),
            "--output",
            target,
            "--bootstrap",
            "200",
            "--secondary",
        )
    elif step == "pc-reader":
        from aw import pc_reader_report as reader
        from aw import reader_results as rr

        r = reader.build(
            ROOT / "results/additional_work/PC-reader",
            tail=out / "ht17/report.json",
            history=reader.DEFAULT_HISTORY,
        )
        text = reader.markdown(r, target).replace(
            "Its current snapshot already covers the eight completed evaluations; no duplicate fit was needed for this report.",
            f"This refresh has {r['completed_evaluations']}/{r['planned_evaluations']} completed evaluations; matched HT-17 rows: {len(r['tail_rows'])}. Tail coverage exceptions are retained in the JSON.",
        )
        r["sources_sha256"][str(Path(__file__).resolve())] = sha(__file__)
        rr.write_outputs(r, text, target, out / "documents/PC-reader_report.md")
    elif step == "option-r":
        cli(
            importlib.import_module("aw.r_report"),
            "--output",
            target,
            "--document",
            out / "documents/R_report.md",
        )
    elif step == "aw-l":
        cli(
            importlib.import_module("aw.aw_l_report"),
            "--output",
            target,
            "--document",
            out / "documents/AW-L_report.md",
        )
    elif step == "figures":
        figures(out, assets)
    elif step == "deck":
        deck(out, assets)
    elif step == "audit":
        from aw import presentation_pc as pc
        from aw import script_numbers_check as numbers
        from aw import supplemental_audit

        audit = supplemental_audit.run(
            target / "X25", {k: str(v) for k, v in report_paths(out).items()}, assets / "deck"
        )
        if audit["status"] != "PASS":
            raise ValueError("X25 discrepancy; inspect staged audit")
        numbers.DECK = out / "documents/deck_v3"
        numbers.SHEET = out / "documents/numbers_to_say.md"
        resolve = pc.resolve
        pc.resolve = lambda: resolve(numbers.DECK / "pc-result-sources.json")
        numbers.run(target / "X26", assets / "deck")
    else:
        raise ValueError(step)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--step", choices=tuple(DEPENDENCIES), required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--assets", type=Path, required=True)
    a = p.parse_args()
    run(a.step, a.output.resolve(), a.assets.resolve())
