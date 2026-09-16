"""R1-64b: metadata-only comparator recipes and additive owner entry point."""

from __future__ import annotations

import argparse
import copy
import json
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

import numpy as np
from scripts import r1_68c_dev_cell as driver
from scripts.r1_68c_rebind_recipe import rebind

from pccap.bases import gpt2_jax as g
from pccap.bases.bp import _digest
from pccap.cap.cap import CapConfig
from pccap.contracts import Budget
from pccap.revision_v1.adapt import FastConfig
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.checkpoint_identity import checkpoint_tree
from pccap.revision_v1.controller import ControllerConfig
from pccap.revision_v1.learner import RevisionConfig
from pccap.revision_v1.matched_update import MatchedRule
from pccap.revision_v1.reader import ReaderConfig, params_hash
from pccap.revision_v1.stage4_adapters import CORE_CONDITIONS, SECONDARY_CONDITION

ROOT = driver.ROOT
CONDITIONS = tuple(c for c in (*CORE_CONDITIONS, SECONDARY_CONDITION) if c != "R1_learned_ff")
S1_RUNS = {"S1_literal": "r1_24_literal_v3b", "S1_LM": "r1_24_lm_v3_lr1e-8"}


def ref(path):
    p = Path(path).resolve()
    if not p.is_relative_to(ROOT.parent) or "confirm" in p.parts:
        raise PermissionError("local unsealed resource required")
    return {"path": str(p), "sha256": driver.sha(p)}


def verify(binding):
    actual = ref(binding["path"])
    if actual["sha256"] != binding["sha256"]:
        raise ValueError("binding mismatch: " + binding["path"])
    return Path(actual["path"])


def metadata_identity(
    condition,
    *,
    d,
    base_hash,
    original_hash,
    calibration,
    seed=0,
    stop_tokens=(),
    params=None,
    budget=None,
):
    """Mirror build_adapter's registered dataclasses without constructing a base/cap."""
    if condition not in (*CORE_CONDITIONS, SECONDARY_CONDITION):
        raise ValueError("unknown condition")
    scales = {int(k): float(v) for k, v in calibration["bank_scales"].items()}
    radii = {int(k): float(v) for k, v in calibration["radii"].items()}
    if (
        set(scales) != {1, 2, 3}
        or set(radii) != {1, 2, 3}
        or any(not np.isfinite(x) or x <= 0 for x in scales.values())
        or any(not np.isfinite(x) or x < 0 for x in radii.values())
    ):
        raise ValueError("all three valid calibrated banks required")
    budget = budget or Budget(A=0.3)
    rule = None
    if condition.startswith("R1_"):
        if params is None:
            raise ValueError("pinned reader parameters required")
        random = condition == "R1_nonlearned"
        cfg = RevisionConfig(
            reader=ReaderConfig(
                d=d, lexical=not random, pairwise_null=not random, stop_tokens=tuple(stop_tokens)
            ),
            controller=ControllerConfig(
                d=d, A=budget.A, bank_scales=tuple(scales[k] for k in (1, 2, 3))
            ),
            fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=budget.tau_edit),
            tau_edit=budget.tau_edit,
            seed=seed,
            min_score=0.93 if random else None,
            null_threshold=1.01 if random else 0.5,
            rare_overlap_min=1 if condition == "R1_learned_ff" else None,
            rare_df_max=2,
        )
        cls = "pccap.revision_v1.learner.RevisionCap"
        ph = params_hash(params)
    else:
        if params is not None:
            raise ValueError("reader parameters do not belong to v0")
        cfg = CapConfig(
            arm="C2" if condition == "v0_live_C2" else "C1",
            d=d,
            radii=radii,
            bank_scales=scales,
            seed=seed,
        )
        cls = "pccap.cap.cap.Cap"
        if condition in ("v0_stable", "S1_literal", "S1_LM"):
            cls = "pccap.revision_v1.v0_stable.StableCap"
        elif condition == "matched_update":
            cls = "pccap.revision_v1.matched_update.MatchedUpdateCap"
            rule = asdict(MatchedRule(steps=5, lr=0.1))
        ph = None
    return {
        "condition": condition,
        "class": cls,
        "config_sha256": digest(asdict(cfg)),
        "rule": rule,
        "budget": asdict(budget),
        "base_sha256": base_hash,
        "locality_base_sha256": original_hash,
        "params_sha256": ph,
    }


