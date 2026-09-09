"""PC-3 (PDF F.5): for edits that reached the per-prefix threshold, an immediate repeat allocates
no additional slots. Development s0-sample items on the BP base (GPU)."""

import json
from pathlib import Path

import pytest

from pccap.bases import gpt2_jax as g

pytestmark = [pytest.mark.gpu, pytest.mark.slow]
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"


def test_pc3_repeat_allocates_nothing():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.cap.learn import update_item
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.stage_s0 import load_items
    from pccap.routers import Full

    base = BPBase()
    tok = GPT2Tokenizer()
    items = load_items([f"s0_sample[{i}]" for i in range(0, 80, 2)][:40], tok)
    cap = Cap(base, CapConfig(arm="C1", radii={1: 0.0, 2: 0.0, 3: 0.0}, bank_scales={1: 60.0, 2: 100.0, 3: 480.0}))
    budget = Budget(A=0.3, R=5, tau_edit=0.1)  # A within the S2 candidate set {0.03, 0.1, 0.3}
    reached, checked, violations, rows = 0, 0, 0, []
    for it in items:
        if reached >= 20:
            break
        out = update_item(cap, it, Full(), budget)
        if not out.acquired_threshold_all_prefixes:
            rows.append({"item": it.item_id, "reached": False})
            continue
        reached += 1
        occ = {m: bs.bank.occupancy() for m, bs in cap.banks.items()}
        out2 = update_item(cap, it, Full(), budget)
        occ2 = {m: bs.bank.occupancy() for m, bs in cap.banks.items()}
        checked += 1
        ok = occ == occ2 and out2.rounds_used == 0
        violations += (not ok)
        rows.append({"item": it.item_id, "reached": True, "occ_before": occ, "occ_after": occ2, "repeat_rounds": out2.rounds_used})
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "pc3_idempotence.json").write_text(json.dumps({"control": "PC-3", "items_tried": len(rows), "reached_threshold": reached,
                                                             "checked": checked, "violations": violations, "rows": rows}, indent=1))
    assert violations == 0
    assert checked >= 1, "no development item reached the threshold; PC-3 not exercised (recorded)"
