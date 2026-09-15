"""R1-61 comparator construction and honest, prompt-only observation.

The wrapper changes no learning algorithm. Audit metadata is supplied separately
from model state; v0 active slots are not relabeled as RevisionCap records.
"""

from __future__ import annotations

import copy
from dataclasses import asdict, replace
from types import SimpleNamespace

import numpy as np

from pccap.cap.cap import CapConfig
from pccap.contracts import Budget
from pccap.harness.arms import make_learner, router_for
from pccap.revision_v1.adapt import FastConfig
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.controller import ControllerConfig
from pccap.revision_v1.endpoints_unseen import revision_selection
from pccap.revision_v1.learner import RevisionCap, RevisionConfig
from pccap.revision_v1.matched_update import MatchedRule, MatchedUpdateCap
from pccap.revision_v1.reader import ReaderConfig, params_hash
from pccap.revision_v1.v0_stable import StableCap

CORE_CONDITIONS = (
    "R1_learned_ff",
    "R1_nonlearned",
    "v0_stable",
    "matched_update",
    "v0_live_C1",
    "v0_live_C2",
    "S1_LM",
    "S1_literal",
)
SECONDARY_CONDITION = "R1_learned_ff_v2"


class CellAdapter:
    def __init__(self, learner, condition, *, budget=None, router=None, locality_base=None):
        if condition not in (*CORE_CONDITIONS, SECONDARY_CONDITION):
            raise ValueError("unknown condition")
        self.learner, self.condition = learner, condition
        self.base = learner.base
        self.locality_base = locality_base if locality_base is not None else self.base
        if condition.startswith("S1_") and locality_base is None:
            raise ValueError("S1 requires the original base as the common locality reference")
        self.ledger = getattr(learner, "ledger", None)
        self.budget, self.router = budget or Budget(A=0.3), router
        self.last_original_outcome = None

    def __getattr__(self, name):
        return getattr(self.learner, name)

    def reset_queries(self):
        reset = getattr(self.learner, "reset_queries", None)
        if reset:
            reset()

    def predict(self, ids):
        return self.learner.predict(ids)

    def import_state(self, state):
        self.learner.import_state(state)
        self.reset_queries()

    def update_item(self, item):
        self.reset_queries()
        # Fixture learners use a one-argument update; production families share
        # the router/budget interface.
        if isinstance(self.learner, (RevisionCap, StableCap, MatchedUpdateCap)) or hasattr(
            self.learner, "banks"
        ):
            out = self.learner.update_item(item, self.router, self.budget)
        else:
            out = self.learner.update_item(item)
        self.last_original_outcome = str(out.code)
        resource = out.code == "resource_stop" or any(
            str(c).startswith("resource_failure:") for c in out.codes
        )
        if out.code == "acquisition_failure" and not resource:
            out = copy.copy(out)
            out.code = "rejected_no_improvement"
        self.reset_queries()
        return out

    def observe_firing(self, ids):
        return revision_selection(self.learner, ids)

    def observe(self):
        memory = self.learner.memory_bytes() if hasattr(self.learner, "memory_bytes") else None
        records = getattr(getattr(self.learner, "store", None), "records", None)
        slots = None
        if hasattr(self.learner, "banks"):
            slots = sum(
                int(np.count_nonzero(bs.bank.metadata.meta["active"]))
                for bs in self.learner.banks.values()
            )
        return {
            "memory_status": "ok" if memory is not None else "unavailable",
            "memory": asdict(memory) if memory is not None else None,
            "active_records": sum(bool(r.active) for r in records) if records is not None else None,
            "active_records_status": "ok" if records is not None else "unavailable",
            "active_slots": slots,
            "firing_observer_status": "available"
            if isinstance(self.learner, RevisionCap)
            else "unavailable",
            "units_note": "v0 slots may represent answer prefixes; they are not one record per fact",
        }

    def memory_inventory(self, items):
        """Authenticate v0 slot owners against full attempted edit history."""
        records = getattr(getattr(self.learner, "store", None), "records", None)
        if records is not None:
            return records
        if not hasattr(self.learner, "banks"):
            return None
        by_digest = {bytes(it.digest[:16]).ljust(16, b"\0"): it for it in items}
        rows = []
        for bank, bs in self.learner.banks.items():
            for slot, row in enumerate(bs.bank.metadata.meta):
                if not row["active"] and not (int(row["flags"]) & 2):
                    continue
                owner = bytes(row["owner_digest"]).ljust(16, b"\0")
                if owner not in by_digest:
                    raise ValueError("memory owner is not covered by attempted edit history")
                rows.append(
                    SimpleNamespace(
                        fact_id=by_digest[owner].fact_id,
                        active=bool(row["active"]),
                        record_id=f"slot:{bank}:{slot}",
                    )
                )
        return rows

    def identity(self):
        cfg = getattr(self.learner, "cfg", None)
        rule = getattr(self.learner, "rule", None)
        return {
            "condition": self.condition,
            "class": type(self.learner).__module__ + "." + type(self.learner).__name__,
            "config_sha256": digest(asdict(cfg)) if cfg is not None else None,
            "rule": asdict(rule) if rule is not None else None,
            "budget": asdict(self.budget),
            "base_sha256": self.base.checksum(recompute=True),
            "locality_base_sha256": self.locality_base.checksum(recompute=True),
            "params_sha256": params_hash(self.learner.params)
            if hasattr(self.learner, "params")
            else None,
        }


