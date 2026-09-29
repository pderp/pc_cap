"""Tiny CPU smoke of PC-12 controls through the native stream/checkpoint engine."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import time
from pathlib import Path

import jax
import numpy as np

from aw.pc_matched_credit import MatchedCreditCap, units
from aw.pc_random_credit import RandomCreditCap
from aw.pc_v0 import dump
from aw.pc_v0_smoke import SequentialTinyEvaluator, Tokens
from aw.tests.test_pc_v0 import TinyEPC
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, EditItem
from pccap.harness.records import append_jsonl
from pccap.harness.runs import run_stream
from pccap.harness.snapshot import restore
from pccap.routers import make_router

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    if jax.default_backend() != "cpu":
        raise RuntimeError("CPU tiny smoke only")
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "results/additional_work/PC12"):
        raise ValueError("use the PC12 synthetic-results namespace")
    output.mkdir(parents=True, exist_ok=False)
    items = [
        EditItem(
            item_id=f"tiny-{i}",
            digest=bytes([i + 1]) * 16,
            prompt=f"4 {11 + i}",
            answer="17",
            aliases=["17"],
            paraphrases=[f"4 {13 + i}"],
            locality_prompts=[],
            prompt_ids=np.int32([4, 11 + i]),
            answer_ids=np.int32([17]),
            dataset="tiny",
        )
        for i in range(2)
    ]
    budget = Budget(R=1, A=0.3, tau_edit=0)
    reference_base = TinyEPC()
    reference = Cap(
        reference_base,
        CapConfig(
            d=reference_base.d, credit="error", credit_iters=8, radii={m: 0.5 for m in (1, 2, 3)}
        ),
        reference_base.ledger,
    )
    allowances = {
        it.item_id: units(reference.update_item(it, make_router("C1"), budget).cost) for it in items
    }
    result = dict(
        population="CPU tiny fixture only; no research result",
        gpu_seconds=0,
        reference_allowances=allowances,
        cells=[],
    )
    for name in ("SE-R", "SE-AM"):
        folder = output / name
        base = TinyEPC()
        cfg = CapConfig(
            d=base.d,
            credit="error" if name == "SE-R" else "adjoint",
            credit_iters=8,
            radii={m: 0.5 for m in (1, 2, 3)},
        )
        cap = (
            RandomCreditCap(base, cfg, base.ledger)
            if name == "SE-R"
            else MatchedCreditCap(base, cfg, base.ledger, allowances=allowances)
        )
        cap.on_decision = lambda record, folder=folder: append_jsonl(
            folder / "decisions.jsonl", record
        )
        if name == "SE-AM":
            cap.on_budget = lambda record, folder=folder: append_jsonl(
                folder / "operation-budgets.jsonl", record
            )
        cap.router_seed = 100
        initial = base.checksum(recompute=True)
        evaluator = SequentialTinyEvaluator(
            base, Tokens(), [], None, max_new=1, secondary_path=folder / "secondary.jsonl"
        )
        started = time.monotonic()
        metrics = run_stream(
            cap,
            items,
            make_router("C1"),
            budget,
            evaluator,
            folder,
            base.ledger,
            checkpoints=(),
            seed=100,
            arm=name,
        )
        if (
            metrics["status"] != "complete"
            or metrics["items_completed"] != 2
            or base.checksum(recompute=True) != initial
        ):
            raise RuntimeError("tiny stream incomplete or changed base")
        checkpoint = (
            Path(pccap.ASSETS_ROOT)
            / "runs"
            / folder.relative_to(ROOT / "results")
            / "learner_end.ckpt"
        )
        state = restore(checkpoint.read_bytes())
        cap.import_state(state)
        if state.content_hash() != cap.state_hash():
            raise RuntimeError("control snapshot roundtrip failed")
        cost = base.ledger.totals()
        item_rows = [json.loads(line) for line in (folder / "items.jsonl").read_text().splitlines()]
        if sum(r["cost"]["reverses"] for r in item_rows) != cost["learning"]["reverses"]:
            raise RuntimeError("item/ledger reverse accounting differs")
        result["cells"].append(
            dict(
                arm=name,
                status="complete",
                items=2,
                elapsed_process_seconds=time.monotonic() - started,
                ledger=cost,
                snapshot_state=cap.state_hash(),
            )
        )
    dump(output / "smoke.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    print(json.dumps(run(parser.parse_args().output)))