@lru_cache(maxsize=4)
def base_identity(serialized):
    binding = json.loads(serialized)
    root = Path(binding["path"])
    for name, h in binding["files"].items():
        if Path(name).name != name:
            raise ValueError("invalid base child")
        verify({"path": str(root / name), "sha256": h})
    cfg = g.GPT2Config.from_snapshot(root)
    return cfg.d, _digest(g.load_params_numpy(root, cfg))


@lru_cache(maxsize=4)
def continuation_identity(path, expected):
    verify({"path": path, "sha256": expected})
    params = g.load_params_npz(Path(path))
    if any(a.dtype != np.float32 or not np.all(np.isfinite(a)) for _, a in g.flatten_named(params)):
        raise ValueError("invalid continued weights")
    h = _digest(params)
    if driver.sha(path) != expected:
        raise ValueError("continued checkpoint changed while reading")
    return h


def build_recipe(source, source_sha256, condition):
    if condition not in CONDITIONS:
        raise ValueError("one of the eight comparator conditions required")
    m = rebind(source, source_sha256, profile="full")
    payload = driver.read_binding(m["payload"])
    if (
        m["cell"]["dataset"] not in ("zsre", "counterfact")
        or len(payload["items"]) != 300
        or m["checkpoints"] != [100, 300]
    ):
        raise ValueError("zsRE/CounterFact 300 edits, checkpoints100/300 required")
    original = copy.deepcopy(m["construction"]["base"])
    d, original_hash = base_identity(json.dumps(original, sort_keys=True))
    spec = copy.deepcopy(m["construction"])
    spec.pop("weights", None)
    spec.pop("stop_tokens", None)
    seed = 0
    spec["seed"] = seed
    bindings = {
        "source_recipe": ref(source),
        "producer": ref(__file__),
        "factory": ref(ROOT / "src/pccap/revision_v1/stage4_adapters.py"),
    }
    weight = None
    stop = []
    bh = original_hash
    if condition == "R1_nonlearned":
        matrix = ROOT / "manifests/revision_v1/run_matrix_draft_v4.json"
        document = json.loads(matrix.read_text())
        row = next(
            r for r in document["cells"] if r["condition_id"] == condition and r["model_seed"] == 0
        )
        weight = row["condition_identity"]["reader"]
        bindings["random_checkpoint_authority"] = ref(matrix)
    elif condition == "R1_learned_ff_v2":
        primary = ROOT / "manifests/revision_v1/primary_condition_v2.json"
        document = json.loads(primary.read_text())
        weight = document["weights"]["seed0"]
        binding = dict(document["stop_tokens"])
        binding["path"] = str((ROOT / binding["path"]).resolve())
        stop = json.loads(verify(binding).read_text())["tokens"]
        spec["stop_tokens"] = binding
        bindings["v2_primary"] = ref(primary)
    elif condition in S1_RUNS:
        summary = ROOT / "results/R1/r1_24" / S1_RUNS[condition] / "summary.json"
        document = json.loads(summary.read_text())
        checkpoint = document["checkpoint"]
        recipe = verify({"path": document["manifest"], "sha256": document["manifest_sha256"]})
        wanted = (
            "r1_24_control_v3.json"
            if condition == "S1_literal"
            else "r1_24_control_lm_v3_lr1e-8.json"
        )
        if recipe.name != wanted or not document["fidelity"]["fidelity_pass"]:
            raise ValueError("S1 source recipe/fidelity mismatch")
        bh = continuation_identity(checkpoint["path"], checkpoint["sha256"])
        if (
            bh != checkpoint["continued_tensor_digest"]
            or original_hash != checkpoint["original_tensor_digest"]
        ):
            raise ValueError("S1 tensor identity mismatch")
        spec["continued_weights"] = {"path": checkpoint["path"], "sha256": checkpoint["sha256"]}
        spec["original_base"] = original
        bindings.update(continuation_summary=ref(summary), continuation_recipe=ref(recipe))
    params = checkpoint_tree(verify(weight)) if weight else None
    if weight:
        spec["weights"] = weight
    m["cell"]["condition"] = condition
    m["construction"] = spec
    m["adapter_identity"] = metadata_identity(
        condition,
        d=d,
        base_hash=bh,
        original_hash=original_hash,
        calibration=spec["calibration"],
        seed=seed,
        stop_tokens=stop,
        params=params,
        budget=Budget(**spec["budget"]),
    )
    m["comparator_recipe"] = {
        "task": "R1-64b",
        "bindings": bindings,
        "method": "registered dataclass + NumPy tensor hashing; no model execution",
        "entry_point": "python -m scripts.r1_64b_comparator_recipes run",
        "source_reader_provenance": "inherited reader_provenance describes source payload recipe only; comparator identity and these bindings define this condition",
        "S1_note": "historical two-pool continuation; final training-budget reconciliation remains open",
        "calibration_note": "historical BP dataset radii/scales; MQuAKE and any final per-continued-base recalibration remain separate admission work",
        "launch_authorized": False,
    }
    driver.validate_development_payload(m, payload)
    return m


