"""DEC-064a: receipt-verified fidelity watch, without models or admission changes.

observations.jsonl is the locked, fsynced journal for all completed observations.
entries.jsonl, alerts.jsonl, maxima.json and the managed Markdown section are
rebuildable views. Retrying after a view-write failure cannot duplicate an event.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from scripts import ht7_concentration as concentration
from scripts import r1_49m_fidelity_policy as fidelity
from scripts import r1_63l_full_validation_contract as full

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- HT-8 managed watch: begin -->"
END = "<!-- HT-8 managed watch: end -->"
POLICY = {
    "version": 1,
    "decision": "DEC-064a",
    "bounds_nats": {"mean_kl": 0.001, "mean_signed_nll_increase": 0.01},
    "breach": "strictly above either bound against either reference",
    "identity": "digest of mode, recipe SHA256 and declared cell coordinates",
    "maxima": "all verified observations; condition x dataset x reference x metric",
    "development_reference": "first verified development observation per condition x dataset, frozen by journal order",
    "creep": "a breaching entry strictly exceeds a previous maximum or twice its frozen development reference, per reference/metric",
    "reporting": "immediate local alert; orchestrator conveys alerts immediately and entries at block boundaries",
    "admission_veto": False,
}


def binding():
    return dict(
        policy=POLICY,
        implementations=[
            full.ref(p)
            for p in (__file__, full.__file__, fidelity.__file__, concentration.__file__)
        ],
    )


def validate_queue_binding(matrix):
    required = (
        matrix.get("full_validation") is not None or matrix.get("cap_fidelity_policy") is not None
    )
    if required or "fidelity_watch" in matrix:
        if matrix.get("fidelity_watch") != binding():
            raise ValueError("DEC-064a queue fidelity-watch binding missing or changed")
    return required


def inspect(recipe_binding, result_path):
    """Read only completed receipts/reports/vectors; never open model/payload bytes."""
    sources = {}

    def read(path):
        path = Path(path).resolve()
        if "confirm" in path.parts or not path.is_relative_to(ROOT):
            raise PermissionError("watch reads unsealed repository metadata only")
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        if h != full.sha(path):
            raise ValueError("watch metadata changed while reading")
        if path.as_posix() in sources and sources[path.as_posix()] != h:
            raise ValueError("watch metadata changed across reads")
        sources[str(path)] = h
        return json.loads(raw)

    recipe_path = Path(recipe_binding["path"]).resolve()
    recipe = read(recipe_path)
    if sources[str(recipe_path)] != recipe_binding["sha256"]:
        raise ValueError("watch recipe binding changed")
    spec = full.validate(recipe.get("full_validation"))
    result_path = Path(result_path).resolve()
    if not result_path.is_relative_to(ROOT / "results") or result_path.name != "result.json":
        raise PermissionError("watch requires a repository completed result")
    result = read(result_path)
    mode = recipe["mode"]
    if mode not in ("stage4_development_cell", "stage4_sealed_cell"):
        raise ValueError("watch requires declared development or sealed-cell mode")
    if (
        result.get("status") != "complete"
        or result.get("cell") != recipe["cell"]
        or result.get("manifest_sha256") != recipe_binding["sha256"]
        or result.get("mode") != mode
        or result.get("completed_checkpoint") != max(recipe["checkpoints"])
    ):
        raise ValueError("watch requires a complete identity-bound terminal result")
    directory = result_path.parent.parent
    meta = read(directory / "cell.json")
    if (
        meta.get("cell") != recipe["cell"]
        or meta.get("manifest_sha256") != recipe_binding["sha256"]
        or meta.get("checkpoints") != recipe["checkpoints"]
        or meta.get("mode") != mode
        or meta.get("adapter_identity") != recipe["adapter_identity"]
    ):
        raise ValueError("watch cell metadata differs from recipe")
    endings = [
        p for p in directory.glob("attempt-*/result.json") if read(p).get("status") == "complete"
    ]
    if endings != [result_path]:
        raise ValueError("watch requires exactly one completed result per recipe cell")
    previous = None
    for n in recipe["checkpoints"]:
        receipts = list(directory.glob(f"attempt-*/checkpoint-{n}.receipt.json"))
        if len(receipts) != 1:
            raise ValueError("watch requires one certified receipt per checkpoint")
        receipt = read(receipts[0])
        report_path = receipts[0].with_name(f"checkpoint-{n}.json")
        report = read(report_path)
        if (
            receipt.get("receipt_sha256")
            != full.digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
            or receipt.get("previous_receipt_sha256") != previous
            or receipt.get("manifest_sha256") != recipe_binding["sha256"]
            or receipt.get("checkpoint") != n
            or report.get("checkpoint") != n
            or receipt.get("state_sha256") != report.get("state_sha256")
            or report.get("mode") != mode
            or receipt.get("report") != full.ref(report_path)
        ):
            raise ValueError("watch checkpoint receipt/report chain differs")
        previous = receipt["receipt_sha256"]
    if result.get("last_receipt_sha256") != previous:
        raise ValueError("watch completed result has wrong terminal receipt")
    summary = full.summary(
        report.get("endpoints", {}).get("full_validation"),
        spec,
        report,
        report_path,
        recipe_binding["sha256"],
        recipe["adapter_identity"],
        sources,
        sampled_population={
            "expected_positions": spec["sample_windows"] * (spec["window_tokens"] - 1)
        }
        if spec.get("sample_windows") is not None
        else None,
    )
    if not summary.get("complete"):
        raise ValueError("completed cell lacks full fidelity evidence: " + summary["status"])
    stats = concentration.from_binding(summary["vectors"])
    for path, h in sources.items():
        if full.sha(path) != h:
            raise ValueError("watch evidence changed during audit: " + path)
    identity = dict(mode=mode, recipe_sha256=recipe_binding["sha256"], cell=recipe["cell"])
    return dict(
        identity=identity,
        cell_id=full.digest(identity),
        scope="development" if mode == "stage4_development_cell" else "confirmatory",
        recipe=dict(path=str(recipe_path), sha256=recipe_binding["sha256"]),
        result=full.ref(result_path),
        cell=recipe["cell"],
        checkpoint=report["checkpoint"],
        actual_records=report.get("observation", {}).get("active_records"),
        contract_sha256=full.digest(spec),
        reference_base_sha256=report["endpoints"]["full_validation"]["reference_base_sha256"],
        benchmark=fidelity.benchmark(summary),
        references=summary["references"],
        concentration=stats,
        bindings_sha256=sources,
    )


def metrics(observation):
    return {
        name: dict(
            mean_kl=ref["kl"]["mean_signed"], mean_signed_nll_increase=ref["loss"]["mean_signed"]
        )
        for name, ref in observation["references"].items()
    }


def replay(events):
    maxima, baselines, entries, alerts, seen = {}, {}, [], [], {}
    for event in events:
        obs = event["observation"]
        cid, fingerprint = obs["cell_id"], full.digest(obs)
        if (
            event.get("policy") != POLICY
            or event.get("observation_sha256") != fingerprint
            or cid in seen
        ):
            raise ValueError("invalid, duplicate or incompatible watch journal event")
        if cid != full.digest(obs["identity"]):
            raise ValueError("watch journal identity mismatch")
        seen[cid] = fingerprint
        group = obs["cell"]["condition"] + ":" + obs["cell"]["dataset"]
        measured = metrics(obs)
        breach = any(
            value > POLICY["bounds_nats"][metric]
            for ref in measured.values()
            for metric, value in ref.items()
        )
        reasons = []
        previous = maxima.get(group, {})
        baseline = baselines.get(group)
        for ref, values in measured.items():
            for metric, value in values.items():
                old = previous.get(ref, {}).get(metric)
                if breach and old is not None and value > old["value"]:
                    reasons.append(
                        dict(
                            kind="new_running_maximum",
                            reference=ref,
                            metric=metric,
                            value=value,
                            compared_value=old["value"],
                            compared_cell_id=old["cell_id"],
                        )
                    )
                if breach and baseline is not None and value > 2 * baseline["metrics"][ref][metric]:
                    reasons.append(
                        dict(
                            kind="above_twice_development_reference",
                            reference=ref,
                            metric=metric,
                            value=value,
                            compared_value=2 * baseline["metrics"][ref][metric],
                            compared_cell_id=baseline["cell_id"],
                        )
                    )
        if obs["scope"] == "development" and baseline is None:
            baselines[group] = dict(cell_id=cid, metrics=measured, recipe=obs["recipe"])
        for ref, values in measured.items():
            dest = maxima.setdefault(group, {}).setdefault(ref, {})
            for metric, value in values.items():
                if metric not in dest or value > dest[metric]["value"]:
                    dest[metric] = dict(value=value, cell_id=cid, scope=obs["scope"])
        if breach:
            entries.append(
                dict(
                    cell_id=cid,
                    recorded_utc=event["recorded_utc"],
                    observation=obs,
                    creep_reasons=reasons,
                )
            )
        if reasons:
            alerts.append(
                dict(
                    cell_id=cid,
                    recorded_utc=event["recorded_utc"],
                    group=group,
                    reasons=reasons,
                    delivery="pending_orchestrator_notification",
                    admission_veto=False,
                )
            )
    return dict(
        maxima=maxima, development_references=baselines, entries=entries, alerts=alerts, seen=seen
    )


def encoded(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n"


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temp.open("x") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def markdown(state):
    lines = [
        BEGIN,
        "",
        "## Automated verified watch (HT-8)",
        "",
        "Manual notes above are preserved. This source-bound table is regenerated from the locked journal; one entry per recipe cell. Both references are shown. Near-zero target-token loss does not establish unchanged predictions or reader inactivity.",
        "",
        f"Audited cells: {len(state['seen'])}; breaching cells: {len(state['entries'])}; creep alerts: {len(state['alerts'])}. Development and confirmatory observations remain labelled; benchmarks never veto primary comparisons.",
        "",
        "| Cell identity / scope | Condition / dataset / realization / order | Actual records / checkpoint | Reference | Mean KL | NLL increase | ES95 loss | Max loss | Positions for half KL | Near-zero loss fraction | Creep |",
        "|---|---|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for entry in state["entries"]:
        obs, cid = entry["observation"], entry["cell_id"]
        coords = " / ".join(
            str(obs["cell"][k]) for k in ("condition", "dataset", "realization", "order")
        )
        for name, ref in obs["references"].items():
            c = obs["concentration"]["references"][name]
            half = c["kl_positions"]["minimum_count_for_half_mass"]
            flags = sorted({r["kind"] for r in entry["creep_reasons"] if r["reference"] == name})
            records = obs["actual_records"] if obs["actual_records"] is not None else "unavailable"
            lines.append(
                f"| `{cid}` / {obs['scope']} | {coords} | {records} / {obs['checkpoint']} | {name} | {ref['kl']['mean_signed']:.9g} | {ref['loss']['mean_signed']:.9g} | {ref['loss']['ES95_positive']:.9g} | {ref['loss']['maximum_positive']:.9g} | {half if half is not None else 'undefined'} | {c['near_zero_loss_change']['fraction']:.8g} | {', '.join(flags) or 'none'} |"
            )
    lines += [
        "",
        "### Running maxima (all audited cells, including no-breach cells)",
        "",
        "| Condition : dataset | Reference | Maximum KL | Maximum signed NLL increase | Development reference cell |",
        "|---|---|---:|---:|---|",
    ]
    for group, refs in sorted(state["maxima"].items()):
        for name, values in refs.items():
            base = state["development_references"].get(group, {}).get("cell_id", "unavailable")
            lines.append(
                f"| {group} | {name} | {values['mean_kl']['value']:.9g} | {values['mean_signed_nll_increase']['value']:.9g} | `{base}` |"
            )
    lines += ["", "### Creep alerts — orchestrator delivery queue", ""]
    for alert in state["alerts"]:
        reasons = "; ".join(
            f"{r['reference']} {r['metric']} {r['value']:.9g} > {r['compared_value']:.9g} ({r['kind']})"
            for r in alert["reasons"]
        )
        lines.append(
            f"- **CREEP** `{alert['cell_id']}` ({alert['group']}): {reasons}. Orchestrator reports immediately; this is not an admission veto."
        )
    if not state["alerts"]:
        lines.append("No creep alerts observed.")
    return "\n".join([*lines, "", END, ""])


def update(observations, *, output=None, document=None):
    output = Path(output or ROOT / "results/R1/fidelity_watch").resolve()
    document = Path(document or ROOT / "docs/fidelity_watch.md").resolve()
    if not output.is_relative_to(ROOT / "results") or not document.is_relative_to(ROOT / "docs"):
        raise PermissionError("watch logs and documentation must stay in repository results/docs")
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        journal = output / "observations.jsonl"
        raw = journal.read_text() if journal.exists() else ""
        if raw and not raw.endswith("\n"):
            raise ValueError("torn watch journal; explicit recovery required")
        events = [json.loads(line) for line in raw.splitlines()]
        state = replay(events)
        new_ids = []
        for observation in observations:
            cid, fingerprint = observation["cell_id"], full.digest(observation)
            if cid in state["seen"]:
                if state["seen"][cid] != fingerprint:
                    raise ValueError("same watched cell has changed evidence; refusing overwrite")
                continue
            event = dict(
                policy=POLICY,
                observation=observation,
                observation_sha256=fingerprint,
                implementation=binding(),
                recorded_utc=datetime.now(UTC).isoformat(),
            )
            next_state = replay([*events, event])
            with journal.open("a") as stream:
                stream.write(encoded(event))
                stream.flush()
                os.fsync(stream.fileno())
            directory_fd = os.open(output, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            events.append(event)
            state = next_state
            new_ids.append(cid)
        # Rebuild even on a duplicate-only retry: a previous write may have stopped
        # after journal fsync but before one of these deterministic views.
        atomic_write(output / "entries.jsonl", "".join(encoded(e) for e in state["entries"]))
        atomic_write(output / "alerts.jsonl", "".join(encoded(a) for a in state["alerts"]))
        atomic_write(
            output / "maxima.json",
            encoded({k: state[k] for k in ("maxima", "development_references")}),
        )
        original = document.read_text() if document.exists() else "# Fidelity watch (DEC-064a)\n"
        if original.count(BEGIN) != original.count(END) or original.count(BEGIN) > 1:
            raise ValueError("invalid managed watch Markdown boundaries")
        if BEGIN in original:
            before, rest = original.split(BEGIN)
            _, after = rest.split(END)
            rendered = before + markdown(state) + after.lstrip("\n")
        else:
            rendered = original.rstrip() + "\n\n" + markdown(state)
        if document.exists() and document.read_text() != original:
            raise ValueError("watch Markdown edited concurrently; retry without overwriting it")
        if rendered != original:
            atomic_write(document, rendered)
        new_alerts = [a for a in state["alerts"] if a["cell_id"] in new_ids]
        for alert in new_alerts:
            print("HT-8 CREEP " + encoded(alert).strip(), file=sys.stderr, flush=True)
        return dict(
            status="updated",
            new_cells=len(new_ids),
            audited_cells=len(state["seen"]),
            breaches=len(state["entries"]),
            alerts=len(state["alerts"]),
            new_alerts=new_alerts,
            journal=full.ref(journal) if journal.exists() else None,
            entries=full.ref(output / "entries.jsonl"),
            alert_log=full.ref(output / "alerts.jsonl"),
            document=full.ref(document),
            admission_veto=False,
        )


def post_cell(matrix, cell, bindings):
    if not validate_queue_binding(matrix):
        return dict(status="not_declared_legacy_endpoint", admission_veto=False)
    directory = Path(cell["result_dir"])
    results = [
        p
        for p in directory.glob("attempt-*/result.json")
        if json.loads(p.read_text()).get("status") == "complete"
    ]
    if len(results) != 1:
        raise ValueError("watch post-cell requires a unique complete result")
    observation = inspect(bindings["recipes"][cell["cell_id"]], results[0])
    if observation["cell"] != {
        k: cell[k] for k in ("condition", "dataset", "realization", "order")
    }:
        raise ValueError("watch queue cell differs from completed recipe")
    return update([observation])


def update_report(report):
    observations = []
    for cell in report["cells"].values():
        if cell["status"] == "complete_development_measurement":
            observations.append(
                inspect(
                    cell["recipe"], Path(cell["full"]["vectors"]["path"]).parent / "result.json"
                )
            )
    return update(observations)


def scan(recipe_paths, result_roots):
    recipes = {}
    for path in recipe_paths:
        path = Path(path).resolve()
        if not path.is_relative_to(ROOT) or "confirm" in path.parts:
            raise PermissionError("watch catalog must be unsealed repository metadata")
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get("full_validation") is not None:
            recipes[full.sha(path)] = full.ref(path)
    observations, unavailable = [], []
    for root in result_roots:
        root = Path(root).resolve()
        if not root.is_relative_to(ROOT / "results") or "confirm" in root.parts:
            raise PermissionError("watch result roots must be unsealed repository results")
        for path in sorted(root.glob("**/result.json")):
            data = json.loads(path.read_text())
            if data.get("status") != "complete":
                continue
            b = recipes.get(data.get("manifest_sha256"))
            if b is None:
                unavailable.append(dict(path=str(path), status="recipe_not_in_declared_catalog"))
                continue
            try:
                observations.append(inspect(b, path))
            except (ValueError, OSError, KeyError, TypeError) as exc:
                unavailable.append(
                    dict(path=str(path), status="invalid_or_missing_full_evidence", reason=str(exc))
                )
    observations.sort(key=lambda o: (o["scope"] != "development", o["cell_id"]))
    return observations, unavailable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", action="append", type=Path, default=[])
    parser.add_argument("--recipe-dir", action="append", type=Path, default=[])
    parser.add_argument("--result-root", action="append", type=Path, default=[])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="persist journal, views and Markdown; default is read-only",
    )
    args = parser.parse_args()
    paths = [*args.recipe, *(p for d in args.recipe_dir for p in d.glob("*.json"))]
    if not paths or not args.result_root:
        parser.error("explicit recipe catalog and result roots required")
    observations, unavailable = scan(paths, args.result_root)
    result = (
        update(observations)
        if args.apply
        else dict(
            status="read_only",
            verified_cells=len(observations),
            breaching_cells=sum(not o["benchmark"]["passes"] for o in observations),
        )
    )
    print(json.dumps(dict(result, unavailable=unavailable), indent=2))


if __name__ == "__main__":
    main()
