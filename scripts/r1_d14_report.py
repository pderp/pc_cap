"""Fill the Stage-4 report template from bound analysis JSON, without inference changes.

All displayed data carry JSON-pointer provenance. Missing values stay unavailable.
Watch observations are replayed read-only; no producer, model, signature or queue runs.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import UTC, datetime
from pathlib import Path

from scripts import ht8_fidelity_watch as watch
from scripts import r1_49g_inference as inference
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_d11_block_report as d11

ROOT = d11.ROOT
TOKENS = {
    "STATUS",
    "METHODS",
    "BLOCKS",
    "PRIMARY",
    "SECONDARY",
    "FIDELITY",
    "WATCH",
    "INCOMPLETE",
    "MQ300",
    "OMISSIONS",
    "TAILS",
    "CONCENTRATION",
    "TRAJECTORIES",
    "NEAR",
    "S1",
    "FIGURES",
    "SOURCES",
}
MISSING = object()


def resolve(value, pointer):
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise ValueError("absolute JSON pointer required")
    for part in pointer[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def at(pointer, document="analysis", operation=None):
    return dict(document=document, pointer=pointer, operation=operation)


def display(value):
    if value is None:
        return "unavailable"
    if isinstance(value, float):
        return f"{value:.8g}"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value)


class Tables:
    def __init__(self, documents):
        self.documents = documents
        self.tables = {}
        self.bindings = {}

    def add(self, table, **columns):
        row, links = {}, {}
        for name, source in columns.items():
            if isinstance(source, dict) and "document" in source:
                try:
                    value = resolve(self.documents[source["document"]], source["pointer"])
                    if source.get("operation") == "length":
                        value = len(value)
                except (KeyError, IndexError, TypeError, ValueError):
                    raise ValueError("unbound report field: " + str(source)) from None
                row[name], links[name] = value, source
            else:
                row[name], links[name] = source, dict(literal=source)
        self.tables.setdefault(table, []).append(row)
        self.bindings.setdefault(table, []).append(links)


def build(analysis, watch_document):
    if (
        analysis.get("analysis_revision") != "R1-49n_DEC066_D4_prospective_scope"
        or analysis.get("primary_family") != inference.FAMILY
    ):
        raise ValueError("registered D4 / 63-interval analysis required")
    contrasts = analysis["contrasts"]
    if len(contrasts) != 21 or any(set(c["metrics"]) != set(inference.METRICS) for c in contrasts):
        raise ValueError(
            "exactly 21 contrasts × three metrics required, including unavailable MQuAKE"
        )
    tables = Tables(dict(analysis=analysis, watch=watch_document))
    for i, _c in enumerate(contrasts):
        p = f"/contrasts/{i}"
        for metric in inference.METRICS:
            m = p + "/metrics/" + metric
            tables.add(
                "primary",
                dataset=at(p + "/dataset"),
                contrast=at(p + "/contrast/id"),
                checkpoint=at(p + "/checkpoint"),
                metric=metric,
                status=at(m + "/status"),
                estimate=at(m + "/estimate"),
                realizations=at(m + "/realization_estimates"),
                pointwise_interval=at(m + "/unadjusted_interval"),
                adjusted_interval=at(m + "/adjusted_interval"),
                classification=at(p + "/classification"),
                scientific_admission=at(p + "/scientific_admission"),
                pairing_issues=at(p + "/pairing_issues"),
            )
    for i, b in enumerate(analysis["blocks"]):
        tables.add("blocks", **{k: at(f"/blocks/{i}/{k}") for k in b})
    for i, c in enumerate(analysis["cells"]):
        p = f"/cells/{i}"
        identity = {
            k: at(p + "/cell/" + k) for k in ("dataset", "condition", "realization", "order")
        }
        tables.add(
            "cell_inventory",
            cell_id=at(p + "/cell_id"),
            **identity,
            status=at(p + "/status"),
            artifact_complete=at(p + "/artifact_complete"),
            missing_checkpoints=at(p + "/missing_checkpoints"),
            scientific_admission=at(p + "/scientific_admission"),
            endpoint_complete=at(p + "/endpoint_complete") if "endpoint_complete" in c else None,
            invalid_reason=at(p + "/reason") if "reason" in c else None,
        )
        benchmark = c.get("cap_fidelity_benchmark", {})
        for reference in ("capoff", "original"):
            b = p + "/cap_fidelity_benchmark"
            if reference in benchmark.get("references", {}):
                r = b + "/references/" + reference
                tables.add(
                    "fidelity",
                    cell_id=at(p + "/cell_id"),
                    **identity,
                    reference=reference,
                    status=at(b + "/status"),
                    **{
                        k: at(r + "/" + k)
                        for k in (
                            "mean_kl_nats",
                            "mean_signed_nll_increase_nats",
                            "mean_kl_label",
                            "mean_nll_label",
                        )
                    },
                    admission_veto=at(b + "/admission_veto"),
                )
            else:
                tables.add(
                    "fidelity",
                    cell_id=at(p + "/cell_id"),
                    **identity,
                    reference=reference,
                    status="unavailable",
                    mean_kl_nats=None,
                    mean_signed_nll_increase_nats=None,
                    mean_kl_label="unavailable",
                    mean_nll_label="unavailable",
                    admission_veto=False,
                )
        for checkpoint, cp in c["checkpoints"].items():
            q = p + "/checkpoints/" + checkpoint
            for metric in cp["primary"]:
                m = q + "/primary/" + metric
                tables.add(
                    "trajectories",
                    cell_id=at(p + "/cell_id"),
                    **identity,
                    checkpoint=int(checkpoint),
                    metric=metric,
                    **{k: at(m + "/" + k) for k in cp["primary"][metric]},
                )
            for endpoint in cp["secondary"]:
                if endpoint not in ("sampled_drift", "full_validation"):
                    tables.add(
                        "endpoint_observations",
                        cell_id=at(p + "/cell_id"),
                        **identity,
                        checkpoint=int(checkpoint),
                        endpoint=endpoint,
                        observation=at(q + "/secondary/" + endpoint),
                    )
            for population in ("sampled_drift", "full_validation"):
                sec = cp["secondary"].get(population)
                if sec is None:
                    continue
                v = q + "/secondary/" + population
                for reference, stats in sec.get("references", {}).items():
                    if stats is None:
                        continue
                    r = v + "/references/" + reference
                    if population == "full_validation":
                        for metric in ("loss", "kl"):
                            m = r + "/" + metric
                            tables.add(
                                "tails",
                                cell_id=at(p + "/cell_id"),
                                **identity,
                                checkpoint=int(checkpoint),
                                population=population,
                                reference=reference,
                                metric=metric,
                                status=at(v + "/status"),
                                planned=at(v + "/planned"),
                                scored=at(v + "/scored"),
                                mean_signed=at(m + "/mean_signed"),
                                mean_positive=at(m + "/mean_positive"),
                                ES95_positive=at(m + "/ES95_positive"),
                                ES99_positive=at(m + "/ES99_positive"),
                                maximum_positive=at(m + "/maximum_positive"),
                                exceedances_nats=at(m + "/exceedances_nats"),
                            )
                    else:
                        tables.add(
                            "tails",
                            cell_id=at(p + "/cell_id"),
                            **identity,
                            checkpoint=int(checkpoint),
                            population=population,
                            reference=reference,
                            metric="loss",
                            status=at(v + "/status"),
                            planned=at(v + "/planned_positions"),
                            scored=at(v + "/scored_positions"),
                            mean_signed=at(r + "/mean_signed_nats"),
                            mean_positive=at(r + "/mean_positive_nats"),
                            ES95_positive=at(r + "/ES95_positive_nats"),
                            ES99_positive=at(r + "/ES99_positive_nats"),
                            maximum_positive=at(r + "/max_positive_nats"),
                            exceedances_nats=at(r + "/exceedances_nats"),
                        )
                concentration = sec.get("concentration")
                if concentration:
                    for reference in concentration["references"]:
                        r = v + "/concentration/references/" + reference
                        tables.add(
                            "concentration",
                            cell_id=at(p + "/cell_id"),
                            **identity,
                            checkpoint=int(checkpoint),
                            reference=reference,
                            **{
                                k: at(r + "/" + k)
                                for k in (
                                    "near_zero_loss_change",
                                    "loss_positive_positions",
                                    "kl_positions",
                                    "kl_windows",
                                    "window_mean_kl",
                                )
                            },
                        )
    for i, c in enumerate(analysis["secondary_benchmarks"]["cells"]):
        p = f"/secondary_benchmarks/cells/{i}"
        identity = {
            k: at(p + "/cell/" + k) for k in ("dataset", "condition", "realization", "order")
        }
        for name in c["benchmarks"]:
            q = p + "/benchmarks/" + name
            tables.add(
                "secondary_cells",
                cell_id=at(p + "/cell_id"),
                **identity,
                benchmark=name,
                **{k: at(q + "/" + k) for k in c["benchmarks"][name]},
            )
        if c["cell"]["dataset"] == "mquake":
            p2 = p + "/actual_occupancy_descriptive"
            tables.add(
                "mquake300",
                cell_id=at(p + "/cell_id"),
                **identity,
                **{
                    k: at(p2 + "/" + k)
                    for k in (
                        "attempted_checkpoint",
                        "required_actual_occupancy",
                        "status",
                        "planned",
                        "scored",
                        "fires",
                        "value",
                        "wilson95",
                        "change_from_actual_100",
                        "threshold",
                        "passes",
                    )
                },
            )
    for i, c in enumerate(analysis["secondary_benchmarks"]["macros"]):
        p = f"/secondary_benchmarks/macros/{i}"
        tables.add("secondary_macros", **{k: at(p + "/" + k) for k in c})
    for i, c in enumerate(analysis["near_miss_family"]["cells"]):
        p = f"/near_miss_family/cells/{i}"
        tables.add("near_miss", **{k: at(p + "/" + k) for k in c})
    for i, c in enumerate(analysis["prospectively_omitted_cells"]):
        tables.add("omissions", **{k: at(f"/prospectively_omitted_cells/{i}/{k}") for k in c})
    for i, c in enumerate(analysis["incomplete_cells"]):
        tables.add("incomplete", **{k: at(f"/incomplete_cells/{i}/{k}") for k in c})
    tables.add("watch_summary", **{k: at("/" + k, "watch") for k in watch_document["summary_keys"]})
    for collection in ("entries", "alerts", "observations"):
        for i, c in enumerate(watch_document[collection]):
            tables.add(
                "watch_" + collection, **{k: at(f"/{collection}/{i}/{k}", "watch") for k in c}
            )
    return dict(tables=tables.tables, bindings=tables.bindings)


def watch_snapshot(path, analysis):
    result = dict(
        status="unavailable_not_supplied",
        journal=None,
        events=None,
        queue_observations=None,
        entries=[],
        alerts=[],
        observations=[],
        delivery="not_sent; report generation does not acknowledge delivery",
        admission_veto=False,
    )
    if path is not None:
        binding = full.ref(path)
        raw = Path(path).read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise ValueError("torn watch journal")
        events = [json.loads(line) for line in raw.splitlines()]
        state = watch.replay(events)
        # Exact coordinate+recipe identities distinguish this queue from old
        # development or another recipe at the same coordinate.
        matrix = json.loads(Path(analysis["matrix_file"]["path"]).read_text())
        expected = {
            full.digest(
                dict(
                    mode="stage4_sealed_cell",
                    recipe_sha256=c["manifest_sha256"],
                    cell={k: c[k] for k in ("condition", "dataset", "realization", "order")},
                )
            )
            for c in [*matrix["cells"], *matrix.get("extension", {}).get("cells", [])]
        }
        rows = []
        for e in events:
            o = e["observation"]
            rows.append(
                dict(
                    identity=o["cell_id"],
                    in_this_matrix=o["cell_id"] in expected,
                    recorded_utc=e["recorded_utc"],
                    cell=o["cell"],
                    scope=o["scope"],
                    metrics=watch.metrics(o),
                )
            )
        result.update(
            status="verified_journal_snapshot",
            journal=binding,
            events=len(events),
            queue_observations=sum(r["in_this_matrix"] for r in rows),
            observations=rows,
            entries=[dict(e, in_this_matrix=e["cell_id"] in expected) for e in state["entries"]],
            alerts=[dict(e, in_this_matrix=e["cell_id"] in expected) for e in state["alerts"]],
        )
        if full.ref(path) != binding:
            raise ValueError("watch changed during report")
    result["breach_entries"] = len(result["entries"]) if path is not None else None
    result["creep_alerts"] = len(result["alerts"]) if path is not None else None
    result["summary_keys"] = [
        "status",
        "journal",
        "events",
        "queue_observations",
        "breach_entries",
        "creep_alerts",
        "delivery",
        "admission_veto",
    ]
    return result


def table_text(name, model, output, limit=8):
    rows = model["tables"].get(name, [])
    if not rows:
        return f"No rows in the bound `{name}` inventory; no values imputed.\n"
    columns = list(dict.fromkeys(k for row in rows for k in row))
    path = output / (name + ".csv")
    with path.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows({k: display(row.get(k)) for k in columns} for row in rows)

    def escaped(value):
        return display(value).replace("|", "\\|").replace("\n", " ")

    # Complete data and per-field bindings are in JSON/CSV. Preview order is
    # mechanical matrix order, never selected for favorable outcomes.
    visible = rows if limit is None else rows[:limit]
    return (
        f"Full table: [{name}.csv]({path.name}), {len(rows)} rows. "
        + (
            f"First {len(visible)} rows shown in source order.\n\n"
            if len(visible) < len(rows)
            else "\n\n"
        )
        + "| "
        + " | ".join(columns)
        + " |\n| "
        + " | ".join("---" for _ in columns)
        + " |\n"
        + "\n".join("| " + " | ".join(escaped(r.get(k)) for k in columns) + " |" for r in visible)
        + "\n"
    )


def fill(template, values):
    found = re.findall(r"\{\{([A-Z0-9_]+)\}\}", template)
    if set(found) != TOKENS or set(values) != TOKENS or len(found) != len(set(found)):
        raise ValueError("template must bind every declared placeholder exactly once")
    rendered = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: values[m[1]], template)
    if re.search(r"\{\{[A-Z0-9_]+\}\}", rendered):
        raise ValueError("unbound placeholder remains")
    return rendered


def run(
    analysis_path, output, *, journal=None, template=ROOT / "docs/R1_stage4_report_skeleton.md"
):
    analysis_path = d11.local(analysis_path)
    output = d11.local(output)
    if not output.is_relative_to(ROOT / "logs") or output.exists():
        raise ValueError("new output directory under repo logs required")
    analysis_ref = full.ref(analysis_path)
    report = json.loads(analysis_path.read_text())
    matrix_ref = report["matrix_file"]
    if full.ref(matrix_ref["path"]) != matrix_ref:
        raise ValueError("analysis matrix changed")
    matrix = json.loads(Path(matrix_ref["path"]).read_text())
    sources = {
        **report["sources_sha256"],
        str(analysis_path): analysis_ref["sha256"],
        matrix_ref["path"]: matrix_ref["sha256"],
        str(template): full.sha(template),
    }
    sources.update({str(ROOT / k): v for k, v in report["analysis_source_sha256"].items()})
    sources[str(Path(__file__).resolve())] = full.sha(__file__)
    for p, h in sources.items():
        if full.sha(p) != h:
            raise ValueError("analysis source changed: " + p)
    ws = watch_snapshot(journal, report)
    model = build(report, ws)
    model.update(
        task="R1-D14",
        synthetic=matrix.get("synthetic", False),
        analysis=analysis_ref,
        watch=ws,
        source_bindings_sha256=sources,
        generated_utc=datetime.now(UTC).isoformat(),
        figures={
            "disposition": "blocks",
            "primary-intervals": "primary",
            "checkpoint-trajectories": "trajectories",
            "cap-fidelity": "fidelity",
            "full-validation-tails": "tails",
            "watch-sequence": "watch_observations",
        },
        scientific_limits="Uncertainty uses three realization clusters; all five orders kept within cluster. Missing, omitted and unavailable are distinct. No alpha redistribution or cap benchmark veto.",
    )
    output.mkdir(parents=True, exist_ok=False)
    sections = {
        name: table_text(name, model, output, limit=None if name == "primary" else 8)
        for name in model["tables"]
    }
    absent = "No rows in the bound inventory; no replacement or imputation.\n"
    values = {
        "STATUS": (
            "**SYNTHETIC SOFTWARE REHEARSAL — NOT RESEARCH RESULTS.**"
            if model["synthetic"]
            else "**Receipt-bound analysis snapshot; inspect completion and admission before interpretation.**"
        ),
        "METHODS": (
            "Bound validation contract: `"
            + json.dumps(report["full_validation_contract"], sort_keys=True)
            + "`.\n\n"
            "Primary family: `" + json.dumps(report["primary_family"], sort_keys=True) + "`."
        ),
        "BLOCKS": sections.get("blocks", absent),
        "PRIMARY": sections.get("primary", absent),
        "SECONDARY": sections.get("secondary_macros", absent)
        + "\n"
        + sections.get("secondary_cells", absent)
        + "\n"
        + report["secondary_benchmarks"]["resource_status"]
        + "\n"
        + sections.get("endpoint_observations", absent),
        "FIDELITY": sections.get("fidelity", absent),
        "WATCH": sections.get("watch_summary", absent)
        + "\n"
        + sections.get("watch_entries", absent)
        + "\n"
        + sections.get("watch_alerts", absent),
        "INCOMPLETE": sections.get("incomplete", absent)
        + "\n"
        + sections.get("cell_inventory", absent),
        "MQ300": sections.get("mquake300", absent),
        "OMISSIONS": sections.get("omissions", absent),
        "TAILS": sections.get("tails", absent),
        "CONCENTRATION": sections.get("concentration", absent),
        "TRAJECTORIES": sections.get("trajectories", absent),
        "NEAR": sections.get("near_miss", absent),
        "S1": "Historical S1_LM / S1_literal controls retain DEC-047 certification and the D.4/U03 qualification. These comparisons do not establish exact-v5-compute-matched controls or exclude all continued-base explanations. Cap-off versus original-base continuation certification is separate from DEC-064 cap benchmarks. See [U03 memo]("
        + str(ROOT / "docs/R1_U03_interpretation_memo.md")
        + ").",
        "FIGURES": "\n".join(
            f"![{name} — "
            + ("SYNTHETIC" if model["synthetic"] else "analysis snapshot")
            + f"](figures/{name}.png)\n\nFigure source: `{table}` table in `report-data.json`; PDF/SVG companions.\n"
            for name, table in model["figures"].items()
        ),
        "SOURCES": "Analysis: `"
        + json.dumps(analysis_ref)
        + "`. Every displayed data field is bound in [report-data.json](report-data.json), `bindings[table][row][column]`, to an analysis/watch JSON pointer or an explicit literal. Full source SHA inventory is included. Watch rows outside this exact matrix retain their scope.\n\n"
        + "\n".join("- " + s for s in report["limits"]),
    }
    text = fill(Path(template).read_text(), values)
    for p, h in sources.items():
        if full.sha(p) != h:
            raise ValueError("source changed during rendering: " + p)
    if journal is not None and full.ref(journal) != ws["journal"]:
        raise ValueError("watch changed during rendering")
    with (output / "report-data.json").open("x") as f:
        json.dump(model, f, indent=2, allow_nan=False)
    with (output / "report.md").open("x") as f:
        f.write(text)
    return dict(
        report=full.ref(output / "report.md"),
        data=full.ref(output / "report-data.json"),
        rows={k: len(v) for k, v in model["tables"].items()},
        unbound_placeholders=0,
        synthetic=model["synthetic"],
        figures_pending=True,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--analysis", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--watch-journal", type=Path)
    a = p.parse_args()
    print(json.dumps(run(a.analysis, a.output, journal=a.watch_journal), indent=2))
