"""ePC checkpoint regeneration (REG-00..03; PA-1, SD-15, DEC-006, DEC-014).

JAX re-implementation of the sibling's 50M-token OpenWebText distillation (read-only reference,
DEC-003): ``recipe`` (the pinned settings), ``data`` (shard preparation and batch indexing),
``schedule`` (homotopy stages and the tracking-residual hold monitor), ``train`` (the jitted
step, checkpoints, milestones, CLI). The predictive-coding math lives in ``pccap.pc``
(``epc_inference.relax_errors``, ``weight_phase.local_weight_energy``, ``kd_energy.KDEnergy``).
"""
