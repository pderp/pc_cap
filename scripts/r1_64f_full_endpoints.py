"""CPU-only full-challenge development recipes; no fresh population or model execution."""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts import r1_d9_receipt_core as core
from scripts import r1_d9f_allocation as allocation
from scripts.r1_64b_comparator_recipes import metadata_identity
from scripts.r1_73b_comparator_recipes import verify_calibration
from scripts.r1_d9_layouts import entry
from scripts.r1_d9_receipts import planned_compositions, read_resource, ref
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10c_endpoints import catalog_from_rows, construct, role_plan
from scripts.r1_locality_contract import validate_locality

from pccap.contracts import Budget
from pccap.data.tokenize import GPT2Tokenizer
from pccap.metrics.editing import normalize_answer
from pccap.revision_v1.checkpoint_identity import checkpoint_tree
from pccap.revision_v1.development_cell import BANNER, MODE, PAYLOAD_ROOT

SEED = 64028  # declared development allocation seed; never search for a better seed
COUNTS = {**core.ROLES, "edits": 300}
SOURCES = {
    "zsre": ["manifests/dev/zsre_dev.json", "manifests/revision_v1/train_pool_zsre_v1.json"],
    "counterfact": [
        "manifests/dev/counterfact_dev.json",
        "manifests/revision_v1/train_pool_counterfact_v1.json",
    ],
    "mquake": [
        "manifests/dev/mquake_dev_v3b.json",
        "manifests/revision_v1/train_pool_mquake_v3.json",
        "manifests/revision_v1/train_pool_mquake_v2.json",
        "manifests/dev/mquake_dev.json",
    ],
}


def prior(row):
    answer = row.get("target_true", row.get("alt"))
    return answer.get("str") if isinstance(answer, dict) else answer


def pools(tokenizer, limits):
    used, ids, facts, bindings, result, source_audit = set(), set(), set(), {}, {}, {}
    for ds in core.DATASETS:
        result[ds] = []
        reasons = Counter()
        for name in SOURCES[ds]:
            path = ROOT / name
            b = ref(path)
            bindings[b["path"]] = b["sha256"]
            for original in json.loads(path.read_text())["items"]:
                subject = normalize_answer(original["subject"])
                if (
                    not subject
                    or subject in used
                    or original["item_id"] in ids
                    or original["fact_id"] in facts
                ):
                    reasons["duplicate_entity_item_or_fact"] += 1
                    continue
                if not original.get("paraphrases"):
                    reasons["no_paraphrase"] += 1
                    continue
                row = dict(
                    original,
                    source_record_sha256=core.content_digest(original),
                    development_source=name,
                    development_only=True,
                )
                plan = role_plan(row, prior(row), tokenizer, limits)
                row.update(
                    _entity=core.content_digest(subject),
                    _canonical_subject=subject,
                    _roles=plan["roles"],
                    _stratum="exposed_development",
                )
                used.add(subject)
                ids.add(row["item_id"])
                facts.add(row["fact_id"])
                result[ds].append(row)
        source_audit[ds] = dict(
            unique_subjects=len(result[ds]),
            omitted=dict(reasons),
            role_capacity=dict(Counter(role for r in result[ds] for role in r["_roles"])),
        )
    return result, bindings, source_audit


def filter_locality(reservation):
    """Source-derived prompts only; remove full-stream collisions before construction."""
    removed = []
    groups = {(g["dataset"], g["role"]): g for g in reservation["allocations"]}
    for ds in core.DATASETS:
        forbidden = {
            text
            for r in groups[ds, "edits"]["records"]
            for text in [r["prompt"], *r["paraphrases"]]
        }
        group = groups[ds, "outside"]
        for meta, row in zip(group["items"], group["records"], strict=True):
            old = list(row.get("locality_prompts", []))
            row["locality_prompts"] = [p for p in old if p not in forbidden]
            if old != row["locality_prompts"]:
                removed.append(
                    dict(
                        dataset=ds,
                        item_id=row["item_id"],
                        excluded=[p for p in old if p in forbidden],
                    )
                )
            meta["payload_sha256"] = core.content_digest(row)
    return removed


