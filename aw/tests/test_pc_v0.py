"""Actual FabricPC solver regression, not a mock of the desired direction."""

import pccap  # noqa: F401 # isort: skip

# isort: split

from dataclasses import replace

import jax
import numpy as np
import pytest
from tests.revision_v1.tiny_base import CFG, tiny_params

from aw.pc_v0 import SupplementalEvaluator, archive, build_cap, credit_diagnostics, design
from pccap.bases import gpt2_jax as g
from pccap.bases.epc import EPCBase
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, EditItem, SiteId, Write
from pccap.data.decode import DecodeResult
from pccap.harness.ledger import Ledger
from pccap.routers import make_router


class TinyEPC(EPCBase):
    """Production EPCBase/solver, with a valid padding token for the 64-token fixture."""

    def __init__(self):
        params = jax.tree_util.tree_map(np.asarray, tiny_params())
        super().__init__(params_np=params, cfg=CFG, ledger=Ledger(), error_lr=0.1)

    def _prep(self, ids, writes):
        ids_d, n_d, w, n, p = super()._prep(ids, writes)
        return ids_d.at[n:].set(0), n_d, w, n, p


@pytest.fixture(scope="module")
def base():
    assert jax.default_backend() == "cpu"
    return TinyEPC()


def nonzero_writes(base, ids):
    rng = np.random.default_rng(12)
    return [Write(SiteId(m, g.BANK_BLOCK[m], len(ids) - 1),
                  rng.normal(size=base.d).astype(np.float32) * 0.7) for m in (1, 2, 3)]


def test_sd24_one_step_with_nonzero_writes(base):
    ids = np.int32([4, 11, 9, 27])
    ws = nonzero_writes(base, ids)
    h0 = base.checksum(recompute=True)
    adj = base.adjoint(ids, 17, ws)
    er = base.infer_errors(ids, 17, iters=1, writes=ws)
    for s, error in er.site_errors.items():
        expected = -0.1 * np.asarray(adj[s])
        np.testing.assert_allclose(error, expected, rtol=3e-5, atol=3e-7)
        # The historical defect produces precisely this additional prior gradient.
        wrong = expected - 0.1 * ws[s.bank - 1].vector
        assert not np.allclose(error, wrong, rtol=3e-5, atol=3e-7)
    assert base.checksum(recompute=True) == h0


def test_zero_error_identity_prior_and_unclamped_targets(base):
    ids = np.int32([4, 11, 9, 27])
    ws = nonzero_writes(base, ids)
    ordinary = base.forward(ids, ws).logits
    graph = base.graph_forward(ids, ws).logits
    np.testing.assert_allclose(graph, ordinary, rtol=2e-5, atol=2e-6)
    er = base.infer_errors(ids, None, iters=8, writes=ws)
    assert er.energies == [0.0] * 9  # nonzero writes have NO prior penalty
    assert all(np.count_nonzero(e) == 0 for e in er.errors.values())
    np.testing.assert_allclose(er.logits, ordinary, rtol=2e-5, atol=2e-6)
    loss, _ = base.loss(ids, 17, ws)
    clamped = base.infer_errors(ids, 17, iters=0, writes=ws)
    assert clamped.energies[0] == pytest.approx(loss, abs=2e-6)


def test_eight_steps_charge_nine_forwards_and_reverses(base):
    before = base.ledger.totals()["learning"]
    er = base.infer_errors(np.int32([4, 11, 9]), 17, iters=8)
    after = base.ledger.totals()["learning"]
    for field, n in (("full_forwards", 9), ("reverses", 9), ("settle_iters", 8)):
        assert getattr(er.cost, field) == n
        assert after[field] - before[field] == n


def test_diagnostic_horizons_and_fresh_error_state(base):
    ids = np.int32([4, 11, 9])
    ws = nonzero_writes(base, ids)
    rows = credit_diagnostics(base, ids, 17, ws)
    assert [x["iters"] for x in rows] == [1, 8, 32]
    assert [len(x["energies"]) for x in rows] == [2, 9, 33]
    assert all(np.isfinite(x["r_k"]) for x in rows)
    a = base.infer_errors(ids, 17, iters=1, writes=ws)
    base.infer_errors(ids, 2, iters=8, writes=ws)
    b = base.infer_errors(ids, 17, iters=1, writes=ws)
    for k in a.errors:
        np.testing.assert_array_equal(a.errors[k], b.errors[k])


