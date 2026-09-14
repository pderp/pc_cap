"""R1-23 bounded CPU counterexamples. Does not alter installed code or run a GPU.

Expected defects are evidence, not failing production tests. Each control records its
observed result so a later repair can be compared without changing this artifact.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys

os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import jax
import jax.numpy as jnp
import numpy as np
from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.contracts import MemoryRecord, SupportExample, assert_no_target_parameter
from pccap.revision_v1.controller import ControllerConfig, init_controller
from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.epc_train import episode_grads_epc
from pccap.revision_v1.learner import RevisionCap, RevisionConfig
from pccap.revision_v1.memory import RecordStore
from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash, param_count
from pccap.revision_v1.train import LossConfig, _records, episode_grads, featurize
from tests.revision_v1.tiny_base import TinyBase


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def flat(tree):
    return np.concatenate([np.asarray(v).reshape(-1) for v in jax.tree_util.tree_leaves(tree)])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    output = a.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT):
        raise ValueError("output must be new and inside pc_cap")
    paths = sorted((ROOT / "src/pccap/revision_v1").glob("*.py")) + [ROOT / "scripts/r1_21_pilot.py", ROOT / "docs/revision_v1_losses.md"]
    sources = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    rc = ReaderConfig(d=16, width=8, hidden=8, d_code=6, top_k=2)
    cc = ControllerConfig(d=16, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1., 1., 1.))
    cfg = RevisionConfig(reader=rc, controller=cc, null_threshold=1.01)
    base = TinyBase()
    cap = RevisionCap(base, cfg, Ledger())
    theta = cap.params
    initial_base_hash = params_hash(base.params)
    initial_theta_hash = params_hash(theta)
    out = {"task": "R1-23", "devices": [str(d) for d in jax.devices()], "source_sha256_before": sources, "controls": {}}
    controls = out["controls"]
    for fn in (cap.predict, cap.selection_for):
        assert_no_target_parameter(fn)
    controls["read_signatures"] = {fn.__name__: str(inspect.signature(fn)) for fn in (cap.predict, cap.selection_for)}
    ep = synthetic_episode(3)
    feats = featurize(base, cap.enc, ep, rc)
    def changed_support(s):
        return replace(s, answer_ids=tuple((int(v) + 7) % 64 for v in s.answer_ids), answer="counterfactual audit answer")
    changed = replace(ep, inputs=replace(ep.inputs, support_history=tuple(map(changed_support, ep.inputs.support_history)),
                                         new_support=tuple(map(changed_support, ep.inputs.new_support))))
    f2 = featurize(base, cap.enc, changed, rc)
    supports_equal = all(np.array_equal(x.last, y.last) and np.array_equal(x.span, y.span) for x, y in zip(feats.supports, f2.supports))
    records_equal = np.array_equal(flat(_records(theta, rc, feats)), flat(_records(theta, rc, f2)))
    controls["support_answer_swap"] = {"changed_support_count": len(feats.supports), "support_features_bit_identical": supports_equal,
        "initial_keys_and_codes_bit_identical": records_equal, "query_labels_held_fixed": True,
        "interpretation": "zero-step outer record construction ignores the taught answers; deliberate inconsistent-label intervention tests data flow"}
    controls["prefix_denominators"] = {}
    def stub(ids, target, W, role):
        return np.full_like(W, 0.125), 2.0, {"r_k": 0.5}
    for role, term in (("new_paraphrase", "answer"), ("unrelated", "preserve")):
        q = next(q for q in feats.queries if q.role == role)
        one = replace(feats, queries=[replace(q, prefixes=q.prefixes[:1])])
        two = replace(feats, queries=[replace(q, prefixes=q.prefixes[:1] * 2)])
        lc = LossConfig(w_answer=int(term == "answer"), w_preserve=int(term == "preserve"), w_retrieval=0)
        before_calls = dict(base.calls)
        g1, m1 = episode_grads(theta, rc, cc, base.params, base.cfg, one, lc)
        g2, m2 = episode_grads(theta, rc, cc, base.params, base.cfg, two, lc)
        e1, em1 = episode_grads_epc(theta, rc, cc, one, lc, stub)
        e2, em2 = episode_grads_epc(theta, rc, cc, two, lc, stub)
        x, y, ex, ey = flat(g1), flat(g2), flat(e1), flat(e2)
        controls["prefix_denominators"][term] = {"reported_mean_one": m1[term], "reported_mean_duplicate": m2[term],
            "gradient_norm_one": float(np.linalg.norm(x)), "gradient_norm_duplicate": float(np.linalg.norm(y)),
            "max_abs_duplicate_minus_twice": float(np.max(np.abs(y - 2*x))),
            "epc_stub_gradient_norm_one": float(np.linalg.norm(ex)), "epc_stub_gradient_norm_duplicate": float(np.linalg.norm(ey)),
            "epc_stub_max_abs_duplicate_minus_twice": float(np.max(np.abs(ey - 2*ex))),
            "base_api_call_deltas_during_bp_gradients": {k: base.calls[k] - before_calls[k] for k in before_calls},
            "epc_control_scope": "tests accumulation with a deterministic stand-in, not the actual ePC gradient estimator"}
    # A nonzero code penalty is silently omitted by the ePC accumulator.
    empty_queries = replace(feats, queries=[])
    lc = LossConfig(w_answer=0, w_preserve=0, w_retrieval=0, w_code_norm=1)
    cg, cm = episode_grads(theta, rc, cc, base.params, base.cfg, empty_queries, lc)
    eg, em = episode_grads_epc(theta, rc, cc, empty_queries, lc, stub)
    controls["optional_code_penalty"] = {"bp_loss": cm["code_norm"], "epc_loss": em["code_norm"],
        "bp_grad_norm": float(np.linalg.norm(flat(cg))), "epc_grad_norm": float(np.linalg.norm(flat(eg)))}

    def planted(rid, fact):
        return MemoryRecord(rid, fact, 1, -1, np.arange(8, dtype=np.float32)/8,
                            np.arange(6, dtype=np.float32)/6, provenance=(rid,), source_ids=np.int32([5, 6]))
    cap.store.add(planted("old", "fact"))
    cap.store.add(planted("unrelated", "other"))
    other_before = cap.store.get("unrelated").code.copy()
    before_state = cap.state_hash()
    support = SupportExample(record_id="replacement", fact_id="fact", revision=2, entity_id="entity", family_id="family",
                             prompt_ids=(5, 6), answer_ids=(7,))
    trace, cost = adapt_record(cap, support, FastConfig(steps=1, lr=float("nan")))
    controls["rejected_revision"] = {"accepted": trace.accepted, "reason": trace.rolled_back_reason,
        "persistent_state_changed": before_state != cap.state_hash(), "old_active": cap.store.get("old").active,
        "new_active": cap.store.get("replacement").active,
        "unrelated_code_unchanged": np.array_equal(other_before, cap.store.get("unrelated").code),
        "reusable_parameters_unchanged": params_hash(theta) == initial_theta_hash}
    # A valid, small support step must also leave unrelated records and theta alone.
    support2 = replace(support, record_id="third", fact_id="fresh")
    tr2, _ = adapt_record(cap, support2, FastConfig(steps=1, lr=0.01))
    controls["ordinary_support_update"] = {"accepted": tr2.accepted, "loss_before": tr2.loss_before, "loss_after": tr2.loss_after,
        "unrelated_code_unchanged": np.array_equal(other_before, cap.store.get("unrelated").code),
        "reusable_parameters_unchanged": params_hash(theta) == initial_theta_hash}
    cap.reset_queries()
    p1, p2 = np.int32([5, 6]), np.int32([5, 6, 7])
    cap.selection_for(p1)
    inherited = cap.selection_for(p2)
    inherited_len = inherited.prompt_len
    stale_logits = cap.predict(p2).logits
    cap.reset_queries()
    fresh = cap.selection_for(p2)
    fresh_logits = cap.predict(p2).logits
    controls["independent_query_prefix_collision"] = {"second_prompt_tokens": len(p2), "cached_selection_prompt_len": inherited_len,
        "fresh_selection_prompt_len": fresh.prompt_len, "logits_max_abs_difference": float(np.max(np.abs(stale_logits - fresh_logits))),
        "condition": "p1 then independent p2 without explicit reset; current harness does not supply a per-query reset boundary"}
    snap = cap.export_state()
    single = RevisionCap(TinyBase(base.params), replace(cfg, single_site=True), Ledger(), params=theta)
    single.import_state(snap)
    cap.reset_queries()
    same_hash = single.state_hash() == cap.state_hash()
    single_logits = single.predict(p2).logits
    full_logits = cap.predict(p2).logits
    threshold = RevisionCap(TinyBase(base.params), replace(cfg, null_threshold=0.0), Ledger(), params=theta)
    threshold.import_state(snap)
    controls["snapshot_configuration"] = {"single_site_mismatch_accepted": True, "single_site_mismatch_same_state_hash": same_hash,
        "single_site_logits_max_abs_difference": float(np.max(np.abs(single_logits - full_logits))),
        "different_null_threshold_import_accepted": True, "threshold_snapshot_hash_matches": threshold.state_hash() == snap.content_hash()}
    empty = RevisionCap(TinyBase(base.params), replace(cfg, ceiling_bytes=1), Ledger(), params=theta)
    declared = empty.memory_bytes().occupied_bytes
    calls = empty.base.calls["forward"]
    fr = empty.predict(p1)
    controls["returned_query_cost"] = {"actual_full_forward_calls": empty.base.calls["forward"] - calls,
        "returned_full_forwards": fr.cost.full_forwards, "returned_tokens": fr.cost.tokens,
        "cached_prompt_reads": empty.cost_counters["cached_prompt_reads"]}
    long_store = RecordStore(dk=8, d_code=6, ceiling_bytes=256)
    long_store.add(planted("x" * 10000, "long"))
    long_state = long_store.export()
    lower_bound = sum(v.nbytes for v in long_state.arrays.values()) + len(long_state.scalars["records"].encode())
    defaults = {"reader": init_reader(jax.random.PRNGKey(8), ReaderConfig()),
                "controller": init_controller(jax.random.PRNGKey(9), ControllerConfig())}
    controls["capacity"] = {"tiny_reusable_weight_bytes": int(sum(v.nbytes for v in jax.tree_util.tree_leaves(theta))),
        "accepted_ceiling_bytes": 1, "empty_cap_reported_bytes": declared,
        "long_record_ceiling_bytes": 256, "long_record_reported_bytes": long_store.bytes()["total"],
        "long_record_serialized_payload_lower_bound_bytes": int(lower_bound), "reported_index_bytes": long_store.bytes()["index"],
        "default_reusable_parameter_count": param_count(defaults),
        "default_reusable_weight_bytes": int(sum(v.nbytes for v in jax.tree_util.tree_leaves(defaults)))}
    # Instrument the observation-only entry point directly.
    original_forward = base.forward
    seen = []
    def spy(ids, writes=(), **kw):
        seen.append(len(writes))
        return original_forward(ids, writes, **kw)
    base.forward = spy
    cap.enc.observe(p1)
    base.forward = original_forward
    controls["observation_write_free"] = {"write_counts": seen, "base_parameters_unchanged": params_hash(base.params) == initial_base_hash}
    out["source_sha256_after"] = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    out["source_changed_during_controls"] = out["source_sha256_after"] != sources
    out["gpu_seconds"] = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as f:
        json.dump(out, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(controls, indent=2))


if __name__ == "__main__":
    main()