def recipe(dataset, condition, payload_binding, sources):
    if condition == "R1_learned_ff":
        parent = ROOT / "docs/tasks/R1-64e/R1-64e-zsre-primary-v5.recipe.json"
    elif dataset == "mquake":
        parent = ROOT / "docs/tasks/R1-73d-post77d/R1-73d-mquake-v0_stable.recipe.json"
    else:
        parent = ROOT / "docs/tasks/R1-64e/R1-64e-zsre-v0_stable.recipe.json"
    value = json.loads(parent.read_text())
    if value["code_sha256"] != driver.code_identity():
        raise ValueError("current driver recipe required")
    for key in list(value):
        if key.startswith("r1_") or key == "integrity_rebind":
            del value[key]
    if dataset == "mquake" and condition == "R1_learned_ff":
        cal = verify_calibration(ROOT / "manifests/revision_v1/calibration_v3.json")
        spec = value["construction"]
        spec["calibration"] = dict(
            bank_scales=cal["b_m"], radii=cal["calibration"]["BP"]["radii"]["mquake"]
        )
        old = value["adapter_identity"]
        config = json.loads((Path(spec["base"]["path"]) / "config.json").read_text())
        value["adapter_identity"] = metadata_identity(
            condition,
            d=config["n_embd"],
            base_hash=old["base_sha256"],
            original_hash=old["locality_base_sha256"],
            calibration=spec["calibration"],
            seed=spec["seed"],
            stop_tokens=json.loads(Path(spec["stop_tokens"]["path"]).read_text())["tokens"],
            params=checkpoint_tree(spec["weights"]["path"]),
            budget=Budget(**spec["budget"]),
        )
    value["cell"].update(
        dataset=dataset, realization="development_full_endpoints_R164f", order="seed64028"
    )
    value.update(
        payload=payload_binding,
        source_bindings_sha256=sources,
        checkpoints=[100, 300],
        code_sha256=driver.code_identity(),
        integrity_driver_bindings=driver.driver_bindings(),
    )
    value["r1_64f"] = dict(
        source_recipe=ref(parent),
        producer=ref(__file__),
        development_only=True,
        allocation_contract=allocation.CONTRACT,
        allocation_seed=SEED,
        note="Exposed development and historical training pools; no fresh-confirmation or selected-reader independence claim",
        full_validation_split=False,
    )
    return value


