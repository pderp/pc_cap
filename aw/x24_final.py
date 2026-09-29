"""Final metadata-only checks of the 60 v0 and four fixed-v5 default cells."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
from pathlib import Path

from aw import x24_replication as v0
from aw.pc_historical import ROOT, SourceRoot, Sources, bind, sha
from pccap.harness.snapshot import restore
from pccap.revision_v1.analysis import digest

V0 = ROOT / "results/additional_work/PC-v0/replication-60-20260927"
V1 = ROOT / "results/additional_work/PC-v1/replication-4-20260927"


def read(path, sources):
    raw = Path(path).read_text()
    sources.bindings[str(Path(path).resolve())] = sha(path)
    return raw


def fixed_v5(group, sources):
    driver = sources.module("pc_v1_run")
    plan = json.loads(read(group / "plan.json", sources))
    v0.check(plan == driver.plan(), "fixed-v5 recorded plan differs from historical design")
    sources.check(plan["sources"])
    rows, pairs = [], {}
    for c in plan["cells"]:
        folder = group / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        cfg, finish = (
            json.loads(read(folder / n, sources)) for n in ("config.json", "finish.json")
        )
        v0.check(cfg["cell"] == c and cfg["sources"] == plan["sources"], "v5 cell/plan mismatch")
        v0.check(cfg["population"] == plan["population"], "v5 exposure label differs")
        v0.check(
            finish["config_sha256"] == sha(folder / "config.json"), "v5 config binding differs"
        )
        v0.check(
            finish["status"] == "complete"
            and finish["items_completed"] == finish["items_planned"] == 300,
            "v5 incomplete cell",
        )
        v0.check(
            finish["checkpoints_completed"] == cfg["checkpoints"] == [100, 300],
            "v5 checkpoint inventory",
        )
        for field, prefix in (("base_sha256", "base_hash"), ("reader_sha256", "reader_hash")):
            v0.check(
                cfg[field] == finish[prefix + "_before"] == finish[prefix + "_after"],
                "v5 immutable hash differs",
            )
        spec = plan["recipes"][c["dataset"]]
        v0.check(cfg["inputs"] == spec, "v5 input recipe differs")
        for k in ("construction_recipe", "payload_recipe", "payload"):
            sources.resolve(spec[k]["path"], spec[k]["sha256"])
        construction = spec["construction"]
        for name, h in construction["base"]["files"].items():
            sources.resolve(Path(construction["base"]["path"]) / name, h)
        for k in ("weights", "stop_tokens"):
            sources.resolve(construction[k]["path"], construction[k]["sha256"])
        sources.check(cfg["profile_sources"])
        # Payload contains no treatment outcomes. Check exact reserved item prefix and endpoints.
        payload = json.loads(Path(spec["payload"]["path"]).read_bytes())
        expected_ids = [x["item_id"] for x in payload["items"][:300]]
        endpoints = {k: payload["endpoints"][k] for k in ("locality", "near_miss", "revision")}
        v0.check(cfg["endpoints_sha256"] == digest(endpoints), "v5 endpoint inventory changed")
        items = [
            v0.project(line, {"item_id", "index"})
            for line in read(folder / "items.jsonl", sources).splitlines()
        ]
        ids = [it["item_id"] for it in items]
        v0.check(
            ids == cfg["item_ids"] == expected_ids and len(set(ids)) == 300, "v5 item order differs"
        )
        v0.check([it["index"] for it in items] == list(range(1, 301)), "v5 item indices differ")
        snapshots = []
        for n in (100, 300):
            raw = read(folder / f"checkpoint-{n}.json", sources)
            cp = v0.project(raw, {"checkpoint", "snapshot", "state_sha256"})
            hist = next(encoded for key, encoded in v0.fields(raw) if key == "history")
            cp_ids = [v0.project(x, {"item_id"})["item_id"] for x in v0.objects(hist)]
            v0.check(cp["checkpoint"] == n and cp_ids == ids[:n], "v5 checkpoint order differs")
            b = cp["snapshot"]
            sources.resolve(b["path"], b["sha256"])
            st = restore(Path(b["path"]).read_bytes(), expected_hash=b["state_sha256"])
            v0.check(cp["state_sha256"] == b["state_sha256"], "v5 checkpoint state differs")
            v0.check(
                b["base_sha256"] == cfg["base_sha256"]
                and b["reader_sha256"] == cfg["reader_sha256"],
                "v5 snapshot model/reader differs",
            )
            v0.check(
                b["credit"] == {"SE-A": "adjoint", "SE-E": "error"}[c["arm"]] and b["iters"] == 8,
                "v5 credit rule differs",
            )
            v0.check(
                json.loads(st.scalars["config"]) == cfg["semantic_config"],
                "snapshot semantic config differs",
            )
            if n == 300:
                v0.check(
                    b["state_sha256"] == finish["state_sha256"],
                    "v5 final checkpoint/finish differs",
                )
            snapshots.append(b)
        phases = [
            v0.project(line, {"phase", "status", "state_before", "state_after"})
            for line in read(folder / "phases.jsonl", sources).splitlines()
        ]
        v0.check(
            phases[0]["state_before"] == cfg["initial_state"], "v5 initial state witness differs"
        )
        v0.check(all(p["status"] == "complete" for p in phases), "v5 incomplete phase")
        v0.check(
            all(
                p["phase"].startswith("edit:") or p["state_before"] == p["state_after"]
                for p in phases
            ),
            "v5 assay changed stream memory",
        )
        v0.check(
            all(a["state_after"] == b["state_before"] for a, b in zip(phases, phases[1:])),
            "v5 phase state continuity differs",
        )
        v0.check(
            phases[-1]["state_after"] == finish["state_sha256"], "v5 final phase state differs"
        )
        ledger = finish["ledger"]
        v0.check(
            ledger["query"]["reverses"] == ledger["query"]["settle_iters"] == 0, "v5 query credit"
        )
        for k in v0.COUNTS:
            v0.check(
                ledger["learning"][k] + ledger["query"][k] == ledger["total"][k], "v5 ledger sum"
            )
        # v5 keeps initial adjoint code gradients; do NOT apply the v0 reverse/settling equality.
        sem = dict(cfg["semantic_config"])
        acquisition = sem.pop("pc_acquisition", None)
        v0.check(
            acquisition
            == (
                dict(credit="error", energy="SD-24 corrected", error_lr=0.1, iters=8)
                if c["arm"] == "SE-E"
                else None
            ),
            "v5 acquisition metadata differs",
        )
        identity = dict(
            inputs=spec,
            ids=ids,
            endpoints=cfg["endpoints_sha256"],
            initial_inference=cfg["initial_inference_state"],
            semantics=sem,
            base=cfg["base_sha256"],
            reader=cfg["reader_sha256"],
            max_new=cfg["max_new"],
        )
        pairs.setdefault(c["dataset"], []).append(identity)
        rows.append(
            dict(
                cell=c,
                status="pass",
                snapshots=snapshots,
                initial_inference=cfg["initial_inference_state"],
            )
        )
    v0.check(
        len(rows) == 4 and all(len(p) == 2 and p[0] == p[1] for p in pairs.values()),
        "v5 pairing differs",
    )
    return dict(
        status="pass_complete",
        audited=4,
        paired=2,
        cells=rows,
        population=plan["population"],
        efficacy_values_read=False,
        model_execution=False,
        limitation="Recorded v5 empty initial-state witness and paired inference hashes; no independent real-base replay.",
    )


def audit(output):
    output = Path(output)
    sources = Sources()
    historical = sources.module("pc_v0")
    expected = historical.source_identities()
    sources.check(expected)
    run = bind(
        v0.audit, ROOT=SourceRoot(sources, expected), source_identities=historical.source_identities
    )
    original = run(V0, output / "v0")
    v0.check(original["status"] == "pass_complete", "v0 final audit did not pass")
    fixed = fixed_v5(V1, sources)
    sources.bindings.update(original["sources_sha256"])
    sources.verify_unchanged()
    result = dict(
        status="pass_complete",
        v0=original,
        v1=fixed,
        sources_sha256=sources.bindings,
        historical_source_substitutions=sources.substitutions,
        efficacy_values_read=False,
        model_execution=False,
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "report.md").write_text(
        "# X24 final integrity audit\n\nPASS: 60 v0 cells / 30 pairs and four fixed-v5 cells / two pairs.\n\n"
        "No efficacy fields decoded by this audit and no model executed. v0 checks retain the prior X24 scope. "
        "v5 checks item order against the sealed payload, both checkpoint inventories and snapshot hashes, "
        "immutable base/reader hashes, paired inference configuration, phase state continuity and read-only assays.\n\n"
        "The original runner/reader bytes are explicitly resolved through the five-file PC-9/10 archive; "
        "all other source drift fails. report.json records every resolved path and digest. "
        "This is recorded-integrity evidence, not a replay or historical-authenticity proof.\n"
    )
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default=str(ROOT / "logs/r1_x24/final"))
    p.add_argument(
        "--require-complete", action="store_true", help="always required by this final-only audit"
    )
    a = p.parse_args()
    result = audit(a.output)
    print(
        json.dumps(
            dict(status=result["status"], v0=result["v0"]["audited"], v1=result["v1"]["audited"])
        )
    )


if __name__ == "__main__":
    main()
