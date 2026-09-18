"""Read-only provenance inventory and synthetic classifier audit; no policy changes."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

from scripts import r1_49g_inference as inference
from scripts.r1_d10a_review import ROOT, write_new


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def inventory():
    paths = [
        ROOT / "docs/updated_plan9.md",
        ROOT / "docs/decisions.md",
        ROOT / "docs/tasks/R1-49f-lead-bindings.md",
        ROOT / "docs/tasks/R1-50b.md",
        ROOT / "docs/tasks/R1-24.md",
        *sorted((ROOT / "docs").glob("R1_stage4_protocol*.md")),
    ]
    rows = []
    for path in paths:
        text = path.read_text()
        excerpts = []
        for match in re.finditer(r"\S[^\n]*(?:\n(?!\n)[^\n]*)*", text):
            paragraph = match.group()
            if path.name == "decisions.md":
                selected = any(
                    f"| DEC-{n} " in paragraph for n in ("033", "040", "047", "057", "058", "063")
                )
                if selected:
                    # Decision tables are one paragraph: keep each exact selected row.
                    for offset, line in enumerate(paragraph.splitlines()):
                        if any(
                            line.startswith(f"| DEC-{n} ")
                            for n in ("033", "040", "047", "057", "058", "063")
                        ):
                            excerpts.append(
                                dict(
                                    line=text[: match.start()].count("\n") + offset + 1, quote=line
                                )
                            )
                continue
            if re.search(r"fidelity|\bKL\b|drift|incorporat", paragraph, re.I):
                excerpts.append(dict(line=text[: match.start()].count("\n") + 1, quote=paragraph))
        added = subprocess.run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--format=%H %aI %s",
                "--",
                str(path.relative_to(ROOT)),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        rows.append(dict(source=binding(path), introduction=added, excerpts=excerpts))
    for name in ("pc_cap_coding_agent_guide (1)", "pc_cap_joint_redesign_proposal (1)"):
        pdf = ROOT / "docs/more_input" / f"{name}.pdf"
        text_path = ROOT / "logs/r1_round32" / f"{name}.txt"
        excerpts = []
        for page, text in enumerate(text_path.read_text().split("\f"), 1):
            for paragraph in re.split(r"\n\s*\n", text):
                if re.search(r"fidelity|\bKL\b|drift", paragraph, re.I):
                    excerpts.append(dict(pdf_page=page, quote=paragraph))
        rows.append(dict(source=binding(pdf), extraction=binding(text_path), excerpts=excerpts))
    return dict(
        task="R1-49l",
        scope="exact local source excerpts, including all protocol versions",
        policy_changed=False,
        sources=rows,
        producer=binding(__file__),
    )


def classifier_rehearsal():
    # Reuse an independently declared complete synthetic 3-realization × 5-order fixture.
    from tests.revision_v1.test_r1_49g_analysis import synthetic_matrix

    matrix, loaded = synthetic_matrix()
    d2_path = ROOT / "manifests/revision_v1/run_matrix_v5_2_D_2.json"
    d2 = json.loads(d2_path.read_text())
    matrix.update(
        name=d2["name"],
        option="D",
        dataset_layouts=d2["dataset_layouts"],
        layout_sha256=d2["layout_sha256"],
        full_validation=d2["full_validation"],
        endpoint_contract_version=1,
    )
    matrix["axes"]["realizations_by_dataset"] = {d: [0, 1, 2] for d in inference.DATASETS}
    for cell in matrix["cells"]:
        cell["checkpoints"] = matrix["dataset_layouts"][cell["dataset"]]["checkpoints"]
        cell["full_validation"] = d2["full_validation"]
        cell["population"]["full_validation"] = d2["full_validation"]
        if cell["dataset"] == "mquake":
            cell["population"]["item_ids"] = cell["population"]["item_ids"][:300]
            cell["population"]["paraphrase_counts"] = cell["population"]["paraphrase_counts"][:300]
    results = {}
    for name, failed_condition in (
        ("all_admitted", None),
        ("one_primary_cell_failed_fidelity", "R1_learned_ff"),
        ("one_control_cell_failed_fidelity", "v0_stable"),
    ):
        observations = copy.deepcopy(loaded)
        if failed_condition:
            c = next(
                c
                for c in matrix["cells"]
                if c["dataset"] == "zsre" and c["condition"] == failed_condition
            )
            observations[c["cell_id"]]["scientific_admission"] = False
            observations[c["cell_id"]]["full_validation_fidelity_passes"] = False
        results[name] = inference.primary_contrasts(matrix, observations)
    return dict(
        task="R1-49l",
        synthetic=True,
        model_calls=0,
        gpu_seconds=0,
        purpose="exercise existing admission/classifier wiring, not propose a new rule",
        qualification="complete synthetic primary metrics; cell admission change supplied as an input",
        matrix=binding(d2_path),
        implementation=binding(inference.__file__),
        producer=binding(__file__),
        scenarios=results,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "logs"):
        parser.error("new repository log directory required")
    args.output.mkdir(parents=True, exist_ok=True)
    print(
        json.dumps(
            {
                "provenance": write_new(args.output / "fidelity-source-quotes.json", inventory()),
                "classifier": write_new(
                    args.output / "fidelity-classifier-rehearsal.json", classifier_rehearsal()
                ),
            },
            indent=2,
        )
    )
