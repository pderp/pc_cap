"""R1-61 owner entry point: inspect a cell recipe or execute its admitted payload.

Inspection opens only the recipe. --execute is for the orchestrating owner after
population admission, protocol freeze, resource lease and real-base validation.
This command performs no draw, no seal and no shared-file append.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from pccap.revision_v1.stage4_cell import (
    ROOT,
    code_identity,
    load_cell,
    read_binding,
    run_cell,
    sha,
)


def inspect_recipe(path, expected_sha256):
    m = read_binding({"path": str(path), "sha256": expected_sha256})
    return {
        "cell": m.get("cell"),
        "mode": m.get("mode"),
        "manifest_sha256": expected_sha256,
        "code_identity_matches": m.get("code_sha256") == code_identity(),
        "payload_opened": False,
        "model_constructed": False,
        "draw_or_seal_performed": False,
        "launch_admission": m.get("admission"),
        "note": "metadata inspection does not certify scientific admission or execution readiness",
    }


def _snapshot(binding):
    """Verify every explicitly admitted base file before constructing BPBase."""
    root = Path(binding["path"])
    required = {"config.json", "model.safetensors"}
    if not required <= set(binding["files"]):
        raise ValueError("base config and weight hashes required")
    for name, expected in binding["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != expected:
            raise ValueError("base snapshot child mismatch")
    return root


def construct_owner_adapter(m):
    import jax

    from pccap.bases.bp import BPBase
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.reader import ReaderConfig, init_reader
    from pccap.revision_v1.stage4_adapters import build_adapter

    spec = m["construction"]
    base_path = _snapshot(spec["base"])
    original_path = _snapshot(spec["original_base"]) if "original_base" in spec else base_path
    if sha(original_path / "tokenizer.json") != m["tokenizer_sha256"]:
        raise ValueError("tokenizer hash mismatch")
    condition = m["cell"]["condition"]
    budget = Budget(**spec["budget"])
    if budget.A != 0.3 or budget.tau_edit != 0.1:
        raise ValueError("registered A=.3 and tau_edit=.1 required")
    calibration = spec["calibration"]
    scales = tuple(float(calibration["bank_scales"][str(k)]) for k in (1, 2, 3))
    stop = read_binding(spec["stop_tokens"])["tokens"] if "stop_tokens" in spec else []
    params = None
    if condition.startswith("R1_"):
        if condition != "R1_nonlearned" and not stop:
            raise ValueError("learned reference requires bound stop tokens")
        rc = ReaderConfig(
            d=768,
            lexical=condition != "R1_nonlearned",
            pairwise_null=condition != "R1_nonlearned",
            stop_tokens=tuple(stop),
        )
        cc = ControllerConfig(d=768, A=budget.A, bank_scales=scales)
        k1, k2 = jax.random.split(jax.random.PRNGKey(spec["seed"]))
        template = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
        binding = spec["weights"]
        if sha(binding["path"]) != binding["sha256"]:
            raise ValueError("reader checkpoint file mismatch")
        paths, tree = jax.tree_util.tree_flatten_with_path(template)
        arrays = []
        with np.load(binding["path"], allow_pickle=False) as z:
            if set(z.files) != {jax.tree_util.keystr(p) for p, _ in paths}:
                raise ValueError("reader checkpoint parameter keys differ")
            for p, ref in paths:
                arr = np.asarray(z[jax.tree_util.keystr(p)])
                if (
                    arr.shape != ref.shape
                    or arr.dtype != np.float32
                    or not np.all(np.isfinite(arr))
                ):
                    raise ValueError("invalid reader checkpoint array")
                arrays.append(arr)
        params = jax.tree_util.tree_unflatten(tree, arrays)
    ledger = Ledger()
    base = BPBase(snapshot=base_path, ledger=ledger)
    original = (
        base
        if base_path.resolve() == original_path.resolve()
        else BPBase(snapshot=original_path, ledger=ledger)
    )
    tokenizer = GPT2Tokenizer(snapshot=original_path)
    adapter = build_adapter(
        condition,
        base,
        ledger,
        calibration=calibration,
        params=params,
        stop_tokens=stop,
        seed=spec["seed"],
        budget=budget,
        locality_base=original,
    )
    return adapter, tokenizer


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--manifest-sha256", required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--output-root", type=Path, default=ROOT / "results/R1/stage4_cells")
    ap.add_argument(
        "--resource-root", type=Path, default=ROOT.parent / "assets/runs/pc_cap/R1/stage4_cells"
    )
    args = ap.parse_args(argv)
    if not args.execute:
        if args.resume:
            ap.error("--resume requires --execute")
        print(json.dumps(inspect_recipe(args.manifest, args.manifest_sha256), indent=2))
        return 0
    m, _payload = load_cell(args.manifest, args.manifest_sha256, allow_sealed=True)
    if m["mode"] != "stage4_sealed_cell":
        ap.error(
            "CLI execution requires an admitted sealed cell; synthetic tests use run_cell directly"
        )
    adapter, tok = construct_owner_adapter(m)
    result = run_cell(
        args.manifest,
        args.manifest_sha256,
        adapter,
        tok,
        output_root=args.output_root,
        resource_root=args.resource_root,
        resume=args.resume,
        allow_sealed=True,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
