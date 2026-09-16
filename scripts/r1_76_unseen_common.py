"""R1-76 fixed-outside development occupancy assay (CPU preparation; owner execution).

One deterministic inventory, one incremental edit stream, outside100 held fixed at
100/300/1000. No final reservation access; no model is constructed by preparation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import time
import unicodedata
from collections import Counter
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts.r1_75_analysis_stage4_v1 import wilson

from pccap.revision_v1.analysis import digest
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.stage4_assays import CellAssays
from pccap.revision_v1.stage4_cell import _ledger

ROOT = driver.ROOT
RESOURCE_ROOT = ROOT.parent / "assets/runs/pc_cap/R1/r1_76_common"
MODE = "development_common_outside_population"
CHECKPOINTS = [100, 300, 1000]
TRAIN_FILES = {
    ds: ROOT / f"manifests/revision_v1/train_pool_{ds}_{'v3' if ds == 'mquake' else 'v1'}.json"
    for ds in ("zsre", "counterfact", "mquake")
}


def norm(s):
    if not isinstance(s, str) or not s.strip():
        raise ValueError("nonempty metadata required")
    return " ".join(unicodedata.normalize("NFKC", s).casefold().split())


def keys(row):
    return (norm(row["item_id"]), norm(row["fact_id"]), norm(row["subject"]), norm(row["prompt"]))


def rowsets(rows):
    sets = [set() for _ in range(4)]
    for row in rows:
        for s, key in zip(sets, keys(row), strict=True):
            s.add(key)
    return sets


def choose_population(
    dataset,
    development,
    tail,
    training,
    *,
    checkpoints=CHECKPOINTS,
    outside_n=100,
    test_fixture=False,
):
    if (
        checkpoints != sorted(set(checkpoints))
        or any(type(n) is not int or n < 1 for n in checkpoints)
        or not checkpoints
    ):
        raise ValueError("positive ordered checkpoints required")
    if type(outside_n) is not int or outside_n < 1:
        raise ValueError("positive outside size required")
    banned = rowsets(training)
    for row in training:
        for q in [*row.get("paraphrases", []), *row.get("locality_prompts", [])]:
            if isinstance(q, str) and q.strip():
                banned[3].add(norm(q))
    used = [set() for _ in range(4)]
    safe = []
    excluded = Counter()
    for origin, rows in (("development", development), ("training_pool_tail", tail)):
        for row in rows:
            if row.get("dataset", dataset) != dataset:
                raise ValueError("mixed dataset candidates")
            k = keys(row)
            if any(key in s for key, s in zip(k, banned, strict=True)):
                excluded["training_item_or_exact_query_overlap"] += 1
                continue
            if any(key in s for key, s in zip(k, used, strict=True)):
                excluded["duplicate_item_fact_subject_or_prompt"] += 1
                continue
            for key, s in zip(k, used, strict=True):
                s.add(key)
            safe.append({**copy.deepcopy(row), "common_population_origin": origin})
    need = max(checkpoints) + outside_n
    if len(safe) < need:
        raise ValueError(
            f"{dataset}: only {len(safe)} eligible reader-training-disjoint rows; need {need} = {max(checkpoints)} edits + {outside_n} outside; no model constructed"
        )
    edits = safe[: max(checkpoints)]
    outside = safe[max(checkpoints) : need]
    p = {
        "schema_version": 1,
        "mode": MODE,
        "dataset": dataset,
        "checkpoints": list(checkpoints),
        "outside_n": outside_n,
        "edits": edits,
        "outside": outside,
        "planned_outside_ids": [r["item_id"] for r in outside],
        "query_population_sha256": digest(
            [{k: r[k] for k in ("item_id", "fact_id", "subject", "prompt")} for r in outside]
        ),
        "selection": {
            "rule": "source-order development then source-order training-pool tail; first1000 edits then next100 outside after all overlaps excluded",
            "candidate_safe_count": len(safe),
            "excluded_counts": dict(excluded),
            "outcome_dependent": False,
            "limits": "disjoint from declared selected-reader training items and exact training query text; broader alias or historical query exposure not certified",
        },
        "launch_authorized": False,
        "confirmatory": False,
    }
    validate_population(p, test_fixture=test_fixture)
    return p


def validate_population(p, *, test_fixture=False):
    if (
        p.get("mode") != MODE
        or p.get("confirmatory") is not False
        or p.get("launch_authorized") is not False
    ):
        raise PermissionError("unsealed nonconfirmatory population required")
    cp = p["checkpoints"]
    if not cp or cp != sorted(set(cp)) or any(type(n) is not int or n < 1 for n in cp):
        raise ValueError("invalid checkpoint schedule")
    partial_mquake = (
        p.get("decision") == "DEC-056"
        and p.get("dataset") == "mquake"
        and cp == [100, 300]
        and p.get("missing_checkpoints") == [1000]
        and all(
            r.get("exposure_label")
            == "new to the selected reader's training; historically exposed elsewhere"
            for r in p["edits"] + p["outside"]
        )
    )
    if not test_fixture and ((cp != CHECKPOINTS and not partial_mquake) or p["outside_n"] != 100):
        raise ValueError("production full cadence or labelled DEC-056 MQuAKE100/300 required")
    if len(p["edits"]) != max(cp) or len(p["outside"]) != p["outside_n"]:
        raise ValueError("complete largest edit/outside population required")
    rows = p["edits"] + p["outside"]
    for index, values in enumerate(rowsets(rows)):
        if len(values) != len(rows):
            raise ValueError(f"duplicate/overlapping identity dimension {index}")
    if p["planned_outside_ids"] != [r["item_id"] for r in p["outside"]]:
        raise ValueError("outside IDs/order changed")
    q = digest(
        [{k: r[k] for k in ("item_id", "fact_id", "subject", "prompt")} for r in p["outside"]]
    )
    if p["query_population_sha256"] != q:
        raise ValueError("outside prompt population changed")
    if any(r.get("dataset", p["dataset"]) != p["dataset"] for r in rows):
        raise ValueError("dataset identity mismatch")
    return p


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def prepare(dataset):
    sources = {}

    def read(path):
        path = Path(path).resolve()
        if not path.is_relative_to(ROOT) or "confirm" in path.parts:
            raise PermissionError("explicit development sources only")
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        sources[str(path)] = h
        return json.loads(raw)

    primary = read(ROOT / "manifests/revision_v1/primary_condition_v5.json")
    summary = read(ROOT / "results/R1/pilot/r1_50_stream_sel6_text_s2/summary.json")
    args = summary["args"]
    if (
        args["tag"] != primary["weights"]["run"]
        or args["pool_items"] != 1000
        or args["seed"] != 2
        or summary.get("memory_guard_abort")
    ):
        raise ValueError("selected training-prefix provenance mismatch")
    pools = {ds: read(path) for ds, path in TRAIN_FILES.items()}
    training = []
    for ds, path in TRAIN_FILES.items():
        if sources[str(path)] != primary["pools"][path.stem]:
            raise ValueError("primary training pool binding mismatch")
        rows = pools[ds]["items"][: args["pool_items"]]
        bank = next(b for b in summary["banks"] if (ROOT / b["pool"]).resolve() == path)
        if bank["identity"]["n_items"] != len(rows):
            raise ValueError("training-prefix count mismatch")
        training.extend(rows)
    dev = read(ROOT / f"manifests/dev/{dataset}_dev{'_v3b' if dataset == 'mquake' else ''}.json")
    p = choose_population(
        dataset, dev["items"], pools[dataset]["items"][args["pool_items"] :], training
    )
    p["sources_sha256"] = sources
    p["primary_reference"] = {
        "path": str(ROOT / "manifests/revision_v1/primary_condition_v5.json"),
        "sha256": sources[str(ROOT / "manifests/revision_v1/primary_condition_v5.json")],
    }
    p["training_prefix_counts"] = {ds: min(1000, len(pool["items"])) for ds, pool in pools.items()}
    for path, h in sources.items():
        if sha(path) != h:
            raise ValueError("preparation source changed")
    return p


def load_spec(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT / "docs/tasks"):
        raise PermissionError("repo development spec required")
    spec = json.loads(path.read_bytes())
    resource = Path(spec["population"]["path"]).resolve()
    if not resource.is_relative_to(RESOURCE_ROOT):
        raise PermissionError("explicit common-population resource required")
    if sha(resource) != spec["population"]["sha256"]:
        raise ValueError("population resource binding mismatch")
    for source, h in spec["runner_bindings"].items():
        if sha(ROOT / source) != h:
            raise ValueError("runner dependency changed")
    p = validate_population(json.loads(resource.read_bytes()))
    if (
        digest(p) != spec["population_identity"]
        or p["primary_reference"] != spec["primary_reference"]
    ):
        raise ValueError("population spec identity mismatch")
    allowed_metadata_resources = set()
    if p.get("decision") == "DEC-056" and p.get("dataset") == "mquake":
        from pccap.bases.gpt2_jax import DEFAULT_SNAPSHOT

        allowed_metadata_resources = {
            (ROOT.parent / "assets/data/prepared/revision_v1/r1_d4_v1/items.jsonl").resolve(),
            (DEFAULT_SNAPSHOT / "tokenizer.json").resolve(),
            (DEFAULT_SNAPSHOT / "config.json").resolve(),
        }
    for source, h in p["sources_sha256"].items():
        source = Path(source).resolve()
        if "confirm" in source.parts or (
            not source.is_relative_to(ROOT) and source not in allowed_metadata_resources
        ):
            raise PermissionError("development metadata source required")
        if sha(source) != h:
            raise ValueError("training/development source changed")
    return p, spec


def paired_occupancy(reports):
    if len(reports) < 2:
        return []
    baseline = reports[0]
    out = []
    for row in reports[1:]:
        a, b = baseline["report"], row["report"]
        if (
            a["requested_item_ids_sha256"] != b["requested_item_ids_sha256"]
            or a["pool_query_metadata_sha256"] != b["pool_query_metadata_sha256"]
        ):
            raise ValueError("outside population differs across checkpoints")
        earlier = {r["item_id"]: r for r in a["rows"]}
        later = {r["item_id"]: r for r in b["rows"]}
        n = a["summary"]["expected_n"]
        valid = (
            len(earlier) == len(later) == n
            and set(earlier) == set(later)
            and all(
                r.get("status") == "ok"
                and r.get("firing_status") == "ok"
                and type(r.get("false_fire")) is bool
                for r in [*earlier.values(), *later.values()]
            )
        )
        result = {
            "from_attempts": baseline["attempted_edits"],
            "to_attempts": row["attempted_edits"],
            "planned_pairs": n,
            "common_outside_sha256": row["query_population_sha256"],
            "exact_occupancy_pair": baseline["exact_occupancy"] and row["exact_occupancy"],
            "delta_fire_rate": None,
            "new_fires": None,
            "ceased_fires": None,
            "classification": "descriptive_U14_unadmitted",
        }
        if valid and result["exact_occupancy_pair"]:
            result.update(
                delta_fire_rate=sum(
                    int(later[i]["false_fire"]) - int(earlier[i]["false_fire"]) for i in earlier
                )
                / n,
                new_fires=sum(
                    later[i]["false_fire"] and not earlier[i]["false_fire"] for i in earlier
                ),
                ceased_fires=sum(
                    earlier[i]["false_fire"] and not later[i]["false_fire"] for i in earlier
                ),
            )
        out.append(result)
    return out


def run_population(
    adapter,
    tokenizer,
    population,
    output,
    *,
    expected_identity=None,
    verify_inputs=None,
    test_fixture=False,
    max_new=32,
    execution_metadata=None,
):
    p = copy.deepcopy(validate_population(population, test_fixture=test_fixture))
    if adapter.condition != "R1_learned_ff":
        raise ValueError("selected learned-reader assay only")
    identity = adapter.identity()
    if test_fixture and identity["base_sha256"] != "tiny":
        raise PermissionError("test fixture requires TinyBase")
    if expected_identity is not None and identity != expected_identity:
        raise ValueError("adapter identity mismatch")
    if not test_fixture and (expected_identity is None or verify_inputs is None or max_new != 32):
        raise ValueError(
            "production execution requires bound identity/input verifier and32-token decoding"
        )
    if adapter.learner.store.records:
        raise ValueError("empty starting memory required")
    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(ROOT / "results/R1"):
        raise FileExistsError("new result directory required")
    items = [as_edit(row, tokenizer) for row in p["edits"]]
    bound = copy.deepcopy(p)
    fingerprint = driver.memory_identity(adapter)
    output.mkdir(parents=True)

    def write(name, obj):
        return driver.durable_json(output / name, {"mode": "development_common_outside_run", **obj})

    def verify():
        if population != bound:
            raise ValueError("population mutated during execution")
        if verify_inputs is not None:
            verify_inputs()
        if adapter.identity() != identity:
            raise RuntimeError("immutable identity changed")

    start = time.monotonic()
    reports = []
    history = []
    outcomes = Counter()
    write(
        "population-binding.json",
        {
            "population_identity": digest(p),
            "query_population_sha256": p["query_population_sha256"],
            "planned_edit_ids": [r["item_id"] for r in p["edits"]],
            "planned_outside_ids": p["planned_outside_ids"],
            "adapter_identity": identity,
            "checkpoints": p["checkpoints"],
            "execution_metadata": execution_metadata,
        },
    )
    assays = CellAssays(adapter, tokenizer, max_new=max_new)
    definition = {"rows": p["outside"], "expected_ids": p["planned_outside_ids"]}
    pool = p["edits"] + p["outside"]
    try:
        verify()
        for n, item in enumerate(items, 1):
            t = time.monotonic()
            before = _ledger(adapter)
            out = adapter.update_item(item)
            history.append(item)
            outcomes[str(out.code)] += 1
            write(
                f"edit-{n:04d}.json",
                {
                    "item_id": item.item_id,
                    "outcome": str(out.code),
                    "codes": list(out.codes),
                    "returned_cost": out.cost.as_dict(),
                    "ledger_before": before,
                    "ledger_after": _ledger(adapter),
                    "wall_seconds": time.monotonic() - t,
                },
            )
            if driver.memory_identity(adapter) != fingerprint:
                raise RuntimeError("immutable memory identity changed")
            if out.code == "resource_stop" or any(
                str(code).startswith("resource_failure:") for code in out.codes
            ):
                raise RuntimeError("resource failure; retain charged work, no replacement items")
            if n not in p["checkpoints"]:
                continue
            state = adapter.state_hash()
            report = assays.unseen(definition, pool, history, str(n), digest(p))
            if adapter.state_hash() != state:
                raise RuntimeError("unseen query mutated memory")
            actual = adapter.observe()["active_records"]
            exact = actual == n
            full = report["summary"]["false_fire_rate_full_inventory"]
            record = {
                "attempted_edits": n,
                "target_records": n,
                "active_records": actual,
                "exact_occupancy": exact,
                "exact_size_status": "complete" if exact and full is not None else "unavailable",
                "exact_size_false_fire_rate": full if exact else None,
                "query_population_sha256": p["query_population_sha256"],
                "report": report,
                "wilson_evaluated": wilson(
                    report["summary"]["false_fires"], report["summary"]["firing_observed_n"]
                ),
                "state_sha256": state,
                "ledger": _ledger(adapter),
            }
            verify()
            write(f"checkpoint-{n}.json", record)
            reports.append(record)
        verify()
        result = {
            "status": "complete_attempted_stream",
            "dataset": p["dataset"],
            "attempted_edits": len(history),
            "checkpoints": [
                {
                    "attempted_edits": r["attempted_edits"],
                    "active_records": r["active_records"],
                    "exact_size_status": r["exact_size_status"],
                    "exact_size_false_fire_rate": r["exact_size_false_fire_rate"],
                    "query_population_sha256": r["query_population_sha256"],
                }
                for r in reports
            ],
            "paired_occupancy": paired_occupancy(reports),
            "outcomes": dict(outcomes),
            "wall_seconds": time.monotonic() - start,
            "ledger": _ledger(adapter),
            "limits": [
                "no confirmatory admission or occupancy-flatness claim",
                "no automatic resume; do not overwrite or merge attempts",
                "all100 outside IDs held fixed and excluded from entire largest edit inventory",
                "missing exact target occupancy remains unavailable",
            ],
        }
        write("result.json", result)
        return result
    except BaseException as exc:
        write(
            "failure.json",
            {
                "error_type": type(exc).__name__,
                "reason": str(exc),
                "attempted_edits": len(history),
                "completed_checkpoints": [r["attempted_edits"] for r in reports],
                "ledger": _ledger(adapter),
                "wall_seconds": time.monotonic() - start,
            },
        )
        raise


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prepare-dataset", choices=tuple(TRAIN_FILES))
    ap.add_argument("--population-output", type=Path)
    ap.add_argument("--spec-output", type=Path)
    ap.add_argument("--spec", type=Path)
    ap.add_argument("--recipe", type=Path)
    ap.add_argument("--recipe-sha256")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--projected-seconds", type=float)
    a = ap.parse_args(argv)
    if a.prepare_dataset:
        if a.execute or a.spec or a.recipe or not a.population_output or not a.spec_output:
            ap.error("preparation requires new population/spec outputs and no execution recipe")
        resource = a.population_output.resolve()
        specpath = a.spec_output.resolve()
        if (
            resource.exists()
            or not resource.is_relative_to(RESOURCE_ROOT)
            or specpath.exists()
            or not specpath.is_relative_to(ROOT / "docs/tasks")
        ):
            ap.error("new explicit resource and docs/tasks spec paths required")
        p = prepare(a.prepare_dataset)
        resource.parent.mkdir(parents=True, exist_ok=True)
        with resource.open("x") as f:
            json.dump(p, f, indent=2, sort_keys=True, allow_nan=False)
            f.write("\n")
        spec = {
            "task": "R1-76",
            "status": "prepared_not_executed",
            "population": {"path": str(resource), "sha256": sha(resource)},
            "population_identity": digest(p),
            "primary_reference": p["primary_reference"],
            "dataset": p["dataset"],
            "checkpoints": p["checkpoints"],
            "outside_n": p["outside_n"],
            "model_calls": 0,
            "gpu_seconds": 0,
            "launch_authorized": False,
            "no_final_reservations_read": True,
            "runner_bindings": {
                name: sha(ROOT / name)
                for name in (
                    "scripts/r1_76_unseen_common.py",
                    "scripts/r1_75_analysis_stage4_v1.py",
                )
            },
        }
        with specpath.open("x") as f:
            json.dump(spec, f, indent=2, sort_keys=True)
            f.write("\n")
        print(json.dumps(spec, indent=2))
        return 0
    if not a.spec:
        ap.error("--spec required")
    p, spec = load_spec(a.spec)
    if not a.execute:
        print(
            json.dumps(
                {
                    "dataset": p["dataset"],
                    "checkpoints": p["checkpoints"],
                    "outside_n": p["outside_n"],
                    "model_constructed": False,
                }
            )
        )
        return 0
    if (
        not a.recipe
        or not a.recipe_sha256
        or not a.output
        or a.projected_seconds is None
        or not math.isfinite(a.projected_seconds)
        or a.projected_seconds <= 0
    ):
        ap.error("execution needs recipe/hash, new output and positive finite projected-seconds")
    out = a.output.resolve()
    if out.exists() or not out.is_relative_to(ROOT / "results/R1"):
        ap.error("new result directory under results/R1 required")
    manifest, _ = driver.load_development_cell(a.recipe, a.recipe_sha256)
    primary = json.loads(Path(p["primary_reference"]["path"]).read_text())
    if (
        manifest["cell"]["condition"] != "R1_learned_ff"
        or manifest["cell"]["dataset"] != p["dataset"]
        or manifest["construction"]["weights"]["sha256"] != primary["weights"]["sha256"]
    ):
        raise ValueError("same dataset and selected-primary constructor required")

    def verify_inputs():
        q, s = load_spec(a.spec)
        if q != p or s != spec:
            raise ValueError("spec changed")
        driver.load_development_cell(a.recipe, a.recipe_sha256)

    # All population/recipe availability checks happen before lease or model construction.
    from scripts.r1_61_cell_driver import construct_owner_adapter

    from pccap.harness.lease import gpu_lease

    with gpu_lease("R1-76:" + out.name, stage="R1", projected_seconds=a.projected_seconds):
        adapter, tok = construct_owner_adapter(manifest)
        result = run_population(
            adapter,
            tok,
            p,
            out,
            expected_identity=manifest["adapter_identity"],
            verify_inputs=verify_inputs,
            execution_metadata={
                "spec": {"path": str(a.spec.resolve()), "sha256": sha(a.spec)},
                "recipe": {"path": str(a.recipe.resolve()), "sha256": a.recipe_sha256},
                "runner_bindings": spec["runner_bindings"],
            },
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