def test_design_archived_settings_and_independent_empty_caps(base):
    assert len(design()) == 12 and len(design(5)) == 60
    assert {x["order"] for x in design()} == {100}
    assert {x["items"] for x in design() if x["dataset"] == "zsre"} == {1000}
    with pytest.raises(ValueError):
        design(2)
    a, b = (build_cap(base, "zsre", arm, 23) for arm in ("SE-A", "SE-E"))
    f = archive()["calibration"]["EPC"]
    assert a.cfg.bank_scales == {int(k): v for k, v in f["b_m"].items()}
    assert b.cfg.credit == "error" and b.cfg.credit_iters == 8
    assert a.cfg.credit == "adjoint"
    for m in a.banks:
        assert a.banks[m] is not b.banks[m]
        assert a.banks[m].bank is not b.banks[m].bank
    assert a.memory_bytes().occupied_bytes == b.memory_bytes().occupied_bytes
    assert a.state_hash() == b.state_hash()  # credit is not memory state


def test_acquisition_clamps_only_current_support_and_prediction_never_clamps(base, monkeypatch):
    cap = Cap(base, CapConfig(d=base.d, arm="C1", credit="error", credit_iters=1,
                             radii={m: 0.5 for m in (1, 2, 3)}, bank_scales={m: 1.0 for m in (1, 2, 3)}), base.ledger)
    item = EditItem(item_id="teaching", digest=b"0" * 16, prompt="p", answer="a", aliases=["a"],
                    prompt_ids=np.int32([4, 11]), answer_ids=np.int32([17, 18]), dataset="tiny",
                    paraphrases=[], locality_prompts=[])
    calls = []
    old = base.infer_errors

    def track(ids, target, *args, **kwargs):
        calls.append((tuple(np.asarray(ids)), int(target), kwargs.get("phase")))
        return old(ids, target, *args, **kwargs)

    monkeypatch.setattr(base, "infer_errors", track)
    cap.update_item(item, make_router("C1"), Budget(R=1, A=0.3))
    assert calls and all((x, y) in (((4, 11), 17), ((4, 11, 17), 18)) for x, y, _ in calls)
    assert all(phase == "learning" for _, _, phase in calls)
    calls.clear()
    before = cap.state_hash()
    cap.predict(np.int32([4, 11]))
    assert not calls and cap.state_hash() == before


def test_secondary_score_does_not_change_primary(monkeypatch):
    from pccap.harness.runs import Evaluator

    own = DecodeResult(np.int32([7]), "accepted", "max", True, 1)
    para = replace(own, stopped_by="newline", truncated=False)

    def original(ev, learner, items):
        ev.last_decodes = [own, para]
        return [{"es": 0.0, "gs": 1.0}]

    monkeypatch.setattr(Evaluator, "items", original)
    ev = object.__new__(SupplementalEvaluator)
    ev.secondary_path = None
    item = EditItem(item_id="one", digest=b"0" * 16, prompt="p", answer="accepted", aliases=["accepted"],
                    paraphrases=["q"], locality_prompts=[], prompt_ids=np.int32([1]), answer_ids=np.int32([2]))
    rows = ev.items(None, [item])
    assert rows[0]["es"] == 0.0 and rows[0]["bounded_es"] == 1.0
    assert rows[0]["gs"] == rows[0]["bounded_gs"] == 1.0
    assert rows[0]["truncated"] and rows[0]["paraphrases_truncated"] == 0


def test_new_output_refuses_reuse_and_orphan_snapshots(tmp_path, monkeypatch):
    from aw import pc_v0

    root = tmp_path / "repo"
    assets = tmp_path / "assets"
    output = root / "results/additional_work/PC-v0"
    monkeypatch.setattr(pc_v0, "ROOT", root)
    monkeypatch.setattr(pc_v0, "OUTPUT", output)
    monkeypatch.setattr(pccap, "ASSETS_ROOT", str(assets))
    target = output / "fresh"
    assert pc_v0._new_output(target) == target
    marker = target / "keep.txt"
    marker.write_text("preserved")
    with pytest.raises(FileExistsError):
        pc_v0._new_output(target)
    assert marker.read_text() == "preserved"
    orphan = output / "orphan"
    (assets / "runs" / orphan.relative_to(root / "results")).mkdir(parents=True)
    with pytest.raises(FileExistsError):
        pc_v0._new_output(orphan)
    assert not orphan.exists()
    with pytest.raises(ValueError):
        pc_v0._new_output(root / "results/S5/do-not-overwrite")
