"""CPU-only readers for completed trained-reader artifacts and their denominators.

No model imports. Reports retain incomplete cells, hash the actual bytes read,
and keep whole-process cost separate from its stream/readout components.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("zsre", "counterfact")
METRICS = ("ES", "RET-ES", "RET-GS", "LS", "near_miss", "revision")
HARM = ("mean_kl", "mean_delta_nll", "es99_positive", "maximum_positive")


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path, sources):
    path = Path(path).resolve()
    raw = path.read_bytes()
    sources[str(path)] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def bound(binding, sources):
    path = Path(binding["path"])
    if not path.is_absolute():
        path = ROOT / path
    actual = sha(path)
    if actual != binding["sha256"]:
        raise ValueError(f"source hash mismatch: {path}")
    sources[str(path.resolve())] = actual
    return path


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError("nonfinite/nonnumeric summary")
    return value


def cost(directory, sources):
    path = Path(directory) / "cost.json"
    if not path.exists():
        return {"status": "missing", "seconds": None, "path": str(path)}
    d = read(path, sources)
    seconds = d.get("elapsed_process_seconds")
    if d["status"] == "complete" and seconds is None:
        raise ValueError("complete process without recorded cost")
    if seconds is not None and finite(seconds) < 0:
        raise ValueError("negative process cost")
    return {
        "status": d["status"],
        "seconds": seconds,
        "path": str(path.resolve()),
        "scope": d.get("scope", d.get("cost_scope")),
        "peak_host_rss_bytes": d.get("peak_host_rss_bytes"),
    }


def training(directory, sources):
    directory = Path(directory)
    receipt = cost(directory, sources)
    row = dict(path=str(directory.resolve()), status="missing", cost=receipt)
    if not (directory / "report.json").exists():
        row["status"] = receipt["status"] if receipt["status"] != "complete" else "incomplete"
        if row["status"] == "missing" and directory.exists():
            row["status"] = "unfinished; no terminal report"
        return row
    d = read(directory / "report.json", sources)
    row.update(
        {k: d[k] for k in ("rule", "seed", "read_taps", "parameter_count", "profile_only", "steps")}
    )
    row["status"] = d["status"] if d["status"] != "complete" else receipt["status"]
    if row["status"] == "complete":
        bound(d["reader"], sources)
        row.update(
            initial_reader_sha256=d["initial_reader_sha256"],
            reader_sha256=d["reader"]["params_sha256"],
            base_sha256=d["base_sha256"],
            recipe=d["recipe"],
            selected_steps=d["selected_steps"],
        )
    return row


def evaluation(directory, sources, *, positions=245237, checkpoint=300, development=False):
    directory = Path(directory)
    receipt = cost(directory, sources)
    row = dict(path=str(directory.resolve()), status="missing", cost=receipt)
    if not (directory / "report.json").exists():
        row["status"] = receipt["status"] if receipt["status"] != "complete" else "incomplete"
        if row["status"] == "missing" and directory.exists():
            row["status"] = "unfinished; no terminal report"
        return row
    d = read(directory / "report.json", sources)
    row.update(
        {k: d[k] for k in ("dataset", "rule", "seed", "read_taps", "write_sites", "development")}
    )
    row["status"] = d["status"] if d["status"] != "complete" else receipt["status"]
    if row["status"] != "complete":
        return row
    if d["development"] != development:
        raise ValueError("development/production population mismatch")
    tr_path = bound(d["training"], sources)
    tr = training(tr_path.parent, sources)
    if (
        tr["status"] != "complete"
        or tr["profile_only"] != development
        or (
            not development and (tr["steps"] != 300 or tr["selected_steps"] != [150, 200, 250, 300])
        )
    ):
        raise ValueError("training incomplete or profile/production mismatch")
    for key in ("rule", "seed", "read_taps"):
        if d[key] != tr[key]:
            raise ValueError("training/evaluation coordinate mismatch")
    for key in ("payload", "payload_recipe", "source_recipe"):
        bound(d[key], sources)
    cp = read(directory / f"stream/checkpoint-{checkpoint}.json", sources)
    finish = read(directory / "stream/finish.json", sources)
    config = read(directory / "stream/config.json", sources)
    harm = read(directory / "harm/summary.json", sources)
    hc = cost(directory / "harm", sources)
    if (
        finish != d["stream"]
        or harm != d["harm"]
        or finish["status"] != "complete"
        or hc["status"] != "complete"
        or cp["checkpoint"] != checkpoint
        or finish["items_completed"] != checkpoint
        or finish["items_planned"] != checkpoint
        or checkpoint not in finish["checkpoints_completed"]
        or len(config["item_ids"]) != checkpoint
        or len(set(config["item_ids"])) != checkpoint
    ):
        raise ValueError("incomplete or inconsistent stream/harm/checkpoint")
    for key in ("state_sha256", "base_sha256"):
        if finish[key] != harm[key] or cp["snapshot"][key] != finish[key]:
            raise ValueError("final state/base mismatch")
    if (
        tr["base_sha256"] != finish["base_sha256"]
        or tr["reader_sha256"] != finish["reader_sha256"]
        or config["reader_sha256"] != tr["reader_sha256"]
        or cp["snapshot"]["reader_sha256"] != tr["reader_sha256"]
    ):
        raise ValueError("reader/base identity mismatch")
    selection, gate = harm["selection"], d["gate_telemetry"]
    if (
        selection["positions"] != positions
        or gate["logical_positions"] != positions
        or gate["selected"] + gate["hard_null"] != positions
        or selection["windows"] * (selection["window_tokens"] - 1) != positions
    ):
        raise ValueError("ordinary-text denominator mismatch")
    if config["acquisition"] != "adjoint" or harm["treatment"]["acquisition"] != "adjoint":
        raise ValueError("unexpected acquisition rule")
    for key in ("read_taps", "write_sites"):
        if config["interface"][key] != d[key] or harm["treatment"][key] != d[key]:
            raise ValueError("interface mismatch")
    bound(harm["vectors"], sources)
    metrics = cp["metrics"]
    for key in METRICS:
        m = metrics[key]
        finite(m["value"])
        if (
            not 0 < m["scored"] == m["planned"]
            or not 0 <= m["value"] <= 1
            or m["status"] != "complete"
            or not math.isclose(m["value"], finite(m["numerator"]) / m["planned"], abs_tol=1e-12)
        ):
            raise ValueError("invalid endpoint denominator/value")
    summary = {}
    for reference in ("capoff", "original"):
        h = harm["summary"][reference]
        if h["loss"]["positions"] != positions or h["kl"]["positions"] != positions:
            raise ValueError("harm summary denominator mismatch")
        summary[reference] = dict(
            mean_kl=finite(h["kl"]["mean_signed"]),
            mean_delta_nll=finite(h["loss"]["mean_signed"]),
            es99_positive=finite(h["loss"]["es99_positive"]),
            maximum_positive=finite(h["loss"]["maximum_positive"]),
            exceedance=h["loss"]["exceedance"],
            half_mass_positions=h["loss"].get("half_mass_positions"),
        )
    row.update(
        metrics=metrics,
        unseen=cp.get("unseen", {}).get("summary", {}),
        gate=gate,
        harm=summary,
        positions=positions,
        population=d["population"],
        selection=selection,
        vector=harm["vectors"],
        pairing=dict(
            items=config["item_ids"],
            endpoints=config["endpoints_sha256"],
            payload_sha256=d["payload"]["sha256"],
            window_sha256=selection["windows_sha256"],
            base_sha256=tr["base_sha256"],
        ),
        training=tr,
        interface=d["interface_accounting"],
        stream_seconds=finite(finish["elapsed_process_seconds"]),
        harm_seconds=hc["seconds"],
        changed_distribution_fraction=d.get("changed_distribution_fraction"),
    )
    return row


def admitted(directory, sources, **kwargs):
    """Invalid completed artifacts remain visible but cannot enter contrasts."""
    try:
        return evaluation(directory, sources, **kwargs)
    except (ValueError, KeyError, OSError) as exc:
        return dict(path=str(Path(directory).resolve()), status="invalid", reason=str(exc))


def values(row):
    if row["status"] != "complete":
        return {}
    return {
        **{k: row["metrics"][k]["value"] for k in METRICS},
        **row["harm"]["capoff"],
        "fired": row["gate"]["selected"],
        "hard_null": row["gate"]["hard_null"],
        "unseen_false_fire_rate": row["unseen"].get("false_fire_rate_full_inventory"),
    }


def paired(a, b):
    if a["status"] != "complete" or b["status"] != "complete":
        return None
    if a["pairing"] != b["pairing"]:
        raise ValueError("paired endpoints/items/base/ordinary-text populations differ")
    av, bv = values(a), values(b)
    return {
        k: av[k] - bv[k]
        for k in (*METRICS, *HARM, "fired", "hard_null", "unseen_false_fire_rate")
        if av[k] is not None and bv[k] is not None
    }


def spread(values_):
    v = list(values_)
    return dict(
        n=len(v),
        mean=statistics.mean(v) if v else None,
        minimum=min(v) if v else None,
        maximum=max(v) if v else None,
        sample_sd=statistics.stdev(v) if len(v) > 1 else None,
    )


def fmt(x):
    if x is None:
        return "—"
    return f"{x:.7g}" if isinstance(x, float) else str(x).replace("|", "\\|").replace("\n", " ")


def table(headers, rows):
    return (
        "| "
        + " | ".join(headers)
        + " |\n| "
        + " | ".join(["---"] * len(headers))
        + " |\n"
        + "".join("| " + " | ".join(map(fmt, r)) + " |\n" for r in rows)
        + "\n"
    )


def tables(rows, identity):
    """All requested endpoint/fidelity denominators, including missing cells."""
    text = "## Per-cell efficacy\n\n" + table(
        ["Cell", "Status", *METRICS, "Unseen fires / observed / planned"],
        [
            [
                identity(c),
                c["status"],
                *[values(c).get(k) for k in METRICS],
                (
                    f"{c['unseen'].get('false_fires')} / {c['unseen'].get('firing_observed_n')} / {c['unseen'].get('expected_n')}"
                    if c["status"] == "complete"
                    else c.get("reason", "—")
                ),
            ]
            for c in rows
        ],
    )
    text += "Values use planned denominators; no unavailable slot is reinterpreted as a correct answer. ES is immediate acquisition success; RET-ES/RET-GS are retained own-prompt/paraphrase scores.\n\n"
    text += table(
        ["Cell", "Endpoint", "Numerator", "Scored / planned", "Status"],
        [
            [
                identity(c),
                k,
                c["metrics"][k].get("numerator"),
                f"{c['metrics'][k]['scored']} / {c['metrics'][k]['planned']}",
                c["metrics"][k]["status"],
            ]
            for c in rows
            if c["status"] == "complete"
            for k in METRICS
        ],
    )
    text += "## Fidelity and ordinary-text gate telemetry\n\nOwn cap-off reference; original-base summaries and full exceedance records are also retained in the JSON. Mean KL .001 is a descriptive fidelity watch, not data-integrity status. Harmful changes and gate firings are different quantities.\n\n"
    text += table(
        [
            "Cell",
            "Mean KL",
            "Mean ΔNLL",
            "ES99+",
            "Max ΔNLL",
            "Δ>.01 / >.1 / >1",
            "Fired / hard null / positions",
        ],
        [
            [
                identity(c),
                *[values(c).get(k) for k in HARM],
                "/".join(
                    str(c["harm"]["capoff"]["exceedance"][k]["count"])
                    for k in ("0.01", "0.1", "1.0")
                ),
                f"{c['gate']['selected']} / {c['gate']['hard_null']} / {c['positions']}",
            ]
            for c in rows
            if c["status"] == "complete"
        ],
    )
    text += "## Evaluation costs and allocated storage\n\nProcess seconds include construction, acquisition, endpoints and harm. Stream and harm are subsets, not extra charges. Inactive dense write slots remain charged; active-coordinate bytes are not a storage saving.\n\n"
    text += table(
        [
            "Cell",
            "Process s",
            "Stream s (subset)",
            "Harm s (subset)",
            "Parameters",
            "Delta allocated bytes",
            "Delta active bytes",
            "Total allocated bytes",
        ],
        [
            [
                identity(c),
                c.get("cost", {}).get("seconds"),
                c.get("stream_seconds"),
                c.get("harm_seconds"),
                *[
                    c.get("interface", {}).get(k)
                    for k in (
                        "parameters",
                        "delta_allocated_bytes",
                        "delta_active_coordinate_bytes",
                        "total_allocated_bytes",
                    )
                ],
            ]
            for c in rows
        ],
    )
    return text


def write_outputs(report, markdown, output, document):
    output, document = Path(output), Path(document)
    output.mkdir(parents=True, exist_ok=False)
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (output / "report.md").write_text(markdown)
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(markdown)