def build():
    primary_path = ROOT / "docs/tasks/R1-64e/R1-64e-zsre-primary-v5.recipe.json"
    primary = json.loads(primary_path.read_text())
    tok = GPT2Tokenizer(snapshot=Path(primary["construction"]["base"]["path"]))
    config = json.loads((Path(primary["construction"]["base"]["path"]) / "config.json").read_text())
    limits = dict(max_context=config["n_positions"])
    rows, sources, inventory = pools(tok, limits)
    exposed_hash = core.content_digest(sources)
    layout = {ds: entry(COUNTS, [0], [100, 300]) for ds in core.DATASETS}
    dry = allocation.allocate(
        rows, seed=SEED, register_sha256=exposed_hash, layout=layout, mode="family_coordinated"
    )
    reservation = allocation.reservation_document(
        dry, dict(path="development-source-map-only", sha256=exposed_hash)
    )
    allocation.audit(reservation)
    removed = filter_locality(reservation)
    plans = [
        role_plan(r, prior(r), tok, limits)
        for g in reservation["allocations"]
        for r in g["records"]
    ]
    for g in reservation["allocations"]:
        if g["role"] == "edits":
            reservation.setdefault("orders", {})[f"{g['dataset']}:0:100"] = [
                r["item_id"] for r in g["records"]
            ]
    manifest_path = ROOT / "manifests/revision_v1/mquake_items_v1.json"
    comp = json.loads(manifest_path.read_text())["artifacts"]["composition"]
    if ref(comp["path"])["sha256"] != comp["sha256"]:
        raise ValueError("composition source changed")
    catalog = catalog_from_rows(
        [json.loads(line) for line in Path(comp["path"]).read_text().splitlines()]
    )
    sources[str(manifest_path)] = driver.sha(manifest_path)
    sources[comp["path"]] = comp["sha256"]
    reservation["planned_compositions"] = planned_compositions(reservation, catalog)
    drift_source = read_resource(primary["payload"])
    drift = copy.deepcopy(drift_source["endpoints"]["drift"])
    # Both arms are constructed for all three datasets to retain D10c's global audit;
    # only the requested zsRE/MQuAKE payloads/recipes are published.
    cells = [
        dict(condition=c, dataset=ds, realization=0, order=100)
        for ds in core.DATASETS
        for c in ("R1_learned_ff", "v0_stable")
    ]
    payloads, population, audit = construct(
        reservation, cells, catalog, {"rows": plans}, drift, layout=layout, locality_count=50
    )
    out = ROOT / "docs/tasks/R1-64f"
    inspections = []
    for ds in ("zsre", "mquake"):
        payload = copy.deepcopy(
            payloads[
                core.coordinate_id(
                    dict(condition="R1_learned_ff", dataset=ds, realization=0, order=100)
                )
            ]
        )
        payload.update(
            mode=MODE,
            banner=BANNER,
            development_summary=dict(
                purpose="full near/revision cost profiling; exposed source pools",
                allocation_seed=SEED,
                source_origins=dict(Counter(r["development_source"] for r in payload["items"])),
                no_new_confirmatory_data=True,
                full_validation_split=False,
            ),
        )
        for key, n in (("near_miss", 100), ("revision", 50), ("locality", 50)):
            if len(payload["endpoints"][key]["rows"]) != n:
                raise ValueError(f"development {ds} {key} shortfall; do not change seed")
        validate_locality(payload["items"], payload["endpoints"]["locality"]["rows"])
        b = write_new(PAYLOAD_ROOT / "r1_64f_round28" / ds / "payload.json", payload)
        for condition in ("R1_learned_ff", "v0_stable"):
            m = recipe(ds, condition, b, sources)
            rb = write_new(out / f"R1-64f-{ds}-{condition}.recipe.json", m)
            driver.load_development_cell(rb["path"], rb["sha256"])
            inspections.append(
                dict(
                    recipe=rb,
                    cell=m["cell"],
                    payload=b,
                    items=300,
                    checkpoints=[100, 300],
                    near_miss_rows=100,
                    revision_rows=50,
                    locality_rows=50,
                    model_constructed=False,
                    expected_result_directory=str(
                        driver.OUTPUT_ROOT / driver.cell_name(m, rb["sha256"])
                    ),
                )
            )
    report = dict(
        task="R1-64f",
        producer=ref(__file__),
        seed=SEED,
        source_inventory=inventory,
        source_bindings_sha256=sources,
        drift_source=primary["payload"],
        constructor=ref(ROOT / "scripts/r1_d10c_endpoints.py"),
        allocation_implementation=ref(ROOT / "scripts/r1_d9f_allocation.py"),
        pair_receipts=dry["near_pair_receipts"],
        locality_filter=removed,
        constructed_coordinate_count=len(payloads),
        published_recipe_count=4,
        constructor_audit=audit,
        independent_population=population,
        inspections=inspections,
        actual_draws=0,
        seals=0,
        gpu_seconds=0,
        status="development recipes ready for owner execution; no measurements yet",
    )
    write_new(out / "inspection-receipts.json", inspections)
    write_new(ROOT / "logs/r1_round28/r1-64f-build.json", report)
    lines = [
        "# R1-64f — owner run list",
        "",
        "Four exposed-development cells; 300 edits, checkpoints 100/300, near100/revision50.",
        "Inspect on CPU with the commands below; owner execution adds --execute in a CUDA/JAX environment with the GPU lease.",
        "Keep /usr/bin/time -v or equivalent process RSS/envelope telemetry; JAX device peak alone does not measure host RSS.",
        "128-window drift is a development assay, not the full validation split. Never resume another recipe identity.",
        "",
    ]
    for r in inspections:
        b = r["recipe"]
        lines += [
            f"## {r['cell']['dataset']} / {r['cell']['condition']}",
            "",
            "```bash",
            f"../venv/bin/python -m scripts.r1_68c_dev_cell --manifest {b['path']} --manifest-sha256 {b['sha256']}",
            "```",
            "",
        ]
    with (out / "ordered-runlist.md").open("x") as f:
        f.write("\n".join(lines))
    return inspections


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
