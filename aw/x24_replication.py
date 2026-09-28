"""X24 metadata-only audit of finished PC-v0 cells; never reads efficacy values.

The JSON projection skips nonselected value spans before decoding. Metrics and
secondary-summary files are not opened; items/decisions/checkpoints are projected
onto IDs, schema keys, identities and operation counts only. No model executes.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import hashlib
import json
import math
import zipfile
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import numpy as np

from aw.pc_v0 import (
    ARCHIVE,
    OUTPUT,
    ROOT,
    WEIGHTS_SHA,
    archive,
    build_cap,
    design,
    sha,
    source_identities,
)
from pccap.harness.ledger import Ledger

COUNTS = (
    "full_forwards",
    "partial_forwards",
    "reverses",
    "settle_iters",
    "prefix_microsteps",
    "search_candidates",
    "router_probes",
    "tokens",
)


def end_value(text, start):
    """Locate an encoded JSON value without decoding its contents."""
    depth, string, escape = 0, False, False
    i = start
    while i < len(text):
        c = text[i]
        if string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                string = False
        elif c == '"':
            string = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            if depth == 0:
                return i
            depth -= 1
        elif c == "," and depth == 0:
            return i
        i += 1
    if string or depth:
        raise ValueError("incomplete JSON value")
    return i


def fields(text):
    text = text.strip()
    if not text.startswith("{") or not text.endswith("}"):
        raise ValueError("expected complete JSON object")
    i, seen = 1, set()
    decoder = json.JSONDecoder()
    while i < len(text) - 1:
        while text[i].isspace():
            i += 1
        key, i = decoder.raw_decode(text, i)
        if not isinstance(key, str) or key in seen:
            raise ValueError("duplicate or nonstring JSON key")
        seen.add(key)
        while text[i].isspace():
            i += 1
        if text[i] != ":":
            raise ValueError("missing JSON colon")
        i += 1
        stop = end_value(text, i)
        yield key, text[i:stop]
        i = stop
        if text[i] == ",":
            i += 1
        else:
            break


def project(text, allowed):
    return {k: json.loads(raw) for k, raw in fields(text) if k in allowed}


def objects(text):
    text = text.strip()
    if not text.startswith("[") or not text.endswith("]"):
        raise ValueError("expected JSON array")
    i = 1
    while i < len(text) - 1:
        stop = end_value(text, i)
        yield text[i:stop]
        i = stop + 1


def check(condition, message):
    if not condition:
        raise ValueError(message)


def operation_check(cost, arm):
    for k in COUNTS:
        check(isinstance(cost[k], int) and cost[k] >= 0, "invalid operation counter: " + k)
    steps, rev, forwards = (cost[k] for k in ("settle_iters", "reverses", "full_forwards"))
    if arm == "SE-E":
        check(
            steps % 8 == 0 and rev == 9 * (steps // 8),
            "SE-E eight-step/nine-reverse accounting differs",
        )
    else:
        check(steps == 0, "SE-A unexpectedly settled errors")
    check(forwards >= rev, "missing full forwards for credit calls")


def cell(folder, c, plan, frozen, dimension, bindings, fresh_states):
    def read(name):
        p = folder / name
        raw = p.read_text()
        bindings[str(p.resolve())] = hashlib.sha256(raw.encode()).hexdigest()
        return raw

    cfg, finish = (json.loads(read(name)) for name in ("config.json", "finish.json"))
    check(finish["status"] == "complete", "finished cell did not complete")
    check(all(cfg[k] == v for k, v in c.items()), "coordinate/config differs")
    check(all(finish[k] == c[k] for k in ("dataset", "arm")), "finish coordinate differs")
    check(
        finish["items_completed"] == finish["items_planned"] == c["items"], "incomplete item count"
    )
    check((cfg["credit_iters"], cfg["error_lr"]) == (8, 0.1), "unexpected solver settings")
    check(
        cfg["population"] == "exposed historical S5; supplemental defect-correction replication",
        "exposure label differs",
    )
    check(
        cfg["scoring"] == "unchanged S5 primary; bounded text secondary",
        "scoring convention differs",
    )
    check(cfg["sources"] == plan["sources"], "cell/plan source identity differs")
    check(cfg["weights_sha256"] == WEIGHTS_SHA, "regenerated weight file differs")
    check(
        finish["base_hash_before"] == finish["base_hash_after"] == cfg["base_hash_before"],
        "base changed",
    )
    manifest = Path(cfg["manifest"])
    check(sha(manifest) == cfg["manifest_sha256"], "population manifest identity differs")
    bindings[str(manifest)] = cfg["manifest_sha256"]
    seeds = project(manifest.read_text(), {"named_seeds"})["named_seeds"][str(c["order"])]
    check(seeds == cfg["named_seeds"], "named seed differs from population manifest")
    ident = (c["dataset"], seeds["seed_cap_init"], c["arm"])
    if ident not in fresh_states:
        fresh = build_cap(
            SimpleNamespace(d=dimension, ledger=Ledger()),
            c["dataset"],
            c["arm"],
            seeds["seed_cap_init"],
            frozen,
        )
        fresh_states[ident] = fresh.state_hash()
        check(
            fresh.item_index == 0 and all(bs.bank.occupancy() == 0 for bs in fresh.banks.values()),
            "fresh constructor is occupied",
        )
    check(
        cfg["initial_state"] == fresh_states[ident],
        "initial memory differs from independently constructed empty state",
    )
    ids, sums = [], {k: 0 for k in COUNTS}
    for idx, line in enumerate(read("items.jsonl").splitlines()):
        schema = {k for k, _ in fields(line)}
        check(
            {"es", "gs", "bounded_es", "bounded_gs", "truncated", "paraphrases_truncated"}
            <= schema,
            "primary/secondary schema field missing",
        )
        item = project(line, {"item_id", "index", "dataset", "cost"})
        check(
            item["index"] == idx and item["dataset"] == c["dataset"], "item index/dataset differs"
        )
        ids.append(item["item_id"])
        operation_check(item["cost"], c["arm"])
        for k in COUNTS:
            sums[k] += item["cost"][k]
    check(
        ids == cfg["item_ids"] and len(ids) == c["items"] and len(set(ids)) == len(ids),
        "recorded item order/count differs",
    )
    decisions, reverse_sum, settle_sum = 0, 0, 0
    for line in read("decisions.jsonl").splitlines():
        cost = project(line, {"cost"})["cost"]
        operation_check(cost, c["arm"])
        reverse_sum += cost["reverses"]
        settle_sum += cost["settle_iters"]
        decisions += 1
    learning = finish["ledger"]["learning"]
    operation_check(learning, c["arm"])
    check(
        reverse_sum == sums["reverses"] == learning["reverses"],
        "decision/item/ledger reverse totals differ",
    )
    check(
        settle_sum == sums["settle_iters"] == learning["settle_iters"],
        "decision/item/ledger settling totals differ",
    )
    ledger = json.loads(read("cost.json"))
    for phase in ("learning", "query", "total"):
        for k in COUNTS:
            check(ledger[phase][k] == finish["ledger"][phase][k], "cost/finish ledger differs")
    for k in COUNTS:
        check(
            ledger["query"][k] + ledger["learning"][k] == ledger["total"][k],
            "ledger phase sum differs",
        )
    check(
        ledger["query"]["reverses"] == ledger["query"]["settle_iters"] == 0,
        "query unexpectedly used target credit",
    )
    check(
        math.isfinite(finish["elapsed_process_seconds"]) and finish["elapsed_process_seconds"] > 0,
        "invalid process time",
    )
    secondary = 0
    for line in read("secondary.jsonl").splitlines():
        parts = dict(fields(line))
        selected = json.loads(parts["item_ids"])
        check(all(i in set(ids) for i in selected), "secondary item outside stream")
        schemas = [{k for k, _ in fields(row)} for row in objects(parts["rows"])]
        check(
            len(schemas) == len(selected)
            and all({"es", "gs", "bounded_es", "bounded_gs"} <= s for s in schemas),
            "secondary schemas differ",
        )
        secondary += 1
    check(secondary > 0, "missing secondary rows")
    checkpoints = []
    for encoded in objects(read("checkpoints.json")):
        cp = project(encoded, {"tag", "items", "checkpoint_sha256", "state_hash"})
        snapshot = (
            Path(pccap.ASSETS_ROOT)
            / "runs"
            / folder.relative_to(ROOT / "results")
            / f"learner_{cp['tag']}.ckpt"
        )
        check(sha(snapshot) == cp["checkpoint_sha256"], "checkpoint bytes differ")
        bindings[str(snapshot)] = cp["checkpoint_sha256"]
        checkpoints.append(cp)
    check(
        any(x["tag"] == "end" and x["items"] == len(ids) for x in checkpoints),
        "missing final checkpoint",
    )
    pair = {
        k: cfg[k]
        for k in (
            "item_ids",
            "sources",
            "weights_sha256",
            "manifest_sha256",
            "named_seeds",
            "initial_state",
            "locality_prompts_sha256",
            "drift",
            "base_hash_before",
        )
    }
    return dict(
        cell=c,
        status="pass",
        pair_identity=pair,
        item_order_sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
        initial_state=cfg["initial_state"],
        base_hash=cfg["base_hash_before"],
        decisions=decisions,
        credit_calls=learning["reverses"] // 9 if c["arm"] == "SE-E" else learning["reverses"],
        secondary_records=secondary,
        checkpoints=checkpoints,
    )


def audit(group, output):
    group, output = Path(group).resolve(), Path(output)
    frozen, bindings = archive(), {}
    plan_path = group / "plan.json"
    plan = json.loads(plan_path.read_text())
    check(plan["cells"] == design(5), "not the declared 60-cell design")
    check(plan["sources"] == source_identities(), "runner source changed")
    for name, h in plan["sources"].items():
        path = ROOT / name
        check(sha(path) == h, "bound source changed: " + name)
        bindings[str(path)] = h
    weights = Path(frozen["base_checkpoints"]["epc"]["path"])
    check(sha(weights) == WEIGHTS_SHA, "weight file hash differs")
    bindings[str(weights)] = WEIGHTS_SHA
    bindings[str(plan_path)] = sha(plan_path)
    bindings[str(ARCHIVE)] = sha(ARCHIVE)
    with zipfile.ZipFile(weights) as z, z.open("wte.npy") as f:
        version = np.lib.format.read_magic(f)
        check(version in ((1, 0), (2, 0)), "unsupported weight header version")
        header_reader = (
            np.lib.format.read_array_header_1_0
            if version == (1, 0)
            else np.lib.format.read_array_header_2_0
        )
        shape, _, _ = header_reader(f)
    rows, waiting, errors, fresh = [], [], [], {}
    # Snapshot the finish inventory once; a currently running cell stays pending.
    completed = {p.parent.name for p in group.glob("*/finish.json")}
    planned_names = {
        f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}" for c in plan["cells"]
    }
    errors.extend(
        dict(cell=name, error="finished cell outside the planned design")
        for name in sorted(completed - planned_names)
    )
    for c in plan["cells"]:
        name = f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        if name not in completed:
            waiting.append(name)
            continue
        try:
            rows.append(cell(group / name, c, plan, frozen, shape[1], bindings, fresh))
        except (ValueError, KeyError, OSError, AttributeError) as exc:
            errors.append(dict(cell=name, error=str(exc)))
    paired, pending_pairs = [], []
    for c in plan["cells"][::2]:
        coord = tuple(c[k] for k in ("dataset", "realization", "order"))
        pair = [
            r
            for r in rows
            if tuple(r["cell"][k] for k in ("dataset", "realization", "order")) == coord
        ]
        if len(pair) != 2:
            pending_pairs.append(coord)
        elif pair[0]["pair_identity"] != pair[1]["pair_identity"]:
            errors.append(
                dict(
                    pair=coord,
                    error="paired items/calibration/seeds/base/fresh-state identities differ",
                )
            )
        else:
            paired.append(coord)
    for r in rows:
        del r["pair_identity"]
    if len({r["base_hash"] for r in rows}) > 1:
        errors.append(dict(error="completed cells do not share one base tensor identity"))
    for path, h in bindings.items():
        check(sha(path) == h, "audited evidence changed during audit: " + path)
    report = dict(
        checked_at=datetime.now(ZoneInfo("America/New_York")).isoformat(),
        status="fail" if errors else "pass_complete" if not waiting else "pass_finished_subset",
        population="exposed historical S5; supplemental defect-correction replication",
        planned=60,
        finished=len(completed),
        audited=len(rows),
        paired=len(paired),
        pending=waiting,
        pending_pairs=pending_pairs,
        errors=errors,
        cells=rows,
        sources_sha256=bindings,
        efficacy_values_read=False,
        model_execution=False,
        limitation="Present recorded identities and accounting, not a replay or proof of historical authenticity; no full-run certificate until all 60 finish.",
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    text = f"# X24 — PC-v0 replication integrity\n\n{report['checked_at']} — **{report['status']}**.\n\n"
    text += f"{len(rows)}/{len(completed)} finished cells audited; {len(paired)} complete matched pairs; {len(waiting)} planned cells pending. Population: exposed historical S5, supplemental defect-correction replication.\n\n"
    text += "Item IDs/order, archived calibration and named seeds, unchanged base hashes, independently constructed fresh-memory hashes, planned eight-step credit, primary/secondary schema and operation accounting are checked. The SE-E reverse count is nine per eight settling steps, with at least nine full forwards per credit; extra prediction/acceptance forwards remain separate. Decision, item and final ledger credit counts agree for passing cells.\n\n"
    text += "Only identity, schema and cost fields were decoded from JSON containing outcomes; metrics and secondary-summary files were not opened. No efficacy result is read or reported. Full-file hashes are retained. Source/config evidence is not a signed historical authenticity proof. Rerun on the complete set before PC-8.\n\n"
    text += (
        "| Cell | Check |\n| --- | --- |\n"
        + "\n".join(f"| {r['cell']} | PASS |" for r in rows)
        + "\n"
    )
    if errors:
        text += "\n## Findings\n\n" + "\n".join(str(e) for e in errors) + "\n"
    (output / "report.md").write_text(text)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=str(OUTPUT / "replication-60-20260927"))
    parser.add_argument("--output", default=str(ROOT / "logs/r1_x24"))
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="exit 2 for a passing subset; final PC-8 gate",
    )
    a = parser.parse_args()
    r = audit(a.run, a.output)
    print(json.dumps({k: r[k] for k in ("status", "finished", "audited", "paired", "errors")}))
    if r["errors"]:
        raise SystemExit(1)
    if a.require_complete and r["status"] != "pass_complete":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