def build_adapter(
    condition,
    base,
    ledger,
    *,
    calibration,
    params=None,
    seed=0,
    stop_tokens=(),
    revision_config=None,
    synthetic=False,
    locality_base=None,
    budget=None,
):
    """Explicit calibrated factory; real readers require supplied pinned weights.

    Admission binds identity() externally. A config override is synthetic-only,
    so a short TinyBase test cannot silently redefine the registered condition.
    """
    if condition not in (*CORE_CONDITIONS, SECONDARY_CONDITION):
        raise ValueError("unknown condition")
    scales = {int(k): float(v) for k, v in calibration["bank_scales"].items()}
    radii = {int(k): float(v) for k, v in calibration["radii"].items()}
    if set(scales) != {1, 2, 3} or set(radii) != {1, 2, 3}:
        raise ValueError("all three calibrated banks required")
    if any(not np.isfinite(v) or v <= 0 for v in scales.values()) or any(
        not np.isfinite(v) or v < 0 for v in radii.values()
    ):
        raise ValueError("invalid calibration")
    budget = budget or Budget(A=0.3)
    arm = "C2" if condition == "v0_live_C2" else "C1"
    if condition.startswith("R1_"):
        if not synthetic and (params is None or revision_config is not None):
            raise ValueError("real reader requires pinned parameters and registered configuration")
        random = condition == "R1_nonlearned"
        rc = ReaderConfig(
            d=base.d, lexical=not random, pairwise_null=not random, stop_tokens=tuple(stop_tokens)
        )
        cc = ControllerConfig(d=base.d, A=budget.A, bank_scales=tuple(scales[k] for k in (1, 2, 3)))
        cfg = RevisionConfig(
            reader=rc,
            controller=cc,
            fast=FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=budget.tau_edit),
            tau_edit=budget.tau_edit,
            seed=seed,
            min_score=0.93 if random else None,
            null_threshold=1.01 if random else 0.5,
            rare_overlap_min=1 if condition == "R1_learned_ff" else None,
            rare_df_max=2,
        )
        if revision_config is not None:
            cfg = replace(
                revision_config,
                null_threshold=cfg.null_threshold,
                min_score=cfg.min_score,
                rare_overlap_min=cfg.rare_overlap_min,
                rare_df_max=2,
            )
            cfg.reader = replace(
                cfg.reader,
                lexical=not random,
                pairwise_null=not random,
                cosine=True,
                tie_heads=True,
            )
        learner = RevisionCap(base, cfg, ledger, params=params)
    else:
        if revision_config is not None or params is not None:
            raise ValueError("reader parameters do not belong to a v0 family")
        cfg = CapConfig(arm=arm, d=base.d, radii=radii, bank_scales=scales, seed=seed)
        if condition in ("v0_stable", "S1_LM", "S1_literal"):
            learner = StableCap(base, cfg, ledger)
        elif condition == "matched_update":
            learner = MatchedUpdateCap(base, cfg, ledger, MatchedRule(steps=5, lr=0.1))
        else:
            learner = make_learner(arm, base, ledger, radii=radii, bank_scales=scales, seed=seed)
    return CellAdapter(
        learner, condition, budget=budget, router=router_for(arm), locality_base=locality_base
    )
