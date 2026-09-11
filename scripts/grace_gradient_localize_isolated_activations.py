#!/usr/bin/env python3
"""Run the boundary diagnostic with separately observable stateless HF activations.

Transformers 4.20 shares the same ACT2FN module instance across GPT-2 blocks.
Independent module objects prevent a hook for block 8 from observing block 0.
Only the in-memory diagnostic copy changes; first-step arrays must remain bit exact
to the previously captured original-GRACE trace.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("reference", "candidate"))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("gradient_diagnostic", ROOT / "scripts/grace_gradient_localize.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    driver.RESOURCES = driver.RESOURCES.with_name(driver.RESOURCES.name + "_independent_activations")
    if args.mode == "reference":
        deepcopy = driver.copy.deepcopy
        def independent_activations(obj, *args, **kwargs):
            result = deepcopy(obj, *args, **kwargs)
            if hasattr(result, "transformer") and hasattr(result.transformer, "h"):
                for block in result.transformer.h:
                    block.mlp.act = deepcopy(block.mlp.act)
            return result
        with patch.object(driver.copy, "deepcopy", independent_activations):
            driver.reference()
    else:
        driver.candidate()


if __name__ == "__main__":
    main()
