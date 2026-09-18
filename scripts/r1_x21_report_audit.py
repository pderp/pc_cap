"""Read-only protocol/report coverage audit; records gaps without changing inference."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_49n_normative_closure as normative
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_75_analysis_stage4_v1 as analysis

ROOT = normative.ROOT
ANALYSIS = ROOT / "logs/r1_round39/d14-complete-final/analysis.json"
DATA = ROOT / "logs/r1_round39/report-rehearsal-final/report-data.json"


def audit():
    closure = normative.closure()
    raw = json.loads(ANALYSIS.read_text())
    rendered = json.loads(DATA.read_text())
    if rendered["analysis"] != full.ref(ANALYSIS):
        raise ValueError("report not bound to inspected analysis")
    sources = dict(closure["bindings_sha256"])
    for path in (
        ANALYSIS,
        DATA,
        ROOT / "docs/R1_stage4_report_skeleton.md",
        ROOT / "scripts/r1_d14_report.py",
        ROOT / "scripts/r1_d14_figures.py",
        ROOT / "scripts/r1_75_analysis_stage4_v1.py",
        ROOT / "scripts/r1_49g_analyze.py",
        ROOT / "scripts/r1_d9_receipts.py",
        ROOT / "scripts/r1_77b_sealed_backend.py",
        ROOT / "docs/R1_U03_interpretation_memo.md",
        __file__,
    ):
        sources[str(Path(path).resolve())] = full.sha(path)
    for path, sha in rendered["source_bindings_sha256"].items():
        if full.sha(path) != sha:
            raise ValueError("rehearsal source changed")
    tables = rendered["tables"]
    rows = []

    def check(identity, description, table, pointers, norm, status="covered", gap=None):
        rows.append(
            dict(
                id=identity,
                requirement=description,
                table=table,
                rows=len(tables.get(table, [])) if table else None,
                analysis_pointers=pointers,
                normative=norm,
                status=status,
                edit_request=gap,
            )
        )

    check(
        "T1",
        "D4 declared blocks and completed-block inventory",
        "blocks",
        ["/blocks", "/complete_blocks"],
        "D4 execution blocks; D1 DEC052",
    )
    check(
        "T2",
        "Planned/missing/invalid cells and independent endpoint completeness",
        "cell_inventory",
        ["/cells", "/incomplete_cells"],
        "D1 DEC052",
        "partial",
        "X21-G4",
    )
    check(
        "T3",
        "21 dataset contrasts ×3 metrics, both intervals, three realization values, classifier, pairing",
        "primary",
        ["/contrasts/*/metrics/*", "/contrasts/*/classification", "/primary_family"],
        "v5.1 §5.3; D4 U12",
    )
    check(
        "T4",
        "11 per-cell descriptive secondary benchmarks, counts/Wilson and availability",
        "secondary_cells",
        ["/secondary_benchmarks/cells/*/benchmarks"],
        "v5.1 §5.1",
        "covered_with_explicit_unavailability",
        "X21-G7",
    )
    check(
        "T5",
        "Equal-weight dataset macros, paired equivalence intervals and failed-cell inventory",
        "secondary_macros",
        ["/secondary_benchmarks/macros"],
        "v5.1 §5.1/5.3",
    )
    check(
        "T5a",
        "Near-family independent denominators and bounded/terminated diagnostics",
        "near_miss",
        ["/near_miss_family/cells"],
        "D1 DEC061/062",
    )
    check(
        "T5b",
        "Actual checkpoint ES/RET-ES/RET-GS/LS values, counts and cell coordinates",
        "trajectories",
        ["/cells/*/checkpoints/*/primary"],
        "D4 U08",
    )
    check(
        "T5c",
        "Endpoint counters, truncation and unsupported/unavailable observations",
        "endpoint_observations",
        ["/cells/*/checkpoints/*/secondary"],
        "v5.1 §5.1",
        "partial",
        "X21-G6",
    )
    check(
        "T6",
        "MQuAKE actual300 occupancy, outside fires, Wilson and change from100; no1000 threshold",
        "mquake300",
        ["/secondary_benchmarks/cells/*/actual_occupancy_descriptive"],
        "D1 actual occupancy; D4 U08/U12",
    )
    check(
        "T6a",
        "Five calibration-determined omitted conditions/75 coordinates; never measured zeros",
        "omissions",
        ["/prospectively_omitted_cells"],
        "D4 scope",
    )
    check(
        "T7",
        "Both cap references and KL/NLL labels, joint numeric flag, no primary veto",
        "fidelity",
        ["/cells/*/cap_fidelity_benchmark"],
        "D3 DEC064",
        "partial",
        "X21-G2",
    )
    check(
        "T8",
        "Watch entries/creep alerts, exact-matrix/global scope, no implicit notification acknowledgement",
        "watch_summary",
        ["watch:/entries", "watch:/alerts", "watch:/observations"],
        "DEC064a in decisions; D3 fidelity",
    )
    check(
        "T9",
        "Full/sample signed and positive means, ES95/99, exceedances, exp(mean), maximum/location and zero masses",
        "tails",
        [
            "/cells/*/checkpoints/*/secondary/full_validation/references/*/{loss,kl}",
            "/cells/*/checkpoints/*/secondary/sampled_drift/references/*",
        ],
        "v5.1 §5.2; D2/D3 tails",
        "partial",
        "X21-G1",
    )
    check(
        "T10",
        "Near-zero loss fraction, half mass/top shares/Gini, window KL summaries and undefined zero-total shares",
        "concentration",
        ["/cells/*/checkpoints/*/secondary/full_validation/concentration/references"],
        "D3 HT7",
    )
    check(
        "U03",
        "Qualified historical LM/literal continuation controls, no exact-v5-compute claim",
        None,
        [],
        "D4 final paragraph; U03 memo",
        "partial",
        "X21-G5",
    )
    check(
        "Secondary-extension",
        "Historical-v2 secondary paired package contrast at each declared checkpoint",
        None,
        ["/historical_pointwise_contrasts/*[contrast.role=secondary]"],
        "v5.1 §5.3; D4 optional extension",
        "missing_formatter_output",
        "X21-G3",
    )
    check(
        "Composition",
        "Predetermined dependency-closed composition, fixed planned cases/questions, conflicts/unavailability",
        None,
        ["raw checkpoint:/endpoints/composition; absent from installed analysis JSON"],
        "v5.1 §5.1; D1 population",
        "missing_analysis_output",
        "X21-G6",
    )
    check(
        "Accounting",
        "Known charged process costs, unknown records, retry exhaustion/host failure and block reconciliation",
        None,
        ["D11/D13 reporting outputs; not joined by scientific formatter"],
        "D1 DEC052; D4 U16",
        "missing_report_integration",
        "X21-G4",
    )
    figures = []
    for name, table in rendered["figures"].items():
        figures.append(
            dict(
                name=name,
                table=table,
                rows=len(tables.get(table, [])),
                status="descriptive_visualization_covered",
                qualification={
                    "primary-intervals": "63 slots; unavailable MQuAKE explicit; existing adjusted intervals only",
                    "checkpoint-trajectories": "means of available cell values, not an uncertainty interval or independent-orders analysis",
                    "disposition": "artifact counts only; not full cost/retry accounting (G4)",
                    "cap-fidelity": "two references and threshold lines; explicit joint flag still needed in table (G2)",
                    "full-validation-tails": "per-cell summaries, not pooled tokens; omitted tail fields requested for table (G1)",
                    "watch-sequence": "KL sequence only; NLL remains in watch tables; observation index is not elapsed time",
                }[name],
            )
        )
    required_family = raw["primary_family"]["family_size"]
    mq = [r for r in tables["primary"] if r["dataset"] == "mquake"]
    assert required_family == 63 and len(tables["primary"]) == 63
    assert len(mq) == 21 and all(r["estimate"] is None for r in mq)
    assert len(tables["omissions"]) == 75 and len(tables["cell_inventory"]) == 330
    extension = [
        r for r in raw["historical_pointwise_contrasts"] if r["contrast"]["role"] == "secondary"
    ]
    assert len(extension) == 8
    assert not any(
        b.get("pointer", "").startswith("/historical_pointwise_contrasts")
        for items in rendered["bindings"].values()
        for row in items
        for b in row.values()
    )
    fields = set(tables["tails"][0])
    assert (
        not {
            "exp_mean_signed",
            "maximum_location",
            "maximum_position",
            "atom_zero_positive",
            "atom_zero_signed",
            "zero_positive_n",
        }
        & fields
    )
    assert "passes" not in tables["fidelity"][0]
    # A valid-shaped synthetic composition section is silently omitted by the
    # current checkpoint consumer; no actual protected payload is opened.
    matrix = json.loads(Path(raw["matrix_file"]["path"]).read_text())
    cell = next(c for c in analysis.all_cells(matrix) if c["dataset"] == "mquake")
    checkpoint = Path(cell["result_dir"]) / "attempt-0000/checkpoint-300.json"
    original = json.loads(checkpoint.read_text())
    augmented = copy.deepcopy(original)
    composition = dict(
        schema_version=1,
        endpoint="composition_direct",
        rows=[
            dict(
                composition_id="SYNTHETIC-X21-COMPOSITION",
                status="ok",
                evaluable=True,
                dependency_ids=cell["population"]["item_ids"][:2],
                composition_success=True,
                paraphrase_successes=3,
                paraphrases_expected=3,
                queries=[dict(post_edit_exact=True)] * 3,
            )
        ],
        summary=dict(planned=1, available_rows=1, evaluable=1, scored=1, successes=1),
    )
    augmented["endpoints"]["composition"] = composition
    population = copy.deepcopy(cell["population"])
    population["endpoints"]["composition"] = ["SYNTHETIC-X21-COMPOSITION"]
    before = analysis.summarize_checkpoint(original, population, 300, 300)
    after = analysis.summarize_checkpoint(augmented, population, 300, 300)
    assert before == after and "composition" not in after["secondary"]
    sources[str(checkpoint)] = full.sha(checkpoint)
    memo = str(ROOT / "docs/R1_U03_interpretation_memo.md")
    for path, sha in sources.items():
        if full.sha(path) != sha:
            raise ValueError("audit evidence changed")
    return dict(
        task="R1-X21",
        status="review_complete_gaps_require_owner_edits",
        normative_files=len(closure["bindings_sha256"]),
        normative_closure=closure,
        obligations=rows,
        figures=figures,
        sources_sha256=sources,
        checks=dict(
            primary_rows=63,
            mquake_unavailable_rows=21,
            omissions=75,
            declared_cells=330,
            secondary_extension_source_contrasts=len(extension),
            secondary_extension_metric_rows=24,
            secondary_extension_not_rendered=True,
            composition_synthetic_section_ignored=True,
            absent_full_tail_fields=[
                "exp_mean_signed",
                "exp_mean_signed_overflow",
                "maximum_location",
                "maximum_signed",
                "maximum_tie_count",
                "atom_zero_positive",
                "atom_zero_signed",
            ],
            absent_sample_tail_fields=[
                "maximum_position",
                "zero_positive_n",
                "exp(mean_signed_nats) derived with overflow handling",
            ],
            joint_cap_pass_not_rendered=True,
            U03_memo_hash_bound_by_formatter=memo in rendered["source_bindings_sha256"],
        ),
        existing_files_changed=False,
        gpu_seconds=0,
        real_payloads_opened=0,
        launch_authorized=False,
    )


def run(output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "logs") or output.exists():
        raise ValueError("new output path in repo logs required")
    result = audit()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as f:
        json.dump(result, f, indent=2)
    return dict(
        report=full.ref(output),
        obligations=len(result["obligations"]),
        figures=len(result["figures"]),
        checks=result["checks"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output), indent=2))