def verify_recipe_bindings(m):
    if m.get("comparator_recipe", {}).get("task") != "R1-64b":
        raise ValueError("comparator recipe required")
    for binding in m["comparator_recipe"]["bindings"].values():
        verify(binding)
    if m["comparator_recipe"]["bindings"]["producer"] != ref(__file__):
        raise ValueError("recipe producer code changed")
    if m["integrity_profile"] != "full":
        raise ValueError(
            "comparators require full profile; optimized path is exact RevisionCap only"
        )


def construct(m):
    """Owner-only; --execute is the sole CLI route to model construction."""
    from scripts.r1_61_cell_driver import _snapshot, construct_owner_adapter

    from pccap.bases.bp import BPBase
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.stage4_adapters import build_adapter

    verify_recipe_bindings(m)
    spec = m["construction"]
    if "continued_weights" not in spec:
        return construct_owner_adapter(m)
    if m["cell"]["condition"] not in S1_RUNS:
        raise ValueError("continued base only for S1")
    base_path = _snapshot(spec["base"])
    original_path = _snapshot(spec["original_base"])
    if driver.sha(original_path / "tokenizer.json") != m["tokenizer_sha256"]:
        raise ValueError("tokenizer identity mismatch")
    params = g.load_params_npz(verify(spec["continued_weights"]))
    ledger = Ledger()
    base = BPBase(snapshot=base_path, params_np=params, ledger=ledger)
    original = BPBase(snapshot=original_path, ledger=ledger)
    tok = GPT2Tokenizer(snapshot=original_path)
    adapter = build_adapter(
        m["cell"]["condition"],
        base,
        ledger,
        calibration=spec["calibration"],
        seed=spec["seed"],
        budget=Budget(**spec["budget"]),
        locality_base=original,
    )
    if adapter.identity() != m["adapter_identity"]:
        raise ValueError("constructed S1 identity mismatch")
    return adapter, tok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", type=Path, required=True)
    b.add_argument("--source-sha256", required=True)
    b.add_argument("--condition", choices=CONDITIONS, required=True)
    b.add_argument("--output", type=Path, required=True)
    r = sub.add_parser("run")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--manifest-sha256", required=True)
    r.add_argument("--execute", action="store_true")
    r.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    if a.command == "build":
        if a.output.exists() or not a.output.resolve().is_relative_to(ROOT / "docs/tasks"):
            ap.error("new recipe under docs/tasks required")
        m = build_recipe(a.source, a.source_sha256, a.condition)
        binding = driver.write_json(a.output, m)
        driver.load_development_cell(a.output, binding["sha256"])
        print(json.dumps(binding))
    else:
        if a.resume and not a.execute:
            ap.error("--resume requires --execute")
        m, p = driver.load_development_cell(a.manifest, a.manifest_sha256)
        verify_recipe_bindings(m)
        if not a.execute:
            print(
                json.dumps(
                    {
                        "cell": m["cell"],
                        "items": len(p["items"]),
                        "profile": m["integrity_profile"],
                        "model_constructed": False,
                        "admission": m["admission"],
                    }
                )
            )
            return
        adapter, tok = construct(m)
        result = driver.run_development_cell(
            a.manifest,
            a.manifest_sha256,
            adapter,
            tok,
            output_root=driver.OUTPUT_ROOT,
            resource_root=driver.RESOURCE_ROOT,
            resume=a.resume,
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
