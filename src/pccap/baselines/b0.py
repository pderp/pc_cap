"""B0 frozen baseline: evaluation is charged, update is a state-preserving no-op."""

from pccap.baselines.lora import state_memory
from pccap.baselines.lora_forward import Prediction
from pccap.contracts import CostRecord, ItemOutcome
from pccap.harness.snapshot import LearnerState, SnapshotError


class B0:
    name = "B0"

    def __init__(self, base):
        self.base, self.ledger = base, base.ledger
        self._base_hash = base.checksum()

    def predict(self, ids):
        return Prediction(self.base.forward(ids, phase="query").logits)

    def update_item(self, item):
        return ItemOutcome(item.item_id, "accepted", False, [], 0, CostRecord(),
                           codes=["frozen_baseline_no_update"])

    def base_checksum(self):
        return self.base.checksum()

    def export_state(self):
        return LearnerState(scalars={"kind": "B0", "base_checksum": self._base_hash})

    def import_state(self, state):
        if state.content_hash() != self.export_state().content_hash() or self.base_checksum() != self._base_hash:
            raise SnapshotError("incompatible frozen baseline snapshot")

    def state_hash(self):
        return self.export_state().content_hash()

    def memory_bytes(self):
        return state_memory(self.export_state(), self.base.d)
