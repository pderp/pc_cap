"""R1-75: identity-bound cell-directory analysis, without models or sealed payloads.

Kept outside src/pccap while owner profiling uses the installed tree identity.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from scripts import ht7_concentration as ht7
from scripts import r1_49m_fidelity_policy as fidelity_policy
from scripts import r1_63l_full_validation_contract as full_contract
from scripts.ht_audit_existing import tail_sum
from scripts.r1_74_rescore import preservation_flags, preservation_summary

from pccap.revision_v1.analysis import (
    MARGINS,
    classify,
    digest,
    fraction,
    measure,
    ordered_rows,
    paired_metric,
)

ROOT = Path(__file__).resolve().parents[1]
COORDS = ("condition", "dataset", "realization", "order")
METRICS = ("ES", "RET-ES", "RET-GS", "LS")


def coordinate(cell):
    return tuple(cell[k] for k in COORDS)


def coordinate_id(cell):
    return digest({"schema": "stage4-cell-coordinate-v1", **{k: cell[k] for k in COORDS}})[:24]


def all_cells(matrix):
    return [*matrix["cells"], *matrix.get("extension", {}).get("cells", [])]


class Files:
    def __init__(self):
        self.sources = {}

    def read(self, path):
        path = Path(path).resolve()
        if (
            not path.is_relative_to(ROOT / "results")
            and not path.is_relative_to(ROOT / "manifests")
            and not path.is_relative_to(ROOT / "docs/tasks")
        ):
            raise PermissionError("analysis inputs must be repo cell reports or declared matrices")
        if not path.is_file():
            return None
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        if str(path) in self.sources and self.sources[str(path)] != h:
            raise ValueError("input changed across reads")
        self.sources[str(path)] = h
        return json.loads(raw)

    def verify(self):
        for path, h in self.sources.items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest() != h:
                raise ValueError("input changed during analysis: " + path)


def wilson(k, n, z=1.959963984540054):
    if type(k) is not int or type(n) is not int or n < 0 or not 0 <= k <= n:
        raise ValueError("binomial count/denominator required")
    if not n:
        return None
    center = (k / n + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt((k / n) * (1 - k / n) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {
        "lower": max(0.0, center - half),
        "upper": min(1.0, center + half),
        "confidence": 0.95,
        "interpretation": "descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference",
    }


def scalar_rows(rows, expected, field):
    byid = ordered_rows(rows, expected, "item_id")
    values = []
    statuses = Counter()
    for identity in expected:
        row = byid.get(identity)
        status = row.get("status", "unavailable") if row else "missing"
        statuses[status] += 1
        value = row.get(field) if row and status == "ok" else None
        if field == "false_fire" and row and row.get("firing_status") != "ok":
            value = None
        values.append(fraction(value))
    if not expected:
        return {
            "planned": 0,
            "scored": 0,
            "numerator": 0,
            "value": None,
            "evaluated_value": None,
            "status": "not_applicable",
        }
    return measure(values, len(expected), statuses)


def preservation_section(section, expected, query_key):
    rows = copy.deepcopy(section.get("rows", []) if section else [])
    ordered_rows(rows, expected, "item_id")
    for row in rows:
        row.update(
            preservation_flags(
                row.get("reference"), row.get(query_key), status=row.get("status", "unavailable")
            )
        )
    return (
        preservation_summary(rows, expected),
        scalar_rows(rows, expected, "preserved"),
        scalar_rows(rows, expected, "preserved_terminated"),
    )


def drift_summary(section, expected):
    if not section:
        return {
            "status": "not_run",
            "planned_positions": expected.get("expected_positions"),
            "scored_positions": 0,
        }
    rows = section.get("rows", [])
    planned = expected.get("expected_positions", section.get("expected_positions"))
    if type(planned) is not int or planned < 1:
        raise ValueError("declared positive drift denominator required")
    ids = [r["item_id"] for r in rows]
    if len(ids) != len(set(ids)) or len(rows) > planned:
        raise ValueError("duplicate/excess drift positions")
    if expected.get("position_ids") is not None and ids != expected["position_ids"]:
        raise ValueError("drift position inventory/order mismatch")
    if expected.get("source_sha256") and section.get("source_sha256") != expected["source_sha256"]:
        raise ValueError("drift source changed")
    result = {
        "status": "complete" if len(rows) == planned else "incomplete",
        "planned_positions": planned,
        "scored_positions": len(rows),
        "source_sha256": section.get("source_sha256"),
        "references": {},
    }
    for reference in ("original", "capoff"):
        values = [float(r["cap"]) - float(r[reference]) for r in rows]
        if any(not math.isfinite(x) for x in values):
            raise ValueError("nonfinite drift observation")
        if len(values) != planned:
            result["references"][reference] = None
            continue
        positive = [max(0.0, x) for x in values]
        maximum = max(positive)
        result["references"][reference] = {
            "mean_signed_nats": math.fsum(values) / planned,
            "mean_positive_nats": math.fsum(positive) / planned,
            "max_positive_nats": maximum,
            "maximum_position": ids[positive.index(maximum)],
            "count_above_0_1_nats": sum(x > 0.1 for x in values),
            "exceedances_nats": {str(x): sum(v > x for v in values) for x in (0.01, 0.1, 1.0)},
            "ES95_positive_nats": tail_sum(positive, 0.05) / (0.05 * planned),
            "ES99_positive_nats": tail_sum(positive, 0.01) / (0.01 * planned),
            "definition": "fractional empirical top1% mean of positive NLL harm; denominator .01*N",
            "zero_positive_n": sum(x == 0 for x in positive),
        }
    return result


def summarize_checkpoint(report, population, n, final):
    if population is None:
        return {"status": "population_unbound", "primary": {}, "secondary": {}}
    expected = population["item_ids"][:n]
    if len(expected) != n:
        raise ValueError("checkpoint outside declared edit population")
    for rows in (report.get("history", []), report.get("retention", {}).get("rows", [])):
        ordered_rows(rows, expected, "item_id")
        for row in rows:
            if (
                row.get("status") == "ok"
                and row.get("paraphrase_n")
                != population["paraphrase_counts"][population["item_ids"].index(row["item_id"])]
            ):
                raise ValueError("paraphrase denominator mismatch")
    eps = population["endpoints"]
    ls, bounded, terminated = preservation_section(report.get("locality"), eps["locality"], "query")
    primary = {
        "ES": scalar_rows(report.get("history", []), expected, "es"),
        "RET-ES": scalar_rows(report.get("retention", {}).get("rows", []), expected, "es"),
        "RET-GS": scalar_rows(report.get("retention", {}).get("rows", []), expected, "gs"),
        "LS": bounded,
    }
    unseen = scalar_rows(report.get("unseen", {}).get("rows", []), eps["unseen"], "false_fire")
    unseen["wilson_evaluated"] = wilson(int(unseen["numerator"]), unseen["scored"])
    unseen["wilson_full_inventory"] = (
        unseen["wilson_evaluated"] if unseen["status"] == "complete" else None
    )
    secondary = {
        "LS_terminated": terminated,
        "locality": ls,
        "unseen_false_fire": unseen,
        "unseen_answer_changed": scalar_rows(
            report.get("unseen", {}).get("rows", []), eps["unseen"], "answer_changed"
        ),
    }
    if n == final:
        near, near_b, near_t = preservation_section(
            report.get("endpoints", {}).get("near_miss"), eps["near_miss"], "neighbour_query"
        )
        revision = report.get("endpoints", {}).get("revision", {}).get("rows", [])
        secondary.update(
            near_miss=near,
            near_miss_bounded=near_b,
            near_miss_terminated=near_t,
            revision_latest=scalar_rows(revision, eps["revision"], "latest_answer_success"),
            revision_semantic=scalar_rows(revision, eps["revision"], "revision_success"),
            old_record_retired=scalar_rows(revision, eps["revision"], "old_record_retired"),
            new_record_active=scalar_rows(revision, eps["revision"], "new_record_active"),
            drift=drift_summary(
                report.get("endpoints", {}).get("drift"), population.get("drift", {})
            ),
        )
    return {
        "status": "complete"
        if all(v["status"] == "complete" for v in primary.values())
        else "incomplete",
        "primary": primary,
        "secondary": secondary,
        "population_identity": digest(population),
        "edit_n": n,
    }


def validate_matrix(matrix):
    cells = all_cells(matrix)
    fidelity_policy.validate_matrix(matrix, cells)
    validation = matrix.get("full_validation")
    if matrix.get("endpoint_contract_version") == 1 or validation is not None:
        full_contract.validate(validation)
        for cell in cells:
            population = cell.get("population")
            if (
                cell.get("full_validation") != validation
                or (population is None and (cell.get("admitted") or cell.get("launch_allowed")))
                or (population is not None and population.get("full_validation") != validation)
            ):
                raise ValueError("matrix/cell/frozen population DEC-063 contract mismatch")
    if not cells:
        raise ValueError("nonempty independently declared matrix required")
    identities = [coordinate(c) for c in cells]
    if len(set(identities)) != len(cells) or len({c["cell_id"] for c in cells}) != len(cells):
        raise ValueError("duplicate expected cell coordinate or ID")
    for c in cells:
        if c["cell_id"] != coordinate_id(c):
            raise ValueError("unstable cell coordinate identity")
        cp = c["checkpoints"]
        if not cp or cp != sorted(set(cp)) or any(type(n) is not int or n <= 0 for n in cp):
            raise ValueError("ordered positive checkpoint contract required")
        if type(c["block_number"]) is not int or type(c["within_block_order"]) is not int:
            raise ValueError("explicit block ordering required")
        p = c.get("population")
        if p is not None:
            if (
                len(p["item_ids"]) != max(cp)
                or len(p["item_ids"]) != len(set(p["item_ids"]))
                or len(p["paraphrase_counts"]) != len(p["item_ids"])
                or any(type(n) is not int or n < 1 for n in p["paraphrase_counts"])
            ):
                raise ValueError("complete ordered edit/paraphrase population required")
            for ids in p["endpoints"].values():
                if len(ids) != len(set(ids)):
                    raise ValueError("duplicate endpoint population")
    slots = [(c["block_number"], c["within_block_order"]) for c in cells]
    if len(set(slots)) != len(slots):
        raise ValueError("duplicate execution order slot")
    return cells


def load_cell(cell, files, scope):
    expected = {k: cell[k] for k in COORDS}
    out = {
        "cell_id": cell["cell_id"],
        "cell": expected,
        "block_number": cell["block_number"],
        "within_block_order": cell["within_block_order"],
        "status": "missing_cell",
        "artifact_complete": False,
        "primary_metrics_complete": False,
        "checkpoints": {},
        "missing_checkpoints": list(cell["checkpoints"]),
        "scientific_admission": False,
        "full_validation_complete": False
        if (cell.get("population") or {}).get("full_validation")
        else None,
        "endpoint_complete": False
        if (cell.get("population") or {}).get("full_validation")
        else None,
    }
    directory = cell.get("result_dir")
    if not directory:
        return out
    directory = Path(directory)
    if not directory.is_absolute():
        directory = ROOT / directory
    directory = directory.resolve()
    if not directory.is_relative_to(ROOT / "results"):
        raise PermissionError("cell directory must be under repo results")
    meta = files.read(directory / "cell.json")
    if meta is None:
        return out
    if meta.get("cell") != expected or meta.get("manifest_sha256") != cell.get("manifest_sha256"):
        raise ValueError("observed cell/recipe identity differs from declared matrix")
    if meta.get("checkpoints") != cell["checkpoints"]:
        raise ValueError("checkpoint cadence differs from matrix")
    for k in ("adapter_identity", "code_sha256", "payload_sha256"):
        if cell.get(k) is not None and meta.get(k) != cell[k]:
            raise ValueError("cell binding mismatch: " + k)
    if scope == "confirmatory" and meta.get("mode") != "stage4_sealed_cell":
        raise ValueError("development cell cannot fill a confirmatory slot")
    out["mode"] = meta.get("mode")
    out["attempts"] = [p.name for p in sorted(directory.glob("attempt-*")) if p.is_dir()]
    receipts = []
    for path in sorted(directory.glob("attempt-*/checkpoint-*.receipt.json")):
        rec = files.read(path)
        if digest({k: v for k, v in rec.items() if k != "receipt_sha256"}) != rec.get(
            "receipt_sha256"
        ):
            raise ValueError("receipt self-hash mismatch")
        receipts.append((rec, path))
    receipts.sort(key=lambda pair: pair[0]["checkpoint"])
    if [r["checkpoint"] for r, _ in receipts] != cell["checkpoints"][: len(receipts)]:
        raise ValueError("duplicate or noncontiguous receipt chain")
    previous = None
    receipt_hashes = {}
    for rec, path in receipts:
        if (
            rec["previous_receipt_sha256"] != previous
            or rec["manifest_sha256"] != cell["manifest_sha256"]
            or rec.get("mode") != meta.get("mode")
        ):
            raise ValueError("receipt chain/recipe/mode mismatch")
        n = rec["checkpoint"]
        local = path.parent / f"checkpoint-{n}.json"
        original = Path(rec["report"]["path"])
        if original.name != local.name or original.parent.name != path.parent.name:
            raise ValueError("receipt report location mismatch")
        report = files.read(local)
        if report is None or files.sources[str(local.resolve())] != rec["report"]["sha256"]:
            raise ValueError("report file hash mismatch")
        if (
            report.get("checkpoint") != n
            or report.get("state_sha256") != rec["state_sha256"]
            or report.get("mode") != meta.get("mode")
        ):
            raise ValueError("report checkpoint/state/mode mismatch")
        out["checkpoints"][str(n)] = summarize_checkpoint(
            report, cell.get("population"), n, max(cell["checkpoints"])
        )
        expected_full = (cell.get("population") or {}).get("full_validation")
        if expected_full is not None:
            secondary = out["checkpoints"][str(n)]["secondary"]
            secondary["sampled_drift"] = {
                **drift_summary(
                    report.get("endpoints", {}).get("drift"), cell["population"]["drift"]
                ),
                "population": "128-window-prefix_descriptive",
            }
            if n == max(cell["checkpoints"]):
                secondary["full_validation"] = full_contract.summary(
                    report.get("endpoints", {}).get("full_validation"),
                    expected_full,
                    report,
                    local,
                    cell["manifest_sha256"],
                    meta["adapter_identity"],
                    files.sources,
                    sampled_population=cell["population"]["drift"],
                )
                if cell.get("cap_fidelity_policy") is not None:
                    fidelity_policy.validate(cell["cap_fidelity_policy"])
                    summary = secondary["full_validation"]
                    if summary.get("complete"):
                        summary["concentration"] = ht7.from_binding(summary["vectors"])
            elif "full_validation" in report.get("endpoints", {}):
                raise ValueError("full-validation observation at an intermediate checkpoint")
        previous = rec["receipt_sha256"]
        receipt_hashes[n] = previous
    completed_results = []
    for path in sorted(directory.glob("attempt-*/result.json")):
        result = files.read(path)
        if (
            result.get("cell") != expected
            or result.get("manifest_sha256") != cell["manifest_sha256"]
        ):
            raise ValueError("result identity mismatch")
        if result.get("status") == "complete":
            if (
                result.get("completed_checkpoint") != max(cell["checkpoints"])
                or result.get("last_receipt_sha256") != previous
                or len(receipts) != len(cell["checkpoints"])
            ):
                raise ValueError("complete result without exact terminal checkpoint chain")
            completed_results.append(str(path))
    if len(completed_results) > 1:
        raise ValueError("duplicate completed result")
    out["missing_checkpoints"] = [n for n in cell["checkpoints"] if n not in receipt_hashes]
    out["artifact_complete"] = len(completed_results) == 1 and not out["missing_checkpoints"]
    out["primary_metrics_complete"] = out["artifact_complete"] and all(
        v["status"] == "complete" for v in out["checkpoints"].values()
    )
    out["status"] = "complete_artifacts" if out["artifact_complete"] else "partial_cell"
    expected_full = (cell.get("population") or {}).get("full_validation")
    final_secondary = out["checkpoints"].get(str(max(cell["checkpoints"])), {}).get("secondary", {})
    out["full_validation_complete"] = (
        final_secondary.get("full_validation", {}).get("complete", False)
        if expected_full is not None
        else None
    )
    out["full_validation_fidelity_passes"] = (
        (final_secondary.get("full_validation", {}).get("fidelity") or {}).get("passes", False)
        if expected_full is not None
        else None
    )
    out["sampled_drift_complete"] = (
        not out["missing_checkpoints"]
        and all(
            cp["secondary"].get("sampled_drift", {}).get("status") == "complete"
            for cp in out["checkpoints"].values()
        )
        if expected_full is not None
        else None
    )
    out["endpoint_complete"] = (
        out["full_validation_complete"] and out["sampled_drift_complete"]
        if expected_full is not None
        else None
    )
    out["scientific_admission"] = fidelity_policy.scientific_admission(cell, out, scope)
    out["cap_fidelity_policy"] = cell.get("cap_fidelity_policy")
    out["cap_fidelity_interpretation"] = (
        "DEC-064 labelled secondary benchmark; numeric failure never vetoes primary comparisons"
        if cell.get("cap_fidelity_policy") is not None
        else "historical pre-DEC-064 behavior; not the current adopted policy"
    )
    if cell.get("cap_fidelity_policy") is not None:
        out["cap_fidelity_benchmark"] = fidelity_policy.benchmark(
            final_secondary.get("full_validation", {})
        )
    out["unreceipted_checkpoints"] = [
        str(p)
        for p in sorted(directory.glob("attempt-*/checkpoint-*.json"))
        if not p.name.endswith(".receipt.json")
        and not p.with_name(p.stem + ".receipt.json").exists()
    ]
    out["receipt_policy"] = (
        "report digests, recipe/state identities and contiguous chain verified; snapshot payloads are not opened"
    )
    return out


def pair_contrasts(matrix, loaded):
    indexed = {coordinate(c): c for c in all_cells(matrix)}
    axes = matrix["axes"]
    out = []
    for dataset in axes["datasets"]:
        for contrast in matrix.get("contrasts", []):
            checkpoints = sorted(
                {n for c in all_cells(matrix) if c["dataset"] == dataset for n in c["checkpoints"]}
            )
            for n in checkpoints:
                stats = {}
                problems = []
                for metric in ("ES", "RET-GS", "LS"):
                    grid = []
                    populations_by_realization = {}
                    for realization in axes.get("realizations_by_dataset", {}).get(
                        dataset, axes.get("realizations", [])
                    ):
                        values = []
                        for order in axes["orders"]:
                            keys = [
                                (contrast[k], dataset, realization, order)
                                for k in ("treatment", "control")
                            ]
                            declared = [indexed.get(k) for k in keys]
                            pair = [loaded.get(d["cell_id"]) if d else None for d in declared]
                            population = [d.get("population") if d else None for d in declared]
                            common = (
                                all(p is not None for p in population)
                                and population[0] == population[1]
                            )
                            values_pair = [
                                c.get("checkpoints", {})
                                .get(str(n), {})
                                .get("primary", {})
                                .get(metric, {})
                                .get("value")
                                if c
                                else None
                                for c in pair
                            ]
                            if common:
                                populations_by_realization.setdefault(realization, []).append(
                                    set(population[0]["item_ids"])
                                )
                            if not common and all(c is not None for c in pair):
                                problems.append(
                                    {
                                        "realization": realization,
                                        "order": order,
                                        "reason": "unbound or different paired populations",
                                    }
                                )
                            values.append(
                                values_pair[0] - values_pair[1]
                                if common and all(v is not None for v in values_pair)
                                else None
                            )
                        grid.append(values)
                    result = paired_metric(
                        grid,
                        **matrix.get("bootstrap", {"seed": 0, "draws": 10000, "confidence": 0.975}),
                    )
                    seen = set()
                    independent = True
                    for groups in populations_by_realization.values():
                        if any(g != groups[0] for g in groups) or seen & groups[0]:
                            independent = False
                        seen |= groups[0]
                    if not independent:
                        result["interval"] = None
                        result["status"] = "dependent_realizations"
                        result["uncertainty"] = (
                            "overlapping realization data or inconsistent order membership; no independent cluster interval"
                        )
                    stats[metric] = result
                final = n == max(checkpoints)
                draft = classify(stats, admitted=True)
                if contrast.get("role") == "secondary":
                    status = "secondary_descriptive"
                elif not final:
                    status = "checkpoint_descriptive"
                elif matrix.get("multiplicity", {}).get("status") != "admitted":
                    status = "unadmitted_multiplicity"
                else:
                    # This version does not invent an unregistered adjustment procedure.
                    status = "requires_registered_multiplicity_implementation"
                out.append(
                    {
                        "dataset": dataset,
                        "checkpoint": n,
                        "contrast": contrast,
                        "metrics": stats,
                        "margins": MARGINS,
                        "draft_margin_classification": draft,
                        "classification": status,
                        "pairing_issues": problems,
                        "multiplicity": "U12 remains open; .975 pointwise cluster intervals are not familywise control",
                    }
                )
    return out


def analyze(matrix):
    cells = validate_matrix(matrix)
    files = Files()
    loaded = {}
    for cell in cells:
        try:
            loaded[cell["cell_id"]] = load_cell(cell, files, matrix["scope"])
        except (ValueError, KeyError, TypeError, OSError) as exc:
            loaded[cell["cell_id"]] = {
                "cell_id": cell["cell_id"],
                "cell": {k: cell[k] for k in COORDS},
                "status": "invalid_cell",
                "reason": str(exc),
                "artifact_complete": False,
                "primary_metrics_complete": False,
                "checkpoints": {},
                "missing_checkpoints": cell["checkpoints"],
                "scientific_admission": False,
            }
    ordered = sorted(cells, key=lambda c: (c["block_number"], c["within_block_order"]))
    incomplete = [
        {
            "cell_id": c["cell_id"],
            "cell": {k: c[k] for k in COORDS},
            "block_number": c["block_number"],
            "status": loaded[c["cell_id"]]["status"],
            "missing_checkpoints": loaded[c["cell_id"]]["missing_checkpoints"],
        }
        for c in ordered
        if not loaded[c["cell_id"]]["artifact_complete"]
        or loaded[c["cell_id"]].get("endpoint_complete") is False
    ]
    blocks = []
    for block in sorted({c["block_number"] for c in cells}):
        rows = [loaded[c["cell_id"]] for c in ordered if c["block_number"] == block]
        blocks.append(
            {
                "block_number": block,
                "planned": len(rows),
                "artifact_complete": sum(r["artifact_complete"] for r in rows),
                "primary_metrics_complete": sum(r["primary_metrics_complete"] for r in rows),
                "complete": all(
                    r["artifact_complete"] and r.get("endpoint_complete") is not False for r in rows
                ),
            }
        )
    comparisons = pair_contrasts(matrix, loaded)
    files.verify()
    return {
        "task": "R1-75",
        "schema_version": 1,
        "matrix_name": matrix["name"],
        "matrix_sha256": digest(matrix),
        "scope": matrix["scope"],
        "cap_fidelity_policy": matrix.get("cap_fidelity_policy"),
        "cap_fidelity_interpretation": (
            "DEC-064 secondary benchmarks; numeric cap failures do not veto primary comparisons."
            if matrix.get("cap_fidelity_policy") is not None
            else "Historical matrix without DEC-064 binding; any D.2 cap-veto behavior is a historical replay, not the current adopted policy."
        ),
        "banner": "development/draft observations do not fill confirmation slots",
        "cells": [loaded[c["cell_id"]] for c in ordered],
        "blocks": blocks,
        "complete_blocks": [b["block_number"] for b in blocks if b["complete"]],
        "incomplete_cells": incomplete,
        "contrasts": comparisons,
        "sources_sha256": files.sources,
        "limits": [
            "Complete blocks mean terminal execution artifacts, not universal endpoint availability or scientific admission.",
            "Missing pairs are not imputed; available-pair means remain diagnostics.",
            "Three fresh realization clusters keep all five orders together; no iid-order claim.",
            "Snapshot payloads and training inputs are not opened; reports and receipts establish analysis provenance.",
            "U12 multiplicity and final secondary thresholds remain pending; no confirmatory verdict is emitted.",
        ],
        "model_calls": 0,
        "gpu_seconds": 0,
    }


def markdown(report):
    lines = [
        f"# {report['matrix_name']} — Stage 4 cell analysis",
        "",
        report["banner"],
        report.get("cap_fidelity_interpretation", ""),
        "",
        "| Block | Planned | Terminal artifacts | Complete primary metrics | Execution complete |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for b in report["blocks"]:
        lines.append(
            f"| {b['block_number']} | {b['planned']} | {b['artifact_complete']} | {b['primary_metrics_complete']} | {b['complete']} |"
        )
    lines += [
        "",
        "| Dataset / condition / realization / order | Checkpoint | ES | RET-GS | LS bounded / terminated | Unseen fires | Near bounded / terminated | Revision latest | Drift mean / max / ES99 nats |",
        "| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
    ]

    def fmt(v):
        return "unavailable" if v is None else f"{v:.6g}"

    def count(v):
        if not v:
            return "not run"
        return f"{fmt(v.get('numerator'))}/{v.get('planned')}" + (
            "" if v.get("value") is not None else " (unavailable full rate)"
        )

    for cell in report["cells"]:
        label = " / ".join(
            str(cell["cell"][k]) for k in ("dataset", "condition", "realization", "order")
        )
        for n, cp in cell["checkpoints"].items():
            p, s = cp["primary"], cp["secondary"]
            if not p:
                lines.append(f"| {label} | {n} | population unbound | — | — | — | — | — | — |")
                continue
            drift = s.get("drift", {}).get("references", {}).get("original")
            d = (
                " / ".join(
                    fmt(drift[k])
                    for k in ("mean_signed_nats", "max_positive_nats", "ES99_positive_nats")
                )
                if drift
                else "not run/unavailable"
            )
            ls = count(p["LS"]) + " / " + count(s["LS_terminated"])
            near = count(s.get("near_miss_bounded")) + " / " + count(s.get("near_miss_terminated"))
            lines.append(
                f"| {label} | {n} | {fmt(p['ES']['value'])} | {fmt(p['RET-GS']['value'])} | {ls} | {count(s['unseen_false_fire'])} | {near} | {count(s.get('revision_latest'))} | {d} |"
            )
    lines += ["", "## Explicit incomplete cells (DEC-051 order)", ""]
    lines.extend(
        f"- {c['cell_id']}: "
        + ", ".join(f"{k}={v}" for k, v in c["cell"].items())
        + f"; {c['status']}; missing checkpoints {c['missing_checkpoints']}"
        for c in report["incomplete_cells"]
    )
    if not report["incomplete_cells"]:
        lines.append("None. Endpoint availability and admission remain separate.")
    lines += [
        "",
        "## Paired contrasts",
        "",
        "| Dataset | Contrast | Checkpoint | ΔES | ΔRET-GS | ΔLS | Classification |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for c in report["contrasts"]:
        vals = [fmt(c["metrics"][k].get("estimate")) for k in ("ES", "RET-GS", "LS")]
        lines.append(
            f"| {c['dataset']} | {c['contrast']['id']} | {c['checkpoint']} | "
            + " | ".join(vals)
            + f" | {c['classification']} |"
        )
    lines += ["", *["- " + s for s in report["limits"]]]
    lines += full_contract.report_lines(report["cells"])
    if report.get("cap_fidelity_policy") is not None:
        lines += fidelity_policy.report_lines(report["cells"])
    return "\n".join(lines) + "\n"
